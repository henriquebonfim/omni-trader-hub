# TODO

Confirmed work for the current sprint. All items validated, scoped, and ready to implement.
Unified Memgraph Architecture: Single persistent database replaces PostgreSQL + Neo4j + QuestDB.

> Last updated: 2026-03-05 | Sprint: Unified Memgraph Architecture (T32-T35)

---

> **⚠️ STRATEGIC PIVOT (2026-03-05)**: Starting immediate implementation of Knowledge Graph Intelligence system using Memgraph as single source of truth. PostgreSQL + Redis + Alembic → Memgraph + Redis (Celery-only). Data reset OK. Timeline: ~10 days for T32-T34 core, T35 backtesting after stabilization.

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

## Completed Sprints

<details>
<summary>Sprint: Post-Audit Critical Fixes (2026-03-03 to 2026-03-05) — ✅ COMPLETE</summary>

All 8 items (T6-T13, T15) implemented and merged. See TASKS.md for details

</details>
