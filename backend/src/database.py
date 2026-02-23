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
        self._connection.row_factory = aiosqlite.Row
        # Enable WAL mode for concurrent reads while bot writes
        await self._connection.execute("PRAGMA journal_mode=WAL")
        await self._create_tables()
        await self._migrate_tables()
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
                expected_price REAL,
                slippage REAL,
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

            CREATE TABLE IF NOT EXISTS equity_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                balance REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS signals_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                signal TEXT NOT NULL,
                reason TEXT,
                indicators TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp);
            CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
            CREATE INDEX IF NOT EXISTS idx_equity_timestamp ON equity_snapshots(timestamp);
            CREATE INDEX IF NOT EXISTS idx_signals_timestamp ON signals_log(timestamp);
        """
        )
        await self._connection.commit()

    async def _migrate_tables(self):
        """Perform schema migrations if needed."""
        try:
            # Check if expected_price column exists in trades
            cursor = await self._connection.execute("PRAGMA table_info(trades)")
            columns = [row["name"] for row in await cursor.fetchall()]

            if "expected_price" not in columns:
                logger.info("migrating_trades_table_add_expected_price")
                await self._connection.execute(
                    "ALTER TABLE trades ADD COLUMN expected_price REAL DEFAULT NULL"
                )

            if "slippage" not in columns:
                logger.info("migrating_trades_table_add_slippage")
                await self._connection.execute(
                    "ALTER TABLE trades ADD COLUMN slippage REAL DEFAULT NULL"
                )

            await self._connection.commit()
        except Exception as e:
            logger.error("migration_failed", error=str(e))

    async def log_trade_open(
        self,
        symbol: str,
        side: str,
        price: float,
        size: float,
        notional: float,
        stop_loss: float | None,
        take_profit: float | None,
        reason: str = "signal",
        expected_price: float | None = None,
        slippage: float | None = None,
    ) -> int:
        """
        Log a trade open event.

        Returns:
            Trade ID
        """
        cursor = await self._connection.execute(
            """
            INSERT INTO trades (
                timestamp, symbol, side, action, price, expected_price, slippage,
                size, notional, reason, stop_loss, take_profit
            )
            VALUES (?, ?, ?, 'OPEN', ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.utcnow().isoformat(),
                symbol,
                side.upper(),
                price,
                expected_price,
                slippage,
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
        return [dict(row) for row in rows]

    async def get_last_trade(self, symbol: str) -> dict | None:
        """Get the most recent trade for a symbol."""
        cursor = await self._connection.execute(
            "SELECT * FROM trades WHERE symbol = ? ORDER BY timestamp DESC LIMIT 1",
            (symbol,),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None

    async def get_daily_summary(self, date: str) -> dict | None:
        """Get daily summary for a specific date."""
        cursor = await self._connection.execute(
            "SELECT * FROM daily_summary WHERE date = ?", (date,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None

    async def log_equity_snapshot(self, balance: float) -> None:
        """Log current balance as an equity snapshot."""
        await self._connection.execute(
            "INSERT INTO equity_snapshots (timestamp, balance) VALUES (?, ?)",
            (datetime.utcnow().isoformat(), balance),
        )
        await self._connection.commit()

    async def get_equity_snapshots(self, limit: int = 200) -> list:
        """Get recent equity snapshots for charting."""
        cursor = await self._connection.execute(
            "SELECT * FROM equity_snapshots ORDER BY timestamp DESC LIMIT ?", (limit,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    async def log_signal(
        self,
        symbol: str,
        price: float,
        signal: str,
        reason: str,
        indicators: dict,
    ) -> None:
        """Log a strategy signal with indicator snapshot."""
        import json

        await self._connection.execute(
            """
            INSERT INTO signals_log (timestamp, symbol, price, signal, reason, indicators)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.utcnow().isoformat(),
                symbol,
                price,
                signal,
                reason,
                json.dumps(indicators),
            ),
        )
        await self._connection.commit()
