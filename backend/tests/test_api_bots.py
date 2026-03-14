from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from src.api import create_api
from src.bot_manager import BotManager
from src.config import Config
from src.main import OmniTrader


@pytest.fixture
def mock_bot_manager():
    manager = BotManager(database=AsyncMock())

    # Setup global config mockup so create_bot works
    manager._global_config = Config(
        {
            "trading": {
                "symbol": "BTC/USDT",
                "timeframe": "1h",
                "position_size_pct": 5.0,
            },
            "exchange": {"paper_mode": True, "leverage": 10},
            "risk": {
                "stop_loss_pct": 2.0,
                "take_profit_pct": 4.0,
                "max_daily_loss_pct": 10.0,
                "max_positions": 1,
            },
            "strategy": {"name": "ema_volume"},
        }
    )

    bot1 = AsyncMock(spec=OmniTrader)
    bot1.bot_id = "bot1"
    bot1.config = Config(
        {
            "trading": {"symbol": "BTC/USDT", "timeframe": "1h"},
            "exchange": {"paper_mode": True, "leverage": 10},
            "strategy": {"name": "ema_volume"},
        }
    )
    bot1._running = True
    bot1.risk = AsyncMock()

    bot1.risk.check_circuit_breaker = lambda: False
    bot1.ws_manager = None

    bot1.risk.daily_stats.realized_pnl = 100.0
    bot1.risk.daily_stats.pnl_pct = 1.0
    bot1.risk.daily_stats.trades_count = 2
    bot1.risk.daily_stats.wins = 1
    bot1.risk.daily_stats.losses = 1

    bot1.get_summary = lambda: {
        "id": "bot1",
        "symbol": "BTC/USDT",
        "timeframe": "1h",
        "running": True,
        "strategy": "ema_volume",
        "market_regime": "trending",
        "daily_pnl": 100.0,
        "daily_pnl_pct": 1.0,
        "total_balance": 10000.0,
        "leverage": 10,
        "paper_mode": True,
        "uptime_seconds": 3600,
        "circuit_breaker_active": False,
        "position": {"is_open": False},
    }

    bot2 = AsyncMock(spec=OmniTrader)
    bot2.bot_id = "bot2"
    bot2.config = Config(
        {
            "trading": {"symbol": "ETH/USDT", "timeframe": "15m"},
            "exchange": {"paper_mode": True, "leverage": 10},
            "strategy": {"name": "ema_volume"},
        }
    )
    bot2._running = False
    bot2.risk = AsyncMock()

    bot2.risk.check_circuit_breaker = lambda: False
    bot2.ws_manager = None

    bot2.risk.daily_stats.realized_pnl = 0.0
    bot2.risk.daily_stats.pnl_pct = 0.0
    bot2.risk.daily_stats.trades_count = 0
    bot2.risk.daily_stats.wins = 0
    bot2.risk.daily_stats.losses = 0

    bot2.get_summary = lambda: {
        "id": "bot2",
        "symbol": "ETH/USDT",
        "timeframe": "15m",
        "running": False,
        "strategy": "ema_volume",
        "market_regime": "ranging",
        "daily_pnl": 0.0,
        "daily_pnl_pct": 0.0,
        "total_balance": 10000.0,
        "leverage": 10,
        "paper_mode": True,
        "uptime_seconds": 0,
        "circuit_breaker_active": False,
        "position": {"is_open": False},
    }

    manager.bots = {"bot1": bot1, "bot2": bot2}

    manager.create_bot = AsyncMock(return_value="bot3")
    manager.update_bot = AsyncMock(return_value=True)
    manager.delete_bot = AsyncMock(return_value=True)
    manager._save_state = AsyncMock()

    return manager


@pytest.fixture
def client(mock_bot_manager):
    app = create_api(bot_manager=mock_bot_manager)
    return TestClient(app)


@pytest.fixture
def auth_headers():
    from src.api.auth import get_api_key

    key = get_api_key()
    return {"Authorization": f"Bearer {key}"}


def test_list_bots(client, auth_headers):
    response = client.get("/api/bots", headers=auth_headers)
    assert response.status_code == 200
    bots = response.json()
    assert len(bots) == 2

    symbols = [b["symbol"] for b in bots]
    assert "BTC/USDT" in symbols
    assert "ETH/USDT" in symbols


def test_get_bot(client, auth_headers):
    response = client.get("/api/bots/bot1", headers=auth_headers)
    assert response.status_code == 200
    bot = response.json()
    assert bot["id"] == "bot1"
    assert bot["running"]
    assert bot["daily_pnl"] == 100.0


def test_get_bot_not_found(client, auth_headers):
    response = client.get("/api/bots/missing", headers=auth_headers)
    assert response.status_code == 404


def test_create_bot_unauthorized(client):
    response = client.post(
        "/api/bots", json={"config": {"trading": {"symbol": "SOL/USDT"}}}
    )
    assert response.status_code == 401


def test_create_bot_authorized(client, auth_headers):
    response = client.post(
        "/api/bots",
        json={"config": {"trading": {"symbol": "SOL/USDT"}}},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["ok"]
    assert response.json()["bot_id"] == "bot3"


def test_status_aggregation(client):
    response = client.get("/api/status")
    assert response.status_code == 200
    status = response.json()
    assert status["total_bots"] == 2
    assert status["running"]
    assert status["running_count"] == 1
    assert status["symbol"] == "multiple"


def test_update_bot_authorized(client, auth_headers, mock_bot_manager):
    payload = {"config": {"trading": {"symbol": "DOGE/USDT"}}}
    response = client.put(
        "/api/bots/bot1",
        json=payload,
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["ok"]
    mock_bot_manager.update_bot.assert_called_once_with(
        "bot1", {"trading": {"symbol": "DOGE/USDT"}}
    )


def test_update_bot_unauthorized(client):
    payload = {"config": {"trading": {"symbol": "DOGE/USDT"}}}
    response = client.put(
        "/api/bots/bot1",
        json=payload,
    )
    assert response.status_code == 401


def test_update_bot_not_found(client, auth_headers, mock_bot_manager):
    mock_bot_manager.update_bot.return_value = False
    payload = {"config": {"trading": {"symbol": "DOGE/USDT"}}}
    response = client.put(
        "/api/bots/missing",
        json=payload,
        headers=auth_headers,
    )
    assert response.status_code == 404
