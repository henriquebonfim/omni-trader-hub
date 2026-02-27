---
name: release-manager-orchestrator
description: Full automated release lifecycle orchestrator — detects unreleased commits, classifies them by conventional prefix, computes SemVer bump, generates dual-format release notes (CHANGELOG.md + GitHub release body), bumps version file, commits, tags, pushes, and publishes via gh release create. Use for ANY release action: "ship a release", "release what's merged", "bump the version", "tag this", "generate release notes", "what's changed since last release", "prepare vX.Y.Z", or "dry run the release". Also triggers for "publish", "deploy to production", "create a tag". Activates the release-manager skill and wraps it with pre-flight checks, structured script execution, and post-release verification.
---

# Release Manager Orchestrator

Automated release lifecycle from merged commits to published GitHub release. Wraps the `release-manager` skill with pre-flight validation, scripted execution, and structured verification.

---

## Setup Check

```bash
gh --version
git --version

mkdir -p .agent/skills/release-manager-orchestrator/tmp
grep -qxF '.agent/skills/release-manager-orchestrator/tmp/' .gitignore \
  || echo '.agent/skills/release-manager-orchestrator/tmp/' >> .gitignore
```

---

## Phase 0 — Pre-flight

No release proceeds with a dirty or failing repo:

```bash
# 1. Must be on main/master
BRANCH=$(git branch --show-current)
[[ "$BRANCH" != "main" && "$BRANCH" != "master" ]] \
  && echo "WARNING: Not on main/master — current: $BRANCH"

# 2. Working tree must be clean
DIRTY=$(git status --short)
[ -n "$DIRTY" ] && echo "ABORT: Uncommitted changes detected. Stash or commit first." && exit 1

# 3. CI must be green on HEAD
LAST_SHA=$(git rev-parse HEAD)
gh run list --commit "$LAST_SHA" --limit 5 \
  --json status,conclusion,workflowName \
  --jq '.[] | "\(.workflowName): \(.status)/\(.conclusion)"'

# 4. Count commits since last tag (if 0, nothing to release)
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "none")
if [ "$LAST_TAG" != "none" ]; then
  COMMIT_COUNT=$(git log ${LAST_TAG}..HEAD --oneline --no-merges | wc -l)
  echo "Commits since ${LAST_TAG}: ${COMMIT_COUNT}"
  [ "$COMMIT_COUNT" -eq 0 ] && echo "ABORT: Nothing new since last tag." && exit 1
fi
```

Store pre-flight results in `tmp/preflight.json`:

```json
{
  "branch": "main",
  "clean_tree": true,
  "ci_status": "PASS|FAIL|UNKNOWN",
  "last_tag": "v1.3.0",
  "commits_since_tag": 12
}
```

---

## Phase 1 — Detect Release Context

```bash
# Last tag
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "NONE")
echo "Last release: $LAST_TAG"

# All commits since tag (written to tmp for script processing)
if [ "$LAST_TAG" != "NONE" ]; then
  git log ${LAST_TAG}..HEAD --oneline --no-merges \
    > .agent/skills/release-manager-orchestrator/tmp/commits-since-tag.txt
else
  git log --oneline --no-merges | head -50 \
    > .agent/skills/release-manager-orchestrator/tmp/commits-since-tag.txt
fi

cat .agent/skills/release-manager-orchestrator/tmp/commits-since-tag.txt

# Detect version file and current version
VERSION_FILE=""
CURRENT_VERSION=""

if [ -f package.json ]; then
  VERSION_FILE="package.json"
  CURRENT_VERSION=$(cat package.json | python3 -c "import sys,json; print(json.load(sys.stdin).get('version','0.0.0'))")
elif [ -f pyproject.toml ]; then
  VERSION_FILE="pyproject.toml"
  CURRENT_VERSION=$(grep "^version" pyproject.toml | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
elif [ -f Cargo.toml ]; then
  VERSION_FILE="Cargo.toml"
  CURRENT_VERSION=$(grep "^version" Cargo.toml | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
elif [ -f VERSION ]; then
  VERSION_FILE="VERSION"
  CURRENT_VERSION=$(cat VERSION)
fi

echo "Version file: $VERSION_FILE"
echo "Current version: $CURRENT_VERSION"
```

---

## Phase 2 — Generate Release Notes (via script)

```bash
python3 .agent/skills/release-manager-orchestrator/scripts/generate_release_notes.py \
  --commits .agent/skills/release-manager-orchestrator/tmp/commits-since-tag.txt \
  --current-version "$CURRENT_VERSION" \
  --output-dir .agent/skills/release-manager-orchestrator/tmp/
```

This produces:
- `tmp/commit-map.json` — commits grouped by category
- `tmp/semver-recommendation.json` — `{ "bump": "MAJOR|MINOR|PATCH", "next_version": "X.Y.Z", "reason": "..." }`
- `tmp/changelog-entry.md` — formatted CHANGELOG.md section
- `tmp/release-body.md` — polished GitHub release notes

### Dry Run Mode

If user said "dry run", "preview", "what would it look like", or "show me the release notes":

→ Print the contents of `tmp/changelog-entry.md` and `tmp/release-body.md` and **STOP HERE**. Do not proceed to Phase 3.

---

## Phase 3 — Version Confirmation

Present the recommendation and wait for confirmation (or auto-proceed if user said "just release"):

```
Current version:  v1.3.0
Suggested next:   v1.4.0  [MINOR — 3 features, 5 fixes]

Changes:
  ✨ Added (3): ...
  🐛 Fixed (5): ...
  🔧 Changed (1): ...

Override? (major / minor / patch / custom vX.Y.Z / proceed):
```

If user provides custom version, validate it matches `vX.Y.Z` or `X.Y.Z` format.

---

## Phase 4 — Execute Release

Run the automated release script:

```bash
python3 .agent/skills/release-manager-orchestrator/scripts/execute_release.py \
  --version "$NEW_VERSION" \
  --version-file "$VERSION_FILE" \
  --changelog-entry .agent/skills/release-manager-orchestrator/tmp/changelog-entry.md \
  --release-body .agent/skills/release-manager-orchestrator/tmp/release-body.md
```

The script performs in order:

### 4a — Bump Version File

```bash
# package.json
npm version <patch|minor|major> --no-git-tag-version
# OR direct sed for pyproject.toml / Cargo.toml / VERSION
```

### 4b — Insert CHANGELOG Entry

Insert above the previous `## [X.Y.Z]` section (or at top if no previous).

```bash
python3 .agent/skills/release-manager-orchestrator/scripts/insert_changelog.py \
  --version "$NEW_VERSION" \
  --entry .agent/skills/release-manager-orchestrator/tmp/changelog-entry.md
```

### 4c — Commit

```bash
git add CHANGELOG.md "${VERSION_FILE}"
git commit -m "chore(release): bump version to v${NEW_VERSION}"
```

### 4d — Tag

```bash
git tag -a "v${NEW_VERSION}" -m "Release v${NEW_VERSION}"
git push origin HEAD
git push origin "v${NEW_VERSION}"
```

### 4e — Create GitHub Release

```bash
RELEASE_BODY=$(cat .agent/skills/release-manager-orchestrator/tmp/release-body.md)

gh release create "v${NEW_VERSION}" \
  --title "v${NEW_VERSION}" \
  --notes "${RELEASE_BODY}" \
  --latest
```

For pre-release:
```bash
gh release create "v${NEW_VERSION}-rc.1" \
  --prerelease \
  --title "v${NEW_VERSION} RC1"
```

---

## Phase 5 — Verify

```bash
# Confirm release is live
gh release view "v${NEW_VERSION}" \
  --json name,tagName,publishedAt,url \
  --jq '"✅ \(.name) published at \(.publishedAt)\n\(.url)"'

# Confirm tag is on correct commit
git log --oneline -3

# Confirm clean state
git status

# Store verification result
echo "{\"version\": \"v${NEW_VERSION}\", \"status\": \"PUBLISHED\"}" \
  > .agent/skills/release-manager-orchestrator/tmp/release-result.json
```

---

## Phase 6 — Cleanup

```bash
rm -f .agent/skills/release-manager-orchestrator/tmp/*.json
rm -f .agent/skills/release-manager-orchestrator/tmp/*.md
rm -f .agent/skills/release-manager-orchestrator/tmp/*.txt
```

---

## Completion Report

```
🚀 Released v${NEW_VERSION}

Tag:       v${NEW_VERSION} → <sha>
GitHub:    https://github.com/{owner}/{repo}/releases/tag/v${NEW_VERSION}
Changes:   <N> added, <N> fixed, <N> changed
CHANGELOG: Updated
```

---

## Abort Conditions

| Condition | Action |
|-----------|--------|
| Uncommitted changes in working tree | ABORT — stash or commit first |
| CI failing on HEAD | ABORT — fix before releasing |
| Zero commits since last tag | ABORT — nothing to release |
| Version file not found | PAUSE — ask user to confirm format |
| Ambiguous breaking changes | PAUSE — request classification before bumping MAJOR |
| Tag already exists | ABORT — already released this version |
