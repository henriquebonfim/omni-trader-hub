"""
Risk management module (Facade).

Orchestrates specialized risk sub-components:
- Persistence (RiskStateStore)
- Sizing & SL/TP (PositionSizer)
- Validation (TradeValidator)
- Circuit Breakers (CircuitBreaker)
- Market Monitoring (MarketWatchdog)
"""

from datetime import date

import pandas as pd
import structlog

from src.config import get_config
from src.domain.risk.circuit_breaker import CircuitBreaker
from src.domain.risk.models import DailyStats, RiskCheck
from src.domain.risk.persistence import RiskStateStore
from src.domain.risk.sizer import PositionSizer
from src.domain.risk.validator import TradeValidator
from src.domain.risk.watchdog import MarketWatchdog

logger = structlog.get_logger()


class RiskManager:
    """
    Risk management facade.

    Enforces position sizing, SL/TP, daily/weekly limits, and market safety checks.
    """

    def __init__(self, database=None, bot_id: str = "default", config=None):
        self.config = config if config else get_config()
        self.bot_id = bot_id

        # Sub-components
        from src.infrastructure.database.factory import DatabaseFactory
        self.db = database or DatabaseFactory.get_database(self.config)

        self.store = RiskStateStore(self.db, bot_id)
        self.sizer = PositionSizer(self.config)
        self.validator = TradeValidator(self.config, self.sizer)
        self.circuit_breaker = CircuitBreaker(self.config)
        self.watchdog = MarketWatchdog(self.config)

        # State
        self.daily_stats = DailyStats()
        self.consecutive_losses = 0
        self.peak_equity = 0.0
        self._circuit_breaker_active = False
        self._weekly_circuit_breaker_active = False
        self.use_atr_stops = self.config.risk.use_atr_stops

    async def load_state(self):
        """Restore state using RiskStateStore."""
        losses, peak, daily, weekly = await self.store.load_state(
            self.daily_stats, self._circuit_breaker_active, self._weekly_circuit_breaker_active
        )
        self.consecutive_losses = losses
        self.peak_equity = peak
        self._circuit_breaker_active = daily
        self._weekly_circuit_breaker_active = weekly

    async def save_state(self):
        """Persist state using RiskStateStore."""
        await self.store.save_state(
            self.daily_stats,
            self.consecutive_losses,
            self.peak_equity,
            self._circuit_breaker_active,
            self._weekly_circuit_breaker_active
        )

    def update_config(self, config):
        """Update configuration and sub-components."""
        self.config = config
        self.sizer.config = config
        self.validator.config = config
        self.circuit_breaker.config = config
        self.watchdog.config = config
        logger.info("risk_config_updated")

    async def initialize_daily_stats(self, current_balance: float):
        """Initialize or reset daily statistics."""
        today = date.today()
        state_changed = False

        if self.daily_stats.date != today:
            self.daily_stats = DailyStats(date=today, starting_balance=current_balance)
            self._circuit_breaker_active = False
            state_changed = True
        elif self.daily_stats.starting_balance == 0:
            self.daily_stats.starting_balance = current_balance
            state_changed = True

        if current_balance > self.peak_equity:
            self.peak_equity = current_balance
            state_changed = True

        if state_changed:
            await self.save_state()

    def calculate_position_size(self, balance: float, entry_price: float) -> float:
        """Proxy to PositionSizer."""
        if balance > self.peak_equity:
            self.peak_equity = balance
        return self.sizer.calculate_position_size(
            balance, entry_price, self.peak_equity, self.consecutive_losses
        )

    def calculate_stop_loss(self, entry_price: float, side: str) -> float:
        """Proxy to PositionSizer."""
        return self.sizer.calculate_stop_loss(entry_price, side)

    def calculate_take_profit(self, entry_price: float, side: str) -> float:
        """Proxy to PositionSizer."""
        return self.sizer.calculate_take_profit(entry_price, side)

    def calculate_atr_stops(self, entry_price: float, side: str, ohlcv: pd.DataFrame) -> tuple[float, float]:
        """Proxy to PositionSizer."""
        return self.sizer.calculate_atr_stops(entry_price, side, ohlcv)

    def validate_trade(self, side: str, balance: float, entry_price: float, **kwargs) -> RiskCheck:
        """Proxy to TradeValidator."""
        return self.validator.validate_trade(
            side=side,
            balance=balance,
            entry_price=entry_price,
            peak_equity=self.peak_equity,
            consecutive_losses=self.consecutive_losses,
            daily_breaker_active=self._circuit_breaker_active,
            **kwargs
        )

    def calculate_trailing_stop(self, current_price: float, position) -> float | None:
        """Proxy to PositionSizer."""
        return self.sizer.calculate_trailing_stop(current_price, position)

    async def record_trade(self, pnl: float):
        """Record trade and update state."""
        self.daily_stats.realized_pnl += pnl
        self.daily_stats.trades_count += 1

        if pnl >= 0:
            self.daily_stats.wins += 1
            self.consecutive_losses = 0
        else:
            self.daily_stats.losses += 1
            self.consecutive_losses += 1

        self._circuit_breaker_active = self.circuit_breaker.check_daily_breaker(self.daily_stats.pnl_pct)
        await self.save_state()

    def check_circuit_breaker(self) -> bool:
        """Check if any circuit breaker is active."""
        return self._circuit_breaker_active or self._weekly_circuit_breaker_active

    async def check_weekly_circuit_breaker(self, weekly_pnl: float, current_balance: float) -> bool:
        """Check weekly breaker and persist state."""
        triggered = self.circuit_breaker.check_weekly_breaker(weekly_pnl, current_balance)
        if triggered != self._weekly_circuit_breaker_active:
            self._weekly_circuit_breaker_active = triggered
            await self.save_state()
        return triggered

    def check_black_swan(self, ohlcv: pd.DataFrame) -> bool:
        """Proxy to MarketWatchdog."""
        return self.watchdog.check_black_swan(ohlcv)

    def check_liquidation_risk(self, position, current_price: float) -> bool:
        """Proxy to MarketWatchdog."""
        return self.watchdog.check_liquidation_risk(position, current_price)

    def get_status(self) -> dict:
        """Get risk status summary."""
        return {
            "circuit_breaker_active": self.check_circuit_breaker(),
            "daily_breaker": self._circuit_breaker_active,
            "weekly_breaker": self._weekly_circuit_breaker_active,
            "daily_pnl": self.daily_stats.realized_pnl,
            "daily_pnl_pct": self.daily_stats.pnl_pct,
            "trades_today": self.daily_stats.trades_count,
            "win_rate": self.daily_stats.win_rate,
            "max_daily_loss_pct": self.config.risk.max_daily_loss_pct,
            "remaining_loss_capacity": self.config.risk.max_daily_loss_pct + self.daily_stats.pnl_pct,
        }
