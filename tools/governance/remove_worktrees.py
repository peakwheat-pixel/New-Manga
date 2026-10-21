# -*- coding: utf-8 -*-
"""Phase B (hardened): remove worktrees that are provably safe to remove.

HARDENING TASK: WORKSPACE-CLEANUP-TOOL-HARDENING-1.  The r208 incident removed
six protected worktrees (five of them PRESERVE_*) plus a preserved-root
descendant.  The old tool compensated by adding a freshly written 7-cell
resource table to the Task file *after* the deletion, which is not protection.
This rewrite removes the root causes:

  * protection is evaluated by normalised absolute path identity with
    parent/child coverage (see ``clean_workspace.ProtectionIndex``), not by
    directory basename equality;
  * a worktree whose directory is not a direct child of ``<workspace>/worktrees``
    is rejected outright: the old ``New Manga.worktrees/<name>`` location cannot
    be mapped to a Task declaration by name, and the r208 ledger shows exactly
    that location being deleted (ROOT-07);
  * a failed ``git status``, ``git stash list``, inventory read or permission
    error is a refusal, never an empty result (AC2);
  * ignored files are enumerated per file with size + SHA-256 before anything is
    removed.  ``git worktree remove`` deletes ignored files silently (verified:
    exit 0 with ignored content), so ignored content blocks apply unless a
    release-window record explicitly accepts the exact inventory hash (AC3);
  * default is dry-run; apply needs ``--apply`` + a release-window record whose
    candidate digest equals the freshly recomputed candidate set (AC5);
  * ``--replay-incident`` feeds the r208 ledger's 15 deleted roots and 18
    protected sources through the same predicate and must reject all 15 (AC6).

No ``--force`` exists in this tool and none is passed to git.
"""
import argparse
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import clean_workspace as guard  # noqa: E402  (shared fail-closed guard core)

TOOL_ID = "remove_worktrees.py"
SCHEMA_VERSION = 1

REPO_DEFAULT = guard.REPO_DEFAULT
WS_DEFAULT = guard.WS_DEFAULT
DEFAULT_INVENTORY = "verification/WORKSPACE-CONSOLIDATION-1/inventory.json"


def worktrees_root(config):
    return guard.norm_abs(
        os.path.join(config["ws"].replace("/", os.sep), "worktrees"),
        "workspace worktrees root")


def load_inventory(path):
    """Strict inventory validation (AC2: schema deviation is a refusal)."""
    data = guard.load_json(path, "consolidation inventory")
    if not isinstance(data, dict):
        guard.fail("INVENTORY_SCHEMA", "inventory root is not an object")
    for key in ("worktrees", "protected_worktree_names"):
        if key not in data:
            guard.fail("INVENTORY_SCHEMA", "inventory is missing %r" % key)
    if not isinstance(data["worktrees"], list):
        guard.fail("INVENTORY_SCHEMA", "inventory.worktrees is not a list")
    if not isinstance(data["protected_worktree_names"], dict):
        guard.fail("INVENTORY_SCHEMA",
                   "inventory.protected_worktree_names is not an object")
    protected_names = set()
    for name, sources in data["protected_worktree_names"].items():
        if not isinstance(name, str) or not name.strip():
            guard.fail("INVENTORY_SCHEMA",
                       "protected_worktree_names contains a non-string key")
        if not isinstance(sources, list) or not all(
                isinstance(item, str) for item in sources):
            guard.fail("INVENTORY_SCHEMA",
                       "protected_worktree_names[%r] is not a list of strings"
                       % name)
        protected_names.add(name)
    entries = []
    seen = {}
    duplicates = []
    for position, item in enumerate(data["worktrees"]):
        if not isinstance(item, dict):
            guard.fail("INVENTORY_SCHEMA", "worktrees[%d] is not an object"
                       % position)
        for key in ("path", "branch", "protected"):
            if key not in item:
                guard.fail("INVENTORY_SCHEMA",
                           "worktrees[%d] is missing %r" % (position, key))
        if not isinstance(item["path"], str) or not item["path"].strip():
            guard.fail("INVENTORY_SCHEMA",
                       "worktrees[%d].path is empty" % position)
        if not guard.is_abs_path(item["path"]):
            guard.fail("INVENTORY_PATH_NOT_ABSOLUTE",
                       "worktrees[%d].path %r is not absolute; a bare/relative "
                       "path has no provable identity" % (position, item["path"]))
        normalized = guard.norm_abs(item["path"], "inventory worktree path")
        if not isinstance(item["branch"], str):
            guard.fail("INVENTORY_SCHEMA",
                       "worktrees[%d].branch is not a string" % position)
        if not isinstance(item["protected"], list):
            guard.fail("INVENTORY_SCHEMA",
                       "worktrees[%d].protected is not a list" % position)
        if normalized in seen:
            duplicates.append({"normalized": normalized,
                               "first_index": seen[normalized],
                               "duplicate_index": position,
                               "raw": item["path"]})
            continue
        seen[normalized] = position
        entries.append({"position": position, "raw": item["path"],
                        "normalized": normalized, "branch": item["branch"],
                        "protected": item["protected"]})
    return data, entries, protected_names, duplicates


def _registered_map(repo):
    entries = guard.list_worktrees(repo)
    mapping = {}
    duplicates = []
    for entry in entries:
        if entry["normalized"] in mapping:
            duplicates.append(entry["normalized"])
            continue
        mapping[entry["normalized"]] = entry
    return mapping, duplicates


def _base_refusal_report(config, errors, mode="dry_run"):
    return {
        "schema_version": SCHEMA_VERSION,
        "tool": TOOL_ID,
        "mode": mode,
        "generated_at": guard.now_iso(),
        "repo_root": config["repo"],
        "workspace_root": config["ws"],
        "declaration_integrity": "FAILED",
        "declaration_errors": errors[:50],
        "declaration_error_count": len(errors),
        "worktrees": [],
        "totals": {"candidates": 0, "would_remove": 0, "rejected": 0,
                   "skipped": 0, "bytes": 0, "deleted": 0},
        "candidates_sha256": guard.candidates_digest([]),
        "candidate_count": 0,
        "refused": "DECLARATION_INTEGRITY",
    }


def evaluate_candidate(entry, config, index, registered, protected_names,
                       wt_root):
    """Evaluate one inventory worktree.  Returns a report record."""
    normalized = entry["normalized"]
    record = {
        "path": entry["raw"].replace("\\", "/"),
        "normalized": normalized,
        "branch": entry["branch"],
        "registered": normalized in registered,
        "decision": "CANDIDATE",
        "reasons": [],
    }
    main_checkout = guard.norm_abs(config["repo"], "main checkout")
    if normalized == main_checkout:
        record["decision"] = "SKIP"
        record["reasons"] = ["main checkout"]
        return record
    if normalized not in registered:
        record["decision"] = "SKIP"
        record["reasons"] = ["not a registered worktree of this repository"]
        return record
    registered_entry = registered[normalized]
    if registered_entry.get("bare"):
        record["decision"] = "SKIP"
        record["reasons"] = ["bare worktree entry"]
        return record
    ident = guard.resolve_identity(entry["raw"], "worktree candidate")
    if ident.is_alias:
        record["decision"] = "REJECT"
        record["reasons"] = [
            "PATH_ALIAS: %r resolves to %s; alias paths are refused"
            % (entry["raw"], ident.real)]
        return record
    if not ident.exists:
        record["decision"] = "SKIP"
        record["reasons"] = ["directory missing"]
        return record
    if not ident.is_dir:
        record["decision"] = "REJECT"
        record["reasons"] = ["PATH_NOT_DIRECTORY: not a directory"]
        return record
    location = guard.path_relation(normalized, wt_root)
    record["standard_location"] = location == "descendant"
    if location != "descendant":
        record["decision"] = "REJECT"
        record["reasons"] = [
            "NON_STANDARD_WORKTREE_LOCATION: %r is not a direct child of %s; "
            "the r208 ledger shows this location being deleted while Task "
            "declarations referenced it by name.  A name-based mapping cannot "
            "be proven, so explicit adjudication is required"
            % (entry["raw"], wt_root)]
        return record
    name = normalized.rsplit("/", 1)[-1]
    protected_lookup = {key.lower(): key for key in protected_names}
    if name in protected_lookup or entry["protected"]:
        display = protected_lookup.get(name, name)
        record["decision"] = "REJECT"
        record["reasons"] = [
            "protected worktree name %r declared by %s"
            % (display, ", ".join(sorted(protected_names.get(display, []))
                                  or [str(item) for item in entry["protected"]][:2]))]
        return record
    hits = index.evaluate(normalized)
    if hits:
        record["decision"] = "REJECT"
        record["reasons"] = [guard.describe_hit(hit) for hit in hits]
        return record
    if registered_entry.get("locked"):
        record["decision"] = "REJECT"
        record["reasons"] = ["GIT_WORKTREE_LOCKED: worktree is locked"]
        return record
    try:
        status = guard.git_status_entries(normalized)
    except guard.GuardError as exc:
        record["decision"] = "REJECT"
        record["reasons"] = ["%s: %s" % (exc.code, exc.message)]
        return record
    if status:
        record["decision"] = "REJECT"
        record["reasons"] = ["GIT_STATUS_DIRTY: %d dirty/untracked entrie(s)"
                             % len(status)]
        record["status_entries"] = status[:20]
        return record
    try:
        stashes = guard.git_stash_entries(normalized)
    except guard.GuardError as exc:
        record["decision"] = "REJECT"
        record["reasons"] = ["%s: %s" % (exc.code, exc.message)]
        return record
    if stashes:
        record["decision"] = "REJECT"
        record["reasons"] = ["GIT_STASH_PRESENT: %d stash entrie(s)"
                             % len(stashes)]
        return record
    try:
        inventory = guard.build_inventory(normalized, git_worktree=True)
    except guard.GuardError as exc:
        record["decision"] = "REJECT"
        record["reasons"] = ["%s: %s" % (exc.code, exc.message)]
        return record
    record["bytes"] = inventory["counts"]["bytes"]
    record["inventory"] = {
        "digest": inventory["digest"],
        "counts": inventory["counts"],
        "requires_acceptance": guard.inventory_requires_acceptance(inventory),
    }
    return record, inventory


def build_worktree_report(config):
    index, scanned = guard.scan_repo_declarations(config["repo"], config["ws"])
    if index.errors:
        return _base_refusal_report(config, index.errors), [], scanned
    inventory_path = config["inventory"]
    data, entries, protected_names, duplicates = load_inventory(inventory_path)
    registered, registered_duplicates = _registered_map(config["repo"])
    protected_names = set(protected_names)
    protected_names.update(index.protected_worktree_names(
        worktrees_root(config)).keys())

    records = []
    inventories = []
    for entry in entries:
        result = evaluate_candidate(entry, config, index, registered,
                                    protected_names, worktrees_root(config))
        if isinstance(result, tuple):
            record, inventory = result
            inventories.append({"candidate": record["normalized"],
                                "inventory": inventory})
        else:
            record = result
        record["inventory_source"] = inventory_path.replace("\\", "/")
        records.append(record)
    deletable = [record["normalized"] for record in records
                 if record["decision"] == "CANDIDATE"]
    report = {
        "schema_version": SCHEMA_VERSION,
        "tool": TOOL_ID,
        "mode": "dry_run",
        "generated_at": guard.now_iso(),
        "repo_root": config["repo"],
        "workspace_root": config["ws"],
        "worktrees_root": worktrees_root(config),
        "inventory": {
            "path": inventory_path.replace("\\", "/"),
            "sha256": guard.sha256_file(inventory_path),
            "worktree_entries": len(data["worktrees"]),
            "unique_entries": len(entries),
            "duplicate_entries": duplicates,
            "protected_names": len(data["protected_worktree_names"]),
            "registered_worktrees": len(registered),
            "registered_duplicates": registered_duplicates,
        },
        "declarations": index.counts(),
        "declaration_scan": scanned,
        "declaration_warnings": index.warnings,
        "worktrees": records,
        "totals": {
            "candidates": len(records),
            "would_remove": len(deletable),
            "rejected": sum(1 for record in records
                            if record["decision"] == "REJECT"),
            "skipped": sum(1 for record in records
                           if record["decision"] == "SKIP"),
            "bytes": sum(record.get("bytes", 0) for record in records
                         if record["decision"] == "CANDIDATE"),
        },
        "candidates_sha256": guard.candidates_digest(deletable),
        "candidate_count": len(deletable),
    }
    report["report_sha256"] = guard.canonical_sha256(
        {key: value for key, value in report.items()
         if key not in ("generated_at", "report_sha256")})
    return report, inventories, scanned


def _write_inventories(config, inventories):
    out_dir = config.get("out")
    if not out_dir:
        return
    for item in inventories:
        safe = re.sub(r"[^A-Za-z0-9._-]+", "_", item["candidate"])[-120:]
        target = os.path.join(out_dir, "inventory", safe + ".json")
        guard.write_json_atomic(target, item["inventory"])
        item["inventory_path"] = target.replace("\\", "/")


def _emit(report, out_dir, filename, lines):
    target = None
    if out_dir:
        target = os.path.join(out_dir, filename)
        guard.write_json_atomic(target, report)
    for line in lines:
        print(line)
    if target:
        print("  report: %s" % target.replace("\\", "/"))


def run_remove_worktrees(config):
    report, inventories, scanned = build_worktree_report(config)
    if report.get("refused"):
        lines = ["REFUSE: %d declaration integrity error(s); no worktree can be "
                 "removed until protection declarations can be trusted"
                 % report["declaration_error_count"]]
        for error in report["declaration_errors"][:8]:
            lines.append("  ERROR %s: %s [%s]" % (error["code"], error["message"],
                                                  error.get("file") or ""))
        _emit(report, config.get("out"), "worktree-removal-refused.json", lines)
        return 2
    lines = ["%s: %d worktree(s), would remove %d, rejected %d, skipped %d, %.2f MB"
             % ("apply" if config["apply"] else "dry_run",
                report["totals"]["candidates"], report["totals"]["would_remove"],
                report["totals"]["rejected"], report["totals"]["skipped"],
                report["totals"]["bytes"] / 1048576.0)]
    for record in report["worktrees"]:
        if record["decision"] in ("REJECT", "CANDIDATE"):
            print("    %-8s %-44s %s"
                  % (record["decision"],
                     os.path.basename(record["path"].rstrip("/\\"))[:44],
                     record["reasons"][0] if record["reasons"] else ""))
    if not config["apply"]:
        _write_inventories(config, inventories)
        _emit(report, config.get("out"), "worktree-removal-dryrun.json", lines)
        return 0

    expected = {
        "tool": TOOL_ID,
        "repo": config["repo"],
        "workspace_root": config["ws"],
        "roots": [worktrees_root(config)],
        "candidates_sha256": report["candidates_sha256"],
        "candidate_count": report["candidate_count"],
    }
    record = guard.verify_release_window(config["release_window"], expected)
    _write_inventories(config, inventories)
    guard.verify_inventory_acceptance(record, inventories)

    deleted = []
    refused = []
    for record_candidate in report["worktrees"]:
        if record_candidate["decision"] != "CANDIDATE":
            continue
        try:
            returncode, stdout, stderr = guard.remove_worktree(
                config["repo"], record_candidate["normalized"])
        except guard.GuardError as exc:
            refused.append({"path": record_candidate["path"],
                            "code": exc.code, "why": exc.message})
            continue
        if returncode != 0:
            refused.append({"path": record_candidate["path"],
                            "code": "GIT_WORKTREE_REMOVE_FAILED",
                            "why": (stderr or stdout or "").strip()[:300]})
            continue
        deleted.append({"path": record_candidate["path"],
                        "normalized": record_candidate["normalized"],
                        "bytes": record_candidate.get("bytes", 0)})
    report["mode"] = "apply"
    report["apply"] = {
        "release_window": {
            "task_id": record["task_id"],
            "authorized_by": record["authorized_by"],
            "authorization_ref": record["authorization_ref"],
            "release_window": record["release_window"],
        },
        "deleted": deleted,
        "refused": refused,
    }
    report["totals"]["deleted"] = len(deleted)
    report.pop("report_sha256", None)
    report["report_sha256"] = guard.canonical_sha256(
        {key: value for key, value in report.items() if key != "report_sha256"})
    lines.append("  removed %d, refused %d" % (len(deleted), len(refused)))
    for item in refused[:8]:
        lines.append("    REFUSED %s %s" % (item["path"], item["why"]))
    _emit(report, config.get("out"), "worktree-removal-apply.json", lines)
    return 0 if not refused else 1


def run_replay(config):
    report = guard.build_incident_replay(config["replay"], ws_root=config["ws"],
                                         repo_root=None)
    wt_root = worktrees_root(config)
    for decision in report["decisions"]:
        normalized = decision.get("normalized")
        if not normalized:
            continue
        location = guard.path_relation(normalized, wt_root)
        decision["standard_worktree_location"] = location == "descendant"
        if location != "descendant":
            decision["additional_tool_reason"] = (
                "NON_STANDARD_WORKTREE_LOCATION: also refused by "
                "remove_worktrees.py location rule")
    report["tool"] = TOOL_ID
    report["schema_version"] = SCHEMA_VERSION
    report.pop("report_sha256", None)
    report["report_sha256"] = guard.canonical_sha256(
        {key: value for key, value in report.items()
         if key not in ("generated_at", "report_sha256")})
    lines = ["incident replay (%s): %d root(s), rejected %d, deleted %d, "
             "violations %d" % (TOOL_ID, report["totals"]["candidates"],
                                report["totals"]["rejected"],
                                report["totals"]["deleted"],
                                report["totals"]["violations"])]
    for item in report["decisions"]:
        print("    %-9s %-6s %-70s %s"
              % (item["decision"], item["id"], item["path"][-70:],
                 item["reasons"][0] if item["reasons"] else ""))
    _emit(report, config.get("out"), "incident-replay-remove-worktrees.json", lines)
    return 0 if report["ok"] else 2


def build_config(args):
    repo = guard.norm_abs(args.repo or REPO_DEFAULT, "repo")
    ws = guard.norm_abs(args.workspace_root or WS_DEFAULT, "workspace root")
    inventory = args.inventory or os.path.join(
        repo.replace("/", os.sep), DEFAULT_INVENTORY.replace("/", os.sep))
    out = os.path.normpath(os.path.abspath(args.out)) if args.out else None
    return {
        "repo": repo,
        "ws": ws,
        "inventory": os.path.abspath(inventory),
        "out": out,
        "apply": bool(args.apply),
        "release_window": args.release_window,
        "replay": args.replay_incident,
    }


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Hardened Phase B worktree removal: dry-run by default; "
                    "apply requires a release window.")
    parser.add_argument("--repo", help="repository root (default %s)" % REPO_DEFAULT)
    parser.add_argument("--workspace-root",
                        help="workspace root (default %s)" % WS_DEFAULT)
    parser.add_argument("--inventory",
                        help="consolidation inventory JSON (default "
                             "<repo>/%s)" % DEFAULT_INVENTORY)
    parser.add_argument("--out", help="directory for JSON report/inventory output")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--release-window",
                        help="release-window record JSON (required with --apply)")
    parser.add_argument("--replay-incident",
                        help="replay an incident ledger; never removes anything")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    config = build_config(args)
    try:
        if config["replay"]:
            if config["apply"]:
                guard.fail("REPLAY_APPLY_REFUSED",
                           "--replay-incident is a read-only proof; --apply is "
                           "refused")
            return run_replay(config)
        if config["apply"] and not config["release_window"]:
            guard.fail("APPLY_NEEDS_RELEASE_WINDOW",
                       "--apply requires an explicit --release-window record")
        if config["apply"] and not config["out"]:
            guard.fail("APPLY_NEEDS_OUT",
                       "--apply requires --out so the pre-delete inventory is "
                       "preserved")
        return run_remove_worktrees(config)
    except guard.GuardError as exc:
        print("REFUSED: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
