"""
OmniTrader API

FastAPI application factory. Call `create_api(bot)` to get a configured app
that can be run alongside the trading loop via asyncio.gather().
"""

import os
from datetime import datetime, timezone

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import bot, candles, config, notifications, status, strategies, trades
from .websocket import router as ws_router

logger = structlog.get_logger()


def create_api(bot_instance) -> FastAPI:
    """
    Create and configure the FastAPI application.

    Args:
        bot_instance: Live OmniTrader instance shared with the trading loop.

    Returns:
        Configured FastAPI app ready to be served with uvicorn.
    """
    app = FastAPI(
        title="OmniTrader API",
        description="REST + WebSocket API for the OmniTrader dashboard",
        version="0.1.0",
    )

    # Store bot reference — accessible in routes via request.app.state.bot
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

    # Check for API key and log warning if missing
    if not os.getenv("OMNITRADER_API_KEY"):
        logger.warning(
            "api_auth_disabled",
            message="OMNITRADER_API_KEY not set in environment. API endpoints are UNPROTECTED.",
        )

    # Mount routers
    app.include_router(status.router, prefix="/api")
    app.include_router(trades.router, prefix="/api")
    app.include_router(strategies.router, prefix="/api")
    app.include_router(config.router, prefix="/api")
    app.include_router(bot.router, prefix="/api")
    app.include_router(notifications.router, prefix="/api")
    app.include_router(candles.router, prefix="/api")
    app.include_router(ws_router)

    @app.get("/api/health")
    async def health():
        return {"status": "ok"}

    return app
