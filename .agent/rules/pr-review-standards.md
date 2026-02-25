---
trigger: model_decision
description: This rule governs strict, read-only PR reviews with structured per-comment responses, minimal artifact footprint, and runtime verification.
---

# Strict No-Modification Rule

During review:

- No code edits allowed.
- No commits allowed.
- No branch pushes allowed.
- No force push.
- No branch creation.
- No file creation outside `.agent/tmp/`.
- No dependency installation committed.
- No test files committed.
- No refactors.

This is a read-only analytical workflow.

If runtime or tests fail:
→ Report via structured review comment.
→ Never fix code.

---

# Branch Safety

Always:

gh pr checkout <PR_NUMBER>

Constraints:

- Never commit on:
  - main
  - master
  - production
- Never create new branch.
- Never rebase.
- Never amend.

Validate current branch before proceeding.

---

# Runtime & Functional Validation (MANDATORY)

After checkout:

1. Install dependencies (non-persistent).
2. Build project.
3. Run lint (if available).
4. Run type-check (if available).
5. Run full test suite.
6. Attempt project start (if applicable).

Store only summarized results (not logs).

If any failure occurs:

- Capture failure type.
- Identify failing file/module.
- Report as structured review comment.
- Classify as:
  - BUG
  - ARCH
  - TEST
  - PERF

Do NOT patch.
Do NOT retry with edits.
Do NOT introduce fixes.

---

# Temporary Artifact Control (Token Optimized)

All review artifacts must live under:

.agent/tmp/

Allowed files (minimal schema only):

- review-analysis.json
- runtime-summary.json

review-analysis.json schema:

[
  {
    path,
    line,
    severity,
    category,
    message
  }
]

runtime-summary.json schema:

{
  build: "PASS | FAIL",
  lint: "PASS | FAIL | N/A",
  typecheck: "PASS | FAIL | N/A",
  tests: "PASS | FAIL | N/A",
  runtime: "PASS | FAIL | N/A"
}

Rules:

- Never store full diffs.
- Never store full logs.
- Never store entire file contents.
- Only store detected issues.
- Skip clean files entirely.
- Delete `.agent/tmp/*` after completion.
- `.agent/tmp/` must exist in `.gitignore`.

---

# Mandatory Per-Comment Review Pattern

Each issue must produce ONE structured comment.
Never bundle unrelated issues.

Allowed patterns:

---

### ✅ APPROVED

Status: ✅ APPROVED

Summary:
- Code correct
- Runtime validated
- Tests passing
- No regressions detected

---

### ⚠️ CHANGES REQUESTED

Status: ⚠️ CHANGES REQUESTED
Severity: LOW | MEDIUM | HIGH
Category: BUG | SAFETY | PERF | SECURITY | ARCH | TEST

Problem:
- Precise technical issue
- File and location

Impact:
- Clear technical consequence

Required Fix:
- Concrete corrective direction

---

### ❓ CLARIFICATION REQUIRED

Status: ❓ CLARIFICATION REQUIRED

Concern:
- What is unclear

Question:
- Explicit request

---

### 🧪 TESTS MISSING

Status: 🧪 TESTS MISSING

Missing Coverage:
- Specific behavior not tested

Required:
- Explicit test requirement

---

# Review Scope (Strict + Optimized)

The review must:

- Analyze only changed files.
- Inspect only modified hunks.
- Detect:
  - Runtime failure risks
  - Null/undefined access
  - Unsafe async usage
  - Missing error handling
  - Architectural boundary violations
  - Security exposure
  - Performance regression
  - Breaking public API changes
  - Missing test coverage

Additionally:

- Validate project builds successfully.
- Validate test suite stability.
- Validate no regression introduced by PR.

Never analyze unrelated files.

---

# Risk Classification

After full analysis:

Classify overall PR:

- SAFE
- LOW RISK
- MEDIUM RISK
- HIGH RISK

If runtime fails → automatically HIGH RISK.
If tests fail → at least MEDIUM RISK.

---

# Validation Before Posting Review

Before finalizing:

- Confirm branch is PR branch.
- Confirm no commits created.
- Confirm no files modified.
- Confirm runtime executed.
- Confirm tests executed.
- Confirm all changed files analyzed.
- Confirm structured comment format respected.
- Confirm no duplicated comment threads.
- Confirm `.agent/tmp/` cleaned.
- Verify via `git status`.

---

# Completion Criteria

- All changed files analyzed.
- Runtime/build/tests validated.
- Structured per-issue comments posted.
- Final review decision submitted.
- No code modified.
- No artifacts committed.
- `.agent/tmp/` empty.
