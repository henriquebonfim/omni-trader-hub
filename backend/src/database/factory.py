"""
Factory for creating database instances based on configuration.
"""

from ..config import Config
from .base import BaseDatabase
from .memgraph import MemgraphDatabase


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
          type: "memgraph"
          host: "memgraph"
          port: 7687
          encrypted: false
          username: null
          password: null
        """
        db_config = getattr(config, "database", None)
        return MemgraphDatabase(
            host=getattr(db_config, "host", "memgraph") if db_config else "memgraph",
            port=int(getattr(db_config, "port", 7687)) if db_config else 7687,
            username=getattr(db_config, "username", None) if db_config else None,
            password=getattr(db_config, "password", None) if db_config else None,
            encrypted=(
                bool(getattr(db_config, "encrypted", False)) if db_config else False
            ),
        )
