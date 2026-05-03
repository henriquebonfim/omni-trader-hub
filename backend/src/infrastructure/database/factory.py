"""
Factory for creating database instances based on configuration.
"""

from src.config import Config
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
          username: ""
          password: ""
        """
        db_config = config.database

        return MemgraphDatabase(
            host=db_config.host,
            port=db_config.port,
            username=db_config.username,
            password=db_config.password,
            encrypted=db_config.encrypted,
        )
