---
description: /handle-close-pr <PR_NUMBER>
---

# Handle Close PR

Merge a PR, clean up branches, and optionally clean up Jules sessions.

---

## Execution Sequence

### 1 — Pre-merge Validation

```bash
# Confirm PR is ready to merge
gh pr view <PR_NUMBER> \
  --json number,title,state,mergeable,mergeStateStatus,statusCheckRollup \
  --jq '{number,title,state,mergeable,mergeState:.mergeStateStatus}'

# Confirm all checks pass
gh pr checks <PR_NUMBER>

# Confirm no outstanding review requests
gh pr view <PR_NUMBER> --json reviewDecision \
  --jq '.reviewDecision'  # Should be "APPROVED" or "REVIEW_REQUIRED" with approvals
```

### 2 — Merge

```bash
# Standard merge (use --squash or --rebase per repo convention)
gh pr merge <PR_NUMBER> \
  --merge \
  --delete-branch \
  --subject "$(gh pr view <PR_NUMBER> --json title --jq .title)"
```

Check repo convention first:

```bash
gh repo view --json mergeCommitAllowed,squashMergeAllowed,rebaseMergeAllowed \
  --jq '{merge:.mergeCommitAllowed, squash:.squashMergeAllowed, rebase:.rebaseMergeAllowed}'
```

### 3 — Post-merge Cleanup

```bash
# Switch back to main and pull
git checkout main
git pull origin main

# Confirm local branch is gone
git branch | grep -v "^\* main"

# Prune remote tracking refs
git remote prune origin
```

### 4 — Jules Session Cleanup (if applicable)

```bash
# List active sessions
COLUMNS=200 jules remote list --session | cat

# Pull final state of any sessions related to this PR
# jules remote pull --session <SESSION_ID>

# No explicit session deletion needed — sessions expire automatically
# But document which session ID was used for this PR for traceability
```

### 5 — Verify

```bash
gh pr view <PR_NUMBER> --json state --jq .state  # Should be "MERGED"
git log --oneline -3  # Confirm merge commit present
```

### 6 — Cleanup

```bash
# Clear any tmp files from the PR workflow
rm -f .agent/skills/pr-code-orchestrator/tmp/*
rm -f .agent/skills/pr-review-orchestrator/tmp/*
```

---

## Abort Conditions

- PR has merge conflicts → resolve first
- CI checks failing → fix before merging
- Outstanding review requests → get approval first
- Invalid PR number

## Success Condition

- PR state is MERGED
- Head branch deleted (remote + local)
- `git status` clean on main
- Jules sessions noted / cleaned up
