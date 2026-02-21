"""
Tests for Strategy Registry and Implementations.
"""

import pandas as pd
import pytest
from unittest.mock import MagicMock

from src.strategies import get_strategy, list_strategies, Signal, register_strategy, BaseStrategy
from src.strategies.ema_volume import EMAVolumeStrategy
from src.strategies.adx_trend import ADXTrendStrategy
from src.strategies.z_score import ZScoreStrategy
from src.config import Config


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    config_data = {
        "trading": {"strategy_name": "ema_volume"},
        "strategy": {
            "ema_fast": 5,
            "ema_slow": 10,
            "volume_sma": 10,
            "volume_threshold": 1.5,
            "adx_period": 14,
            "adx_threshold": 25,
            "z_score_window": 10,
            "z_score_threshold": 2.0,
        },
    }
    return Config(config_data)


def test_registry():
    """Test strategy registration and retrieval."""
    strategies = list_strategies()
    assert "ema_volume" in strategies
    assert "adx_trend" in strategies
    assert "z_score" in strategies

    cls = get_strategy("ema_volume")
    assert cls == EMAVolumeStrategy

    with pytest.raises(ValueError):
        get_strategy("non_existent_strategy")


def test_ema_volume_strategy(mock_config):
    """Test EMA Volume Strategy logic."""
    strategy = EMAVolumeStrategy(mock_config)

    # Create fake OHLCV data
    # Scenario: Bullish Cross with High Volume
    # EMA(5) crosses above EMA(10)
    # Volume > 1.5x SMA(10)

    data = {
        "close": [100] * 20, # Flat
        "volume": [1000] * 20
    }
    # Last 2 candles create cross
    data["close"][-2] = 100
    data["close"][-1] = 110 # Jump up
    data["volume"][-1] = 2000 # High volume

    df = pd.DataFrame(data)
    df["high"] = df["close"]
    df["low"] = df["close"]

    # Needs update
    strategy.update(df)

    assert bool(strategy.should_long()) is True
    assert bool(strategy.should_short()) is False

    # Test Short scenario
    data["close"][-1] = 90 # Jump down
    df = pd.DataFrame(data)
    strategy.update(df)

    assert bool(strategy.should_long()) is False
    assert bool(strategy.should_short()) is True


def test_adx_trend_strategy(mock_config):
    """Test ADX Trend Strategy logic."""
    strategy = ADXTrendStrategy(mock_config)

    # ADX requires significant data (length + smoothing)
    # We will mock the internal state because mocking OHLCV for ADX is complex math

    # Mock update to set internal state directly
    # This bypasses calculation but tests logic

    strategy.adx = 30 # > 25
    strategy.plus_di = 20
    strategy.minus_di = 10

    assert strategy.should_long() is True # 30 > 25 and 20 > 10
    assert strategy.should_short() is False

    strategy.plus_di = 10
    strategy.minus_di = 20

    assert strategy.should_long() is False
    assert strategy.should_short() is True

    strategy.adx = 20 # < 25
    assert strategy.should_long() is False
    assert strategy.should_short() is False


def test_z_score_strategy(mock_config):
    """Test Z-Score Strategy logic."""
    strategy = ZScoreStrategy(mock_config)

    # Mock internal state for simplicity
    strategy.z_score = -2.5 # < -2.0
    assert strategy.should_long() is True
    assert strategy.should_short() is False

    strategy.z_score = 2.5 # > 2.0
    assert strategy.should_long() is False
    assert strategy.should_short() is True

    strategy.z_score = 0.5
    assert strategy.should_long() is False
    assert strategy.should_short() is False

    # Test Exit logic
    strategy.current_position = "long"
    strategy.z_score = 0.1 # > 0
    assert strategy.should_exit() is True

    strategy.z_score = -0.1
    assert strategy.should_exit() is False

    strategy.current_position = "short"
    strategy.z_score = -0.1 # < 0
    assert strategy.should_exit() is True


def test_strategy_metadata(mock_config):
    """Test metadata presence."""
    s1 = EMAVolumeStrategy(mock_config)
    assert s1.metadata["type"] == "trend_following"

    s2 = ADXTrendStrategy(mock_config)
    assert s2.metadata["type"] == "trend_following"

    s3 = ZScoreStrategy(mock_config)
    assert s3.metadata["type"] == "mean_reversion"
