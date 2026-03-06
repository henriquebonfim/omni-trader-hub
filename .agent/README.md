# .agent/

Autonomous engineering pipeline with enforcement gates and observability. Issues in, shipped releases out.

> **Product context**: See [`ROADMAP.md`](../tasks/ROADMAP.md) for the full product roadmap — strategy portfolio, risk framework, architecture, KPIs, and prioritization.

## Quick Start

```bash
# 1. Configure your project's toolchain
vi .agent/scripts/make/stack.make

# 2. Verify setup
make help

# 3. Run full pipeline (enforces SOPs automatically)
/start-workflow
```

## How It Works

```
Issues → Triage → Score → Branch → Implement → PR → Review → Merge → Release → O11y
```

| Command | What it does |
|---------|-------------|
| `/start-workflow` | Full sprint cycle — triage to release |
| `/handle-issues` | Process open GitHub issues |
| `/handle-code <task>` | Implement a scoped task |
| `/handle-pr-review <N>` | Read-only PR review |
| `/handle-pr-code <N>` | Fix PR review comments |
| `/handle-close-pr <N>` | Merge + cleanup |
| `/handle-release` | Tag, CHANGELOG, GitHub release |
| `/handle-po-review` | Full PO review: Docker + tests + visual + triage |
| `/handle-backlog-triage` | Quick issue triage (no Docker/tests) |

## Structure

```
.agent/
├── scripts/
│   ├── orchestrator.py     ← SOP enforcement gate (branch safety, docker, make)
│   ├── friction_logger.py  ← Automated friction event recorder
│   ├── jules_poll.py       ← Async polling engine
│   └── make/
│       ├── stack.make      ← YOUR project commands (test, lint, build)
│       ├── agents.make     ← Orchestration scripts
│       ├── gh.make         ← GitHub CLI targets
│       └── jules.make      ← Jules CLI targets
│
├── workflows/           ← 9 hardened pipelines with SOP gates + traps
├── skills/              ← 8 specialized agents (issue, PR, release, etc.)
├── rules/               ← 6 governance documents (architecture, security, testing)
├── docs/                ← Reference documentation (MCP, CLI tools)
├── tmp/                 ← Unified temporary cache (auto-cleaned)
└── logs/FRICTION.md     ← Friction log (O11y black box)
```

## Enforcement & Mandates

### Automatic SOP Gates
Every workflow runs `orchestrator.py` to enforce:
- **Branch Protection**: Blocks code changes on main/master/production/staging
- **Docker Availability**: Validates `docker compose` for containerized execution
- **Make Targets**: Confirms build/test/lint/typecheck exist in stack.make
- **Release Branch**: Ensures releases only run from main/master

### Automated Observability
Every workflow has trap-based cleanup:
- **Friction Logging**: Auto-logs failures with exit code, workflow name, and timestamp
- **Temp Cleanup**: Always runs `make clean-tmp` on exit (success or failure)
- **Fail-Safe**: Logging and cleanup never block workflow execution

### Developer Mandates
1. **Strict Makefile Commands** — All test/lint/build go through `make` targets in `stack.make`. Never guess package managers.
2. **Sequential-Thinking MCP** — Every multi-step task uses structured reasoning. Think → Plan → Act → Verify.
3. **Docker-First** — All builds and tests run inside containers when available.

## Setup

1. Copy `.agent/` into your project root
2. Edit `.agent/scripts/make/stack.make` with your exact commands
3. Add entries from `_gitignore-additions.txt` to `.gitignore`
4. Run `gh auth status` to confirm GitHub CLI
5. Run `make help` to verify
