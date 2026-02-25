---
name: pr-review-orchestrator
description: Deterministic, structured, read-only pull request code review with strict per-comment status responses
trigger: when user references reviewing a PR without making code changes
---

# THINKING PROTOCOL (MANDATORY)

Before writing any review comment:

1. Fetch PR metadata.
2. Fetch full diff.
3. Identify changed files.
4. Build structured matrix:

.agent/tmp/review-analysis.json

Schema:

{
  file,
  change_type,
  risk_level,
  issues_detected,
  test_coverage_status
}

5. Evaluate each changed file for:

- Type safety violations
- Null/undefined risk
- Error handling gaps
- Concurrency risks
- Security risks
- Performance risks
- Architectural boundary violations
- Missing tests

No review comments before full diff analysis complete.

---

# EXECUTION WORKFLOW

## Phase 1 — Discovery

gh pr view <PR_NUMBER> --json number,title,body,headRefName
gh pr diff <PR_NUMBER>

Store analysis artifacts in `.agent/tmp/`.

---

## Phase 2 — File-Level Review

For each changed file:

- Validate logic correctness.
- Detect possible runtime failures.
- Check input validation.
- Check error handling.
- Check async/await correctness.
- Check public API changes.
- Evaluate test presence.

Populate review matrix.

---

## Phase 3 — Risk Classification

Classify overall PR:

- SAFE
- LOW RISK
- MEDIUM RISK
- HIGH RISK

If high-risk patterns detected:
- Must issue CHANGES REQUESTED.

---

## Phase 4 — Structured Review Comments

For each detected issue:

Use:

gh pr comment <PR_NUMBER> --body "<structured review comment>"

Follow rule patterns strictly:

- APPROVED
- CHANGES REQUESTED
- CLARIFICATION REQUIRED
- TESTS MISSING

One comment per issue.
Do not bundle unrelated findings.

---

## Phase 5 — Final Review Decision

If no issues detected:

gh pr review <PR_NUMBER> --approve

If issues detected:

gh pr review <PR_NUMBER> --request-changes

Never leave PR without final state.

---

## Phase 6 — Cleanup

- Delete .agent/tmp/*
- Ensure no artifacts staged.

---

# SELF-VALIDATION

Before posting:

- Confirm no code edits made.
- Confirm no commits created.
- Confirm structured pattern respected.
- Confirm all changed files analyzed.

---

# COMPLETION CRITERIA

- Every issue found has structured comment.
- Final review decision submitted.
- No code modified.
- No temp artifacts remain.
