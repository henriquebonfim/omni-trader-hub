import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from src.api.auth import verify_api_key
from src.intelligence.analytics import GraphAnalytics

router = APIRouter(prefix="/graph", tags=["graph"])


class CrisisUpdatePayload(BaseModel):
    active: bool
    reason: str | None = None


def _dedupe_keep_order(items: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def _resolve_symbols(request: Request, symbols: str | None) -> List[str]:
    if symbols:
        parts = [s.strip() for s in symbols.split(",") if s.strip()]
        return _dedupe_keep_order(parts)

    manager = request.app.state.bot_manager
    if manager:
        listed = manager.list_bots()
        running_symbols = [b["symbol"] for b in listed if b.get("running")]
        all_symbols = [b["symbol"] for b in listed]
        resolved = running_symbols or all_symbols
        if resolved:
            return _dedupe_keep_order(resolved)

    bot = request.app.state.bot
    return [bot.config.trading.symbol]


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
    active: bool | None = None,
    reason: str = "Manual override via API",
    payload: CrisisUpdatePayload | None = None,
    api_key: str = Depends(verify_api_key),
) -> Dict[str, Any]:
    """Manually activate or deactivate crisis mode."""
    # Backward-compatible input handling:
    # - query params: /graph/crisis?active=true&reason=...
    # - JSON body: {"active": true, "reason": "..."}
    if active is None and payload is not None:
        active = payload.active
        if payload.reason:
            reason = payload.reason
    if active is None:
        raise HTTPException(status_code=422, detail="active is required")

    bot = request.app.state.bot
    await bot.crisis_manager.set_crisis_mode(active, reason)
    state = await bot.crisis_manager.get_crisis_state()
    return {"status": "success", "state": state}


@router.get("/news")
async def get_news_feed(request: Request, limit: int = 20) -> List[Dict[str, Any]]:
    """Return latest cross-asset news feed for the intelligence page."""
    bot = request.app.state.bot

    query = """
    MATCH (n:NewsEvent)
    OPTIONAL MATCH (n)-[:MENTIONS]->(a:Asset)
    OPTIONAL MATCH (n)-[:MENTIONS]->(s:Sector)
    RETURN
      coalesce(n.id, toString(id(n))) as id,
      coalesce(n.title, "") as title,
      coalesce(n.source, "") as source,
      coalesce(n.published_at, n.timestamp, 0) as published_at,
      coalesce(n.sentiment_score, 0.0) as sentiment_score,
      coalesce(n.impact_level, 0.0) as impact_level,
      collect(DISTINCT a.symbol) as assets,
      collect(DISTINCT s.name) as sectors
    ORDER BY published_at DESC
    LIMIT $limit
    """

    try:
        async with bot.database._driver.session() as session:
            result = await session.run(query, limit=limit)
            records = await result.fetch(limit)
    except Exception:
        # Keep intelligence page resilient; frontend shows empty-state if feed is unavailable.
        return []

    items: List[Dict[str, Any]] = []
    for record in records:
        items.append(
            {
                "id": str(record.get("id", "")),
                "title": str(record.get("title", "")),
                "source": str(record.get("source", "")),
                "published_at": int(record.get("published_at", 0) or 0),
                "sentiment_score": float(record.get("sentiment_score", 0.0) or 0.0),
                "impact_level": float(record.get("impact_level", 0.0) or 0.0),
                "assets": [a for a in (record.get("assets") or []) if a],
                "sectors": [s for s in (record.get("sectors") or []) if s],
            }
        )
    return items


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
        coalesce(n.published_at, n.timestamp, 0) as timestamp,
        r.sentiment as sentiment,
        n.source as source
    ORDER BY timestamp DESC
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


@router.get("/macro")
async def get_macro_indicators(request: Request) -> List[Dict[str, Any]]:
    """Return latest MacroIndicator values stored in Memgraph."""
    bot = request.app.state.bot
    query = """
    MATCH (m:MacroIndicator)
    RETURN m.name AS name, m.value AS value, m.timestamp AS timestamp
    ORDER BY m.name
    """
    try:
        async with bot.database._driver.session() as session:
            result = await session.run(query)
            records = await result.fetch(100)
    except Exception:
        return []

    return [
        {
            "name": str(r.get("name", "")),
            "value": float(r.get("value", 0)),
            "timestamp": int(r.get("timestamp", 0) or 0),
        }
        for r in records
    ]


@router.get("/correlation-matrix")
async def get_correlation_matrix(
    request: Request,
    timeframe: str = "1h",
    limit: int = 120,
    symbols: str | None = None,
) -> Dict[str, Any]:
    """Return rolling return correlation matrix for active bot symbols."""
    if limit < 30 or limit > 1000:
        raise HTTPException(status_code=400, detail="limit must be between 30 and 1000")

    bot = request.app.state.bot
    target_symbols = _resolve_symbols(request, symbols)
    if not target_symbols:
        raise HTTPException(status_code=400, detail="No symbols available")

    ohlcv_tasks = [
        bot.exchange.fetch_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit)
        for symbol in target_symbols
    ]
    raw_results = await asyncio.gather(*ohlcv_tasks, return_exceptions=True)

    returns_columns: List[pd.Series] = []
    valid_symbols: List[str] = []

    for symbol, result in zip(target_symbols, raw_results, strict=False):
        if isinstance(result, Exception):
            continue
        if result is None or result.empty or "close" not in result.columns:
            continue

        close = pd.to_numeric(result["close"], errors="coerce")
        returns = close.pct_change().dropna()
        if returns.empty:
            continue
        returns.name = symbol
        returns_columns.append(returns)
        valid_symbols.append(symbol)

    if not returns_columns:
        raise HTTPException(
            status_code=400, detail="Not enough market data to compute correlations"
        )

    if len(returns_columns) == 1:
        return {
            "symbols": valid_symbols,
            "timeframe": timeframe,
            "window": int(len(returns_columns[0])),
            "matrix": [[1.0]],
            "as_of": int(datetime.now(timezone.utc).timestamp() * 1000),
        }

    returns_df = pd.concat(returns_columns, axis=1, join="inner").dropna()
    if returns_df.empty:
        raise HTTPException(
            status_code=400,
            detail="Not enough overlapping data to compute correlations",
        )

    corr = returns_df.corr().fillna(0.0)
    for idx in corr.index:
        corr.loc[idx, idx] = 1.0

    matrix = [
        [float(round(corr.loc[row, col], 4)) for col in valid_symbols]
        for row in valid_symbols
    ]

    return {
        "symbols": valid_symbols,
        "timeframe": timeframe,
        "window": int(len(returns_df)),
        "matrix": matrix,
        "as_of": int(datetime.now(timezone.utc).timestamp() * 1000),
    }
