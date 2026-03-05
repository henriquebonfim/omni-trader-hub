# Stack Configuration — Single Source of Truth
# Agents NEVER guess package managers. Edit these per project.
# All skills and workflows call `make test`, `make lint`, etc.

# ─── Runtime ───────────────────────────────────────────────
RUNTIME    = python
PKG_MGR    = pip

# ─── Commands ──────────────────────────────────────────────
SETUP_CMD  = cp -n .env.example .env 2>/dev/null || true && docker compose build
START_CMD  = docker compose up -d
STOP_CMD   = docker compose down
TEST_CMD   = docker compose run --rm -e PYTHONPATH=/app omnitrader pytest -q tests/ && docker compose run --rm frontend-test bun test --pass-with-no-tests
LINT_CMD   = docker compose run --rm -e PYTHONPATH=/app omnitrader ruff check src/ && docker compose run --rm frontend-test bun run lint
TYPE_CMD   = docker compose run --rm -e PYTHONPATH=/app omnitrader mypy src/ && docker compose run --rm frontend-test bun run typecheck
BUILD_CMD  = docker compose build
DEV_CMD    = docker compose up

# ─── Targets ──────────────────────────────────────────────
.PHONY: setup start stop test tests lint typecheck build dev logs ps stack-info

setup:
	@echo "Setting up OmniTrader..."
	@if [ ! -f .env ]; then \
		cp .env.example .env && echo "✓ Created .env from .env.example"; \
		echo "⚠️  Edit .env and set POSTGRES_PASSWORD before running 'make start'"; \
	else \
		echo "✓ .env already exists"; \
	fi
	@echo "Building Docker images..."
	$(BUILD_CMD)
	@echo "✓ Setup complete! Run 'make start' to launch the application."

start:
	@echo "Starting OmniTrader stack..."
	$(START_CMD)
	@echo "✓ Stack started!"
	@echo "  Dashboard: http://localhost:3000"
	@echo "  API:       http://localhost:8000/docs"
	@echo "  Health:    http://localhost:8000/api/health"
	@echo ""
	@echo "Run 'make logs' to view container logs"
	@echo "Run 'make stop' to stop all containers"

stop:
	@echo "Stopping OmniTrader stack..."
	$(STOP_CMD)
	@echo "✓ Stack stopped"

test:
	$(TEST_CMD) $(ARGS)

tests: test

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
	@echo ""
	@echo "Common Commands:"
	@echo "  make setup      - Initial setup (create .env, build images)"
	@echo "  make start      - Start all containers in background"
	@echo "  make stop       - Stop all containers"
	@echo "  make test       - Run all tests inside Docker"
	@echo "  make logs       - View container logs"
	@echo "  make build      - Rebuild Docker images"
	@echo "  make dev        - Start in foreground (with logs)"
	@echo "  make lint       - Run linters"
	@echo "  make typecheck  - Run type checking"

logs:
	docker compose logs -f

ps:
	docker compose ps
