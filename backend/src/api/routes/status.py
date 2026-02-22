"""
Status, balance, and position routes.
"""

from datetime import datetime

from fastapi import APIRouter, Request

router = APIRouter(tags=["status"])


@router.get("/status")
async def get_status(request: Request):
    """Bot status — running state, uptime, symbol, paper mode."""
    bot = request.app.state.bot
    started_at: datetime = request.app.state.started_at

    uptime_seconds = (datetime.utcnow() - started_at).total_seconds()

    return {
        "running": bot._running,
        "symbol": bot.config.trading.symbol,
        "paper_mode": bot.exchange.paper_mode,
        "strategy": getattr(bot.config.strategy, "name", "ema_volume"),
        "uptime_seconds": int(uptime_seconds),
        "circuit_breaker_active": bot.risk.check_circuit_breaker(),
        "ws_clients": await bot.ws_manager.get_client_count() if bot.ws_manager else 0,
    }


@router.get("/balance")
async def get_balance(request: Request):
    """Current account balance."""
    bot = request.app.state.bot
    balance = await bot.exchange.get_balance()
    return balance


@router.get("/position")
async def get_position(request: Request):
    """Current open position (or null if flat)."""
    bot = request.app.state.bot
    symbol = bot.config.trading.symbol
    position = await bot.exchange.get_position(symbol)

    if not position.is_open:
        return {"is_open": False}

    return {
        "is_open": True,
        "symbol": position.symbol,
        "side": position.side,
        "size": position.size,
        "entry_price": position.entry_price,
        "notional": position.notional,
        "unrealized_pnl": position.unrealized_pnl,
        "leverage": position.leverage,
        "liquidation_price": position.liquidation_price,
    }
