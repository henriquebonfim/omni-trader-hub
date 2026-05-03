# OmniTrader

Self-hosted BTC/USDT Futures trading system with pluggable strategies, regime detection, risk management, and a real-time React dashboard. Built on Python asyncio, FastAPI, Celery, Redis, PostgreSQL, and Docker Compose.

> **⚠️ DISCLAIMER: Use at your own risk.** Trading cryptocurrencies involves significant risk of loss. This software is provided "as is" for educational and research purposes. Never trade with capital you cannot afford to lose.

## Features

- **5 Pluggable Strategies** — ADX Trend (active), EMA+Volume, Bollinger Bands+RSI, Donchian Breakout, Z-Score Mean Reversion
- **Regime Detection** — ADX/ATR-based classifier gates strategies by market regime (Trending / Ranging / Volatile)
- **Smart Money Concepts** — BOS/CHoCH structure analysis layer (implemented, not yet wired to signals)
- **Risk Management** — Position sizing, SL/TP (fixed + ATR config), trailing stops, daily/weekly circuit breakers, black swan detection, liquidation monitoring, auto-deleverage, consecutive-loss reduction
- **Paper Trading Mode** — $10k simulated balance with live market data *(known bugs in PnL formula and SL/TP simulation — see TASKS.md T7, T8)*
- **Manual Trading & Charting** — Buy/Sell/Close from dashboard, real-time candlestick charts (1s–1M timeframes)
- **WebSocket Live Feed** — Real-time ticker, multi-TF OHLCV, and order fill streaming via CCXT Pro
- **Celery Worker Offloading** — Strategy and regime analysis dispatched to separate worker process
- **PostgreSQL + SQLite** — Dual database support via factory pattern (Postgres ready, SQLite default)
- **Redis State Persistence** — Risk state (daily PnL, loss streaks, circuit breakers) survives restarts
- **External Watchdog** — Separate process monitors `/api/health`, alerts via Discord on failure
- **Discord Alerts** — Positions opened/closed, circuit breakers, errors, daily summaries
- **React Dashboard** — Vite + React + TradingView Lightweight Charts + Recharts
- **Docker Compose** — Full stack: backend, frontend, Celery worker, PostgreSQL, Redis, Ollama (optional), watchdog

## Quick Start

### Docker Compose (Recommended)

```bash
# Initial setup: create .env and build images
make setup

# Edit .env file to configure (POSTGRES_PASSWORD is required)
nano .env

# Start all services in background
make start

# View logs
make logs

# Stop all services
make stop
```

- **Dashboard**: http://localhost:3333
- **API**: http://localhost:8000/api/health
- **API Docs**: http://localhost:8000/docs

### Manual Setup

```bash
cd backend
uv venv && source .venv/bin/activate
uv pip install .
python -m src.main
```

### Make Targets

```bash
make setup      # Initial setup (create .env, build images)
make start      # Start application in background
make stop       # Stop all containers
make test       # Run pytest + frontend tests via Docker
make logs       # View container logs
make build      # Rebuild Docker images
make dev        # Start in foreground with live logs
make lint       # Run linters (ruff)
make typecheck  # Run type checking (mypy)
```

## Discord Alerts

- 🟢 Long positions opened
- 🔴 Short positions opened
- ✅ Profitable trades closed
- ❌ Losing trades closed
- ⚠️ Circuit breaker triggered
- 🚨 Errors and watchdog alerts
- 📊 Daily P&L summaries


## Documentation

| Document | Purpose |
|----------|---------|
| [ROADMAP.md](ROADMAP.md) | Strategy assessments, risk framework, architecture, phase planning |
| [TASKS.md](TASKS.md) | All technical debt + audit findings (single source of truth) |
| [TODO.md](TODO.md) | Current sprint — ready to implement |
| [BACKLOG.md](BACKLOG.md) | Items needing design decisions before implementation |

## License

MIT License. See [LICENSE](LICENSE) for details.
