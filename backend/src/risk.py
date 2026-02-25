"""
Risk management module.

Handles:
- Position sizing (% of wallet)
- Stop loss / Take profit calculation
- Daily loss tracking
- Circuit breaker (pause trading if daily loss exceeded)
- Trailing Stop Logic
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional

import pandas as pd
import structlog

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

    def __init__(self):
        config = get_config()
        self.position_size_pct = config.trading.position_size_pct
        self.stop_loss_pct = config.risk.stop_loss_pct
        self.take_profit_pct = config.risk.take_profit_pct
        self.max_daily_loss_pct = config.risk.max_daily_loss_pct
        self.max_weekly_loss_pct = getattr(config.risk, "max_weekly_loss_pct", 10.0)
        self.max_positions = config.risk.max_positions
        self.leverage = config.exchange.leverage

        self.liquidation_buffer_pct = getattr(config.risk, "liquidation_buffer_pct", 0.5)

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
        self._circuit_breaker_active = False
        self._weekly_circuit_breaker_active = False

    def update_config(self, config):
        """Update risk parameters from new configuration."""
        self.position_size_pct = config.trading.position_size_pct
        self.stop_loss_pct = config.risk.stop_loss_pct
        self.take_profit_pct = config.risk.take_profit_pct
        self.max_daily_loss_pct = config.risk.max_daily_loss_pct
        self.max_weekly_loss_pct = getattr(config.risk, "max_weekly_loss_pct", 10.0)
        self.max_positions = config.risk.max_positions
        self.leverage = config.exchange.leverage

        self.liquidation_buffer_pct = getattr(config.risk, "liquidation_buffer_pct", 0.5)

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
        )

    def initialize_daily_stats(self, current_balance: float):
        """Initialize or reset daily statistics."""
        today = date.today()

        if self.daily_stats.date != today:
            # New day - reset stats
            logger.info(
                "daily_stats_reset",
                previous_date=str(self.daily_stats.date),
                previous_pnl=self.daily_stats.realized_pnl,
            )
            self.daily_stats = DailyStats(date=today, starting_balance=current_balance)
            self.consecutive_losses = 0  # Reset streak for new day
            self._circuit_breaker_active = False
        elif self.daily_stats.starting_balance == 0:
            # First run of the day
            self.daily_stats.starting_balance = current_balance

    def calculate_position_size(self, balance: float, entry_price: float) -> float:
        """
        Calculate position size based on risk parameters.

        Args:
            balance: Available USDT balance
            entry_price: Expected entry price

        Returns:
            Position size in base currency (e.g., BTC)
        """
        # Risk amount in USDT
        risk_amount = balance * (self.position_size_pct / 100)

        # With leverage, we can open a larger position
        notional_value = risk_amount * self.leverage

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
            leverage=self.leverage,
            notional=notional_value,
            size=position_size,
            consecutive_losses=self.consecutive_losses,
        )

        return position_size

    def calculate_stop_loss(self, entry_price: float, side: str) -> float:
        """
        Calculate stop loss price.

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
        Calculate take profit price.

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

    def validate_trade(
        self, side: str, balance: float, entry_price: float, current_positions: int = 0
    ) -> RiskCheck:
        """
        Validate a potential trade against risk rules.

        Args:
            side: "long" or "short"
            balance: Available balance
            entry_price: Expected entry price
            current_positions: Number of open positions

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
        stop_loss = self.calculate_stop_loss(entry_price, side)
        take_profit = self.calculate_take_profit(entry_price, side)

        # Validate position size
        min_size = 0.001  # Minimum BTC size
        if position_size < min_size:
            return RiskCheck(
                approved=False,
                reason=f"Position too small: {position_size:.6f} < {min_size}",
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

    def record_trade(self, pnl: float):
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

    def check_weekly_circuit_breaker(self, weekly_pnl: float, current_balance: float) -> bool:
        """
        Check if weekly loss limit is exceeded.

        Args:
            weekly_pnl: Accumulated PnL for the rolling week
            current_balance: Current account balance

        Returns:
            True if weekly circuit breaker is triggered
        """
        if self._weekly_circuit_breaker_active:
            return True

        # Approximate start of week balance
        # start_balance + weekly_pnl = current_balance => start_balance = current_balance - weekly_pnl
        # This approximation assumes no deposits/withdrawals
        start_week_balance = current_balance - weekly_pnl

        if start_week_balance <= 0:
            return False

        weekly_pnl_pct = (weekly_pnl / start_week_balance) * 100

        if weekly_pnl_pct <= -self.max_weekly_loss_pct:
            self._weekly_circuit_breaker_active = True
            logger.warning(
                "weekly_circuit_breaker_triggered",
                weekly_pnl=weekly_pnl,
                weekly_pnl_pct=f"{weekly_pnl_pct:.2f}%",
                limit=f"-{self.max_weekly_loss_pct}%"
            )
            return True

        return False

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
                    duration="1h"
                )
                return True

        except Exception as e:
            logger.error("black_swan_check_failed", error=str(e))

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
            "circuit_breaker_active": self._circuit_breaker_active or self._weekly_circuit_breaker_active,
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
