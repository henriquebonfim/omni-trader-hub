# Agent Pipeline

Automated engineering pipeline for Antigravity IDE. Issues in, shipped releases out.

---

## Quick Start

```
/start-workflow
```

That's it. The orchestrator handles everything from there.

---

## Pipeline Overview

```
Issues → Triage → Score → Branch → Implement → PR → Review → Merge → Release → O11y (Friction)
```

| Stage | Command | What happens |
|-------|---------|-------------|
| Context scan | `/start-workflow` | Reads TODO.md, README, open PRs, velocity |
| Issue triage | `/handle-issues` | Fetch, classify, score, reply, implement, PR |
| Implementation | `/handle-code <task>` | Auto-detect stack, implement, validate, CHANGELOG |
| PR review | `/handle-pr-review <N>` | Read-only analysis, runtime check, submit review |
| PR fixes | `/handle-pr-code <N>` | Implement review comments, reply per thread |
| Merge | `/handle-close-pr <N>` | Validate CI, merge, delete branch, clean sessions |
| Release | `/handle-release` | Classify commits, SemVer, CHANGELOG, tag, publish |

---

## Directory Structure

```
.agent/
├── AGENTS.md               ← You are here
├── _gitignore-additions.txt ← Add these 8 lines to your root .ignore
├── logs/                   ← System Observability (O11y)
│   └── FRICTION.md          ← Global Friction Log (Black Box Recorder)
│
├── make/                   ← Centralized Agent Makefiles
│   ├── agents.make          ← Orchestration scripts (scoring, triage, etc.)
│   ├── gh.make              ← GitHub CLI targets
│   └── jules.make           ← Jules CLI targets
│
├── skills/
│   ├── issue-task-orchestrator/
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   ├── score_issues.py          ← 4-axis priority scoring
│   │   │   └── post_issue_comments.py   ← Structured status replies
│   │   └── tmp/                         ← gitignored, auto-wiped
│   │
│   ├── pr-code-orchestrator/
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   └── post_comment_replies.py  ← Reply per comment thread
│   │   └── tmp/
│   │
│   ├── pr-review-orchestrator/
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   └── post_review.py           ← Batched GitHub review submission
│   │   └── tmp/
│   │
│   ├── release-manager-orchestrator/    ← Full automated release execution
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   ├── generate_release_notes.py ← Commit classifier + notes generator
│   │   │   ├── execute_release.py        ← Atomic bump+commit+tag+push+gh release
│   │   │   └── insert_changelog.py       ← CHANGELOG insertion utility
│   │   └── tmp/
│   │
│   ├── software-engineer-worker/
│   │   ├── SKILL.md                     ← Stack detection, implement, validate, CHANGELOG
│   │   └── tmp/
│   │
│   └── ui-ux-pro-max/
│       ├── SKILL.md                     ← Design system → component code
│       ├── scripts/
│       │   └── search.py                ← Design pattern database search
│       └── tmp/
│
├── workflows/
│   ├── start-workflow.md       ← Master orchestrator loop
│   ├── handle-issues.md        ← Issue triage + batch PR
│   ├── handle-code.md          ← Direct implementation
│   ├── handle-pr-review.md     ← Read-only PR review
│   ├── handle-pr-code.md       ← Implement PR review feedback
│   ├── handle-close-pr.md      ← Validate + merge + cleanup
│   └── handle-release.md       ← Release lifecycle
│
└── rules/
    ├── software-engineering-standards.md  ← Architecture, types, tests, security
    ├── issue-task-standards.md            ← Branch safety, PR creation, gh CLI
    ├── pr-code-standards.md               ← Commit format, reply patterns, scope
    ├── pr-review-standards.md             ← Read-only enforcement, risk classification
    └── release-standards.md              ← SemVer, tagging, CHANGELOG, pre-flight
```

---

## Skill Reference

### `issue-task-orchestrator`
Transforms GitHub issues into a prioritized, scored task matrix. Classifies each issue as BUG/FEATURE/REFACTOR/DOC/DUPLICATE/INVALID/ALREADY_FIXED. Posts structured status comments. Detects already-resolved issues by scanning recent merged PR bodies.

**Key scripts:** `score_issues.py` (4-axis priority scoring), `post_issue_comments.py` (gh issue comment automation)

### `pr-code-orchestrator`
Implements all actionable PR review comments. Fetches inline + general review threads, classifies each comment, groups into task batches, invokes `/handle-code`, then posts exactly one structured reply per thread. Creates GitHub issues for out-of-scope requests.

**Key scripts:** `post_comment_replies.py` (gh api pulls/comments/{id}/replies)

### `pr-review-orchestrator`
Read-only PR review. Checks out PR branch, runs full validation suite (build/lint/typecheck/tests), analyzes only changed files, classifies findings by severity and category, submits a single batched review via GitHub API. Zero code modifications.

**Key scripts:** `post_review.py` (gh api pulls/{N}/reviews)

### `release-manager`
Core release logic: detect last tag, classify commits by conventional prefix, compute SemVer bump, generate dual-format release notes. Has dry-run mode. Used by `release-manager-orchestrator`.

### `release-manager-orchestrator`
Full automated release execution. Pre-flight checks → commit detection → notes generation → version bump → CHANGELOG insertion → git commit → tag → push → `gh release create`. Wraps `release-manager` with scripted execution and structured verification.

**Key scripts:**
- `generate_release_notes.py` — commit classifier, SemVer recommendation, dual-format output
- `execute_release.py` — atomic release executor (bump → commit → tag → push → gh release)
- `insert_changelog.py` — CHANGELOG.md insertion utility

### `software-engineer-worker`
The implementation engine. Auto-detects stack (runtime, test framework, lint, typecheck). Enforces architecture discipline, strict typing, test coverage. Self-healing validation loop with error taxonomy. Always updates CHANGELOG.md under [Unreleased].

### `ui-ux-pro-max`
Design-to-code intelligence. Searches design pattern database (style/color/landing/product/ux/typography domains), generates a complete design system with color palette + typography + effects, then outputs production-ready Tailwind component code wired to those tokens.

**Key scripts:** `search.py` (design pattern database query)

---

## Workflow Reference

| Workflow | When to use |
|----------|-------------|
| `/start-workflow` | Beginning of a work session — full pipeline from triage to release |
| `/handle-issues` | Process all open GitHub issues, implement confirmed ones, create batch PR |
| `/handle-code <task>` | Implement a specific scoped task directly (no Jules) |
| `/handle-pr-review <N>` | Code review a PR — read-only, posts structured review via GitHub API |
| `/handle-pr-code <N>` | Implement all actionable review comments on a PR |
| `/handle-close-pr <N>` | Validate CI, merge PR, delete branch, clean Jules sessions |
| `/handle-release` | Full release: classify commits → version → CHANGELOG → tag → GitHub release |

---

## Rules Reference

| Rule | Triggers when... |
|------|-----------------|
| `software-engineering-standards` | Any code creation or modification |
| `issue-task-standards` | Processing or acting on GitHub issues |
| `pr-code-standards` | Implementing PR review feedback |
| `pr-review-standards` | Performing read-only code review |
| `release-standards` | Any release, versioning, or tagging action |

---

## gh CLI Commands Used

```bash
# Issues
make gh-issue-list ARGS="--state open --limit 100 --json ..."
make gh-issue-view ID=N ARGS="--json number,title,body,comments,labels"
make gh-issue-comment ID=N ARGS="--body \"...\""
make gh-issue-close ID=N ARGS="--reason completed|not-planned"

# Pull Requests
make gh-pr-list ARGS="--state open|merged --json ..."
make gh-pr-view ID=N ARGS="--json number,title,headRefName,mergeable"
make gh-pr-checkout ID=N
make gh-pr-create ARGS="--title \"...\" --body \"...\""
make gh-api ENDPOINT="repos/{owner}/{repo}/pulls/{N}/checks"
make gh-pr-create ARGS="--title \"...\" --body \"...\" --label \"...\""
make gh-api ENDPOINT="repos/{owner}/{repo}/pulls/{N}/merge" ARGS="-X PUT"
gh pr comment N --body "@jules ..."

# GitHub API (direct)
gh api repos/{owner}/{repo}/pulls/N/comments
gh api repos/{owner}/{repo}/pulls/comments/{id}/replies -f body="..."
gh api repos/{owner}/{repo}/pulls/N/reviews --method POST --input payload.json

# Releases
gh release create vX.Y.Z --title --notes --latest
gh release view vX.Y.Z
gh repo view --json nameWithOwner,mergeCommitAllowed,...
gh run list --branch main --limit 3 --json status,conclusion
```

## jules CLI Commands Used

```bash
make j-dispatch ARGS="--repo owner/repo" TASK="enriched task description"
make j-dispatch ARGS="--repo owner/repo" PARALLEL=1 TASK="task"
make j-list
make j-pull ID=N # With --apply integrated in j-pull
make j-pull-apply ID=N # Explicit pull with --apply
make j-teleport ID=SESSION_ID
```

---

## Jules Discipline

To guarantee a clean handoff from Jules remote sessions to the local workspace:

1. **Local Branch First**: Always create a feature branch (`git checkout -b feature/...`) before pulling changes.
2. **Apply with Pull**: Use `jules remote pull --session <ID> --apply`. This ensures the changes are immediately available for verification.
3. **Docker Verification**: NEVER test changes in the host environment. Build the image (`docker compose build`) and run tests inside the container (`docker compose run`).
4. **Self-Correction**: If Jules's code breaks existing patterns (e.g. bypasses a factory), refactor immediately before committing.

---

## Setup

1. Copy this entire `.agent/` directory into the root of your repository.
2. Add the lines from `_gitignore-additions.txt` to your `.gitignore`.
3. Ensure `gh` CLI is authenticated: `gh auth status`
4. Ensure `jules` CLI is installed and authenticated.
5. Run `/start-workflow` to begin.

---

## Troubleshooting

**"ABORT: Uncommitted changes detected"**
→ Run `git status` and either commit or `git stash` before proceeding.

**"ERROR: On protected branch"**
→ A skill tried to commit to main/master. This is always a bug — check `git branch --show-current` and file an issue.

**"Search engine not available" from ui-ux-pro-max**
→ The full `search.py` engine requires the complete skill package. The stub generates a skeleton design system that's still usable.

**Jules session not completing**
→ Check `make j-list` and `gh pr list --state open` to find the PR Jules created, then proceed with `/handle-pr-review N`.
