"""
Base Strategy Interface for OmniTrader.

Defines the contract that all strategies must follow to be used in the bot.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import pandas as pd
import structlog

from src.domain import indicators
from src.config import Config
from src.domain.intelligence.regime import MarketRegime
from src.domain.strategy.smc.analysis import SMCAnalyzer
from src.domain.strategy.smc.structure import Trend

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
    indicators: dict[str, Any] = field(default_factory=dict)


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
        self._last_exit_time: pd.Timestamp | None = None

    @property
    @abstractmethod
    def metadata(self) -> dict[str, str]:
        """
        Metadata about the strategy.

        Returns:
            Dict with keys like 'type' (trend/mean_reversion), 'risk' (low/medium/high)
        """
        pass

    @property
    @abstractmethod
    def valid_regimes(self) -> list[MarketRegime]:
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
        Defaults to the configured trading timeframe + bias confirmation TF + SMC TF.
        """
        tfs = [self.config.trading.timeframe]
        bias_enabled = getattr(self.config.strategy, "bias_confirmation", False)
        if bias_enabled:
            bias_tf = getattr(self.config.strategy, "bias_timeframe", "4h")
            if bias_tf not in tfs:
                tfs.append(bias_tf)

        smc_enabled = getattr(self.config.strategy, "smc_confirmation", False)
        if smc_enabled:
            smc_tf = getattr(self.config.strategy, "smc_timeframe", "4h")
            if smc_tf not in tfs:
                tfs.append(smc_tf)

        return tfs

    @abstractmethod
    def update(self, ohlcv: pd.DataFrame, current_position: str | None = None):
        """
        Update strategy state with latest market data.

        Args:
            ohlcv: DataFrame with OHLCV data
            current_position: "long", "short", or None
        """
        self.current_position = current_position
        self.ohlcv = ohlcv

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
        market_data: dict[str, pd.DataFrame],
        ohlcv: pd.DataFrame,
        current_position: str | None = None,
        market_trend: str = "neutral",
    ) -> StrategyResult:
        """
        Orchestrate strategy execution.
        """
        primary_tf = self.config.trading.timeframe
        ohlcv = market_data.get(primary_tf)

        if ohlcv is None:
            logger.error("primary_timeframe_data_missing", timeframe=primary_tf)
            return StrategyResult(signal=Signal.HOLD, reason="Missing data")

        # Track exit time for cooldowns before update() potentially changes state
        if self.current_position is not None and current_position is None:
            self._last_exit_time = ohlcv.index[-1]
            logger.info("strategy_exit_detected", timestamp=self._last_exit_time)

        self.update(ohlcv, current_position)

        signal = Signal.HOLD
        reason = "No signal"

        if current_position is None:
            signal, reason = self._get_entry_signal(ohlcv, market_trend)
            if signal != Signal.HOLD:
                signal, reason = self._apply_entry_filters(signal, reason, market_data)
        else:
            signal, reason = self._get_exit_signal()

        return StrategyResult(
            signal=signal, reason=reason, indicators=self.get_indicators()
        )

    def _get_entry_signal(self, ohlcv: pd.DataFrame, market_trend: str) -> tuple[Signal, str]:
        """Calculate potential entry signals and apply primary trend filter."""
        signal = Signal.HOLD
        reason = "No signal"

        trend_filter_enabled = self.config.strategy.trend_filter_enabled

        if self.should_long():
            if trend_filter_enabled and market_trend == "bearish":
                reason = "Trend Filter (Bearish) blocked Long"
            else:
                signal = Signal.LONG
                reason = "Strategy Entry Long"
        elif self.should_short():
            if trend_filter_enabled and market_trend == "bullish":
                reason = "Trend Filter (Bullish) blocked Short"
            else:
                signal = Signal.SHORT
                reason = "Strategy Entry Short"

        if signal != Signal.HOLD:
            signal, reason = self._check_entry_cooldown(signal, reason, ohlcv)

        if signal != Signal.HOLD:
            signal, reason = self._check_time_cooldown(signal, reason, ohlcv)

        return signal, reason

    def _check_time_cooldown(
        self, signal: Signal, reason: str, ohlcv: pd.DataFrame
    ) -> tuple[Signal, str]:
        """Check if time-based entry cooldown is active."""
        cooldown_seconds = getattr(self.config.strategy, "cooldown_seconds", 0)
        if cooldown_seconds <= 0 or self._last_exit_time is None:
            return signal, reason

        current_time = ohlcv.index[-1]
        seconds_since_exit = (current_time - self._last_exit_time).total_seconds()

        if seconds_since_exit < cooldown_seconds:
            logger.info(
                "time_cooldown_active",
                signal=signal.value,
                seconds_since=seconds_since_exit,
                cooldown=cooldown_seconds,
            )
            return (
                Signal.HOLD,
                f"Time Cooldown ({int(seconds_since_exit)}/{cooldown_seconds}s) blocked {signal.value}",
            )

        return signal, reason

    def _check_entry_cooldown(self, signal: Signal, reason: str, ohlcv: pd.DataFrame) -> tuple[Signal, str]:
        """Check if entry cooldown is active."""
        min_bars = getattr(self.config.strategy, "min_bars_between_entries", 10)
        current_bar_index = ohlcv.index[-1]

        if self._last_entry_bar is not None and self._last_entry_side == signal.value:
            bars_since = self._calculate_bars_since(ohlcv, self._last_entry_bar)
            if bars_since < min_bars:
                logger.info(
                    "entry_cooldown_active",
                    signal=signal.value,
                    bars_since=bars_since,
                    min_bars=min_bars,
                )
                return Signal.HOLD, f"Entry Cooldown ({bars_since}/{min_bars} bars) blocked {signal.value}"

        self._last_entry_bar = current_bar_index
        self._last_entry_side = signal.value
        return signal, reason

    def _calculate_bars_since(self, ohlcv: pd.DataFrame, last_bar: Any) -> float:
        """Calculate number of bars since last_bar."""
        if isinstance(ohlcv.index, pd.DatetimeIndex) and isinstance(last_bar, pd.Timestamp):
            return len(ohlcv.loc[last_bar:]) - 1
        try:
            last_pos = ohlcv.index.get_loc(last_bar)
            return (len(ohlcv) - 1) - last_pos
        except KeyError:
            return float("inf")

    def _apply_entry_filters(self, signal: Signal, reason: str, market_data: dict[str, pd.DataFrame]) -> tuple[Signal, str]:
        """Apply higher-timeframe filters (Bias, SMC)."""
        # Bias Confirmation
        if self.config.strategy.bias_confirmation:
            signal, reason = self._apply_bias_filter(signal, reason, market_data)
            if signal == Signal.HOLD:
                return signal, reason

        # SMC Confirmation
        if getattr(self.config.strategy, "smc_confirmation", False):
            signal, reason = self._apply_smc_filter(signal, reason, market_data)

        return signal, reason

    def _apply_bias_filter(self, signal: Signal, reason: str, market_data: dict[str, pd.DataFrame]) -> tuple[Signal, str]:
        """Apply HTF trend bias filter."""
        bias_tf = self.config.strategy.bias_timeframe
        bias_ohlcv = market_data.get(bias_tf)
        if bias_ohlcv is not None:
            bias = self.check_trend(bias_ohlcv)
            if (signal == Signal.LONG and bias != "bullish") or (signal == Signal.SHORT and bias != "bearish"):
                logger.info("bias_confirmation_rejected", signal=signal.value, bias=bias, tf=bias_tf)
                return Signal.HOLD, f"Bias Filter ({bias_tf}: {bias}) blocked {signal.value}"
        return signal, reason

    def _apply_smc_filter(self, signal: Signal, reason: str, market_data: dict[str, pd.DataFrame]) -> tuple[Signal, str]:
        """Apply Smart Money Concept (SMC) bias filter."""
        smc_tf = getattr(self.config.strategy, "smc_timeframe", "4h")
        smc_ohlcv = market_data.get(smc_tf)

        if smc_ohlcv is None or smc_ohlcv.empty:
            logger.warning("smc_confirmation_missing_data", tf=smc_tf)
            return Signal.HOLD, f"SMC Bias Filter missing data for {smc_tf}"

        smc_swing_window = getattr(self.config.strategy, "smc_swing_window", 5)
        smc_analyzer = SMCAnalyzer(swing_window=smc_swing_window)
        smc_results = smc_analyzer.analyze({smc_tf: smc_ohlcv})
        smc_bias = smc_analyzer.get_bias(smc_results, bias_tf=smc_tf)

        if smc_bias != Trend.NEUTRAL:
            if (signal == Signal.LONG and smc_bias == Trend.BEARISH) or (signal == Signal.SHORT and smc_bias == Trend.BULLISH):
                logger.info("smc_confirmation_rejected", signal=signal.value, smc_bias=smc_bias.value, tf=smc_tf)
                return Signal.HOLD, f"SMC Bias Filter ({smc_tf}: {smc_bias.value}) blocked {signal.value}"

        return signal, reason

    def _get_exit_signal(self) -> tuple[Signal, str]:
        """Calculate exit signals for current position."""
        if self.current_position == "long" and self.should_exit():
            return Signal.EXIT_LONG, "Strategy Exit Long"
        if self.current_position == "short" and self.should_exit():
            return Signal.EXIT_SHORT, "Strategy Exit Short"
        return Signal.HOLD, "No exit signal"


    def get_indicators(self) -> dict[str, Any]:
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
            ema = indicators.ema(ohlcv["close"], length=period)
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
