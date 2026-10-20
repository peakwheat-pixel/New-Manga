# -*- coding: utf-8 -*-
"""Phase C: release disk held by derived, regenerable workspace areas.

Only four named areas are considered, and only because they are derived by
construction: review scratch space, build output, temp, tmp.

Two things are deliberately excluded from the analysis:

  workspace/worktrees   - holds the PRESERVE_REFERENCED recovery points.
                          node_modules inside them is not ours to reclaim.
  workspace/task-envs   - small, and it contains the venv that makes the
                          manga detection chain work. Deleting it would undo
                          M2-PROD-DETECT-ENV-1 while looking like cleanup.

Protection rule: a child directory is skipped entirely if any evidence-pinned
path falls inside it. Pins are recomputed from tracked task files and resource
manifests, not from prose mentions - a path merely named in a paragraph is not a
pin, and treating it as one would block every cleanup forever.

Default is a dry run.
"""
import io
import json
import os
import re
import shutil
import subprocess
import sys

REPO = r"G:\CODEX\New Manga"
WS = r"G:\CODEX\New Manga.workspace"
OUT = os.path.join(REPO, "verification", "WORKSPACE-CONSOLIDATION-1")
APPLY = "--apply" in sys.argv

ROOTS = [
    ("review-scratch", os.path.join(WS, "review-scratch")),
    ("builds", os.path.join(WS, "builds")),
    ("temp", os.path.join(WS, "temp")),
    ("tmp", os.path.join(WS, "tmp")),
]


def sect(t, name):
    m = re.search(r"(?m)^##\s+" + re.escape(name) + r"\s*$", t)
    if not m:
        return ""
    rest = t[m.end():]
    n = re.search(r"(?m)^##\s", rest)
    return rest[:n.start()] if n else rest


def pinned_paths():
    tracked = subprocess.run(
        ["git", "-C", REPO, "ls-files", "--", "doc/tasks", "verification"],
        capture_output=True, text=True, encoding="utf-8").stdout.split("\n")
    out = set()
    for f in tracked:
        f = f.strip()
        if not f or f.startswith(".agents/") or not f.endswith((".md", ".json")):
            continue
        p = os.path.join(REPO, f.replace("/", os.sep))
        if not os.path.isfile(p):
            continue
        try:
            t = io.open(p, encoding="utf-8", errors="ignore").read().replace("\r\n", "\n")
        except Exception:
            continue
        for block in (sect(t, "Canonical Evidence"), sect(t, "Resource Manifest")):
            for cell in re.findall(r"`([^`]+)`", block):
                out.add(cell.strip().replace("\\", "/"))
        if f.endswith(".json"):
            try:
                d = json.loads(t)
                if isinstance(d, dict):
                    for r in (d.get("resources") or []):
                        if isinstance(r, dict):
                            for k in ("source_path", "destination_path"):
                                if r.get(k):
                                    out.add(str(r[k]).replace("\\", "/"))
            except Exception:
                pass
    return out


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
    pins = pinned_paths()
    print("  evidence-pinned paths: %d" % len(pins))

    removed, kept = [], []
    for label, root in ROOTS:
        if not os.path.isdir(root):
            print("  %-16s (absent)" % label)
            continue
        for child in sorted(os.listdir(root)):
            cpath = os.path.join(root, child)
            cposix = cpath.replace("\\", "/")
            size = dir_size(cpath) if os.path.isdir(cpath) else os.path.getsize(cpath)
            hit = [p for p in pins if p.startswith(cposix + "/") or p == cposix]
            if hit:
                kept.append({"area": label, "path": cposix, "bytes": size,
                             "why": "pinned: " + hit[0][-70:]})
                continue
            entry = {"area": label, "path": cposix, "bytes": size}
            if APPLY:
                try:
                    if os.path.isdir(cpath):
                        shutil.rmtree(cpath)
                    else:
                        os.remove(cpath)
                except OSError as e:
                    kept.append({"area": label, "path": cposix, "bytes": size,
                                 "why": "delete failed: " + str(e)[:60]})
                    continue
            removed.append(entry)

    doc = {
        "generated_at": "2026-10-20",
        "mode": "apply" if APPLY else "dry_run",
        "removed": removed,
        "kept": kept,
        "totals": {
            "removed_items": len(removed),
            "removed_bytes": sum(e["bytes"] for e in removed),
            "kept_items": len(kept),
            "kept_bytes": sum(e["bytes"] for e in kept),
        },
    }
    fn = "workspace-cleanup.json" if APPLY else "workspace-cleanup-dryrun.json"
    io.open(os.path.join(OUT, fn), "w", encoding="utf-8", newline="\n").write(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n")

    t = doc["totals"]
    print("  %s: remove %d item(s) / %.2f GB ; keep %d item(s) / %.2f GB"
          % (doc["mode"], t["removed_items"], t["removed_bytes"] / 1073741824.0,
             t["kept_items"], t["kept_bytes"] / 1073741824.0))
    for k in kept[:8]:
        print("    keep %-14s %-46s %s"
              % (k["area"], os.path.basename(k["path"])[:46], k["why"][:46]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
