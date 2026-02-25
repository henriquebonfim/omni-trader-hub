import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock

from src.api import create_api

@pytest.fixture
def mock_bot():
    bot = MagicMock()
    bot.config.trading.symbol = "BTC/USDT"
    bot.config.strategy.name = "ema_volume"
    bot.exchange.paper_mode = True
    bot.risk.check_circuit_breaker.return_value = False
    bot.ws_manager = None
    bot.database.get_recent_trades = AsyncMock(return_value=[])
    bot.database.get_daily_summary = AsyncMock(return_value={"date": "2023-01-01", "pnl": 0})
    bot.database.get_equity_snapshots = AsyncMock(return_value=[])
    bot.reload_config = AsyncMock()
    return bot

def test_config_validation(mock_bot, monkeypatch):
    monkeypatch.delenv("OMNITRADER_API_KEY", raising=False)
    app = create_api(mock_bot)
    client = TestClient(app)

    # 1. Valid partial update should be accepted
    response = client.put("/api/config", json={"strategy": {"ema_fast": 10}})
    assert response.status_code == 200

    # 2. Invalid field type
    response = client.put("/api/config", json={"strategy": {"ema_fast": "not_an_int"}})
    assert response.status_code == 422

    # 3. Unknown field rejected (extra=forbid)
    response = client.put("/api/config", json={"unknown_field": 123})
    assert response.status_code == 422

    # 4. Constraint violations
    response = client.put("/api/config", json={"exchange": {"leverage": 200}})
    assert response.status_code == 422

    response = client.put("/api/config", json={"risk": {"stop_loss_pct": -5}})
    assert response.status_code == 422
