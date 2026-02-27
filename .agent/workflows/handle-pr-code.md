---
description: /handle-pr-code <PR_NUMBER>
---

# Handle PR Code

Implement all actionable review comments, validate CI, post structured replies.

---

## Execution Sequence

### 1 — Setup

```bash
mkdir -p .agent/skills/pr-code-orchestrator/tmp
grep -qxF '.agent/skills/pr-code-orchestrator/tmp/' .gitignore \
  || echo '.agent/skills/pr-code-orchestrator/tmp/' >> .gitignore
```

### 2 — Load Skill

```
pr-code-orchestrator
```

### 3 — Checkout & Baseline

```bash
gh pr checkout <PR_NUMBER>

# Validate NOT on protected branch
BRANCH=$(git branch --show-current)
[[ "$BRANCH" == "main" || "$BRANCH" == "master" || "$BRANCH" == "production" ]] \
  && echo "ABORT: protected branch" && exit 1

# Run baseline validation before ANY changes
# Store in tmp/runtime-summary.json
```

### 4 — Discovery

```bash
gh pr view <PR_NUMBER> --json number,title,headRefName,baseRefName \
  > .agent/skills/pr-code-orchestrator/tmp/pr-meta.json

gh api "repos/{owner}/{repo}/pulls/<PR_NUMBER>/comments" \
  --jq '[.[] | {id:.id, url:.html_url, path:.path, line:(.line // .original_line), body:.body}]' \
  > .agent/skills/pr-code-orchestrator/tmp/review-comments.json

gh pr diff <PR_NUMBER> --name-only \
  > .agent/skills/pr-code-orchestrator/tmp/changed-files.txt
```

### 5 — Build & Execute Matrix

- Classify every comment
- Build `tmp/pr-code-matrix.json`
- Veto out-of-scope items → create issues
- Group into task batches → `tmp/task-plan.json`
- Execute: `/handle-code <task>` for each batch

### 6 — Post Replies

```bash
python3 .agent/skills/pr-code-orchestrator/scripts/post_comment_replies.py <PR_NUMBER>
```

### 7 — CI Check

```bash
gh pr checks <PR_NUMBER> --watch
```

### 8 — Final Checks

```bash
gh pr diff <PR_NUMBER> --name-only   # Only expected files changed
git log --oneline -5                  # Clean history
git status                            # Clean tree
```

### 9 — Cleanup

```bash
rm -f .agent/skills/pr-code-orchestrator/tmp/*
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
