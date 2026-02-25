---
trigger: model_decision
description: Transform Github issues into tasks
---

## Branch Safety Enforcement (STRICT)

Before any implementation:

- Current branch MUST NOT be:
  - main
  - master
  - production
- If on protected branch:
  - Create new branch:
    feature/issues-batch-<timestamp>
  - Never commit directly to protected branches.
- All confirmed issue implementations must be done in a dedicated branch.
- A new PR must be created referencing all confirmed issues.

---

## Mandatory PR Creation Rule (NEW)

After confirmed issues are implemented:

- A new PR must be created.
- The PR body must reference all confirmed issues using:

Closes #<issue_number>

- One PR per issue batch execution.
- Do not mix unrelated work.

---

## Temporary Artifact Control

All issue analysis artifacts must live under:

.agent/tmp/

Allowed files:

- issue-matrix.json
- issue-task-plan.json

Rules:

- No temp files outside `.agent/tmp/`
- No temp files committed
- `.agent/tmp/` must be in `.gitignore`
- All temp files deleted after workflow completion

---

## Mandatory Per-Issue Status Pattern

Each issue must receive exactly one structured reply:

### ✅ CONFIRMED TASK

Status: ✅ CONFIRMED TASK

Scope:

- Implementation boundaries: Describe exactly which files/functions will be modified.

PR:

- Will be included in new PR

**Example:**
Status: ✅ CONFIRMED TASK

Scope:

- Implement the `ADXTrendStrategy` in `backend/src/strategies/adx_trend.py`.
- Register the new strategy in `backend/src/strategies/registry.py`.
- Add unit tests in `backend/tests/test_strategies.py`.

PR:

- Will be included in new PR

---

### ❌ NEEDS CLARIFICATION

Status: ❌ NEEDS CLARIFICATION

Missing:

- Explicit missing details: List the specific information required from the user.

**Example:**
Status: ❌ NEEDS CLARIFICATION

Missing:

- Please specify the target timeframe for the ADX calculation (e.g., 1m, 5m, 1h).
- Clarify if the strategy should use a fixed stop-loss or a trailing one.

---

### 🟢 ALREADY RESOLVED

Status: 🟢 ALREADY RESOLVED

Evidence:

- Commit or PR reference: Link to the specific commit or pull request.

**Example:**
Status: 🟢 ALREADY RESOLVED

Evidence:

- Feature implemented in commit `a1b2c3d` and merged in PR #42.

Issue should be closed.

---

### ⏭ INVALID / WON’T FIX

Status: ⏭ INVALID

Reason:

- Technical explanation: Why this issue cannot or will not be addressed.

**Example:**
Status: ⏭ INVALID

Reason:

- The requested feature is already covered by the existing `BollingerBandsStrategy` with the `auto_reversal` flag enabled.

---

## Engineering Validation Requirement

Before confirming:

- Reproduce issue (if bug)
- Confirm not already fixed
- Validate architecture alignment
- Ensure minimal viable solution exists

No speculative tasks allowed.

---

## CLI Enforcement

All GitHub operations must use:

- gh issue list
- gh issue view
- gh issue comment
- gh issue close
- gh pr create
- gh api

---

## Completion Requirements

- All issues reviewed
- Only confirmed issues implemented
- New PR created referencing all confirmed issues
- No temp artifacts committed
- `.agent/tmp/` cleaned
