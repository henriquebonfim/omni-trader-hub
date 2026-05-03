"""
Direct Binance Futures REST API implementation.
"""

import asyncio
import hashlib
import hmac
import os
import time
import urllib.parse
import uuid
from typing import Any

import aiohttp
import pandas as pd
import structlog

from src.config import get_config
from ..rate_limiter import LeakyBucketRateLimiter
from .base import BaseExchange, ExchangeError, NetworkError, Position

logger = structlog.get_logger()


class BinanceDirectExchange(BaseExchange):
    """
    Binance Futures exchange wrapper using direct REST API.
    Provides identical public interface and paper trading functionality as CCXTExchange.
    """

    def __init__(self):
        config = get_config()
        self.config = config
        self.paper_mode = config.exchange.paper_mode
        self.testnet = config.exchange.testnet

        self.api_key = None
        self.secret = None

        if not self.paper_mode:
            self.api_key = os.getenv("BINANCE_API_KEY")
            self.secret = os.getenv("BINANCE_SECRET")

        if self.testnet:
            self.base_url = "https://testnet.binancefuture.com"
        else:
            self.base_url = "https://fapi.binance.com"

        self.session = None
        self._markets_loaded = False
        self._rate_limiter = LeakyBucketRateLimiter()

        # Paper trading state
        self._paper_balance = 10000.0  # $10k simulated
        self._paper_position: dict[str, Any] | None = None
        self._paper_orders: list[dict[str, Any]] = []
        self._paper_trades: list[dict[str, Any]] = []

    def _sign(self, params: dict[str, Any]) -> str:
        query_string = urllib.parse.urlencode(params)
        signature = hmac.new(
            self.secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return signature

    async def _request(
        self,
        method: str,
        endpoint: str,
        signed: bool = False,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not self.session:
            self.session = aiohttp.ClientSession()

        params = params or {}
        headers = {}

        if signed:
            if not self.api_key or not self.secret:
                raise ValueError("API keys required for signed requests")
            headers["X-MBX-APIKEY"] = self.api_key
            params["timestamp"] = int(time.time() * 1000)
            params["recvWindow"] = 5000
            params["signature"] = self._sign(params)
        elif self.api_key:
            headers["X-MBX-APIKEY"] = self.api_key

        url = f"{self.base_url}{endpoint}"

        # Mapping for rate limiter endpoints
        rl_endpoint = "default"
        if "klines" in endpoint:
            rl_endpoint = "fetch_ohlcv"
        elif "ticker" in endpoint:
            rl_endpoint = "fetch_ticker"
        elif "balance" in endpoint:
            rl_endpoint = "fetch_balance"
        elif "positionRisk" in endpoint:
            rl_endpoint = "fetch_positions"
        elif "openOrders" in endpoint:
            rl_endpoint = "fetch_open_orders"
        elif "order" in endpoint and method == "POST":
            rl_endpoint = "create_order"
        elif "allOpenOrders" in endpoint and method == "DELETE":
            rl_endpoint = "cancel_all_orders"
        elif "userTrades" in endpoint:
            rl_endpoint = "fetch_my_trades"

        await self._rate_limiter.acquire(rl_endpoint)

        for attempt in range(3):
            try:
                if method == "GET":
                    async with self.session.get(
                        url, params=params, headers=headers
                    ) as response:
                        self._last_headers = response.headers
                        data = await response.json()
                        if response.status >= 400:
                            logger.error(
                                "binance_api_error", status=response.status, data=data
                            )
                            raise ExchangeError(f"Binance API error: {data}")
                        return data
                elif method == "POST":
                    async with self.session.post(
                        url, data=params, headers=headers
                    ) as response:
                        self._last_headers = response.headers
                        data = await response.json()
                        if response.status >= 400:
                            logger.error(
                                "binance_api_error", status=response.status, data=data
                            )
                            raise ExchangeError(f"Binance API error: {data}")
                        return data
                elif method == "DELETE":
                    async with self.session.delete(
                        url, params=params, headers=headers
                    ) as response:
                        self._last_headers = response.headers
                        data = await response.json()
                        if response.status >= 400:
                            logger.error(
                                "binance_api_error", status=response.status, data=data
                            )
                            raise ExchangeError(f"Binance API error: {data}")
                        return data
            except aiohttp.ClientError as e:
                if attempt == 2:
                    raise NetworkError(
                        f"Network error during {method} {endpoint}: {e}"
                    ) from e
                await asyncio.sleep(1)
        return {}

    def _check_paper_orders(self, current_price: float):
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

                if side == "long" and current_price <= stop_price or side == "short" and current_price >= stop_price:
                    triggered_order = order
                    trigger_price = stop_price
                    break

            elif order_type == "take_profit_market":
                tp_price = order.get("take_profit_price") or order.get("stopPrice")
                if tp_price is None:
                    continue

                if side == "long" and current_price >= tp_price or side == "short" and current_price <= tp_price:
                    triggered_order = order
                    trigger_price = tp_price
                    break

        if triggered_order and trigger_price is not None:
            exit_price = trigger_price
            entry_price = self._paper_position.get("entryPrice", 0.0)

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

    async def update_config(self, config):
        old_paper_mode = self.paper_mode
        self.config = config
        self.paper_mode = config.exchange.paper_mode
        self.testnet = config.exchange.testnet

        if self.testnet:
            self.base_url = "https://testnet.binancefuture.com"
        else:
            self.base_url = "https://fapi.binance.com"

        if old_paper_mode and not self.paper_mode:
            self.api_key = os.getenv("BINANCE_API_KEY")
            self.secret = os.getenv("BINANCE_SECRET")
            if not self.api_key or not self.secret:
                logger.error("cannot_switch_to_live_missing_keys")
                self.paper_mode = True
                return
            logger.info("switched_to_live_trading")

        elif not old_paper_mode and self.paper_mode:
            self.api_key = None
            self.secret = None
            logger.info("switched_to_paper_trading")

        if not self.paper_mode and self._markets_loaded:
            symbol = self.config.trading.symbol
            # Transform symbol format: BTC/USDT or BTC/USDT:USDT -> BTCUSDT
            b_symbol = symbol.split(":")[0].replace("/", "")
            leverage = self.config.exchange.leverage
            try:
                await self._request(
                    "POST",
                    "/fapi/v1/leverage",
                    signed=True,
                    params={"symbol": b_symbol, "leverage": leverage},
                )
                logger.info("leverage_updated", symbol=symbol, leverage=leverage)
            except Exception as e:
                logger.warning("leverage_update_failed", error=str(e))

    async def connect(self) -> bool:
        if not self.session:
            self.session = aiohttp.ClientSession()

        try:
            # Ping exchange info
            await self._request("GET", "/fapi/v1/exchangeInfo")
            self._markets_loaded = True
        except Exception as e:
            if self.paper_mode:
                logger.warning(
                    "exchange_connection_failed_paper_mode_offline", error=str(e)
                )
                self._markets_loaded = False
            else:
                logger.error("exchange_connection_failed", error=str(e))
                raise

        symbol = self.config.trading.symbol

        if self.paper_mode:
            logger.info("paper_mode_enabled", balance=self._paper_balance)
            logger.info("exchange_connected", paper_mode=True, symbol=symbol)
            return True

        if self._markets_loaded:
            b_symbol = symbol.split(":")[0].replace("/", "")
            leverage = self.config.exchange.leverage
            try:
                await self._request(
                    "POST",
                    "/fapi/v1/leverage",
                    signed=True,
                    params={"symbol": b_symbol, "leverage": leverage},
                )
                logger.info("leverage_set", symbol=symbol, leverage=leverage)
            except Exception as e:
                logger.warning("leverage_set_failed", error=str(e))

            try:
                margin_type = self.config.exchange.margin_type.upper()
                await self._request(
                    "POST",
                    "/fapi/v1/marginType",
                    signed=True,
                    params={"symbol": b_symbol, "marginType": margin_type},
                )
                logger.info("margin_mode_set", symbol=symbol, mode=margin_type)
            except Exception as e:
                # Often fails if already set
                logger.debug("margin_mode_set_failed_or_already_set", error=str(e))

            logger.info("exchange_connected", paper_mode=False, symbol=symbol)
            return True

        raise ConnectionError("Failed to connect to exchange in live mode.")

    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None
        logger.info("exchange_disconnected")

    async def fetch_ohlcv(
        self,
        symbol: str | None = None,
        timeframe: str | None = None,
        limit: int = 100,
    ) -> pd.DataFrame:
        symbol = symbol or self.config.trading.symbol
        b_symbol = symbol.split(":")[0].replace("/", "")
        timeframe = timeframe or self.config.trading.timeframe

        # CCXT uses '1m', Binance uses '1m' etc, mapping is straightforward mostly

        data = await self._request(
            "GET",
            "/fapi/v1/klines",
            params={"symbol": b_symbol, "interval": timeframe, "limit": limit},
        )

        # Binance klines format: [Open time, Open, High, Low, Close, Volume, Close time, Quote asset volume, Number of trades, Taker buy base asset volume, Taker buy quote asset volume, Ignore]
        df = pd.DataFrame(
            data,
            columns=[
                "timestamp",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "close_time",
                "qav",
                "num_trades",
                "taker_base_vol",
                "taker_quote_vol",
                "ignore",
            ],
        )
        df = df[["timestamp", "open", "high", "low", "close", "volume"]]
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = df[col].astype(float)
        df.set_index("timestamp", inplace=True)

        if self.paper_mode and not df.empty:
            self._check_paper_orders(float(df["close"].iloc[-1]))

        return df

    async def fetch_candles(
        self,
        symbol: str | None = None,
        timeframe: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        symbol = symbol or self.config.trading.symbol
        b_symbol = symbol.split(":")[0].replace("/", "")
        timeframe = timeframe or self.config.trading.timeframe

        data = await self._request(
            "GET",
            "/fapi/v1/klines",
            params={"symbol": b_symbol, "interval": timeframe, "limit": limit},
        )

        result = []
        for candle in data:
            result.append(
                {
                    "timestamp": int(candle[0]),
                    "open": float(candle[1]),
                    "high": float(candle[2]),
                    "low": float(candle[3]),
                    "close": float(candle[4]),
                    "volume": float(candle[5]),
                }
            )

        if self.paper_mode and result:
            self._check_paper_orders(result[-1]["close"])

        return result

    async def get_ticker(self, symbol: str | None = None) -> dict[str, Any]:
        symbol = symbol or self.config.trading.symbol
        b_symbol = symbol.split(":")[0].replace("/", "")

        if self.paper_mode and not self._markets_loaded:
            return {
                "last": 50000.0,
                "symbol": symbol,
                "timestamp": int(time.time() * 1000),
            }

        data = await self._request(
            "GET", "/fapi/v1/ticker/24hr", params={"symbol": b_symbol}
        )
        # Wrap like CCXT
        ticker = {
            "symbol": symbol,
            "last": float(data.get("lastPrice", 0)),
            "timestamp": int(data.get("closeTime", time.time() * 1000)),
        }

        if self.paper_mode:
            self._check_paper_orders(ticker["last"])

        return ticker

    async def get_balance(self) -> dict[str, float]:
        if self.paper_mode:
            used = 0.0
            if self._paper_position:
                used = abs(self._paper_position.get("notional", 0))
            return {
                "total": self._paper_balance,
                "free": self._paper_balance - used,
                "used": used,
            }

        data = await self._request("GET", "/fapi/v2/balance", signed=True)
        # Find USDT
        usdt_bal = next((b for b in data if b["asset"] == "USDT"), {})

        total = float(usdt_bal.get("balance", 0))
        available = float(usdt_bal.get("availableBalance", 0))

        return {
            "total": total,
            "free": available,
            "used": total - available,
        }

    def _format_position(self, pos_data: dict, symbol: str) -> Position:
        amt = float(pos_data.get("positionAmt", 0))
        entry = float(pos_data.get("entryPrice", 0))
        unrealized = float(pos_data.get("unRealizedProfit", 0))
        notional = float(pos_data.get("notional", abs(amt * entry)))
        lev = int(pos_data.get("leverage", 1))
        liq = float(pos_data.get("liquidationPrice", 0))

        if amt == 0:
            return Position()

        side = "long" if amt > 0 else "short"
        return Position(
            {
                "symbol": symbol,
                "side": side,
                "contracts": abs(amt),
                "entryPrice": entry,
                "notional": notional,
                "unrealizedPnl": unrealized,
                "leverage": lev,
                "liquidationPrice": liq,
            }
        )

    async def get_position(self, symbol: str | None = None) -> Position:
        symbol = symbol or self.config.trading.symbol

        if self.paper_mode:
            if self._paper_position and self._paper_position.get("symbol") == symbol:
                return Position(self._paper_position)
            return Position()

        b_symbol = symbol.split(":")[0].replace("/", "")
        data = await self._request(
            "GET", "/fapi/v2/positionRisk", signed=True, params={"symbol": b_symbol}
        )

        if data and len(data) > 0:
            return self._format_position(data[0], symbol)

        return Position()

    async def get_open_positions(self) -> list[Position]:
        if self.paper_mode:
            if self._paper_position and self._paper_position.get("contracts", 0) > 0:
                return [Position(self._paper_position)]
            return []

        data = await self._request("GET", "/fapi/v2/positionRisk", signed=True)
        open_positions = []
        for pos in data:
            amt = float(pos.get("positionAmt", 0))
            if amt != 0:
                # Recover ccxt-like symbol format or just use what we have,
                # we'll approximate CCXT symbol mapping for simplicity if needed
                sym = pos["symbol"]
                if sym.endswith("USDT"):
                    sym = sym.replace("USDT", "/USDT:USDT")
                open_positions.append(self._format_position(pos, sym))

        return open_positions

    async def fetch_open_orders(
        self, symbol: str | None = None
    ) -> list[dict[str, Any]]:
        symbol = symbol or self.config.trading.symbol
        if self.paper_mode:
            return [
                o
                for o in self._paper_orders
                if o["status"] == "open" and o["symbol"] == symbol
            ]

        b_symbol = symbol.split(":")[0].replace("/", "")
        data = await self._request(
            "GET", "/fapi/v1/openOrders", signed=True, params={"symbol": b_symbol}
        )

        # Transform slightly to match expected CCXT keys
        orders = []
        for o in data:
            orders.append(
                {
                    "id": str(o.get("orderId")),
                    "symbol": symbol,
                    "type": o.get("type"),
                    "side": "buy" if o.get("side") == "BUY" else "sell",
                    "price": float(o.get("price", 0)),
                    "stopPrice": float(o.get("stopPrice", 0)),
                    "amount": float(o.get("origQty", 0)),
                    "status": "open",
                }
            )
        return orders

    def _execute_paper_market(
        self, symbol: str, amount: float, price: float, side: str
    ) -> dict[str, Any]:
        leverage = self.config.exchange.leverage
        notional = amount * price

        self._paper_position = {
            "symbol": symbol,
            "side": side,
            "contracts": amount,
            "entryPrice": price,
            "notional": notional,
            "unrealizedPnl": 0.0,
            "leverage": leverage,
            "liquidationPrice": price * (1 - 1 / leverage * 0.9)
            if side == "long"
            else price * (1 + 1 / leverage * 0.9),
        }

        order_id = f"paper_{int(time.time() * 1000)}_{uuid.uuid4().hex[:6]}"
        bs_side = "buy" if side == "long" else "sell"
        order = {
            "id": order_id,
            "symbol": symbol,
            "side": bs_side,
            "type": "market",
            "amount": amount,
            "price": price,
            "average": price,
            "filled": amount,
            "status": "closed",
            "fees": [{"cost": amount * price * 0.0004, "currency": "USDT"}],
        }

        self._paper_trades.append(
            {
                "id": f"trade_{int(time.time() * 1000)}",
                "order": order_id,
                "symbol": symbol,
                "side": bs_side,
                "price": price,
                "amount": amount,
                "cost": notional,
                "fee": {"cost": amount * price * 0.0004, "currency": "USDT"},
                "timestamp": int(time.time() * 1000),
                "datetime": pd.Timestamp.now(tz="UTC").isoformat(),
            }
        )

        logger.info(f"paper_{side}_opened", symbol=symbol, amount=amount, price=price)
        return order

    async def market_long(
        self, symbol: str | None = None, amount: float | None = None
    ) -> dict[str, Any]:
        if amount is None or amount <= 0:
            raise ValueError(f"market_long requires amount > 0, got {amount}")
        symbol = symbol or self.config.trading.symbol

        if self.paper_mode:
            ticker = await self.get_ticker(symbol)
            return self._execute_paper_market(symbol, amount, ticker["last"], "long")

        b_symbol = symbol.split(":")[0].replace("/", "")
        data = await self._request(
            "POST",
            "/fapi/v1/order",
            signed=True,
            params={
                "symbol": b_symbol,
                "side": "BUY",
                "type": "MARKET",
                "quantity": amount,
            },
        )

        logger.info(
            "long_opened", symbol=symbol, amount=amount, order_id=data.get("orderId")
        )
        return {"id": str(data.get("orderId"))}

    async def market_short(
        self, symbol: str | None = None, amount: float | None = None
    ) -> dict[str, Any]:
        if amount is None or amount <= 0:
            raise ValueError(f"market_short requires amount > 0, got {amount}")
        symbol = symbol or self.config.trading.symbol

        if self.paper_mode:
            ticker = await self.get_ticker(symbol)
            return self._execute_paper_market(symbol, amount, ticker["last"], "short")

        b_symbol = symbol.split(":")[0].replace("/", "")
        data = await self._request(
            "POST",
            "/fapi/v1/order",
            signed=True,
            params={
                "symbol": b_symbol,
                "side": "SELL",
                "type": "MARKET",
                "quantity": amount,
            },
        )

        logger.info(
            "short_opened", symbol=symbol, amount=amount, order_id=data.get("orderId")
        )
        return {"id": str(data.get("orderId"))}

    async def close_position(
        self, symbol: str | None = None
    ) -> dict[str, Any] | None:
        symbol = symbol or self.config.trading.symbol
        position = await self.get_position(symbol)

        if not position.is_open:
            logger.warning("no_position_to_close", symbol=symbol)
            return None

        if self.paper_mode:
            ticker = await self.get_ticker(symbol)
            exit_price = ticker["last"]
            entry_price = position.entry_price

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
            self._paper_orders = []
            logger.info(
                "paper_position_closed",
                symbol=symbol,
                side=position.side,
                size=position.size,
                pnl=pnl,
            )
            return order

        b_symbol = symbol.split(":")[0].replace("/", "")
        side = "SELL" if position.side == "long" else "BUY"

        data = await self._request(
            "POST",
            "/fapi/v1/order",
            signed=True,
            params={
                "symbol": b_symbol,
                "side": side,
                "type": "MARKET",
                "quantity": position.size,
                "reduceOnly": "true",
            },
        )

        logger.info(
            "position_closed",
            symbol=symbol,
            side=position.side,
            size=position.size,
            pnl=position.unrealized_pnl,
        )
        return {"id": str(data.get("orderId"))}

    async def set_stop_loss(
        self,
        symbol: str | None = None,
        stop_price: float | None = None,
        position_side: str = "long",
    ) -> dict[str, Any]:
        symbol = symbol or self.config.trading.symbol
        position = await self.get_position(symbol)

        if not position.is_open:
            raise ValueError("No position to set stop loss for")

        side = "sell" if position.side == "long" else "buy"
        b_side = "SELL" if position.side == "long" else "BUY"

        if self.paper_mode:
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

        b_symbol = symbol.split(":")[0].replace("/", "")

        # Cancel open SLs
        open_orders = await self.fetch_open_orders(symbol)
        for o in open_orders:
            if o["type"] == "STOP_MARKET":
                await self._request(
                    "DELETE",
                    "/fapi/v1/order",
                    signed=True,
                    params={"symbol": b_symbol, "orderId": o["id"]},
                )

        data = await self._request(
            "POST",
            "/fapi/v1/order",
            signed=True,
            params={
                "symbol": b_symbol,
                "side": b_side,
                "type": "STOP_MARKET",
                "stopPrice": stop_price,
                "closePosition": "true",
                "timeInForce": "GTC",
            },
        )

        logger.info("stop_loss_set", symbol=symbol, stop_price=stop_price)
        return {"id": str(data.get("orderId"))}

    async def set_take_profit(
        self,
        symbol: str | None = None,
        take_profit_price: float | None = None,
        position_side: str = "long",
    ) -> dict[str, Any]:
        symbol = symbol or self.config.trading.symbol
        position = await self.get_position(symbol)

        if not position.is_open:
            raise ValueError("No position to set take profit for")

        side = "sell" if position.side == "long" else "buy"
        b_side = "SELL" if position.side == "long" else "BUY"

        if self.paper_mode:
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

        b_symbol = symbol.split(":")[0].replace("/", "")

        open_orders = await self.fetch_open_orders(symbol)
        for o in open_orders:
            if o["type"] == "TAKE_PROFIT_MARKET":
                await self._request(
                    "DELETE",
                    "/fapi/v1/order",
                    signed=True,
                    params={"symbol": b_symbol, "orderId": o["id"]},
                )

        data = await self._request(
            "POST",
            "/fapi/v1/order",
            signed=True,
            params={
                "symbol": b_symbol,
                "side": b_side,
                "type": "TAKE_PROFIT_MARKET",
                "stopPrice": take_profit_price,
                "closePosition": "true",
                "timeInForce": "GTC",
            },
        )

        logger.info("take_profit_set", symbol=symbol, tp_price=take_profit_price)
        return {"id": str(data.get("orderId"))}

    async def cancel_all_orders(
        self, symbol: str | None = None
    ) -> list[dict[str, Any]]:
        symbol = symbol or self.config.trading.symbol
        if self.paper_mode:
            self._paper_orders = []
            logger.info("orders_cancelled", symbol=symbol, count=0)
            return []

        b_symbol = symbol.split(":")[0].replace("/", "")
        await self._request(
            "DELETE", "/fapi/v1/allOpenOrders", signed=True, params={"symbol": b_symbol}
        )
        logger.info("orders_cancelled", symbol=symbol)
        # Fake return format since actual count not returned by this endpoint nicely
        return []

    async def get_current_price(self, symbol: str | None = None) -> float:
        ticker = await self.get_ticker(symbol)
        return float(ticker["last"])

    async def fetch_my_trades(
        self, symbol: str | None = None, limit: int = 10, since: int | None = None
    ) -> list[dict[str, Any]]:
        symbol = symbol or self.config.trading.symbol

        if self.paper_mode:
            trades = [t for t in self._paper_trades if t["symbol"] == symbol]
            if since:
                trades = [t for t in trades if t["timestamp"] >= since]
            trades.sort(key=lambda x: x["timestamp"])
            if limit:
                trades = trades[-limit:]
            return trades

        b_symbol = symbol.split(":")[0].replace("/", "")
        params = {"symbol": b_symbol, "limit": limit}
        if since:
            params["startTime"] = since

        data = await self._request(
            "GET", "/fapi/v1/userTrades", signed=True, params=params
        )

        trades = []
        for t in data:
            trades.append(
                {
                    "id": str(t.get("id")),
                    "order": str(t.get("orderId")),
                    "symbol": symbol,
                    "side": "buy" if t.get("buyer") else "sell",
                    "price": float(t.get("price", 0)),
                    "amount": float(t.get("qty", 0)),
                    "cost": float(t.get("quoteQty", 0)),
                    "fee": {
                        "cost": float(t.get("commission", 0)),
                        "currency": t.get("commissionAsset"),
                    },
                    "timestamp": t.get("time"),
                }
            )
        return trades

    async def fetch_funding_rate(self, symbol: str | None = None) -> float:
        symbol = symbol or self.config.trading.symbol
        if self.paper_mode and not self._markets_loaded:
            return 0.0001

        b_symbol = symbol.split(":")[0].replace("/", "")
        try:
            data = await self._request(
                "GET", "/fapi/v1/premiumIndex", params={"symbol": b_symbol}
            )
            if isinstance(data, list):
                data = data[0]
            return float(data.get("lastFundingRate", 0.0))
        except Exception as e:
            logger.warning("fetch_funding_rate_failed", error=str(e))
            return 0.0

    async def get_rate_limit_usage(self) -> dict[str, Any]:
        bucket = self._rate_limiter.status()
        if self.paper_mode:
            return {"source": "paper", "bucket": bucket}

        result = {"source": "live", "bucket": bucket}

        if hasattr(self, "_last_headers") and self._last_headers:
            result["binance_used_weight_1m"] = int(
                self._last_headers.get("x-mbx-used-weight-1m", 0)
            )
            result["binance_used_weight"] = int(
                self._last_headers.get("x-mbx-used-weight", 0)
            )

        return result

    async def get_order_fill_details(
        self,
        order_id: str,
        symbol: str | None = None,
        retries: int = 5,
        delay: float = 1.0,
    ) -> dict[str, Any]:
        symbol = symbol or self.config.trading.symbol
        logger.info("verifying_order_fills", order_id=order_id, symbol=symbol)

        for attempt in range(retries):
            try:
                trades = await self.fetch_my_trades(symbol, limit=50)
                order_trades = [
                    t for t in trades if str(t.get("order")) == str(order_id)
                ]

                if not order_trades:
                    if self.paper_mode:
                        logger.warning(
                            "paper_trade_not_found_retrying", order_id=order_id
                        )
                    else:
                        logger.debug("no_fills_found_retrying", attempt=attempt + 1)
                    await asyncio.sleep(delay)
                    continue

                total_cost = sum(t.get("cost", 0) for t in order_trades)
                total_amount = sum(t.get("amount", 0) for t in order_trades)
                total_fee = sum(
                    t.get("fee", {}).get("cost", 0)
                    for t in order_trades
                    if t.get("fee")
                )

                fee_currency = None
                for t in order_trades:
                    if t.get("fee") and t["fee"].get("currency"):
                        fee_currency = t["fee"]["currency"]
                        break

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

        logger.error("order_verification_timeout", order_id=order_id)
        return {
            "average_price": 0.0,
            "total_fee": 0.0,
            "fee_currency": None,
            "confirmed": False,
        }

    async def fetch_markets(self) -> list[dict[str, Any]]:
        """
        Fetch all active markets (symbols) from the exchange.
        """
        exchange_info = await self._public_request("GET", "/fapi/v1/exchangeInfo")
        tickers = await self._public_request("GET", "/fapi/v1/ticker/24hr")

        tickers_map = {t["symbol"]: t for t in tickers}

        result = []
        for symbol_info in exchange_info.get("symbols", []):
            if symbol_info.get("status") != "TRADING":
                continue
            if symbol_info.get("contractType") != "PERPETUAL":
                continue

            symbol = symbol_info["symbol"]

            # Format symbol to standard format (e.g. BTC/USDT)
            base = symbol_info.get("baseAsset", "")
            quote = symbol_info.get("quoteAsset", "")
            formatted_symbol = f"{base}/{quote}"

            ticker = tickers_map.get(symbol, {})

            min_size = 0.0
            tick_size = 0.0

            for f in symbol_info.get("filters", []):
                if f.get("filterType") == "PRICE_FILTER":
                    tick_size = float(f.get("tickSize", 0.0))
                elif f.get("filterType") == "LOT_SIZE":
                    min_size = float(f.get("minQty", 0.0))

            result.append(
                {
                    "symbol": formatted_symbol,
                    "base": base,
                    "quote": quote,
                    "min_size": min_size,
                    "tick_size": tick_size,
                    "volume_24h": float(ticker.get("quoteVolume", 0.0)),
                    "last_price": float(ticker.get("lastPrice", 0.0)),
                    "status": "active",
                }
            )

        return result
