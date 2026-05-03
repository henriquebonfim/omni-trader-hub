import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock

from src.interfaces.api import create_api

@pytest.fixture
def mock_bot():
    bot = MagicMock()
    bot.database = AsyncMock()
    bot.database.get_recent_signals = AsyncMock(return_value=[
        {"symbol": "BTC/USDT", "signal": "BUY", "timestamp": 1710000000000}
    ])
    return bot

@pytest.fixture
def client(mock_bot):
    app = create_api(mock_bot)
    return TestClient(app)

def test_get_signals_authorized(client, monkeypatch):
    monkeypatch.setenv("OMNITRADER_API_KEY", "test-secret")
    
    # We need to re-initialize auth or bypass it
    import src.interfaces.api.auth as auth
    auth._API_KEY = "test-secret"
    auth._AUTH_DEV_MODE = False

    response = client.get(
        "/api/signals?limit=5",
        headers={"Authorization": "Bearer test-secret"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "signals" in data
    assert len(data["signals"]) == 1
    assert data["signals"][0]["symbol"] == "BTC/USDT"

def test_get_signals_unauthorized(client):
    response = client.get("/api/signals")
    assert response.status_code == 401
