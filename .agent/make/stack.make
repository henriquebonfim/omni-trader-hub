# Stack Configuration — Single Source of Truth
# Agents NEVER guess package managers. Edit these per project.
# All skills and workflows call `make test`, `make lint`, etc.

# ─── Runtime ───────────────────────────────────────────────
RUNTIME    = python
PKG_MGR    = pip

# ─── Commands ──────────────────────────────────────────────
TEST_CMD   = cd backend && .venv/bin/pytest -q tests/ && cd ../frontend && bun test
LINT_CMD   = cd backend && .venv/bin/ruff check src/ && cd ../frontend && bun run lint
TYPE_CMD   = cd backend && .venv/bin/mypy src/ && cd ../frontend && bun run typecheck
BUILD_CMD  = docker compose build
DEV_CMD    = docker compose up

# ─── Targets ──────────────────────────────────────────────
.PHONY: test lint typecheck build dev stack-info

test:
	$(TEST_CMD) $(ARGS)

lint:
	$(LINT_CMD) $(ARGS)

typecheck:
	$(TYPE_CMD) $(ARGS)

build:
	$(BUILD_CMD)

dev:
	$(DEV_CMD)

stack-info:
	@echo "Stack Configuration:"
	@echo "  Runtime:    $(RUNTIME)"
	@echo "  Pkg Mgr:   $(PKG_MGR)"
	@echo "  Test:       $(TEST_CMD)"
	@echo "  Lint:       $(LINT_CMD)"
	@echo "  Typecheck:  $(TYPE_CMD)"
	@echo "  Build:      $(BUILD_CMD)"
	@echo "  Dev:        $(DEV_CMD)"
