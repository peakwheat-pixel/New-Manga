"""Closed disposition alias table (GOV-DECLARATION-SCAN-CLEANUP-1 AC3, Q3).

Ruling: Codex adjudication 2026-11-16.  The alias table is *closed*: five exact
legacy tokens map to canonical dispositions, every application is warned with
raw AND canonical value, and any other unknown token still fails closed.

These tests must fail if the alias table is widened (e.g. case folding, affix
stripping, regex relaxation) or if an alias stops registering protection.
"""
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import clean_workspace as guard


class DispositionAliasTable(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="nm-alias-")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.protected_file = os.path.join(self.tmp, "artifact.bin")
        with open(self.protected_file, "wb") as handle:
            handle.write(b"x")
        self.index = guard.ProtectionIndex(repo_root=self.tmp, ws_root=self.tmp)

    def warnings(self, code):
        return [w for w in self.index.warnings if w["code"] == code]

    def errors(self, code):
        return [e for e in self.index.errors if e["code"] == code]

    def test_preserve_maps_to_preserve_unknown_and_still_protects(self):
        decl = self.index.add_declaration(
            self.protected_file, "PRESERVE", "fixture.md", "line 6")
        self.assertIsNotNone(decl)
        self.assertEqual(decl.disposition, "PRESERVE_UNKNOWN")
        self.assertTrue(guard.is_protective(decl.disposition))
        self.assertIn(guard.norm_abs(self.protected_file, "p"), self.index.protected)
        applied = self.warnings("DISPOSITION_ALIAS_APPLIED")
        self.assertEqual(len(applied), 1)
        self.assertIn("PRESERVE", applied[0]["message"])
        self.assertIn("PRESERVE_UNKNOWN", applied[0]["message"])

    def test_read_only_referenced_maps_to_preserve_referenced(self):
        decl = self.index.add_declaration(
            self.protected_file, "READ_ONLY_REFERENCED", "fixture.md", "line 5")
        self.assertEqual(decl.disposition, "PRESERVE_REFERENCED")
        self.assertTrue(guard.is_protective(decl.disposition))

    def test_modified_and_restored_in_place_map_to_preserve_in_repo(self):
        for token in ("MODIFIED_IN_PLACE", "RESTORED_IN_PLACE"):
            with self.subTest(token=token):
                index = guard.ProtectionIndex(repo_root=self.tmp, ws_root=self.tmp)
                decl = index.add_declaration(
                    self.protected_file, token, "fixture.md", "$.resources[2].disposition")
                self.assertEqual(decl.disposition, "PRESERVE_IN_REPO")
                self.assertTrue(guard.is_protective(decl.disposition))

    def test_not_created_no_scratch_maps_to_already_absent_without_protection(self):
        absent = os.path.join(self.tmp, "never-created")
        decl = self.index.add_declaration(
            absent, "NOT_CREATED_NO_SCRATCH", "fixture.md", "$.resources[1].disposition")
        self.assertEqual(decl.disposition, "ALREADY_ABSENT")
        self.assertFalse(guard.is_protective(decl.disposition))
        self.assertNotIn(guard.norm_abs(absent, "p"), self.index.protected)

    def test_unlisted_tokens_still_fail_closed(self):
        # Tokens outside both the frozen grammar and the alias table keep failing.
        for token in ("FOO_BAR", "MODIFIED", "READ_ONLY", "NOT_CREATED",
                      "PRESERVE-REFERENCED"):
            with self.subTest(token=token):
                index = guard.ProtectionIndex(repo_root=self.tmp, ws_root=self.tmp)
                index.add_declaration(self.protected_file, token, "fixture.md", "line 1")
                self.assertTrue([e for e in index.errors
                                 if e["code"] == "DECL_UNKNOWN_DISPOSITION"])
                self.assertEqual(index.warnings, [])

    def test_only_universal_cell_trim_is_a_normalised_before_matching(self):
        # clean_cell trims surrounding whitespace for EVERY cell in the scanner,
        # so " PRESERVE " reaches the alias table as "PRESERVE".  That single
        # inherited trim is the only normalisation; no other folding happens.
        index = guard.ProtectionIndex(repo_root=self.tmp, ws_root=self.tmp)
        decl = index.add_declaration(
            self.protected_file, "  PRESERVE  ", "fixture.md", "line 1")
        self.assertEqual(decl.disposition, "PRESERVE_UNKNOWN")
        self.assertEqual(len([w for w in index.warnings
                              if w["code"] == "DISPOSITION_ALIAS_APPLIED"]), 1)

    def test_frozen_grammar_still_accepts_any_preserve_suffix_without_alias(self):
        # Pre-existing boundary, documented not widened: DISPOSITION_RE accepts
        # every PRESERVE_<suffix>.  The alias table must NOT be the thing that
        # accepts it (no alias warning), and tightening that grammar is a
        # separate decision, not part of AC3.
        index = guard.ProtectionIndex(repo_root=self.tmp, ws_root=self.tmp)
        decl = index.add_declaration(
            self.protected_file, "PRESERVE_NOT_A_REAL_SUFFIX", "fixture.md", "line 1")
        self.assertIsNotNone(decl)
        self.assertEqual(decl.disposition, "PRESERVE_NOT_A_REAL_SUFFIX")
        self.assertEqual(index.warnings, [])
        self.assertEqual(index.errors, [])

    def test_alias_matching_is_case_sensitive(self):
        for token in ("preserve", "Preserve", "read_only_referenced",
                      "modified_in_place"):
            with self.subTest(token=token):
                index = guard.ProtectionIndex(repo_root=self.tmp, ws_root=self.tmp)
                index.add_declaration(self.protected_file, token, "fixture.md", "line 1")
                self.assertTrue([e for e in index.errors
                                 if e["code"] == "DECL_UNKNOWN_DISPOSITION"])

    def test_alias_table_is_exactly_the_five_adjudicated_tokens(self):
        self.assertEqual(
            guard.DISPOSITION_ALIASES,
            {"PRESERVE": "PRESERVE_UNKNOWN",
             "READ_ONLY_REFERENCED": "PRESERVE_REFERENCED",
             "MODIFIED_IN_PLACE": "PRESERVE_IN_REPO",
             "RESTORED_IN_PLACE": "PRESERVE_IN_REPO",
             "NOT_CREATED_NO_SCRATCH": "ALREADY_ABSENT"})


if __name__ == "__main__":
    unittest.main()
