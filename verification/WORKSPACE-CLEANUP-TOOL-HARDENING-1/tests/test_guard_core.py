# -*- coding: utf-8 -*-
"""AC1/AC2/AC3 unit tests for the shared fail-closed guard core.

No filesystem outside %TEMP% is touched.  The fixture repository is needed only
so that repo-relative declarations have a concrete repository root.
"""
import os
import sys
import unittest

from fixture_support import (RepoFixture, TOOLS, acceptance_digest_from_report,
                             guard, load_json, make_release_window, utc_now,
                             write_json)
import datetime

if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)


class TestPathIdentity(unittest.TestCase):
    """AC1: normalised absolute identity, never guessed."""

    def test_equivalent_spellings_normalise_to_one_identity(self):
        variants = [
            "G:/CODEX/Example/root",
            "G:\\CODEX\\Example\\root\\",
            "G:/CODEX/Example/./root",
            "G:/CODEX/Example/sub/../root",
            "g:/codex/example/ROOT",
        ]
        identities = {guard.norm_abs(value, "path") for value in variants}
        self.assertEqual(len(identities), 1, identities)
        self.assertEqual(guard.norm_abs(variants[0]), "g:/codex/example/root")

    def test_bare_and_relative_paths_are_refused(self):
        for raw in ("temp/foo", "foo", "./foo", "../foo", ""):
            with self.assertRaises(guard.GuardError) as caught:
                guard.norm_abs(raw, "candidate")
            self.assertIn(caught.exception.code,
                          ("PATH_EMPTY", "PATH_NOT_ABSOLUTE"))

    def test_drive_relative_and_nul_are_refused(self):
        with self.assertRaises(guard.GuardError) as caught:
            guard.norm_abs("\\foo", "candidate")
        self.assertEqual(caught.exception.code, "PATH_AMBIGUOUS_DRIVE")
        with self.assertRaises(guard.GuardError) as caught:
            guard.norm_abs("G:/foo\x00bar", "candidate")
        self.assertEqual(caught.exception.code, "PATH_NUL")

    def test_relation_uses_component_boundaries(self):
        same = guard.norm_abs("G:/ws/temp/P02-NEW-TIME-X")
        descendant = guard.norm_abs("G:/ws/temp/P02-NEW-TIME-X/deep/child")
        sibling = guard.norm_abs("G:/ws/temp/P02-NEW-TIME-X6")
        parent = guard.norm_abs("G:/ws/temp")
        self.assertEqual(guard.path_relation(same, same), "same")
        self.assertEqual(guard.path_relation(descendant, same), "descendant")
        self.assertEqual(guard.path_relation(same, descendant), "ancestor")
        self.assertEqual(guard.path_relation(sibling, same), "disjoint")
        self.assertEqual(guard.path_relation(parent, same), "ancestor")

    def test_escape_outside_managed_root_is_refused(self):
        root = guard.norm_abs("G:/ws/temp")
        with self.assertRaises(guard.GuardError) as caught:
            guard.ensure_within(guard.norm_abs("G:/ws/other/child"), root)
        self.assertEqual(caught.exception.code, "PATH_ESCAPE")


class TestProtectionIndex(unittest.TestCase):
    """AC1: exact / descendant / ancestor protection, shared declarations."""

    def setUp(self):
        self.fixture = RepoFixture(prefix="wc-guard-")
        self.addCleanup(self.fixture.cleanup)
        self.ws = os.path.join(self.fixture.tmp, "New Manga.workspace")
        os.makedirs(self.ws, exist_ok=True)
        self.index = guard.ProtectionIndex(repo_root=self.fixture.repo,
                                           ws_root=self.ws)

    def _norm(self, value):
        return guard.norm_abs(value, "test path")

    def test_exact_descendant_and_ancestor_are_protected(self):
        root = os.path.join(self.ws, "temp", "PROTECTED-ROOT")
        self.index.add_declaration(root, "PRESERVE_REFERENCED",
                                   "doc/tasks/FIXTURE.md", "line 1")
        self.index.finalize()
        exact = self.index.evaluate(self._norm(root))
        self.assertEqual([hit["kind"] for hit in exact], ["exact_source_path"])
        deeper = self.index.evaluate(self._norm(
            os.path.join(root, "a", "b", "c", "file.bin")))
        self.assertEqual([hit["kind"] for hit in deeper],
                         ["descendant_of_preserved_root"])
        parent = self.index.evaluate(self._norm(os.path.join(self.ws, "temp")))
        self.assertEqual([hit["kind"] for hit in parent],
                         ["ancestor_of_preserved_source"])
        sibling = self.index.evaluate(self._norm(root + "-OTHER"))
        self.assertEqual(sibling, [])

    def test_shared_declarations_are_merged_not_deduplicated_away(self):
        root = os.path.join(self.ws, "temp", "SHARED")
        self.index.add_declaration(root, "PRESERVE_REFERENCED", "task-a.md", "l1")
        self.index.add_declaration(root, "PRESERVE_USER_DATA", "task-b.md", "l2")
        # Equivalent spelling from a third source: same identity, still merged.
        self.index.add_declaration(root.replace("/", "\\") + "\\",
                                   "PRESERVE_UNKNOWN", "task-c.md", "l3")
        self.index.finalize()
        hits = self.index.evaluate(self._norm(root))
        self.assertEqual(len(hits), 1)
        self.assertIn("PRESERVE_REFERENCED", hits[0]["dispositions"])
        self.assertIn("PRESERVE_USER_DATA", hits[0]["dispositions"])
        self.assertEqual(len(hits[0]["sources"]), 3)

    def test_unresolved_declarations_fail_closed(self):
        cases = [
            ("*.bundle", "glob"),
            ("%TEMP%/x", "environment variable"),
            ("../outside", "traversal"),
            ("temp/relative-workspace-path", "workspace-relative"),
            ("BARE-NAME-ONLY", "bare name"),
            ("verification/not-a-repo-top-level", "ambiguous relative"),
        ]
        for raw, label in cases:
            with self.subTest(raw=raw):
                index = guard.ProtectionIndex(repo_root=self.fixture.repo,
                                              ws_root=self.ws)
                index.add_declaration(raw, "PRESERVE_REFERENCED", "f.md", "l")
                self.assertTrue(index.errors, label)
                with self.assertRaises(guard.GuardError) as caught:
                    index.finalize()
                self.assertEqual(caught.exception.code,
                                 "DECLARATION_INTEGRITY")

    def test_unknown_and_empty_dispositions_fail_closed(self):
        root = os.path.join(self.ws, "temp", "X")
        self.index.add_declaration(root, "BOGUS", "f.md", "l1")
        self.index.add_declaration(root, "", "f.md", "l2")
        codes = {error["code"] for error in self.index.errors}
        self.assertIn("DECL_UNKNOWN_DISPOSITION", codes)
        self.assertIn("DECL_EMPTY_DISPOSITION", codes)
        with self.assertRaises(guard.GuardError):
            self.index.finalize()

    def test_generalised_declarations_are_refused(self):
        for raw in (self.ws, os.path.join(self.ws, "worktrees"),
                    os.path.dirname(self.ws)):
            with self.subTest(raw=raw):
                index = guard.ProtectionIndex(repo_root=self.fixture.repo,
                                              ws_root=self.ws)
                index.add_declaration(raw, "PRESERVE_REFERENCED", "f.md", "l")
                self.assertEqual([error["code"] for error in index.errors],
                                 ["DECL_GENERALIZED"])

    def test_delete_safe_does_not_protect_and_migrate_does(self):
        safe = os.path.join(self.ws, "temp", "SAFE")
        migrating = os.path.join(self.ws, "temp", "MIGRATING")
        self.index.add_declaration(safe, "DELETE_SAFE", "f.md", "l1")
        self.index.add_declaration(migrating, "MIGRATE", "f.md", "l2")
        self.index.finalize()
        self.assertEqual(self.index.evaluate(self._norm(safe)), [])
        self.assertTrue(self.index.evaluate(self._norm(migrating)))

    def test_repo_relative_declaration_is_resolved_against_repo_root(self):
        self.index.add_declaration("README.md", "PRESERVE_REFERENCED",
                                   "doc/tasks/FIXTURE.md", "l1")
        self.index.finalize()
        self.assertTrue(self.index.evaluate(
            guard.norm_abs(os.path.join(self.fixture.repo, "README.md"))))


class TestMarkdownDeclarations(unittest.TestCase):
    """AC1/AC2: table parsing, bare paths, PRESERVE_UNKNOWN, bad columns."""

    def setUp(self):
        self.fixture = RepoFixture(prefix="wc-md-")
        self.addCleanup(self.fixture.cleanup)
        self.ws = os.path.join(self.fixture.tmp, "New Manga.workspace")
        os.makedirs(self.ws, exist_ok=True)

    def _index(self):
        return guard.ProtectionIndex(repo_root=self.fixture.repo, ws_root=self.ws)

    def test_bare_and_backticked_paths_are_both_protected(self):
        bare = os.path.join(self.ws, "temp", "BARE-PATH")
        ticked = os.path.join(self.ws, "review-scratch", "TICKED-PATH")
        text = "\n".join([
            "## Resource Manifest",
            "",
            "| resource_type | source_path | disposition | destination_path | "
            "sha256/manifest | reference/process check and result |",
            "|---|---|---|---|---|---|",
            "| scratch | %s | PRESERVE_REFERENCED | - | - | fixture |" % bare,
            "| scratch | `%s` | PRESERVE_UNKNOWN | - | - | fixture |" % ticked,
            "",
        ])
        index = self._index()
        guard.parse_markdown_declarations(index, text, "doc/tasks/FIXTURE.md")
        index.finalize()
        self.assertTrue(index.evaluate(guard.norm_abs(bare)))
        hits = index.evaluate(guard.norm_abs(ticked))
        self.assertEqual(hits[0]["dispositions"], ["PRESERVE_UNKNOWN"])

    def test_nonstandard_column_count_is_a_hard_error(self):
        text = "\n".join([
            "## Resource Manifest",
            "",
            "| resource_type | source_path | disposition | destination_path | "
            "sha256/manifest | reference/process check and result |",
            "|---|---|---|---|---|---|",
            "| scratch | G:/x/y | PRESERVE_REFERENCED | - | - | one | extra |",
            "",
        ])
        index = self._index()
        guard.parse_markdown_declarations(index, text, "doc/tasks/FIXTURE.md")
        self.assertEqual([error["code"] for error in index.errors],
                         ["TABLE_ROW_ARITY"])
        with self.assertRaises(guard.GuardError) as caught:
            index.finalize()
        self.assertEqual(caught.exception.code, "DECLARATION_INTEGRITY")

    def test_canonical_evidence_paths_are_protective(self):
        evidence = os.path.join(self.ws, "temp", "EVIDENCE-PIN")
        text = "\n".join([
            "## Canonical Evidence",
            "",
            "| evidence_id | AC/Gate | path | commit | sha256 | class |",
            "|---|---|---|---|---|---|",
            "| E1 | AC1 | %s | - | %s | SOURCE_PIN |"
            % (evidence, "0" * 64),
            "",
        ])
        index = self._index()
        guard.parse_markdown_declarations(index, text, "doc/tasks/FIXTURE.md")
        index.finalize()
        self.assertTrue(index.evaluate(guard.norm_abs(evidence)))

    def test_not_applicable_placeholder_row_is_skipped(self):
        text = "\n".join([
            "## Resource Manifest",
            "",
            "| resource_type | source_path | disposition | destination_path | "
            "sha256/manifest | reference/process check and result |",
            "|---|---|---|---|---|---|",
            "| NOT_APPLICABLE | - | NOT_APPLICABLE | - | - | fixture |",
            "",
        ])
        index = self._index()
        guard.parse_markdown_declarations(index, text, "doc/tasks/FIXTURE.md")
        index.finalize()
        self.assertEqual(index.declarations, [])


class TestJsonDeclarations(unittest.TestCase):
    """AC1/AC2: recursive JSON declarations and schema errors."""

    def setUp(self):
        self.fixture = RepoFixture(prefix="wc-json-")
        self.addCleanup(self.fixture.cleanup)
        self.ws = os.path.join(self.fixture.tmp, "New Manga.workspace")
        os.makedirs(self.ws, exist_ok=True)

    def _index(self):
        return guard.ProtectionIndex(repo_root=self.fixture.repo, ws_root=self.ws)

    def test_nested_resources_and_ledger_style_records(self):
        first = os.path.join(self.ws, "temp", "FIRST")
        second = os.path.join(self.ws, "temp", "SECOND")
        data = {
            "resources": [{"source_path": first,
                           "disposition": "PRESERVE_REFERENCED"}],
            "entries": [{"source_path": second,
                         "disposition_original": "PRESERVE_UNKNOWN"}],
        }
        index = self._index()
        guard.parse_json_declarations(index, data, "verification/FIXTURE.json")
        index.finalize()
        self.assertTrue(index.evaluate(guard.norm_abs(first)))
        self.assertTrue(index.evaluate(guard.norm_abs(second)))

    def test_resource_type_path_style_is_supported(self):
        path = os.path.join(self.ws, "temp", "ENV-BUNDLE-STYLE")
        data = {"resources": [{"resource_type": "build-venv",
                               "path": path,
                               "disposition": "PRESERVE_REFERENCED"}]}
        index = self._index()
        guard.parse_json_declarations(index, data, "verification/FIXTURE.json")
        index.finalize()
        self.assertTrue(index.evaluate(guard.norm_abs(path)))

    def test_unknown_json_disposition_fails_closed(self):
        data = {"resources": [{"source_path": os.path.join(self.ws, "temp", "X"),
                               "disposition": "CLEANED_BY_OWNER"}]}
        index = self._index()
        guard.parse_json_declarations(index, data, "verification/FIXTURE.json")
        self.assertIn("DECL_UNKNOWN_DISPOSITION",
                      [error["code"] for error in index.errors])
        with self.assertRaises(guard.GuardError):
            index.finalize()


class TestReleaseWindowAndInventory(unittest.TestCase):
    """AC5/AC3: release window validation and pre-delete inventory."""

    def setUp(self):
        self.fixture = RepoFixture(prefix="wc-window-")
        self.addCleanup(self.fixture.cleanup)
        self.ws = os.path.join(self.fixture.tmp, "New Manga.workspace")
        self.roots = [guard.norm_abs(os.path.join(self.ws, "temp"))]
        self.expected = {
            "tool": "clean_workspace.py",
            "repo": guard.norm_abs(self.fixture.repo),
            "workspace_root": guard.norm_abs(self.ws),
            "roots": self.roots,
            "candidates_sha256": guard.candidates_digest(["g:/x/a", "g:/x/b"]),
            "candidate_count": 2,
        }

    def _record(self, **overrides):
        path = os.path.join(self.fixture.tmp, "window.json")
        make_release_window(
            path, self.expected["tool"], self.expected["repo"],
            self.expected["workspace_root"], self.expected["roots"],
            self.expected["candidates_sha256"],
            self.expected["candidate_count"], **overrides)
        return path

    def test_valid_record_passes(self):
        record = guard.verify_release_window(self._record(), self.expected)
        self.assertEqual(record["task_id"], "FIXTURE-HARDENING-CLI")

    def test_candidate_drift_is_refused(self):
        path = self._record()
        data = load_json(path)
        data["candidates_sha256"] = "0" * 64
        write_json(path, data)
        with self.assertRaises(guard.GuardError) as caught:
            guard.verify_release_window(path, self.expected)
        self.assertEqual(caught.exception.code, "WINDOW_CANDIDATE_DRIFT")

    def test_missing_field_is_refused(self):
        path = self._record()
        data = load_json(path)
        del data["authorized_by"]
        write_json(path, data)
        with self.assertRaises(guard.GuardError) as caught:
            guard.verify_release_window(path, self.expected)
        self.assertEqual(caught.exception.code, "WINDOW_INVALID")

    def test_expired_window_is_refused(self):
        past = utc_now() - datetime.timedelta(days=2)
        path = self._record(created_at=past)
        with self.assertRaises(guard.GuardError) as caught:
            guard.verify_release_window(path, self.expected)
        self.assertEqual(caught.exception.code, "WINDOW_CLOSED")

    def test_root_mismatch_is_refused(self):
        path = self._record()
        data = load_json(path)
        data["roots"] = ["g:/somewhere/else"]
        write_json(path, data)
        with self.assertRaises(guard.GuardError) as caught:
            guard.verify_release_window(path, self.expected)
        self.assertEqual(caught.exception.code, "WINDOW_ROOTS_MISMATCH")

    def test_inventory_records_size_and_sha256_per_file(self):
        root = os.path.join(self.ws, "temp", "CANDIDATE")
        os.makedirs(root)
        files = {"a.txt": "alpha", "sub/b.bin": "beta"}
        for relative, content in files.items():
            target = os.path.join(root, *relative.split("/"))
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "w", encoding="utf-8") as handle:
                handle.write(content)
        inventory = guard.build_inventory(root)
        entries = {entry["path"]: entry for entry in inventory["entries"]}
        self.assertEqual(entries["a.txt"]["size"], 5)
        self.assertEqual(entries["a.txt"]["sha256"],
                         guard.sha256_file(os.path.join(root, "a.txt")))
        self.assertEqual(entries["sub/b.bin"]["origin"], "non_git")
        self.assertEqual(inventory["counts"]["files"], 2)
        self.assertTrue(guard.inventory_requires_acceptance(inventory))

    def test_permission_denied_is_fail_closed(self):
        root = os.path.join(self.ws, "temp", "CANDIDATE")
        os.makedirs(root)
        with open(os.path.join(root, "a.txt"), "w", encoding="utf-8") as handle:
            handle.write("alpha")
        original = guard.sha256_file

        def denied(path):
            raise guard.GuardError("PERMISSION_DENIED",
                                   "simulated denial for %s" % path)

        guard.sha256_file = denied
        try:
            with self.assertRaises(guard.GuardError) as caught:
                guard.build_inventory(root)
            self.assertEqual(caught.exception.code, "PERMISSION_DENIED")
        finally:
            guard.sha256_file = original


if __name__ == "__main__":
    unittest.main(verbosity=2)
