#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Evidence-based liveness probe for non-terminal tasks.

r38 §2.3 ruled that a status field records lifecycle history and cannot
establish liveness, so the only honest way to say "this task is dead" is to look
at what the repository actually contains: its ACs, its delivery commits, whether
the things it wanted to change already are changed.

This does not decide. It assembles the evidence a human or Codex needs to decide,
and it refuses to output a verdict derived from status alone.

    python tools/governance/task_liveness.py
    python tools/governance/task_liveness.py --task P22
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


def git(*args: str) -> str:
    try:
        r = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=60)
        return (r.stdout or "").strip()
    except Exception:
        return ""


def frontmatter(text: str) -> dict:
    out = {}
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return out
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip().strip("\"'")
    return out


def ac_counts(text: str) -> tuple[int, int]:
    """(ticked, total) for lines that look like ACs."""
    ticked = total = 0
    for line in text.split("\n"):
        if re.match(r"^[ \t]*-[ \t]*\[[ xX]\][ \t]*\**AC", line):
            total += 1
            if re.match(r"^[ \t]*-[ \t]*\[[xX]\]", line):
                ticked += 1
    return ticked, total


def probe(path: str) -> dict:
    text = io.open(path, encoding="utf-8", errors="replace").read()
    meta = frontmatter(text)
    task_id = os.path.basename(path)[:-3]
    ticked, total = ac_counts(text)

    # A bare --grep matches the id anywhere in the message, including inside
    # another task's name or a passing mention ("release P04 after P22
    # convergence"). Count only commits that name this id at a message
    # boundary; the loose count overstated P22 by more than half.
    commits = git("log", "--all", "--oneline", "--grep", task_id, "-40")
    boundary = re.compile(
        r"(?:^|[\s(\[,;/])" + re.escape(task_id) + r"(?:[\s)\]):,;/]|$)")
    real = []
    for line in commits.split("\n"):
        if not line.strip():
            continue
        subject = line.split(" ", 1)[1] if " " in line else line
        if boundary.search(subject):
            real.append(line)
    n_commits = len(real)
    last_commit = real[0] if real else ""

    # does any non-terminal task mention it as a dependency
    dependents = []
    for other in glob.glob(os.path.join(TASKS_DIR, "*.md")):
        if other == path:
            continue
        otext = io.open(other, encoding="utf-8", errors="replace").read()
        ometa = frontmatter(otext)
        if ometa.get("status", "").lower() in TERMINAL:
            continue
        if re.search(r"depends_on:.*\b" + re.escape(task_id) + r"\b", otext):
            dependents.append(os.path.basename(other)[:-3])

    return {
        "id": task_id,
        "status": meta.get("status", "(none)"),
        "owner": meta.get("owner", "?"),
        "branch": meta.get("branch", ""),
        "integration_commit": meta.get("integration_commit", ""),
        "acs": (ticked, total),
        "commits": n_commits,
        "commits_loose": len([l for l in commits.split("\n") if l.strip()]),
        "last_commit": last_commit,
        "dependents": dependents,
    }


def classify(info: dict) -> tuple[str, str]:
    """Return (evidence_class, why). Neither is 'dead' - r38 forbids that leap."""
    ticked, total = info["acs"]
    if total and ticked == total:
        return ("all ACs ticked, status not updated",
                "every AC is ticked but the frontmatter still says %s - a closeout "
                "was likely never recorded" % info["status"])
    if total and ticked == 0 and info["commits"] == 0:
        return ("no visible work",
                "no ACs ticked and no commit mentions the id - but absence of commits "
                "is not proof of abandonment, only that this repository holds none")
    if info["commits"] > 0:
        return ("commits exist",
                "%d commit(s) mention the id; last %s" %
                (info["commits"], info["last_commit"] or "?"))
    return ("undetermined", "status is %s; nothing else in the repo settles it"
            % info["status"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", help="probe one task id")
    parser.add_argument("--all", action="store_true", help="include terminal tasks")
    args = parser.parse_args()

    paths = sorted(glob.glob(os.path.join(TASKS_DIR, "*.md")))
    rows = []
    for path in paths:
        if os.path.basename(path).lower() == "readme.md":
            continue
        info = probe(path)
        if not args.all and info["status"].lower() in TERMINAL:
            continue
        if args.task and info["id"] != args.task:
            continue
        rows.append(info)

    if args.task:
        for info in rows:
            print("task      : %s" % info["id"])
            print("status    : %s" % info["status"])
            print("owner     : %s" % info["owner"])
            print("branch    : %s" % (info["branch"] or "-"))
            print("ACs       : %d/%d ticked" % info["acs"])
            print("commits   : %d (loose grep: %d)"
                  % (info["commits"], info.get("commits_loose", 0)))
            print("last      : %s" % (info["last_commit"] or "-"))
            print("dependents: %s" % (", ".join(info["dependents"]) or "-"))
            cls, why = classify(info)
            print("evidence  : %s" % cls)
            print("            %s" % why)
        return 0

    print("Non-terminal task liveness evidence")
    print("(r38: status alone proves nothing; each row below is evidence, not a verdict)")
    print()
    buckets: dict[str, list[dict]] = {}
    for info in rows:
        cls, _ = classify(info)
        buckets.setdefault(cls, []).append(info)

    for cls in sorted(buckets, key=lambda c: -len(buckets[c])):
        members = buckets[cls]
        print("%s  (%d)" % (cls, len(members)))
        for info in sorted(members, key=lambda r: r["id"]):
            ticked, total = info["acs"]
            print("   %-46s %-18s AC %d/%d  commits %d"
                  % (info["id"], info["status"], ticked, total, info["commits"]))
        print()

    print("Nothing here is labelled abandoned. Deciding that requires either a")
    print("superseding task or an architecture ruling, per r38 §2 and §3.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
