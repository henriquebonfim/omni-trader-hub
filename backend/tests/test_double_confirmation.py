import pandas as pd
import pytest

from src.analysis.regime import MarketRegime
from src.config import Config
from src.strategies.base import BaseStrategy, Signal


class MockStrategy(BaseStrategy):
    @property
    def metadata(self):
        return {"type": "trend", "risk": "low"}

    @property
    def valid_regimes(self):
        return [MarketRegime.TRENDING]

    def update(self, ohlcv, current_position=None):
        self.ohlcv = ohlcv

    def should_long(self):
        return self.ohlcv["close"].iloc[-1] > self.ohlcv["open"].iloc[-1]

    def should_short(self):
        return self.ohlcv["close"].iloc[-1] < self.ohlcv["open"].iloc[-1]

    def should_exit(self):
        return False

@pytest.fixture
def mock_config():
    config_data = {
        "trading": {"symbol": "BTC/USDT", "timeframe": "15min"},
        "strategy": {
            "bias_confirmation": True,
            "bias_timeframe": "4h"
        }
    }
    return Config(config_data)

def create_ohlcv(prices):
    return pd.DataFrame({
        "open": prices,
        "high": [p + 1 for p in prices],
        "low": [p - 1 for p in prices],
        "close": [p + 0.5 for p in prices if p == prices[-1]] + [p for p in prices[:-1]], # make last candle bullish if close > open
        "volume": [100] * len(prices)
    }, index=pd.date_range("2021-01-01", periods=len(prices), freq="15min"))

def test_signal_bias_confirmation_long_blocked(mock_config):
    # Mock HTF (4h) as bearish
    # EMA 200 on 4h. Let's say prices are way below 100
    htf_prices = [50] * 210
    htf_df = pd.DataFrame({
        "open": htf_prices,
        "high": htf_prices,
        "low": htf_prices,
        "close": htf_prices,
        "volume": [100] * 210
    }, index=pd.date_range("2021-01-01", periods=210, freq="4h"))

    # Mock LTF (15m) as bullish signal (close > open)
    ltf_df = pd.DataFrame({
        "open": [40] * 10,
        "high": [42] * 10,
        "low": [38] * 10,
        "close": [41] * 10, # Bullish candle
        "volume": [100] * 10
    }, index=pd.date_range("2021-01-01", periods=10, freq="15min"))

    strategy = MockStrategy(mock_config)
    market_data = {"15min": ltf_df, "4h": htf_df}

    result = strategy.analyze(market_data, ltf_df)

    # HTF is bearish (avg 50 < EMA 100? No, let's see. EMA 200 of 50 is 50. Close is 50.
    # check_trend uses Close > EMA for bullish, else bearish.
    # So if close == EMA, it's bearish? Let's check base.py:230
    # if current_close > current_ema: return "bullish" else: return "bearish"
    # So 50 > 50 is False -> bearish.

    assert result.signal == Signal.HOLD
    assert "Bias Filter (4h: bearish) blocked Long" in result.reason

def test_signal_bias_confirmation_long_allowed(mock_config):
    # Mock HTF (4h) as bullish
    htf_prices = [150] * 210
    # EMA 200 of 150 is 150? No, let's make it clearly bullish.
    # Start at 100, end at 150.
    htf_prices = list(range(100, 310))
    htf_df = pd.DataFrame({
        "open": htf_prices,
        "high": htf_prices,
        "low": htf_prices,
        "close": htf_prices,
        "volume": [100] * 210
    }, index=pd.date_range("2021-01-01", periods=210, freq="4h"))

    ltf_df = pd.DataFrame({
        "open": [40] * 10,
        "high": [42] * 10,
        "low": [38] * 10,
        "close": [41] * 10,
        "volume": [100] * 10
    }, index=pd.date_range("2021-01-01", periods=10, freq="15min"))

    strategy = MockStrategy(mock_config)
    market_data = {"15min": ltf_df, "4h": htf_df}

    result = strategy.analyze(market_data, ltf_df)

    # Close 309 > EMA 200 -> bullish
    assert result.signal == Signal.LONG
    assert result.reason == "Strategy Entry Long"
