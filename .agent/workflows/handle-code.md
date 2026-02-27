---
description: /handle-code <short_description>
---

# Handle Code

Direct implementation via software-engineer-worker. Use for scoped tasks.

---

## Execution Sequence

### 1 — Load Skill

```
software-engineer-worker
```

### 2 — Branch Safety

```bash
BRANCH=$(git branch --show-current)
[[ "$BRANCH" == "main" || "$BRANCH" == "master" || "$BRANCH" == "production" ]] \
  && echo "WARNING: On protected branch — ensure this is intentional"
```

### 3 — Execute

Run all phases from the skill:

1. Stack Detection (Phase 0)
2. Thinking Protocol (Phase 1)
3. Discovery (Phase 2)
4. Design (Phase 3)
5. Veto Checkpoint (Phase 4)
6. Implementation (Phase 5)
7. Documentation Update — including CHANGELOG (Phase 6)
8. Self-Correction & Verification (Phase 7) ← MANDATORY
9. Final Validation (Phase 8)
10. Self-healing loop if needed

### 4 — Post-Implementation Check

```bash
git diff --stat HEAD    # Confirm minimal scoped diff
git status             # Confirm clean
git log --oneline -3   # Confirm clean history
```

---

## Abort Conditions

- Architectural redesign required beyond scope
- Requirements unclear after review
- Test suite cannot be stabilized safely

## Success Condition

- Feature or fix implemented
- Build green, tests passing, lint clean
- CHANGELOG.md updated
- No unrelated changes in diff
