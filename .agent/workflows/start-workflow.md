---
description: /start-workflow
---

# Start Workflow

Full-cycle: PO review → triage → implement → PR → review → merge → release.

---

## Step 0 — PO Gate

> **sequential-thinking**: Assess TASKS.md freshness, Docker health, test status. Decide: proceed or run `/handle-po-review` first.

```bash
TASKS_AGE=$(( ($(date +%s) - $(stat -c %Y TASKS.md 2>/dev/null || echo 0)) / 3600 ))
echo "TASKS.md age: ${TASKS_AGE}h"
[ $TASKS_AGE -gt 24 ] && echo "⚠️  Stale — run /handle-po-review" || echo "✅ Current"
```

If stale → `/handle-po-review` first. If current → Step 1.

---

## Step 1 — Context Scan

```bash
[ -f TODO.md ] && head -40 TODO.md
gh pr list --state open --json number,title,headRefName --jq '.[] | "#\(.number) \(.title)"'
gh pr list --state merged --limit 10 --json number,title,mergedAt --jq '.[] | "\(.mergedAt[:10]) #\(.number) \(.title)"'
```

---

## Step 2 — New Issues Check

```bash
gh issue list --state open --json number,createdAt \
  --jq '[.[] | select(.createdAt > "'"$(date -d '24 hours ago' --iso-8601=seconds 2>/dev/null || echo '2000-01-01')"'")] | length'
```

New issues → `/handle-backlog-triage`. Otherwise → Step 3.

---

## Step 3 — Pick Top Task

> **sequential-thinking**: Read TASKS.md. Validate top item is not already an open PR or Jules session. Confirm prerequisites (Docker + tests green via `make build && make test`).

```bash
cat TASKS.md | head -50
```

---

## Step 4 — Jules Dispatch & Poll

> **sequential-thinking**: Think → Dispatch → Poll → Pull → Verify. Polling is async to avoid blocking.

**Think**: Build enriched task description from TASKS.md item. Include context, constraints, and acceptance criteria.

```bash
make j-dispatch ARGS="--repo <owner>/<repo>" TASK="<enriched task>"
```

**Poll**: Monitor session for completion. This can be run in the background if needed.

```bash
make j-status ID=<id>
# Or use the polling script for automated wait
make j-poll ID=<id>
```

**Pull + Verify**: Once the status indicates completion (or the session is no longer in the active list).

```bash
git checkout -b feature/<task-slug>
make j-pull ID=<id>
make test && make lint
```

---

## Step 5 — Code Review

```
/handle-pr-review <PR_NUMBER>
```

If changes needed → `/handle-pr-code <PR_NUMBER>`

---

## Step 6 — Merge

```
/handle-close-pr <PR_NUMBER>
```

---

## Step 7 — Release (when milestone complete)

```bash
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "none")
[ "$LAST_TAG" != "none" ] && git log ${LAST_TAG}..HEAD --oneline | wc -l || echo "No tags"
```

If 5+ commits or milestone complete → `/handle-release`

---

## Step 8 — Loop

Remove completed item from TASKS.md. Pick next. Return to Step 3.

---

## Abort Conditions

- Protected branch violation → STOP
- Test suite broken → fix first
- Docker broken → fix first
- TASKS.md empty → `/handle-po-review`
