"""
Base Strategy Interface for OmniTrader.

Defines the contract that all strategies must follow to be used in the bot.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict

import pandas as pd
import structlog

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

    @property
    @abstractmethod
    def metadata(self) -> Dict[str, str]:
        """
        Metadata about the strategy.

        Returns:
            Dict with keys like 'type' (trend/mean_reversion), 'risk' (low/medium/high)
        """
        pass

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

    def analyze(
        self, ohlcv: pd.DataFrame, current_position: str | None = None
    ) -> StrategyResult:
        """
        Orchestrate strategy execution.

        1. Update state
        2. Check for signals
        3. Return result
        """
        self.update(ohlcv, current_position)

        signal = Signal.HOLD
        reason = "No signal"

        if current_position is None:
            if self.should_long():
                signal = Signal.LONG
                reason = "Strategy Entry Long"
            elif self.should_short():
                signal = Signal.SHORT
                reason = "Strategy Entry Short"
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
