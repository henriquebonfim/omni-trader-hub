import pytest
from fastapi.testclient import TestClient

from src.api import create_api
from src.config import Config
from src.strategy.custom_executor import CustomStrategyExecutor


class MockDatabase:
    def __init__(self):
        self.strats = {}

    async def save_custom_strategy(
        self,
        name,
        description,
        regime_affinity,
        entry_long_json,
        entry_short_json,
        exit_long_json,
        exit_short_json,
        indicators_json,
        stop_loss_atr_mult,
        take_profit_atr_mult,
        min_bars_between_entries,
    ):
        self.strats[name] = {
            "name": name,
            "description": description,
            "regime_affinity": regime_affinity,
            "entry_long_json": entry_long_json,
            "entry_short_json": entry_short_json,
            "exit_long_json": exit_long_json,
            "exit_short_json": exit_short_json,
            "indicators_json": indicators_json,
            "stop_loss_atr_mult": stop_loss_atr_mult,
            "take_profit_atr_mult": take_profit_atr_mult,
            "min_bars_between_entries": min_bars_between_entries,
            "created_at": 1,
            "updated_at": 1,
        }

    async def get_custom_strategy(self, name):
        return self.strats.get(name)

    async def list_custom_strategies(self):
        return list(self.strats.values())

    async def delete_custom_strategy(self, name):
        if name in self.strats:
            del self.strats[name]
            return True
        return False


class MockBot:
    def __init__(self, db):
        self.config = Config(
            {
                "exchange": {"paper_mode": True},
                "trading": {"timeframe": "1h"},
                "strategy": {"name": "ema_volume"},
            }
        )
        self.database = db
        self.strategy = None


class MockBotManager:
    def __init__(self, db):
        self.bots = {"default": MockBot(db)}
        self.default_bot_id = "default"

    def get_bot(self, bot_id=None):
        return self.bots["default"]


@pytest.mark.asyncio
async def test_custom_strategy_crud():
    db = MockDatabase()
    app = create_api(bot_manager=MockBotManager(db))
    client = TestClient(app)

    # 1. Create custom strategy via API
    payload = {
        "name": "test_custom_rsi",
        "description": "A test custom RSI strategy",
        "regime_affinity": ["trending"],
        "indicators_json": [
            {"function": "RSI", "params": {"timeperiod": 14}, "output_name": "rsi_14"}
        ],
        "entry_long_json": [{"indicator": "rsi_14", "operator": "<", "value": 30}],
        "entry_short_json": [],
        "exit_long_json": [],
        "exit_short_json": [],
        "stop_loss_atr_mult": 1.5,
        "take_profit_atr_mult": 3.0,
        "min_bars_between_entries": 10,
    }

    # Bypass API Key for tests by overriding _API_KEY
    import src.api.auth

    src.api.auth._API_KEY = "test_api_key"
    headers = {"Authorization": "Bearer test_api_key"}

    res = client.post("/api/strategies", json=payload, headers=headers)
    assert res.status_code == 200
    assert res.json()["name"] == "test_custom_rsi"

    # 2. Retrieve via GET
    res = client.get("/api/strategies/test_custom_rsi")
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "test_custom_rsi"
    assert data["type"] == "custom"
    assert len(data["indicators"]) == 1

    # 3. List combined
    res = client.get("/api/strategies")
    assert res.status_code == 200
    strats = res.json()["strategies"]
    names = [s["name"] for s in strats]
    assert "ema_volume" in names
    assert "test_custom_rsi" in names

    # 4. Executor check logic
    import numpy as np
    import pandas as pd

    cs = await db.get_custom_strategy("test_custom_rsi")
    executor = CustomStrategyExecutor(
        Config({"trading": {"timeframe": "1h"}, "strategy": {}, "risk": {}}), cs
    )

    ohlcv = pd.DataFrame(
        {
            "open": np.random.rand(100),
            "high": np.random.rand(100),
            "low": np.random.rand(100),
            "close": np.random.rand(100),
            "volume": np.random.rand(100),
        }
    )
    ohlcv.loc[ohlcv.index[-1], "close"] = 10  # Fake a large drop to tank RSI
    ohlcv.loc[ohlcv.index[-2], "close"] = 100

    executor.update(ohlcv)
    executor._indicators["rsi_14"] = pd.Series([40, 40, 20])
    assert executor.should_long()

    # 5. DELETE fails for built-in
    res = client.delete("/api/strategies/ema_volume", headers=headers)
    assert res.status_code == 404
    assert "Strategy not found" in res.json()["detail"]

    # 6. DELETE succeeds for custom
    res = client.delete("/api/strategies/test_custom_rsi", headers=headers)
    assert res.status_code == 200
