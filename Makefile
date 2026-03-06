# Root Makefile — thin dispatcher
# All stack commands defined in .agent/make/stack.make
# All agent orchestration in .agent/make/agents.make

.PHONY: help docker-ps

help:
	@echo "=== Quick Start ==="
	@echo "  make setup  - Initial setup (create .env, build images)"
	@echo "  make start  - Start application in background"
	@echo "  make stop   - Stop all containers"
	@echo "  make test   - Run all tests inside Docker"
	@echo "  make logs   - View container logs"
	@echo ""
	@echo "=== Project Commands ==="
	@$(MAKE) --no-print-directory -f .agent/scripts/make/stack.make stack-info
	@echo ""
	@echo "=== Agent Commands ==="
	@$(MAKE) --no-print-directory -f .agent/scripts/make/agents.make agent-help
	@echo ""
	@$(MAKE) --no-print-directory -f .agent/scripts/make/jules.make j-help
	@echo ""
	@$(MAKE) --no-print-directory -f .agent/scripts/make/gh.make gh-help

include .agent/scripts/make/stack.make
include .agent/scripts/make/agents.make
include .agent/scripts/make/jules.make
include .agent/scripts/make/gh.make

docker-ps:
	docker compose ps
