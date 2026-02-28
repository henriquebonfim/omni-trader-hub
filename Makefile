
.PHONY: help test docker-build docker-ps

help:
	@echo "Available commands:"
	@$(MAKE) -f .agent/make/agents.make agent-help
	@echo ""
	@$(MAKE) -f .agent/make/jules.make j-help
	@echo ""
	@$(MAKE) -f .agent/make/gh.make gh-help
	@echo ""
	@echo "Infrastructure commands:"
	@echo "  test                Run project tests (pytest or bun test)"
	@echo "  docker-build        Build docker containers"
	@echo "  docker-ps           Show docker container status"

include .agent/make/agents.make
include .agent/make/jules.make
include .agent/make/gh.make

test:
	@if [ -f pytest.ini ] || [ -f pyproject.toml ]; then \
		pytest -q $(ARGS); \
	elif [ -f package.json ]; then \
		bun test $(ARGS); \
	fi

docker-build:
	@if [ -n "$(COMPOSE_FILE)" ]; then \
		docker compose -f $(COMPOSE_FILE) build; \
	elif [ -f docker-compose.yml ]; then \
		docker compose build; \
	elif [ -f Dockerfile ]; then \
		docker build -t app-check .; \
	fi

docker-ps:
	docker compose ps
