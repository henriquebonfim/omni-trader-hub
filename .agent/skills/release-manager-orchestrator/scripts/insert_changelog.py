#!/usr/bin/env python3
"""
Insert a prepared changelog entry into CHANGELOG.md above the previous release.

Usage:
  python3 insert_changelog.py --version 1.4.0 --entry tmp/changelog-entry.md
"""

import argparse
import re
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--entry", required=True, help="Path to prepared .md entry")
    args = parser.parse_args()

    version = args.version.lstrip("v")
    entry_path = Path(args.entry)
    changelog_path = Path("CHANGELOG.md")

    if not entry_path.exists():
        print(f"ERROR: Entry file not found: {entry_path}", file=sys.stderr)
        sys.exit(1)

    entry = entry_path.read_text()

    if not changelog_path.exists():
        content = (
            "# Changelog\n\n"
            "All notable changes to this project will be documented here.\n"
            "Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)\n\n"
            + entry
        )
        changelog_path.write_text(content)
        print(f"✅ Created CHANGELOG.md with [{version}]")
        return

    content = changelog_path.read_text()

    if f"## [{version}]" in content:
        print(f"⚠️  [{version}] already in CHANGELOG.md — skipping")
        return

    match = re.search(r"^## \[", content, re.MULTILINE)
    if match:
        pos = match.start()
        new_content = content[:pos] + entry + "\n" + content[pos:]
    else:
        new_content = content.rstrip() + "\n\n" + entry

    changelog_path.write_text(new_content)
    print(f"✅ Inserted [{version}] into CHANGELOG.md")


if __name__ == "__main__":
    main()
