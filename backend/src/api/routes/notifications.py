"""
Discord notification config routes.
"""

from fastapi import APIRouter, Request
from pydantic import BaseModel

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
    """Update Discord webhook URL and enable/disable notifications in-memory."""
    bot = request.app.state.bot
    bot.notifier.webhook_url = payload.webhook_url
    bot.notifier.enabled = payload.enabled
    return {"ok": True, "message": "Discord config updated"}


@router.post("/discord/test")
async def test_discord(request: Request):
    """Fire a test message to the configured webhook."""
    bot = request.app.state.bot
    if not bot.notifier.enabled or not bot.notifier.webhook_url:
        return {"ok": False, "message": "Discord not configured or disabled"}

    sent = await bot.notifier.send("🤖 OmniTrader test notification — webhook is working!")
    return {"ok": sent, "message": "Test sent" if sent else "Send failed"}
