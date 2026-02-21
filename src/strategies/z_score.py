"""
Z-Score Strategy.

Logic:
- Calculate Z-Score of Close Price (period 20).
- Long if Z-Score < -threshold (Oversold).
- Short if Z-Score > threshold (Overbought).
- Exit when Z-Score crosses 0 (Mean Reversion).
"""

from typing import Any, Dict

import pandas as pd
import structlog

from src.config import Config
from .base import BaseStrategy
from .registry import register_strategy

logger = structlog.get_logger()


@register_strategy("z_score")
class ZScoreStrategy(BaseStrategy):
    """
    Mean Reversion Strategy using Z-Score.
    """

    def __init__(self, config: Config):
        super().__init__(config)

        # Parameters
        if hasattr(config.strategy, "z_score"):
             self.window = getattr(config.strategy.z_score, "window", 20)
             self.threshold = getattr(config.strategy.z_score, "threshold", 2.0)
        else:
             self.window = getattr(config.strategy, "z_score_window", 20)
             self.threshold = getattr(config.strategy, "z_score_threshold", 2.0)

        # State
        self.z_score = 0.0
        self.mean = 0.0
        self.std = 0.0

    @property
    def metadata(self) -> Dict[str, str]:
        return {
            "type": "mean_reversion",
            "risk": "medium",
            "timeframe": "15m",
        }

    def update(self, ohlcv: pd.DataFrame, current_position: str | None = None):
        """Calculate Z-Score."""
        self.ohlcv = ohlcv
        self.current_position = current_position

        if len(ohlcv) < self.window + 1:
            return

        close = ohlcv["close"]

        # Calculate Rolling Mean and Std
        rolling_mean = close.rolling(window=self.window).mean()
        rolling_std = close.rolling(window=self.window).std()

        self.mean = rolling_mean.iloc[-1]
        self.std = rolling_std.iloc[-1]

        current_price = close.iloc[-1]

        if self.std > 0:
            self.z_score = (current_price - self.mean) / self.std
        else:
            self.z_score = 0.0

    def should_long(self) -> bool:
        """Long if price is statistically cheap (Z-Score < -threshold)."""
        return self.z_score < -self.threshold

    def should_short(self) -> bool:
        """Short if price is statistically expensive (Z-Score > threshold)."""
        return self.z_score > self.threshold

    def should_exit(self) -> bool:
        """
        Exit when price reverts to mean (Z-Score crosses 0).
        Long: Z-Score becomes > 0
        Short: Z-Score becomes < 0
        """
        if self.current_position == "long":
            return self.z_score > 0
        elif self.current_position == "short":
            return self.z_score < 0
        return False

    def get_indicators(self) -> Dict[str, Any]:
        return {
            "z_score": self.z_score,
            "mean": self.mean,
            "std": self.std,
            "threshold": self.threshold,
        }
