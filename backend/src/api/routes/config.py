"""
Config read/write routes.
"""

from pathlib import Path

import yaml
from fastapi import APIRouter, HTTPException, Request

router = APIRouter(tags=["config"])

_CONFIG_PATH = Path(__file__).parent.parent.parent.parent / "config" / "config.yaml"


@router.get("/config")
async def get_config(request: Request):
    """Return current configuration as JSON (sensitive values redacted)."""
    bot = request.app.state.bot
    cfg = bot.config.to_dict()

    # Redact secrets
    if "exchange" in cfg:
        cfg["exchange"].pop("api_key", None)
        cfg["exchange"].pop("api_secret", None)

    return cfg


@router.put("/config")
async def update_config(updates: dict, request: Request):
    """
    Deep-merge `updates` into config.yaml and reload.

    Only top-level section keys are merged (e.g. {"trading": {"symbol": "ETH/USDT:USDT"}}).
    Missing sections are preserved unchanged.
    """
    bot = request.app.state.bot

    # Load raw YAML to preserve comments / env-var placeholders
    if not _CONFIG_PATH.exists():
        raise HTTPException(status_code=500, detail="config.yaml not found on server")

    with open(_CONFIG_PATH) as f:
        current = yaml.safe_load(f) or {}

    # Deep-merge: only update keys provided
    def _merge(base: dict, patch: dict) -> dict:
        for k, v in patch.items():
            if isinstance(v, dict) and isinstance(base.get(k), dict):
                _merge(base[k], v)
            else:
                base[k] = v
        return base

    merged = _merge(current, updates)

    with open(_CONFIG_PATH, "w") as f:
        yaml.dump(merged, f, default_flow_style=False, allow_unicode=True)

    # Reload bot configuration
    await bot.reload_config()

    return {"ok": True, "message": "Config updated and reloaded"}
