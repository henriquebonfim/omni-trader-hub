"""
Discord notification config routes.
"""


from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from src.config import save_config_to_db
from src.interfaces.api.auth import verify_api_key

router = APIRouter(prefix="/notifications", tags=["notifications"])


class DiscordWebhookPayload(BaseModel):
    webhook_url: str | None = None
    enabled: bool = True


class AlertRules(BaseModel):
    circuit_breaker: bool = True
    strategy_rotation: bool = True
    regime_change: bool = True
    pnl_thresholds: bool = True
    pnl_warning_pct: float = 3.0
    pnl_critical_pct: float = 5.0


def _merge_alert_rules(raw: dict | None) -> dict:
    defaults = AlertRules().model_dump()
    if not isinstance(raw, dict):
        return defaults
    merged = {**defaults, **raw}
    # Keep threshold relation sane even if data is manually edited in DB.
    if merged["pnl_critical_pct"] < merged["pnl_warning_pct"]:
        merged["pnl_critical_pct"] = merged["pnl_warning_pct"]
    return merged


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


@router.put("/discord", dependencies=[Depends(verify_api_key)])
async def update_discord_config(payload: DiscordWebhookPayload, request: Request):
    """Update Discord webhook URL and persist to database."""
    bot = request.app.state.bot

    current_config = bot.config
    if payload.webhook_url is not None:
        current_config.notifications.discord_webhook_url = payload.webhook_url
    current_config.notifications.enabled = payload.enabled

    try:
        await save_config_to_db(bot.database, current_config)
        await bot.reload_config()
    except Exception as e:
        import structlog
        logger = structlog.get_logger()
        logger.error("discord_config_persist_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to persist config: {str(e)}")

    return {"ok": True, "message": "Discord config updated and saved"}


@router.post("/discord/test", dependencies=[Depends(verify_api_key)])
async def test_discord(request: Request):
    """Fire a test message to the configured webhook."""
    bot = request.app.state.bot
    if not bot.notifier.enabled or not bot.notifier.webhook_url:
        return {"ok": False, "message": "Discord not configured or disabled"}

    sent = await bot.notifier.send(
        "🤖 OmniTrader test notification — webhook is working!"
    )
    return {"ok": sent, "message": "Test sent" if sent else "Send failed"}


@router.get("/rules")
async def get_notification_rules(request: Request):
    """Return notification alert rules used by live WebSocket alerts."""
    bot = request.app.state.bot
    notifications = getattr(bot.config, "notifications", None)
    alert_rules = getattr(notifications, "alert_rules", None)
    if hasattr(alert_rules, "to_dict"):
        alert_rules = alert_rules.to_dict()
    return _merge_alert_rules(alert_rules)


@router.put("/rules", dependencies=[Depends(verify_api_key)])
async def update_notification_rules(payload: AlertRules, request: Request):
    """Persist notification alert rules into database and reload runtime config."""
    bot = request.app.state.bot
    
    current_config = bot.config
    current_config.notifications.alert_rules = payload.model_dump()

    try:
        await save_config_to_db(bot.database, current_config)
        await bot.reload_config()
    except Exception as e:
        import structlog
        logger = structlog.get_logger()
        logger.error("notification_rules_persist_failed", error=str(e))
        raise HTTPException(
            status_code=500, detail=f"Failed to persist notification rules: {str(e)}"
        )

    return {"ok": True, "rules": payload.model_dump()}
