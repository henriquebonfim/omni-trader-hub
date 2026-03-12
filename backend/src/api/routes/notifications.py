"""
Discord notification config routes.
"""

from typing import Optional

import yaml
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from src.api.auth import verify_api_key

from .config import _CONFIG_PATH

router = APIRouter(prefix="/notifications", tags=["notifications"])


class DiscordWebhookPayload(BaseModel):
    webhook_url: Optional[str] = None
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
    # Keep threshold relation sane even if file is manually edited.
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
    """Update Discord webhook URL and persist to config.yaml."""
    bot = request.app.state.bot

    # Persist to file
    try:
        with open(_CONFIG_PATH) as f:
            current = yaml.safe_load(f) or {}

        if "notifications" not in current:
            current["notifications"] = {}

        if payload.webhook_url is not None:
            current["notifications"]["discord_webhook"] = payload.webhook_url
        current["notifications"]["enabled"] = payload.enabled

        with open(_CONFIG_PATH, "w") as f:
            yaml.dump(current, f, default_flow_style=False, allow_unicode=True)

        await bot.reload_config()

    except PermissionError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Permission denied while writing {_CONFIG_PATH}",
        ) from e
    except Exception as e:
        import structlog

        logger = structlog.get_logger()
        logger.error("discord_config_persist_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to persist config") from e

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
    """Persist notification alert rules into config.yaml and reload runtime config."""
    bot = request.app.state.bot
    try:
        with open(_CONFIG_PATH) as f:
            current = yaml.safe_load(f) or {}

        notifications = current.setdefault("notifications", {})
        notifications["alert_rules"] = payload.model_dump()

        with open(_CONFIG_PATH, "w") as f:
            yaml.dump(current, f, default_flow_style=False, allow_unicode=True)

        await bot.reload_config()
    except PermissionError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Permission denied while writing {_CONFIG_PATH}",
        ) from e
    except Exception as e:
        import structlog

        logger = structlog.get_logger()
        logger.error("notification_rules_persist_failed", error=str(e))
        raise HTTPException(
            status_code=500, detail="Failed to persist notification rules"
        ) from e

    return {"ok": True, "rules": payload.model_dump()}
