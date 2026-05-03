import hmac
import os
import secrets

import structlog
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = structlog.get_logger()

# Security scheme for Bearer token
security = HTTPBearer(auto_error=False)

_API_KEY = None
_AUTH_DEV_MODE = False


def init_auth():
    """
    Initialize authentication key and mode.
    If OMNITRADER_API_KEY is not set, generate a random 32-character hex key.
    """
    global _API_KEY, _AUTH_DEV_MODE

    if _API_KEY is not None:
        return  # Already initialized

    env_key = os.getenv("OMNITRADER_API_KEY")
    if env_key:
        _API_KEY = env_key
        _AUTH_DEV_MODE = False
    else:
        _API_KEY = secrets.token_hex(32)
        _AUTH_DEV_MODE = True
        masked_key = f"{_API_KEY[:4]}...{_API_KEY[-4:]}"
        
        # Attempt to persist in .env if it's empty
        _persist_key_to_env(_API_KEY)

        print(
            f"\n{'=' * 50}\nAUTO-GENERATED API KEY: {masked_key}\n(Key has been persisted to your .env file)\nKEEP THIS SECURE!\n{'=' * 50}\n"
        )
        logger.info(
            "auth_dev_mode_enabled",
            message="Generated random API key for dev mode.",
            key_preview=masked_key,
        )


def _persist_key_to_env(key: str):
    """
    Attempt to write the generated API key to the .env file if it's empty.
    Requires .env to be bind-mounted at /app/.env.
    """
    env_path = "/app/.env"
    if not os.path.exists(env_path):
        return

    try:
        import re
        with open(env_path, "r") as f:
            content = f.read()

        # Matches 'OMNITRADER_API_KEY=' followed by optional spaces and then newline or EOF
        pattern = r"^(OMNITRADER_API_KEY=)\s*$"
        new_content = re.sub(pattern, f"OMNITRADER_API_KEY={key}", content, flags=re.MULTILINE)

        if new_content != content:
            with open(env_path, "w") as f:
                f.write(new_content)
    except Exception:
        # Silently fail if we can't write to .env (e.g. permission issues)
        pass


def get_api_key():
    if _API_KEY is None:
        init_auth()
    return _API_KEY


def is_dev_mode():
    if _API_KEY is None:
        init_auth()
    return _AUTH_DEV_MODE


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Security(security),  # noqa: B008
):
    """
    Verify the API key provided in the Authorization header.
    Expects 'Bearer <key>'.
    The key is retrieved from the OMNITRADER_API_KEY environment variable or auto-generated.
    """
    expected_key = get_api_key()

    # If no credentials provided or they don't match
    if not credentials or not hmac.compare_digest(
        credentials.credentials, expected_key
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return credentials.credentials
