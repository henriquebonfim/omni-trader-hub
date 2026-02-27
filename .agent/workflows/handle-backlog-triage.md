---
description: /handle-backlog-triage
---

# Handle Backlog Triage

Lightweight triage cycle — no Docker build, no visual review. Just issues → three planning files. Use for quick daily triage or when only GitHub issues need to be processed.

For full product health review (Docker + tests + visual), use `/handle-po-review`.

---

## When to run

```
/handle-backlog-triage
```

Triggers for:
- "triage the issues"
- "update the backlog quickly"
- "process new issues"
- "sort the issues into tasks and backlog"
- Daily standup prep

---

## Step 1 — Read Current State

```bash
[ -f TASKS.md ]   && echo "TASKS:" && grep -c "\- \[ \]" TASKS.md || echo "0" && echo " open items"
[ -f TODO.md ]    && echo "TODO:"  && grep -c "\- \[ \]" TODO.md  || echo "0" && echo " open items"
[ -f BACKLOG.md ] && echo "BACKLOG:" && grep -c "\- \[ \]" BACKLOG.md || echo "0" && echo " open items"
```

---

## Step 2 — Fetch Issues

```bash
mkdir -p .agent/skills/po-lifecycle-orchestrator/tmp

gh issue list \
  --state open --limit 200 \
  --json number,title,body,labels,assignees,milestone,createdAt,updatedAt \
  > .agent/skills/po-lifecycle-orchestrator/tmp/gh-issues-open.json

gh issue list \
  --state closed --limit 30 \
  --json number,title,closedAt,labels \
  > .agent/skills/po-lifecycle-orchestrator/tmp/gh-issues-closed.json

gh pr list \
  --state open \
  --json number,title,headRefName \
  > .agent/skills/po-lifecycle-orchestrator/tmp/open-prs.json

gh pr list \
  --state merged --limit 15 \
  --json number,title,mergedAt,body \
  > .agent/skills/po-lifecycle-orchestrator/tmp/merged-prs.json
```

---

## Step 3 — Triage (Issues Only)

```bash
python3 .agent/skills/po-lifecycle-orchestrator/scripts/gather_and_triage.py \
  --issues  .agent/skills/po-lifecycle-orchestrator/tmp/gh-issues-open.json \
  --closed  .agent/skills/po-lifecycle-orchestrator/tmp/gh-issues-closed.json \
  --prs     .agent/skills/po-lifecycle-orchestrator/tmp/open-prs.json \
  --merged  .agent/skills/po-lifecycle-orchestrator/tmp/merged-prs.json \
  --output-dir .agent/skills/po-lifecycle-orchestrator/tmp/
```

---

## Step 4 — Post Issue Comments

```bash
python3 .agent/skills/po-lifecycle-orchestrator/scripts/post_triage_comments.py \
  --matrix .agent/skills/po-lifecycle-orchestrator/tmp/triage-matrix.json
```

---

## Step 5 — Commit

```bash
git add TASKS.md TODO.md BACKLOG.md
git commit -m "chore(po): triage $(date +%Y-%m-%d)" 2>/dev/null || echo "No changes to commit"
```

---

## Step 6 — Cleanup

```bash
rm -f .agent/skills/po-lifecycle-orchestrator/tmp/*.json
```

---

## Output

```
TASKS.md  — N priority items
TODO.md   — N next-sprint items
BACKLOG.md — N deferred items

Top task: /start-workflow
```
