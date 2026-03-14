"""
Exchange factory for selecting and initializing the correct exchange adapter.
"""

import structlog

from ..config import get_config
from .base import BaseExchange
from .binance_direct import BinanceDirectExchange
from .ccxt_adapter import CCXTExchange

logger = structlog.get_logger()


class ExchangeFactory:
    """Factory to create and fallback exchange adapters based on configuration."""

    @staticmethod
    def create_exchange() -> BaseExchange:
        """
        Creates the exchange adapter specified in the config.
        Provides a fallback if binance_direct fails to initialize.
        """
        config = get_config()
        adapter_name = getattr(config.exchange, "adapter", "ccxt")

        if adapter_name == "binance_direct":
            logger.info("initializing_binance_direct_adapter")
            try:
                adapter = BinanceDirectExchange()
                return adapter
            except Exception as e:
                logger.error(
                    "binance_direct_initialization_failed_falling_back_to_ccxt",
                    error=str(e),
                )
                return CCXTExchange()

        # Default / Fallback
        logger.info("initializing_ccxt_adapter")
        return CCXTExchange()
