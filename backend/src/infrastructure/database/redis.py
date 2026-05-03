import os
import redis

_redis_instance = None

def get_redis_client():
    """Get or create a Redis client instance."""
    global _redis_instance
    if _redis_instance is None:
        host = os.getenv("REDIS_HOST", "redis")
        port = int(os.getenv("REDIS_PORT", "6379"))
        db = int(os.getenv("REDIS_DB", "0"))
        password = os.getenv("REDIS_PASSWORD", None)
        
        _redis_instance = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True
        )
    return _redis_instance
