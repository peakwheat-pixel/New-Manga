"""Recompute Canonical Evidence pins in the audit Task card against Git blobs.

Read-only: reads the Task card, resolves every pinned commit/path with
`git cat-file`, recomputes the BLOB SHA-256, and reports mismatches.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_TASK = ROOT / "doc/tasks/NEW-MANGA-V1-FULL-AUDIT.md"
OUT_JSON = ROOT / "audit/V1-FULL-AUDIT/evidence/task-card-pin-recompute-20261113.json"
OUT_LOG = ROOT / "audit/V1-FULL-AUDIT/logs/task-card-pin-recompute-20261113.log"

ROW = re.compile(
    r"^\|\s*(?P<eid>[A-Za-z0-9._-]+)\s*\|\s*(?P<ac>[^|]*?)\s*\|\s*`(?P<path>[^`]+)`\s*\|"
    r"\s*`(?P<commit>[0-9a-fA-F]{7,40})`\s*\|\s*`(?P<sha>[0-9A-Fa-f]{64})`\s*\|"
    r"\s*(?P<klass>CANONICAL|SOURCE_PIN)\s*\|\s*(?P<basis>BLOB|WORKTREE)\s*\|\s*$"
)


def git(*args: str, binary: bool = False):
    result = subprocess.run(
        ["git", *args], cwd=ROOT, check=False, capture_output=True
    )
    if result.returncode != 0:
        return result.returncode, result.stdout if binary else result.stdout.decode("utf-8", "replace")
    return 0, result.stdout if binary else result.stdout.decode("utf-8", "replace")


def main() -> int:
    argv = sys.argv[1:]
    task_path = DEFAULT_TASK
    suffix = ""
    if "--task" in argv:
        task_path = Path(argv[argv.index("--task") + 1]).resolve()
    if "--suffix" in argv:
        suffix = argv[argv.index("--suffix") + 1]
    out_json = OUT_JSON if not suffix else OUT_JSON.with_name(OUT_JSON.stem + suffix + ".json")
    out_log = OUT_LOG if not suffix else OUT_LOG.with_name(OUT_LOG.stem + suffix + ".log")
    text = task_path.read_text(encoding="utf-8")
    rows = []
    for line in text.splitlines():
        match = ROW.match(line.strip())
        if match:
            rows.append(match.groupdict())

    head_rc, head = git("rev-parse", "HEAD")
    head = head.strip()
    branch_rc, branch = git("branch", "--show-current")

    results = []
    failures = []
    for row in rows:
        entry = {"evidence_id": row["eid"], "path": row["path"],
                 "commit": row["commit"], "expected_sha256": row["sha"],
                 "sha256_basis": row["basis"], "class": row["klass"]}
        type_rc, type_out = git("cat-file", "-t", row["commit"])
        entry["commit_type"] = type_out.strip() if type_rc == 0 else None
        if type_rc != 0 or entry["commit_type"] != "commit":
            entry["result"] = "FAIL_COMMIT"
            failures.append(entry)
            results.append(entry)
            continue
        exists_rc, _ = git("cat-file", "-e", f"{row['commit']}:{row['path']}")
        if exists_rc != 0:
            entry["result"] = "FAIL_PATH"
            failures.append(entry)
            results.append(entry)
            continue
        if row["basis"] != "BLOB":
            entry["result"] = "SKIP_BASIS_WORKTREE"
            results.append(entry)
            continue
        blob_rc, blob = git("cat-file", "blob", f"{row['commit']}:{row['path']}", binary=True)
        if blob_rc != 0:
            entry["result"] = "FAIL_BLOB"
            failures.append(entry)
            results.append(entry)
            continue
        actual = hashlib.sha256(blob).hexdigest().upper()
        entry["actual_sha256"] = actual
        entry["bytes"] = len(blob)
        if actual == row["sha"].upper():
            entry["result"] = "PASS"
        else:
            entry["result"] = "FAIL_SHA256"
            failures.append(entry)
        results.append(entry)

    payload = {
        "schema": "task-card-pin-recompute/v1",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "head": head,
        "branch": branch.strip(),
        "task_card": str(task_path.relative_to(ROOT)) if task_path.is_relative_to(ROOT) else str(task_path),
        "pin_rows": len(rows),
        "pass": sum(1 for item in results if item["result"] == "PASS"),
        "skipped_worktree_basis": sum(1 for item in results if item["result"] == "SKIP_BASIS_WORKTREE"),
        "failed": len(failures),
        "failures": failures,
        "results": results,
    }
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        f"START_UTC={payload['checked_at_utc']}",
        f"HEAD={head}",
        f"BRANCH={branch.strip()}",
        "SHELL=Python subprocess (no shell)",
        f"INTERPRETER={sys.executable}",
        f"TASK={payload['task_card']}",
        "",
        f"pin_rows={payload['pin_rows']} pass={payload['pass']} "
        f"skipped_worktree_basis={payload['skipped_worktree_basis']} failed={payload['failed']}",
    ]
    for item in results:
        lines.append(
            f"{item['result']}: {item['evidence_id']} commit={item['commit']} "
            f"path={item['path']} expected={item['expected_sha256']}"
            + (f" actual={item.get('actual_sha256')}" if item.get("actual_sha256") else "")
        )
    lines.append("")
    lines.append(f"EXIT={0 if not failures else 1}")
    out_log.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
