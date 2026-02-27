---
name: software-engineer-orchestrator
description: Full engineering task orchestrator — receives a task, validates scope, auto-detects stack, implements with discipline, validates build/tests/lint, updates CHANGELOG, and commits clean. Use for ANY code task: "implement X", "fix bug Y", "add tests for Z", "refactor module W", "add a field", "fix this error", or any request that results in committed code. Wraps software-engineer-worker with pre-flight branch safety, stack detection, and structured completion reporting. Also triggers for Jules-assigned tasks, batch issue implementations, and PR review followups that require code changes.
---

# Software Engineer Orchestrator

Receives a scoped task, validates the environment, executes via `software-engineer-worker`, and delivers a clean validated commit. The enforcement layer that ensures every code change follows standards regardless of where the task came from.

---

## Setup Check

```bash
mkdir -p .agent/skills/software-engineer-orchestrator/tmp
grep -qxF '.agent/skills/software-engineer-orchestrator/tmp/' .gitignore \
  || echo '.agent/skills/software-engineer-orchestrator/tmp/' >> .gitignore
```

---

## Phase 0 — Branch Safety

```bash
BRANCH=$(git branch --show-current)
echo "Current branch: $BRANCH"

PROTECTED=("main" "master" "production" "staging")
for p in "${PROTECTED[@]}"; do
  if [[ "$BRANCH" == "$p" ]]; then
    echo "ERROR: Cannot commit directly to protected branch '$p'."
    echo "Create a feature branch first:"
    echo "  git checkout -b feature/<task-slug>"
    exit 1
  fi
done

echo "✅ Branch safe: $BRANCH"
```

If called from `/handle-issues` batch flow, the branch is already created. If called directly, confirm with user before creating a branch.

---

## Phase 1 — Stack Auto-Detection

Detect and store the project's toolchain before touching any code:

```bash
# Runtime & package manager
[ -f package.json ]   && PM="npm"  && RUNTIME="node"
[ -f pnpm-lock.yaml ] && PM="pnpm"
[ -f yarn.lock ]      && PM="yarn"
[ -f pyproject.toml ] && RUNTIME="python"
[ -f Cargo.toml ]     && RUNTIME="rust"
[ -f go.mod ]         && RUNTIME="go"

# Test framework
[ -f jest.config.js ]    || [ -f jest.config.ts ]   && TEST_CMD="npx jest"
[ -f vitest.config.ts ]  || [ -f vitest.config.js ]  && TEST_CMD="npx vitest run"
[ -f pytest.ini ]        || grep -q "pytest" pyproject.toml 2>/dev/null && TEST_CMD="pytest"
[ -f Cargo.toml ]        && TEST_CMD="cargo test"
[ -f go.mod ]            && TEST_CMD="go test ./..."

# Linter
[ -f .eslintrc* ]    || [ -f eslint.config* ] && LINT_CMD="npx eslint ."
[ -f biome.json ]                              && LINT_CMD="npx biome check ."
grep -q "ruff" pyproject.toml 2>/dev/null     && LINT_CMD="ruff check ."

# Type checker
[ -f tsconfig.json ]                            && TYPE_CMD="npx tsc --noEmit"
grep -q "mypy"   pyproject.toml 2>/dev/null    && TYPE_CMD="mypy ."
grep -q "pyright" pyproject.toml 2>/dev/null   && TYPE_CMD="pyright"

# Build command
[ -f package.json ] && grep -q '"build"' package.json && BUILD_CMD="npm run build"
[ -f Cargo.toml ]   && BUILD_CMD="cargo build"
[ -f go.mod ]       && BUILD_CMD="go build ./..."

echo "Runtime:  ${RUNTIME:-unknown}"
echo "Test:     ${TEST_CMD:-not detected}"
echo "Lint:     ${LINT_CMD:-not detected}"
echo "Typecheck:${TYPE_CMD:-not detected}"
echo "Build:    ${BUILD_CMD:-not detected}"
```

Store as `tmp/stack-context.json`:

```json
{
  "runtime": "node|python|rust|go",
  "package_manager": "npm|pnpm|yarn|pip|cargo",
  "test_cmd": "...",
  "lint_cmd": "...",
  "typecheck_cmd": "...",
  "build_cmd": "..."
}
```

---

## Phase 2 — Baseline Validation

Run the full validation suite BEFORE any changes. This establishes what was already broken (not your fault) vs. what you introduced:

```bash
# Record baseline state
echo "Running baseline validation..."

BUILD_BEFORE="PASS"
TEST_BEFORE="PASS"
LINT_BEFORE="PASS"

$BUILD_CMD 2>&1 || BUILD_BEFORE="FAIL"
$TEST_CMD  2>&1 || TEST_BEFORE="FAIL"
$LINT_CMD  2>&1 || LINT_BEFORE="FAIL"
```

Store in `tmp/baseline.json`:

```json
{
  "build": "PASS|FAIL",
  "tests": "PASS|FAIL",
  "lint":  "PASS|FAIL|N/A"
}
```

If baseline tests are failing — **do not hide pre-existing failures**. Note them in the completion report but do not fix them unless the task explicitly asks for it.

---

## Phase 3 — Load Skill & Execute

```
software-engineer-worker
```

Run all 8 phases from the skill:

| Phase | Action |
|-------|--------|
| 1 — Thinking Protocol | Restate, trace call graph, classify, assess risk |
| 2 — Discovery | Read source, trace dependencies, check git log |
| 3 — Design | Plan: files, signatures, test strategy, compat |
| 4 — Veto Checkpoint | Architecture, abstraction, scope, security |
| 5 — Implementation | Strict types, small functions, no duplication |
| 6 — Documentation | CHANGELOG.md always; README/docstrings if applicable |
| 7 — Self-Correction | lint → typecheck → tests → build; classify + heal failures |
| 8 — Final Validation | `git diff --stat`, `git status` |

---

## Phase 4 — Post-Implementation Validation

After the skill completes, run the full suite one final time from the orchestrator level:

```bash
echo "Running post-implementation validation..."

$LINT_CMD     && echo "✅ Lint" || echo "❌ Lint FAIL"
$TYPE_CMD     && echo "✅ Typecheck" || echo "❌ Typecheck FAIL"
$TEST_CMD     && echo "✅ Tests" || echo "❌ Tests FAIL"
$BUILD_CMD    && echo "✅ Build" || echo "❌ Build FAIL"
```

Compare against baseline. Any NEW failures introduced by this change are blocking — fix before proceeding.

---

## Phase 5 — Diff Review

```bash
# Confirm the diff is scoped to the task
git diff --stat HEAD

# Confirm no unrelated files changed
git status

# Confirm no temp files staged
git ls-files --others --exclude-standard | head -10
```

**Blockers:**
- Unrelated files in diff → unstage them
- Temp files staged → remove from staging
- Empty diff → nothing was committed, report failure

---

## Phase 6 — Commit Audit

```bash
git log --oneline -5
```

Every commit in this change must follow the convention:

```
<type>(<module>): <imperative description>

<body if non-obvious>

Refs: #<issue> | <pr-comment-url>
```

Valid types: `feat` `fix` `refactor` `perf` `test` `docs` `chore`

If commits are missing the `Refs:` line and the task has an issue/PR comment reference, amend:

```bash
git commit --amend --no-edit
```

---

## Phase 7 — Cleanup

```bash
rm -f .agent/skills/software-engineer-orchestrator/tmp/*.json
git status  # Must show clean
```

---

## Completion Report

```
✅ Task complete

Branch:        <branch-name>
Type:          feat|fix|refactor|...
Files changed: N
Tests:         N added/updated
CHANGELOG:     Updated under [Unreleased]
Baseline delta: build PASS→PASS | tests PASS→PASS | lint PASS→PASS

Commits:
  <sha>  <type(module): description>
```

---

## Abort Conditions

| Condition | Action |
|-----------|--------|
| On protected branch | ABORT — create feature branch first |
| Requirements ambiguous after reading source | PAUSE — ask user for clarification |
| Architectural redesign required beyond scope | BLOCK — report, create issue, do not implement |
| 3+ self-healing iterations on same failure | BLOCK — report exact error + context to user |
| Test suite introduces regressions after 3 fix attempts | BLOCK — do not skip/comment tests to hide failures |
