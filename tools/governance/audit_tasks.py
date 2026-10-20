# -*- coding: utf-8 -*-
"""Check every task file individually and tabulate what fails.

`check.ps1` only validates the task STATUS points at, so a plain PASS has always
meant "this one task is fine, and nothing else was looked at". This runs the
checker against all of them to find out how many others were never validated.

Read-only with respect to tasks: it invokes the checker and writes one audit
JSON. It never edits a task file.

Tracked vs draft
----------------
`doc/tasks/` on disk holds more files than git tracks: 26 drafts exist that no
one has committed. Those drafts are counted by the directory scan, so a naive
total mixes two different things - debt in the repository, and work that is not
in the repository at all. r196 measured the difference: of 84 failing tasks, 18
were drafts and their 74 error rows were 37% of the total. Both numbers are
reported so the repository's own debt is readable on its own.
"""
import io
import json
import os
import re
import subprocess
import sys
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TASKS = os.path.join(REPO, "doc", "tasks")
CHECK = os.path.join(REPO, "tools", "governance", "check.ps1")
OUT_JSON = os.path.join(REPO, "verification", "P09-GOVERNANCE-DEBT-20261019",
                        "per-task-check-audit.json")


def tracked_ids() -> set:
    """Task ids git has committed. A draft is not repository debt."""
    try:
        out = subprocess.run(["git", "-C", REPO, "ls-files", "--", "doc/tasks"],
                             capture_output=True, text=True, encoding="utf-8",
                             check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return set()
    ids = set()
    for line in out.splitlines():
        name = os.path.basename(line.strip())
        if name.endswith(".md"):
            ids.add(name[:-3])
    return ids


def task_files():
    for name in sorted(os.listdir(TASKS)):
        if name.endswith(".md") and name != "README.md":
            yield name[:-3], os.path.join(TASKS, name)


def status_of(path):
    head = io.open(path, encoding="utf-8", errors="replace").read().split("\n")[:40]
    for line in head:
        m = re.match(r"^status:\s*(.+?)\s*$", line)
        if m:
            return m.group(1).strip('"\'').lower()
    return "(none)"


def main():
    rows = []
    errors_by_kind = Counter()
    errors_by_kind_tracked = Counter()
    total = 0
    committed = tracked_ids()
    for task_id, path in task_files():
        total += 1
        r = subprocess.run(
            ["pwsh", "-NoProfile", "-File", CHECK, "-TaskPath",
             os.path.join("doc", "tasks", task_id + ".md")],
            cwd=REPO, capture_output=True, text=True, encoding="utf-8",
            errors="replace")
        out = (r.stdout or "") + (r.stderr or "")
        fails = [line.strip()[len("FAIL: "):] for line in out.split("\n")
                 if line.strip().startswith("FAIL:")]
        tracked = task_id in committed
        rows.append({
            "task": task_id,
            "status": status_of(path),
            "tracked": tracked,
            "exit": r.returncode,
            "fail_count": len(fails),
            "fails": fails,
        })
        for f in fails:
            # collapse the variable parts so failures group by cause
            kind = re.sub(r"：.*$", "", f).strip()
            errors_by_kind[kind] += 1
            if tracked:
                errors_by_kind_tracked[kind] += 1

    failing = [r for r in rows if r["fail_count"]]
    failing_tracked = [r for r in failing if r["tracked"]]
    failing_drafts = [r for r in failing if not r["tracked"]]
    rows_tracked = sum(r["fail_count"] for r in failing_tracked)
    rows_drafts = sum(r["fail_count"] for r in failing_drafts)

    print("tasks checked : %d  (tracked %d, untracked drafts %d)"
          % (total, len([r for r in rows if r["tracked"]]),
             len([r for r in rows if not r["tracked"]])))
    print("tasks failing : %d  (tracked %d, untracked drafts %d)"
          % (len(failing), len(failing_tracked), len(failing_drafts)))
    print("error rows    : %d  (tracked %d, untracked drafts %d)"
          % (rows_tracked + rows_drafts, rows_tracked, rows_drafts))
    print()
    print("failure causes (all):")
    for kind, count in errors_by_kind.most_common():
        print("  %-52s %d" % (kind[:52], count))
    print()
    print("failure causes (tracked only - this is the repository's debt):")
    for kind, count in errors_by_kind_tracked.most_common():
        print("  %-52s %d" % (kind[:52], count))
    print()
    print("failing tracked tasks:")
    for r in sorted(failing_tracked, key=lambda r: -r["fail_count"]):
        print("  %-42s %-24s %d" % (r["task"][:42], r["status"], r["fail_count"]))
    print()
    print("failing untracked drafts (not repository debt; the author has not committed):")
    for r in sorted(failing_drafts, key=lambda r: -r["fail_count"]):
        print("  %-42s %-24s %d" % (r["task"][:42], r["status"], r["fail_count"]))

    io.open(OUT_JSON, "w", encoding="utf-8", newline="\n").write(
        json.dumps({"total": total, "failing": len(failing),
                    "failing_tracked": len(failing_tracked),
                    "failing_drafts": len(failing_drafts),
                    "error_rows": rows_tracked + rows_drafts,
                    "error_rows_tracked": rows_tracked,
                    "error_rows_drafts": rows_drafts,
                    "causes": dict(errors_by_kind),
                    "causes_tracked": dict(errors_by_kind_tracked),
                    "tasks": rows},
                   indent=2, ensure_ascii=False))
    print("\nwritten:", OUT_JSON)
    return 0


if __name__ == "__main__":
    sys.exit(main())
