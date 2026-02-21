"""
EMA + Volume trading strategy.

Entry signals:
- LONG: EMA(fast) crosses above EMA(slow) + Volume > threshold
- SHORT: EMA(fast) crosses below EMA(slow) + Volume > threshold

Exit signals:
- Opposite EMA cross
- Stop loss / Take profit (handled by exchange orders)
"""

from dataclasses import dataclass
from enum import Enum

import pandas as pd
import pandas_ta as ta
import structlog

from .config import get_config

logger = structlog.get_logger()


class Signal(Enum):
    """Trading signal types."""

    HOLD = "hold"
    LONG = "long"
    SHORT = "short"
    EXIT_LONG = "exit_long"
    EXIT_SHORT = "exit_short"


@dataclass
class StrategyResult:
    """Result of strategy analysis."""

    signal: Signal
    ema_fast: float
    ema_slow: float
    volume: float
    volume_avg: float
    volume_ratio: float
    reason: str


class EMAVolumeStrategy:
    """
    EMA Crossover + Volume Confirmation Strategy.

    This strategy generates signals when:
    1. Fast EMA crosses slow EMA (trend change)
    2. Volume is above average (confirmation)
    """

    def __init__(self):
        config = get_config()
        self.ema_fast_period = config.strategy.ema_fast
        self.ema_slow_period = config.strategy.ema_slow
        self.volume_sma_period = config.strategy.volume_sma
        self.volume_threshold = config.strategy.volume_threshold

    def analyze(
        self, ohlcv: pd.DataFrame, current_position: str | None = None
    ) -> StrategyResult:
        """
        Analyze market data and generate trading signal.

        Args:
            ohlcv: DataFrame with OHLCV data (needs at least ema_slow + 2 rows)
            current_position: "long", "short", or None

        Returns:
            StrategyResult with signal and indicator values
        """
        if len(ohlcv) < self.ema_slow_period + 2:
            return StrategyResult(
                signal=Signal.HOLD,
                ema_fast=0,
                ema_slow=0,
                volume=0,
                volume_avg=0,
                volume_ratio=0,
                reason="Insufficient data",
            )

        # Calculate indicators
        ema_fast = ta.ema(ohlcv["close"], length=self.ema_fast_period)
        ema_slow = ta.ema(ohlcv["close"], length=self.ema_slow_period)
        volume_sma = ta.sma(ohlcv["volume"], length=self.volume_sma_period)

        # Get current and previous values
        curr_ema_fast = ema_fast.iloc[-1]
        curr_ema_slow = ema_slow.iloc[-1]
        prev_ema_fast = ema_fast.iloc[-2]
        prev_ema_slow = ema_slow.iloc[-2]
        curr_volume = ohlcv["volume"].iloc[-1]
        avg_volume = volume_sma.iloc[-1]

        # Calculate volume ratio
        volume_ratio = curr_volume / avg_volume if avg_volume > 0 else 0
        high_volume = volume_ratio >= self.volume_threshold

        # Detect crossovers
        bullish_cross = (prev_ema_fast <= prev_ema_slow) and (
            curr_ema_fast > curr_ema_slow
        )
        bearish_cross = (prev_ema_fast >= prev_ema_slow) and (
            curr_ema_fast < curr_ema_slow
        )

        # Determine signal
        signal = Signal.HOLD
        reason = "No signal"

        # Entry signals (only when no position)
        if current_position is None:
            if bullish_cross and high_volume:
                signal = Signal.LONG
                reason = f"Bullish EMA cross with volume {volume_ratio:.2f}x avg"
            elif bearish_cross and high_volume:
                signal = Signal.SHORT
                reason = f"Bearish EMA cross with volume {volume_ratio:.2f}x avg"
            elif bullish_cross:
                reason = f"Bullish cross but low volume ({volume_ratio:.2f}x)"
            elif bearish_cross:
                reason = f"Bearish cross but low volume ({volume_ratio:.2f}x)"

        # Exit signals (when in position)
        elif current_position == "long":
            if bearish_cross:
                signal = Signal.EXIT_LONG
                reason = "Bearish EMA cross - exit long"
        elif current_position == "short":
            if bullish_cross:
                signal = Signal.EXIT_SHORT
                reason = "Bullish EMA cross - exit short"

        result = StrategyResult(
            signal=signal,
            ema_fast=curr_ema_fast,
            ema_slow=curr_ema_slow,
            volume=curr_volume,
            volume_avg=avg_volume,
            volume_ratio=volume_ratio,
            reason=reason,
        )

        logger.debug(
            "strategy_analyzed",
            signal=signal.value,
            ema_fast=f"{curr_ema_fast:.2f}",
            ema_slow=f"{curr_ema_slow:.2f}",
            volume_ratio=f"{volume_ratio:.2f}",
            reason=reason,
        )

        return result

    def get_indicator_summary(self, ohlcv: pd.DataFrame) -> dict:
        """Get current indicator values for display."""
        ema_fast = ta.ema(ohlcv["close"], length=self.ema_fast_period)
        ema_slow = ta.ema(ohlcv["close"], length=self.ema_slow_period)
        volume_sma = ta.sma(ohlcv["volume"], length=self.volume_sma_period)

        return {
            "price": ohlcv["close"].iloc[-1],
            "ema_fast": ema_fast.iloc[-1],
            "ema_slow": ema_slow.iloc[-1],
            "ema_trend": (
                "bullish" if ema_fast.iloc[-1] > ema_slow.iloc[-1] else "bearish"
            ),
            "volume": ohlcv["volume"].iloc[-1],
            "volume_avg": volume_sma.iloc[-1],
            "volume_ratio": (
                ohlcv["volume"].iloc[-1] / volume_sma.iloc[-1]
                if volume_sma.iloc[-1] > 0
                else 0
            ),
        }
