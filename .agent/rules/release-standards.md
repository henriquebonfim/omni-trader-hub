---
trigger: model_decision
description: Governs all release operations — version bumping, tagging, CHANGELOG generation, and GitHub release creation. Apply whenever any release-related action is requested or triggered.
---

# Release Standards

---

## Pre-Release Gate (Non-Negotiable)

No release proceeds unless ALL pass:

```bash
# 1. Clean working tree
git status --short  # Must be empty

# 2. On main/master
git branch --show-current  # Must be main or master

# 3. CI green on HEAD
gh run list --limit 3 --json conclusion \
  --jq '[.[] | .conclusion] | all(. == "success")'

# 4. Something to release
git log $(git describe --tags --abbrev=0)..HEAD --oneline | wc -l
# Must be > 0
```

If any check fails: ABORT with clear error message. Never release from a dirty, failing, or empty-since-last-tag state.

---

## SemVer Rules (Strict)

| Commits contain | Bump |
|-----------------|------|
| Any `BREAKING CHANGE` or `feat!:` | **MAJOR** |
| Any `feat:` (no breaking) | **MINOR** |
| Only `fix:`, `perf:`, `refactor:` | **PATCH** |
| Only `docs:`, `chore:`, `ci:` | No bump |

Rules:
- MAJOR resets MINOR and PATCH to 0
- MINOR resets PATCH to 0
- Pre-release versions: `vX.Y.Z-rc.N`, `vX.Y.Z-beta.N`
- Never skip versions (1.3.0 → 1.4.0, not 1.3.0 → 2.0.0 without breaking changes)

---

## Tagging Convention

```bash
# Annotated tag always (not lightweight)
git tag -a vX.Y.Z -m "Release vX.Y.Z"

# Push tag explicitly (push HEAD + tag separately)
git push origin HEAD
git push origin vX.Y.Z

# Never push --tags (pushes all tags, including unintended ones)
```

Tag format: `vX.Y.Z` (with `v` prefix, lowercase).

---

## CHANGELOG.md Discipline

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/):

```markdown
## [X.Y.Z] — YYYY-MM-DD

### ✨ Added
- ...

### 🐛 Fixed
- ...

### 🔒 Security
- ...

### ⚡ Performance
- ...

### 🔧 Changed
- ...

### ⚠️ BREAKING CHANGES
- ...
```

Rules:
- Always insert above the previous release section, never below
- Never edit existing release sections
- Link PR/issue numbers when present: `(#N)`
- Maintenance commits (chore/ci/docs) go in collapsed `<details>` — not main view
- Breaking changes always at top with ⚠️ prefix

If CHANGELOG.md doesn't exist → create it with the standard header.

---

## GitHub Release Requirements

```bash
# Required flags
gh release create vX.Y.Z \
  --title "vX.Y.Z" \        # Always exact tag name
  --notes "..." \           # Always include release body
  --latest                  # Only for stable releases

# For pre-releases
gh release create vX.Y.Z-rc.1 \
  --prerelease \            # Required for pre-releases
  --title "vX.Y.Z RC1"
```

Release body requirements:
- Opens with 1-2 sentence summary of the release theme (not a commit dump)
- `### Highlights` section for new features (top 5-6 max)
- `### Bug Fixes` for fixes
- `### Security` if any security fixes (always include, update urgently advised)
- `### Upgrading` section with migration steps if breaking changes
- Ends with comparison URL to previous tag

---

## Version File Rules

| File | Tool/method |
|------|-------------|
| `package.json` | Direct JSON edit (update `"version"` field) |
| `pyproject.toml` | `sed` regex on `^version = "..."` |
| `Cargo.toml` | `sed` regex on first `^version = "..."` |
| `VERSION` | Direct file write |

Rules:
- NEVER use `npm version` (creates its own tag by default)
- Only bump the version file — don't edit lockfiles manually
- Commit version file + CHANGELOG.md together in one release commit

---

## Release Commit Format

```
chore(release): bump version to vX.Y.Z
```

This is the only change in the release commit. No code changes mixed in.

---

## Temporary Artifacts

Location: `.agent/tmp/`

Files created during release:
- `preflight.json` — pre-flight check results
- `commits-since-tag.txt` — raw git log output
- `commit-map.json` — classified commits
- `semver-recommendation.json` — computed bump + reasoning
- `changelog-entry.md` — prepared CHANGELOG section
- `release-body.md` — prepared GitHub release notes
- `release-result.json` — post-release verification

All wiped after successful release. Never committed.

---

## Post-Release Verification

Always verify:

```bash
gh release view vX.Y.Z --json name,tagName,publishedAt,url
git log --oneline -3       # Confirm release commit is HEAD
git status                 # Must be clean
```

If verification fails: do NOT attempt to undo — document the state and escalate.

---

## Abort Conditions — Hard Stops

| Condition | Action |
|-----------|--------|
| Tag already exists | ABORT — never re-tag or overwrite |
| Working tree dirty | ABORT — stash or commit first |
| CI failing | ABORT — fix before releasing |
| No commits since last tag | ABORT — nothing to release |
| CHANGELOG already contains this version | SKIP insertion, proceed with tag/release |
