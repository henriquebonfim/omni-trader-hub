from .base import BaseDatabase
from .factory import DatabaseFactory
from .postgres import PostgresDatabase
from .sqlite import SqliteDatabase

# Backward compatibility alias - will default to Sqlite if instantiated directly
# However, the old usage was `Database(path)`.
# We should probably make `Database` an alias for `SqliteDatabase` for minimal friction,
# OR make it a factory method disguised as a class?
# The plan says "Delete the original backend/src/database.py file".
# So `from src.database import Database` will now look here.
# If we want to support existing tests that do `Database(":memory:")`, we should alias SqliteDatabase to Database.

Database = SqliteDatabase

__all__ = [
    "BaseDatabase",
    "SqliteDatabase",
    "PostgresDatabase",
    "DatabaseFactory",
    "Database",
]
