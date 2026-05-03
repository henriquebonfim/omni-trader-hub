"""
WebSocket feed — maintains live-streamed market data via CCXT WebSocket API.

Replaces per-cycle REST polling for price and OHLCV with persistent WebSocket
subscriptions.  REST remains as a fallback when the WS cache is not yet warm.

Streaming channels:
    - ``watch_ticker``  → real-time last-price cache (public)
    - ``watch_ohlcv``   → rolling OHLCV DataFrame per timeframe (public)
    - ``watch_orders``  → live order-fill events (authenticated; live mode only)

Usage::

    feed = WsFeed(symbol="BTC/USDT:USDT", timeframes=["1m", "5m"])
    feed.seed_ohlcv("1m", rest_df)          # pre-populate from REST
    await feed.start()

    ticker  = feed.latest_ticker()          # dict | None
    df_1m   = feed.latest_ohlcv("1m")      # pd.DataFrame | None
    fills   = feed.recent_fills()           # list[dict]

    await feed.stop()
"""

import asyncio
import time
from collections import deque

import ccxt.pro as ccxtpro
import pandas as pd
import structlog

logger = structlog.get_logger()

# Maximum candles to keep in the rolling OHLCV cache per timeframe.
_MAX_OHLCV_ROWS = 500

_OHLCV_COLS = ["timestamp", "open", "high", "low", "close", "volume"]


def _raw_to_df(raw: list[list]) -> pd.DataFrame:
    """Convert a raw CCXT OHLCV list of lists to a DatetimeIndex DataFrame."""
    df = pd.DataFrame(raw, columns=_OHLCV_COLS)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    return df


class WsFeed:
    """
    Persistent WebSocket feed for live market data.

    Parameters
    ----------
    symbol:
        CCXT unified symbol, e.g. ``"BTC/USDT:USDT"``.
    timeframes:
        Timeframes to subscribe, e.g. ``["1m", "5m", "1h"]``.
    api_key / api_secret:
        Exchange credentials.  Only required for ``watch_orders`` (live mode).
    paper_mode:
        When *True*, ``watch_orders`` is skipped (no auth needed for public
        channels).
    """

    def __init__(
        self,
        symbol: str,
        timeframes: list[str],
        api_key: str | None = None,
        api_secret: str | None = None,
        paper_mode: bool = True,
    ) -> None:
        self._symbol = symbol
        self._timeframes = list(timeframes)
        self._paper_mode = paper_mode

        exchange_config = {
            "enableRateLimit": True,
            "options": {"defaultType": "swap"},
        }

        if not self._paper_mode:
            exchange_config["apiKey"] = api_key
            exchange_config["secret"] = api_secret

        self._client = ccxtpro.binanceusdm(exchange_config)

        # Caches
        self._ticker: dict | None = None
        self._last_ticker_update_time: float = 0.0
        self._ohlcv: dict[str, pd.DataFrame] = {}
        self._fills: deque[dict] = deque(maxlen=50)

        # Streaming tasks
        self._tasks: list[asyncio.Task] = []
        self._stopped = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Launch background WebSocket streaming tasks."""
        self._stopped = False
        self._tasks.append(asyncio.create_task(self._stream_ticker(), name="ws-ticker"))
        for tf in self._timeframes:
            self._tasks.append(
                asyncio.create_task(self._stream_ohlcv(tf), name=f"ws-ohlcv-{tf}")
            )
        if not self._paper_mode:
            self._tasks.append(
                asyncio.create_task(self._stream_orders(), name="ws-orders")
            )
        logger.info(
            "ws_feed_started",
            symbol=self._symbol,
            timeframes=self._timeframes,
            paper_mode=self._paper_mode,
        )

    async def stop(self) -> None:
        """Cancel all streaming tasks and close the WebSocket client."""
        self._stopped = True
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        try:
            await self._client.close()
        except Exception:
            pass
        logger.info("ws_feed_stopped")

    # ------------------------------------------------------------------
    # Seeding
    # ------------------------------------------------------------------

    def seed_ohlcv(self, timeframe: str, df: pd.DataFrame) -> None:
        """
        Pre-populate the OHLCV cache for *timeframe* with *df*.

        Called once per timeframe after the first REST fetch so that subsequent
        cycles can use the WS-maintained cache instead of calling REST again.
        """
        if df.empty:
            return
        trimmed = df.iloc[-_MAX_OHLCV_ROWS:]
        self._ohlcv[timeframe] = trimmed.copy()
        logger.debug("ws_feed_seeded", timeframe=timeframe, rows=len(trimmed))

    # ------------------------------------------------------------------
    # Public accessors
    # ------------------------------------------------------------------

    def latest_ticker(self) -> dict | None:
        """Return the most recent ticker dict, or *None* if not yet received."""
        return self._ticker

    def ticker_age(self) -> float:
        """
        Return the age of the latest ticker update in seconds.
        Returns float('inf') if no ticker has been received yet.
        """
        if self._last_ticker_update_time == 0.0:
            return float("inf")
        return time.time() - self._last_ticker_update_time

    def latest_ohlcv(self, timeframe: str) -> pd.DataFrame | None:
        """Return the most recent OHLCV DataFrame for *timeframe*, or *None*."""
        return self._ohlcv.get(timeframe)

    def recent_fills(self) -> list[dict]:
        """Return a snapshot of the most recent order fills (up to 50)."""
        return list(self._fills)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _merge_ohlcv(self, timeframe: str, new_candles: pd.DataFrame) -> None:
        """
        Merge *new_candles* into the cached DataFrame for *timeframe*.

        Rows with matching timestamps are updated (the forming candle changes on
        every tick); genuinely new timestamps are appended.  The cache is trimmed
        to ``_MAX_OHLCV_ROWS``.
        """
        existing = self._ohlcv.get(timeframe)
        if existing is None or existing.empty:
            self._ohlcv[timeframe] = new_candles.iloc[-_MAX_OHLCV_ROWS:]
            return

        merged = pd.concat([existing, new_candles])
        merged = merged[~merged.index.duplicated(keep="last")]
        merged.sort_index(inplace=True)
        self._ohlcv[timeframe] = merged.iloc[-_MAX_OHLCV_ROWS:]

    # ------------------------------------------------------------------
    # Streaming loops
    # ------------------------------------------------------------------

    async def _stream_ticker(self) -> None:
        """Continuously watch the live ticker and update the cache."""
        while not self._stopped:
            try:
                ticker = await self._client.watch_ticker(self._symbol)
                self._ticker = ticker
                self._last_ticker_update_time = time.time()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.warning("ws_ticker_reconnecting", error=str(exc))
                await asyncio.sleep(5)

    async def _stream_ohlcv(self, timeframe: str) -> None:
        """
        Continuously watch the OHLCV stream and maintain a rolling DataFrame.

        ``watch_ohlcv`` delivers the currently forming candle on each update.
        We merge it into the existing cache so that the last row in
        ``latest_ohlcv(tf)`` is always the most recent real-time candle.
        """
        while not self._stopped:
            try:
                raw = await self._client.watch_ohlcv(self._symbol, timeframe)
                if raw:
                    new_candles = _raw_to_df(raw)
                    self._merge_ohlcv(timeframe, new_candles)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.warning(
                    "ws_ohlcv_reconnecting", timeframe=timeframe, error=str(exc)
                )
                await asyncio.sleep(5)

    async def _stream_orders(self) -> None:
        """
        Continuously watch order updates and collect fills.

        Only started in live (non-paper) mode because it requires authentication.
        """
        while not self._stopped:
            try:
                orders = await self._client.watch_orders(self._symbol)
                for order in orders:
                    if (
                        order.get("status") == "closed"
                        and float(order.get("filled", 0)) > 0
                    ):
                        self._fills.append(order)
                        logger.info(
                            "ws_order_fill",
                            order_id=order.get("id"),
                            side=order.get("side"),
                            filled=order.get("filled"),
                            price=order.get("average"),
                        )
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.warning("ws_orders_reconnecting", error=str(exc))
                await asyncio.sleep(5)
