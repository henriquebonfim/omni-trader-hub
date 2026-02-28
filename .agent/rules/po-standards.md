---
trigger: model_decision
description: triage, planning file management (TASKS.md, TODO.md, BACKLOG.md), Docker health checks, visual review, and sprint planning. Apply whenever triage, backlog, sprint planning, product review, or planning file updates are involved.
---

# PO Standards

Rules for maintaining a healthy, trustworthy planning system. Every decision must be traceable, every file must be current, every item must live in exactly one place.

---

## Planning File Hierarchy

Three files, three distinct purposes. Never mix them:

| File | Purpose | Horizon | Items are... |
|------|---------|---------|-------------|
| `TASKS.md` | Immediate priority work | This sprint | Assigned or in-progress NOW |
| `TODO.md` | Confirmed next work | Next sprint | Validated, scoped, ready to assign |
| `BACKLOG.md` | Long-term and deferred | Future | Not yet scheduled — needs design, decision, or sequencing |

**Rules:**
- Every item lives in exactly ONE file. No duplicates across files.
- TASKS.md items must be actionable today — if not, move to TODO.
- TODO.md items must have enough detail to be handed to an engineer without clarification.
- BACKLOG.md items may be vague — they're waiting for clarification.
- Completed items are removed from planning files, not marked done. Git history is the record.

---

## Triage Rules (Non-Negotiable Order)

Apply in this order — first matching rule wins:

1. **Skip** — Issue already fixed by merged PR, or open PR in-flight, or labeled `wontfix`/`invalid`
2. **TASKS** — Any: security vulnerability · blocker · critical label · failing test · Docker broken · milestone overdue · manual override `triage:tasks`
3. **TODO** — Any: `bug` + non-critical · `feature` + clear scope · `priority: medium` · recent activity (< 14 days)
4. **BACKLOG** — Everything else

Override mechanism: apply GitHub labels `triage:tasks`, `triage:todo`, or `triage:backlog` to manually override automated triage. Always respected.

---

## Docker Health

Before any PO review:

```bash
make build 2>&1 | tail -20
```

Docker failures are TASKS-level blockers.

---

## Visual Review

Use browser-agent for live review. Minimum routes:
- `/` — Landing
- Auth entry point
- Main feature route
- Dashboard
- Any previously broken route

Broken core routes → TASKS.md. Secondary issues → TODO.md.

---

## Planning File Format Standards

### TASKS.md
- Always has system health line at top: `Docker [PASS|FAIL] · Tests [PASS|FAIL]`
- Items grouped: 🔴 Critical → 🟠 High Priority → 🟡 This Sprint
- Each item has: issue ref, label tags, acceptance criteria direction
- Never more than ~15 items — if more exist, lower-priority items belong in TODO

### TODO.md
- Items grouped by type: Bugs → Features → UI/Design → Refactors → Other
- Each item has enough context for an engineer to start without asking questions
- Links to related issues and PRs

### BACKLOG.md
- Items grouped: Ideas → Tech Debt → Needs Discussion → Stale
- Stale section: items 30+ days old with no activity
- Reviewed each sprint — items that become relevant graduate to TODO

---

## Sprint Planning Gate

Before running `/start-workflow` or assigning Jules tasks:

1. `TASKS.md` must be current (< 24 hours since last update OR manually confirmed current)
2. Docker build must pass
3. Test suite must pass (or failing tests must already be in TASKS.md)
4. Top item in TASKS.md must have clear acceptance criteria

If any fail → run `/handle-po-review` before engineering work begins.

---

## GitHub Issue Hygiene

After triage:
- Post one structured comment per issue with its bucket assignment
- Close issues labeled `wontfix`, `invalid`, `duplicate` with appropriate reason
- Milestone check: issues in active milestone with no assignee → escalate to TODO

Never:
- Create duplicate GitHub issues
- Leave issues uncommented for > 7 days after triage
- Have the same issue in multiple planning files

---

## Integration Handoffs

| PO output | Engineering input |
|-----------|-------------------|
| TASKS.md top item | `/start-workflow` → picks it up |
| TASKS.md specific issue | `/handle-issues` → processes it |
| TASKS.md failing test | `/handle-code "fix: failing test <name>"` |
| TASKS.md Docker broken | `/handle-code "fix: docker build failure"` |
| TODO.md batch | `/handle-issues` → processes confirmed items |
| Visual finding | `/handle-code "fix: <route> — <issue>"` |

The PO lifecycle output directly feeds the engineering pipeline. The files are the contract between product and engineering.
