import time
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from src.api import create_api
from src.api.routes import indicators


# Reset rate limiter before each test
@pytest.fixture(autouse=True)
def reset_rate_limiter():
    indicators._rate_limits.clear()

@pytest.fixture
def mock_bot():
    bot = MagicMock()
    bot.db = AsyncMock()
    # Mock some candles
    candles = [
        {"timestamp": int(time.time() * 1000) - i*60000, 
         "open": 100 + i, 
         "high": 105 + i, 
         "low": 95 + i, 
         "close": 102 + i, 
         "volume": 1000}
        for i in range(200, 0, -1)
    ]
    bot.db.get_candles.return_value = candles
    return bot

@pytest.fixture
def client(mock_bot):
    app = create_api(bot_instance=mock_bot)
    # mock auth
    app.dependency_overrides[indicators.verify_api_key] = lambda: "valid-key"
    return TestClient(app)

def test_get_indicators(client):
    response = client.get("/api/indicators")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    
    # Check if Momentum Indicators are present (where RSI should be)
    assert "Momentum Indicators" in data
    
    rsi_found = False
    for _group, funcs in data.items():
        for func in funcs:
            if func["name"] == "RSI":
                rsi_found = True
                assert "timeperiod" in [p["name"] for p in func["params"]]
                assert "close" in func["inputs"]
                assert "real" in func["outputs"]
    
    assert rsi_found

def test_compute_indicator_rsi(client):
    payload = {
        "function": "RSI",
        "params": {"timeperiod": 14},
        "symbol": "BTC/USDT",
        "timeframe": "1h",
        "bars": 100
    }
    response = client.post("/api/indicators/compute", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["function"] == "RSI"
    assert data["symbol"] == "BTC/USDT"
    assert data["timeframe"] == "1h"
    assert data["bars"] == 100
    assert "outputs" in data
    assert "real" in data["outputs"]
    assert len(data["outputs"]["real"]) == 100

def test_compute_indicator_unknown_function(client):
    payload = {
        "function": "UNKNOWN_INDICATOR_XYZ",
        "params": {},
        "symbol": "BTC/USDT",
        "timeframe": "1h",
        "bars": 100
    }
    response = client.post("/api/indicators/compute", json=payload)
    assert response.status_code == 400
    assert "Unknown or unsupported TA-Lib function" in response.json()["detail"]

def test_compute_indicator_rate_limit(client):
    payload = {
        "function": "RSI",
        "params": {"timeperiod": 14},
        "symbol": "BTC/USDT",
        "timeframe": "1h",
        "bars": 100
    }
    
    # Hit the limit (10 requests)
    for _ in range(10):
        response = client.post("/api/indicators/compute", json=payload)
        assert response.status_code == 200
        
    # 11th request should fail with 429
    response = client.post("/api/indicators/compute", json=payload)
    assert response.status_code == 429
    assert "Too many requests" in response.json()["detail"]
