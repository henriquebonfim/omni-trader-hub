# OmniTrader — Technical Debt & Architectural Backlog

This list tracks the structural weak points identified during the Production Readiness Audit. Transitioning from Paper Trading to Live Funds / Multi-Pair scaling requires addressing these items.

## 🔴 High Priority (Risk Mitigation)

### 1. Database Infrastructure Migration
- [x] **Migrate to High-Performance Database**
    - **Risk Level**: 🔴 High
    - **Issue**: SQLite (single-file) lacks the concurrency needed for high-frequency writes and multi-pair scaling.
    - **Vulnerability**: Potential for database corruption during crashes or high-write volumes.
    - **Impact**: Loss of trade history and broken state reconciliation.
    - **Mitigation Path**:
        - **PostgreSQL**: For relational trade history and user metadata.
        - **QuestDB**: Specialized time-series database for OHLCV, order book snapshots, and trade ticks. *Recommended for performance scaling.*

### 2. State Persistence Implementation
- [x] **Implement "Anti-Amnesia" Persistence Layer**
    - **Risk Level**: 🔴 High
    - **Issue**: Trailing stop levels, loss streaks, and daily PnL reset states currently reside partially in memory.
    - **Vulnerability**: Docker restarts or process crashes wipe critical trading state.
    - **Impact**: Bot may re-enter failed trades or ignore daily loss limits upon restart.
    - **Mitigation Path**: Persist rolling state indicators to a fast caching layer (Redis) or strictly enforce DB state syncing on every cycle.

## 🟠 Medium Priority (Performance & Reliability)

### 3. Advanced Rate Limiting
- [ ] **Implement Leaky-Bucket Rate Limiter**
    - **Risk Level**: 🟠 Medium
    - **Issue**: Current rate limiting relies on simple logic and `asyncio.sleep` after errors occur.
    - **Vulnerability**: In volatile markets, the bot may exceed exchange limits and face temporary IP bans.
    - **Impact**: Inability to exit positions during a crash.
    - **Mitigation Path**: Intercept all CCXT calls with a weight-aware rate limiter *before* transmission.

### 4. Event Loop Optimization
- [ ] **Offload Heavy Calculations**
    - **Risk Level**: 🟠 Medium
    - **Issue**: FastAPI and the trading loop share a single-threaded event loop.
    - **Vulnerability**: Large Pandas/NumPy indicator calculations can block the heartbeats.
    - **Impact**: Delayed API responses and missed price triggers.
    - **Mitigation Path**: Use `ProcessPoolExecutor` for indicator processing or offload to a dedicated worker.

## 🟡 Low Priority (Execution Precision)

### 5. WebSocket Integration
- [ ] **CCXT Pro (WebSockets) Migration**
    - **Risk Level**: 🟡 Low to Medium
    - **Issue**: Relies on REST polling for order status and price updates.
    - **Vulnerability**: Potentially outdated market data and missed partial fill events.
    - **Impact**: Inaccurate position sizing and slower execution.
    - **Mitigation Path**: Integrate CCXT Pro for real-time market data and user data streams.
