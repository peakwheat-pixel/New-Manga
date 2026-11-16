"""Unit tests for the read-only Canonical Evidence pin sweep (GOV-EVIDENCE-PIN-REPAIR-1 AC1)."""
import hashlib
import pathlib
import sys
import unittest

REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools" / "governance"))

import audit_evidence_pins as sweep  # noqa: E402


def row(digests, commit="-", path="doc/STATUS.md"):
    return {"card": "doc/tasks/X.md", "line": 1, "path": path, "commit": commit,
            "digests": digests, "recorded_cell": ",".join(digests)}


class JudgeTests(unittest.TestCase):
    def setUp(self):
        self.data = b"line one\nline two\n"
        self.good = hashlib.sha256(self.data).hexdigest()
        self.reps = {"WORKTREE": self.good,
                     "LF": hashlib.sha256(self.data).hexdigest(),
                     "CRLF": hashlib.sha256(self.data.replace(b"\n", b"\r\n")).hexdigest()}

    def test_64_hex_matching_worktree_passes(self):
        verdict, code, _, basis = sweep.judge(row([self.good]), None, self.reps, False)
        self.assertEqual((verdict, code, basis), ("PASS", "WORKTREE_MATCH", "WORKTREE"))

    def test_multi_digest_cell_passes_when_one_is_valid(self):
        other = "0" * 64
        verdict, code, _, _ = sweep.judge(row([other, self.good]), None, self.reps, False)
        self.assertEqual((verdict, code), ("PASS", "WORKTREE_MATCH"))

    def test_no_64_hex_digest_fails(self):
        verdict, code, _, _ = sweep.judge(row([]), None, self.reps, False)
        self.assertEqual((verdict, code), ("FAIL", "SHA_NOT_64_HEX"))

    def test_content_change_of_one_byte_fails(self):
        changed = hashlib.sha256(b"line one\nline twO\n").hexdigest()
        verdict, code, _, _ = sweep.judge(row([changed]), None, self.reps, False)
        self.assertEqual(verdict, "FAIL")
        self.assertEqual(code, "SHA_MISMATCH")

    def test_unregistered_line_ending_variant_fails(self):
        # only CRLF is registered; a mixed representation matches nothing
        mixed = self.data.replace(b"\n", b"\r\n", 1)
        digest = hashlib.sha256(mixed).hexdigest()
        verdict, code, _, _ = sweep.judge(row([digest]), None, self.reps, False)
        self.assertEqual((verdict, code), ("FAIL", "SHA_MISMATCH"))

    def test_missing_path_wins_over_other_reasons(self):
        verdict, code, _, _ = sweep.judge(row([self.good]), None, {}, False)
        self.assertEqual((verdict, code), ("FAIL", "PATH_MISSING"))

    def test_commit_blob_match_passes(self):
        verdict, code, _, basis = sweep.judge(row([self.good]), self.data, self.reps, True)
        self.assertEqual((verdict, code, basis), ("PASS", "BLOB_MATCH", "BLOB"))

    def test_commit_blob_mismatch_but_worktree_match_is_warn(self):
        verdict, code, _, _ = sweep.judge(row([self.good]), b"other bytes\n", self.reps, True)
        self.assertEqual((verdict, code), ("WARN", "BLOB_MISMATCH_WORKTREE"))

    def test_pending_commit_text_is_not_commit_shaped(self):
        self.assertIsNone(sweep.COMMIT.match("pending"))
        verdict, code, _, _ = sweep.judge(row([self.good], commit="pending"),
                                          None, self.reps, False)
        self.assertEqual(verdict, "PASS")

    def test_multi_digest_extraction_from_cell(self):
        cell = ("`" + "a" * 64 + "` / `" + "b" * 64 + "`").lower()
        self.assertEqual(sweep.HEX64.findall(cell), ["a" * 64, "b" * 64])


class RealRepoTests(unittest.TestCase):
    """The tool must self-validate on two known cards."""

    def run_sweep(self, *cards):
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = sweep.main(["--cards"] + list(cards))
        return rc, buf.getvalue()

    def test_known_good_card_has_no_failures(self):
        rc, out = self.run_sweep("doc/tasks/GOV-DECLARATION-SCAN-CLEANUP-1.md")
        self.assertEqual(rc, 0, out)
        self.assertIn("FAIL: 0", out)

    def test_known_broken_card_reports_its_rows(self):
        rc, out = self.run_sweep("doc/tasks/FEA-11-HOST-AUTH-2.md")
        self.assertEqual(rc, 1, out)
        self.assertIn("FEA-11-HOST-AUTH-3.md", out)


if __name__ == "__main__":
    unittest.main()
