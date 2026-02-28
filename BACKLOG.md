# Backlog

Items requiring design, external decisions, or lower priority. Reviewed each sprint — graduate to TODO when ready.

> Last updated: 2026-02-28 by PO Lifecycle Orchestrator

---

## Agent Infrastructure & Reliability

Improvements identified during the Feb 2026 Architectural Review.

- [ ] **Mitigate Shell Argument Limits**: Refactor `make` targets to stop passing large JSON strings/bodies via CLI arguments. Use temporary file-exchange protocols instead.

#
