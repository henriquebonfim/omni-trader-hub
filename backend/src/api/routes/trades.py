"""
Trades, daily summary, and equity curve routes.
"""

from fastapi import APIRouter, Depends, Query, Request

from ..auth import verify_api_key

router = APIRouter(tags=["trades"], dependencies=[Depends(verify_api_key)])


@router.get("/trades")
async def get_trades(
    request: Request,
    limit: int = Query(default=50, ge=1, le=500),
    symbol: str | None = Query(
        None, description="Filter trades by trading pair, e.g. BTC/USDT"
    ),
):
    """Recent trade history, optionally filtered by symbol."""
    bot = request.app.state.bot
    trades = await bot.database.get_recent_trades(limit=limit)
    if symbol:
        trades = [t for t in trades if t.get("symbol") == symbol]
    return {"trades": trades, "count": len(trades)}


@router.get("/signals")
async def get_signals(
    request: Request,
    limit: int = Query(default=20, ge=1, le=100),
    symbol: str | None = Query(
        None, description="Filter signals by trading pair, e.g. BTC/USDT"
    ),
):
    """Recent strategy signals, optionally filtered by symbol."""
    bot = request.app.state.bot
    signals = await bot.database.get_recent_signals(symbol=symbol, limit=limit)
    return {"signals": signals, "count": len(signals)}


@router.get("/equity")
async def get_equity(
    request: Request,
    limit: int = Query(default=200, ge=1, le=1000),
):
    """Equity snapshots for chart rendering."""
    bot = request.app.state.bot
    snapshots = await bot.database.get_equity_snapshots(limit=limit)
    # Return in chronological order for charting
    return {"snapshots": list(reversed(snapshots)), "count": len(snapshots)}
