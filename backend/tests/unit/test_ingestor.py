from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.domain.intelligence.ingestor import NewsIngestor


@pytest.fixture
def ingestor():
    db = AsyncMock()
    return NewsIngestor(db=db, cryptopanic_api_key="test_key")


@pytest.mark.asyncio
async def test_generate_id(ingestor):
    url = "https://example.com"
    title = "Example News"
    event_id = ingestor._generate_id(url, title)
    assert len(event_id) == 16
    assert isinstance(event_id, str)


@pytest.mark.asyncio
async def test_is_duplicate(ingestor):
    mock_session = AsyncMock()
    ingestor.db._driver.session = MagicMock()
    ingestor.db._driver.session.return_value.__aenter__.return_value = mock_session

    class MockResult:
        def __init__(self, records):
            self.records = records

        def __aiter__(self):
            self.idx = 0
            return self

        async def __anext__(self):
            if self.idx < len(self.records):
                item = self.records[self.idx]
                self.idx += 1
                return item
            else:
                raise StopAsyncIteration

    # Test True
    mock_session.run.return_value = MockResult([{"id": "test_id"}])
    assert await ingestor.is_duplicate("test_id") is True

    # Test False
    mock_session.run.return_value = MockResult([])
    assert await ingestor.is_duplicate("new_id") is False


@pytest.mark.asyncio
async def test_fetch_cryptopanic(ingestor):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "results": [
            {
                "url": "https://test.com/news/1",
                "title": "Bitcoin reaches new high",
                "source": {"domain": "test.com"},
                "published_at": "2023-10-01T12:00:00Z",
                "votes": {"positive": 100, "negative": 10},
                "currencies": [{"code": "BTC"}],
            }
        ]
    }

    with patch.object(ingestor, "_fetch_url", return_value=mock_response):
        with patch.object(ingestor, "is_duplicate", return_value=False):
            with patch.object(ingestor, "create_news_event") as mock_create:
                event_ids = await ingestor.fetch_cryptopanic()
                assert len(event_ids) == 1
                mock_create.assert_called_once()
                args, kwargs = mock_create.call_args
                assert kwargs["title"] == "Bitcoin reaches new high"
                assert kwargs["sentiment_score"] == 0.9  # (100-10)/100
                assert "BTC" in kwargs["currencies"]


@pytest.mark.asyncio
async def test_fetch_fear_greed(ingestor):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [{"value": "75", "timestamp": "1633046400"}]
    }

    mock_session = AsyncMock()
    ingestor.db._driver.session = MagicMock()
    ingestor.db._driver.session.return_value.__aenter__.return_value = mock_session

    with patch.object(ingestor, "_fetch_url", return_value=mock_response):
        await ingestor.fetch_fear_greed()

        mock_session.run.assert_called_once()
        args, kwargs = mock_session.run.call_args
        assert kwargs["value"] == 75
        assert kwargs["timestamp"] == 1633046400000


@pytest.mark.asyncio
async def test_fetch_rss_feeds(ingestor):
    mock_feed = MagicMock()
    mock_feed.entries = [
        {
            "link": "https://coindesk.com/article/1",
            "title": "Ethereum upgrade successful",
            "published": "2023-10-01T12:00:00Z",
            "summary": "Ethereum has completed its upgrade.",
        }
    ]

    with patch("feedparser.parse", return_value=mock_feed):
        with patch.object(ingestor, "is_duplicate", return_value=False):
            with patch.object(ingestor, "create_news_event") as mock_create:
                event_ids = await ingestor.fetch_rss_feeds()

                # We have 3 feeds
                assert len(event_ids) == 3
                assert mock_create.call_count == 3

                args, kwargs = mock_create.call_args
                assert kwargs["title"] == "Ethereum upgrade successful"
                assert "ETH" in kwargs["currencies"] or len(kwargs["currencies"]) == 0


@pytest.mark.asyncio
async def test_prune_old_news(ingestor):
    mock_session = AsyncMock()
    ingestor.db._driver.session = MagicMock()
    ingestor.db._driver.session.return_value.__aenter__.return_value = mock_session

    class MockResult:
        def __init__(self, records):
            self.records = records

        def __aiter__(self):
            self.idx = 0
            return self

        async def __anext__(self):
            if self.idx < len(self.records):
                item = self.records[self.idx]
                self.idx += 1
                return item
            else:
                raise StopAsyncIteration

    mock_session.run.return_value = MockResult([{"deleted_count": 5}])

    await ingestor.prune_old_news(days=7)
    mock_session.run.assert_called_once()


@pytest.mark.asyncio
async def test_create_news_event_uses_impacts_relationship(ingestor):
    mock_session = AsyncMock()
    ingestor.db._driver.session = MagicMock()
    ingestor.db._driver.session.return_value.__aenter__.return_value = mock_session

    await ingestor.create_news_event(
        event_id="event123",
        title="BTC volatility spike",
        url="https://example.com/news",
        source="example",
        published_at="2024-01-01T00:00:00Z",
        sentiment_score=0.1,
        raw_text="BTC volatility spike",
        currencies=["BTC", "ETH"],
    )

    queries = [call.args[0] for call in mock_session.run.call_args_list]
    assert any("CREATE (n:NewsEvent" in q for q in queries)
    assert any("MERGE (n)-[:IMPACTS" in q for q in queries)
