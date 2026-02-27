from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from src.api import create_api


@pytest.fixture
def mock_bot():
    bot = MagicMock()
    bot.config.trading.symbol = "BTC/USDT:USDT"
    bot.config.strategy.name = "ema_volume"
    bot.exchange.paper_mode = True
    bot.risk.check_circuit_breaker.return_value = False
    bot.ws_manager = None

    # Async mocks
    bot.database.get_recent_trades = AsyncMock(return_value=[])
    bot.database.get_daily_summary = AsyncMock(return_value={"date": "2023-01-01", "pnl": 0})
    bot.database.get_equity_snapshots = AsyncMock(return_value=[])

    return bot

def test_trades_unprotected_when_no_key_set(mock_bot, monkeypatch):
    # Ensure OMNITRADER_API_KEY is NOT set
    monkeypatch.delenv("OMNITRADER_API_KEY", raising=False)

    app = create_api(mock_bot)
    client = TestClient(app)

    response = client.get("/api/trades")
    assert response.status_code == 200

def test_trades_protected_when_key_set(mock_bot, monkeypatch):
    # Set the API key
    monkeypatch.setenv("OMNITRADER_API_KEY", "test-secret")

    app = create_api(mock_bot)
    client = TestClient(app)

    for endpoint in ["/api/trades", "/api/daily-summary/2023-01-01", "/api/equity"]:
        # Request without token
        response = client.get(endpoint)
        # FastAPI HTTPBearer with auto_error=False returns 401 because of our logic in auth.py
        assert response.status_code == 401

        # Request with invalid token
        response = client.get(endpoint, headers={"Authorization": "Bearer wrong-token"})
        assert response.status_code == 401

        # Request with valid token
        response = client.get(endpoint, headers={"Authorization": "Bearer test-secret"})
        assert response.status_code == 200

def test_other_routes_unprotected(mock_bot, monkeypatch):
    # Set the API key
    monkeypatch.setenv("OMNITRADER_API_KEY", "test-secret")

    app = create_api(mock_bot)
    client = TestClient(app)

    # /api/status should still be unprotected (as we only applied to trades.py)
    response = client.get("/api/status")
    assert response.status_code == 200
