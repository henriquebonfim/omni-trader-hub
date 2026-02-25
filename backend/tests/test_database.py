import asyncio
from datetime import datetime

import json
from datetime import datetime, timezone

import pytest
import pytest_asyncio

from src.database import Database


@pytest_asyncio.fixture
async def db():
    # Use :memory: for testing
    db = Database(":memory:")
    await db.connect()
    yield db
    await db.close()

@pytest.mark.asyncio
async def test_connect_and_tables(db):
    # db fixture already calls connect() which calls _create_tables and _migrate_tables
    # We can verify tables exist by querying sqlite_master
    async with db._connection.execute("SELECT name FROM sqlite_master WHERE type='table'") as cursor:
        tables = [row[0] for row in await cursor.fetchall()]

    assert "trades" in tables
    assert "daily_summary" in tables
    assert "equity_snapshots" in tables
    assert "signals_log" in tables

    async with db._connection.execute("SELECT name FROM sqlite_master WHERE type='index'") as cursor:
        indexes = [row[0] for row in await cursor.fetchall()]

    assert "idx_trades_timestamp" in indexes
    assert "idx_trades_symbol" in indexes
    assert "idx_equity_timestamp" in indexes
    assert "idx_signals_timestamp" in indexes

@pytest.mark.asyncio
async def test_log_trade_open_and_get_recent(db):
    trade_id = await db.log_trade_open(
        symbol="BTC/USDT",
        side="LONG",
        price=50000.0,
        size=0.1,
        notional=5000.0,
        stop_loss=49000.0,
        take_profit=55000.0,
        reason="test_signal",
        expected_price=49950.0,
        slippage=50.0
    )
    assert trade_id == 1

    trades = await db.get_recent_trades(limit=1)
    assert len(trades) == 1
    trade = trades[0]
    assert trade["symbol"] == "BTC/USDT"
    assert trade["side"] == "LONG"
    assert trade["action"] == "OPEN"
    assert trade["price"] == 50000.0
    assert trade["expected_price"] == 49950.0
    assert trade["slippage"] == 50.0
    assert trade["size"] == 0.1
    assert trade["notional"] == 5000.0
    assert trade["stop_loss"] == 49000.0
    assert trade["take_profit"] == 55000.0
    assert trade["reason"] == "test_signal"

@pytest.mark.asyncio
async def test_log_trade_close(db):
    trade_id = await db.log_trade_close(
        symbol="BTC/USDT",
        side="LONG",
        price=51000.0,
        size=0.1,
        notional=5100.0,
        pnl=100.0,
        pnl_pct=2.0,
        reason="take_profit"
    )
    assert trade_id == 1

    trades = await db.get_recent_trades(limit=1)
    assert len(trades) == 1
    trade = trades[0]
    assert trade["symbol"] == "BTC/USDT"
    assert trade["action"] == "CLOSE"
    assert trade["price"] == 51000.0
    assert trade["pnl"] == 100.0
    assert trade["pnl_pct"] == 2.0

@pytest.mark.asyncio
async def test_get_last_trade(db):
    await db.log_trade_open("BTC/USDT", "LONG", 50000.0, 0.1, 5000.0, None, None)
    await asyncio.sleep(0.01) # Ensure timestamp difference
    await db.log_trade_open("ETH/USDT", "SHORT", 3000.0, 1.0, 3000.0, None, None)

    last_btc = await db.get_last_trade("BTC/USDT")
    assert last_btc["symbol"] == "BTC/USDT"

    last_eth = await db.get_last_trade("ETH/USDT")
    assert last_eth["symbol"] == "ETH/USDT"

    # Test None case
    last_none = await db.get_last_trade("SOL/USDT")
    assert last_none is None

@pytest.mark.asyncio
async def test_daily_summary(db):
    today = datetime.utcnow().date().isoformat()
    await db.save_daily_summary(
        date=today,
        starting_balance=10000.0,
        ending_balance=10500.0,
        pnl=500.0,
        pnl_pct=5.0,
        trades_count=5,
        wins=3,
        losses=2
    )

    summary = await db.get_daily_summary(today)
    assert summary["date"] == today
    assert summary["starting_balance"] == 10000.0
    assert summary["pnl"] == 500.0
    assert summary["trades_count"] == 5

    # Test update (INSERT OR REPLACE)
    await db.save_daily_summary(
        date=today,
        starting_balance=10000.0,
        ending_balance=10600.0,
        pnl=600.0,
        pnl_pct=6.0,
        trades_count=6,
        wins=4,
        losses=2
    )

    summary = await db.get_daily_summary(today)
    assert summary["ending_balance"] == 10600.0
    assert summary["trades_count"] == 6

    # Test None case for a non-existent date
    summary_none = await db.get_daily_summary("1970-01-01")
    assert summary_none is None

@pytest.mark.asyncio
async def test_equity_snapshots(db):
    await db.log_equity_snapshot(10000.0)
    await db.log_equity_snapshot(10100.0)

    snapshots = await db.get_equity_snapshots(limit=10)
    assert len(snapshots) == 2
    # Ordered by timestamp DESC
    assert snapshots[0]["balance"] == 10100.0
    assert snapshots[1]["balance"] == 10000.0

@pytest.mark.asyncio
async def test_log_signal(db):
    indicators = {"rsi": 75.0, "ema_cross": True}
    await db.log_signal(
        symbol="BTC/USDT",
        price=52000.0,
        signal="SELL",
        reason="rsi_overbought",
        indicators=indicators
    )

    async with db._connection.execute("SELECT * FROM signals_log") as cursor:
        row = await cursor.fetchone()
        columns = [description[0] for description in cursor.description]
        signal = dict(zip(columns, row, strict=False))

    assert signal["symbol"] == "BTC/USDT"
    assert signal["price"] == 52000.0
    assert signal["signal"] == "SELL"
    assert json.loads(signal["indicators"]) == indicators
