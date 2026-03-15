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


def test_trades_protected_when_no_key_set_uses_generated_key(mock_bot, monkeypatch):
    # Ensure OMNITRADER_API_KEY is NOT set
    monkeypatch.delenv("OMNITRADER_API_KEY", raising=False)

    # Reset the singleton in auth.py for testing
    import src.api.auth as auth

    auth._API_KEY = None
    auth._AUTH_DEV_MODE = False

    app = create_api(mock_bot)
    client = TestClient(app)

    # It should be protected, so missing token should be 401
    response = client.get("/api/trades")
    assert response.status_code == 401

    # Using the generated key should succeed
    generated_key = auth.get_api_key()
    response = client.get(
        "/api/trades", headers={"Authorization": f"Bearer {generated_key}"}
    )
    assert response.status_code == 200


def test_trades_protected_when_key_set(mock_bot, monkeypatch):
    # Set the API key
    monkeypatch.setenv("OMNITRADER_API_KEY", "test-secret")

    # Reset the singleton in auth.py for testing
    import src.api.auth as auth

    auth._API_KEY = None
    auth._AUTH_DEV_MODE = False

    app = create_api(mock_bot)
    client = TestClient(app)

    for endpoint in ["/api/trades", "/api/equity"]:
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

    # Reset the singleton in auth.py for testing
    import src.api.auth as auth

    auth._API_KEY = None
    auth._AUTH_DEV_MODE = False

    app = create_api(mock_bot)
    client = TestClient(app)

    # GET /api/status should still be unprotected
    response = client.get("/api/status")
    assert response.status_code == 200

    # GET /api/bot/state should be unprotected
    response = client.get("/api/bot/state")
    assert response.status_code == 200

    # GET /api/config should be unprotected
    response = client.get("/api/config")
    assert response.status_code == 200

    # GET /api/notifications/discord should be unprotected
    response = client.get("/api/notifications/discord")
    assert response.status_code == 200

    # GET /api/notifications/rules should be unprotected
    response = client.get("/api/notifications/rules")
    assert response.status_code == 200

    # GET /api/env should be unprotected
    response = client.get("/api/env")
    assert response.status_code == 200

    # GET /api/metrics should be unprotected
    response = client.get("/api/metrics")
    assert response.status_code == 200

    # GET /api/runtime/logs should be unprotected
    response = client.get("/api/runtime/logs")
    assert response.status_code == 200

    # GET /api/runtime/performance should be unprotected
    response = client.get("/api/runtime/performance")
    assert response.status_code == 200


def test_mutation_routes_protected_when_key_set(mock_bot, monkeypatch):
    monkeypatch.setenv("OMNITRADER_API_KEY", "test-secret")

    # Reset the singleton in auth.py for testing
    import src.api.auth as auth

    auth._API_KEY = None
    auth._AUTH_DEV_MODE = False

    app = create_api(mock_bot)
    client = TestClient(app)

    mutation_endpoints = [
        ("POST", "/api/bot/start", {}),
        ("POST", "/api/bot/stop", {}),
        ("POST", "/api/bot/restart", {}),
        ("POST", "/api/bot/trade/open", {"side": "buy"}),
        ("POST", "/api/bot/trade/close", {}),
        ("PUT", "/api/config", {"strategy": {"name": "ema_volume"}}),
        ("PUT", "/api/notifications/discord", {"enabled": True}),
        (
            "PUT",
            "/api/notifications/rules",
            {
                "circuit_breaker": True,
                "strategy_rotation": True,
                "regime_change": True,
                "pnl_thresholds": True,
                "pnl_warning_pct": 3.0,
                "pnl_critical_pct": 5.0,
            },
        ),
        ("POST", "/api/notifications/discord/test", {}),
    ]

    for method, endpoint, payload in mutation_endpoints:
        # Request without token
        if method == "POST":
            response = client.post(endpoint, json=payload)
        else:
            response = client.put(endpoint, json=payload)
        assert response.status_code == 401, (
            f"{method} {endpoint} should be 401 without token"
        )

        # Request with invalid token
        headers = {"Authorization": "Bearer wrong-token"}
        if method == "POST":
            response = client.post(endpoint, json=payload, headers=headers)
        else:
            response = client.put(endpoint, json=payload, headers=headers)
        assert response.status_code == 401, (
            f"{method} {endpoint} should be 401 with invalid token"
        )

        # Request with valid token (we just expect it NOT to be 401, could be 200 or 500/400 depending on mock)
        headers = {"Authorization": "Bearer test-secret"}
        if method == "POST":
            response = client.post(endpoint, json=payload, headers=headers)
        else:
            response = client.put(endpoint, json=payload, headers=headers)
        assert response.status_code != 401, (
            f"{method} {endpoint} should not be 401 with valid token"
        )
