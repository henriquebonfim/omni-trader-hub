---
description: /start-workflow
---

# Execution Sequence

1. **Strategic Planning**: Use the Context7 and Sequential Thinking MCP to read and analyze `TODO.md` to identify the next priority tasks and form a strategic plan.
2. **Issue Fetching**: Execute the `/handle-issues` workflow to process all GitHub issues and generate a detailed `TASKS.md` file based on the analysis.
3. **Agent Assignment**: Use `jules new` or `jules remote new` to hand off one fully described task from `TASKS.md` to the Jules engineering team.
4. **Agent Execution**: Await Jules to complete the task and create a PR with a full description of the solution.
5. **Code Review**: Perform manual code review on the individual PRs.
   - Run `/handle-pr-review <PR_NUMBER>` to perform AI code review without code changes.
   - Run `/handle-pr-code <PR_NUMBER>` if AI code modifications are required.
6. **Revisions**: If changes are requested or PR comments are added, mention `@jules` in the comment to re-trigger the agent on the related problem.
7. **Completion**: Once the manual review is finished and the PR is ready to merge, run the `/handle-close-pr <PR_NUMBER>` workflow to finalize the PR and clean up the session.
8. **Specialized Assistance**: Use the `ui-ux-pro-max` and `software-engineer-worker` skills as needed for UI/UX tasks and specific software engineering tasks.
