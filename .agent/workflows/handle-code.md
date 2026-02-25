---
description: /handle-code <short_description>
---

# Execution Sequence

1. Load Skill:
   software-engineer

2. Execute:

   - Discovery
   - Design
   - Veto Check
   - Implementation
   - Self-Correction & Verification (MANDATORY)
   - Final Validation
   - Self-healing loop if required

3. After successful validation:

   - Ensure code is verified against `software-engineering-standards.md`.
   - Ensure tests included.
   - Ensure no unrelated file changes.
   - Ensure architecture boundaries respected.

---

# Abort Conditions

Abort if:

- Architectural redesign required beyond scope.
- Requirements unclear.
- Backward compatibility risk unresolvable.
- Test suite instability cannot be stabilized safely.

---

# Success Condition

Workflow completes only when:

- Feature or fix implemented cleanly.
- Tests passing.
- No lint/type errors.
- No architectural violations.
- Diff minimal and scoped.
