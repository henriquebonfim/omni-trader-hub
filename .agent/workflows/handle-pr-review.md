---
description: /handle-pr-review <PR_NUMBER>
---

# Execution Sequence

1. Ensure `.agent/tmp/` exists.
2. Ensure `.agent/tmp/` in `.gitignore`.

3. Load Skill:
   pr-review-orchestrator

4. Checkout PR branch:

   gh pr checkout <PR_NUMBER>

5. Execute:
   - Full diff analysis
   - File-by-file validation
   - Risk classification
   - Structured review comments
   - Final approval or request-changes
   - Cleanup

6. Final Verification:
   - No commits created
   - No branch modified
   - No temp files staged
   - Review state submitted

---

# Abort Conditions

Abort if:

- PR cannot be checked out
- Diff retrieval fails
- Repository in unstable state

---

# Success Condition

Workflow completes only when:

- All changed files analyzed
- Structured review comments posted
- Final review decision submitted
- No code changes performed
- `.agent/tmp/` empty
