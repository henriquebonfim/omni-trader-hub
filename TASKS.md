# OmniTrader — Technical Debt & Architectural Backlog

This list tracks the structural weak points identified during the Production Readiness Audit. Transitioning from Paper Trading to Live Funds / Multi-Pair scaling requires addressing these items.

## 🔴 High Priority (Risk Mitigation)

### 1. Database Infrastructure Migration
- [/] **Migrate to High-Performance Database**
    - **Status**: ✅ **Implemented** (`src/database/postgres.py`). Ready for config switch.
    - **Risk Level**: 🔴 High
    - **Issue**: SQLite (single-file) lacks the concurrency needed for high-frequency writes and multi-pair scaling.
    - **Vulnerability**: Potential for database corruption during crashes or high-write volumes.
    - **Impact**: Loss of trade history and broken state reconciliation.
    - **Mitigation Path**:
        - **PostgreSQL**: ✅ **Coded**. Includes schema initialization and trade history persistence. Ready for production switch.

### 2. State Persistence Implementation
- [/] **Implement "Anti-Amnesia" Persistence Layer**
    - **Status**: ✅ **Implemented** (`src/database/redis_store.py`).
    - **Risk Level**: 🔴 High
    - **Issue**: Trailing stop levels, loss streaks, and daily PnL reset states currently reside partially in memory.
    - **Vulnerability**: Docker restarts or process crashes wipe critical trading state.
    - **Impact**: Bot may re-enter failed trades or ignore daily loss limits upon restart.
    - **Mitigation Path**: ✅ **Redis**: Store logic implemented. Linked via `DatabaseFactory`. Next step: Explicitly hook into `RiskManager` rolling state.

## 🟠 Medium Priority (Performance & Reliability)

### 3. Advanced Rate Limiting
- [x] **Implement Leaky-Bucket Rate Limiter**
    - **Status**: ✅ **Implemented** (`src/rate_limiter.py`, `tests/test_rate_limiter.py`). Wired into all CCXT call-sites in `src/exchange.py`.
    - **Risk Level**: 🟠 Medium
    - **Issue**: Current rate limiting relied on simple logic and `asyncio.sleep` after errors occur.
    - **Vulnerability**: In volatile markets, the bot may exceed exchange limits and face temporary IP bans.
    - **Impact**: Inability to exit positions during a crash.
    - **Mitigation Path**: ✅ **Proactive token-bucket limiter** intercepts all CCXT calls *before* transmission. Capacity=2000 weight units, refill at 40 units/s (Binance 2400/60s). Per-endpoint weight table. Thread-safe via asyncio.Lock. `Exchange.get_rate_limit_usage()` now returns bucket status.

### 4. Event Loop Optimization (Worker Offloading)
- [x] **Implement Celery + Redis Worker Architecture**
    - **Risk Level**: 🟠 Medium
    - **Issue**: FastAPI and the trading loop share a single-threaded event loop. Large Pandas/NumPy indicator calculations block heartbeats.
    - **Vulnerability**: Delayed API responses and missed price triggers.
    - **Impact**: Execution slippage and heartbeat timeouts.
    - **Mitigation Path**: ✅ **Celery worker offload** dispatches `analyze_strategy` + `analyze_regime` tasks to a separate worker process via asyncio-safe `dispatch()` (ThreadPoolExecutor bridge). Broker=Redis DB1, backend=Redis DB2. `compose.yml` adds `celery-worker` service. Local fallback if worker unavailable. 12 new tests. All 84 tests pass.

## 🟡 Low Priority (Execution Precision)

### 5. WebSocket Integration
- [x] **CCXT WebSocket Integration**
    - **Risk Level**: 🟡 Low to Medium
    - **Issue**: Current implementation relies on REST polling for order status and price updates.
    - **Vulnerability**: Potentially outdated market data and missed partial fill events during high volatility.
    - **Impact**: Inaccurate position sizing and slower execution.
    - **Mitigation Path**: ✅ **WsFeed module** (`src/ws_feed.py`) uses `ccxt.pro.binanceusdm` to stream `watch_ticker`, `watch_ohlcv`, and `watch_orders` as background asyncio tasks. OHLCV cache is pre-seeded via REST on first cycle then kept fresh via WS merges. `run_cycle()` prefers WS cache (avoids REST round-trips when warm); real-time price sourced from WS ticker. Order fills tracked via `watch_orders` (live mode). Paper/offline mode skips auth-required streams. 23 new tests. All 107 tests pass.
