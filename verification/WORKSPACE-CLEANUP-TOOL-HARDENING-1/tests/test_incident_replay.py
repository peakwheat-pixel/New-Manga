# -*- coding: utf-8 -*-
"""AC6: r208 incident replay must reject all 15 deleted roots (0 deletions).

Input is the tracked incident ledger
``verification/WORKSPACE-CONSOLIDATION-1/incident-ledger-r208.json``:
18 protected sources, 15 removed roots.  Both path-deletion tools must reject
every root with a per-item reason and report zero deletions.  Negative controls
prove the replay is not a rubber stamp: removing a source from the ledger makes
the uncovered root a violation and the tool exits non-zero.
"""
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest

from fixture_support import (LEDGER, ROOT, TOOLS, guard, load_json, run_tool,
                             write_json)

if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)

import clean_workspace  # noqa: E402
import remove_worktrees  # noqa: E402


class TestIncidentReplay(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="wc-replay-")
        self.addCleanup(lambda: shutil.rmtree(self.tmp, ignore_errors=True))
        self.ledger = load_json(LEDGER)
        self.roots = [item["path"] for item in self.ledger["removed_roots"]]
        self.sources = [item["source_path"]
                        for item in self.ledger["protected_sources"]]

    def _snapshot(self):
        return {path: os.path.lexists(path) for path in self.roots + self.sources}

    def _run_replay(self, script, *extra):
        out = os.path.join(self.tmp, script.replace(".py", ""))
        os.makedirs(out, exist_ok=True)
        result = run_tool(script, "--replay-incident", LEDGER, "--out", out,
                          *extra)
        return result, out

    def test_replay_clean_workspace_rejects_all_15_roots(self):
        before = self._snapshot()
        status_before = self._git_snapshot()
        result, out = self._run_replay("clean_workspace.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = load_json(os.path.join(out, "incident-replay-clean-workspace.json"))
        self.assertEqual(report["mode"], "incident_replay")
        self.assertEqual(report["input_counts"], {
            "protected_sources": 18, "removed_roots": 15})
        self.assertEqual(report["totals"]["candidates"], 15)
        self.assertEqual(report["totals"]["rejected"], 15)
        self.assertEqual(report["totals"]["deleted"], 0)
        self.assertEqual(report["totals"]["violations"], 0)
        self.assertTrue(report["ok"])
        self.assertEqual(report["coverage"]["sources_covering_roots"], 18)
        self.assertEqual(report["violations"], [])
        decisions = {item["id"]: item for item in report["decisions"]}
        self.assertEqual(len(decisions), 15)
        for root in self.ledger["removed_roots"]:
            decision = decisions[root["id"]]
            self.assertEqual(decision["decision"], "REJECT", root["id"])
            self.assertTrue(decision["reasons"], root["id"])
            self.assertEqual(decision["path"], root["path"])
        # ROOT-02 is the preserved-root descendant that r208 actually deleted.
        nested = decisions["ROOT-02"]
        self.assertTrue(any("descendant_of_preserved_root" in reason
                            for reason in nested["reasons"]))
        self.assertEqual(self._snapshot(), before)
        self.assertEqual(self._git_snapshot(), status_before)

    def test_replay_remove_worktrees_rejects_all_15_roots(self):
        result, out = self._run_replay("remove_worktrees.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = load_json(os.path.join(
            out, "incident-replay-remove-worktrees.json"))
        self.assertEqual(report["tool"], "remove_worktrees.py")
        self.assertEqual(report["totals"]["candidates"], 15)
        self.assertEqual(report["totals"]["rejected"], 15)
        self.assertEqual(report["totals"]["deleted"], 0)
        self.assertEqual(report["totals"]["violations"], 0)
        self.assertTrue(report["ok"])
        decisions = {item["id"]: item for item in report["decisions"]}
        for root in self.ledger["removed_roots"]:
            self.assertEqual(decisions[root["id"]]["decision"], "REJECT")
            self.assertTrue(decisions[root["id"]]["reasons"])
        # The tool also records its location rule for non-standard worktrees.
        self.assertFalse(decisions["ROOT-07"]["standard_worktree_location"])
        self.assertIn("NON_STANDARD_WORKTREE_LOCATION",
                      decisions["ROOT-07"]["additional_tool_reason"])

    def test_replay_refuses_apply(self):
        for script in ("clean_workspace.py", "remove_worktrees.py"):
            result, _out = self._run_replay(script, "--apply")
            self.assertEqual(result.returncode, 2,
                             result.stdout + result.stderr)
            self.assertIn("REPLAY_APPLY_REFUSED", result.stderr)

    def test_replay_never_reaches_a_deletion_function(self):
        original_delete = guard.delete_path
        original_remove = guard.remove_worktree

        def forbidden(*_args, **_kwargs):
            raise AssertionError("replay reached a deletion function")

        guard.delete_path = forbidden
        guard.remove_worktree = forbidden
        try:
            report = clean_workspace.build_incident_replay(LEDGER)
            self.assertTrue(report["ok"])
            report = remove_worktrees.run_replay({
                "replay": LEDGER,
                "ws": guard.norm_abs(guard.WS_DEFAULT),
                "repo": guard.norm_abs(ROOT),
                "out": None,
            })
            self.assertEqual(report, 0)
        finally:
            guard.delete_path = original_delete
            guard.remove_worktree = original_remove

    def test_negative_control_unprotected_root_is_a_violation(self):
        tampered = dict(self.ledger)
        tampered["protected_sources"] = [
            source for source in self.ledger["protected_sources"]
            if source["id"] != "SRC-02"]
        path = os.path.join(self.tmp, "tampered-ledger.json")
        write_json(path, tampered)
        result = run_tool("clean_workspace.py", "--replay-incident", path,
                          "--out", self.tmp)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        report = load_json(os.path.join(
            self.tmp, "incident-replay-clean-workspace.json"))
        self.assertGreater(report["totals"]["violations"], 0)
        self.assertFalse(report["ok"])
        violations = {item["id"] for item in report["violations"]}
        self.assertIn("ROOT-02", violations)

    def test_negative_control_relative_root_is_a_violation(self):
        tampered = json.loads(json.dumps(self.ledger))
        tampered["removed_roots"][0]["path"] = "workspace/temp/relative"
        path = os.path.join(self.tmp, "tampered-ledger.json")
        write_json(path, tampered)
        result = run_tool("clean_workspace.py", "--replay-incident", path,
                          "--out", self.tmp)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        report = load_json(os.path.join(
            self.tmp, "incident-replay-clean-workspace.json"))
        self.assertGreater(report["totals"]["violations"], 0)

    def test_negative_control_bad_schema_is_refused(self):
        tampered = json.loads(json.dumps(self.ledger))
        del tampered["protected_sources"]
        path = os.path.join(self.tmp, "tampered-ledger.json")
        write_json(path, tampered)
        result = run_tool("clean_workspace.py", "--replay-incident", path,
                          "--out", self.tmp)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("LEDGER_SCHEMA", result.stderr)

    def test_ledger_sha_is_recorded(self):
        result, out = self._run_replay("clean_workspace.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = load_json(os.path.join(out, "incident-replay-clean-workspace.json"))
        expected = hashlib.sha256(open(LEDGER, "rb").read()).hexdigest()
        self.assertEqual(report["ledger"]["sha256"], expected)
    # -- helpers -----------------------------------------------------------
    def _git_snapshot(self):
        status = guard.git(ROOT, "status", "--porcelain")
        head = guard.git(ROOT, "rev-parse", "HEAD")
        return (status.returncode, status.stdout, status.stderr,
                head.returncode, head.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
