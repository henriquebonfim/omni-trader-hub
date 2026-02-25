---
name: pr-review-orchestrator
description: Deterministic, structured, read-only pull request review that replies directly to file-level review threads with "CHANGES REQUESTED" status
trigger: when user references reviewing a PR without making code changes
---

# THINKING PROTOCOL (MANDATORY)

Before writing any review comment:

1. Fetch PR metadata.
2. Fetch changed files (NOT full repo context).
3. Fetch existing review threads (to avoid duplication).
4. Build compact structured matrix:

.agent/tmp/pr-review-orchestrator-matrix.json

Schema (token-optimized):

[
  {
    path,               // file path
    line,               // line number in diff
    severity,           // LOW | MEDIUM | HIGH
    category,           // BUG | SAFETY | PERF | SECURITY | ARCH | TEST
    message,            // short problem statement
    required_action     // short corrective directive
  }
]

Rules:

- Only store issues.
- Do NOT store full diff.
- Do NOT store entire file contents.
- Do NOT store analysis narrative.
- One entry per actionable problem.
- Skip files with no issues.

No review comments before full diff scan completes.

---

# EXECUTION WORKFLOW

## Phase 1 — Discovery (Performance Optimized)

Fetch minimal data:

gh pr view <PR_NUMBER> --json number,headRefName
gh pr diff <PR_NUMBER> --name-only
gh api repos/:owner/:repo/pulls/<PR_NUMBER>/comments

Do NOT fetch entire repository.
Analyze only changed hunks.

---

## Phase 2 — File-Level Targeted Review

For each changed file:

Analyze only modified lines.

Detect:

- Runtime failure risks
- Null/undefined access
- Missing error handling
- Unsafe async usage
- Security exposure
- Performance regression
- Architectural boundary violation
- Missing test coverage (when logic added)

For each issue found:

Append minimal entry to:

.agent/tmp/pr-review-orchestrator-matrix.json

Do not generate commentary yet.

---

## Phase 3 — Thread Mapping (NEW)

For each detected issue:

- Identify correct diff position.
- Determine if an existing thread already exists for same line.
- If thread exists → reply in thread.
- If no thread → create new review comment tied to file and line.

Never duplicate existing concerns.

---

# PHASE 4 — Structured Per-File Comment Replies

For each issue entry:

Use file-level review comment (not generic PR comment):

gh pr review <PR_NUMBER> \
  --request-changes \
  --comment \
  --body "<structured message>" \
  --path "<file_path>" \
  --line <line_number>

Structured format (MANDATORY):

Status: ⚠️ CHANGES REQUESTED
Severity: <LOW|MEDIUM|HIGH>
Category: <BUG|SAFETY|PERF|SECURITY|ARCH|TEST>

Problem:
- Concise description

Required Fix:
- Concrete corrective direction

Do not bundle unrelated issues.
One comment per issue entry.

---

# PHASE 5 — Final Review State

If pr-review-orchestrator-matrix.json is empty:

gh pr review <PR_NUMBER> --approve

If at least one issue exists:

gh pr review <PR_NUMBER> --request-changes

Never leave PR without explicit decision.

---

# PHASE 6 — Cleanup

- Delete .agent/tmp/pr-review-orchestrator-matrix.json
- Ensure no temp artifacts staged

---

# SELF-VALIDATION

Before submission:

- Confirm no commits created.
- Confirm no file modifications made.
- Confirm each issue tied to exact file + line.
- Confirm no duplicated review threads.
- Confirm structured pattern respected.
- Confirm minimal token footprint (no stored diffs).

---

# COMPLETION CRITERIA

- All changed files scanned.
- Each detected issue has file-level "CHANGES REQUESTED" comment.
- Review decision submitted.
- No code modified.
- `.agent/tmp/` empty.
