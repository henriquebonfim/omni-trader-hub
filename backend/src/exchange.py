"""
Binance Futures exchange wrapper using CCXT.

Handles all exchange interactions: data fetching, order placement, position management.
"""

import asyncio

import ccxt.async_support as ccxt
import pandas as pd
import structlog

from .config import get_config

logger = structlog.get_logger()


class Position:
    """Represents a futures position."""

    def __init__(self, data: dict | None = None):
        if data is None:
            self.symbol = None
            self.side = None
            self.size = 0.0
            self.entry_price = 0.0
            self.notional = 0.0
            self.unrealized_pnl = 0.0
            self.leverage = 1
            self.liquidation_price = 0.0
        else:
            self.symbol = data.get("symbol")
            self.side = data.get("side")  # "long" or "short"
            self.size = float(data.get("contracts", 0))
            self.entry_price = float(data.get("entryPrice", 0))
            self.notional = float(data.get("notional", 0))
            self.unrealized_pnl = float(data.get("unrealizedPnl", 0))
            self.leverage = int(data.get("leverage", 1))
            self.liquidation_price = float(data.get("liquidationPrice", 0))

    @property
    def is_open(self) -> bool:
        return self.size > 0

    def __repr__(self) -> str:
        if not self.is_open:
            return "Position(None)"
        return f"Position({self.side} {self.size} @ {self.entry_price}, PnL: {self.unrealized_pnl:.2f})"


class Exchange:
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
            import os

            exchange_config["apiKey"] = os.getenv("BINANCE_API_KEY")
            exchange_config["secret"] = os.getenv("BINANCE_SECRET")

        # Paper trading state
        self._paper_balance = 10000.0  # $10k simulated
        self._paper_position: dict | None = None
        self._paper_orders: list = []  # Track paper orders

        self.client = ccxt.binance(exchange_config)
        self.config = config
        self._markets_loaded = False

    async def update_config(self, config):
        """Update exchange configuration."""
        old_paper_mode = self.paper_mode
        self.config = config
        self.paper_mode = getattr(config.exchange, "paper_mode", False)

        # If switching from Paper -> Live, we need to load API keys
        if old_paper_mode and not self.paper_mode:
            import os

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

            symbol = self.config.trading.symbol

            if self.paper_mode:
                logger.info("paper_mode_enabled", balance=self._paper_balance)
                logger.info("exchange_connected", paper_mode=True, symbol=symbol)
                return True

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

        except Exception as e:
            logger.error("exchange_connection_failed", error=str(e))
            raise

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
        symbol = symbol or self.config.trading.symbol
        timeframe = timeframe or self.config.trading.timeframe

        ohlcv = await self.client.fetch_ohlcv(symbol, timeframe, limit=limit)

        df = pd.DataFrame(
            ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"]
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)

        return df

    async def get_ticker(self, symbol: str | None = None) -> dict:
        """Get current ticker for symbol."""
        symbol = symbol or self.config.trading.symbol
        return await self.client.fetch_ticker(symbol)

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

        positions = await self.client.fetch_positions([symbol])

        for pos in positions:
            if pos["symbol"] == symbol and float(pos.get("contracts", 0)) > 0:
                return Position(pos)

        return Position()  # Empty position

    async def fetch_open_orders(self, symbol: str | None = None) -> list:
        """Get all open orders for symbol."""
        symbol = symbol or self.config.trading.symbol
        if self.paper_mode:
            return [
                o
                for o in self._paper_orders
                if o["status"] == "open" and o["symbol"] == symbol
            ]

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

            import time

            order = {
                "id": f"paper_{int(time.time() * 1000)}",
                "symbol": symbol,
                "side": "buy",
                "type": "market",
                "amount": amount,
                "price": price,
                "filled": amount,
                "status": "closed",
            }
            logger.info("paper_long_opened", symbol=symbol, amount=amount, price=price)
            return order

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

            import time

            order = {
                "id": f"paper_{int(time.time() * 1000)}",
                "symbol": symbol,
                "side": "sell",
                "type": "market",
                "amount": amount,
                "price": price,
                "filled": amount,
                "status": "closed",
            }
            logger.info("paper_short_opened", symbol=symbol, amount=amount, price=price)
            return order

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
                pnl = (exit_price - entry_price) / entry_price * position.notional
            else:
                pnl = (entry_price - exit_price) / entry_price * position.notional

            self._paper_balance += pnl

            import time

            order = {
                "id": f"paper_{int(time.time() * 1000)}",
                "symbol": symbol,
                "side": "sell" if position.side == "long" else "buy",
                "type": "market",
                "amount": position.size,
                "price": exit_price,
                "filled": position.size,
                "status": "closed",
                "pnl": pnl,
            }

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

            import time

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
        open_orders = await self.client.fetch_open_orders(symbol)
        orders_to_cancel = [o for o in open_orders if o["type"] == "STOP_MARKET"]
        if orders_to_cancel:
            tasks = [self.client.cancel_order(o["id"], symbol) for o in orders_to_cancel]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for o, res in zip(orders_to_cancel, results):
                if isinstance(res, Exception):
                    logger.warning(
                        "stop_loss_cancel_failed", order_id=o.get("id"), error=str(res)
                    )

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

            import time

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
        open_orders = await self.client.fetch_open_orders(symbol)
        orders_to_cancel = [o for o in open_orders if o["type"] == "TAKE_PROFIT_MARKET"]
        if orders_to_cancel:
            tasks = [self.client.cancel_order(o["id"], symbol) for o in orders_to_cancel]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for o, res in zip(orders_to_cancel, results):
                if isinstance(res, Exception):
                    logger.warning(
                        "take_profit_cancel_failed", order_id=o.get("id"), error=str(res)
                    )

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

        orders = await self.client.cancel_all_orders(symbol)
        logger.info("orders_cancelled", symbol=symbol, count=len(orders))
        return orders

    async def get_current_price(self, symbol: str | None = None) -> float:
        """Get current market price."""
        ticker = await self.get_ticker(symbol)
        return float(ticker["last"])
