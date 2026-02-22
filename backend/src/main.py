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
from datetime import datetime

import structlog
import uvicorn

from src.strategies import Signal, get_strategy

from .config import get_config, reload_config
from .database import Database
from .exchange import Exchange
from .notifier import Notifier
from .risk import RiskManager

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
        self.database = Database()

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
        self._reconcile_counter = 0

    async def reload_config(self):
        """Reload configuration and update all components."""
        logger.info("reloading_configuration")
        try:
            old_strategy_name = getattr(self.config.strategy, "name", "ema_volume")
            self.config = reload_config()
            new_strategy_name = getattr(self.config.strategy, "name", "ema_volume")

            # Update components
            await self.exchange.update_config(self.config)
            self.risk.update_config(self.config)

            # Switch strategy if name changed
            if new_strategy_name != old_strategy_name:
                logger.info(
                    "strategy_switching", old=old_strategy_name, new=new_strategy_name
                )
                try:
                    strategy_class = get_strategy(new_strategy_name)
                    self.strategy = strategy_class(self.config)
                    logger.info(
                        "strategy_switched", metadata=self.strategy.metadata
                    )
                except Exception as e:
                    logger.error(
                        "strategy_switch_failed",
                        error=str(e),
                        keeping=old_strategy_name,
                    )
            else:
                self.strategy.update_config(self.config)

            logger.info("configuration_reloaded")
        except Exception as e:
            logger.error("config_reload_failed", error=str(e))

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

        # Initialize daily stats
        balance_info = await self.exchange.get_balance()
        self.risk.initialize_daily_stats(balance_info["total"])

        # Send startup notification
        await self.notifier.bot_started(self.config.trading.symbol, paper_mode)

        self._running = True
        logger.info("omnitrader_started")

    async def _reconcile_positions(self, symbol, position):
        """
        Check for discrepancies between exchange position and database state.
        Fixes missed updates (e.g. SL hit while offline).
        """
        last_trade = await self.database.get_last_trade(symbol)

        # Case 1: DB says OPEN, Exchange says FLAT -> Missed CLOSE
        if last_trade and last_trade["action"] == "OPEN" and not position.is_open:
            logger.warning(
                "reconciliation_mismatch_closed",
                db_action="OPEN",
                exchange_status="FLAT",
                last_trade_id=last_trade["id"],
            )

            # We don't know the exact exit price, so use current market price (approx)
            ticker = await self.exchange.get_ticker(symbol)
            exit_price = float(ticker["last"])

            entry_price = float(last_trade["price"])
            size = float(last_trade["size"])
            side = last_trade["side"].lower()

            # Calculate PnL
            if side == "long":
                pnl = (exit_price - entry_price) * size
                pnl_pct = ((exit_price - entry_price) / entry_price) * 100
            else:
                pnl = (entry_price - exit_price) * size
                pnl_pct = ((entry_price - exit_price) / entry_price) * 100

            # Record in risk manager
            self.risk.record_trade(pnl)

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

            # Log the missing open
            await self.database.log_trade_open(
                symbol=symbol,
                side=position.side,
                price=position.entry_price,
                size=position.size,
                notional=position.notional,
                stop_loss=None,  # Unknown
                take_profit=None,  # Unknown
                reason="reconciliation_detected_open",
            )

            await self.notifier.send(
                f"⚠️ **Reconciliation Alert**: Detected open position for {symbol}. Database updated."
            )

    async def stop(self, reason: str = "Manual stop"):
        """Gracefully stop the trading bot."""
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
            # 1. Check circuit breaker
            if self.risk.check_circuit_breaker():
                logger.warning("circuit_breaker_active", status="skipping_cycle")
                return

            # 2. Get current position
            position = await self.exchange.get_position(symbol)
            current_side = position.side if position.is_open else None

            # 2b. Reconcile state with database (throttled)
            self._reconcile_counter += 1
            if self._reconcile_counter >= 5:
                await self._reconcile_positions(symbol, position)
                self._reconcile_counter = 0

            # 3. Update daily stats with current balance
            balance_info = await self.exchange.get_balance()
            self.risk.initialize_daily_stats(balance_info["total"])

            # 4. Fetch market data
            ohlcv = await self.exchange.fetch_ohlcv(symbol, limit=100)
            current_price = float(ohlcv["close"].iloc[-1])

            # 5. Analyze with strategy
            result = self.strategy.analyze(ohlcv, current_side)

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
                reason=result.reason,
                indicators=sanitized_indicators,
            )

            # 5c. Broadcast to connected WebSocket clients
            if self.ws_manager:
                await self.ws_manager.broadcast(
                    {
                        "type": "cycle",
                        "timestamp": datetime.utcnow().isoformat(),
                        "symbol": symbol,
                        "price": current_price,
                        "signal": result.signal.value,
                        "reason": result.reason,
                        "indicators": sanitized_indicators,
                        "position": current_side,
                        "balance": balance_info["total"],
                        "daily_pnl": self.risk.daily_stats.realized_pnl,
                        "daily_pnl_pct": self.risk.daily_stats.pnl_pct,
                        "circuit_breaker": self.risk.check_circuit_breaker(),
                    }
                )

            # 6. Manage Trailing Stop (if in position)
            if position.is_open:
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
                    "long", current_price, balance_info["free"], result.reason
                )

            elif result.signal == Signal.SHORT:
                await self._open_position(
                    "short", current_price, balance_info["free"], result.reason
                )

            elif result.signal in (Signal.EXIT_LONG, Signal.EXIT_SHORT):
                await self._close_position(position, current_price, result.reason)

        except Exception as e:
            logger.error("cycle_error", error=str(e))
            await self.notifier.error(str(e), "run_cycle")

    async def _open_position(
        self, side: str, current_price: float, balance: float, reason: str = "signal"
    ):
        """Open a new position."""
        symbol = self.config.trading.symbol

        # Validate with risk manager
        risk_check = self.risk.validate_trade(
            side=side, balance=balance, entry_price=current_price, current_positions=0
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

            # Get actual fill price
            entry_price = float(order.get("average", current_price))
            notional = risk_check.position_size * entry_price

            # Calculate slippage
            slippage = 0.0
            if side == "long":
                slippage = entry_price - current_price
            else:
                slippage = current_price - entry_price

            # Recalculate SL/TP with actual entry
            stop_loss = self.risk.calculate_stop_loss(entry_price, side)
            take_profit = self.risk.calculate_take_profit(entry_price, side)

            # Set stop loss
            try:
                await self.exchange.set_stop_loss(symbol, stop_loss, side)
            except Exception as e:
                logger.error("set_stop_loss_failed", error=str(e))

            # Set take profit
            try:
                await self.exchange.set_take_profit(symbol, take_profit, side)
            except Exception as e:
                logger.error("set_take_profit_failed", error=str(e))

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

        try:
            # Cancel any existing orders
            await self.exchange.cancel_all_orders(symbol)

            # Close position
            order = await self.exchange.close_position(symbol)

            if order is None:
                return

            # Calculate P/L
            exit_price = float(order.get("average", current_price))
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

            # Record in risk manager
            self.risk.record_trade(pnl)

            # Log to database
            await self.database.log_trade_close(
                symbol=symbol,
                side=position.side,
                price=exit_price,
                size=position.size,
                notional=position.size * exit_price,
                pnl=pnl,
                pnl_pct=pnl_pct,
                reason=reason,
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
