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

## Step 2 — Aggregate Issues

```bash
echo "Skipping bash gh CLI — data is now fetched natively in Python."
```

---

## Step 3 — Triage (Issues Only)

```bash
make po-triage ARGS="--output-dir .agent/tmp/"
```

---

## Step 4 — Post Issue Comments

```bash
make po-post ARGS="--matrix .agent/tmp/triage-matrix.json"
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
make clean-tmp
```

---

## Output

```
TASKS.md  — N priority items
TODO.md   — N next-sprint items
BACKLOG.md — N deferred items

Top task: /start-workflow
```
