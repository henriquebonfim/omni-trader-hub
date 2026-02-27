---
description: /handle-po-review
---

# Handle PO Review

Full Product Owner review cycle. Aggregates all sources, checks system health, reviews the product visually, triages everything into TASKS.md / TODO.md / BACKLOG.md, and hands off to engineering.

Run at the start of every sprint, or whenever planning files need to be refreshed.

---

## When to run

```
/handle-po-review
```

Triggers for:
- "PO review"
- "update the backlog"
- "triage everything"
- "what should we work on"
- "sprint planning"
- "product health check"
- "review the product"
- Start of any new sprint

---

## Step 1 — Load Skill

```
po-lifecycle-orchestrator
```

---

## Step 2 — Setup

```bash
mkdir -p .agent/skills/po-lifecycle-orchestrator/tmp
grep -qxF '.agent/skills/po-lifecycle-orchestrator/tmp/' .gitignore \
  || echo '.agent/skills/po-lifecycle-orchestrator/tmp/' >> .gitignore
```

---

## Step 3 — Phase 0: Context Scan

```bash
# Read existing planning files first
[ -f TASKS.md ]   && echo "=== CURRENT TASKS.md ===" && cat TASKS.md
[ -f TODO.md ]    && echo "=== CURRENT TODO.md ===" && cat TODO.md
[ -f BACKLOG.md ] && echo "=== CURRENT BACKLOG.md ===" && cat BACKLOG.md

# Product context
[ -f README.md ]  && head -80 README.md
[ -f ROADMAP.md ] && cat ROADMAP.md
```

---

## Step 4 — Phase 1: Aggregate Issues

```bash
# Open issues
gh issue list \
  --state open --limit 200 \
  --json number,title,body,labels,assignees,milestone,createdAt,updatedAt \
  > .agent/skills/po-lifecycle-orchestrator/tmp/gh-issues-open.json

# Recently closed (last 50)
gh issue list \
  --state closed --limit 50 \
  --json number,title,closedAt,labels \
  > .agent/skills/po-lifecycle-orchestrator/tmp/gh-issues-closed.json

# Open PRs (skip in-flight work)
gh pr list \
  --state open \
  --json number,title,headRefName,author,isDraft \
  > .agent/skills/po-lifecycle-orchestrator/tmp/open-prs.json

# Merged PRs (velocity + issue resolution refs)
gh pr list \
  --state merged --limit 20 \
  --json number,title,mergedAt,body \
  > .agent/skills/po-lifecycle-orchestrator/tmp/merged-prs.json

ISSUE_COUNT=$(python3 -c "import json; print(len(json.load(open('.agent/skills/po-lifecycle-orchestrator/tmp/gh-issues-open.json'))))")
echo "Open issues: $ISSUE_COUNT"
```

---

## Step 5 — Phase 2: Docker + Test Health

```bash
# Docker build check
COMPOSE_FILE=""
for f in docker-compose.yml docker-compose.yaml compose.yml compose.yaml; do
  [ -f "$f" ] && COMPOSE_FILE="$f" && break
done

if [ -n "$COMPOSE_FILE" ]; then
  echo "Building from $COMPOSE_FILE..."
  make docker-build COMPOSE_FILE="$COMPOSE_FILE" 2>&1 | tail -20
  DOCKER_STATUS=$?

  echo "{\"compose_file\": \"$COMPOSE_FILE\", \"build_status\": \"$([ $DOCKER_STATUS -eq 0 ] && echo PASS || echo FAIL)\"}" \
    > .agent/skills/po-lifecycle-orchestrator/tmp/docker-health.json
else
  echo '{"build_status": "SKIPPED", "reason": "No compose file found"}' \
    > .agent/skills/po-lifecycle-orchestrator/tmp/docker-health.json
fi

# Test suite
TEST_CMD="make test ARGS=\"2>&1\""

if [ -n "$TEST_CMD" ]; then
  echo "Running: $TEST_CMD"
  TEST_OUTPUT=$(eval "$TEST_CMD")
  TEST_EXIT=$?
  echo "$TEST_OUTPUT" | tail -20

  # Write summary
  python3 -c "
import json, sys
output = '''${TEST_OUTPUT}'''
status = 'PASS' if ${TEST_EXIT} == 0 else 'FAIL'
# Try to parse test count from common formats
import re
summary = ''
for pattern in [r'(\d+ passed)', r'(\d+ tests? passed)', r'Tests:\s+\d+ passed']:
    m = re.search(pattern, output)
    if m:
        summary = m.group(0)
        break
print(json.dumps({'status': status, 'exit_code': ${TEST_EXIT}, 'summary': summary, 'test_cmd': '${TEST_CMD}'}))
" > .agent/skills/po-lifecycle-orchestrator/tmp/test-health.json 2>/dev/null \
  || echo "{\"status\": \"$([ $TEST_EXIT -eq 0 ] && echo PASS || echo FAIL)\", \"exit_code\": $TEST_EXIT}" \
    > .agent/skills/po-lifecycle-orchestrator/tmp/test-health.json
else
  echo '{"status": "SKIPPED", "reason": "No test command detected"}' \
    > .agent/skills/po-lifecycle-orchestrator/tmp/test-health.json
fi
```

---

## Step 6 — Phase 3: Visual Product Review

Detect app URL:

```bash
# From docker-compose
APP_PORT=$(grep -A2 "ports:" "$COMPOSE_FILE" 2>/dev/null | grep -oE '"?[0-9]+:[0-9]+"?' | head -1 | cut -d: -f1 | tr -d '"' || echo "3000")

# From package.json scripts
[ -z "$APP_PORT" ] && APP_PORT=$(cat package.json 2>/dev/null | python3 -c "
import sys, json, re
try:
    d = json.load(sys.stdin)
    for v in d.get('scripts', {}).values():
        m = re.search(r'--port\s+(\d+)|PORT=(\d+)', v)
        if m:
            print(m.group(1) or m.group(2))
            break
except: pass
" 2>/dev/null || echo "3000")

APP_URL="http://localhost:${APP_PORT:-3000}"
echo "App URL: $APP_URL"
```

**If Antigravity browser is available in this session:**

→ Navigate to `$APP_URL` directly using the browser tool
→ Take screenshots of each main route
→ Record findings in `tmp/visual-review.json`

**Otherwise, use Playwright:**

```bash
mkdir -p .agent/skills/po-lifecycle-orchestrator/tmp/screenshots

make po-playwright ARGS="--url \"$APP_URL\" --output-dir .agent/skills/po-lifecycle-orchestrator/tmp/screenshots/"
```

If server isn't running:
```bash
# Static analysis fallback
echo "Server not running — running static analysis"
ROUTE_COUNT=$(find ./src -name "page.*" -o -name "*Page.*" 2>/dev/null | wc -l)
echo "Pages/views detected: $ROUTE_COUNT"

echo '{"server_reachable": false, "findings": [], "summary": "Static analysis only"}' \
  > .agent/skills/po-lifecycle-orchestrator/tmp/visual-review.json
```

---

## Step 7 — Phase 4: Triage

```bash
make po-triage ARGS="--issues .agent/skills/po-lifecycle-orchestrator/tmp/gh-issues-open.json \
  --closed .agent/skills/po-lifecycle-orchestrator/tmp/gh-issues-closed.json \
  --prs .agent/skills/po-lifecycle-orchestrator/tmp/open-prs.json \
  --merged .agent/skills/po-lifecycle-orchestrator/tmp/merged-prs.json \
  --docker .agent/skills/po-lifecycle-orchestrator/tmp/docker-health.json \
  --tests .agent/skills/po-lifecycle-orchestrator/tmp/test-health.json \
  --visual .agent/skills/po-lifecycle-orchestrator/tmp/visual-review.json \
  --output-dir .agent/skills/po-lifecycle-orchestrator/tmp/"
```

Review output:
```bash
echo "=== TASKS.md ===" && head -40 TASKS.md
echo "=== TODO.md ===" && head -30 TODO.md
echo "=== BACKLOG.md ===" && head -20 BACKLOG.md
```

---

## Step 8 — Phase 5: Post to GitHub

```bash
make po-post ARGS="--matrix .agent/skills/po-lifecycle-orchestrator/tmp/triage-matrix.json"
```

Commit the updated planning files:
```bash
git add TASKS.md TODO.md BACKLOG.md
git diff --cached --stat
git commit -m "chore(po): update planning files — sprint $(date +%Y-%m-%d)"
```

---

## Step 9 — Hand Off to Engineering

Based on TASKS.md content:

```bash
# If Docker is broken
DOCKER_STATUS=$(cat .agent/skills/po-lifecycle-orchestrator/tmp/docker-health.json | python3 -c "import sys,json; print(json.load(sys.stdin).get('build_status','SKIPPED'))")
[ "$DOCKER_STATUS" = "FAIL" ] && echo "⚠️  Docker broken — run /handle-code 'fix docker build' FIRST"

# If tests failing
TEST_STATUS=$(cat .agent/skills/po-lifecycle-orchestrator/tmp/test-health.json | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','SKIPPED'))")
[ "$TEST_STATUS" = "FAIL" ] && echo "⚠️  Tests failing — run /handle-code 'fix failing tests' BEFORE new features"

# Otherwise start engineering pipeline
echo "✅ Ready — run /start-workflow to begin engineering on TASKS.md"
```

---

## Step 10 — Cleanup

```bash
rm -f .agent/skills/po-lifecycle-orchestrator/tmp/*.json
rm -f .agent/skills/po-lifecycle-orchestrator/tmp/screenshots/*.png
# TASKS.md, TODO.md, BACKLOG.md stay — they're project artifacts
```
