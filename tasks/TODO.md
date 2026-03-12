# TODO

Forward-looking queue only. Completed work is archived in DONE.md, and active execution work belongs in TASKS.md.

> Last updated: 2026-03-11 | Sprint: Next-sprint queue

---

## CRITICAL — Runtime-Breaking Bugs

### T63. [BUG] Fix exchange method name mismatches in API routes
- **Priority**: CRITICAL
- **Depends on**: None
- **Scope**: `bot.py:72,97`, `bots.py:116,144`, `system.py:31` call `exchange.fetch_position()` and `exchange.fetch_balance()` — methods that do not exist on `BaseExchange`. Correct names are `get_position()` and `get_balance()`. All three endpoints throw `AttributeError` at runtime.
- **Files**: `backend/src/api/routes/bot.py`, `backend/src/api/routes/bots.py`, `backend/src/api/routes/system.py`

### T64. [BUG] Add `redis` attribute to `OmniTrader` (markets endpoint crash)
- **Priority**: CRITICAL
- **Depends on**: None
- **Scope**: `markets.py:42` reads `bot.redis` but `OmniTrader` never defines `self.redis`. The markets endpoint throws `AttributeError` in production (test fixture masks this with `MagicMock`). Add `self.redis = aioredis.from_url(...)` in `OmniTrader.__init__` or inject via app state.
- **Files**: `backend/src/api/routes/markets.py`, `backend/src/main.py`

### T65. [BUG] Fix `bot.db` → `bot.database` in indicators route
- **Priority**: CRITICAL
- **Depends on**: None
- **Scope**: `indicators.py:102` checks `if not bot or not bot.db:`. Runtime bot uses `bot.database`. Indicator computation endpoint always short-circuits as if the database is missing.
- **Files**: `backend/src/api/routes/indicators.py`

---

## HIGH — Logic / Schema Bugs

### T66. [BUG] Fix strategy selector Cypher schema mismatch
- **Priority**: HIGH
- **Depends on**: T63 (stable route layer before testing auto-mode)
- **Scope**: `selector.py:42` queries `(:Trade)-[:TRIGGERED_BY]->(:Signal)`, `t.status='closed'`, `s.strategy_name` — none of which exist in the actual Memgraph schema. Auto-selection always falls back to `adx_trend` regardless of performance history.
- **Options**: (A) Add `strategy_name` to Signal nodes and create `:TRIGGERED_BY` relationship in `memgraph.py` trade-close writer; (B) rewrite selector query against existing Trade + Signal fields.
- **Files**: `backend/src/strategy/selector.py`, `backend/src/database/memgraph.py`

### T67. [BUG] Standardize graph relationship name `:IMPACTS` vs `:MENTIONS`
- **Priority**: HIGH
- **Depends on**: None
- **Scope**: `ingestor.py:258` creates `:IMPACTS` edges; `graph.py:134` queries `:MENTIONS` edges for per-asset news. News graph endpoints return empty results for correctly ingested data.
- **Resolution**: Standardize to `:MENTIONS` — update `ingestor.py` to write `:MENTIONS`, or update all graph route queries to use `:IMPACTS`.
- **Files**: `backend/src/intelligence/ingestor.py`, `backend/src/api/routes/graph.py`

### T68. [BUG] Add Celery Beat schedule for `ingest_news_cycle`
- **Priority**: HIGH
- **Depends on**: None
- **Scope**: `ingest_news_cycle` Celery task is implemented but `workers/__init__.py` defines no `beat_schedule`. News ingestion never runs automatically; the news graph accumulates no live data unless triggered manually.
- **Files**: `backend/src/workers/__init__.py`

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

---

## LOW — Test Coverage Gaps

### T71. [TEST] Add integration tests for live exchange method naming
- **Priority**: LOW
- **Depends on**: T63
- **Scope**: `test_api_bot.py` and `test_api_bots.py` mock at the fixture level (injecting `MagicMock` exchange), masking the `fetch_position` vs `get_position` naming bug. Add contract tests that call `hasattr(exchange, 'get_position')` against all concrete `BaseExchange` implementations.
- **Files**: `backend/tests/test_api_bots.py`, `backend/tests/test_api_bot.py`

### T72. [TEST] Add live-schema integration test for strategy selector
- **Priority**: LOW
- **Depends on**: T66
- **Scope**: `test_selector.py` mocks the DB driver with pre-canned records, hiding the Cypher schema mismatch. Add a test that runs the selector query against an in-memory Memgraph instance (or validated fixture data) to assert correct field and relationship names.
- **Files**: `backend/tests/test_selector.py`

### T73. [TEST] Add end-to-end news ingestion + graph route test
- **Priority**: LOW
- **Depends on**: T67
- **Scope**: No test validates the round-trip: ingestor writes `:IMPACTS`/`:MENTIONS` → graph route reads back data for the same asset. Add a parametrized integration test fixture that seeds a news event and asserts the graph route returns it.
- **Files**: `backend/tests/test_ingestor.py`, `backend/tests/test_api_graph.py`

---

## Local Triage (No Open GitHub Issues) - 2026-03-11

Promoted from BACKLOG with explicit research labels and dependency mapping.

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

---

## Notes

> **⚠️ STRATEGIC PIVOT (2026-03-05)**: Memgraph is the single source of truth. PostgreSQL + Redis + Alembic were replaced by Memgraph + Redis (Celery-only).

> **🚀 PLATFORM EXPANSION (2026-03-09)**: The platform now targets multi-asset autonomous trading with per-asset bots, regime-aware strategy selection, and custom TA-Lib strategies.

Historical plans and completed sprint items have been moved to DONE.md.

---
