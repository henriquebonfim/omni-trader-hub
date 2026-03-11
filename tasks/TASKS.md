# OmniTrader — Technical Debt & Audit Findings

Single source of truth for all technical work: architecture items, audit-discovered bugs, and risk gaps.
Institutional-grade audit completed **2026-03-03** — findings integrated below.
Multi-asset autonomous platform expansion added **2026-03-09** — T37-T42 driven by frontend spec (PROMPT.md).
Last updated: 2026-03-11 | Sprint status: T32-T43 completed and merged to master. Next: TBD.
Frontend-backend integration migration added **2026-03-09** — T43 bridges new frontend to existing backend.

> Last updated: 2026-03-11 | Sprint status: T32-T43 completed and merged to master. Next: TBD

---

## 🔴 Critical (Capital-at-Risk Bugs)

**Strategic Shift (2026-03-05)**: Replace PostgreSQL + planned Neo4j + QuestDB with unified **Memgraph** database. Single persistent store for trades, signals, equity, knowledge graph (news/assets/sectors), and candles. Redis drops to Celery-only. Data can be reset — clean slate.

> **T32 COMPLETED**: ✅ All Phase 1 tasks complete (2026-03-09). See DONE.md for details. Memgraph infrastructure fully operational.
> **T33 COMPLETED**: ✅ News ingestion pipeline complete (2026-03-09). See DONE.md.
> **T34 COMPLETED**: ✅ Graph analytics, crisis mode, and pipeline integration complete (2026-03-09). See DONE.md.

> **T35 COMPLETED**: ✅ Backtesting engine complete (2026-03-09). See DONE.md.
> **T36 COMPLETED**: ✅ Exchange adapter architecture complete (2026-03-09). See DONE.md.

---

## Multi-Asset Autonomous Platform (Frontend-Driven Backend Requirements)

> **Context (2026-03-09)**: The frontend design spec (PROMPT.md) defines a multi-asset dashboard with 9 pages. These tasks represent the backend features needed to support that frontend. Each task is a backend API/service that the frontend will consume.

### T37. Multi-Asset Bot Management API
> **T37 COMPLETED**: ✅ Core bot management API, BotManager orchestrator, multi-bot CRUD/lifecycle, per-bot risk isolation, status aggregation (2026-03-10). See PR #70.
- [x] **Phase 7a: Bot entity model in Memgraph**
    - New node label: `:Bot {id (UUID), symbol, status, mode, active_strategy, regime, leverage, balance_allocated, timeframe, max_daily_loss_pct, stop_loss_mode, position_size_pct, created_at, updated_at}`
    - Status enum: `running | stopped | paused | error`
    - Mode enum: `auto | manual` (auto = bot picks strategy, manual = user locks one)
    - Relationships:
        - `(:Bot)-[:HAS_POSITION]->(:Position)` — current open position (0 or 1)
        - `(:Bot)-[:EXECUTED]->(:Trade)` — historical trades by this bot
        - `(:Bot)-[:USES_STRATEGY]->(:Strategy)` — currently active strategy
    - Indexes: `:Bot(id)`, `:Bot(symbol)`, `:Bot(status)`
    - Risk state per bot: `:State {key: "risk:{bot_id}:daily_stats"}`, `"risk:{bot_id}:consecutive_losses"`, etc.
- [ ] **Phase 7b: Bot CRUD API endpoints** ([backend/src/api/routes/bots.py](backend/src/api/routes/bots.py))
    - `GET /api/bots` — list all bots with current state, position, daily PnL
    - `POST /api/bots` — create new bot:
        ```json
        {
          "symbol": "ETH/USDT",
          "mode": "auto",
          "strategy": null,
          "leverage": 3,
          "allocation_pct": 20,
          "timeframe": "15m"
        }
        ```
    - `GET /api/bots/{id}` — full detail: config, position, last 5 signals, risk metrics
    - `PUT /api/bots/{id}` — update config (mode, strategy, leverage, allocation)
    - `DELETE /api/bots/{id}` — remove bot. Guards: must be stopped, no open position
    - `POST /api/bots/{id}/start` — start bot trading loop
    - `POST /api/bots/{id}/stop` — stop bot. Optional: `{close_position: true}`
    - `POST /api/bots/{id}/trade/open` — manual trade: `{side: "long", size_pct: 2.0}`
    - `POST /api/bots/{id}/trade/close` — manual close position
    - All mutations require `verify_api_key`
    - `GET /api/status` — updated to return global stats: total bots, combined PnL, portfolio value
- [ ] **Phase 7c: Bot lifecycle manager** ([backend/src/bot_manager.py](backend/src/bot_manager.py))
    - `BotManager` class: orchestrates multiple `OmniTrader` instances
    - Each bot runs its own `run_cycle()` loop with independent timing
    - Shared resources: exchange connection (with per-bot symbol), rate limiter (shared bucket), Memgraph connection pool
    - WebSocket: subscribe to multiple symbols simultaneously via CCXT Pro `watchTicker()` / `watchOHLCV()`
    - Graceful shutdown: stop all bots, close positions if configured, persist state
    - Status aggregation:
        ```python
        def get_portfolio_summary() -> dict:
            return {
                'total_value': sum(bot.balance for bot in bots),
                'active_bots': len([b for b in bots if b.status == 'running']),
                'open_positions': len([b for b in bots if b.position]),
                'combined_daily_pnl': sum(bot.daily_pnl for bot in bots),
            }
        ```
- [ ] **Phase 7d: Per-bot risk isolation + global portfolio risk**
    - Each bot has independent: daily loss tracker, consecutive loss counter, circuit breakers
    - Global portfolio-level risk:
        - Max total allocation: sum of all bot allocations ≤ 100%
        - Global drawdown circuit breaker: if combined portfolio drops > 10% from HWM → pause all bots
        - Max concurrent positions across all bots (configurable, default 5)
        - Correlation check: warn if adding highly correlated pair (BTC+ETH correlation ~0.85)
    - Position size validation: `bot.allocation_pct * total_capital * leverage` must not exceed exchange position limits
- [ ] **Phase 7e: WebSocket per-bot updates**
    - Modify WebSocket to send per-bot messages:
        ```json
        {
          "type": "cycle_update",
          "bot_id": "abc-123",
          "symbol": "ETH/USDT",
          "price": 3245.50,
          "signal": "HOLD",
          "active_strategy": "bollinger_bands",
          "regime": "ranging",
          "position": null,
          "balance": 3000,
          "daily_pnl": 12.50,
          "daily_pnl_pct": 0.42
        }
        ```
    - New message types: `trade` (execution events), `alert` (circuit breakers, regime changes, strategy rotations)
    - Frontend receives a stream of updates for all bots, keyed by `bot_id`
- **Consolidates**: BACKLOG B6 (Portfolio Construction / Multi-Asset)
- **Priority**: 🔴 CRITICAL | **Effort**: ~3 days
- **Depends on**: T32 (Memgraph), T36 (Exchange adapter for multi-symbol)
- **Acceptance criteria**:
    - Create 3 bots (BTC/USDT, ETH/USDT, SOL/USDT), start all simultaneously
    - Each bot trades independently with its own strategy and risk state
    - Stop one bot without affecting the other two
    - Portfolio summary correctly aggregates all bot PnLs
    - WebSocket sends distinct `cycle_update` per bot

### T38. Autonomous Strategy Selection Engine
> **T38 COMPLETED**: ✅ StrategySelector with composite scoring, eligibility gate, 4h cooldown, fallback; auto-mode integration with BotManager; manual override; GET /api/strategies/performance (2026-03-10). See PR #71. Deferred: regime-driven position-close choreography on rotation.
- [x] **Phase 8a: Strategy scoring model** ([backend/src/strategy/selector.py](backend/src/strategy/selector.py))
    - New node: `:StrategyScore {strategy_name, regime, sharpe_ratio, win_rate, profit_factor, sample_size, last_updated}`
    - One node per strategy-regime combination (e.g., "adx_trend + trending", "bollinger_bands + ranging")
    - Populated from:
        1. **Backtest results** (T35): run each strategy on historical data per regime period
        2. **Live trading history**: update scores as real trades complete
    - Minimum sample size: 20 trades before strategy eligible for auto-selection
    - Update frequency: recalculate after each completed trade or daily batch
    - Relationship: `(:Strategy)-[:SCORED_FOR {regime}]->(:StrategyScore)`
- [x] **Phase 8b: Selection algorithm** ([backend/src/strategies/selector.py](backend/src/strategies/selector.py))
    - `select_strategy(regime: str, available_strategies: List[str]) -> str`:
        1. Query all `:StrategyScore` nodes for given regime
        2. Filter: only strategies with `sample_size >= 20`
        3. Composite score: `0.4 * normalized_sharpe + 0.3 * normalized_pf + 0.3 * normalized_wr`
        4. Select highest score; break ties by larger sample size
        5. If no eligible strategy (all < 20 samples): fall back to `adx_trend` (safest default)
    - Integration point: called in `BotManager` before each cycle when `bot.mode == 'auto'`
    - **Regime change handling**:
        - When `analyze_regime()` returns a different regime than current:
            1. Close current position (if open and strategy incompatible with new regime)
            2. Select new best strategy for new regime
            3. Log rotation event
        - Cooldown: minimum 4 hours between strategy rotations (prevent churn)
- [x] **Phase 8c: Manual override per bot**
    - `PUT /api/bots/{id}` with `{mode: 'manual', active_strategy: 'bollinger_bands'}`
    - Ignores regime-based rotation; uses locked strategy regardless
    - Dashboard shows badge: "Auto 🤖" or "Manual 🔒"
- [x] **Phase 8d: Strategy performance API**
    - `GET /api/strategies/performance` — returns all strategy scores grouped by regime
    - Used by Strategy Lab's StrategyPerformanceComparison component
    - Response:
        ```json
        [
          {"strategy": "adx_trend", "regime": "trending", "sharpe": 1.8, "win_rate": 0.55, "pf": 2.1, "samples": 142},
          {"strategy": "bollinger_bands", "regime": "ranging", "sharpe": 1.2, "win_rate": 0.48, "pf": 1.6, "samples": 89}
        ]
        ```
- **Priority**: 🔴 CRITICAL | **Effort**: ~2 days
- **Depends on**: T35 (backtest data), T37 (bot model)
- **Acceptance criteria**:
    - Bot in auto mode runs ADX Trend during TRENDING regime
    - When regime flips to RANGING, bot auto-switches to Bollinger Bands (if scored higher)
    - Manual mode bot stays on locked strategy regardless of regime
    - Rotation events logged with reason

### T39. TA-Lib Migration & Indicator Service
> **Phase 9a COMPLETED**: ✅ All strategies migrated to TA-Lib (2026-03-09). See DONE.md for details.
> **T39 COMPLETED**: ✅ Indicator catalog (GET /api/indicators, startup-cached) and compute endpoint (POST /api/indicators/compute, 10 req/min rate-limited, auth required) implemented (2026-03-10). See PR #72.

- [x] **Phase 9b: Indicator catalog API** ([backend/src/api/routes/indicators.py](backend/src/api/routes/indicators.py))
    - `GET /api/indicators` — returns all TA-Lib functions grouped by category:
        ```json
        {
          "Overlap Studies": [
            {"name": "EMA", "display": "Exponential Moving Average", "inputs": ["close"], "params": [{"name": "timeperiod", "default": 30, "min": 2, "max": 500}], "outputs": ["real"]},
            {"name": "BBANDS", "display": "Bollinger Bands", "inputs": ["close"], "params": [{"name": "timeperiod", "default": 5}, {"name": "nbdevup", "default": 2}, {"name": "nbdevdn", "default": 2}], "outputs": ["upperband", "middleband", "lowerband"]}
          ],
          "Momentum Indicators": [...],
          ...
        }
        ```
    - Implementation: use `talib.get_function_groups()` + `talib.abstract.Function(name)` for introspection
    - Cache response (static data, recalculate only on startup)
- [x] **Phase 9c: Indicator computation endpoint**
    - `POST /api/indicators/compute`:
        ```json
        {"function": "RSI", "params": {"timeperiod": 14}, "symbol": "BTC/USDT", "timeframe": "1h", "bars": 100}
        ```
    - Fetches OHLCV from Memgraph candles (or exchange if not stored), computes indicator, returns values
    - Used by Strategy Editor for live indicator preview on chart
    - Rate limited: max 10 requests/minute (computation is moderately expensive)
- **Priority**: 🟠 HIGH | **Effort**: ~2 days
- **Acceptance criteria**:
    - All 5 strategies produce identical signals with TA-Lib vs old pandas-ta
    - `GET /api/indicators` returns 158 functions in 9 categories
    - Compute endpoint returns RSI values for BTC/USDT 1h candles

### T40. Custom Strategy System (CRUD + Execution)
> **T40 COMPLETED**: ✅ Custom strategy persistence, CRUD API, TA-Lib executor, and runtime integration delivered (2026-03-10). See PR #73.
- [x] **Phase 10a: Custom strategy data model**
    - New node: `:CustomStrategy {name (unique), description, regime_affinity, entry_long_json, entry_short_json, exit_long_json, exit_short_json, indicators_json, stop_loss_atr_mult, take_profit_atr_mult, min_bars_between_entries, created_at, updated_at}`
    - Condition JSON schema:
        ```json
        [
          {"indicator": "rsi_14", "operator": "<", "value": 30},
          {"indicator": "ema_9", "operator": "crosses_above", "value": "ema_21"}
        ]
        ```
    - Indicators JSON schema:
        ```json
        [
          {"function": "RSI", "params": {"timeperiod": 14}, "output_name": "rsi_14"},
          {"function": "EMA", "params": {"timeperiod": 9}, "output_name": "ema_9"},
          {"function": "EMA", "params": {"timeperiod": 21}, "output_name": "ema_21"}
        ]
        ```
    - Validation: all referenced indicators in conditions must exist in indicators array
- [x] **Phase 10b: Custom strategy CRUD API** ([backend/src/api/routes/strategies.py](backend/src/api/routes/strategies.py))
    - `GET /api/strategies` — returns combined list:
        - Built-in: `{name, type: "built-in", description, regime_affinity, editable: false}`
        - Custom: `{name, type: "custom", description, regime_affinity, conditions, indicators, editable: true}`
    - `GET /api/strategies/{name}` — full detail including parameters and conditions
    - `POST /api/strategies` — create custom strategy (auth required)
        - Validate: unique name, valid TA-Lib function names, valid operators, no circular refs
        - Store as `:CustomStrategy` node in Memgraph
    - `PUT /api/strategies/{name}` — update (auth, must be `type: custom`)
    - `DELETE /api/strategies/{name}` — delete (auth, must be `type: custom`, warn if active on any bot)
- [x] **Phase 10c: Custom strategy executor** ([backend/src/strategies/custom_executor.py](backend/src/strategies/custom_executor.py))
    - `CustomStrategyExecutor(BaseStrategy)`:
        - On init: load `:CustomStrategy` config from Memgraph
        - `analyze()`:
            1. Compute all indicators from OHLCV data using TA-Lib
            2. Evaluate entry_long conditions (AND logic by default)
            3. Evaluate entry_short conditions
            4. Evaluate exit conditions
            5. Return `StrategyResult(signal, reason, indicators_dict)`
        - Operator implementations:
            - `>`, `<`, `>=`, `<=`: simple numeric comparison
            - `crosses_above`: `prev_val < threshold AND curr_val >= threshold`
            - `crosses_below`: `prev_val > threshold AND curr_val <= threshold`
            - Value can be numeric or another indicator name (e.g., `ema_9 crosses_above ema_21`)
    - Register dynamically: on bot startup, if strategy is custom, instantiate `CustomStrategyExecutor` with that config
    - Hot reload: if strategy is updated via API while bot is running, reload on next cycle
- [x] **Phase 10d: Integration with backtesting and auto-selection**
    - Custom strategies work with `BacktestEngine` (T35) — no special handling needed (same `BaseStrategy` interface)
    - Auto-selection (T38) can include custom strategies if they have ≥20 backtest trades
    - Strategy Lab page shows backtest results per custom strategy
- **Priority**: 🟠 HIGH | **Effort**: ~3 days
- **Depends on**: T39 (TA-Lib), T32 (Memgraph for storage)
- **Acceptance criteria**:
    - Create custom strategy "RSI Bounce" via API: entry_long when RSI(14) < 30, exit_long when RSI(14) > 70
    - Deploy on a bot, run backtest → generates trades
    - Edit strategy parameters via API, bot picks up changes on next cycle
    - Delete strategy → fails if any bot is actively using it

### T41. Environment Variable Management API
> **T41 COMPLETED**: ✅ Env reader/updater API with masking + atomic writes, and restart endpoint with open-position safety checks (2026-03-10). Commit `9fca480`.
- [x] **Phase 11a: Env reader** ([backend/src/api/routes/env.py](backend/src/api/routes/env.py))
    - `GET /api/env` — read `.env` file from project root, parse key=value pairs
    - Group by category:
        - **Binance API**: `BINANCE_API_KEY`, `BINANCE_SECRET`
        - **Database**: `MEMGRAPH_HOST`, `MEMGRAPH_PORT`, `MEMGRAPH_USERNAME`, `MEMGRAPH_PASSWORD`
        - **Redis**: `REDIS_HOST`, `REDIS_PORT`
        - **Notifications**: `DISCORD_WEBHOOK_URL`
        - **Security**: `OMNITRADER_API_KEY`
    - Masked fields (secrets): `BINANCE_API_KEY`, `BINANCE_SECRET`, `MEMGRAPH_PASSWORD`, `OMNITRADER_API_KEY`
    - Response per var: `{key, value, masked, category, description, requires_restart}`
    - `requires_restart`: true for DB/Redis connection vars, false for webhook URL
- [x] **Phase 11b: Env updater**
    - `PUT /api/env` — update env vars (auth required)
    - Request body: `{variables: [{key: "DISCORD_WEBHOOK_URL", value: "https://..."}]}`
    - Validation:
        - Port numbers: must be valid int 1-65535
        - URLs: must be valid URL format
        - Required fields: BINANCE_API_KEY required if paper_mode is false
    - Write atomically: write `.env.tmp` → rename to `.env` (prevents corruption on crash)
    - Audit log: store change event as `:Signal {type: 'env_change', key: ..., changed_by: ...}`
    - Return: `{updated: ["DISCORD_WEBHOOK_URL"], requires_restart: false}`
- [x] **Phase 11c: Service restart endpoint**
    - `POST /api/system/restart` — requires auth + confirmation body `{confirm: true}`
    - Executes `docker compose restart` via subprocess (only restarts, not recreates)
    - Returns immediately with `{status: "restarting"}` — frontend shows progress
    - Safety: cannot restart if any bot has open position (must close first)
- **Priority**: 🟠 HIGH | **Effort**: ~1 day
- **Security**: `.env` file is never served raw. Only defined variables are exposed. Env values are never logged.
- **Acceptance criteria**:
    - GET returns grouped env vars with secrets masked
    - PUT updates .env file atomically
    - Changing REDIS_PORT shows "requires restart" warning
    - Restart endpoint refuses if positions are open

### T42. Markets Discovery API
> **T42 COMPLETED**: ✅ Markets discovery API with search/filter/Redis caching implemented (2026-03-10). See PR #74.
- [x] **Phase 12a: Markets endpoint** ([backend/src/api/routes/markets.py](backend/src/api/routes/markets.py))
    - `GET /api/markets` — fetch all active Binance Futures pairs
    - Source: `exchange.fetch_markets()` (CCXT) or `GET /fapi/v1/exchangeInfo` (direct)
    - Response:
        ```json
        [
          {"symbol": "BTC/USDT", "base": "BTC", "quote": "USDT", "min_size": 0.001, "tick_size": 0.1, "volume_24h": 1250000000, "last_price": 67500.0, "status": "active"},
          {"symbol": "ETH/USDT", "base": "ETH", "quote": "USDT", "min_size": 0.01, "tick_size": 0.01, "volume_24h": 890000000, "last_price": 3245.5, "status": "active"}
        ]
        ```
    - Filter: only `status: "active"` pairs, only perpetual contracts
    - Cache in Redis with 5-minute TTL (market info changes rarely)
    - Sort by `volume_24h` descending (most liquid first)
- [x] **Phase 12b: Search and filter**
    - Query params: `GET /api/markets?search=SOL&quote=USDT&min_volume=1000000`
    - Used by frontend "Add Bot" drawer: searchable symbol picker showing symbol + volume + price
    - Response limited to 100 results max
- **Priority**: 🟠 HIGH | **Effort**: ~1 day
- **Depends on**: T36 (exchange adapter)
- **Acceptance criteria**:
    - Returns all Binance Futures USDT perpetual pairs
    - Search for "SOL" returns SOL/USDT with correct volume and price
    - Cached: second call completes in <10ms

---
## 🔵 Frontend Integration Bridge

> **Context (2026-03-09)**: The new React frontend (10 pages, full API client, WebSocket client) was previously using mock data on every page. T43 connected the frontend to the existing backend using adapter + stub layers so unimplemented features degrade gracefully. See DONE.md for the full T43 audit trail.

> **T43 COMPLETED**: ✅ Moved to DONE.md (2026-03-11). All 7 phases verified. See PR #75 + commit `101aa50`.

> **T44 COMPLETED**: ✅ Backend DDD migration complete (2026-03-09). See DONE.md.

---
## 🟠 High Priority (Correctness & Reliability)

---

## 🟡 Medium Priority (Hardening & Hygiene)

---
