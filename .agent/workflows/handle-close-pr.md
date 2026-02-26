---
description: /handle-close-pr <PR_NUMBER>
---

# Execution Sequence

1. Ensure `.agent/tmp/` exists.
2. Ensure `.agent/tmp/` is listed in `.gitignore`.

3. Merge the PR and delete the branch:

   gh pr merge <PR_NUMBER> --merge --delete-branch

   *(Use `--squash` or `--rebase` depending on your repository's preferred merge strategy)*

4. Cleanup the local and remote session references:
   - Run `jules remote list --session` to check active sessions.
   - Clean up any local branches and temporary states that were created for this PR.

5. Final Validation:
   - Ensure the PR is successfully merged (`gh pr view <PR_NUMBER>`).
   - Ensure the respective branch is deleted.
   - Clear the `.agent/tmp/` directory.

---

# Abort Conditions

Abort if:

- PR cannot be merged due to conflicts or failing checks.
- PR number is invalid or not accessible.
- Repository is in an unstable state.

---

# Success Condition

Workflow completes only when:

- PR is successfully merged and closed.
- Associated branch is deleted.
- Temporary artifacts and Jules sessions are verified cleaned up.
