from datetime import UTC, datetime
from typing import Any

import structlog

from src.domain.strategy import BaseStrategy, get_strategy
from src.domain.strategy.selector import StrategySelector

logger = structlog.get_logger()

class StrategyManager:
    """
    Manages the lifecycle of trading strategies.

    Responsibilities:
    - Loading strategies (built-in or custom)
    - Handling strategy rotation based on market regime
    - Updating strategy configuration
    """

    def __init__(self, config, database):
        self.config = config
        self.database = database
        self.strategy_selector = StrategySelector(database=self.database)
        self.strategy: BaseStrategy | None = None
        self.last_strategy_rotation = datetime.min.replace(tzinfo=UTC)

    async def load_strategy(self, strategy_name: str | None = None) -> BaseStrategy:
        """Load a strategy by name, defaulting to config value."""
        if strategy_name is None:
            strategy_name = getattr(self.config.strategy, "name", "ema_volume")

        logger.info("loading_strategy", name=strategy_name)

        try:
            # Allow tests to override get_strategy via src.main.get_strategy patch,
            # while maintaining fallback to the default registry.
            strategy_class = None
            try:
                import sys

                main_module = sys.modules.get("src.main")
                if main_module and hasattr(main_module, "get_strategy"):
                    strategy_class = main_module.get_strategy(strategy_name)
            except Exception:
                strategy_class = None

            if strategy_class is None:
                strategy_class = get_strategy(strategy_name)

            self.strategy = strategy_class(self.config)
            logger.info("strategy_loaded", metadata=self.strategy.metadata)
        except ValueError:
            # If not in registry, try custom strategy from database
            from src.domain.strategy.custom_executor import CustomStrategyExecutor

            cs_data = await self.database.get_custom_strategy(strategy_name)
            if cs_data:
                self.strategy = CustomStrategyExecutor(self.config, cs_data)
                logger.info("custom_strategy_loaded", name=strategy_name)
            else:
                logger.warning("strategy_not_found_deferring_to_fallback", name=strategy_name)
                # Fallback to ema_volume
                strategy_class = get_strategy("ema_volume")
                self.strategy = strategy_class(self.config)
        except Exception as e:
            logger.critical("strategy_load_failed", error=str(e))
            raise

        return self.strategy

    async def update_config(self, config):
        """Update strategy configuration, potentially switching strategy."""
        old_strategy_name = getattr(self.config.strategy, "name", "ema_volume")
        self.config = config
        new_strategy_name = getattr(self.config.strategy, "name", "ema_volume")

        if new_strategy_name != old_strategy_name:
            logger.info("strategy_switching", old=old_strategy_name, new=new_strategy_name)
            await self.load_strategy(new_strategy_name)
        elif self.strategy:
            self.strategy.update_config(config)

    async def rotate_if_needed(self, regime: Any, respect_cooldown: bool = True) -> bool:
        """
        Check if strategy should rotate based on regime and performance.
        Returns True if rotated.
        """
        best_strategy_name = await self.strategy_selector.get_best_strategy(
            regime, respect_cooldown=respect_cooldown
        )

        if best_strategy_name and best_strategy_name != getattr(self.config.strategy, "name", None):
            logger.info("rotating_strategy", new=best_strategy_name, regime=regime.value)
            # Update config name so reload_config or future references are consistent
            self.config.strategy.name = best_strategy_name
            await self.load_strategy(best_strategy_name)
            self.strategy_selector.record_rotation()
            return True

        return False
