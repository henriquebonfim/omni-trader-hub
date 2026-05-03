from datetime import UTC, datetime
from typing import Any

import structlog

logger = structlog.get_logger()

class PositionReconciler:
    """
    Handles reconciliation of positions between the exchange and the database.
    """

    def __init__(self, config, exchange, database, risk, notifier):
        self.config = config
        self.exchange = exchange
        self.database = database
        self.risk = risk
        self.notifier = notifier

    async def reconcile(self, symbol: str, position: Any):
        """
        Check for discrepancies between exchange position and database state.
        Fixes missed updates (e.g. SL hit while offline).
        """
        last_trade = await self.database.get_last_trade(symbol)
        lookback = getattr(self.config.risk, "reconciliation_lookback_trades", 50)

        # Case 1: DB says OPEN, Exchange says FLAT -> Missed CLOSE
        if last_trade and last_trade["action"] == "OPEN" and not position.is_open:
            await self._handle_missed_close(symbol, last_trade, lookback)

        # Case 2: DB says CLOSE (or None), Exchange says OPEN -> Missed OPEN
        elif (not last_trade or last_trade["action"] == "CLOSE") and position.is_open:
            await self._handle_missed_open(symbol, last_trade, position, lookback)

    async def _handle_missed_close(self, symbol, last_trade, lookback):
        logger.warning(
            "reconciliation_mismatch_closed",
            db_action="OPEN",
            exchange_status="FLAT",
            last_trade_id=last_trade["id"],
        )

        exit_price = 0.0
        found_trade = False
        slippage = 0.0

        try:
            last_open_dt = datetime.fromisoformat(last_trade["timestamp"])
            if last_open_dt.tzinfo is None:
                last_open_dt = last_open_dt.replace(tzinfo=UTC)
            last_open_ts = last_open_dt.timestamp() * 1000

            since_ts = int(last_open_ts)
            trades = await self.exchange.fetch_my_trades(symbol, since=since_ts, limit=lookback)

            db_side = last_trade["side"].lower()
            closing_side = "sell" if db_side == "long" else "buy"

            closing_trades = [
                t for t in trades
                if t["timestamp"] > last_open_ts and t["side"] == closing_side
            ]

            if closing_trades:
                total_vol = sum(t["amount"] for t in closing_trades)
                total_notional = sum(t["amount"] * t["price"] for t in closing_trades)
                if total_vol > 0:
                    exit_price = total_notional / total_vol
                    found_trade = True
                    logger.info("reconciliation_found_trade", exit_price=exit_price, trades_count=len(closing_trades))
        except Exception as e:
            logger.error("reconciliation_fetch_failed", error=str(e))

        if not found_trade:
            logger.warning("reconciliation_trade_not_found_using_fallback")
            ticker = await self.exchange.get_ticker(symbol)
            current_price = float(ticker["last"])
            exit_price = current_price

            if last_trade.get("stop_loss"):
                sl = float(last_trade["stop_loss"])
                side = last_trade["side"].lower()
                if (side == "long" and current_price < sl) or (side == "short" and current_price > sl):
                    exit_price = sl

        entry_price = float(last_trade["price"])
        size = float(last_trade["size"])
        side = last_trade["side"].lower()

        pnl = (exit_price - entry_price) * size if side == "long" else (entry_price - exit_price) * size
        pnl_pct = ((exit_price - entry_price) / entry_price * 100) if side == "long" else ((entry_price - exit_price) / entry_price * 100)

        await self.risk.record_trade(pnl)
        await self.database.log_trade_close(
            symbol=symbol, side=side, price=exit_price, size=size,
            notional=size * exit_price, pnl=pnl, pnl_pct=pnl_pct,
            reason="reconciliation_detected_close", slippage=slippage,
            expected_price=exit_price if found_trade else None,
        )

        await self.notifier.send(f"⚠️ **Reconciliation Alert**: Detected closed position for {symbol}. Database updated.")

    async def _handle_missed_open(self, symbol, last_trade, position, lookback):
        logger.warning(
            "reconciliation_mismatch_opened",
            db_action=last_trade["action"] if last_trade else "NONE",
            exchange_status="OPEN",
            size=position.size,
        )

        open_price = position.entry_price
        try:
            trades = await self.exchange.fetch_my_trades(symbol, limit=lookback)
            target_side = "buy" if position.side == "long" else "sell"
            matching_trades = sorted([t for t in trades if t["side"] == target_side], key=lambda x: x["timestamp"], reverse=True)

            if matching_trades:
                latest_trade = matching_trades[0]
                open_price = latest_trade["price"]
                logger.info("reconciliation_found_open_trade", price=open_price, timestamp=latest_trade["timestamp"])
        except Exception as e:
            logger.error("reconciliation_open_fetch_failed", error=str(e))

        await self.database.log_trade_open(
            symbol=symbol, side=position.side, price=open_price, size=position.size,
            notional=position.notional, stop_loss=None, take_profit=None,
            expected_price=None, slippage=None, reason="reconciliation_detected_open",
        )

        await self.notifier.send(f"⚠️ **Reconciliation Alert**: Detected open position for {symbol}. Database updated.")
