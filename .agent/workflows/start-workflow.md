---
description: /start-workflow
---

# Start Workflow

Full-cycle orchestration: PO review → triage → score → implement → PR → review → merge → release.

Always begins with a PO health check to ensure planning files are current before any engineering starts.

---

## Step 0 — PO Health Check

Before engineering, confirm planning files are current:

```bash
# Are planning files fresh? (< 24h)
TASKS_AGE=$(( ($(date +%s) - $(stat -c %Y TASKS.md 2>/dev/null || echo 0)) / 3600 ))
echo "TASKS.md age: ${TASKS_AGE}h"

[ $TASKS_AGE -gt 24 ] \
  && echo "⚠️  TASKS.md stale — running /handle-po-review first" \
  || echo "✅ TASKS.md current"
```

If TASKS.md is stale or doesn't exist:
```
→ Run /handle-po-review first
```

If TASKS.md is current and Docker + tests are passing:
```
→ Continue to Step 1
```

---

## Step 1 — Strategic Context Scan

```bash
[ -f TODO.md ]   && cat TODO.md | head -40
[ -f README.md ] && head -80 README.md

# Check what's already in-flight
gh pr list --state open \
  --json number,title,headRefName,author \
  --jq '.[] | "#\(.number) [\(.headRefName)] \(.title)"'

# Recent velocity
gh pr list --state merged --limit 10 \
  --json number,title,mergedAt \
  --jq '.[] | "\(.mergedAt[:10]) #\(.number) \(.title)"'
```

---

## Step 2 — Issue Processing (if new issues since last triage)

```bash
# Quick check: new issues since last triage
gh issue list --state open --json number,createdAt \
  --jq '[.[] | select(.createdAt > "'"$(date -d '24 hours ago' --iso-8601=seconds 2>/dev/null || date -v-24H +%Y-%m-%dT%H:%M:%S 2>/dev/null || echo '2000-01-01')"'")] | length'
```

If new issues detected: `/handle-backlog-triage` (lightweight — just updates planning files)

Otherwise: proceed with current TASKS.md

---

## Step 3 — Pick Top Priority Task

Read TASKS.md and identify the top unstarted item:

```bash
cat TASKS.md | head -50
```

Cross-check:
- Not already assigned as an open PR
- Not already in a Jules session (`jules remote list --session`)
- Engineering prerequisites met (Docker + tests green)

---

## Step 4 — Jules Task Assignment

Build enriched task description from the TASKS.md item and issue body:

```bash
TASK_BODY=$(cat <<'EOF'
## Task: <title from TASKS.md>

**Closes:** #<issue_number>
**Priority:** <Critical|High|Sprint>
**Source:** TASKS.md — $(date +%Y-%m-%d)

### Context
<2-3 sentences from issue body>

### Acceptance Criteria
- [ ] <specific testable criterion>
- [ ] <specific testable criterion>
- [ ] All existing tests pass
- [ ] New tests cover changed behavior
- [ ] CHANGELOG.md updated under [Unreleased]

### Technical Notes
<Architecture constraints, relevant files, patterns to follow>

### Definition of Done
- [ ] PR created with Closes #N
- [ ] CI passing
- [ ] No regressions
- [ ] Visual review: no new broken routes
EOF
)

jules new --repo <owner>/<repo> "$TASK_BODY"
```

For parallel tasks:
```bash
jules new --repo <owner>/<repo> --parallel 2 "$TASK_BODY"
```

---

## Step 5 — Monitor Jules Session

```bash
jules remote list --session
```

When Jules creates a PR → Step 6

If Jules needs correction:
```bash
gh pr comment <N> --body "@jules <specific correction>"
```

---

## Step 6 — Code Review

```bash
/handle-pr-review <PR_NUMBER>
```

If changes needed:
```bash
/handle-pr-code <PR_NUMBER>
```

---

## Step 7 — Merge

```bash
/handle-close-pr <PR_NUMBER>
```

---

## Step 8 — Release (when milestone complete)

Count unreleased commits:
```bash
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "none")
[ "$LAST_TAG" != "none" ] \
  && git log ${LAST_TAG}..HEAD --oneline | wc -l \
  || echo "No tags yet"
```

If significant (5+ commits or milestone complete):
```bash
/handle-release
```

---

## Step 9 — Loop

```bash
# Remove completed item from TASKS.md
# Pick next item
# Return to Step 4
```

Update planning files after each completed item:
- Remove done item from TASKS.md
- Promote top TODO item to TASKS.md if TASKS is now empty
- Track velocity: `Avg cycle: Xh per task`

---

## Abort Conditions

- Protected branch violation → STOP, never force-push
- Test suite broken → Fix before assigning new work
- Docker broken → Fix before assigning new work
- TASKS.md empty → Run `/handle-po-review` to get new priorities

---

## Specialized Commands Reference

| Task type | Command |
|-----------|---------|
| Full sprint start | `/handle-po-review` |
| Quick daily triage | `/handle-backlog-triage` |
| Process open issues | `/handle-issues` |
| Direct implementation | `/handle-code "<task>"` |
| Review PR | `/handle-pr-review <N>` |
| Fix PR feedback | `/handle-pr-code <N>` |
| Merge PR | `/handle-close-pr <N>` |
| Ship release | `/handle-release` |
| Any UI task | load `ui-ux-pro-max` skill first |
