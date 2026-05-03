import asyncio
import os
import signal
from datetime import UTC, datetime

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from src.interfaces.api.auth import verify_api_key

logger = structlog.get_logger()

router = APIRouter(prefix="/system", tags=["system"])


class RestartRequest(BaseModel):
    confirm: bool = False
    force: bool = False


@router.get("/info")
async def get_system_info(request: Request):
    """System info: uptime, graph DB stats, exchange rate-limit usage, service health."""
    bot = request.app.state.bot
    started_at = request.app.state.started_at
    uptime_seconds = int((datetime.now(UTC) - started_at).total_seconds())

    # Rate limiter stats
    rate_limit_used = 0
    rate_limit_capacity = 2000
    try:
        rl = await bot.exchange.get_rate_limit_usage()
        bucket = rl.get("bucket", {})
        rate_limit_capacity = int(bucket.get("capacity", 2000))
        rate_limit_used = int(
            rate_limit_capacity - bucket.get("tokens_available", rate_limit_capacity)
        )
    except Exception:
        pass

    # Memgraph node / relationship counts
    node_count = 0
    rel_count = 0
    mg_ok = False
    try:
        db = bot.database
        if hasattr(db, "_driver") and db._driver:
            async with db._driver.session() as session:
                r = await session.run("MATCH (n) RETURN count(n) AS c")
                rec = await r.single()
                node_count = int(rec["c"]) if rec else 0
            async with db._driver.session() as session:
                r = await session.run("MATCH ()-[rel]->() RETURN count(rel) AS c")
                rec = await r.single()
                rel_count = int(rec["c"]) if rec else 0
            mg_ok = True
    except Exception:
        pass

    # Ollama model from config.graph section
    ollama_model = "llama3:8b"
    try:
        ollama_model = bot.config.graph.ollama_model
    except AttributeError:
        pass

    # Service status snapshot
    services = {
        "omnitrader": "running" if getattr(bot, "_running", False) else "stopped",
        "memgraph": "running" if mg_ok else "unreachable",
        "redis": "running",  # if the API responded, Redis is up
        "ollama": "running",  # assumed if model is configured
    }

    return {
        "uptime_seconds": uptime_seconds,
        "node_count": node_count,
        "relationship_count": rel_count,
        "rate_limit_used": rate_limit_used,
        "rate_limit_capacity": rate_limit_capacity,
        "ollama_model": ollama_model,
        "version": "2.4.1",
        "services": services,
    }


@router.post("/backup", dependencies=[Depends(verify_api_key)])
async def backup_database(request: Request):
    """Trigger a Memgraph snapshot backup."""
    bot = request.app.state.bot
    try:
        timestamp = await bot.database.backup_db()
        return {"ok": True, "timestamp": timestamp}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/restart", dependencies=[Depends(verify_api_key)])
async def restart_system(request: Request, body: RestartRequest):
    """
    Restart the backend system.
    Requires force=True if there are open positions.
    """
    bot = request.app.state.bot

    if not body.confirm:
        raise HTTPException(
            status_code=400,
            detail="This endpoint is destructive. Pass confirm=true to proceed.",
        )

    if bot and bot._running:
        # Check for open positions
        try:
            position = await bot.exchange.get_position(bot.config.trading.symbol)
            if position.is_open and not body.force:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot restart system with open positions. Pass force=True to override.",
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.error("restart_position_check_failed", error=str(e))
            if not body.force:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to check open positions. Pass force=True to override.",
                ) from e

        # Gracefully stop the bot before restarting
        logger.info("system_restart_requested", force=body.force)
        await bot.stop("System restart requested via API")
        await asyncio.sleep(1)  # Give it a moment to cleanup

    # Terminate the current python process
    # Docker/watchdog is expected to restart the container
    def _restart():
        logger.warning("terminating_process_for_restart")
        os.kill(os.getpid(), signal.SIGTERM)

    # Schedule the restart to allow the HTTP response to be returned first
    asyncio.get_running_loop().call_later(0.5, _restart)

    return {"ok": True, "message": "System restart initiated"}
