"""T01-T18: isolated Git fixtures; never apply to a real resource."""
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import unittest
from unittest import mock
from contextlib import redirect_stderr

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "verification" /
                      "WORKSPACE-CLEANUP-TOOL-HARDENING-1" / "tests"))
from fixture_support import RepoFixture, guard, run_tool, load_json

FIRST = "doc/tasks/SEC-FIX-PATH-ECHO-1.md"
SECOND = "doc/tasks/WORKSPACE-CONSOLIDATION-1.md"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class BroadPreservationTests(unittest.TestCase):
    def setUp(self):
        self.f = RepoFixture(prefix="broad-preservation-")
        self.addCleanup(self.cleanup_fixture)
        self.ws = guard.norm_abs(self.f.ws)
        self.f.write(guard.BROAD_PRESERVATION_RULING, "fixture-only ruling\n")
        header = ("| resource_type | source_path | disposition | "
                  "destination_path | sha256/manifest | description |")
        for file, roots in [(FIRST, [self.ws]), (SECOND, [
                self.ws, self.ws + "/task-envs", self.ws + "/worktrees",
                self.ws + "/review-scratch", self.ws + "/temp"])]:
            lines = ["# fixture", "", "## Resource Manifest", "", header,
                     "|---|---|---|---|---|---|"]
            for root in roots:
                keep = ("PRESERVE_UNKNOWN" if root in (
                    self.ws + "/review-scratch", self.ws + "/temp")
                        else "PRESERVE_REFERENCED")
                lines.append("| fixture | %s | %s | %s | - | fixture |"
                             % (root, keep, root))
            self.f.write(file, "\n".join(lines) + "\n")
        self.f.commit("six fixture declarations")
        self.base, self.scanned = self.scan()
        self.assertEqual(len(self.base.errors), 12)
        bindings = []
        for file in (FIRST, SECOND):
            raw = (Path(self.f.repo) / file).read_bytes()
            manifest = guard.section_text(raw.decode(), "Resource Manifest")
            for start, block in guard.iter_table_blocks(manifest):
                _, rows = guard.parse_table_block(block, start)
                for number, row in rows:
                    physical = raw.decode()[:raw.decode().index(
                        manifest)].count("\n") + number
                    line = raw.splitlines(keepends=True)[physical - 1]
                    locator = "line %d" % number
                    bindings.append({
                        "id": "BPR-%02d" % (len(bindings) + 1),
                        "origin_file": file, "origin_raw_sha256": sha(raw),
                        "global_line": physical, "row_raw_sha256": sha(line),
                        "row_verbatim": line.decode(), "parser_locator": locator,
                        "root_abs": row[1], "root_normalized": row[1],
                        "root_real_expected": row[1], "source_keep": row[2],
                        "error_pair": [copy.deepcopy(e) for e in self.base.errors
                                       if e["file"] == file
                                       and e["locator"] == locator]})
        self.policy = {
            "schema_version": 1, "policy_kind": "BROAD_ROOT_PRESERVATION",
            "scope_id": "workspace-preserve-20261021-5roots",
            "decision_ref": guard.BROAD_PRESERVATION_RULING,
            "decision_sha256": sha((Path(self.f.repo) /
                                   guard.BROAD_PRESERVATION_RULING).read_bytes()),
            "bindings": bindings}

    def cleanup_fixture(self):
        # Recursive cleanup is restricted to this test's owned TMP fixture.
        fixture = Path(self.f.tmp).resolve()
        permitted = Path(os.environ["TMP"]).resolve()
        assert fixture != permitted and fixture.is_relative_to(permitted)
        self.f.cleanup()

    def scan(self):
        return guard.scan_repo_declarations(self.f.repo, self.f.ws)

    def install(self, policy=None, tracked=True):
        self.f.write(guard.BROAD_PRESERVATION_POLICY,
                     json.dumps(policy or self.policy, ensure_ascii=False))
        if tracked:
            self.f.git("add", "--", guard.BROAD_PRESERVATION_POLICY)

    def rejected(self, policy, code=None):
        self.install(policy)
        index, scanned = self.scan()
        self.assertTrue(index.errors)
        for error in self.base.errors:
            self.assertIn(error, index.errors)
        self.assertEqual(index.protected, self.base.protected)
        self.assertEqual(index.declarations, self.base.declarations)
        self.assertEqual(index.warnings, self.base.warnings)
        self.assertEqual(scanned["errors"], len(index.errors))
        if code:
            self.assertIn(code, [e["code"] for e in index.errors])
        return index

    def resign_first_row(self, policy, new_text):
        self.f.write(FIRST, new_text)
        raw = (Path(self.f.repo) / FIRST).read_bytes()
        binding = policy["bindings"][0]
        line = raw.splitlines(keepends=True)[binding["global_line"] - 1]
        binding.update(origin_raw_sha256=sha(raw), row_verbatim=line.decode(),
                       row_raw_sha256=sha(line))

    def test_t01_complete_policy_registers_all_roles_and_counts(self):
        self.install()
        index, scanned = self.scan()
        self.assertEqual(index.errors, [])
        self.assertEqual(len(index.declarations), 12)
        self.assertEqual(len(index.protected), 5)
        self.assertEqual(len(index.warnings) - len(self.base.warnings), 12)
        self.assertEqual({e["code"] for e in index.warnings},
                         {"DECL_BROAD_ROOT_PRESERVED"})
        self.assertEqual({d.disposition for d in index.declarations},
                         {"PRESERVE_REFERENCED", "PRESERVE_UNKNOWN",
                          "DESTINATION_PIN"})
        self.assertEqual(scanned["declarations"], len(index.declarations))
        self.assertEqual(scanned["warnings"], len(index.warnings))

    def test_t02_other_source_even_same_name_is_not_authority(self):
        policy = copy.deepcopy(self.policy)
        policy["bindings"][0]["origin_file"] = "elsewhere/SEC-FIX-PATH-ECHO-1.md"
        self.rejected(policy, "POLICY_INVALID")

    def test_t03_byte_and_eol_drift_never_resigns_source(self):
        original = (Path(self.f.repo) / FIRST).read_bytes()
        self.install()
        for changed in (original + b"\n", original.replace(b"\n", b"\r\n")):
            with self.subTest(sha=sha(changed)):
                (Path(self.f.repo) / FIRST).write_bytes(changed)
                index, _ = self.scan()
                self.assertIn("SOURCE_DRIFT", [e["code"] for e in index.errors])
                self.assertEqual(index.protected, self.base.protected)
        (Path(self.f.repo) / FIRST).write_bytes(original)

    def test_t04_row_and_locator_are_both_bound(self):
        for field, value in (("global_line", 1), ("global_line", True),
                             ("row_raw_sha256", "0" * 64),
                             ("parser_locator", "line 999")):
            with self.subTest(field=field, value=value):
                policy = copy.deepcopy(self.policy)
                policy["bindings"][0][field] = value
                self.rejected(policy, "RECORD_DRIFT")

    def test_t05_strict_schema_hashes_and_duplicate_json_keys(self):
        for field, value in (("schema_version", True), ("schema_version", 2),
                             ("unknown", "value"), ("bindings", {}),
                             ("decision_sha256", "bad")):
            with self.subTest(field=field):
                policy = copy.deepcopy(self.policy)
                policy[field] = value
                self.rejected(policy)
        self.install()
        policy_path = Path(self.f.repo) / guard.BROAD_PRESERVATION_POLICY
        for raw in (b"{bad", b'{"schema_version":1,"schema_version":1}'):
            policy_path.write_bytes(raw)
            index, _ = self.scan()
            self.assertIn("POLICY_INVALID", [e["code"] for e in index.errors])
        policy = copy.deepcopy(self.policy)
        policy["decision_sha256"] = policy["decision_sha256"].upper()
        for binding in policy["bindings"]:
            binding["origin_raw_sha256"] = binding["origin_raw_sha256"].upper()
            binding["row_raw_sha256"] = binding["row_raw_sha256"].upper()
        self.install(policy)
        self.assertEqual(self.scan()[0].errors, [])

    def test_t06_exact_complete_unique_binding_set(self):
        for change in ("missing", "extra", "duplicate_id", "duplicate_record"):
            with self.subTest(change=change):
                policy = copy.deepcopy(self.policy)
                bindings = policy["bindings"]
                if change == "missing":
                    bindings.pop()
                elif change == "extra":
                    bindings.append(copy.deepcopy(bindings[0]))
                elif change == "duplicate_id":
                    bindings[1]["id"] = bindings[0]["id"]
                else:
                    bindings[1] = copy.deepcopy(bindings[0])
                    bindings[1]["id"] = "BPR-02"
                self.rejected(policy, "POLICY_INVALID")

    def test_t07_nonpreserving_or_unknown_dispositions_are_rejected(self):
        original = (Path(self.f.repo) / FIRST).read_text(encoding="utf-8")
        for keep in ("DELETE_SAFE", "MIGRATE", "ARCHIVE", "NOT_APPLICABLE",
                     "PRESERVE_USER_DATA", "UNKNOWN"):
            with self.subTest(keep=keep):
                policy = copy.deepcopy(self.policy)
                self.resign_first_row(
                    policy, original.replace("PRESERVE_REFERENCED", keep))
                policy["bindings"][0]["source_keep"] = keep
                self.install(policy)
                index, _ = self.scan()
                self.assertIn("RECORD_DRIFT", [e["code"] for e in index.errors])
                self.assertFalse(index.protected)

    def test_t08_destination_and_complete_error_pair_required(self):
        for change in ("destination", "missing_pair", "message", "duplicate_pair"):
            with self.subTest(change=change):
                policy = copy.deepcopy(self.policy)
                if change == "destination":
                    text = (Path(self.f.repo) / FIRST).read_text(encoding="utf-8")
                    self.resign_first_row(policy, text.replace(
                        "| %s | - | fixture" % self.ws,
                        "| %s/temp | - | fixture" % self.ws))
                elif change == "missing_pair":
                    policy["bindings"][0]["error_pair"].pop()
                elif change == "message":
                    policy["bindings"][0]["error_pair"][0]["message"] += "!"
                else:
                    policy["bindings"][0]["error_pair"][1] = copy.deepcopy(
                        policy["bindings"][0]["error_pair"][0])
                self.install(policy)
                index, _ = self.scan()
                self.assertTrue(index.errors)
                self.assertFalse(index.protected)
                if change == "destination":
                    # Restore only this owned synthetic input.
                    raw = self.policy["bindings"][0]["row_verbatim"]
                    current = (Path(self.f.repo) / FIRST).read_text(
                        encoding="utf-8").splitlines(keepends=True)
                    current[self.policy["bindings"][0]["global_line"] - 1] = raw
                    self.f.write(FIRST, "".join(current))

    def test_t09_no_generic_broad_or_environment_escape(self):
        for root in (str(Path(self.f.ws).parent), self.ws + "/builds",
                     "%TEMP%/anything", self.ws + "/*", "../escape",
                     self.ws + "/child/.."):
            with self.subTest(root=root):
                policy = copy.deepcopy(self.policy)
                binding = policy["bindings"][0]
                text = (Path(self.f.repo) / FIRST).read_text(encoding="utf-8")
                self.resign_first_row(policy, text.replace(self.ws, root))
                binding["root_abs"] = root
                if root.endswith("/child/.."):
                    # Even a resigned row and matching normal-parser errors
                    # must not authorize a traversing absolute spelling.
                    with mock.patch.object(guard, "_apply_broad_preservation",
                                           guard._finish_declaration_scan):
                        normal, _ = self.scan()
                    binding["error_pair"] = [e for e in normal.errors
                                             if e["file"] == FIRST]
                self.install(policy)
                index, _ = self.scan()
                self.assertTrue(index.errors)
                self.assertFalse(index.protected)
                self.f.write(FIRST, text)

    def test_t10_real_target_drift_is_fatal(self):
        self.install()
        original = guard.resolve_real_target
        with mock.patch.object(guard, "resolve_real_target", side_effect=(
                lambda path, what: self.ws + "-outside" if path == self.ws
                else original(path, what))):
            index, _ = self.scan()
        self.assertIn("REAL_DRIFT", [e["code"] for e in index.errors])
        self.assertFalse(index.protected)

    def test_t11_ancestor_descendant_and_new_root_boundary(self):
        self.install()
        index, _ = self.scan()
        added = set(index.protected) - set(self.base.protected)
        for root in added:
            self.assertTrue(index.evaluate(root))
            self.assertTrue(index.evaluate(root + "/future/deep/file"))
        self.assertTrue(index.evaluate(guard.norm_abs(str(Path(self.f.ws).parent))))
        for adjacent in (guard.norm_abs(self.f.repo), self.ws + "-other"):
            self.assertFalse([h for h in index.evaluate(adjacent)
                              if h["root"] in added])

    def test_t12_other_errors_and_staging_failures_never_partially_publish(self):
        self.install()
        self.f.write("doc/tasks/EXTRA.md",
                     "## Resource Manifest\n\n"
                     "| resource_type | source_path | disposition |\n"
                     "|---|---|---|\n| x | %TEMP%/x | PRESERVE_UNKNOWN |\n")
        before, scanned = self.scan()
        self.assertEqual(len(before.errors), 1)
        self.assertEqual(before.errors[0]["code"], "DECL_ENV")
        for method, failures in (("_register_protective", (1, 6, 12)),
                                 ("add_warning", (1, 6, 12))):
            original = getattr(guard.ProtectionIndex, method)
            for failure_at in failures:
                with self.subTest(method=method, failure_at=failure_at):
                    base = copy.deepcopy(self.base)
                    calls = [0]

                    def inject(instance, *args):
                        calls[0] += 1
                        if calls[0] == failure_at:
                            raise RuntimeError("injected staging failure")
                        return original(instance, *args)

                    with mock.patch.object(guard.ProtectionIndex, method, inject):
                        result, report = guard._apply_broad_preservation(
                            base, self.scanned)
                    self.assertIs(result, base)
                    self.assertEqual(base.protected, self.base.protected)
                    self.assertEqual(base.declarations, self.base.declarations)
                    self.assertEqual(base.warnings, self.base.warnings)
                    self.assertEqual(base.errors[:-1], self.base.errors)
                    self.assertEqual(report["errors"], 13)
        base = copy.deepcopy(self.base)
        original_finish = guard._finish_declaration_scan

        def fail_count(index, scanned):
            if index is not base:
                raise RuntimeError("injected counting failure")
            return original_finish(index, scanned)

        with mock.patch.object(guard, "_finish_declaration_scan", fail_count):
            result, report = guard._apply_broad_preservation(base, self.scanned)
        self.assertIs(result, base)
        self.assertFalse(base.protected)
        self.assertEqual(report["errors"], 13)

    def test_t13_evidence_json_prose_and_direct_index_have_no_permission(self):
        self.install()
        self.assertEqual(self.scan()[0].errors, [])
        index = guard.ProtectionIndex(self.f.repo, self.f.ws)
        index.add_evidence_pin(self.ws, FIRST, "pin")
        index.add_declaration(self.ws, "PRESERVE_REFERENCED", FIRST, "source")
        guard.parse_json_declarations(index, {
            "source_path": self.ws, "disposition": "PRESERVE_REFERENCED"},
            "fixture.json")
        self.assertEqual(index._prose_probe(self.ws)[0], "error")
        self.assertEqual(len(index.errors), 3)
        self.assertFalse(index.protected)

    def test_t14_missing_untracked_git_failure_and_read_failure(self):
        self.install(tracked=False)
        self.assertIn("POLICY_UNTRACKED", [e["code"] for e in self.scan()[0].errors])
        self.install()
        policy_path = Path(self.f.repo) / guard.BROAD_PRESERVATION_POLICY
        policy_path.unlink()
        self.assertIn("BROAD_PRESERVATION_POLICY_MISSING",
                      [e["code"] for e in self.scan()[0].errors])
        self.install()
        original_git = guard.git_checked

        def bad_git(repo, *args, **kwargs):
            if guard.BROAD_PRESERVATION_POLICY in args:
                raise guard.GuardError("GIT_FAILED", "injected Git failure")
            return original_git(repo, *args, **kwargs)

        with mock.patch.object(guard, "git_checked", bad_git):
            self.assertIn("GIT_FAILED", [e["code"] for e in self.scan()[0].errors])
        original_open = guard.io.open

        def bad_read(path, *args, **kwargs):
            if os.path.normcase(str(path)) == os.path.normcase(str(policy_path)):
                raise PermissionError("injected policy read failure")
            return original_open(path, *args, **kwargs)

        with mock.patch.object(guard.io, "open", bad_read):
            self.assertTrue(self.scan()[0].errors)
        nongit = Path(self.f.tmp) / "nongit"
        nongit.mkdir()
        with self.assertRaises(guard.GuardError):
            guard.scan_repo_declarations(str(nongit), self.f.ws)

    def test_t15_input_replaced_during_final_read_aborts_staging(self):
        self.install()
        original_open = guard.io.open
        for target, fail_at in ((Path(self.f.repo) / FIRST, 3),
                                (Path(self.f.repo) /
                                 guard.BROAD_PRESERVATION_POLICY, 2)):
            with self.subTest(target=target):
                calls = [0]

                def race(path, *args, **kwargs):
                    if os.path.normcase(str(path)) == os.path.normcase(str(target)):
                        calls[0] += 1
                        if calls[0] == fail_at:
                            return io.BytesIO(b"injected read drift")
                    return original_open(path, *args, **kwargs)

                with mock.patch.object(guard.io, "open", race):
                    index, scanned = self.scan()
                self.assertIn("SOURCE_DRIFT", [e["code"] for e in index.errors])
                self.assertFalse(index.protected)
                self.assertEqual(scanned["declarations"], 0)
        state = [0]
        original_register = guard.ProtectionIndex._register_protective
        original_real = guard.resolve_real_target

        def register(instance, declaration):
            original_register(instance, declaration)
            state[0] += 1

        def late_alias(path, what):
            if state[0] == 12 and path == self.ws:
                return self.ws + "-changed-target"
            return original_real(path, what)

        with mock.patch.object(guard.ProtectionIndex, "_register_protective",
                               register), mock.patch.object(
                                   guard, "resolve_real_target", late_alias):
            index, scanned = self.scan()
        self.assertIn("REAL_DRIFT", [e["code"] for e in index.errors])
        self.assertFalse(index.protected)
        self.assertEqual(scanned["declarations"], 0)

    def test_t16_three_consumers_share_whole_root_protection(self):
        self.install()
        candidate = self.f.candidate("temp", "future", {"keep.txt": "keep"})
        wt = self.f.make_worktree("future-wt", "fixture-wt")
        inventory = self.f.write_inventory([{"path": wt, "branch": "fixture-wt"}])
        clean_out = os.path.join(self.f.out, "clean")
        removed_out = os.path.join(self.f.out, "remove")
        consolidated_out = os.path.join(self.f.out, "consolidate")
        for script, args in (
                ("clean_workspace.py", ["--out", clean_out]),
                ("remove_worktrees.py", ["--inventory", inventory,
                                         "--out", removed_out]),
                ("consolidate.py", ["--mainline", "main",
                                    "--out", consolidated_out])):
            with self.subTest(script=script):
                result = run_tool(script, "--repo", self.f.repo,
                                  "--workspace-root", self.f.ws, *args)
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        clean = load_json(os.path.join(clean_out, "clean-workspace-dryrun.json"))
        self.assertEqual(clean["totals"]["would_delete"], 0)
        remove = load_json(os.path.join(removed_out, "worktree-removal-dryrun.json"))
        self.assertEqual(remove["totals"]["would_remove"], 0)
        self.assertEqual(remove["worktrees"][0]["decision"], "REJECT")
        consolidated = load_json(os.path.join(consolidated_out, "inventory.json"))
        self.assertTrue(any(w["protected"] for w in consolidated["worktrees"]
                            if w["normalized"] == guard.norm_abs(wt)))
        self.assertTrue(Path(candidate, "keep.txt").exists())
        self.assertTrue(Path(wt).exists())

    def test_t17_ruling_reference_and_bytes_are_not_substitutable(self):
        for ref in ("../ruling.md", "https://invalid/ruling.md",
                    "verification/another-ruling.md"):
            with self.subTest(ref=ref):
                policy = copy.deepcopy(self.policy)
                policy["decision_ref"] = ref
                self.rejected(policy, "POLICY_INVALID")
        self.install()
        self.f.write(guard.BROAD_PRESERVATION_RULING, "different ruling")
        self.assertIn("RULING_DRIFT", [e["code"] for e in self.scan()[0].errors])

    def test_t18_untracked_activation_and_cli_bypass_are_not_available(self):
        self.install(tracked=False)
        self.assertIn("POLICY_UNTRACKED", [e["code"] for e in self.scan()[0].errors])
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            guard.parse_args(["--allow-broad"])
        # The separate fixed-commit independent Review is a Task Gate,
        # never inferred from tracking or a successful fixture.


if __name__ == "__main__":
    unittest.main(verbosity=2)
