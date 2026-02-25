---
name: software-engineer-worker
description: Structured engineering execution for implementing features, refactors, and bug fixes with architectural discipline
trigger: when user requests implementation, refactor, feature development, or bug fixing
---

# THINKING PROTOCOL (MANDATORY)

Before writing code:

1. Understand the request precisely.
2. Identify affected modules.
3. Identify architectural boundaries.
4. Determine:
   - Is this a feature, fix, refactor, or performance task?
   - Does this impact public APIs?
   - Does this require migration?
5. Identify risks:
   - Breaking changes
   - Concurrency risks
   - Performance risks
   - Security implications
6. Design minimal solution aligned with standards.

No coding before architecture reasoning is complete.

---

# EXECUTION WORKFLOW

## Phase 1 — Discovery

- Inspect relevant modules.
- Trace call graph.
- Identify data flow.
- Identify validation boundaries.
- Review existing tests.

---

## Phase 2 — Design

Produce internal implementation plan:

- Files to modify
- Functions to add/change
- Data structures impacted
- Test strategy
- Backward compatibility strategy

If change is large:

- Break into logical sub-tasks.

---

## Phase 3 — Veto Point

Before implementation:

- Does this violate architecture rules?
- Is abstraction premature?
- Is solution minimal?
- Is performance considered?
- Are security boundaries respected?

If violation detected → redesign before proceeding.

---

## Phase 4 — Implementation

- Write minimal code necessary.
- Maintain strict typing.
- Follow naming clarity.
- Avoid duplication.
- Respect separation of concerns.
- Add or update tests.

Commit pattern:

<type>(module): concise description

Example:

feat(auth): add token expiration validation

---

## Phase 5 — Self-Correction & Verification (MANDATORY)

Before finalizing:

1.  **Code Review:** Review your own changes against `.agent/rules/software-engineering-standards.md`.
2.  **Lint & Type Check:** Run the project's linter and type checker.
3.  **Test Execution:** Run the full test suite (e.g., `pytest`).
4.  **Refactor:** If any standard is violated or tests fail, fix them immediately and re-run validation.
5.  **Documentation:** Ensure public APIs are documented and comments are clear.

---

## Phase 6 — Final Validation

- Review diff for unrelated changes.
- Confirm no architectural drift.
- Ensure all artifacts are cleaned up.

---

# SELF-HEALING LOOP

If:

- Tests fail
- Type errors occur
- Lint errors occur

Then:

1. Analyze failure root cause.
2. Apply minimal corrective patch.
3. Re-run validation.
4. Repeat until stable.

If architecture inconsistency discovered:

- Pause.
- Redesign.
- Re-validate before committing.

---

# COMPLETION CRITERIA

- Code compiles.
- Tests pass.
- New logic fully covered.
- No duplicated logic introduced.
- No architectural boundary violations.
- Minimal diff.
- Standards fully respected.
