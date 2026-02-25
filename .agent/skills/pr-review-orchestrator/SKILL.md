---
name: pr-review-orchestrator
description: Deterministic, structured, read-only pull request review with runtime validation and batched GitHub review submission
trigger: when user references reviewing a PR without making code changes
---

# THINKING PROTOCOL (MANDATORY)

Before writing ANY review comment:

1. Checkout PR branch.
2. Validate baseline runtime (build + tests).
3. Fetch changed files only.
4. Fetch existing review threads.
5. Build compact structured matrix:

.agent/skills/pr-review-orchestrator/tmp/pr-review-orchestrator-matrix.json

Schema:

[
  {
    path,
    line,
    severity,      // LOW | MEDIUM | HIGH
    category,      // BUG | SAFETY | PERF | SECURITY | ARCH | TEST
    message
  }
]

Optional runtime summary:

.agent/skills/pr-review-orchestrator/tmp/runtime-summary.json

{
  build,
  lint,
  typecheck,
  tests,
  runtime
}

Rules:

- Only store actionable issues.
- Do NOT store full diffs.
- Do NOT store file contents.
- Do NOT store full logs.
- Skip clean files.
- No review submission before matrix complete.

---

# EXECUTION WORKFLOW

## Phase 0 — Branch + Runtime Validation

gh pr checkout <PR_NUMBER>

Then:

- Install dependencies (non-persistent).
- Build project.
- Run lint (if available).
- Run type-check (if available).
- Run full test suite.
- Attempt runtime start (if applicable).

Store PASS/FAIL only in runtime-summary.json.

If runtime/test failure:
- Add HIGH severity issue entries referencing failing file/module.
- Do NOT fix code.

---

## Phase 1 — Discovery (Optimized)

gh pr view <PR_NUMBER> --json number,headRefOid
gh pr diff <PR_NUMBER> --name-only
gh api repos/:owner/:repo/pulls/<PR_NUMBER>/comments

Analyze modified hunks only.

---

## Phase 2 — Targeted File Review

For each changed file:

Analyze modified lines only.

Detect:

- Runtime failure risks
- Null/undefined access
- Missing error handling
- Unsafe async usage
- Security exposure
- Performance regression
- Architectural boundary violations
- Missing test coverage

Append minimal entries to:

tmp/pr-review-orchestrator-matrix.json

No commentary generation yet.

---

## Phase 3 — Batched Review Submission

Submit single review via helper script:

python3 .agent/skills/pr-review-orchestrator/scripts/post_review.py <PR_NUMBER>

Behavior:

- If matrix empty → APPROVE
- If matrix contains issues → REQUEST_CHANGES
- All inline comments submitted in single API call
- Runtime summary included in review body

---

## Phase 4 — Cleanup (MANDATORY)

Delete:

- tmp/pr-review-orchestrator-matrix.json
- tmp/runtime-summary.json
- tmp/review_payload.json

Ensure no artifacts staged.

Verify via `git status`.

---

# SELF-VALIDATION

- Confirm PR branch active.
- Confirm no commits created.
- Confirm no file modifications made.
- Confirm runtime executed.
- Confirm tests executed.
- Confirm each issue tied to file + line.
- Confirm single batched review used.
- Confirm tmp directory empty.

---

# COMPLETION CRITERIA

- All changed files scanned.
- Runtime validated.
- Issues reported inline.
- Final review state explicit.
- No code modified.
- tmp directory empty.
