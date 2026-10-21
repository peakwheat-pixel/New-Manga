# -*- coding: utf-8 -*-
"""Delete branch refs, only after every unmerged one is bundled and tagged.

HARDENING TASK: WORKSPACE-CLEANUP-TOOL-HARDENING-1.  Rules enforced here:

  * default is a dry run; ``--apply`` requires a release-window record whose
    candidate digest equals the freshly recomputed set (AC5);
  * the mainline is never touched; ``master``/``main`` are excluded;
  * a branch checked out in any registered worktree is skipped (git cannot
    delete it and forcing would be wrong -- ``--force`` is never used);
  * the inventory's ``merged`` flag is re-checked against the live repository;
    a mismatch is a stale inventory and aborts the whole run (AC2);
  * a missing branch is skipped and reported, never silently ignored;
  * an unmerged branch is deletable only when ``archive-manifest.json`` has a
    ``verified`` archive entry for that exact branch whose recorded tip equals
    the current tip, whose archive tag still points at that tip, whose bundle
    file exists and whose ``git bundle verify`` passes *now*;
  * the archive manifest and inventory are schema-validated (AC2);
  * merged branches use ``git branch -d``; unmerged branches use ``-D`` only
    after every check above passed.  Nothing is reported deleted on failure.

Filtering order is deliberate: protections are evaluated before the deletion
plan is built, so the release-window digest covers exactly the branches that
would be deleted.
"""
import argparse
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import clean_workspace as guard  # noqa: E402

TOOL_ID = "delete_branches.py"
SCHEMA_VERSION = 1

REPO_DEFAULT = guard.REPO_DEFAULT
WS_DEFAULT = guard.WS_DEFAULT
MAINLINE_DEFAULT = "antigravity/P09-AC3-DELETE-HARDEN-1"
DEFAULT_INVENTORY = "verification/WORKSPACE-CONSOLIDATION-1/inventory.json"
DEFAULT_ARCHIVE = "verification/WORKSPACE-CONSOLIDATION-1/archive-manifest.json"
KEEP = {"master", "main"}


def load_inventory(path):
    data = guard.load_json(path, "consolidation inventory")
    if not isinstance(data, dict) or not isinstance(data.get("branches"), list):
        guard.fail("INVENTORY_SCHEMA", "inventory has no branches list")
    entries = []
    seen = set()
    for position, item in enumerate(data["branches"]):
        if not isinstance(item, dict):
            guard.fail("INVENTORY_SCHEMA", "branches[%d] is not an object"
                       % position)
        for key in ("branch", "merged"):
            if key not in item:
                guard.fail("INVENTORY_SCHEMA",
                           "branches[%d] is missing %r" % (position, key))
        if not isinstance(item["branch"], str) or not item["branch"].strip():
            guard.fail("INVENTORY_SCHEMA", "branches[%d].branch is empty" % position)
        if not isinstance(item["merged"], bool):
            guard.fail("INVENTORY_SCHEMA",
                       "branches[%d].merged is not a boolean" % position)
        if item["branch"] in seen:
            guard.fail("INVENTORY_SCHEMA",
                       "duplicate branch entry %r" % item["branch"])
        seen.add(item["branch"])
        entries.append(item)
    return data, entries


def load_archive(path):
    data = guard.load_json(path, "archive manifest")
    if not isinstance(data, dict):
        guard.fail("ARCHIVE_SCHEMA", "archive manifest root is not an object")
    archived = data.get("archived")
    if not isinstance(archived, list):
        guard.fail("ARCHIVE_SCHEMA", "archive manifest has no archived list")
    mapping = {}
    for position, item in enumerate(archived):
        if not isinstance(item, dict):
            guard.fail("ARCHIVE_SCHEMA", "archived[%d] is not an object"
                       % position)
        for key in ("branch", "tag", "tip", "verified", "bundle"):
            if key not in item:
                guard.fail("ARCHIVE_SCHEMA",
                           "archived[%d] is missing %r" % (position, key))
        if not isinstance(item["branch"], str) or not item["branch"].strip():
            guard.fail("ARCHIVE_SCHEMA", "archived[%d].branch is empty" % position)
        if not isinstance(item["verified"], bool):
            guard.fail("ARCHIVE_SCHEMA",
                       "archived[%d].verified is not a boolean" % position)
        if not isinstance(item["tip"], str) or not re.fullmatch(
                r"[0-9a-fA-F]{40,64}", item["tip"]):
            guard.fail("ARCHIVE_SCHEMA",
                       "archived[%d].tip is not a full object id" % position)
        if item["branch"] in mapping:
            guard.fail("ARCHIVE_SCHEMA",
                       "duplicate archive entry for %r" % item["branch"])
        mapping[item["branch"]] = item
    return data, mapping


def _checked_out_branches(repo):
    checked = set()
    for entry in guard.list_worktrees(repo):
        if entry.get("branch"):
            checked.add(entry["branch"])
    return checked


def build_plan(config, tips, checked_out, archive):
    data, entries = load_inventory(config["inventory"])
    plan = []
    skipped = []
    refused = []
    for item in entries:
        branch = item["branch"]
        if branch == config["mainline"]:
            skipped.append({"branch": branch, "why": "mainline"})
            continue
        if branch in KEEP:
            skipped.append({"branch": branch,
                            "why": "reserved for the AC8 main/master decision"})
            continue
        if branch in checked_out:
            skipped.append({"branch": branch,
                            "why": "checked out in a registered worktree"})
            continue
        if branch not in tips:
            skipped.append({"branch": branch, "why": "branch is already absent"})
            continue
        merged = guard.git_is_ancestor(config["repo"], branch, config["mainline"])
        if merged != item["merged"]:
            guard.fail("INVENTORY_STALE",
                       "branch %r: inventory merged=%r but git reports merged=%r; "
                       "rerun the inventory" % (branch, item["merged"], merged))
        tip = tips[branch]
        if merged:
            plan.append({"branch": branch, "tip": tip, "merged": True,
                         "via": "-d", "unique": 0})
            continue
        proof = archive.get(branch)
        if not proof:
            refused.append({"branch": branch,
                            "why": "NO_ARCHIVE_ENTRY: no verified bundle records "
                                   "this unmerged branch"})
            continue
        if not proof["verified"]:
            refused.append({"branch": branch,
                            "why": "ARCHIVE_NOT_VERIFIED"})
            continue
        if proof["tip"].lower() != tip.lower():
            refused.append({"branch": branch,
                            "why": "ARCHIVE_TIP_MISMATCH: bundle covers %s, branch "
                                   "tip is %s" % (proof["tip"], tip)})
            continue
        tag_ref = "refs/tags/" + proof["tag"]
        tag_tip = guard.git(config["repo"], "rev-parse", "--verify", "--quiet",
                            tag_ref)
        if tag_tip.returncode != 0 or tag_tip.stdout.strip().lower() != tip.lower():
            refused.append({"branch": branch,
                            "why": "ARCHIVE_TAG_MISSING_OR_WRONG: %s does not "
                                   "point at the archived tip" % tag_ref})
            continue
        bundle_path = proof["bundle"]
        if not os.path.isfile(bundle_path):
            refused.append({"branch": branch,
                            "why": "ARCHIVE_BUNDLE_MISSING: %s" % bundle_path})
            continue
        verify = guard.git(config["repo"], "bundle", "verify", bundle_path)
        if verify.returncode != 0:
            refused.append({"branch": branch,
                            "why": "ARCHIVE_BUNDLE_VERIFY_FAILED: %s"
                                   % ((verify.stderr or verify.stdout or "")
                                      .strip()[:160])})
            continue
        plan.append({"branch": branch, "tip": tip, "merged": False,
                     "via": "-D", "unique": item.get("unique_commits"),
                     "bundle": bundle_path.replace("\\", "/")})
    plan.sort(key=lambda item: item["branch"])
    return plan, skipped, refused


def _digest(plan):
    return guard.canonical_sha256(
        [{"branch": item["branch"], "tip": item["tip"]} for item in plan])


def run_delete(config):
    repo = config["repo"]
    tips = guard.git_branch_tips(repo)
    if config["mainline"] not in tips:
        guard.fail("MAINLINE_MISSING",
                   "configured mainline %r is not a local branch"
                   % config["mainline"])
    checked_out = _checked_out_branches(repo)
    archive_data, archive = load_archive(config["archive_manifest"])
    plan, skipped, refused = build_plan(config, tips, checked_out, archive)
    digest = _digest(plan)
    report = {
        "schema_version": SCHEMA_VERSION,
        "tool": TOOL_ID,
        "mode": "apply" if config["apply"] else "dry_run",
        "generated_at": guard.now_iso(),
        "repo_root": repo,
        "mainline": config["mainline"],
        "inventory": {"path": config["inventory"].replace("\\", "/"),
                      "sha256": guard.sha256_file(config["inventory"])},
        "archive_manifest": {
            "path": config["archive_manifest"].replace("\\", "/"),
            "sha256": guard.sha256_file(config["archive_manifest"]),
            "archived_entries": len(archive_data["archived"]),
        },
        "plan": plan,
        "skipped": skipped,
        "refused": refused,
        "deleted": [],
        "delete_failures": [],
        "totals": {
            "planned": len(plan),
            "planned_merged": sum(1 for item in plan if item["merged"]),
            "planned_unmerged": sum(1 for item in plan if not item["merged"]),
            "skipped": len(skipped),
            "refused": len(refused),
            "deleted": 0,
        },
        "candidates_sha256": digest,
        "candidate_count": len(plan),
    }
    lines = ["%s: %d branch(es) deletable (merged %d / unmerged %d), "
             "skipped %d, refused %d"
             % (report["mode"], len(plan), report["totals"]["planned_merged"],
                report["totals"]["planned_unmerged"], len(skipped), len(refused))]
    for item in plan[:15]:
        print("    plan %-52s via %s" % (item["branch"], item["via"]))
    for item in refused[:10]:
        print("    REFUSED %-46s %s" % (item["branch"], item["why"][:110]))
    if refused:
        # A refused unmerged branch means the archive proof is incomplete; the
        # plan is not executable as a whole and must not be partially applied.
        report["refused_plan"] = "INCOMPLETE_ARCHIVE_PROOF"
        _emit(report, config.get("out"), "branch-deletion-refused.json", lines)
        return 2
    if not config["apply"]:
        _emit(report, config.get("out"), "branch-deletion-dryrun.json", lines)
        return 0

    expected = {
        "tool": TOOL_ID,
        "repo": config["repo"],
        "workspace_root": config["ws"],
        "roots": [config["repo"]],
        "candidates_sha256": digest,
        "candidate_count": len(plan),
    }
    record = guard.verify_release_window(config["release_window"], expected)
    for item in plan:
        args = ["branch", item["via"], item["branch"]]
        result = guard.git(config["repo"], *args)
        if result.returncode != 0:
            report["delete_failures"].append({
                "branch": item["branch"], "via": item["via"],
                "detail": (result.stderr or result.stdout or "").strip()[:200]})
            continue
        report["deleted"].append({"branch": item["branch"], "via": item["via"],
                                  "merged": item["merged"],
                                  "unique": item.get("unique")})
    report["totals"]["deleted"] = len(report["deleted"])
    report["mode"] = "apply"
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
    lines.append("  deleted %d, failures %d" % (len(report["deleted"]),
                                                len(report["delete_failures"])))
    for item in report["delete_failures"][:8]:
        lines.append("    FAILED %s %s" % (item["branch"], item["detail"][:100]))
    _emit(report, config.get("out"), "branch-deletion-apply.json", lines)
    return 0 if not report["delete_failures"] else 1


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
        description="Delete archived branches (dry-run by default).")
    parser.add_argument("--repo", help="repository root (default %s)" % REPO_DEFAULT)
    parser.add_argument("--workspace-root",
                        help="workspace root (default %s)" % WS_DEFAULT)
    parser.add_argument("--mainline", default=MAINLINE_DEFAULT)
    parser.add_argument("--inventory",
                        help="inventory JSON (default <repo>/%s)"
                             % DEFAULT_INVENTORY)
    parser.add_argument("--archive-manifest",
                        help="archive manifest JSON (default <repo>/%s)"
                             % DEFAULT_ARCHIVE)
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
        "archive_manifest": os.path.abspath(
            args.archive_manifest or os.path.join(
                repo.replace("/", os.sep),
                DEFAULT_ARCHIVE.replace("/", os.sep))),
        "out": os.path.normpath(os.path.abspath(args.out)) if args.out else None,
        "apply": bool(args.apply),
        "release_window": args.release_window,
    }
    try:
        if config["apply"] and not config["release_window"]:
            guard.fail("APPLY_NEEDS_RELEASE_WINDOW",
                       "--apply requires an explicit --release-window record")
        return run_delete(config)
    except guard.GuardError as exc:
        print("REFUSED: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
