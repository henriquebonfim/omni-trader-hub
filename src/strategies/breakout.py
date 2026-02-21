"""
Donchian Channel Breakout Strategy.

Logic:
- Long: Price > Highest High of last N candles (Breakout)
- Short: Price < Lowest Low of last N candles (Breakdown)
- Exit: Price touches Middle Band (Trailing Stop logic)
"""

from typing import Any, Dict

import pandas as pd
import pandas_ta as ta
import structlog

from src.config import Config
from .base import BaseStrategy
from .registry import register_strategy

logger = structlog.get_logger()


@register_strategy("breakout")
class BreakoutStrategy(BaseStrategy):
    """
    Trend Following Strategy using Donchian Channels.
    """

    def __init__(self, config: Config):
        super().__init__(config)

        # Parameters
        if hasattr(config.strategy, "breakout"):
            self.donchian_period = getattr(config.strategy.breakout, "period", 20)
        else:
            self.donchian_period = getattr(config.strategy, "donchian_period", 20)

        # State
        self.upper_channel = 0.0
        self.lower_channel = 0.0
        self.mid_channel = 0.0
        self.current_price = 0.0

    @property
    def metadata(self) -> Dict[str, str]:
        return {
            "type": "trend_following",
            "risk": "high",
            "timeframe": "1h",
            "description": "Donchian Channel Breakout"
        }

    def update(self, ohlcv: pd.DataFrame, current_position: str | None = None):
        """Calculate Donchian Channels."""
        self.ohlcv = ohlcv
        self.current_position = current_position

        if len(ohlcv) < self.donchian_period + 1:
            return

        self.current_price = ohlcv["close"].iloc[-1]

        try:
            # Calculate Donchian Channels
            donchian = ta.donchian(ohlcv["high"], ohlcv["low"], lower_length=self.donchian_period, upper_length=self.donchian_period)

            if donchian is not None and not donchian.empty:
                # Find columns dynamically or by construction
                l_col = f"DCL_{self.donchian_period}_{self.donchian_period}"
                m_col = f"DCM_{self.donchian_period}_{self.donchian_period}"
                u_col = f"DCU_{self.donchian_period}_{self.donchian_period}"

                # Handle pandas-ta variations.
                # Sometimes it returns columns without period if it's default? No, usually follows pattern.
                if l_col in donchian.columns:
                    self.lower_channel = donchian[l_col].iloc[-1]
                    self.mid_channel = donchian[m_col].iloc[-1]
                    self.upper_channel = donchian[u_col].iloc[-1]
                else:
                    # Fallback check
                    for col in donchian.columns:
                        if col.startswith("DCL"): self.lower_channel = donchian[col].iloc[-1]
                        if col.startswith("DCM"): self.mid_channel = donchian[col].iloc[-1]
                        if col.startswith("DCU"): self.upper_channel = donchian[col].iloc[-1]

        except Exception as e:
            logger.error("breakout_strategy_error", error=str(e))

    def should_long(self) -> bool:
        """Long if price breaks above the Upper Channel."""
        if self.upper_channel == 0: return False
        return self.current_price > self.upper_channel

    def should_short(self) -> bool:
        """Short if price breaks below the Lower Channel."""
        if self.lower_channel == 0: return False
        return self.current_price < self.lower_channel

    def should_exit(self) -> bool:
        """
        Exit when trend weakens (Price crosses Mid Channel).
        Long: Price < Mid Channel
        Short: Price > Mid Channel
        """
        if self.mid_channel == 0: return False

        if self.current_position == "long":
            return self.current_price < self.mid_channel
        elif self.current_position == "short":
            return self.current_price > self.mid_channel
        return False

    def get_indicators(self) -> Dict[str, Any]:
        return {
            "upper_channel": self.upper_channel,
            "mid_channel": self.mid_channel,
            "lower_channel": self.lower_channel,
        }
