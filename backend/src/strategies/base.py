"""
Base Strategy Interface for OmniTrader.

Defines the contract that all strategies must follow to be used in the bot.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List

import pandas as pd
import pandas_ta as ta
import structlog

from src.analysis.regime import MarketRegime
from src.config import Config

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
    """Generic result of strategy analysis."""

    signal: Signal
    reason: str
    indicators: Dict[str, Any] = field(default_factory=dict)


class BaseStrategy(ABC):
    """
    Abstract Base Class for all trading strategies.

    Strategies must implement:
    - __init__: Initialize parameters
    - update: Calculate indicators from OHLCV
    - should_long: Condition for entering long
    - should_short: Condition for entering short
    - should_exit: Condition for exiting current position
    """

    def __init__(self, config: Config):
        """
        Initialize strategy with configuration.

        Args:
            config: Global configuration object
        """
        self.config = config
        self.ohlcv: pd.DataFrame | None = None
        self.current_position: str | None = None
        self._last_entry_bar: Any = None
        self._last_entry_side: str | None = None

    @property
    @abstractmethod
    def metadata(self) -> Dict[str, str]:
        """
        Metadata about the strategy.

        Returns:
            Dict with keys like 'type' (trend/mean_reversion), 'risk' (low/medium/high)
        """
        pass

    @property
    @abstractmethod
    def valid_regimes(self) -> List[MarketRegime]:
        """
        List of market regimes where this strategy is safe to operate.

        Returns:
            List of MarketRegime enums (e.g. [MarketRegime.TRENDING])
        """
        pass

    @property
    def required_candles(self) -> int:
        """
        Minimum number of candles required by the strategy for calculation.
        Defaults to 100.
        """
        return 100

    @property
    def required_timeframes(self) -> list[str]:
        """
        List of timeframes required by the strategy.
        Defaults to the configured trading timeframe + bias confirmation TF.
        """
        tfs = [self.config.trading.timeframe]
        bias_enabled = getattr(self.config.strategy, "bias_confirmation", False)
        if bias_enabled:
            bias_tf = getattr(self.config.strategy, "bias_timeframe", "4h")
            if bias_tf not in tfs:
                tfs.append(bias_tf)
        return tfs

    @abstractmethod
    def update(self, ohlcv: pd.DataFrame, current_position: str | None = None):
        """
        Update strategy state with latest market data.

        Args:
            ohlcv: DataFrame with OHLCV data
            current_position: "long", "short", or None
        """
        pass

    @abstractmethod
    def should_long(self) -> bool:
        """Check if entry conditions for LONG are met."""
        pass

    @abstractmethod
    def should_short(self) -> bool:
        """Check if entry conditions for SHORT are met."""
        pass

    @abstractmethod
    def should_exit(self) -> bool:
        """Check if exit conditions are met for current position."""
        pass

    def update_config(self, config: Config):
        """
        Update strategy configuration.

        Args:
            config: New configuration object
        """
        self.config = config

    def analyze(
        self,
        market_data: Dict[str, pd.DataFrame],
        ohlcv: pd.DataFrame,
        current_position: str | None = None,
        market_trend: str = "neutral",
    ) -> StrategyResult:
        """
        Orchestrate strategy execution.

        Args:
            market_data: Dictionary mapping timeframe (str) to OHLCV DataFrame.
            current_position: Current position side ("long", "short", or None).

        1. Update state
        2. Check for signals
        3. Apply filters (trend)
        4. Return result
        """
        # Default behavior: Extract primary timeframe and pass to update()
        # Strategies requiring MTF should override analyze() or access other timeframes differently
        primary_tf = self.config.trading.timeframe
        ohlcv = market_data.get(primary_tf)

        if ohlcv is None:
            # Fallback or error if primary timeframe missing?
            # Should be guaranteed by main loop if required_timeframes is correct.
            # But let's be safe.
            logger.error("primary_timeframe_data_missing", timeframe=primary_tf)
            return StrategyResult(signal=Signal.HOLD, reason="Missing data")

        self.update(ohlcv, current_position)

        signal = Signal.HOLD
        reason = "No signal"
        trend_filter_enabled = getattr(
            self.config.strategy, "trend_filter_enabled", False
        )

        if current_position is None:
            if self.should_long():
                if trend_filter_enabled and market_trend == "bearish":
                    signal = Signal.HOLD
                    reason = "Trend Filter (Bearish) blocked Long"
                else:
                    signal = Signal.LONG
                    reason = "Strategy Entry Long"

            elif self.should_short():
                if trend_filter_enabled and market_trend == "bullish":
                    signal = Signal.HOLD
                    reason = "Trend Filter (Bullish) blocked Short"
                else:
                    signal = Signal.SHORT
                    reason = "Strategy Entry Short"

            if signal in (Signal.LONG, Signal.SHORT):
                min_bars = getattr(self.config.strategy, "min_bars_between_entries", 10)
                current_bar_index = ohlcv.index[-1]

                if (
                    self._last_entry_bar is not None
                    and self._last_entry_side == signal.value
                ):
                    if isinstance(ohlcv.index, pd.DatetimeIndex) and isinstance(
                        self._last_entry_bar, pd.Timestamp
                    ):
                        bars_since = len(ohlcv.loc[self._last_entry_bar :]) - 1
                    else:
                        try:
                            # Try to locate the position of the last entry bar in the current index
                            last_pos = ohlcv.index.get_loc(self._last_entry_bar)
                            current_pos = len(ohlcv) - 1
                            bars_since = current_pos - last_pos
                        except KeyError:
                            # If the last entry bar is no longer in the dataframe, it means it was a long time ago
                            bars_since = float("inf")

                    if bars_since < min_bars:
                        logger.info(
                            "entry_cooldown_active",
                            signal=signal.value,
                            bars_since=bars_since,
                            min_bars=min_bars,
                        )
                        reason = f"Entry Cooldown ({bars_since}/{min_bars} bars) blocked {signal.value}"
                        signal = Signal.HOLD

                # Update last entry tracker if we are actually emitting a signal
                if signal in (Signal.LONG, Signal.SHORT):
                    self._last_entry_bar = current_bar_index
                    self._last_entry_side = signal.value

        # Apply Bias Confirmation (Higher Timeframe)
        bias_enabled = getattr(self.config.strategy, "bias_confirmation", False)
        if bias_enabled and signal in (Signal.LONG, Signal.SHORT):
            bias_tf = getattr(self.config.strategy, "bias_timeframe", "4h")
            bias_ohlcv = market_data.get(bias_tf)
            if bias_ohlcv is not None:
                bias = self.check_trend(bias_ohlcv)
                if signal == Signal.LONG and bias != "bullish":
                    logger.info(
                        "bias_confirmation_rejected",
                        signal="LONG",
                        bias=bias,
                        tf=bias_tf,
                    )
                    signal = Signal.HOLD
                    reason = f"Bias Filter ({bias_tf}: {bias}) blocked Long"
                elif signal == Signal.SHORT and bias != "bearish":
                    logger.info(
                        "bias_confirmation_rejected",
                        signal="SHORT",
                        bias=bias,
                        tf=bias_tf,
                    )
                    signal = Signal.HOLD
                    reason = f"Bias Filter ({bias_tf}: {bias}) blocked Short"

        elif current_position == "long":
            if self.should_exit():
                signal = Signal.EXIT_LONG
                reason = "Strategy Exit Long"
        elif current_position == "short":
            if self.should_exit():
                signal = Signal.EXIT_SHORT
                reason = "Strategy Exit Short"

        return StrategyResult(
            signal=signal, reason=reason, indicators=self.get_indicators()
        )

    def get_indicators(self) -> Dict[str, Any]:
        """
        Return current indicator values for logging/display.

        Can be overridden by subclasses to provide specific indicators.
        """
        return {}

    def check_trend(self, ohlcv: pd.DataFrame, period: int = 200) -> str:
        """
        Determine market trend using EMA 200 (or specified period).

        Returns:
            "bullish" if Close > EMA, "bearish" if Close < EMA, "neutral" if undefined.
        """
        if len(ohlcv) < period:
            return "neutral"

        try:
            ema = ta.ema(ohlcv["close"], length=period)
            if ema is None or pd.isna(ema.iloc[-1]):
                return "neutral"

            current_close = ohlcv["close"].iloc[-1]
            current_ema = ema.iloc[-1]

            if current_close > current_ema:
                return "bullish"
            else:
                return "bearish"
        except Exception as e:
            logger.warning("trend_check_failed", error=str(e))
            return "neutral"
