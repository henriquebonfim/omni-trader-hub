# Backlog

Items requiring design decisions, external dependencies, or are lower-priority long-term investments. Reviewed each sprint — promote to TODO when scoped and ready.

> Last updated: 2026-03-05 | Promoted: B1→T29, B4→T30, B14→T31 | Completed: B8, B9

---

## 🔴 Research-Blocked (Need Design Before Implementation)

### B1. Build Backtesting Engine
- **Priority**: CRITICAL — **no statistical evidence of edge exists without this**
- **Status**: ✅ **PROMOTED to TASKS.md T29** (2026-03-05)
- **Next**: Design data pipeline and simulation engine

### B2. Walk-Forward Validation Framework
- **Priority**: CRITICAL
- **Depends on**: T29 (backtesting engine)
- **Design needed**: Rolling train/test splits. Parameter stability analysis across windows. Detect overfitting via in-sample vs. out-of-sample performance decay.
- **Status**: Waiting on T29 completion

### B3. Monte Carlo Stress Testing
- **Priority**: HIGH
- **Depends on**: T29 (backtesting engine)
- **Design needed**: Bootstrap trade sequences. Randomize entry timing ±N bars. Simulate 10,000 equity paths. Report: probability of >15% drawdown, >25% drawdown, risk of ruin.
- **Status**: Waiting on T29 completion

### B4. Geopolitical & Macro Risk Module
- **Priority**: HIGH — **active crisis (Iran/Hormuz) exposes total lack of macro awareness**
- **Status**: ✅ **PROMOTED to TASKS.md T30** (2026-03-05)
- **Next**: Design data sources and crisis-mode protocol

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
- **Status**: ✅ **COMPLETED** as T21 (2026-03-05)
- **Ref**: TASKS.md T21

### B9. Postgres Integration Testing
- **Status**: ✅ **COMPLETED** as T20 (2026-03-05)
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
- **Status**: ✅ **PROMOTED to TASKS.md T31** (2026-03-05)
- **Next**: Design approval UI and timeout logic
