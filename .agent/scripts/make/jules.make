JULES_DIR = .agent/tmp/jules
$(shell mkdir -p $(JULES_DIR)/sessions)

.PHONY: j-help j-login j-logout j-list j-status j-dispatch j-pull j-teleport j-clean j-version

# Default values
PARALLEL ?= 1
J_POLL_TIMEOUT ?= 3600

j-help:
	@echo "Event-Oriented Jules commands:"
	@echo "  j-dispatch TASK=\"...\" ARGS=\"--repo ...\" PARALLEL=1"
	@echo "  j-dispatch-file TASK_FILE=\"...\" ARGS=\"--repo ...\" PARALLEL=1"
	@echo "  j-list                 List all remote sessions"
	@echo "  j-status ID=<id>       Check status of a specific session"
	@echo "  j-poll ID=<id>         Poll session until completion"
	@echo "  j-pull ID=<id>         Pull and apply changes from session ID"
	@echo "  j-teleport ID=<id>     Teleport to session ID"
	@echo "  j-clean                Clear local session markers"
	@echo "  j-version              Show Jules CLI version"

j-login:
	jules login

j-logout:
	jules logout

j-version:
	jules version

j-list:
	@jules remote list --session

# Dispatch creates a local record of the task
j-dispatch:
	@echo "Dispatching task: $(TASK) (parallel=$(PARALLEL))"
	@ID=$$(jules new $(ARGS) --parallel $(PARALLEL) "$(TASK)" | grep -oE '[0-9]{6,}') && \
	echo "Created session $$ID" && \
	echo "$(TASK)" > $(JULES_DIR)/sessions/$$ID.task && \
	touch $(JULES_DIR)/sessions/$$ID.dispatched

j-dispatch-file:
	@echo "Dispatching task from file: $(TASK_FILE) (parallel=$(PARALLEL))"
	@ID=$$(jules new $(ARGS) --parallel $(PARALLEL) "$$(cat $(TASK_FILE))" | grep -oE '[0-9]{6,}') && \
	echo "Created session $$ID" && \
	cat $(TASK_FILE) > $(JULES_DIR)/sessions/$$ID.task && \
	touch $(JULES_DIR)/sessions/$$ID.dispatched

j-status:
	@if [ -z "$(ID)" ]; then echo "Usage: make j-status ID=<id>"; exit 1; fi
	@COLUMNS=200 jules remote list --session | grep "$(ID)" || echo "Session $(ID) not found or completed."

j-poll:
	@if [ -z "$(ID)" ]; then echo "Usage: make j-poll ID=<id>"; exit 1; fi
	@python3 .agent/scripts/jules_poll.py --id $(ID) --interval 60 --timeout $(J_POLL_TIMEOUT)

j-pull:
	@if [ -z "$(ID)" ]; then echo "Usage: make j-pull ID=<id>"; exit 1; fi
	jules remote pull --session $(ID) --apply
	@mv $(JULES_DIR)/sessions/$(ID).dispatched $(JULES_DIR)/sessions/$(ID).applied 2>/dev/null || true

j-teleport:
	@if [ -z "$(ID)" ]; then echo "Usage: make j-teleport ID=<id>"; exit 1; fi
	jules teleport $(ID)

j-clean:
	rm -rf $(JULES_DIR)/sessions/*
