#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Evidence probe for non-terminal tasks - SIGNALS ONLY, no conclusions.

Rewritten after r39. The previous version had a structural bug that produced a
task which did not exist: frontmatter() read only the first --- block while
ac_counts() scanned the whole file, so a task that had been rewritten (old
proposal header above, new AC set below) was reported as '8 of 8 ACs done, no
owner' - a single record stitched from two. r39 also demoted 'all ACs ticked'
from a workability ranking to an unchecked signal.

So this version emits four independent signal groups and no classification:

  A. record structure      - is this even one coherent record?
  B. AC evidence trace     - do the ACs point at anything checkable?
  C. explicit conflicts    - does the text say finished and unfinished at once?
  D. integration cross-ref - does the named commit exist and is it reachable?

A row with conflicts in group A is not evidence about the task at all; it is
evidence about the file. Both are worth knowing, but they are not the same
thing and are never averaged together.

    python tools/governance/task_liveness.py
    python tools/governance/task_liveness.py --task M2-TA2B
    python tools/governance/task_liveness.py --unreadable   # only group A failures
"""
from __future__ import annotations

import argparse
import glob
import io
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TASKS_DIR = os.path.join(REPO, "doc", "tasks")
TERMINAL = {"done", "closed_with_limitations", "cancelled", "superseded", "historical"}

#: words that, appearing in an AC line next to a tick, mean the AC contradicts
#: itself. Kept deliberately small: this flags for a human, it does not judge.
UNFINISHED_MARKERS = [
    "待跑", "待人工", "待补", "待确认", "未运行", "未做", "尚未", "TODO", "pending",
    "not run", "not yet", "待执行", "待复核", "未验证", "BLOCKED",
]


def git(*args: str) -> str:
    try:
        r = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=60)
        return (r.stdout or "").strip()
    except Exception:
        return ""


def split_frontmatter(text: str) -> tuple[dict, str, int]:
    """Return (frontmatter, body, number_of_frontmatter_blocks_seen).

    The block count is the point. A file with two front-matter blocks is either a
    rewritten task or a malformed one, and either way the probe must say so
    rather than silently using the first and then reading ACs from everything
    below it - which is exactly what produced a phantom task.
    """
    meta: dict[str, str] = {}
    blocks = 0
    lines = text.split("\n")
    i = 0
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    if i < len(lines) and lines[i].strip() == "---":
        start = i + 1
        for j in range(start, len(lines)):
            if lines[j].strip() == "---":
                blocks += 1
                for line in lines[start:j]:
                    if ":" in line:
                        k, v = line.split(":", 1)
                        meta[k.strip()] = v.strip().strip("\"'")
                i = j + 1
                break
        else:
            return {}, text, 0
    body = "\n".join(lines[i:])
    # a second YAML-looking block below is a structural problem, not a rule line
    for _ in re.finditer(r"(?m)^---\s*\n((?:[A-Za-z_][\w-]*:[^\n]*\n)+)---\s*$", body):
        blocks += 1
    return meta, body, blocks


def ac_lines(body: str) -> list[tuple[int, bool, str]]:
    """(line_number, ticked, text) for AC lines in the body only."""
    out = []
    for n, line in enumerate(body.split("\n"), 1):
        m = re.match(r"^[ \t]*-[ \t]*\[([ xX])\][ \t]*\**AC", line)
        if m:
            out.append((n, m.group(1).lower() == "x", line.strip()))
    return out


def signal_structure(path: str, meta: dict, blocks: int) -> list[str]:
    """A. Is this one coherent record?"""
    problems = []
    if blocks == 0:
        problems.append("no front matter")
    elif blocks > 1:
        problems.append("%d front-matter blocks - file was likely rewritten; "
                        "metadata and ACs may belong to different versions" % blocks)
    if "status" not in meta:
        problems.append("front matter has no status")
    if "id" in meta and os.path.basename(path)[:-3] != meta["id"]:
        problems.append("front-matter id %r does not match the file name" % meta["id"])
    return problems


def signal_ac_evidence(acs: list[tuple[int, bool, str]]) -> list[str]:
    """B. Do the ticked ACs point at anything checkable? Paths only."""
    notes = []
    for n, ticked, line in acs:
        if not ticked:
            continue
        if not re.search(r"(?:verification|tests|src|doc)/[\w./-]+", line):
            notes.append("L%d ticked but names no repository path" % n)
    return notes


def signal_conflicts(acs: list[tuple[int, bool, str]]) -> list[str]:
    """C. Does the AC say finished and unfinished in the same line?"""
    found = []
    for n, ticked, line in acs:
        if not ticked:
            continue
        lowered = line.lower()
        for marker in UNFINISHED_MARKERS:
            if marker.lower() in lowered:
                found.append("L%d ticked but contains %r: %s"
                             % (n, marker, line[:110]))
                break
    return found


def signal_integration(meta: dict) -> list[str]:
    """D. Does the named commit exist and can it be reached?"""
    notes = []
    commit = meta.get("integration_commit", "").strip()
    # YAML spells absence as null / ~ / "" - that is "not set yet", which is a
    # normal state for a non-terminal task, not a defect. Reporting it as a
    # malformed hash produced 30 false positives on the first run.
    if not commit or commit.lower() in {"null", "~", "none", '""', "''"}:
        return notes
    if not re.fullmatch(r"[0-9a-fA-F]{7,40}", commit):
        notes.append("integration_commit %r is not a hash" % commit)
        return notes
    if subprocess.run(["git", "cat-file", "-e", commit + "^{commit}"],
                      cwd=REPO, capture_output=True).returncode != 0:
        notes.append("integration_commit %s does not exist here" % commit)
        return notes
    for ref in ("antigravity/P09-AC3-DELETE-HARDEN-1", "HEAD"):
        if subprocess.run(["git", "merge-base", "--is-ancestor", commit, ref],
                          cwd=REPO, capture_output=True).returncode == 0:
            notes.append("integration_commit %s reachable from %s" % (commit, ref))
            return notes
    notes.append("integration_commit %s exists but is not an ancestor of mainline" % commit)
    return notes


def probe(path: str) -> dict:
    text = io.open(path, encoding="utf-8", errors="replace").read()
    meta, body, blocks = split_frontmatter(text)
    acs = ac_lines(body)
    ticked = sum(1 for _, t, _ in acs if t)
    return {
        "id": os.path.basename(path)[:-3],
        "status": meta.get("status", "(none)"),
        "blocks": blocks,
        "acs": (ticked, len(acs)),
        "A_structure": signal_structure(path, meta, blocks),
        "B_evidence": signal_ac_evidence(acs),
        "C_conflicts": signal_conflicts(acs),
        "D_integration": signal_integration(meta),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", help="probe one task id")
    parser.add_argument("--unreadable", action="store_true",
                        help="only tasks whose record structure is broken")
    parser.add_argument("--all", action="store_true", help="include terminal tasks")
    args = parser.parse_args()

    rows = []
    for path in sorted(glob.glob(os.path.join(TASKS_DIR, "*.md"))):
        if os.path.basename(path).lower() == "readme.md":
            continue
        info = probe(path)
        if not args.all and info["status"].lower() in TERMINAL:
            continue
        if args.task and info["id"] != args.task:
            continue
        if args.unreadable and not info["A_structure"]:
            continue
        rows.append(info)

    if args.task:
        for info in rows:
            ticked, total = info["acs"]
            print("task      : %s" % info["id"])
            print("status    : %s" % info["status"])
            print("ACs ticked: %d/%d   (a count, not a conclusion - r39)" % (ticked, total))
            for group, key in (("A record structure", "A_structure"),
                               ("B AC evidence", "B_evidence"),
                               ("C explicit conflicts", "C_conflicts"),
                               ("D integration", "D_integration")):
                items = info[key]
                print("%s:" % group)
                if not items:
                    print("    (no signal)")
                for item in items:
                    print("    %s" % item)
        return 0

    print("Non-terminal task signals - four independent groups, no conclusion")
    print()

    broken = [r for r in rows if r["A_structure"]]
    conflicts = [r for r in rows if r["C_conflicts"]]
    no_evidence = [r for r in rows if r["B_evidence"]]
    unreachable = [r for r in rows if any(
        "not an ancestor" in x or "does not exist" in x or "not a hash" in x
        for x in r["D_integration"])]

    print("A. record structure broken      : %d" % len(broken))
    for r in broken:
        print("   %-46s %s" % (r["id"], "; ".join(r["A_structure"])[:100]))
    print()
    print("C. ticked AC contradicts itself : %d" % len(conflicts))
    for r in conflicts:
        print("   %-46s %s" % (r["id"], r["C_conflicts"][0][:100]))
    print()
    print("B. ticked AC names no repo path : %d" % len(no_evidence))
    print("D. integration commit suspect   : %d" % len(unreachable))
    for r in unreachable:
        print("   %-46s %s" % (r["id"], "; ".join(r["D_integration"])[:100]))
    print()
    print("%d non-terminal task(s) total." % len(rows))
    print()
    print("Nothing above is a verdict. r39: 'all ACs ticked' is a signal to")
    print("check, not a ranking; a group-A failure means the file is not one")
    print("coherent record, so its ACs say nothing about any single task.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
