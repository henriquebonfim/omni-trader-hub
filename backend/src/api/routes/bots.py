import asyncio

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from src.api.auth import verify_api_key
from src.api.schemas import ConfigUpdate

router = APIRouter(prefix="/bots", tags=["bots"])


class BotCreateRequest(BaseModel):
    config: dict


class BotUpdateRequest(BaseModel):
    config: dict


class TradeRequest(BaseModel):
    side: str


@router.get("")
async def list_bots(request: Request):
    """List all registered bots."""
    manager = request.app.state.bot_manager
    if not manager:
        return []
    return manager.list_bots()


@router.post("", dependencies=[Depends(verify_api_key)])
async def create_bot(request: Request, body: BotCreateRequest):
    """Create a new bot with specified configuration overrides."""
    manager = request.app.state.bot_manager
    if not manager:
        raise HTTPException(status_code=500, detail="Bot manager not initialized")
    bot_id = await manager.create_bot(body.config)
    return {"ok": True, "bot_id": bot_id}


@router.get("/{bot_id}")
async def get_bot(request: Request, bot_id: str):
    """Get details for a specific bot."""
    manager = request.app.state.bot_manager
    bot = manager.get_bot(bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    return {
        "id": bot_id,
        "config": bot.config.to_dict(),
        "running": bot._running,
        "circuit_breaker_active": bot.risk.check_circuit_breaker(),
        "daily_pnl": bot.risk.daily_stats.realized_pnl,
        "daily_pnl_pct": bot.risk.daily_stats.pnl_pct,
        "trades_today": bot.risk.daily_stats.trades_count,
        "wins": bot.risk.daily_stats.wins,
        "losses": bot.risk.daily_stats.losses,
    }


@router.put("/{bot_id}", dependencies=[Depends(verify_api_key)])
async def update_bot(request: Request, bot_id: str, body: ConfigUpdate):
    """Update a specific bot's configuration."""
    manager = request.app.state.bot_manager
    try:
        # Pass the validated model payload as dictionary
        updated = await manager.update_bot(bot_id, body.model_dump(exclude_unset=True))
        if not updated:
            raise HTTPException(status_code=404, detail="Bot not found")
        return {"ok": True, "message": "Bot updated"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/{bot_id}", dependencies=[Depends(verify_api_key)])
async def delete_bot(request: Request, bot_id: str):
    """Delete a bot instance."""
    manager = request.app.state.bot_manager
    deleted = await manager.delete_bot(bot_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Bot not found")
    return {"ok": True, "message": "Bot deleted"}


@router.post("/{bot_id}/start", dependencies=[Depends(verify_api_key)])
async def start_bot(request: Request, bot_id: str):
    """Start a specific bot."""
    manager = request.app.state.bot_manager
    bot = manager.get_bot(bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    success = await manager.start_bot(bot_id)
    if not success:
        return {
            "ok": False,
            "message": "Bot is already running or could not be started",
        }
    return {"ok": True, "message": "Bot started"}


@router.post("/{bot_id}/stop", dependencies=[Depends(verify_api_key)])
async def stop_bot(request: Request, bot_id: str, confirm: bool = False):
    """Stop a specific bot."""
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="This endpoint is destructive. Pass confirm=true to proceed.",
        )

    manager = request.app.state.bot_manager
    bot = manager.get_bot(bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    success = await manager.stop_bot(bot_id)
    if not success:
        return {"ok": False, "message": "Bot is not running or could not be stopped"}
    return {"ok": True, "message": "Bot stopped"}


@router.post("/{bot_id}/trade/open", dependencies=[Depends(verify_api_key)])
async def manual_open_trade(request: Request, bot_id: str, body: TradeRequest):
    """Manually open a trade on a specific bot."""
    manager = request.app.state.bot_manager
    bot = manager.get_bot(bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

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

    asyncio.create_task(
        bot._open_position(body.side, current_price, balance, reason="manual_trade")
    )

    return {"ok": True, "message": f"Manual {body.side} order initiated"}


@router.post("/{bot_id}/trade/close", dependencies=[Depends(verify_api_key)])
async def manual_close_trade(request: Request, bot_id: str):
    """Manually close a trade on a specific bot."""
    manager = request.app.state.bot_manager
    bot = manager.get_bot(bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

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
