# .agent/

Autonomous engineering pipeline for AI-assisted development. Issues in, shipped releases out.

> **Product context**: See [`ROADMAP.md`](../ROADMAP.md) for the full product roadmap — strategy portfolio, risk framework, architecture, KPIs, and prioritization.

## Quick Start

```bash
# 1. Configure your project's toolchain
vi .agent/make/stack.make

# 2. Verify setup
make help

# 3. Run full pipeline
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

## Structure

```
.agent/
├── tmp/                 ← Unified temporary cache
├── make/
│   ├── stack.make       ← YOUR project commands (test, lint, build)
│   ├── agents.make      ← Orchestration scripts
│   ├── gh.make          ← GitHub CLI targets
│   └── jules.make       ← Jules CLI targets
│
├── skills/              ← Execution logic (scoring, review, release, etc.)
├── workflows/           ← Pipeline steps (thin dispatchers → skills)
├── rules/               ← Governance (architecture, security, testing)
├── logs/FRICTION.md     ← Friction log (O11y black box)
└── AGENTS.md            ← Full pipeline reference
```

## Three Mandates

1. **Strict Makefile Commands** — All test/lint/build go through `make` targets in `stack.make`. Never guess package managers.
2. **Sequential-Thinking MCP** — Every multi-step task uses structured reasoning. Think → Plan → Act → Verify.
3. **Docker-First** — All builds and tests run inside containers when available.

## Setup

1. Copy `.agent/` into your project root
2. Edit `make/stack.make` with your exact commands
3. Add entries from `_gitignore-additions.txt` to `.gitignore`
4. Run `gh auth status` to confirm GitHub CLI
5. Run `make help` to verify
