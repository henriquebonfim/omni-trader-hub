---
description: /handle-pr-review <PR_NUMBER>
---

# Handle PR Review

Read-only code review with runtime validation. No code changes.

---

## Execution Sequence

### 1 — SOP Validation Gate

```bash
python3 .agent/scripts/orchestrator.py handle-pr-review
ENFORCE_EXIT=$?
[ $ENFORCE_EXIT -ne 0 ] && echo "❌ SOP validation failed" && exit 1

WORKFLOW_NAME="handle-pr-review"
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

### 2 — Setup

```bash
mkdir -p .agent/tmp
grep -qxF '.agent/tmp/' .gitignore \
  || echo '.agent/tmp/' >> .gitignore
```

### 3 — Load Skill

```
pr-review-orchestrator
```

### 4 — Checkout

```bash
gh pr checkout <PR_NUMBER>

# Validate branch
EXPECTED=$(gh pr view <PR_NUMBER> --json headRefName --jq .headRefName)
CURRENT=$(git branch --show-current)
echo "Expected: $EXPECTED | Current: $CURRENT"
```

### 5 — Execute Review

- Runtime validation (build, lint, typecheck, tests) → `tmp/runtime-summary.json`
- Full diff analysis → `tmp/review-matrix.json`
- Risk classification
- Submit batched review via `post_review.py`

```bash
make pr-review PR=<PR_NUMBER>
```

### 6 — Verify No Changes Made

```bash
git status          # Must be clean
git log --oneline -3  # Must be unchanged from checkout
```

### 7 — Cleanup

```bash
make clean-tmp
```

---

## Abort Conditions

- PR cannot be checked out
- Repository in unstable state

## Success Condition

- All changed files analyzed
- Structured review submitted via `gh api`
- Risk level stated
- Zero code modifications
- `tmp/` empty
