---
name: pr-code-orchestrator
description: Deterministic PR lifecycle automation — fetch review comments, implement fixes, post structured replies, validate CI. Use when user references fixing PR comments, addressing review feedback, implementing requested changes, or "handle the PR". Also triggers for "fix the review comments on PR #N" or "address the feedback".
---

# PR Code Orchestrator

Implements all actionable review comments on a PR, validates the result, and posts structured status replies. Strict scope — never touches unrelated code.

---

## Setup Check

```bash
# Verify tooling
gh --version
git --version

mkdir -p .agent/skills/pr-code-orchestrator/tmp
grep -qxF '.agent/skills/pr-code-orchestrator/tmp/' .gitignore \
  || echo '.agent/skills/pr-code-orchestrator/tmp/' >> .gitignore
```

---

## Phase 0 — Branch Checkout & Baseline

```bash
# Checkout the PR branch
gh pr checkout <PR_NUMBER>

# Validate we're NOT on a protected branch
CURRENT=$(git branch --show-current)
if [[ "$CURRENT" == "main" || "$CURRENT" == "master" || "$CURRENT" == "production" ]]; then
  echo "ERROR: On protected branch. Aborting." && exit 1
fi

# Confirm we're on the right branch
gh pr view <PR_NUMBER> --json headRefName --jq '"Expected branch: " + .headRefName'
echo "Current branch: $CURRENT"
```

Run baseline validation BEFORE any changes:

```bash
# Detect and run: install → build → lint → typecheck → test
# Store result in tmp/runtime-summary.json
# Format: { "build": "PASS|FAIL", "lint": "PASS|FAIL|N/A", ... }
```

If baseline is already failing → mark all comments `UNSOLVED` with `"Baseline already failing — not introducing further changes"`. Do NOT fix unrelated failures.

---

## Phase 1 — Discovery

```bash
# Fetch PR metadata
gh pr view <PR_NUMBER> \
  --json number,title,headRefName,baseRefName,author,additions,deletions \
  > .agent/skills/pr-code-orchestrator/tmp/pr-meta.json

# Fetch ALL review comments (inline + general)
gh api \
  "repos/{owner}/{repo}/pulls/<PR_NUMBER>/comments" \
  --jq '[.[] | {
    id: .id,
    url: .html_url,
    path: .path,
    line: (.line // .original_line),
    body: .body,
    author: .user.login,
    resolved: (.resolved // false)
  }]' \
  > .agent/skills/pr-code-orchestrator/tmp/review-comments.json

# Fetch review-level (non-inline) comments
gh api \
  "repos/{owner}/{repo}/pulls/<PR_NUMBER>/reviews" \
  --jq '[.[] | {id:.id, state:.state, body:.body, author:.user.login}]' \
  >> .agent/skills/pr-code-orchestrator/tmp/review-comments.json

# Get changed files only
gh pr diff <PR_NUMBER> --name-only \
  > .agent/skills/pr-code-orchestrator/tmp/changed-files.txt
```

---

## Phase 2 — Build Comment Matrix

Write to `tmp/pr-code-matrix.json`:

```json
[
  {
    "comment_id": 123456,
    "comment_url": "https://github.com/...",
    "path": "src/auth.ts",
    "line": 42,
    "classification": "BUG|REFACTOR|PERF|TEST|DOC|CLARIFICATION_ONLY|OUT_OF_SCOPE|INVALID",
    "task_id": "task-1",
    "status": "PENDING|SOLVED|UNSOLVED|SKIPPED|NEW_ISSUE",
    "commit_sha": null,
    "issue_number": null
  }
]
```

**Classification rules:**

| Comment asks for... | Classification |
|---------------------|---------------|
| Fix a null check, error handling, logic error | `BUG` |
| Rename, extract, restructure | `REFACTOR` |
| Add test, improve coverage | `TEST` |
| Performance optimization | `PERF` |
| Just a question, "what does this do?" | `CLARIFICATION_ONLY` |
| Architectural redesign, new subsystem | `OUT_OF_SCOPE` |
| Already handled elsewhere | `INVALID` |

Pre-assign status:
- `CLARIFICATION_ONLY` → `SOLVED` (just reply, no code change)
- `OUT_OF_SCOPE` → `NEW_ISSUE` (create GitHub issue, don't implement)
- `INVALID` / already done → `SKIPPED`
- Everything else → `PENDING`

---

## Phase 3 — Scope Veto

For each PENDING comment, validate:

- [ ] Change is within files already touched by this PR
- [ ] Change doesn't require architectural redesign
- [ ] Change doesn't break public API without versioning

If scope violation: change status to `NEW_ISSUE`.

---

## Phase 4 — Implementation

Group PENDING comments into minimal logical tasks (`tmp/task-plan.json`):

```json
[{"task_id": "task-1", "related_comment_ids": [123, 124], "description": "..."}]
```

For each task, invoke:

```
/handle-code "<scoped description from task>"
```

After each successful commit:

```bash
COMMIT_SHA=$(git rev-parse HEAD)
# Update matrix: status = SOLVED, commit_sha = $COMMIT_SHA
```

After each commit, re-validate:

```bash
# Re-run build + tests
# If regression: git revert, mark comment UNSOLVED
```

---

## Phase 5 — Create Issues for OUT_OF_SCOPE Items

```bash
# For each comment with status NEW_ISSUE:
ISSUE_URL=$(gh issue create \
  --title "Follow-up (PR #<PR_NUMBER>): <comment summary>" \
  --body "$(cat <<EOF
## Context

This was raised as a review comment on PR #<PR_NUMBER> but is out of scope for that change.

**Original comment:** <comment_url>

## Description

<comment body paraphrased>

## Why separate issue

<reason it needs separate treatment>
EOF
)" \
  --label "follow-up")

ISSUE_NUMBER=$(echo $ISSUE_URL | grep -oE '[0-9]+$')
# Update matrix: issue_number = $ISSUE_NUMBER
```

---

## Phase 6 — Post Replies

Run the reply script after matrix is fully finalized:

```bash
python3 .agent/skills/pr-code-orchestrator/scripts/post_comment_replies.py <PR_NUMBER>
```

Manual format (if running inline):

### ✅ SOLVED
```bash
gh api \
  "repos/{owner}/{repo}/pulls/comments/<COMMENT_ID>/replies" \
  -f body="**Status: ✅ SOLVED**
Commit: \`<SHA>\`

**Summary:**
- <What changed>
- <Why it resolves the feedback>
- <Tests added/updated>"
```

### ❌ UNSOLVED
```bash
gh api \
  "repos/{owner}/{repo}/pulls/comments/<COMMENT_ID>/replies" \
  -f body="**Status: ❌ UNSOLVED**

**Reason:** <Technical explanation>
**Blocker:** <What is needed to proceed>"
```

### 🆕 NEW ISSUE
```bash
gh api \
  "repos/{owner}/{repo}/pulls/comments/<COMMENT_ID>/replies" \
  -f body="**Status: 🆕 NEW ISSUE**
Issue: #<NUMBER>

**Reason:** This exceeds the scope of this PR and has been tracked separately."
```

### ⏭ SKIPPED
```bash
gh api \
  "repos/{owner}/{repo}/pulls/comments/<COMMENT_ID>/replies" \
  -f body="**Status: ⏭ SKIPPED**

**Reason:** <Already addressed / invalid / outdated>"
```

---

## Phase 7 — Final Validation

```bash
# Confirm CI status
gh pr checks <PR_NUMBER> --watch

# Confirm diff is minimal
gh pr diff <PR_NUMBER> --name-only

# Confirm no force pushes
git log --oneline -5

# Confirm no unrelated changes
git diff origin/<base-branch>..HEAD --name-only
```

Verify:
- [ ] All comments have exactly one structured reply
- [ ] No NEW_ISSUE comment is left without a tracking issue
- [ ] CI passing
- [ ] No unrelated files in diff
- [ ] No protected branch commits
- [ ] `git status` clean

---

## Phase 8 — Cleanup

```bash
rm -f .agent/skills/pr-code-orchestrator/tmp/*.json
rm -f .agent/skills/pr-code-orchestrator/tmp/*.txt
```

---

## Commit Message Convention

```
<type>(<module>): <description>

Addresses PR #<PR_NUMBER> comment:
<comment_url>
```

Never squash without explicit approval. One commit per logical fix.
