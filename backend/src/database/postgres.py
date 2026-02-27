"""
PostgreSQL implementation of the database interface using asyncpg.
"""

import json
import os
from datetime import datetime, timezone
from typing import Optional

import asyncpg
import structlog

from .base import BaseDatabase

logger = structlog.get_logger()


class PostgresDatabase(BaseDatabase):
    """
    PostgreSQL database for trade history and statistics.
    """

    def __init__(self, connection_string: str = None):
        if connection_string is None:
            user = os.getenv("POSTGRES_USER", "omnitrader")
            password = os.getenv("POSTGRES_PASSWORD", "omnitrader_password")
            db = os.getenv("POSTGRES_DB", "trades_db")
            host = os.getenv("POSTGRES_HOST", "localhost")
            port = os.getenv("POSTGRES_PORT", "5432")
            connection_string = f"postgresql://{user}:{password}@{host}:{port}/{db}"

        self.dsn = connection_string
        self._pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        """Initialize database connection pool and create tables."""
        try:
            self._pool = await asyncpg.create_pool(
                dsn=self.dsn,
                min_size=1,
                max_size=10,
            )
            await self._create_tables()
            logger.info("database_connected", type="postgres")
        except Exception as e:
            logger.error("postgres_connection_failed", error=str(e))
            raise

    async def close(self):
        """Close database connection pool."""
        if self._pool:
            await self._pool.close()
            logger.info("database_disconnected", type="postgres")

    async def backup_db(self):
        """
        Create a backup of the database.
        
        Note: For Postgres, this usually involves calling pg_dump via subprocess.
        """
        try:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            # This requires pg_dump to be installed and accessible
            # Implementing this fully requires system calls, which we might skip for MVP or log warning
            logger.warning("postgres_backup_not_implemented_via_app", hint="use pg_dump externally")
        except Exception as e:
            logger.error("database_backup_failed", error=str(e))

    async def _create_tables(self):
        """Create database tables if they don't exist."""
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS trades (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMPTZ NOT NULL,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    action TEXT NOT NULL,
                    price DOUBLE PRECISION NOT NULL,
                    expected_price DOUBLE PRECISION,
                    slippage DOUBLE PRECISION,
                    size DOUBLE PRECISION NOT NULL,
                    notional DOUBLE PRECISION NOT NULL,
                    fee DOUBLE PRECISION,
                    fee_currency TEXT,
                    pnl DOUBLE PRECISION,
                    pnl_pct DOUBLE PRECISION,
                    reason TEXT,
                    stop_loss DOUBLE PRECISION,
                    take_profit DOUBLE PRECISION
                );

                CREATE TABLE IF NOT EXISTS daily_summary (
                    date DATE PRIMARY KEY,
                    starting_balance DOUBLE PRECISION NOT NULL,
                    ending_balance DOUBLE PRECISION NOT NULL,
                    pnl DOUBLE PRECISION NOT NULL,
                    pnl_pct DOUBLE PRECISION NOT NULL,
                    trades_count INTEGER NOT NULL,
                    wins INTEGER NOT NULL,
                    losses INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS equity_snapshots (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMPTZ NOT NULL,
                    balance DOUBLE PRECISION NOT NULL
                );

                CREATE TABLE IF NOT EXISTS signals_log (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMPTZ NOT NULL,
                    symbol TEXT NOT NULL,
                    price DOUBLE PRECISION NOT NULL,
                    signal TEXT NOT NULL,
                    regime TEXT,
                    reason TEXT,
                    indicators JSONB
                );

                CREATE TABLE IF NOT EXISTS funding_payments (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMPTZ NOT NULL,
                    symbol TEXT NOT NULL,
                    rate DOUBLE PRECISION NOT NULL,
                    payment DOUBLE PRECISION NOT NULL,
                    position_size DOUBLE PRECISION NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp);
                CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
                CREATE INDEX IF NOT EXISTS idx_equity_timestamp ON equity_snapshots(timestamp);
                CREATE INDEX IF NOT EXISTS idx_signals_timestamp ON signals_log(timestamp);
                CREATE INDEX IF NOT EXISTS idx_funding_timestamp ON funding_payments(timestamp);
                """
            )

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
        async with self._pool.acquire() as conn:
            trade_id = await conn.fetchval(
                """
                INSERT INTO trades (
                    timestamp, symbol, side, action, price, expected_price, slippage,
                    size, notional, reason, stop_loss, take_profit, fee, fee_currency
                )
                VALUES ($1, $2, $3, 'OPEN', $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                RETURNING id
                """,
                datetime.now(timezone.utc),
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
                fee,
                fee_currency,
            )
        
        logger.info(
            "trade_logged", action="OPEN", symbol=symbol, side=side, price=price
        )
        return trade_id

    async def get_open_trade_fee(self, symbol: str) -> float:
        async with self._pool.acquire() as conn:
            fee = await conn.fetchval(
                "SELECT fee FROM trades WHERE symbol=$1 AND action='OPEN' ORDER BY timestamp DESC LIMIT 1",
                symbol,
            )
        return float(fee) if fee else 0.0

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
        async with self._pool.acquire() as conn:
            trade_id = await conn.fetchval(
                """
                INSERT INTO trades (
                    timestamp, symbol, side, action, price, size, notional, pnl, pnl_pct, reason,
                    expected_price, slippage, fee, fee_currency
                )
                VALUES ($1, $2, $3, 'CLOSE', $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                RETURNING id
                """,
                datetime.now(timezone.utc),
                symbol,
                side.upper(),
                price,
                size,
                notional,
                pnl,
                pnl_pct,
                reason,
                expected_price,
                slippage,
                fee,
                fee_currency,
            )

        logger.info("trade_logged", action="CLOSE", symbol=symbol, side=side, pnl=pnl)
        return trade_id

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
        # Handle string date to date object conversion if needed
        if isinstance(date, str):
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        else:
            date_obj = date

        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO daily_summary
                (date, starting_balance, ending_balance, pnl, pnl_pct, trades_count, wins, losses)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT (date) DO UPDATE SET
                    starting_balance = EXCLUDED.starting_balance,
                    ending_balance = EXCLUDED.ending_balance,
                    pnl = EXCLUDED.pnl,
                    pnl_pct = EXCLUDED.pnl_pct,
                    trades_count = EXCLUDED.trades_count,
                    wins = EXCLUDED.wins,
                    losses = EXCLUDED.losses
                """,
                date_obj,
                starting_balance,
                ending_balance,
                pnl,
                pnl_pct,
                trades_count,
                wins,
                losses,
            )

    async def get_recent_trades(self, limit: int = 10) -> list:
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM trades ORDER BY timestamp DESC LIMIT $1", limit
            )
        
        # Convert rows (Record objects) to dicts and serialize datetimes
        results = []
        for row in rows:
            d = dict(row)
            if d['timestamp']:
                d['timestamp'] = d['timestamp'].isoformat()
            results.append(d)
        return results

    async def get_last_trade(self, symbol: str) -> Optional[dict]:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM trades WHERE symbol = $1 ORDER BY timestamp DESC LIMIT 1",
                symbol,
            )
        
        if row:
            d = dict(row)
            if d['timestamp']:
                d['timestamp'] = d['timestamp'].isoformat()
            return d
        return None

    async def get_daily_summary(self, date: str) -> Optional[dict]:
        # date is typically YYYY-MM-DD string
        if isinstance(date, str):
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        else:
            date_obj = date
            
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM daily_summary WHERE date = $1", date_obj
            )
        
        if row:
            d = dict(row)
            if d['date']:
                d['date'] = d['date'].isoformat()
            return d
        return None

    async def get_weekly_pnl(self, start_date: str) -> float:
        # Postgres date(timestamp) works similarly to SQLite
        if isinstance(start_date, str):
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        else:
            start_date_obj = start_date

        async with self._pool.acquire() as conn:
            total_pnl = await conn.fetchval(
                "SELECT SUM(pnl) FROM trades WHERE action='CLOSE' AND date(timestamp) >= $1",
                start_date_obj,
            )
        return float(total_pnl) if total_pnl is not None else 0.0

    async def log_equity_snapshot(self, balance: float) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO equity_snapshots (timestamp, balance) VALUES ($1, $2)",
                datetime.now(timezone.utc),
                balance,
            )

    async def get_equity_snapshots(self, limit: int = 200) -> list:
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM equity_snapshots ORDER BY timestamp DESC LIMIT $1", limit
            )
        
        results = []
        for row in rows:
            d = dict(row)
            if d['timestamp']:
                d['timestamp'] = d['timestamp'].isoformat()
            results.append(d)
        return results

    async def log_signal(
        self,
        symbol: str,
        price: float,
        signal: str,
        regime: str,
        reason: str,
        indicators: dict,
    ) -> None:
        # asyncpg handles JSON/JSONB automatically if indicators is passed as a string 
        # OR if we configure a type codec. But simplest is often to pass as string for generic JSONB
        # However, asyncpg can map dict to jsonb automatically.
        # Let's verify: usually we need to json.dumps it if we haven't set up codecs, 
        # OR just pass string. 
        # Safe bet: pass json.dumps(indicators) and let Postgres parse it if column is JSONB.
        # But wait, if column is JSONB, asyncpg usually expects a string unless we set_type_codec.
        # Let's try passing the string representation.
        
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO signals_log (timestamp, symbol, price, signal, regime, reason, indicators)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                datetime.now(timezone.utc),
                symbol,
                price,
                signal,
                regime,
                reason,
                json.dumps(indicators),
            )

    async def log_funding_payment(
        self,
        symbol: str,
        rate: float,
        payment: float,
        position_size: float,
    ) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO funding_payments (timestamp, symbol, rate, payment, position_size)
                VALUES ($1, $2, $3, $4, $5)
                """,
                datetime.now(timezone.utc),
                symbol,
                rate,
                payment,
                position_size,
            )
        logger.info(
            "funding_payment_logged",
            symbol=symbol,
            rate=rate,
            payment=payment,
        )
