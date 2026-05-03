"""
Status, balance, and position routes.
"""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Request

from ..auth import get_api_key, is_dev_mode
from ..schemas import StatusResponse

router = APIRouter(tags=["status"])


@router.get("/health")
async def health_check():
    """Health check endpoint for watchdogs."""
    return {"status": "ok", "timestamp": datetime.now(UTC).isoformat()}


@router.get("/status", response_model=StatusResponse)
async def get_status(request: Request):
    """Bot status — running state, uptime, symbol, paper mode. Aggregated if multiple bots."""
    manager = getattr(request.app.state, "bot_manager", None)
    started_at: datetime = request.app.state.started_at
    uptime_seconds = int((datetime.now(UTC) - started_at).total_seconds())

    # Initialize enhanced fields
    last_trade: dict[str, Any] | None = None
    position_data: dict[str, Any] | None = None
    risk_metrics: dict[str, Any] | None = None
    strategy_indicators: dict[str, Any] | None = None

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

        # Gather enhanced metrics for single bot case
        if len(manager.bots) == 1:
            try:
                # 1. Last trade details
                if primary_bot.database:
                    trade = await primary_bot.database.get_last_trade(symbol)
                    if trade:
                        last_trade = {
                            "timestamp": trade.get("timestamp"),
                            "side": trade.get("side"),
                            "price": trade.get("price"),
                            "size": trade.get("size"),
                            "pnl": trade.get("pnl"),
                        }

                # 2. Current position
                if primary_bot.exchange:
                    pos = await primary_bot.exchange.get_position(symbol)
                    if pos and pos.is_open:
                        position_data = {
                            "side": pos.side,
                            "size": pos.size,
                            "entry_price": pos.entry_price,
                            "unrealized_pnl": pos.unrealized_pnl,
                        }

                # 3. Risk metrics
                if primary_bot.risk:
                    daily_stats = primary_bot.risk.daily_stats
                    risk_metrics = {
                        "daily_pnl_pct": daily_stats.pnl_pct if daily_stats else 0.0,
                        "win_rate": daily_stats.win_rate if daily_stats else 0.0,
                        "trades_today": daily_stats.trades_count if daily_stats else 0,
                    }

                # 4. Strategy indicators (most recent)
                if hasattr(primary_bot, "strategy_state"):
                    strategy_indicators = getattr(primary_bot.strategy_state, "indicators", {})
            except Exception:
                pass

        return StatusResponse(
            running=running_count > 0,
            running_count=running_count,
            total_bots=len(manager.bots),
            symbol=symbol,
            paper_mode=paper_mode,
            strategy=strategy,
            uptime_seconds=uptime_seconds,
            circuit_breaker_active=cb_active,
            ws_clients=ws_clients,
            last_trade=last_trade,
            position=position_data,
            risk_metrics=risk_metrics,
            strategy_indicators=strategy_indicators,
        )
    else:
        # Fallback for single-bot legacy
        bot = request.app.state.bot
        ws_clients = 0
        if bot.ws_manager:
            ws_clients = await bot.ws_manager.get_client_count()

        symbol = bot.config.trading.symbol
        try:
            if bot.database:
                trade = await bot.database.get_last_trade(symbol)
                if trade:
                    last_trade = {
                        "timestamp": trade.get("timestamp"),
                        "side": trade.get("side"),
                        "price": trade.get("price"),
                        "size": trade.get("size"),
                        "pnl": trade.get("pnl"),
                    }
            if bot.exchange:
                pos = await bot.exchange.get_position(symbol)
                if pos and pos.is_open:
                    position_data = {
                        "side": pos.side,
                        "size": pos.size,
                        "entry_price": pos.entry_price,
                        "unrealized_pnl": pos.unrealized_pnl,
                    }
            if bot.risk:
                daily_stats = bot.risk.daily_stats
                risk_metrics = {
                    "daily_pnl_pct": daily_stats.pnl_pct if daily_stats else 0.0,
                    "win_rate": daily_stats.win_rate if daily_stats else 0.0,
                    "trades_today": daily_stats.trades_count if daily_stats else 0,
                }
            if hasattr(bot, "strategy_state"):
                strategy_indicators = getattr(bot.strategy_state, "indicators", {})
        except Exception:
            pass

        return StatusResponse(
            running=bot._running,
            symbol=symbol,
            paper_mode=bot.exchange.paper_mode,
            strategy=getattr(bot.config.strategy, "name", "ema_volume"),
            uptime_seconds=uptime_seconds,
            circuit_breaker_active=bot.risk.check_circuit_breaker(),
            ws_clients=ws_clients,
            last_trade=last_trade,
            position=position_data,
            risk_metrics=risk_metrics,
            strategy_indicators=strategy_indicators,
        )


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
