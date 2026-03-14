"""
Status, balance, and position routes.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Request

from ..auth import get_api_key, is_dev_mode

router = APIRouter(tags=["status"])


@router.get("/health")
async def health_check():
    """Health check endpoint for watchdogs."""
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@router.get("/status")
async def get_status(request: Request):
    """Bot status — running state, uptime, symbol, paper mode. Aggregated if multiple bots."""
    manager = getattr(request.app.state, "bot_manager", None)
    started_at: datetime = request.app.state.started_at
    uptime_seconds = (datetime.now(timezone.utc) - started_at).total_seconds()

    if manager and manager.bots:
        # Aggregate multi-bot stats
        running_count = sum(1 for bot in manager.bots.values() if bot._running)
        cb_active = any(
            bot.risk.check_circuit_breaker() for bot in manager.bots.values()
        )
        paper_mode = all(
            getattr(bot.config.exchange, "paper_mode", True)
            for bot in manager.bots.values()
        )

        # Use primary bot for basic fields if there's only one, otherwise generalized
        primary_bot = manager.get_bot("default") or list(manager.bots.values())[0]
        symbol = (
            primary_bot.config.trading.symbol if len(manager.bots) == 1 else "multiple"
        )
        strategy = (
            getattr(primary_bot.config.strategy, "name", "unknown")
            if len(manager.bots) == 1
            else "multiple"
        )

        ws_clients = 0
        if primary_bot.ws_manager:
            ws_clients = await primary_bot.ws_manager.get_client_count()

        return {
            "running": running_count > 0,
            "running_count": running_count,
            "total_bots": len(manager.bots),
            "symbol": symbol,
            "paper_mode": paper_mode,
            "strategy": strategy,
            "uptime_seconds": int(uptime_seconds),
            "circuit_breaker_active": cb_active,
            "ws_clients": ws_clients,
        }
    else:
        # Fallback for single-bot legacy
        bot = request.app.state.bot
        ws_clients = 0
        if bot.ws_manager:
            ws_clients = await bot.ws_manager.get_client_count()

        return {
            "running": bot._running,
            "symbol": bot.config.trading.symbol,
            "paper_mode": bot.exchange.paper_mode,
            "strategy": getattr(bot.config.strategy, "name", "ema_volume"),
            "uptime_seconds": int(uptime_seconds),
            "circuit_breaker_active": bot.risk.check_circuit_breaker(),
            "ws_clients": ws_clients,
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


@router.get("/auth/key")
async def get_auth_key():
    """Get the API key for authentication (dev mode only)."""
    if not is_dev_mode():
        return {"error": "Not in dev mode"}
    return {"api_key": get_api_key()}
