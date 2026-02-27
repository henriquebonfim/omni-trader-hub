#!/usr/bin/env python3
"""
Execute the full release sequence atomically:
  1. Bump version file
  2. Insert CHANGELOG entry
  3. git add + commit
  4. git tag
  5. git push + push tag
  6. gh release create

Usage:
  python3 execute_release.py \
    --version 1.4.0 \
    --version-file package.json \
    --changelog-entry tmp/changelog-entry.md \
    --release-body tmp/release-body.md
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], check: bool = True, capture: bool = True) -> str:
    result = subprocess.run(
        cmd,
        check=check,
        capture_output=capture,
        text=True,
    )
    return result.stdout.strip()


def bump_package_json(version: str) -> None:
    import json as _json
    path = Path("package.json")
    data = _json.loads(path.read_text())
    data["version"] = version
    path.write_text(_json.dumps(data, indent=2) + "\n")
    print(f"  ✅ package.json → {version}")


def bump_pyproject_toml(version: str) -> None:
    path = Path("pyproject.toml")
    content = path.read_text()
    new_content = re.sub(
        r'^(version\s*=\s*")[^"]*(")',
        rf'\g<1>{version}\2',
        content,
        flags=re.MULTILINE,
    )
    path.write_text(new_content)
    print(f"  ✅ pyproject.toml → {version}")


def bump_cargo_toml(version: str) -> None:
    path = Path("Cargo.toml")
    content = path.read_text()
    new_content = re.sub(
        r'^(version\s*=\s*")[^"]*(")',
        rf'\g<1>{version}\2',
        content,
        count=1,
        flags=re.MULTILINE,
    )
    path.write_text(new_content)
    print(f"  ✅ Cargo.toml → {version}")


def bump_version_file(version: str) -> None:
    Path("VERSION").write_text(version + "\n")
    print(f"  ✅ VERSION → {version}")


def bump_version(version_file: str, version: str) -> None:
    """Route to the correct bumper based on version file type."""
    print(f"\n[1/6] Bumping version in {version_file}...")
    vf = version_file.lower()

    if vf == "package.json":
        bump_package_json(version)
    elif vf == "pyproject.toml":
        bump_pyproject_toml(version)
    elif vf == "cargo.toml":
        bump_cargo_toml(version)
    elif vf == "version":
        bump_version_file(version)
    else:
        print(f"  ⚠️  Unknown version file '{version_file}' — skipping auto-bump.")
        print(f"  → Please manually update {version_file} to {version} and re-run.")
        sys.exit(1)


def insert_changelog(version: str, entry_path: Path) -> None:
    """Insert the new changelog entry above the previous release section."""
    print(f"\n[2/6] Updating CHANGELOG.md...")

    entry = entry_path.read_text()
    changelog_path = Path("CHANGELOG.md")

    if not changelog_path.exists():
        # Create from scratch
        changelog_content = (
            "# Changelog\n\n"
            "All notable changes to this project will be documented here.\n"
            "Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)\n\n"
            + entry
        )
        changelog_path.write_text(changelog_content)
        print(f"  ✅ Created CHANGELOG.md with {version} entry")
        return

    content = changelog_path.read_text()

    # Check if this version is already in the changelog
    if f"## [{version}]" in content:
        print(f"  ⚠️  CHANGELOG.md already contains [{version}] — skipping insertion")
        return

    # Find the insertion point: above the first existing ## [X.Y.Z] section
    # but below any top-level header and description
    insertion_pattern = re.compile(r"^## \[", re.MULTILINE)
    match = insertion_pattern.search(content)

    if match:
        pos = match.start()
        new_content = content[:pos] + entry + "\n" + content[pos:]
    else:
        # No existing versioned sections — append at end
        new_content = content.rstrip() + "\n\n" + entry

    changelog_path.write_text(new_content)
    print(f"  ✅ CHANGELOG.md updated with [{version}] entry")


def commit_release(version_file: str, version: str) -> str:
    """Stage version file + CHANGELOG and commit."""
    print(f"\n[3/6] Committing release files...")

    run(["git", "add", "CHANGELOG.md", version_file])
    run(["git", "commit", "-m", f"chore(release): bump version to v{version}"])
    sha = run(["git", "rev-parse", "--short", "HEAD"])
    print(f"  ✅ Committed: chore(release): bump version to v{version} ({sha})")
    return sha


def create_tag(version: str) -> None:
    """Create annotated tag and push."""
    print(f"\n[4/6] Tagging v{version}...")

    # Check tag doesn't already exist
    existing = run(["git", "tag", "-l", f"v{version}"])
    if existing:
        print(f"  ❌ ABORT: Tag v{version} already exists.")
        sys.exit(1)

    run(["git", "tag", "-a", f"v{version}", "-m", f"Release v{version}"])
    print(f"  ✅ Created tag v{version}")


def push_release(version: str) -> None:
    """Push commits and tag."""
    print(f"\n[5/6] Pushing to remote...")

    run(["git", "push", "origin", "HEAD"])
    run(["git", "push", "origin", f"v{version}"])
    print(f"  ✅ Pushed HEAD and tag v{version}")


def create_github_release(version: str, release_body_path: Path) -> str:
    """Create GitHub release via gh CLI."""
    print(f"\n[6/6] Creating GitHub release...")

    release_body = release_body_path.read_text()

    result = run([
        "gh", "release", "create", f"v{version}",
        "--title", f"v{version}",
        "--notes", release_body,
        "--latest",
    ])

    release_url = result.strip()
    print(f"  ✅ Published: {release_url}")
    return release_url


def verify_release(version: str) -> None:
    """Quick sanity check post-release."""
    print(f"\nVerifying release...")

    result = run([
        "gh", "release", "view", f"v{version}",
        "--json", "name,tagName,publishedAt,url",
        "--jq", '"✅ " + .name + " published at " + .publishedAt',
    ])
    print(f"  {result}")

    git_check = run(["git", "log", "--oneline", "-3"])
    print(f"\n  Recent commits:\n  {git_check}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute release sequence")
    parser.add_argument("--version", required=True, help="New version e.g. 1.4.0")
    parser.add_argument("--version-file", required=True, help="package.json / pyproject.toml / etc.")
    parser.add_argument("--changelog-entry", required=True, help="Path to changelog-entry.md")
    parser.add_argument("--release-body", required=True, help="Path to release-body.md")
    args = parser.parse_args()

    version = args.version.lstrip("v")
    changelog_path = Path(args.changelog_entry)
    release_body_path = Path(args.release_body)

    # Validate inputs
    if not changelog_path.exists():
        print(f"ERROR: Changelog entry not found: {changelog_path}", file=sys.stderr)
        sys.exit(1)
    if not release_body_path.exists():
        print(f"ERROR: Release body not found: {release_body_path}", file=sys.stderr)
        sys.exit(1)

    # Guard: ensure clean working tree before starting
    dirty = run(["git", "status", "--short"])
    if dirty:
        print(f"ERROR: Working tree is dirty. Stage or stash changes before releasing.", file=sys.stderr)
        print(dirty)
        sys.exit(1)

    print(f"\n{'━' * 56}")
    print(f"  🚀  RELEASING v{version}")
    print(f"{'━' * 56}")

    try:
        bump_version(args.version_file, version)
        insert_changelog(version, changelog_path)
        sha = commit_release(args.version_file, version)
        create_tag(version)
        push_release(version)
        release_url = create_github_release(version, release_body_path)
        verify_release(version)

        print(f"\n{'━' * 56}")
        print(f"  ✅  v{version} SHIPPED")
        print(f"  Tag:    v{version} → {sha}")
        print(f"  URL:    {release_url}")
        print(f"{'━' * 56}\n")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ RELEASE FAILED at step:", file=sys.stderr)
        print(f"   Command: {' '.join(e.cmd)}", file=sys.stderr)
        print(f"   Error:   {e.stderr}", file=sys.stderr)
        print(f"\n⚠️  Manual cleanup may be required.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
