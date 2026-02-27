---
name: pr-review-orchestrator
description: Structured, read-only pull request review with runtime validation and batched GitHub review submission. Use when user wants to review a PR without making code changes — "review PR #N", "what do you think of this PR", "give me a code review", "check this PR". Read-only mode only — never commits or modifies code.
---

# PR Review Orchestrator

Deterministic, read-only code review. Validates runtime, analyzes every changed file, classifies risk, and submits a single structured GitHub review. Zero code modifications.

---

## Setup Check

```bash
mkdir -p .agent/skills/pr-review-orchestrator/tmp
grep -qxF '.agent/skills/pr-review-orchestrator/tmp/' .gitignore \
  || echo '.agent/skills/pr-review-orchestrator/tmp/' >> .gitignore
```

---

## Phase 0 — Branch Checkout (Read-Only)

```bash
# Checkout PR branch WITHOUT modifying anything
make gh-pr-checkout ID=<PR_NUMBER>

# Confirm current branch matches PR head
EXPECTED=$(make gh-pr-view ID=<PR_NUMBER> ARGS="--json headRefName --jq .headRefName")
CURRENT=$(git branch --show-current)
echo "Expected: $EXPECTED | Current: $CURRENT"
[[ "$EXPECTED" == "$CURRENT" ]] || echo "WARNING: Branch mismatch"
```

Run full validation suite (read-only — detect issues, do NOT fix):

```bash
# Store results in tmp/runtime-summary.json
# { "build": "PASS|FAIL", "lint": "PASS|FAIL|N/A", "typecheck": "PASS|FAIL|N/A", "tests": "PASS|FAIL|N/A", "runtime": "PASS|FAIL|N/A" }
```

---

## Phase 1 — Discovery

```bash
# PR metadata
make gh-pr-view ID=<PR_NUMBER> ARGS="--json number,title,body,state,baseRefName,headRefName,mergeable,headRefOid,author,additions,deletions,changedFiles" \
  > .agent/skills/pr-review-orchestrator/tmp/pr-meta.json

# Changed files only (analyze these, not the whole repo)
make gh-pr-diff ID=<PR_NUMBER> ARGS="--name-only" \
  > .agent/skills/pr-review-orchestrator/tmp/changed-files.txt

# Full diff for analysis
make gh-pr-diff ID=<PR_NUMBER> \
  > .agent/skills/pr-review-orchestrator/tmp/pr-diff.patch

# Existing review threads (avoid duplicating resolved comments)
make gh-api ENDPOINT="repos/{owner}/{repo}/pulls/<PR_NUMBER>/comments" ARGS="--jq '[.[] | {id:.id, path:.path, line:.line, body:.body, resolved:(.resolved // false)}]' " \
  > .agent/skills/pr-review-orchestrator/tmp/existing-comments.json
```

---

## Phase 2 — File-by-File Analysis

Read `changed-files.txt` and analyze **only the changed lines** in each file using the diff.

For each changed file, detect:

| Category | What to look for |
|----------|-----------------|
| `BUG` | Null/undefined access, off-by-one, wrong operator, unhandled rejection, logic inversion |
| `SAFETY` | Unchecked external input, missing validation at boundaries, unhandled error paths |
| `SECURITY` | SQL/command injection risk, hardcoded secrets, insecure direct object reference, missing auth check |
| `PERF` | N+1 queries, blocking in async context, unnecessary re-renders, missing pagination |
| `ARCH` | Business logic in controller/route, circular dependency, cross-layer data access |
| `TEST` | New public function without tests, bug fix without regression test |

Write findings to `tmp/review-matrix.json`:

```json
[
  {
    "path": "src/auth/login.ts",
    "line": 47,
    "severity": "HIGH",
    "category": "SECURITY",
    "message": "User-supplied `redirectUrl` is not validated against an allowlist — open redirect vulnerability."
  }
]
```

**Severity rules:**

| Severity | Criteria |
|----------|----------|
| `HIGH` | Runtime failure risk, security exposure, data loss |
| `MEDIUM` | Bug that affects functionality but not catastrophically |
| `LOW` | Style, naming, minor inefficiency |

Skip clean files. Only record actionable findings.

---

## Phase 3 — Risk Classification

After full analysis, classify the overall PR:

| Risk Level | Condition |
|------------|-----------|
| `HIGH RISK` | Runtime fails, security issues present, or HIGH severity findings |
| `MEDIUM RISK` | Test failures, MEDIUM severity findings, missing test coverage on critical paths |
| `LOW RISK` | Only LOW findings, all tests pass |
| `SAFE` | No findings, all validation passes |

---

## Phase 4 — Submit Review

Run the batch review script:

```bash
make pr-review PR=<PR_NUMBER>
```

Or manually compose the review:

```bash
# Get commit SHA for review anchoring
COMMIT_SHA=$(gh pr view <PR_NUMBER> --json headRefOid --jq .headRefOid)
PR_AUTHOR=$(gh pr view <PR_NUMBER> --json author --jq .author.login)
CURRENT_USER=$(gh api user --jq .login)

# Decide event type
# If author == current user → COMMENT (can't approve/request own PR)
# If findings present → REQUEST_CHANGES
# If clean → APPROVE

# Build review body
RUNTIME_SUMMARY=$(cat .agent/skills/pr-review-orchestrator/tmp/runtime-summary.json 2>/dev/null || echo '{}')

gh api \
  "repos/{owner}/{repo}/pulls/<PR_NUMBER>/reviews" \
  --method POST \
  --input .agent/skills/pr-review-orchestrator/tmp/review-payload.json
```

**Review body template:**

```markdown
## Code Review — PR #<N>

**Overall Risk:** <SAFE|LOW RISK|MEDIUM RISK|HIGH RISK>

### Runtime Validation
- Build: <PASS/FAIL>
- Lint: <PASS/FAIL/N/A>
- Type Check: <PASS/FAIL/N/A>
- Tests: <PASS/FAIL/N/A>

### Summary
<2-3 sentence description of what was found or confirmed clean.>

<If APPROVE:>
No issues detected in modified files. All validation passes. ✅

<If REQUEST_CHANGES:>
N issue(s) found in changed files. See inline comments for details.
```

**Inline comment format (per finding):**

```markdown
**Status: ⚠️ CHANGES REQUESTED**
**Severity:** HIGH | MEDIUM | LOW
**Category:** BUG | SECURITY | PERF | ARCH | TEST | SAFETY

**Problem:**
<Precise description of the issue and its location>

**Impact:**
<What goes wrong if this isn't fixed>

**Suggested Fix:**
<Concrete direction — not necessarily full code, but enough to act on>
```

---

## Phase 5 — Cleanup + Verification

```bash
# CRITICAL: Confirm no commits were made
git status
git log --oneline -3

# Clean tmp
rm -f .agent/skills/pr-review-orchestrator/tmp/*.json
rm -f .agent/skills/pr-review-orchestrator/tmp/*.patch
rm -f .agent/skills/pr-review-orchestrator/tmp/*.txt

# Final check
git status  # Must show clean working tree
```

Verify:
- [ ] No commits made (`git log` unchanged from checkout)
- [ ] No files modified (`git status` clean)
- [ ] Review submitted via `gh api`
- [ ] `tmp/` cleared
- [ ] Risk level stated in review body

---

## Hard Constraints

These are **never** negotiable:

- ❌ No code edits during review
- ❌ No commits
- ❌ No branch creation
- ❌ No force push
- ❌ No file creation outside `.agent/*/tmp/`
- ❌ No fixing failing tests or build errors (report only)
