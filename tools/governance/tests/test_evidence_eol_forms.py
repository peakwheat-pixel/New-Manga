"""Gate acceptance of exact EOL forms for six-column historical evidence rows.

Codex ruling 2026-11-16 Q1=A: only rows that already existed, unchanged, in a
terminal card at the frozen baseline may use the LF/CRLF inference; everything
else must match an exact raw representation.
"""
import hashlib
import json
import shutil
import sys
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
BASELINE = "8db997f94683c6c959c30ba672af6df5d1bbc977"
CARD = "doc/tasks/FEA-11-HOST-AUTH-2.md"


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def check(clone, card):
    r = run(["pwsh", "-NoProfile", "-File", str(clone / "tools/governance/check.ps1"),
             "-TaskPath", card], clone)
    return r.stdout + r.stderr


class EolFormGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = Path(tempfile.mkdtemp(prefix=".eol-gate-test-"))
        cls.head = run(["git", "rev-parse", "HEAD"], REPO).stdout.strip()
        cls.template = cls.base / "template"
        run(["git", "clone", "--quiet", "--shared", "--no-checkout", str(REPO), str(cls.template)], REPO)
        run(["git", "-C", str(cls.template), "config", "core.autocrlf", "false"], REPO)
        run(["git", "-C", str(cls.template), "checkout", "--quiet", "--detach", cls.head], REPO)
        (cls.template / "tools/governance/check.ps1").write_bytes(
            (REPO / "tools/governance/check.ps1").read_bytes())

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.base, ignore_errors=True)

    # ------------------------------------------------------------------ helpers
    def clone(self):
        dst = Path(tempfile.mkdtemp(prefix="clone-", dir=self.base))
        shutil.rmtree(dst)
        shutil.copytree(self.template, dst, symlinks=True)
        return dst

    def synthetic(self, clone, *, sha, commit="-", status="done", card="GP-EOL-FIXTURE-1",
                  baseline="HEAD"):
        """Commit a minimal terminal card plus the pinned file, then point the
        checker's frozen baseline at that commit (mechanism test, not policy)."""
        if baseline == "HEAD":
            if (clone / "tools/governance/check.ps1").read_text(encoding="utf-8").count(BASELINE) != 1:
                raise AssertionError("frozen baseline constant not found")
        ck = clone / "tools/governance/check.ps1"
        ck.write_text(ck.read_text(encoding="utf-8").replace(BASELINE, "b" * 40), encoding="utf-8")
        body = "\n".join([
            "---",
            "id: " + card,
            "title: fixture",
            "kind: governance",
            "governance_version: 3",
            "status: " + status,
            "approval: fixture",
            "suggested_owner: dsh",
            "owner: dsh",
            "reviewer: dsh",
            "depends_on: []",
            "base_commit: " + self.head,
            "branch: main",
            "worktree: main",
            "integration_commit: " + self.head,
            "delivery_head: " + self.head,
            "canonical_evidence_status: complete",
            "resource_closeout_status: complete",
            "evidence_dir: null",
            "allowed_paths: []",
            "---",
            "",
            "## Acceptance Criteria",
            "",
            "- [x] **AC1 Fixture**: fixture. <<MET>>",
            "",
            "## Canonical Evidence",
            "",
            "| evidence_id | AC/Gate | path | commit | sha256 | class |",
            "|---|---|---|---|---|---|",
            "| EV-01 | AC1 | doc/STATUS.md | %s | %s | CANONICAL |" % (commit, sha),
            "",
            "## Resource Manifest",
            "",
            "| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |",
            "|---|---|---|---|---|---|",
            "| worktree | — | NOT_APPLICABLE | — | — | fixture |",
            "",
            "## Closeout Record",
            "",
            "- fixture",
            "",
        ])
        (clone / "doc/tasks" / (card + ".md")).write_text(body, encoding="utf-8", newline="\n")
        # make it the commit the (patched) baseline points at
        run(["git", "-C", str(clone), "add", "-A"], clone)
        run(["git", "-C", str(clone), "commit", "-q", "-m", "fixture"], clone)
        # keep the throw-away clone self-consistent for the ledger rule
        run([sys.executable, "-B", "tools/governance/task_ledger.py", "--write"], clone)
        run(["git", "-C", str(clone), "add", "-A"], clone)
        run(["git", "-C", str(clone), "commit", "-q", "-m", "fixture ledger"], clone)
        new_head = run(["git", "-C", str(clone), "rev-parse", "HEAD"], clone).stdout.strip()
        ck.write_text(ck.read_text(encoding="utf-8").replace("b" * 40, new_head), encoding="utf-8")
        return "doc/tasks/" + card + ".md"

    def worktree_forms(self, clone, rel="doc/STATUS.md"):
        raw = (clone / rel).read_bytes()
        lf = raw.replace(b"\r\n", b"\n")
        return {
            "RAW": hashlib.sha256(raw).hexdigest(),
            "LF": hashlib.sha256(lf).hexdigest(),
            "CRLF": hashlib.sha256(lf.replace(b"\n", b"\r\n")).hexdigest(),
        }

    # ------------------------------------------------------------------ positives
    def test_blob_crlf_and_lf_forms_pass(self):
        out = check(self.template, "doc/tasks/HOST-CORECLIENT-1.md")
        self.assertIn("Governance check: PASS", out)
        self.assertIn("行尾形态匹配（BLOB_CRLF）", out)

    def test_cleaned_worktree_path_still_passes_via_blob(self):
        out = check(self.template, "doc/tasks/HOST-CORECLIENT-1.md")
        self.assertNotIn("Canonical evidence 路径缺失", out)
        self.assertNotIn("Evidence SHA-256 不匹配", out)

    def test_no_commit_row_accepts_worktree_crlf_form(self):
        clone = self.clone()
        forms = self.worktree_forms(clone)
        card = self.synthetic(clone, sha=forms["CRLF"])
        out = check(clone, card)
        self.assertIn("Governance check: PASS", out)
        self.assertIn("行尾形态匹配（WORKTREE_CRLF）", out)

    # ------------------------------------------------------------------ negatives
    def test_one_byte_content_change_still_fails(self):
        clone = self.clone()
        forms = self.worktree_forms(clone)
        card = self.synthetic(clone, sha=forms["CRLF"])
        target = clone / "doc/STATUS.md"
        data = bytearray(target.read_bytes())
        data[0] = ord("X") if data[0] != ord("X") else ord("Y")
        target.write_bytes(bytes(data))
        out = check(clone, card)
        self.assertIn("Evidence SHA-256 不匹配", out)

    def test_mixed_line_endings_still_fail(self):
        clone = self.clone()
        forms = self.worktree_forms(clone)
        card = self.synthetic(clone, sha=forms["CRLF"])
        target = clone / "doc/STATUS.md"
        raw = target.read_bytes().replace(b"\r\n", b"\n")
        target.write_bytes(raw.replace(b"\n", b"\r\n", 1))
        out = check(clone, card)
        self.assertIn("Evidence SHA-256 不匹配", out)

    def test_unknown_digest_still_fails(self):
        clone = self.clone()
        card = self.synthetic(clone, sha="f" * 64)
        out = check(clone, card)
        self.assertIn("Evidence SHA-256 不匹配", out)

    def test_row_added_after_the_frozen_baseline_cannot_infer(self):
        # real frozen baseline (not patched): a row created now must match raw bytes
        clone = self.clone()
        forms = self.worktree_forms(clone)
        if (clone / "tools/governance/check.ps1").read_text(encoding="utf-8").count(BASELINE) != 1:
            raise AssertionError("frozen baseline constant not found")
        body = (clone / "doc/tasks/GP-LATE-FIXTURE-1.md")
        body.write_text("\n".join([
            "---",
            "id: GP-LATE-FIXTURE-1",
            "title: fixture",
            "kind: governance",
            "governance_version: 3",
            "status: done",
            "approval: fixture",
            "suggested_owner: dsh",
            "owner: dsh",
            "reviewer: dsh",
            "depends_on: []",
            "base_commit: " + self.head,
            "branch: main",
            "worktree: main",
            "integration_commit: " + self.head,
            "delivery_head: " + self.head,
            "canonical_evidence_status: complete",
            "resource_closeout_status: complete",
            "evidence_dir: null",
            "allowed_paths: []",
            "---",
            "",
            "## Acceptance Criteria",
            "",
            "- [x] **AC1 Fixture**: fixture. <<MET>>",
            "",
            "## Canonical Evidence",
            "",
            "| evidence_id | AC/Gate | path | commit | sha256 | class |",
            "|---|---|---|---|---|---|",
            "| EV-01 | AC1 | doc/STATUS.md | - | %s | CANONICAL |" % forms["CRLF"],
            "",
            "## Resource Manifest",
            "",
            "| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |",
            "|---|---|---|---|---|---|",
            "| worktree | — | NOT_APPLICABLE | — | — | fixture |",
            "",
            "## Closeout Record",
            "",
            "- fixture",
            "",
        ]), encoding="utf-8", newline="\n")
        out = check(clone, "doc/tasks/GP-LATE-FIXTURE-1.md")
        self.assertIn("Evidence SHA-256 不匹配", out)


if __name__ == "__main__":
    unittest.main()
