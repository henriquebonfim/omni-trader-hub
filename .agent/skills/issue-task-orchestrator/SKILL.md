---
name: issue-task-orchestrator
description: Deterministic transformation of GitHub issues into validated engineering tasks with strict branch and PR enforcement. Trigger when user references reviewing issues, converting issues to tasks, processing backlog, triaging, or "handle my issues". Also activates for "what issues are open", "pick the next task", or any request to process GitHub issues into actionable work.
---

# Issue Task Orchestrator

Transforms open GitHub issues into validated, scored, and assigned engineering tasks. Integrates with the full gh + jules CLI pipeline.

---

## Setup Check

```bash
# Verify tooling
gh --version
jules version

# Ensure tmp/ exists and is gitignored
mkdir -p .agent/skills/issue-task-orchestrator/tmp
grep -qxF '.agent/skills/issue-task-orchestrator/tmp/' .gitignore \
  || echo '.agent/skills/issue-task-orchestrator/tmp/' >> .gitignore
```

---

## Phase 1 — Discovery

Fetch all open issues with full metadata in one call:

```bash
gh issue list \
  --state open \
  --limit 100 \
  --json number,title,body,labels,assignees,milestone,comments,createdAt,updatedAt \
  > .agent/skills/issue-task-orchestrator/tmp/raw-issues.json
```

Check for issues already in active PRs (avoid duplicate work):

```bash
gh pr list \
  --state open \
  --json number,title,body,headRefName \
  --jq '[.[] | {number,title,body,branch:.headRefName}]' \
  > .agent/skills/issue-task-orchestrator/tmp/open-prs.json
```

Check recent merged work to detect already-resolved issues:

```bash
gh pr list \
  --state merged \
  --limit 20 \
  --json number,title,body,mergedAt \
  --jq '[.[] | {number,title,body,mergedAt}]' \
  > .agent/skills/issue-task-orchestrator/tmp/recent-merged.json
```

---

## Phase 2 — Build Issue Matrix

Analyse each issue and write the matrix to tmp/:

```bash
# Schema: .agent/skills/issue-task-orchestrator/tmp/issue-matrix.json
```

```json
[
  {
    "issue_number": 42,
    "title": "...",
    "classification": "BUG|FEATURE|REFACTOR|DOC|DUPLICATE|INVALID|ALREADY_FIXED|NEEDS_INFO",
    "status": "CONFIRMED|NEEDS_CLARIFICATION|ALREADY_RESOLVED|INVALID",
    "priority_score": 0,
    "in_active_pr": false,
    "confirmed": false
  }
]
```

**Classification rules:**

| Label hint | Classification |
|------------|---------------|
| `bug`, `fix`, crash report | `BUG` |
| `feat`, `enhancement`, new behavior | `FEATURE` |
| `refactor`, `cleanup`, `debt` | `REFACTOR` |
| `docs`, `documentation` | `DOC` |
| References another issue | `DUPLICATE` |
| Already merged in recent PRs | `ALREADY_FIXED` |
| Missing repro steps / ambiguous | `NEEDS_INFO` |

**Priority scoring** (0–10 each axis):

| Axis | 10 | 5 | 1 |
|------|----|---|---|
| User Impact | Data loss/crash | Feature broken | Cosmetic |
| Effort (inverse) | < 1 hour | Half day | Multi-week |
| Dependency Unblock | Blocks 3+ issues | Blocks 1 | Standalone |
| Risk if Delayed | Security/compliance | User-facing bug | Nice-to-have |

`priority_score = (impact × 2) + effort + (unblock × 1.5) + risk`

---

## Phase 3 — Branch Safety (STRICT)

```bash
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"

# Abort if on protected branch
if [[ "$CURRENT_BRANCH" == "main" || "$CURRENT_BRANCH" == "master" || "$CURRENT_BRANCH" == "production" ]]; then
  TIMESTAMP=$(date +%Y%m%d%H%M%S)
  BRANCH="feature/issues-batch-${TIMESTAMP}"
  git checkout -b "$BRANCH"
  echo "Created branch: $BRANCH"
fi
```

---

## Phase 4 — Engineering Validation

For each issue with status `CONFIRMED`:

1. **Bug**: Attempt to locate the failing code path. Confirm it's not already patched.
2. **Feature**: Verify it aligns with project architecture. Confirm minimal viable scope.
3. **Refactor**: Validate it won't break public APIs.
4. **Already fixed?**: Cross-reference body text against `recent-merged.json` commits.

```bash
# View full issue detail including comments
gh issue view <NUMBER> \
  --json number,title,body,comments,labels,assignees \
  --jq '{number,title,body,labels:[.labels[].name],comments:[.comments[].body]}'
```

---

## Phase 5 — Post Structured Reply Per Issue

Use the script for consistent, automated replies:

```bash
python3 .agent/skills/issue-task-orchestrator/scripts/post_issue_comments.py
```

Manual format per issue status:

### ✅ CONFIRMED TASK
```bash
gh issue comment <NUMBER> --body "$(cat <<'EOF'
**Status: ✅ CONFIRMED TASK**

**Scope:**
- <Specific files/functions to be modified>
- <Test files to be created/updated>

**Priority Score:** <N>/40

**PR:** Will be included in upcoming batch PR
EOF
)"
```

### ❌ NEEDS CLARIFICATION
```bash
gh issue comment <NUMBER> --body "$(cat <<'EOF'
**Status: ❌ NEEDS CLARIFICATION**

**Missing:**
- <Specific information required>
- <Repro steps / acceptance criteria needed>
EOF
)"
```

### 🟢 ALREADY RESOLVED
```bash
gh issue comment <NUMBER> --body "**Status: 🟢 ALREADY RESOLVED**

**Evidence:** Resolved in PR #<N> / commit \`<sha>\`"

gh issue close <NUMBER> --reason completed --comment "Closing — already resolved."
```

### ⏭ INVALID / WON'T FIX
```bash
gh issue comment <NUMBER> --body "**Status: ⏭ INVALID**

**Reason:** <Technical explanation>"

gh issue close <NUMBER> --reason "not planned"
```

---

## Phase 6 — Implementation

For each CONFIRMED task in priority order, invoke:

```
/handle-code "<scoped task from issue>"
```

Each commit must reference the issue:
```
feat(module): implement feature X

Closes #<issue_number>
```

---

## Phase 7 — Jules Handoff (for complex tasks)

For issues that benefit from Jules' async execution:

```bash
# Read issue details for task description
ISSUE_BODY=$(gh issue view <NUMBER> \
  --json number,title,body,labels \
  --jq '"Issue #\(.number): \(.title)\n\nDescription:\n\(.body)\n\nLabels: \(.labels[].name)"')

# Create Jules session with enriched task description
jules new --repo $(gh repo view --json nameWithOwner -q .nameWithOwner) \
  "$(cat <<EOF
## Task: Fix Issue #<NUMBER>

**Closes:** #<NUMBER>
**Priority:** <score>

### Problem
${ISSUE_BODY}

### Acceptance Criteria
- [ ] Root cause addressed (not patched around)
- [ ] Regression test added that would have caught this
- [ ] All existing tests still pass
- [ ] CHANGELOG.md updated under [Unreleased]

### Definition of Done
- PR created referencing this issue
- CI green
- No unrelated file changes
EOF
)"
```

Track session IDs:

```bash
# List active sessions
jules remote list --session

# Check session status / pull result
jules remote pull --session <SESSION_ID>
```

---

## Phase 8 — Create Batch PR

After all confirmed tasks are implemented:

```bash
# Collect all closed issue numbers from matrix
ISSUE_REFS=$(python3 -c "
import json
matrix = json.load(open('.agent/skills/issue-task-orchestrator/tmp/issue-matrix.json'))
confirmed = [f'Closes #{i[\"issue_number\"]}' for i in matrix if i['status'] == 'CONFIRMED']
print('\n'.join(confirmed))
")

gh pr create \
  --title "feat: resolve confirmed issues batch $(date +%Y-%m-%d)" \
  --body "$(cat <<EOF
## Summary

This PR resolves all confirmed issues from the latest triage batch.

## Resolved Issues

${ISSUE_REFS}

## Changes

$(git log origin/main..HEAD --oneline --no-merges)

## Checklist
- [ ] All tests passing
- [ ] CHANGELOG.md updated
- [ ] No unrelated changes
EOF
)" \
  --label "batch-fix"
```

---

## Phase 9 — Cleanup

```bash
rm -f .agent/skills/issue-task-orchestrator/tmp/*.json
git status  # Confirm nothing staged accidentally
```

---

## Completion Criteria

- [ ] All issues classified and replied to
- [ ] Confirmed issues implemented on feature branch
- [ ] PR created referencing all `Closes #N`
- [ ] Protected branches untouched
- [ ] `tmp/` cleared
- [ ] `git status` clean (no temp files staged)
