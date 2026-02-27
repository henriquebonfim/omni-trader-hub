# Database Infrastructure Migration

OmniTrader has migrated from a flat SQLite architecture to a scalable, multi-backend database architecture.

## Architecture

- **`BaseDatabase`**: Abstract base class defining the database interface.
- **`SqliteDatabase`**: Implementation for local development and minor testing.
- **`PostgresDatabase`**: Implementation for production, multi-pair, and dashboard scaling.
- **`DatabaseFactory`**: Utility to instantiate the correct backend based on configuration.

## Configuration

The database backend is configured in `config/config.yaml`:

```yaml
database:
  # To use SQLite:
  type: sqlite
  path: "data/trades.db"

  # To use PostgreSQL:
  # type: postgres
  # connection_string: "postgresql://user:password@host:port/dbname"
```

The system also supports environment variables for PostgreSQL:
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `POSTGRES_HOST`
- `POSTGRES_PORT`

## Docker Setup

The `compose.yml` file includes a PostgreSQL service (`postgres`) and Redis service (`redis`).

To start the full stack including databases:
```bash
docker compose up -d
```

## Development

- `BaseDatabase` (Abstract): Interface definition.
- `SqliteDatabase`: Existing SQLite implementation using `aiosqlite`.
- `PostgresDatabase`: New PostgreSQL implementation using `asyncpg`.
- `DatabaseFactory`: Handles instantiation based on config.
