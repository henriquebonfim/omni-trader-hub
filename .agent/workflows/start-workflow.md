---
description: /start-workflow
---

# Start Workflow

Full-cycle: PO review → triage → implement → PR → review → merge → release.

DDD mode: every change must preserve bounded contexts, explicit layer boundaries, and dependency direction.

---

## DDD Guardrail Defaults

- Keep domain rules in domain/application layers; keep orchestration thin.
- Prevent cross-context leakage and architecture shortcuts.
- Require `make ddd-guard` to pass before review/merge.

---

## Step 0 — SOP Validation Gate

```bash
python3 .agent/scripts/orchestrator.py start-workflow
ENFORCE_EXIT=$?
[ $ENFORCE_EXIT -ne 0 ] && echo "❌ SOP validation failed" && exit 1

WORKFLOW_NAME="start-workflow"
cleanup_workflow() {
  EXIT_CODE=$?
  if [ $EXIT_CODE -ne 0 ]; then
    python3 .agent/scripts/friction_logger.py \
      --task "$WORKFLOW_NAME" \
      --type "Workflow" \
      --friction "Workflow exited with code $EXIT_CODE" \
      --resolution "Inspect workflow output and rerun after fix" || true
  fi
  make clean-tmp >/dev/null 2>&1 || true
}
trap cleanup_workflow EXIT
```

---

## Step 1 — PO Gate

> **sequential-thinking**: Assess tasks/TASKS.md freshness, Docker health, test status, and DDD boundary health. Decide: proceed or run `/handle-po-review` first.

```bash
TASKS_AGE=$(( ($(date +%s) - $(stat -c %Y tasks/TASKS.md 2>/dev/null || echo 0)) / 3600 ))
echo "tasks/TASKS.md age: ${TASKS_AGE}h"
[ $TASKS_AGE -gt 24 ] && echo "⚠️  Stale — run /handle-po-review" || echo "✅ Current"

# Quick DDD boundary sanity
make ddd-guard || true
```

If stale → `/handle-po-review` first. If current → Step 2.

---

## Step 2 — Context Scan

```bash
[ -f tasks/TODO.md ] && head -40 tasks/TODO.md
gh pr list --state open --json number,title,headRefName --jq '.[] | "#\(.number) \(.title)"'
gh pr list --state merged --limit 10 --json number,title,mergedAt --jq '.[] | "\(.mergedAt[:10]) #\(.number) \(.title)"'
```

---

## Step 3 — New Issues Check

```bash
gh issue list --state open --json number,createdAt \
  --jq '[.[] | select(.createdAt > "'"$(date -d '24 hours ago' --iso-8601=seconds 2>/dev/null || echo '2000-01-01')"'")] | length'
```

New issues → `/handle-backlog-triage`. Otherwise → Step 3.

---

## Step 4 — Pick Top Task

> **sequential-thinking**: Read tasks/TASKS.md. Validate top item is not already an open PR or Jules session. Confirm prerequisites (Docker + tests green via `make build && make test`).
>
> DDD checks before dispatch:
- Map task to one bounded context.
- Define expected layer changes (`domain`, `application`, `infrastructure`).
- Reject tasks that bypass boundaries or dependency direction.

```bash
cat tasks/TASKS.md | head -50
```

---

## Step 5 — Jules Dispatch & Poll

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

# DDD architecture boundary gate (mandatory)
make ddd-guard
```

---

## Step 6 — Code Review

```
/handle-pr-review <PR_NUMBER>
```

If changes needed → `/handle-pr-code <PR_NUMBER>`

---

## Step 7 — Merge

```
/handle-close-pr <PR_NUMBER>
```

---

## Step 8 — Release (when milestone complete)

```bash
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "none")
[ "$LAST_TAG" != "none" ] && git log ${LAST_TAG}..HEAD --oneline | wc -l || echo "No tags"
```

If 5+ commits or milestone complete → `/handle-release`

---

## Step 9 — Loop

Remove completed item from tasks/TASKS.md. Pick next. Return to Step 4.

---

## Abort Conditions

- Protected branch violation → STOP
- Test suite broken → fix first
- Docker broken → fix first
- TASKS.md empty → `/handle-po-review`
- `make ddd-guard` fails → STOP and fix before review
