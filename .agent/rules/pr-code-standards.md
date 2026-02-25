---
trigger: model_decision
description: review of a Pull Request with code modifications.
---

## Branch Discipline

- Never force push to shared or protected branches.
- Never rebase a branch under active review unless explicitly approved.
- Always work on the PR head branch (`gh pr checkout <number>`).
- Never modify files unrelated to the review comment scope.
- No drive-by refactors.
- Keep PR scope aligned with original intent.

---

## Temporary Artifacts Control (NEW)

The PR operator may generate temporary analysis artifacts.

Rules:

- All temporary files must live under:

  .agent/tmp/

- No temp files allowed in root or source directories.
- Temp files must never be committed.
- `.agent/tmp/` must be listed in `.gitignore`.
- Temp artifacts must be deleted after workflow completion.

Allowed temp files:

- review-matrix.json
- task-plan.json
- pr-context.json

No additional ad-hoc files allowed.

---

## Commit Standards

- Follow Conventional Commits:
  - fix:
  - feat:
  - refactor:
  - test:
  - docs:
  - perf:
  - chore:

- One logical change per commit.
- Each commit must reference the PR comment URL in the body.
- Never bundle unrelated fixes.

Example:

fix(auth): validate null token

Addresses PR comment:
https://github.com/org/repo/pull/123#discussion_r456

- Do not squash without approval.

---

## Mandatory Comment Reply Pattern (NEW)

Every PR comment must receive an individual reply using one of the following status headers:

### ✅ SOLVED
Used when code change implemented.

Format:

Status: ✅ SOLVED
Commit: <SHA>

Summary:
- What changed
- Why it fixes issue
- Tests added (if any)
- **Self-Correction Check:** Confirmed that these changes follow `software-engineering-standards.md`.

---

### ❌ UNSOLVED
Used when change cannot be safely implemented.

Format:

Status: ❌ UNSOLVED

Reason:
- Clear technical explanation
- What is required to proceed

---

## Mandatory Self-Correction (NEW)

Before committing any code or replying to a comment:

1.  **Analyze Standards:** Re-read `software-engineering-standards.md`.
2.  **Verify Implementation:** Does the code use strict typing? Is it modular? Does it have tests?
3.  **Validate Integrity:** Run `pytest` or relevant test suites to ensure zero regressions.
4.  **Fix Deviations:** If the code fails any check, fix it BEFORE proceeding.

---

### 🆕 NEW ISSUE
Used when request exceeds PR scope.

Format:

Status: 🆕 NEW ISSUE
Issue: #<number>

Reason:
- Why it exceeds scope
- Why separation is required

---

### ⏭ SKIPPED
Used when feedback is invalid, outdated, or already addressed.

Format:

Status: ⏭ SKIPPED

Reason:
- Explanation

---

- Never close a thread without one of these statuses.
- Never combine multiple comments into one reply.
- One reply per comment thread.

---

## Scope Control

Create a new Issue if:

- Architectural redesign required.
- Cross-module refactor required.
- Product clarification required.
- Significant scope expansion detected.

Never expand PR scope silently.

---

## CLI Enforcement

All GitHub operations must use:

- gh pr view
- gh pr diff
- gh pr comment
- gh pr review
- gh pr checkout
- gh issue create
- gh api

No UI simulation.

---

## Final Validation Requirements

Before completion:

- All review threads have a status reply.
- CI passing.
- No unrelated file changes.
- No temp files committed.
- `.agent/tmp/` cleaned.
