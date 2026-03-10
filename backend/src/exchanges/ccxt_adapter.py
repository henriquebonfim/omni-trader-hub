"""
Binance Futures exchange wrapper using CCXT.

Handles all exchange interactions: data fetching, order placement, position management.
"""

import asyncio
import os
import time
import uuid

import ccxt.async_support as ccxt
import pandas as pd
import structlog

from ..config import get_config
from ..rate_limiter import LeakyBucketRateLimiter
from .base import BaseExchange, Position

logger = structlog.get_logger()


class CCXTExchange(BaseExchange):
    """
    Binance Futures exchange wrapper.

    Provides a clean interface for:
    - Fetching market data (OHLCV, ticker)
    - Getting account info (balance, positions)
    - Placing orders (market, limit, stop)
    - Managing positions
    """

    def __init__(self):
        config = get_config()

        self.paper_mode = getattr(config.exchange, "paper_mode", False)

        exchange_config = {
            "apiKey": None,  # Not needed for paper mode
            "secret": None,
            "enableRateLimit": True,
            "options": {
                "defaultType": "swap",  # Perpetual futures
                "adjustForTimeDifference": True,
            },
        }

        # Only add API keys if not in paper mode
        if not self.paper_mode:
            exchange_config["apiKey"] = os.getenv("BINANCE_API_KEY")
            exchange_config["secret"] = os.getenv("BINANCE_SECRET")

        # Paper trading state
        self._paper_balance = 10000.0  # $10k simulated
        self._paper_position: dict | None = None
        self._paper_orders: list = []  # Track paper orders
        self._paper_trades: list = []  # Track paper trade history

        self.client = ccxt.binance(exchange_config)
        self.config = config
        self._markets_loaded = False
        self._rate_limiter = LeakyBucketRateLimiter()

    def _check_paper_orders(self, current_price: float):
        """
        Evaluate active paper protective orders (SL/TP) against current market price.
        If a crossover occurs, execute the close at the order's trigger price.
        """
        if not self.paper_mode or not self._paper_position:
            return

        side = self._paper_position.get("side")
        symbol = self._paper_position.get("symbol")
        contracts = self._paper_position.get("contracts", 0)

        if contracts <= 0:
            return

        triggered_order = None
        trigger_price = None

        for order in self._paper_orders:
            if order.get("status") != "open" or order.get("symbol") != symbol:
                continue

            order_type = order.get("type")
            if order_type == "stop_market":
                stop_price = order.get("stopPrice")
                if stop_price is None:
                    continue

                if side == "long" and current_price <= stop_price:
                    triggered_order = order
                    trigger_price = stop_price
                    break
                elif side == "short" and current_price >= stop_price:
                    triggered_order = order
                    trigger_price = stop_price
                    break

            elif order_type == "take_profit_market":
                tp_price = order.get("take_profit_price") or order.get("stopPrice")
                if tp_price is None:
                    continue

                if side == "long" and current_price >= tp_price:
                    triggered_order = order
                    trigger_price = tp_price
                    break
                elif side == "short" and current_price <= tp_price:
                    triggered_order = order
                    trigger_price = tp_price
                    break

        if triggered_order and trigger_price is not None:
            # Execute the order at the trigger price
            exit_price = trigger_price
            entry_price = self._paper_position.get("entryPrice", 0.0)

            # Calculate PnL
            if side == "long":
                pnl = (exit_price - entry_price) * contracts
            else:
                pnl = (entry_price - exit_price) * contracts

            self._paper_balance += pnl

            close_side = "sell" if side == "long" else "buy"
            order_id = f"paper_close_{int(time.time() * 1000)}_{uuid.uuid4().hex[:6]}"

            self._paper_trades.append(
                {
                    "id": f"trade_{int(time.time() * 1000)}",
                    "order": order_id,
                    "symbol": symbol,
                    "side": close_side,
                    "price": exit_price,
                    "amount": contracts,
                    "cost": contracts * exit_price,
                    "fee": {
                        "cost": contracts * exit_price * 0.0004,
                        "currency": "USDT",
                    },
                    "timestamp": int(time.time() * 1000),
                    "datetime": pd.Timestamp.now(tz="UTC").isoformat(),
                }
            )

            # Mark order as closed, and reset position and orders
            triggered_order["status"] = "closed"
            self._paper_position = None
            self._paper_orders = []

            logger.info(
                "paper_order_triggered",
                symbol=symbol,
                side=side,
                order_type=triggered_order.get("type"),
                trigger_price=trigger_price,
                pnl=pnl,
            )

    async def _check_rate_limit(self):
        """
        Legacy stub — superseded by the proactive LeakyBucketRateLimiter.

        Kept for backward compatibility; calling code should use
        ``self._rate_limiter.acquire(endpoint)`` directly.
        """
        # No-op: the bucket limiter handles throttling proactively before
        # each CCXT call, so reactive header inspection is no longer needed.

    async def update_config(self, config):
        """Update exchange configuration."""
        old_paper_mode = self.paper_mode
        self.config = config
        self.paper_mode = getattr(config.exchange, "paper_mode", False)

        # If switching from Paper -> Live, we need to load API keys
        if old_paper_mode and not self.paper_mode:
            api_key = os.getenv("BINANCE_API_KEY")
            secret = os.getenv("BINANCE_SECRET")

            if not api_key or not secret:
                logger.error("cannot_switch_to_live_missing_keys")
                # Revert to paper mode for safety
                self.paper_mode = True
                return

            # Re-initialize client with keys
            exchange_config = {
                "apiKey": api_key,
                "secret": secret,
                "enableRateLimit": True,
                "options": {
                    "defaultType": "swap",
                    "adjustForTimeDifference": True,
                },
            }
            await self.client.close()
            self.client = ccxt.binance(exchange_config)
            await self.client.load_markets()
            logger.info("switched_to_live_trading")

        # If switching from Live -> Paper, reset client
        elif not old_paper_mode and self.paper_mode:
            exchange_config = {
                "apiKey": None,
                "secret": None,
                "enableRateLimit": True,
                "options": {
                    "defaultType": "swap",
                    "adjustForTimeDifference": True,
                },
            }
            await self.client.close()
            self.client = ccxt.binance(exchange_config)
            await self.client.load_markets()
            logger.info("switched_to_paper_trading")

        # Attempt to update leverage if live
        if not self.paper_mode and self._markets_loaded:
            symbol = self.config.trading.symbol
            leverage = self.config.exchange.leverage
            try:
                await self.client.set_leverage(leverage, symbol)
                logger.info("leverage_updated", symbol=symbol, leverage=leverage)
            except Exception as e:
                logger.warning("leverage_update_failed", error=str(e))

    async def connect(self) -> bool:
        """
        Initialize connection to exchange.

        Returns:
            True if connection successful
        """
        try:
            await self.client.load_markets()
            self._markets_loaded = True
        except Exception as e:
            if self.paper_mode:
                logger.warning(
                    "exchange_connection_failed_paper_mode_offline", error=str(e)
                )
                self._markets_loaded = False
                # Continue in offline paper mode
            else:
                logger.error("exchange_connection_failed", error=str(e))
                raise

        symbol = self.config.trading.symbol

        if self.paper_mode:
            logger.info("paper_mode_enabled", balance=self._paper_balance)
            logger.info("exchange_connected", paper_mode=True, symbol=symbol)
            return True

        if self._markets_loaded:
            # Set leverage and margin type for trading symbol (live only)
            leverage = self.config.exchange.leverage

            try:
                await self.client.set_leverage(leverage, symbol)
                logger.info("leverage_set", symbol=symbol, leverage=leverage)
            except Exception as e:
                logger.warning("leverage_set_failed", error=str(e))

            try:
                margin_type = self.config.exchange.margin_type.upper()
                await self.client.set_margin_mode(margin_type, symbol)
                logger.info("margin_mode_set", symbol=symbol, mode=margin_type)
            except Exception as e:
                logger.warning("margin_mode_set_failed", error=str(e))

            logger.info("exchange_connected", paper_mode=False, symbol=symbol)
            return True

        # Should be unreachable if raise happens in except block for non-paper mode,
        # but as a safety for live mode if _markets_loaded is somehow False without exception:
        raise ConnectionError("Failed to connect to exchange in live mode.")

    async def close(self):
        """Close exchange connection."""
        await self.client.close()
        logger.info("exchange_disconnected")

    async def fetch_ohlcv(
        self, symbol: str | None = None, timeframe: str | None = None, limit: int = 100
    ) -> pd.DataFrame:
        """
        Fetch OHLCV candle data.

        Args:
            symbol: Trading pair (default from config)
            timeframe: Candle timeframe (default from config)
            limit: Number of candles to fetch

        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        await self._rate_limiter.acquire("fetch_ohlcv")
        symbol = symbol or self.config.trading.symbol
        timeframe = timeframe or self.config.trading.timeframe

        ohlcv = await self.client.fetch_ohlcv(symbol, timeframe, limit=limit)

        df = pd.DataFrame(
            ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"]
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)

        if self.paper_mode and not df.empty:
            self._check_paper_orders(float(df["close"].iloc[-1]))

        return df

    async def get_ticker(self, symbol: str | None = None) -> dict:
        """Get current ticker for symbol."""
        await self._rate_limiter.acquire("fetch_ticker")
        symbol = symbol or self.config.trading.symbol

        if self.paper_mode and not self._markets_loaded:
            # Fallback for offline paper mode
            return {
                "last": 50000.0,
                "symbol": symbol,
                "timestamp": int(time.time() * 1000),
            }

        ticker = await self.client.fetch_ticker(symbol)

        if self.paper_mode:
            last_price = ticker.get("last")
            if last_price is not None:
                self._check_paper_orders(float(last_price))

        return ticker

    async def get_balance(self) -> dict:
        """
        Get account balance.

        Returns:
            Dict with 'total', 'free', 'used' USDT balances
        """
        if self.paper_mode:
            used = 0.0
            if self._paper_position:
                used = abs(self._paper_position.get("notional", 0))
            return {
                "total": self._paper_balance,
                "free": self._paper_balance - used,
                "used": used,
            }

        await self._rate_limiter.acquire("fetch_balance")
        balance = await self.client.fetch_balance()
        usdt = balance.get("USDT", {})
        return {
            "total": float(usdt.get("total", 0)),
            "free": float(usdt.get("free", 0)),
            "used": float(usdt.get("used", 0)),
        }

    async def get_position(self, symbol: str | None = None) -> Position:
        """
        Get current position for symbol.

        Returns:
            Position object (may be empty if no position)
        """
        symbol = symbol or self.config.trading.symbol

        if self.paper_mode:
            if self._paper_position and self._paper_position.get("symbol") == symbol:
                return Position(self._paper_position)
            return Position()

        await self._rate_limiter.acquire("fetch_positions")
        positions = await self.client.fetch_positions([symbol])

        for pos in positions:
            if pos["symbol"] == symbol and float(pos.get("contracts", 0)) > 0:
                return Position(pos)

        return Position()  # Empty position

    async def get_open_positions(self) -> list[Position]:
        """
        Get all current open positions across all symbols.

        Returns:
            List of Position objects that are currently open.
        """
        if self.paper_mode:
            if self._paper_position and self._paper_position.get("contracts", 0) > 0:
                return [Position(self._paper_position)]
            return []

        await self._rate_limiter.acquire("fetch_positions")
        # Fetch positions for all symbols by passing no symbol list
        positions = await self.client.fetch_positions()

        open_positions = []
        for pos in positions:
            if float(pos.get("contracts", 0)) > 0:
                open_positions.append(Position(pos))

        return open_positions

    async def fetch_open_orders(self, symbol: str | None = None) -> list:
        """Get all open orders for symbol."""
        symbol = symbol or self.config.trading.symbol
        if self.paper_mode:
            return [
                o
                for o in self._paper_orders
                if o["status"] == "open" and o["symbol"] == symbol
            ]

        await self._rate_limiter.acquire("fetch_open_orders")
        return await self.client.fetch_open_orders(symbol)

    async def market_long(
        self, symbol: str | None = None, amount: float = None
    ) -> dict:
        """
        Open a long position with market order.

        Args:
            symbol: Trading pair
            amount: Position size in contracts (base currency)

        Returns:
            Order result
        """
        if amount is None or amount <= 0:
            raise ValueError(f"market_long requires amount > 0, got {amount}")

        symbol = symbol or self.config.trading.symbol

        if self.paper_mode:
            ticker = await self.get_ticker(symbol)
            price = ticker["last"]
            leverage = self.config.exchange.leverage
            notional = amount * price

            self._paper_position = {
                "symbol": symbol,
                "side": "long",
                "contracts": amount,
                "entryPrice": price,
                "notional": notional,
                "unrealizedPnl": 0.0,
                "leverage": leverage,
                "liquidationPrice": price * (1 - 1 / leverage * 0.9),
            }

            order_id = f"paper_{int(time.time() * 1000)}_{uuid.uuid4().hex[:6]}"
            order = {
                "id": order_id,
                "symbol": symbol,
                "side": "buy",
                "type": "market",
                "amount": amount,
                "price": price,
                "average": price,
                "filled": amount,
                "status": "closed",
                "fees": [
                    {"cost": amount * price * 0.0004, "currency": "USDT"}
                ],  # 0.04% fee simulation
            }

            # Log paper trade
            self._paper_trades.append(
                {
                    "id": f"trade_{int(time.time() * 1000)}",
                    "order": order_id,
                    "symbol": symbol,
                    "side": "buy",
                    "price": price,
                    "amount": amount,
                    "cost": notional,
                    "fee": {"cost": amount * price * 0.0004, "currency": "USDT"},
                    "timestamp": int(time.time() * 1000),
                    "datetime": pd.Timestamp.now(tz="UTC").isoformat(),
                }
            )

            logger.info("paper_long_opened", symbol=symbol, amount=amount, price=price)
            return order

        await self._rate_limiter.acquire("create_order")
        order = await self.client.create_market_buy_order(
            symbol,
            amount,
            params={},
        )

        logger.info("long_opened", symbol=symbol, amount=amount, order_id=order["id"])
        return order

    async def market_short(
        self, symbol: str | None = None, amount: float = None
    ) -> dict:
        """
        Open a short position with market order.

        Args:
            symbol: Trading pair
            amount: Position size in contracts (base currency)

        Returns:
            Order result
        """
        if amount is None or amount <= 0:
            raise ValueError(f"market_short requires amount > 0, got {amount}")

        symbol = symbol or self.config.trading.symbol

        if self.paper_mode:
            ticker = await self.get_ticker(symbol)
            price = ticker["last"]
            leverage = self.config.exchange.leverage
            notional = amount * price

            self._paper_position = {
                "symbol": symbol,
                "side": "short",
                "contracts": amount,
                "entryPrice": price,
                "notional": notional,
                "unrealizedPnl": 0.0,
                "leverage": leverage,
                "liquidationPrice": price * (1 + 1 / leverage * 0.9),
            }

            order_id = f"paper_{int(time.time() * 1000)}_{uuid.uuid4().hex[:6]}"
            order = {
                "id": order_id,
                "symbol": symbol,
                "side": "sell",
                "type": "market",
                "amount": amount,
                "price": price,
                "average": price,
                "filled": amount,
                "status": "closed",
                "fees": [{"cost": amount * price * 0.0004, "currency": "USDT"}],
            }

            # Log paper trade
            self._paper_trades.append(
                {
                    "id": f"trade_{int(time.time() * 1000)}",
                    "order": order_id,
                    "symbol": symbol,
                    "side": "sell",
                    "price": price,
                    "amount": amount,
                    "cost": notional,
                    "fee": {"cost": amount * price * 0.0004, "currency": "USDT"},
                    "timestamp": int(time.time() * 1000),
                    "datetime": pd.Timestamp.now(tz="UTC").isoformat(),
                }
            )

            logger.info("paper_short_opened", symbol=symbol, amount=amount, price=price)
            return order

        await self._rate_limiter.acquire("create_order")
        order = await self.client.create_market_sell_order(
            symbol,
            amount,
            params={},
        )

        logger.info("short_opened", symbol=symbol, amount=amount, order_id=order["id"])
        return order

    async def close_position(self, symbol: str | None = None) -> dict | None:
        """
        Close the current position.

        Returns:
            Order result or None if no position
        """
        symbol = symbol or self.config.trading.symbol
        position = await self.get_position(symbol)

        if not position.is_open:
            logger.warning("no_position_to_close", symbol=symbol)
            return None

        if self.paper_mode:
            ticker = await self.get_ticker(symbol)
            exit_price = ticker["last"]
            entry_price = position.entry_price

            # Calculate PnL
            if position.side == "long":
                pnl = (exit_price - entry_price) * position.contracts
            else:
                pnl = (entry_price - exit_price) * position.contracts

            self._paper_balance += pnl

            side = "sell" if position.side == "long" else "buy"
            order_id = f"paper_{int(time.time() * 1000)}_{uuid.uuid4().hex[:6]}"

            order = {
                "id": order_id,
                "symbol": symbol,
                "side": side,
                "type": "market",
                "amount": position.size,
                "price": exit_price,
                "average": exit_price,
                "filled": position.size,
                "status": "closed",
                "pnl": pnl,
                "fees": [{"cost": position.notional * 0.0004, "currency": "USDT"}],
            }

            # Log paper trade
            self._paper_trades.append(
                {
                    "id": f"trade_{int(time.time() * 1000)}",
                    "order": order_id,
                    "symbol": symbol,
                    "side": side,
                    "price": exit_price,
                    "amount": position.size,
                    "cost": position.size * exit_price,
                    "fee": {
                        "cost": position.size * exit_price * 0.0004,
                        "currency": "USDT",
                    },
                    "timestamp": int(time.time() * 1000),
                    "datetime": pd.Timestamp.now(tz="UTC").isoformat(),
                }
            )

            self._paper_position = None
            self._paper_orders = []  # Cancel all paper orders
            logger.info(
                "paper_position_closed",
                symbol=symbol,
                side=position.side,
                size=position.size,
                pnl=pnl,
                new_balance=self._paper_balance,
            )
            return order

        # Close by opening opposite position
        await self._rate_limiter.acquire("create_order")
        if position.side == "long":
            order = await self.client.create_market_sell_order(
                symbol, position.size, params={"reduceOnly": True}
            )
        else:
            order = await self.client.create_market_buy_order(
                symbol, position.size, params={"reduceOnly": True}
            )

        logger.info(
            "position_closed",
            symbol=symbol,
            side=position.side,
            size=position.size,
            pnl=position.unrealized_pnl,
        )
        return order

    async def set_stop_loss(
        self,
        symbol: str | None = None,
        stop_price: float = None,
        position_side: str = "long",
    ) -> dict:
        """
        Place a stop-loss order.

        Args:
            symbol: Trading pair
            stop_price: Price to trigger stop
            position_side: "long" or "short"

        Returns:
            Order result
        """
        symbol = symbol or self.config.trading.symbol
        position = await self.get_position(symbol)

        if not position.is_open:
            raise ValueError("No position to set stop loss for")

        # For long position, sell to close; for short, buy to close
        side = "sell" if position.side == "long" else "buy"

        if self.paper_mode:
            # Cancel existing SL orders
            self._paper_orders = [
                o for o in self._paper_orders if o["type"] != "stop_market"
            ]

            order = {
                "id": f"paper_sl_{int(time.time() * 1000)}",
                "symbol": symbol,
                "type": "stop_market",
                "side": side,
                "stopPrice": stop_price,
                "status": "open",
            }
            self._paper_orders.append(order)
            logger.info("paper_stop_loss_set", symbol=symbol, stop_price=stop_price)
            return order

        # Cancel existing open STOP_MARKET orders to replace them
        await self._rate_limiter.acquire("fetch_open_orders")
        open_orders = await self.client.fetch_open_orders(symbol)
        cancel_tasks = [
            self.client.cancel_order(o["id"], symbol)
            for o in open_orders
            if o["type"] == "STOP_MARKET"
        ]
        if cancel_tasks:
            await asyncio.gather(*cancel_tasks)

        order = await self.client.create_order(
            symbol,
            type="STOP_MARKET",
            side=side,
            amount=position.size,
            params={
                "stopPrice": stop_price,
                "reduceOnly": True,
                "closePosition": True,
            },
        )

        logger.info("stop_loss_set", symbol=symbol, stop_price=stop_price)
        return order

    async def set_take_profit(
        self,
        symbol: str | None = None,
        take_profit_price: float = None,
        position_side: str = "long",
    ) -> dict:
        """
        Place a take-profit order.

        Args:
            symbol: Trading pair
            take_profit_price: Price to take profit
            position_side: "long" or "short"

        Returns:
            Order result
        """
        symbol = symbol or self.config.trading.symbol
        position = await self.get_position(symbol)

        if not position.is_open:
            raise ValueError("No position to set take profit for")

        # For long position, sell to close; for short, buy to close
        side = "sell" if position.side == "long" else "buy"

        if self.paper_mode:
            # Cancel existing TP orders
            self._paper_orders = [
                o for o in self._paper_orders if o["type"] != "take_profit_market"
            ]

            order = {
                "id": f"paper_tp_{int(time.time() * 1000)}",
                "symbol": symbol,
                "type": "take_profit_market",
                "side": side,
                "take_profit_price": take_profit_price,
                "status": "open",
            }
            self._paper_orders.append(order)
            logger.info(
                "paper_take_profit_set", symbol=symbol, tp_price=take_profit_price
            )
            return order

        # Cancel existing open TAKE_PROFIT_MARKET orders
        await self._rate_limiter.acquire("fetch_open_orders")
        open_orders = await self.client.fetch_open_orders(symbol)
        cancel_tasks = [
            self.client.cancel_order(o["id"], symbol)
            for o in open_orders
            if o["type"] == "TAKE_PROFIT_MARKET"
        ]
        if cancel_tasks:
            await asyncio.gather(*cancel_tasks)

        order = await self.client.create_order(
            symbol,
            type="TAKE_PROFIT_MARKET",
            side=side,
            amount=position.size,
            params={
                "stopPrice": take_profit_price,
                "reduceOnly": True,
                "closePosition": True,
            },
        )

        logger.info("take_profit_set", symbol=symbol, tp_price=take_profit_price)
        return order

    async def cancel_all_orders(self, symbol: str | None = None) -> list:
        """Cancel all open orders for symbol."""
        symbol = symbol or self.config.trading.symbol
        if self.paper_mode:
            self._paper_orders = []
            logger.info("orders_cancelled", symbol=symbol, count=0)
            return []

        await self._rate_limiter.acquire("cancel_all_orders")
        orders = await self.client.cancel_all_orders(symbol)
        logger.info("orders_cancelled", symbol=symbol, count=len(orders))
        return orders

    async def get_current_price(self, symbol: str | None = None) -> float:
        """Get current market price."""
        ticker = await self.get_ticker(symbol)
        return float(ticker["last"])

    async def fetch_my_trades(
        self, symbol: str | None = None, limit: int = 10, since: int = None
    ) -> list:
        """
        Fetch user's trade history.

        Args:
            symbol: Trading pair
            limit: Number of trades to fetch
            since: Timestamp in ms to fetch from

        Returns:
            List of trade dictionaries
        """
        symbol = symbol or self.config.trading.symbol

        if self.paper_mode:
            trades = [t for t in self._paper_trades if t["symbol"] == symbol]
            if since:
                trades = [t for t in trades if t["timestamp"] >= since]

            # Sort by timestamp desc and take limit?
            # CCXT usually returns ascending.
            trades.sort(key=lambda x: x["timestamp"])

            # If limit is applied, it's usually the *last* N trades or first N after since?
            # CCXT default is usually most recent if no since, or starting from since.
            if limit:
                trades = trades[-limit:]

            return trades

        await self._rate_limiter.acquire("fetch_my_trades")
        return await self.client.fetch_my_trades(symbol, since=since, limit=limit)

    async def fetch_funding_rate(self, symbol: str | None = None) -> float:
        """
        Fetch current funding rate for symbol.

        Returns:
            Funding rate (e.g. 0.0001 for 0.01%)
        """
        symbol = symbol or self.config.trading.symbol

        if self.paper_mode and not self._markets_loaded:
            return 0.0001  # 0.01% dummy rate

        try:
            funding_info = await self.client.fetch_funding_rate(symbol)
            return float(funding_info.get("fundingRate", 0.0))
        except Exception as e:
            logger.warning("fetch_funding_rate_failed", error=str(e))
            return 0.0

    async def get_rate_limit_usage(self) -> dict:
        """
        Get current API rate limit usage.

        Returns:
            Dict with leaky-bucket status plus Binance response-header weight
            (if available from the last live request).
        """
        bucket = self._rate_limiter.status()

        if self.paper_mode:
            return {"source": "paper", "bucket": bucket}

        result: dict = {"source": "live", "bucket": bucket}
        try:
            # CCXT stores last response headers in client.last_response_headers
            # Binance headers: x-mbx-used-weight, x-mbx-used-weight-1m
            if (
                hasattr(self.client, "last_response_headers")
                and self.client.last_response_headers
            ):
                headers = self.client.last_response_headers
                used_weight_1m = headers.get("x-mbx-used-weight-1m")
                used_weight = headers.get("x-mbx-used-weight")

                result["binance_used_weight_1m"] = (
                    int(used_weight_1m) if used_weight_1m else 0
                )
                result["binance_used_weight"] = int(used_weight) if used_weight else 0
        except Exception:
            pass

        return result

    async def get_order_fill_details(
        self,
        order_id: str,
        symbol: str | None = None,
        retries: int = 5,
        delay: float = 1.0,
    ) -> dict:
        """
        Verify order fills and return actual average price and fees.

        Args:
            order_id: The ID of the order to verify.
            symbol: Trading pair.
            retries: Number of times to retry fetching trades.
            delay: Seconds to wait between retries.

        Returns:
            Dict containing 'average_price', 'total_fee', 'fee_currency'.
        """
        symbol = symbol or self.config.trading.symbol

        logger.info("verifying_order_fills", order_id=order_id, symbol=symbol)

        for attempt in range(retries):
            try:
                # Fetch trades for this specific order
                # Note: Some exchanges support fetching order with trades, others require fetch_my_trades
                # Binance supports fetch_my_trades, filtering by order id client-side is robust
                trades = await self.fetch_my_trades(
                    symbol, limit=50
                )  # fetch recent trades

                # Filter for this order
                order_trades = [
                    t for t in trades if str(t.get("order")) == str(order_id)
                ]

                if not order_trades:
                    # If paper mode, it should be instant. If live, might take a moment.
                    if self.paper_mode:
                        # Should have been recorded immediately
                        logger.warning(
                            "paper_trade_not_found_retrying", order_id=order_id
                        )
                    else:
                        logger.debug("no_fills_found_retrying", attempt=attempt + 1)

                    await asyncio.sleep(delay)
                    continue

                # Calculate weighted average price
                total_cost = 0.0
                total_amount = 0.0
                total_fee = 0.0
                fee_currency = None

                for trade in order_trades:
                    amount = float(trade.get("amount", 0))
                    price = float(trade.get("price", 0))
                    cost = float(trade.get("cost", 0)) or (amount * price)

                    total_cost += cost
                    total_amount += amount

                    if trade.get("fee"):
                        total_fee += float(trade["fee"].get("cost", 0))
                        fee_currency = trade["fee"].get("currency")

                if total_amount == 0:
                    logger.warning("zero_amount_filled", order_id=order_id)
                    return {
                        "average_price": 0.0,
                        "total_fee": 0.0,
                        "fee_currency": None,
                    }

                average_price = total_cost / total_amount

                logger.info(
                    "order_verified",
                    order_id=order_id,
                    avg_price=average_price,
                    total_fee=total_fee,
                    currency=fee_currency,
                )

                return {
                    "average_price": average_price,
                    "total_fee": total_fee,
                    "fee_currency": fee_currency,
                    "confirmed": True,
                }

            except Exception as e:
                logger.error(
                    "order_verification_failed", error=str(e), attempt=attempt + 1
                )
                await asyncio.sleep(delay)

        # Fallback if verification fails
        logger.error("order_verification_timeout", order_id=order_id)
        return {
            "average_price": 0.0,
            "total_fee": 0.0,
            "fee_currency": None,
            "confirmed": False,
        }
