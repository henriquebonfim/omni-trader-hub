"""
Config read/write routes.
"""

from pathlib import Path

import yaml
from fastapi import APIRouter, Depends, HTTPException, Request

from src.api.auth import verify_api_key
from src.api.schemas import ConfigUpdate

router = APIRouter(tags=["config"])

# Resolves to project root/config/config.yaml
# __file__ = backend/src/api/routes/config.py
# parents[0] = backend/src/api/routes
# parents[1] = backend/src/api
# parents[2] = backend/src
# parents[3] = backend
_CONFIG_PATH = Path(__file__).parents[3] / "config" / "config.yaml"


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
    Deep-merge `updates` into config.yaml and reload.

    Note: This operation rewrites the YAML file, so comments and formatting
    may be lost.
    """
    bot = request.app.state.bot

    if not _CONFIG_PATH.exists():
        raise HTTPException(status_code=500, detail="config.yaml not found on server")

    # Validate and convert to dict, excluding unset fields
    updates_dict = updates.model_dump(exclude_unset=True)

    try:
        with open(_CONFIG_PATH) as f:
            current = yaml.safe_load(f) or {}
    except PermissionError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Permission denied while reading {_CONFIG_PATH}",
        ) from e

    # Deep-merge: only update keys provided
    def _merge(base: dict, patch: dict) -> dict:
        for k, v in patch.items():
            if isinstance(v, dict) and isinstance(base.get(k), dict):
                _merge(base[k], v)
            else:
                base[k] = v
        return base

    merged = _merge(current, updates_dict)

    try:
        with open(_CONFIG_PATH, "w") as f:
            yaml.dump(merged, f, default_flow_style=False, allow_unicode=True)
    except PermissionError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Permission denied while writing {_CONFIG_PATH}",
        ) from e

    # Reload bot configuration
    await bot.reload_config()

    return {"ok": True, "message": "Config updated and reloaded"}
