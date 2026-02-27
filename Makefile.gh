.PHONY: gh-help gh-issue-list gh-issue-view gh-issue-comment gh-issue-close gh-pr-list gh-pr-view gh-pr-checkout gh-pr-create gh-pr-diff gh-api gh-release-create gh-run-list

gh-help:
	@echo "GitHub CLI Commands:"
	@echo "  gh-issue-list ARGS=\"...\"        List issues"
	@echo "  gh-issue-view ID=123             View issue"
	@echo "  gh-issue-comment ID=123 ARGS=\"...\" Post issue comment"
	@echo "  gh-issue-close ID=123 ARGS=\"...\"   Close issue"
	@echo "  gh-pr-list ARGS=\"...\"           List PRs"
	@echo "  gh-pr-view ID=123                View PR"
	@echo "  gh-pr-checkout ID=123            Checkout PR"
	@echo "  gh-pr-create ARGS=\"...\"         Create PR"
	@echo "  gh-pr-diff ID=123 ARGS=\"...\"     View PR diff"
	@echo "  gh-api ENDPOINT=\"...\" ARGS=\"...\" Call GitHub API"
	@echo "  gh-release-create ARGS=\"...\"    Create a release"
	@echo "  gh-run-list ARGS=\"...\"          List GitHub Actions runs"

gh-issue-list:
	gh issue list $(ARGS)

gh-issue-view:
	gh issue view $(ID) $(ARGS)

gh-issue-comment:
	gh issue comment $(ID) $(ARGS)

gh-issue-close:
	gh issue close $(ID) $(ARGS)

gh-pr-list:
	gh pr list $(ARGS)

gh-pr-view:
	gh pr view $(ID) $(ARGS)

gh-pr-checkout:
	gh pr checkout $(ID) $(ARGS)

gh-pr-create:
	gh pr create $(ARGS)

gh-pr-diff:
	gh pr diff $(ID) $(ARGS)

gh-release-create:
	gh release create $(ARGS)

gh-run-list:
	gh run list $(ARGS)

gh-api:
	gh api $(ENDPOINT) $(ARGS)
