# -*- coding: utf-8 -*-
"""Regression tests for the three non-path-deletion tools (AC2/AC5/AC7).

Covers:
  * ``consolidate.py``: fail-closed Git handling, path-identity protection and
    shape compatibility of ``inventory.json`` for the deletion tools;
  * ``archive_branches.py``: dry-run default, no ``-f`` tag overwrite, no bundle
    overwrite, bundle verified before it is claimed, release-window gate;
  * ``delete_branches.py``: stale inventory refusal, incomplete-archive refusal,
    release-window gate, merged ``-d`` / unmerged ``-D`` only after proof.
"""
import os
import subprocess
import sys
import unittest

from fixture_support import (RepoFixture, guard, load_json, make_release_window,
                             run_tool, write_json)

import archive_branches  # noqa: E402
import consolidate  # noqa: E402
import delete_branches  # noqa: E402
import remove_worktrees  # noqa: E402


class BranchFixture(unittest.TestCase):
    """Repository with a merged branch and an unmerged worktree branch."""

    def setUp(self):
        self.fx = RepoFixture(prefix="wc-branches-")
        self.addCleanup(self.fx.cleanup)
        self.fx.write("shared.txt", "base\n")
        self.fx.commit("base")
        self.fx.git("checkout", "-q", "-b", "feature-merged")
        self.fx.write("merged.txt", "merged\n")
        self.fx.commit("merged work")
        self.fx.git("checkout", "-q", "main")
        merge = self.fx.git("merge", "-q", "--no-ff", "feature-merged",
                            "-m", "merge feature-merged", check=False)
        self.assertEqual(merge.returncode, 0, merge.stderr)
        self.worktree = self.fx.make_worktree("UNMERGED-WT", "feature-unmerged")
        self.fx.write_abs(os.path.join(self.worktree, "unique.txt"), "unique\n")
        self.fx.git("add", "-A", cwd=self.worktree)
        self.fx.git("commit", "-q", "-m", "unique unmerged commit",
                    cwd=self.worktree)
        self.branches = self._inventory_branches()

    def _inventory_branches(self):
        tips = guard.git_branch_tips(guard.norm_abs(self.fx.repo))
        merged_out = guard.git_checked(guard.norm_abs(self.fx.repo), "branch",
                                       "--merged", "main",
                                       "--format=%(refname:short)")
        merged = {line.strip() for line in merged_out.split("\n") if line.strip()}
        rows = []
        for branch in sorted(tips):
            unique = int(guard.git_checked(
                guard.norm_abs(self.fx.repo), "rev-list", "--count",
                "main..%s" % branch).strip())
            rows.append({"branch": branch, "merged": branch in merged,
                         "unique_commits": unique,
                         "tip": tips[branch], "tip_date": "2026-10-21",
                         "checked_out_at": [],
                         "is_mainline": branch == "main"})
        return rows

    def _inventory(self, mutate=None):
        rows = [dict(row) for row in self.branches]
        if mutate:
            mutate(rows, self)
        return self.fx.write_branches_inventory(rows)

    # ==================================================================
    # consolidate.py
    # ==================================================================
    def test_consolidate_builds_path_identity_inventory(self):
        self.fx.declare([(self.worktree, "PRESERVE_REFERENCED")])
        out = os.path.join(self.fx.tmp, "consolidate-out")
        result = run_tool("consolidate.py", "--repo", self.fx.repo,
                          "--workspace-root", self.fx.ws, "--mainline", "main",
                          "--out", out)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        inventory = load_json(os.path.join(out, "inventory.json"))
        self.assertEqual(inventory["mainline"], "main")
        self.assertEqual(inventory["counts"]["merged"], 2)
        self.assertEqual(inventory["counts"]["unmerged"], 1)
        names = list(inventory["protected_worktree_names"])
        self.assertIn("UNMERGED-WT", names)
        protected = [row for row in inventory["worktrees"]
                     if row["normalized"] == guard.norm_abs(self.worktree)][0]
        self.assertTrue(protected["protected"])
        self.assertEqual(protected["inspection"], "OK")
        self.assertEqual(protected["stashes"], 0)
        branch_row = [row for row in inventory["branches"]
                      if row["branch"] == "feature-unmerged"][0]
        self.assertFalse(branch_row["merged"])
        self.assertEqual(branch_row["tip"],
                         guard.git_branch_tips(guard.norm_abs(self.fx.repo))[
                             "feature-unmerged"])
        self.assertTrue(os.path.isfile(os.path.join(out, "inventory.md")))
        # The deletion tools must be able to consume the generated inventory.
        path = os.path.join(out, "inventory.json")
        _data, entries, protected_names, duplicates = \
            remove_worktrees.load_inventory(path)
        self.assertEqual(duplicates, [])
        self.assertIn("UNMERGED-WT", protected_names)

    def test_consolidate_missing_mainline_is_refused(self):
        result = run_tool("consolidate.py", "--repo", self.fx.repo,
                          "--workspace-root", self.fx.ws, "--mainline", "nope")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("MAINLINE_MISSING", result.stderr)

    def test_consolidate_inspection_failure_is_not_silently_none(self):
        git_file = os.path.join(self.worktree, ".git")
        subprocess.run(["attrib", "-H", "-R", git_file],
                       capture_output=True, text=True)
        try:
            os.chmod(git_file, 0o666)
        except OSError:
            pass
        with open(git_file, "w", encoding="utf-8") as handle:
            handle.write("gitdir: C:/definitely/not/a/git/dir\n")
        out = os.path.join(self.fx.tmp, "consolidate-out")
        result = run_tool("consolidate.py", "--repo", self.fx.repo,
                          "--workspace-root", self.fx.ws, "--mainline", "main",
                          "--out", out)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("REFUSE", result.stderr)
        inventory = load_json(os.path.join(out, "inventory.json"))
        self.assertEqual(inventory["counts"]["inspection_errors"], 1)
        broken = [row for row in inventory["worktrees"]
                  if row["normalized"] == guard.norm_abs(self.worktree)][0]
        self.assertEqual(broken["inspection"], "FAILED")
        self.assertIsNone(broken["dirty_entries"])

    # ==================================================================
    # archive_branches.py
    # ==================================================================
    def test_archive_default_is_plan_only(self):
        inventory = self._inventory()
        result = self._archive(inventory)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = load_json(os.path.join(self.fx.out, "archive-plan-dryrun.json"))
        self.assertEqual(report["mode"], "dry_run")
        self.assertEqual(report["totals"]["planned"], 1)
        self.assertEqual(report["plan"][0]["branch"], "feature-unmerged")
        self.assertFalse(self._tag_exists())
        self.assertFalse(os.path.isdir(os.path.join(self.fx.ws, "archive")))
        self.assertEqual(self.fx.git("status", "--porcelain").stdout.strip(), "")

    def test_archive_apply_requires_release_window(self):
        inventory = self._inventory()
        result = self._archive(inventory, "--apply")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("APPLY_NEEDS_RELEASE_WINDOW", result.stderr)
        self.assertFalse(self._tag_exists())

    def test_archive_apply_creates_verified_bundle_without_force(self):
        inventory = self._inventory()
        result = self._archive(inventory)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = load_json(os.path.join(self.fx.out, "archive-plan-dryrun.json"))
        record = self._archive_window(report)
        result = self._archive(inventory, "--apply", "--release-window", record)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        apply_report = load_json(os.path.join(
            self.fx.out, "archive-manifest-apply.json"))
        self.assertEqual(apply_report["totals"]["archived"], 1)
        self.assertEqual(apply_report["totals"]["failed"], 0)
        archived = apply_report["archived"][0]
        self.assertTrue(archived["verified"])
        self.assertEqual(archived["tip"], guard.git_branch_tips(
            guard.norm_abs(self.fx.repo))["feature-unmerged"])
        self.assertTrue(os.path.isfile(archived["bundle"]))
        verify = self.fx.git("bundle", "verify", archived["bundle"], check=False)
        self.assertEqual(verify.returncode, 0, verify.stderr)
        self.assertTrue(self._tag_exists())

        # A second run must refuse to overwrite the existing bundle (no -f).
        result = self._archive(inventory)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        refused = load_json(os.path.join(self.fx.out,
                                         "archive-plan-refused.json"))
        self.assertEqual(refused["conflicts"][0]["why"], "BUNDLE_EXISTS")

    def test_archive_stale_inventory_is_refused(self):
        inventory = self._inventory(
            lambda rows, fixture: [row.__setitem__("merged", True)
                                   for row in rows
                                   if row["branch"] == "feature-unmerged"])
        result = self._archive(inventory)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        report = load_json(os.path.join(self.fx.out, "archive-plan-refused.json"))
        self.assertEqual(report["conflicts"][0]["why"], "INVENTORY_STALE")

    def _archive(self, inventory, *extra):
        return run_tool("archive_branches.py", "--repo", self.fx.repo,
                        "--workspace-root", self.fx.ws, "--mainline", "main",
                        "--inventory", inventory, "--out", self.fx.out, *extra)

    def _archive_window(self, report):
        bundles = guard.norm_abs(os.path.join(self.fx.ws, "archive", "bundles"))
        record = os.path.join(self.fx.tmp, "archive-window.json")
        make_release_window(
            record, "archive_branches.py", guard.norm_abs(self.fx.repo),
            guard.norm_abs(self.fx.ws), [bundles],
            report["candidates_sha256"], report["candidate_count"],
            dry_run_report=os.path.join(self.fx.out, "archive-plan-dryrun.json"))
        return record

    def _tag_exists(self):
        return self.fx.git("rev-parse", "--verify", "--quiet",
                           "refs/tags/archive/feature-unmerged",
                           check=False).returncode == 0

    # ==================================================================
    # delete_branches.py
    # ==================================================================
    def _detach_worktree(self):
        if os.path.isdir(self.worktree):
            result = self.fx.git("worktree", "remove", self.worktree,
                                 check=False)
            self.assertEqual(result.returncode, 0, result.stderr)

    def _prepare_archive_proof(self):
        inventory = self._inventory()
        self.assertEqual(self._archive(inventory).returncode, 0)
        report = load_json(os.path.join(self.fx.out, "archive-plan-dryrun.json"))
        record = self._archive_window(report)
        result = self._archive(inventory, "--apply", "--release-window", record)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self._detach_worktree()
        return inventory, os.path.join(self.fx.out, "archive-manifest-apply.json")

    def _delete(self, inventory, manifest, *extra):
        return run_tool("delete_branches.py", "--repo", self.fx.repo,
                        "--workspace-root", self.fx.ws, "--mainline", "main",
                        "--inventory", inventory,
                        "--archive-manifest", manifest,
                        "--out", self.fx.out, *extra)

    def _delete_window(self, report):
        record = os.path.join(self.fx.tmp, "delete-window.json")
        make_release_window(
            record, "delete_branches.py", guard.norm_abs(self.fx.repo),
            guard.norm_abs(self.fx.ws), [guard.norm_abs(self.fx.repo)],
            report["candidates_sha256"], report["candidate_count"],
            dry_run_report=os.path.join(self.fx.out,
                                        "branch-deletion-dryrun.json"))
        return record

    def test_delete_default_is_dry_run(self):
        inventory, manifest = self._prepare_archive_proof()
        result = self._delete(inventory, manifest)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = load_json(os.path.join(self.fx.out, "branch-deletion-dryrun.json"))
        self.assertEqual(report["mode"], "dry_run")
        self.assertEqual(report["totals"]["planned"], 2)  # merged + unmerged
        self.assertTrue(self.fx.git("rev-parse", "--verify", "--quiet",
                                    "refs/heads/feature-merged",
                                    check=False).returncode == 0)
        self.assertTrue(self.fx.git("rev-parse", "--verify", "--quiet",
                                    "refs/heads/feature-unmerged",
                                    check=False).returncode == 0)

    def test_delete_apply_requires_release_window(self):
        inventory, manifest = self._prepare_archive_proof()
        result = self._delete(inventory, manifest, "--apply")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("APPLY_NEEDS_RELEASE_WINDOW", result.stderr)

    def test_delete_apply_deletes_only_with_proof(self):
        inventory, manifest = self._prepare_archive_proof()
        self.assertEqual(self._delete(inventory, manifest).returncode, 0)
        report = load_json(os.path.join(self.fx.out, "branch-deletion-dryrun.json"))
        record = self._delete_window(report)
        result = self._delete(inventory, manifest, "--apply",
                              "--release-window", record)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        apply_report = load_json(os.path.join(
            self.fx.out, "branch-deletion-apply.json"))
        self.assertEqual(apply_report["totals"]["deleted"], 2)
        self.assertTrue(apply_report["apply"]["release_window"]["task_id"])
        for branch in ("feature-merged", "feature-unmerged"):
            self.assertNotEqual(self.fx.git("rev-parse", "--verify", "--quiet",
                                            "refs/heads/" + branch,
                                            check=False).returncode, 0)

    def test_delete_stale_inventory_is_refused(self):
        inventory, manifest = self._prepare_archive_proof()
        stale = self._inventory(
            lambda rows, fixture: [row.__setitem__("merged", True)
                                   for row in rows
                                   if row["branch"] == "feature-unmerged"])
        result = self._delete(stale, manifest)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("INVENTORY_STALE", result.stderr)
        self.assertTrue(self.fx.git("rev-parse", "--verify", "--quiet",
                                    "refs/heads/feature-unmerged",
                                    check=False).returncode == 0)

    def test_delete_refuses_unmerged_without_archive_proof(self):
        self._detach_worktree()
        inventory = self._inventory()
        manifest = os.path.join(self.fx.tmp, "empty-manifest.json")
        write_json(manifest, {"archived": []})
        result = self._delete(inventory, manifest)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        report = load_json(os.path.join(
            self.fx.out, "branch-deletion-refused.json"))
        self.assertEqual(report["refused_plan"], "INCOMPLETE_ARCHIVE_PROOF")
        self.assertTrue(any(item["branch"] == "feature-unmerged"
                            for item in report["refused"]))
        self.assertTrue(self.fx.git("rev-parse", "--verify", "--quiet",
                                    "refs/heads/feature-unmerged",
                                    check=False).returncode == 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
