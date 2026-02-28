# Root Makefile — thin dispatcher
# All stack commands defined in .agent/make/stack.make
# All agent orchestration in .agent/make/agents.make

.PHONY: help docker-ps

help:
	@echo "=== Project Commands ==="
	@$(MAKE) --no-print-directory -f .agent/make/stack.make stack-info
	@echo ""
	@echo "=== Agent Commands ==="
	@$(MAKE) --no-print-directory -f .agent/make/agents.make agent-help
	@echo ""
	@$(MAKE) --no-print-directory -f .agent/make/jules.make j-help
	@echo ""
	@$(MAKE) --no-print-directory -f .agent/make/gh.make gh-help

include .agent/make/stack.make
include .agent/make/agents.make
include .agent/make/jules.make
include .agent/make/gh.make

docker-ps:
	docker compose ps
