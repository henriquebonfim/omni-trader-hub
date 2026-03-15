import asyncio
import pytest
import pytest_asyncio
from datetime import datetime, timezone

from src.database import Database
from src.strategy.selector import StrategySelector
from src.intelligence.regime import MarketRegime

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
    async with db._driver.session() as session:
        await session.run("MATCH (n) DETACH DELETE n")
    yield db
    async with db._driver.session() as session:
        await session.run("MATCH (n) DETACH DELETE n")
    await db.close()

@pytest.mark.asyncio
async def test_selector_with_real_schema(db):
    selector = StrategySelector(database=db)
    selector.min_sample_size = 1 # Lower for testing
    
    regime = MarketRegime.TRENDING
    symbol = "BTC/USDT"
    strat_name = "ema_volume"
    
    # 1. Log a signal
    sig_id = await db.log_signal(
        symbol=symbol,
        price=50000.0,
        signal="BUY",
        regime=regime.value,
        reason="test",
        strategy_name=strat_name
    )
    assert sig_id is not None
    
    # 2. Log a trade open linked to signal
    trade_open_id = await db.log_trade_open(
        symbol=symbol,
        side="long",
        price=50000.0,
        size=1.0,
        notional=50000.0,
        stop_loss=49000.0,
        take_profit=52000.0,
        signal_id=sig_id
    )
    
    # Wait a bit to ensure timestamp diff
    await asyncio.sleep(0.1)
    
    # 3. Log a trade close
    await db.log_trade_close(
        symbol=symbol,
        side="long",
        price=51000.0,
        size=1.0,
        notional=51000.0,
        pnl=1000.0,
        pnl_pct=2.0
    )
    
    # 4. Verify TRIGGERED_BY relationship exists
    async with db._driver.session() as session:
        res = await session.run(
            "MATCH (t:Trade {action: 'OPEN'})-[:TRIGGERED_BY]->(s:Signal) RETURN id(t), id(s)"
        )
        record = await res.single()
        assert record is not None
        
    # 5. Get strategy performance
    scores = await selector.get_strategy_performance(regime)
    assert len(scores) >= 1
    
    ema_score = next((s for s in scores if s.name == strat_name), None)
    assert ema_score is not None
    assert ema_score.sample_size == 1
    assert ema_score.win_rate == 1.0
    assert ema_score.profit_factor == 1000.0 # gross_profit / gross_loss(0) -> gross_profit
