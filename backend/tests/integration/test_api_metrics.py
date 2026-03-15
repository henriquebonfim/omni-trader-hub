from unittest.mock import MagicMock, AsyncMock

import pytest
from fastapi.testclient import TestClient

from src.api import create_api


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


def test_get_metrics_basic(client, mock_bot):
    """Test basic metrics endpoint returns expected structure."""
    # Mock the risk daily stats
    mock_stats = MagicMock()
    mock_stats.win_rate = 0.65
    mock_stats.realized_pnl = 123.45
    mock_stats.trades_count = 20
    mock_bot.risk.get_daily_stats.return_value = mock_stats

    # Mock exchange ticker call
    mock_bot.exchange.get_ticker = AsyncMock(return_value={"last": 50000})

    response = client.get("/api/metrics")
    assert response.status_code == 200

    data = response.json()
    assert "win_rate" in data
    assert "total_pnl" in data
    assert "cpu_usage_pct" in data
    assert "memory_usage_mb" in data
    assert "exchange_status" in data
    assert "error_count" in data
    assert "queue_depths" in data

    # Check values
    assert data["win_rate"] == 0.65
    assert data["total_pnl"] == 123.45
    assert data["total_trades"] == 20
    assert data["exchange_status"] == "connected"
    assert isinstance(data["exchange_latency_ms"], float)


def test_get_metrics_no_bot_data(client):
    """Test metrics with minimal bot data."""
    response = client.get("/api/metrics")
    assert response.status_code == 200

    data = response.json()
    assert data["win_rate"] == 0.0
    assert data["total_pnl"] == 0.0
    assert data["total_trades"] == 0
    assert data["exchange_status"] == "unknown"


def test_get_metrics_exchange_disconnected(client, mock_bot):
    """Test metrics when exchange is disconnected."""
    mock_bot.exchange.get_ticker = AsyncMock(side_effect=Exception("Connection failed"))

    response = client.get("/api/metrics")
    assert response.status_code == 200

    data = response.json()
    assert data["exchange_status"] == "disconnected"