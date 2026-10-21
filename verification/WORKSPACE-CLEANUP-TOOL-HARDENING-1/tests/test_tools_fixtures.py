# -*- coding: utf-8 -*-
"""AC2/AC3/AC4/AC5 end-to-end fixture tests for the hardened tools.

Every scenario builds an isolated repository + workspace under %TEMP% and proves
that the tool refuses (or, for the explicit apply tests, only touches the
fixture).  The AC4 matrix names one test per required fault-injection scenario:

  01 nested root                  07 non-standard worktree location
  02 bare declaration path        08 stash non-zero exit
  03 relative path                09 permission denied
  04 non-standard table columns   10 duplicate / alias path
  05 PRESERVE_UNKNOWN             11 symlink / escape path
  06 parent-directory protection
"""
import os
import shutil
import subprocess
import sys
import unittest

from fixture_support import (RepoFixture, acceptance_digest_from_report,
                             acceptance_digest_from_worktree_report, guard,
                             load_json, make_release_window, run_tool, utc_now,
                             write_json)

import clean_workspace  # noqa: E402
import remove_worktrees  # noqa: E402

AC4_SCENARIOS = {
    "01_nested_root": "test_ac4_01_nested_root",
    "02_bare_declaration_path": "test_ac4_02_bare_declaration_path",
    "03_relative_path": "test_ac4_03_relative_path",
    "04_nonstandard_table_columns": "test_ac4_04_nonstandard_table_columns",
    "05_preserve_unknown": "test_ac4_05_preserve_unknown",
    "06_parent_protection": "test_ac4_06_parent_protection",
    "07_nonstandard_worktree_location":
        "test_ac4_07_nonstandard_worktree_location",
    "08_stash_nonzero": "test_ac4_08_stash_nonzero",
    "09_permission_denied": "test_ac4_09_permission_denied",
    "10_duplicate_alias_path": "test_ac4_10_duplicate_alias_path",
    "11_symlink_escape": "test_ac4_11_symlink_escape",
}


def make_junction(link, target):
    """Windows directory junction; returns True when created."""
    result = subprocess.run(["cmd", "/c", "mklink", "/J", link, target],
                            capture_output=True, text=True, encoding="utf-8",
                            errors="replace")
    return result.returncode == 0 and os.path.isdir(link)


def force_write(path, text):
    """Overwrite a file git marks hidden/read-only (the worktree ``.git`` file)."""
    subprocess.run(["attrib", "-H", "-R", path], capture_output=True, text=True)
    try:
        os.chmod(path, 0o666)
    except OSError:
        pass
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


class ToolFixture(unittest.TestCase):
    def setUp(self):
        self.fx = RepoFixture(prefix="wc-tools-")
        self.addCleanup(self.fx.cleanup)
        self.roots = [guard.norm_abs(os.path.join(self.fx.ws, name))
                      for name in ("builds", "review-scratch", "temp", "tmp")]
        self.temp_root = guard.norm_abs(os.path.join(self.fx.ws, "temp"))

    # -- helpers -----------------------------------------------------------
    def run_clean(self, *args):
        return run_tool("clean_workspace.py", "--repo", self.fx.repo,
                        "--workspace-root", self.fx.ws, "--out", self.fx.out,
                        *args)

    def run_worktrees(self, inventory, *args):
        return run_tool("remove_worktrees.py", "--repo", self.fx.repo,
                        "--workspace-root", self.fx.ws, "--inventory", inventory,
                        "--out", self.fx.out, *args)

    def report(self, name):
        return load_json(os.path.join(self.fx.out, name))

    def candidate(self, report, normalized):
        for item in report["candidates"]:
            if item.get("normalized") == normalized:
                return item
        self.fail("candidate %s not found in report" % normalized)

    def worktree_record(self, report, normalized):
        for item in report["worktrees"]:
            if item.get("normalized") == normalized:
                return item
        self.fail("worktree %s not found in report" % normalized)

    def make_clean_record(self, report_name="clean-workspace-dryrun.json",
                          acceptance=None):
        report = self.report(report_name)
        record = os.path.join(self.fx.tmp, "release-window.json")
        acceptance_block = acceptance
        if acceptance is None and any(
                item.get("inventory", {}).get("requires_acceptance")
                for item in report["candidates"]
                if item["decision"] == "CANDIDATE"):
            acceptance_block = {
                "reviewed": True,
                "reviewer": "unit-test",
                "reference": "fixture",
                "inventory_sha256": acceptance_digest_from_report(report),
            }
        make_release_window(
            record, "clean_workspace.py", guard.norm_abs(self.fx.repo),
            guard.norm_abs(self.fx.ws), self.roots,
            report["candidates_sha256"], report["candidate_count"],
            dry_run_report=os.path.join(self.fx.out, report_name),
            inventory_acceptance=acceptance_block)
        return record

    def make_worktree_record(self, report_name,
                             acceptance):
        report = self.report(report_name)
        record = os.path.join(self.fx.tmp, "worktree-release-window.json")
        make_release_window(
            record, "remove_worktrees.py", guard.norm_abs(self.fx.repo),
            guard.norm_abs(self.fx.ws),
            [guard.norm_abs(os.path.join(self.fx.ws, "worktrees"))],
            report["candidates_sha256"], report["candidate_count"],
            dry_run_report=os.path.join(self.fx.out, report_name),
            inventory_acceptance=acceptance)
        return record

    # ==================================================================
    # AC4 matrix
    # ==================================================================
    def test_ac4_matrix_is_complete(self):
        for scenario, method in AC4_SCENARIOS.items():
            self.assertTrue(callable(getattr(self, method, None)),
                            "missing test for AC4 scenario %s" % scenario)
        self.assertEqual(len(AC4_SCENARIOS), 11)

    def test_ac4_01_nested_root(self):
        """A preserved root nested inside a managed area is protected exactly."""
        protected = os.path.join(self.fx.ws, "temp", "NESTED-ROOT")
        self.fx.declare([(protected, "PRESERVE_REFERENCED")])
        self.fx.candidate("temp", "NESTED-ROOT", {"deep/child.bin": "keep me"})
        result = self.run_clean()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = self.report("clean-workspace-dryrun.json")
        record = self.candidate(report, guard.norm_abs(protected))
        self.assertEqual(record["decision"], "REJECT")
        self.assertTrue(any("exact_source_path" in reason
                            for reason in record["reasons"]))
        self.assertEqual(report["totals"]["would_delete"], 0)
        self.assertTrue(os.path.isdir(protected))

    def test_ac4_02_bare_declaration_path(self):
        """A path in a table cell without backticks is still protection (r208)."""
        protected = os.path.join(self.fx.ws, "temp", "BARE-PATH")
        self.fx.declare([(protected, "PRESERVE_REFERENCED")])
        self.fx.candidate("temp", "BARE-PATH", {"file.txt": "data"})
        declaration = os.path.join(self.fx.repo, "doc", "tasks",
                                   "FIXTURE-RESOURCES.md")
        with open(declaration, encoding="utf-8") as handle:
            text = handle.read()
        self.assertNotIn("`" + protected.replace("\\", "/") + "`", text)
        result = self.run_clean()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = self.report("clean-workspace-dryrun.json")
        record = self.candidate(report, guard.norm_abs(protected))
        self.assertEqual(record["decision"], "REJECT")
        self.assertTrue(os.path.isdir(protected))

    def test_ac4_03_relative_path(self):
        """A relative deletion candidate has no provable identity (AC2)."""
        worktree = self.fx.make_worktree("REL-WT", "rel-branch")
        inventory = self.fx.write_inventory(
            [{"path": "worktrees/REL-WT", "branch": "rel-branch"}])
        result = self.run_worktrees(inventory)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("INVENTORY_PATH_NOT_ABSOLUTE", result.stderr)
        self.assertTrue(os.path.isdir(worktree))

    def test_ac4_04_nonstandard_table_columns(self):
        """A resource row with a non-standard column count is a refusal (AC2)."""
        raw = "\n".join([
            "# fixture",
            "",
            "## Resource Manifest",
            "",
            "| resource_type | source_path | disposition | destination_path | "
            "sha256/manifest | reference/process check and result |",
            "|---|---|---|---|---|---|",
            "| scratch | G:/nope/nope | PRESERVE_REFERENCED | - | - | one | two |",
            "",
        ])
        self.fx.declare_raw(raw)
        target = self.fx.candidate("temp", "ARITY-CANDIDATE", {"f.txt": "x"})
        result = self.run_clean()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        output = result.stdout + result.stderr
        self.assertIn("TABLE_ROW_ARITY", output)
        self.assertIn("declaration integrity", output)
        self.assertTrue(os.path.isdir(target))

    def test_ac4_05_preserve_unknown(self):
        protected = os.path.join(self.fx.ws, "review-scratch", "UNKNOWN-SOURCE")
        self.fx.declare([(protected, "PRESERVE_UNKNOWN")])
        self.fx.candidate("review-scratch", "UNKNOWN-SOURCE", {"x.bin": "x"})
        result = self.run_clean()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = self.report("clean-workspace-dryrun.json")
        record = self.candidate(report, guard.norm_abs(protected))
        self.assertEqual(record["decision"], "REJECT")
        self.assertIn("PRESERVE_UNKNOWN", " ".join(record["reasons"]))
        self.assertEqual(report["totals"]["would_delete"], 0)

    def test_ac4_06_parent_protection(self):
        """Deleting a parent of a preserved root is refused (ancestor coverage)."""
        worktree = self.fx.make_worktree("PARENT-WT", "parent-branch")
        nested_source = os.path.join(worktree, "inner-preserved")
        os.makedirs(nested_source, exist_ok=True)
        with open(os.path.join(nested_source, "state.bin"), "w",
                  encoding="utf-8") as handle:
            handle.write("preserved bytes")
        self.fx.declare([(nested_source, "PRESERVE_REFERENCED")])
        inventory = self.fx.write_inventory(
            [{"path": worktree, "branch": "parent-branch"}])
        result = self.run_worktrees(inventory)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = self.report("worktree-removal-dryrun.json")
        record = self.worktree_record(report, guard.norm_abs(worktree))
        self.assertEqual(record["decision"], "REJECT")
        self.assertTrue(any("ancestor_of_preserved_source" in reason
                            for reason in record["reasons"]), record["reasons"])
        self.assertTrue(os.path.isdir(worktree))

    def test_ac4_07_nonstandard_worktree_location(self):
        """r208 ROOT-07 lived under `New Manga.worktrees/` and was deleted."""
        worktree = self.fx.make_worktree("ODD-WT", "odd-branch",
                                         location="legacy-location")
        inventory = self.fx.write_inventory(
            [{"path": worktree, "branch": "odd-branch"}])
        result = self.run_worktrees(inventory)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = self.report("worktree-removal-dryrun.json")
        record = self.worktree_record(report, guard.norm_abs(worktree))
        self.assertEqual(record["decision"], "REJECT")
        self.assertTrue(any("NON_STANDARD_WORKTREE_LOCATION" in reason
                            for reason in record["reasons"]))
        self.assertTrue(os.path.isdir(worktree))

    def test_ac4_08_stash_nonzero(self):
        """A failed `git stash list` is a refusal, never an empty result."""
        broken = os.path.join(self.fx.tmp, "broken-gitdir")
        os.makedirs(broken, exist_ok=True)
        with open(os.path.join(broken, ".git"), "w", encoding="utf-8") as handle:
            handle.write("gitdir: C:/definitely/not/a/git/dir\n")
        with self.assertRaises(guard.GuardError) as caught:
            guard.git_stash_entries(broken)
        self.assertEqual(caught.exception.code, "GIT_CMD_FAILED")
        self.assertIn("git stash list", caught.exception.message)

        worktree = self.fx.make_worktree("STASH-WT", "stash-branch")
        inventory = self.fx.write_inventory(
            [{"path": worktree, "branch": "stash-branch"}])
        config = {"repo": guard.norm_abs(self.fx.repo),
                  "ws": guard.norm_abs(self.fx.ws), "inventory": inventory,
                  "out": self.fx.out, "apply": False, "release_window": None,
                  "replay": None}
        original = guard.git_stash_entries

        def failing(_path):
            raise guard.GuardError("GIT_STASH_FAILED",
                                   "git stash list failed (exit 128)")

        guard.git_stash_entries = failing
        try:
            report, _, _ = remove_worktrees.build_worktree_report(config)
        finally:
            guard.git_stash_entries = original
        record = [item for item in report["worktrees"]
                  if item["normalized"] == guard.norm_abs(worktree)][0]
        self.assertEqual(record["decision"], "REJECT")
        self.assertIn("GIT_STASH_FAILED", " ".join(record["reasons"]))
        self.assertTrue(os.path.isdir(worktree))

    def test_ac4_09_permission_denied(self):
        """An unreadable file refuses the candidate instead of skipping it."""
        target = self.fx.candidate("temp", "PERMISSION-CANDIDATE",
                                   {"a.txt": "alpha"})
        original = guard.sha256_file

        def denied(_path):
            raise guard.GuardError("PERMISSION_DENIED",
                                   "simulated denial while hashing")

        guard.sha256_file = denied
        try:
            config = {"repo": guard.norm_abs(self.fx.repo),
                      "ws": guard.norm_abs(self.fx.ws),
                      "roots": (("review-scratch", "review-scratch"),
                                ("builds", "builds"), ("temp", "temp"),
                                ("tmp", "tmp")),
                      "root_norm": {}, "out": self.fx.out, "apply": False,
                      "release_window": None, "replay": None, "audit": False,
                      "incident_ledger": None}
            for area in ("review-scratch", "builds", "temp", "tmp"):
                config["root_norm"][area] = guard.norm_abs(
                    os.path.join(self.fx.ws, area))
            index, _scanned = clean_workspace.scan_repo_declarations(
                config["repo"], config["ws"])
            report, _inventories = clean_workspace.build_clean_report(
                config, index, {})
        finally:
            guard.sha256_file = original
        record = self.candidate(report, guard.norm_abs(target))
        self.assertEqual(record["decision"], "REJECT")
        self.assertIn("PERMISSION_DENIED", " ".join(record["reasons"]))
        self.assertTrue(os.path.isdir(target))

    def test_ac4_10_duplicate_alias_path(self):
        """Duplicate spellings collapse to one identity; a junction is an alias."""
        worktree = self.fx.make_worktree("DUP-WT", "dup-branch")
        inventory = self.fx.write_inventory([
            {"path": worktree, "branch": "dup-branch"},
            {"path": worktree.replace("/", "\\") + "\\", "branch": "dup-branch"},
            {"path": os.path.join(self.fx.ws, "worktrees", ".", "DUP-WT"),
             "branch": "dup-branch"},
        ])
        result = self.run_worktrees(inventory)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = self.report("worktree-removal-dryrun.json")
        self.assertEqual(report["inventory"]["unique_entries"], 1)
        self.assertEqual(len(report["inventory"]["duplicate_entries"]), 2)
        self.assertEqual(len([item for item in report["worktrees"]
                              if item["normalized"] == guard.norm_abs(worktree)]),
                         1)
        self.assertTrue(os.path.isdir(worktree))

        real = self.fx.candidate("temp", "ALIAS-TARGET", {"f.txt": "x"})
        alias = os.path.join(self.fx.ws, "temp", "ALIAS-JUNCTION")
        if not make_junction(alias, real):
            self.skipTest("directory junctions are not supported on this host")
        result = self.run_clean()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = self.report("clean-workspace-dryrun.json")
        record = self.candidate(report, guard.norm_abs(alias))
        self.assertEqual(record["decision"], "REJECT")
        self.assertTrue(any("PATH_ALIAS" in reason
                            for reason in record["reasons"]))
        shutil.rmtree(alias, ignore_errors=True)

    def test_ac4_11_symlink_escape(self):
        """A junction pointing outside the managed root cannot be deleted."""
        outside = os.path.join(self.fx.tmp, "outside-workspace")
        os.makedirs(outside, exist_ok=True)
        with open(os.path.join(outside, "user-data.bin"), "w",
                  encoding="utf-8") as handle:
            handle.write("outside data")
        escape = os.path.join(self.fx.ws, "temp", "ESCAPE-LINK")
        os.makedirs(os.path.dirname(escape), exist_ok=True)
        if not make_junction(escape, outside):
            self.skipTest("directory junctions are not supported on this host")
        result = self.run_clean()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = self.report("clean-workspace-dryrun.json")
        record = self.candidate(report, guard.norm_abs(escape))
        self.assertEqual(record["decision"], "REJECT")
        self.assertTrue(any("PATH_ALIAS" in reason
                            for reason in record["reasons"]))
        self.assertTrue(os.path.exists(os.path.join(outside, "user-data.bin")))
        shutil.rmtree(escape, ignore_errors=True)

    # ==================================================================
    # AC2 additional e2e checks
    # ==================================================================
    def test_ac2_git_status_failure_is_refused(self):
        worktree = self.fx.make_worktree("BROKEN-WT", "broken-branch")
        git_file = os.path.join(worktree, ".git")
        force_write(git_file, "gitdir: C:/definitely/not/a/git/dir\n")
        inventory = self.fx.write_inventory(
            [{"path": worktree, "branch": "broken-branch"}])
        result = self.run_worktrees(inventory)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = self.report("worktree-removal-dryrun.json")
        record = self.worktree_record(report, guard.norm_abs(worktree))
        self.assertEqual(record["decision"], "REJECT")
        self.assertIn("GIT_CMD_FAILED", " ".join(record["reasons"]))
        self.assertTrue(os.path.isdir(worktree))

    def test_ac2_tampered_inventory_schema_is_refused(self):
        worktree = self.fx.make_worktree("SCHEMA-WT", "schema-branch")
        path = os.path.join(self.fx.tmp, "tampered-inventory.json")
        write_json(path, {"worktrees": [{"path": worktree}],
                          "protected_worktree_names": {}})
        result = self.run_worktrees(path)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("INVENTORY_SCHEMA", result.stderr)
        self.assertTrue(os.path.isdir(worktree))

    def test_audit_declarations_refuses_unknown_disposition(self):
        self.fx.declare([(os.path.join(self.fx.ws, "temp", "X"),
                          "CLEANED_BY_OWNER")])
        result = run_tool("clean_workspace.py", "--repo", self.fx.repo,
                          "--workspace-root", self.fx.ws, "--audit-declarations",
                          "--out", self.fx.out)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        report = self.report("declaration-audit.json")
        codes = [error["code"] for error in report["errors"]]
        self.assertIn("DECL_UNKNOWN_DISPOSITION", codes)

    # ==================================================================
    # AC3 pre-delete inventory
    # ==================================================================
    def test_ac3_ignored_content_blocks_apply_until_accepted(self):
        worktree = self.fx.make_worktree("IGNORED-WT", "ignored-branch")
        ignored_dir = os.path.join(worktree, "node_modules")
        os.makedirs(ignored_dir)
        ignored_file = os.path.join(ignored_dir, "payload.bin")
        with open(ignored_file, "wb") as handle:
            handle.write(b"ignored but not cache")
        self.assertEqual(self.fx.git("status", "--porcelain", cwd=worktree)
                         .stdout.strip(), "",
                         "ignored content must be invisible to git status")
        inventory = self.fx.write_inventory(
            [{"path": worktree, "branch": "ignored-branch"}])
        result = self.run_worktrees(inventory)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = self.report("worktree-removal-dryrun.json")
        record = self.worktree_record(report, guard.norm_abs(worktree))
        self.assertEqual(record["decision"], "CANDIDATE")
        self.assertEqual(record["inventory"]["counts"]["git_ignored"], 1)
        inventory_files = os.listdir(os.path.join(self.fx.out, "inventory"))
        self.assertEqual(len(inventory_files), 1)
        detail = load_json(os.path.join(self.fx.out, "inventory",
                                        inventory_files[0]))
        entry = [item for item in detail["entries"]
                 if item["path"] == "node_modules/payload.bin"][0]
        self.assertEqual(entry["size"], len(b"ignored but not cache"))
        self.assertEqual(entry["sha256"],
                         guard.sha256_file(ignored_file))
        self.assertEqual(entry["origin"], "git_ignored")

        # Apply without an inventory acceptance block: refused, nothing removed.
        record_path = self.make_worktree_record(
            "worktree-removal-dryrun.json", acceptance=None)
        result = self.run_worktrees(inventory, "--apply", "--release-window",
                                    record_path)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("INVENTORY_ACCEPTANCE_MISSING",
                      result.stdout + result.stderr)
        self.assertTrue(os.path.isdir(worktree))

        # Apply with a stale acceptance hash: refused, nothing removed.
        bad_record = self.make_worktree_record(
            "worktree-removal-dryrun.json",
            acceptance={"reviewed": True, "reviewer": "unit-test",
                        "reference": "fixture",
                        "inventory_sha256": "0" * 64})
        result = self.run_worktrees(inventory, "--apply", "--release-window",
                                    bad_record)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("INVENTORY_ACCEPTANCE_MISMATCH",
                      result.stdout + result.stderr)
        self.assertTrue(os.path.isdir(worktree))

        # Accepted inventory: the fixture worktree (and only it) is removed.
        good_record = self.make_worktree_record(
            "worktree-removal-dryrun.json",
            acceptance={"reviewed": True, "reviewer": "unit-test",
                        "reference": "fixture",
                        "inventory_sha256":
                            acceptance_digest_from_worktree_report(report)})
        result = self.run_worktrees(inventory, "--apply", "--release-window",
                                    good_record)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        apply_report = self.report("worktree-removal-apply.json")
        self.assertEqual(apply_report["totals"]["deleted"], 1)
        self.assertFalse(os.path.exists(worktree))

    # ==================================================================
    # AC5 dry-run / apply decoupling
    # ==================================================================
    def test_ac5_default_is_dry_run_and_apply_needs_release_window(self):
        target = self.fx.candidate("temp", "DEFAULT-DRYRUN", {"f.txt": "x"})
        result = self.run_clean()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = self.report("clean-workspace-dryrun.json")
        self.assertEqual(report["mode"], "dry_run")
        self.assertEqual(report["totals"]["would_delete"], 1)
        self.assertTrue(os.path.isdir(target))

        result = self.run_clean("--apply")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("APPLY_NEEDS_RELEASE_WINDOW",
                      result.stdout + result.stderr)
        self.assertTrue(os.path.isdir(target))

    def test_ac5_dry_run_report_is_reproducible(self):
        self.fx.candidate("temp", "REPRO-A", {"a.txt": "alpha"})
        self.fx.candidate("temp", "REPRO-B", {"b.txt": "beta"})
        first = self.run_clean()
        self.assertEqual(first.returncode, 0, first.stderr)
        report_one = self.report("clean-workspace-dryrun.json")
        second = self.run_clean()
        self.assertEqual(second.returncode, 0, second.stderr)
        report_two = self.report("clean-workspace-dryrun.json")
        self.assertEqual(report_one["report_sha256"],
                         report_two["report_sha256"])
        self.assertEqual(report_one["candidates_sha256"],
                         report_two["candidates_sha256"])

    def test_ac5_apply_matches_dry_run_and_deletes_only_fixture(self):
        target = self.fx.candidate("temp", "APPLY-ME",
                                   {"one.txt": "one", "two.bin": "two"})
        keeper = self.fx.candidate("temp", "KEEP-ME", {"keep.txt": "keep"})
        self.fx.declare([(keeper, "PRESERVE_REFERENCED")])
        dry = self.run_clean()
        self.assertEqual(dry.returncode, 0, dry.stderr)
        dry_report = self.report("clean-workspace-dryrun.json")
        self.assertEqual(dry_report["totals"]["would_delete"], 1)
        record = self.make_clean_record()
        apply_result = self.run_clean("--apply", "--release-window", record)
        self.assertEqual(apply_result.returncode, 0,
                         apply_result.stdout + apply_result.stderr)
        apply_report = self.report("clean-workspace-apply.json")
        self.assertEqual(apply_report["candidates_sha256"],
                         dry_report["candidates_sha256"])
        self.assertEqual(apply_report["totals"]["deleted"], 1)
        self.assertEqual([item["normalized"]
                          for item in apply_report["apply"]["deleted"]],
                         [guard.norm_abs(target)])
        self.assertFalse(os.path.exists(target))
        self.assertTrue(os.path.isdir(keeper))

    def test_ac5_candidate_drift_refuses_apply(self):
        first = self.fx.candidate("temp", "DRIFT-A", {"a.txt": "alpha"})
        self.assertEqual(self.run_clean().returncode, 0)
        record = self.make_clean_record()
        second = self.fx.candidate("temp", "DRIFT-B", {"b.txt": "beta"})
        result = self.run_clean("--apply", "--release-window", record)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("WINDOW_CANDIDATE_DRIFT", result.stdout + result.stderr)
        self.assertTrue(os.path.isdir(first))
        self.assertTrue(os.path.isdir(second))


if __name__ == "__main__":
    import clean_workspace
    import remove_worktrees
    unittest.main(verbosity=2)
