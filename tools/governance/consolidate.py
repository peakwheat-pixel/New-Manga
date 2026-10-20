# -*- coding: utf-8 -*-
"""AC1: build the four inventory tables for WORKSPACE-CONSOLIDATION-1.

Read-only. Writes inventory.json + inventory.md into the task's evidence_dir.

Branch table per branch: merged into mainline? how many commits it has that the
mainline does not? when was its tip? is a worktree currently checked out on it?
No sampling - all 418 are measured.
"""
import io
import json
import os
import re
import subprocess
import sys

REPO = r"G:\CODEX\New Manga"
WS = r"G:\CODEX\New Manga.workspace"
OUT = os.path.join(REPO, "verification", "WORKSPACE-CONSOLIDATION-1")
MAINLINE = "antigravity/P09-AC3-DELETE-HARDEN-1"


def git(*args):
    r = subprocess.run(["git", "-C", REPO] + list(args),
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout.strip() if r.returncode == 0 else ""


def branches():
    out = git("for-each-ref", "--format=%(refname:short)", "refs/heads")
    return [b for b in out.split("\n") if b.strip()]


def merged_set():
    out = git("branch", "--merged", MAINLINE, "--format=%(refname:short)")
    return set(b for b in out.split("\n") if b.strip())


def worktrees():
    """Parse `git worktree list --porcelain` into structured entries."""
    out = git("worktree", "list", "--porcelain")
    entries, cur = [], {}
    for line in out.split("\n"):
        if line.startswith("worktree "):
            if cur:
                entries.append(cur)
            cur = {"path": line[len("worktree "):], "branch": "", "head": ""}
        elif line.startswith("HEAD "):
            cur["head"] = line[5:].strip()
        elif line.startswith("branch "):
            ref = line[len("branch "):].strip()
            cur["branch"] = ref[len("refs/heads/"):] if ref.startswith("refs/heads/") else ref
        elif line.strip() == "detached":
            cur["branch"] = "(detached)"
    if cur:
        entries.append(cur)
    return entries


def section(text, name):
    m = re.search(r"(?m)^##\s+" + re.escape(name) + r"\s*$", text)
    if not m:
        return ""
    rest = text[m.end():]
    n = re.search(r"(?m)^##\s", rest)
    return rest[:n.start()] if n else rest


def protected_worktrees():
    """Worktree names any resource record says must be preserved."""
    keep = {}
    vdir = os.path.join(REPO, "verification")
    for root, dirs, files in os.walk(vdir):
        dirs[:] = [d for d in dirs if d != ".git"]
        for fn in files:
            if not fn.lower().endswith(".json"):
                continue
            fp = os.path.join(root, fn)
            try:
                d = json.load(io.open(fp, encoding="utf-8"))
            except Exception:
                continue
            if not isinstance(d, dict):
                continue
            for r in (d.get("resources") or []):
                if not isinstance(r, dict) or r.get("disposition") != "PRESERVE_REFERENCED":
                    continue
                p = (r.get("source_path") or "").replace("\\", "/")
                m = re.search(r"/worktrees/([^/]+)", p)
                if m:
                    keep.setdefault(m.group(1), []).append(
                        os.path.relpath(fp, REPO).replace("\\", "/"))
    # task resource tables
    tdir = os.path.join(REPO, "doc", "tasks")
    for fn in os.listdir(tdir):
        if not fn.endswith(".md"):
            continue
        t = io.open(os.path.join(tdir, fn), encoding="utf-8", errors="replace").read()
        for m in re.finditer(r"worktrees/([A-Za-z0-9._-]+)[^\n|]*\|[^\n|]*PRESERVE_REFERENCED", t):
            keep.setdefault(m.group(1), []).append("doc/tasks/" + fn)
    return keep


def main():
    if not os.path.isdir(OUT):
        os.makedirs(OUT, exist_ok=True)

    bl = branches()
    merged = merged_set()
    wts = worktrees()
    by_branch = {}
    for w in wts:
        by_branch.setdefault(w["branch"], []).append(w["path"])
    keep = protected_worktrees()

    rows = []
    for b in bl:
        uniq = git("rev-list", "--count", "%s..%s" % (MAINLINE, b))
        when = git("log", "-1", "--format=%cs", b)
        rows.append({
            "branch": b,
            "merged": b in merged,
            "unique_commits": int(uniq) if uniq.isdigit() else None,
            "tip_date": when,
            "checked_out_at": by_branch.get(b, []),
            "is_mainline": b == MAINLINE,
        })

    wrows = []
    for w in wts:
        p = w["path"]
        st = subprocess.run(["git", "-C", p, "status", "--porcelain"],
                            capture_output=True, text=True, encoding="utf-8",
                            errors="replace") if os.path.isdir(p) else None
        dirty = len([l for l in (st.stdout or "").split("\n") if l.strip()]) if st else None
        stash = subprocess.run(["git", "-C", p, "stash", "list"],
                               capture_output=True, text=True, encoding="utf-8",
                               errors="replace") if os.path.isdir(p) else None
        stashes = len([l for l in (stash.stdout or "").split("\n") if l.strip()]) if stash else None
        name = os.path.basename(p.rstrip("/\\"))
        # workspace worktree dir name is the task id; .codex ones use a different scheme
        prot = keep.get(name)
        wrows.append({
            "path": p,
            "branch": w["branch"],
            "head": w["head"][:9],
            "exists": os.path.isdir(p),
            "dirty_entries": dirty,
            "stashes": stashes,
            "protected": sorted(prot) if prot else [],
        })

    doc = {
        "generated_at": "2026-10-20",
        "mainline": MAINLINE,
        "head": git("rev-parse", "HEAD"),
        "counts": {
            "branches": len(rows),
            "merged": sum(1 for r in rows if r["merged"]),
            "unmerged": sum(1 for r in rows if not r["merged"]),
            "worktrees": len(wrows),
            "protected_worktree_names": len(keep),
        },
        "branches": rows,
        "worktrees": wrows,
        "protected_worktree_names": {k: sorted(set(v)) for k, v in sorted(keep.items())},
    }
    io.open(os.path.join(OUT, "inventory.json"), "w", encoding="utf-8",
            newline="\n").write(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")

    # markdown summary
    un = [r for r in rows if not r["merged"]]
    un_sorted = sorted(un, key=lambda r: (-(r["unique_commits"] or 0), r["branch"]))
    prot_in_wt = [w for w in wrows if w["protected"]]
    live_clean = [w for w in wrows if not w["protected"] and w["dirty_entries"] == 0
                  and w["stashes"] == 0]
    lines = [
        "# 工作区整理盘点（AC1 四表）",
        "",
        "生成：`tools/governance/consolidate.py`（只读），2026-10-20。",
        "主 checkout：`%s`，HEAD `%s`，主线 `%s`。"
        % (REPO, doc["head"][:9], MAINLINE),
        "",
        "## 一、总量",
        "",
        "| 项 | 数 |",
        "|---|---:|",
        "| 本地分支 | **%d** |" % len(rows),
        "| 已并入主线 | %d |" % doc["counts"]["merged"],
        "| **未并入主线** | **%d** |" % doc["counts"]["unmerged"],
        "| 已注册 worktree | **%d** |" % len(wrows),
        "| 受保护 worktree 名 | **%d** |" % len(keep),
        "| 受保护且在注册表中 | %d |" % len(prot_in_wt),
        "| 非保护且干净无 stash | %d |" % len(live_clean),
        "",
        "## 二、分支表（未并入主线的 %d 条，按独有提交数降序）" % len(un),
        "",
        "| 分支 | 独有提交 | tip 日期 | worktree 检出 |",
        "|---|---:|---|---|",
    ]
    for r in un_sorted:
        co = ", ".join(os.path.basename(p.rstrip("/\\")) for p in r["checked_out_at"]) or "—"
        lines.append("| `%s` | %s | %s | %s |"
                     % (r["branch"], r["unique_commits"], r["tip_date"], co))
    lines += ["", "## 三、worktree 表（受保护者）", "",
              "| 路径 | 分支 | 保护来源数 |", "|---|---|---:|"]
    for w in sorted(prot_in_wt, key=lambda w: w["path"]):
        lines.append("| `%s` | `%s` | %d |"
                     % (w["path"].replace(REPO, "<repo>"), w["branch"], len(w["protected"])))
    lines += ["", "## 四、可清理候选（非保护 且 干净 且 无 stash）", "",
              "| 路径 | 分支 | 脏条目 | stash |", "|---|---|---:|---:|"]
    for w in sorted(live_clean, key=lambda w: w["path"]):
        lines.append("| `%s` | `%s` | 0 | 0 |"
                     % (w["path"].replace(REPO, "<repo>"), w["branch"]))
    lines += ["", "## 五、带改动因而不得清理的 worktree", "",
              "| 路径 | 分支 | 脏条目 | stash | protected |", "|---|---|---:|---:|---|"]
    for w in sorted([x for x in wrows if x["dirty_entries"] or x["stashes"]],
                    key=lambda w: -(w["dirty_entries"] or 0)):
        lines.append("| `%s` | `%s` | %s | %s | %s |"
                     % (w["path"].replace(REPO, "<repo>"), w["branch"],
                        w["dirty_entries"], w["stashes"], "yes" if w["protected"] else "no"))
    io.open(os.path.join(OUT, "inventory.md"), "w", encoding="utf-8",
            newline="\n").write("\n".join(lines) + "\n")

    print("  branches: %d  (merged %d / unmerged %d)"
          % (len(rows), doc["counts"]["merged"], doc["counts"]["unmerged"]))
    print("  worktrees: %d  protected %d" % (len(wrows), len(keep)))
    print("  protected present in registry: %d" % len(prot_in_wt))
    print("  clean+unprotected candidates : %d" % len(live_clean))
    print("  dirty/stashed worktrees      : %d"
          % len([x for x in wrows if x["dirty_entries"] or x["stashes"]]))
    print("  wrote inventory.json + inventory.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
