"""
Risk management module.

Handles:
- Position sizing (% of wallet)
- Stop loss / Take profit calculation
- Daily loss tracking
- Circuit breaker (pause trading if daily loss exceeded)
- Trailing Stop Logic
"""

from dataclasses import asdict, dataclass, field
from datetime import date
from typing import Optional

import pandas as pd
import structlog

from src import indicators

from .config import get_config

logger = structlog.get_logger()


@dataclass
class DailyStats:
    """Track daily trading statistics."""

    date: date = field(default_factory=date.today)
    starting_balance: float = 0.0
    realized_pnl: float = 0.0
    trades_count: int = 0
    wins: int = 0
    losses: int = 0

    @property
    def pnl_pct(self) -> float:
        """Daily P/L as percentage of starting balance."""
        if self.starting_balance <= 0:
            return 0.0
        return (self.realized_pnl / self.starting_balance) * 100

    @property
    def win_rate(self) -> float:
        """Win rate as percentage."""
        if self.trades_count == 0:
            return 0.0
        return (self.wins / self.trades_count) * 100

    def to_dict(self):
        """Convert to dictionary with date serialized."""
        data = asdict(self)
        data["date"] = self.date.isoformat()
        return data

    @classmethod
    def from_dict(cls, data):
        """Create from dictionary."""
        if isinstance(data.get("date"), str):
            data["date"] = date.fromisoformat(data["date"])
        return cls(**data)


@dataclass
class RiskCheck:
    """Result of a risk validation check."""

    approved: bool
    reason: str
    position_size: float = 0.0
    stop_loss_price: float = 0.0
    take_profit_price: float = 0.0


class RiskManager:
    """
    Risk management for trading operations.

    Enforces:
    - Position sizing limits
    - Stop loss and take profit levels
    - Daily loss limits (circuit breaker)
    """

    def __init__(self, database=None):
        config = get_config()
        self.position_size_pct = config.trading.position_size_pct
        self.stop_loss_pct = config.risk.stop_loss_pct
        self.take_profit_pct = config.risk.take_profit_pct
        self.max_daily_loss_pct = config.risk.max_daily_loss_pct
        self.max_weekly_loss_pct = getattr(config.risk, "max_weekly_loss_pct", 10.0)
        self.max_positions = config.risk.max_positions
        self.leverage = config.exchange.leverage
        self.auto_deleverage_threshold = getattr(
            config.risk, "auto_deleverage_threshold_pct", 10.0
        )

        self.liquidation_buffer_pct = getattr(
            config.risk, "liquidation_buffer_pct", 0.5
        )

        # ATR Stops Config
        self.use_atr_stops = getattr(config.risk, "use_atr_stops", False)
        self.atr_period = getattr(config.risk, "atr_period", 14)
        self.atr_multiplier_sl = getattr(config.risk, "atr_multiplier_sl", 1.5)
        self.atr_multiplier_tp = getattr(config.risk, "atr_multiplier_tp", 2.0)

        # Trailing Stop Config
        self.trailing_stop_activation_pct = getattr(
            config.risk, "trailing_stop_activation_pct", 1.0
        )
        self.trailing_stop_callback_pct = getattr(
            config.risk, "trailing_stop_callback_pct", 0.5
        )

        # Daily tracking
        self.daily_stats = DailyStats()
        self.consecutive_losses = 0  # Track consecutive losses for drawdown sizing
        self.peak_equity = 0.0  # Track peak equity for max drawdown sizing
        self._circuit_breaker_active = False
        self._weekly_circuit_breaker_active = False

        # Persistence
        from .database.factory import DatabaseFactory

        self.database = database or DatabaseFactory.get_database(config)
        self._state_key_prefix = "omnitrader:risk:"

    async def load_state(self):
        """Restore state from persistent database."""
        logger.info("risk_manager_restoring_state")
        try:
            # Restore Daily Stats
            daily_stats_data = await self.database.get_state(
                f"{self._state_key_prefix}daily_stats"
            )
            is_same_day = False
            if daily_stats_data:
                stats = DailyStats.from_dict(daily_stats_data)
                # Only restore if it's the same day
                if stats.date == date.today():
                    self.daily_stats = stats
                    is_same_day = True
                    logger.info("restored_daily_stats", stats=daily_stats_data)
                else:
                    logger.info(
                        "skipping_stale_daily_stats", stored_date=str(stats.date)
                    )

            # Restore Consecutive Losses (streak carries over days unless reset by win)
            losses = await self.database.get_state(
                f"{self._state_key_prefix}consecutive_losses"
            )
            if losses is not None:
                self.consecutive_losses = int(losses.get("value", 0))
                logger.info(
                    "restored_consecutive_losses", count=self.consecutive_losses
                )

            # Restore Peak Equity
            peak_eq = await self.database.get_state(
                f"{self._state_key_prefix}peak_equity"
            )
            if peak_eq is not None:
                self.peak_equity = float(peak_eq.get("value", 0.0))
                logger.info("restored_peak_equity", peak_equity=self.peak_equity)

            # Restore Circuit Breakers
            if is_same_day:
                cb_active = await self.database.get_state(
                    f"{self._state_key_prefix}circuit_breaker"
                )
                if cb_active is not None:
                    self._circuit_breaker_active = bool(cb_active.get("value", False))
            else:
                self._circuit_breaker_active = False

            wcb_active = await self.database.get_state(
                f"{self._state_key_prefix}weekly_circuit_breaker"
            )
            if wcb_active is not None:
                self._weekly_circuit_breaker_active = bool(
                    wcb_active.get("value", False)
                )

            logger.info("risk_state_restored")

        except Exception as e:
            logger.error("risk_state_restore_failed_critical", error=str(e))
            raise  # Fail-fast on startup if we cannot retrieve critical risk state

    async def save_state(self):
        """Persist state to database."""
        try:
            # Save Daily Stats (expire in 24h just in case, though we check date on load)
            await self.database.set_state(
                f"{self._state_key_prefix}daily_stats",
                self.daily_stats.to_dict(),
                expires_in=86400,
            )

            # Save other fields
            await self.database.set_state(
                f"{self._state_key_prefix}consecutive_losses",
                {"value": self.consecutive_losses},
            )
            await self.database.set_state(
                f"{self._state_key_prefix}peak_equity", {"value": self.peak_equity}
            )
            await self.database.set_state(
                f"{self._state_key_prefix}circuit_breaker",
                {"value": self._circuit_breaker_active},
            )
            await self.database.set_state(
                f"{self._state_key_prefix}weekly_circuit_breaker",
                {"value": self._weekly_circuit_breaker_active},
            )
        except Exception as e:
            logger.error("risk_state_save_failed_critical", error=str(e))
            raise  # Fail-fast during operation if risk limits cannot be persisted safely

    def update_config(self, config):
        """Update risk parameters from new configuration."""
        self.position_size_pct = config.trading.position_size_pct
        self.stop_loss_pct = config.risk.stop_loss_pct
        self.take_profit_pct = config.risk.take_profit_pct
        self.max_daily_loss_pct = config.risk.max_daily_loss_pct
        self.max_weekly_loss_pct = getattr(config.risk, "max_weekly_loss_pct", 10.0)
        self.max_positions = config.risk.max_positions
        self.leverage = config.exchange.leverage

        self.liquidation_buffer_pct = getattr(
            config.risk, "liquidation_buffer_pct", 0.5
        )

        # Update ATR stops config
        self.use_atr_stops = getattr(config.risk, "use_atr_stops", False)
        self.atr_period = getattr(config.risk, "atr_period", 14)
        self.atr_multiplier_sl = getattr(config.risk, "atr_multiplier_sl", 1.5)
        self.atr_multiplier_tp = getattr(config.risk, "atr_multiplier_tp", 2.0)

        self.trailing_stop_activation_pct = getattr(
            config.risk, "trailing_stop_activation_pct", 1.0
        )
        self.trailing_stop_callback_pct = getattr(
            config.risk, "trailing_stop_callback_pct", 0.5
        )

        logger.info(
            "risk_config_updated",
            position_size_pct=self.position_size_pct,
            stop_loss_pct=self.stop_loss_pct,
            take_profit_pct=self.take_profit_pct,
            max_daily_loss_pct=self.max_daily_loss_pct,
            liquidation_buffer_pct=self.liquidation_buffer_pct,
            use_atr_stops=self.use_atr_stops,
        )

    async def initialize_daily_stats(self, current_balance: float):
        """Initialize or reset daily statistics."""
        today = date.today()

        state_changed = False
        if self.daily_stats.date != today:
            # New day - reset stats
            logger.info(
                "daily_stats_reset",
                previous_date=str(self.daily_stats.date),
                previous_pnl=self.daily_stats.realized_pnl,
            )
            self.daily_stats = DailyStats(date=today, starting_balance=current_balance)
            self._circuit_breaker_active = False
            state_changed = True
        elif self.daily_stats.starting_balance == 0:
            # First run of the day
            self.daily_stats.starting_balance = current_balance
            state_changed = True

        # Update peak equity
        if current_balance > self.peak_equity:
            logger.info(
                "peak_equity_updated",
                old_peak=self.peak_equity,
                new_peak=current_balance,
            )
            self.peak_equity = current_balance
            state_changed = True

        if state_changed:
            await self.save_state()

    def calculate_position_size(self, balance: float, entry_price: float) -> float:
        """
        Calculate position size based on risk parameters.

        Args:
            balance: Available USDT balance
            entry_price: Expected entry price

        Returns:
            Position size in base currency (e.g., BTC)
        """
        # Determine effective leverage (Auto-Deleverage)
        effective_leverage = self.leverage

        # Check for significant drawdown against peak equity
        if balance > self.peak_equity:
            self.peak_equity = balance

        if self.peak_equity > 0:
            drawdown_pct = ((self.peak_equity - balance) / self.peak_equity) * 100
            if drawdown_pct >= self.auto_deleverage_threshold:
                effective_leverage = 1
                logger.warning(
                    "auto_deleverage_active",
                    drawdown_pct=drawdown_pct,
                    threshold=self.auto_deleverage_threshold,
                    original_leverage=self.leverage,
                    new_leverage=1,
                )

        # Risk amount in USDT
        risk_amount = balance * (self.position_size_pct / 100)

        # With leverage, we can open a larger position
        notional_value = risk_amount * effective_leverage

        # Convert to base currency
        position_size = notional_value / entry_price

        # Drawdown sizing: Reduce size by 50% if 3+ consecutive losses
        if self.consecutive_losses >= 3:
            original_size = position_size
            position_size *= 0.5
            logger.warning(
                "drawdown_sizing_active",
                consecutive_losses=self.consecutive_losses,
                original_size=original_size,
                new_size=position_size,
            )

        logger.debug(
            "position_size_calculated",
            balance=balance,
            risk_pct=self.position_size_pct,
            leverage=effective_leverage,
            notional=notional_value,
            size=position_size,
            consecutive_losses=self.consecutive_losses,
        )

        return position_size

    def calculate_stop_loss(self, entry_price: float, side: str) -> float:
        """
        Calculate stop loss price based on fixed percentage.

        Args:
            entry_price: Position entry price
            side: "long" or "short"

        Returns:
            Stop loss price
        """
        if side == "long":
            return entry_price * (1 - self.stop_loss_pct / 100)
        else:  # short
            return entry_price * (1 + self.stop_loss_pct / 100)

    def calculate_take_profit(self, entry_price: float, side: str) -> float:
        """
        Calculate take profit price based on fixed percentage.

        Args:
            entry_price: Position entry price
            side: "long" or "short"

        Returns:
            Take profit price
        """
        if side == "long":
            return entry_price * (1 + self.take_profit_pct / 100)
        else:  # short
            return entry_price * (1 - self.take_profit_pct / 100)

    def calculate_atr_stops(
        self, entry_price: float, side: str, ohlcv: pd.DataFrame
    ) -> tuple[float, float]:
        """
        Calculate Stop Loss and Take Profit using ATR.

        Args:
            entry_price: Position entry price
            side: "long" or "short"
            ohlcv: OHLCV DataFrame for ATR calculation

        Returns:
            Tuple (stop_loss, take_profit)
        """
        if ohlcv is None or ohlcv.empty:
            # Fallback to fixed percentage
            logger.warning("atr_stops_fallback_no_data")
            return (
                self.calculate_stop_loss(entry_price, side),
                self.calculate_take_profit(entry_price, side),
            )

        try:
            atr = indicators.atr(
                ohlcv["high"], ohlcv["low"], ohlcv["close"], length=self.atr_period
            )
            if atr is None or atr.empty:
                logger.warning("atr_stops_fallback_calc_failed")
                return (
                    self.calculate_stop_loss(entry_price, side),
                    self.calculate_take_profit(entry_price, side),
                )

            current_atr = atr.iloc[-1]

            if side == "long":
                stop_loss = entry_price - (current_atr * self.atr_multiplier_sl)
                take_profit = entry_price + (current_atr * self.atr_multiplier_tp)
            else:  # short
                stop_loss = entry_price + (current_atr * self.atr_multiplier_sl)
                take_profit = entry_price - (current_atr * self.atr_multiplier_tp)

            return stop_loss, take_profit

        except Exception as e:
            logger.error("atr_stops_calculation_failed", error=str(e))
            # Fallback
            return (
                self.calculate_stop_loss(entry_price, side),
                self.calculate_take_profit(entry_price, side),
            )

    def validate_trade(
        self,
        side: str,
        balance: float,
        entry_price: float,
        symbol: str = "BTC/USDT",
        exchange=None,
        current_positions: int = 0,
        ohlcv: pd.DataFrame = None,
    ) -> RiskCheck:
        """
        Validate a potential trade against risk rules.

        Args:
            side: "long" or "short"
            balance: Available balance
            entry_price: Expected entry price
            symbol: Trading symbol (e.g., "BTC/USDT") for exchange market info
            exchange: Exchange instance to fetch market minimum order size
            current_positions: Number of open positions
            ohlcv: OHLCV DataFrame for dynamic stop calculations

        Returns:
            RiskCheck with approval status and calculated values
        """
        # Check circuit breaker
        if self._circuit_breaker_active:
            return RiskCheck(
                approved=False,
                reason=f"Circuit breaker active: daily loss exceeded {self.max_daily_loss_pct}%",
            )

        # Check max positions
        if current_positions >= self.max_positions:
            return RiskCheck(
                approved=False, reason=f"Max positions reached ({self.max_positions})"
            )

        # Check minimum balance
        min_balance = 10.0  # Minimum $10 to trade
        if balance < min_balance:
            return RiskCheck(
                approved=False,
                reason=f"Insufficient balance: ${balance:.2f} < ${min_balance}",
            )

        # Calculate position parameters
        position_size = self.calculate_position_size(balance, entry_price)

        if self.use_atr_stops and ohlcv is not None:
            stop_loss, take_profit = self.calculate_atr_stops(entry_price, side, ohlcv)
            logger.info("using_atr_stops", sl=stop_loss, tp=take_profit)
        else:
            stop_loss = self.calculate_stop_loss(entry_price, side)
            take_profit = self.calculate_take_profit(entry_price, side)

        # Validate position size - fetch min from exchange if available
        min_size = 0.001  # Fallback default (BTC)
        if exchange is not None and symbol in exchange.markets:
            try:
                limit_info = (
                    exchange.markets[symbol].get("limits", {}).get("amount", {})
                )
                exchange_min = limit_info.get("min")
                if exchange_min is not None:
                    min_size = exchange_min
                    logger.info(
                        "using_exchange_min_size", symbol=symbol, min_size=min_size
                    )
            except (KeyError, AttributeError, TypeError) as e:
                logger.warning(
                    "failed_to_fetch_exchange_min_size",
                    symbol=symbol,
                    error=str(e),
                    fallback_min_size=min_size,
                )

        if position_size < min_size:
            return RiskCheck(
                approved=False,
                reason=f"Position too small: {position_size:.6f} < {min_size} ({symbol})",
            )

        return RiskCheck(
            approved=True,
            reason="Trade approved",
            position_size=position_size,
            stop_loss_price=stop_loss,
            take_profit_price=take_profit,
        )

    def calculate_trailing_stop(
        self, current_price: float, position
    ) -> Optional[float]:
        """
        Calculate potential new stop loss price based on trailing rules.

        Note: This does not check against existing stop loss (ratcheting).
        That check must be performed by the caller who has access to open orders.

        Args:
            current_price: Current market price
            position: Position object (entry_price, side, etc.)

        Returns:
            Potential new stop price if activation threshold met, else None
        """
        if not position.is_open:
            return None

        # Calculate Unrealized PnL %
        if position.side == "long":
            pnl_pct = (
                (current_price - position.entry_price) / position.entry_price
            ) * 100

            # Check Activation
            if pnl_pct >= self.trailing_stop_activation_pct:
                return current_price * (1 - self.trailing_stop_callback_pct / 100)

        else:  # Short
            pnl_pct = (
                (position.entry_price - current_price) / position.entry_price
            ) * 100

            # Check Activation
            if pnl_pct >= self.trailing_stop_activation_pct:
                return current_price * (1 + self.trailing_stop_callback_pct / 100)

        return None

    async def record_trade(self, pnl: float):
        """
        Record a completed trade.

        Args:
            pnl: Realized P/L from the trade
        """
        self.daily_stats.realized_pnl += pnl
        self.daily_stats.trades_count += 1

        if pnl >= 0:
            self.daily_stats.wins += 1
            self.consecutive_losses = 0  # Reset streak
        else:
            self.daily_stats.losses += 1
            self.consecutive_losses += 1  # Increment streak

        logger.info(
            "trade_recorded",
            pnl=pnl,
            consecutive_losses=self.consecutive_losses,
            daily_pnl=self.daily_stats.realized_pnl,
            daily_pnl_pct=f"{self.daily_stats.pnl_pct:.2f}%",
        )

        # Check circuit breaker
        self._check_circuit_breaker()

        # Save state
        await self.save_state()

    def _check_circuit_breaker(self):
        """Check if circuit breaker should be triggered."""
        if self.daily_stats.pnl_pct <= -self.max_daily_loss_pct:
            self._circuit_breaker_active = True
            logger.warning(
                "circuit_breaker_triggered",
                daily_pnl_pct=f"{self.daily_stats.pnl_pct:.2f}%",
                limit=f"-{self.max_daily_loss_pct}%",
            )

    def check_circuit_breaker(self) -> bool:
        """
        Check if trading should be paused (daily or weekly).

        Returns:
            True if circuit breaker is active
        """
        return self._circuit_breaker_active or self._weekly_circuit_breaker_active

    async def check_weekly_circuit_breaker(
        self, weekly_pnl: float, current_balance: float
    ) -> bool:
        """
        Check if weekly loss limit is exceeded.

        Args:
            weekly_pnl: Accumulated PnL for the rolling week
            current_balance: Current account balance

        Returns:
            True if weekly circuit breaker is triggered
        """
        # If already active, check if condition still holds (allow recovery)
        # Or should it be latched until manual reset?
        # Requirement implies "pause trading", but rolling window naturally allows exit.
        # Removing the latch allows auto-recovery if PnL improves.

        # Approximate start of week balance
        # start_balance + weekly_pnl = current_balance => start_balance = current_balance - weekly_pnl
        # This approximation assumes no deposits/withdrawals
        start_week_balance = current_balance - weekly_pnl

        if start_week_balance <= 0:
            return False

        weekly_pnl_pct = (weekly_pnl / start_week_balance) * 100

        state_changed = False
        result = False

        if weekly_pnl_pct <= -self.max_weekly_loss_pct:
            if not self._weekly_circuit_breaker_active:
                self._weekly_circuit_breaker_active = True
                logger.warning(
                    "weekly_circuit_breaker_triggered",
                    weekly_pnl=weekly_pnl,
                    weekly_pnl_pct=f"{weekly_pnl_pct:.2f}%",
                    limit=f"-{self.max_weekly_loss_pct}%",
                )
                state_changed = True
            result = True
        else:
            if self._weekly_circuit_breaker_active:
                self._weekly_circuit_breaker_active = False
                state_changed = True
            result = False

        if state_changed:
            await self.save_state()

        return result

    def check_black_swan(self, ohlcv: pd.DataFrame) -> bool:
        """
        Detect extreme market moves (Black Swan events).
        Logic: >10% move in the last hour (High - Low range).

        Args:
            ohlcv: DataFrame containing OHLCV data.

        Returns:
            True if black swan event detected.
        """
        if ohlcv is None or ohlcv.empty:
            return False

        # Consider last 60 candles (assuming 1m timeframe)
        # Or check config timeframe? If timeframe is 1h, checking last 1 candle is enough.
        # But if timeframe is 1m, checking last 60 is safer.
        # Let's assume we want to check volatility over last 1 hour regardless of timeframe.
        # If timeframe > 1h, checking last candle covers > 1h.

        # Calculate volatility
        # We'll use the last 60 rows as a proxy for "recent" volatility if we don't know the timeframe explicitly here.
        # Better: use time index.

        try:
            last_timestamp = ohlcv.index[-1]
            one_hour_ago = last_timestamp - pd.Timedelta(hours=1)
            recent_data = ohlcv[ohlcv.index >= one_hour_ago]

            if recent_data.empty:
                return False

            high_max = recent_data["high"].max()
            low_min = recent_data["low"].min()

            if low_min <= 0:
                return False

            volatility_pct = (high_max - low_min) / low_min

            # Threshold: 10% move
            if volatility_pct > 0.10:
                logger.critical(
                    "black_swan_detected",
                    volatility_pct=f"{volatility_pct:.2%}",
                    high=high_max,
                    low=low_min,
                    duration="1h",
                )
                return True

        except (KeyError, IndexError, TypeError, AttributeError):
            logger.exception("black_swan_check_failed_malformed_data")
            # If data is malformed, we can't guarantee safety.
            # Fail-safe: triggering stop is safer than running blind.
            return True
        except Exception:
            logger.exception("black_swan_check_failed_unexpected_error")
            # For unexpected errors, fail-safe closed (trigger Black Swan stop).
            # A silent False on unexpected error can mask real Black Swan events.
            return True

        return False

    def check_liquidation_risk(self, position, current_price: float) -> bool:
        """
        Check if position is too close to liquidation price.

        Args:
            position: Position object
            current_price: Current market price

        Returns:
            True if risk is high (should close), False otherwise
        """
        if not position.is_open or position.liquidation_price <= 0:
            return False

        dist_to_liq = abs(current_price - position.liquidation_price)
        total_dist = abs(position.entry_price - position.liquidation_price)

        if total_dist == 0:
            return False

        # If remaining distance is less than X% of original distance
        remaining_pct = dist_to_liq / total_dist

        if remaining_pct < self.liquidation_buffer_pct:
            logger.warning(
                "liquidation_risk_critical",
                symbol=position.symbol,
                current_price=current_price,
                liquidation_price=position.liquidation_price,
                remaining_pct=f"{remaining_pct:.2%}",
                threshold=f"{self.liquidation_buffer_pct:.2%}",
            )
            return True

        return False

    def get_status(self) -> dict:
        """Get current risk status summary."""
        return {
            "circuit_breaker_active": self._circuit_breaker_active
            or self._weekly_circuit_breaker_active,
            "daily_breaker": self._circuit_breaker_active,
            "weekly_breaker": self._weekly_circuit_breaker_active,
            "daily_pnl": self.daily_stats.realized_pnl,
            "daily_pnl_pct": self.daily_stats.pnl_pct,
            "trades_today": self.daily_stats.trades_count,
            "win_rate": self.daily_stats.win_rate,
            "max_daily_loss_pct": self.max_daily_loss_pct,
            "remaining_loss_capacity": self.max_daily_loss_pct
            + self.daily_stats.pnl_pct,
        }
