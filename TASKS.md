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
- [ ] **Implement Leaky-Bucket Rate Limiter**
    - **Risk Level**: 🟠 Medium
    - **Issue**: Current rate limiting relies on simple logic and `asyncio.sleep` after errors occur.
    - **Vulnerability**: In volatile markets, the bot may exceed exchange limits and face temporary IP bans.
    - **Impact**: Inability to exit positions during a crash.
    - **Mitigation Path**: Intercept all CCXT calls with a weight-aware rate limiter *before* transmission.

### 4. Event Loop Optimization (Worker Offloading)
- [ ] **Implement Celery + Redis Worker Architecture**
    - **Risk Level**: 🟠 Medium
    - **Issue**: FastAPI and the trading loop share a single-threaded event loop. Large Pandas/NumPy indicator calculations block heartbeats.
    - **Vulnerability**: Delayed API responses and missed price triggers.
    - **Impact**: Execution slippage and heartbeat timeouts.
    - **Mitigation Path**: Offload indicator calculations and heavy data processing to a **Celery** worker. Use existing **Redis** container as the message broker. This ensures the trading loop remains strictly for I/O and order management.

## 🟡 Low Priority (Execution Precision)

### 5. WebSocket Integration
- [ ] **CCXT WebSocket Integration**
    - **Risk Level**: 🟡 Low to Medium
    - **Issue**: Current implementation relies on REST polling for order status and price updates.
    - **Vulnerability**: Potentially outdated market data and missed partial fill events during high volatility.
    - **Impact**: Inaccurate position sizing and slower execution.
    - **Mitigation Path**: Implement `watch_ticker`, `watch_ohlcv`, and `watch_orders` using the unified CCXT async WebSocket API (formerly CCXT Pro). Since we already use `ccxt.async_support`, this involves enabling the `pro` features and refactoring the event loop targets.
