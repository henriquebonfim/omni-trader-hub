# OmniTrader Implementation Plan

Dual-track roadmap: **Backend** (trading engine) + **Frontend** (dashboard).
Each priority level evolves both tracks in parallel.
Maps to the 13-module System Architecture spec.

**Stack**: FastAPI (backend) · Vite + React + TypeScript (frontend) · SQLite WAL → Postgres · Docker Compose

---

## 🔴 P0: Foundation (MUST HAVE)

### Phase A — Trading Core ✅

*Modules: Scanner (basic), Signal (basic), Decision (basic), Execution (basic), Exit (basic)*

| # | Task | Track | Status | Description |
|---|------|-------|--------|-------------|
| 1 | Project structure | BE | ✅ | src/, config/, data/, tests/ |
| 2 | Config system | BE | ✅ | YAML config + env var substitution |
| 3 | Exchange wrapper | BE | ✅ | CCXT Binance Futures (connect, fetch OHLCV, orders) |
| 4 | Base strategy | BE | ✅ | EMA(9/21) + Volume confirmation |
| 5 | Risk manager | BE | ✅ | Position sizing (2%), SL (2%), TP (4%) |
| 6 | Main loop | BE | ✅ | Async trading cycle (60s) |
| 7 | Paper trading | BE | ✅ | $10k simulated balance, no API keys needed |
| 8 | Trade logging | BE | ✅ | SQLite database for all trades |

### Phase B — Backend API

*New `backend/src/api/` module — FastAPI runs alongside the async trading loop via `asyncio.gather()`*

| # | Task | Track | Status | Description |
|---|------|-------|--------|-------------|
| 9 | FastAPI app factory | BE | ✅ | `create_api(bot)` receives OmniTrader instance, mounts routes |
| 10 | REST: status & balance | BE | ✅ | `GET /api/status`, `/api/balance`, `/api/position` |
| 11 | REST: trades & history | BE | ✅ | `GET /api/trades`, `/api/daily-summary/{date}`, `/api/equity` |
| 12 | REST: strategies | BE | ✅ | `GET /api/strategies` — list registered + metadata |
| 13 | REST: config CRUD | BE | ✅ | `GET/PUT /api/config` — read/write config.yaml from UI |
| 14 | REST: bot control | BE | ✅ | `POST /api/bot/start`, `/stop`, `/restart` — lifecycle mgmt |
| 15 | REST: notifications | BE | ✅ | `GET/PUT /api/notifications/discord` — webhook config |
| 16 | WebSocket: live feed | BE | ✅ | `/ws/live` — streams cycle results (price, signal, indicators, PnL) |
| 17 | SQLite WAL mode | BE | ✅ | Enable WAL for concurrent API reads while bot writes |
| 18 | Equity snapshots table | BE | ✅ | Log balance every cycle → `equity_snapshots` table for charting |
| 19 | Signals log table | BE | ✅ | Log every cycle's signal + indicators → `signals_log` table |
| 20 | API auth | BE | — | Deferred — CORS localhost-only; add Bearer token when deploying remotely |

### Phase C — Frontend Dashboard

*`frontend/` directory — Vite + React + TypeScript SPA*

| # | Task | Track | Status | Description |
|---|------|-------|--------|-------------|
| 21 | Vite + React scaffold | FE | ✅ | Project init, TypeScript, dark theme, sidebar layout |
| 22 | API client + hooks | FE | ✅ | Typed fetch wrapper, React Query, WebSocket hook |
| 23 | Live status panel | FE | ✅ | Price, signal, position, balance — all via WebSocket |
| 24 | Trade history table | FE | ✅ | Paginated, PnL coloring (green/red) |
| 25 | Equity curve chart | FE | ✅ | Line chart from balance snapshots (recharts) |
| 26 | Strategy selector | FE | ✅ | Dropdown + metadata display, saves via API |
| 27 | Config editor | FE | ✅ | Risk, trading params as forms — no raw YAML |
| 28 | Bot control panel | FE | ✅ | Start/Stop/Restart buttons, status badge, daily stats |
| 29 | Discord webhook config | FE | ✅ | Set/test webhook URL from UI |

### Phase D — Docker

| # | Task | Track | Status | Description |
|---|------|-------|--------|-------------|
| 30 | Backend Dockerfile | INF | ✅ | `backend/Dockerfile` — copies config/, exposes 8000, healthcheck `/api/health` |
| 31 | Frontend Dockerfile | INF | ✅ | `frontend/Dockerfile` — multi-stage: node build → nginx serve with API proxy |
| 32 | compose.yml | INF | ✅ | Services: `omnitrader` (8000) from `./backend`, `frontend` (3000/80) from `./frontend` |

**Exit Criteria**: `docker compose up` → dashboard at localhost:3000 showing live BTC price, trade history, and working bot controls

---

## 🟠 P1: Production Ready (SHOULD HAVE)

*Modules: Risk Engine (full), Monitoring Engine, Infrastructure & Safety*

### Backend

| # | Task | Track | Status | Description |
|---|------|-------|--------|-------------|
| 33 | Daily circuit breaker | BE | ✅ | Pause trading if daily loss >5% |
| 34 | Discord notifications | BE | ✅ | Alerts for trades, errors, circuit breaker |
| 35 | Graceful shutdown | BE | ✅ | Handle Ctrl+C, cleanup connections |
| 36 | Error handling | BE | ✅ | Retry logic, connection recovery |
| 37 | Trailing stop | BE | ✅ | Dynamic SL follows price (1% activation, 0.5% callback) |
| 38 | Strategy registry | BE | ✅ | Pluggable strategies via decorator |
| 39 | EMA 200 trend filter | BE | ⬜ | Only trade in direction of EMA 200 on higher TF |
| 40 | Live trading mode | BE | ⏳ | Switch paper_mode: false, add Binance keys |
| 41 | Position monitoring | BE | ⏳ | Track open positions, update PnL every cycle |
| 42 | Slippage tracking | BE | ⬜ | Log expected vs actual fill price on every order |
| 43 | Drawdown size reduction | BE | ⬜ | 3 consecutive losses → reduce size 50% or pause 24h |
| 44 | Position reconciliation | BE | ⬜ | Verify local state matches exchange every hour |

### Frontend

| # | Task | Track | Status | Description |
|---|------|-------|--------|-------------|
| 45 | Risk dashboard panel | FE | ⬜ | Circuit breaker status, daily PnL bar, drawdown gauge |
| 46 | Position monitor panel | FE | ⬜ | Live PnL %, trailing stop level, time in trade |
| 47 | Slippage report page | FE | ⬜ | Table of expected vs actual fills, avg drift |

**Exit Criteria**: Safe to deploy with $100 real capital, dashboard shows risk state in real time

---

## 🟡 P2: Strategy Expansion + SMC (NICE TO HAVE)

*Modules: Signal Engine (full), Scanner (enhanced)*

### Classical Strategies (Done)

| # | Task | Track | Status | Description |
|---|------|-------|--------|-------------|
| 48 | ADX trend filter | BE | ✅ | Only trade when ADX >25 (trending market) |
| 49 | Bollinger Bands | BE | ✅ | Mean reversion strategy + RSI |
| 50 | Breakout strategy | BE | ✅ | Price breaks N-period high/low |
| 51 | Z-Score strategy | BE | ✅ | Statistical mean reversion |
| 52 | Unit tests | BE | ✅ | Test all strategies (283 lines) |

### Signal Enhancement

| # | Task | Track | Status | Description |
|---|------|-------|--------|-------------|
| 53 | Confidence score | BE | ⬜ | Normalize all signals to 0-1 score with threshold gate |
| 54 | ATR-based stops | BE | ⬜ | Stop loss sized to volatility, not fixed percentage |
| 55 | Time-based stop | BE | ⬜ | Exit if trade doesn't move in N candles (thesis decay) |
| 56 | Regime classifier | BE | ⬜ | Classify market: trending / ranging / high-vol / chop |

### SMC Foundation (Build First)

*Multi-timeframe is prerequisite for all SMC — without it, setups conflict across timeframes.*

| # | Task | Track | Status | Description |
|---|------|-------|--------|-------------|
| 57 | Multi-timeframe analysis | BE | ⬜ | **H4/Daily**: bias → **H1**: structure → **M15**: entry |
| 58 | Market Structure tracker | BE | ⬜ | Track swing highs/lows, identify HH/HL/LH/LL |
| 59 | BOS detection | BE | ⬜ | Break of Structure — confirms trend continuation |
| 60 | CHoCH detection | BE | ⬜ | Change of Character — early reversal signal |
| 61 | Premium/Discount zones | BE | ⬜ | Fib 50% split — buy discount, sell premium |

### SMC Entry Refinement (Points of Interest)

| # | Task | Track | Status | Description |
|---|------|-------|--------|-------------|
| 62 | Order Block detection | BE | ⬜ | Last opposing candle before impulsive move (POI) |
| 63 | Fair Value Gap (FVG) | BE | ⬜ | 3-candle imbalance — market revisits to rebalance |
| 64 | OTE Zone (Fib 62-79%) | BE | ⬜ | Optimal Trade Entry for sniper entries |
| 65 | Liquidity Sweep | BE | ⬜ | Detect stop hunts at equal highs/lows, enter on rejection |
| 66 | Equal Highs/Lows | BE | ⬜ | Map obvious liquidity pools as targets |

### Kill Zones & Execution

| # | Task | Track | Status | Description |
|---|------|-------|--------|-------------|
| 67 | Kill Zone session filter | BE | ⬜ | London: 04:00-06:00 BRT / NY: 10:00-13:00 BRT |
| 68 | DCA logic | BE | ⬜ | Add to position at better prices (max 2x) |
| 69 | Multiple pairs | BE | ⬜ | ETH/USDT, SOL/USDT (one at a time) |

### Frontend

| # | Task | Track | Status | Description |
|---|------|-------|--------|-------------|
| 70 | Strategy analytics page | FE | ⬜ | Per-strategy win rate, avg PnL, Sharpe over last N trades |
| 71 | SMC chart overlay | FE | ⬜ | Order blocks, FVG, liquidity levels, BOS/CHoCH on chart |
| 72 | Multi-timeframe view | FE | ⬜ | Toggle H4/H1/M15 with structure annotations |
| 73 | Regime indicator | FE | ⬜ | Current market classification in dashboard header |

### SMC Implementation Order

```
Step 1: Multi-timeframe (#57)        ← PREREQUISITE for all SMC
  │     H4 sets bias, H1 structure, M15 entry
  │
Step 2: Market Structure (#58-60)    ← Foundation
  │     Track swings → detect BOS → detect CHoCH
  │
Step 3: Zones (#61)                  ← Where to look
  │     Premium/Discount split via Fib 50%
  │
Step 4: POI (#62-64)                 ← Where to enter
  │     Order Blocks → FVG → OTE Zone
  │
Step 5: Liquidity (#65-66)           ← Confirmation
  │     Sweep detection → Equal H/L mapping
  │
Step 6: Kill Zones (#67)             ← When to trade
        London KZ: 04:00-06:00 BRT
        New York KZ: 10:00-13:00 BRT
```

**Exit Criteria**: Sharpe ratio >1.0 on backtest data, SMC zones visible on dashboard chart

---

## 🟢 P3: Automation & Scale (OPTIONAL)

*Modules: Strategy Evolution, Capital Allocation Controller*

### Backtesting & Optimization

| # | Task | Track | Status | Description |
|---|------|-------|--------|-------------|
| 74 | Backtesting engine | BE | ⬜ | Test strategies on historical data |
| 75 | Walk-Forward Analysis | BE | ⬜ | Rolling optimization to prevent overfitting |
| 76 | Monte Carlo sims | BE | ⬜ | Stress test with randomized conditions |

### Capital Allocation Controller

| # | Task | Track | Status | Description |
|---|------|-------|--------|-------------|
| 77 | Max concurrent positions | BE | ⬜ | Limit to N open trades at once |
| 78 | Portfolio exposure cap | BE | ⬜ | Max 40% of capital deployed at any time |
| 79 | Correlation check | BE | ⬜ | Prevent correlated positions (e.g. BTC + ETH both long) |
| 80 | Risk-on / Risk-off mode | BE | ⬜ | Reduce exposure in high-vol regimes |
| 81 | Kelly Criterion sizing | BE | ⬜ | Optimal position size from win rate + payoff ratio |

### Execution Improvements

| # | Task | Track | Status | Description |
|---|------|-------|--------|-------------|
| 82 | Limit order entries | BE | ⬜ | Slippage-aware limits with market order fallback |
| 83 | Partial fill handling | BE | ⬜ | Track and manage partially filled orders |
| 84 | Multi-pair trading | BE | ⬜ | Trade multiple pairs simultaneously |

### Performance & Infra

| # | Task | Track | Status | Description |
|---|------|-------|--------|-------------|
| 85 | Celery + Redis | INF | ⬜ | Async job queue for backtests & heavy computations |
| 86 | Semi-autonomous mode | BE | ⬜ | Trade proposals in dashboard, approve/reject with one click |
| 87 | Cloud deployment | INF | ⬜ | GCP e2-micro with failover |

### Frontend

| # | Task | Track | Status | Description |
|---|------|-------|--------|-------------|
| 88 | Backtest results UI | FE | ⬜ | Equity curve, trade list, metrics table per backtest run |
| 89 | Capital allocation dash | FE | ⬜ | Current exposure, position limits, correlation matrix |
| 90 | Semi-auto approval | FE | ⬜ | Trade proposal cards: approve/reject/modify before execution |
| 91 | Job progress tracker | FE | ⬜ | Celery job status: backtest progress bar, queue depth |

**Exit Criteria**: $1000+ capital, fully automated, backtests run from dashboard

---

## 🔵 P4: Intelligence Layer (FUTURE)

*Modules: Research Engine, Journaling Engine, Salience Engine, Strategy Evolution*

### Research Engine (LLM-Augmented)

| # | Task | Track | Status | Description |
|---|------|-------|--------|-------------|
| 92 | LLM API integration | BE | ⬜ | Paid API (Claude/GPT-4) for research & analysis |
| 93 | LLM research step | BE | ⬜ | SIGNAL → RESEARCH (API) → DECIDE pipeline |
| 94 | Thesis generation | BE | ⬜ | LLM generates: thesis, risk factors, invalidation conditions |
| 95 | LLM daily reports | BE | ⬜ | AI-generated market summary + trade review |
| 96 | News filter | BE | ⬜ | Pause trading on major events (LLM-parsed) |

### Journaling Engine

| # | Task | Track | Status | Description |
|---|------|-------|--------|-------------|
| 97 | Structured trade journal | BE | ⬜ | Auto-log: thesis, entry reason, outcome, mistake, lesson |
| 98 | Thesis invalidation exit | BE | ⬜ | Close trade if LLM detects thesis no longer valid |

### Salience & Self-Learning

| # | Task | Track | Status | Description |
|---|------|-------|--------|-------------|
| 99 | Salience scoring | BE | ⬜ | Self-learning memory (+0.1 win, -0.1 loss, -0.02/wk decay) |
| 100 | Learning extraction | BE | ⬜ | Auto-extract patterns from journal: what worked, what didn't |
| 101 | Strategy evolution | BE | ⬜ | Promote high-salience learnings → propose rule changes → backtest → adopt |

### Market Intelligence

| # | Task | Track | Status | Description |
|---|------|-------|--------|-------------|
| 102 | On-chain metrics | BE | ⬜ | Whale cohorts (1k-10k BTC), exchange flows, cycle detection |
| 103 | Sentiment analysis | BE | ⬜ | LunarCrush Fear/Greed index |
| 104 | Funding rate monitor | BE | ⬜ | Track perpetual funding for imbalance signals |
| 105 | Open interest tracking | BE | ⬜ | Detect crowded trades, divergence from price |

### Frontend

| # | Task | Track | Status | Description |
|---|------|-------|--------|-------------|
| 106 | Research reports viewer | FE | ⬜ | LLM analysis inline with trade, thesis + risk factors |
| 107 | Trade journal page | FE | ⬜ | Structured entries: thesis, entry reason, outcome, lessons |
| 108 | Salience dashboard | FE | ⬜ | Ranked learnings with decay visualization, promote/demote |
| 109 | Market intelligence panel | FE | ⬜ | On-chain flows, funding rate chart, sentiment gauge |

**LLM Strategy**: Paid API (Claude Opus/Sonnet or GPT-4o) — no local inference, no GPU bottleneck, best quality.
Ollama container kept for offline fallback only.

**Exit Criteria**: LLM research step improves win rate by >5%, all reports viewable in dashboard

---

## ⚪ P5: Enterprise Architecture (MAYBE NEVER)

*Full microservices — only if simple bot outgrows itself.*

### Data Architecture

| # | Task | Track | Status | Description |
|---|------|-------|--------|-------------|
| 110 | PostgreSQL migration | INF | ⬜ | Replace SQLite for trades, positions, metrics |
| 111 | Redis state cache | INF | ⬜ | Real-time shared state between services |
| 112 | Vector DB | INF | ⬜ | Store learning embeddings for semantic retrieval |

### Microservices

| # | Task | Track | Status | Description |
|---|------|-------|--------|-------------|
| 113 | Streamer service | BE | ⬜ | WebSocket real-time data feed |
| 114 | Sentinel service | BE | ⬜ | Dedicated sentiment + on-chain analysis |
| 115 | Quant service | BE | ⬜ | Backtesting, WFA, optimization |
| 116 | Strategist service | BE | ⬜ | LLM-powered decision making |
| 117 | Guardian service | BE | ⬜ | Centralized risk management |

**Note**: Most profitable bots are simple. Only scale if necessary.

---

## Project Structure

```
OmniTrader/
  src/                      ← Python backend
    main.py                 ← Entry: starts bot + API via asyncio.gather()
    config.py
    exchange.py
    risk.py
    database.py
    notifier.py
    strategies/
      __init__.py
      base.py
      registry.py
      ema_volume.py
      adx_trend.py
      bollinger_bands.py
      breakout.py
      z_score.py
    api/                    ← NEW: FastAPI routes
      __init__.py
      app.py                ← create_api(bot) factory
      routes_bot.py         ← /api/bot/*
      routes_config.py      ← /api/config, /api/notifications
      routes_trades.py      ← /api/trades, /api/equity, /api/daily-summary
      routes_status.py      ← /api/status, /api/balance, /api/position
      routes_strategies.py  ← /api/strategies
      ws.py                 ← /ws/live WebSocket
  frontend/                 ← NEW: Vite + React + TypeScript
    src/
      components/           ← Reusable UI (charts, tables, forms)
      pages/                ← Dashboard, Trades, Strategies, Config, etc.
      hooks/                ← useWebSocket, useApi, useBot
      lib/                  ← API client, types, utils
    index.html
    package.json
    tsconfig.json
    vite.config.ts
    Dockerfile              ← Multi-stage: node build → nginx
  config/
    config.yaml
  docker/                   ← NEW: reverse proxy config
    nginx.conf
  data/
    trades.db
  tests/
  compose.yml               ← REWRITTEN: omnitrader + frontend + nginx
  Dockerfile                ← UPDATED: expose 8000, healthcheck
  pyproject.toml
  Makefile
```

---

## Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| **Backend** | Python 3.13, FastAPI, uvicorn | Async — bot + API share event loop |
| **Frontend** | Vite, React 19, TypeScript | SPA, dark theme, responsive |
| **Database** | SQLite (WAL mode) | Concurrent reads for API, Postgres later (P5) |
| **Exchange** | CCXT (Binance Futures) | Paper mode + live mode |
| **Charts** | recharts or lightweight-charts | Equity curve, candlestick, overlays |
| **State** | React Query (@tanstack) | Server state management, auto-refetch |
| **Styling** | Tailwind CSS | Utility-first, dark mode built-in |
| **Docker** | Compose v2 | 3 services: backend, frontend, nginx |
| **Jobs** | Celery + Redis (P3) | Async backtests, heavy computations |
| **Notifications** | Discord webhooks | Via backend API + UI config |

---

## Performance Metrics (Track From Day 1)

| Metric | Description |
|--------|-------------|
| Sharpe Ratio | Risk-adjusted return (target >1.0) |
| Sortino Ratio | Downside-risk-adjusted return |
| Max Drawdown | Worst peak-to-trough drop |
| Profit Factor | Gross profit / gross loss |
| Win Rate | % of trades that are profitable |
| Expectancy | Average $ per trade |
| Slippage Drift | Expected vs actual fill price |
| Strategy Decay Rate | How fast a strategy loses edge |

---

## Risk Hierarchy (Non-Negotiable)

```
Priority 1: Capital Survival
Priority 2: Exposure Control
Priority 3: Drawdown Containment
Priority 4: Edge Preservation
Priority 5: Growth
```

The system never chases profits. It compounds edge while protecting downside.

---

## System Failsafe Logic

```
IF   3 consecutive losses
  OR daily drawdown > 5%
  OR abnormal volatility spike (>3x ATR)
THEN
  → Reduce position size by 50%
  → OR pause trading for 24h
  → Notify via Discord + Dashboard alert
```

---

## Autonomy Levels

| Level | Mode | Description |
|-------|------|-------------|
| 1 | **Paper** | Simulated trades, no real money (current) |
| 2 | **Semi-Auto** | Bot signals, human approves via **dashboard** |
| 3 | **Full Auto** | No intervention, emergency override only |

---

## System Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                   │
│  SCAN ──→ SIGNAL ──→ RESEARCH ──→ DECIDE ──→ RISK GATE          │
│  (cycle)   (strategies)  (LLM API)   (gate)    (hard limits)     │
│                                                                   │
│  ──→ EXECUTE ──→ MONITOR ──→ CLOSE ──→ JOURNAL                   │
│      (orders)    (every cycle) (SL/TP/thesis) (structured log)    │
│                                                                   │
│  ──→ EXTRACT LEARNING ──→ UPDATE SALIENCE ──→ EVOLVE STRATEGY    │
│      (pattern mining)     (score ±0.1)        (backtest + adopt)  │
│                                                                   │
│                      ┌─────────────┐                              │
│                      │  DASHBOARD  │  ← reads all state via API   │
│                      │  (React)    │  ← controls bot lifecycle    │
│                      │  ← WebSocket live feed                     │
│                      └─────────────┘                              │
└──────────────────────────────────────────────────────────────────┘
```

---

## Module Coverage Map

| Module | P0 | P1 | P2 | P3 | P4 | P5 |
|--------|----|----|----|----|----|----|
| 1. Market Scanner | ✅ basic | | ✅ full | | | |
| 2. Signal Engine | ✅ basic | | ✅ full | | | |
| 3. Research Engine | | | | | ✅ | |
| 4. Decision Engine | ✅ basic | | ✅ regime | | ✅ thesis | |
| 5. Risk Engine | ✅ basic | ✅ full | | ✅ capital | | |
| 6. Execution Engine | ✅ basic | ✅ slippage | | ✅ limits | | |
| 7. Monitoring Engine | | ✅ | | | ✅ thesis | |
| 8. Exit Engine | ✅ SL/TP | ✅ trailing | ✅ time | | ✅ thesis | |
| 9. Journaling Engine | | | | | ✅ | |
| 10. Salience Engine | | | | | ✅ | |
| 11. Strategy Evolution | | | | ✅ backtest | ✅ auto | |
| 12. Capital Allocation | | | | ✅ | | |
| 13. Infrastructure | ✅ docker | ✅ safety | | ✅ cloud | | ✅ |
| **14. Dashboard** | **✅ full** | **✅ risk** | **✅ charts** | **✅ backtest** | **✅ intel** | |

---

## Task Summary

| Priority | Backend | Frontend | Infra | Total | Done |
|----------|---------|----------|-------|-------|------|
| P0 | 20 | 9 | 3 | **32** | 8 |
| P1 | 12 | 3 | — | **15** | 6 |
| P2 | 22 | 4 | — | **26** | 5 |
| P3 | 11 | 4 | 2 | **17** | — |
| P4 | 14 | 4 | — | **18** | — |
| P5 | 5 | — | 3 | **8** | — |
| **Total** | **84** | **24** | **8** | **116** | **19** |

Progress: **19/116 (16%)** — all backend trading core

---

## Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Complete |
| ⏳ | In Progress |
| ⬜ | Not Started |
| BE | Backend (Python) |
| FE | Frontend (React) |
| INF | Infrastructure (Docker, CI, Cloud) |

---

## Changelog

### 2026-02-21 (Update 4)
- **Major restructure**: dual-track roadmap (Backend + Frontend)
- P0 expanded: Phase A (trading core ✅) + Phase B (FastAPI API) + Phase C (React dashboard) + Phase D (Docker)
- Dashboard V1 in P0: live status, trade history, equity curve, strategy selector, config editor, bot control, Discord config
- Stack chosen: FastAPI + Vite/React/TS + SQLite WAL + Docker Compose + nginx
- Every priority level now has a Frontend subsection
- P1 FE: risk dashboard, position monitor, slippage report
- P2 FE: strategy analytics, SMC chart overlay, multi-TF view, regime indicator
- P3 FE: backtest results, capital allocation dash, semi-auto approval, job tracker
- P3: Celery + Redis added (performance optimization deferred from P0)
- P4 FE: research viewer, trade journal, salience dashboard, market intel panel
- Semi-autonomous mode moved from Discord-only to dashboard approval (P3)
- 78 → 116 tasks (24 frontend + 8 infra + 6 backend additions)
- Added: Project Structure, Tech Stack, Task Summary tables

### 2026-02-21 (Update 3)
- Full system spec integration: 78 tasks (was 57)
- Added P1: slippage tracking, drawdown reduction, position reconciliation
- Added P2: confidence scores, ATR stops, time stops, regime classifier
- Added P3: Capital Allocation Controller (5 tasks), execution improvements, semi-auto mode
- Added P4: thesis generation/invalidation, learning extraction, strategy evolution, OI tracking
- Added P5: PostgreSQL, Redis, Vector DB
- Added: Performance Metrics, Risk Hierarchy, Failsafe Logic, Autonomy Levels
- Added: System Flow diagram, Module Coverage Map

### 2026-02-21 (Update 2)
- Roadmap audit: added missing SMC setups (FVG, Liquidity, OB)
- Added EMA 200 filter to P1
- Added on-chain metrics, session filter
- Full SMC methodology with 6-step implementation order

### 2026-02-21
- ✅ Strategy Book: 5 strategies with registry pattern
- ✅ Trailing stop in RiskManager
- ✅ Unit tests for strategies
- ✅ Docker/Ollama setup (compose.yml)
- ✅ Code quality: Ruff, pre-commit, pyproject.toml
- Discussed SMC framework (3 setups, top-down analysis, session windows)
- Discussed self-learning loop (salience scoring)
- Decided paid LLM API over local Ollama

### 2026-02-20
- ✅ MVP complete with paper trading mode
- ✅ Bot ran live: BTC $68k, signal HOLD (volume below threshold)
- ✅ Paper trading after Binance testnet deprecation
- ✅ Discord alerts configured
- ✅ Makefile and README

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-21 | Dashboard as P0, not P3 | Can't manage a trading bot by editing YAML files — UI is essential |
| 2026-02-21 | Vite + React over Next.js | SPA sufficient, no SSR needed for personal dashboard |
| 2026-02-21 | FastAPI alongside async bot | Natural fit — shares event loop, reads bot state directly |
| 2026-02-21 | SQLite WAL now, Postgres later | Zero migration overhead, concurrent reads work at this scale |
| 2026-02-21 | Celery deferred to P3 | No async job queue needed until backtesting |
| 2026-02-21 | Dual-track roadmap (BE+FE) | Dashboard evolves with every backend feature, never falls behind |
| 2026-02-21 | 13-module system spec as single roadmap | Keep everything in one place, avoid doc fragmentation |
| 2026-02-21 | Full SMC methodology (10 concepts) | Institutional-grade entries aligned with your framework |
| 2026-02-21 | Paid LLM API over local Ollama | Best quality, no GPU bottleneck, faster iteration |
| 2026-02-21 | Strategy Pattern Architecture | Enable plug-and-play strategies for backtesting |
| 2026-02-20 | Start with single-service MVP | Prove concept before complexity |
| 2026-02-20 | EMA + Volume strategy | Simple, proven, debuggable |
| 2026-02-20 | Paper trading mode | Binance futures testnet deprecated |
| 2026-02-20 | Discord for alerts | Already in use, simple setup |
