import hmac
import os

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Security scheme for Bearer token
security = HTTPBearer(auto_error=False)

async def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Security(security), # noqa: B008
):
    """
    Verify the API key provided in the Authorization header.
    Expects 'Bearer <key>'.
    The key is retrieved from the OMNITRADER_API_KEY environment variable.
    If OMNITRADER_API_KEY is not set, authentication is bypassed (not recommended for production).
    """
    expected_key = os.getenv("OMNITRADER_API_KEY")

    # If no key is configured in the environment, we allow access
    if not expected_key:
        return None

    # If a key is configured but no credentials provided or they don't match
    if not credentials or not hmac.compare_digest(credentials.credentials, expected_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return credentials.credentials
