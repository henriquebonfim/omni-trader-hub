"""
Trading Strategies Module.

Contains the base strategy interface, registry, and concrete implementations.
"""

from .base import BaseStrategy, Signal, StrategyResult
from .registry import get_strategy, list_strategies, register_strategy

# Import strategies to ensure registration
from . import adx_trend, ema_volume, z_score, bollinger_bands, breakout

__all__ = [
    "BaseStrategy",
    "Signal",
    "StrategyResult",
    "register_strategy",
    "get_strategy",
    "list_strategies",
]
