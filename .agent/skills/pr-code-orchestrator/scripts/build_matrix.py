import json
from pathlib import Path

BASE_DIR = Path(".agent/tmp")

def main():
    with open(BASE_DIR / "pr-comments.json") as f:
        data = json.load(f)

    # Filter out bot replies
    comments = [c for c in data if "bot" not in c["user"]["login"]]

    matrix = []
    for c in comments:
        matrix.append({
            "comment_id": c["id"],
            "comment_url": c["html_url"],
            "path": c["path"],
            "line": c.get("line") or c.get("original_line"),
            "classification": "INVALID",
            "task_id": "group1",
            "status": "UNSOLVED",
            "commit_sha": None,
            "issue_number": None
        })

    with open(BASE_DIR / "pr-code-orchestrator-matrix.json", "w") as f:
        json.dump(matrix, f, indent=2)

    with open(BASE_DIR / "task-plan.json", "w") as f:
        json.dump([], f, indent=2)

    print(f"Matrix created with {len(matrix)} entries.")

if __name__ == "__main__":
    main()
