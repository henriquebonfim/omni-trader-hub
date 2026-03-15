from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from src.intelligence.regime import MarketRegime, RegimeClassifier


@pytest.fixture
def sample_ohlcv():
    # Provide a minimal length of 28 (14 * 2) rows to pass length check
    length = 30
    df = pd.DataFrame(
        {
            "high": np.linspace(10, 20, length),
            "low": np.linspace(5, 15, length),
            "close": np.linspace(8, 18, length),
        }
    )
    return df


@patch("src.intelligence.regime.ta.sma")
@patch("src.intelligence.regime.ta.atr")
@patch("src.intelligence.regime.ta.adx")
def test_hysteresis_trending(mock_adx, mock_atr, mock_sma, sample_ohlcv):
    classifier = RegimeClassifier(hysteresis_enabled=True)

    # Mock ATR to ensure not volatile
    mock_atr.return_value = pd.Series([1.0] * 30)
    mock_sma.return_value = pd.Series([1.0] * 30)

    # Step 1: ADX = 25 -> Not TRENDING yet (requires > 28)
    mock_adx.return_value = pd.DataFrame({"ADX_14": [25.0] * 30})
    regime = classifier.analyze(sample_ohlcv)
    assert regime == MarketRegime.RANGING
    assert classifier.current_regime == MarketRegime.RANGING

    # Step 2: ADX = 29 -> Enters TRENDING
    mock_adx.return_value = pd.DataFrame({"ADX_14": [29.0] * 30})
    regime = classifier.analyze(sample_ohlcv)
    assert regime == MarketRegime.TRENDING
    assert classifier.current_regime == MarketRegime.TRENDING

    # Step 3: ADX drops to 25 -> Stays TRENDING because >= 22
    mock_adx.return_value = pd.DataFrame({"ADX_14": [25.0] * 30})
    regime = classifier.analyze(sample_ohlcv)
    assert regime == MarketRegime.TRENDING
    assert classifier.current_regime == MarketRegime.TRENDING

    # Step 4: ADX drops to 23 -> Stays TRENDING
    mock_adx.return_value = pd.DataFrame({"ADX_14": [23.0] * 30})
    regime = classifier.analyze(sample_ohlcv)
    assert regime == MarketRegime.TRENDING

    # Step 5: ADX drops to 21 -> Exits TRENDING (to RANGING)
    mock_adx.return_value = pd.DataFrame({"ADX_14": [21.0] * 30})
    regime = classifier.analyze(sample_ohlcv)
    assert regime == MarketRegime.RANGING


@patch("src.intelligence.regime.ta.sma")
@patch("src.intelligence.regime.ta.atr")
@patch("src.intelligence.regime.ta.adx")
def test_hysteresis_volatile(mock_adx, mock_atr, mock_sma, sample_ohlcv):
    classifier = RegimeClassifier(hysteresis_enabled=True)

    # Mock ADX to ensure not trending
    mock_adx.return_value = pd.DataFrame({"ADX_14": [10.0] * 30})

    # Set baseline ATR to 1.0
    mock_sma.return_value = pd.Series([1.0] * 30)

    # Step 1: ATR = 1.6 -> Not VOLATILE yet (requires > 1.7)
    mock_atr.return_value = pd.Series([1.6] * 30)
    regime = classifier.analyze(sample_ohlcv)
    assert regime == MarketRegime.RANGING

    # Step 2: ATR = 1.8 -> Enters VOLATILE
    mock_atr.return_value = pd.Series([1.8] * 30)
    regime = classifier.analyze(sample_ohlcv)
    assert regime == MarketRegime.VOLATILE

    # Step 3: ATR drops to 1.4 -> Stays VOLATILE because >= 1.3
    mock_atr.return_value = pd.Series([1.4] * 30)
    regime = classifier.analyze(sample_ohlcv)
    assert regime == MarketRegime.VOLATILE

    # Step 4: ATR drops to 1.2 -> Exits VOLATILE
    mock_atr.return_value = pd.Series([1.2] * 30)
    regime = classifier.analyze(sample_ohlcv)
    assert regime == MarketRegime.RANGING


@patch("src.intelligence.regime.ta.sma")
@patch("src.intelligence.regime.ta.atr")
@patch("src.intelligence.regime.ta.adx")
def test_no_hysteresis(mock_adx, mock_atr, mock_sma, sample_ohlcv):
    classifier = RegimeClassifier(
        hysteresis_enabled=False, adx_threshold=25, atr_multiplier=1.5
    )

    # Mock SMA ATR to 1.0
    mock_sma.return_value = pd.Series([1.0] * 30)

    # Test ADX > 25 -> TRENDING
    mock_atr.return_value = pd.Series([1.0] * 30)
    mock_adx.return_value = pd.DataFrame({"ADX_14": [26.0] * 30})
    regime = classifier.analyze(sample_ohlcv)
    assert regime == MarketRegime.TRENDING

    # Test ADX <= 25 -> RANGING
    mock_adx.return_value = pd.DataFrame({"ADX_14": [25.0] * 30})
    regime = classifier.analyze(sample_ohlcv)
    assert regime == MarketRegime.RANGING

    # Test ATR > 1.5 -> VOLATILE
    mock_adx.return_value = pd.DataFrame({"ADX_14": [20.0] * 30})
    mock_atr.return_value = pd.Series([1.6] * 30)
    regime = classifier.analyze(sample_ohlcv)
    assert regime == MarketRegime.VOLATILE

    # Test ATR <= 1.5 -> RANGING
    mock_atr.return_value = pd.Series([1.5] * 30)
    regime = classifier.analyze(sample_ohlcv)
    assert regime == MarketRegime.RANGING
