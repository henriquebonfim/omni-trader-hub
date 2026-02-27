---
description: /handle-issues
---

# Handle Issues

Full issue triage, implementation, and PR creation pipeline.

---

## Execution Sequence

### 1 — Environment Setup

```bash
mkdir -p .agent/skills/issue-task-orchestrator/tmp
grep -qxF '.agent/skills/issue-task-orchestrator/tmp/' .gitignore \
  || echo '.agent/skills/issue-task-orchestrator/tmp/' >> .gitignore
```

### 2 — Load Skill

```
issue-task-orchestrator
```

### 3 — Branch Safety

```bash
BRANCH=$(git branch --show-current)
if [[ "$BRANCH" == "main" || "$BRANCH" == "master" || "$BRANCH" == "production" ]]; then
  git checkout -b "feature/issues-batch-$(date +%Y%m%d%H%M%S)"
fi
```

### 4 — Fetch & Score Issues

```bash
# Fetch raw issues
gh issue list --state open --limit 100 \
  --json number,title,body,labels,assignees,milestone,createdAt,updatedAt \
  > .agent/skills/issue-task-orchestrator/tmp/raw-issues.json

# Detect already-in-progress work
gh pr list --state open --json number,title,body,headRefName \
  > .agent/skills/issue-task-orchestrator/tmp/open-prs.json

gh pr list --state merged --limit 20 --json number,title,body,mergedAt \
  > .agent/skills/issue-task-orchestrator/tmp/recent-merged.json

# Score and rank
python3 .agent/skills/issue-task-orchestrator/scripts/score_issues.py
```

### 5 — Engineering Validation

For each CONFIRMED issue from the matrix:
- View full issue: `gh issue view <N> --json number,title,body,comments`
- Validate scope alignment
- Confirm not already fixed
- Refine status if needed

### 6 — Post Structured Replies

```bash
python3 .agent/skills/issue-task-orchestrator/scripts/post_issue_comments.py
```

### 7 — Implement Confirmed Tasks

For each CONFIRMED issue in priority order:

```
/handle-code "<scoped task>"
```

Each commit must include `Closes #<N>`.

### 8 — Generate TASKS.md

```bash
python3 -c "
import json
matrix = json.load(open('.agent/skills/issue-task-orchestrator/tmp/issue-matrix.json'))
confirmed = [i for i in matrix if i['status'] == 'CONFIRMED']
lines = ['# Tasks\n', f'Generated: $(date)\n\n']
for i, task in enumerate(confirmed, 1):
    lines.append(f'## {i}. Issue #{task[\"issue_number\"]}: {task[\"title\"]}')
    lines.append(f'- Priority Score: {task[\"priority_score\"]}')
    lines.append(f'- Classification: {task[\"classification\"]}')
    lines.append('')
print('\n'.join(lines))
" > TASKS.md
```

### 9 — Create Batch PR

```bash
ISSUE_CLOSES=$(python3 -c "
import json
m = json.load(open('.agent/skills/issue-task-orchestrator/tmp/issue-matrix.json'))
print('\n'.join(f'Closes #{i[\"issue_number\"]}' for i in m if i['status']=='CONFIRMED'))
")

gh pr create \
  --title "feat: resolve confirmed issues batch $(date +%Y-%m-%d)" \
  --body "## Batch Issue Resolution

${ISSUE_CLOSES}

## Changes
$(git log origin/main..HEAD --oneline --no-merges)

---
- [ ] All tests passing
- [ ] CHANGELOG updated
- [ ] No unrelated changes"
```

### 10 — Cleanup

```bash
rm -f .agent/skills/issue-task-orchestrator/tmp/*.json
```

### 11 — Final Validation

```bash
gh pr view  # Confirm PR created
git status  # Confirm clean
```

---

## Abort Conditions

- Cannot switch off protected branch
- Test suite globally unstable (fix before issuing new work)
- Massive architectural redesign required for any single issue

---

## Success Condition

- All open issues classified and replied to
- Confirmed ones implemented on feature branch
- PR created with `Closes #N` for each
- `tmp/` clean
- TASKS.md generated for Jules handoff
