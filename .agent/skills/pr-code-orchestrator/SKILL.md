---
name: pr-code-orchestrator
description: Deterministic PR lifecycle automation with structured per-comment replies, strict file-level mapping, and minimal artifact footprint
trigger: when user references reviewing PRs, handling review comments, or fixing PR feedback
---

# THINKING PROTOCOL (MANDATORY)

Before ANY implementation:

1. Fetch PR metadata.
2. Fetch ALL review comments (including resolved + unresolved).
3. Fetch changed files only (no full repo scan).
4. Build compact structured matrix:

.agent/tmp/pr-code-orchestrator-matrix.json

Schema (token-optimized, one entry per comment):

[
  {
    comment_id,        // numeric GitHub comment id
    comment_url,
    path,              // file path (null if general comment)
    line,              // line number if applicable
    classification,    // BUG | REFACTOR | PERF | TEST | DOC | CLARIFICATION_ONLY | OUT_OF_SCOPE | INVALID
    task_id,           // logical batch id or null
    status,            // SOLVED | UNSOLVED | NEW_ISSUE | SKIPPED
    commit_sha         // nullable
  }
]

Rules:

- One matrix entry per comment.
- Do NOT store full diff.
- Do NOT store comment bodies.
- Do NOT store analysis narrative.
- No code changes before matrix complete.

---

# EXECUTION WORKFLOW

## Phase 1 — Discovery (Minimal + Deterministic)

gh pr view <PR_NUMBER> --json number,title,headRefName
gh api repos/:owner/:repo/pulls/<PR_NUMBER>/comments
gh pr diff <PR_NUMBER> --name-only

Only analyze changed files referenced by comments.

Persist matrix to:

.agent/tmp/pr-code-orchestrator-matrix.json

---

## Phase 2 — Deterministic Classification

For each comment:

Classify strictly:

- BUG → incorrect behavior
- REFACTOR → structure improvement
- PERF → performance risk
- TEST → missing/incorrect tests
- DOC → documentation change
- CLARIFICATION_ONLY → explanation required only
- OUT_OF_SCOPE → exceeds PR scope
- INVALID → already resolved / not applicable

Assign:

- status = SOLVED (if trivial + explanation only)
- status = SKIPPED (if INVALID)
- status = NEW_ISSUE (if OUT_OF_SCOPE)
- status = UNSOLVED (default for technical work)

Group technical items into minimal logical task batches:

.agent/tmp/task-plan.json

Schema:

[
  {
    task_id,
    related_comment_ids[]
  }
]

Rules:

- No over-grouping.
- No cross-boundary batching.
- Keep commits minimal and scoped.

---

## Phase 3 — Scope Veto

For each task:

- Validate against architecture boundaries.
- Validate against PR intent.
- Confirm change belongs in this branch.

If violates scope:

- status = NEW_ISSUE
- Remove from task-plan.

---

## Phase 4 — Nested Engineering Execution

For each task in task-plan:

Invoke:

/handle-code <precise scoped task>

After successful implementation:

- Capture commit SHA.
- Update each related matrix entry:
    status = SOLVED
    commit_sha = <sha>

If implementation fails:

- Run self-healing loop.
- If stabilization fails:
    status = UNSOLVED

Never batch unrelated fixes into same commit.

---

# PHASE 5 — Structured Per-Comment Replies (STRICT)

Reply to EACH comment individually.

If comment tied to file/line:

Use file-level reply:

gh api repos/:owner/:repo/pulls/comments/<comment_id>/replies \
  -f body="<structured message>"

If general PR comment:

gh pr comment <PR_NUMBER> --body "<structured message>"

Mandatory format:

Status: <SOLVED | UNSOLVED | NEW ISSUE | SKIPPED>
Commit: <SHA or N/A>

Summary:
- Concise explanation
- If NEW ISSUE → reference issue number
- If UNSOLVED → explain blocker

Rules:

- Never bundle multiple comment replies.
- Never skip a comment.
- Never omit status field.
- Never reply before matrix status finalized.

---

## Phase 6 — Issue Creation (Scoped)

If status = NEW_ISSUE:

gh issue create \
  --title "Follow-up (PR #<PR_NUMBER>): <short description>" \
  --body "Context:\n- Origin PR: #<PR_NUMBER>\n- Comment: <comment_url>\n- Rationale: Out of scope for current PR." \
  --label "refactor"

Capture issue number.
Update matrix entry.
Reference issue in reply.

---

## Phase 7 — Self-Healing Loop (Strict)

If:

- Tests fail
- Lint fails
- Type check fails

Then:

1. Identify exact failing boundary.
2. Validate against engineering standards.
3. Apply smallest corrective patch.
4. Re-run validation.
5. Repeat until stable.

If cannot stabilize:

- Mark affected entries UNSOLVED.

---

## Phase 8 — Final Validation

Before finishing:

- Ensure every matrix entry has final status.
- Ensure all technical comments processed.
- Ensure CI passing.
- Ensure no force push performed.
- Ensure no unrelated files modified.
- Ensure commits are minimal and scoped.

---

## Phase 9 — Cleanup (MANDATORY)

- Delete:
    .agent/tmp/pr-code-orchestrator-matrix.json
    .agent/tmp/task-plan.json
- Ensure .agent/tmp/ empty.
- Verify via:
    git status
- Confirm no temp artifacts staged.

---

# COMPLETION CRITERIA

- Every comment has structured reply.
- Matrix fully resolved.
- CI passing.
- No temp artifacts committed.
- No scope creep.
- No force push.
- Minimal, deterministic commits only.
