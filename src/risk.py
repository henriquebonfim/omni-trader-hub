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
        self.max_positions = config.risk.max_positions
        self.leverage = config.exchange.leverage

        # Trailing Stop Config
        self.trailing_stop_activation_pct = getattr(config.risk, "trailing_stop_activation_pct", 1.0)
        self.trailing_stop_callback_pct = getattr(config.risk, "trailing_stop_callback_pct", 0.5)

        # Daily tracking
        self.daily_stats = DailyStats()
        self._circuit_breaker_active = False

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

        logger.debug(
            "position_size_calculated",
            balance=balance,
            risk_pct=self.position_size_pct,
            leverage=self.leverage,
            notional=notional_value,
            size=position_size,
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

    def calculate_trailing_stop(self, current_price: float, position) -> Optional[float]:
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
            pnl_pct = ((current_price - position.entry_price) / position.entry_price) * 100

            # Check Activation
            if pnl_pct >= self.trailing_stop_activation_pct:
                return current_price * (1 - self.trailing_stop_callback_pct / 100)

        else: # Short
            pnl_pct = ((position.entry_price - current_price) / position.entry_price) * 100

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
        else:
            self.daily_stats.losses += 1

        logger.info(
            "trade_recorded",
            pnl=pnl,
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
        Check if trading should be paused.

        Returns:
            True if circuit breaker is active
        """
        return self._circuit_breaker_active

    def get_status(self) -> dict:
        """Get current risk status summary."""
        return {
            "circuit_breaker_active": self._circuit_breaker_active,
            "daily_pnl": self.daily_stats.realized_pnl,
            "daily_pnl_pct": self.daily_stats.pnl_pct,
            "trades_today": self.daily_stats.trades_count,
            "win_rate": self.daily_stats.win_rate,
            "max_daily_loss_pct": self.max_daily_loss_pct,
            "remaining_loss_capacity": self.max_daily_loss_pct
            + self.daily_stats.pnl_pct,
        }
