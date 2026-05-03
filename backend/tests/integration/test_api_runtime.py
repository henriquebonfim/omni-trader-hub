from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from src.interfaces.api import create_api


@pytest.fixture
def mock_bot():
    bot = MagicMock()
    bot.config.trading.symbol = "BTC/USDT"
    return bot


@pytest.fixture
def client(mock_bot):
    app = create_api(mock_bot)
    return TestClient(app)


def test_get_logs_basic(client):
    """Test basic logs endpoint."""
    response = client.get("/api/runtime/logs")
    assert response.status_code == 200

    data = response.json()
    assert "logs" in data
    assert isinstance(data["logs"], list)


def test_get_logs_with_filters(client):
    """Test logs endpoint with time and level filters."""
    response = client.get("/api/runtime/logs?minutes=30&level=ERROR")
    assert response.status_code == 200

    data = response.json()
    assert "logs" in data


def test_get_performance_basic(client):
    """Test basic performance endpoint."""
    response = client.get("/api/runtime/performance")
    assert response.status_code == 200

    data = response.json()
    assert "function_execution_times" in data
    assert "database_query_performance" in data
    assert "websocket_message_rates" in data

    # Check structure
    assert isinstance(data["function_execution_times"], dict)
    assert isinstance(data["database_query_performance"], dict)
    assert isinstance(data["websocket_message_rates"], dict)