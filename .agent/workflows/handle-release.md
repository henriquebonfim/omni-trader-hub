---
description: /handle-release [--dry-run]
---

# Handle Release

Prepare and publish a versioned release using the release-manager skill.

---

## Execution Sequence

### 1 — Load Skill

```
release-manager
```

### 2 — Pre-flight

```bash
# Confirm on main/master
git branch --show-current

# Confirm clean working tree
git status --short

# Check CI on HEAD
gh run list --branch main --limit 3 \
  --json status,conclusion,workflowName \
  --jq '.[] | "\(.workflowName): \(.conclusion)"'
```

### 3 — Dry Run (optional)

If user passed `--dry-run` or wants to preview:

```
release-manager → Phase 0, 1, 2, 3, 4 only
```

Present proposed version, changelog entry, and release body. Stop before executing.

### 4 — Execute Release

Run all phases from the skill:

1. Phase 0 — Pre-flight checks
2. Phase 1 — Detect release context  
3. Phase 2 — Classify commits
4. Phase 3 — Version recommendation + user confirmation
5. Phase 4 — Generate release notes
6. Phase 5 — Execute (bump → commit → tag → push → gh release create)
7. Phase 6 — Verify
8. Phase 7 — Cleanup

### 5 — Announce (optional)

```bash
# View the live release
gh release view "v<VERSION>" --web
```

---

## Abort Conditions

- Dirty working tree
- CI failing on HEAD
- No commits since last tag (nothing to release)

## Success Condition

- Tag pushed to remote
- GitHub release published
- CHANGELOG.md updated
- `git status` clean
