---
description: /handle-issues
---

# Handle Issues

Full issue triage, implementation, and PR creation pipeline.

---

## Execution Sequence

### 1 — Environment Setup

```bash
mkdir -p .agent/tmp
grep -qxF '.agent/tmp/' .gitignore \
  || echo '.agent/tmp/' >> .gitignore
```

### 2 — Load Skill

```
issue-task-orchestrator
```

### 3 — Branch Safety

```bash
BRANCH=$(git branch --show-current)
if [[ "$BRANCH" == "main" || "$BRANCH" == "master" || "$BRANCH" == "production" ]]; then
  git checkout -b "feature/issues-batch-$(date +%Y%m%d%H%M%S)"
fi
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

### 8 — Generate TASKS.md

```bash
make issue-tasks
```

### 9 — Create Batch PR

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

### 10 — Cleanup

```bash
make clean-tmp
```

### 11 — Final Validation

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
