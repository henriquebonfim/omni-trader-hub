"""
Bot lifecycle control routes.
"""

import asyncio

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from src.api.auth import verify_api_key

router = APIRouter(prefix="/bot", tags=["bot"])


class TradeRequest(BaseModel):
    side: str


class RestartRequest(BaseModel):
    confirm: bool = False
    force: bool = False


@router.post("/start", dependencies=[Depends(verify_api_key)])
async def start_bot(request: Request):
    """Start the trading bot (no-op if already running)."""
    bot = request.app.state.bot
    if bot._running:
        return {"ok": False, "message": "Bot is already running"}
    await bot.start()
    return {"ok": True, "message": "Bot started"}


@router.post("/stop", dependencies=[Depends(verify_api_key)])
async def stop_bot(request: Request, confirm: bool = False):
    """Gracefully stop the trading bot."""
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="This endpoint is destructive. Pass confirm=true to proceed.",
        )
    bot = request.app.state.bot
    if not bot._running:
        return {"ok": False, "message": "Bot is not running"}
    await bot.stop("API stop request")
    return {"ok": True, "message": "Bot stopped"}


@router.post("/restart", dependencies=[Depends(verify_api_key)])
async def restart_bot(request: Request, body: RestartRequest):
    """Stop then start the trading bot."""
    if not body.confirm:
        raise HTTPException(
            status_code=400,
            detail="This endpoint is destructive. Pass confirm=true to proceed.",
        )

    bot = request.app.state.bot
    if bot._running:
        position = await bot.exchange.get_position(bot.config.trading.symbol)
        if position.is_open and not body.force:
            raise HTTPException(
                status_code=400,
                detail="Cannot restart bot with open positions. Pass force=true to override.",
            )
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


@router.post("/trade/open", dependencies=[Depends(verify_api_key)])
async def manual_open_trade(request: Request, body: TradeRequest):
    bot = request.app.state.bot
    if not bot._running:
        return {"ok": False, "message": "Bot is not running"}

    position = await bot.exchange.get_position(bot.config.trading.symbol)
    if position.is_open:
        return {"ok": False, "message": "Position already open"}

    ticker = bot.ws_feed.latest_ticker()
    if not ticker:
        return {"ok": False, "message": "No price data"}

    current_price = float(ticker.get("last", 0))
    balance = await bot.exchange.get_balance()

    # We call _open_position using create_task so it runs in background
    asyncio.create_task(
        bot._open_position(body.side, current_price, balance, reason="manual_trade")
    )

    return {"ok": True, "message": f"Manual {body.side} order initiated"}


@router.post("/trade/close", dependencies=[Depends(verify_api_key)])
async def manual_close_trade(request: Request):
    bot = request.app.state.bot
    if not bot._running:
        return {"ok": False, "message": "Bot is not running"}

    position = await bot.exchange.get_position(bot.config.trading.symbol)
    if not position.is_open:
        return {"ok": False, "message": "No open position"}

    ticker = bot.ws_feed.latest_ticker()
    if not ticker:
        return {"ok": False, "message": "No price data"}

    current_price = float(ticker.get("last", 0))

    asyncio.create_task(
        bot._close_position(position, current_price, reason="manual_close")
    )

    return {"ok": True, "message": "Manual close order initiated"}
