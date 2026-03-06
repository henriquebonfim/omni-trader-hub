# Backlog

Items requiring design decisions, external dependencies, or are lower-priority long-term investments. Reviewed each sprint — promote to TODO when scoped and ready.

> Last updated: 2026-03-05 | **MAJOR CONSOLIDATION (2026-03-05)**: Memgraph replaces PostgreSQL + Neo4j + QuestDB. B1→T35, B4→T34, B11/B12→Memgraph, B13→T33, B14→absorbed into T34. Completed: B8, B9

---

## 🔴 Research-Blocked (Need Design Before Implementation)

### B1. Build Backtesting Engine
- **Priority**: CRITICAL — **no statistical evidence of edge exists without this**
- **Status**: ✅ **PROMOTED to TASKS.md T35** (2026-03-05) — consolidated into Memgraph unified architecture
- **Change**: Historical candles stored as `:Candle` nodes in Memgraph; no need for separate QuestDB
- **Phasing**: After T32-T34 stabilize

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
- **Priority**: HIGH — **active crisis (I4 (Graph Analytics)** (2026-03-05) — consolidated into graph layer
- **Change**: Crisis mode + macro indicators are graph queries, not separate module. Macro data as `:MacroIndicator` nodes
- **Now includes**: Crisis detection, sentiment-reality divergence, sector contagion alerts)
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
ELIMINATED** (2026-03-05) — Memgraph is schemaless; no migrations needed
- **Note**: Alembic directory deleted, replaced by Memgraph index creation on startup

### B9. Postgres Integration Testing
- **Status**: ✅ **COMPLETED** (2026-03-05) as T20
- **Note**: Postgres completely removed 2026-03-05 during Memgraph consolidation

### B11. QuestDB Time-Series Scaling
- **Status**: ✅ **ELIMINATED** (2026-03-05) — Memgraph replaces
- **Rationale**: `:Candle` node storage + indexes sufficient for single-pair LFT/MFT. QuestDB only needed at multi-pair production scale

### B12. Cross-Exchange Arbitrage (Neo4j)
- **Status**: ✅ **REPLACED BY MEMGRAPH** (2026-03-05)
- **Rationale**: Memgraph is Cypher-compatible with superior real-time performance. Neo4j no longer needed

### B13. Ollama Intelligence Sidecar
- **Status**: ✅ **PROMOTED to T33** (2026-03-05) — news NLP entity extraction
- **Active**: Ollama uncommented in compose.yml, GPU-enabled

### B14. Semi-Automatic Mode
- **Status**: ✅ **ABSORBED (deferred)** (2026-03-05) — lower priority than T32-T34-T35
- **Rationale**: Approval gate is institutional feature; graph intelligence + backtesting are foundation requirements
- **Timeline**: Post-Phase-4, if needed for production deployment

---

### B15. Factor Decomposition & Beta Hedging
- **Priority**: LOW (institutional-grade upgrade)
- **Design needed**:
    - Factor model: crypto beta, momentum, carry (funding rate), value
    - Decompose strategy returns into factor exposures vs. true alpha
    - Beta hedging mechanism (if correlated to BTC spot, hedge with inverse position)
    - Data sources: BTC dominance, sector indices, funding rate history
- **Deferred**: Post-backtesting validation (after T35)

---

## 🟡 Future Phases

### Phase 5: GPU Acceleration (deferred)
- Upgrade Memgraph to CUDA: `memgraph/memgraph-mage:3.8.0-relwithdebinfo-cuda`
- Implement MAGE GPU algorithms: Louvain community detection, Betweenness centrality
- GNN model training via PyTorch Geometric
- Timeline: When multi-pair scaling or GPU hardware justified
### B13. Ollama Intelligence Sidecar
- Local LLM for trade post-mortems, market narrative summaries, sentiment filtering. Phase 4 vision item.

### B14. Semi-Automatic Mode
- **Status**: ✅ **PROMOTED to TASKS.md T31** (2026-03-05)
- **Next**: Design approval UI and timeout logic
