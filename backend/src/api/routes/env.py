import os
import tempfile
from pathlib import Path
from typing import Dict

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from src.api.auth import verify_api_key

logger = structlog.get_logger()

router = APIRouter(prefix="/env", tags=["system", "env"])

# We locate the application root where .env usually is.
# In container runtime this file is /app/src/api/routes/env.py => parents[3] = /app.
# In local backend layout this resolves to the backend directory.
ROOT_DIR = Path(__file__).resolve().parents[3]
ENV_FILE = ROOT_DIR / ".env"

# Whitelisted keys that can be viewed/modified
# Grouped into logical sections
ENV_WHITELIST = {
    "exchange": [
        "BINANCE_API_KEY",
        "BINANCE_SECRET",
    ],
    "database": [
        "MEMGRAPH_HOST",
        "MEMGRAPH_PORT",
        "MEMGRAPH_USERNAME",
        "MEMGRAPH_PASSWORD",
        "REDIS_HOST",
        "REDIS_PORT",
    ],
    "notifications": [
        "DISCORD_WEBHOOK_URL",
    ],
    "security": [
        "OMNITRADER_API_KEY",
    ],
}

SENSITIVE_KEYS = {
    "BINANCE_SECRET",
    "MEMGRAPH_PASSWORD",
    "OMNITRADER_API_KEY",
}

ENV_METADATA = {
    "BINANCE_API_KEY": ("Binance API Key", True),
    "BINANCE_SECRET": ("Binance API Secret", True),
    "MEMGRAPH_HOST": ("Memgraph Host", True),
    "MEMGRAPH_PORT": ("Memgraph Port", True),
    "MEMGRAPH_USERNAME": ("Memgraph Username", True),
    "MEMGRAPH_PASSWORD": ("Memgraph Password", True),
    "REDIS_HOST": ("Redis Host", True),
    "REDIS_PORT": ("Redis Port", True),
    "DISCORD_WEBHOOK_URL": ("Discord Webhook URL", False),
    "OMNITRADER_API_KEY": ("OmniTrader API Key", False),
}


class EnvVarMetadata(BaseModel):
    value: str
    masked: bool
    description: str
    requires_restart: bool


def mask_value(key: str, value: str) -> str:
    """Mask sensitive values."""
    if not value:
        return ""
    if key in SENSITIVE_KEYS:
        if len(value) <= 4:
            return "*" * len(value)
        return f"{value[:2]}...{value[-2:]}"
    return value


def read_env_file() -> Dict[str, str]:
    """Read the .env file and return a dictionary of parsed values."""
    env_vars = {}
    if ENV_FILE.exists():
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip()
                    if (v.startswith('"') and v.endswith('"')) or (
                        v.startswith("'") and v.endswith("'")
                    ):
                        v = v[1:-1]
                    env_vars[k] = v
    return env_vars


def write_env_file(updates: Dict[str, str]):
    """
    Atomically write updates to .env file.
    Preserves comments and existing formatting where possible.
    """
    lines = []
    updated_keys = set()

    if ENV_FILE.exists():
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    lines.append(line)
                    continue

                if "=" in stripped:
                    k, v = stripped.split("=", 1)
                    k = k.strip()
                    if k in updates:
                        lines.append(f"{k}={updates[k]}\n")
                        updated_keys.add(k)
                    else:
                        lines.append(line)
                else:
                    lines.append(line)

    # Add any new keys that weren't in the file
    for k, v in updates.items():
        if k not in updated_keys:
            lines.append(f"{k}={v}\n")

    # Atomic write
    fd, temp_path = tempfile.mkstemp(dir=ENV_FILE.parent, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.writelines(lines)
        os.replace(temp_path, ENV_FILE)
    except Exception as e:
        os.remove(temp_path)
        raise e


class EnvUpdate(BaseModel):
    updates: Dict[str, str]


@router.get("")
async def get_env() -> Dict[str, Dict[str, EnvVarMetadata]]:
    """
    Get grouped and masked environment variables.
    Only whitelisted variables are exposed.
    """
    raw_env = read_env_file()

    response_data: Dict[str, Dict[str, EnvVarMetadata]] = {}
    for group, keys in ENV_WHITELIST.items():
        group_data = {}
        for key in keys:
            val = raw_env.get(key, "")
            masked_val = mask_value(key, val)
            desc, restart = ENV_METADATA.get(key, ("No description available.", True))
            group_data[key] = EnvVarMetadata(
                value=masked_val,
                masked=key in SENSITIVE_KEYS,
                description=desc,
                requires_restart=restart,
            )
        response_data[group] = group_data

    return response_data


@router.put("", dependencies=[Depends(verify_api_key)])
async def update_env(payload: EnvUpdate, request: Request):
    """
    Atomic updater for environment variables.
    Validates against whitelist and emits an audit signal.
    """
    updates = payload.updates

    # Flatten whitelist for quick lookup
    allowed_keys = {key for keys in ENV_WHITELIST.values() for key in keys}

    validated_updates = {}
    for k, v in updates.items():
        if k not in allowed_keys:
            raise HTTPException(
                status_code=400, detail=f"Key {k} is not allowed to be modified."
            )

        # Basic validation: Binance API keys shouldn't be empty if provided as part of updates,
        # unless they are explicitly being cleared. We'll just ensure they're strings.
        if not isinstance(v, str):
            raise HTTPException(
                status_code=400, detail=f"Value for {k} must be a string."
            )

        # Strip newlines to prevent injection
        validated_updates[k] = v.replace("\n", "").replace("\r", "")

    # Emit audit signal before writing
    logger.info(
        "env_update_audit",
        keys=list(validated_updates.keys()),
        ip=request.client.host if request.client else "unknown",
    )

    try:
        write_env_file(validated_updates)
    except PermissionError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Permission denied while writing {ENV_FILE}",
        ) from e

    return {"ok": True, "message": "Environment variables updated successfully"}
