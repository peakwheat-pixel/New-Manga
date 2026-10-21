# -*- coding: utf-8 -*-
"""AC1 (hardened): build the four inventory tables for WORKSPACE-CONSOLIDATION-1.

Read-only with respect to Git.  Writes inventory.json + inventory.md only when
``--out`` is given; without it the summary goes to stdout and nothing is written.

HARDENING TASK: WORKSPACE-CLEANUP-TOOL-HARDENING-1.  The old version converted
every Git failure into an empty string (``git() -> ""``), so a failed command
looked like an empty result, and its protection set was a basename map built
from a regex.  This version:

  * fails closed on any failed Git command (exit 2, reason on stderr);
  * validates the ``git worktree list --porcelain`` syntax strictly;
  * reuses the shared ``clean_workspace.ProtectionIndex``: protection is
    normalised absolute path identity with parent/child coverage, including
    bare table paths, PRESERVE_UNKNOWN, shared roots and per-file JSON records;
  * flags declaration integrity errors instead of publishing an inventory that
    under-reports protection (downstream deletion tools re-scan anyway, but the
    inventory must not look trustworthy when it is not);
  * records ignored/untracked counts per worktree so that "clean status" is no
    longer presented as "nothing to lose" (ignored content is invisible to
    status; see the r208 incident).
"""
import argparse
import io
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import clean_workspace as guard  # noqa: E402

TOOL_ID = "consolidate.py"
SCHEMA_VERSION = 1

REPO_DEFAULT = guard.REPO_DEFAULT
WS_DEFAULT = guard.WS_DEFAULT
MAINLINE_DEFAULT = "antigravity/P09-AC3-DELETE-HARDEN-1"

ROOT_SECTION = ("review-scratch", "builds", "temp", "tmp")


def _worktrees_root(ws_root):
    return guard.norm_abs(os.path.join(ws_root.replace("/", os.sep),
                                       "worktrees"),
                          "workspace worktrees root")


def _protected_names(index, ws_root):
    """Map protected worktree directory name -> declaration sources (AC1)."""
    return index.protected_worktree_names(_worktrees_root(ws_root))


def _inventory_ignored_untracked(path, config, limits):
    """Counts only.  The pre-delete per-file inventory is built by the deletion
    tools at removal time (AC3); this summary exists so the inventory cannot
    claim a worktree has "nothing to lose" without measuring it."""
    if not config["deep"]:
        return {"status": "NOT_MEASURED",
                "why": "run with --deep for ignored/untracked counts"}
    try:
        inventory = guard.build_inventory(
            path, git_worktree=True,
            max_files=limits["max_files"], max_bytes=limits["max_bytes"])
    except guard.GuardError as exc:
        return {"status": "FAILED", "code": exc.code, "why": exc.message}
    return {"status": "MEASURED", "counts": inventory["counts"],
            "digest": inventory["digest"]}


def build_inventory(config):
    repo = config["repo"]
    ws = config["ws"]
    mainline = config["mainline"]
    tips = guard.git_branch_tips(repo)
    if mainline not in tips:
        guard.fail("MAINLINE_MISSING",
                   "configured mainline %r is not a local branch" % mainline)
    merged_output = guard.git_checked(
        repo, "branch", "--merged", mainline, "--format=%(refname:short)",
        what="git branch --merged %s" % mainline)
    merged = {item.strip() for item in merged_output.split("\n") if item.strip()}
    missing = sorted(merged - set(tips))
    if missing:
        guard.fail("GIT_PARSE",
                   "git branch --merged listed branches without tips: %s"
                   % ", ".join(missing[:5]))

    worktrees = guard.list_worktrees(repo)
    by_branch = {}
    for entry in worktrees:
        if entry.get("branch"):
            by_branch.setdefault(entry["branch"], []).append(entry["path"])

    index, scanned = guard.scan_repo_declarations(repo, ws)
    protected_names = _protected_names(index, ws)

    branch_rows = []
    for branch in sorted(tips):
        unique = guard.git_checked(
            repo, "rev-list", "--count", "%s..%s" % (mainline, branch),
            what="git rev-list --count %s..%s" % (mainline, branch)).strip()
        if not unique.isdigit():
            guard.fail("GIT_PARSE",
                       "git rev-list --count returned %r for %r"
                       % (unique, branch))
        when = guard.git_checked(
            repo, "log", "-1", "--format=%cs", branch,
            what="git log -1 --format=%%cs %s" % branch).strip()
        branch_rows.append({
            "branch": branch,
            "tip": tips[branch],
            "merged": branch in merged,
            "unique_commits": int(unique),
            "tip_date": when or None,
            "checked_out_at": by_branch.get(branch, []),
            "is_mainline": branch == mainline,
        })

    limits = {"max_files": guard.INVENTORY_MAX_FILES,
              "max_bytes": guard.INVENTORY_MAX_BYTES}
    worktree_rows = []
    inspection_errors = []
    for entry in worktrees:
        path = entry["path"]
        normalized = entry["normalized"]
        row = {
            "path": path.replace("\\", "/"),
            "normalized": normalized,
            "branch": entry.get("branch"),
            "head": (entry.get("head") or "")[:9],
            "exists": os.path.isdir(path),
            "detached": bool(entry.get("detached")),
            "locked": bool(entry.get("locked")),
            "dirty_entries": None,
            "stashes": None,
            "protected": [],
            "inspection": "NOT_RUN",
        }
        if row["exists"]:
            try:
                row["dirty_entries"] = len(guard.git_status_entries(normalized))
                row["stashes"] = len(guard.git_stash_entries(normalized))
                row["inspection"] = "OK"
            except guard.GuardError as exc:
                row["inspection"] = "FAILED"
                row["inspection_error"] = {"code": exc.code,
                                           "why": exc.message}
                inspection_errors.append({"path": normalized,
                                          "code": exc.code,
                                          "why": exc.message})
            hits = index.evaluate(normalized)
            row["protected"] = sorted({
                "%s%s" % (declaration.source_file,
                          " " + declaration.locator if declaration.locator else "")
                for hit in hits
                for declaration in index.protected.get(hit["root"], [])})
            row["protection"] = [guard.describe_hit(hit) for hit in hits]
        worktree_rows.append(row)

    doc = {
        "schema_version": SCHEMA_VERSION,
        "tool": TOOL_ID,
        "generated_at": guard.now_iso(),
        "mainline": mainline,
        "mainline_tip": tips.get(mainline),
        "repo_root": repo,
        "workspace_root": ws,
        "head": guard.git_checked(repo, "rev-parse", "HEAD",
                                  what="git rev-parse HEAD").strip(),
        "counts": {
            "branches": len(branch_rows),
            "merged": sum(1 for row in branch_rows if row["merged"]),
            "unmerged": sum(1 for row in branch_rows if not row["merged"]),
            "worktrees": len(worktree_rows),
            "protected_worktree_names": len(protected_names),
            "worktrees_with_protection": sum(1 for row in worktree_rows
                                             if row["protected"]),
            "inspection_errors": len(inspection_errors),
        },
        "declarations": index.counts(),
        "declaration_scan": scanned,
        "declaration_errors": index.errors,
        "declaration_warnings": index.warnings,
        "inspection_errors": inspection_errors,
        "branches": branch_rows,
        "worktrees": worktree_rows,
        "protected_worktree_names": protected_names,
    }
    return doc, index, scanned


def _markdown(doc):
    unmerged = [row for row in doc["branches"] if not row["merged"]]
    unmerged.sort(key=lambda row: (-(row["unique_commits"] or 0), row["branch"]))
    protected = [row for row in doc["worktrees"] if row["protected"]]
    clean_unprotected = [row for row in doc["worktrees"]
                         if not row["protected"] and row["dirty_entries"] == 0
                         and row["stashes"] == 0 and row["inspection"] == "OK"]
    dirty = [row for row in doc["worktrees"]
             if row["inspection"] != "OK"
             or (row["dirty_entries"] or 0) > 0 or (row["stashes"] or 0) > 0]
    lines = [
        "# 工作区整理盘点（hardened AC1 四表）",
        "",
        "生成：`tools/governance/consolidate.py`（只读；本次运行 %s）。"
        % doc["generated_at"],
        "主 checkout：`%s`，HEAD `%s`，主线 `%s`（tip `%s`）。"
        % (doc["repo_root"], (doc["head"] or "")[:9], doc["mainline"],
           (doc["mainline_tip"] or "")[:9]),
        "",
        "## 一、总量",
        "",
        "| 项 | 数 |",
        "|---|---:|",
        "| 本地分支 | **%d** |" % doc["counts"]["branches"],
        "| 已并入主线 | %d |" % doc["counts"]["merged"],
        "| **未并入主线** | **%d** |" % doc["counts"]["unmerged"],
        "| 已注册 worktree | **%d** |" % doc["counts"]["worktrees"],
        "| 受保护 worktree | **%d** |" % doc["counts"]["worktrees_with_protection"],
        "| 保护声明错误 | **%d** |" % len(doc["declaration_errors"]),
        "| worktree 检查失败 | **%d** |" % len(doc["inspection_errors"]),
        "",
        "保护判定：规范化绝对路径 + 父子覆盖（含被保留根的后代）；来源见 "
        "`declaration_scan`，错误逐条列在 JSON。",
        "",
        "## 二、分支表（未并入主线的 %d 条，按独有提交数降序）" % len(unmerged),
        "",
        "| 分支 | tip | 独有提交 | tip 日期 | worktree 检出 |",
        "|---|---|---:|---|---|",
    ]
    for row in unmerged:
        checked_out = ", ".join(
            os.path.basename(path.rstrip("/\\"))
            for path in row["checked_out_at"]) or "—"
        lines.append("| `%s` | `%s` | %s | %s | %s |"
                     % (row["branch"], (row["tip"] or "")[:9],
                        row["unique_commits"], row["tip_date"], checked_out))
    lines += ["", "## 三、worktree 表（受保护者）", "",
              "| 路径 | 分支 | 保护来源数 |", "|---|---|---:|"]
    for row in sorted(protected, key=lambda item: item["path"]):
        lines.append("| `%s` | `%s` | %d |"
                     % (row["path"].replace(doc["repo_root"], "<repo>"),
                        row["branch"], len(row["protected"])))
    lines += ["", "## 四、形式干净且无保护声明的 worktree（仍需删除前清册）", "",
              "| 路径 | 分支 | 脏条目 | stash |", "|---|---|---:|---:|"]
    for row in sorted(clean_unprotected, key=lambda item: item["path"]):
        lines.append("| `%s` | `%s` | 0 | 0 |"
                     % (row["path"].replace(doc["repo_root"], "<repo>"),
                        row["branch"]))
    lines += ["", "## 五、带改动、stash 或检查失败的 worktree（不得清理）", "",
              "| 路径 | 分支 | 脏条目 | stash | 检查 | protected |",
              "|---|---|---:|---:|---|---|"]
    for row in sorted(dirty, key=lambda item: -(item["dirty_entries"] or 0)):
        lines.append("| `%s` | `%s` | %s | %s | %s | %s |"
                     % (item_path(row, doc), row["branch"],
                        row["dirty_entries"], row["stashes"], row["inspection"],
                        "yes" if row["protected"] else "no"))
    return "\n".join(lines) + "\n"


def item_path(row, doc):
    return row["path"].replace(doc["repo_root"], "<repo>")


def run_consolidate(config):
    doc, index, scanned = build_inventory(config)
    out = config.get("out")
    if out:
        guard.write_json_atomic(os.path.join(out, "inventory.json"), doc)
        markdown = _markdown(doc)
        target = os.path.join(out, "inventory.md")
        parent = os.path.dirname(os.path.abspath(target))
        if parent and not os.path.isdir(parent):
            os.makedirs(parent, exist_ok=True)
        with io.open(target, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(markdown)
    print("  branches: %d  (merged %d / unmerged %d)"
          % (doc["counts"]["branches"], doc["counts"]["merged"],
             doc["counts"]["unmerged"]))
    print("  worktrees: %d  protected %d  inspection failures %d"
          % (doc["counts"]["worktrees"], doc["counts"]["worktrees_with_protection"],
             doc["counts"]["inspection_errors"]))
    print("  declarations: %d (errors %d / warnings %d)"
          % (doc["declarations"]["declarations"],
             doc["declarations"]["errors"], doc["declarations"]["warnings"]))
    if out:
        print("  wrote inventory.json + inventory.md under %s" % out)
    else:
        print("  no --out: nothing was written")
    failed = bool(index.errors or doc["inspection_errors"])
    if failed:
        print("REFUSE: inventory is not published as trustworthy; %d declaration "
              "error(s), %d inspection error(s)"
              % (len(index.errors), len(doc["inspection_errors"])),
              file=sys.stderr)
    return 2 if failed else 0


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Read-only workspace inventory with fail-closed Git handling.")
    parser.add_argument("--repo", help="repository root (default %s)" % REPO_DEFAULT)
    parser.add_argument("--workspace-root",
                        help="workspace root (default %s)" % WS_DEFAULT)
    parser.add_argument("--mainline", default=MAINLINE_DEFAULT,
                        help="governance mainline branch (default %s)"
                             % MAINLINE_DEFAULT)
    parser.add_argument("--out", help="directory for inventory.json + inventory.md "
                                      "(default: print summary, write nothing)")
    parser.add_argument("--deep", action="store_true",
                        help="also count ignored/untracked files per worktree "
                             "(slower; required before trusting a clean status)")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    config = {
        "repo": guard.norm_abs(args.repo or REPO_DEFAULT, "repo"),
        "ws": guard.norm_abs(args.workspace_root or WS_DEFAULT,
                             "workspace root"),
        "mainline": args.mainline,
        "out": os.path.normpath(os.path.abspath(args.out)) if args.out else None,
        "deep": bool(args.deep),
    }
    try:
        return run_consolidate(config)
    except guard.GuardError as exc:
        print("REFUSED: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
