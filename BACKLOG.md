# Backlog

Items requiring design decisions, external dependencies, or are lower-priority long-term investments. Reviewed each sprint — promote to TODO when scoped and ready.

> Last updated: 2026-03-03 by Institutional Audit

---

## 🔴 Research-Blocked (Need Design Before Implementation)

### B1. Build Backtesting Engine
- **Priority**: CRITICAL — **no statistical evidence of edge exists without this**
- **Depends on**: Historical data pipeline (Binance API or Kaggle/Tardis)
- **Design needed**:
    - Data source: Binance historical klines API vs. third-party (Tardis, Kaiko)
    - Walk-forward framework: rolling window or expanding window?
    - Cost modeling: spread, slippage, funding rates, commission
    - Execution simulation: fill at close vs. VWAP of next bar
    - Minimum dataset: 2+ years BTC/USDT 15m OHLCV across bull/bear/range
- **Acceptance**: Sharpe, Sortino, max drawdown, profit factor, win rate output per strategy. Walk-forward with minimum 6-month out-of-sample holdout.

### B2. Walk-Forward Validation Framework
- **Priority**: CRITICAL
- **Depends on**: B1 (backtesting engine)
- **Design needed**: Rolling train/test splits. Parameter stability analysis across windows. Detect overfitting via in-sample vs. out-of-sample performance decay.

### B3. Monte Carlo Stress Testing
- **Priority**: HIGH
- **Depends on**: B1 (backtesting engine)
- **Design needed**: Bootstrap trade sequences. Randomize entry timing ±N bars. Simulate 10,000 equity paths. Report: probability of >15% drawdown, >25% drawdown, risk of ruin.

### B4. Geopolitical & Macro Risk Module
- **Priority**: HIGH — **active crisis (Iran/Hormuz) exposes total lack of macro awareness**
- **Design needed**:
    - **Data sources**: Fear & Greed Index (Alternative.me), DXY (FRED/Yahoo), oil futures (for Hormuz-class events), VIX equivalent for crypto
    - **Crisis-mode protocol**: Configurable override that reduces leverage to 1×, cuts position_size_pct to 0.5%, enables only ADX strategy, tightens daily loss to 2%, adds manual approval gate
    - **Sentiment-reality divergence detector**: When greed index is high but geopolitical risk is elevated (e.g., active conflict + supply disruption), flag as "greed noise" — mean-reversion signals become unreliable, reduce confidence in all signals
    - **Integration point**: New field in `config.yaml` for `crisis_mode: true/false` that overrides risk parameters. Dashboard toggle.
- **Context**: As of 2026-03-03, Day 3 of US-Israeli war with Iran; Strait of Hormuz closed. Oil spike → inflation fears → risk-off. BTC correlation to equities increases during systemic stress. The system has zero macro awareness and no mechanism to distinguish "greed noise" from genuine bullish sentiment.

### B5. Complete SMC Integration
- **Priority**: MEDIUM
- **Design needed**: Wire `smc/analysis.py` output into strategy pipeline. Options:
    - A) Register as standalone strategy in registry (HIGH overfitting risk per ROADMAP)
    - B) Use as confirmation layer — filter signals through BOS/CHoCH bias (RECOMMENDED)
    - C) Use as entry refinement — sniper entries at order block zones after strategy signal
- **Missing SMC features**: Order block detection, fair value gap identification, liquidity sweep detection. Current implementation only detects structure (BOS/CHoCH).
- **Depends on**: Multi-timeframe data pipeline (currently only primary TF analyzed)

### B6. Portfolio Construction / Multi-Asset
- **Priority**: MEDIUM
- **Design needed**:
    - Asset selection criteria (liquidity minimums, correlation caps)
    - Correlation management: max pairwise correlation exposure (BTC/ETH ~0.85 — don't long both)
    - Capital allocation: equal-risk vs. volatility-parity vs. Kelly criterion
    - Sector exposure caps (L1s, DeFi, memes)
    - Risk: `min_size` is currently hardcoded for BTC (T27)

### B7. Execution Optimization
- **Priority**: MEDIUM
- **Design needed**:
    - Limit orders for entries (reduce spread crossing, earn maker rebates)
    - TWAP/VWAP for larger positions (relevant only at >$50k notional)
    - Adaptive execution: market orders for urgency, limit for patience
    - Stop-limit vs. stop-market tradeoff (stop-limit avoids bad fills but risks no fill)

### B8. Alembic Migration Framework
- **Priority**: MEDIUM
- **Depends on**: Decision on primary DB (Postgres vs. SQLite for dev)
- **Design needed**: Generate initial migration from current inline DDL. Version-track all schema changes. Handle SQLite→Postgres migration path.
- **Ref**: TASKS.md T21

### B9. Postgres Integration Testing
- **Priority**: MEDIUM
- **Depends on**: CI/CD setup or local testcontainers
- **Design needed**: Docker-based test Postgres. Test all CRUD operations, schema creation, type differences (TIMESTAMPTZ, JSONB). Validate SQLite↔Postgres behavioral parity.
- **Ref**: TASKS.md T20

### B10. Factor Decomposition & Beta Hedging
- **Priority**: LOW (institutional-grade upgrade)
- **Design needed**:
    - Factor model: crypto beta, momentum, carry (funding rate), value
    - Decompose strategy returns into factor exposures vs. true alpha
    - Beta hedging mechanism (if correlated to BTC spot, hedge with inverse position)
    - Data sources: BTC dominance, sector indices, funding rate history

---

## 🟡 Nice-to-Have / Future Phases

### B11. QuestDB Time-Series Scaling
- Migrate OHLCV and tick data to QuestDB for high-performance ingestion. Needed for multi-pair at scale.

### B12. Cross-Exchange Arbitrage (Neo4j)
- Graph-based pathfinding for multi-exchange profit loops. Phase 4 vision item.

### B13. Ollama Intelligence Sidecar
- Local LLM for trade post-mortems, market narrative summaries, sentiment filtering. Phase 4 vision item.

### B14. Semi-Automatic Mode
- Dashboard trade approval gate for first 2 weeks of live trading. Button to approve/reject each signal before execution.
