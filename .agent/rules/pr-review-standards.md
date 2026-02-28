---
trigger: model_decision
description: Governs strict, read-only PR reviews. Apply whenever performing code review without making changes.
---

# PR Review Standards

---

## Strict No-Modification Rule

During review, the following are absolutely forbidden:

- No code edits
- No commits
- No branch creation or modification
- No force push
- No file creation outside `.agent/*/tmp/`
- No dependency installs committed
- No test files committed
- No refactors

This is a **read-only analytical workflow**. If runtime or tests fail, report via review comment — never fix code.

---

## Branch Safety

```bash
gh pr checkout <PR_NUMBER>

# Validate
EXPECTED=$(gh pr view <PR_NUMBER> --json headRefName --jq .headRefName)
CURRENT=$(git branch --show-current)
[[ "$CURRENT" == "main" || "$CURRENT" == "master" ]] && echo "WARNING: On main"
[[ "$CURRENT" == "$EXPECTED" ]] || echo "WARNING: Branch mismatch"
```

Never create a new branch. Never rebase. Never amend.

---

## Runtime Validation (MANDATORY)

After checkout:

1. Install dependencies (non-persistent)
2. Build project
3. Run lint
4. Run type-check
5. Run full test suite

Store only `PASS|FAIL|N/A` in `tmp/runtime-summary.json`.

If failure: capture the failing file/module, report as HIGH severity review comment. Do NOT fix.

---

## Temporary Artifacts

Location: `.agent/tmp/`

Allowed files:
- `pr-meta.json`
- `review-matrix.json`
- `runtime-summary.json`
- `review-payload.json`
- `changed-files.txt`
- `pr-diff.patch`

Rules:
- Never store full diffs in matrix (reference file+line only)
- Never store full comment bodies
- Never commit temp files
- Delete all after workflow completion

---

## Review Comment Pattern

Each issue produces ONE structured comment. No bundling.

### ✅ APPROVED
```
**Status: ✅ APPROVED**

**Summary:**
- Code correct for the stated intent
- All validation passes (build, lint, typecheck, tests)
- No regressions detected
```

### ⚠️ CHANGES REQUESTED
```
**Status: ⚠️ CHANGES REQUESTED**
**Severity:** HIGH | MEDIUM | LOW
**Category:** BUG | SAFETY | PERF | SECURITY | ARCH | TEST

**Problem:**
<Precise technical issue with file + line context>

**Impact:**
<What goes wrong if unfixed>

**Required Fix:**
<Concrete corrective direction>
```

### ❓ CLARIFICATION REQUIRED
```
**Status: ❓ CLARIFICATION REQUIRED**

**Concern:** <what is unclear>
**Question:** <explicit request>
```

### 🧪 TESTS MISSING
```
**Status: 🧪 TESTS MISSING**

**Missing Coverage:** <specific behavior not tested>
**Required:** <explicit test requirement>
```

---

## Risk Classification

Classify overall PR after analysis:

| Level | Condition |
|-------|-----------|
| `HIGH RISK` | Runtime fails, security issues, data loss risk |
| `MEDIUM RISK` | Test failures, missing coverage on critical paths |
| `LOW RISK` | Only LOW-severity findings, all validation passes |
| `SAFE` | No findings, full validation green |

Runtime fails → automatically `HIGH RISK`.

---

## Tooling: gh CLI Only

```bash
gh pr checkout <N>          # Branch checkout
gh pr view <N>              # PR metadata
gh pr diff <N>              # Changed files + diff
gh pr diff <N> --name-only  # Changed file list
gh api repos/.../pulls/<N>/comments     # Existing comments
gh api repos/.../pulls/<N>/reviews      # Submit review
```

---

## Final Verification

- [ ] No commits made (`git log` unchanged)
- [ ] No files modified (`git status` clean)  
- [ ] Review submitted via `gh api`
- [ ] Risk level stated in review body
- [ ] All changed files analyzed
- [ ] tmp/ empty
