---
description: /handle-pr-code <PR_NUMBER>
---

# Execution Sequence

1. Ensure `.agent/tmp/` exists.
2. Ensure `.agent/tmp/` is listed in `.gitignore`.

3. Load Skill:
   pr-code-orchestrator

4. Checkout PR:

   gh pr checkout <PR_NUMBER>

5. Execute:

   - Discovery
   - Classification
   - Task Planning
   - Veto Check
   - Nested /handle-code executions
   - Structured Per-Comment Replies
   - Issue Creation (if required)
   - Cleanup

6. Final Validation:

   gh pr view <PR_NUMBER>

Ensure:

- All comments have status replies.
- No unresolved threads.
- CI passing.
- `.agent/tmp/` empty.
- No temp files staged.

---

# Abort Conditions

Abort if:

- Protected branch violation.
- Large redesign required without issue creation.
- Test suite unstable beyond safe repair.

---

# Success Condition

Workflow completes only when:

- All comments resolved, escalated, or explicitly marked.
- Replies follow structured status pattern.
- Code validated.
- No temporary artifacts remain.
