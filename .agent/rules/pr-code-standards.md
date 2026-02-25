---
trigger: model_decision
description: This rule governs structured PR implementation workflows with strict scope control, minimal artifacts, runtime validation, and deterministic comment handling.
---

# Branch Discipline (With Runtime Validation)

Always begin with:

gh pr checkout <PR_NUMBER>

Then validate:

- Current branch equals PR head branch.
- Branch is NOT:
  - main
  - master
  - production

Strict constraints:

- Never force push.
- Never rebase under active review (unless explicitly approved).
- Never create new branch.
- Never amend historical commits.
- Never modify unrelated files.
- No drive-by refactors.
- Keep scope aligned with original PR intent.

---

# Runtime & Project Validation (MANDATORY)

After checkout and before ANY code changes:

1. Install dependencies (non-persistent).
2. Build project.
3. Run lint (if available).
4. Run type-check (if available).
5. Run full test suite.
6. Attempt application start (if applicable).

Store only summarized status (no logs).

If baseline is already failing:
→ Mark related comments as ❌ UNSOLVED
→ Report blocker
→ Do NOT introduce fixes outside scope

After each commit:

- Re-run build.
- Re-run tests.
- Confirm zero regressions.
- Confirm no new lint/type errors.

---

# Temporary Artifacts Control (Token Optimized)

All temporary files must live under:

.agent/tmp/

Allowed files ONLY:

- pr-code-matrix.json
- task-plan.json
- runtime-summary.json

No additional ad-hoc files allowed.

Minimal schemas:

pr-code-matrix.json

[
{
comment_id,
path,
line,
classification,
status,
commit_sha
}
]

task-plan.json

[
{
task_id,
related_comment_ids[]
}
]

runtime-summary.json

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
- Never store full comment bodies.
- Only store structured metadata.
- Skip clean entries.
- Never commit temp files.
- `.agent/tmp/` must be in `.gitignore`.
- Delete `.agent/tmp/*` after workflow completion.

---

# Commit Standards (Deterministic + Minimal)

Follow Conventional Commits:

- fix:
- feat:
- refactor:
- test:
- docs:
- perf:
- chore:

Rules:

- One logical change per commit.
- Never bundle unrelated fixes.
- Each commit must reference the PR comment URL in body.
- Never squash without approval.

Example:

fix(auth): validate null token

Addresses PR comment:
https://github.com/org/repo/pull/123#discussion_r456

Commit must be minimal and scoped strictly to affected files.

---

# Mandatory Comment Reply Pattern (STRICT)

Every PR comment must receive exactly ONE reply.

Never bundle replies.
Never close thread silently.

---

### ✅ SOLVED

Status: ✅ SOLVED
Commit: <SHA>

Summary:

- What changed
- Why it resolves issue
- Tests added or updated
- Self-Correction Check passed

---

### ❌ UNSOLVED

Status: ❌ UNSOLVED

Reason:

- Clear technical explanation
- Blocker details
- What is required to proceed

---

### 🆕 NEW ISSUE

Status: 🆕 NEW ISSUE
Issue: #<number>

Reason:

- Why request exceeds scope
- Why separation required

---

### ⏭ SKIPPED

Status: ⏭ SKIPPED

Reason:

- Invalid / outdated / already resolved

---

Mandatory:

- One reply per comment thread.
- No reply before matrix status finalized.
- Status header must match exactly.
- Commit SHA required for SOLVED.

---

# Mandatory Self-Correction Loop

Before committing or replying:

1. Re-read `software-engineering-standards.md`.
2. Validate:
   - Strict typing
   - Modularity
   - Test presence
   - Boundary compliance
3. Run build + tests.
4. Fix deviations BEFORE proceeding.

If cannot stabilize:
→ Mark affected comment ❌ UNSOLVED.

---

# Scope Control

Create a NEW ISSUE when:

- Architectural redesign required.
- Cross-module refactor required.
- Product clarification required.
- Significant scope expansion detected.

Never expand scope silently.

Never introduce opportunistic improvements.

---

# CLI Enforcement

All GitHub operations must use:

- gh pr view
- gh pr diff
- gh pr comment
- gh pr review
- gh pr checkout
- gh issue create
- gh api

No UI simulation.
No manual workflow deviations.

---

# Final Validation Requirements

Before completion:

- Confirm PR branch active.
- Confirm no protected branch commits.
- Confirm build passing.
- Confirm tests passing.
- Confirm no regressions.
- Confirm all comments have status reply.
- Confirm no unrelated file changes.
- Confirm no force push.
- Confirm minimal commit set.
- Confirm `.agent/tmp/` cleaned.
- Verify via `git status`.

---

# Completion Criteria

- All PR comments resolved with structured status.
- Runtime validated.
- CI passing.
- No scope creep.
- No temp artifacts committed.
- Deterministic, minimal, reproducible execution.
