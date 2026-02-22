"""
Discord notification config routes.
"""

from fastapi import APIRouter, Request
from pydantic import BaseModel
from pathlib import Path
import yaml

from .config import _CONFIG_PATH

router = APIRouter(prefix="/notifications", tags=["notifications"])


class DiscordWebhookPayload(BaseModel):
    webhook_url: str
    enabled: bool = True


@router.get("/discord")
async def get_discord_config(request: Request):
    """Return current Discord notification config (URL masked for security)."""
    bot = request.app.state.bot
    url = bot.notifier.webhook_url or ""
    masked = (url[:30] + "…") if len(url) > 30 else url
    return {
        "enabled": bot.notifier.enabled,
        "webhook_url_preview": masked,
        "configured": bool(url),
    }


@router.put("/discord")
async def update_discord_config(payload: DiscordWebhookPayload, request: Request):
    """Update Discord webhook URL and persist to config.yaml."""
    bot = request.app.state.bot

    # Update runtime
    bot.notifier.webhook_url = payload.webhook_url
    bot.notifier.enabled = payload.enabled

    # Persist to file
    try:
        with open(_CONFIG_PATH) as f:
            current = yaml.safe_load(f) or {}

        if "notifications" not in current:
            current["notifications"] = {}

        current["notifications"]["discord_webhook"] = payload.webhook_url
        current["notifications"]["enabled"] = payload.enabled

        with open(_CONFIG_PATH, "w") as f:
            yaml.dump(current, f, default_flow_style=False, allow_unicode=True)

        await bot.reload_config()

    except Exception as e:
        # Don't fail the request if persistence fails, but log it
        import structlog
        logger = structlog.get_logger()
        logger.error("discord_config_persist_failed", error=str(e))
        return {"ok": True, "message": "Updated in-memory (persistence failed)"}

    return {"ok": True, "message": "Discord config updated and saved"}


@router.post("/discord/test")
async def test_discord(request: Request):
    """Fire a test message to the configured webhook."""
    bot = request.app.state.bot
    if not bot.notifier.enabled or not bot.notifier.webhook_url:
        return {"ok": False, "message": "Discord not configured or disabled"}

    sent = await bot.notifier.send("🤖 OmniTrader test notification — webhook is working!")
    return {"ok": sent, "message": "Test sent" if sent else "Send failed"}
