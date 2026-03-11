"""
Abstract base class for exchange adapters.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import pandas as pd


class ExchangeError(Exception):
    """Base exception for exchange-related errors."""
    pass


class NetworkError(ExchangeError):
    """Exception for network-related errors (e.g. timeouts, connection refused)."""
    pass


class Position:
    """Represents a futures position."""

    def __init__(self, data: Optional[Dict[str, Any]] = None):
        if data is None:
            self.symbol = None
            self.side = None
            self.size = 0.0
            self.entry_price = 0.0
            self.notional = 0.0
            self.unrealized_pnl = 0.0
            self.leverage = 1
            self.liquidation_price = 0.0
        else:
            self.symbol = data.get("symbol")
            self.side = data.get("side")  # "long" or "short"
            self.size = float(data.get("contracts", 0))
            self.entry_price = float(data.get("entryPrice", 0))
            self.notional = float(data.get("notional", 0))
            self.unrealized_pnl = float(data.get("unrealizedPnl", 0))
            self.leverage = int(data.get("leverage", 1))
            self.liquidation_price = float(data.get("liquidationPrice", 0))

    @property
    def contracts(self) -> float:
        """Alias for size to match standard naming."""
        return self.size

    @property
    def is_open(self) -> bool:
        return self.size > 0

    def __repr__(self) -> str:
        if not self.is_open:
            return "Position(None)"
        return f"Position({self.side} {self.size} @ {self.entry_price}, PnL: {self.unrealized_pnl:.2f})"


class BaseExchange(ABC):
    """
    Abstract base class for exchange adapters.

    Provides a standard interface for:
    - Fetching market data
    - Managing positions
    - Placing orders
    """

    @abstractmethod
    async def connect(self) -> bool:
        """Initialize connection to exchange."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close exchange connection."""
        pass

    @abstractmethod
    async def update_config(self, config: Any) -> None:
        """Update exchange configuration."""
        pass

    @abstractmethod
    async def fetch_ohlcv(
        self,
        symbol: Optional[str] = None,
        timeframe: Optional[str] = None,
        limit: int = 100,
    ) -> pd.DataFrame:
        """Fetch OHLCV candle data."""
        pass

    @abstractmethod
    async def get_ticker(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Get current ticker for symbol."""
        pass

    @abstractmethod
    async def get_balance(self) -> Dict[str, float]:
        """Get account balance."""
        pass

    @abstractmethod
    async def get_position(self, symbol: Optional[str] = None) -> Position:
        """Get current position for symbol."""
        pass

    @abstractmethod
    async def get_open_positions(self) -> List[Position]:
        """Get all current open positions across all symbols."""
        pass

    @abstractmethod
    async def fetch_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all open orders for symbol."""
        pass

    @abstractmethod
    async def market_long(
        self, symbol: Optional[str] = None, amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """Open a long position with market order."""
        pass

    @abstractmethod
    async def market_short(
        self, symbol: Optional[str] = None, amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """Open a short position with market order."""
        pass

    @abstractmethod
    async def close_position(self, symbol: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Close the current position."""
        pass

    @abstractmethod
    async def set_stop_loss(
        self,
        symbol: Optional[str] = None,
        stop_price: Optional[float] = None,
        position_side: str = "long",
    ) -> Dict[str, Any]:
        """Place a stop-loss order."""
        pass

    @abstractmethod
    async def set_take_profit(
        self,
        symbol: Optional[str] = None,
        take_profit_price: Optional[float] = None,
        position_side: str = "long",
    ) -> Dict[str, Any]:
        """Place a take-profit order."""
        pass

    @abstractmethod
    async def cancel_all_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Cancel all open orders for symbol."""
        pass

    @abstractmethod
    async def get_current_price(self, symbol: Optional[str] = None) -> float:
        """Get current market price."""
        pass

    @abstractmethod
    async def fetch_my_trades(
        self, symbol: Optional[str] = None, limit: int = 10, since: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Fetch user's trade history."""
        pass

    @abstractmethod
    async def fetch_funding_rate(self, symbol: Optional[str] = None) -> float:
        """Fetch current funding rate for symbol."""
        pass

    @abstractmethod
    async def get_rate_limit_usage(self) -> Dict[str, Any]:
        """Get current API rate limit usage."""
        pass

    @abstractmethod
    async def get_order_fill_details(
        self,
        order_id: str,
        symbol: Optional[str] = None,
        retries: int = 5,
        delay: float = 1.0,
    ) -> Dict[str, Any]:
        """Verify order fills and return actual average price and fees."""
        pass

    @abstractmethod
    async def fetch_markets(self) -> List[Dict[str, Any]]:
        """Fetch all active markets (symbols) from the exchange."""
        pass
