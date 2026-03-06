---
description: /handle-pr-code <PR_NUMBER>
---

# Handle PR Code

Implement all actionable review comments, validate CI, post structured replies.

---

## Execution Sequence

### 1 — SOP Validation Gate

```bash
python3 .agent/scripts/orchestrator.py handle-pr-code
ENFORCE_EXIT=$?
[ $ENFORCE_EXIT -ne 0 ] && echo "❌ SOP validation failed" && exit 1

WORKFLOW_NAME="handle-pr-code"
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

### 2 — Setup

```bash
mkdir -p .agent/tmp
grep -qxF '.agent/tmp/' .gitignore \
  || echo '.agent/tmp/' >> .gitignore
```

> **sequential-thinking**: Read review comments → group by theme → assess change scope → plan implementation order → identify test coverage needs.

### 3 — Load Skill

```
pr-code-orchestrator
```

### 4 — Checkout & Baseline

```bash
gh pr checkout <PR_NUMBER>

# Run baseline validation before ANY changes
# Store in tmp/runtime-summary.json
```

### 5 — Discovery

```bash
gh pr view <PR_NUMBER> --json number,title,headRefName,baseRefName \
  > .agent/tmp/pr-meta.json

gh api "repos/{owner}/{repo}/pulls/<PR_NUMBER>/comments" \
  --jq '[.[] | {id:.id, url:.html_url, path:.path, line:(.line // .original_line), body:.body}]' \
  > .agent/tmp/review-comments.json

gh pr diff <PR_NUMBER> --name-only \
  > .agent/tmp/changed-files.txt
```

### 6 — Build & Execute Matrix

- Classify every comment
- Build `tmp/pr-code-matrix.json`
- Veto out-of-scope items → create issues
- Group into task batches → `tmp/task-plan.json`
- Execute: `/handle-code <task>` for each batch

### 7 — Post Replies

```bash
make pr-reply PR=<PR_NUMBER>
```

### 8 — CI Check

```bash
gh pr checks <PR_NUMBER> --watch
```

### 9 — Final Checks

```bash
gh pr diff <PR_NUMBER> --name-only   # Only expected files changed
git log --oneline -5                  # Clean history
git status                            # Clean tree
```

### 10 — Cleanup

```bash
make clean-tmp
```

---

## Abort Conditions

- Protected branch violation
- Large redesign required → create issue, mark UNSOLVED
- Test suite unstable beyond safe repair

## Success Condition

- All comments have exactly one structured reply
- CI passing
- No unrelated file changes
- `tmp/` empty
