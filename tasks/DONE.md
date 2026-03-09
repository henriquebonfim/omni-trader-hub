
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
