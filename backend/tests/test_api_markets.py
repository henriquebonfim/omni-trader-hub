import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from src.api import create_api


@pytest.fixture
def mock_markets_data():
    return [
        {
            "symbol": "BTC/USDT",
            "base": "BTC",
            "quote": "USDT",
            "min_size": 0.001,
            "tick_size": 0.1,
            "volume_24h": 1000000.0,
            "last_price": 60000.0,
            "status": "active"
        },
        {
            "symbol": "ETH/USDT",
            "base": "ETH",
            "quote": "USDT",
            "min_size": 0.01,
            "tick_size": 0.01,
            "volume_24h": 500000.0,
            "last_price": 3000.0,
            "status": "active"
        },
        {
            "symbol": "DOGE/BUSD",
            "base": "DOGE",
            "quote": "BUSD",
            "min_size": 10.0,
            "tick_size": 0.0001,
            "volume_24h": 50000.0,
            "last_price": 0.1,
            "status": "active"
        }
    ]

@pytest.fixture
def mock_bot(mock_markets_data):
    bot = MagicMock()
    bot.exchange = MagicMock()
    bot.exchange.fetch_markets = AsyncMock(return_value=mock_markets_data)
    
    bot.redis = MagicMock()
    bot.redis.get = AsyncMock(return_value=None)
    bot.redis.set = AsyncMock()
    return bot

@pytest.fixture
def api_client(mock_bot):
    app = create_api(bot_instance=mock_bot)
    return TestClient(app)

def test_get_markets(api_client, mock_bot):
    response = api_client.get("/api/markets")
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 3
    # Check sorted by volume desc
    assert data[0]["symbol"] == "BTC/USDT"
    assert data[1]["symbol"] == "ETH/USDT"
    assert data[2]["symbol"] == "DOGE/BUSD"
    
    mock_bot.exchange.fetch_markets.assert_called_once()
    mock_bot.redis.set.assert_called_once()
    args, kwargs = mock_bot.redis.set.call_args
    assert args[0] == "api:markets:all"
    assert kwargs["ex"] == 300

def test_get_markets_filter_search(api_client, mock_bot, mock_markets_data):
    mock_bot.redis.get = AsyncMock(return_value=json.dumps(mock_markets_data).encode("utf-8"))
    
    response = api_client.get("/api/markets?search=ETH")
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 1
    assert data[0]["symbol"] == "ETH/USDT"

def test_get_markets_filter_quote(api_client, mock_bot, mock_markets_data):
    mock_bot.redis.get = AsyncMock(return_value=json.dumps(mock_markets_data).encode("utf-8"))
    
    response = api_client.get("/api/markets?quote=BUSD")
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 1
    assert data[0]["symbol"] == "DOGE/BUSD"

def test_get_markets_filter_min_volume(api_client, mock_bot, mock_markets_data):
    mock_bot.redis.get = AsyncMock(return_value=json.dumps(mock_markets_data).encode("utf-8"))
    
    response = api_client.get("/api/markets?min_volume=600000")
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 1
    assert data[0]["symbol"] == "BTC/USDT"
