---
trigger: model_decision
description: Activate for any code creation, modification, refactor, bug fix, test, or architecture changes
---

## Architecture Discipline

- Prefer simple, composable designs over complex abstractions.
- Enforce separation of concerns.
- No business logic inside controllers/routes.
- No direct database access outside repository/data layer.
- No circular dependencies.
- All modules must have clear responsibility boundaries.

---

## Type & Safety Enforcement

- Strict typing required (no `any`, no implicit types).
- No unchecked null/undefined access. Use optional chaining or explicit null checks.
- All external inputs must be validated using schemas (e.g., Pydantic, Zod).
- All async operations must handle failure paths with try/except or catch blocks.
- No silent error swallowing; always log the error before returning or re-throwing.

---

## Code Quality

- Functions must be small and single-purpose (ideally < 50 lines).
- No duplicated logic across modules. Extract common logic into utils or services.
- Avoid premature abstraction; wait for the third use case.
- All public functions must have clear, descriptive naming and docstrings/JSDoc.
- Remove dead code immediately.

---

## Testing Requirements

- Every new public function or API endpoint MUST have a corresponding unit or integration test.
- Bug fixes MUST include a regression test that reproduces the failure.
- No merging if critical paths lack coverage.
- Tests must validate behavior, not implementation details.
- Avoid brittle mocks; prefer integration tests with a test database where possible.

---

## Performance & Scalability

- No blocking operations in async environments.
- Avoid N+1 queries; use joins or eager loading.
- Avoid unnecessary allocations in hot paths.
- All new endpoints must consider load implications and have pagination if returning lists.

---

## Security Requirements

- Validate and sanitize all user input.
- Never log secrets, tokens, or PII.
- Never hardcode credentials; use environment variables.
- Enforce least-privilege access patterns.
- All auth-sensitive changes must include test coverage.

---

## Change Control

Before modifying code:

- Understand existing architecture by tracing call graphs.
- Confirm backward compatibility.
- Avoid breaking public APIs without explicit versioning.
- Document significant decisions in code comments or README.

---

## Self-Correction & Validation

Before finalizing any task:

1.  **Review Standards:** Explicitly check your code against every section of this document.
2.  **Lint & Type Check:** Run the project's linter and type checker.
3.  **Test:** Run all relevant tests.
4.  **Clean Up:** Ensure no unrelated file changes or temporary artifacts remain.
5.  **Verify Integrity:** Confirm no architectural drift was introduced.
