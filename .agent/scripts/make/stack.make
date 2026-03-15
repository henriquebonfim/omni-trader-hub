# Stack Configuration — Single Source of Truth
# Agents NEVER guess package managers. Edit these per project.
# All skills and workflows call `make test`, `make lint`, etc.

# ─── Runtime ───────────────────────────────────────────────
RUNTIME    = python
PKG_MGR    = pip
COMPOSE_DEV = docker compose -f compose.yml -f compose.dev.yml
COMPOSE_PROD = docker compose -f compose.yml

# ─── Commands ──────────────────────────────────────────────
SETUP_CMD  = cp -n .env.example .env 2>/dev/null || true && $(COMPOSE_DEV) build
START_CMD  = $(COMPOSE_DEV) up -d
STOP_CMD   = $(COMPOSE_DEV) down
TEST_CMD   = $(COMPOSE_DEV) run --rm -e PYTHONPATH=/app omnitrader pytest -q tests/ && $(COMPOSE_DEV) --profile test run --rm frontend-test bun run test --pass-with-no-tests
LINT_CMD   = $(COMPOSE_DEV) run --rm -e PYTHONPATH=/app omnitrader ruff check src/ && $(COMPOSE_DEV) run --rm frontend-test bun run lint
TYPE_CMD   = $(COMPOSE_DEV) run --rm -e PYTHONPATH=/app omnitrader mypy src/ && $(COMPOSE_DEV) run --rm frontend-test bun run typecheck
BUILD_CMD  = $(COMPOSE_DEV) build
DEV_CMD    = $(COMPOSE_DEV) up

# DDD guardrail contract (override per project as needed)
DDD_BOUNDARY_CMD ?= true
DDD_LINT_CMD ?= true
DDD_IMPORT_GUARD_CMD ?= true
DDD_GUARD_CMD = $(DDD_BOUNDARY_CMD) && $(DDD_LINT_CMD) && $(DDD_IMPORT_GUARD_CMD)

# ─── Targets ──────────────────────────────────────────────
.PHONY: setup start stop test tests lint typecheck build dev ddd-guard logs ps start-prod stop-prod build-prod stack-info

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

ddd-guard:
	@echo "Running DDD architecture guard..."
	@$(DDD_GUARD_CMD)
	@echo "✓ DDD guard passed"

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
	@echo "  make ddd-guard  - Run project DDD guardrails"
	@echo "  make start-prod - Start production compose stack"
	@echo "  make stop-prod  - Stop production compose stack"
	@echo "  make build-prod - Build production compose images"
	@echo "  make lint       - Run linters"
	@echo "  make typecheck  - Run type checking"

logs:
	$(COMPOSE_DEV) logs -f

ps:
	$(COMPOSE_DEV) ps

start-prod:
	@echo "Starting production stack..."
	$(COMPOSE_PROD) up -d

stop-prod:
	@echo "Stopping production stack..."
	$(COMPOSE_PROD) down

build-prod:
	@echo "Building production images..."
	$(COMPOSE_PROD) build
