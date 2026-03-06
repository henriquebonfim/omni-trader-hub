---
description: /handle-po-review
---

# Handle PO Review

Full Product Owner cycle: aggregate → health check → live review → triage → write planning files.

---

## Step 1 — SOP Validation Gate

```bash
python3 .agent/scripts/orchestrator.py handle-po-review
ENFORCE_EXIT=$?
[ $ENFORCE_EXIT -ne 0 ] && echo "❌ SOP validation failed" && exit 1

WORKFLOW_NAME="handle-po-review"
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

## Step 2 — Load Skill

> **sequential-thinking**: Review product state → assess Docker/test health → evaluate backlog freshness → determine triage priorities → balance strategic vs tactical work.

```
po-lifecycle-orchestrator
```

## Step 3 — Setup

```bash
mkdir -p .agent/tmp
```

## Step 4 — Context Scan

```bash
[ -f tasks/TASKS.md ]   && cat tasks/TASKS.md
[ -f tasks/TODO.md ]    && cat tasks/TODO.md
[ -f tasks/BACKLOG.md ] && cat tasks/BACKLOG.md
[ -f README.md ]  && head -80 README.md
```

## Step 5 — Aggregate Issues

```bash
echo "Skipping bash gh CLI — data is now fetched natively in Python."
```

## Step 6 — System Health

```bash
make build 2>&1 | tail -20; echo "Build: $?"
make test  2>&1 | tail -20; echo "Tests: $?"
```

> **STRICT**: Use `make` targets only. Never guess package managers.

## Step 7 — Visual Review (browser-agent)

Detect app URL → invoke browser-agent for live product review → record findings in `tmp/visual-review.json`.

## Step 8 — Triage

```bash
make po-triage ARGS="--output-dir .agent/tmp/"
```

## Step 9 — Post to GitHub

```bash
make po-post ARGS="--matrix .agent/tmp/triage-matrix.json"
git add tasks/TASKS.md tasks/TODO.md tasks/BACKLOG.md
git commit -m "chore(po): update planning files — $(date +%Y-%m-%d)"
```

## Step 10 — Cleanup

```bash
make clean-tmp
```

---

## Success: tasks/TASKS.md + tasks/TODO.md + tasks/BACKLOG.md updated · Issues commented · Ready for `/start-workflow`
