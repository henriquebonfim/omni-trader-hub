import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = None


def get_url():
    # Provide the database URL explicitly via config when programmatic execution is used
    # Otherwise fallback to SQLite defaults.
    url = config.get_main_option("sqlalchemy.url")
    if url and url != "driver://user:pass@localhost/dbname":
        return url

    # If not provided in configuration (e.g., CLI usage), look for an env var or fallback to SQLite

    # Try to make sure the data directory exists if we use sqlite default
    db_path = os.getenv("DATABASE_URL", "sqlite:////tmp/trades.db")
    if db_path.startswith("sqlite:///") and db_path != "sqlite:///:memory:":
        import pathlib

        path = db_path.replace("sqlite:///", "")
        if path.startswith("/"):
            # absolute
            pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
        else:
            # relative
            pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)

    return db_path


def run_migrations_offline() -> None:
    url = get_url()

    # We use psycopg2 or standard psycopg for sync migrations
    if url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql://")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url = get_url()
    if url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql://")

    configuration = config.get_section(config.config_ini_section)
    if configuration is None:
        configuration = {}
    configuration["sqlalchemy.url"] = url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
