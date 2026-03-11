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
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

import structlog
import uvicorn

from src.shared.domain.events import EventBus
from src.strategy import Signal, get_strategy

from .config import get_config, reload_config
from .database import DatabaseFactory
from .exchanges import ExchangeFactory
from .intelligence.crisis import CrisisManager
from .intelligence.regime import MarketRegime, RegimeClassifier
from .notifier import Notifier
from .risk import RiskManager
from .strategy.base import StrategyResult
from .trading.application.close_position import ClosePositionUseCase
from .trading.application.open_position import OpenPositionUseCase
from .workers.dispatch import dispatch
from .workers.serializers import df_to_json, market_data_to_json
from .workers.tasks import analyze_knowledge_graph, analyze_regime, analyze_strategy
from .ws_feed import WsFeed

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


@dataclass
class CyclePreflightResult:
    """Cycle preflight snapshot needed by downstream orchestration steps."""

    balance_info: dict
    total_balance: float
    position: object
    current_side: str | None


@dataclass
class CycleAnalysisResult:
    """Cycle analysis output used by persistence, broadcasting, and execution."""

    result: StrategyResult
    current_regime: MarketRegime
    graph_analytics: dict


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
        self.exchange = ExchangeFactory.create_exchange()
        self.database = DatabaseFactory.get_database(self.config)
        self.risk = RiskManager(database=self.database, bot_id=bot_id, config=self.config)
        self.notifier = Notifier()
        self.regime_classifier = RegimeClassifier()
        self.crisis_manager = CrisisManager(database=self.database)

        # Initialize event bus (DDD) — use cases are instantiated per-call for late collaborator binding
        self.event_bus = EventBus()

        # Setup event handlers (domain events → notifier side effects)
        self._setup_event_handlers()
        
        from src.strategy.selector import StrategySelector
        self.strategy_selector = StrategySelector(database=self.database)
        self.last_strategy_rotation = datetime.min.replace(tzinfo=timezone.utc)

        # Load strategy dynamically
        strategy_name = getattr(self.config.strategy, "name", "ema_volume")
        logger.info("loading_strategy", name=strategy_name)

        # To support async database operations inside __init__ logic
        # We define a helper that gets called inside start() instead, 
        # but for initial load we assume it might be a built-in strategy.
        try:
            strategy_class = get_strategy(strategy_name)
            self.strategy = strategy_class(self.config)
            logger.info("strategy_loaded", metadata=self.strategy.metadata)
        except ValueError:
            # If it's custom, we load it dynamically later in start() or assume ema_volume for now
            logger.warning("strategy_not_found_in_registry_deferring_load", name=strategy_name)
            strategy_class = get_strategy("ema_volume")
            self.strategy = strategy_class(self.config)
        except Exception as e:
            logger.critical("strategy_load_failed", error=str(e))
            raise

        self._running = False
        self._shutdown_event = asyncio.Event()
        self.ws_manager = None  # Set by main() after API creation

        # Build the WS timeframe subscription list from the loaded strategy
        _ws_tfs = list(self.strategy.required_timeframes)
        _primary_tf = self.config.trading.timeframe
        if _primary_tf not in _ws_tfs:
            _ws_tfs.append(_primary_tf)
        _trend_filter = getattr(self.config.strategy, "trend_filter_enabled", False)
        if _trend_filter:
            _trend_tf = getattr(self.config.strategy, "trend_timeframe", "4h")
            if _trend_tf not in _ws_tfs:
                _ws_tfs.append(_trend_tf)

        import os

        self.ws_feed = WsFeed(
            symbol=self.config.trading.symbol,
            timeframes=_ws_tfs,
            api_key=os.getenv("BINANCE_API_KEY"),
            api_secret=os.getenv("BINANCE_SECRET"),
            paper_mode=getattr(self.config.exchange, "paper_mode", True),
        )

        self._reconcile_counter = 0
        # Initialize to 60 so it runs immediately on first cycle
        self._weekly_check_counter = 60
        self._funding_check_counter = 0

    def _setup_event_handlers(self) -> None:
        """Wire domain events to notifier side effects."""

        async def on_position_opened(event) -> None:
            """Handle PositionOpened domain event."""
            payload = event.payload
            await self.notifier.trade_opened(
                symbol=payload["symbol"],
                side=payload["side"],
                entry_price=payload["entry_price"],
                size=payload["size"],
                notional=payload["notional"],
                stop_loss=payload["stop_loss"],
                take_profit=payload["take_profit"],
                leverage=payload.get("leverage", self.config.exchange.leverage),
            )

        async def on_position_closed(event) -> None:
            """Handle PositionClosed domain event."""
            payload = event.payload
            await self.notifier.trade_closed(
                symbol=payload["symbol"],
                side=payload["side"],
                entry_price=payload["entry_price"],
                exit_price=payload["exit_price"],
                pnl=payload["pnl"],
                pnl_pct=payload["pnl_pct"],
                reason=payload["reason"],
            )

        async def on_circuit_breaker_triggered(event) -> None:
            """Handle CircuitBreakerTriggered domain event."""
            payload = event.payload
            await self.notifier.circuit_breaker(
                daily_pnl=payload["daily_pnl"],
                daily_pnl_pct=payload["daily_pnl_pct"],
                limit_pct=payload["limit_pct"],
            )

        async def on_emergency_close(event) -> None:
            """Handle EmergencyClose domain event — flatten open position then notify."""
            payload = event.payload
            symbol = payload["symbol"]
            reason = payload["reason"]
            close_price = payload.get("entry_price")
            try:
                position = await self.exchange.get_position(symbol)
                if position.is_open:
                    if close_price is None:
                        ticker = await self.exchange.get_ticker(symbol)
                        close_price = float(ticker["last"])
                    await self._close_position(position, close_price, reason)
            except Exception as e:
                logger.error("emergency_close_failed", symbol=symbol, error=str(e))
            await self.notifier.send(
                f"🚨 **EMERGENCY CLOSE**: {symbol} closed due to {reason}"
            )

        # Register event handlers
        self.event_bus.subscribe("PositionOpened", on_position_opened)
        self.event_bus.subscribe("PositionClosed", on_position_closed)
        self.event_bus.subscribe(
            "CircuitBreakerTriggered", on_circuit_breaker_triggered
        )
        self.event_bus.subscribe("EmergencyClose", on_emergency_close)

        async def on_fill_unconfirmed(event) -> None:
            """Handle FillUnconfirmed domain event — log warning for monitoring."""
            payload = event.payload
            logger.warning(
                "order_fill_not_confirmed",
                order_id=payload["order_id"],
                symbol=payload["symbol"],
            )

        self.event_bus.subscribe("FillUnconfirmed", on_fill_unconfirmed)

    async def _open_position(
        self,
        side: str,
        current_price: float,
        balance: float,
        reason: str = "signal",
        ohlcv=None,
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

    def _config_dict(self) -> dict:
        """Serialize current config to a plain dict for Celery worker transport."""
        return self.config.to_dict()

    async def reload_config(self):
        """Reload configuration and update all components."""
        logger.info("reloading_configuration")
        old_config = self.config
        try:
            old_strategy_name = getattr(self.config.strategy, "name", "ema_volume")
            new_config = reload_config()
            self.config = new_config
            new_strategy_name = getattr(self.config.strategy, "name", "ema_volume")

            # Update components
            await self.exchange.update_config(self.config)
            self.risk.update_config(self.config)
            self.notifier.update_config(self.config)

            # Switch strategy if name changed
            if new_strategy_name != old_strategy_name:
                logger.info(
                    "strategy_switching", old=old_strategy_name, new=new_strategy_name
                )
                try:
                    strategy_class = get_strategy(new_strategy_name)
                    self.strategy = strategy_class(self.config)
                except ValueError:
                    from src.strategy.custom_executor import CustomStrategyExecutor
                    cs_data = await self.database.get_custom_strategy(new_strategy_name)
                    if cs_data:
                        self.strategy = CustomStrategyExecutor(self.config, cs_data)
                    else:
                        raise ValueError(f"Strategy {new_strategy_name} not found") from None
                logger.info("strategy_switched", metadata=self.strategy.metadata)
            else:
                self.strategy.update_config(self.config)

            logger.info("configuration_reloaded")

        except Exception as e:
            logger.error("config_reload_failed", error=str(e))
            # Full rollback of all components
            logger.info("rolling_back_configuration")
            self.config = old_config
            try:
                await self.exchange.update_config(old_config)
                self.risk.update_config(old_config)
                self.notifier.update_config(old_config)
                # If strategy was switched, we might need to revert it?
                # But here we rely on the fact that if strategy init failed, self.strategy is untouched.
                # If strategy init succeeded but something else failed later (unlikely here), we keep new strategy?
                # Actually, if strategy init fails, exception is raised, self.strategy is NOT updated.
                # So we just update config on the old strategy instance.
                self.strategy.update_config(old_config)
            except Exception as rollback_error:
                logger.critical("rollback_failed", error=str(rollback_error))

    async def start(self):
        """Initialize and start the trading bot."""
        paper_mode = getattr(self.config.exchange, "paper_mode", False)
        logger.info(
            "omnitrader_starting",
            symbol=self.config.trading.symbol,
            paper_mode=paper_mode,
        )

        # Connect to services
        await self.exchange.connect()
        await self.database.connect()

        # Restore risk state (Anti-Amnesia)
        await self.risk.load_state()

        # Initialize daily stats
        balance_info = await self.exchange.get_balance()
        await self.risk.initialize_daily_stats(balance_info["total"])

        # Load custom strategy if needed
        strategy_name = getattr(self.config.strategy, "name", "ema_volume")
        if self.strategy.metadata.get("name") != strategy_name:
            from src.strategy.custom_executor import CustomStrategyExecutor
            cs_data = await self.database.get_custom_strategy(strategy_name)
            if cs_data:
                self.strategy = CustomStrategyExecutor(self.config, cs_data)
                logger.info("custom_strategy_loaded_on_start", name=strategy_name)
            else:
                logger.error("strategy_not_found_in_db_or_registry", name=strategy_name)

        # Send startup notification
        await self.notifier.bot_started(self.config.trading.symbol, paper_mode)

        # Start WebSocket feed (non-blocking background tasks)
        await self.ws_feed.start()

        self._running = True
        logger.info("omnitrader_started")

    async def _reconcile_positions(self, symbol, position):
        """
        Check for discrepancies between exchange position and database state.
        Fixes missed updates (e.g. SL hit while offline).
        """
        last_trade = await self.database.get_last_trade(symbol)

        lookback = getattr(self.config.risk, "reconciliation_lookback_trades", 50)

        # Case 1: DB says OPEN, Exchange says FLAT -> Missed CLOSE
        if last_trade and last_trade["action"] == "OPEN" and not position.is_open:
            logger.warning(
                "reconciliation_mismatch_closed",
                db_action="OPEN",
                exchange_status="FLAT",
                last_trade_id=last_trade["id"],
            )

            exit_price = 0.0
            found_trade = False
            slippage = 0.0

            # Try to fetch actual trade from exchange history
            try:
                # Parse last open timestamp (ISO format in DB, assumed UTC)
                last_open_dt = datetime.fromisoformat(last_trade["timestamp"])
                # Ensure it's treated as UTC before converting to timestamp
                if last_open_dt.tzinfo is None:
                    last_open_dt = last_open_dt.replace(tzinfo=timezone.utc)
                last_open_ts = last_open_dt.timestamp() * 1000

                # Fetch all trades since the last known open trade
                # Using 'since' parameter ensures we don't miss trades if they are older than 'limit'
                since_ts = int(last_open_ts)
                # Use configured lookback or default to 50
                limit = getattr(self.config.risk, "reconciliation_lookback_trades", 50)
                trades = await self.exchange.fetch_my_trades(
                    symbol, since=since_ts, limit=limit
                )

                # Filter for trades that closed this position (after open, opposite side)
                # Note: last_trade['side'] is UPPER ("LONG"/"SHORT"), exchange trade['side'] is lower ("buy"/"sell")
                db_side = last_trade["side"].lower()
                closing_side = "sell" if db_side == "long" else "buy"

                closing_trades = [
                    t
                    for t in trades
                    if t["timestamp"] > last_open_ts and t["side"] == closing_side
                ]

                if closing_trades:
                    # Calculate weighted average price if multiple fills
                    total_vol = sum(t["amount"] for t in closing_trades)
                    total_notional = sum(
                        t["amount"] * t["price"] for t in closing_trades
                    )
                    if total_vol > 0:
                        exit_price = total_notional / total_vol
                        found_trade = True
                        logger.info(
                            "reconciliation_found_trade",
                            exit_price=exit_price,
                            trades_count=len(closing_trades),
                        )

            except Exception as e:
                logger.error("reconciliation_fetch_failed", error=str(e))

            # Fallback if trade not found (e.g. liquidated or too old)
            if not found_trade:
                logger.warning("reconciliation_trade_not_found_using_fallback")
                ticker = await self.exchange.get_ticker(symbol)
                current_price = float(ticker["last"])
                exit_price = current_price

                if last_trade.get("stop_loss"):
                    sl = float(last_trade["stop_loss"])
                    # If current price is below SL (long) or above SL (short),
                    # it's likely the SL was hit. Use SL as exit price.
                    side = last_trade["side"].lower()
                    if side == "long" and current_price < sl:
                        exit_price = sl
                    elif side == "short" and current_price > sl:
                        exit_price = sl

            entry_price = float(last_trade["price"])
            size = float(last_trade["size"])
            side = last_trade["side"].lower()

            # Calculate PnL
            if side == "long":
                pnl = (exit_price - entry_price) * size
                pnl_pct = ((exit_price - entry_price) / entry_price) * 100
                # Slippage estimate if we found trade (assuming expected price was entry price?? No, we don't know expected price for exit)
                # But we can assume stop loss price was expected if it was a SL hit
            else:
                pnl = (entry_price - exit_price) * size
                pnl_pct = ((entry_price - exit_price) / entry_price) * 100

            # Record in risk manager
            await self.risk.record_trade(pnl)

            # Log to database
            await self.database.log_trade_close(
                symbol=symbol,
                side=side,
                price=exit_price,
                size=size,
                notional=size * exit_price,
                pnl=pnl,
                pnl_pct=pnl_pct,
                reason="reconciliation_detected_close",
                slippage=slippage,
                expected_price=exit_price if found_trade else None,
            )

            await self.notifier.send(
                f"⚠️ **Reconciliation Alert**: Detected closed position for {symbol}. Database updated."
            )

        # Case 2: DB says CLOSE (or None), Exchange says OPEN -> Missed OPEN
        elif (not last_trade or last_trade["action"] == "CLOSE") and position.is_open:
            logger.warning(
                "reconciliation_mismatch_opened",
                db_action=last_trade["action"] if last_trade else "NONE",
                exchange_status="OPEN",
                size=position.size,
            )

            # Try to find the opening trade
            open_price = position.entry_price
            slippage = None
            expected_price = None

            try:
                trades = await self.exchange.fetch_my_trades(symbol, limit=lookback)
                # Look for recent trade that matches position side
                # Exchange side: buy (for long), sell (for short)
                target_side = "buy" if position.side == "long" else "sell"

                # We want the most recent trade of this side that created the position
                # This is a bit heuristic if there are multiple trades.
                # Ideally we find the trade that transitioned position from 0 to size.
                # But since we are stateless here, let's grab the most recent large trade or aggregate recent trades?
                # Simplify: find the most recent trade of correct side.

                matching_trades = [t for t in trades if t["side"] == target_side]
                matching_trades.sort(key=lambda x: x["timestamp"], reverse=True)

                if matching_trades:
                    # Check if it matches roughly the size or is recent enough?
                    # Let's assume the most recent one is the entry.
                    latest_trade = matching_trades[0]
                    open_price = latest_trade["price"]
                    logger.info(
                        "reconciliation_found_open_trade",
                        price=open_price,
                        timestamp=latest_trade["timestamp"],
                    )

            except Exception as e:
                logger.error("reconciliation_open_fetch_failed", error=str(e))

            # Log the missing open
            await self.database.log_trade_open(
                symbol=symbol,
                side=position.side,
                price=open_price,
                size=position.size,
                notional=position.notional,
                stop_loss=None,  # Unknown
                take_profit=None,  # Unknown
                expected_price=expected_price,
                slippage=slippage,
                reason="reconciliation_detected_open",
            )

            await self.notifier.send(
                f"⚠️ **Reconciliation Alert**: Detected open position for {symbol}. Database updated."
            )

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

    async def _fetch_market_context(self, symbol: str):
        """Fetch market data, resolve current price, and compute trend context."""
        limit = max(
            getattr(self.config.trading, "ohlcv_limit", 100),
            self.strategy.required_candles,
        )

        required_timeframes = list(self.strategy.required_timeframes)
        primary_tf = self.config.trading.timeframe
        if primary_tf not in required_timeframes:
            required_timeframes.append(primary_tf)

        market_data = {}
        rest_needed = []
        for tf in required_timeframes:
            cached = self.ws_feed.latest_ohlcv(tf)
            if cached is not None and len(cached) >= limit:
                market_data[tf] = cached.tail(limit)
            else:
                rest_needed.append(tf)

        if rest_needed:
            rest_tasks = [
                self.exchange.fetch_ohlcv(symbol, timeframe=tf, limit=limit)
                for tf in rest_needed
            ]
            rest_results = await asyncio.gather(*rest_tasks)
            for tf, df in zip(rest_needed, rest_results, strict=False):
                market_data[tf] = df
                self.ws_feed.seed_ohlcv(tf, df)

        primary_ohlcv = market_data[primary_tf]
        ticker_age = self.ws_feed.ticker_age()
        if ticker_age > 120.0:
            logger.warning(
                "ws_ticker_extremely_stale",
                age=ticker_age,
                status="pausing_trading",
            )
            await self.notifier.send(
                f"⚠️ **Stale Data Alert**: WS ticker is {ticker_age:.0f}s old. Trading paused."
            )
            return None

        if ticker_age > 60.0:
            logger.warning(
                "ws_ticker_stale",
                age=ticker_age,
                status="falling_back_to_rest",
            )
            rest_ticker = await self.exchange.get_ticker(symbol)
            current_price = float(rest_ticker["last"])
        else:
            ws_ticker = self.ws_feed.latest_ticker()
            if ws_ticker and ws_ticker.get("last"):
                current_price = float(ws_ticker["last"])
            else:
                current_price = float(primary_ohlcv["close"].iloc[-1])

        market_trend = "neutral"
        trend_filter_enabled = getattr(
            self.config.strategy, "trend_filter_enabled", False
        )
        if trend_filter_enabled:
            trend_tf = getattr(self.config.strategy, "trend_timeframe", "4h")
            try:
                trend_cached = self.ws_feed.latest_ohlcv(trend_tf)
                if trend_cached is not None and len(trend_cached) >= 210:
                    trend_ohlcv = trend_cached
                else:
                    trend_ohlcv = await self.exchange.fetch_ohlcv(
                        symbol, timeframe=trend_tf, limit=210
                    )
                    self.ws_feed.seed_ohlcv(trend_tf, trend_ohlcv)
                market_trend = self.strategy.check_trend(trend_ohlcv)
            except Exception as e:
                logger.warning("trend_fetch_failed", error=str(e))

        return market_data, primary_ohlcv, current_price, market_trend

    async def _analyze_cycle(
        self,
        symbol: str,
        market_data,
        primary_ohlcv,
        current_price: float,
        current_side,
        market_trend: str,
    ):
        """Analyze strategy/regime/graph and apply gating rules."""
        strategy_mode = getattr(self.config.strategy, "mode", "manual")
        
        # Determine regime first if in auto mode
        regime_value = MarketRegime.TRENDING.value
        primary_ohlcv_json = df_to_json(primary_ohlcv)
        try:
            regime_value_result = await dispatch(
                analyze_regime,
                primary_ohlcv_json,
                timeout=25.0,
            )
            if not isinstance(regime_value_result, Exception):
                regime_value = regime_value_result
        except Exception as e:
            logger.warning("regime_analysis_failed_fallback_to_trending", error=str(e))
            current_regime_fallback = self.regime_classifier.analyze(primary_ohlcv)
            regime_value = current_regime_fallback.value
            
        current_regime = MarketRegime(regime_value)

        # Handle strategy auto-selection
        if strategy_mode == "auto":
            now = datetime.now(timezone.utc)
            if not current_side and (now - self.last_strategy_rotation).total_seconds() >= 14400: # 4 hours cooldown
                best_strategy = await self.strategy_selector.get_best_strategy(current_regime)
                if best_strategy != getattr(self.config.strategy, "name", "ema_volume"):
                    logger.info("strategy_rotated", old=getattr(self.config.strategy, "name", "ema_volume"), new=best_strategy, regime=current_regime.value)
                    self.config.strategy.name = best_strategy
                    try:
                        try:
                            strategy_class = get_strategy(best_strategy)
                            self.strategy = strategy_class(self.config)
                        except ValueError:
                            from src.strategy.custom_executor import (
                                CustomStrategyExecutor,
                            )
                            cs_data = await self.database.get_custom_strategy(best_strategy)
                            if cs_data:
                                self.strategy = CustomStrategyExecutor(self.config, cs_data)
                            else:
                                raise ValueError(f"Strategy {best_strategy} not found") from None
                    except Exception as e:
                        logger.error("strategy_rotation_failed", error=str(e))
                self.last_strategy_rotation = now

        strategy_name = getattr(self.config.strategy, "name", "ema_volume")
        config_dict = self._config_dict()
        market_data_json = market_data_to_json(market_data)

        try:
            strategy_result_dict, graph_analytics_dict = (
                await asyncio.gather(
                    dispatch(
                        analyze_strategy,
                        strategy_name,
                        config_dict,
                        market_data_json,
                        current_side,
                        market_trend,
                        timeout=25.0,
                    ),
                    dispatch(
                        analyze_knowledge_graph,
                        symbol,
                        current_price,
                        config_dict,
                        timeout=25.0,
                    ),
                    return_exceptions=True,
                )
            )

            if isinstance(strategy_result_dict, Exception):
                raise strategy_result_dict

            result = StrategyResult(
                signal=Signal(strategy_result_dict["signal"]),
                reason=strategy_result_dict["reason"],
                indicators=strategy_result_dict["indicators"],
            )
            graph_analytics = (
                graph_analytics_dict
                if not isinstance(graph_analytics_dict, Exception)
                else {}
            )
        except Exception as celery_exc:
            logger.warning(
                "celery_dispatch_failed_using_local_fallback",
                error=str(celery_exc),
            )
            result = self.strategy.analyze(
                market_data, current_side, market_trend=market_trend
            )
            graph_analytics = {}

        if graph_analytics:
            contagion_risk = graph_analytics.get("contagion", {}).get(
                "contagion_risk", False
            )
            sentiment_level = graph_analytics.get("sentiment", {}).get(
                "avg_sentiment", 0.0
            )
            await self.crisis_manager.evaluate_automated_crisis(
                contagion_risk, sentiment_level
            )

        is_crisis = await self.crisis_manager.is_crisis_active()
        if is_crisis:
            if result.signal in (Signal.LONG, Signal.SHORT) and not current_side:
                logger.warning(
                    "signal_rejected_crisis_mode",
                    signal=result.signal,
                    reason="Crisis Mode Active",
                )
                result.signal = Signal.HOLD
                result.reason = "Crisis Mode Active"
        elif current_regime not in self.strategy.valid_regimes:
            if result.signal in (Signal.LONG, Signal.SHORT) and not current_side:
                logger.warning(
                    "signal_rejected_regime_mismatch",
                    signal=result.signal,
                    regime=current_regime.value,
                    valid_regimes=[r.value for r in self.strategy.valid_regimes],
                )
                result.signal = Signal.HOLD
                result.reason = f"Regime Mismatch: {current_regime.value}"

        return CycleAnalysisResult(
            result=result,
            current_regime=current_regime,
            graph_analytics=graph_analytics,
        )

    async def _persist_and_broadcast_cycle(
        self,
        symbol: str,
        current_price: float,
        result: StrategyResult,
        current_regime: MarketRegime,
        market_trend: str,
        current_side,
        balance_total: float,
        graph_analytics,
    ) -> None:
        """Persist cycle outputs and push updates to connected websocket clients."""
        sanitized_indicators = self._sanitize_indicators(result.indicators)

        logger.info(
            "cycle_analyzed",
            price=f"${current_price:,.2f}",
            signal=result.signal.value,
            position=current_side or "none",
            reason=result.reason,
            **sanitized_indicators,
        )

        await self.database.log_equity_snapshot(balance_total)
        await self.database.log_signal(
            symbol=symbol,
            price=current_price,
            signal=result.signal.value,
            regime=current_regime.value,
            reason=result.reason,
            indicators=sanitized_indicators,
        )

        time_in_trade_s = 0
        if current_side:
            try:
                last_trade = await self.database.get_last_trade(symbol)
                if last_trade and last_trade["action"] == "OPEN":
                    entry_dt = datetime.fromisoformat(last_trade["timestamp"])
                    if entry_dt.tzinfo is None:
                        entry_dt = entry_dt.replace(tzinfo=timezone.utc)
                    now_dt = datetime.now(timezone.utc)
                    time_in_trade_s = max(0, (now_dt - entry_dt).total_seconds())
            except Exception as e:
                logger.warning("time_in_trade_calc_failed", error=str(e))

        if self.ws_manager:
            await self.ws_manager.broadcast(
                {
                    "type": "cycle",
                    "timestamp": datetime.utcnow().isoformat(),
                    "symbol": symbol,
                    "price": current_price,
                    "signal": result.signal.value,
                    "regime": current_regime.value,
                    "reason": result.reason,
                    "market_trend": market_trend,
                    "indicators": sanitized_indicators,
                    "position": current_side,
                    "time_in_trade": time_in_trade_s,
                    "balance": balance_total,
                    "daily_pnl": self.risk.daily_stats.realized_pnl,
                    "daily_pnl_pct": self.risk.daily_stats.pnl_pct,
                    "circuit_breaker": self.risk.check_circuit_breaker(),
                    "graph_analytics": graph_analytics,
                }
            )

    async def _manage_open_position(
        self, symbol: str, position, current_price: float
    ) -> bool:
        """Manage liquidation risk and trailing stop. Returns True when cycle should stop early."""
        if not position.is_open:
            return False

        if self.risk.check_liquidation_risk(position, current_price):
            await self._close_position(
                position, current_price, reason="liquidation_risk_exit"
            )
            await self.notifier.send(
                f"🚨 **URGENT**: Position closed due to liquidation risk! Price: {current_price}, Liq: {position.liquidation_price}"
            )
            return True

        open_orders = await self.exchange.fetch_open_orders(symbol)
        current_stop_price = None
        for order in open_orders:
            if order.get("type") == "stop_market" or order.get("type") == "STOP_MARKET":
                current_stop_price = float(
                    order.get("stopPrice") or order.get("triggerPrice") or 0
                )
                break

        new_stop = self.risk.calculate_trailing_stop(current_price, position)
        if not new_stop:
            return False

        should_update = False
        if current_stop_price is None:
            should_update = True
        elif position.side == "long" and new_stop > current_stop_price:
            should_update = True
        elif position.side == "short" and new_stop < current_stop_price:
            should_update = True

        if should_update:
            logger.info(
                "trailing_stop_update",
                symbol=symbol,
                current_stop=current_stop_price,
                new_stop=new_stop,
            )
            try:
                await self.exchange.set_stop_loss(symbol, new_stop, position.side)
            except Exception as e:
                logger.error("trailing_stop_update_failed", error=str(e))

        return False

    async def _execute_signal(
        self,
        symbol: str,
        result: StrategyResult,
        position,
        current_price: float,
        free_balance: float,
        primary_ohlcv,
    ) -> None:
        """Execute final trading signal through DDD use cases."""
        if result.signal == Signal.LONG:
            await self._open_position(
                "long",
                current_price,
                free_balance,
                reason=result.reason,
                ohlcv=primary_ohlcv,
            )
        elif result.signal == Signal.SHORT:
            await self._open_position(
                "short",
                current_price,
                free_balance,
                reason=result.reason,
                ohlcv=primary_ohlcv,
            )
        elif result.signal in (Signal.EXIT_LONG, Signal.EXIT_SHORT):
            await self._close_position(position, current_price, reason=result.reason)

    async def _cycle_preflight(self, symbol: str) -> CyclePreflightResult | None:
        """Run cycle-level safety checks and return state needed for analysis."""
        if self.risk.check_circuit_breaker():
            logger.warning("circuit_breaker_active", status="skipping_cycle")
            return None

        balance_info = await self.exchange.get_balance()
        total_balance = balance_info["total"]

        self._weekly_check_counter += 1
        if self._weekly_check_counter >= 60:
            self._weekly_check_counter = 0
            try:
                today = date.today()
                start_of_week = today - timedelta(days=6)
                weekly_pnl = await self.database.get_weekly_pnl(
                    start_of_week.isoformat()
                )
                if await self.risk.check_weekly_circuit_breaker(
                    weekly_pnl, total_balance
                ):
                    logger.critical(
                        "weekly_circuit_breaker_active", status="skipping_cycle"
                    )
                    await self.notifier.send(
                        "🚨 **Weekly Circuit Breaker Triggered**! Trading paused."
                    )
                    return None
            except Exception as e:
                logger.error("weekly_circuit_breaker_check_failed", error=str(e))

        if self.risk._weekly_circuit_breaker_active:
            logger.warning("weekly_circuit_breaker_active", status="skipping_cycle")
            return None

        position = await self.exchange.get_position(symbol)
        current_side = position.side if position.is_open else None

        self._reconcile_counter += 1
        if self._reconcile_counter >= 5:
            await self._reconcile_positions(symbol, position)
            self._reconcile_counter = 0

        self._funding_check_counter += 1
        if self._funding_check_counter >= 60:
            self._funding_check_counter = 0
            funding_rate = await self.exchange.fetch_funding_rate(symbol)
            if abs(funding_rate) > 0.0003:
                logger.warning("high_funding_rate", rate=funding_rate)
                await self.notifier.send(
                    f"⚠️ **High Funding Rate**: {funding_rate * 100:.4f}% for {symbol}"
                )
            if position.is_open:
                payment = position.notional * funding_rate
                cost = payment if position.side == "long" else -payment
                await self.database.log_funding_payment(
                    symbol=symbol,
                    rate=funding_rate,
                    payment=cost,
                    position_size=position.size,
                )

        await self.risk.initialize_daily_stats(total_balance)
        return CyclePreflightResult(
            balance_info=balance_info,
            total_balance=total_balance,
            position=position,
            current_side=current_side,
        )

    async def _handle_black_swan(
        self,
        symbol: str,
        primary_ohlcv,
        position,
        current_price: float,
    ) -> bool:
        """Handle black swan detection and emergency shutdown. Returns True if cycle should stop."""
        if not self.risk.check_black_swan(primary_ohlcv):
            return False

        try:
            if position.is_open:
                logger.critical("black_swan_flattening_positions")
                await self.close_position_use_case.execute(
                    symbol=symbol,
                    position=position,
                    current_price=current_price,
                    reason="black_swan_emergency_exit",
                )
        except Exception as e:
            logger.error("black_swan_close_failed", error=str(e))

        await self.notifier.send(
            "🚨 **BLACK SWAN DETECTED**: >10% move in 1h. Positions flattened. Bot stopping."
        )
        await self.stop("Black Swan Event")
        return True

    async def run_cycle(self):
        """Execute one trading cycle."""
        symbol = self.config.trading.symbol

        try:
            preflight = await self._cycle_preflight(symbol)
            if preflight is None:
                return
            balance_info = preflight.balance_info
            total_balance = preflight.total_balance
            position = preflight.position
            current_side = preflight.current_side

            market_context = await self._fetch_market_context(symbol)
            if market_context is None:
                return
            market_data, primary_ohlcv, current_price, market_trend = market_context

            should_stop = await self._handle_black_swan(
                symbol=symbol,
                primary_ohlcv=primary_ohlcv,
                position=position,
                current_price=current_price,
            )
            if should_stop:
                return

            analysis = await self._analyze_cycle(
                symbol=symbol,
                market_data=market_data,
                primary_ohlcv=primary_ohlcv,
                current_price=current_price,
                current_side=current_side,
                market_trend=market_trend,
            )

            await self._persist_and_broadcast_cycle(
                symbol=symbol,
                current_price=current_price,
                result=analysis.result,
                current_regime=analysis.current_regime,
                market_trend=market_trend,
                current_side=current_side,
                balance_total=total_balance,
                graph_analytics=analysis.graph_analytics,
            )

            should_stop = await self._manage_open_position(
                symbol, position, current_price
            )
            if should_stop:
                return

            await self._execute_signal(
                symbol=symbol,
                result=analysis.result,
                position=position,
                current_price=current_price,
                free_balance=balance_info["free"],
                primary_ohlcv=primary_ohlcv,
            )

        except Exception as e:
            logger.error("cycle_error", error=str(e))
            await self.notifier.error(str(e), "run_cycle")

    async def run(self):
        """Main trading loop."""
        await self.start()

        cycle_seconds = self.config.trading.cycle_seconds

        try:
            while self._running:
                cycle_start = datetime.now()

                await self.run_cycle()

                # Calculate sleep time to maintain consistent cycle
                cycle_duration = (datetime.now() - cycle_start).total_seconds()
                sleep_time = max(0, cycle_seconds - cycle_duration)

                if sleep_time > 0:
                    try:
                        await asyncio.wait_for(
                            self._shutdown_event.wait(), timeout=sleep_time
                        )
                    except asyncio.TimeoutError:
                        pass  # Normal timeout, continue loop

        except asyncio.CancelledError:
            logger.info("trading_loop_cancelled")

        finally:
            await self.stop("Loop ended")


async def main():
    """Main entry point — runs trading loop + API server concurrently."""
    from .api import create_api
    from .api.websocket import manager as _ws_manager
    from .bot_manager import BotManager

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
    
    def handle_shutdown(signum):
        sig_name = signal.Signals(signum).name
        logger.info("shutdown_signal_received", signal=sig_name)
        
        # Stop all bots concurrently
        asyncio.create_task(bot_manager.stop_all())
        
        # Stop uvicorn server
        server.should_exit = True

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, handle_shutdown, sig)

    logger.info("omnitrader_system_starting")

    # Start all bots concurrently
    for bot_id in bot_manager.bots.keys():
        await bot_manager.start_bot(bot_id)
    
    # Run the API server
    await server.serve()



if __name__ == "__main__":
    asyncio.run(main())
