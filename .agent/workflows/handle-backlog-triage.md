---
description: /handle-backlog-triage
---

# Handle Backlog Triage

Lightweight triage cycle — no Docker build, no visual review. Just issues → three planning files. Use for quick daily triage or when only GitHub issues need to be processed.

For full product health review (Docker + tests + visual), use `/handle-po-review`.

---

## Step 0 — SOP Validation Gate

```bash
python3 .agent/scripts/orchestrator.py handle-backlog-triage
ENFORCE_EXIT=$?
[ $ENFORCE_EXIT -ne 0 ] && echo "❌ SOP validation failed" && exit 1

WORKFLOW_NAME="handle-backlog-triage"
cleanup_workflow() {
  EXIT_CODE=$?
  if [ $EXIT_CODE -ne 0 ]; then
    python3 .agent/scripts/friction_logger.py \
      --task "$WORKFLOW_NAME" \
      --type "Workflow" \
      --friction "Workflow exited with code $EXIT_CODE" \
      --resolution "Inspect workflow output and rerun after fix" || true
  fi
  rm -f .agent/tmp/triage.lock
  make clean-tmp >/dev/null 2>&1 || true
}
trap cleanup_workflow EXIT
```

---

## Step 0.5 — Pre-Flight Checks

```bash
# Concurrent execution lock
LOCK_FILE=".agent/tmp/triage.lock"
if [ -f "$LOCK_FILE" ]; then
  PID=$(cat "$LOCK_FILE")
  if kill -0 "$PID" 2>/dev/null; then
    echo "❌ Another triage is running (PID: $PID)"
    exit 1
  else
    echo "⚠️  Stale lock removed"
    rm "$LOCK_FILE"
  fi
fi
echo $$ > "$LOCK_FILE"

# GitHub API rate limit check
RATE_LIMIT=$(gh api rate_limit --jq '.rate.remaining' 2>/dev/null || echo "0")
if [ "$RATE_LIMIT" -lt 10 ]; then
  RESET_TIME=$(gh api rate_limit --jq '.rate.reset' 2>/dev/null || echo "unknown")
  echo "❌ GitHub API rate limit low: $RATE_LIMIT requests remaining"
  echo "Rate limit resets at: $(date -d @${RESET_TIME} 2>/dev/null || echo 'unknown')"
  exit 1
fi

# Network connectivity check
if ! curl -s --connect-timeout 3 https://api.github.com >/dev/null 2>&1; then
  echo "❌ Cannot reach GitHub API (check network/VPN)"
  exit 1
fi

# Git configuration check
if ! git config user.name >/dev/null || ! git config user.email >/dev/null; then
  echo "⚠️  Git not configured, setting defaults"
  git config user.name "OmniTrader Bot"
  git config user.email "bot@omnitrader.local"
fi
```

---

## Step 1 — Initialize & Read State

```bash
# Ensure tasks/ directory and files exist
mkdir -p tasks/

if [ ! -f tasks/TASKS.md ]; then
  echo "⚠️  Creating tasks/TASKS.md"
  cat > tasks/TASKS.md << 'EOF'
# TASKS

Priority engineering work — do these immediately.

---

EOF
fi

if [ ! -f tasks/TODO.md ]; then
  echo "⚠️  Creating tasks/TODO.md"
  cat > tasks/TODO.md << 'EOF'
# TODO

Next sprint items — confirmed but not urgent.

---

EOF
fi

if [ ! -f tasks/BACKLOG.md ]; then
  echo "⚠️  Creating tasks/BACKLOG.md"
  cat > tasks/BACKLOG.md << 'EOF'
# BACKLOG

Long-term work — needs research or low priority.

---

EOF
fi

# Read current state
TASKS_COUNT=$(grep -c "\- \[ \]" tasks/TASKS.md 2>/dev/null || echo "0")
TODO_COUNT=$(grep -c "\- \[ \]" tasks/TODO.md 2>/dev/null || echo "0")
BACKLOG_COUNT=$(grep -c "\- \[ \]" tasks/BACKLOG.md 2>/dev/null || echo "0")
echo "Current state: TASKS=$TASKS_COUNT | TODO=$TODO_COUNT | BACKLOG=$BACKLOG_COUNT"
```

---

## Step 2 — Check Issue Volume and Select Mode

```bash
# Check issue volume
ISSUE_COUNT=$(gh issue list --limit 1000 --json number --state open | jq 'length' 2>/dev/null || echo "0")

if [ "$ISSUE_COUNT" -eq 0 ]; then
  TRIAGE_MODE="local"
  echo "✅ No open issues found — switching to local planning-file triage"
else
  TRIAGE_MODE="issues"
fi

if [ "$ISSUE_COUNT" -gt 200 ]; then
  echo "⚠️  High issue volume ($ISSUE_COUNT issues), this may take several minutes..."
else
  echo "Processing $ISSUE_COUNT open issues..."
fi

echo "Triage mode: $TRIAGE_MODE"
```

---

## Step 3 — Triage

### Step 3A — GitHub Issue Triage (when issues exist)

```bash
if [ "$TRIAGE_MODE" = "issues" ]; then
  make po-triage ARGS="--output-dir .agent/tmp/"
  TRIAGE_EXIT=$?

  if [ $TRIAGE_EXIT -ne 0 ]; then
    echo "❌ Triage script failed with exit code $TRIAGE_EXIT"
    exit $TRIAGE_EXIT
  fi

  # Validate output JSON
  if [ ! -f .agent/tmp/triage-matrix.json ]; then
    echo "❌ Triage script did not produce triage-matrix.json"
    exit 1
  fi

  if ! jq empty .agent/tmp/triage-matrix.json 2>/dev/null; then
    echo "❌ Triage matrix is invalid JSON"
    cat .agent/tmp/triage-matrix.json
    exit 1
  fi

  # Check if any issues were triaged
  TRIAGED_COUNT=$(jq 'length' .agent/tmp/triage-matrix.json 2>/dev/null || echo "0")
  if [ "$TRIAGED_COUNT" -eq 0 ]; then
    echo "✅ No issue-driven planning changes"
  else
    echo "✅ Triaged $TRIAGED_COUNT issues"
  fi
fi
```

### Step 3B — Local Planning-File Fallback (when no issues exist)

When `TRIAGE_MODE=local`, continue by triaging local planning files instead of exiting.

Required actions:
- Read `tasks/TASKS.md`, `tasks/TODO.md`, and `tasks/BACKLOG.md`.
- Re-prioritize current work based on latest repo state (recent merges, active regressions, unfinished integrations).
- Promote 1-3 concrete implementation items into `tasks/TASKS.md` (priority now).
- Keep next-sprint items in `tasks/TODO.md`.
- Keep research/deferred items in `tasks/BACKLOG.md`.
- Add a dated section header: `Local Triage (No Open GitHub Issues) - YYYY-MM-DD`.
- Ensure edits are additive and traceable (do not delete historical audit sections).

```bash
if [ "$TRIAGE_MODE" = "local" ]; then
  echo "Running local tasks triage fallback (TASKS/TODO/BACKLOG)"
  # This step is intentionally human/agent-driven file triage.
  # After edits, continue to Step 5 commit.
fi
```

---

## Step 4 — Post Issue Comments

```bash
if [ "$TRIAGE_MODE" = "issues" ]; then
  make po-post ARGS="--matrix .agent/tmp/triage-matrix.json"
  POST_EXIT=$?

  if [ $POST_EXIT -ne 0 ]; then
    echo "❌ Post comments failed with exit code $POST_EXIT"
    exit $POST_EXIT
  fi
  echo "✅ Posted triage comments to GitHub"
else
  echo "ℹ️  Skipping GitHub comments (local fallback mode)"
fi
```

---

## Step 5 — Commit

```bash
# Check for merge conflicts
if git diff --cached tasks/*.md 2>/dev/null | grep -q "^+<<<<<<<"; then
  echo "❌ Merge conflict detected in planning files"
  git reset HEAD tasks/ 2>/dev/null || true
  exit 1
fi

# Stage changes
git add tasks/TASKS.md tasks/TODO.md tasks/BACKLOG.md

# Safety: ensure only planning files are staged for this workflow commit
EXTRA_STAGED=$(git diff --cached --name-only | grep -vE '^tasks/(TASKS|TODO|BACKLOG)\.md$' || true)
if [ -n "$EXTRA_STAGED" ]; then
  echo "❌ Refusing commit: unrelated staged files detected"
  echo "$EXTRA_STAGED"
  echo "Run: git restore --staged <files> (or commit them separately), then rerun triage"
  exit 1
fi

# Check if there are changes to commit
if git diff --cached --quiet; then
  echo "✅ No changes to commit (planning files unchanged)"
else
  # Commit with timestamp to avoid collisions
  TIMESTAMP=$(date +%Y-%m-%d-%H%M)
  git commit -m "chore(po): triage $TIMESTAMP" 2>/dev/null || {
    echo "⚠️  Commit failed, but changes are staged"
    exit 1
  }
  echo "✅ Committed triage results: $TIMESTAMP"
fi
```

---

## Step 6 — Cleanup & Summary

```bash
make clean-tmp

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Triage Complete"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Re-read final state
TASKS_COUNT=$(grep -c "\- \[ \]" tasks/TASKS.md 2>/dev/null || echo "0")
TODO_COUNT=$(grep -c "\- \[ \]" tasks/TODO.md 2>/dev/null || echo "0")
BACKLOG_COUNT=$(grep -c "\- \[ \]" tasks/BACKLOG.md 2>/dev/null || echo "0")

echo "Final state:"
echo "  tasks/TASKS.md    — $TASKS_COUNT priority items"
echo "  tasks/TODO.md     — $TODO_COUNT next-sprint items"
echo "  tasks/BACKLOG.md  — $BACKLOG_COUNT deferred items"
echo ""

if [ "$TASKS_COUNT" -gt 0 ]; then
  echo "Next action: /start-workflow"
else
  echo "Next action: /handle-po-review (no priority tasks after fallback triage)"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
```
