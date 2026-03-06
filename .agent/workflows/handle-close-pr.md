---
description: /handle-close-pr <PR_NUMBER>
---

# Handle Close PR

Merge a PR, clean up branches, and optionally clean up Jules sessions.

---

## Execution Sequence

### 1 — SOP Validation Gate

```bash
python3 .agent/scripts/orchestrator.py handle-close-pr
ENFORCE_EXIT=$?
[ $ENFORCE_EXIT -ne 0 ] && echo "❌ SOP validation failed" && exit 1

WORKFLOW_NAME="handle-close-pr"
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

### 2 — Pre-merge Validation

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

### 3 — Merge

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

### 4 — Post-merge Cleanup

```bash
# Switch back to main and pull
git checkout main
git pull origin main

# Confirm local branch is gone
git branch | grep -v "^\* main"

# Prune remote tracking refs
git remote prune origin
```

### 5 — Jules Session Cleanup (if applicable)

```bash
# List active sessions
COLUMNS=200 jules remote list --session | cat

# Pull final state of any sessions related to this PR
# jules remote pull --session <SESSION_ID>

# No explicit session deletion needed — sessions expire automatically
# But document which session ID was used for this PR for traceability
```

### 6 — Verify

```bash
gh pr view <PR_NUMBER> --json state --jq .state  # Should be "MERGED"
git log --oneline -3  # Confirm merge commit present
```

### 7 — Cleanup

```bash
# Clear any tmp files from the PR workflow
make clean-tmp
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
