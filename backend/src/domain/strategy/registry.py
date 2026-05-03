"""
Strategy Registry.

Allows strategies to be registered and retrieved by name.
"""


from .base import BaseStrategy


class StrategyRegistry:
    """Singleton registry for trading strategies."""

    _instance: "StrategyRegistry | None" = None
    _strategies: dict[str, type[BaseStrategy]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register(self, name: str):
        """Decorator to register a strategy class."""

        def decorator(cls: type[BaseStrategy]):
            if name in self._strategies:
                raise ValueError(f"Strategy '{name}' already registered")
            self._strategies[name] = cls
            return cls

        return decorator

    def get(self, name: str) -> type[BaseStrategy]:
        """Get a strategy class by name."""
        if name not in self._strategies:
            available = list(self._strategies.keys())
            raise ValueError(f"Strategy '{name}' not found. Available: {available}")
        return self._strategies[name]

    def list(self) -> list[str]:
        """List all registered strategy names."""
        return list(self._strategies.keys())

    def get_all(self) -> dict[str, type[BaseStrategy]]:
        """Return a copy of all registered strategies."""
        return self._strategies.copy()


# Global instance for easy access
registry = StrategyRegistry()


# Backward compatibility: global function interface
def register_strategy(name: str):
    return registry.register(name)


def get_strategy(name: str) -> type[BaseStrategy]:
    return registry.get(name)


def list_strategies() -> list[str]:
    return registry.list()


def get_all_strategies() -> dict[str, type[BaseStrategy]]:
    return registry.get_all()

