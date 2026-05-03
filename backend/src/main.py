"""
OmniTrader MVP - Main Entry Point

A simple BTC/USDT Futures trading bot using EMA + Volume strategy.

Usage:
    python -m src.main
"""

import asyncio
import logging
import signal
import sys
from datetime import UTC, datetime

import structlog
import uvicorn

from src.domain.shared.events import EventBus
from src.domain.strategy import get_strategy

from src.config import get_config, reload_config
from src.infrastructure.database import DatabaseFactory
from src.interfaces.events import BotEventManager
from src.infrastructure.exchanges import ExchangeFactory
from src.domain.intelligence.crisis import CrisisManager
from src.domain.intelligence.regime import RegimeClassifier
from src.infrastructure.notifier import Notifier
from src.application.reconciler import PositionReconciler
from src.domain.risk import RiskManager
from src.application.strategy_manager import StrategyManager
from src.application.trading.close_position import ClosePositionUseCase
from src.application.trading.open_position import OpenPositionUseCase
from src.infrastructure.ws_feed import WsFeed

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer(colors=True),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)


logging.basicConfig(
    format="%(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)

logger = structlog.get_logger()





class OmniTrader:
    """
    Main trading bot class.

    Orchestrates the trading loop:
    1. Fetch market data
    2. Analyze with strategy
    3. Execute trades if signals
    4. Manage risk and positions
    5. Send notifications
    """

    def __init__(self, bot_id: str = "default", config=None):
        self.bot_id = bot_id
        self.config = config if config else get_config()

        self._init_components()
        self._init_managers()
        self._init_state()
        self._init_ws_feed()

    def _init_components(self):
        """Initialize core infrastructure components."""
        self.exchange = ExchangeFactory.create_exchange()
        self.database = DatabaseFactory.get_database(self.config)
        self.risk = RiskManager(
            database=self.database, bot_id=self.bot_id, config=self.config
        )
        self.notifier = Notifier()
        self.regime_classifier = RegimeClassifier()
        self.crisis_manager = CrisisManager(database=self.database)  # type: ignore
        self.event_bus = EventBus()

    def _init_managers(self):
        """Initialize specialized management logic."""
        self.strategy_manager = StrategyManager(self.config, self.database)
        self.strategy_selector = self.strategy_manager.strategy_selector
        self.reconciler = PositionReconciler(
            self.config, self.exchange, self.database, self.risk, self.notifier
        )
        self.event_manager = BotEventManager(
            self.event_bus,
            self.config,
            self.notifier,
            close_position_cb=self._close_position,
        )
        self.event_manager.setup_handlers()

        # Pre-load strategy
        if self.strategy_manager.strategy is None:
            strategy_name = self.config.strategy.name
            self.strategy_manager.strategy = get_strategy(strategy_name)(self.config)

    def _init_state(self):
        """Initialize bot operational state."""
        self._running = False
        self._shutdown_event = asyncio.Event()
        self.ws_manager = None
        self._reconcile_counter = 0
        self._weekly_check_counter = 60
        self._funding_check_counter = 0
        self._last_regime = None
        self._last_position = None
        self._last_balance = 0.0
        self._started_at = None

    def _init_ws_feed(self):
        """Initialize WebSocket data feed based on strategy requirements."""
        ws_tfs = list(self.strategy.required_timeframes)
        primary_tf = self.config.trading.timeframe

        if primary_tf not in ws_tfs:
            ws_tfs.append(primary_tf)

        if self.config.strategy.trend_filter_enabled:
            trend_tf = self.config.strategy.trend_timeframe
            if trend_tf not in ws_tfs:
                ws_tfs.append(trend_tf)

        import os
        self.ws_feed = WsFeed(
            symbol=self.config.trading.symbol,
            timeframes=ws_tfs,
            api_key=os.getenv("BINANCE_API_KEY"),
            api_secret=os.getenv("BINANCE_SECRET"),
            paper_mode=self.config.exchange.paper_mode,
        )

        self._started_at = None

    @property
    def strategy(self):
        """Facade for the current active strategy."""
        return self.strategy_manager.strategy

    @strategy.setter
    def strategy(self, value):
        self.strategy_manager.strategy = value

    @property
    def dispatch(self):
        """Expose dispatch so tests can patch src.main.dispatch seamlessly."""
        from src.interfaces.workers.dispatch import dispatch as module_dispatch

        return module_dispatch

    async def _emit_ws_alert(self, *args, **kwargs):
        """Proxy to event manager."""
        await self.event_manager._emit_ws_alert(*args, **kwargs)

    async def _emit_ws_trade(self, *args, **kwargs):
        """Proxy to event manager."""
        await self.event_manager._emit_ws_trade(*args, **kwargs)




    async def _open_position(
        self,
        side: str,
        current_price: float,
        balance: float,
        reason: str = "signal",
        ohlcv=None,
        signal_id: str | None = None,
    ) -> None:
        """Open a position through the use case (fresh instance for late collaborator binding)."""
        # Sync max_positions so tests and live config changes are respected
        self.risk.max_positions = self.config.risk.max_positions
        use_case = OpenPositionUseCase(
            exchange=self.exchange,
            database=self.database,
            risk=self.risk,
            event_bus=self.event_bus,
        )
        await use_case.execute(
            symbol=self.config.trading.symbol,
            side=side,
            current_price=current_price,
            balance=balance,
            reason=reason,
            ohlcv=ohlcv,
            use_atr_stops=getattr(self.risk, "use_atr_stops", False),
            signal_id=signal_id,
        )

    async def _close_position(
        self,
        position,
        current_price: float,
        reason: str = "signal",
    ) -> None:
        """Close a position through the use case (fresh instance for late collaborator binding)."""
        use_case = ClosePositionUseCase(
            exchange=self.exchange,
            database=self.database,
            risk=self.risk,
            event_bus=self.event_bus,
        )
        await use_case.execute(
            symbol=self.config.trading.symbol,
            position=position,
            current_price=current_price,
            reason=reason,
        )

    async def _analyze_cycle(
        self,
        symbol: str,
        market_data,
        primary_ohlcv,
        current_price: float,
        current_side,
        market_trend: str,
    ):
        """Proxy to CycleOrchestrator analysis method."""
        from src.application.trading.cycle_orchestrator import CycleOrchestrator

        orchestrator = CycleOrchestrator(self)
        return await orchestrator._analyze_cycle(
            symbol,
            market_data,
            primary_ohlcv,
            current_price,
            current_side,
            market_trend,
        )

    def _config_dict(self) -> dict:
        """Serialize current config to a plain dict for Celery worker transport."""
        return self.config.to_dict()

    async def _reconcile_positions(self, symbol: str, position):
        """Reconcile position state between exchange and database."""
        if hasattr(self, "reconciler"):
            if hasattr(self, "database"):
                self.reconciler.database = self.database
            if hasattr(self, "exchange"):
                self.reconciler.exchange = self.exchange
            if hasattr(self, "risk"):
                self.reconciler.risk = self.risk
            if hasattr(self, "notifier"):
                self.reconciler.notifier = self.notifier
            if hasattr(self, "config"):
                self.reconciler.config = self.config

        await self.reconciler.reconcile(symbol, position)

    async def run_cycle(self):
        """Run a single bot cycle through the cycle orchestrator."""
        from src.application.trading.cycle_orchestrator import CycleOrchestrator

        orchestrator = CycleOrchestrator(self)
        await orchestrator.run_cycle()

    async def reload_config(self):
        """Reload configuration from database and update all components."""
        logger.info("reloading_configuration")
        try:
            from src.config import load_config_from_db
            new_config = await load_config_from_db(self.database)
            self.config = new_config

            # Update specialized managers
            await self.strategy_manager.update_config(self.config)
            self.event_manager.config = self.config
            self.reconciler.config = self.config

            # Update other components
            await self.exchange.update_config(self.config)
            self.risk.update_config(self.config)
            self.notifier.update_config(self.config)

            logger.info("configuration_reloaded")
        except Exception as e:
            logger.error("configuration_reload_failed", error=str(e))


    async def start(self):
        """Initialize and start the trading bot."""
        paper_mode = getattr(self.config.exchange, "paper_mode", False)
        logger.info(
            "omnitrader_starting",
            symbol=self.config.trading.symbol,
            paper_mode=paper_mode,
        )

        self._started_at = datetime.now(UTC)

        # Connect to services
        await self.exchange.connect()
        await self.database.connect()

        # Restore risk state
        await self.risk.load_state()

        # Initialize daily stats
        balance_info = await self.exchange.get_balance()
        await self.risk.initialize_daily_stats(balance_info["total"])

        # Load strategy via manager
        await self.strategy_manager.load_strategy()

        # Send startup notification
        await self.notifier.bot_started(self.config.trading.symbol, paper_mode)

        # Update event manager dependencies
        self.event_manager.ws_manager = self.ws_manager

        # Start WebSocket feed
        await self.ws_feed.start()

        self._running = True
        logger.info("omnitrader_started")




    async def stop(self, reason: str = "Manual stop"):
        """Gracefully stop the trading bot."""
        if not self._running:
            logger.warning("omnitrader_already_stopped", reason=reason)
            return

        logger.info("omnitrader_stopping", reason=reason)

        self._running = False
        self._shutdown_event.set()

        # Save daily summary
        try:
            balance_info = await self.exchange.get_balance()
            await self.database.save_daily_summary(
                date=str(self.risk.daily_stats.date),
                starting_balance=self.risk.daily_stats.starting_balance,
                ending_balance=balance_info["total"],
                pnl=self.risk.daily_stats.realized_pnl,
                pnl_pct=self.risk.daily_stats.pnl_pct,
                trades_count=self.risk.daily_stats.trades_count,
                wins=self.risk.daily_stats.wins,
                losses=self.risk.daily_stats.losses,
            )
        except Exception as e:
            logger.error("failed_to_save_summary", error=str(e))

        # Send stop notification
        await self.notifier.bot_stopped(reason)

        # Backup database
        try:
            await self.database.backup_db()
        except Exception as e:
            logger.error("backup_failed_on_stop", error=str(e))

        # Stop WebSocket feed before closing exchange connection
        try:
            await self.ws_feed.stop()
        except Exception as e:
            logger.warning("ws_feed_stop_failed", error=str(e))

        # Close connections
        await self.exchange.close()
        await self.database.close()
        await self.notifier.close()

        logger.info("omnitrader_stopped")

    def _sanitize_indicators(self, value):
        """Convert numpy-like scalars in indicator payloads to plain JSON types."""
        if hasattr(value, "item"):
            return value.item()
        if isinstance(value, dict):
            return {k: self._sanitize_indicators(v) for k, v in value.items()}
        return value

    def get_summary(self) -> dict:
        """Get a summary of the bot's current state."""
        uptime = 0
        if self._started_at:
            uptime = int((datetime.now(UTC) - self._started_at).total_seconds())

        return {
            "id": self.bot_id,
            "symbol": self.config.trading.symbol,
            "timeframe": self.config.trading.timeframe,
            "running": self._running,
            "strategy": getattr(self.config.strategy, "name", "ema_volume"),
            "market_regime": self._last_regime or "trending",
            "daily_pnl": self.risk.daily_stats.realized_pnl,
            "daily_pnl_pct": self.risk.daily_stats.pnl_pct,
            "total_balance": self._last_balance,
            "leverage": self.config.exchange.leverage,
            "paper_mode": getattr(self.config.exchange, "paper_mode", True),
            "uptime_seconds": uptime,
            "circuit_breaker_active": self.risk.check_circuit_breaker(),
            "position": (
                self._last_position.to_dict()
                if self._last_position
                else {"is_open": False}
            ),
        }


    async def run(self):
        """Main trading loop."""
        await self.start()

        from src.application.trading.cycle_orchestrator import CycleOrchestrator
        orchestrator = CycleOrchestrator(self)
        cycle_seconds = self.config.trading.cycle_seconds

        try:
            while self._running:
                cycle_start = datetime.now()

                await orchestrator.run_cycle()

                # Calculate sleep time to maintain consistent cycle
                cycle_duration = (datetime.now() - cycle_start).total_seconds()
                sleep_time = max(0, cycle_seconds - cycle_duration)

                if sleep_time > 0:
                    try:
                        await asyncio.wait_for(
                            self._shutdown_event.wait(), timeout=sleep_time
                        )
                    except TimeoutError:
                        pass  # Normal timeout, continue loop

        except asyncio.CancelledError:
            logger.info("trading_loop_cancelled")

        finally:
            await self.stop("Loop ended")


async def main():
    """Main entry point — runs trading loop + API server concurrently."""
    from src.interfaces.api import create_api
    from src.interfaces.api.websocket import manager as _ws_manager
    from src.application.bot_manager import BotManager

    # Initialize BotManager and load bots
    bot_manager = BotManager()
    await bot_manager.load_bots()

    # Pre-configure all loaded bots with the WebSocket manager
    for bot in bot_manager.bots.values():
        bot.ws_manager = _ws_manager

    # Pass bot_manager to the API factory
    app = create_api(bot_manager=bot_manager)

    api_config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="warning",
        access_log=False,
    )
    server = uvicorn.Server(api_config)

    # Setup signal handlers for graceful shutdown
    loop = asyncio.get_event_loop()
    stop_event = asyncio.Event()

    def handle_shutdown(signum):
        sig_name = signal.Signals(signum).name
        logger.info("shutdown_signal_received", signal=sig_name)
        stop_event.set()
        server.should_exit = True

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, handle_shutdown, sig)

    logger.info("omnitrader_system_starting")

    # Start all bots concurrently
    for bot_id in bot_manager.bots.keys():
        await bot_manager.start_bot(bot_id)

    # Run the API server
    server_task = asyncio.create_task(server.serve())

    # Wait for shutdown signal
    await stop_event.wait()

    logger.info("shutting_down_system")

    # Stop all bots gracefully and await
    await bot_manager.stop_all()

    # Wait for server to finish
    await server_task

    logger.info("omnitrader_system_stopped")


if __name__ == "__main__":
    asyncio.run(main())
