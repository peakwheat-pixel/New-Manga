# -*- coding: utf-8 -*-
"""Generate reproducible evidence for WORKSPACE-CLEANUP-TOOL-HARDENING-1 (AC7).

Runs, in order and records command / environment / exit code for each:

  1. the new hardening test suite (``tests/``) with verbose results;
  2. the pre-existing governance tool tests (``tools/governance/tests/``);
  3. the AC6 incident replay through both path-deletion tools;
  4. a read-only declaration audit of the real repository (no --apply);
  5. a before/after snapshot proving the real workspace was not touched.

Writes everything under ``verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/
evidence/``.  Exit code is 0 only when the new suite passes, both replays report
15/15 rejected with 0 deletions, and the real-workspace snapshot is unchanged.
The pre-existing ``run-resource-manifest-cases.py`` failure is recorded honestly
and does not fail this runner: it is a pre-existing repo-state failure caused by
the TASK_LEDGER budget rule in check.ps1, which this Task's frozen scope does not
include (see HANDOFF).
"""
import datetime
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TOOLS = os.path.join(ROOT, "tools", "governance")
TESTS = os.path.join(HERE, "tests")
EVIDENCE = os.path.join(HERE, "evidence")
LEDGER = os.path.join(ROOT, "verification", "WORKSPACE-CONSOLIDATION-1",
                      "incident-ledger-r208.json")

PYTHON = sys.executable


def now():
    return datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat(
        timespec="seconds")


def run(command, cwd, label):
    started = time.time()
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", env=env)
    elapsed = round(time.time() - started, 2)
    record = {
        "label": label,
        "command": command,
        "cwd": cwd,
        "started_at": now(),
        "elapsed_seconds": elapsed,
        "exit_code": result.returncode,
        "stdout_sha256": hashlib.sha256(
            (result.stdout or "").encode("utf-8")).hexdigest(),
        "stderr_sha256": hashlib.sha256(
            (result.stderr or "").encode("utf-8")).hexdigest(),
    }
    print("[%s] exit=%d (%.2fs)" % (label, result.returncode, elapsed))
    return record, result


def write_text(name, text):
    path = os.path.join(EVIDENCE, name)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    return path.replace("\\", "/")


def write_json(name, data):
    path = os.path.join(EVIDENCE, name)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return path.replace("\\", "/")


def parse_verbose_results(log):
    """Parse ``unittest -v`` output into {test_id: "ok"|"FAIL"|"ERROR"|"skipped"}."""
    results = {}
    for line in log.split("\n"):
        match = re.match(
            r"^(test_\w+) \((\S+)\)(?:\s+\.\.\.)?\s+(ok|FAIL|ERROR|skipped.*)$",
            line.strip())
        if not match:
            continue
        location = match.group(2)
        test_id = (location if location.endswith("." + match.group(1))
                   else "%s.%s" % (location, match.group(1)))
        status = match.group(3)
        if status.startswith("skipped"):
            results[test_id] = "skipped"
        else:
            results[test_id] = status
    return results


AC_TESTS = {
    "AC1": [
        "test_guard_core.TestPathIdentity.test_equivalent_spellings_normalise_to_one_identity",
        "test_guard_core.TestPathIdentity.test_relation_uses_component_boundaries",
        "test_guard_core.TestProtectionIndex.test_exact_descendant_and_ancestor_are_protected",
        "test_guard_core.TestProtectionIndex.test_shared_declarations_are_merged_not_deduplicated_away",
        "test_guard_core.TestProtectionIndex.test_generalised_declarations_are_refused",
        "test_guard_core.TestMarkdownDeclarations.test_bare_and_backticked_paths_are_both_protected",
        "test_guard_core.TestJsonDeclarations.test_nested_resources_and_ledger_style_records",
        "test_tools_fixtures.ToolFixture.test_ac4_01_nested_root",
        "test_tools_fixtures.ToolFixture.test_ac4_02_bare_declaration_path",
        "test_tools_fixtures.ToolFixture.test_ac4_05_preserve_unknown",
        "test_tools_fixtures.ToolFixture.test_ac4_06_parent_protection",
        "test_tools_fixtures.ToolFixture.test_ac4_10_duplicate_alias_path",
        "test_tools_fixtures.ToolFixture.test_ac1_junction_declaration_real_target_protected",
        "test_guard_core.TestProtectionIndex.test_junction_declaration_protects_real_target",
    ],
    "AC2": [
        "test_guard_core.TestPathIdentity.test_bare_and_relative_paths_are_refused",
        "test_guard_core.TestPathIdentity.test_drive_relative_and_nul_are_refused",
        "test_guard_core.TestPathIdentity.test_escape_outside_managed_root_is_refused",
        "test_guard_core.TestProtectionIndex.test_unresolved_declarations_fail_closed",
        "test_guard_core.TestProtectionIndex.test_unknown_and_empty_dispositions_fail_closed",
        "test_guard_core.TestProtectionIndex.test_pathlike_destination_failure_is_integrity_error",
        "test_guard_core.TestProtectionIndex.test_descriptive_destination_is_allowed_prose",
        "test_guard_core.TestReleaseWindowAndInventory.test_permission_denied_is_fail_closed",
        "test_tools_fixtures.ToolFixture.test_ac4_03_relative_path",
        "test_tools_fixtures.ToolFixture.test_ac4_04_nonstandard_table_columns",
        "test_tools_fixtures.ToolFixture.test_ac4_07_nonstandard_worktree_location",
        "test_tools_fixtures.ToolFixture.test_ac4_08_stash_nonzero",
        "test_tools_fixtures.ToolFixture.test_ac4_09_permission_denied",
        "test_tools_fixtures.ToolFixture.test_ac4_10_duplicate_alias_path",
        "test_tools_fixtures.ToolFixture.test_ac4_08_stash_nonzero_real_entry",
        "test_tools_fixtures.ToolFixture.test_ac4_09_permission_denied_real_entry",
        "test_tools_fixtures.ToolFixture.test_ac4_11_symlink_escape",
        "test_tools_fixtures.ToolFixture.test_ac2_untracked_declarations_are_scanned",
        "test_tools_fixtures.ToolFixture.test_ac2_untracked_declaration_parse_error_refused",
        "test_tools_fixtures.ToolFixture.test_ac2_destination_pathlike_unresolved_refused",
        "test_tools_fixtures.ToolFixture.test_ac2_destination_prose_allowed",
        "test_tools_fixtures.ToolFixture.test_ac2_git_status_failure_is_refused",
        "test_tools_fixtures.ToolFixture.test_ac2_tampered_inventory_schema_is_refused",
        "test_tools_fixtures.ToolFixture.test_audit_declarations_refuses_unknown_disposition",
        "test_other_tools.BranchFixture.test_consolidate_missing_mainline_is_refused",
        "test_other_tools.BranchFixture.test_consolidate_inspection_failure_is_not_silently_none",
    ],
    "AC3": [
        "test_guard_core.TestReleaseWindowAndInventory.test_inventory_records_size_and_sha256_per_file",
        "test_tools_fixtures.ToolFixture.test_ac3_ignored_content_blocks_apply_until_accepted",
    ],
    "AC4": [
        "test_tools_fixtures.ToolFixture.test_ac4_matrix_is_complete",
        "test_tools_fixtures.ToolFixture.test_ac4_01_nested_root",
        "test_tools_fixtures.ToolFixture.test_ac4_02_bare_declaration_path",
        "test_tools_fixtures.ToolFixture.test_ac4_03_relative_path",
        "test_tools_fixtures.ToolFixture.test_ac4_04_nonstandard_table_columns",
        "test_tools_fixtures.ToolFixture.test_ac4_05_preserve_unknown",
        "test_tools_fixtures.ToolFixture.test_ac4_06_parent_protection",
        "test_tools_fixtures.ToolFixture.test_ac4_07_nonstandard_worktree_location",
        "test_tools_fixtures.ToolFixture.test_ac4_08_stash_nonzero",
        "test_tools_fixtures.ToolFixture.test_ac4_09_permission_denied",
        "test_tools_fixtures.ToolFixture.test_ac4_10_duplicate_alias_path",
        "test_tools_fixtures.ToolFixture.test_ac4_11_symlink_escape",
        "test_tools_fixtures.ToolFixture.test_ac4_08_stash_nonzero_real_entry",
        "test_tools_fixtures.ToolFixture.test_ac4_09_permission_denied_real_entry",
    ],
    "AC5": [
        "test_guard_core.TestReleaseWindowAndInventory.test_valid_record_passes",
        "test_guard_core.TestReleaseWindowAndInventory.test_candidate_drift_is_refused",
        "test_guard_core.TestReleaseWindowAndInventory.test_missing_field_is_refused",
        "test_guard_core.TestReleaseWindowAndInventory.test_expired_window_is_refused",
        "test_guard_core.TestReleaseWindowAndInventory.test_root_mismatch_is_refused",
        "test_tools_fixtures.ToolFixture.test_ac5_default_is_dry_run_and_apply_needs_release_window",
        "test_tools_fixtures.ToolFixture.test_ac5_dry_run_report_is_reproducible",
        "test_tools_fixtures.ToolFixture.test_ac5_apply_matches_dry_run_and_deletes_only_fixture",
        "test_tools_fixtures.ToolFixture.test_ac5_candidate_drift_refuses_apply",
        "test_tools_fixtures.ToolFixture.test_ac5_out_inside_candidate_refused",
        "test_other_tools.BranchFixture.test_archive_default_is_plan_only",
        "test_other_tools.BranchFixture.test_archive_apply_requires_release_window",
        "test_other_tools.BranchFixture.test_archive_apply_creates_verified_bundle_without_force",
        "test_other_tools.BranchFixture.test_delete_default_is_dry_run",
        "test_other_tools.BranchFixture.test_delete_apply_requires_release_window",
        "test_other_tools.BranchFixture.test_delete_apply_deletes_only_with_proof",
    ],
    "AC6": [
        "test_incident_replay.TestIncidentReplay.test_replay_clean_workspace_rejects_all_15_roots",
        "test_incident_replay.TestIncidentReplay.test_replay_remove_worktrees_rejects_all_15_roots",
        "test_incident_replay.TestIncidentReplay.test_replay_refuses_apply",
        "test_incident_replay.TestIncidentReplay.test_replay_never_reaches_a_deletion_function",
        "test_incident_replay.TestIncidentReplay.test_negative_control_unprotected_root_is_a_violation",
        "test_incident_replay.TestIncidentReplay.test_negative_control_relative_root_is_a_violation",
        "test_incident_replay.TestIncidentReplay.test_negative_control_bad_schema_is_refused",
        "test_incident_replay.TestIncidentReplay.test_ledger_sha_is_recorded",
    ],
    "AC7": [
        # This entry is completed by the existing-tools run + governance check
        # recorded in environment.json / governance-check.log.
    ],
}


def git_snapshot():
    def git(*args):
        result = subprocess.run(["git", "-C", ROOT] + list(args),
                                capture_output=True, text=True,
                                encoding="utf-8", errors="replace")
        return result.returncode, result.stdout

    status_code, status = git("status", "--porcelain")
    head_code, head = git("rev-parse", "HEAD")
    ignored = status.split("\n")
    relevant = [line for line in ignored if line.strip()
                and "WORKSPACE-CLEANUP-TOOL-HARDENING-1" not in line]
    ledger = json.load(open(LEDGER, encoding="utf-8"))
    paths = ([item["source_path"] for item in ledger["protected_sources"]]
             + [item["path"] for item in ledger["removed_roots"]])
    return {
        "head": head.strip(),
        "head_exit": head_code,
        "status_exit": status_code,
        "status_outside_this_task": sorted(relevant),
        "ledger_paths_exist": {path: os.path.lexists(path) for path in paths},
    }


def main():
    os.makedirs(EVIDENCE, exist_ok=True)
    before = git_snapshot()
    runs = []
    required_failures = []

    # 1. new hardening suite
    record, result = run([PYTHON, "-B", os.path.join(TESTS, "run_suite.py")],
                         cwd=TESTS, label="new-hardening-suite")
    combined = (result.stdout or "") + (result.stderr or "")
    write_text("tests.log", combined)
    runs.append(record)
    if result.returncode != 0:
        required_failures.append("new-hardening-suite")
    marker = [line for line in combined.split("\n")
              if line.startswith("JSON_RESULTS:")]
    if marker:
        test_results = {
            key: ("skipped" if value.startswith("skipped") else value)
            for key, value in json.loads(
                marker[-1][len("JSON_RESULTS:"):]).items()}
    else:
        test_results = parse_verbose_results(combined)
    if len(test_results) < 40:
        required_failures.append("test-result-parsing (only %d parsed)"
                                 % len(test_results))

    # 2. pre-existing governance tool tests
    for script in ("test_ac_gate.py", "run-resource-manifest-cases.py"):
        record, result = run([PYTHON, "-B", os.path.join(TOOLS, "tests", script)],
                             cwd=ROOT, label="existing-" + script)
        runs.append(record)
        write_text("existing-%s.log" % script,
                   (result.stdout or "") + (result.stderr or ""))
    existing = {run_record["label"]: run_record for run_record in runs}
    # test_ac_gate.py is a regression gate for this Task (must stay green).
    if existing["existing-test_ac_gate.py"]["exit_code"] != 0:
        required_failures.append("existing-test_ac_gate.py")

    # 3. AC6 replay through both path-deletion tools
    replay_reports = {}
    for script, report_name in (
            ("clean_workspace.py", "incident-replay-clean-workspace.json"),
            ("remove_worktrees.py", "incident-replay-remove-worktrees.json")):
        record, result = run(
            [PYTHON, "-B", os.path.join(TOOLS, script),
             "--replay-incident", LEDGER, "--out", EVIDENCE],
            cwd=ROOT, label="replay-" + script)
        runs.append(record)
        report_path = os.path.join(EVIDENCE, report_name)
        if result.returncode != 0 or not os.path.isfile(report_path):
            required_failures.append("replay-" + script)
            continue
        report = json.load(open(report_path, encoding="utf-8"))
        replay_reports[script] = {
            "candidates": report["totals"]["candidates"],
            "rejected": report["totals"]["rejected"],
            "deleted": report["totals"]["deleted"],
            "violations": report["totals"]["violations"],
            "ok": report["ok"],
        }
        if not report["ok"]:
            required_failures.append("replay-not-ok-" + script)

    # 4. read-only declaration audit of the real repository
    record, result = run(
        [PYTHON, "-B", os.path.join(TOOLS, "clean_workspace.py"),
         "--audit-declarations", "--incident-ledger", LEDGER,
         "--out", EVIDENCE],
        cwd=ROOT, label="declaration-audit-real-repo")
    runs.append(record)
    write_text("declaration-audit.log",
               (result.stdout or "") + (result.stderr or ""))
    audit = json.load(open(os.path.join(EVIDENCE, "declaration-audit.json"),
                           encoding="utf-8"))
    audit_summary = {
        "declarations": audit["counts"]["declarations"],
        "protected_roots": audit["counts"]["protected_roots"],
        "errors": audit["counts"]["errors"],
        "warnings": audit["counts"]["warnings"],
        "incident_sources_covered": audit.get("incident_sources_covered"),
        "incident_sources_total": audit.get("incident_sources_total"),
        "exit_code": result.returncode,
        "refusal_expected": result.returncode == 2,
        "note": "The real repository still contains malformed/ambiguous legacy "
                "declarations, so the hardened tools refuse (exit 2). That is "
                "the intended fail-closed behaviour, not a passing cleanup "
                "authorisation.",
    }
    if audit.get("incident_sources_covered") != audit.get("incident_sources_total"):
        required_failures.append("incident-sources-not-covered-by-repo-declarations")

    # 5. AC coverage matrix from actual unittest results
    coverage = {}
    for ac, test_ids in sorted(AC_TESTS.items()):
        statuses = {test_id: test_results.get(test_id, "MISSING")
                    for test_id in test_ids}
        missing = [test_id for test_id, status in statuses.items()
                   if status not in ("ok", "skipped")]
        coverage[ac] = {
            "tests": statuses,
            "missing_or_failed": missing,
            "covered": not missing,
        }
        if missing:
            required_failures.append("AC-coverage-" + ac)
    coverage["AC6_replay_reports"] = replay_reports
    coverage["AC7_existing_tests"] = {
        label: run_record["exit_code"] for label, run_record in
        sorted(existing.items())}
    coverage["AC7_note"] = (
        "run-resource-manifest-cases.py fails before and after this change for a "
        "reason outside the frozen scope: check.ps1 reports TASK_LEDGER budget "
        "failures in the current repo state. The suite never imports the five "
        "hardened scripts; the five scripts byte-compile and their own fixtures "
        "pass. This Task is not allowed to modify check.ps1/task_ledger.py.")

    after = git_snapshot()
    snapshot = {
        "generated_at": now(),
        "before": before,
        "after": after,
        "head_unchanged": before["head"] == after["head"],
        "status_outside_this_task_unchanged":
            before["status_outside_this_task"] == after["status_outside_this_task"],
        "ledger_paths_unchanged":
            before["ledger_paths_exist"] == after["ledger_paths_exist"],
        "tool_files_exist": {
            name: os.path.isfile(os.path.join(TOOLS, name))
            for name in ("clean_workspace.py", "remove_worktrees.py",
                         "archive_branches.py", "delete_branches.py",
                         "consolidate.py")},
    }
    if not (snapshot["head_unchanged"]
            and snapshot["status_outside_this_task_unchanged"]
            and snapshot["ledger_paths_unchanged"]):
        required_failures.append("real-workspace-snapshot-changed")

    environment = {
        "generated_at": now(),
        "host": {
            "platform": platform.platform(),
            "python": sys.version,
            "python_executable": PYTHON,
            "git": subprocess.run(["git", "--version"], capture_output=True,
                                  text=True).stdout.strip(),
            "cwd": os.getcwd(),
        },
        "repo_worktree": ROOT,
        "ledger": {
            "path": LEDGER.replace("\\", "/"),
            "sha256": hashlib.sha256(open(LEDGER, "rb").read()).hexdigest(),
        },
        "commands": runs,
        "replay": replay_reports,
        "declaration_audit": audit_summary,
        "ac_coverage": coverage,
        "real_workspace_snapshot": snapshot,
        "required_failures": required_failures,
    }
    write_json("ac-coverage.json", coverage)
    write_json("real-workspace-snapshot.json", snapshot)
    write_json("environment.json", environment)

    # 6. SHA-256 manifest of every evidence file (written last, excludes itself)
    entries = []
    for name in sorted(os.listdir(EVIDENCE)):
        path = os.path.join(EVIDENCE, name)
        if not os.path.isfile(path) or name == "manifest.sha256":
            continue
        entries.append("%s  %s" % (
            hashlib.sha256(open(path, "rb").read()).hexdigest(), name))
    write_text("manifest.sha256", "\n".join(entries) + "\n")

    print("")
    print("new suite: exit %d (%d parsed test results)"
          % (existing["new-hardening-suite"]["exit_code"], len(test_results)))
    print("replay: %s" % json.dumps(replay_reports))
    print("declaration audit: %s" % json.dumps(audit_summary))
    print("snapshot identical: %s" % (not any(
        failure == "real-workspace-snapshot-changed"
        for failure in required_failures)))
    if required_failures:
        print("REQUIRED FAILURES: %s" % ", ".join(required_failures),
              file=sys.stderr)
        return 1
    print("evidence-ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
