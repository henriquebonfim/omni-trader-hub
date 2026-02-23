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
):
    """Recent trade history."""
    bot = request.app.state.bot
    trades = await bot.database.get_recent_trades(limit=limit)
    return {"trades": trades, "count": len(trades)}


@router.get("/daily-summary/{date}")
async def get_daily_summary(date: str, request: Request):
    """Daily performance summary for a given date (YYYY-MM-DD)."""
    bot = request.app.state.bot
    summary = await bot.database.get_daily_summary(date)
    if summary is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"No summary found for {date}")
    return summary


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
