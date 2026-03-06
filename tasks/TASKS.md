# OmniTrader — Technical Debt & Audit Findings

Single source of truth for all technical work: architecture items, audit-discovered bugs, and risk gaps.
Institutional-grade audit completed **2026-03-03** — findings integrated below.

> Last updated: 2026-03-05 | Sprint promotion: T29-T31 added

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

## 🟠 High Priority (Correctness & Reliability)

---

## 🟡 Medium Priority (Hardening & Hygiene)

---
