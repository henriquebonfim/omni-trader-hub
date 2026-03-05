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
        print(f"\n{'='*50}\nAUTO-GENERATED API KEY: {_API_KEY}\nKEEP THIS SECURE!\n{'='*50}\n")
        logger.info("auth_dev_mode_enabled", message="Generated random API key for dev mode.")


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
