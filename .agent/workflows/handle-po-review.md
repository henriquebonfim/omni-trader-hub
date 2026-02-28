---
description: /handle-po-review
---

# Handle PO Review

Full Product Owner cycle: aggregate → health check → live review → triage → write planning files.

---

## Step 1 — Load Skill

```
po-lifecycle-orchestrator
```

## Step 2 — Setup

```bash
mkdir -p .agent/tmp
```

## Step 3 — Context Scan

```bash
[ -f TASKS.md ]   && cat TASKS.md
[ -f TODO.md ]    && cat TODO.md
[ -f BACKLOG.md ] && cat BACKLOG.md
[ -f README.md ]  && head -80 README.md
```

## Step 4 — Aggregate Issues

```bash
echo "Skipping bash gh CLI — data is now fetched natively in Python."
```

## Step 5 — System Health

```bash
make build 2>&1 | tail -20; echo "Build: $?"
make test  2>&1 | tail -20; echo "Tests: $?"
```

> **STRICT**: Use `make` targets only. Never guess package managers.

## Step 6 — Visual Review (browser-agent)

Detect app URL → invoke browser-agent for live product review → record findings in `tmp/visual-review.json`.

## Step 7 — Triage

```bash
make po-triage ARGS="--output-dir .agent/tmp/"
```

## Step 8 — Post to GitHub

```bash
make po-post ARGS="--matrix .agent/tmp/triage-matrix.json"
git add TASKS.md TODO.md BACKLOG.md
git commit -m "chore(po): update planning files — $(date +%Y-%m-%d)"
```

## Step 9 — Cleanup

```bash
make clean-tmp
```

---

## Success: TASKS.md + TODO.md + BACKLOG.md updated · Issues commented · Ready for `/start-workflow`
