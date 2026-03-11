"""
OmniTrader API

FastAPI application factory. Call `create_api(bot)` to get a configured app
that can be run alongside the trading loop via asyncio.gather().
"""

from datetime import datetime, timezone

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import (
    bot,
    bots,
    candles,
    config,
    env,
    graph,
    indicators,
    notifications,
    status,
    strategies,
    system,
    trades,
)
from .websocket import router as ws_router

logger = structlog.get_logger()


def create_api(bot_instance=None, bot_manager=None) -> FastAPI:
    """
    Create and configure the FastAPI application.

    Args:
        bot_instance: (Legacy) Live OmniTrader instance shared with the trading loop.
        bot_manager: Orchestrates multiple OmniTrader instances.

    Returns:
        Configured FastAPI app ready to be served with uvicorn.
    """
    app = FastAPI(
        title="OmniTrader API",
        description="REST + WebSocket API for the OmniTrader dashboard",
        version="0.1.0",
    )

    # Store bot references
    app.state.bot_manager = bot_manager
    if bot_manager:
        # Provide fallback for legacy consumers
        bots_list = list(bot_manager.bots.values())
        app.state.bot = bot_manager.get_bot("default") or (bots_list[0] if bots_list else bot_instance)
    else:
        app.state.bot = bot_instance
    app.state.started_at = datetime.now(timezone.utc)

    # CORS — allow local dashboard dev servers
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize authentication
    from .auth import init_auth, is_dev_mode

    init_auth()

    # Warn if auth is auto-generated in production
    if getattr(app.state, "bot", None):
        paper_mode = getattr(app.state.bot.config.exchange, "paper_mode", True)
        if is_dev_mode() and not paper_mode:
            logger.warning(
                "auth_dev_mode_in_production",
                message="OMNITRADER_API_KEY is not set while paper_mode is False. Auth is auto-generated in production!",
            )

    # Mount routers
    app.include_router(status.router, prefix="/api")
    app.include_router(trades.router, prefix="/api")
    app.include_router(strategies.router, prefix="/api")
    app.include_router(config.router, prefix="/api")
    app.include_router(bot.router, prefix="/api")
    app.include_router(bots.router, prefix="/api")

    app.include_router(notifications.router, prefix="/api")
    app.include_router(candles.router, prefix="/api")
    app.include_router(graph.router, prefix="/api")
    app.include_router(indicators.router, prefix="/api")
    app.include_router(env.router, prefix="/api")
    app.include_router(system.router, prefix="/api")
    app.include_router(ws_router)

    @app.get("/api/health")
    async def health():
        return {"status": "ok"}

    return app
