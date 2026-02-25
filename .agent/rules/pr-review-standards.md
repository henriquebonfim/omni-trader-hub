---
trigger: model_decision
description: review of a Pull Request without code modifications.
---

## Strict No-Modification Rule

During review:

- No code edits allowed.
- No commits allowed.
- No branch pushes allowed.
- No file creation outside `.agent/tmp/`.
- No test files committed.
- No refactors.

This is a read-only analytical workflow.

---

## Branch Safety

- Always checkout PR branch using:
  gh pr checkout <PR_NUMBER>
- Never commit on:
  - main
  - master
  - production
- Never create new branch during review.

---

## Temporary Artifact Control

All review artifacts must live under:

.agent/tmp/

Allowed files:

- review-analysis.json
- diff-analysis.json
- test-evaluation.json

Rules:

- Never commit temp files.
- Delete `.agent/tmp/*` after completion.
- `.agent/tmp/` must be in `.gitignore`.

---

## Mandatory Per-Comment Review Pattern

Every review must post structured comments using one of:

### ✅ APPROVED

Status: ✅ APPROVED

Summary:
- Code is correct
- Tests sufficient
- No regressions detected

---

### ⚠️ CHANGES REQUESTED

Status: ⚠️ CHANGES REQUESTED

Problem:
- Precise technical issue
- File and location
- Why it is incorrect or unsafe

Impact:
- Bug / Performance / Security / Architecture

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

## Review Scope

The review must:

- Analyze only changed files.
- Validate type safety.
- Validate architectural boundaries.
- Detect potential runtime errors.
- Detect missing null checks.
- Detect unsafe async usage.
- Detect performance red flags.
- Detect missing test coverage.
- Detect breaking API changes.

---

## Validation Before Posting Review

Before finalizing:

- Ensure all changed files analyzed.
- Ensure no modifications made.
- Ensure structured reply format used.
- Ensure `.agent/tmp/` cleaned.
