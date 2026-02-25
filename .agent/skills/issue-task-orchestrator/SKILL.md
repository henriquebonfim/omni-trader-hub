---
name: issue-task-orchestrator
description: Deterministic transformation of GitHub issues into validated engineering tasks with strict branch and PR enforcement
trigger: when user references reviewing issues, converting issues to tasks, or processing backlog
---

# THINKING PROTOCOL (MANDATORY)

1. Fetch all open issues.
2. Build matrix:

.agent/tmp/issue-matrix.json

Schema:

{
  issue_number,
  classification,
  status,
  confirmed
}

3. Classify each issue:

- BUG
- FEATURE
- REFACTOR
- DOC
- DUPLICATE
- INVALID
- ALREADY_FIXED
- NEEDS_INFO

No implementation before full classification.

---

# EXECUTION WORKFLOW

## Phase 1 — Discovery

gh issue list --state open
gh issue view <NUMBER> --json title,body,comments

Populate matrix.

---

## Phase 2 — Engineering Validation

For each issue:

- Attempt reproduction (if applicable)
- Validate architecture alignment
- Check if already resolved
- Evaluate scope safety

Set status:

- CONFIRMED TASK
- NEEDS CLARIFICATION
- ALREADY RESOLVED
- INVALID

---

## Phase 3 — Branch Safety Check (STRICT)

Run:

git branch --show-current

If branch is:

- main
- master
- production

Then:

git checkout -b feature/issues-batch-<timestamp>

Never proceed otherwise.

---

## Phase 4 — Structured Per-Issue Reply

For each issue:

gh issue comment <NUMBER> --body "<structured status reply>"

Follow exact rule format.

---

## Phase 5 — Confirmed Task Execution

For each CONFIRMED TASK:

Invoke:

/handle-code "<scoped task derived from issue>"

Commits must reference:

Closes #<issue_number>

---

## Phase 6 — Create New PR (MANDATORY)

After all confirmed tasks implemented:

gh pr create \
  --title "Batch: Resolve confirmed issues" \
  --body "
This PR resolves the following issues:

Closes #<issue1>
Closes #<issue2>
Closes #<issue3>
"

Do not skip PR creation.

---

## Phase 7 — Cleanup

- Delete .agent/tmp/*
- Ensure no temp artifacts staged

---

# SELF-HEALING LOOP

If implementation fails:

- Attempt minimal correction
- Re-run validation
- If unstable → mark issue NEEDS CLARIFICATION

---

# COMPLETION CRITERIA

- All issues classified
- Structured replies posted
- Confirmed issues implemented
- New PR created referencing all confirmed issues
- No protected branch modified
- No temp artifacts committed
