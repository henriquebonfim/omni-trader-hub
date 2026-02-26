"""
SMC Market Structure Analysis.

Implements detection of:
- Swings (Fractal Highs/Lows)
- Break of Structure (BOS)
- Change of Character (CHoCH)
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional

import pandas as pd
import structlog

logger = structlog.get_logger()


class Trend(Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class SwingType(Enum):
    HIGH = "high"
    LOW = "low"


@dataclass
class Swing:
    index: int
    time: datetime
    price: float
    type: SwingType
    confirmed: bool = True  # Historic swings are confirmed


@dataclass
class StructureEvent:
    index: int
    time: datetime
    price: float
    type: str  # "BOS", "CHOCH"
    trend: Trend


@dataclass
class MarketStructureResult:
    trend: Trend
    swings: List[Swing]
    events: List[StructureEvent]
    last_swing_high: Optional[Swing] = None
    last_swing_low: Optional[Swing] = None
    last_bos: Optional[StructureEvent] = None
    last_choch: Optional[StructureEvent] = None


class MarketStructure:
    """
    Analyzes price data to identify market structure.
    """

    def __init__(self, swing_window: int = 5):
        """
        Args:
            swing_window: Number of bars on left/right to confirm a fractal.
        """
        self.swing_window = swing_window

    def detect_swings(self, df: pd.DataFrame) -> List[Swing]:
        """
        Identify fractal highs and lows.

        A High is a candle with N lower highs on left and right.
        A Low is a candle with N higher lows on left and right.
        """
        swings = []
        if len(df) < self.swing_window * 2 + 1:
            return swings

        # Convert to numpy for faster iteration? Or use pandas rolling.
        # Pandas rolling with center=True works for historical.
        # But for precise index matching, simple iteration is robust.

        # We only scan up to len - window because we need future data to confirm
        # the right side.
        for i in range(self.swing_window, len(df) - self.swing_window):
            current_high = df["high"].iloc[i]
            current_low = df["low"].iloc[i]

            # Check for Swing High
            is_high = True
            for j in range(1, self.swing_window + 1):
                if df["high"].iloc[i - j] > current_high or df["high"].iloc[i + j] > current_high:
                    is_high = False
                    break

            if is_high:
                swings.append(Swing(
                    index=i,
                    time=df.index[i], # Assuming DatetimeIndex
                    price=current_high,
                    type=SwingType.HIGH
                ))

            # Check for Swing Low
            is_low = True
            for j in range(1, self.swing_window + 1):
                if df["low"].iloc[i - j] < current_low or df["low"].iloc[i + j] < current_low:
                    is_low = False
                    break

            if is_low:
                swings.append(Swing(
                    index=i,
                    time=df.index[i],
                    price=current_low,
                    type=SwingType.LOW
                ))

        # Sort by index
        swings.sort(key=lambda x: x.index)
        return swings

    def analyze_structure(self, df: pd.DataFrame) -> MarketStructureResult:
        """
        Analyze BOS/CHoCH based on identified swings and price action.
        """
        swings = self.detect_swings(df)
        return self._analyze_events_robust(df, swings)

    def _analyze_events_robust(self, df: pd.DataFrame, swings: List[Swing]) -> MarketStructureResult:
        events = []
        trend = Trend.NEUTRAL

        # Structural points
        active_high: Optional[Swing] = None
        active_low: Optional[Swing] = None

        swing_iter = iter(swings)
        next_swing = next(swing_iter, None)

        last_bos_event: Optional[StructureEvent] = None
        last_choch_event: Optional[StructureEvent] = None

        # To handle "spamming", we track the ID of the last broken swing
        last_broken_high_idx = -1
        last_broken_low_idx = -1

        for i in range(len(df)):
            current_close = df["close"].iloc[i]
            current_time = df.index[i]

            # 1. Update active swings if they are confirmed at this index
            while next_swing and i >= next_swing.index + self.swing_window:
                if next_swing.type == SwingType.HIGH:
                    active_high = next_swing
                elif next_swing.type == SwingType.LOW:
                    active_low = next_swing
                next_swing = next(swing_iter, None)

            # 2. Logic
            if trend == Trend.NEUTRAL:
                if active_high and current_close > active_high.price:
                    trend = Trend.BULLISH
                    evt = StructureEvent(i, current_time, current_close, "BOS", trend)
                    events.append(evt)
                    last_bos_event = evt
                    last_broken_high_idx = active_high.index
                elif active_low and current_close < active_low.price:
                    trend = Trend.BEARISH
                    evt = StructureEvent(i, current_time, current_close, "BOS", trend)
                    events.append(evt)
                    last_bos_event = evt
                    last_broken_low_idx = active_low.index

            elif trend == Trend.BULLISH:
                # BOS: Break above active high
                if active_high and current_close > active_high.price:
                    if active_high.index != last_broken_high_idx:
                        # Valid new BOS
                        evt = StructureEvent(i, current_time, current_close, "BOS", trend)
                        events.append(evt)
                        last_bos_event = evt
                        last_broken_high_idx = active_high.index

                # CHoCH: Break below active low
                if active_low and current_close < active_low.price:
                    trend = Trend.BEARISH
                    evt = StructureEvent(i, current_time, current_close, "CHOCH", trend)
                    events.append(evt)
                    last_choch_event = evt
                    last_broken_low_idx = active_low.index

            elif trend == Trend.BEARISH:
                # BOS: Break below active low
                if active_low and current_close < active_low.price:
                    if active_low.index != last_broken_low_idx:
                        evt = StructureEvent(i, current_time, current_close, "BOS", trend)
                        events.append(evt)
                        last_bos_event = evt
                        last_broken_low_idx = active_low.index

                # CHoCH: Break above active high
                if active_high and current_close > active_high.price:
                    trend = Trend.BULLISH
                    evt = StructureEvent(i, current_time, current_close, "CHOCH", trend)
                    events.append(evt)
                    last_choch_event = evt
                    last_broken_high_idx = active_high.index

        return MarketStructureResult(
            trend=trend,
            swings=swings,
            events=events,
            last_swing_high=active_high,
            last_swing_low=active_low,
            last_bos=last_bos_event,
            last_choch=last_choch_event
        )
