# TODO

Forward-looking queue only. Completed work is archived in DONE.md, and active execution work belongs in TASKS.md.

> Last updated: 2026-03-12 | Sprint: Next-sprint queue

---

## CRITICAL — Runtime-Breaking Bugs

### T63. [BUG] Normalize OHLCV contract between exchange adapters and backtest engine
- **Priority**: CRITICAL
- **Depends on**: None
- **Scope**: `CCXTExchange.fetch_ohlcv()` returns a Pandas DataFrame, while `BacktestEngine.run()` expects a list of candle dictionaries with integer millisecond timestamps. The live execution path cannot feed fetched historical data into the backtest engine without ad hoc conversion.
- **Files**: `backend/src/exchanges/ccxt_adapter.py`, `backend/src/exchanges/base.py`, `backend/src/backtest/engine.py`

### T64. [BUG] Fix shutdown cleanup for WebSocket and CCXT client resources
- **Priority**: CRITICAL
- **Depends on**: None
- **Scope**: Restarting the stack produces `asyncio.CancelledError` traces, explicit CCXT warnings about missing `await exchange.close()`, and unclosed `aiohttp` client sessions. The bot stop path needs deterministic shutdown ordering and task cancellation for WS feed and exchange resources.
- **Files**: `backend/src/main.py`, `backend/src/ws_feed.py`, `backend/src/exchanges/ccxt_adapter.py`

### T65. [SECURITY] Stop printing full auto-generated API keys to logs/stdout
- **Priority**: CRITICAL
- **Depends on**: None
- **Scope**: Dev-mode auth initialization prints the entire generated bearer token to stdout on startup. This is unsafe in shared terminals, CI logs, and container logs. Replace it with masked output or a one-time secure retrieval path.
- **Files**: `backend/src/api/auth.py`

---

## HIGH — Logic / Schema Bugs

### T66. [BUG] Fix strategy selector Cypher schema mismatch
- **Priority**: HIGH
- **Depends on**: None
- **Scope**: `selector.py:42` queries `(:Trade)-[:TRIGGERED_BY]->(:Signal)`, `t.status='closed'`, `s.strategy_name` — none of which exist in the actual Memgraph schema. Auto-selection always falls back to `adx_trend` regardless of performance history.
- **Options**: (A) Add `strategy_name` to Signal nodes and create `:TRIGGERED_BY` relationship in `memgraph.py` trade-close writer; (B) rewrite selector query against existing Trade + Signal fields.
- **Files**: `backend/src/strategy/selector.py`, `backend/src/database/memgraph.py`

### T67. [BUG] Standardize graph relationship name `:IMPACTS` vs `:MENTIONS`
- **Priority**: HIGH
- **Depends on**: None
- **Scope**: `ingestor.py:258` creates `:IMPACTS` edges; `graph.py:134` queries `:MENTIONS` edges for per-asset news. News graph endpoints return empty results for correctly ingested data.
- **Resolution**: Standardize to `:MENTIONS` — update `ingestor.py` to write `:MENTIONS`, or update all graph route queries to use `:IMPACTS`.
- **Files**: `backend/src/intelligence/ingestor.py`, `backend/src/api/routes/graph.py`

### T68. [BUG] Run Celery Beat in the deployed stack so `ingest_news_cycle` actually executes
- **Priority**: HIGH
- **Depends on**: None
- **Scope**: `workers/__init__.py` already defines a beat schedule, but the compose stack only starts a Celery worker and never launches a Beat process. News ingestion still never runs automatically in production-like runtime.
- **Files**: `backend/src/workers/__init__.py`, `compose.yml`, `compose.dev.yml`

### T74. [FEATURE] Add a live signals API endpoint backed by persisted `Signal` nodes
- **Priority**: HIGH
- **Depends on**: None
- **Scope**: Signals are persisted through `database.log_signal(...)`, but there is no `/api/signals` route in the current API surface. Monitoring and dashboard flows cannot retrieve recent signal history directly.
- **Files**: `backend/src/api/__init__.py`, `backend/src/api/routes`, `backend/src/database/memgraph.py`

---

## MEDIUM — Backtest & Metrics Gaps

### T69. [IMPROVEMENT] Enhance backtest metrics to institutional standard
- **Priority**: MEDIUM
- **Depends on**: T55 (Walk-Forward Validation Framework research)
- **Scope**: Current metrics include Sharpe, Sortino, profit factor, win rate, max drawdown, bootstrap CI, walk-forward splits. Missing: Calmar ratio, portfolio turnover, information ratio (IC), IC decay curve, factor attribution, t-stat significance reporting.
- **Files**: `backend/src/backtest/metrics.py`, `backend/src/backtest/engine.py`

### T70. [IMPROVEMENT] Add explicit slippage/spread model to backtest engine
- **Priority**: MEDIUM
- **Depends on**: T58 (Execution Optimization Design research)
- **Scope**: Engine currently simulates fills at bar close with no market impact model. Add configurable slippage (fixed bps, vol-scaled, or empirical) and spread cost per trade. Required for realistic P&L reporting and execution policy validation.
- **Files**: `backend/src/backtest/engine.py`

### T75. [IMPROVEMENT] Add executable walk-forward runner over real fetched history
- **Priority**: MEDIUM
- **Depends on**: T55
- **Scope**: `generate_walk_forward_splits()` exists, but there is no integrated runner that fetches enough history, validates horizon sufficiency, executes train/test windows, and summarizes out-of-sample performance. In the live run, a 1,000-bar sample produced zero monthly splits.
- **Files**: `backend/src/backtest/metrics.py`, `backend/src/backtest/engine.py`

### T76. [IMPROVEMENT] Improve runtime reporting surface for backtest and trade analytics
- **Priority**: MEDIUM
- **Depends on**: T69
- **Scope**: Current monitoring surface exposes health, status, trades, and indicators, but there is no API/report contract for equity curves, drawdowns, bootstrap CI, or backtest summaries. Add a reporting endpoint or export layer aligned with the implemented metrics.
- **Files**: `backend/src/api/routes/trades.py`, `backend/src/backtest/engine.py`, `backend/src/backtest/metrics.py`

---

## LOW — Test Coverage Gaps

### T71. [TEST] Add live-schema integration test for strategy selector
- **Priority**: LOW
- **Depends on**: T66
- **Scope**: `test_selector.py` mocks the DB driver with pre-canned records, hiding the Cypher schema mismatch. Add a test that runs the selector query against an in-memory Memgraph instance (or validated fixture data) to assert correct field and relationship names.
- **Files**: `backend/tests/test_selector.py`

### T72. [TEST] Add end-to-end news ingestion + graph route test
- **Priority**: LOW
- **Depends on**: T67
- **Scope**: No test validates the round-trip: ingestor writes `:IMPACTS`/`:MENTIONS` → graph route reads back data for the same asset. Add a parametrized integration test fixture that seeds a news event and asserts the graph route returns it.
- **Files**: `backend/tests/test_ingestor.py`, `backend/tests/test_api_graph.py`

### T73. [TEST] Add regression coverage for exchange-to-backtest OHLCV normalization
- **Priority**: LOW
- **Depends on**: T63
- **Scope**: Current tests validate backtest behavior with fixture candles, but not the real adapter output shape. Add a contract test that uses concrete exchange adapter output or a DataFrame-shaped fixture and verifies the normalization path into `BacktestEngine.run()`.
- **Files**: `backend/tests/test_backtest.py`, `backend/tests/test_exchanges.py`

### T77. [TEST] Fix unawaited AsyncMock warning in crisis integration tests
- **Priority**: LOW
- **Depends on**: None
- **Scope**: `make test` passes but still emits an unawaited coroutine warning from `test_crisis_integration.py` via the circuit-breaker path in `main.py`. Clean up the mock/await contract so the suite is warning-free.
- **Files**: `backend/tests/test_crisis_integration.py`, `backend/src/main.py`

### T78. [DOC] Reconcile README/API documentation with the actual runtime surface
- **Priority**: LOW
- **Depends on**: None
- **Scope**: Some operator-facing docs and assumptions lag behind the actual stack behavior and API surface. Update documentation to reflect current routes, Memgraph-first persistence, auth behavior, and implemented reporting capabilities.
- **Files**: `README.md`, `tasks/TODO.md`, `tasks/BACKLOG.md`

---

## Local Triage (No Open GitHub Issues) - 2026-03-12

Runtime verification completed against the live Docker stack. Stale items removed where the current code already matches the intended behavior, and newly verified runtime gaps have been promoted into the queue.

---

## Promoted Research Queue (Needs Design Before Build)

### T55. [RESEARCH] Walk-Forward Validation Framework (B2)
- **Priority**: CRITICAL
- **Research label**: Methodology design + statistical protocol
- **Depends on**: T35 (Backtesting Engine), stable strategy parameter interface
- **Deliverable**: Design doc for rolling train/test windows, decay thresholds, and acceptance criteria for promotion to implementation

### T56. [RESEARCH] Monte Carlo Stress Testing (B3)
- **Priority**: HIGH
- **Research label**: Risk modeling + simulation architecture
- **Depends on**: T35 (Backtesting Engine), T55 (validation assumptions)
- **Deliverable**: Design doc for bootstrap/shuffle model, scenario count, and drawdown/ruin reporting contract

### T57. [RESEARCH] Complete SMC Integration Plan (B5)
- **Priority**: MEDIUM
- **Research label**: Strategy architecture and overfitting controls
- **Depends on**: T46 (SMC confirmation baseline), multi-timeframe data plan
- **Deliverable**: Decision record for integration mode (confirmation vs standalone vs entry-refinement) and missing feature scope (order blocks/FVG/liquidity sweeps)

### T58. [RESEARCH] Execution Optimization Design (B7)
- **Priority**: MEDIUM
- **Research label**: Execution microstructure + fill-quality policy
- **Depends on**: T37 (multi-bot flow), live slippage/fill telemetry baselines
- **Deliverable**: Execution policy spec for market vs limit, TWAP/VWAP triggers, and stop-limit tradeoffs

### T59. [RESEARCH] Factor Decomposition & Beta Hedging (B15)
- **Priority**: LOW
- **Research label**: Institutional analytics design
- **Depends on**: T35 (validated strategy return streams), T37 (multi-asset exposure history)
- **Deliverable**: Factor model proposal, hedge mechanics, and required data-source inventory

---

## Promoted Build-Ready Queue (Implementation-First)

### T60. [IMPLEMENTATION] Visual Strategy Builder (B16)
- **Priority**: LOW
- **Research label**: Light UX discovery only (not blocker)
- **Depends on**: T40 (Custom Strategy System, completed)
- **Scope**: Frontend node/canvas editor that emits existing strategy JSON format

### T61. [IMPLEMENTATION] Trade Journal & Post-Mortem Annotations (B18)
- **Priority**: LOW
- **Research label**: Schema choice review during implementation
- **Depends on**: Trade history data model, optional T33 (auto summary enhancement)
- **Scope**: Trade annotation UX with notes/tags and persistence model

### T62. [IMPLEMENTATION] Theme Toggle (Dark/Light) (B20)
- **Priority**: LOW
- **Research label**: None (frontend implementation task)
- **Depends on**: None
- **Scope**: CSS variable theme tokens + persisted user preference


- `T73` - Decide fate of `GET /api/backtest/history`
	- Details: Endpoint exists as 501 stub and has no frontend caller; backtest UI currently uses run/results with mock fallback.
	- Possible solutions: (1) implement real backtest history and wire UI history table; (2) hide history route until backtest engine ships; (3) remove stub route and track in backlog until implementation window
---

## Notes

> **⚠️ STRATEGIC PIVOT (2026-03-05)**: Memgraph is the single source of truth. PostgreSQL + Redis + Alembic were replaced by Memgraph + Redis (Celery-only).

> **🚀 PLATFORM EXPANSION (2026-03-09)**: The platform now targets multi-asset autonomous trading with per-asset bots, regime-aware strategy selection, and custom TA-Lib strategies.

Historical plans and completed sprint items have been moved to DONE.md.

---
