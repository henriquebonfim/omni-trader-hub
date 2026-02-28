# Agent Pipeline

Automated engineering pipeline. Issues in, shipped releases out.

---

## Quick Start

```
/start-workflow
```

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
├── logs/
│   └── FRICTION.md          ← Global Friction Log (O11y)
│
├── make/
│   ├── stack.make           ← Project toolchain (test, lint, build)
│   ├── agents.make          ← Orchestration scripts
│   ├── gh.make              ← GitHub CLI targets
│   └── jules.make           ← Jules CLI targets
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
├── workflows/
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
└── rules/
    ├── software-engineering-standards.md
    ├── issue-task-standards.md
    ├── po-standards.md
    ├── pr-code-standards.md
    ├── pr-review-standards.md
    └── release-standards.md
```

---

## Key Mandates

1. **Strict Makefile Commands**: All test/lint/build/typecheck commands go through `make` targets defined in `stack.make`. Never guess package managers.
2. **Sequential-Thinking MCP**: Mandatory for all multi-step tasks. Think → Plan → Act → Verify.
3. **Docker-First Execution**: All tests and builds run inside containers when available.
4. **Jules Discipline**: Always `jules remote pull --apply`. Always branch first. Always verify in Docker.
5. **Friction Logging**: Every technical hurdle recorded in `.agent/logs/FRICTION.md`.

---

## Jules Discipline

1. **Branch First**: `git checkout -b feature/...` before pulling
2. **Pull with Apply**: `make j-pull ID=<id>` (uses `--apply`)
3. **Docker Verify**: `make test && make lint` after pull
4. **Self-Correct**: If Jules breaks patterns, fix before committing

---

## Setup

1. Copy `.agent/` into project root
2. Edit `.agent/make/stack.make` with your project's exact commands
3. Add lines from `_gitignore-additions.txt` to `.gitignore`
4. Ensure `gh auth status` passes
5. Run `/start-workflow`

---

## Troubleshooting

- **"ABORT: protected branch"** → `git checkout -b feature/<name>`
- **Wrong test command** → Edit `.agent/make/stack.make`
- **Jules not completing** → `make j-list` then `/handle-pr-review <N>`
