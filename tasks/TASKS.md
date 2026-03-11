# OmniTrader — Technical Debt & Audit Findings

Single source of truth for all technical work: architecture items, audit-discovered bugs, and risk gaps.
Institutional-grade audit completed **2026-03-03** — findings integrated below.
Multi-asset autonomous platform expansion added **2026-03-09** — T37-T42 driven by frontend spec (PROMPT.md).
Last updated: 2026-03-10 | Sprint status: T32-T39 completed and merged to master. Next: T40-T42.
Frontend-backend integration migration added **2026-03-09** — T43 bridges new frontend to existing backend.

> Last updated: 2026-03-10 | Sprint status: T32-T38 completed and merged to master. Next: T39-T42 (TA-Lib Indicators, Custom Strategies, Frontend Integration)

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
- [ ] **Phase 10a: Custom strategy data model**
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
- [ ] **Phase 10b: Custom strategy CRUD API** ([backend/src/api/routes/strategies.py](backend/src/api/routes/strategies.py))
    - `GET /api/strategies` — returns combined list:
        - Built-in: `{name, type: "built-in", description, regime_affinity, editable: false}`
        - Custom: `{name, type: "custom", description, regime_affinity, conditions, indicators, editable: true}`
    - `GET /api/strategies/{name}` — full detail including parameters and conditions
    - `POST /api/strategies` — create custom strategy (auth required)
        - Validate: unique name, valid TA-Lib function names, valid operators, no circular refs
        - Store as `:CustomStrategy` node in Memgraph
    - `PUT /api/strategies/{name}` — update (auth, must be `type: custom`)
    - `DELETE /api/strategies/{name}` — delete (auth, must be `type: custom`, warn if active on any bot)
- [ ] **Phase 10c: Custom strategy executor** ([backend/src/strategies/custom_executor.py](backend/src/strategies/custom_executor.py))
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
- [ ] **Phase 10d: Integration with backtesting and auto-selection**
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
- [ ] **Phase 11a: Env reader** ([backend/src/api/routes/env.py](backend/src/api/routes/env.py))
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
- [ ] **Phase 11b: Env updater**
    - `PUT /api/env` — update env vars (auth required)
    - Request body: `{variables: [{key: "DISCORD_WEBHOOK_URL", value: "https://..."}]}`
    - Validation:
        - Port numbers: must be valid int 1-65535
        - URLs: must be valid URL format
        - Required fields: BINANCE_API_KEY required if paper_mode is false
    - Write atomically: write `.env.tmp` → rename to `.env` (prevents corruption on crash)
    - Audit log: store change event as `:Signal {type: 'env_change', key: ..., changed_by: ...}`
    - Return: `{updated: ["DISCORD_WEBHOOK_URL"], requires_restart: false}`
- [ ] **Phase 11c: Service restart endpoint**
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
- [ ] **Phase 12a: Markets endpoint** ([backend/src/api/routes/markets.py](backend/src/api/routes/markets.py))
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
- [ ] **Phase 12b: Search and filter**
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

> **Context (2026-03-09)**: The new React frontend (10 pages, full API client, WebSocket client) has zero actual backend integration — every page uses mock data. T43 connects the frontend to the existing backend now, using adapter + stub layers so unimplemented features (T33-T42) degrade gracefully instead of crashing. As each backend task completes, its corresponding frontend stub is replaced with real data.

### T43. Frontend-Backend Integration Migration
- [ ] **Phase 13a: Infrastructure — Vite proxy + Nginx upstream + auth**
    - Add dev proxy to [frontend/vite.config.ts](frontend/vite.config.ts): `/api/*` → `http://localhost:8000`, `/ws` → `ws://localhost:8000/ws/live`
    - Update [frontend/nginx.conf](frontend/nginx.conf): add `upstream backend` block and `proxy_pass` for `/api/` and `/ws` (production)
    - Add auth token injection to [frontend/src/lib/api.ts](frontend/src/lib/api.ts): `Authorization: Bearer <token>` header in `request()`, sourced from `VITE_API_KEY` env var
- [ ] **Phase 13b: Adapter layer — backend shapes → frontend types**
    - Create [frontend/src/lib/adapters.ts](frontend/src/lib/adapters.ts) (~200 lines)
    - `adaptBotState(backendStatus, backendPosition, backendBalance) → Bot` — maps single-bot `/api/bot/state` + `/api/position` + `/api/balance` responses to frontend `Bot` type
    - `adaptTrade(backendTrade) → Trade` — field renames (`id` string→number, `timestamp` ISO→epoch, add missing `bot_id`, `notional`, `fee`)
    - `adaptEquitySnapshot(backendSnapshot) → EquitySnapshot` — `{timestamp, balance}` → `{timestamp, equity}`
    - `adaptStrategy(backendStrategy) → Strategy` — map `{name, active, metadata}` → full `Strategy` type with defaults for missing fields
    - `adaptConfig(backendConfig) → AppConfig` — flatten nested backend config (`exchange.leverage`, `risk.stop_loss_pct`, `notifications.discord_webhook`) into flat frontend `AppConfig`
    - `reverseAdaptConfig(appConfig) → ConfigUpdate` — reverse: flat frontend → nested backend `ConfigUpdate` schema
    - `adaptWsMessage(backendMsg) → CycleMessage` — map `current_price`→`price`, `market_regime`→`regime`, `circuit_breaker_active`→`circuit_breaker`, inject `bot_id` for first bot
- [ ] **Phase 13c: Stub layer — typed fallbacks for unimplemented endpoints**
    - Create [frontend/src/lib/stubs.ts](frontend/src/lib/stubs.ts) (~150 lines)
    - Each stub annotated with future task ID: `// STUB: replaced by T{N}`
    - `stubBots() → Bot[]` — returns mock bots from `mock-data.ts`, first bot enriched with real data at call site
    - `stubSentiment() → SentimentData` — `{score: 0, label: "Neutral", article_count: 0, max_impact: 0}` (→ T33/T34)
    - `stubCrisis() → CrisisStatus` — `{active: false, source: "auto"}` (→ T34)
    - `stubNews() → NewsItem[]` — empty array (→ T33)
    - `stubBacktestResults() → BacktestResults` — mock results from `mock-data.ts` (→ T35)
    - `stubMarkets() → MarketPair[]` — hardcoded top-20 pairs with approximate volumes (→ T42)
    - `stubEnvVars() → EnvVariable[]` — mock env vars from `mock-data.ts` (→ T41)
- [ ] **Phase 13d: API client rewiring — try/real → catch/stub**
    - Rewire all functions in [frontend/src/lib/api.ts](frontend/src/lib/api.ts):
    - **Real endpoints** (backend exists now):
        - `fetchBots()` → call `GET /api/bot/state` + `/api/position` + `/api/balance`, adapt to `Bot[]` (single bot as first item, rest from stubs)
        - `startBot(id)` / `stopBot(id)` → proxy first bot to `POST /api/bot/start|stop`, others no-op
        - `fetchStrategies()` → `GET /api/strategies` + `adaptStrategy()`
        - `fetchTradeHistory()` → `GET /api/trades?limit=50` + `adaptTrade()`
        - `fetchEquitySnapshots()` → `GET /api/equity?limit=200` + `adaptEquitySnapshot()`
        - `fetchConfig()` / `updateConfig()` → `GET|PUT /api/config` + bidirectional adapter
    - **Stubbed endpoints** (backend not yet built):
        - `createBot()` / `updateBot()` / `deleteBot()` → stub no-op, return mock (→ T37)
        - `createStrategy()` / `updateStrategy()` / `deleteStrategy()` → stub (→ T40)
        - `fetchSentiment()` / `fetchCrisis()` / `updateCrisis()` / `fetchNews()` → stub (→ T33/T34)
        - `runBacktest()` / `fetchBacktestResults()` → stub (→ T35)
        - `fetchMarkets()` → stub (→ T42)
        - `fetchEnvVars()` / `updateEnvVars()` → stub (→ T41)
- [ ] **Phase 13e: WebSocket integration**
    - Update [frontend/src/lib/ws.ts](frontend/src/lib/ws.ts): connect via proxy `ws://${location.host}/ws`
    - Adapt incoming messages using `adaptWsMessage()`: backend sends flat cycle JSON → frontend `CycleMessage`
    - Field mapping: `current_price`→`price`, `market_regime`→`regime`, `circuit_breaker_active`→`circuit_breaker`, `balance`→`balance_allocated`
    - Only handle cycle messages (backend has no `alert` or `trade` WS types yet)
    - Keep existing auto-reconnect with exponential backoff
- [ ] **Phase 13f: Page-by-page wiring (all pages)**
    - **Dashboard.tsx**: TanStack Query hooks for `fetchBots()`, `fetchTradeHistory()`, `fetchEquitySnapshots()`. Live data from WS store. Alerts: mock fallback
    - **BotsAssets.tsx**: wire start/stop buttons to `startBot()`/`stopBot()`. CRUD drawers use stub mutations
    - **Charts.tsx**: replace procedurally-generated candles with `GET /api/candles/?timeframe=X`. Symbol selector from real bot symbols
    - **TradeHistory.tsx**: replace `mockTrades` with `fetchTradeHistory()`. Client-side sort/pagination unchanged
    - **Settings.tsx**: two-way config binding via `fetchConfig()`/`updateConfig()` adapters (General/Risk/Notifications tabs). Env + System tabs: stub
    - **StrategyLab.tsx**: real strategy list via `fetchStrategies()`. Custom CRUD: stub
    - **RiskMonitor.tsx**: derive from `fetchBots()` (which calls `/api/bot/state` + `/api/position`). Circuit breakers: derive from bot state. Rest: stub
    - **Intelligence.tsx**: all stub — sentiment gauge, crisis toggle, news feed, macro indicators
    - **Backtesting.tsx**: all stub — config form, metrics display, equity chart, monthly returns
    - **Topbar.tsx + AppSidebar.tsx**: already wired to Zustand store; live once WS connects (Phase 13e). Alerts: mock fallback
- [ ] **Phase 13g: Backend stub routes (recommended)**
    - Create [backend/src/api/routes/stubs.py](backend/src/api/routes/stubs.py) — placeholder endpoints returning `501 Not Implemented` with JSON bodies:
        - `GET /api/bots` → `[{single bot from current /api/bot/state}]`
        - `POST/PUT/DELETE /api/bots/*` → 501 `{"error": "Not implemented", "task": "T37"}`
        - `GET /api/graph/*` → neutral/empty stubs with task references
        - `POST /api/backtest/*` → 501 `{"error": "Not implemented", "task": "T35"}`
        - `GET /api/markets` → hardcoded top-20 USDT perps
        - `GET/PUT /api/env` → 501 `{"error": "Not implemented", "task": "T41"}`
    - Register in [backend/src/api/__init__.py](backend/src/api/__init__.py)
    - This gives frontend clean 501s instead of ambiguous 404s — stubs annotated with which task replaces them
- **Files created**: `frontend/src/lib/adapters.ts`, `frontend/src/lib/stubs.ts`, `backend/src/api/routes/stubs.py`
- **Files modified**: `frontend/vite.config.ts`, `frontend/nginx.conf`, `frontend/src/lib/api.ts`, `frontend/src/lib/ws.ts`, all 9 pages, `frontend/src/components/layout/Topbar.tsx`, `frontend/src/components/layout/AppSidebar.tsx`, `backend/src/api/__init__.py`
- **Stub replacement map**:
    | Stub | Replaced by | Backend Task |
    |------|-------------|-------------|
    | `stubBots()` | Real multi-bot API | T37 |
    | `stubSentiment()` / `stubCrisis()` / `stubNews()` | Graph analytics API | T33/T34 |
    | `stubBacktestResults()` | Backtesting engine API | T35 |
    | `stubMarkets()` | Markets discovery API | T42 |
    | `stubEnvVars()` | Env management API | T41 |
    | Strategy CRUD stubs | Custom strategy API | T40 |
- **Priority**: 🔴 CRITICAL (unblocks frontend usability) | **Effort**: ~2 days
- **Depends on**: T32 (Memgraph — ✅ done)
- **Enables**: All future backend tasks (T33-T42) to be visible in frontend as stubs are progressively replaced
- **Acceptance criteria**:
    - Dashboard shows real balance/position/PnL from backend (not mock)
    - Topbar WS status shows "connected" when backend is running
    - Charts render real Binance candles for selected timeframe
    - Trade history shows actual trades from backend
    - Settings round-trip: change leverage → persists across reload
    - Bot start/stop buttons control the real backend bot
    - Stubbed pages (Intelligence, Backtesting, Env) render with placeholder data, no console errors
    - `Authorization: Bearer` header sent on protected endpoints
    - `make test` frontend profile: no regressions

> **T44 COMPLETED**: ✅ Backend DDD migration complete (2026-03-09). See DONE.md.

---
## 🟠 High Priority (Correctness & Reliability)

---

## 🟡 Medium Priority (Hardening & Hygiene)

---
