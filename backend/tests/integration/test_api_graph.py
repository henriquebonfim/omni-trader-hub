from unittest.mock import AsyncMock, MagicMock

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from src.interfaces.api import create_api


def _df_from_prices(prices: list[float]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "open": prices,
            "high": prices,
            "low": prices,
            "close": prices,
            "volume": [1000.0] * len(prices),
        }
    )


@pytest.fixture
def mock_bot() -> MagicMock:
    bot = MagicMock()
    bot.config.trading.symbol = "BTC/USDT"

    async def _fetch_ohlcv(symbol: str, timeframe: str, limit: int):
        if symbol == "BTC/USDT":
            return _df_from_prices([100, 101, 102, 101, 103, 104])
        if symbol == "ETH/USDT":
            return _df_from_prices([200, 199, 201, 202, 203, 201])
        return pd.DataFrame()

    bot.exchange.fetch_ohlcv = AsyncMock(side_effect=_fetch_ohlcv)
    return bot


@pytest.fixture
def client(mock_bot: MagicMock) -> TestClient:
    app = create_api(mock_bot)
    return TestClient(app)


def test_correlation_matrix_success(client: TestClient):
    response = client.get(
        "/api/graph/correlation-matrix?symbols=BTC/USDT,ETH/USDT&timeframe=1h&limit=120"
    )
    assert response.status_code == 200

    data = response.json()
    assert data["symbols"] == ["BTC/USDT", "ETH/USDT"]
    assert data["timeframe"] == "1h"
    assert data["window"] >= 2
    assert len(data["matrix"]) == 2
    assert data["matrix"][0][0] == 1.0
    assert data["matrix"][1][1] == 1.0


def test_correlation_matrix_single_symbol_defaults(client: TestClient):
    response = client.get("/api/graph/correlation-matrix?symbols=BTC/USDT")
    assert response.status_code == 200

    data = response.json()
    assert data["symbols"] == ["BTC/USDT"]
    assert data["matrix"] == [[1.0]]


def test_correlation_matrix_limit_validation(client: TestClient):
    response = client.get("/api/graph/correlation-matrix?limit=10")
    assert response.status_code == 400
    assert "limit must be between 30 and 1000" in response.json()["detail"]


def test_correlation_matrix_no_data_returns_400(client: TestClient):
    response = client.get("/api/graph/correlation-matrix?symbols=SOL/USDT")
    assert response.status_code == 400
    assert "Not enough market data" in response.json()["detail"]


def test_graph_news_feed_endpoint_returns_list(client: TestClient):
    response = client.get("/api/graph/news")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_graph_crisis_update_accepts_json_body(client: TestClient, monkeypatch):
    monkeypatch.setenv("OMNITRADER_API_KEY", "test-secret")

    import src.interfaces.api.auth as auth

    auth._API_KEY = None
    auth._AUTH_DEV_MODE = False

    bot = MagicMock()
    bot.config.trading.symbol = "BTC/USDT"
    bot.exchange.fetch_ohlcv = AsyncMock(return_value=_df_from_prices([100, 101, 102]))
    bot.crisis_manager.set_crisis_mode = AsyncMock()
    bot.crisis_manager.get_crisis_state = AsyncMock(return_value={"active": True})

    app = create_api(bot)
    local_client = TestClient(app)

    response = local_client.put(
        "/api/graph/crisis",
        json={"active": True, "reason": "test"},
        headers={"Authorization": "Bearer test-secret"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_graph_asset_news_uses_impacts_relationship(monkeypatch):
    monkeypatch.setenv("OMNITRADER_API_KEY", "test-secret")

    import src.interfaces.api.auth as auth

    auth._API_KEY = None
    auth._AUTH_DEV_MODE = False

    class _Result:
        async def fetch(self, _limit):
            return [
                {
                    "title": "Market stress update",
                    "timestamp": 1710000000000,
                    "sentiment": 0.8,
                    "source": "CoinDesk",
                }
            ]

    class _Session:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def run(self, query, **kwargs):
            assert "[r:IMPACTS]" in query
            assert "r.magnitude as sentiment" in query
            assert kwargs["symbol"] == "BTC"
            return _Result()

    bot = MagicMock()
    bot.config.trading.symbol = "BTC/USDT"
    bot.exchange.fetch_ohlcv = AsyncMock(return_value=_df_from_prices([100, 101, 102]))
    bot.database = MagicMock()
    bot.database._driver = MagicMock()
    bot.database._driver.session = MagicMock(return_value=_Session())

    app = create_api(bot)
    local_client = TestClient(app)

    response = local_client.get("/api/graph/news/BTC")
    assert response.status_code == 200
    payload = response.json()
    assert payload["symbol"] == "BTC"
    assert payload["news"][0]["sentiment"] == 0.8
