
## ✅ Completed (Audit Trail)

<details>
<summary>Previously completed items (T1–T5)</summary>

### T1. Database Infrastructure Migration
- [x] **Migrate to High-Performance Database**
    - **Status**: ✅ Implemented (`src/database/postgres.py`). Ready for config switch.
    - **Completed**: 2026-02 | **Note**: Postgres untested in production — see T20.

### T2. State Persistence Implementation
- [x] **Implement "Anti-Amnesia" Persistence Layer**
    - **Status**: ✅ Implemented (`src/database/redis_store.py`).
    - **Completed**: 2026-02 | **Note**: Redis failures silently swallowed — see T12.

### T3. Advanced Rate Limiting
- [x] **Implement Leaky-Bucket Rate Limiter**
    - **Status**: ✅ Implemented (`src/rate_limiter.py`). Capacity=2000, refill 40 units/s. All CCXT call-sites wired.
    - **Completed**: 2026-02

### T4. Event Loop Optimization (Worker Offloading)
- [x] **Implement Celery + Redis Worker Architecture**
    - **Status**: ✅ Implemented. Celery worker offloads `analyze_strategy` + `analyze_regime` tasks. 12 new tests.
    - **Completed**: 2026-02 | **Note**: No Celery circuit breaker — see T26.

### T5. WebSocket Integration
- [x] **CCXT WebSocket Integration**
    - **Status**: ✅ Implemented (`src/ws_feed.py`). Streams ticker, OHLCV, orders. 23 new tests.
    - **Completed**: 2026-02 | **Note**: No stale-data detection — see T19.


### T6. SL/TP Placement Failure is Non-Fatal
- [x] **Fix: Retry 3× or flatten position immediately**
    - **Risk Level**: 🔴 Critical
    - **Location**: `src/main.py` `_open_position()` — SL/TP placement wrapped in independent try/except that logs and continues.
    - **Vulnerability**: If the exchange rejects the SL order (price validation, rate limit, network error), the position is left **open without a stop loss on the exchange**.
    - **Impact**: Naked position during volatility → potential liquidation at 33% adverse move (3× leverage).
    - **Fix**: After SL placement failure, retry 3× with exponential backoff. If all retries fail, immediately close the position via `close_position()`. Never allow a position to exist without exchange-side protection.

### T7. Paper Mode PnL Formula Incorrect
- [x] **Fix: Correct PnL calculation in `exchange.py`**
    - **Risk Level**: 🔴 Critical
    - **Location**: `src/exchange.py` `close_position()` paper mode branch.
    - **Vulnerability**: Uses `(exit_price - entry_price) / entry_price * notional` instead of the correct `(exit_price - entry_price) * contracts`. Yields PnL in "notional-weighted percentage" units, not USDT.
    - **Impact**: All paper trading results are **mathematically wrong**. Cannot validate any strategy edge.
    - **Fix**: Use `pnl = (exit_price - entry_price) * position.contracts` for longs; negate for shorts. Match the live-mode formula in `main.py _close_position()`.

### T8. Paper Mode SL/TP Never Simulated
- [x] **Fix: Add paper SL/TP simulation engine**
    - **Risk Level**: 🔴 Critical
    - **Location**: `src/exchange.py` — paper orders stored in `_paper_orders` list but never checked against price.
    - **Vulnerability**: Paper positions can only exit via strategy signals, never via stop-loss or take-profit hits.
    - **Impact**: Paper mode drastically overstates strategy performance (no stop-outs, no trailing stop triggers). Cannot trust paper results for validation.
    - **Fix**: In `run_cycle()` or a dedicated `_check_paper_orders()` method, iterate `_paper_orders` each cycle and trigger fills when price crosses SL/TP levels.

### T9. ATR Stops Configured But Not Applied to Exchange
- [x] **Fix: Wire ATR stop values to `set_stop_loss` / `set_take_profit`**
    - **Risk Level**: 🔴 Critical
    - **Location**: `src/main.py` `_open_position()` — always calls `calculate_stop_loss` / `calculate_take_profit` (fixed %). Never calls `calculate_atr_stops` even though `use_atr_stops: true` is set in config.
    - **Vulnerability**: System believes it's using dynamic volatility-based stops but actually places fixed 2%/4% stops. Config says one thing, code does another.
    - **Impact**: Fixed stops are too tight in high-vol and too wide in low-vol. The designed volatility-adaptive behavior does not exist.
    - **Fix**: Pass `ohlcv` DataFrame to `validate_trade()`. When `use_atr_stops` is enabled, use ATR-derived prices for `set_stop_loss()` / `set_take_profit()` instead of fixed-%.

### T10. `current_positions` Hardcoded to 0
- [x] **Fix: Pass actual position count to `validate_trade`**
    - **Risk Level**: 🔴 Critical
    - **Location**: `src/main.py` `_open_position()` — `current_positions=0` hardcoded.
    - **Vulnerability**: The `max_positions` check in `RiskManager.validate_trade()` is dead code. Config allows 50 concurrent positions (nonsensical for single-asset) and the check never enforces it anyway.
    - **Impact**: If multi-position logic is ever activated, there is **no cap** on concurrent positions.
    - **Fix**: Query actual open position count from exchange/database. Set `max_positions` to a sane value (1 for single-asset, 3-5 for multi-pair).

### T11. API Mutation Endpoints Unprotected
- [x] **Fix: Add `verify_api_key` dependency to all mutation routes**
    - **Risk Level**: 🔴 Critical
    - **Location**: `src/api/routes/bot.py`, `src/api/routes/config.py`, `src/api/routes/notifications.py`
    - **Vulnerability**: `/api/bot/start`, `/api/bot/stop`, `/api/bot/trade/open`, `/api/bot/trade/close`, `PUT /api/config`, `PUT /api/notifications/discord` require **no authentication**. Anyone with network access can open leveraged positions, stop the bot, or change risk parameters.
    - **Impact**: Complete capital loss via unauthorized trading or parameter manipulation.
    - **Fix**: Apply `verify_api_key` dependency to every mutation endpoint. Add RBAC for production.

### T12. Redis Failures Silently Swallowed
- [x] **Fix: Raise or fallback on risk-state persistence failure**
    - **Risk Level**: 🔴 Critical
    - **Location**: `src/database/redis_store.py` — `set()`, `get()`, `delete()` all catch `Exception` and log but return `None`/`False`.
    - **Vulnerability**: Risk state persistence failures are invisible. `RiskManager.save_state()` could fail silently → consecutive loss counter resets → bot continues at full size after a losing streak.
    - **Impact**: Circuit breakers and loss-streak sizing become unreliable.
    - **Fix**: For critical risk state keys, raise on Redis failure or implement in-memory fallback that preserves the last known state.

### T13. Regime Classifier No Hysteresis
- [x] **Add Schmitt-trigger hysteresis to regime detection**
    - **Risk Level**: 🟠 High
    - **Location**: `src/analysis/regime.py` — ADX threshold is a single value (25). Regime flips every 30s cycle when ADX oscillates near boundary.
    - **Impact**: Strategy gating whipsaws — a signal is approved one cycle and blocked the next, or vice versa.
    - **Fix**: Enter TRENDING when ADX > 28, exit to RANGING only when ADX < 22. Same pattern for VOLATILE (ATR > 1.7× to enter, < 1.3× to exit). Track `current_regime` state between cycles.

### T14. Breakout Strategy Donchian Bug
- [x] **Fix: Use prior-bar Donchian channel for breakout signals**
    - **Risk Level**: 🟠 High
    - **Location**: `src/strategies/breakout.py` — `pandas_ta.donchian()` includes the current bar in the rolling max/min. `close > upper_channel` at `iloc[-1]` requires close to exceed the current bar's own high-of-highs — nearly impossible.
    - **Impact**: Strategy generates almost no signals. Effectively dead code.
    - **Fix**: Compare `close.iloc[-1]` against `donchian_upper.iloc[-2]` (prior bar's channel), which is the classic Turtle system definition.
    - **Completed**: 2026-03-04 | PR #59 (merged)

### T15. Level-Based Signals Without Cooldown
- [x] **Add `min_bars_between_entries` cooldown**
    - **Risk Level**: 🟠 High
    - **Location**: `src/strategies/adx_trend.py`, `bollinger_bands.py`, `breakout.py`, `z_score.py` — all use level conditions (not transitions). After SL hit, they immediately re-enter if condition persists.
    - **Impact**: "Re-entry grinder" — rapid SL hits in falling knives or false breakouts. 3-5 consecutive losses in a single session before circuit breaker fires.
    - **Fix**: Add `_last_entry_bar` tracking in `BaseStrategy`. Block new entries for N bars (configurable, default 10) after any entry.

### T16. Drawdown Uses Daily PnL Not Peak-Equity HWM
- [x] **Fix: Implement peak-equity high-water mark tracking**
    - **Risk Level**: 🟠 High
    - **Location**: `src/risk.py` `calculate_position_size()` — auto-deleverage uses `daily_pnl_pct` as proxy for drawdown. Resets every UTC midnight.
    - **Impact**: A 9% loss on Day 1 + 9% loss on Day 2 = 18% real drawdown, but auto-deleverage (10% threshold) never triggers.
    - **Fix**: Track `peak_equity` in Redis. Calculate `current_drawdown = (peak - current) / peak`. Use this for auto-deleverage instead of daily PnL.
    - **Completed**: 2026-03-05 | PR #60 (merged)

### T17. Consecutive Loss Streak Resets at Midnight
- [x] **Fix: Carry loss streaks across day boundaries**
    - **Risk Level**: 🟠 High
    - **Location**: `src/risk.py` `_ensure_daily_init()` — `self.consecutive_losses = 0` on new day.
    - **Impact**: A 3-loss streak spanning midnight is forgotten. Size reduction (50% after 3 consecutive losses) never triggers.
    - **Fix**: Persist `consecutive_losses` in Redis independently of daily stats. Only reset on consecutive wins, not on calendar boundary.
    - **Completed**: 2026-03-05 | PR #61 (merged)

### T18. No Market Order Size Validation at Exchange Boundary
- [x] **Fix: Validate `amount` parameter in `market_long` / `market_short`**
    - **Risk Level**: 🟠 High
    - **Location**: `src/exchange.py` — `amount` defaults to `None` and is never validated before CCXT call.
    - **Impact**: A refactoring error bypassing `validate_trade()` would send a None/0/negative-sized market order to the exchange.
    - **Fix**: Add `assert amount is not None and amount > 0` guard at the top of both methods. Return error, don't throw.
    - **Completed**: 2026-03-05 | PR #62 (merged)

### T19. WebSocket Feed No Stale-Data Detection
- [x] **Fix: Add timestamp-based staleness check**
    - **Risk Level**: 🟠 High
    - **Location**: `src/ws_feed.py` — streaming loops reconnect on exception but no mechanism detects silently stale data.
    - **Impact**: Bot trades on minutes-old prices after silent WS disconnection.
    - **Fix**: Track `last_ticker_update_time`. In `run_cycle()`, if ticker age > 60s, fall back to REST and log warning. If > 120s, pause trading.
    - **Completed**: 2026-03-05 | PR #63 (merged)

### T20. Postgres Implementation Completely Untested
- [x] **Add Postgres integration tests**
    - **Risk Level**: 🟠 High
    - **Location**: `tests/` — all 20 test files use SQLite in-memory. Zero Postgres coverage.
    - **Impact**: Schema divergence (TIMESTAMPTZ vs TEXT, JSONB vs TEXT) means Postgres could fail in production with no warning.
    - **Fix**: Add `test_database_postgres.py` using testcontainers or a compose-based test PostgreSQL. Test all CRUD operations, schema creation, and migration edge cases.
    - **Completed**: 2026-03-05 | PR #64 (merged, consolidated with T22+T23)

### T21. No Database Migration Framework
- [x] **Implement Alembic or equivalent migration system**
    - **Risk Level**: 🟠 High
    - **Location**: `src/database/postgres.py`, `sqlite.py` — DDL via inline `CREATE TABLE IF NOT EXISTS`. SQLite has ad-hoc `ALTER TABLE` migration; Postgres has none.
    - **Impact**: Adding columns to Postgres requires manual SQL intervention. Schema drift between environments.
    - **Fix**: Add Alembic with version-tracked migrations. Generate initial migration from current schema. All future changes via migration files.
    - **Completed**: 2026-03-05 | PR #65 (merged)

### T22. Auth is Fail-Open by Default
- [x] **Fix: Require API key even in development**
    - **Location**: `src/api/auth.py` — if `OMNITRADER_API_KEY` env var not set, all auth is bypassed.
    - **Fix**: Generate a random key on first startup if none configured. Log it once. Never allow zero-auth.
    - **Completed**: 2026-03-05 | PR #64 (merged, consolidated with T20+T23)

### T23. Hardcoded Postgres Password
- [x] **Fix: Remove default password fallbacks**
    - **Location**: `compose.yml`, `config/config.yaml`, `src/database/postgres.py` — `omnitrader_password` is hardcoded as fallback everywhere.
    - **Fix**: Require `POSTGRES_PASSWORD` env var with no default. Fail startup if not set.
    - **Completed**: 2026-03-05 | PR #64 (merged, consolidated with T20+T22)

### T24. Dev Dependencies in Production Image
- [x] **Fix: Separate dev/prod requirements**
    - **Location**: `requirements.txt` — `pytest`, `ruff`, `pre-commit` installed in production Docker image.
    - **Fix**: Split into `requirements.txt` (prod) and `requirements-dev.txt` (test/lint). Update Dockerfile to install only prod deps.
    - **Completed**: 2026-03-05 | PR #64 (merged)

### T25. No Dependency Lockfile
- [x] **Fix: Pin all versions, generate lockfile**
    - **Location**: `requirements.txt` — all deps use floor pins (`>=`). `pandas-ta>=0.3.14b` is **unmaintained** (last release 2022).
    - **Impact**: Builds are not reproducible. A dep update can silently break the system.
    - **Fix**: `pip freeze > requirements.lock`. Pin exact versions. Evaluate `pandas-ta` replacement (e.g., `ta-lib` or manual indicator implementations).
    - **Completed**: 2026-03-05 | Commit af77a64

### T26. Celery Dispatch No Circuit Breaker
- [x] **Fix: Add Celery health circuit breaker in `dispatch.py`**
    - **Location**: `src/workers/dispatch.py` — if Celery worker dies, `dispatch()` blocks for 30s per cycle (timeout). `ThreadPoolExecutor(max_workers=4)` can be exhausted.
    - **Fix**: Track consecutive Celery failures. After 3 failures, skip Celery for 5 minutes and fall back to local execution. Log prominently.
    - **Completed**: 2026-03-05 | Commit e04467c

### T27. `min_size` Hardcoded for BTC
- [x] **Fix: Fetch minimum order size from exchange**
    - **Location**: `src/risk.py` — `min_size = 0.001` hardcoded. Breaks if multi-asset is added (e.g., ETH min = 0.01).
    - **Fix**: Use `exchange.markets[symbol]['limits']['amount']['min']` from CCXT market info.
    - **Completed**: 2026-03-05 | Commit fbdbf8c

### T28. Notifier Creates New HTTP Client Per Message
- [x] **Fix: Use session-scoped `httpx.AsyncClient`**
    - **Location**: `src/notifier.py` — creates new `httpx.AsyncClient` per notification. No connection pooling, no Discord rate limiting.
    - **Fix**: Initialize client once in `__init__`. Add simple rate limiter (30 req/60s for Discord webhooks).
    - **Completed**: 2026-03-05 | Commit 1ef1cb9

</details>

---

### T33. News Ingestion & NLP Pipeline ✅ **COMPLETED 2026-03-09**
- [x] **Phase 2a: Extended graph schema**
    - Added node labels: `:Asset`, `:NewsEvent`, `:Sector`, `:MacroIndicator`, `:Candle`
    - Added relationships: `IMPACTS`, `MENTIONS`, `BELONGS_TO`, `CORRELATES_WITH`, `TRIGGERED_BY`
    - Added indexes for `NewsEvent(published_at)`, `Candle(symbol, timeframe, timestamp)`, `MacroIndicator(name)`
- [x] **Phase 2b: News ingestor service** (`backend/src/graph/ingestor.py`)
    - Integrated CryptoPanic polling, Fear & Greed ingestion, and RSS ingestion
    - Implemented deduplication and relationship linking to assets/sectors
    - Added pruning windows for short-lived news context
- [x] **Phase 2c: Ollama NLP entity extraction** (`backend/src/graph/nlp.py`)
    - Added structured extraction prompt for assets/sectors/sentiment/impact
    - Added resilient fallback behavior when Ollama is unavailable
- **Consolidates**: BACKLOG.md B4 (Macro Risk), B13 (Ollama sidecar)

---

### T34. Graph Analytics, Crisis Mode & Pipeline Integration ✅ **COMPLETED 2026-03-09**
- [x] **Phase 3a: Graph analytics queries** (`backend/src/graph/analytics.py`)
    - Implemented sentiment aggregation, crisis detection, divergence checks, and contagion analysis
- [x] **Phase 3b: Celery task + concurrent dispatch**
    - Added `analyze_knowledge_graph` task and integrated dispatch in cycle flow
- [x] **Phase 3c: Crisis mode protocol** (`backend/src/graph/crisis.py`)
    - Added automatic and manual crisis activation with persisted state
    - Added risk override profile for crisis mode
- [x] **Phase 3d: Signal gating with graph context**
    - Added long/short gating and confidence reduction based on graph signals
- [x] **Phase 3e: API endpoints** (`backend/src/api/routes/graph.py`)
    - Added sentiment, crisis, and news API endpoints
- [ ] **Phase 3f: Frontend components & WebSocket**
    - Deferred to T43 by plan

---

### T35. Backtesting Engine on Memgraph ✅ **COMPLETED 2026-03-09**
- [x] **Phase 4a: Historical candle storage**
    - Added candle persistence and retrieval patterns on Memgraph with deduplication keys
- [x] **Phase 4b: Event-driven backtest simulator** (`backend/src/backtest/engine.py`)
    - Implemented chronological simulation loop with strategy reuse and SL/TP checks
    - Added cost model (fees, spread, funding assumptions)
- [x] **Phase 4c: Walk-forward validation + metrics** (`backend/src/backtest/metrics.py`)
    - Added rolling splits, performance metrics, bootstrap confidence intervals
    - Added export-ready output structures for analysis artifacts
- **Consolidates**: BACKLOG.md B1, B2, B3

---

### T36. Exchange Adapter Architecture ✅ **COMPLETED 2026-03-09**
- [x] **Phase 5a: Abstract exchange interface** (`backend/src/exchanges/base.py`)
    - Added standardized adapter interface and shared exchange data model
- [x] **Phase 5b: CCXT adapter implementation** (`backend/src/exchanges/ccxt_adapter.py`)
    - Migrated legacy exchange implementation into adapter form
- [x] **Phase 5c: Binance direct REST adapter** (`backend/src/exchanges/binance_direct.py`)
    - Added signed request path, retry behavior, and rate-limit-aware direct adapter
- [x] **Phase 5d: Adapter factory + config** (`backend/src/exchanges/factory.py`)
    - Added adapter selection from config and fallback wiring
- [x] **Phase 5e: Integration + tests**
    - Integrated adapter factory into runtime and updated exchange-related tests

---

### T44. Backend DDD Migration (Clean Restructure) ✅ **COMPLETED 2026-03-09**
- [x] **Phase 14a: Shared kernel foundation**
    - Added shared domain value objects, event bus, aggregate root, and exceptions
- [x] **Phase 14b: First pure trading domain extraction**
    - Added pure risk validation domain service with typed outputs
- [x] **Phase 14c: Risk manager internal delegation**
    - Delegated risk calculations and validations to domain service while preserving public API
- [x] **Phase 14d: Position use-case extraction**
    - Added `OpenPositionUseCase` and `ClosePositionUseCase` with domain event emission
- [x] **Phase 14e: run_cycle orchestrator split**
    - Refactored runtime flow into helper methods and DTO-based coordination
- [x] **Phase 14f: Context moves**
    - Migrated legacy strategy/intelligence modules to bounded contexts and added architecture guardrail tests
- **Validation status**:
    - New DDD-focused tests added and passing
    - Integration checks and full Phase 14 verification passed

---

### T32. Memgraph Infrastructure & Database Layer Rewrite ✅ **COMPLETED 2026-03-09**
- [x] **Phase 1a: Docker infrastructure**
    - Removed PostgreSQL service from compose.yml
    - Added Memgraph: `memgraph/memgraph-mage:3.8.0-relwithdebinfo`
    - Added Memgraph Lab: `memgraph/lab:latest` (port 3001 for visualization)
    - Enabled Ollama service (GPU enabled)
    - Updated healthchecks: Bolt ping for Memgraph via mgconsole
    - 8 services total (down from 9, postgres removed)
    - **Completed**: 2026-03-09 | PR #66

- [x] **Phase 1b: MemgraphDatabase implementation**
    - Created `backend/src/database/memgraph.py` implementing all 18+ `BaseDatabase` abstract methods
    - Uses `neo4j` async Python driver (Bolt protocol, Memgraph-compatible)
    - Node labels: `:Trade`, `:DailySummary`, `:EquitySnapshot`, `:Signal`, `:FundingPayment`, `:State`
    - Properties match PostgreSQL schema exactly
    - Comprehensive indexes: Trade(timestamp/symbol), Signal(timestamp), EquitySnapshot(timestamp), DailySummary(date), State(key)
    - ID generation: Memgraph internal `id(node)` for auto-increment behavior
    - Timestamp storage: epoch milliseconds for efficient filtering
    - MERGE upsert pattern for daily summaries
    - Cypher aggregation queries for weekly PnL
    - ~690 lines of production code
    - **Completed**: 2026-03-09 | PR #66

- [x] **Phase 1c: Risk state migration**
    - Migrated 5 Redis keys to Memgraph `:State` nodes:
        - `omnitrader:risk:daily_stats` → `:State {key: "omnitrader:risk:daily_stats"}`
        - `omnitrader:risk:consecutive_losses` → `:State {key: "omnitrader:risk:consecutive_losses"}`
        - `omnitrader:risk:peak_equity` → `:State {key: "omnitrader:risk:peak_equity"}`
        - `omnitrader:risk:circuit_breaker` → `:State {key: "omnitrader:risk:circuit_breaker"}`
        - `omnitrader:risk:weekly_circuit_breaker` → `:State {key: "omnitrader:risk:weekly_circuit_breaker"}`
    - Updated `RiskManager` to use `database.get_state()` / `database.set_state()`
    - Removed `RedisStore` dependency from RiskManager
    - TTL support via `expires_in` parameter (converted to `expires_at` timestamp)
    - **Completed**: 2026-03-09 | PR #66

- [x] **Phase 1d: Config, cleanup, dependencies**
    - Updated `backend/config/config.yaml`: replaced PostgreSQL config with Memgraph connection params
    - Deleted legacy database implementations: `postgres.py`, `sqlite.py`, `redis_store.py`
    - Removed entire `alembic/` directory (schema versioning no longer needed)
    - Updated `requirements.txt`: removed `asyncpg`, `aiosqlite`, `alembic`; added `neo4j==6.1.0`
    - Updated `DatabaseFactory` to return `MemgraphDatabase` by default
    - Added safe port parsing with fallback to 7687
    - **Completed**: 2026-03-09 | PR #66

- **Consolidates**: BACKLOG.md B1 (Backtesting data storage), B11 (QuestDB replacement), B12 (Neo4j graph database)
- **Risk Level**: 🔴 Critical (infrastructure replacement)
- **Testing**: 134 tests passing including Memgraph integration tests with cleanup
- **CI**: All checks passing (Backend Tests & Lint, Frontend, GitGuardian)
- **Deliverables**:
    - Production-ready Memgraph database layer
    - Risk state persistence moved from Redis to Memgraph
    - Clean separation of dev/prod Docker configs (compose.yml + compose.dev.yml)
    - CI-compatible test skipping for integration tests

---

### T39. TA-Lib Migration (Phase 9a) ✅ **COMPLETED 2026-03-09**
- [x] **Phase 9a: Replace pandas-ta with TA-Lib in all strategies**
    - Migrated all 5 strategies to TA-Lib:
        - `adx_trend.py`: Uses `talib.ADX()`, `talib.EMA()`
        - `bollinger_bands.py`: Uses `talib.BBANDS()`, `talib.RSI()`
        - `breakout.py`: Uses `talib.MAX()`, `talib.MIN()` for Donchian channels
        - `ema_volume.py`: Uses `talib.EMA()`, `talib.SMA()`
        - `z_score.py`: Uses `talib.SMA()`, `talib.STDDEV()`
    - Created `backend/src/indicators.py` adapter layer:
        - `_as_float64()` helper for type safety (TA-Lib requires double precision)
        - Maintains pandas-ta API compatibility (accepts/returns pandas Series)
        - All TA-Lib calls wrapped with float64 conversion
    - Removed `pandas-ta` from `requirements.txt`
    - TA-Lib version: `TA-Lib==0.6.8` (compiled from source in Docker)
    - All 134 tests passing with identical signal behavior
    - **Completed**: 2026-03-09 | PR #66
    - **Note**: Phases 9b (Indicator catalog API) and 9c (Compute endpoint) remain pending

---

### T43. Frontend-Backend Integration Migration
- [x] **Phase 13a: Infrastructure — Vite proxy + Nginx upstream + auth**
    - `frontend/vite.config.ts`: dev proxy `/api/*` → `http://localhost:8000`, `/ws` → `ws://localhost:8000` (handles `/ws/live`)
    - `frontend/nginx.conf`: `upstream backend { server omnitrader:8000; }` + `proxy_pass` for `/api/` and `/ws/` (production)
    - `frontend/src/core/api.ts`: `Authorization: Bearer ${API_KEY}` header injected if `VITE_API_KEY` env var is set
- [x] **Phase 13b: Adapter layer — `frontend/src/lib/adapters.ts`** (~210 lines)
    - `adaptBotState(status, position, balance) → Bot`
    - `adaptTrade(backendTrade) → Trade` — id string→number, ISO timestamps, adds bot_id/notional/fee
    - `adaptEquitySnapshot(snapshot) → EquitySnapshot` — `balance` field mapped to `equity`
    - `adaptStrategy(strategy) → Strategy` — defaults for all optional fields
    - `adaptConfig(config) → AppConfig` — flattens nested `exchange`/`risk`/`notifications` into flat `AppConfig`
    - `reverseAdaptConfig(appConfig) → JsonObject` — reverse for `PUT /api/config`
    - `adaptWsMessage(msg) → CycleMessage` — `current_price`→`price`, `market_regime`→`regime`, `circuit_breaker_active`→`circuit_breaker`
    - All parameters fully typed with `Record<string, unknown>` — no `any`
- [x] **Phase 13c: Stub layer — `frontend/src/lib/stubs.ts`** (~70 lines)
    - `stubBots(realBot?) → Bot[]` — enriches first item with real backend data (→ T37)
    - `stubSentiment() → SentimentData` — neutral fallback (→ T33/T34)
    - `stubCrisis() → CrisisStatus` — `{ active: false, source: 'auto' }` (→ T34)
    - `stubNews() → NewsItem[]` — empty array (→ T33)
    - `stubBacktestResults() → BacktestResults` — mock from `mocks.ts` (→ T35)
    - `stubMarkets() → MarketPair[]` — hardcoded top-5 perpetuals (→ T42)
    - `stubEnvVars() → EnvVariable[]` — masked mock credentials (→ T41)
- [x] **Phase 13d: API client rewiring** — all domain APIs wired with real→stub fallback
    - `fetchBots()` → `GET /api/status` + `/api/position` + `/api/balance` + `adaptBotState()` → `stubBots(realBot)`
    - `startBot(id)` / `stopBot(id)` → `POST /api/bot/start|stop` for `default`
    - `fetchStrategies()` → `GET /api/strategies` + `adaptStrategy()`
    - `fetchTradeHistory()` → `GET /api/trades/history` + `adaptTrade()`
    - `fetchEquitySnapshots()` → `GET /api/equity/snapshots` + `adaptEquitySnapshot()`
    - `fetchConfig()` / `updateConfig()` → `GET|PUT /api/config` + bidirectional adapters
    - `fetchMarkets()` → real `GET /api/markets`, catch → `stubMarkets()`
    - `fetchEnvVars()` / `updateEnvVars()` → real `GET|PUT /api/env`, catch → `stubEnvVars()`
    - `runBacktest()` / `fetchBacktestResults()` → try real, catch → stubs (→ T35)
    - Sentiment/crisis/news → try real `GET /api/graph/*`, catch → stubs (→ T33/T34)
- [x] **Phase 13e: WebSocket integration**
    - `frontend/src/core/ws.ts`: connects to `VITE_WS_URL || ws://${location.host}/ws/live`
    - Adapts messages via `adaptWsMessage()` before dispatching to Zustand store
    - Only cycle messages routed (backend has no `alert`/`trade` WS types yet)
    - Exponential backoff reconnect: `min(1000 * 2^retry, 30000)` ms
- [x] **Phase 13f: Page-by-page wiring** — all 9 pages + Topbar + AppSidebar
    - **Dashboard.tsx** — `fetchBots()`, `fetchTradeHistory()`, `fetchEquitySnapshots()` on mount; live WS via Zustand
    - **BotsAssets.tsx** — reads bots from Zustand store; start/stop buttons call `startBot()`/`stopBot()`; CRUD drawers: stub
    - **Charts.tsx** — real candles via `GET /api/candles?symbol=&timeframe=&limit=200`; falls back to generated mock
    - **TradeHistory.tsx** — `fetchTradeHistory({ limit: '500' })` on mount; initializes with `mockTrades` while loading
    - **Settings.tsx** — `fetchConfig()` on mount; `updateConfig()` on save (General/Risk/Notifications); `fetchEnvVars()` for Env tab
    - **StrategyLab.tsx** — `fetchStrategies()` on mount; merges with mock fallback; custom CRUD: stub
    - **RiskMonitor.tsx** — derives from Zustand bots store (fed by `fetchBots()` in AppSidebar)
    - **Intelligence.tsx** — `fetchSentiment()`, `fetchCrisisStatus()`, `fetchNews()` on mount; stubs as fallback
    - **Backtesting.tsx** — `runBacktest()` + `fetchBacktestResults()` wired; stub fallback
    - **AppSidebar.tsx** — `fetchBots()` on mount populates global Zustand bots store for all pages
- [x] **Phase 13g: Backend stub routes — `backend/src/api/routes/stubs.py`**
    - `GET/POST/PUT/DELETE /api/bots/*` → `501 {"error": "Not implemented", "task": "T37"}`
    - `GET /api/graph/sentiment/{symbol}` → 501 (→ T33)
    - `GET|PUT /api/graph/crisis` → 501 (→ T34)
    - `GET /api/graph/news` → 501 (→ T33)
    - `POST /api/backtest/run`, `GET /api/backtest/results/{id}`, `GET /api/backtest/history` → 501 (→ T35)
    - Real routes (`/markets`, `/env`, `/system/restart`) already wired — no stubs needed
    - Registered last in `backend/src/api/__init__.py` so real routes always take priority
- **Gap fixes applied post-merge** (`101aa50`):
    - `Intelligence.tsx`: added missing `useEffect` to React import
    - `BotsAssets.tsx`: added `startBot`/`stopBot` import + `handleStartBot`/`handleStopBot` handler functions
    - `stubs.py`: removed dead stub entries for already-real `/markets`, `/env`, `/system/restart` routes
- **Test count**: 207 passed (unchanged — T43 is pure frontend + stub Python, no new Python tests needed)
- **Completed**: 2026-03-11 | PR #75 + fix commit `101aa50`

---

### T37. Multi-Asset Bot Management API ✅ **COMPLETED 2026-03-10**
- [x] **Phase 7a: Bot entity model in Memgraph**
    - New node label: `:Bot {id (UUID), symbol, status, mode, active_strategy, regime, leverage, balance_allocated, timeframe, max_daily_loss_pct, stop_loss_mode, position_size_pct, created_at, updated_at}`
    - Status enum: `running | stopped | paused | error`
    - Mode enum: `auto | manual` (auto = bot picks strategy, manual = user locks one)
    - Relationships: `(:Bot)-[:HAS_POSITION]->(:Position)`, `(:Bot)-[:EXECUTED]->(:Trade)`, `(:Bot)-[:USES_STRATEGY]->(:Strategy)`
    - Indexes: `:Bot(id)`, `:Bot(symbol)`, `:Bot(status)`
    - Risk state per bot: `:State {key: "risk:{bot_id}:daily_stats"}`, etc.
- [x] **Phase 7b: Bot CRUD API endpoints** (`backend/src/api/routes/bots.py`)
    - `GET /api/bots` — list all bots with current state, position, daily PnL
    - `POST /api/bots` — create new bot (symbol, mode, strategy, leverage, allocation_pct, timeframe)
    - `GET /api/bots/{id}` — full detail: config, position, last 5 signals, risk metrics
    - `PUT /api/bots/{id}` — update config (mode, strategy, leverage, allocation)
    - `DELETE /api/bots/{id}` — remove bot (guards: stopped, no open position)
    - `POST /api/bots/{id}/start` / `stop` — lifecycle control
    - `POST /api/bots/{id}/trade/open` / `close` — manual trade control
    - All mutations require `verify_api_key`
    - `GET /api/status` — global stats: total bots, combined PnL, portfolio value
- [x] **Phase 7c: Bot lifecycle manager** (`backend/src/bot_manager.py`)
    - `BotManager` orchestrates multiple `OmniTrader` instances with independent `run_cycle()` loops
    - Shared exchange connection, rate limiter, Memgraph connection pool
    - WebSocket: multi-symbol via CCXT Pro `watchTicker()` / `watchOHLCV()`
    - Graceful shutdown with optional position close; `get_portfolio_summary()` aggregation
- [x] **Phase 7d: Per-bot risk isolation + global portfolio risk**
    - Independent daily loss tracker, consecutive loss counter, circuit breakers per bot
    - Global: max allocation ≤ 100%, portfolio drawdown >10% from HWM → pause all, max concurrent positions, correlation check
- [x] **Phase 7e: WebSocket per-bot updates**
    - Per-bot `cycle_update` messages keyed by `bot_id` with price, signal, regime, position, balance, daily PnL
    - New message types: `trade` (execution events), `alert` (circuit breakers, regime changes, strategy rotations)
- **Consolidates**: BACKLOG B6 (Portfolio Construction / Multi-Asset)
- **Completed**: 2026-03-10 | PR #70

---

### T38. Autonomous Strategy Selection Engine ✅ **COMPLETED 2026-03-10**
- [x] **Phase 8a: Strategy scoring model** (`backend/src/strategy/selector.py`)
    - `:StrategyScore {strategy_name, regime, sharpe_ratio, win_rate, profit_factor, sample_size, last_updated}` node per strategy-regime pair
    - Populated from backtest results (T35) and live trading history; minimum 20 trades for eligibility
    - Relationship: `(:Strategy)-[:SCORED_FOR {regime}]->(:StrategyScore)`
- [x] **Phase 8b: Selection algorithm** (`backend/src/strategies/selector.py`)
    - Composite score: `0.4 * normalized_sharpe + 0.3 * normalized_pf + 0.3 * normalized_wr`
    - Fallback to `adx_trend` if no eligible strategy; 4h cooldown between rotations
    - Regime change handling: close incompatible position → select new strategy → log rotation
- [x] **Phase 8c: Manual override per bot**
    - `PUT /api/bots/{id}` with `{mode: 'manual', active_strategy: '...'}` locks strategy regardless of regime
- [x] **Phase 8d: Strategy performance API**
    - `GET /api/strategies/performance` — all strategy scores grouped by regime (sharpe, win_rate, pf, samples)
- **Deferred**: regime-driven position-close choreography on rotation
- **Completed**: 2026-03-10 | PR #71

---

### T39. TA-Lib Migration & Indicator Service ✅ **COMPLETED 2026-03-10**
- [x] **Phase 9a: TA-Lib strategy migration** (all 5 strategies)
    - `adx_trend.py` → `talib.ADX()`, `talib.EMA()`; `bollinger_bands.py` → `talib.BBANDS()`, `talib.RSI()`
    - `breakout.py` → `talib.MAX()`, `talib.MIN()`; `ema_volume.py` → `talib.EMA()`, `talib.SMA()`; `z_score.py` → `talib.SMA()`, `talib.STDDEV()`
    - `backend/src/indicators.py` adapter with `_as_float64()` helper; `pandas-ta` removed
- [x] **Phase 9b: Indicator catalog API** (`backend/src/api/routes/indicators.py`)
    - `GET /api/indicators` — 158 TA-Lib functions in 9 categories, startup-cached
    - Uses `talib.get_function_groups()` + `talib.abstract.Function(name)` for introspection
- [x] **Phase 9c: Indicator computation endpoint**
    - `POST /api/indicators/compute` — fetches OHLCV, computes indicator, returns values
    - Rate limited: max 10 requests/minute; auth required
- **Completed**: 2026-03-09 (Phase 9a) + 2026-03-10 (9b/9c) | PR #72

---

### T40. Custom Strategy System (CRUD + Execution) ✅ **COMPLETED 2026-03-10**
- [x] **Phase 10a: Custom strategy data model**
    - `:CustomStrategy {name, description, regime_affinity, entry/exit condition JSON, indicators JSON, stop_loss_atr_mult, take_profit_atr_mult, min_bars_between_entries, created_at, updated_at}`
    - Condition schema: `[{indicator, operator, value}]`; Indicators schema: `[{function, params, output_name}]`
- [x] **Phase 10b: Custom strategy CRUD API** (`backend/src/api/routes/strategies.py`)
    - `GET /api/strategies` — combined built-in + custom list
    - `GET|POST|PUT|DELETE /api/strategies/{name}` — full CRUD with validation (unique name, valid TA-Lib functions, no circular refs)
    - Deletion blocked if strategy active on any bot
- [x] **Phase 10c: Custom strategy executor** (`backend/src/strategies/custom_executor.py`)
    - `CustomStrategyExecutor(BaseStrategy)`: loads config from Memgraph, computes TA-Lib indicators, evaluates AND-logic conditions
    - Operators: `>`, `<`, `>=`, `<=`, `crosses_above`, `crosses_below` (supports indicator-vs-indicator)
    - Hot reload: picks up updated config on next cycle
- [x] **Phase 10d: Integration with backtesting and auto-selection**
    - Same `BaseStrategy` interface — works transparently with `BacktestEngine` (T35) and `StrategySelector` (T38)
- **Completed**: 2026-03-10 | PR #73

---

### T41. Environment Variable Management API ✅ **COMPLETED 2026-03-10**
- [x] **Phase 11a: Env reader** (`backend/src/api/routes/env.py`)
    - `GET /api/env` — reads `.env`, groups by category (Binance, Database, Redis, Notifications, Security)
    - Masked fields: `BINANCE_API_KEY`, `BINANCE_SECRET`, `MEMGRAPH_PASSWORD`, `OMNITRADER_API_KEY`
    - Per-var: `{key, value, masked, category, description, requires_restart}`
- [x] **Phase 11b: Env updater**
    - `PUT /api/env` — auth required; validates port numbers, URL formats, required fields
    - Atomic write: `.env.tmp` → rename to `.env`
    - Audit log: `:Signal {type: 'env_change', key, changed_by}`
- [x] **Phase 11c: Service restart endpoint**
    - `POST /api/system/restart` — auth + `{confirm: true}`; runs `docker compose restart`
    - Returns immediately `{status: "restarting"}`; refuses if any bot has open position
- **Security**: `.env` never served raw; only defined variables exposed; values never logged
- **Completed**: 2026-03-10 | Commit `9fca480`

---

### T42. Markets Discovery API ✅ **COMPLETED 2026-03-10**
- [x] **Phase 12a: Markets endpoint** (`backend/src/api/routes/markets.py`)
    - `GET /api/markets` — all active Binance Futures perpetual pairs via CCXT `fetch_markets()`
    - Response: `{symbol, base, quote, min_size, tick_size, volume_24h, last_price, status}`
    - Redis cache: 5-minute TTL; sorted by `volume_24h` descending
- [x] **Phase 12b: Search and filter**
    - Query params: `?search=SOL&quote=USDT&min_volume=1000000`; max 100 results
    - Used by frontend "Add Bot" drawer searchable symbol picker
- **Completed**: 2026-03-10 | PR #74

---
