from .base import BaseDatabase
from .factory import DatabaseFactory
from .memgraph import MemgraphDatabase

Database = MemgraphDatabase

__all__ = [
    "BaseDatabase",
    "MemgraphDatabase",
    "DatabaseFactory",
    "Database",
]
