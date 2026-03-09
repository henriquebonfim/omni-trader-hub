# OmniTrader — Technical Debt & Audit Findings

Single source of truth for all technical work: architecture items, audit-discovered bugs, and risk gaps.
Institutional-grade audit completed **2026-03-03** — findings integrated below.
Multi-asset autonomous platform expansion added **2026-03-09** — T37-T42 driven by frontend spec (PROMPT.md).

> Last updated: 2026-03-09 | Sprint promotion: T37-T42 added (Multi-Asset Platform)

---

## 🔴 Critical (Capital-at-Risk Bugs)

**Strategic Shift (2026-03-05)**: Replace PostgreSQL + planned Neo4j + QuestDB with unified **Memgraph** database. Single persistent store for trades, signals, equity, knowledge graph (news/assets/sectors), and candles. Redis drops to Celery-only. Data can be reset — clean slate.

### T32. Memgraph Infrastructure & Database Layer Rewrite
- [ ] **Phase 1a: Docker infrastructure**
    - Remove PostgreSQL service from compose.yml
    - Add Memgraph: `memgraph/memgraph-mage:3.8.0-relwithdebinfo`
    - Add Memgraph Lab: `memgraph/lab:latest` (port 3001 for visualization)
    - Uncomment Ollama service (GPU enabled)
    - Update healthchecks: Bolt ping for Memgraph, remove Postgres dependency
    - 8 services total (down from 9, no postgres)
- [ ] **Phase 1b: MemgraphDatabase implementation (~500 lines)**
    - Create `backend/src/database/memgraph.py` implementing all 18 `BaseDatabase` abstract methods
    - Use `neo4j` async Python driver (Bolt protocol, Memgraph-compatible)
    - Node labels: `:Trade`, `:DailySummary`, `:EquitySnapshot`, `:Signal`, `:FundingPayment`, `:Position`, `:State`
    - Properties mimic PostgreSQL columns exactly
    - Indexes: `:Trade(timestamp)`, `:Trade(symbol)`, `:Signal(timestamp)`, `:EquitySnapshot(timestamp)`, `:DailySummary(date)`, `:State(key)`, `:Position(symbol)`
    - ID generation: use Memgraph internal `id(node)` for RETURNING id behavior
    - Timestamp storage: epoch milliseconds for easy filtering
    - `save_daily_summary()`: use `MERGE (d:DailySummary {date: $date}) SET d += $props` for upsert
    - `get_weekly_pnl()`: `MATCH (t:Trade) WHERE t.action='CLOSE' AND t.timestamp >= $start RETURN sum(t.pnl)`
    - `backup_db()`: execute `DUMP DATABASE` via mgclient or Memgraph snapshot
- [ ] **Phase 1c: Risk state migration**
    - Move 5 Redis keys to Memgraph `:State` nodes:
        - `omnitrader:risk:daily_stats` → `:State {key: "risk:daily_stats", value: {...}}`
        - `omnitrader:risk:consecutive_losses` → `:State {key: "risk:consecutive_losses"}`
        - `omnitrader:risk:peak_equity` → `:State {key: "risk:peak_equity"}`
        - `omnitrader:risk:circuit_breaker` → `:State {key: "risk:circuit_breaker"}`
        - `omnitrader:risk:weekly_circuit_breaker` → `:State {key: "risk:weekly_circuit_breaker"}`
    - Update `RiskManager` ([risk.py](backend/src/risk.py)) to use `db.get_state()` / `db.set_state()`
    - Remove `RedisStore` dependency from `RiskManager.__init__`
    - TTL handling: `:State {expires_at: <timestamp>}` property + periodic cleanup query (`MATCH (s:State) WHERE s.expires_at < now() DELETE s`)
- [ ] **Phase 1d: Config, cleanup, dependencies**
    - Update [backend/config/config.yaml](backend/config/config.yaml): replace `database:` section with Memgraph connection
    - Remove from .env template: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
    - Delete: [postgres.py](backend/src/database/postgres.py), [sqlite.py](backend/src/database/sqlite.py), [redis_store.py](backend/src/database/redis_store.py), entire [alembic/](backend/alembic/) directory
    - Update [requirements.txt](backend/requirements.txt): remove `asyncpg`, `aiosqlite`, `alembic`; add `neo4j`
    - Update `DatabaseFactory` in [factory.py](backend/src/database/factory.py): default to `memgraph` type
- **Consolidates**: BACKLOG.md B1 (Backtesting data), B11 (QuestDB), B12 (Neo4j) | **Priority**: 🔴 CRITICAL
- **Effort**: ~2 days (code + testing)

### T33. News Ingestion & NLP Pipeline
- [ ] **Phase 2a: Extended graph schema**
    - Add node labels: `:Asset {symbol, name, sector, exchange, market_cap_tier}`, `:NewsEvent {id, title, source, published_at, sentiment_score, impact_level, raw_text}`, `:Sector {name}`, `:MacroIndicator {name, value, timestamp}`, `:Candle {symbol, timeframe, timestamp, open, high, low, close, volume}`
    - Relationships: `(:NewsEvent)-[:IMPACTS {magnitude}]->(:Asset)`, `(:NewsEvent)-[:MENTIONS]->(:Sector)`, `(:Asset)-[:BELONGS_TO]->(:Sector)`, `(:Asset)-[:CORRELATES_WITH {coefficient}]->(:Asset)`, `(:Trade)-[:TRIGGERED_BY]->(:Signal)` (new!)
    - Indexes: `:NewsEvent(published_at)`, `:Candle(symbol, timeframe, timestamp)`, `:MacroIndicator(name)`
    - Create indices in startup: `CREATE INDEX ON :NewsEvent(published_at)`, etc.
- [ ] **Phase 2b: News ingestor service** ([backend/src/graph/ingestor.py](backend/src/graph/ingestor.py))
    - CryptoPanic API polling (60s interval): `GET api/v1/posts/` → returns crypto news with `vote_count` (sentiment proxy)
    - Fear & Greed Index (300s interval): Alternative.me `/api/fear-and-greed` → store as `:MacroIndicator`
    - RSS feed parsing (300s interval): feedparser library for CoinDesk, CoinTelegraph, The Block
    - Deduplication: hash(url + title) before insert
    - Create `NewsEvent` nodes with extracted metadata
    - Create `IMPACTS` relationships to mentioned Asset nodes
    - Create `MENTIONS` relationships to Sector nodes
    - Use existing [rate_limiter.py](backend/src/rate_limiter.py) pattern for all API calls
    - TTL: prune old news nodes (7 days for individual `:NewsEvent`, 30 days for aggregated sentiment)
- [ ] **Phase 2c: Ollama NLP entity extraction** ([backend/src/graph/nlp.py](backend/src/graph/nlp.py))
    - POST news text to Ollama at `http://ollama:11434/api/generate` with structured extraction prompt
    - Prompt extracts: mentioned asset tickers, sectors, sentiment polarity (-1 to +1), impact magnitude (0 to 1)
    - Structured JSON schema: `{assets: ["BTC", "ETH"], sectors: ["L1", "DeFi"], sentiment: 0.7, impact: 0.85}`
    - Session-scoped `httpx.AsyncClient` (pooling pattern from [notifier.py](backend/src/notifier.py))
    - Graceful fallback: if Ollama timeout/error, use CryptoPanic's built-in sentiment (degraded mode)
    - Insert extracted data into graph relationships
- **Consolidates**: BACKLOG.md B4 (Macro Risk module), B13 (Ollama sidecar) | **Priority**: 🟠 HIGH
- **Effort**: ~2 days

### T34. Graph Analytics, Crisis Mode & Pipeline Integration
- [ ] **Phase 3a: Graph analytics queries** ([backend/src/graph/analytics.py](backend/src/graph/analytics.py))
    - Sentiment aggregation: `MATCH (n:NewsEvent)-[:IMPACTS]->(a:Asset {symbol: $sym}) WHERE n.published_at > $since RETURN avg(n.sentiment_score) as sentiment, count(n) as volume, max(n.impact_level) as max_impact`
    - Crisis detection: `MATCH (n:NewsEvent)-[:IMPACTS]->(a) WHERE n.published_at >= now() - duration('1h') AND n.impact_level > 0.7 AND n.sentiment_score < -0.5 RETURN count(n) as negative_impact_count` → flag if > 3
    - Sentiment-reality divergence: compare Fear & Greed index > 75 (Extreme Greed) + rolling news sentiment < -0.3 (Extreme Negative) → return `divergence_flag: true` with warning
    - Sector contagion: if news impacts Asset A, query for `:Asset`-[:`CORRELATES_WITH`]->() → Alert correlated assets
    - All queries return JSON-serializable results (strings, numbers, lists, dicts only — no objects)
- [ ] **Phase 3b: Celery task + concurrent dispatch**
    - New Celery task: `analyze_knowledge_graph(symbol: str, config_dict: dict) → Dict[str, Any]` in [backend/src/workers/tasks.py](backend/src/workers/tasks.py)
    - Returns: `{sentiment: float, impact: float, crisis_flag: bool, divergence_flag: bool, correlated_alerts: List[str]}`
    - Modify [backend/src/main.py](backend/src/main.py) `run_cycle()`: concat `dispatch()` to include 3rd task: `analyze_knowledge_graph`
    - After all 3 tasks return: apply graph-derived overrides before execution
- [ ] **Phase 3c: Crisis mode protocol** ([backend/src/graph/crisis.py](backend/src/graph/crisis.py))
    - Automatic activation: when `crisis_flag=True` from graph analytics
    - Manual toggle: `config.graph.crisis_mode` field + API endpoint `PUT /api/graph/crisis`
    - **Overrides when active**: leverage → 1.0× (from 3×), position_size_pct → 0.5% (from 2%), restrict strategy to `adx_trend` only, max_daily_loss_pct → 2% (from 5%)
    - State persisted in Memgraph `:State {key: "crisis_mode", value: {active: bool, triggered_by: str, activated_at: timestamp}}`
    - Survives restarts
    - Log activation/deactivation to `signals_log` table
- [ ] **Phase 3d: Signal gating using graph context**
    - In `_open_position()` before risk validation:
        - If `divergence_flag=True`: reduce confidence in signal by 50% (widen SL or higher entry threshold)
        - If `sentiment < -0.5` and signal is LONG: block entry
        - If `sentiment > 0.5` and signal is SHORT: block entry
        - Pass graph context dict to strategy result for logging
- [ ] **Phase 3e: API endpoints** ([backend/src/api/routes/graph.py](backend/src/api/routes/graph.py))
    - `GET /api/graph/sentiment/{symbol}`: return `{sentiment: float, volume: int, max_impact: float, recent_news: [...]}`
    - `GET /api/graph/crisis`: return `{active: bool, triggered_by: str, macro_indicators: {dxy, oil, fear_greed, btc_dominance}, latest_alert: str}`
    - `PUT /api/graph/crisis`: toggle manual crisis mode (require `verify_api_key`)
    - `GET /api/graph/news`: latest 20 news events with sentiment/impact scores
- [ ] **Phase 3f: Frontend components & WebSocket**
    - New components: `SentimentGauge.tsx` (emoji gauge -1 to +1), `NewsFeed.tsx` (scrollable with impact colors), `MacroPanel.tsx` (DXY, Oil, Fear & Greed cards, red/green arrows)
    - Update [frontend/src/lib/api.ts](frontend/src/lib/api.ts) with new endpoint types
    - Extend `CycleMessage` type: add `sentiment?: number`, `crisis_mode?: boolean`, `macro_indicators?: {...}`
    - Update [frontend/src/components/ConfigEditor.tsx](frontend/src/components/ConfigEditor.tsx): add crisis mode toggle
- **Fully absorbs**: BACKLOG.md B4 (Geopolitical Risk), previously-planned T30 | **Priority**: 🟠 HIGH
- **Effort**: ~3 days

### T35. Backtesting Engine on Memgraph (absorbs T29)
- [ ] **Phase 4a: Historical candle storage**
    - Bulk download from Binance REST API `/api/v3/klines`: handle pagination (1000 bars/call max), rate limiting
    - Store as `:Candle {symbol, timeframe, timestamp, open, high, low, close, volume}` nodes
    - Composite key: (symbol, timeframe, timestamp) — use Memgraph index
    - Query pattern: `MATCH (c:Candle {symbol: $sym, timeframe: $tf}) WHERE c.timestamp >= $start AND c.timestamp <= $end RETURN c ORDER BY c.timestamp`
    - Deduplication: skip inserts if node already exists
- [ ] **Phase 4b: Event-driven backtest simulator** ([backend/src/backtest/engine.py](backend/src/backtest/engine.py))
    - `BacktestEngine` class: iterates `:Candle` nodes chronologically
    - Reuse existing `BaseStrategy` interface — **zero changes to strategy code**
    - On each candle:
        1. Call `strategy.analyze(market_data, current_position, market_trend)` → `StrategyResult`
        2. Check SL/TP on current bar: if `bar.low <= sl_price` → exit at SL; if `bar.high >= tp_price` → exit at TP
        3. Risk validation: position sizing, margin checks
        4. Update position state, unrealized PnL
    - Cost model: 0.04% taker fee (assume all market orders), bid-ask spread (0.01% + ATR volatility adjustment), funding rate costs (8h intervals for perpetuals)
    - Store trades, signals, snapshots as Memgraph nodes during simulation
- [ ] **Phase 4c: Walk-forward validation + performance metrics** ([backend/src/backtest/metrics.py](backend/src/backtest/metrics.py))
    - Rolling train/test splits: train on 6 months, test on 1 month, roll forward
    - Separate in-sample vs out-of-sample tracking (detect overfitting)
    - Performance metrics: Sharpe ratio (annualized, assume 252 trading days), Sortino ratio, max drawdown, profit factor, win rate, avg win/loss, consecutive win/loss streaks
    - Bootstrap validation: resample trades 1000 times with replacement → confidence intervals on Sharpe, max DD, profit factor
    - Export outputs: JSON summary stats, CSV trade log, PNG equity curve + drawdown overlay, monthly returns heatmap
    - Comparison: backtest results vs paper trading results (sanity check)
- **Consolidates**: BACKLOG.md B1 (Backtesting Engine), B2 (Walk-Forward), B3 (Monte Carlo) | **Priority**: 🔴 CRITICAL (after T32-T34 stabilize)
- **Effort**: ~4 days
- **Acceptance criteria**:
    - Backtest on ADX Trend strategy over 2022 bear market completes in <30 seconds
    - Metrics pass institutional thresholds: Sharpe >1.0, max DD < 15%, profit factor > 1.5, win rate >40%
    - Paper mode results (after T7/T8 fixes) within 5% of backtest (slippage variance)
    - Walk-forward: no severe in-sample vs out-of-sample degradation
    - Bootstrap CIs don't include zero expectancy

### T36. Exchange Adapter Architecture — Decouple from CCXT
- [ ] **Phase 5a: Abstract exchange interface** ([backend/src/exchanges/base.py](backend/src/exchanges/base.py))
    - Create `BaseExchangeAdapter` abstract class with 18 core methods (match current `Exchange` API surface):
        - Connection: `connect()`, `close()`, `health_check()`
        - Market data: `fetch_ohlcv()`, `get_ticker()`, `get_mark_price()`
        - Account: `get_balance()`, `get_position()`, `get_open_positions()`, `fetch_open_orders()`
        - Trading: `market_long()`, `market_short()`, `close_position()`, `set_stop_loss()`, `set_take_profit()`, `cancel_order()`
        - Configuration: `set_leverage()`, `update_config()`
    - All methods return standardized DTOs (dataclasses): `TickerData`, `PositionData`, `BalanceData`, `OrderResult`
    - Paper trading simulation: move from CCXT wrapper to base adapter (`_paper_mode` flag → shared logic across all adapters)
    - Rate limiting: shared `LeakyBucketRateLimiter` instance per adapter
- [ ] **Phase 5b: CCXT adapter implementation** ([backend/src/exchanges/ccxt_adapter.py](backend/src/exchanges/ccxt_adapter.py))
    - `CCXTAdapter(BaseExchangeAdapter)` — wraps existing `ccxt.binance()` client
    - Move all current `Exchange` class code into this adapter (minimal refactor)
    - Translate CCXT responses to DTOs: `ccxt_ticker → TickerData`, `ccxt_position → PositionData`, etc.
    - Handle CCXT-specific exceptions → standardized `ExchangeError`, `RateLimitError`, `OrderRejectedError`
    - Dependency pinning: `ccxt>=4.0.0,<4.4.0` (avoid lighter-client bug)
    - Version warnings: log when using CCXT 4.3.x (explain stability choice)
- [ ] **Phase 5c: Binance Direct REST adapter** ([backend/src/exchanges/binance_direct.py](backend/src/exchanges/binance_direct.py))
    - `BinanceDirectAdapter(BaseExchangeAdapter)` — pure HTTP client using `httpx` or `aiohttp`
    - Binance Futures REST API v1: `POST /fapi/v1/order`, `GET /fapi/v2/balance`, `GET /fapi/v2/positionRisk`
    - Full control over:
        - Request signing: HMAC-SHA256 with timestamp + query string
        - Rate limiting: implement Binance weight-based tracking (1200/minute, 50/10s, order-specific weights)
        - Retry logic: exponential backoff on 429 errors, immediate fail on 4xx client errors
        - Error mapping: Binance error codes → standardized exceptions
    - No third-party dependencies except HTTP client
    - Handle WebSocket keepalive (listenKey for user data stream)
    - Add response schema validation: `pydantic` models for type safety
    - Implement order recvWindow validation (avoid timestamp rejections)
- [ ] **Phase 5d: Adapter factory + configuration** ([backend/src/exchanges/factory.py](backend/src/exchanges/factory.py))
    - `ExchangeFactory.create_adapter(adapter_type: str) → BaseExchangeAdapter`
    - Config options in [config.yaml](backend/config/config.yaml):
        ```yaml
        exchange:
          adapter: binance_direct  # or "ccxt"
          paper_mode: true
          fallback_enabled: true   # retry with CCXT on Binance direct failure
        ```
    - Fallback logic: if `binance_direct` fails 3× consecutively → switch to `ccxt_adapter` for session
    - Adapter health tracking: Redis metrics for success/error rates per adapter type
    - Startup validation: test adapter connection before OmniTrader initializes strategies
- [ ] **Phase 5e: Integration + testing updates**
    - Update `OmniTrader.__init__()` in [main.py](backend/src/main.py): replace `self.exchange = Exchange()` with `self.exchange = ExchangeFactory.create_adapter(config.exchange.adapter)`
    - Update all tests: replace `Exchange` mocks with `BaseExchangeAdapter` mocks
    - Create adapter-specific test suites:
        - `test_ccxt_adapter.py`: CCXT response parsing, error handling
        - `test_binance_direct.py`: signature generation, rate limit tracking, response validation
        - `test_adapter_factory.py`: fallback logic, health checks
    - Add integration test: run same strategy against both adapters → assert equivalent results
- **Risk Mitigation**: CCXT bugs (lighter-client, version lock, unmaintained exchanges) no longer block critical trading operations
- **Benefits**:
    - ✅ Full control over Binance API behavior (no CCXT black box)
    - ✅ Faster order execution (direct REST, no CCXT overhead)
    - ✅ Easier debugging (raw HTTP requests visible)
    - ✅ Future exchange support: add `bybit_direct.py`, `okx_direct.py` as needed
    - ✅ Graceful degradation: CCXT as fallback if direct adapter breaks
- **Priority**: 🟠 HIGH (before live capital deployment)
- **Effort**: ~3 days
- **Acceptance criteria**:
    - Both adapters pass all unit tests with identical mock responses
    - Paper mode parity: CCXT and Binance Direct produce same PnL/trades over 1000 bars
    - Binance Direct handles all Binance error codes gracefully (no unhandled exceptions)
    - Fallback mechanism works: simulated Binance Direct outage → automatic CCXT failover
    - Performance: Direct adapter 20-30% faster latency than CCXT (measure median order RTT)

---

## � Multi-Asset Autonomous Platform (Frontend-Driven Backend Requirements)

> **Context (2026-03-09)**: The frontend design spec (PROMPT.md) defines a multi-asset dashboard with 9 pages. These tasks represent the backend features needed to support that frontend. Each task is a backend API/service that the frontend will consume.

### T37. Multi-Asset Bot Management API
- [ ] **Phase 7a: Bot entity model in Memgraph**
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
- [ ] **Phase 8a: Strategy scoring model** ([backend/src/strategies/selector.py](backend/src/strategies/selector.py))
    - New node: `:StrategyScore {strategy_name, regime, sharpe_ratio, win_rate, profit_factor, sample_size, last_updated}`
    - One node per strategy-regime combination (e.g., "adx_trend + trending", "bollinger_bands + ranging")
    - Populated from:
        1. **Backtest results** (T35): run each strategy on historical data per regime period
        2. **Live trading history**: update scores as real trades complete
    - Minimum sample size: 20 trades before strategy eligible for auto-selection
    - Update frequency: recalculate after each completed trade or daily batch
    - Relationship: `(:Strategy)-[:SCORED_FOR {regime}]->(:StrategyScore)`
- [ ] **Phase 8b: Selection algorithm** ([backend/src/strategies/selector.py](backend/src/strategies/selector.py))
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
- [ ] **Phase 8c: Manual override per bot**
    - `PUT /api/bots/{id}` with `{mode: 'manual', active_strategy: 'bollinger_bands'}`
    - Ignores regime-based rotation; uses locked strategy regardless
    - Dashboard shows badge: "Auto 🤖" or "Manual 🔒"
- [ ] **Phase 8d: Strategy performance API**
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
- [ ] **Phase 9a: Replace pandas-ta with TA-Lib in all strategies**
    - `adx_trend.py`: `pandas_ta.adx()` → `talib.ADX(high, low, close, timeperiod=14)`, `talib.EMA(close, timeperiod=N)`
    - `bollinger_bands.py`: `pandas_ta.bbands()` → `talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2)`, `talib.RSI(close, timeperiod=14)`
    - `breakout.py`: manual Donchian → `talib.MAX(high, timeperiod=20)`, `talib.MIN(low, timeperiod=20)`
    - `ema_volume.py`: `pandas_ta.ema()` → `talib.EMA(close, timeperiod=N)`, `talib.SMA(volume, timeperiod=20)`
    - `z_score.py`: manual z-score → `talib.SMA(close, timeperiod=20)` + `talib.STDDEV(close, timeperiod=20)`
    - Conversion pattern: pandas Series → numpy array (`df['close'].values`) before passing to TA-Lib
    - Remove `pandas-ta` from `requirements.txt`; TA-Lib (`TA-Lib>=0.4.28`) already installed
    - Run full test suite: all strategy tests must pass with identical signal behavior
- [ ] **Phase 9b: Indicator catalog API** ([backend/src/api/routes/indicators.py](backend/src/api/routes/indicators.py))
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
- [ ] **Phase 9c: Indicator computation endpoint**
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

## �🟠 High Priority (Correctness & Reliability)

---

## 🟡 Medium Priority (Hardening & Hygiene)

---
