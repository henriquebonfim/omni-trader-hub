import asyncio
import os
import signal

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from src.api.auth import verify_api_key

logger = structlog.get_logger()

router = APIRouter(prefix="/system", tags=["system"])


class RestartRequest(BaseModel):
    confirm: bool = False
    force: bool = False


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
