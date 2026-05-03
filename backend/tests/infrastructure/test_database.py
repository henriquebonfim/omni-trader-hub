import asyncio
import json
from datetime import datetime, timezone

import pytest
import pytest_asyncio

from src.infrastructure.database import Database


def is_memgraph_available() -> bool:
    """Check if Memgraph is available for integration tests."""
    try:
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver("bolt://memgraph:7687", auth=None)
        with driver.session() as session:
            session.run("RETURN 1").single()
        driver.close()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not is_memgraph_available(), reason="Memgraph not available (integration test)"
)


@pytest_asyncio.fixture
async def db():
    db = Database(host="memgraph", port=7687)
    await db.connect()

    # Keep tests isolated in shared integration Memgraph.
    async with db._driver.session() as session:
        await session.run("MATCH (n) DETACH DELETE n")

    yield db

    async with db._driver.session() as session:
        await session.run("MATCH (n) DETACH DELETE n")
    await db.close()


@pytest.mark.asyncio
async def test_connect_and_tables(db):
    assert db._driver is not None

    async with db._driver.session() as session:
        result = await session.run("RETURN 1 as connected")
        record = await result.single()

    assert record is not None
    assert record["connected"] == 1


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
        slippage=50.0,
    )
    assert isinstance(trade_id, int)
    assert trade_id >= 0

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
        reason="take_profit",
        expected_price=50950.0,
        slippage=-50.0,
    )
    assert isinstance(trade_id, int)
    assert trade_id >= 0

    trades = await db.get_recent_trades(limit=1)
    assert len(trades) == 1
    trade = trades[0]
    assert trade["symbol"] == "BTC/USDT"
    assert trade["action"] == "CLOSE"
    assert trade["price"] == 51000.0
    assert trade["pnl"] == 100.0
    assert trade["pnl_pct"] == 2.0
    assert trade["expected_price"] == 50950.0
    assert trade["slippage"] == -50.0


@pytest.mark.asyncio
async def test_get_last_trade(db):
    await db.log_trade_open("BTC/USDT", "LONG", 50000.0, 0.1, 5000.0, None, None)
    await asyncio.sleep(0.01)
    await db.log_trade_open("ETH/USDT", "SHORT", 3000.0, 1.0, 3000.0, None, None)

    last_btc = await db.get_last_trade("BTC/USDT")
    assert last_btc["symbol"] == "BTC/USDT"

    last_eth = await db.get_last_trade("ETH/USDT")
    assert last_eth["symbol"] == "ETH/USDT"

    last_none = await db.get_last_trade("SOL/USDT")
    assert last_none is None


@pytest.mark.asyncio
async def test_daily_summary(db):
    today = datetime.now(timezone.utc).date().isoformat()
    await db.save_daily_summary(
        date=today,
        starting_balance=10000.0,
        ending_balance=10500.0,
        pnl=500.0,
        pnl_pct=5.0,
        trades_count=5,
        wins=3,
        losses=2,
    )

    summary = await db.get_daily_summary(today)
    assert summary["date"] == today
    assert summary["starting_balance"] == 10000.0
    assert summary["pnl"] == 500.0
    assert summary["trades_count"] == 5

    await db.save_daily_summary(
        date=today,
        starting_balance=10000.0,
        ending_balance=10600.0,
        pnl=600.0,
        pnl_pct=6.0,
        trades_count=6,
        wins=4,
        losses=2,
    )

    summary = await db.get_daily_summary(today)
    assert summary["ending_balance"] == 10600.0
    assert summary["trades_count"] == 6

    summary_none = await db.get_daily_summary("1970-01-01")
    assert summary_none is None


@pytest.mark.asyncio
async def test_equity_snapshots(db):
    await db.log_equity_snapshot(10000.0)
    await asyncio.sleep(0.01)
    await db.log_equity_snapshot(10100.0)

    snapshots = await db.get_equity_snapshots(limit=10)
    assert len(snapshots) == 2
    assert snapshots[0]["balance"] == 10100.0
    assert snapshots[1]["balance"] == 10000.0


@pytest.mark.asyncio
async def test_log_signal(db):
    indicators = {"rsi": 75.0, "ema_cross": True}
    await db.log_signal(
        symbol="BTC/USDT",
        price=52000.0,
        signal="SELL",
        regime="bull",
        reason="rsi_overbought",
        indicators=indicators,
    )

    async with db._driver.session() as session:
        result = await session.run(
            """
            MATCH (s:Signal)
            RETURN s.symbol as symbol, s.price as price, s.signal as signal, s.indicators as indicators
            ORDER BY s.timestamp DESC
            LIMIT 1
            """
        )
        record = await result.single()

    assert record is not None
    assert record["symbol"] == "BTC/USDT"
    assert record["price"] == 52000.0
    assert record["signal"] == "SELL"
    assert json.loads(record["indicators"]) == indicators


@pytest.mark.asyncio
async def test_get_recent_signals(db):
    await db.log_signal("BTC/USDT", 50000.0, "BUY", "trending", "test1", "ema_volume")
    await asyncio.sleep(0.01)
    await db.log_signal("ETH/USDT", 3000.0, "SELL", "ranging", "test2", "ema_volume")

    signals = await db.get_recent_signals(limit=10)
    assert len(signals) == 2
    assert signals[0]["symbol"] == "ETH/USDT"
    assert signals[1]["symbol"] == "BTC/USDT"

    btc_signals = await db.get_recent_signals(symbol="BTC/USDT")
    assert len(btc_signals) == 1
    assert btc_signals[0]["symbol"] == "BTC/USDT"
