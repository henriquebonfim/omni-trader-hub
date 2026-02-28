---
trigger: model_decision
description: Governs structured PR implementation workflows. Apply whenever implementing review feedback, fixing PR comments, or modifying code within an active PR.
---

# PR Code Standards

---

## Branch Discipline

Always begin by checking out the PR branch:

```bash
gh pr checkout <PR_NUMBER>
```

Then validate:

```bash
BRANCH=$(git branch --show-current)
EXPECTED=$(gh pr view <PR_NUMBER> --json headRefName --jq .headRefName)
[[ "$BRANCH" == "$EXPECTED" ]] || echo "WARNING: Branch mismatch"
[[ "$BRANCH" == "main" || "$BRANCH" == "master" || "$BRANCH" == "production" ]] && echo "ABORT: protected branch" && exit 1
```

Hard constraints — never:
- Force push
- Rebase under active review (unless explicitly approved)
- Create a new branch
- Amend historical commits
- Modify unrelated files
- Introduce drive-by refactors

---

## Runtime Validation (MANDATORY)

Before ANY code changes:

1. Install dependencies
2. Build project
3. Run lint
4. Run type-check
5. Run full test suite

Store only summarized status in `tmp/runtime-summary.json`:
```json
{"build":"PASS|FAIL","lint":"PASS|FAIL|N/A","typecheck":"PASS|FAIL|N/A","tests":"PASS|FAIL|N/A"}
```

If baseline already failing:
- Mark affected comments `UNSOLVED` with "baseline already failing"  
- Do NOT introduce fixes outside scope

After each commit: re-run build + tests. Zero regressions.

---

## Temporary Artifacts

Location: `.agent/tmp/`

Allowed files:
- `pr-meta.json`
- `review-comments.json`
- `pr-code-matrix.json`
- `task-plan.json`
- `runtime-summary.json`
- `changed-files.txt`

Rules:
- Never store full diffs or full comment bodies in artifacts
- Never commit temp files
- `.agent/tmp/` must be in `.gitignore`
- Delete all after workflow completion

---

## Commit Standards

Follow Conventional Commits:

```
fix(auth): validate null token before decode

Addresses PR #123 comment:
https://github.com/org/repo/pull/123#discussion_r456
```

- One logical change per commit
- Never bundle unrelated fixes
- Each commit references the PR comment URL in body
- Never squash without approval

---

## Comment Reply Pattern

Every PR comment gets exactly ONE structured reply. Never bundle replies. Never close silently.

### ✅ SOLVED
```
**Status: ✅ SOLVED**
Commit: `<SHA>`

**Summary:**
- What changed
- Why it resolves the feedback
- Tests added/updated
```

### ❌ UNSOLVED
```
**Status: ❌ UNSOLVED**

**Reason:** <technical explanation>
**Blocker:** <what is required to proceed>
```

### 🆕 NEW ISSUE
```
**Status: 🆕 NEW ISSUE**
Issue: #<number>

**Reason:** Exceeds scope of this PR — tracked separately
```

### ⏭ SKIPPED
```
**Status: ⏭ SKIPPED**

**Reason:** <invalid / outdated / already resolved>
```

---

## Tooling: gh CLI Only

```bash
gh pr view <N>             # PR metadata
gh pr diff <N>             # Changed files + diff
gh pr checkout <N>         # Branch checkout
gh pr checks <N>           # CI status
gh pr comment <N>          # General comment
gh api repos/.../pulls/comments/<ID>/replies  # Inline reply
gh issue create            # Create follow-up issues
```

---

## Final Validation

Before completion:

- [ ] PR branch active, not protected branch
- [ ] Build passing
- [ ] Tests passing, zero regressions
- [ ] Every comment has exactly one structured reply
- [ ] No unrelated file changes in diff
- [ ] No force push
- [ ] tmp/ cleared
- [ ] `git status` clean
