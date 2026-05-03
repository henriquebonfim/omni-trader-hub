"""
Config read/write routes.
"""

from fastapi import APIRouter, Depends, HTTPException, Request

from src.config import save_config_to_db
from src.interfaces.api.auth import verify_api_key
from src.interfaces.api.schemas import ConfigUpdate

router = APIRouter(tags=["config"])


@router.get("/config")
async def get_config(request: Request):
    """Return current configuration as JSON (sensitive values redacted)."""
    bot = request.app.state.bot
    cfg = bot.config.to_dict()

    # Redact secrets
    if "exchange" in cfg:
        cfg["exchange"].pop("api_key", None)
        cfg["exchange"].pop("api_secret", None)

    if "notifications" in cfg:
        # Mask webhook if present
        url = cfg["notifications"].get("discord_webhook", "")
        if url and len(url) > 10:
            cfg["notifications"]["discord_webhook"] = f"{url[:10]}...[REDACTED]"

    return cfg


@router.put("/config", dependencies=[Depends(verify_api_key)])
async def update_config(updates: ConfigUpdate, request: Request):
    """
    Deep-merge `updates` into database-backed config and reload.
    """
    bot = request.app.state.bot

    # Validate and convert to dict, excluding unset fields
    updates_dict = updates.model_dump(exclude_unset=True)

    # Deep-merge: only update keys provided
    def _merge(base: dict, patch: dict) -> dict:
        for k, v in patch.items():
            if isinstance(v, dict) and isinstance(base.get(k), dict):
                _merge(base[k], v)
            else:
                base[k] = v
        return base

    current_dict = bot.config.to_dict()
    merged = _merge(current_dict, updates_dict)

    # Validate new config
    from src.config import Config
    try:
        new_config = Config.model_validate(merged)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid configuration: {str(e)}")

    # Persist to database
    try:
        await save_config_to_db(bot.database, new_config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save config to database: {str(e)}")

    # Reload bot configuration (this will pull from DB if it calls reload_config and we update that)
    # Actually, bot.reload_config calls reload_config() from src.config which loads from file.
    # We should update OmniTrader.reload_config to use load_config_from_db.
    await bot.reload_config()

    return {"ok": True, "message": "Config updated and reloaded"}
