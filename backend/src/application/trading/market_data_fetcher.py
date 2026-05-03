import asyncio
from typing import Any

import structlog

logger = structlog.get_logger()


class MarketDataFetcher:
    """
    Responsible for gathering necessary market data (OHLCV, current price, trend)
    for a trading cycle.
    """

    def __init__(self, exchange, ws_feed, config, notifier=None):
        self.exchange = exchange
        self.ws_feed = ws_feed
        self.config = config
        self.notifier = notifier

    async def fetch_market_context(
        self, symbol: str, strategy
    ) -> tuple[dict[str, Any], Any, float, str] | None:
        """
        Fetch market data, resolve current price, and compute trend context.
        Returns Optional: (market_data_dict, primary_ohlcv, current_price, market_trend)
        If returning None, the cycle should be aborted (e.g. extremely stale data).
        """
        limit = max(
            getattr(self.config.trading, "ohlcv_limit", 100),
            strategy.required_candles,
        )

        required_timeframes = list(strategy.required_timeframes)
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
            if self.notifier is not None:
                age_str = int(ticker_age) if isinstance(ticker_age, (int, float)) else ticker_age
                await self.notifier.send(
                    f"⚠️ **Stale Data Alert**: WS ticker is {age_str}s old. Trading paused."
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
                market_trend = strategy.check_trend(trend_ohlcv)
            except Exception as e:
                logger.warning("trend_fetch_failed", error=str(e))

        return market_data, primary_ohlcv, current_price, market_trend
