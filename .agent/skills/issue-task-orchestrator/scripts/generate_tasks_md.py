import json
import os
import datetime

def main():
    matrix_path = '.agent/tmp/issue-matrix.json'
    try:
        with open(matrix_path, 'r') as f:
            matrix = json.load(f)
    except FileNotFoundError:
        matrix = []

    confirmed = [i for i in matrix if i.get('status') == 'CONFIRMED']
    lines = ['# Tasks\n', f'Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n']

    for i, task in enumerate(confirmed, 1):
        lines.append(f"## {i}. Issue #{task.get('issue_number', 'UNKNOWN')}: {task.get('title', 'Untitled')}")
        lines.append(f"- Priority Score: {task.get('priority_score', 'N/A')}")
        lines.append(f"- Classification: {task.get('classification', 'N/A')}")
        lines.append("")

    with open('TASKS.md', 'w') as f:
        f.write('\n'.join(lines))

    print(f"Generated TASKS.md with {len(confirmed)} confirmed items.")

if __name__ == "__main__":
    main()
