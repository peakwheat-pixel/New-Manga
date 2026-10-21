# -*- coding: utf-8 -*-
"""AC4 (hardened): archive every unmerged branch before anything is deleted.

HARDENING TASK: WORKSPACE-CLEANUP-TOOL-HARDENING-1.  The old version created
tags and bundles unconditionally (no dry-run), used ``git tag -f`` (overwrote an
existing archive ref) and silently overwrote an existing bundle file.  This
version:

  * default is a plan-only dry run; ``--apply`` plus a release-window record is
    required before any tag/bundle is written (AC5);
  * every Git command's exit code is checked (AC2);
  * the inventory is re-validated against the live repository (branch set, tips,
    merge state); a stale inventory is a refusal, not a subset run;
  * an existing archive tag is only accepted when it already points at the exact
    tip, and an existing bundle file is never overwritten; both are conflicts
    that abort the whole apply;
  * the bundle is written to a temporary file inside the archive directory,
    verified with ``git bundle verify`` and only then renamed into place;
  * failures are recorded and returned as a non-zero exit; nothing is reported
    as archived unless its bundle verified.

A bundle here is an incremental ``<mainline>..<branch>`` bundle: its prerequisite
is the mainline commit, which must stay reachable.  It is not a self-contained
backup.
"""
import argparse
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import clean_workspace as guard  # noqa: E402

TOOL_ID = "archive_branches.py"
SCHEMA_VERSION = 1

REPO_DEFAULT = guard.REPO_DEFAULT
WS_DEFAULT = guard.WS_DEFAULT
MAINLINE_DEFAULT = "antigravity/P09-AC3-DELETE-HARDEN-1"
DEFAULT_BUNDLES = "archive/bundles"
DEFAULT_INVENTORY = "verification/WORKSPACE-CONSOLIDATION-1/inventory.json"
TAG_PREFIX = "archive/"
SAFE_RE = re.compile(r"[^A-Za-z0-9._-]+")


def bundles_dir(config):
    return guard.norm_abs(os.path.join(config["ws"].replace("/", os.sep),
                                       DEFAULT_BUNDLES.replace("/", os.sep)),
                          "bundles directory")


def load_inventory(path):
    data = guard.load_json(path, "consolidation inventory")
    if not isinstance(data, dict) or not isinstance(data.get("branches"), list):
        guard.fail("INVENTORY_SCHEMA",
                   "inventory has no branches list")
    entries = []
    seen = set()
    for position, item in enumerate(data["branches"]):
        if not isinstance(item, dict):
            guard.fail("INVENTORY_SCHEMA", "branches[%d] is not an object"
                       % position)
        for key in ("branch", "merged", "unique_commits"):
            if key not in item:
                guard.fail("INVENTORY_SCHEMA",
                           "branches[%d] is missing %r" % (position, key))
        if not isinstance(item["branch"], str) or not item["branch"].strip():
            guard.fail("INVENTORY_SCHEMA", "branches[%d].branch is empty" % position)
        if not isinstance(item["merged"], bool):
            guard.fail("INVENTORY_SCHEMA",
                       "branches[%d].merged is not a boolean" % position)
        if item["unique_commits"] is None or not isinstance(
                item["unique_commits"], int):
            guard.fail("INVENTORY_SCHEMA",
                       "branches[%d].unique_commits is not an integer" % position)
        if item["branch"] in seen:
            guard.fail("INVENTORY_SCHEMA",
                       "duplicate branch entry %r" % item["branch"])
        seen.add(item["branch"])
        entries.append(item)
    return data, entries


def safe_name(branch):
    name = SAFE_RE.sub("_", branch)
    if not name or name.strip("._") == "":
        guard.fail("BRANCH_TAG_UNSAFE",
                   "branch %r cannot be represented as an archive tag" % branch)
    return name


def plan_archive(config):
    """Return (plan, conflicts).  No mutation happens here."""
    repo = config["repo"]
    mainline = config["mainline"]
    tips = guard.git_branch_tips(repo)
    if mainline not in tips:
        guard.fail("MAINLINE_MISSING",
                   "configured mainline %r is not a local branch" % mainline)
    data, entries = load_inventory(config["inventory"])
    conflicts = []
    plan = []
    for item in entries:
        branch = item["branch"]
        if branch == mainline:
            continue
        if branch not in tips:
            conflicts.append({"branch": branch, "why": "BRANCH_MISSING",
                              "detail": "listed in the inventory but absent now"})
            continue
        merged = guard.git_is_ancestor(repo, branch, mainline)
        if merged != item["merged"]:
            conflicts.append({
                "branch": branch, "why": "INVENTORY_STALE",
                "detail": "inventory merged=%r but git says merged=%r"
                          % (item["merged"], merged)})
            continue
        if merged:
            continue
        tip = tips[branch]
        name = safe_name(branch)
        tag = TAG_PREFIX + name
        check = guard.git(repo, "check-ref-format", "refs/tags/" + tag)
        if check.returncode != 0:
            conflicts.append({"branch": branch, "why": "TAG_INVALID",
                              "detail": tag})
            continue
        tag_tip = None
        existing = guard.git(repo, "rev-parse", "--verify", "--quiet",
                             "refs/tags/" + tag)
        if existing.returncode == 0:
            tag_tip = existing.stdout.strip()
            if tag_tip != tip:
                conflicts.append({
                    "branch": branch, "why": "TAG_CONFLICT",
                    "detail": "existing %s points at %s, branch tip is %s"
                              % (tag, tag_tip, tip)})
                continue
        bundle = os.path.join(bundles_dir(config).replace("/", os.sep),
                              name + ".bundle")
        if os.path.exists(bundle):
            conflicts.append({
                "branch": branch, "why": "BUNDLE_EXISTS",
                "detail": "refusing to overwrite %s" % bundle})
            continue
        plan.append({
            "branch": branch, "tip": tip, "tag": tag,
            "tag_exists": tag_tip == tip,
            "bundle": bundle.replace("\\", "/"),
            "unique_commits": item["unique_commits"],
        })
    plan.sort(key=lambda item: item["branch"])
    return plan, conflicts


def _candidate_digest(plan):
    return guard.canonical_sha256(
        [{"branch": item["branch"], "tip": item["tip"]} for item in plan])


def run_archive(config):
    plan, conflicts = plan_archive(config)
    digest = _candidate_digest(plan)
    report = {
        "schema_version": SCHEMA_VERSION,
        "tool": TOOL_ID,
        "mode": "apply" if config["apply"] else "dry_run",
        "generated_at": guard.now_iso(),
        "repo_root": config["repo"],
        "mainline": config["mainline"],
        "bundles_dir": bundles_dir(config),
        "inventory": {
            "path": config["inventory"].replace("\\", "/"),
            "sha256": guard.sha256_file(config["inventory"]),
        },
        "plan": plan,
        "conflicts": conflicts,
        "archived": [],
        "failed": [],
        "totals": {
            "planned": len(plan),
            "conflicts": len(conflicts),
            "archived": 0,
            "failed": 0,
            "unique_commits": sum(item["unique_commits"] for item in plan),
        },
        "candidates_sha256": digest,
        "candidate_count": len(plan),
    }
    lines = ["%s: %d unmerged branch(es) to archive, %d conflict(s)"
             % (report["mode"], len(plan), len(conflicts))]
    for item in plan[:15]:
        print("    plan %-52s tag=%s%s" % (item["branch"], item["tag"],
                                           " (existing, verified)" if item[
                                               "tag_exists"] else ""))
    for item in conflicts[:10]:
        print("    CONFLICT %-46s %s: %s" % (item["branch"], item["why"],
                                             item["detail"][:100]))
    if conflicts:
        # A conflict means the inventory cannot be trusted for THIS set; stop
        # before writing anything, including in dry-run (the plan is incomplete).
        report["refused"] = "INVENTORY_CONFLICT"
        _emit(report, config.get("out"), "archive-plan-refused.json", lines)
        return 2

    if not config["apply"]:
        _emit(report, config.get("out"), "archive-plan-dryrun.json", lines)
        return 0

    expected = {
        "tool": TOOL_ID,
        "repo": config["repo"],
        "workspace_root": config["ws"],
        "roots": [bundles_dir(config)],
        "candidates_sha256": digest,
        "candidate_count": len(plan),
    }
    record = guard.verify_release_window(config["release_window"], expected)
    repo = config["repo"]
    target_dir = bundles_dir(config).replace("/", os.sep)
    try:
        os.makedirs(target_dir, exist_ok=True)
    except OSError as exc:
        guard.fail("ARCHIVE_DIR_FAILED",
                   "cannot create bundles directory %s: %s" % (target_dir, exc))

    for item in plan:
        branch = item["branch"]
        tip = item["tip"]
        if not item["tag_exists"]:
            result = guard.git(repo, "tag", item["tag"], branch)
            if result.returncode != 0:
                report["failed"].append({
                    "branch": branch, "why": "TAG_FAILED",
                    "detail": (result.stderr or "").strip()[:200]})
                continue
        temp = item["bundle"] + ".tmp-%d" % os.getpid()
        result = guard.git(repo, "bundle", "create", temp,
                           "%s..%s" % (config["mainline"], branch))
        if result.returncode != 0 or not os.path.isfile(temp):
            report["failed"].append({
                "branch": branch, "why": "BUNDLE_CREATE_FAILED",
                "detail": (result.stderr or "").strip()[:200]})
            continue
        verify = guard.git(repo, "bundle", "verify", temp)
        if verify.returncode != 0:
            report["failed"].append({
                "branch": branch, "why": "BUNDLE_VERIFY_FAILED",
                "detail": ((verify.stdout or "") + (verify.stderr or ""))
                          .strip()[:200]})
            try:
                os.remove(temp)
            except OSError:
                pass
            continue
        if os.path.exists(item["bundle"]):
            report["failed"].append({
                "branch": branch, "why": "BUNDLE_EXISTS",
                "detail": "another run created the bundle; not overwriting"})
            try:
                os.remove(temp)
            except OSError:
                pass
            continue
        try:
            os.replace(temp, item["bundle"].replace("/", os.sep))
        except OSError as exc:
            report["failed"].append({"branch": branch, "why": "BUNDLE_MOVE_FAILED",
                                     "detail": str(exc)[:200]})
            continue
        report["archived"].append({
            "branch": branch, "tip": tip, "tag": item["tag"],
            "bundle": item["bundle"],
            "bundle_bytes": guard.file_size(item["bundle"].replace("/", os.sep)),
            "verified": True,
            "unique_commits": item["unique_commits"],
        })
    report["totals"]["archived"] = len(report["archived"])
    report["totals"]["failed"] = len(report["failed"])
    report["apply"] = {
        "release_window": {
            "task_id": record["task_id"],
            "authorized_by": record["authorized_by"],
            "authorization_ref": record["authorization_ref"],
            "release_window": record["release_window"],
        },
    }
    report["report_sha256"] = guard.canonical_sha256(
        {key: value for key, value in report.items() if key != "report_sha256"})
    lines.append("  archived %d, failed %d" % (len(report["archived"]),
                                               len(report["failed"])))
    for item in report["failed"][:8]:
        lines.append("    FAILED %s %s: %s" % (item["branch"], item["why"],
                                               item["detail"][:100]))
    _emit(report, config.get("out"), "archive-manifest-apply.json", lines)
    return 0 if not report["failed"] else 1


def _emit(report, out, filename, lines):
    target = None
    if out:
        target = os.path.join(out, filename)
        guard.write_json_atomic(target, report)
    for line in lines:
        print(line)
    if target:
        print("  report: %s" % target.replace("\\", "/"))


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Archive unmerged branches (dry-run by default).")
    parser.add_argument("--repo", help="repository root (default %s)" % REPO_DEFAULT)
    parser.add_argument("--workspace-root",
                        help="workspace root (default %s)" % WS_DEFAULT)
    parser.add_argument("--mainline", default=MAINLINE_DEFAULT)
    parser.add_argument("--inventory",
                        help="inventory JSON (default <repo>/%s)"
                             % DEFAULT_INVENTORY)
    parser.add_argument("--out", help="directory for JSON report output")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--release-window",
                        help="release-window record JSON (required with --apply)")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    repo = guard.norm_abs(args.repo or REPO_DEFAULT, "repo")
    config = {
        "repo": repo,
        "ws": guard.norm_abs(args.workspace_root or WS_DEFAULT,
                             "workspace root"),
        "mainline": args.mainline,
        "inventory": os.path.abspath(args.inventory or os.path.join(
            repo.replace("/", os.sep), DEFAULT_INVENTORY.replace("/", os.sep))),
        "out": os.path.normpath(os.path.abspath(args.out)) if args.out else None,
        "apply": bool(args.apply),
        "release_window": args.release_window,
    }
    try:
        if config["apply"] and not config["release_window"]:
            guard.fail("APPLY_NEEDS_RELEASE_WINDOW",
                       "--apply requires an explicit --release-window record")
        return run_archive(config)
    except guard.GuardError as exc:
        print("REFUSED: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
