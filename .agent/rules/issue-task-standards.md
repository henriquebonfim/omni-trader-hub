---
trigger: model_decision
description: Governs the transformation of GitHub issues into engineering tasks. Apply whenever processing, triaging, or acting on GitHub issues.
---

# Issue Task Standards

---

## Branch Safety (STRICT)

Before any implementation:

```bash
BRANCH=$(git branch --show-current)
PROTECTED=("main" "master" "production")

for p in "${PROTECTED[@]}"; do
  if [[ "$BRANCH" == "$p" ]]; then
    git checkout -b "feature/issues-batch-$(date +%Y%m%d%H%M%S)"
    break
  fi
done
```

Never commit directly to protected branches. All confirmed issue work lives on a dedicated feature branch. A new PR is mandatory.

---

## Mandatory PR Creation

After implementing confirmed issues:

```bash
gh pr create \
  --title "feat: resolve confirmed issues batch $(date +%Y-%m-%d)" \
  --body "$(generate-closes-references)"
```

- PR body must include `Closes #N` for every confirmed issue
- One PR per triage batch
- No mixing unrelated work

---

## Jules Session Integration

When working with Jules remote sessions:

- **Mandatory Pull with Apply**: Always use `jules remote pull --session <ID> --apply` to bring changes into the local workspace.
- **Verification**: After pulling, verify the changes inside Docker before pushing or creating a PR.
- **Branch Management**: Always create a local branch *before* applying the Jules session result.

---

## Tooling: gh CLI Only

All GitHub operations use the gh CLI:

```bash
gh issue list              # Fetch issues
gh issue view <N>          # Read full issue
gh issue comment <N>       # Post reply
gh issue close <N>         # Close resolved/invalid
gh pr create               # Create batch PR
gh api                     # Advanced operations
```

No web UI simulation. No manual workarounds.

---

## Temporary Artifacts

All temp files in `.agent/skills/issue-task-orchestrator/tmp/`:

- `raw-issues.json` — fetched from gh API
- `open-prs.json` — active PRs for duplicate detection
- `recent-merged.json` — for resolved detection
- `issue-matrix.json` — scored classification matrix

Rules:
- `.agent/skills/issue-task-orchestrator/tmp/` must be in `.gitignore`
- Never commit temp files
- Delete all after workflow completion

---

## Per-Issue Status Pattern

Each issue gets exactly one structured status reply. Formats:

### ✅ CONFIRMED TASK
```
**Status: ✅ CONFIRMED TASK**

**Scope:**
- <files/functions to modify>
- <tests to create/update>

**Priority Score:** N/40

**PR:** Included in upcoming batch PR
```

### ❌ NEEDS CLARIFICATION
```
**Status: ❌ NEEDS CLARIFICATION**

**Missing:**
- <specific information required>
```

### 🟢 ALREADY RESOLVED
```
**Status: 🟢 ALREADY RESOLVED**

**Evidence:** PR #N / commit `sha`
```
→ Close the issue after posting.

### ⏭ INVALID / WON'T FIX
```
**Status: ⏭ INVALID**

**Reason:** <technical explanation>
```
→ Close the issue after posting.

---

## Engineering Validation Requirement

Before confirming any issue:

- Bug: locate the failing code path, confirm not already patched
- Feature: validate architecture alignment and minimal viable scope
- Refactor: confirm no public API breaks

No speculative tasks. No tasks added without validation.

---

## Completion Requirements

- [ ] All issues fetched and classified
- [ ] Matrix saved to tmp/
- [ ] Priority scores computed
- [ ] Structured replies posted to all issues
- [ ] Confirmed issues implemented on feature branch
- [ ] PR created with `Closes #N` references
- [ ] tmp/ cleared
- [ ] TASKS.md generated for Jules handoff
