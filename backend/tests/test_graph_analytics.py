
import pytest

from src.database.memgraph import MemgraphDatabase
from src.intelligence.analytics import GraphAnalytics
from src.intelligence.crisis import CrisisManager


class MockSession:
    def __init__(self, return_value=None):
        self.return_value = return_value

    async def run(self, query, **kwargs):
        class MockResult:
            def __init__(self, rv):
                self.rv = rv
            async def single(self):
                return self.rv
            async def fetch(self, limit):
                return self.rv if isinstance(self.rv, list) else [self.rv]
        return MockResult(self.return_value)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

class MockDriver:
    def __init__(self, session_return_value=None):
        self.session_return_value = session_return_value

    def session(self):
        return MockSession(self.session_return_value)

class MockMemgraph(MemgraphDatabase):
    def __init__(self, session_return_value=None):
        self._driver = MockDriver(session_return_value)
        self.state_store = {}

    async def get_state(self, key):
        return self.state_store.get(key)

    async def set_state(self, key, value, expires_in=None):
        self.state_store[key] = value

@pytest.mark.asyncio
async def test_graph_analytics_sentiment():
    db = MockMemgraph({
        "avg_sentiment": -0.8,
        "mention_count": 5,
        "positive_mentions": 1,
        "negative_mentions": 4
    })
    ga = GraphAnalytics(db)
    
    res = await ga.get_asset_sentiment("BTC")
    assert res["avg_sentiment"] == -0.8
    assert res["mention_count"] == 5

@pytest.mark.asyncio
async def test_graph_analytics_contagion():
    db = MockMemgraph({
        "sector_name": "DeFi",
        "peers_in_distress": 3,
        "sector_distress_level": -0.6
    })
    ga = GraphAnalytics(db)
    
    res = await ga.detect_sector_contagion("UNI")
    assert res["contagion_risk"] is True
    assert res["sector"] == "DeFi"

@pytest.mark.asyncio
async def test_crisis_manager():
    db = MockMemgraph()
    cm = CrisisManager(db)
    
    assert await cm.is_crisis_active() is False
    
    await cm.set_crisis_mode(True, "Test panic")
    assert await cm.is_crisis_active() is True
    
    state = await cm.get_crisis_state()
    assert state["active"] is True
    assert state["reason"] == "Test panic"
    
@pytest.mark.asyncio
async def test_evaluate_automated_crisis():
    db = MockMemgraph()
    cm = CrisisManager(db)
    
    # Not bad enough
    assert await cm.evaluate_automated_crisis(contagion_risk=False, sentiment_level=-0.5) is False
    assert await cm.is_crisis_active() is False
    
    # Bad enough
    assert await cm.evaluate_automated_crisis(contagion_risk=True, sentiment_level=-0.9) is True
    assert await cm.is_crisis_active() is True
