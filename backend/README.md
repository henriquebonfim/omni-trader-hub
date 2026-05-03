# OmniTrader Backend

Core trading engine, risk management, and API for OmniTrader.

## Tech Stack

- **FastAPI**: High-performance async API framework.
- **CCXT**: Connectivity to 100+ crypto exchanges (Binance Futures primarily supported).
- **TA-Lib**: Technical analysis indicators.
- **Memgraph**: Graph database for market intelligence and regime detection.
- **Redis**: Real-time state persistence and message queuing.
- **Celery**: Distributed task queue for strategy analysis.
- **PostgreSQL**: Long-term trade and signal persistence.

## Project Structure

- `src/api/`: FastAPI routes, middleware, and authentication.
- `src/exchanges/`: Exchange adapters and paper trading simulation.
- `src/intelligence/`: News ingestion, NLP sentiment analysis, and graph analytics.
- `src/risk/`: Multi-layer risk management (Circuit breakers, sizing, validation).
- `src/strategy/`: Pluggable trading strategies and regime detectors.
- `src/trading/`: Core domain logic for cycle orchestration and position management.
- `src/workers/`: Celery tasks for background processing.

## Getting Started

### Prerequisites

- Python 3.12+
- TA-Lib C Library installed.

### Setup

```bash
# Install dependencies
pip install .[dev]

# Set up environment
cp ../.env.example .env
# Edit .env with your credentials
```

### Running Locally

```bash
# Start API server
python -m src.main

# Start Celery worker (requires Redis)
celery -A src.workers worker --loglevel=info
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src
```

## Documentation

API documentation is available at `/docs` (Swagger) or `/redoc` when the server is running.
Technical analysis function references can be found in `talib-docs/`.
