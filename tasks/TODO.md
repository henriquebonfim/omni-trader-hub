# TODO

Forward-looking queue only. Completed work is archived in DONE.md, and active execution work belongs in TASKS.md.

> Last updated: 2026-03-14 | Sprint: Next-sprint queue

---

## Local Triage (No Open GitHub Issues) - 2026-03-12

Runtime verification completed against the live Docker stack. Gaps promoted to `TASKS.md`.

---

## Promoted Research Queue (Needs Design Before Build)

### T55. [RESEARCH] Walk-Forward Validation Framework (B2)
- **Priority**: CRITICAL
- **Research label**: Methodology design + statistical protocol
- **Depends on**: T35 (Backtesting Engine), stable strategy parameter interface
- **Deliverable**: Design doc for rolling train/test windows, decay thresholds, and acceptance criteria for promotion to implementation

### T56. [RESEARCH] Monte Carlo Stress Testing (B3)
- **Priority**: HIGH
- **Research label**: Risk modeling + simulation architecture
- **Depends on**: T35 (Backtesting Engine), T55 (validation assumptions)
- **Deliverable**: Design doc for bootstrap/shuffle model, scenario count, and drawdown/ruin reporting contract

### T57. [RESEARCH] Complete SMC Integration Plan (B5)
- **Priority**: MEDIUM
- **Research label**: Strategy architecture and overfitting controls
- **Depends on**: T46 (SMC confirmation baseline), multi-timeframe data plan
- **Deliverable**: Decision record for integration mode (confirmation vs standalone vs entry-refinement) and missing feature scope (order blocks/FVG/liquidity sweeps)

### T58. [RESEARCH] Execution Optimization Design (B7)
- **Priority**: MEDIUM
- **Research label**: Execution microstructure + fill-quality policy
- **Depends on**: T37 (multi-bot flow), live slippage/fill telemetry baselines
- **Deliverable**: Execution policy spec for market vs limit, TWAP/VWAP triggers, and stop-limit tradeoffs

### T59. [RESEARCH] Factor Decomposition & Beta Hedging (B15)
- **Priority**: LOW
- **Research label**: Institutional analytics design
- **Depends on**: T35 (validated strategy return streams), T37 (multi-asset exposure history)
- **Deliverable**: Factor model proposal, hedge mechanics, and required data-source inventory

---

## Promoted Build-Ready Queue (Implementation-First)

### T60. [IMPLEMENTATION] Visual Strategy Builder (B16)
- **Priority**: LOW
- **Research label**: Light UX discovery only (not blocker)
- **Depends on**: T40 (Custom Strategy System, completed)
- **Scope**: Frontend node/canvas editor that emits existing strategy JSON format

### T61. [IMPLEMENTATION] Trade Journal & Post-Mortem Annotations (B18)
- **Priority**: LOW
- **Research label**: Schema choice review during implementation
- **Depends on**: Trade history data model, optional T33 (auto summary enhancement)
- **Scope**: Trade annotation UX with notes/tags and persistence model

### T62. [IMPLEMENTATION] Theme Toggle (Dark/Light) (B20)
- **Priority**: LOW
- **Research label**: None (frontend implementation task)
- **Depends on**: None
- **Scope**: CSS variable theme tokens + persisted user preference

---

## Notes

> **⚠️ STRATEGIC PIVOT (2026-03-05)**: Memgraph is the single source of truth. PostgreSQL + Redis + Alembic were replaced by Memgraph + Redis (Celery-only).

> **🚀 PLATFORM EXPANSION (2026-03-09)**: The platform now targets multi-asset autonomous trading with per-asset bots, regime-aware strategy selection, and custom TA-Lib strategies.

Historical plans and completed sprint items have been moved to DONE.md.
