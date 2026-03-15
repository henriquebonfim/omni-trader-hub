"""
Tests for ATR-based stops logic in RiskManager.
"""

from datetime import datetime, timedelta

import pandas as pd
import pytest

from src.config import Config
from src.risk import RiskManager


@pytest.fixture
def mock_ohlcv():
    """Create a mock OHLCV DataFrame."""
    dates = [datetime.now() - timedelta(minutes=i * 15) for i in range(100)]
    dates.reverse()

    data = {
        "timestamp": dates,
        "open": [100.0] * 100,
        "high": [105.0] * 100,
        "low": [95.0] * 100,
        "close": [100.0] * 100,
        "volume": [1000.0] * 100,
    }

    df = pd.DataFrame(data)
    df.set_index("timestamp", inplace=True)
    return df


@pytest.fixture
def risk_manager():
    """Create a RiskManager instance with ATR stops enabled."""
    rm = RiskManager()

    # Mock config
    config_data = {
        "trading": {"position_size_pct": 2.0},
        "risk": {
            "stop_loss_pct": 2.0,
            "take_profit_pct": 4.0,  # Fixed: was take_profit_price
            "max_daily_loss_pct": 5.0,
            "max_positions": 5,
            "use_atr_stops": True,
            "atr_period": 14,
            "atr_multiplier_sl": 1.5,
            "atr_multiplier_tp": 2.0,
            "liquidation_buffer_pct": 0.5,
            "trailing_stop_activation_pct": 1.0,
            "trailing_stop_callback_pct": 0.5,
        },
        "exchange": {"leverage": 1},
    }

    config = Config(config_data)
    rm.update_config(config)
    return rm


def test_atr_stops_calculation(risk_manager, mock_ohlcv):
    """Test ATR-based stop loss and take profit calculation."""
    # ATR for High=105, Low=95, Close=100 is roughly 10 (TR = 10)
    # SMA of TR over 14 periods should be 10.

    # Let's verify with pandas_ta or manual check if possible, but mocking exact values is easier.
    # Given constant candles H=105, L=95, C=100, Previous Close=100.
    # TR = max(105-95, abs(105-100), abs(95-100)) = 10.
    # ATR(14) should be 10.

    entry_price = 100.0
    sl, tp = risk_manager.calculate_atr_stops(entry_price, "long", mock_ohlcv)

    # Expected SL = Entry - (ATR * 1.5) = 100 - (10 * 1.5) = 85
    # Expected TP = Entry + (ATR * 2.0) = 100 + (10 * 2.0) = 120

    # Allow some floating point variance
    assert abs(sl - 85.0) < 0.1
    assert abs(tp - 120.0) < 0.1

    # Test Short
    sl_short, tp_short = risk_manager.calculate_atr_stops(
        entry_price, "short", mock_ohlcv
    )

    # Expected SL = Entry + (ATR * 1.5) = 100 + 15 = 115
    # Expected TP = Entry - (ATR * 2.0) = 100 - 20 = 80

    assert abs(sl_short - 115.0) < 0.1
    assert abs(tp_short - 80.0) < 0.1


def test_atr_stops_fallback(risk_manager):
    """Test fallback to fixed stops when OHLCV is missing."""
    risk_manager.stop_loss_pct = 2.0
    risk_manager.take_profit_pct = 4.0

    entry_price = 100.0
    sl, tp = risk_manager.calculate_atr_stops(entry_price, "long", None)

    # Expected SL = 100 * (1 - 0.02) = 98
    # Expected TP = 100 * (1 + 0.04) = 104

    assert sl == 98.0
    assert tp == 104.0


def test_validate_trade_with_atr(risk_manager, mock_ohlcv):
    """Test validate_trade uses ATR stops."""
    check = risk_manager.validate_trade(
        side="long",
        balance=1000.0,
        entry_price=100.0,
        current_positions=0,
        ohlcv=mock_ohlcv,
    )

    assert check.approved is True
    # Verify values match ATR calc
    assert abs(check.stop_loss_price - 85.0) < 0.1
    assert abs(check.take_profit_price - 120.0) < 0.1
