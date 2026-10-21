# -*- coding: utf-8 -*-
"""AC2–AC5 fixtures for WORKSPACE-DECLARATION-REMEDIATION-1.

Reuses the isolated repository fixture from the previous Task read-only
(``verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/fixture_support.py``);
nothing in that directory is modified.
"""
import os
import shutil
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OLD_TESTS = os.path.join(ROOT, "verification",
                         "WORKSPACE-CLEANUP-TOOL-HARDENING-1", "tests")
sys.path.insert(0, OLD_TESTS)

from fixture_support import (RepoFixture, guard, load_json,  # noqa: E402
                             run_tool, TOOLS)


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
                  % (normalized, [c.get("normalized") for c in report["candidates"]]))

    # ==================================================================
    # AC2: JSON declaration file identification
    # ==================================================================
    def test_ac2_non_declaration_json_is_warning(self):
        target = self.fx.candidate("temp", "JSON-NONDECL", {"f.txt": "x"})
        self.fx.declare_raw('runner stdout, not JSON at all',
                            relative="verification/runner.stdout.json",
                            commit=False)
        result = self.run_clean()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = self.report()
        self.assertTrue(any("JSON_NON_DECLARATION" in w["code"]
                            for w in report["declaration_warnings"]))
        self.assertEqual(report["declaration_scan"]["json_non_declaration"], 1)
        self.assertEqual(report["declaration_scan"]["json_parse_fatal"], 0)
        record = self.candidate_record(report, target)
        self.assertEqual(record["decision"], "CANDIDATE")

    def test_ac2_malformed_json_with_token_is_fatal(self):
        target = self.fx.candidate("temp", "JSON-TOKEN", {"f.txt": "x"})
        self.fx.declare_raw(
            '{"source_path": "%s", "disposition": "MIGRATE",'
            % target.replace("\\", "\\\\"),
            relative="verification/runner.stdout.json", commit=False)
        result = self.run_clean()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("JSON_PARSE", result.stdout + result.stderr)
        self.assertTrue(os.path.isdir(target))

    def test_ac2_malformed_json_with_manifest_name_is_fatal(self):
        target = self.fx.candidate("temp", "JSON-NAME", {"f.txt": "x"})
        self.fx.declare_raw('{"truncated": ',
                            relative="verification/resource-manifest.json",
                            commit=False)
        result = self.run_clean()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("JSON_PARSE", result.stdout + result.stderr)
        self.assertTrue(os.path.isdir(target))

    def test_ac2_tracked_artifact_json_stays_fatal(self):
        """Tracked malformed non-instrumentation JSON keeps the old contract."""
        self.fx.declare_raw('{"truncated": ',
                            relative="verification/broken-tracked.json")
        result = self.run_clean()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("JSON_PARSE", result.stdout + result.stderr)

    # ==================================================================
    # AC3: non-path source values
    # ==================================================================
    def test_ac3_not_applicable_source_is_warning(self):
        target = self.fx.candidate("temp", "PROSE-NA", {"f.txt": "x"})
        self.fx.declare([("NOT_APPLICABLE", "PRESERVE_REFERENCED")])
        result = self.run_clean()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = self.report()
        self.assertTrue(any("DECL_SOURCE_NOT_A_PATH" in w["code"]
                            for w in report["declaration_warnings"]))
        self.assertEqual(self.candidate_record(report, target)["decision"],
                         "CANDIDATE")

    def test_ac3_none_yet_and_chinese_prose_are_warnings(self):
        target = self.fx.candidate("temp", "PROSE-CJK", {"f.txt": "x"})
        self.fx.declare([("none yet", "PRESERVE_REFERENCED"),
                         ("见 G:/CODEX/New Manga", "PRESERVE_REFERENCED"),
                         ("释放后真实记录", "PRESERVE_REFERENCED")])
        result = self.run_clean()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = self.report()
        codes = [w["code"] for w in report["declaration_warnings"]]
        self.assertEqual(codes.count("DECL_SOURCE_NOT_A_PATH"), 3)
        self.assertEqual(self.candidate_record(report, target)["decision"],
                         "CANDIDATE")

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
        record = self.candidate_record(self.report(), target)
        self.assertEqual(record["decision"], "REJECT")
        self.assertTrue(os.path.isdir(target))

    # ==================================================================
    # AC4: legacy encoding
    # ==================================================================
    def test_ac4_gb18030_markdown_is_read_with_warning(self):
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
        record = self.candidate_record(report, target)
        self.assertEqual(record["decision"], "REJECT")

    def test_ac4_undecodable_markdown_stays_unreadable(self):
        path = os.path.join(self.fx.repo, "verification", "broken-encoding.md")
        write_bytes(path, b"\xff\xfe\x00\x00not text")
        self.fx.commit("broken encoding")
        result = self.run_clean()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("FILE_UNREADABLE", result.stdout + result.stderr)

    # ==================================================================
    # AC5: narrative table recognition
    # ==================================================================
    def test_ac5_chinese_header_table_is_narrative(self):
        target = self.fx.candidate("temp", "NARRATIVE", {"f.txt": "x"})
        self.fx.declare_raw(
            "# fixture\n\n## Resource Manifest\n\n"
            "| 资源类型 | 来源 | 处置 | 目标 |\n"
            "|---|---|---|---|\n"
            "| worktree | %s | PRESERVE_REFERENCED | - |\n"
            % target.replace("\\", "/"),
            relative="doc/tasks/FIXTURE-NARRATIVE.md")
        result = self.run_clean()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = self.report()
        self.assertTrue(any("TABLE_NOT_RESOURCE_MANIFEST" in w["code"]
                            for w in report["declaration_warnings"]))
        self.assertEqual(self.candidate_record(report, target)["decision"],
                         "CANDIDATE")

    def test_ac5_narrative_english_table_is_not_a_manifest(self):
        target = self.fx.candidate("temp", "NARRATIVE-EN", {"f.txt": "x"})
        self.fx.declare_raw(
            "# fixture\n\n## Resource Manifest\n\n"
            "| note | value |\n"
            "|---|---|\n"
            "| source | %s |\n"
            % target.replace("\\", "/"),
            relative="doc/tasks/FIXTURE-NARRATIVE-EN.md")
        result = self.run_clean()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = self.report()
        self.assertTrue(any("TABLE_NOT_RESOURCE_MANIFEST" in w["code"]
                            for w in report["declaration_warnings"]))

    def test_ac5_malformed_english_manifest_stays_hard_error(self):
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

    def test_ac5_narrative_canonical_evidence_table_is_skipped(self):
        self.fx.declare_raw(
            "# fixture\n\n## Canonical Evidence\n\n"
            "| 文件 | 提交 | 校验 |\n"
            "|---|---|---|\n"
            "| a.md | abc1234 | sha |\n",
            relative="doc/tasks/FIXTURE-EVIDENCE-NARRATIVE.md")
        result = self.run_clean()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = self.report()
        self.assertTrue(any("TABLE_NOT_CANONICAL_EVIDENCE" in w["code"]
                            for w in report["declaration_warnings"]))


if __name__ == "__main__":
    unittest.main()
