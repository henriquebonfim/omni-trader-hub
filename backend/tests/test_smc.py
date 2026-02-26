"""
Tests for SMC Market Structure Logic.
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pandas as pd
import pytest

from src.strategies.smc.structure import MarketStructure, Swing, SwingType, Trend, StructureEvent
from src.strategies.smc.analysis import SMCAnalyzer


@pytest.fixture
def sample_ohlcv_bullish():
    """
    Create a bullish trend structure:
    Low -> High -> Higher Low -> Higher High
    """
    # Simple zig-zag pattern
    # 0: Low (100)
    # 5: High (110)
    # 10: Higher Low (105)
    # 15: Higher High (115)

    dates = [datetime(2023, 1, 1) + timedelta(minutes=i) for i in range(20)]
    prices = [100] * 20

    # Ramp up 0-5
    for i in range(6): prices[i] = 100 + i*2 # 100, 102, 104, 106, 108, 110
    # Ramp down 5-10
    for i in range(6, 11): prices[i] = 110 - (i-5) # 109, 108, 107, 106, 105
    # Ramp up 10-15
    for i in range(11, 16): prices[i] = 105 + (i-10)*2 # 107, 109, 111, 113, 115
    # Ramp down 15-20
    for i in range(16, 20): prices[i] = 115 - (i-15) # 114, 113, 112, 111

    df = pd.DataFrame({
        "open": prices,
        "high": prices,
        "low": prices,
        "close": prices,
        "volume": [1000] * 20
    }, index=dates)

    return df

def test_detect_swings(sample_ohlcv_bullish):
    # Use window=2
    ms = MarketStructure(swing_window=2)
    swings = ms.detect_swings(sample_ohlcv_bullish)

    # Index 5 should be High (110)
    # Index 10 should be Low (105)
    # Index 15 should be High (115)

    # Note: Window=2 means we need 2 bars after to confirm.
    # 5 is confirmed at 7.
    # 10 is confirmed at 12.
    # 15 is confirmed at 17.

    # Check High at 5
    h1 = next((s for s in swings if s.index == 5), None)
    assert h1 is not None
    assert h1.type == SwingType.HIGH
    assert h1.price == 110

    # Check Low at 10
    l1 = next((s for s in swings if s.index == 10), None)
    assert l1 is not None
    assert l1.type == SwingType.LOW
    assert l1.price == 105

    # Check High at 15
    h2 = next((s for s in swings if s.index == 15), None)
    assert h2 is not None
    assert h2.type == SwingType.HIGH
    assert h2.price == 115

def test_structure_bos():
    """Test Break of Structure logic."""
    # Scenario:
    # 1. Swing High established at 100.
    # 2. Price drops, Swing Low established at 90.
    # 3. Price rallies and breaks 100 -> BOS Bullish.

    dates = [datetime(2023, 1, 1) + timedelta(minutes=i) for i in range(30)]
    prices = [90] * 30

    # 0-5: Ramp to 100 (High at 5)
    for i in range(6): prices[i] = 90 + i*2 # 90..100
    # 5-10: Drop to 90 (Low at 10)
    for i in range(6, 11): prices[i] = 100 - (i-5)*2 # 98..90
    # 10-20: Rally to 110 (Break 100 at ~15)
    for i in range(11, 21): prices[i] = 90 + (i-10)*2 # 92..110

    # BOS should happen when price > 100.
    # Index 15: price 100. Index 16: price 102 -> BOS.

    df = pd.DataFrame({
        "open": prices, "high": prices, "low": prices, "close": prices, "volume": 1000
    }, index=dates)

    ms = MarketStructure(swing_window=2)
    result = ms.analyze_structure(df)

    assert result.trend == Trend.BULLISH
    assert len(result.events) > 0

    bos = result.events[0]
    assert bos.type == "BOS"
    assert bos.trend == Trend.BULLISH
    assert bos.price > 100

def test_structure_choch():
    """Test Change of Character logic."""
    # Scenario: Uptrend then break of higher low.
    # 1. Low 90 (0)
    # 2. High 100 (5)
    # 3. Higher Low 95 (10)
    # 4. Higher High 105 (15) -> Trend Bullish (BOS of 100)
    # 5. Drop below 95 (20) -> CHOCH Bearish

    dates = [datetime(2023, 1, 1) + timedelta(minutes=i) for i in range(40)]
    prices = [90.0] * 40

    # 0-5: 90->100
    for i in range(6): prices[i] = 90 + i*2
    # 5-10: 100->95
    for i in range(6, 11): prices[i] = 100 - (i-5)
    # 10-15: 95->105
    for i in range(11, 16): prices[i] = 95 + (i-10)*2
    # 15-25: 105->85 (Crosses 95 at 20)
    for i in range(16, 26): prices[i] = 105 - (i-15)*2

    df = pd.DataFrame({
        "open": prices, "high": prices, "low": prices, "close": prices, "volume": 1000
    }, index=dates)

    ms = MarketStructure(swing_window=2)
    result = ms.analyze_structure(df)

    # We expect:
    # 1. BOS (Bullish) when crossing 100 (around index 13-14)
    # 2. CHOCH (Bearish) when crossing 95 (around index 20)

    assert result.trend == Trend.BEARISH

    # Filter for CHOCH
    chochs = [e for e in result.events if e.type == "CHOCH"]
    assert len(chochs) > 0
    last_choch = chochs[-1]
    assert last_choch.trend == Trend.BEARISH
    assert last_choch.price < 95

def test_smc_analyzer():
    """Test Multi-Timeframe Analyzer coordinator."""
    # Create minimal DF
    df = pd.DataFrame({"close": [100]}, index=[datetime.now()])
    data = {"1h": df, "4h": df}

    analyzer = SMCAnalyzer(swing_window=2)

    # Mock the internal analyzer to avoid running complex logic on empty data
    analyzer.structure_analyzer.analyze_structure = MagicMock(return_value="MOCKED_RESULT")

    results = analyzer.analyze(data)

    assert results["1h"] == "MOCKED_RESULT"
    assert results["4h"] == "MOCKED_RESULT"
