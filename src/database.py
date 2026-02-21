"""
Database module for trade logging.

Uses SQLite for persistent storage of trades and daily summaries.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

import aiosqlite
import structlog

logger = structlog.get_logger()


class Database:
    """
    SQLite database for trade history and statistics.
    """

    def __init__(self, db_path: str = None):
        if db_path is None:
            project_root = Path(__file__).parent.parent
            db_path = project_root / "data" / "trades.db"

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection: Optional[aiosqlite.Connection] = None

    async def connect(self):
        """Initialize database connection and create tables."""
        self._connection = await aiosqlite.connect(self.db_path)
        await self._create_tables()
        logger.info("database_connected", path=str(self.db_path))

    async def close(self):
        """Close database connection."""
        if self._connection:
            await self._connection.close()
            logger.info("database_disconnected")

    async def _create_tables(self):
        """Create database tables if they don't exist."""
        await self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                action TEXT NOT NULL,
                price REAL NOT NULL,
                size REAL NOT NULL,
                notional REAL NOT NULL,
                pnl REAL,
                pnl_pct REAL,
                reason TEXT,
                stop_loss REAL,
                take_profit REAL
            );

            CREATE TABLE IF NOT EXISTS daily_summary (
                date TEXT PRIMARY KEY,
                starting_balance REAL NOT NULL,
                ending_balance REAL NOT NULL,
                pnl REAL NOT NULL,
                pnl_pct REAL NOT NULL,
                trades_count INTEGER NOT NULL,
                wins INTEGER NOT NULL,
                losses INTEGER NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp);
            CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
        """
        )
        await self._connection.commit()

    async def log_trade_open(
        self,
        symbol: str,
        side: str,
        price: float,
        size: float,
        notional: float,
        stop_loss: float,
        take_profit: float,
        reason: str = "signal",
    ) -> int:
        """
        Log a trade open event.

        Returns:
            Trade ID
        """
        cursor = await self._connection.execute(
            """
            INSERT INTO trades (timestamp, symbol, side, action, price, size, notional, reason, stop_loss, take_profit)
            VALUES (?, ?, ?, 'OPEN', ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.utcnow().isoformat(),
                symbol,
                side.upper(),
                price,
                size,
                notional,
                reason,
                stop_loss,
                take_profit,
            ),
        )
        await self._connection.commit()

        logger.info(
            "trade_logged", action="OPEN", symbol=symbol, side=side, price=price
        )
        return cursor.lastrowid

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
    ) -> int:
        """
        Log a trade close event.

        Returns:
            Trade ID
        """
        cursor = await self._connection.execute(
            """
            INSERT INTO trades (timestamp, symbol, side, action, price, size, notional, pnl, pnl_pct, reason)
            VALUES (?, ?, ?, 'CLOSE', ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.utcnow().isoformat(),
                symbol,
                side.upper(),
                price,
                size,
                notional,
                pnl,
                pnl_pct,
                reason,
            ),
        )
        await self._connection.commit()

        logger.info("trade_logged", action="CLOSE", symbol=symbol, side=side, pnl=pnl)
        return cursor.lastrowid

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
        await self._connection.execute(
            """
            INSERT OR REPLACE INTO daily_summary
            (date, starting_balance, ending_balance, pnl, pnl_pct, trades_count, wins, losses)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                date,
                starting_balance,
                ending_balance,
                pnl,
                pnl_pct,
                trades_count,
                wins,
                losses,
            ),
        )
        await self._connection.commit()

    async def get_recent_trades(self, limit: int = 10) -> list:
        """Get recent trades."""
        cursor = await self._connection.execute(
            "SELECT * FROM trades ORDER BY timestamp DESC LIMIT ?", (limit,)
        )
        rows = await cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row, strict=False)) for row in rows]

    async def get_daily_summary(self, date: str) -> dict | None:
        """Get daily summary for a specific date."""
        cursor = await self._connection.execute(
            "SELECT * FROM daily_summary WHERE date = ?", (date,)
        )
        row = await cursor.fetchone()
        if row:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row, strict=False))
        return None
