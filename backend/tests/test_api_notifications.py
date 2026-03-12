from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
import yaml
from fastapi.testclient import TestClient

from src.api import create_api


@pytest.fixture
def mock_bot():
    bot = MagicMock()
    bot.config.trading.symbol = "BTC/USDT:USDT"
    bot.config.strategy.name = "ema_volume"
    bot.config.exchange.paper_mode = True
    bot.config.notifications.alert_rules = {}
    bot.risk.check_circuit_breaker.return_value = False
    bot.ws_manager = None
    bot._running = True

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
    bot.exchange.fetch_position = AsyncMock(return_value=mock_position)
    bot.exchange.fetch_balance = AsyncMock(return_value=1000)

    bot.notifier = MagicMock()
    bot.notifier.send = AsyncMock(return_value=True)
    bot.notifier.enabled = True
    bot.notifier.webhook_url = "https://discord.com/api/webhooks/test"

    return bot


@pytest.fixture
def client(mock_bot, monkeypatch):
    monkeypatch.setenv("OMNITRADER_API_KEY", "test-secret")

    import src.api.auth as auth

    auth._API_KEY = None
    auth._AUTH_DEV_MODE = False

    app = create_api(mock_bot)
    return TestClient(app)


def test_get_notification_rules_defaults(client):
    response = client.get("/api/notifications/rules")
    assert response.status_code == 200
    data = response.json()

    assert data["circuit_breaker"] is True
    assert data["strategy_rotation"] is True
    assert data["regime_change"] is True
    assert data["pnl_thresholds"] is True
    assert data["pnl_warning_pct"] == 3.0
    assert data["pnl_critical_pct"] == 5.0


def test_update_notification_rules_persists_to_config(
    client, mock_bot, monkeypatch, tmp_path
):
    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml.safe_dump({"notifications": {"enabled": True}}))

    import src.api.routes.notifications as notifications_route

    monkeypatch.setattr(notifications_route, "_CONFIG_PATH", Path(config_file))

    payload = {
        "circuit_breaker": True,
        "strategy_rotation": False,
        "regime_change": True,
        "pnl_thresholds": True,
        "pnl_warning_pct": 2.5,
        "pnl_critical_pct": 4.0,
    }

    response = client.put(
        "/api/notifications/rules",
        json=payload,
        headers={"Authorization": "Bearer test-secret"},
    )
    assert response.status_code == 200
    assert response.json()["ok"] is True

    saved = yaml.safe_load(config_file.read_text())
    assert saved["notifications"]["alert_rules"]["strategy_rotation"] is False
    assert saved["notifications"]["alert_rules"]["pnl_warning_pct"] == 2.5
    assert saved["notifications"]["alert_rules"]["pnl_critical_pct"] == 4.0

    mock_bot.reload_config.assert_awaited_once()
