"""
Tests for Strategy Registry and Implementations.
"""

from unittest.mock import MagicMock

import pandas as pd
import pytest

from src.config import Config
from src.risk import RiskManager
from src.strategies import (
    get_strategy,
    list_strategies,
)
from src.strategies.adx_trend import ADXTrendStrategy
from src.strategies.bollinger_bands import BollingerBandsStrategy
from src.strategies.breakout import BreakoutStrategy
from src.strategies.ema_volume import EMAVolumeStrategy
from src.strategies.z_score import ZScoreStrategy


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
            "bollinger_bands": {
                "length": 20,
                "std": 2.0,
                "rsi_length": 14,
                "rsi_lower": 30,
                "rsi_upper": 70,
            },
            "breakout": {"period": 20},
        },
        "risk": {
            "trailing_stop_activation_pct": 1.0,
            "trailing_stop_callback_pct": 0.5,
        },
    }
    return Config(config_data)


def test_registry():
    """Test strategy registration and retrieval."""
    strategies = list_strategies()
    assert "ema_volume" in strategies
    assert "adx_trend" in strategies
    assert "z_score" in strategies
    assert "bollinger_bands" in strategies
    assert "breakout" in strategies

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
        "close": [100] * 20,  # Flat
        "volume": [1000] * 20,
    }
    # Last 2 candles create cross
    data["close"][-2] = 100
    data["close"][-1] = 110  # Jump up
    data["volume"][-1] = 2000  # High volume

    df = pd.DataFrame(data)
    df["high"] = df["close"]
    df["low"] = df["close"]

    # Needs update
    strategy.update(df)

    assert bool(strategy.should_long()) is True
    assert bool(strategy.should_short()) is False

    # Test Short scenario
    data["close"][-1] = 90  # Jump down
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

    strategy.adx = 30  # > 25
    strategy.plus_di = 20
    strategy.minus_di = 10

    assert strategy.should_long() is True  # 30 > 25 and 20 > 10
    assert strategy.should_short() is False

    strategy.plus_di = 10
    strategy.minus_di = 20

    assert strategy.should_long() is False
    assert strategy.should_short() is True

    strategy.adx = 20  # < 25
    assert strategy.should_long() is False
    assert strategy.should_short() is False


def test_z_score_strategy(mock_config):
    """Test Z-Score Strategy logic."""
    strategy = ZScoreStrategy(mock_config)

    # Mock internal state for simplicity
    strategy.z_score = -2.5  # < -2.0
    assert strategy.should_long() is True
    assert strategy.should_short() is False

    strategy.z_score = 2.5  # > 2.0
    assert strategy.should_long() is False
    assert strategy.should_short() is True

    strategy.z_score = 0.5
    assert strategy.should_long() is False
    assert strategy.should_short() is False

    # Test Exit logic
    strategy.current_position = "long"
    strategy.z_score = 0.1  # > 0
    assert strategy.should_exit() is True

    strategy.z_score = -0.1
    assert strategy.should_exit() is False

    strategy.current_position = "short"
    strategy.z_score = -0.1  # < 0
    assert strategy.should_exit() is True


def test_bollinger_bands_strategy(mock_config):
    """Test Bollinger Bands Strategy logic."""
    strategy = BollingerBandsStrategy(mock_config)

    # Mock internal state
    strategy.lower_band = 90
    strategy.upper_band = 110
    strategy.mid_band = 100

    # Case: Long (Price < Lower Band and RSI < 30)
    strategy.current_price = 85
    strategy.rsi = 25
    assert strategy.should_long() is True

    strategy.rsi = 40
    assert strategy.should_long() is False

    # Case: Short (Price > Upper Band and RSI > 70)
    strategy.current_price = 115
    strategy.rsi = 75
    assert strategy.should_short() is True

    strategy.rsi = 60
    assert strategy.should_short() is False

    # Case: Exit Long (Price > Mid Band)
    strategy.current_position = "long"
    strategy.current_price = 101
    assert strategy.should_exit() is True

    strategy.current_price = 99
    assert strategy.should_exit() is False


def test_breakout_strategy(mock_config):
    """Test Breakout Strategy logic."""
    strategy = BreakoutStrategy(mock_config)

    # Mock internal state
    strategy.upper_channel = 110
    strategy.lower_channel = 90
    strategy.mid_channel = 100

    # Case: Long (Price > Upper Channel)
    strategy.current_price = 111
    assert strategy.should_long() is True

    strategy.current_price = 109
    assert strategy.should_long() is False

    # Case: Short (Price < Lower Channel)
    strategy.current_price = 89
    assert strategy.should_short() is True

    strategy.current_price = 91
    assert strategy.should_short() is False

    # Case: Exit Long (Price < Mid Channel)
    strategy.current_position = "long"
    strategy.current_price = 99
    assert strategy.should_exit() is True


def test_trailing_stop():
    """Test Trailing Stop logic in RiskManager."""

    # Create fake config
    class FakeConfig:
        def __init__(self):
            self.trading = MagicMock()
            self.trading.position_size_pct = 1.0
            self.risk = MagicMock()
            self.risk.stop_loss_pct = 2.0
            self.risk.take_profit_pct = 4.0
            self.risk.max_daily_loss_pct = 5.0
            self.risk.max_positions = 1
            self.risk.trailing_stop_activation_pct = 1.0
            self.risk.trailing_stop_callback_pct = 0.5
            self.exchange = MagicMock()
            self.exchange.leverage = 1

    # Mock get_config
    import src.risk

    src.risk.get_config = lambda: FakeConfig()

    risk = RiskManager()

    # Case 1: Long Position
    # Entry: 100. Current: 102. PnL: +2%. Activation: 1%. Callback: 0.5%
    # Expected Stop: 102 * (1 - 0.005) = 101.49

    position_data = {
        "symbol": "BTC",
        "side": "long",
        "contracts": 1,
        "entryPrice": 100,
        "notional": 100,
        "unrealizedPnl": 2,
        "leverage": 1,
    }

    # Mock position object similar to exchange.Position
    class MockPosition:
        def __init__(self, data):
            self.is_open = True
            self.side = data["side"]
            self.entry_price = data["entryPrice"]

    pos = MockPosition(position_data)

    new_stop = risk.calculate_trailing_stop(102.0, pos)
    assert new_stop is not None
    assert abs(new_stop - 101.49) < 0.01

    # Case 2: PnL not high enough (< 1%)
    new_stop = risk.calculate_trailing_stop(100.5, pos)
    assert new_stop is None


def test_strategy_required_candles(mock_config):
    """Test that strategies correctly report required candles."""
    ema = EMAVolumeStrategy(mock_config)
    expected_ema = max(mock_config.strategy.ema_slow, mock_config.strategy.volume_sma) + 2
    assert ema.required_candles == expected_ema

    adx = ADXTrendStrategy(mock_config)
    assert adx.required_candles == mock_config.strategy.adx_period + 20

    zscore = ZScoreStrategy(mock_config)
    assert zscore.required_candles == mock_config.strategy.z_score_window + 1

    bb = BollingerBandsStrategy(mock_config)
    expected_bb = (
        max(
            mock_config.strategy.bollinger_bands.length,
            mock_config.strategy.bollinger_bands.rsi_length,
        )
        + 1
    )
    assert bb.required_candles == expected_bb

    breakout = BreakoutStrategy(mock_config)
    assert breakout.required_candles == mock_config.strategy.breakout.period + 1
