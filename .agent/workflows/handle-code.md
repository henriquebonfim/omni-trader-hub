---
description: /handle-code <short_description>
---

# Handle Code

Direct implementation via software-engineer-worker.

---

## Execution

### 1 — SOP Validation Gate

```bash
python3 .agent/scripts/orchestrator.py handle-code
ENFORCE_EXIT=$?
[ $ENFORCE_EXIT -ne 0 ] && echo "❌ SOP validation failed" && exit 1

WORKFLOW_NAME="handle-code"
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

### 2 — Think First

> **sequential-thinking** (MANDATORY): Restate task → assess scope → trace affected files → plan changes → evaluate risk.

### 3 — Load Skill & Execute

```
software-engineer-worker (all phases)
```

### 4 — Verify

```bash
git diff --stat HEAD
git status
git log --oneline -3
```

---

## Abort: Architectural redesign required · Requirements unclear · Test suite unstable

## Success: Feature/fix implemented · `make test` green · CHANGELOG updated · Clean diff
