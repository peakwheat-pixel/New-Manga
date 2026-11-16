"""Discriminate legacy six-column pins from explicit seven-column byte bases."""
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
R0_HEAD = "bfae0b9bd6a9b85a9a546d2adda0b684783ddb24"
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


def git_blob(commit, path, repo=REPO):
    return subprocess.run(
        ["git", "cat-file", "blob", f"{commit}:{path}"],
        cwd=repo,
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
        task_workspace = next(
            (parent for parent in REPO.parents if parent.name == "FEA-15-PIN-BASIS-ENFORCE-1"),
            REPO.parent.with_name(REPO.name + ".workspace") / "FEA-15-PIN-BASIS-ENFORCE-1",
        )
        task_workspace.mkdir(parents=True, exist_ok=True)
        cls.clone_temp = tempfile.TemporaryDirectory(prefix="ac2ac3-governance-fixture-", dir=task_workspace)
        cls.repo_root = Path(cls.clone_temp.name) / "repo"
        autocrlf_result = subprocess.run(
            ["git", "config", "--get", "core.autocrlf"],
            cwd=REPO,
            capture_output=True,
            text=True,
        )
        cls.autocrlf = autocrlf_result.stdout.strip().lower() if autocrlf_result.returncode == 0 else "false"
        if cls.autocrlf not in {"true", "false", "input"}:
            cls.autocrlf = "false"
        subprocess.run(
            ["git", "clone", "--shared", "--no-checkout", str(REPO), str(cls.repo_root)],
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(["git", "-C", str(cls.repo_root), "config", "--local", "core.autocrlf", cls.autocrlf], check=True)
        subprocess.run(["git", "-C", str(cls.repo_root), "config", "--local", "core.longpaths", "true"], check=True)
        subprocess.run(
            ["git", "-C", str(cls.repo_root), "checkout", "--detach", cls.head],
            check=True,
            capture_output=True,
            text=True,
        )
        cls.check = cls.repo_root / "tools" / "governance" / "check.ps1"
        plan = cls.repo_root / PLAN_REL
        plan_bytes = plan.read_bytes()
        if len(plan_bytes) > 7000:
            marker = "## 历史快照".encode("utf-8")
            marker_at = plan_bytes.find(marker)
            if marker_at < 0:
                raise RuntimeError("Fixture checkout Plan exceeds byte budget and has no history boundary")
            marker_end = plan_bytes.find(b"\n", marker_at)
            if marker_end < 0:
                raise RuntimeError("Fixture checkout Plan history heading is not line-terminated")
            plan.write_bytes(plan_bytes[: marker_end + 1])

    @classmethod
    def tearDownClass(cls):
        cls.clone_temp.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix=".pin-basis-test-", dir=self.repo_root)
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def run_fixture(self, header, values):
        task = self.repo_root / "doc" / "tasks" / "FEA-15-PIN-BASIS-ENFORCE-1.md"
        row = "| " + " | ".join(values) + " |"
        table_header = "| " + " | ".join(header) + " |"
        separator = "| " + " | ".join(["---"] * len(header)) + " |"
        task.write_text(
            "\n".join(
                [
                    "---",
                    "id: FEA-15-PIN-BASIS-ENFORCE-1",
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
        # The fixture card changes a terminal Task into a non-terminal one, so the
        # clone's ledger no longer matches its own Task set.  Regenerate it inside
        # the throw-away clone; this keeps the fixture self-consistent without
        # touching any assertion (the checked invariants stay exactly the same).
        subprocess.run(
            [sys.executable, "-B", "tools/governance/task_ledger.py", "--write"],
            cwd=self.repo_root,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        result = subprocess.run(
            ["pwsh", "-NoProfile", "-File", str(self.check), "-TaskPath", "doc/tasks/FEA-15-PIN-BASIS-ENFORCE-1.md"],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return f"FIXTURE_PROCESS_EXIT={result.returncode}\n" + (result.stdout or "") + (result.stderr or "")

    def assert_basis_passes(self, output):
        self.assertIn("FIXTURE_PROCESS_EXIT=0", output)
        self.assertIn("Governance check: PASS", output)
        self.assertNotIn("EVIDENCE_BASIS_", output)
        self.assertNotIn("Evidence SHA-256 不匹配", output)
        self.assertNotIn("Evidence commit 不含所 pin 文件", output)

    def assert_basis_fails(self, output, code):
        self.assertIn(code, output)

    def explicit_row(self, path, sha, basis, commit="null", gate="AC2 fixture"):
        return ["EV1", gate, str(path), commit, sha, "CANONICAL", basis]

    def test_legacy_six_column_worktree_pin_remains_valid(self):
        path = self.repo_root / PLAN_REL
        digest = sha256(path.read_bytes())
        output = self.run_fixture(
            LEGACY_HEADER,
            ["EV1", "AC2 legacy worktree", PLAN_REL, self.head, digest, "CANONICAL"],
        )
        self.assert_basis_passes(output)

    def test_legacy_plain_path_header_remains_supported(self):
        header = LEGACY_HEADER.copy()
        header[2] = "path"
        path = self.repo_root / PLAN_REL
        output = self.run_fixture(
            header,
            ["EV1", "AC2 legacy path alias", PLAN_REL, self.head, sha256(path.read_bytes()), "CANONICAL"],
        )
        self.assert_basis_passes(output)

    def test_legacy_six_column_blob_pin_remains_an_alternative(self):
        path = self.repo_root / PLAN_REL
        blob = git_blob(self.head, PLAN_REL, self.repo_root)
        worktree = path.read_bytes()
        if worktree == blob:
            self.skipTest("checkout has identical blob and worktree bytes; AC4 provides the cross-EOL differential")
        output = self.run_fixture(
            LEGACY_HEADER,
            ["EV1", "AC2 legacy blob", PLAN_REL, self.head, sha256(blob), "CANONICAL"],
        )
        self.assert_basis_passes(output)

    def test_legacy_png_blob_fallback_matches_r0_checker(self):
        png_path = self.repo_root / PNG_REL
        original = png_path.read_bytes()
        blob = git_blob(self.head, PNG_REL, self.repo_root)
        self.assertEqual(original, blob)
        candidate_checker = self.check.read_bytes()
        baseline_checker = subprocess.run(
            ["git", "show", f"{R0_HEAD}:tools/governance/check.ps1"],
            cwd=self.repo_root,
            check=True,
            capture_output=True,
        ).stdout
        png_path.write_bytes(original + b"\x00WORKTREE-ONLY")
        try:
            row = ["EV1", "AC2 legacy PNG blob", PNG_REL, self.head, sha256(blob), "CANONICAL"]
            candidate_output = self.run_fixture(LEGACY_HEADER, row)
            self.assert_basis_passes(candidate_output)
            self.check.write_bytes(baseline_checker)
            baseline_output = self.run_fixture(LEGACY_HEADER, row)
            self.assert_basis_passes(baseline_output)
        finally:
            self.check.write_bytes(candidate_checker)
            png_path.write_bytes(original)

    def test_new_blob_basis_hashes_exact_png_blob_bytes(self):
        blob = git_blob(self.head, PNG_REL, self.repo_root)
        self.assertTrue(blob.startswith(b"\x89PNG\r\n\x1a\n"))
        output = self.run_fixture(
            BASIS_HEADER,
            self.explicit_row(PNG_REL, sha256(blob), "BLOB", commit=self.head),
        )
        self.assert_basis_passes(output)

    def test_new_blob_basis_uses_commit_bytes_across_checkout_eol(self):
        blob = git_blob(self.head, PLAN_REL, self.repo_root)
        worktree = (self.repo_root / PLAN_REL).read_bytes()
        output = self.run_fixture(
            BASIS_HEADER,
            self.explicit_row(PLAN_REL, sha256(blob), "BLOB", commit=self.head),
        )
        self.assert_basis_passes(output)
        if blob != worktree:
            self.assertNotEqual(sha256(blob), sha256(worktree))

    def test_blob_commit_without_path_fails_even_if_worktree_path_is_missing(self):
        missing = self.repo_root / self.root.name / "absent.png"
        output = self.run_fixture(
            BASIS_HEADER,
            self.explicit_row(missing, "0" * 64, "BLOB", commit=self.head),
        )
        self.assert_basis_fails(output, "EVIDENCE_BASIS_BLOB_PATH_MISSING")

    def test_basis_is_required_and_case_sensitive(self):
        path = self.repo_root / PLAN_REL
        digest = sha256(git_blob(self.head, PLAN_REL, self.repo_root))
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
        path = self.repo_root / PLAN_REL
        header = BASIS_HEADER[:-1] + ["basis"]
        output = self.run_fixture(
            header,
            self.explicit_row(PLAN_REL, sha256(git_blob(self.head, PLAN_REL, self.repo_root)), "BLOB", commit=self.head),
        )
        self.assert_basis_fails(output, "EVIDENCE_BASIS_HEADER_INVALID")

    def test_new_basis_rows_reject_missing_or_extra_columns(self):
        row = self.explicit_row(PLAN_REL, sha256(git_blob(self.head, PLAN_REL, self.repo_root)), "BLOB", commit=self.head)
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
        digest = sha256(git_blob(self.head, PLAN_REL, self.repo_root))
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
        path = self.repo_root / PLAN_REL
        blob_sha = sha256(git_blob(self.head, PLAN_REL, self.repo_root))
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
        png = git_blob(self.head, PNG_REL, self.repo_root)
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
