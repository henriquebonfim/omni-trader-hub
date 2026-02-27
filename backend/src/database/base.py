"""
Abstract base class for database implementations.
"""

from abc import ABC, abstractmethod
from typing import Optional

class BaseDatabase(ABC):
    """
    Abstract interface for trade and signal storage.
    """

    @abstractmethod
    async def connect(self):
        """Initialize database connection."""
        pass

    @abstractmethod
    async def close(self):
        """Close database connection."""
        pass

    @abstractmethod
    async def backup_db(self):
        """Create a backup of the database."""
        pass

    @abstractmethod
    async def log_trade_open(
        self,
        symbol: str,
        side: str,
        price: float,
        size: float,
        notional: float,
        stop_loss: Optional[float],
        take_profit: Optional[float],
        reason: str = "signal",
        expected_price: Optional[float] = None,
        slippage: Optional[float] = None,
        fee: Optional[float] = None,
        fee_currency: Optional[str] = None,
    ) -> int:
        """Log a trade open event."""
        pass

    @abstractmethod
    async def log_trade_close(
        self,
        symbol: str,
        side: str,
        price: float,
        size: float,
        notional: float,
        pnl: float,
        pnl_pct: float,
        reason: str = "signal",
        expected_price: Optional[float] = None,
        slippage: Optional[float] = None,
        fee: Optional[float] = None,
        fee_currency: Optional[str] = None,
    ) -> int:
        """Log a trade close event."""
        pass

    @abstractmethod
    async def get_open_trade_fee(self, symbol: str) -> float:
        """Get the fee of the last OPEN trade for a symbol."""
        pass

    @abstractmethod
    async def save_daily_summary(
        self,
        date: str,
        starting_balance: float,
        ending_balance: float,
        pnl: float,
        pnl_pct: float,
        trades_count: int,
        wins: int,
        losses: int,
    ):
        """Save or update daily summary."""
        pass

    @abstractmethod
    async def get_recent_trades(self, limit: int = 10) -> list:
        """Get recent trades."""
        pass

    @abstractmethod
    async def get_last_trade(self, symbol: str) -> Optional[dict]:
        """Get the most recent trade for a symbol."""
        pass

    @abstractmethod
    async def get_daily_summary(self, date: str) -> Optional[dict]:
        """Get daily summary for a specific date."""
        pass

    @abstractmethod
    async def get_weekly_pnl(self, start_date: str) -> float:
        """Get total PnL since start_date (inclusive)."""
        pass

    @abstractmethod
    async def log_equity_snapshot(self, balance: float) -> None:
        """Log current balance as an equity snapshot."""
        pass

    @abstractmethod
    async def get_equity_snapshots(self, limit: int = 200) -> list:
        """Get recent equity snapshots."""
        pass

    @abstractmethod
    async def log_signal(
        self,
        symbol: str,
        price: float,
        signal: str,
        regime: str,
        reason: str,
        indicators: dict,
    ) -> None:
        """Log a strategy signal with indicator snapshot."""
        pass

    @abstractmethod
    async def log_funding_payment(
        self,
        symbol: str,
        rate: float,
        payment: float,
        position_size: float,
    ) -> None:
        """Log a funding payment."""
        pass
