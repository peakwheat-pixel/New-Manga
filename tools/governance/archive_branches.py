# -*- coding: utf-8 -*-
"""AC4: archive every unmerged branch before anything is deleted.

For each branch the mainline does not contain:
  git tag archive/<safe> <branch>              - keeps the tip addressable even
                                                 after the branch ref is gone
  git bundle create <dir>/<safe>.bundle <mainline>..<branch>
  git bundle verify <file>                     - and it must pass, or the branch
                                                 is not deletable

Bundles are incremental: their prerequisite is the mainline commit, which stays.
That keeps them small; a full bundle per branch would duplicate the repository
76 times.

Writes archive-manifest.json recording, per branch, the tip SHA, unique commit
count, bundle path, size and verification result. Anything that fails stays in
the 'failed' list and is excluded from deletion.
"""
import io
import json
import os
import subprocess
import sys

REPO = r"G:\CODEX\New Manga"
MAINLINE = "antigravity/P09-AC3-DELETE-HARDEN-1"
INV = os.path.join(REPO, "verification", "WORKSPACE-CONSOLIDATION-1", "inventory.json")
OUT = os.path.join(REPO, "verification", "WORKSPACE-CONSOLIDATION-1")
BUNDLES = r"G:\CODEX\New Manga.workspace\archive\bundles"


def git(*args, cwd=REPO):
    r = subprocess.run(["git", "-C", cwd] + list(args),
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip()


def safe(name):
    return name.replace("/", "_").replace("\\", "_")


def main():
    os.makedirs(BUNDLES, exist_ok=True)
    inv = json.load(io.open(INV, encoding="utf-8"))
    todo = [r for r in inv["branches"] if not r["merged"]]
    print("  unmerged branches to archive: %d" % len(todo))

    done, failed = [], []
    for i, r in enumerate(todo, 1):
        b = r["branch"]
        s = safe(b)
        _, tip, _ = git("rev-parse", b)
        if not tip:
            failed.append({"branch": b, "why": "rev-parse failed"})
            continue
        rc, _, err = git("tag", "-f", "archive/" + s, b)
        if rc != 0:
            failed.append({"branch": b, "why": "tag failed: " + err[:80]})
            continue
        bpath = os.path.join(BUNDLES, s + ".bundle")
        rc, _, err = git("bundle", "create", bpath, "%s..%s" % (MAINLINE, b))
        if rc != 0 or not os.path.isfile(bpath):
            failed.append({"branch": b, "why": "bundle failed: " + err[:80]})
            continue
        rc, vout, verr = git("bundle", "verify", bpath)
        size = os.path.getsize(bpath)
        entry = {
            "branch": b,
            "tag": "archive/" + s,
            "tip": tip,
            "unique_commits": r["unique_commits"],
            "bundle": bpath.replace(REPO, "<repo>"),
            "bundle_bytes": size,
            "verified": rc == 0,
            "verify_first_line": (vout or verr).split("\n")[0][:90],
        }
        if rc != 0:
            failed.append({"branch": b, "why": "bundle verify failed"})
        else:
            done.append(entry)
        if i % 10 == 0:
            print("    ... %d/%d" % (i, len(todo)))

    doc = {
        "generated_at": "2026-10-20",
        "mainline": MAINLINE,
        "bundles_dir": BUNDLES,
        "archived": done,
        "failed": failed,
        "totals": {
            "branches": len(todo),
            "archived_ok": len(done),
            "failed": len(failed),
            "bundle_bytes": sum(e["bundle_bytes"] for e in done),
            "unique_commits": sum(e["unique_commits"] or 0 for e in done),
        },
    }
    io.open(os.path.join(OUT, "archive-manifest.json"), "w", encoding="utf-8",
            newline="\n").write(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")

    t = doc["totals"]
    print("  archived ok   : %d" % t["archived_ok"])
    print("  failed        : %d" % t["failed"])
    print("  bundle bytes  : %.1f MB" % (t["bundle_bytes"] / 1048576.0))
    print("  unique commits covered: %d" % t["unique_commits"])
    for f in failed[:10]:
        print("    FAILED:", f["branch"], "-", f["why"][:70])
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
