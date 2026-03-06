---
description: /handle-issues
---

# Handle Issues

Full issue triage, implementation, and PR creation pipeline.

---

## Execution Sequence

### 1 — SOP Validation Gate

```bash
python3 .agent/scripts/orchestrator.py handle-issues
ENFORCE_EXIT=$?
[ $ENFORCE_EXIT -ne 0 ] && echo "❌ SOP validation failed" && exit 1

WORKFLOW_NAME="handle-issues"
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

### 2 — Environment Setup

```bash
mkdir -p .agent/tmp
grep -qxF '.agent/tmp/' .gitignore \
  || echo '.agent/tmp/' >> .gitignore
```

> **sequential-thinking**: Review open issues → assess priority signals (labels, age, assignee) → evaluate scope and risk → determine triage strategy.

### 3 — Load Skill

```
issue-task-orchestrator
```

### 4 — Fetch & Score Issues

```bash
# Fetching, scoring, and ranking is handled natively in Python
make issue-score

# Score and rank
make issue-score
```

### 5 — Engineering Validation

For each CONFIRMED issue from the matrix:
- View full issue: `gh issue view <N> --json number,title,body,comments`
- Validate scope alignment
- Confirm not already fixed
- Refine status if needed

### 6 — Post Structured Replies

```bash
make issue-post
```

### 7 — Implement Confirmed Tasks

For each CONFIRMED issue in priority order:

```
/handle-code "<scoped task>"
```

Each commit must include `Closes #<N>`.

### 9 — Generate TASKS.md

```bash
make issue-tasks
```

### 10 — Create Batch PR

```bash
ISSUE_CLOSES=$(jq -r '.[] | select(.status=="CONFIRMED") | "Closes #\(.issue_number)"' .agent/tmp/issue-matrix.json 2>/dev/null || true)

gh pr create \
  --title "feat: resolve confirmed issues batch $(date +%Y-%m-%d)" \
  --body "## Batch Issue Resolution

${ISSUE_CLOSES}

## Changes
$(git log origin/main..HEAD --oneline --no-merges)

---
- [ ] All tests passing
- [ ] CHANGELOG updated
- [ ] No unrelated changes"
```

### 11 — Cleanup

```bash
make clean-tmp
```

### 12 — Final Validation

```bash
gh pr view  # Confirm PR created
git status  # Confirm clean
```

---

## Abort Conditions

- Cannot switch off protected branch
- Test suite globally unstable (fix before issuing new work)
- Massive architectural redesign required for any single issue

---

## Success Condition

- All open issues classified and replied to
- Confirmed ones implemented on feature branch
- PR created with `Closes #N` for each
- `tmp/` clean
- TASKS.md generated for Jules handoff
