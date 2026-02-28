---
description: /handle-code <short_description>
---

# Handle Code

Direct implementation via software-engineer-worker.

---

## Execution

### 1 — Think First

> **sequential-thinking** (MANDATORY): Restate task → assess scope → trace affected files → plan changes → evaluate risk.

### 2 — Branch Safety

```bash
BRANCH=$(git branch --show-current)
[[ "$BRANCH" == "main" || "$BRANCH" == "master" ]] \
  && echo "WARNING: On protected branch"
```

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
