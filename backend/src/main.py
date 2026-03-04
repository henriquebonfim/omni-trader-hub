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
from datetime import date, datetime, timedelta, timezone

import structlog
import uvicorn

from src.strategies import Signal, get_strategy

from .analysis.regime import MarketRegime, RegimeClassifier
from .config import get_config, reload_config
from .database import DatabaseFactory
from .exchange import Exchange
from .notifier import Notifier
from .risk import RiskManager
from .strategies.base import StrategyResult
from .workers.dispatch import dispatch
from .workers.serializers import df_to_json, market_data_to_json
from .workers.tasks import analyze_regime, analyze_strategy
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

    def __init__(self):
        self.config = get_config()
        self.exchange = Exchange()
        self.risk = RiskManager()
        self.notifier = Notifier()
        self.database = DatabaseFactory.get_database(self.config)
        self.regime_classifier = RegimeClassifier()

        # Load strategy dynamically
        strategy_name = getattr(self.config.strategy, "name", "ema_volume")
        logger.info("loading_strategy", name=strategy_name)

        try:
            strategy_class = get_strategy(strategy_name)
            self.strategy = strategy_class(self.config)
            logger.info("strategy_loaded", metadata=self.strategy.metadata)
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
                strategy_class = get_strategy(new_strategy_name)
                self.strategy = strategy_class(self.config)
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
                trades = await self.exchange.fetch_my_trades(symbol, since=since_ts, limit=limit)

                # Filter for trades that closed this position (after open, opposite side)
                # Note: last_trade['side'] is UPPER ("LONG"/"SHORT"), exchange trade['side'] is lower ("buy"/"sell")
                db_side = last_trade["side"].lower()
                closing_side = "sell" if db_side == "long" else "buy"

                closing_trades = [
                    t for t in trades
                    if t["timestamp"] > last_open_ts and t["side"] == closing_side
                ]

                if closing_trades:
                    # Calculate weighted average price if multiple fills
                    total_vol = sum(t["amount"] for t in closing_trades)
                    total_notional = sum(t["amount"] * t["price"] for t in closing_trades)
                    if total_vol > 0:
                        exit_price = total_notional / total_vol
                        found_trade = True
                        logger.info(
                            "reconciliation_found_trade",
                            exit_price=exit_price,
                            trades_count=len(closing_trades)
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
                expected_price=exit_price if found_trade else None
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
                    logger.info("reconciliation_found_open_trade", price=open_price, timestamp=latest_trade["timestamp"])

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

        logger.info("omnitrader_stopped")

    async def run_cycle(self):
        """
        Execute one trading cycle.

        This is the main trading logic that runs every cycle_seconds.
        """
        symbol = self.config.trading.symbol

        try:
            # 1. Check Circuit Breakers (Daily & Weekly)
            if self.risk.check_circuit_breaker():
                logger.warning("circuit_breaker_active", status="skipping_cycle")
                return

            # Fetch balance early for risk checks
            balance_info = await self.exchange.get_balance()
            total_balance = balance_info["total"]

            # 1b. Update Weekly Circuit Breaker Status (Throttled: every 60 cycles ~1 hour)
            self._weekly_check_counter += 1
            if self._weekly_check_counter >= 60:
                self._weekly_check_counter = 0
                try:
                    today = date.today()
                    start_of_week = today - timedelta(days=6) # 7 days inclusive
                    weekly_pnl = await self.database.get_weekly_pnl(start_of_week.isoformat())

                    if await self.risk.check_weekly_circuit_breaker(weekly_pnl, total_balance):
                        logger.critical("weekly_circuit_breaker_active", status="skipping_cycle")
                        await self.notifier.send("🚨 **Weekly Circuit Breaker Triggered**! Trading paused.")
                        return
                except Exception as e:
                    logger.error("weekly_circuit_breaker_check_failed", error=str(e))

            # Check if breaker is ALREADY active (fast check)
            if self.risk._weekly_circuit_breaker_active:
                logger.warning("weekly_circuit_breaker_active", status="skipping_cycle")
                return

            # 2. Get current position
            position = await self.exchange.get_position(symbol)
            current_side = position.side if position.is_open else None

            # 2b. Reconcile state with database (throttled)
            self._reconcile_counter += 1
            if self._reconcile_counter >= 5:
                await self._reconcile_positions(symbol, position)
                self._reconcile_counter = 0

            # 2c. Check Funding Rate (Throttled: every 60 cycles ~1 hour)
            self._funding_check_counter += 1
            if self._funding_check_counter >= 60:
                self._funding_check_counter = 0
                funding_rate = await self.exchange.fetch_funding_rate(symbol)

                # Alert if rate is high (> 0.01% * 3 = 0.03% or whatever "normal" is)
                # Normal is usually 0.01% (0.0001) per 8h. High is > 0.05%?
                # Task says > 3x normal. Normal = 0.01%. So > 0.03% (0.0003).
                if abs(funding_rate) > 0.0003:
                    logger.warning("high_funding_rate", rate=funding_rate)
                    await self.notifier.send(f"⚠️ **High Funding Rate**: {funding_rate*100:.4f}% for {symbol}")

                # Log payment estimation if in position
                if position.is_open:
                    payment = position.notional * funding_rate
                    # If long and positive rate, I pay. If short and positive, I receive.
                    # Payment direction: Positive rate -> Longs pay Shorts.
                    # So if Long, cost = rate * notional. If Short, cost = -rate * notional (income).
                    # We store "payment" as cost (positive = cost, negative = income).
                    if position.side == "long":
                        cost = payment
                    else:
                        cost = -payment

                    await self.database.log_funding_payment(
                        symbol=symbol,
                        rate=funding_rate,
                        payment=cost,
                        position_size=position.size
                    )

            # 3. Update daily stats with current balance
            await self.risk.initialize_daily_stats(total_balance)

            # 4. Fetch market data (Multi-Timeframe)
            # Prefer the WS cache to avoid REST round-trips; fall back to REST
            # when the cache is empty or hasn't been seeded yet, then seed it.
            limit = max(
                getattr(self.config.trading, "ohlcv_limit", 100),
                self.strategy.required_candles,
            )

            required_timeframes = self.strategy.required_timeframes
            primary_tf = self.config.trading.timeframe

            # Ensure primary timeframe is fetched even if strategy doesn't explicitly list it
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

            # Get primary OHLCV for price and risk checks
            primary_ohlcv = market_data[primary_tf]

            # Prefer real-time WS ticker price over last-close REST proxy
            ws_ticker = self.ws_feed.latest_ticker()
            if ws_ticker and ws_ticker.get("last"):
                current_price = float(ws_ticker["last"])
            else:
                current_price = float(primary_ohlcv["close"].iloc[-1])

            # 4a. Check Trend (if enabled)
            market_trend = "neutral"
            trend_filter_enabled = getattr(self.config.strategy, "trend_filter_enabled", False)
            if trend_filter_enabled:
                trend_tf = getattr(self.config.strategy, "trend_timeframe", "4h")
                try:
                    # Use WS cache if available (needs ≥ 210 rows for EMA 200)
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

            # 4b. Check Black Swan Event
            if self.risk.check_black_swan(primary_ohlcv):
                try:
                    if position.is_open:
                        logger.critical("black_swan_flattening_positions")
                        await self._close_position(position, current_price, "black_swan_emergency_exit")
                except Exception as e:
                    logger.error("black_swan_close_failed", error=str(e))
                await self.notifier.send("🚨 **BLACK SWAN DETECTED**: >10% move in 1h. Positions flattened. Bot stopping.")
                await self.stop("Black Swan Event")
                return

            # 5. Analyze with strategy + regime — dispatched to Celery workers
            # Both tasks run concurrently; the event loop is free for I/O while
            # workers crunch Pandas/NumPy indicators in a separate process.
            strategy_name = getattr(self.config.strategy, "name", "ema_volume")
            config_dict = self._config_dict()
            market_data_json = market_data_to_json(market_data)
            primary_ohlcv_json = df_to_json(primary_ohlcv)

            try:
                strategy_result_dict, regime_value = await asyncio.gather(
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
                        analyze_regime,
                        primary_ohlcv_json,
                        timeout=25.0,
                    ),
                )
                result = StrategyResult(
                    signal=Signal(strategy_result_dict["signal"]),
                    reason=strategy_result_dict["reason"],
                    indicators=strategy_result_dict["indicators"],
                )
                current_regime = MarketRegime(regime_value)
            except Exception as celery_exc:
                # Celery worker unavailable or timed out — fall back to local execution.
                logger.warning(
                    "celery_dispatch_failed_using_local_fallback",
                    error=str(celery_exc),
                )
                result = self.strategy.analyze(market_data, current_side, market_trend=market_trend)
                current_regime = self.regime_classifier.analyze(primary_ohlcv)

            # 5b. Regime Gating
            # If current regime is not in strategy's valid regimes, force HOLD for entries.
            # We allow exits to proceed even in wrong regime (to get out of trouble).
            if current_regime not in self.strategy.valid_regimes:
                if result.signal in (Signal.LONG, Signal.SHORT) and not position.is_open:
                    logger.warning(
                        "signal_rejected_regime_mismatch",
                        signal=result.signal,
                        regime=current_regime.value,
                        valid_regimes=[r.value for r in self.strategy.valid_regimes],
                    )
                    result.signal = Signal.HOLD
                    result.reason = f"Regime Mismatch: {current_regime.value}"

            # Sanitize indicators for JSON serialization (handle numpy types)
            def _sanitize(v):
                if hasattr(v, "item"):  # Numpy scalar
                    return v.item()
                if isinstance(v, dict):
                    return {k: _sanitize(val) for k, val in v.items()}
                return v

            sanitized_indicators = _sanitize(result.indicators)

            logger.info(
                "cycle_analyzed",
                price=f"${current_price:,.2f}",
                signal=result.signal.value,
                position=current_side or "none",
                reason=result.reason,
                **sanitized_indicators,
            )

            # 5b. Persist cycle data for the dashboard
            await self.database.log_equity_snapshot(balance_info["total"])
            await self.database.log_signal(
                symbol=symbol,
                price=current_price,
                signal=result.signal.value,
                regime=current_regime.value,
                reason=result.reason,
                indicators=sanitized_indicators,
            )

            # 5c. Broadcast to connected WebSocket clients
            time_in_trade_s = 0
            if position.is_open:
                try:
                    last_trade = await self.database.get_last_trade(symbol)
                    # If we have a position, valid open trade should exist
                    # However, if partial fills or restart, we might need robust logic.
                    # Simple MVP: If last trade is OPEN, use it.
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
                        "balance": balance_info["total"],
                        "daily_pnl": self.risk.daily_stats.realized_pnl,
                        "daily_pnl_pct": self.risk.daily_stats.pnl_pct,
                        "circuit_breaker": self.risk.check_circuit_breaker(),
                    }
                )

            # 6. Manage Trailing Stop (if in position)
            if position.is_open:
                # Check Liquidation Risk
                if self.risk.check_liquidation_risk(position, current_price):
                    await self._close_position(position, current_price, "liquidation_risk_exit")
                    await self.notifier.send(
                        f"🚨 **URGENT**: Position closed due to liquidation risk! Price: {current_price}, Liq: {position.liquidation_price}"
                    )
                    # Skip trailing stop logic since we are closing
                    return

                # Get existing stop loss
                open_orders = await self.exchange.fetch_open_orders(symbol)
                current_stop_price = None
                for order in open_orders:
                    if (
                        order.get("type") == "stop_market"
                        or order.get("type") == "STOP_MARKET"
                    ):
                        # ccxt unifies "stopPrice" or "triggerPrice" usually
                        current_stop_price = float(
                            order.get("stopPrice") or order.get("triggerPrice") or 0
                        )
                        break

                new_stop = self.risk.calculate_trailing_stop(current_price, position)

                if new_stop:
                    should_update = False
                    if current_stop_price is None:
                        # No stop exists? Should create one
                        should_update = True
                    else:
                        # Ratchet Logic: Only update if better
                        if position.side == "long":
                            if new_stop > current_stop_price:
                                should_update = True
                        elif position.side == "short":
                            if new_stop < current_stop_price:
                                should_update = True

                    if should_update:
                        logger.info(
                            "trailing_stop_update",
                            symbol=symbol,
                            current_stop=current_stop_price,
                            new_stop=new_stop,
                        )
                        try:
                            await self.exchange.set_stop_loss(
                                symbol, new_stop, position.side
                            )
                        except Exception as e:
                            logger.error("trailing_stop_update_failed", error=str(e))

            # 7. Execute based on signal
            if result.signal == Signal.LONG:
                await self._open_position(
                    "long", current_price, balance_info["free"], result.reason, primary_ohlcv
                )

            elif result.signal == Signal.SHORT:
                await self._open_position(
                    "short", current_price, balance_info["free"], result.reason, primary_ohlcv
                )

            elif result.signal in (Signal.EXIT_LONG, Signal.EXIT_SHORT):
                await self._close_position(position, current_price, result.reason)

        except Exception as e:
            logger.error("cycle_error", error=str(e))
            await self.notifier.error(str(e), "run_cycle")

    async def _open_position(
        self, side: str, current_price: float, balance: float, reason: str = "signal", ohlcv=None
    ):
        """Open a new position."""
        symbol = self.config.trading.symbol

        # Validate with risk manager
        risk_check = self.risk.validate_trade(
            side=side, balance=balance, entry_price=current_price, current_positions=0, ohlcv=ohlcv
        )

        if not risk_check.approved:
            logger.warning("trade_rejected", reason=risk_check.reason)
            return

        try:
            # Cancel any existing orders
            await self.exchange.cancel_all_orders(symbol)

            # Place market order
            if side == "long":
                order = await self.exchange.market_long(
                    symbol, risk_check.position_size
                )
            else:
                order = await self.exchange.market_short(
                    symbol, risk_check.position_size
                )

            # Verify fills and get actual price/fees
            fill_details = await self.exchange.get_order_fill_details(order["id"], symbol)
            entry_price = float(fill_details["average_price"] or order.get("average", current_price))
            total_fee = fill_details["total_fee"]
            fee_currency = fill_details["fee_currency"]
            is_confirmed = fill_details.get("confirmed", False)

            if not is_confirmed:
                logger.warning("order_fill_not_confirmed", order_id=order["id"], symbol=symbol)

            notional = risk_check.position_size * entry_price

            # Calculate slippage (Expected - Actual for buy is bad if Actual > Expected)
            # Long (Buy): Slippage = Actual - Expected (Positive = Bad)
            # Short (Sell): Slippage = Expected - Actual (Positive = Bad)
            slippage = 0.0
            if side == "long":
                slippage = entry_price - current_price
            else:
                slippage = current_price - entry_price

            logger.info(
                "order_fill_verified",
                side=side,
                expected=current_price,
                actual=entry_price,
                slippage=slippage,
                fee=fill_details.get("fee")
            )

            # Recalculate SL/TP with actual entry
            stop_loss = None
            take_profit = None
            if self.risk.use_atr_stops and ohlcv is not None:
                try:
                    stop_loss, take_profit = self.risk.calculate_atr_stops(entry_price, side, ohlcv)
                except Exception as e:
                    logger.error("atr_stops_recalc_failed_fallback_to_fixed", error=str(e))
            
            if stop_loss is None or take_profit is None:
                stop_loss = self.risk.calculate_stop_loss(entry_price, side)
                take_profit = self.risk.calculate_take_profit(entry_price, side)

            # Set stop loss with retries
            sl_success = False
            for attempt in range(4):
                try:
                    await self.exchange.set_stop_loss(symbol, stop_loss, side)
                    sl_success = True
                    break
                except Exception as e:
                    if attempt < 3:
                        logger.warning("set_stop_loss_failed_retrying", attempt=attempt+1, error=str(e))
                        await asyncio.sleep(1 * (2 ** attempt))
                    else:
                        logger.error("set_stop_loss_failed_final", error=str(e))

            if not sl_success:
                logger.critical("flattening_position_due_to_sl_failure")
                pos = await self.exchange.get_position(symbol)
                if pos.is_open:
                    await self._close_position(pos, entry_price, "emergency_close_sl_placement_failed")
                return

            # Set take profit with retries
            tp_success = False
            for attempt in range(4):
                try:
                    await self.exchange.set_take_profit(symbol, take_profit, side)
                    tp_success = True
                    break
                except Exception as e:
                    if attempt < 3:
                        logger.warning("set_take_profit_failed_retrying", attempt=attempt+1, error=str(e))
                        await asyncio.sleep(1 * (2 ** attempt))
                    else:
                        logger.error("set_take_profit_failed_final", error=str(e))

            if not tp_success:
                logger.critical("flattening_position_due_to_tp_failure")
                pos = await self.exchange.get_position(symbol)
                if pos.is_open:
                    await self._close_position(pos, entry_price, "emergency_close_tp_placement_failed")
                return

            # Log to database
            await self.database.log_trade_open(
                symbol=symbol,
                side=side,
                price=entry_price,
                size=risk_check.position_size,
                notional=notional,
                stop_loss=stop_loss,
                take_profit=take_profit,
                reason=reason,
                expected_price=current_price,
                slippage=slippage,
                fee=total_fee,
                fee_currency=fee_currency,
            )

            # Send notification
            await self.notifier.trade_opened(
                symbol=symbol,
                side=side,
                entry_price=entry_price,
                size=risk_check.position_size,
                notional=notional,
                stop_loss=stop_loss,
                take_profit=take_profit,
                leverage=self.config.exchange.leverage,
            )

            logger.info(
                "position_opened",
                side=side,
                entry=entry_price,
                size=risk_check.position_size,
                sl=stop_loss,
                tp=take_profit,
            )

        except Exception as e:
            logger.error("open_position_failed", error=str(e))
            await self.notifier.error(str(e), f"Opening {side} position")

    async def _close_position(self, position, current_price: float, reason: str):
        """Close the current position."""
        symbol = self.config.trading.symbol

        if not position.is_open:
            logger.warning("no_position_to_close")
            return

        # Store expected price (decision price)
        expected_price = current_price

        try:
            # Cancel any existing orders
            await self.exchange.cancel_all_orders(symbol)

            # Close position
            order = await self.exchange.close_position(symbol)

            if order is None:
                return

            # Verify fills and get actual price/fees
            fill_details = await self.exchange.get_order_fill_details(order["id"], symbol)
            exit_price = float(fill_details["average_price"] or order.get("average") or order.get("price") or current_price)
            total_fee = fill_details["total_fee"]
            fee_currency = fill_details["fee_currency"]
            is_confirmed = fill_details.get("confirmed", False)

            if not is_confirmed:
                logger.warning("close_order_fill_not_confirmed", order_id=order["id"], symbol=symbol)

            # Calculate Slippage (Positive = Bad, Negative = Good)
            # Long Exit (Sell): Expected - Actual
            # Short Exit (Buy): Actual - Expected
            slippage = 0.0
            if position.side == "long":
                slippage = expected_price - exit_price
            else:
                slippage = exit_price - expected_price

            # Subtract fees from PnL?
            # Usually PnL is (Exit - Entry) * Size. Fees are separate.
            # But "Net PnL" includes fees.
            # For now, we calculate Gross PnL here as per standard, and log fees separately.

            if position.side == "long":
                pnl = (exit_price - position.entry_price) * position.size
                pnl_pct = (
                    (exit_price - position.entry_price) / position.entry_price
                ) * 100
            else:
                pnl = (position.entry_price - exit_price) * position.size
                pnl_pct = (
                    (position.entry_price - exit_price) / position.entry_price
                ) * 100

            # Adjust PnL for fees if currency matches quote currency (USDT)
            # RiskManager.record_trade takes `pnl`.
            # Let's subtract fees from the reported PnL to RiskManager so it tracks Net Equity.

            # Fetch opening trade to get entry fees.
            # We specifically look for the last OPEN trade, not just the last trade (which could be this close if race condition, or older close).
            # Assuming FIFO/single position logic for MVP.
            open_fee = await self.database.get_open_trade_fee(symbol)

            net_pnl = pnl

            # Subtract fees from Net PnL.
            # Note: This assumes fees are in USDT (quote currency).
            # If fees are in BNB or base asset, this simple subtraction is an approximation for MVP.
            if total_fee > 0:
                net_pnl -= total_fee

            if open_fee > 0:
                net_pnl -= open_fee

            # Record in risk manager (use Net PnL to reflect actual equity change)
            await self.risk.record_trade(net_pnl)

            # Log to database
            await self.database.log_trade_close(
                symbol=symbol,
                side=position.side,
                price=exit_price,
                size=position.size,
                notional=position.size * exit_price,
                pnl=pnl,       # Log Gross PnL
                pnl_pct=pnl_pct,
                reason=reason,
                expected_price=expected_price,
                slippage=slippage,
                fee=total_fee,
                fee_currency=fee_currency,
            )

            # Send notification
            await self.notifier.trade_closed(
                symbol=symbol,
                side=position.side,
                entry_price=position.entry_price,
                exit_price=exit_price,
                pnl=pnl,
                pnl_pct=pnl_pct,
                reason=reason,
            )

            # Check if circuit breaker triggered
            if self.risk.check_circuit_breaker():
                await self.notifier.circuit_breaker(
                    daily_pnl=self.risk.daily_stats.realized_pnl,
                    daily_pnl_pct=self.risk.daily_stats.pnl_pct,
                    limit_pct=self.risk.max_daily_loss_pct,
                )

            logger.info(
                "position_closed",
                side=position.side,
                entry=position.entry_price,
                exit=exit_price,
                pnl=f"${pnl:.2f}",
                pnl_pct=f"{pnl_pct:.2f}%",
            )

        except Exception as e:
            logger.error("close_position_failed", error=str(e))
            await self.notifier.error(str(e), "Closing position")

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

    bot = OmniTrader()
    bot.ws_manager = _ws_manager

    app = create_api(bot)

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

    def signal_handler():
        logger.info("shutdown_signal_received")
        bot._running = False
        bot._shutdown_event.set()
        server.should_exit = True

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)

    logger.info("api_server_starting", host="0.0.0.0", port=8000)

    try:
        await asyncio.gather(bot.run(), server.serve())
    except KeyboardInterrupt:
        logger.info("keyboard_interrupt")
    except Exception as e:
        logger.error("fatal_error", error=str(e))
        raise


if __name__ == "__main__":
    asyncio.run(main())
