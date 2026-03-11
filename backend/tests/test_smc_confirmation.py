import pandas as pd

from src.config import Config
from src.strategy.base import BaseStrategy, Signal


class DummyStrategy(BaseStrategy):
    def __init__(self, config):
        super().__init__(config)
        self.long_signal = False
        self.short_signal = False

    @property
    def metadata(self):
        return {}

    @property
    def valid_regimes(self):
        return []

    def update(self, ohlcv, current_position=None):
        pass

    def should_long(self):
        return self.long_signal

    def should_short(self):
        return self.short_signal

    def should_exit(self):
        return False

def test_smc_confirmation_enabled_long_rejected():
    config_data = {
        "trading": {
            "timeframe": "1h"
        },
        "strategy": {
            "min_bars_between_entries": 0,
            "bias_confirmation": False,
            "smc_confirmation": True,
            "smc_timeframe": "4h",
            "smc_swing_window": 1
        }
    }
    config = Config(config_data)
    strategy = DummyStrategy(config)
    strategy.long_signal = True

    # Create dummy 1h data
    dates_1h = pd.date_range("2020-01-01", periods=10, freq="h")
    df_1h = pd.DataFrame({"close": range(10)}, index=dates_1h)

    # Create dummy 4h data that results in BEARISH trend
    dates_4h = pd.date_range("2020-01-01", periods=10, freq="4h")
    df_4h = pd.DataFrame({
        "open": [95,  100, 88,  92, 78,  82, 68,  72, 58,  62],
        "high": [100, 105, 90,  95, 80,  85, 70,  75, 60,  65],
        "low":  [90,  95,  85,  90, 75,  80, 65,  70, 55,  60],
        "close":[95,  100, 88,  92, 78,  82, 68,  72, 58,  62],
        "volume": [1000]*10
    }, index=dates_4h)

    market_data = {
        "1h": df_1h,
        "4h": df_4h
    }

    res = strategy.analyze(market_data, ohlcv=df_1h)
    
    assert res.signal == Signal.HOLD
    assert "SMC Bias Filter (4h: bearish) blocked Long" in res.reason

def test_smc_confirmation_enabled_short_rejected():
    config_data = {
        "trading": {
            "timeframe": "1h"
        },
        "strategy": {
            "min_bars_between_entries": 0,
            "bias_confirmation": False,
            "smc_confirmation": True,
            "smc_timeframe": "4h",
            "smc_swing_window": 1
        }
    }
    config = Config(config_data)
    strategy = DummyStrategy(config)
    strategy.short_signal = True

    # Create dummy 1h data
    dates_1h = pd.date_range("2020-01-01", periods=10, freq="h")
    df_1h = pd.DataFrame({"close": range(10)}, index=dates_1h)

    # Create dummy 4h data that results in BULLISH trend
    dates_4h = pd.date_range("2020-01-01", periods=10, freq="4h")
    df_4h = pd.DataFrame({
        "open": [55,  50,  65,  60,  75,  70,  85,  80,  95, 90],
        "high": [60,  55,  70,  65,  80,  75,  90,  85, 100, 95],
        "low":  [50,  45,  60,  55,  70,  65,  80,  75,  90, 85],
        "close":[55,  50,  65,  60,  75,  70,  85,  80,  95, 90],
        "volume": [1000]*10
    }, index=dates_4h)

    market_data = {
        "1h": df_1h,
        "4h": df_4h
    }

    res = strategy.analyze(market_data, ohlcv=df_1h)
    
    assert res.signal == Signal.HOLD
    assert "SMC Bias Filter (4h: bullish) blocked Short" in res.reason

def test_smc_confirmation_disabled_accepts():
    config_data = {
        "trading": {
            "timeframe": "1h"
        },
        "strategy": {
            "min_bars_between_entries": 0,
            "bias_confirmation": False,
            "smc_confirmation": False
        }
    }
    config = Config(config_data)
    strategy = DummyStrategy(config)
    strategy.long_signal = True

    dates_1h = pd.date_range("2020-01-01", periods=10, freq="h")
    df_1h = pd.DataFrame({"close": range(10)}, index=dates_1h)

    market_data = {"1h": df_1h}
    res = strategy.analyze(market_data, ohlcv=df_1h)
    assert res.signal == Signal.LONG

def test_smc_confirmation_missing_data_rejects():
    config_data = {
        "trading": {
            "timeframe": "1h"
        },
        "strategy": {
            "min_bars_between_entries": 0,
            "bias_confirmation": False,
            "smc_confirmation": True,
            "smc_timeframe": "4h"
        }
    }
    config = Config(config_data)
    strategy = DummyStrategy(config)
    strategy.long_signal = True

    dates_1h = pd.date_range("2020-01-01", periods=10, freq="h")
    df_1h = pd.DataFrame({"close": range(10)}, index=dates_1h)

    market_data = {"1h": df_1h} # 4h data is missing
    res = strategy.analyze(market_data, ohlcv=df_1h)
    assert res.signal == Signal.HOLD
    assert "missing data" in res.reason

