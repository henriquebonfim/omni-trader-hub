# Agent Orchestration Scripts
ISSUE_SCORE = .agent/skills/issue-task-orchestrator/scripts/score_issues.py
ISSUE_POST = .agent/skills/issue-task-orchestrator/scripts/post_issue_comments.py
ISSUE_TASKS = .agent/skills/issue-task-orchestrator/scripts/generate_tasks_md.py
PR_REPLY = .agent/skills/pr-code-orchestrator/scripts/post_comment_replies.py
PR_REVIEW = .agent/skills/pr-review-orchestrator/scripts/post_review.py
PO_TRIAGE = .agent/skills/po-lifecycle-orchestrator/scripts/gather_and_triage.py
PO_POST = .agent/skills/po-lifecycle-orchestrator/scripts/post_triage_comments.py
RELEASE_GEN = .agent/skills/release-manager-orchestrator/scripts/generate_release_notes.py
RELEASE_EXEC = .agent/skills/release-manager-orchestrator/scripts/execute_release.py
RELEASE_INSERT = .agent/skills/release-manager-orchestrator/scripts/insert_changelog.py

.PHONY: agent-help issue-score issue-post issue-tasks pr-reply pr-review po-triage po-post release-gen release-exec release-insert issue-refs clean-tmp

agent-help:
	@echo "Agent Orchestration Commands:"
	@echo "  issue-score         Score open issues"
	@echo "  issue-post          Post status comments to issues"
	@echo "  issue-tasks         Generate TASKS.md from confirmed issues"
	@echo "  pr-reply PR=<num>   Post comment replies to a PR"
	@echo "  pr-review PR=<num>  Post a PR review"
	@echo "  po-triage           Gather and triage backlog"
	@echo "  po-post             Post triage results as comments"
	@echo "  release-gen         Generate release notes"
	@echo "  release-exec         Execute full release"
	@echo "  release-insert       Insert changelog entry"
	@echo "  clean-tmp            Clean all agent temporary artifacts"

issue-score:
	python3 $(ISSUE_SCORE)

issue-post:
	python3 $(ISSUE_POST)

issue-tasks:
	python3 $(ISSUE_TASKS)

pr-reply:
	python3 $(PR_REPLY) $(PR)

pr-review:
	python3 $(PR_REVIEW) $(PR)

po-triage:
	python3 $(PO_TRIAGE) $(ARGS)

po-post:
	python3 $(PO_POST) $(ARGS)

release-gen:
	python3 $(RELEASE_GEN) $(ARGS)

release-exec:
	python3 $(RELEASE_EXEC) $(ARGS)

release-insert:
	python3 $(RELEASE_INSERT) $(ARGS)

issue-refs:
	@jq -r '.[] | select(.status=="CONFIRMED") | "Closes #\(.issue_number)"' .agent/tmp/issue-matrix.json 2>/dev/null || true

clean-tmp:
	@echo "Cleaning temporary agent artifacts..."
	@rm -f .agent/tmp/*.json
	@rm -f .agent/tmp/*.md
	@rm -f .agent/tmp/*.txt
	@rm -f .agent/tmp/*.patch
	@rm -f .agent/tmp/*.png
