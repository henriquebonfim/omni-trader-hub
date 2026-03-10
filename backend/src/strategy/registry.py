"""
Strategy Registry.

Allows strategies to be registered and retrieved by name.
"""

from typing import Dict, Type

from .base import BaseStrategy

_STRATEGIES: Dict[str, Type[BaseStrategy]] = {}


def register_strategy(name: str):
    """
    Decorator to register a strategy class.

    Args:
        name: The name to register the strategy under.
    """

    def decorator(cls: Type[BaseStrategy]):
        if name in _STRATEGIES:
            raise ValueError(f"Strategy '{name}' already registered")
        _STRATEGIES[name] = cls
        return cls

    return decorator


def get_strategy(name: str) -> Type[BaseStrategy]:
    """
    Get a strategy class by name.

    Args:
        name: The name of the strategy.

    Returns:
        The strategy class.

    Raises:
        ValueError: If the strategy is not found.
    """
    if name not in _STRATEGIES:
        raise ValueError(
            f"Strategy '{name}' not found. Available: {list(_STRATEGIES.keys())}"
        )
    return _STRATEGIES[name]


def list_strategies() -> list[str]:
    """List all registered strategies."""
    return list(_STRATEGIES.keys())


def get_all_strategies() -> Dict[str, Type[BaseStrategy]]:
    """Return a dictionary of all registered strategies."""
    return _STRATEGIES.copy()
