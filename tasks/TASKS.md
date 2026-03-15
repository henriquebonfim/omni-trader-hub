# OmniTrader — Technical Debt & Audit Findings

Active execution queue only. Completed work is archived in DONE.md. Use `TODO.md` for lower-priority candidates and `BACKLOG.md` for research/design candidates.

> Last updated: 2026-03-14 | Sprint status: Promoting verified gaps to active queue.

---

## Active Queue

### HIGH — Logic / Schema Bugs

- `T66` - [BUG] Fix strategy selector Cypher schema mismatch
        - Details: `selector.py` queries non-existent relationships/fields in Memgraph.
        - Files: `backend/src/strategy/selector.py`, `backend/src/database/memgraph.py`

- `T67` - [BUG] Standardize graph relationship name `:IMPACTS` vs `:MENTIONS`
        - Details: Ingestor uses `:IMPACTS`, route queries use `:MENTIONS`. Resulting in empty news feeds.
        - Files: `backend/src/intelligence/ingestor.py`, `backend/src/api/routes/graph.py`

- `T74` - [FEATURE] Add a live signals API endpoint
        - Details: No `/api/signals` route to retrieve recent signal history.
        - Files: `backend/src/api/__init__.py`, `backend/src/api/routes`, `backend/src/database/memgraph.py`

### MEDIUM — Backtest & Metrics Gaps

- `T69` - [IMPROVEMENT] Enhance backtest metrics to institutional standard
- `T70` - [IMPROVEMENT] Add explicit slippage/spread model to backtest engine
- `T75` - [IMPROVEMENT] Add executable walk-forward runner
- `T76` - [IMPROVEMENT] Improve runtime reporting surface

### LOW — Test Coverage & Docs

- `T77` - [TEST] Fix unawaited AsyncMock warning in crisis integration tests
- `T78` - [DOC] Reconcile README/API documentation with actual runtime surface
- `T73_history` - Decide fate of `GET /api/backtest/history` (501 stub)

---
