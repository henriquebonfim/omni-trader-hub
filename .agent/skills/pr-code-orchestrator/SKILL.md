---
name: pr-code-orchestrator
description: Deterministic PR lifecycle automation with structured per-comment replies and strict artifact control
trigger: when user references reviewing PRs, handling review comments, or fixing PR feedback
---

# THINKING PROTOCOL (MANDATORY)

Before any implementation:

1. Fetch PR metadata.
2. Fetch all review comments.
3. Create structured matrix:

   .agent/tmp/review-matrix.json

Schema:

{
  comment_url,
  file,
  classification,
  task_group,
  status
}

4. Classify each comment:

   - BUG
   - REFACTOR
   - PERF
   - TEST
   - DOC
   - CLARIFICATION_ONLY
   - OUT_OF_SCOPE
   - INVALID

5. Group technical comments into task batches.
6. Map each comment → intended status:
   - SOLVED
   - UNSOLVED
   - NEW ISSUE
   - SKIPPED

No code modification before matrix complete.

---

# EXECUTION WORKFLOW

## Phase 1 — Discovery

gh pr view <PR_NUMBER> --json number,title,body,headRefName,author
gh api repos/:owner/:repo/pulls/<PR_NUMBER>/comments
gh pr diff <PR_NUMBER>

Store structured matrix in:

.agent/tmp/review-matrix.json

---

## Phase 2 — Task Planning

Generate:

.agent/tmp/task-plan.json

Rules:

- Group comments logically.
- Each task must reference comment URLs.
- No over-grouping.
- Keep commits minimal.

---

## Phase 3 — Veto Point

For each task:

- Does it violate architecture?
- Is it beyond scope?
- Is it safe?

If beyond scope:

- Mark comment as NEW ISSUE.

---

## Phase 4 — Nested Engineering Execution

For each technical task:

Invoke:

/handle-code <precise scoped task>

After success:

- Update matrix status = SOLVED
- Record commit SHA

If failure:

- Attempt self-healing
- If still failing → mark UNSOLVED

---

## Phase 5 — Per-Comment Replies (STRICT PATTERN)

For each comment individually:

Use:

gh pr comment <PR_NUMBER> --body "<structured status reply>"

Format must strictly follow rule definitions:

Status: <TYPE>
Commit: <SHA if applicable>

Summary or Reason:
- Bullet explanation

Never combine replies.
Never skip a comment.

---

## Phase 6 — Issue Creation

If comment classified OUT_OF_SCOPE:

gh issue create \
  --title "Follow-up: <description>" \
  --body "<context>" \
  --label "refactor"

Update comment status to NEW ISSUE and reply accordingly.

---

## Phase 7 — Cleanup (MANDATORY)

- Delete .agent/tmp/*
- Ensure .agent/tmp/ is empty.
- Ensure no temp files staged.
- Verify via git status.

---

# SELF-HEALING LOOP

If:

- Tests fail
- Lint fails
- Type check fails

Then:

1.  **Analyze Root Cause:** Identify the specific line or architectural boundary being violated.
2.  **Verify Standards:** Consult `software-engineering-standards.md` to ensure the fix doesn't introduce a different violation.
3.  **Patch Minimally:** Apply the smallest possible change to resolve the issue.
4.  **Re-Run Validation:** Run all tests, lint, and type checks again.
5.  **Iterate:** Repeat until stable and standard-compliant.

If cannot stabilize:

- Mark affected comment UNSOLVED.

---

# COMPLETION CRITERIA

- Every comment has structured reply.
- Matrix fully resolved.
- CI passing.
- No temp artifacts committed.
- No scope creep.
- No force push.
