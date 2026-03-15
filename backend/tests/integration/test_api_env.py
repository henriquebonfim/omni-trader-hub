from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from src.api import create_api
from src.api.routes.env import mask_value


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

    # Reset the singleton in auth.py for testing
    import src.api.auth as auth

    auth._API_KEY = None
    auth._AUTH_DEV_MODE = False

    app = create_api(mock_bot)
    return TestClient(app)


def test_mask_value():
    assert mask_value("NON_SENSITIVE", "hello") == "hello"
    assert mask_value("BINANCE_SECRET", "1234") == "****"
    assert mask_value("OMNITRADER_API_KEY", "12345678") == "12...78"
    assert mask_value("MEMGRAPH_PASSWORD", "") == ""


def test_get_env(client, monkeypatch, tmp_path):
    env_content = """
BINANCE_API_KEY=public_key
BINANCE_SECRET=super_secret_value
MEMGRAPH_HOST=localhost
NOT_WHITELISTED=hidden
# A comment
MEMGRAPH_PASSWORD="password123"
    """
    env_file = tmp_path / ".env"
    env_file.write_text(env_content)

    # Monkeypatch the ENV_FILE to use our tmp file
    import src.api.routes.env as env_route

    monkeypatch.setattr(env_route, "ENV_FILE", env_file)

    response = client.get("/api/env")
    assert response.status_code == 200
    data = response.json()

    assert "exchange" in data
    assert "database" in data

    assert data["exchange"]["BINANCE_API_KEY"]["value"] == "public_key"
    assert data["exchange"]["BINANCE_API_KEY"]["description"] == "Binance API Key"
    assert data["exchange"]["BINANCE_API_KEY"]["requires_restart"] is True
    assert data["exchange"]["BINANCE_API_KEY"]["masked"] is False

    assert data["exchange"]["BINANCE_SECRET"]["value"] == "su...ue"  # masked
    assert data["exchange"]["BINANCE_SECRET"]["masked"] is True

    assert data["database"]["MEMGRAPH_HOST"]["value"] == "localhost"
    assert (
        data["database"]["MEMGRAPH_PASSWORD"]["value"] == "pa...23"
    )  # masked (also tests quotes stripping)

    # Check that non-whitelisted variable is NOT exposed
    assert "NOT_WHITELISTED" not in str(data)


def test_put_env_atomic_updater(client, monkeypatch, tmp_path):
    env_content = """
BINANCE_API_KEY=old_key
# A comment
NOT_WHITELISTED=hidden
    """
    env_file = tmp_path / ".env"
    env_file.write_text(env_content)

    import src.api.routes.env as env_route

    monkeypatch.setattr(env_route, "ENV_FILE", env_file)

    payload = {
        "updates": {
            "BINANCE_API_KEY": "new_key",
            "MEMGRAPH_HOST": "new_host",
        }
    }

    response = client.put(
        "/api/env", json=payload, headers={"Authorization": "Bearer test-secret"}
    )
    assert response.status_code == 200

    # Verify the file was updated correctly
    new_content = env_file.read_text()
    assert "BINANCE_API_KEY=new_key" in new_content
    assert "MEMGRAPH_HOST=new_host" in new_content
    assert "# A comment" in new_content
    assert "NOT_WHITELISTED=hidden" in new_content


def test_put_env_validation(client, monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("")
    import src.api.routes.env as env_route

    monkeypatch.setattr(env_route, "ENV_FILE", env_file)

    # Test updating a non-whitelisted key
    payload = {"updates": {"NOT_WHITELISTED": "value"}}
    response = client.put(
        "/api/env", json=payload, headers={"Authorization": "Bearer test-secret"}
    )
    assert response.status_code == 400
    assert "not allowed to be modified" in response.json()["detail"]

    # Test invalid value type (raises 422 Unprocessable Entity)
    payload = {"updates": {"BINANCE_API_KEY": 123}}
    response = client.put(
        "/api/env", json=payload, headers={"Authorization": "Bearer test-secret"}
    )
    assert response.status_code == 422
