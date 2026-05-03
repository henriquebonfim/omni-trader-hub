from unittest.mock import MagicMock, AsyncMock

import pytest
from fastapi.testclient import TestClient

from src.interfaces.api import create_api
from src.domain.risk import DailyStats

@pytest.fixture
def mock_bot():
    bot = MagicMock()
    bot.config.trading.symbol = "BTC/USDT"
    bot._running = True
    bot.exchange.paper_mode = True
    bot.config.strategy.name = "ema_volume"
    bot.risk.check_circuit_breaker.return_value = False
    bot.ws_manager = MagicMock()
    bot.ws_manager.get_client_count = AsyncMock(return_value=5)
    return bot


@pytest.fixture
def client(mock_bot):
    app = create_api(mock_bot)
    return TestClient(app)



def test_get_metrics_exchange_disconnected(client, mock_bot):
    """Test metrics when exchange is disconnected."""
    mock_bot.exchange.get_ticker = AsyncMock(side_effect=Exception("Connection failed"))

    response = client.get("/api/metrics")
    assert response.status_code == 200

    data = response.json()
    assert data["exchange_status"] == "disconnected"
