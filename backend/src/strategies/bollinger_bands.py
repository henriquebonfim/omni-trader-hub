"""
Bollinger Bands Mean Reversion Strategy.

Logic:
- Long: Price < Lower Band (Oversold) + RSI < 30
- Short: Price > Upper Band (Overbought) + RSI > 70
- Exit: Price crosses Middle Band (Mean Reversion)
"""

from typing import Any, Dict

import pandas as pd
import pandas_ta as ta
import structlog

from src.config import Config

from .base import BaseStrategy
from .registry import register_strategy

logger = structlog.get_logger()


@register_strategy("bollinger_bands")
class BollingerBandsStrategy(BaseStrategy):
    """
    Mean Reversion Strategy using Bollinger Bands + RSI.
    """

    def __init__(self, config: Config):
        super().__init__(config)

        # Parameters
        if hasattr(config.strategy, "bollinger_bands"):
            self.bb_length = getattr(config.strategy.bollinger_bands, "length", 20)
            self.bb_std = getattr(config.strategy.bollinger_bands, "std", 2.0)
            self.rsi_length = getattr(config.strategy.bollinger_bands, "rsi_length", 14)
            self.rsi_lower = getattr(config.strategy.bollinger_bands, "rsi_lower", 30)
            self.rsi_upper = getattr(config.strategy.bollinger_bands, "rsi_upper", 70)
        else:
            # Fallback to simple attributes if nested config not used
            self.bb_length = getattr(config.strategy, "bb_length", 20)
            self.bb_std = getattr(config.strategy, "bb_std", 2.0)
            self.rsi_length = getattr(config.strategy, "rsi_length", 14)
            self.rsi_lower = getattr(config.strategy, "rsi_lower", 30)
            self.rsi_upper = getattr(config.strategy, "rsi_upper", 70)

        # State
        self.upper_band = 0.0
        self.mid_band = 0.0
        self.lower_band = 0.0
        self.rsi = 50.0
        self.current_price = 0.0

    @property
    def metadata(self) -> Dict[str, str]:
        return {
            "type": "mean_reversion",
            "risk": "medium",
            "timeframe": "15m",
            "description": "Mean reversion using BB and RSI",
        }

    @property
    def required_candles(self) -> int:
        return max(self.bb_length, self.rsi_length) + 1

    def update(self, ohlcv: pd.DataFrame, current_position: str | None = None):
        """Calculate BB and RSI."""
        self.ohlcv = ohlcv
        self.current_position = current_position

        if len(ohlcv) < max(self.bb_length, self.rsi_length) + 1:
            return

        self.current_price = ohlcv["close"].iloc[-1]

        try:
            # Calculate Bollinger Bands
            bb = ta.bbands(ohlcv["close"], length=self.bb_length, std=self.bb_std)
            # pandas-ta returns column names like BBL_20_2.0, BBM_20_2.0, BBU_20_2.0
            # Need to find them dynamically or construct the string
            if bb is not None and not bb.empty:
                # Construct column names
                l_col = f"BBL_{self.bb_length}_{self.bb_std}"
                m_col = f"BBM_{self.bb_length}_{self.bb_std}"
                u_col = f"BBU_{self.bb_length}_{self.bb_std}"

                # Check if columns exist (pandas-ta sometimes uses different naming for floats)
                # But typically it respects the input types. 2.0 -> 2.0

                if l_col in bb.columns:
                    self.lower_band = bb[l_col].iloc[-1]
                    self.mid_band = bb[m_col].iloc[-1]
                    self.upper_band = bb[u_col].iloc[-1]
                else:
                    # Fallback: try to find columns starting with BBL, BBM, BBU
                    cols = bb.columns
                    for col in cols:
                        if col.startswith("BBL"):
                            self.lower_band = bb[col].iloc[-1]
                        if col.startswith("BBM"):
                            self.mid_band = bb[col].iloc[-1]
                        if col.startswith("BBU"):
                            self.upper_band = bb[col].iloc[-1]

            # Calculate RSI
            rsi_series = ta.rsi(ohlcv["close"], length=self.rsi_length)
            if rsi_series is not None and not rsi_series.empty:
                self.rsi = rsi_series.iloc[-1]

        except Exception as e:
            logger.error("bb_strategy_error", error=str(e))

    def should_long(self) -> bool:
        """Long if price < Lower Band AND RSI < Lower Threshold (Oversold)."""
        if self.lower_band == 0:
            return False
        return (self.current_price < self.lower_band) and (self.rsi < self.rsi_lower)

    def should_short(self) -> bool:
        """Short if price > Upper Band AND RSI > Upper Threshold (Overbought)."""
        if self.upper_band == 0:
            return False
        return (self.current_price > self.upper_band) and (self.rsi > self.rsi_upper)

    def should_exit(self) -> bool:
        """
        Exit when price reverts to mean (Middle Band).
        Long: Price crosses above Mid Band
        Short: Price crosses below Mid Band
        """
        if self.mid_band == 0:
            return False

        if self.current_position == "long":
            return self.current_price > self.mid_band
        elif self.current_position == "short":
            return self.current_price < self.mid_band
        return False

    def get_indicators(self) -> Dict[str, Any]:
        return {
            "rsi": self.rsi,
            "upper_band": self.upper_band,
            "mid_band": self.mid_band,
            "lower_band": self.lower_band,
        }
