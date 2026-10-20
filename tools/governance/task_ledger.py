#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reconcilable Task ledger: every task file against the plan's node set.

r38 §3 ruled this should exist and that nobody should rely on an agent
remembering to count. It also ruled the counting must be reproducible, so this
is a script, not a hand-written table: run it and you get the same numbers.

    python tools/governance/task_ledger.py            # summary
    python tools/governance/task_ledger.py --diff     # plus the drift list
    python tools/governance/task_ledger.py --write    # refresh the ledger file

Nothing here changes a task's status. The ledger reports; ruling on what to do
about 40 non-terminal tasks is a separate decision (r38 declined to bulk-close
them, because a status field records history rather than proving liveness).
"""
from __future__ import annotations

import argparse
import glob
import io
import os
import sys
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TASKS_DIR = os.path.join(REPO, "doc", "tasks")
PLAN = os.path.join(REPO, "doc", "REBASELINE_PLAN.md")
STATUS = os.path.join(REPO, "doc", "STATUS.md")
LEDGER = os.path.join(REPO, "doc", "TASK_LEDGER.md")

#: A task in one of these states is finished; everything else is not.
TERMINAL = {"done", "closed_with_limitations", "cancelled", "superseded", "historical"}
#: These states mean someone may still be working, so they must not be swept
#: up by a bulk close (r38 §2.3).
ACTIVE_TRACES = {"in_progress", "in_review", "approved", "changes_requested", "ready"}


def read_frontmatter_status(text: str) -> str | None:
    """status: from the YAML front matter only, not from the prose body."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith("status:"):
            return line.split(":", 1)[1].strip().strip("\"'")
    return None


def collect() -> list[dict]:
    rows = []
    for path in sorted(glob.glob(os.path.join(TASKS_DIR, "*.md"))):
        task_id = os.path.basename(path)[:-3]
        # README.md is the task index, not a task. Counting it produced a
        # phantom "(none)" row and shifted every total by one.
        if task_id.lower() == "readme":
            continue
        text = io.open(path, encoding="utf-8", errors="replace").read()
        rows.append(
            {
                "id": task_id,
                "status": read_frontmatter_status(text) or "(none)",
                "path": os.path.relpath(path, REPO).replace("\\", "/"),
            }
        )
    return rows


def plan_text() -> str:
    return io.open(PLAN, encoding="utf-8", errors="replace").read()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--diff", action="store_true",
                        help="list the non-terminal tasks and whether the plan names them")
    parser.add_argument("--write", action="store_true",
                        help="rewrite doc/TASK_LEDGER.md")
    args = parser.parse_args()

    rows = collect()
    plan = plan_text()

    counts = Counter(row["status"] for row in rows)
    terminal = [r for r in rows if r["status"] in TERMINAL]
    non_terminal = [r for r in rows if r["status"] not in TERMINAL]

    for row in rows:
        # a plan node is one whose id appears as a table-row id, which is
        # stricter than 'the string occurs somewhere in the prose'
        # Three shapes occur in the plan: a bare row id (|ID|status|), a
        # spaced cell (| ID |), and an id embedded in a combined cell such as
        # |RUST-ENV-BASELINE-1（...）/ P07...|. All three mean "the plan names
        # this task"; only the first two mean "this is its own row".
        row["plan_row"] = ("|" + row["id"] + "|") in plan or (
            "| " + row["id"] + " |") in plan
        row["in_plan"] = row["plan_row"] or (row["id"] in plan)
    named_only = [r for r in non_terminal if r["in_plan"]]
    outside = [r for r in non_terminal if not r["in_plan"]]

    print("Task ledger (reproducible from doc/tasks/*.md)")
    print("  task files            : %d" % len(rows))
    print("  terminal              : %d" % len(terminal))
    print("  non-terminal          : %d" % len(non_terminal))
    own_row = [r for r in non_terminal if r.get("plan_row")]
    print("    own plan row        : %d" % len(own_row))
    print("    named anywhere      : %d" % len(named_only))
    print("    outside the plan    : %d" % len(outside))
    print("  by status:")
    for status, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        marker = " (terminal)" if status in TERMINAL else ""
        print("    %-24s %3d%s" % (status, count, marker))

    active = [r for r in non_terminal if r["status"] in ACTIVE_TRACES]
    if active:
        print("\n  %d task(s) in a state that implies activity or dispatchability:"
              % len(active))
        print("  (r38: none of these may be bulk-closed; each needs individual proof)")
        for row in sorted(active, key=lambda r: (r["status"], r["id"])):
            where = ("plan-row" if row.get("plan_row")
                     else "plan-mention" if row["in_plan"] else "outside")
            print("    %-24s %-46s %s" % (row["status"], row["id"], where))

    if args.diff:
        print("\n  non-terminal tasks outside the plan (%d):" % len(outside))
        for row in sorted(outside, key=lambda r: (r["status"], r["id"])):
            print("    %-24s %s" % (row["status"], row["id"]))

    if args.write:
        lines = [
            "# Task Ledger",
            "",
            "**Generated by `tools/governance/task_ledger.py --write`.** "
            "Do not edit by hand: rerun the script.",
            "",
            "Reconciliation of every `doc/tasks/*.md` against the plan's node set. "
            "r38 §3 established this as the audit layer, because 'READY is empty' "
            "and 'nothing is active' are claims about different sets and had been "
            "read as the same one.",
            "",
            "| metric | value |",
            "|---|---:|",
            "| task files | %d |" % len(rows),
            "| terminal | %d |" % len(terminal),
            "| non-terminal | %d |" % len(non_terminal),
            "| non-terminal named in the plan | %d |" % len(named_only),
            "| non-terminal outside the plan | %d |" % len(outside),
            "",
            "## By status",
            "",
            "| status | count | terminal |",
            "|---|---:|---|",
        ]
        for status, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
            lines.append("| `%s` | %d | %s |"
                         % (status, count, "yes" if status in TERMINAL else "no"))
        lines += ["", "## Non-terminal tasks", "",
                  "| task | status | in plan |", "|---|---|---|"]
        for row in sorted(non_terminal, key=lambda r: (r["status"], r["id"])):
            where = ("own row" if row.get("plan_row")
                     else "mentioned" if row["in_plan"] else "no")
            lines.append("| `%s` | `%s` | %s |"
                         % (row["id"], row["status"], where))
        lines += ["", "## What this ledger does not say", "",
                  "It does not say whether a non-terminal task is still being worked "
                  "on. r38 §2.3 ruled that a status field records lifecycle history and "
                  "cannot establish liveness either way, so no task here is marked "
                  "abandoned on the strength of its status alone.", ""]
        io.open(LEDGER, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
        print("\n  wrote %s" % os.path.relpath(LEDGER, REPO))

    return 0


if __name__ == "__main__":
    sys.exit(main())
