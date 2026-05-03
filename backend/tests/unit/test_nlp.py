from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.domain.intelligence.nlp import OllamaNLP


@pytest.fixture
def nlp():
    return OllamaNLP()


@pytest.mark.asyncio
async def test_extract_entities_success(nlp):
    news_text = "Bitcoin rallies as DeFi sees massive adoption."
    mock_response = {
        "response": '{"assets": ["BTC"], "sectors": ["DeFi"], "sentiment": 0.8, "impact": 0.5}'
    }

    with patch.object(nlp.client, "post", new_callable=AsyncMock) as mock_post:
        mock_post_res = AsyncMock()
        mock_post_res.raise_for_status = MagicMock()
        mock_post_res.json.return_value = mock_response
        mock_post.return_value = mock_post_res

        entities = await nlp.extract_entities(news_text)

        assert "BTC" in entities["assets"]
        assert "DeFi" in entities["sectors"]
        assert entities["sentiment"] == 0.8
        assert entities["impact"] == 0.5


@pytest.mark.asyncio
async def test_extract_entities_failure(nlp):
    news_text = "Market crashes."

    with patch.object(nlp.client, "post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.RequestError("Timeout")

        entities = await nlp.extract_entities(news_text)

        assert entities == {}


@pytest.mark.asyncio
async def test_enrich_news_event(nlp):
    mock_db = AsyncMock()
    mock_session = AsyncMock()
    mock_db._driver.session = MagicMock()
    mock_db._driver.session.return_value.__aenter__.return_value = mock_session

    mock_record = {
        "raw_text": "Ethereum upgrades to proof of stake.",
        "fallback_sentiment": 0.2,
    }

    # Setup mock result to be an asynchronous iterable
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

    mock_session.run.return_value = MockResult([mock_record])

    mock_response = {
        "response": '{"assets": ["ETH"], "sectors": ["L1"], "sentiment": 0.9, "impact": 0.6}'
    }

    with patch.object(nlp.client, "post", new_callable=AsyncMock) as mock_post:
        mock_post_res = AsyncMock()
        mock_post_res.raise_for_status = MagicMock()
        mock_post_res.json.return_value = mock_response
        mock_post.return_value = mock_post_res

        await nlp.enrich_news_event("event_123", mock_db)

        # verify session.run was called multiple times
        assert mock_session.run.call_count == 4  # fetch, update, asset, sector
