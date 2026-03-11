import json
from typing import List, Optional

import structlog
from fastapi import APIRouter, Query, Request
from pydantic import BaseModel

logger = structlog.get_logger()

router = APIRouter(tags=["markets"])

class MarketInfo(BaseModel):
    symbol: str
    base: str
    quote: str
    min_size: float
    tick_size: float
    volume_24h: float
    last_price: float
    status: str

@router.get("/markets", response_model=List[MarketInfo])
async def get_markets(
    request: Request,
    search: Optional[str] = Query(None, description="Filter by symbol, base or quote"),
    quote: Optional[str] = Query(None, description="Filter by quote currency (e.g., USDT)"),
    min_volume: Optional[float] = Query(None, description="Minimum 24h volume in quote currency"),
):
    """
    Fetch active Binance Futures perpetual pairs.
    Supports filtering and sorts by volume_24h descending. Max 100 results.
    Cached in Redis for 5 minutes.
    """
    bot = request.app.state.bot
    if not bot or not bot.exchange:
        return []

    cache_key = "api:markets:all"
    markets_data = []

    # Try to get from cache
    redis_store = bot.redis
    if redis_store:
        try:
            cached = await redis_store.get(cache_key)
            if cached:
                if isinstance(cached, bytes):
                    cached = cached.decode("utf-8")
                markets_data = json.loads(cached)
        except Exception as e:
            logger.warning("redis_cache_error_markets", error=str(e))

    # Fetch from exchange if not cached
    if not markets_data:
        try:
            markets_data = await bot.exchange.fetch_markets()
            # Cache the result for 5 minutes
            if redis_store:
                try:
                    await redis_store.set(cache_key, json.dumps(markets_data), ex=300)
                except Exception as e:
                    logger.warning("redis_cache_set_error_markets", error=str(e))
        except Exception as e:
            logger.error("exchange_fetch_markets_error", error=str(e))
            return []

    # Apply filters
    filtered_markets = []
    for m in markets_data:
        # Search filter
        if search:
            search_lower = search.lower()
            if (search_lower not in m.get("symbol", "").lower() and
                search_lower not in m.get("base", "").lower() and
                search_lower not in m.get("quote", "").lower()):
                continue
        
        # Quote filter
        if quote:
            if quote.lower() != m.get("quote", "").lower():
                continue

        # Min volume filter
        if min_volume is not None:
            if float(m.get("volume_24h", 0.0)) < min_volume:
                continue

        filtered_markets.append(m)

    # Sort by volume_24h descending
    filtered_markets.sort(key=lambda x: float(x.get("volume_24h", 0.0)), reverse=True)

    # Return top 100
    return filtered_markets[:100]

