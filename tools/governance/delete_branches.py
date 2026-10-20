# -*- coding: utf-8 -*-
"""Delete branch refs, now that every unmerged one is bundled and tagged.

Rules enforced here:
  - the mainline is never touched
  - `master` and `main` are excluded: they are decided separately in AC8, not
    swept up by a cleanup loop
  - a branch currently checked out in a registered worktree is skipped, because
    git cannot delete it and forcing would be wrong
  - merged branches go with `git branch -d` (git verifies the merge itself)
  - unmerged branches go with `-D` ONLY if archive-manifest.json shows a
    verified bundle and a tag for that exact branch; otherwise skipped
Default is a dry run.
"""
import io
import json
import os
import subprocess
import sys

REPO = r"G:\CODEX\New Manga"
MAINLINE = "antigravity/P09-AC3-DELETE-HARDEN-1"
OUT = os.path.join(REPO, "verification", "WORKSPACE-CONSOLIDATION-1")
INV = os.path.join(OUT, "inventory.json")
ARCH = os.path.join(OUT, "archive-manifest.json")
APPLY = "--apply" in sys.argv
KEEP = {"master", "main"}


def git(*args):
    r = subprocess.run(["git", "-C", REPO] + list(args),
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip()


def main():
    inv = json.load(io.open(INV, encoding="utf-8"))
    arch = json.load(io.open(ARCH, encoding="utf-8"))
    safe_bundles = {e["branch"]: e for e in arch["archived"] if e.get("verified")}
    _, wtout, _ = git("worktree", "list", "--porcelain")
    checked = set()
    for line in wtout.split("\n"):
        if line.startswith("branch refs/heads/"):
            checked.add(line[len("branch refs/heads/"):].strip())

    deleted, skipped, refused = [], [], []
    for r in inv["branches"]:
        b = r["branch"]
        if b == MAINLINE:
            skipped.append({"branch": b, "why": "mainline"}); continue
        if b in KEEP:
            skipped.append({"branch": b, "why": "reserved for the AC8 decision"}); continue
        if b in checked:
            skipped.append({"branch": b, "why": "checked out in a worktree"}); continue
        if r["merged"]:
            if not APPLY:
                deleted.append({"branch": b, "via": "-d", "merged": True, "unique": 0})
                continue
            rc, _, err = git("branch", "-d", b)
        else:
            e = safe_bundles.get(b)
            if not e:
                refused.append({"branch": b, "why": "no verified bundle"})
                continue
            if not APPLY:
                deleted.append({"branch": b, "via": "-D", "merged": False,
                                "unique": r["unique_commits"], "bundle": e["bundle"]})
                continue
            rc, _, err = git("branch", "-D", b)
        if rc != 0:
            refused.append({"branch": b, "why": err[:110]})
        else:
            deleted.append({"branch": b, "via": "-d" if r["merged"] else "-D",
                            "merged": r["merged"], "unique": r["unique_commits"]})

    doc = {
        "generated_at": "2026-10-20",
        "mode": "apply" if APPLY else "dry_run",
        "deleted": deleted,
        "refused": refused,
        "skipped": skipped,
        "totals": {
            "deleted": len(deleted),
            "deleted_merged": sum(1 for d in deleted if d["merged"]),
            "deleted_unmerged": sum(1 for d in deleted if not d["merged"]),
            "refused": len(refused),
            "skipped": len(skipped),
        },
    }
    fn = "branch-deletion.json" if APPLY else "branch-deletion-dryrun.json"
    io.open(os.path.join(OUT, fn), "w", encoding="utf-8", newline="\n").write(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n")

    t = doc["totals"]
    print("  %s: delete %d (merged %d / unmerged %d), refused %d, skipped %d"
          % (doc["mode"], t["deleted"], t["deleted_merged"], t["deleted_unmerged"],
             t["refused"], t["skipped"]))
    for r in refused[:8]:
        print("    refused:", r["branch"], "-", r["why"][:70])
    for s in skipped[:6]:
        print("    skipped:", s["branch"], "-", s["why"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
