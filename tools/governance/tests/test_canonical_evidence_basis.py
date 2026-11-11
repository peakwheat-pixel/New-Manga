"""Discriminate legacy six-column pins from explicit seven-column byte bases."""
import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
CHECK = REPO / "tools" / "governance" / "check.ps1"
PNG_REL = "experiments/TASK-018/samples/s5-structure-crossing.png"
PLAN_REL = "doc/REBASELINE_PLAN.md"

LEGACY_HEADER = [
    "evidence_id",
    "AC/Gate",
    "path（仓库相对路径或绝对路径）",
    "commit",
    "sha256",
    "class (`CANONICAL` / `SOURCE_PIN`)",
]
BASIS_HEADER = LEGACY_HEADER + ["sha256_basis"]


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def git_blob(commit, path):
    return subprocess.run(
        ["git", "cat-file", "blob", f"{commit}:{path}"],
        cwd=REPO,
        check=True,
        capture_output=True,
    ).stdout


class CanonicalEvidenceBasisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=REPO, check=True,
            capture_output=True, text=True,
        ).stdout.strip()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix=".pin-basis-test-", dir=REPO)
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def run_fixture(self, header, values):
        task = self.root / "fixture.md"
        row = "| " + " | ".join(values) + " |"
        table_header = "| " + " | ".join(header) + " |"
        separator = "| " + " | ".join(["---"] * len(header)) + " |"
        task.write_text(
            "\n".join(
                [
                    "---",
                    "id: FIXTURE-PIN-BASIS-1",
                    "title: pin basis fixture",
                    "kind: governance",
                    "governance_version: 3",
                    "status: in_review",
                    "approval: fixture",
                    "suggested_owner: codex",
                    "owner: codex",
                    "reviewer: codex",
                    "depends_on: []",
                    f"base_commit: {self.head}",
                    "branch: fixture",
                    "worktree: fixture",
                    "integration_commit: null",
                    "delivery_head: null",
                    "canonical_evidence_status: complete",
                    "resource_closeout_status: pending",
                    "evidence_dir: null",
                    "allowed_paths: []",
                    "---",
                    "# Pin basis fixture",
                    "",
                    "## Acceptance Criteria",
                    "",
                    "- [x] **AC1 Fixture**: Exercise evidence bytes. <<MET>>",
                    "",
                    "## Canonical Evidence",
                    "",
                    table_header,
                    separator,
                    row,
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
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        result = subprocess.run(
            ["pwsh", "-NoProfile", "-File", str(CHECK), "-TaskPath", str(task)],
            cwd=REPO,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return (result.stdout or "") + (result.stderr or "")

    def assert_basis_passes(self, output):
        self.assertNotIn("EVIDENCE_BASIS_", output)
        self.assertNotIn("Evidence SHA-256 不匹配", output)
        self.assertNotIn("Evidence commit 不含所 pin 文件", output)

    def assert_basis_fails(self, output, code):
        self.assertIn(code, output)

    def explicit_row(self, path, sha, basis, commit="null", gate="AC2 fixture"):
        return ["EV1", gate, str(path), commit, sha, "CANONICAL", basis]

    def test_legacy_six_column_worktree_pin_remains_valid(self):
        path = REPO / PLAN_REL
        digest = sha256(path.read_bytes())
        output = self.run_fixture(
            LEGACY_HEADER,
            ["EV1", "AC2 legacy worktree", PLAN_REL, self.head, digest, "CANONICAL"],
        )
        self.assert_basis_passes(output)

    def test_legacy_plain_path_header_remains_supported(self):
        header = LEGACY_HEADER.copy()
        header[2] = "path"
        path = REPO / PLAN_REL
        output = self.run_fixture(
            header,
            ["EV1", "AC2 legacy path alias", PLAN_REL, self.head, sha256(path.read_bytes()), "CANONICAL"],
        )
        self.assert_basis_passes(output)

    def test_legacy_six_column_blob_pin_remains_an_alternative(self):
        path = REPO / PLAN_REL
        blob = git_blob(self.head, PLAN_REL)
        worktree = path.read_bytes()
        if worktree == blob:
            self.skipTest("checkout has identical blob and worktree bytes; AC4 provides the cross-EOL differential")
        output = self.run_fixture(
            LEGACY_HEADER,
            ["EV1", "AC2 legacy blob", PLAN_REL, self.head, sha256(blob), "CANONICAL"],
        )
        self.assert_basis_passes(output)

    def test_new_blob_basis_hashes_exact_png_blob_bytes(self):
        blob = git_blob(self.head, PNG_REL)
        self.assertTrue(blob.startswith(b"\x89PNG\r\n\x1a\n"))
        output = self.run_fixture(
            BASIS_HEADER,
            self.explicit_row(PNG_REL, sha256(blob), "BLOB", commit=self.head),
        )
        self.assert_basis_passes(output)

    def test_new_blob_basis_uses_commit_bytes_across_checkout_eol(self):
        blob = git_blob(self.head, PLAN_REL)
        worktree = (REPO / PLAN_REL).read_bytes()
        output = self.run_fixture(
            BASIS_HEADER,
            self.explicit_row(PLAN_REL, sha256(blob), "BLOB", commit=self.head),
        )
        self.assert_basis_passes(output)
        if blob != worktree:
            self.assertNotEqual(sha256(blob), sha256(worktree))

    def test_blob_commit_without_path_fails_even_if_worktree_path_is_missing(self):
        missing = REPO / self.root.name / "absent.png"
        output = self.run_fixture(
            BASIS_HEADER,
            self.explicit_row(missing, "0" * 64, "BLOB", commit=self.head),
        )
        self.assert_basis_fails(output, "EVIDENCE_BASIS_BLOB_PATH_MISSING")

    def test_basis_is_required_and_case_sensitive(self):
        path = REPO / PLAN_REL
        digest = sha256(git_blob(self.head, PLAN_REL))
        blank = self.run_fixture(
            BASIS_HEADER,
            ["EV1", "AC2 fixture", PLAN_REL, self.head, digest, "CANONICAL", ""],
        )
        self.assert_basis_fails(blank, "EVIDENCE_BASIS_INVALID")
        lowercase = self.run_fixture(
            BASIS_HEADER,
            self.explicit_row(PLAN_REL, digest, "blob", commit=self.head),
        )
        self.assert_basis_fails(lowercase, "EVIDENCE_BASIS_INVALID")

    def test_new_table_header_must_identify_the_basis_column(self):
        path = REPO / PLAN_REL
        header = BASIS_HEADER[:-1] + ["basis"]
        output = self.run_fixture(
            header,
            self.explicit_row(PLAN_REL, sha256(git_blob(self.head, PLAN_REL)), "BLOB", commit=self.head),
        )
        self.assert_basis_fails(output, "EVIDENCE_BASIS_HEADER_INVALID")

    def test_new_basis_rows_reject_missing_or_extra_columns(self):
        row = self.explicit_row(PLAN_REL, sha256(git_blob(self.head, PLAN_REL)), "BLOB", commit=self.head)
        for name, values in (("missing", row[:-1]), ("extra", row + ["unexpected"])):
            with self.subTest(name=name):
                output = self.run_fixture(BASIS_HEADER, values)
                self.assert_basis_fails(output, "EVIDENCE_BASIS_ROW_ARITY")

    def test_new_basis_rejects_malformed_sha256(self):
        output = self.run_fixture(
            BASIS_HEADER,
            self.explicit_row(PLAN_REL, "not-a-sha256", "BLOB", commit=self.head),
        )
        self.assert_basis_fails(output, "EVIDENCE_BASIS_SHA_INVALID")

    def test_blob_basis_rejects_invalid_commit_values(self):
        digest = sha256(git_blob(self.head, PLAN_REL))
        for name, commit in (("malformed", "not-a-commit"), ("unknown", "f" * 40)):
            with self.subTest(name=name):
                output = self.run_fixture(
                    BASIS_HEADER,
                    self.explicit_row(PLAN_REL, digest, "BLOB", commit=commit),
                )
                self.assert_basis_fails(output, "EVIDENCE_BASIS_BLOB_COMMIT_REQUIRED" if name == "malformed" else "EVIDENCE_BASIS_BLOB_PATH_MISSING")

    def test_each_basis_rejects_paths_outside_its_declared_domain(self):
        digest = "0" * 64
        with tempfile.TemporaryDirectory(prefix="pin-basis-external-path-") as external:
            external_path = Path(external) / "evidence.txt"
            external_path.write_text("external", encoding="utf-8")
            cases = (
                ("blob outside repo", external_path, "BLOB", self.head, "EVIDENCE_BASIS_BLOB_PATH_INVALID"),
                ("worktree outside repo", external_path, "WORKTREE", self.head, "EVIDENCE_BASIS_WORKTREE_PATH_INVALID"),
                ("external inside repo", self.root / "inside.txt", "EXTERNAL_SHA256", "null", "EVIDENCE_BASIS_EXTERNAL_PATH_INVALID"),
            )
            for name, path, basis, commit, code in cases:
                with self.subTest(name=name):
                    output = self.run_fixture(
                        BASIS_HEADER,
                        self.explicit_row(path, digest, basis, commit=commit, gate="AC4 path-domain fixture WORKTREE_ENV=Windows"),
                    )
                    self.assert_basis_fails(output, code)

    def test_worktree_requires_environment_and_never_falls_back_to_blob(self):
        path = REPO / PLAN_REL
        blob_sha = sha256(git_blob(self.head, PLAN_REL))
        worktree_sha = sha256(path.read_bytes())
        if blob_sha == worktree_sha:
            self.skipTest("checkout has identical blob and worktree bytes; AC4 provides the cross-EOL differential")
        missing_environment = self.run_fixture(
            BASIS_HEADER,
            self.explicit_row(PLAN_REL, worktree_sha, "WORKTREE", commit=self.head),
        )
        self.assert_basis_fails(missing_environment, "EVIDENCE_BASIS_WORKTREE_ENV_REQUIRED")
        blob_fallback = self.run_fixture(
            BASIS_HEADER,
            self.explicit_row(
                PLAN_REL, blob_sha, "WORKTREE", commit=self.head,
                gate="AC2 WORKTREE_ENV=Windows; Git=2.52.0; core.autocrlf=true",
            ),
        )
        self.assert_basis_fails(blob_fallback, "EVIDENCE_BASIS_HASH_MISMATCH")

    def test_worktree_hashes_crlf_and_mixed_eol_exact_bytes(self):
        cases = {
            "crlf": b"first\r\nsecond\r\n",
            "mixed": b"first\r\nsecond\nthird\r\n",
        }
        for name, raw in cases.items():
            with self.subTest(name=name):
                path = self.root / f"{name}.txt"
                path.write_bytes(raw)
                normalized = raw.replace(b"\r\n", b"\n")
                self.assertNotEqual(sha256(raw), sha256(normalized))
                output = self.run_fixture(
                    BASIS_HEADER,
                    self.explicit_row(
                        path,
                        sha256(raw),
                        "WORKTREE",
                        gate="AC3 WORKTREE_ENV=Windows; raw fixture bytes",
                    ),
                )
                self.assert_basis_passes(output)
                normalized_pin = self.run_fixture(
                    BASIS_HEADER,
                    self.explicit_row(
                        path,
                        sha256(normalized),
                        "WORKTREE",
                        gate="AC3 WORKTREE_ENV=Windows; raw fixture bytes",
                    ),
                )
                self.assert_basis_fails(normalized_pin, "EVIDENCE_BASIS_HASH_MISMATCH")

    def test_external_sha256_reads_exact_png_bytes(self):
        png = git_blob(self.head, PNG_REL)
        with tempfile.TemporaryDirectory(prefix="pin-basis-external-") as external:
            path = Path(external) / "sample.png"
            path.write_bytes(png)
            output = self.run_fixture(
                BASIS_HEADER,
                self.explicit_row(path, sha256(png), "EXTERNAL_SHA256"),
            )
            self.assert_basis_passes(output)

    def test_external_sha256_unreadable_path_fails_closed(self):
        with tempfile.TemporaryDirectory(prefix="pin-basis-external-") as external:
            missing = Path(external) / "missing.png"
            output = self.run_fixture(
                BASIS_HEADER,
                self.explicit_row(missing, "0" * 64, "EXTERNAL_SHA256"),
            )
            self.assert_basis_fails(output, "EVIDENCE_BASIS_EXTERNAL_PATH_UNREADABLE")

    def test_worktree_missing_path_fails_closed(self):
        missing = self.root / "not-created.txt"
        output = self.run_fixture(
            BASIS_HEADER,
            self.explicit_row(
                missing,
                "0" * 64,
                "WORKTREE",
                gate="AC3 WORKTREE_ENV=Windows; raw fixture bytes",
            ),
        )
        self.assert_basis_fails(output, "EVIDENCE_BASIS_WORKTREE_PATH_UNREADABLE")


if __name__ == "__main__":
    unittest.main()
