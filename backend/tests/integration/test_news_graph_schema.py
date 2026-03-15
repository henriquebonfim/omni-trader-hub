import pytest
import pytest_asyncio
from datetime import datetime, timezone

from src.database import Database
from src.intelligence.ingestor import NewsIngestor

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
async def test_news_ingestion_and_retrieval_standardized(db):
    ingestor = NewsIngestor(db=db)
    
    event_id = "test-event-123"
    title = "Bitcoin hits new all-time high"
    source = "TestNews"
    published_at = datetime.now(timezone.utc).isoformat()
    sentiment_score = 0.8
    currencies = ["BTC"]
    
    # 1. Create news event via ingestor
    await ingestor.create_news_event(
        event_id=event_id,
        title=title,
        url="http://test.com",
        source=source,
        published_at=published_at,
        sentiment_score=sentiment_score,
        currencies=currencies,
        raw_text="BTC is mooning today!"
    )
    
    # 2. Verify MENTIONS relationship exists with sentiment property
    async with db._driver.session() as session:
        res = await session.run(
            "MATCH (n:NewsEvent {id: $id})-[r:MENTIONS]->(a:Asset {symbol: 'BTC'}) RETURN r.sentiment as sentiment",
            id=event_id
        )
        record = await res.single()
        assert record is not None
        assert record["sentiment"] == sentiment_score
        
    # 3. Test Graph Analytics aggregate query
    from src.intelligence.analytics import GraphAnalytics
    ga = GraphAnalytics(database=db)
    sentiment_data = await ga.get_asset_sentiment("BTC")
    assert sentiment_data["mention_count"] == 1
    assert sentiment_data["avg_sentiment"] == sentiment_score
