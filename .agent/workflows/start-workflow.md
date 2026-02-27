---
description: /start-workflow
---

# Start Workflow

Full-cycle orchestration: triage issues → score by priority → assign top task to Jules → review PR → merge → repeat.

---

## Step 1 — Strategic Context Scan

Build project context before touching issues:

```bash
# Product context
[ -f TODO.md ]   && cat TODO.md
[ -f README.md ] && head -80 README.md

# Avoid creating duplicate work
gh pr list --state open \
  --json number,title,headRefName,author \
  --jq '.[] | "#\(.number) [\(.headRefName)] \(.title)"'

# Understand recent velocity
gh pr list --state merged --limit 10 \
  --json number,title,mergedAt \
  --jq '.[] | "\(.mergedAt[:10]) #\(.number) \(.title)"'

# Snapshot open issue count by label
gh issue list --state open --limit 100 \
  --json number,title,labels \
  --jq 'group_by(.labels[0].name // "unlabeled") | .[] | {label: .[0].labels[0].name, count: length}'
```

Use Sequential Thinking MCP (if available) to reason about:
- Current product focus and momentum
- Highest-risk open items
- Blocking dependencies between issues

---

## Step 2 — Process Issues

```
/handle-issues
```

This classifies all open issues, posts structured replies, implements confirmed tasks, creates a batch PR, and generates `TASKS.md`.

---

## Step 3 — Priority Review

After `/handle-issues` completes, review the ranked task list:

```bash
# View generated task priority ranking
cat TASKS.md

# Cross-reference against open PRs (don't assign work already in flight)
gh pr list --state open --json number,title,body \
  --jq '.[] | "PR #\(.number): \(.title)"'

# Check if Jules already has active sessions
jules remote list --session
```

Confirm with user which task to assign next, or proceed automatically with #1.

---

## Step 4 — Jules Assignment

Build an enriched task description from TASKS.md and assign:

```bash
REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)

# Read top confirmed task
TASK_TITLE="<title from TASKS.md>"
TASK_ISSUE="#<issue number>"
TASK_CONTEXT="<body from issue>"

jules new --repo "${REPO}" \
"## Task: ${TASK_TITLE}

**Closes:** ${TASK_ISSUE}

### Context
${TASK_CONTEXT}

### Acceptance Criteria
- [ ] Root cause addressed (bugs) or feature fully implemented
- [ ] Unit/integration tests cover the new behavior
- [ ] All existing tests still pass
- [ ] CHANGELOG.md updated under [Unreleased]
- [ ] No unrelated file changes

### Technical Constraints
- Follow existing patterns in the codebase
- Keep commits conventional: feat/fix/refactor/test/chore
- One logical change per commit

### Definition of Done
- PR created referencing ${TASK_ISSUE}
- CI green
- All acceptance criteria checked"
```

For parallel workstreams (2nd and 3rd ranked tasks ready simultaneously):

```bash
jules new --repo "${REPO}" --parallel 2 "<task description>"
```

---

## Step 5 — Monitor Jules

```bash
# Check session status
jules remote list --session

# When Jules completes and creates a PR:
gh pr list --state open --json number,title,author \
  --jq '.[] | select(.author.login | startswith("jules")) | "#\(.number) \(.title)"'

# Pull the session result (without applying)
jules remote pull --session <SESSION_ID>

# OR: apply the patch to local repo for review
jules remote pull --session <SESSION_ID> --apply
# OR: teleport (clone repo + checkout branch + apply)
jules teleport <SESSION_ID>
```

---

## Step 6 — Code Review

```bash
# AI read-only review
/handle-pr-review <PR_NUMBER>
```

If changes are needed, comment on the PR and mention Jules:

```bash
gh pr comment <PR_NUMBER> --body "@jules <specific correction requested>"
```

If direct code fixes are faster:

```bash
/handle-pr-code <PR_NUMBER>
```

---

## Step 7 — Merge

```bash
/handle-close-pr <PR_NUMBER>
```

---

## Step 8 — Release (when milestone is complete)

Check if enough work has accumulated for a release:

```bash
# Count unreleased commits since last tag
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "none")
git log ${LAST_TAG}..HEAD --oneline --no-merges | wc -l
```

If significant work is merged, trigger:

```bash
# "Prepare a release for everything merged since vX.Y.Z"
# → activates release-manager skill
```

---

## Step 9 — Loop

Return to Step 3. Pick the next ranked task.

**Tracking velocity:**

```bash
# Issues closed this cycle
gh issue list --state closed \
  --search "closed:>$(date -d '7 days ago' +%Y-%m-%d)" \
  --json number --jq 'length'

# PRs merged this week
gh pr list --state merged \
  --search "merged:>$(date -d '7 days ago' +%Y-%m-%d)" \
  --json number --jq 'length'
```

---

## Available Skills Reference

| Skill | Invoke when... |
|-------|---------------|
| `ui-ux-pro-max` | Any frontend/UI work before writing component code |
| `software-engineer-worker` | Direct implementation (small tasks, no Jules needed) |
| `release-manager` | After merging a milestone batch, or on release day |
| `issue-task-orchestrator` | Triaging issues into scored, confirmed tasks |
| `pr-code-orchestrator` | Implementing PR review feedback |
| `pr-review-orchestrator` | Read-only code review before merge |

---

## Abort Conditions

- Protected branch violation detected → stop, investigate, never force-push
- CI globally broken → fix before assigning new work  
- Circular task dependencies → resolve with user before scoring
