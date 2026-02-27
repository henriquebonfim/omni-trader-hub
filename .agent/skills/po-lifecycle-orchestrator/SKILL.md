---
name: po-lifecycle-orchestrator
description: Complete Product Owner lifecycle orchestrator. Aggregates GitHub issues, TASKS.md, TODO.md, BACKLOG.md, runs Docker + test suite, visually reviews the product via Antigravity integrated browser or Playwright screenshots, then triages every item into the correct planning file: BACKLOG.md (long-term), TODO.md (next sprint), TASKS.md (immediate priority). Use for "PO review", "triage the backlog", "product review", "what should we work on next", "update the backlog", "run the full product review", "review product health", or any request to organize and prioritize work. Also triggers at the start of any sprint or planning session.
---

# PO Lifecycle Orchestrator

Complete Product Owner intelligence loop. Sees the full picture — GitHub issues, planning docs, running product, test health — then produces three clean, prioritized planning files that feed directly into the engineering pipeline.

---

## Setup Check

```bash
gh --version
git --version
docker --version || echo "Docker not available — skipping container checks"
python3 --version

mkdir -p .agent/skills/po-lifecycle-orchestrator/tmp
grep -qxF '.agent/skills/po-lifecycle-orchestrator/tmp/' .gitignore \
  || echo '.agent/skills/po-lifecycle-orchestrator/tmp/' >> .gitignore
```

---

## Phase 0 — Project Context Scan

Read everything before deciding anything:

```bash
# Product context
[ -f README.md ]    && cat README.md | head -100
[ -f PRODUCT.md ]   && cat PRODUCT.md
[ -f ROADMAP.md ]   && cat ROADMAP.md

# Existing planning files — read current state first
[ -f TASKS.md ]     && cat TASKS.md
[ -f TODO.md ]      && cat TODO.md
[ -f BACKLOG.md ]   && cat BACKLOG.md

# Package.json / pyproject for product name + version
[ -f package.json ]    && cat package.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"Product: {d.get('name')} v{d.get('version')}\")"
[ -f pyproject.toml ]  && grep -E "^(name|version)" pyproject.toml | head -2

# Current milestone/sprint context
make gh-api ENDPOINT="repos/{owner}/{repo}/milestones" ARGS="--jq '.[] | \"\\(.title): \\(.open_issues) open, due \\(.due_on // \"no date\")\"'"
```

Store project summary in `tmp/project-context.json`:

```json
{
  "product_name": "...",
  "current_version": "...",
  "active_milestone": "...",
  "has_tasks_md": true,
  "has_todo_md": true,
  "has_backlog_md": true
}
```

---

## Phase 1 — Aggregate All Issue Sources

Gather every item that might become work:

```bash
# All open GitHub issues (full metadata)
make gh-issue-list ARGS="--state open --limit 100 --json number,title,labels,updatedAt,assignees,milestone,createdAt,comments" \
  > .agent/skills/po-lifecycle-orchestrator/tmp/gh-issues-open.json

# Recently closed (last 30 days — detect already-done items)
make gh-issue-list ARGS="--state closed --limit 50 --json number,title,labels,closedAt" \
  > .agent/skills/po-lifecycle-orchestrator/tmp/gh-issues-closed.json

# Open PRs (in-progress work — don't re-assign)
make gh-pr-list ARGS="--state open --json number,title,headRefName,author,isDraft,reviewDecision" \
  > .agent/skills/po-lifecycle-orchestrator/tmp/open-prs.json

# Merged PRs (velocity reference)
make gh-pr-list ARGS="--state merged --limit 20 --json number,title,mergedAt" \
  > .agent/skills/po-lifecycle-orchestrator/tmp/merged-prs.json

echo "Issues collected: $(cat .agent/skills/po-lifecycle-orchestrator/tmp/gh-issues-open.json | python3 -c 'import sys,json; print(len(json.load(sys.stdin)))')"
```

---

## Phase 2 — System Health Check

### 2a — Docker

```bash
# Detect docker-compose or compose.yml
COMPOSE_FILE=""
[ -f docker-compose.yml ]      && COMPOSE_FILE="docker-compose.yml"
[ -f docker-compose.yaml ]     && COMPOSE_FILE="docker-compose.yaml"
[ -f compose.yml ]             && COMPOSE_FILE="compose.yml"
[ -f compose.yaml ]            && COMPOSE_FILE="compose.yaml"

if [ -n "$COMPOSE_FILE" ]; then
  echo "Found: $COMPOSE_FILE"

  # Attempt to build (don't start — just validate)
  make docker-build COMPOSE_FILE="$COMPOSE_FILE" 2>&1 | tail -20
  BUILD_STATUS=$?

  # Check if services are already running
  docker compose -f "$COMPOSE_FILE" ps 2>/dev/null

  echo "Docker build exit code: $BUILD_STATUS"
else
  # Try plain Dockerfile
  [ -f Dockerfile ] && make docker-build 2>&1 | tail -20
fi
```

Store in `tmp/docker-health.json`:
```json
{
  "compose_file": "docker-compose.yml",
  "build_status": "PASS|FAIL|SKIPPED",
  "services_running": [],
  "build_errors": []
}
```

### 2b — Test Suite

Auto-detect and run:

```bash
# Detect test command (same logic as software-engineer-orchestrator)
TEST_CMD=""
[ -f jest.config.js ]    || [ -f jest.config.ts ]   && TEST_CMD="npx jest --passWithNoTests 2>&1"
[ -f vitest.config.ts ]                              && TEST_CMD="npx vitest run 2>&1"
[ -f pytest.ini ]        || [ -f pyproject.toml ] && grep -q pytest pyproject.toml && TEST_CMD="pytest -q 2>&1"
[ -f Cargo.toml ]                                    && TEST_CMD="cargo test 2>&1"
[ -f go.mod ]                                        && TEST_CMD="go test ./... 2>&1"

# Also check package.json scripts
[ -f package.json ] && grep -q '"test"' package.json && TEST_CMD="bun test 2>&1 || npm test 2>&1 || make test ARGS=\"2>&1\""

if [ -n "$TEST_CMD" ]; then
  echo "Running: $TEST_CMD"
  eval "$TEST_CMD" | tail -30
  TEST_EXIT=$?
  echo "Exit: $TEST_EXIT"
else
  echo "No test command detected"
  TEST_EXIT=-1
fi
```

Store in `tmp/test-health.json`:
```json
{
  "test_cmd": "...",
  "exit_code": 0,
  "status": "PASS|FAIL|SKIPPED",
  "summary": "42 passed, 0 failed",
  "failing_tests": []
}
```

---

## Phase 3 — Product Visual Review

Navigate the running product to see what the user actually experiences. Use whichever is available:

### 3a — Antigravity Integrated Browser (preferred)

If Antigravity browser tool is available in the session:

```
1. Navigate to http://localhost:<PORT> (detect from docker-compose ports or package.json scripts)
2. Take a screenshot of the home/landing page
3. Navigate to each main route (from README, sitemap, or detected router config)
4. Take screenshot per route
5. Look for: broken layouts, error states, 404s, console errors, missing assets
```

Extract app URL:
```bash
# From docker-compose ports
grep -A2 "ports:" "$COMPOSE_FILE" | grep -oE '[0-9]+:[0-9]+' | head -1

# From package.json dev server
cat package.json | python3 -c "
import sys, json, re
d = json.load(sys.stdin)
scripts = d.get('scripts', {})
for k,v in scripts.items():
    m = re.search(r'--port\s+(\d+)|:(\d+)', v)
    if m:
        print(f'Port found in scripts.{k}: {m.group(1) or m.group(2)}')
        break
" 2>/dev/null

# From .env files
grep -E "PORT=|VITE_PORT=|NEXT_PUBLIC_PORT=" .env .env.local .env.development 2>/dev/null | head -3
```

For each screenshot taken, record findings in `tmp/visual-review.json`:
```json
[
  {
    "route": "/",
    "screenshot_path": "tmp/screenshots/home.png",
    "status": "OK|BROKEN|MISSING",
    "issues_found": ["broken nav link", "console error: ..."]
  }
]
```

### 3b — Playwright (fallback / CI mode)

```bash
# Install playwright if needed
make install-playwright

# Run the review script
make po-playwright ARGS="--url \"http://localhost:${APP_PORT:-3000}\" --routes \"$(cat .agent/skills/po-lifecycle-orchestrator/tmp/routes.json 2>/dev/null || echo '[]')\" --output-dir .agent/skills/po-lifecycle-orchestrator/tmp/screenshots/"
```

### 3c — Static Analysis Fallback

If no running server is available:

```bash
# Extract routes from router config files
find . -name "*.router.*" -o -name "routes.ts" -o -name "routes.js" \
   -o -name "app.tsx" -o -name "App.tsx" 2>/dev/null | head -5 | xargs grep -h "path:" 2>/dev/null

# Count pages/views
find ./src -name "page.*" -o -name "Page.*" -o -name "*.view.*" -o -name "*View.*" 2>/dev/null | wc -l

# Look for error boundaries, loading states
grep -r "ErrorBoundary\|Suspense\|loading\|skeleton" src/ --include="*.tsx" --include="*.jsx" -l 2>/dev/null | wc -l
```

Store findings even without screenshots — note `"browser_available": false` in visual review.

---

## Phase 4 — Triage Engine

Run the full aggregation and triage script:

```bash
make po-triage ARGS="--issues .agent/skills/po-lifecycle-orchestrator/tmp/gh-issues-open.json \
  --closed .agent/skills/po-lifecycle-orchestrator/tmp/gh-issues-closed.json \
  --prs .agent/skills/po-lifecycle-orchestrator/tmp/open-prs.json \
  --merged .agent/skills/po-lifecycle-orchestrator/tmp/merged-prs.json \
  --docker .agent/skills/po-lifecycle-orchestrator/tmp/docker-health.json \
  --tests .agent/skills/po-lifecycle-orchestrator/tmp/test-health.json \
  --visual .agent/skills/po-lifecycle-orchestrator/tmp/visual-review.json \
  --context .agent/skills/po-lifecycle-orchestrator/tmp/project-context.json \
  --output-dir .agent/skills/po-lifecycle-orchestrator/tmp/"
```

### Triage Decision Rules

Every item (GitHub issue, visual finding, test failure, Docker issue) gets placed into exactly one bucket:

#### → TASKS.md (Priority — do now)
Criteria (any one):
- Security vulnerability, auth bypass, data loss risk
- Test failing in CI (blocking merges)
- Docker build broken (blocking local dev)
- Visual review shows critical broken route or error state
- Bug affecting core user flow (login, checkout, main feature)
- Issue with `priority: critical` or `priority: high` label
- Issue blocking another confirmed task
- Issue assigned to current active milestone AND unstarted

#### → TODO.md (Next — do this sprint)
Criteria (any one):
- Bug that degrades UX but doesn't block critical path
- Feature with clear acceptance criteria and confirmed scope
- Test coverage gap on existing functionality
- Visual review shows non-critical UI issue (misalignment, missing state)
- Issue with `priority: medium` label
- Issue confirmed by engineering validation (from issue-task-orchestrator)
- Refactor needed to unblock upcoming feature

#### → BACKLOG.md (Long-term — plan for later)
Criteria (any one):
- Feature request needing design/spec first
- `enhancement`, `idea`, `question`, `discussion` labels
- Dependent on other TODO/TASKS items not yet started
- Low user impact (cosmetic, edge case, developer experience)
- Needs external decision (legal, design, marketing sign-off)
- Duplicate of an existing item (mark and close)
- Issue open > 30 days with no activity

#### Skip entirely
- Already fixed by recent merged PR (cross-reference merged-prs.json)
- In-flight as open PR (in open-prs.json)
- `wontfix` or `invalid` label

---

## Phase 5 — Write Planning Files

### 5a — TASKS.md (Priority — do now)

```markdown
# Tasks

Priority work for the current sprint. Items here should be picked up immediately by the engineering pipeline.

> Last updated: YYYY-MM-DD by PO Lifecycle Orchestrator
> System health: Build [PASS|FAIL] · Tests [PASS|FAIL] · Docker [PASS|FAIL]

---

## 🔴 Critical

- [ ] **[BUG] #42 — Null pointer in payment flow** `bug` `critical`
  - Scope: `src/payment/checkout.ts` line 87
  - Impact: Users cannot complete checkout
  - Acceptance: Null guard added + regression test
  - → Assign: `/handle-code "fix null pointer in checkout.ts#87 Refs: #42"`

## 🟠 High Priority

- [ ] **[FEAT] #38 — Add OAuth2 login** `feature` `high`
  - Scope: `src/auth/` — new provider flow
  - Acceptance: Login via Google works, session persists, existing auth unaffected
  - → Assign: `/handle-issues` or Jules

## 🟡 Fix Required (CI/Docker)

- [ ] **[TEST] Fix failing test: AuthService.logout**
  - Failing since: commit abc1234
  - → `/handle-code "fix failing test in auth.test.ts"`
```

### 5b — TODO.md (Next sprint)

```markdown
# TODO

Work confirmed for the next sprint. Items are validated, scoped, and ready to assign once TASKS are cleared.

> Last updated: YYYY-MM-DD by PO Lifecycle Orchestrator

---

## Features

- [ ] **#45 — Add dark mode toggle** `feature` `medium`
  - Design: figma.com/... (if linked)
  - Scope: CSS variables + localStorage preference
  - Estimated: S (1-3 days)

## Bugs

- [ ] **#41 — Mobile nav overflow on Safari** `bug` `medium`
  - Reproduces: iPhone 14 Safari 17
  - Scope: `src/components/Nav.tsx`

## Refactors

- [ ] **#39 — Extract retry logic from 3 call sites** `refactor`
  - Precondition: #38 merged first
```

### 5c — BACKLOG.md (Long-term)

```markdown
# Backlog

Items requiring further design, external decisions, or lower priority. Reviewed each sprint — items graduate to TODO when ready.

> Last updated: YYYY-MM-DD by PO Lifecycle Orchestrator

---

## Ideas / Enhancements

- [ ] **#55 — AI-powered search** `enhancement` `idea`
  - Status: Needs product spec
  - Blocker: Design sign-off
  - Revisit: Q3

## Technical Debt

- [ ] **#48 — Migrate from class components to hooks** `refactor` `tech-debt`
  - Scope: 12 legacy components
  - Estimated: L (1-2 weeks)
  - Precondition: No active feature work on affected components

## Needs Info / Discussion

- [ ] **#51 — Multi-tenant support** `question` `discussion`
  - Status: Awaiting architecture decision
  - Owner: @<lead>

## Won't Fix (This Cycle)

- [ ] **#33 — IE11 support** `wontfix`
  - Reason: <0.1% traffic, EOL browser
```

---

## Phase 6 — Sync Back to GitHub

Post a summary comment on every processed issue:

```bash
make po-post ARGS="--matrix .agent/skills/po-lifecycle-orchestrator/tmp/triage-matrix.json"
```

Per-issue comment format:
```
**📋 PO Triage — [YYYY-MM-DD]**

**Bucket:** TASKS | TODO | BACKLOG
**Priority:** Critical | High | Medium | Low
**Reason:** <one sentence why this bucket>
**Target sprint:** <sprint or "Backlog">

> Triaged by PO Lifecycle Orchestrator
```

Also post a summary on the GitHub repo discussions or as a gist (if configured):
```bash
# Create sprint planning gist
gh gist create \
  TASKS.md TODO.md BACKLOG.md \
  --desc "Sprint planning — $(date +%Y-%m-%d)" \
  --public
```

---

## Phase 7 — Report

```
📋 PO LIFECYCLE COMPLETE — YYYY-MM-DD

Sources aggregated:
  GitHub issues:  N open, N recently closed
  Open PRs:       N (skipped — in-flight)
  Existing items: TASKS.md (N), TODO.md (N), BACKLOG.md (N)

System health:
  Docker:  PASS | FAIL | SKIPPED
  Tests:   N passing, N failing
  Visual:  N routes reviewed, N issues found

Triage results:
  🔴 TASKS.md    → N items (priority)
  🟡 TODO.md     → N items (next sprint)
  🔵 BACKLOG.md  → N items (long-term)
  ✅ Skipped      → N items (in-flight, fixed, or invalid)

Top priority item:
  #<N> — <title> → /handle-code or /start-workflow

Next step:
  Run /start-workflow to begin engineering on TASKS.md
```

---

## Phase 8 — Cleanup

```bash
rm -f .agent/skills/po-lifecycle-orchestrator/tmp/*.json
rm -f .agent/skills/po-lifecycle-orchestrator/tmp/screenshots/*.png
# Keep TASKS.md, TODO.md, BACKLOG.md — these are project artifacts, not tmp
```

---

## Triage Priority Override Rules

The PO can always override automated triage:

```bash
# Manually promote to TASKS
# Add label: triage:tasks

# Manually promote to TODO
# Add label: triage:todo

# Manually defer to BACKLOG
# Add label: triage:backlog

# Manually close as duplicate
# Run: gh issue close N --reason "not planned" --comment "Duplicate of #M"
```

---

## Integration with Engineering Pipeline

After planning files are updated, trigger the engineering pipeline:

| Planning file | Engineering command |
|---------------|---------------------|
| `TASKS.md` updated | `/start-workflow` → picks up top TASKS item |
| Specific issue | `/handle-issues` → processes confirmed issues |
| Single task | `/handle-code "<task description>"` |
| Visual bug confirmed | `/handle-code "fix: <specific UI issue>"` |
| Test failure confirmed | `/handle-code "fix: failing test <test name>"` |
