---
name: pr-code-orchestrator
description: Deterministic PR lifecycle automation with structured per-comment replies, scoped commits, runtime validation, and batched status execution
trigger: when user references reviewing PRs, handling review comments, or fixing PR feedback
---

# THINKING PROTOCOL (MANDATORY)

Before ANY implementation:

1. Checkout PR branch.
2. Run baseline build + tests.
3. Fetch PR metadata.
4. Fetch ALL review comments (resolved + unresolved).
5. Fetch changed files only.
6. Build compact structured matrix:

.agent/skills/pr-code-orchestrator/tmp/pr-code-orchestrator-matrix.json

Schema:

[
  {
    comment_id,
    comment_url,
    path,
    line,
    classification,
    task_id,
    status,
    commit_sha,
    issue_number
  }
]

Rules:

- One matrix entry per comment.
- Do NOT store full diff.
- Do NOT store comment bodies.
- Do NOT store logs.
- No code changes before matrix complete.

---

# EXECUTION WORKFLOW

## Phase 0 — Branch + Baseline Runtime

gh pr checkout <PR_NUMBER>

Then:

- Install dependencies
- Build project
- Run lint
- Run type-check
- Run full test suite

If baseline already failing:
→ Mark affected comments UNSOLVED
→ Do NOT introduce unrelated fixes

Store runtime result in:

tmp/runtime-summary.json

---

## Phase 1 — Discovery

gh pr view <PR_NUMBER> --json number,title,headRefName
gh api repos/:owner/:repo/pulls/<PR_NUMBER>/comments
gh pr diff <PR_NUMBER> --name-only

Persist:

tmp/pr-code-orchestrator-matrix.json

---

## Phase 2 — Classification

For each comment:

Classify:

BUG | REFACTOR | PERF | TEST | DOC | CLARIFICATION_ONLY | OUT_OF_SCOPE | INVALID

Assign initial status:

- SOLVED → clarification-only
- SKIPPED → invalid
- NEW_ISSUE → out of scope
- UNSOLVED → technical work required

Group technical comments into minimal batches:

tmp/task-plan.json

---

## Phase 3 — Scope Veto

Validate each task:

- Architecture boundaries
- PR intent
- Branch ownership

If violation:

- status = NEW_ISSUE
- Remove from task plan

---

## Phase 4 — Engineering Execution

For each task:

Invoke:

/handle-code <scoped task>

After success:

- Capture commit SHA
- Update matrix entries:
  status = SOLVED
  commit_sha = <sha>

If fails after stabilization:
  status = UNSOLVED

Never batch unrelated fixes.

---

## Phase 5 — Automated Reply Execution (Batched Script)

After matrix fully finalized:

python3 .agent/skills/pr-code-orchestrator/scripts/post_comment_replies.py <PR_NUMBER>

Behavior:

- Replies individually to each comment
- Creates issues when required
- Injects commit SHA
- Injects issue number if created
- Enforces strict status format
- No duplicate replies

---

## Phase 6 — Final Validation

- Confirm CI passing
- Confirm no force push
- Confirm minimal commits
- Confirm no unrelated file changes
- Confirm every matrix entry resolved

---

## Phase 7 — Cleanup

Delete:

- tmp/pr-code-orchestrator-matrix.json
- tmp/task-plan.json
- tmp/runtime-summary.json

Ensure tmp/ empty.

Verify via git status.

---

# COMPLETION CRITERIA

- Every comment has structured reply.
- Issues created when required.
- Commits minimal and scoped.
- CI passing.
- No temp artifacts committed.
- Deterministic execution.
