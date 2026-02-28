"""
Factory for creating database instances based on configuration.
"""

from ..config import Config
from .base import BaseDatabase
from .postgres import PostgresDatabase
from .redis_store import RedisStore
from .sqlite import SqliteDatabase


class DatabaseFactory:
    """
    Factory to instantiate the correct database backend.
    """

    @staticmethod
    def get_database(config: Config) -> BaseDatabase:
        """
        Get database instance based on config.

        Config structure expected:
        database:
          type: "sqlite" | "postgres"
          path: "path/to/db.sqlite" (for sqlite)
          connection_string: "postgresql://..." (for postgres)
        """
        # Default to sqlite if not configured
        db_type = getattr(config, "database", None)
        if db_type:
            db_type_name = getattr(db_type, "type", "sqlite")
        else:
            db_type_name = "sqlite"

        if db_type_name == "postgres":
            connection_string = getattr(db_type, "connection_string", None)
            return PostgresDatabase(connection_string)
        else:
            # SQLite default
            path = getattr(db_type, "path", None) if db_type else None
            return SqliteDatabase(path)

    @staticmethod
    def get_redis_store(config: Config) -> RedisStore:
        """Get Redis store instance based on config."""
        # Check for redis config, fallback to env/default
        db_config = getattr(config, "database", None)
        redis_url = getattr(db_config, "redis_url", None) if db_config else None
        return RedisStore(url=redis_url)
