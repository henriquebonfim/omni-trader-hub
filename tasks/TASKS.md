# OmniTrader — Technical Debt & Audit Findings

Single source of truth for all technical work: architecture items, audit-discovered bugs, and risk gaps.
Institutional-grade audit completed **2026-03-03** — findings integrated below.
Multi-asset autonomous platform expansion added **2026-03-09** — T37-T42 driven by frontend spec (PROMPT.md).
Last updated: 2026-03-11 | Sprint status: T32-T43 completed and merged to master. Next: TBD.
Frontend-backend integration migration added **2026-03-09** — T43 bridges new frontend to existing backend.

> Last updated: 2026-03-11 | Sprint status: T32-T43 completed and merged to master. Next: TBD

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
> **T37 COMPLETED**: ✅ Core bot management API, BotManager orchestrator, multi-bot CRUD/lifecycle, per-bot risk isolation, status aggregation (2026-03-10). See PR #70 + DONE.md.

### T38. Autonomous Strategy Selection Engine
> **T38 COMPLETED**: ✅ StrategySelector with composite scoring, eligibility gate, 4h cooldown, fallback; auto-mode integration with BotManager; manual override; GET /api/strategies/performance (2026-03-10). See PR #71 + DONE.md. Deferred: regime-driven position-close choreography on rotation.

### T39. TA-Lib Migration & Indicator Service
> **T39 COMPLETED**: ✅ All 5 strategies migrated to TA-Lib; indicator catalog (GET /api/indicators, startup-cached) and compute endpoint (POST /api/indicators/compute, 10 req/min rate-limited, auth required) implemented (2026-03-10). See PR #72 + DONE.md.

### T40. Custom Strategy System (CRUD + Execution)
> **T40 COMPLETED**: ✅ Custom strategy persistence, CRUD API, TA-Lib executor, and runtime integration delivered (2026-03-10). See PR #73 + DONE.md.

### T41. Environment Variable Management API
> **T41 COMPLETED**: ✅ Env reader/updater API with masking + atomic writes, and restart endpoint with open-position safety checks (2026-03-10). See Commit `9fca480` + DONE.md.

### T42. Markets Discovery API
> **T42 COMPLETED**: ✅ Markets discovery API with search/filter/Redis caching implemented (2026-03-10). See PR #74 + DONE.md.

---
## 🔵 Frontend Integration Bridge

> **Context (2026-03-09)**: The new React frontend (10 pages, full API client, WebSocket client) was previously using mock data on every page. T43 connected the frontend to the existing backend using adapter + stub layers so unimplemented features degrade gracefully. See DONE.md for the full T43 audit trail.

> **T43 COMPLETED**: ✅ Moved to DONE.md (2026-03-11). All 7 phases verified. See PR #75 + commit `101aa50`.

> **T44 COMPLETED**: ✅ Backend DDD migration complete (2026-03-09). See DONE.md.

---
## 🟠 High Priority (Correctness & Reliability)

---

## 🟡 Medium Priority (Hardening & Hygiene)

---
