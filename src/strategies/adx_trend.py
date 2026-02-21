"""
ADX Trend Strategy.

Logic:
- Long: ADX > threshold AND +DI > -DI (Strong Uptrend)
- Short: ADX > threshold AND -DI > +DI (Strong Downtrend)
- Exit: Trend Reversal (DI Cross)
"""

from typing import Any, Dict

import pandas as pd
import pandas_ta as ta
import structlog

from src.config import Config

from .base import BaseStrategy
from .registry import register_strategy

logger = structlog.get_logger()


@register_strategy("adx_trend")
class ADXTrendStrategy(BaseStrategy):
    """
    ADX Trend Following Strategy.
    """

    def __init__(self, config: Config):
        super().__init__(config)

        # Default values if not in config
        # Expecting config to have strategy.adx section or just strategy fields
        # Trying both for flexibility
        if hasattr(config.strategy, "adx"):
            self.adx_period = getattr(config.strategy.adx, "period", 14)
            self.adx_threshold = getattr(config.strategy.adx, "threshold", 25)
        else:
            self.adx_period = getattr(config.strategy, "adx_period", 14)
            self.adx_threshold = getattr(config.strategy, "adx_threshold", 25)

        self.adx = 0.0
        self.plus_di = 0.0
        self.minus_di = 0.0

    @property
    def metadata(self) -> Dict[str, str]:
        return {
            "type": "trend_following",
            "risk": "low",
            "timeframe": "1h",
        }

    def update(self, ohlcv: pd.DataFrame, current_position: str | None = None):
        """Calculate ADX/DMI indicators."""
        self.ohlcv = ohlcv
        self.current_position = current_position

        if len(ohlcv) < self.adx_period + 20:
            return

        try:
            # Calculate ADX
            adx_df = ta.adx(
                ohlcv["high"], ohlcv["low"], ohlcv["close"], length=self.adx_period
            )

            if adx_df is None or adx_df.empty:
                return

            # Column names: ADX_14, DMP_14, DMN_14
            adx_col = f"ADX_{self.adx_period}"
            dmp_col = f"DMP_{self.adx_period}"
            dmn_col = f"DMN_{self.adx_period}"

            if adx_col in adx_df.columns:
                self.adx = adx_df[adx_col].iloc[-1]
                self.plus_di = adx_df[dmp_col].iloc[-1]
                self.minus_di = adx_df[dmn_col].iloc[-1]
            else:
                logger.warning("adx_columns_missing", columns=adx_df.columns)

        except Exception as e:
            logger.error("adx_calculation_failed", error=str(e))

    def should_long(self) -> bool:
        return (self.adx > self.adx_threshold) and (self.plus_di > self.minus_di)

    def should_short(self) -> bool:
        return (self.adx > self.adx_threshold) and (self.minus_di > self.plus_di)

    def should_exit(self) -> bool:
        if self.current_position == "long":
            return self.plus_di < self.minus_di
        elif self.current_position == "short":
            return self.minus_di < self.plus_di
        return False

    def get_indicators(self) -> Dict[str, Any]:
        return {
            "adx": self.adx,
            "plus_di": self.plus_di,
            "minus_di": self.minus_di,
            "threshold": self.adx_threshold,
        }
