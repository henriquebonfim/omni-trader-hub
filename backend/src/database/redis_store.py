"""
Redis storage for persistent state management.

Handles key-value persistence for risk manager and other components
to ensure state survival across restarts.
"""

import json
import os
from typing import Any, Optional

import redis.asyncio as redis
import structlog

logger = structlog.get_logger()


class RedisStore:
    """
    Async Redis client wrapper for JSON storage.
    """

    def __init__(self, url: Optional[str] = None):
        self.url = url or os.getenv("REDIS_URL", "redis://omnitrader-redis:6379")
        self._client: Optional[redis.Redis] = None

    async def connect(self):
        """Establish connection to Redis."""
        if self._client:
            return

        try:
            self._client = redis.from_url(self.url, decode_responses=True)
            await self._client.ping()
            logger.info("redis_connected", url=self.url)
        except Exception as e:
            logger.error("redis_connection_failed", error=str(e), url=self.url)
            self._client = None
            raise

    async def close(self):
        """Close Redis connection."""
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.info("redis_disconnected")

    async def set(self, key: str, value: Any, expire: Optional[int] = None):
        """
        Save value to Redis as JSON.

        Args:
            key: Storage key
            value: Data to store (must be JSON serializable)
            expire: Expiration time in seconds (optional)
        """
        if not self._client:
            await self.connect()

        try:
            json_val = json.dumps(value)
            if expire:
                await self._client.setex(key, expire, json_val)
            else:
                await self._client.set(key, json_val)
        except Exception as e:
            logger.error("redis_set_failed", key=key, error=str(e))

    async def get(self, key: str) -> Optional[Any]:
        """
        Retrieve value from Redis and deserialize JSON.

        Args:
            key: Storage key

        Returns:
            Deserialized value or None if not found
        """
        if not self._client:
            await self.connect()

        try:
            val = await self._client.get(key)
            if val:
                return json.loads(val)
            return None
        except Exception as e:
            logger.error("redis_get_failed", key=key, error=str(e))
            return None

    async def delete(self, key: str):
        """Delete key from Redis."""
        if not self._client:
            await self.connect()

        try:
            await self._client.delete(key)
        except Exception as e:
            logger.error("redis_delete_failed", key=key, error=str(e))
