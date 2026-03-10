from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request

from src.api.auth import verify_api_key
from src.intelligence.analytics import GraphAnalytics

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/sentiment/{symbol:path}")
async def get_sentiment(symbol: str, request: Request) -> Dict[str, Any]:
    """Get aggregate sentiment for an asset."""
    bot = request.app.state.bot
    ga = GraphAnalytics(bot.database)
    sentiment = await ga.get_asset_sentiment(symbol)
    return sentiment


@router.get("/crisis")
async def get_crisis_mode(request: Request) -> Dict[str, Any]:
    """Get current global crisis state."""
    bot = request.app.state.bot
    state = await bot.crisis_manager.get_crisis_state()
    return state


@router.put("/crisis")
async def update_crisis_mode(
    request: Request,
    active: bool,
    reason: str = "Manual override via API",
    api_key: str = Depends(verify_api_key),
) -> Dict[str, Any]:
    """Manually activate or deactivate crisis mode."""
    bot = request.app.state.bot
    await bot.crisis_manager.set_crisis_mode(active, reason)
    state = await bot.crisis_manager.get_crisis_state()
    return {"status": "success", "state": state}


@router.get("/news/{symbol:path}")
async def get_asset_news(
    symbol: str, request: Request, limit: int = 10
) -> Dict[str, Any]:
    """Get recent news mentions for an asset."""
    bot = request.app.state.bot

    query = """
    MATCH (n:NewsEvent)-[r:MENTIONS]->(a:Asset {symbol: $symbol})
    RETURN
        n.title as title,
        n.timestamp as timestamp,
        r.sentiment as sentiment,
        n.source as source
    ORDER BY n.timestamp DESC
    LIMIT $limit
    """

    news = []
    try:
        async with bot.database._driver.session() as session:
            result = await session.run(query, symbol=symbol, limit=limit)
            records = await result.fetch(limit)

            for record in records:
                news.append(
                    {
                        "title": record.get("title", ""),
                        "timestamp": record.get("timestamp", 0),
                        "sentiment": record.get("sentiment", 0.0),
                        "source": record.get("source", ""),
                    }
                )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    return {"symbol": symbol, "news": news}
