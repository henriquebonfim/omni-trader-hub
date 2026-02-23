"""
Bot lifecycle control routes.
"""

import asyncio

from fastapi import APIRouter, Request

router = APIRouter(prefix="/bot", tags=["bot"])


@router.post("/start")
async def start_bot(request: Request):
    """Start the trading bot (no-op if already running)."""
    bot = request.app.state.bot
    if bot._running:
        return {"ok": False, "message": "Bot is already running"}
    await bot.start()
    return {"ok": True, "message": "Bot started"}


@router.post("/stop")
async def stop_bot(request: Request):
    """Gracefully stop the trading bot."""
    bot = request.app.state.bot
    if not bot._running:
        return {"ok": False, "message": "Bot is not running"}
    await bot.stop("API stop request")
    return {"ok": True, "message": "Bot stopped"}


@router.post("/restart")
async def restart_bot(request: Request):
    """Stop then start the trading bot."""
    bot = request.app.state.bot
    if bot._running:
        await bot.stop("API restart request")
        # Give the loop a moment to clean up
        await asyncio.sleep(1)
    await bot.start()
    return {"ok": True, "message": "Bot restarted"}


@router.get("/state")
async def get_state(request: Request):
    """Current bot lifecycle state."""
    bot = request.app.state.bot
    return {
        "running": bot._running,
        "circuit_breaker": bot.risk.check_circuit_breaker(),
        "daily_pnl": bot.risk.daily_stats.realized_pnl,
        "daily_pnl_pct": bot.risk.daily_stats.pnl_pct,
        "trades_today": bot.risk.daily_stats.trades_count,
        "wins": bot.risk.daily_stats.wins,
        "losses": bot.risk.daily_stats.losses,
    }
