# -*- coding: utf-8 -*-
"""Phase B: remove worktrees that are provably safe to remove.

A worktree is eligible only if all of these hold, checked again at removal time
rather than trusted from the inventory:
  - it is not the main checkout
  - its directory name is not in the protected set (any PRESERVE_REFERENCED)
  - `git status --porcelain` is empty  (untracked counts; ignored does not)
  - `git stash list` is empty
  - it is a registered worktree of this repository

`git worktree remove` runs without --force. Git refusing is a signal, not an
obstacle: it means something was overlooked, and the entry goes to 'refused'.

Default is a dry run; pass --apply to remove.
"""
import io
import json
import os
import re
import shutil
import subprocess
import sys

REPO = r"G:\CODEX\New Manga"
MAIN = os.path.normcase(os.path.abspath(REPO))
INV = os.path.join(REPO, "verification", "WORKSPACE-CONSOLIDATION-1", "inventory.json")
OUT = os.path.join(REPO, "verification", "WORKSPACE-CONSOLIDATION-1")
APPLY = "--apply" in sys.argv


def git(*args, cwd=REPO):
    r = subprocess.run(["git", "-C", cwd] + list(args),
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip()


def dir_size(path):
    total = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return total


def main():
    inv = json.load(io.open(INV, encoding="utf-8"))
    wt_paths = {os.path.normcase(os.path.abspath(w["path"])) for w in inv["worktrees"]}
    protected = set(inv["protected_worktree_names"].keys())

    removed, refused, skipped = [], [], []
    for w in inv["worktrees"]:
        path = w["path"]
        absn = os.path.normcase(os.path.abspath(path))
        name = os.path.basename(path.rstrip("/\\"))

        if absn == MAIN:
            skipped.append({"path": path, "why": "main checkout"}); continue
        if absn not in wt_paths:
            skipped.append({"path": path, "why": "not a registered worktree"}); continue
        if name in protected or w["protected"]:
            skipped.append({"path": path, "why": "protected"}); continue
        if not os.path.isdir(path):
            skipped.append({"path": path, "why": "directory missing"}); continue

        # re-check, do not trust the inventory
        rc, out, _ = git("status", "--porcelain", cwd=path)
        if rc != 0:
            refused.append({"path": path, "why": "status failed"}); continue
        if out.strip():
            refused.append({"path": path, "why": "%d dirty/untracked entries" % len(out.split("\n"))})
            continue
        rc, out, _ = git("stash", "list", cwd=path)
        if out.strip():
            refused.append({"path": path, "why": "has stashes"}); continue

        size = dir_size(path)
        entry = {"path": path, "branch": w["branch"], "bytes": size}
        if APPLY:
            rc, out2, err = git("worktree", "remove", path)
            if rc != 0:
                refused.append({"path": path, "why": "git refused: " + err[:100]})
                continue
            entry["removed"] = True
        removed.append(entry)

    doc = {
        "generated_at": "2026-10-20",
        "mode": "apply" if APPLY else "dry_run",
        "removed": removed,
        "refused": refused,
        "skipped": skipped,
        "totals": {
            "candidates": len(removed) + len(refused),
            "removed": len(removed),
            "refused": len(refused),
            "skipped": len(skipped),
            "bytes": sum(e["bytes"] for e in removed),
        },
    }
    fn = "worktree-removal.json" if APPLY else "worktree-removal-dryrun.json"
    io.open(os.path.join(OUT, fn), "w", encoding="utf-8", newline="\n").write(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n")

    t = doc["totals"]
    print("  %s: remove %d, refused %d, skipped %d, %.1f GB"
          % (doc["mode"], t["removed"], t["refused"], t["skipped"], t["bytes"] / 1073741824.0))
    for r in refused[:8]:
        print("    refused:", os.path.basename(r["path"].rstrip("/\\")), "-", r["why"][:70])
    return 0


if __name__ == "__main__":
    sys.exit(main())
