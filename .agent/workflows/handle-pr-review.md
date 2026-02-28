---
description: /handle-pr-review <PR_NUMBER>
---

# Handle PR Review

Read-only code review with runtime validation. No code changes.

---

## Execution Sequence

### 1 — Setup

```bash
mkdir -p .agent/tmp
grep -qxF '.agent/tmp/' .gitignore \
  || echo '.agent/tmp/' >> .gitignore
```

### 2 — Load Skill

```
pr-review-orchestrator
```

### 3 — Checkout

```bash
gh pr checkout <PR_NUMBER>

# Validate branch
EXPECTED=$(gh pr view <PR_NUMBER> --json headRefName --jq .headRefName)
CURRENT=$(git branch --show-current)
echo "Expected: $EXPECTED | Current: $CURRENT"
```

### 4 — Execute Review

- Runtime validation (build, lint, typecheck, tests) → `tmp/runtime-summary.json`
- Full diff analysis → `tmp/review-matrix.json`
- Risk classification
- Submit batched review via `post_review.py`

```bash
make pr-review PR=<PR_NUMBER>
```

### 5 — Verify No Changes Made

```bash
git status          # Must be clean
git log --oneline -3  # Must be unchanged from checkout
```

### 6 — Cleanup

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
