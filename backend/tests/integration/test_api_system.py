from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from src.interfaces.api import create_api


@pytest.fixture
def mock_bot():
    bot = MagicMock()
    bot.config.trading.symbol = "BTC/USDT:USDT"
    bot.config.strategy.name = "ema_volume"
    bot.exchange.paper_mode = True
    bot.risk.check_circuit_breaker.return_value = False
    bot.ws_manager = None
    bot._running = True

    # Async mocks
    bot.database.get_recent_trades = AsyncMock(return_value=[])
    bot.database.get_daily_summary = AsyncMock(
        return_value={"date": "2023-01-01", "pnl": 0}
    )
    bot.database.get_equity_snapshots = AsyncMock(return_value=[])
    bot.start = AsyncMock()
    bot.stop = AsyncMock()
    bot.reload_config = AsyncMock()
    bot._open_position = AsyncMock()
    bot._close_position = AsyncMock()

    mock_position = MagicMock()
    mock_position.is_open = False
    bot.exchange.get_position = AsyncMock(return_value=mock_position)
    bot.exchange.get_balance = AsyncMock(return_value=1000)

    bot.notifier = MagicMock()
    bot.notifier.send = AsyncMock(return_value=True)
    bot.notifier.enabled = True
    bot.notifier.webhook_url = "https://discord.com/api/webhooks/test"

    return bot


@pytest.fixture
def client(mock_bot, monkeypatch):
    monkeypatch.setenv("OMNITRADER_API_KEY", "test-secret")

    # Reset the singleton in auth.py for testing
    import src.interfaces.api.auth as auth

    auth._API_KEY = None
    auth._AUTH_DEV_MODE = False

    app = create_api(mock_bot)
    return TestClient(app)


def test_restart_system_no_open_positions(client, mock_bot, monkeypatch):
    mock_position = MagicMock()
    mock_position.is_open = False
    mock_bot.exchange.get_position = AsyncMock(return_value=mock_position)

    # Mock os.kill to prevent actual killing of the test runner
    mock_kill = MagicMock()
    monkeypatch.setattr("os.kill", mock_kill)

    response = client.post(
        "/api/system/restart",
        json={"force": False, "confirm": True},
        headers={"Authorization": "Bearer test-secret"},
    )
    assert response.status_code == 200
    assert response.json()["ok"] is True

    # Check that bot was stopped
    mock_bot.stop.assert_called_once()


def test_restart_system_with_open_positions_no_force(client, mock_bot, monkeypatch):
    mock_position = MagicMock()
    mock_position.is_open = True
    mock_bot.exchange.get_position = AsyncMock(return_value=mock_position)

    mock_kill = MagicMock()
    monkeypatch.setattr("os.kill", mock_kill)

    response = client.post(
        "/api/system/restart",
        json={"force": False, "confirm": True},
        headers={"Authorization": "Bearer test-secret"},
    )
    assert response.status_code == 400
    assert "Cannot restart system with open positions" in response.json()["detail"]

    # Check that bot was not stopped
    mock_bot.stop.assert_not_called()
    mock_kill.assert_not_called()


def test_restart_system_with_open_positions_with_force(client, mock_bot, monkeypatch):
    mock_position = MagicMock()
    mock_position.is_open = True
    mock_bot.exchange.get_position = AsyncMock(return_value=mock_position)

    mock_kill = MagicMock()
    monkeypatch.setattr("os.kill", mock_kill)

    response = client.post(
        "/api/system/restart",
        json={"force": True, "confirm": True},
        headers={"Authorization": "Bearer test-secret"},
    )
    assert response.status_code == 200
    assert response.json()["ok"] is True

    # Check that bot was stopped despite open positions
    mock_bot.stop.assert_called_once()


def test_restart_system_requires_confirm(client, mock_bot):
    response = client.post(
        "/api/system/restart",
        json={"force": False},
        headers={"Authorization": "Bearer test-secret"},
    )
    assert response.status_code == 400
    assert "confirm=true" in response.json()["detail"]
    mock_bot.stop.assert_not_called()


def test_bot_restart_blocks_open_positions_without_force(client, mock_bot):
    mock_position = MagicMock()
    mock_position.is_open = True
    mock_bot.exchange.get_position = AsyncMock(return_value=mock_position)

    response = client.post(
        "/api/bot/restart",
        json={"confirm": True, "force": False},
        headers={"Authorization": "Bearer test-secret"},
    )

    assert response.status_code == 400
    assert "Cannot restart bot with open positions" in response.json()["detail"]
    mock_bot.stop.assert_not_called()
