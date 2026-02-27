"""
Factory for creating database instances based on configuration.
"""

from .base import BaseDatabase
from .sqlite import SqliteDatabase
from .postgres import PostgresDatabase
from ..config import Config

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
