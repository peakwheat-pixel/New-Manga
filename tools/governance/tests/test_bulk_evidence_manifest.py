"""EVIDENCE-MANIFEST.json (bulk evidence) — Codex ruling 2026-11-17 Q1=A / Q3 / Q4.

The gate must re-enumerate and re-hash the evidence dir itself: the manifest is
never trusted, the file set must be exactly equal, and the mechanism is limited to
``kind: research`` cards.
"""
import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


class BulkEvidenceManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = Path(tempfile.mkdtemp(prefix=".bulk-evidence-test-"))
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

    def clone(self):
        dst = Path(tempfile.mkdtemp(prefix="clone-", dir=self.base))
        shutil.rmtree(dst)
        shutil.copytree(self.template, dst, symlinks=True)
        return dst

    # ---------------------------------------------------------------- fixtures
    def build(self, clone, *, kind="research", files=None, manifest=None, register=True):
        ev = clone / "verification" / "GP-BULK-1"
        ev.mkdir(parents=True, exist_ok=True)
        files = files if files is not None else {"a.txt": b"alpha\n", "sub/b.json": b'{"b":1}\n'}
        for rel, data in files.items():
            target = ev / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        entries = manifest if manifest is not None else [
            {"path": rel, "sha256": hashlib.sha256(data).hexdigest()} for rel, data in files.items()]
        (ev / "EVIDENCE-MANIFEST.json").write_text(
            json.dumps({"schema_version": 1, "task_id": "GP-BULK-1", "files": entries}),
            encoding="utf-8")
        man_digest = hashlib.sha256((ev / "EVIDENCE-MANIFEST.json").read_bytes()).hexdigest()
        rows = ["| evidence_id | AC/Gate | path | commit | sha256 | class |", "|---|---|---|---|---|---|"]
        if register:
            rows.append("| EV-MANIFEST | AC1 | verification/GP-BULK-1/EVIDENCE-MANIFEST.json | - | %s | CANONICAL |" % man_digest)
        body = "\n".join([
            "---", "id: GP-BULK-1", "title: fixture", "kind: " + kind,
            "governance_version: 3", "status: done", "approval: fixture",
            "suggested_owner: dsh", "owner: dsh", "reviewer: dsh", "depends_on: []",
            "base_commit: " + self.head, "branch: main", "worktree: main",
            "integration_commit: " + self.head, "delivery_head: " + self.head,
            "canonical_evidence_status: complete", "resource_closeout_status: complete",
            "evidence_dir: verification/GP-BULK-1", "allowed_paths: []", "---",
            "",
            "## Acceptance Criteria",
            "", "- [x] **AC1 Fixture**: fixture. <<MET>> <!-- verified: fixture -->",
            "",
            "## Canonical Evidence",
            "", *rows,
            "",
            "## Resource Manifest",
            "",
            "| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |",
            "|---|---|---|---|---|---|",
            "| doc-only | — | NOT_APPLICABLE | — | — | fixture |",
            "",
            "## Closeout Record", "", "- fixture", "",
        ])
        path = clone / "doc/tasks/GP-BULK-1.md"
        path.write_text(body, encoding="utf-8", newline="\n")
        run([__import__("sys").executable, "-B", "tools/governance/task_ledger.py", "--write"], clone)
        return "doc/tasks/GP-BULK-1.md"

    def check(self, clone):
        r = run(["pwsh", "-NoProfile", "-File", str(clone / "tools/governance/check.ps1"),
                 "-TaskPath", "doc/tasks/GP-BULK-1.md"], clone)
        return r.stdout + r.stderr

    # ---------------------------------------------------------------- positives
    def test_complete_manifest_passes(self):
        clone = self.clone()
        self.build(clone)
        out = self.check(clone)
        self.assertIn("Governance check: PASS", out)

    # ---------------------------------------------------------------- negatives
    def test_unlisted_file_fails(self):
        clone = self.clone()
        files = {"a.txt": b"alpha\n"}
        self.build(clone, files=files)
        (clone / "verification/GP-BULK-1/extra.txt").write_bytes(b"extra\n")
        out = self.check(clone)
        self.assertIn("EVIDENCE_MANIFEST_INCOMPLETE", out)

    def test_missing_file_fails(self):
        clone = self.clone()
        files = {"a.txt": b"alpha\n"}
        entries = [{"path": "a.txt", "sha256": hashlib.sha256(b"alpha\n").hexdigest()},
                   {"path": "gone.txt", "sha256": hashlib.sha256(b"x").hexdigest()}]
        self.build(clone, files=files, manifest=entries)
        out = self.check(clone)
        self.assertIn("EVIDENCE_MANIFEST_MISSING_FILE", out)

    def test_hash_mismatch_fails(self):
        clone = self.clone()
        files = {"a.txt": b"alpha\n"}
        entries = [{"path": "a.txt", "sha256": "f" * 64}]
        self.build(clone, files=files, manifest=entries)
        out = self.check(clone)
        self.assertIn("EVIDENCE_MANIFEST_HASH_MISMATCH", out)

    def test_path_escape_is_rejected(self):
        clone = self.clone()
        entries = [{"path": "../escape.txt", "sha256": "a" * 64},
                   {"path": "C:/tmp/x.txt", "sha256": "a" * 64},
                   {"path": "*.txt", "sha256": "a" * 64}]
        self.build(clone, files={"a.txt": b"alpha\n"}, manifest=entries)
        out = self.check(clone)
        self.assertIn("EVIDENCE_MANIFEST_INVALID", out)

    def test_duplicate_path_is_rejected(self):
        clone = self.clone()
        dup = hashlib.sha256(b"alpha\n").hexdigest()
        entries = [{"path": "a.txt", "sha256": dup}, {"path": "a.txt", "sha256": dup}]
        self.build(clone, files={"a.txt": b"alpha\n"}, manifest=entries)
        out = self.check(clone)
        self.assertIn("EVIDENCE_MANIFEST_INVALID", out)

    def test_unregistered_manifest_is_rejected(self):
        clone = self.clone()
        self.build(clone, register=False)
        out = self.check(clone)
        self.assertIn("EVIDENCE_MANIFEST_NOT_REGISTERED", out)

    def test_non_research_card_cannot_use_the_manifest(self):
        clone = self.clone()
        self.build(clone, kind="implementation")
        out = self.check(clone)
        self.assertIn("EVIDENCE_MANIFEST_NOT_ALLOWED", out)


if __name__ == "__main__":
    unittest.main()
