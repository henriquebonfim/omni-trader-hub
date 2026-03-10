"""Strategy bounded context.

Contains strategy interfaces, registry, and concrete strategy implementations.
"""

# Import strategies to ensure registration
from . import (  # noqa: F401
    adx_trend,
    bollinger_bands,
    breakout,
    ema_volume,
    z_score,
)
from .base import BaseStrategy, Signal, StrategyResult
from .registry import get_strategy, list_strategies, register_strategy

__all__ = [
    "BaseStrategy",
    "Signal",
    "StrategyResult",
    "register_strategy",
    "get_strategy",
    "list_strategies",
]
