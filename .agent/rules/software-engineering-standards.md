---
trigger: model_decision
description: Activate for any code creation, modification, refactor, bug fix, test, or architecture change. These standards apply universally — no exceptions.
---

# Software Engineering Standards

These standards exist to keep the codebase predictable, safe, and easy to change. When a standard feels bureaucratic, it's usually protecting against a real failure mode. Understand the why, not just the rule.

---

## Architecture Discipline

Good architecture makes future changes cheap. These rules prevent the most common forms of drift:

- **Separation of concerns**: controllers/routes handle HTTP only; services contain business logic; repositories handle data access. When these mix, changes to one layer break others unexpectedly.
- **No circular dependencies**: a dependency cycle is a design smell — split the shared logic into a third module.
- **Clear module boundaries**: every module has one reason to exist. If you can't name it in 5 words, it's probably doing too much.
- **Prefer simple, composable designs**: complexity compounds. A simple design with good interfaces beats a clever abstraction that nobody understands in 6 months.

---

## Type & Safety Enforcement

Type errors caught at compile/lint time are free. Type errors caught in production are expensive:

- No `any`, no implicit types — if you don't know the type, figure it out.
- No unchecked null/undefined access — use optional chaining, explicit guards, or non-null assertions with a comment explaining why it's safe.
- All external inputs validated at the boundary — nothing from the outside world enters the system unvalidated (use Pydantic, Zod, etc.).
- All async operations must handle failure paths — unhandled rejections and uncaught exceptions are silent data corruption waiting to happen.
- Never swallow errors silently — always log before returning or re-throwing.

---

## Code Quality

Code is read far more often than it's written. Optimize for the reader:

- Functions < 50 lines, single purpose. If you need a comment to explain what a section does, it should probably be its own function.
- Extract duplicated logic after the second use (not the first — wait to see the real pattern).
- Avoid premature abstraction. Write the concrete implementation twice, then abstract.
- All public functions: descriptive names, docstrings/JSDoc with parameter descriptions.
- Remove dead code immediately — it misleads readers and adds maintenance burden.
- No commented-out code in commits — use git history for that.

---

## Testing Requirements

Tests are the proof that code does what it claims:

- Every new public function or API endpoint → at least one unit or integration test.
- Every bug fix → a regression test that would have caught the bug. This prevents it from silently returning.
- Tests must validate **behavior** not **implementation** — test what it does, not how it does it. Tests coupled to implementation break on every refactor.
- Prefer integration tests with a real test database over heavy mocking when the logic involves data persistence.
- No skipping tests to make CI pass — fix the underlying issue.

---

## Execution Environment (Docker Mandatory)

To ensure consistency and avoid environment drift:

- **All tests, builds, and complex commands** (e.g., database migrations, dependency installs) **MUST** run inside the project's Docker containers.
- **Never rely on the host machine's global Python/Node environment**.
- Use `docker compose run --rm <service> <command>` for one-off tasks.

---

## Global Observability (O11y)

All agents, workflows, and skills operate under a mandatory observability mandate:

- **Record Every Friction Point**: Any technical hurdle (environment drift, tool failure, dependency gap, API delay) **MUST** be recorded in `.agent/logs/FRICTION.md`.
- **Systemic Learning**: Friction logs are the "Black Box" of the pipeline. They are used for automated self-correction and infrastructure hardening.
- **Log Format**: Date, Task, Type, Friction, Resolution, and Action Required.

---

## Pipeline Control (Sequential-Thinking Mandatory)

All multi-step tasks MUST use the `sequential-thinking` MCP tool:

- **Before implementation**: Break the task into numbered thoughts. Assess scope, trace call graph, plan changes.
- **At phase gates**: Validate prerequisites before transitioning to the next phase.
- **On failure**: Use a revision thought to reassess approach before retrying.
- **Never skip**: Even "simple" tasks benefit from structured reasoning. The overhead is trivial; the cost of a wrong approach is not.

---

## Performance & Scalability

Performance problems in production are the hardest to debug:

- No blocking operations in async environments.
- No N+1 queries — if you're calling the database in a loop, use a join or eager load.
- All list-returning endpoints must have pagination (no unbounded queries).
- Avoid unnecessary allocations in hot paths.

---

## Security Requirements

Security mistakes are often invisible until they're catastrophic:

- Validate and sanitize all user input — never trust external data.
- Never log secrets, tokens, session IDs, or PII.
- Never hardcode credentials — use environment variables, referenced in `.env.example`.
- Enforce least-privilege: components should only have access to what they need.
- Auth-sensitive changes (login, sessions, permissions) must have test coverage.

---

## Change Control

Understand before you change:

- Read the call graph before modifying — trace from entrypoint to understand blast radius.
- Confirm backward compatibility before changing public APIs.
- If breaking a public API, version it explicitly.
- Document significant decisions with a comment or README update — future maintainers will thank you.

---

## CHANGELOG Discipline

Every user-visible or behavior-changing commit deserves a CHANGELOG entry:

```markdown
## [Unreleased]

### Added
- feat(auth): implement OAuth2 PKCE flow (#42)

### Fixed
- fix(api): handle null response from upstream (#38)

### Security
- security(deps): bump axios to 1.6.8 (CVE-2024-xxxxx)
```

Categories: Added / Fixed / Changed / Removed / Security / Performance / Deprecated

---

## Self-Correction Checklist

Before finalizing any task, explicitly verify:

1. **Architecture**: Does this respect layer boundaries? Any circular deps?
2. **Types**: Is everything typed? No any? No unsafe null access?
3. **Tests**: Is new behavior covered? Is the bug regression-tested?
4. **Execution**: Were all tests and builds run inside Docker? Any local environment leaks?
5. **Lint + Typecheck**: Run both (inside Docker). Fix every warning.
5. **CHANGELOG**: Updated under [Unreleased]?
6. **O11y**: Have all technical hurdles been logged in .agent/logs/FRICTION.md?
7. **Diff review**: Are all changed files intentional? No temp files?
8. **Secrets**: No credentials, tokens, or PII in the diff?
