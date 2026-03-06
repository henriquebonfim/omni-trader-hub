# Agent Pipeline

Hardened automated engineering pipeline with enforcement gates. Issues in, shipped releases out.

---

## Quick Start

```bash
# All workflows now enforce SOPs automatically
/start-workflow
```

**New in Phase 1 Enforcement:**
- ✅ SOP validation gates on all 9 workflows
- ✅ Protected branch blocking (main/master/production/staging)
- ✅ Automated friction logging on failures
- ✅ Trap-based cleanup (always runs make clean-tmp)

---

## Pipeline

```
Issues → Triage → Score → Branch → Implement → PR → Review → Merge → Release → O11y
```

| Stage | Command |
|-------|---------|
| Context scan | `/start-workflow` |
| Issue triage | `/handle-issues` |
| Implementation | `/handle-code <task>` |
| PR review | `/handle-pr-review <N>` |
| PR fixes | `/handle-pr-code <N>` |
| Merge | `/handle-close-pr <N>` |
| Release | `/handle-release` |

---

## Directory Structure

```
.agent/
├── AGENTS.md
├── README.md
│
├── orchestrator.py          ← Enforcement gate (NEW)
│
├── logs/
│   └── FRICTION.md          ← Auto-populated friction log (O11y)
│
├── scripts/
│   ├── friction_logger.py   ← Automated logger (NEW)
│   └── jules_poll.py        ← Async polling engine
│
├── make/
│   ├── stack.make           ← Project toolchain (test, lint, build)
│   ├── agents.make          ← Orchestration scripts
│   ├── gh.make              ← GitHub CLI targets
│   └── jules.make           ← Jules CLI targets
│
├── workflows/               ← 9 hardened workflows (SOP gates + traps)
│   ├── start-workflow.md
│   ├── handle-issues.md
│   ├── handle-code.md
│   ├── handle-pr-review.md
│   ├── handle-pr-code.md
│   ├── handle-close-pr.md
│   ├── handle-po-review.md
│   ├── handle-backlog-triage.md
│   └── handle-release.md
│
├── skills/
│   ├── issue-task-orchestrator/
│   ├── po-lifecycle-orchestrator/
│   ├── pr-code-orchestrator/
│   ├── pr-review-orchestrator/
│   ├── release-manager-orchestrator/
│   ├── software-engineer-worker/
│   └── ui-ux-pro-max/
│
└── rules/
    ├── software-engineering-standards.md
    ├── issue-task-standards.md
    ├── po-standards.md
    ├── pr-code-standards.md
    ├── pr-review-standards.md
    └── release-standards.md
```

---

## Enforcement Architecture

### SOP Gates (orchestrator.py)
Every workflow validates before execution:

| Check | Severity | Enforces |
|-------|----------|----------|
| Protected Branch | CRITICAL | Blocks code changes on main/master/production/staging |
| Release Branch | CRITICAL | Ensures releases only from main/master |
| Docker Available | HIGH | Validates `docker compose` for containerization |
| Make Targets | HIGH | Confirms build/test/lint/typecheck exist |
| Gitignore Hygiene | HIGH | Verifies `.agent/tmp/` not committed |
| Sequential-Thinking | WARN | Reminds to use structured reasoning token |

### Observability Traps
Every workflow includes fail-safe cleanup:

```bash
cleanup_workflow() {
  EXIT_CODE=$?
  if [ $EXIT_CODE -ne 0 ]; then
    python3 .agent/scripts/friction_logger.py \
      --task "$WORKFLOW_NAME" \
      --type "Workflow" \
      --friction "Workflow exited with code $EXIT_CODE" \
      --resolution "Inspect output and rerun" || true
  fi
  make clean-tmp >/dev/null 2>&1 || true
}
trap cleanup_workflow EXIT
```

### Developer Mandates

1. **Strict Makefile Commands**: All test/lint/build/typecheck commands go through `make` targets defined in `stack.make`. Never guess package managers.
2. **Sequential-Thinking MCP**: Mandatory for all multi-step tasks. Think → Plan → Act → Verify.
3. **Docker-First Execution**: All tests and builds run inside containers when available.
4. **Jules Discipline**: Always `jules remote pull --apply`. Always branch first. Always verify in Docker.
5. **Friction Logging**: Automated on failures; manual additions encouraged for systemic issues.

---

## Jules Discipline

1. **Branch First**: `git checkout -b feature/...` before pulling
2. **Poll for Completion**: `make j-poll ID=<id>` (async wait for remote session)
3. **Pull with Apply**: `make j-pull ID=<id>` (uses `--apply`)
4. **Docker Verify**: `make test && make lint` after pull
5. **Self-Correct**: If Jules breaks patterns, fix before committing

---

## Setup

1. Copy `.agent/` into project root
2. Edit `.agent/make/stack.make` with your project's exact commands
3. Add lines from `_gitignore-additions.txt` to `.gitignore`
4. Ensure `gh auth status` passes
5. Run `/start-workflow`

---

## Troubleshooting

- **"❌ SOP validation failed"** → Check orchestrator output for specific failure
- **"ABORT: protected branch"** → `git checkout -b feature/<name>`
- **Wrong test command** → Edit `.agent/make/stack.make`
- **Jules not completing** → `make j-poll ID=<id>` or `make j-list`
- **Friction log growing** → Review `.agent/logs/FRICTION.md` for patterns

## Workflow Anatomy (Post-Enforcement)

Every workflow now follows this structure:

1. **SOP Validation Gate**: `python3 .agent/orchestrator.py <workflow-name>`
2. **Trap Installation**: Automatic cleanup + friction logging on exit
3. **Workflow Steps**: Original implementation logic
4. **Auto-Cleanup**: `make clean-tmp` always runs (trap-based)
5. **Friction Capture**: Failures logged to `.agent/logs/FRICTION.md`
