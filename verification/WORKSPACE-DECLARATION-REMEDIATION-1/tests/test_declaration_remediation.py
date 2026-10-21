# -*- coding: utf-8 -*-
"""AC2–AC5 fixtures for WORKSPACE-DECLARATION-REMEDIATION-1 (review r2).

Reuses the isolated repository fixture from the previous Task read-only
(``verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/fixture_support.py``);
nothing in that directory is modified.
"""
import hashlib
import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OLD_TESTS = os.path.join(ROOT, "verification",
                         "WORKSPACE-CLEANUP-TOOL-HARDENING-1", "tests")
sys.path.insert(0, OLD_TESTS)

from fixture_support import (RepoFixture, guard, load_json,  # noqa: E402
                             run_tool)


def make_junction(link, target):
    """Windows directory junction; returns False on unsupported hosts."""
    os.makedirs(target, exist_ok=True)
    if os.path.isdir(link):
        return True
    result = subprocess.run(["cmd", "/c", "mklink", "/J", link, target],
                            capture_output=True, text=True)
    return result.returncode == 0 and os.path.isdir(link)


def write_bytes(path, payload):
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(payload)
    return path


class DeclarationRemediationFixture(unittest.TestCase):
    def setUp(self):
        self.fx = RepoFixture(prefix="wc-decl-")
        self.addCleanup(self.fx.cleanup)

    # -- helpers -----------------------------------------------------------
    def run_clean(self, *extra):
        argv = ["--repo", self.fx.repo, "--workspace-root", self.fx.ws,
                "--out", self.fx.out]
        argv.extend(extra)
        return run_tool("clean_workspace.py", *argv)

    def report(self, name="clean-workspace-dryrun.json"):
        return load_json(os.path.join(self.fx.out, name))

    def candidate_record(self, report, path):
        normalized = guard.norm_abs(path)
        for item in report["candidates"]:
            if item.get("normalized") == normalized:
                return item
        self.fail("candidate %s not in report: %s"
                  % (normalized,
                     [c.get("normalized") for c in report["candidates"]]))

    def exception_manifest(self, entries):
        path = os.path.join(self.fx.tmp, "json-exceptions.json")
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(entries, handle, ensure_ascii=False)
        return path

    def sha(self, relative):
        full = os.path.join(self.fx.repo, relative.replace("/", os.sep))
        return hashlib.sha256(open(full, "rb").read()).hexdigest()

    # ==================================================================
    # F-02 / AC2: JSON declaration file identification
    # ==================================================================
    def test_ac2_explicit_path_sha_exception_is_warning(self):
        target = self.fx.candidate("temp", "JSON-NONDECL", {"f.txt": "x"})
        relative = "verification/runner.stdout.json"
        self.fx.declare_raw("runner stdout, not JSON at all", relative=relative,
                            commit=False)
        manifest = self.exception_manifest([{
            "path": relative, "sha256": self.sha(relative),
            "reason": "runner stdout fixture"}])
        result = self.run_clean("--json-exceptions", manifest)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = self.report()
        self.assertTrue(any("JSON_NON_DECLARATION" in w["code"]
                            for w in report["declaration_warnings"]))
        self.assertEqual(self.candidate_record(report, target)["decision"],
                         "CANDIDATE")

    def test_ac2_renamed_declaration_stdout_json_stays_fatal(self):
        """A real declaration renamed *.stdout.json cannot buy an exemption."""
        target = self.fx.candidate("temp", "JSON-RENAMED", {"f.txt": "x"})
        self.fx.declare_raw(
            '{"resources": [{"source_path": "%s", "disposition": "MIGRATE"},'
            % target.replace("\\", "\\\\"),
            relative="verification/real-decl.stdout.json", commit=False)
        result = self.run_clean()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("JSON_PARSE", result.stdout + result.stderr)
        self.assertTrue(os.path.isdir(target))

    def test_ac2_exception_with_wrong_sha_does_not_apply(self):
        target = self.fx.candidate("temp", "JSON-STALE", {"f.txt": "x"})
        relative = "verification/runner.stdout.json"
        self.fx.declare_raw("not json", relative=relative, commit=False)
        manifest = self.exception_manifest([{
            "path": relative, "sha256": "0" * 64,
            "reason": "stale fixture"}])
        result = self.run_clean("--json-exceptions", manifest)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("JSON_PARSE", result.stdout + result.stderr)

    def test_ac2_tracked_malformed_artifact_json_is_fatal(self):
        self.fx.declare_raw('{"truncated": ',
                            relative="verification/broken-tracked.json")
        result = self.run_clean()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("JSON_PARSE", result.stdout + result.stderr)

    # ==================================================================
    # F-01 / AC3: non-path source values and path-like values
    # ==================================================================
    def test_ac3_explicit_placeholder_and_pure_prose_are_warnings(self):
        target = self.fx.candidate("temp", "PROSE-CJK", {"f.txt": "x"})
        self.fx.declare([("NOT_APPLICABLE", "PRESERVE_REFERENCED"),
                         ("none yet", "PRESERVE_REFERENCED"),
                         ("释放后真实记录", "PRESERVE_REFERENCED")])
        result = self.run_clean()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = self.report()
        codes = [w["code"] for w in report["declaration_warnings"]]
        self.assertEqual(codes.count("DECL_SOURCE_NOT_A_PATH"), 3)
        self.assertEqual(self.candidate_record(report, target)["decision"],
                         "CANDIDATE")

    def test_ac3_pathlike_value_with_spaces_and_cjk_is_protected(self):
        """F-01: path-like values must never be skipped as prose."""
        target = self.fx.candidate("temp", "spaced data 中文", {"f.txt": "x"})
        self.fx.declare([(target, "PRESERVE_REFERENCED")])
        result = self.run_clean()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        record = self.candidate_record(self.report(), target)
        self.assertEqual(record["decision"], "REJECT")
        self.assertTrue(os.path.isdir(target))

    def test_ac3_pathlike_value_with_embedded_path_is_fatal(self):
        self.fx.declare([("见 G:/CODEX/New Manga", "PRESERVE_REFERENCED")])
        result = self.run_clean()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertNotIn("DECL_SOURCE_NOT_A_PATH", result.stdout + result.stderr)

    def test_ac3_bare_identifier_still_fails_closed(self):
        self.fx.declare([("P06-GC-DISTRIBUTION-MIGRATION",
                          "PRESERVE_REFERENCED")])
        result = self.run_clean()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("DECL_BARE_NAME", result.stdout + result.stderr)

    def test_ac3_real_preserve_path_still_protects(self):
        target = self.fx.candidate("temp", "REAL-PRESERVE", {"f.txt": "x"})
        self.fx.declare([(target, "PRESERVE_REFERENCED")])
        result = self.run_clean()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.candidate_record(self.report(), target)["decision"],
                         "REJECT")

    # ==================================================================
    # F-03 / AC5: generalized destination stays fatal
    # ==================================================================
    def test_ac5_generalized_destination_is_fatal(self):
        target = self.fx.candidate("temp", "GEN-DEST", {"f.txt": "x"})
        self.fx.declare([(target, "PRESERVE_REFERENCED", self.fx.ws)])
        result = self.run_clean()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("DECL_DESTINATION_GENERALIZED",
                      result.stdout + result.stderr)

    # ==================================================================
    # F-04 / AC5: incomplete resource/evidence schemas
    # ==================================================================
    def test_ac5_incomplete_resource_schema_is_fatal(self):
        self.fx.declare_raw(
            "# fixture\n\n## Resource Manifest\n\n"
            "| resource_type | source_path |\n"
            "|---|---|\n"
            "| worktree | G:/some/path |\n",
            relative="doc/tasks/FIXTURE-INCOMPLETE-RESOURCE.md")
        result = self.run_clean()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("TABLE_SCHEMA_INCOMPLETE", result.stdout + result.stderr)

    def test_ac5_incomplete_evidence_schema_is_fatal(self):
        self.fx.declare_raw(
            "# fixture\n\n## Canonical Evidence\n\n"
            "| evidence_id | sha256 |\n"
            "|---|---|\n"
            "| EV-1 | abc |\n",
            relative="doc/tasks/FIXTURE-INCOMPLETE-EVIDENCE.md")
        result = self.run_clean()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("TABLE_SCHEMA_INCOMPLETE", result.stdout + result.stderr)

    def test_ac5_narrative_table_without_identity_columns_is_warning(self):
        target = self.fx.candidate("temp", "NARRATIVE", {"f.txt": "x"})
        self.fx.declare_raw(
            "# fixture\n\n## Resource Manifest\n\n"
            "| 资源类型 | 说明 |\n"
            "|---|---|\n"
            "| worktree | %s |\n" % target.replace("\\", "/"),
            relative="doc/tasks/FIXTURE-NARRATIVE.md")
        result = self.run_clean()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = self.report()
        self.assertTrue(any("TABLE_NOT_RESOURCE_MANIFEST" in w["code"]
                            for w in report["declaration_warnings"]))
        self.assertEqual(self.candidate_record(report, target)["decision"],
                         "CANDIDATE")

    def test_ac5_malformed_english_manifest_stays_arity_error(self):
        self.fx.declare_raw(
            "# fixture\n\n## Resource Manifest\n\n"
            "| resource_type | source_path | disposition | destination_path "
            "| sha256/manifest | reference |\n"
            "|---|---|---|---|---|---|\n"
            "| worktree | G:/some/path | PRESERVE_REFERENCED | - | - | extra "
            "| seventh |\n",
            relative="doc/tasks/FIXTURE-MALFORMED.md")
        result = self.run_clean()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("TABLE_ROW_ARITY", result.stdout + result.stderr)

    # ==================================================================
    # F-05 / AC4: GB18030 fallback boundary
    # ==================================================================
    def test_ac4_gb18030_chinese_markdown_is_read_with_warning(self):
        target = self.fx.candidate("temp", "GBK-READ", {"f.txt": "x"})
        text = (
            "# 历史说明（GBK）\n\n"
            "## Resource Manifest\n\n"
            "| resource_type | source_path | disposition | destination_path "
            "| sha256/manifest | reference |\n"
            "|---|---|---|---|---|---|\n"
            "| worktree | %s | PRESERVE_REFERENCED | - | - | 说明 |\n"
            % target.replace("\\", "/"))
        path = os.path.join(self.fx.repo, "verification", "legacy-gbk.md")
        write_bytes(path, text.encode("gb18030"))
        self.fx.commit("legacy gbk")
        result = self.run_clean()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = self.report()
        self.assertTrue(any("FILE_ENCODING_LEGACY" in w["code"]
                            for w in report["declaration_warnings"]))
        self.assertEqual(self.candidate_record(report, target)["decision"],
                         "REJECT")

    def test_ac4_binary_with_nul_is_unreadable(self):
        path = os.path.join(self.fx.repo, "verification", "binary-nul.md")
        write_bytes(path, b"\x00\x01\x02\x03 not text")
        self.fx.commit("binary nul")
        result = self.run_clean()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("FILE_UNREADABLE", result.stdout + result.stderr)

    # ==================================================================
    # Review r3 F-01: existing single-component top-level CJK/space entries
    # ==================================================================
    def test_ac3_existing_single_component_cjk_toplevel_is_protected(self):
        """Review r3 F-01: existing repo top-level '资料 文件' must protect."""
        top = os.path.join(self.fx.repo, "资料 文件")
        os.makedirs(top, exist_ok=True)
        with open(os.path.join(top, "keep.txt"), "w", encoding="utf-8") as handle:
            handle.write("keep")
        self.fx.commit("top-level cjk dir")
        self.fx.declare([("资料 文件", "PRESERVE_REFERENCED")])
        command = ["--repo", self.fx.repo, "--workspace-root", self.fx.ws,
                   "--out", self.fx.out, "--audit-declarations"]
        result = run_tool("clean_workspace.py", *command)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        audit = load_json(os.path.join(self.fx.out,
                                       "declaration-audit.json"))
        self.assertEqual(audit["errors"], [])
        self.assertFalse(any("DECL_SOURCE_NOT_A_PATH" in w["code"]
                             for w in audit["warnings"]))
        self.assertGreaterEqual(audit["counts"]["protected_roots"], 1)

    def test_ac3_nonexistent_single_component_cjk_is_warning(self):
        target = self.fx.candidate("temp", "CJK-BARE", {"f.txt": "x"})
        self.fx.declare([("中文目录不存在", "PRESERVE_REFERENCED")])
        result = self.run_clean()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = self.report()
        self.assertTrue(any("DECL_SOURCE_NOT_A_PATH" in w["code"]
                            for w in report["declaration_warnings"]))
        self.assertEqual(self.candidate_record(report, target)["decision"],
                         "CANDIDATE")

    def test_ac3_generalized_junction_source_is_fatal(self):
        """Review r4 F-01: CJK junction to the workspace root stays fatal."""
        link = os.path.join(self.fx.repo, "资料 链接")
        if not make_junction(link, self.fx.ws):
            self.skipTest("directory junctions are not supported on this host")
        self.fx.declare([("资料 链接", "PRESERVE_REFERENCED")])
        result = self.run_clean()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("DECL_GENERALIZED", result.stdout + result.stderr)
        self.assertNotIn("DECL_SOURCE_NOT_A_PATH", result.stdout + result.stderr)

    def test_ac3_safe_junction_source_is_protected(self):
        """A CJK top-level junction to a repo dir resolves, not prose-skipped."""
        target = os.path.join(self.fx.repo, "safe-target")
        os.makedirs(target, exist_ok=True)
        link = os.path.join(self.fx.repo, "安全 链接")
        if not make_junction(link, target):
            self.skipTest("directory junctions are not supported on this host")
        self.fx.declare([("安全 链接", "PRESERVE_REFERENCED")])
        command = ["--repo", self.fx.repo, "--workspace-root", self.fx.ws,
                   "--out", self.fx.out, "--audit-declarations"]
        result = run_tool("clean_workspace.py", *command)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        audit = load_json(os.path.join(self.fx.out, "declaration-audit.json"))
        self.assertFalse(any("DECL_SOURCE_NOT_A_PATH" in w["code"]
                             for w in audit["warnings"]))

    def test_ac5_generalized_junction_evidence_is_fatal(self):
        link = os.path.join(self.fx.repo, "证据 链接")
        if not make_junction(link, self.fx.ws):
            self.skipTest("directory junctions are not supported on this host")
        self.fx.declare_raw(
            "# fixture\n\n## Canonical Evidence\n\n"
            "| evidence_id | path | commit | sha256 | class |\n"
            "|---|---|---|---|---|\n"
            "| EV-J | `证据 链接` | abc1234 | sha | CANONICAL |\n",
            relative="doc/tasks/FIXTURE-EVIDENCE-JUNCTION.md")
        result = self.run_clean()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("DECL_GENERALIZED", result.stdout + result.stderr)

    def test_ac4_short_control_rich_gb18030_payload_is_unreadable(self):
        # 24 bytes: 20 x 0x01 + GB18030 "中文" (4 bytes).  Decodes as GB18030
        # and contains CJK, but the control ratio must still reject it
        # (review r3: check applies to every length, not just >= 64).
        path = os.path.join(self.fx.repo, "verification", "short-binary.md")
        write_bytes(path, b"\x01" * 20 + "中文".encode("gb18030"))
        self.fx.commit("short binary")
        result = self.run_clean()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("FILE_UNREADABLE", result.stdout + result.stderr)

    def test_ac4_gb18030_decodable_binary_is_unreadable(self):
        # Decodes as one non-CJK control character, no NUL: rejected because a
        # legacy declaration note must contain CJK text.
        path = os.path.join(self.fx.repo, "verification", "binary-gb.md")
        write_bytes(path, b"\x81\x30\x81\x30")
        self.fx.commit("binary gb")
        result = self.run_clean()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("FILE_UNREADABLE", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()

