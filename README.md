# OmniTrader

Self-hosted BTC/USDT Futures trading system with pluggable strategies, regime detection, risk management, and a real-time React dashboard. Built on Python asyncio, FastAPI, Celery, Redis, PostgreSQL, and Docker Compose.

> **⚠️ DO NOT DEPLOY LIVE CAPITAL.** An institutional-grade audit (2026-03-03) identified critical bugs in stop-loss handling, paper mode simulation, and API security. See [TASKS.md](TASKS.md) for the full findings. Additionally, the current geopolitical environment (US-Israeli/Iran conflict, Hormuz closure) creates extreme macro volatility that this system has no mechanism to detect or respond to.

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
cp .env.example .env          # Configure API keys, Discord webhook
docker compose up -d --build   # Start full stack
```

- **Dashboard**: http://localhost:3000
- **API**: http://localhost:8000/api/health
- **API Docs**: http://localhost:8000/docs

### Manual Setup

```bash
cd backend
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
python -m src.main
```

### Make Targets

```bash
make test       # Run pytest + frontend tests via Docker
make lint       # Ruff + frontend lint
make build      # Build all Docker images
make dev        # Start in development mode
```

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Frontend   │────▶│   FastAPI    │────▶│  Binance Futures │
│  Vite/React  │◀────│  + Trading   │◀────│  REST + WebSocket│
│  :3000       │ WS  │  Loop :8000  │     └─────────────────┘
└─────────────┘     └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Celery   │ │ Postgres │ │  Redis   │
        │ Worker   │ │ (trades) │ │ (state + │
        │ (analysis)│ │          │ │  broker) │
        └──────────┘ └──────────┘ └──────────┘
              ▲
        ┌──────────┐     ┌──────────┐
        │ Watchdog │     │  Ollama  │
        │ (health) │     │ (optional│
        └──────────┘     │  LLM)   │
                         └──────────┘
```

## Trading Strategies

| Strategy | Signal Type | Market Condition | Config Key |
|----------|-----------|-----------------|------------|
| **ADX Trend** *(active)* | Level: ADX>25 + DI direction | Trending | `adx_trend` |
| **EMA + Volume** | Transition: EMA(10/21) cross + volume>1.5× | Trending | `ema_volume` |
| **Bollinger Bands + RSI** | Level: price outside BB(20,2σ) + RSI extreme | Ranging | `bollinger_bands` |
| **Donchian Breakout** | Level: price above/below 20-period channel | Post-consolidation | `breakout` |
| **Z-Score** | Level: z-score beyond ±2.0 threshold | Ranging | `z_score` |

Strategy selection in `config/config.yaml`:
```yaml
strategy:
  name: adx_trend    # Change to any registered strategy
```

## Risk Management

| Parameter | Value | Notes |
|-----------|-------|-------|
| Position Size | 2% of wallet | Per-trade risk |
| Stop Loss | 2% fixed | ATR-based configured but not yet wired (T9) |
| Take Profit | 4% (2:1 R:R) | ATR-based configured but not yet wired (T9) |
| Trailing Stop | 1% activation, 0.5% callback | Exchange-side STOP_MARKET |
| Daily Loss Limit | 5% | Circuit breaker — auto-resume next UTC day |
| Weekly Loss Limit | 10% | 48h pause, manual restart |
| Consecutive Losses | 3 → 50% size reduction | Resets on 2 consecutive wins |
| Black Swan | >10% BTC move in 1h | Flatten all, manual restart |
| Liquidation Monitor | Alert at 50% distance | Configurable buffer |
| Auto-Deleverage | >10% daily drawdown → 1× leverage | Uses daily PnL (T16: should use HWM) |
| Leverage | 3× isolated | Conservative for retail |

## Project Structure

```
OmniTrader/
├── backend/
│   ├── src/
│   │   ├── main.py             # Entry point, trading loop, orchestrator
│   │   ├── config.py           # YAML config loader with env var substitution
│   │   ├── exchange.py         # CCXT Binance Futures wrapper, paper mode
│   │   ├── risk.py             # Position sizing, SL/TP, circuit breakers
│   │   ├── notifier.py         # Discord webhook notifications
│   │   ├── watchdog.py         # External health monitor
│   │   ├── ws_feed.py          # WebSocket live data feed
│   │   ├── rate_limiter.py     # Leaky-bucket rate limiter
│   │   ├── strategies/
│   │   │   ├── base.py         # BaseStrategy ABC + analyze() pipeline
│   │   │   ├── registry.py     # Decorator-based strategy registration
│   │   │   ├── adx_trend.py    # ADX + DI directional strategy
│   │   │   ├── ema_volume.py   # EMA crossover + volume confirmation
│   │   │   ├── bollinger_bands.py  # BB + RSI mean reversion
│   │   │   ├── breakout.py     # Donchian channel breakout
│   │   │   ├── z_score.py      # Statistical mean reversion
│   │   │   └── smc/            # Smart Money Concepts (analysis layer)
│   │   ├── analysis/
│   │   │   └── regime.py       # ADX/ATR regime classifier
│   │   ├── database/
│   │   │   ├── factory.py      # Database factory (SQLite/Postgres/Redis)
│   │   │   ├── sqlite.py       # SQLite implementation + WAL mode
│   │   │   ├── postgres.py     # PostgreSQL implementation (asyncpg)
│   │   │   └── redis_store.py  # Redis state persistence
│   │   ├── api/
│   │   │   ├── auth.py         # API key authentication
│   │   │   ├── schemas.py      # Pydantic request/response schemas
│   │   │   ├── websocket.py    # WS connection manager
│   │   │   └── routes/         # FastAPI route handlers
│   │   └── workers/
│   │       ├── tasks.py        # Celery task definitions
│   │       ├── dispatch.py     # Async-safe Celery dispatch bridge
│   │       └── serializers.py  # DataFrame ↔ JSON serialization
│   ├── tests/                  # 20 test files, pytest + pytest-asyncio
│   ├── config/config.yaml      # Trading configuration
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.tsx             # Main dashboard layout
│   │   ├── components/         # BotControl, CandleChart, RiskDashboard, etc.
│   │   └── lib/                # API client, WebSocket client
│   └── Dockerfile
├── compose.yml                 # Full stack: 7 services
├── TASKS.md                    # Technical debt + audit findings (source of truth)
├── TODO.md                     # Current sprint items
├── BACKLOG.md                  # Items needing design
└── ROADMAP.md                  # Strategy assessment, risk framework, architecture
```

## Configuration

Full configuration in `backend/config/config.yaml`:

```yaml
exchange:
  name: binance
  paper_mode: true           # Set false for live trading
  leverage: 3
  margin_type: isolated

trading:
  symbol: BTC/USDT:USDT
  timeframe: 15m
  cycle_seconds: 30
  position_size_pct: 2.0

strategy:
  name: adx_trend            # adx_trend | ema_volume | bollinger_bands | breakout | z_score
  adx_period: 14
  adx_threshold: 25
  ema_fast: 10
  ema_slow: 21
  volume_threshold: 1.5

risk:
  stop_loss_pct: 2.0
  take_profit_pct: 4.0
  use_atr_stops: true        # Configured but not yet wired — see TASKS.md T9
  atr_multiplier_sl: 1.5
  atr_multiplier_tp: 2.0
  max_daily_loss_pct: 5.0
  trailing_stop_activation_pct: 1.0
  trailing_stop_callback_pct: 0.5

notifications:
  enabled: true
  discord_webhook: ${DISCORD_WEBHOOK_URL}
```

## Discord Alerts

- 🟢 Long positions opened
- 🔴 Short positions opened
- ✅ Profitable trades closed
- ❌ Losing trades closed
- ⚠️ Circuit breaker triggered
- 🚨 Errors and watchdog alerts
- 📊 Daily P&L summaries

## Known Issues

See [TASKS.md](TASKS.md) for the complete list. Critical items:

| ID | Issue | Severity |
|----|-------|----------|
| T6 | SL/TP placement failure leaves naked positions | 🔴 Critical |
| T7 | Paper mode PnL formula incorrect | 🔴 Critical |
| T8 | Paper SL/TP orders never simulated | 🔴 Critical |
| T9 | ATR stops configured but not applied | 🔴 Critical |
| T11 | API mutation endpoints unprotected | 🔴 Critical |

## Documentation

| Document | Purpose |
|----------|---------|
| [ROADMAP.md](ROADMAP.md) | Strategy assessments, risk framework, architecture, phase planning |
| [TASKS.md](TASKS.md) | All technical debt + audit findings (single source of truth) |
| [TODO.md](TODO.md) | Current sprint — ready to implement |
| [BACKLOG.md](BACKLOG.md) | Items needing design decisions before implementation |

## License

Personal project — not for commercial use.
