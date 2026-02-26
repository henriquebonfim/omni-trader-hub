---
description: /handle-issues
---

# Execution Sequence

1. Ensure `.agent/tmp/` exists.
2. Ensure `.agent/tmp/` in `.gitignore`.

3. Load Skill:
   issue-task-orchestrator

4. Execute:
   - Discovery
   - Classification
   - Engineering validation
   - Strict branch safety check
   - Structured per-issue replies
   - Confirmed task execution via /handle-code
   - Mandatory PR creation
   - Generation of structured `TASKS.md` file (e.g. `gh issue list --json title,body > TASKS.md` or similar structured output) for handoff to the Jules CLI
   - Cleanup

5. Final Validation:

   gh pr view

Ensure:

- No commits made to main/master/production
- New PR created
- PR references all confirmed issues
- All issues handled
- `.agent/tmp/` empty
- No temp artifacts staged

---

# Abort Conditions

Abort if:

- Protected branch cannot be switched
- Test suite globally unstable
- Massive architectural redesign required

---

# Success Condition

Workflow completes only when:

- All open issues reviewed
- Confirmed ones implemented
- New PR created referencing them
- Protected branches untouched
- Repository stable
- No temporary artifacts remain
