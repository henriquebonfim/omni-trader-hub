# Backlog

Items requiring design, external decisions, or lower priority. Reviewed each sprint — graduate to TODO when ready.

> Last updated: 2026-02-28 by PO Lifecycle Orchestrator

---

## Agent Infrastructure & Reliability

Improvements identified during the Feb 2026 Architectural Review.

### 🛡️ Orchestration Hardening
- [ ] **Deprecate `gh` Subprocess Calls**: Replace brittle `subprocess.run(["gh", ...])` calls in Python orchestrators with native `PyGithub` or `httpx` SDK implementation for better error handling and connection pooling.
- [ ] **Mitigate Shell Argument Limits**: Refactor `make` targets to stop passing large JSON strings/bodies via CLI arguments. Use temporary file-exchange protocols instead.

### 🧪 Quality & Observability
- [ ] **Agent Pipeline Testing**: Implement a test suite for the `.agent/skills/` Python logic. Ensure orchestrators like `post_review.py` and `gather_and_triage.py` are unit tested.
- [ ] **Structured Friction Logging**: Convert `.agent/logs/FRICTION.md` into a structured SQLite or JSONL store to enable automated error-pattern analysis and predictive context injection.
- [ ] **Agent Typecheck Enforcement**: Add a `.agent/pyproject.toml` and enforce `mypy` checks on the entire `.agent/skills/` directory.

### 🧠 Intelligence & UX
- [ ] **Dynamic Design Memory**: Implement a RAG-based search for UI/UX Pro Max that pulls from past successful PRs and design decisions, rather than just static text files.
- [ ] **Async Jules Delegation**: Refactor `start-workflow.md` to handle Jules sessions asynchronously, allowing the agent to poll for completion rather than blocking on sync execution.
