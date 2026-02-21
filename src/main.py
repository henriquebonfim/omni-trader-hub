"""
OmniTrader MVP - Main Entry Point

A simple BTC/USDT Futures trading bot using EMA + Volume strategy.

Usage:
    python -m src.main
"""

import asyncio
import signal
import sys
from datetime import datetime

import structlog

from .config import get_config
from .database import Database
from .exchange import Exchange
from .notifier import Notifier
from .risk import RiskManager
from src.strategies import get_strategy, Signal

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

import logging

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

            # 3. Update daily stats with current balance
            balance_info = await self.exchange.get_balance()
            self.risk.initialize_daily_stats(balance_info["total"])

            # 4. Fetch market data
            ohlcv = await self.exchange.fetch_ohlcv(symbol, limit=100)
            current_price = ohlcv["close"].iloc[-1]

            # 5. Analyze with strategy
            result = self.strategy.analyze(ohlcv, current_side)

            logger.info(
                "cycle_analyzed",
                price=f"${current_price:,.2f}",
                signal=result.signal.value,
                position=current_side or "none",
                reason=result.reason,
                **result.indicators,
            )

            # 6. Execute based on signal
            if result.signal == Signal.LONG:
                await self._open_position("long", current_price, balance_info["free"], result.reason)

            elif result.signal == Signal.SHORT:
                await self._open_position("short", current_price, balance_info["free"], result.reason)

            elif result.signal in (Signal.EXIT_LONG, Signal.EXIT_SHORT):
                await self._close_position(position, current_price, result.reason)

        except Exception as e:
            logger.error("cycle_error", error=str(e))
            await self.notifier.error(str(e), "run_cycle")

    async def _open_position(self, side: str, current_price: float, balance: float, reason: str = "signal"):
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
    """Main entry point."""
    bot = OmniTrader()

    # Setup signal handlers for graceful shutdown
    loop = asyncio.get_event_loop()

    def signal_handler():
        logger.info("shutdown_signal_received")
        bot._running = False
        bot._shutdown_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)

    try:
        await bot.run()
    except KeyboardInterrupt:
        logger.info("keyboard_interrupt")
    except Exception as e:
        logger.error("fatal_error", error=str(e))
        raise


if __name__ == "__main__":
    asyncio.run(main())
