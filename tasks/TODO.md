# TODO

Confirmed work for the current and next sprints. All items validated, scoped, and ready to implement.
Unified Memgraph Architecture → Multi-Asset Autonomous Trading Platform.

> Last updated: 2026-03-09 | Sprint: Unified Memgraph Architecture (T32-T36) + Frontend Integration (T43) + Multi-Asset Platform (T37-T42)

---

## Local Triage (No Open GitHub Issues) - 2026-03-11

Items kept in next-sprint queue after promoting T45-T47 to `TASKS.md`.

- [ ] **T48. Alert and Notification Center (B19 Promotion)**
    Scope: In-app notification stream plus configurable backend alert rules (circuit breaker, strategy rotation, regime change, PnL thresholds).
    Acceptance: WebSocket-driven frontend notification queue with configurable rule persistence.

- [ ] **T49. Correlation Matrix Analytics API + Dashboard (B17 Promotion)**
    Scope: Add rolling correlation matrix endpoint and render heatmap in risk/intelligence surfaces.
    Acceptance: API returns NxN matrix for active bot symbols; frontend displays interpretable heatmap.

---

> **⚠️ STRATEGIC PIVOT (2026-03-05)**: Memgraph as single source of truth. PostgreSQL + Redis + Alembic → Memgraph + Redis (Celery-only). Data reset OK.

> **🚀 PLATFORM EXPANSION (2026-03-09)**: Evolving from single-pair BTC/USDT bot to **multi-asset autonomous trading platform**. Bots run per-asset, auto-select strategies via regime + backtest performance, and support custom user-created strategies built from 158 TA-Lib indicators. Frontend design spec (PROMPT.md) drives these new backend requirements (T37-T42).

## Sprint: Unified Memgraph Architecture — Graph Intelligence Foundation

**Goal**: Consolidate all persistent storage into Memgraph graph database. Enable knowledge graph layer for news sentiment + crisis detection. Enable backtesting with historical candle data. Foundation for LFT/MFT bot intelligence.

**Phase breakdown:**
- **T32 (2 days)**: Infrastructure + database layer rewrite
- **T33 (2 days)**: News ingestor + Ollama NLP
- **T34 (3 days)**: Graph analytics + trading pipeline integration
- **T35 (4 days)**: Backtesting engine (post-stabilization)

### 1. Memgraph Infrastructure & Database Layer (T32) 🔴 CRITICAL
- [ ] **Phase 1a: Docker infrastructure**
    - Remove PostgreSQL service from compose.yml (delete `postgres` block, `postgres_data` volume)
    - Add Memgraph service with `memgraph/memgraph-mage:3.8.0-relwithdebinfo` (CPU mode, port 7687)
    - Add Memgraph Lab visualization: `memgraph/lab:latest` (port 3001)
    - Uncomment Ollama service (GPU-enabled, port 11434)
    - Remove `postgres` from service dependencies in `omnitrader` service
    - Add Memgraph Bolt health check: `["CMD", "timeout", "5", "cypher-shell", "-a", "bolt://memgraph:7687", "RETURN 1"]`
    - Result: 8 services (omnitrader, celery-worker, watchdog, frontend, frontend-test, memgraph, memgraph-lab, ollama)
    - **Verify**: `docker compose config | grep -E '^  [a-z]' | wc -l` = 8
- [ ] **Phase 1b: MemgraphDatabase implementation**
    - Create [backend/src/database/memgraph.py](backend/src/database/memgraph.py) (~500 lines)
    - Implement `MemgraphDatabase` class extending `BaseDatabase` abstract interface
    - All 18 abstract methods → Cypher queries using `neo4j` async Python driver
    - Node labels with properties:
        - `:Trade {timestamp, symbol, side, action, price, expected_price, slippage, size, notional, fee, fee_currency, pnl, pnl_pct, reason, stop_loss, take_profit}`
        - `:DailySummary {date (unique), starting_balance, ending_balance, pnl, pnl_pct, trades_count, wins, losses}`
        - `:EquitySnapshot {timestamp, balance}`
        - `:Signal {timestamp, symbol, price, signal, regime, reason, indicators}`
        - `:FundingPayment {timestamp, symbol, rate, payment, position_size}`
        - `:Position {symbol, side, size, entry_price, unrealized_pnl, created_at, updated_at}`
        - `:State {key (unique), value (map/JSON), updated_at}`
    - Index creation on startup:
        ```cypher
        CREATE INDEX ON :Trade(timestamp);
        CREATE INDEX ON :Trade(symbol);
        CREATE INDEX ON :Signal(timestamp);
        CREATE INDEX ON :EquitySnapshot(timestamp);
        CREATE INDEX ON :DailySummary(date);
        CREATE INDEX ON :State(key);
        CREATE INDEX ON :Position(symbol);
        ```
    - ID handling: use internal `id(node)` for return values from `log_trade_open` / `log_trade_close`
    - Timestamp storage: milliseconds since epoch (for easy range queries)
    - Methods (in order of call frequency):
        1. `log_equity_snapshot()` — `CREATE (:EquitySnapshot {timestamp: now(), balance: $bal})`
        2. `log_signal()` — `CREATE (:Signal {timestamp: now(), symbol: $sym, signal: $sig, indicators: $ind})`
        3. `log_trade_open()` — `CREATE (:Trade {timestamp: now(), ...}) RETURN id(n)`
        4. `log_trade_close()` — `CREATE (:Trade {action: 'CLOSE', ...}) RETURN id(n)`
        5. `get_last_trade()` — `MATCH (t:Trade {symbol: $sym}) RETURN t ORDER BY t.timestamp DESC LIMIT 1`
        6. `get_open_trade_fee()` — `MATCH (t:Trade {symbol: $sym, action: 'OPEN'}) ... RETURN t.fee`
        7. `save_daily_summary()` — `MERGE (d:DailySummary {date: $date}) SET d += $props`
        8. `get_daily_summary()` — `MATCH (d:DailySummary {date: $date}) RETURN d`
        9. `get_recent_trades()` — `MATCH (t:Trade) RETURN t ORDER BY t.timestamp DESC LIMIT $limit`
        10. `get_weekly_pnl()` — `MATCH (t:Trade {action: 'CLOSE'}) WHERE t.timestamp >= $start RETURN sum(t.pnl)`
        11. `save_state()`/`get_state()` — `MERGE (:State {key: $k}) SET ... / MATCH ... RETURN`
        12. TTL cleanup: daily task deletes expired `:State` nodes
- [ ] **Phase 1c: Risk state migration**
    - Remove Redis DB0 persistence; move to Memgraph `:State` nodes
    - Keys → nodes:
        - `risk:daily_stats` → `:State {key: "risk:daily_stats", value: <JSON>, expires_at: now + 86400s}`
        - `risk:consecutive_losses` → `:State {key: "consecutive_losses", value: <int>}`
        - `risk:peak_equity` → `:State {key: "peak_equity", value: <float>}`
        - `risk:circuit_breaker` → `:State {key: "circuit_breaker", value: <bool>}`
        - `risk:weekly_circuit_breaker` → `:State {key: "weekly_circuit_breaker", value: <bool>}`
    - Update [backend/src/risk.py](backend/src/risk.py) `RiskManager.__init__`: remove `self.redis = redis_store` parameter
    - Replace all `self.redis.set()` / `self.redis.get()` calls with `self.database.set_state()` / `self.database.get_state()`
    - TTL: add `expires_at` property to `:State` nodes that need TTL (daily_stats); implement cleanup query
    - **Test**: `pytest backend/tests/test_risk.py` — all assertions pass with new Memgraph-backed state
- [ ] **Phase 1d: Config, dependencies, cleanup**
    - Update [backend/config/config.yaml](backend/config/config.yaml):
        ```yaml
        database:
          type: memgraph
          host: ${MEMGRAPH_HOST:-memgraph}
          port: ${MEMGRAPH_PORT:-7687}
          encrypted: false
          username: null
          password: null
        redis:
          host: ${REDIS_HOST:-redis}
          port: ${REDIS_PORT:-6379}
          db: 1  # Celery broker only
        ```
    - Remove from .env template: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`
    - Delete files:
        - `backend/src/database/postgres.py`
        - `backend/src/database/sqlite.py`
        - `backend/src/database/redis_store.py`
        - `backend/alembic/` directory
        - `backend/alembic.ini`
    - Update [backend/requirements.txt](backend/requirements.txt):
        - Remove: `asyncpg`, `aiosqlite`, `alembic`
        - Add: `neo4j>=5.18`
    - Update [backend/src/database/factory.py](backend/src/database/factory.py):
        - Change default from `postgres` to `memgraph`
        - Remove `postgres` and `sqlite` branches if not needed
    - Update [backend/src/database/\_\_init\_\_.py](backend/src/database/__init__.py): remove exports of deleted classes
    - Update imports in [main.py](backend/src/main.py): no changes needed (uses factory interface)
- **Verification**:
    - `docker compose up -d` runs 8 services, omnitrader healthy
    - Memgraph Lab at `localhost:3001` accessible
    - `MATCH (n) RETURN labels(n), count(n)` shows Trade/Signal/Equity nodes
    - Risk state persists across restarts: toggle circuit breaker, restart, check `:State` nodes

### 2. News Ingestion & NLP Pipeline (T33) 🟠 HIGH
- [ ] **Phase 2a: Extended graph schema**
    - Add node labels:
        - `:Asset {symbol, name, sector, exchange, market_cap_tier}`
        - `:NewsEvent {id (unique URL hash), title, source, published_at, sentiment_score, impact_level, raw_text}`
        - `:Sector {name}`
        - `:MacroIndicator {name (unique), value, timestamp}`
    - Add relationships:
        - `(:NewsEvent)-[:IMPACTS {magnitude}]->(:Asset)` — news impact magnitude (0-1)
        - `(:NewsEvent)-[:MENTIONS]->(:Sector)` — extracted from news text
        - `(:Asset)-[:BELONGS_TO]->(:Sector)` — static mapping (seed data)
        - `(:Asset)-[:CORRELATES_WITH {coefficient, window}]->(:Asset)` — correlation pairs
        - `(:Trade)-[:TRIGGERED_BY]->(:Signal)` — new! enables trade analysis
    - Create indexes:
        ```cypher
        CREATE INDEX ON :NewsEvent(published_at);
        CREATE INDEX ON :Asset(symbol);
        CREATE INDEX ON :MacroIndicator(name);
        ```
- [ ] **Phase 2b: News ingestor service** ([backend/src/graph/ingestor.py](backend/src/graph/ingestor.py))
    - Polling loop (runs every 60s in background):
        1. **CryptoPanic API**: `GET api/v1/posts/` (params: `kind=news`, `public=true`)
           - Returns: `{posts: [{id, title, source, created_at, votes: {liked, disliked}}]}`
           - Sentiment heuristic: `sentiment = (votes.liked - votes.disliked) / (votes.liked + votes.disliked)` capped at [-1, +1]
           - Create `:NewsEvent {id: hash(url), title, source: "CryptoPanic", published_at, sentiment_score, impact_level: 0.7, raw_text: title}`
        2. **Fear & Greed Index**: `GET https://api.alternative.me/fng/`
           - Returns: `{data: [{value, value_classification, timestamp}]}`
           - Create/merge `:MacroIndicator {name: "fear_and_greed", value: <int>, timestamp}`
        3. **RSS Feeds**: CoinDesk, CoinTelegraph, The Block
           - Use `feedparser.parse(url)` → extract `{title, link, published, summary}`
           - Sentiment: simple heuristic (keyword matching) or zero (neutral)
           - Create `:NewsEvent {id: hash(link), title, source, published_at, sentiment_score, impact_level: 0.5, raw_text: summary}`
        4. **Deduplication**: hash(url + title) — skip if already exists
    - Store in Memgraph: insert nodes + relationships
    - Rate limiting: use [rate_limiter.py](backend/src/rate_limiter.py) for API calls
    - TTL: daily job deletes `:NewsEvent` nodes older than 7 days
- [ ] **Phase 2c: Ollama NLP entity extraction** ([backend/src/graph/nlp.py](backend/src/graph/nlp.py))
    - Hook: before inserting `:NewsEvent`, send title/summary to Ollama
    - Request: `POST http://ollama:11434/api/generate`
        ```json
        {
          "model": "llama2",
          "prompt": "Extract: assets (tickers), sectors (L1/DeFi/etc), sentiment (-1 to +1), impact (0 to 1). Go:\n\n{news_text}\n\nAnswer JSON: ",
          "stream": false
        }
        ```
    - Response: parse JSON from `response.response` field
    - Update node properties: `sentiment_score, impact_level` from NLP output
    - Fallback: if Ollama timeout (>5s), use CryptoPanic's built-in sentiment or default to 0
    - Session: `httpx.AsyncClient` with timeout=5s, pooling (max 10 connections)
- **Verification**:
    - CryptoPanic polling: `:NewsEvent` nodes appear within 60s
    - Ollama extraction: `sentiment_score` and `impact_level` populated on `:NewsEvent`
    - Fallback: if Ollama container down, news still ingests with CryptoPanic sentiment

###  3. Graph Analytics, Crisis Mode & Pipeline (T34) 🟠 HIGH
- [ ] **Phase 3a: Graph analytics queries** ([backend/src/graph/analytics.py](backend/src/graph/analytics.py))
    - Sentiment aggregation:
        ```cypher
        MATCH (n:NewsEvent)-[:IMPACTS]->(a:Asset {symbol: $sym})
        WHERE n.published_at > $since
        RETURN avg(n.sentiment_score) as sentiment, count(n) as volume, max(n.impact_level) as max_impact
        ```
    - Crisis detection:
        ```cypher
        MATCH (n:NewsEvent)-[:IMPACTS]->(a)
        WHERE n.published_at >= timestamp(now()) - duration('1h')
                AND n.impact_level > 0.7 AND n.sentiment_score < -0.5
        RETURN count(n) as negative_count
        ```
        → If count > 3: `crisis_flag = True`
    - Sentiment-reality divergence:
        ```cypher
        MATCH (m:MacroIndicator {name: "fear_and_greed"})
        MATCH (n:NewsEvent) WHERE n.published_at > timestamp(now()) - duration('24h')
        WITH m.value as fear_greed, avg(n.sentiment_score) as news_sentiment
        RETURN fear_greed > 75 AND news_sentiment < -0.3 as divergence_flag
        ```
    - All methods return JSON-serializable dicts (no custom objects)
- [ ] **Phase 3b: `analyze_knowledge_graph` Celery task**
    - New task in [backend/src/workers/tasks.py](backend/src/workers/tasks.py):
        ```python
        @app.task(name='analyze_knowledge_graph')
        def analyze_knowledge_graph(symbol: str, config_dict: dict) -> dict:
            # Call analytics methods
            return {
                'sentiment': float,
                'impact': float,
                'crisis_flag': bool,
                'divergence_flag': bool,
                'correlated_alerts': List[str]
            }
        ```
    - Dispatch alongside `analyze_strategy` + `analyze_regime` in [main.py](backend/src/main.py) `run_cycle()`
    - Wait for all 3 tasks: `tasks = await asyncio.gather(dispatch(strat), dispatch(regime), dispatch(graph))`
- [ ] **Phase 3c: Crisis mode protocol** ([backend/src/graph/crisis.py](backend/src/graph/crisis.py))
    - Automatic activation when graph returns `crisis_flag=True`
    - Manual toggle via API endpoint `PUT /api/graph/crisis` + config field `graph.crisis_mode`
    - Applied overrides in `_open_position()`:
        - leverage: 3.0 → 1.0
        - position_size_pct: 2.0 → 0.5
        - max_daily_loss_pct: 5.0 → 2.0
        - allowed_strategies: all → [adx_trend] only
    - State: `:State {key: "crisis_mode", value: {active: bool, triggered_by: str, activated_at: timestamp}}`
    - Persist across restarts
    - Log to `signals_log` on activation/deactivation
- [ ] **Phase 3d: Signal gating with graph context**
    - In `_open_position()` before `RiskManager.validate_trade()`:
        ```python
        if divergence_flag:
            # Reduce signal confidence
            if signal == LONG_SIGNAL:
                position_size_pct *= 0.5  # Halve position size
        if graph_sentiment < -0.5 and signal == LONG:
            return SIGNAL_BLOCKED  # Don't enter
        if graph_sentiment > 0.5 and signal == SHORT:
            return SIGNAL_BLOCKED
        ```
- [ ] **Phase 3e: API endpoints** ([backend/src/api/routes/graph.py](backend/src/api/routes/graph.py) — 4 endpoints)
    - `GET /api/graph/sentiment/{symbol}`: `{sentiment: float, volume: int, max_impact: float, recent_news: [{title, source, sentiment, impact}]}`
    - `GET /api/graph/crisis`: `{active: bool, triggered_by: str, macro_indicators: {dxy, oil, fear_greed, btc_dominance}, latest_alert: str}`
    - `PUT /api/graph/crisis` (auth): toggle crisis mode, persist state
    - `GET /api/graph/news`: latest 20 `:NewsEvent` nodes sorted by published_at DESC
- [ ] **Phase 3f: Frontend components**
    - New dashboard page: `/dashboard/intelligence`
    - Components:
        - `SentimentGauge.tsx`: emoji + color based on [-1, +1] scale (sad → happy)
        - `NewsFeed.tsx`: scrollable latest 10 news with impact badge (red/yellow/green)
        - `MacroPanel.tsx`: 4 cards for DXY, Oil, Fear & Greed, BTC Dominance (with trend arrows)
        - Crisis mode toggle in `ConfigEditor.tsx` or separate crisis banner
    - Update [frontend/src/lib/api.ts](frontend/src/lib/api.ts): add graph endpoint types
    - Extend `CycleMessage` WebSocket type: add `sentiment?: number`, `crisis_mode?: boolean`, `macro_indicators?: {...}`
    - Update [frontend/src/lib/ws.ts](frontend/src/lib/ws.ts): pass new fields to components
- **Verification**:
    - API returns correct sentiment aggregation
    - Crisis detection triggers on >3 negative high-impact news in 1h
    - Divergence flag when Fear & Greed > 75 + news sentiment < -0.3
    - Signal gating: long blocked when sentiment < -0.5
    - Frontend displays sentim gauge, news feed, macro indicators in real-time

### 4. Backtesting Engine (T35) 🔴 CRITICAL (after T32-T34)
- [ ] **Phase 4a: Historical candle storage**
    - Bulk download: Binance REST API `/api/v3/klines`
    - Pagination: max 1000 bars/call, handle loop for multi-year ranges
    - Rate limiting: use [rate_limiter.py](backend/src/rate_limiter.py) for API calls
    - Store as `:Candle {symbol, timeframe, timestamp, open, high, low, close, volume}` nodes
    - Composite index: `(symbol, timeframe, timestamp)`
    - Query: `MATCH (c:Candle {symbol: $sym, timeframe: $tf}) WHERE c.timestamp >= $start AND c.timestamp <= $end RETURN c ORDER BY c.timestamp`
- [ ] **Phase 4b: Backtesting simulator**
    - Event-driven: iterate `:Candle` nodes chronologically
    - Reuse all existing strategies (`BaseStrategy` interface) — zero changes
    - Per bar:
        1. Call `strategy.analyze(market_data, current_position, market_trend) → StrategyResult`
        2. Check SL/TP: if `bar.low <= sl_price` exit at SL; if `bar.high >= tp_price` exit at TP
        3. Risk validation: position sizing, leverage checks
        4. Update position state, unrealized PnL
    - Cost model: 0.04% taker fee, bid-ask spread (0.01% + ATR volatility), funding costs
    - Store trades/signals as Memgraph nodes during sim
- [ ] **Phase 4c: Walk-forward validation + metrics**
    - Rolling train/test: 6-month training, 1-month test windows
    - Performance metrics: Sharpe (annualized), Sortino, max drawdown, profit factor, win rate
    - Bootstrap: 1000 resample runs → confidence intervals
    - Export: JSON summary, CSV trades, PNG equity curve, monthly heatmap
    - Compare: backtest vs paper mode results (sanity check)
- **Acceptance**:
    - ADX Trend backtest on 2022 bear market: <30s runtime
    - Metrics: Sharpe >1.0, max DD <15%, profit factor >1.5, win rate >40%
    - Bootstrap CIs don't cross zero

### 5. Exchange Adapter Architecture (T36) 🟠 HIGH
- [ ] **Phase 5a: Abstract exchange interface**
    - Create `BaseExchangeAdapter` abstract class in [backend/src/exchanges/base.py](backend/src/exchanges/base.py)
    - Define 18 core methods: connect, close, health_check, fetch_ohlcv, get_ticker, get_balance, get_position, get_open_positions, fetch_open_orders, market_long, market_short, close_position, set_stop_loss, set_take_profit, cancel_order, set_leverage, update_config, get_mark_price
    - DTOs: `TickerData`, `PositionData`, `BalanceData`, `OrderResult` (dataclasses)
    - Move paper trading logic to base adapter (shared across CCXT + Binance Direct)
- [ ] **Phase 5b: CCXT adapter**
    - Wrap existing `Exchange` class → `CCXTAdapter(BaseExchangeAdapter)` in [backend/src/exchanges/ccxt_adapter.py](backend/src/exchanges/ccxt_adapter.py)
    - Translate CCXT responses to standardized DTOs
    - Handle CCXT exceptions → `ExchangeError`, `RateLimitError`, `OrderRejectedError`
    - Keep `ccxt>=4.0.0,<4.4.0` pinning (avoid lighter-client bug)
- [ ] **Phase 5c: Binance Direct REST adapter**
    - Implement `BinanceDirectAdapter(BaseExchangeAdapter)` in [backend/src/exchanges/binance_direct.py](backend/src/exchanges/binance_direct.py)
    - Pure `httpx` HTTP client for Binance Futures REST API v1
    - HMAC-SHA256 request signing, Binance weight-based rate limiting (1200/min)
    - Response validation: `pydantic` models for type safety
    - WebSocket listenKey management for user data stream
- [ ] **Phase 5d: Adapter factory + fallback**
    - `ExchangeFactory.create_adapter()` in [backend/src/exchanges/factory.py](backend/src/exchanges/factory.py)
    - Config: `exchange.adapter: binance_direct` or `ccxt`
    - Fallback logic: switch to CCXT if Binance Direct fails 3× consecutively
    - Health metrics: track success/error rates per adapter in Redis
- [ ] **Phase 5e: Integration + testing**
    - Update `OmniTrader.__init__()`: replace `Exchange()` with `ExchangeFactory.create_adapter()`
    - Update all tests: mock `BaseExchangeAdapter` instead of `Exchange`
    - Add adapter-specific test suites: `test_ccxt_adapter.py`, `test_binance_direct.py`, `test_adapter_factory.py`
    - Integration test: run same strategy on both adapters → assert equivalent results
- **Rationale**: CCXT bugs (lighter-client, unmaintained exchanges, version lock) create capital risk. Direct adapter gives full control, faster execution, easier debugging. CCXT remains as fallback.
- **Effort**: ~3 days
- **Acceptance**:
    - Both adapters pass all unit tests with identical mock responses
    - Paper mode parity: CCXT and Binance Direct produce same PnL over 1000 bars
    - Binance Direct handles all error codes gracefully
    - Fallback works: simulated outage → automatic CCXT switch
    - Performance: Direct adapter 20-30% faster RTT than CCXT

---

## Sprint: Multi-Asset Autonomous Platform (T37-T42)

**Goal**: Transform single-pair BTC/USDT bot into a multi-asset platform where each bot instance manages one asset pair, autonomously selects strategies, and supports user-created custom strategies. Expose environment variable management via API. These backend features are required by the frontend design (see PROMPT.md).

**Phase breakdown:**
- **T37 (3 days)**: Multi-asset bot management — CRUD API, per-bot lifecycle, isolated positions
- **T38 (2 days)**: Autonomous strategy selection — regime-based ranking, auto-rotation
- **T39 (2 days)**: TA-Lib migration — replace pandas-ta, expose indicator catalog API
- **T40 (3 days)**: Custom strategy system — user-created strategies with TA-Lib conditions
- **T41 (1 day)**: Environment variable management API — read/write .env from dashboard
- **T42 (1 day)**: Markets discovery API — fetch tradeable pairs from exchange

**Depends on**: T32 (Memgraph), T35 (Backtesting for strategy scoring), T36 (Exchange adapter for multi-pair)

### T37. Multi-Asset Bot Management API 🔴 CRITICAL
- [ ] **Phase 7a: Bot entity model in Memgraph**
    - New node label: `:Bot {id, symbol, status, mode, active_strategy, regime, leverage, balance_allocated, timeframe, created_at, updated_at}`
    - Relationships: `(:Bot)-[:HAS_POSITION]->(:Position)`, `(:Bot)-[:EXECUTED]->(:Trade)`, `(:Bot)-[:USES]->(:Strategy)`
    - Indexes: `:Bot(id)`, `:Bot(symbol)`, `:Bot(status)`
    - Each bot runs independently — isolated position, risk state, and strategy context
- [ ] **Phase 7b: Bot CRUD API endpoints** ([backend/src/api/routes/bots.py](backend/src/api/routes/bots.py))
    - `GET /api/bots` — list all bots with current state
    - `POST /api/bots` — create new bot `{symbol, mode, strategy?, leverage, allocation, timeframe}`
    - `GET /api/bots/{id}` — single bot detail with position, recent trades, risk metrics
    - `PUT /api/bots/{id}` — update bot configuration
    - `DELETE /api/bots/{id}` — remove bot (with safety: must be stopped, no open position)
    - `POST /api/bots/{id}/start` — start bot trading loop
    - `POST /api/bots/{id}/stop` — stop bot, optionally close position
    - `POST /api/bots/{id}/trade/open` — manual trade on specific bot
    - `POST /api/bots/{id}/trade/close` — manual close on specific bot
    - All mutation endpoints require `verify_api_key` auth
- [ ] **Phase 7c: Bot lifecycle manager** ([backend/src/bot_manager.py](backend/src/bot_manager.py))
    - `BotManager` class: manages multiple bot instances concurrently
    - Each bot is an `OmniTrader` instance with its own symbol, strategy, and risk state
    - Start/stop individual bots without affecting others
    - Shared exchange connection (rate limiter is global) but isolated positions
    - WebSocket feed: subscribe to multiple symbols via CCXT Pro
    - Aggregate status: total portfolio value, combined PnL, open positions count
- [ ] **Phase 7d: Per-bot risk isolation**
    - Each bot gets its own risk state in Memgraph: `:State {key: "risk:{bot_id}:daily_stats"}`
    - Independent circuit breakers per bot
    - Global portfolio-level circuit breaker: if combined drawdown > threshold, pause all bots
    - Per-bot allocation: sum of all allocations must not exceed 100%
- **Effort**: ~3 days | **Consolidates**: BACKLOG B6 (Multi-Asset)
- **Acceptance**: Create 3 bots (BTC, ETH, SOL), start all, each trades independently, stop one without affecting others

### T38. Autonomous Strategy Selection Engine 🔴 CRITICAL
- [ ] **Phase 8a: Strategy scoring model** ([backend/src/strategies/selector.py](backend/src/strategies/selector.py))
    - For each registered strategy, maintain performance metrics per regime:
        ```python
        StrategyScore {
            strategy_name: str
            regime: str           # 'trending' | 'ranging' | 'volatile'
            sharpe_ratio: float
            win_rate: float
            profit_factor: float
            sample_size: int      # number of trades in this regime
            last_updated: int
        }
        ```
    - Store as `:StrategyScore` nodes in Memgraph, linked to `:Strategy` nodes
    - Populate from backtesting results (T35) or live trading history
    - Minimum sample size (20 trades) before strategy is eligible for auto-selection
- [ ] **Phase 8b: Selection algorithm**
    - When bot is in `mode: 'auto'`:
        1. Detect current regime via `analyze_regime` (existing)
        2. Query all strategy scores for that regime
        3. Rank by composite score: `0.4 * sharpe + 0.3 * profit_factor + 0.3 * win_rate`
        4. Select top strategy; if tie, prefer strategy with larger sample size
        5. If regime changes → re-evaluate and rotate strategy
    - Cooldown: don't rotate strategy more than once per 4 hours (avoid churn)
    - Log rotation events: `:Signal {type: 'strategy_rotation', from: X, to: Y, reason: 'regime_change'}`
- [ ] **Phase 8c: Manual override**
    - When bot `mode: 'manual'` → lock to user-specified strategy, ignore regime changes
    - API: `PUT /api/bots/{id}` with `{mode: 'manual', active_strategy: 'bollinger_bands'}`
    - Dashboard shows "Auto" or "Manual" badge per bot
- **Effort**: ~2 days | **Depends on**: T35 (backtest data for scoring), T37 (bot model)
- **Acceptance**: Bot in auto mode switches from ADX Trend → Bollinger Bands when regime flips from TRENDING → RANGING

### T39. TA-Lib Migration & Indicator Service 🟠 HIGH
- [ ] **Phase 9a: Replace pandas-ta with TA-Lib**
    - TA-Lib already installed in Docker image
    - Update all 5 built-in strategies to use `talib.*` instead of `pandas_ta.*`:
        - `adx_trend.py`: `talib.ADX()`, `talib.EMA()`
        - `bollinger_bands.py`: `talib.BBANDS()`, `talib.RSI()`
        - `breakout.py`: replace pandas-ta Donchian with manual or TA-Lib `talib.MAX()`/`talib.MIN()`
        - `ema_volume.py`: `talib.EMA()`, `talib.SMA()`
        - `z_score.py`: `talib.STDDEV()`, `talib.SMA()`
    - Remove `pandas-ta` from requirements.txt
    - Verify all existing tests pass after migration
- [ ] **Phase 9b: Indicator catalog API**
    - `GET /api/indicators` — returns all 158 TA-Lib functions grouped by category
    - Response includes: function name, group, input params with defaults, output names
    - Use `talib.get_function_groups()` and `talib.abstract.Function()` for introspection
    - Categories: Overlap Studies (17), Momentum (30), Volume (3), Volatility (3), Price Transform (4), Cycle (5), Pattern Recognition (61), Math Operators (11), Statistic Functions (9)
- [ ] **Phase 9c: Indicator computation endpoint**
    - `POST /api/indicators/compute` — compute any indicator on given OHLCV data
    - Used by Strategy Editor for preview charts
    - Input: `{function: "RSI", params: {timeperiod: 14}, symbol: "BTC/USDT", timeframe: "1h"}`
    - Output: array of values aligned with candle timestamps
- **Effort**: ~2 days | **Note**: TA-Lib is already installed per user confirmation
- **Acceptance**: All 5 strategies produce identical signals before/after migration; indicator catalog API returns all 158 functions

### T40. Custom Strategy System (CRUD + Execution) 🟠 HIGH
- [ ] **Phase 10a: Custom strategy data model**
    - New node: `:CustomStrategy {name, description, regime_affinity, entry_long, entry_short, exit_long, exit_short, indicators, risk_overrides, created_at, updated_at, created_by}`
    - `entry_long` / `entry_short` / `exit_long` / `exit_short`: JSON arrays of conditions
    - Each condition: `{indicator: "RSI", operator: "<", value: 30}`
    - `indicators`: JSON array of `{function: "RSI", params: {timeperiod: 14}, output_name: "rsi_14"}`
- [ ] **Phase 10b: Custom strategy CRUD API**
    - `GET /api/strategies` — list all strategies (built-in read-only + custom editable)
    - `GET /api/strategies/{name}` — strategy detail with parameters
    - `POST /api/strategies` — save new custom strategy (auth required)
    - `PUT /api/strategies/{name}` — update custom strategy (auth, only user-created)
    - `DELETE /api/strategies/{name}` — delete custom strategy (auth, only user-created)
    - Built-in strategies (ADX Trend, Bollinger, etc.) cannot be modified or deleted
- [ ] **Phase 10c: Custom strategy executor** ([backend/src/strategies/custom_executor.py](backend/src/strategies/custom_executor.py))
    - `CustomStrategyExecutor(BaseStrategy)` — dynamically evaluates conditions
    - Computes all required TA-Lib indicators from OHLCV data
    - Evaluates entry/exit conditions: supports `>`, `<`, `>=`, `<=`, `crosses_above`, `crosses_below`
    - `crosses_above`: previous bar indicator < value AND current bar indicator >= value
    - Register in strategy registry dynamically at bot startup
- [ ] **Phase 10d: Integration with Strategy Lab**
    - Custom strategies appear alongside built-in in all dropdowns
    - Backtesting (T35) works with custom strategies
    - Autonomous selector (T38) can include custom strategies if they have enough backtest data
- **Effort**: ~3 days | **Depends on**: T39 (TA-Lib indicators)
- **Acceptance**: Create custom strategy "RSI Bounce" (RSI<30 entry, RSI>70 exit), backtest it, deploy on a bot

### T41. Environment Variable Management API 🟠 HIGH
- [ ] **Phase 11a: Env reader/writer** ([backend/src/api/routes/env.py](backend/src/api/routes/env.py))
    - `GET /api/env` — read `.env` file, return variables grouped by category
    - Mask secrets: BINANCE_API_KEY, BINANCE_SECRET, MEMGRAPH_PASSWORD, OMNITRADER_API_KEY → show `•••••`
    - Categories: Binance API, Database, Redis, Notifications, Security
    - Include metadata: `{key, value, masked, category, description, requires_restart}`
- [ ] **Phase 11b: Env updater**
    - `PUT /api/env` — update `.env` file (auth required)
    - Validate: non-empty required fields, valid port numbers, valid URLs
    - Write atomically: write to `.env.tmp`, then rename to `.env`
    - Return `{requires_restart: boolean}` — true if any changed var needs service restart
    - Log all env changes to `:Signal {type: 'config_change', ...}` for audit trail
- [ ] **Phase 11c: Service restart endpoint**
    - `POST /api/system/restart` — trigger Docker Compose restart (auth required)
    - Uses `subprocess` to run `docker compose restart` (or reload specific services)
    - Must confirm via request body: `{confirm: true}`
- **Effort**: ~1 day
- **Acceptance**: Change DISCORD_WEBHOOK_URL from Settings page, verify .env updated; change REDIS_PORT, see restart warning

### T42. Markets Discovery API 🟠 HIGH
- [ ] **Phase 12a: Markets endpoint** ([backend/src/api/routes/markets.py](backend/src/api/routes/markets.py))
    - `GET /api/markets` — fetch all tradeable futures pairs from Binance
    - Use exchange adapter: `exchange.fetch_markets()` or Binance REST `/fapi/v1/exchangeInfo`
    - Return: `[{symbol, base, quote, min_size, tick_size, volume_24h, last_price, status}]`
    - Filter: only active pairs, optionally filter by quote currency (USDT)
    - Cache: Redis with 5-minute TTL (market info doesn't change frequently)
- [ ] **Phase 12b: Market search**
    - Query param: `GET /api/markets?search=ETH&quote=USDT`
    - Used by frontend "Add Bot" symbol picker — searchable with volume + price display
- **Effort**: ~1 day | **Depends on**: T36 (exchange adapter)
- **Acceptance**: Frontend symbol picker shows all Binance Futures USDT pairs with volume and price

---

## Sprint: Frontend-Backend Integration Bridge (T43)

**Goal**: Connect the new React frontend to the existing backend. The frontend has 10 pages with a full API client + WebSocket client but zero actual backend integration (100% mock data). This sprint creates an adapter layer (backend shapes → frontend types) and a stub layer (typed fallbacks for unimplemented features) so the frontend works with real data where available and degrades gracefully elsewhere. As T33-T42 complete, each stub is replaced with the real endpoint.

**Depends on**: T32 (Memgraph — ✅ done)
**Enables**: All T33-T42 backend work to surface in the frontend progressively
**Plan file**: `plan-frontendBackendIntegrationMigration.prompt.md`

**Phase breakdown:**
- **Phase 13a**: Infrastructure — Vite dev proxy, Nginx production proxy, auth token injection
- **Phase 13b**: Adapter layer — `adapters.ts` converting backend response shapes to frontend TypeScript types
- **Phase 13c**: Stub layer — `stubs.ts` providing typed fallbacks annotated with future task IDs (T33-T42)
- **Phase 13d**: API client rewiring — each `api.ts` function calls real backend or falls back to stub
- **Phase 13e**: WebSocket integration — connect to real WS, adapt message format
- **Phase 13f**: Page-by-page wiring — replace mock imports with TanStack Query hooks in all 9 pages + layout
- **Phase 13g**: Backend stub routes — `stubs.py` returning 501 with task references for unbuilt endpoints

**Real endpoints (backend exists):** `/api/bot/state`, `/api/position`, `/api/balance`, `/api/strategies`, `/api/trades`, `/api/equity`, `/api/config`, `/api/candles`, `/api/bot/start|stop`, `/api/notifications/discord`

**Stubbed endpoints (→ replaced by future tasks):**
| Frontend Feature | Stub | Replaced by |
|---|---|---|
| Multi-bot management | `stubBots()` | T37 |
| Sentiment/Crisis/News | `stubSentiment()`, `stubCrisis()`, `stubNews()` | T33/T34 |
| Backtesting | `stubBacktestResults()` | T35 |
| Markets discovery | `stubMarkets()` | T42 |
| Env variable management | `stubEnvVars()` | T41 |
| Custom strategy CRUD | Strategy mutation stubs | T40 |

**Files created**: `frontend/src/lib/adapters.ts`, `frontend/src/lib/stubs.ts`, `backend/src/api/routes/stubs.py`
**Files modified**: `frontend/vite.config.ts`, `frontend/nginx.conf`, `frontend/src/lib/api.ts`, `frontend/src/lib/ws.ts`, all 9 pages, Topbar, AppSidebar, `backend/src/api/__init__.py`

**Effort**: ~2 days
**Acceptance**: Dashboard shows real data, WS connected, Charts show real candles, Settings persist, stubbed pages render without errors

---

## Completed Sprints

<details>
<summary>Sprint: Post-Audit Critical Fixes (2026-03-03 to 2026-03-05) — ✅ COMPLETE</summary>

All 8 items (T6-T13, T15) implemented and merged. See TASKS.md for details

</details>
