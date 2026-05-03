"""
EMA + Volume Strategy.

Logic:
- Long if Fast EMA crosses above Slow EMA and Volume > threshold.
- Short if Fast EMA crosses below Slow EMA and Volume > threshold.
- Exit on opposite crossover.
"""

from typing import Any

import pandas as pd
import structlog

from src.domain import indicators
from src.config import Config
from src.domain.intelligence.regime import MarketRegime

from .base import BaseStrategy
from .registry import register_strategy

logger = structlog.get_logger()


@register_strategy("ema_volume")
class EMAVolumeStrategy(BaseStrategy):
    """
    EMA Crossover + Volume Confirmation Strategy.
    """

    def __init__(self, config: Config):
        super().__init__(config)
        self.ema_fast_period = config.strategy.ema_fast
        self.ema_slow_period = config.strategy.ema_slow
        self.volume_sma_period = config.strategy.volume_sma
        self.volume_threshold = config.strategy.volume_threshold

        # Internal state
        self.ema_fast = 0.0
        self.ema_slow = 0.0
        self.volume_ratio = 0.0
        self.bullish_cross = False
        self.bearish_cross = False
        self.high_volume = False

    def update_config(self, config: Config):
        """Update strategy configuration."""
        super().update_config(config)
        self.ema_fast_period = config.strategy.ema_fast
        self.ema_slow_period = config.strategy.ema_slow
        self.volume_sma_period = config.strategy.volume_sma
        self.volume_threshold = config.strategy.volume_threshold
        logger.info(
            "strategy_config_updated",
            ema_fast=self.ema_fast_period,
            ema_slow=self.ema_slow_period,
            volume_sma=self.volume_sma_period,
            volume_threshold=self.volume_threshold,
        )

    @property
    def metadata(self) -> dict[str, str]:
        return {
            "type": "trend_following",
            "risk": "medium",
            "timeframe": "15m",  # Default recommended
        }

    @property
    def valid_regimes(self) -> list[MarketRegime]:
        return [MarketRegime.TRENDING]

    @property
    def required_candles(self) -> int:
        return max(self.ema_slow_period, self.volume_sma_period) + 2

    def update(self, ohlcv: pd.DataFrame, current_position: str | None = None):
        """Calculate indicators and update state."""
        self.ohlcv = ohlcv
        self.current_position = current_position

        if len(ohlcv) < self.required_candles:
            return

        # Calculate indicators
        ema_fast_series = indicators.ema(ohlcv["close"], length=self.ema_fast_period)
        ema_slow_series = indicators.ema(ohlcv["close"], length=self.ema_slow_period)
        volume_sma_series = indicators.sma(
            ohlcv["volume"], length=self.volume_sma_period
        )

        # Store current values
        self.ema_fast = ema_fast_series.iloc[-1]
        self.ema_slow = ema_slow_series.iloc[-1]

        curr_volume = ohlcv["volume"].iloc[-1]
        avg_volume = (
            volume_sma_series.iloc[-1] if volume_sma_series.iloc[-1] > 0 else 1.0
        )
        self.volume_ratio = curr_volume / avg_volume

        # Detect crossovers (using previous values)
        prev_ema_fast = ema_fast_series.iloc[-2]
        prev_ema_slow = ema_slow_series.iloc[-2]
        curr_ema_fast = self.ema_fast
        curr_ema_slow = self.ema_slow

        self.bullish_cross = (prev_ema_fast <= prev_ema_slow) and (
            curr_ema_fast > curr_ema_slow
        )
        self.bearish_cross = (prev_ema_fast >= prev_ema_slow) and (
            curr_ema_fast < curr_ema_slow
        )
        self.high_volume = self.volume_ratio >= self.volume_threshold

    def should_long(self) -> bool:
        return self.bullish_cross and self.high_volume

    def should_short(self) -> bool:
        return self.bearish_cross and self.high_volume

    def should_exit(self) -> bool:
        if self.current_position == "long":
            return self.bearish_cross
        elif self.current_position == "short":
            return self.bullish_cross
        return False

    def get_indicators(self) -> dict[str, Any]:
        return {
            "ema_fast": self.ema_fast,
            "ema_slow": self.ema_slow,
            "volume_ratio": self.volume_ratio,
            "bullish_cross": self.bullish_cross,
            "bearish_cross": self.bearish_cross,
        }
