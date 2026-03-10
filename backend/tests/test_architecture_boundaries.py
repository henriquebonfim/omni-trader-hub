import re
from pathlib import Path

FORBIDDEN_IMPORT_PATTERNS = (
    re.compile(r"^\s*from\s+src\.analysis\b"),
    re.compile(r"^\s*import\s+src\.analysis\b"),
    re.compile(r"^\s*from\s+src\.graph\b"),
    re.compile(r"^\s*import\s+src\.graph\b"),
    re.compile(r"^\s*from\s+src\.strategies\b"),
    re.compile(r"^\s*import\s+src\.strategies\b"),
    re.compile(r"^\s*from\s+\.analysis\b"),
    re.compile(r"^\s*from\s+\.graph\b"),
    re.compile(r"^\s*from\s+\.strategies\b"),
)

ALLOWED_RELATIVE_ANALYSIS_PATHS = {
    Path("src/strategy/smc/__init__.py"),
}

GUARDRAIL_TEST_FILE = Path("tests/test_architecture_boundaries.py")


def test_no_legacy_layer_imports_remain() -> None:
    """DDD guardrail: disallow imports from pre-migration layer modules."""
    repo_root = Path(__file__).resolve().parents[1]
    violations: list[str] = []

    for rel_root in (Path("src"), Path("tests")):
        for py_file in (repo_root / rel_root).rglob("*.py"):
            rel_path = py_file.relative_to(repo_root)
            if rel_path == GUARDRAIL_TEST_FILE:
                continue
            text = py_file.read_text(encoding="utf-8")

            # `src/strategy/smc/__init__.py` legitimately uses local `.analysis`.
            if rel_path in ALLOWED_RELATIVE_ANALYSIS_PATHS:
                patterns = [
                    p
                    for p in FORBIDDEN_IMPORT_PATTERNS
                    if p.pattern != r"^\s*from\s+\.analysis\b"
                ]
            else:
                patterns = FORBIDDEN_IMPORT_PATTERNS

            for line_no, line in enumerate(text.splitlines(), start=1):
                for pattern in patterns:
                    if pattern.search(line):
                        violations.append(f"{rel_path}:{line_no} -> {line.strip()}")

    assert not violations, "\n".join(
        [
            "Legacy layer imports detected (DDD boundary violation):",
            *violations,
        ]
    )
