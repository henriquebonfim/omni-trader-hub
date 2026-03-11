import pandas as pd
import pytest

from src.config import Config
from src.strategy.custom_executor import CustomStrategyExecutor


@pytest.fixture
def config():
    return Config({"trading": {"timeframe": "1h"}, "strategy": {}, "risk": {}})

def test_custom_strategy_executor_init(config):
    custom_config = {
        "name": "my_strat",
        "description": "desc",
        "regime_affinity": ["trending"],
        "indicators_json": [{"function": "RSI", "params": {"timeperiod": 14}, "output_name": "rsi_14"}],
        "entry_long_json": [{"indicator": "rsi_14", "operator": "<", "value": 30}]
    }
    
    executor = CustomStrategyExecutor(config, custom_config)
    assert executor.name == "my_strat"
    assert executor.metadata["description"] == "desc"

def test_custom_strategy_executor_indicators(config):
    custom_config = {
        "name": "rsi_strat",
        "indicators_json": [{"function": "RSI", "params": {"timeperiod": 14}, "output_name": "rsi_14"}],
        "entry_long_json": [{"indicator": "rsi_14", "operator": "<", "value": 30}]
    }
    executor = CustomStrategyExecutor(config, custom_config)
    
    # Create fake OHLCV
    import numpy as np
    data = {"open": np.random.rand(100), "high": np.random.rand(100), "low": np.random.rand(100), "close": np.random.rand(100), "volume": np.random.rand(100)}
    data["close"][[-1, -2]] = [10, 10]  # Just to ensure it calculates
    df = pd.DataFrame(data)
    
    executor.update(df)
    assert "rsi_14" in executor._indicators

def test_custom_strategy_executor_crosses_above(config):
    custom_config = {
        "name": "cross_strat",
        "indicators_json": [{"function": "SMA", "params": {"timeperiod": 10}, "output_name": "sma_10"}],
        "entry_long_json": [{"indicator": "close", "operator": "crosses_above", "value": "sma_10"}]
    }
    executor = CustomStrategyExecutor(config, custom_config)
    
    # Fake OHLCV
    import numpy as np
    data = {"open": np.ones(100), "high": np.ones(100), "low": np.ones(100), "close": np.ones(100), "volume": np.ones(100)}
    df = pd.DataFrame(data)
    
    # Set up scenario: previous close < sma, current close > sma
    executor.update(df)
    executor._indicators["sma_10"] = pd.Series(np.ones(100) * 5)
    df.loc[df.index[-2], "close"] = 4
    df.loc[df.index[-1], "close"] = 6
    executor.ohlcv = df
    
    assert executor.should_long()

