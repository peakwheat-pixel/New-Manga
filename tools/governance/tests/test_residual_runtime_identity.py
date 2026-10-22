"""Residual runtime identity: exact bindings and fail-closed negatives.

The stage must turn exactly the seven adjudicated declaration errors into
auditable warnings while (a) never expanding an environment token or wildcard,
(b) keeping every pre-existing protected root, and (c) refusing any drift.
"""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import clean_workspace as guard

REPO = Path(__file__).resolve().parents[3]
POLICY_REL = "tools/governance/residual-runtime-identity.json"
MATRIX_REL = "verification/GOV-RESIDUAL-RUNTIME-IDENTITY-1/matrix.md"
ORIGINS = (
    "doc/tasks/P19.md",
    "verification/ENV-BUNDLE-1-FU1/resource-manifest.json",
    "verification/P19-UI-FIX-1/resource-manifest.json",
)
RESIDUAL_WARNING = "DECL_RESIDUAL_RUNTIME_PRESERVED"
APPDATA_ROOT = "C:/Users/49745/AppData/Roaming/com.newmanga.m2rc1.desktop"
WORKSPACE_ROOT = "G:/CODEX/New Manga.workspace"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical_digest(obj):
    return sha(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":")).encode("utf-8"))


def norm(path):
    return guard.norm_abs(str(path), "fixture path")


def residual_warnings(index):
    return [w for w in index.warnings if w["code"] == RESIDUAL_WARNING]


class FixtureRepo(object):
    """A tiny tracked git repo carrying copies of the three real origins."""

    TARGETS = {
        "RRI-01": "worktrees/P19-AC3-1",
        "RRI-02": "temp/p19-ac2-r1",
        "RRI-03": "temp/p19-ac2-main-1",
    }
    APPDATA_TARGETS = ("appdata/catalog", "appdata/data", "appdata/derived")

    def __init__(self, tmp):
        self.root = Path(tmp) / "repo"
        self.ws = Path(tmp) / "ws"
        self.root.mkdir()
        self.ws.mkdir()
        for rel in ORIGINS:
            dst = self.root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO / rel, dst)
        for rel in self.APPDATA_TARGETS:
            (self.root / rel).mkdir(parents=True, exist_ok=True)
        # The UI-FIX manifest resolves these product paths against a repo top-level
        # entry; the fixture only needs the top-level name to exist.
        (self.root / "apps").mkdir(exist_ok=True)
        matrix = self.root / MATRIX_REL
        matrix.parent.mkdir(parents=True, exist_ok=True)
        matrix.write_text("# fixture matrix\n", encoding="utf-8")
        (self.root / "tools" / "governance").mkdir(parents=True, exist_ok=True)
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("-c", "user.email=t@example.invalid", "-c", "user.name=fixture",
                 "commit", "-q", "-m", "fixture base")
        self.evidence_commit = self.git("rev-parse", "HEAD").stdout.strip()
        self.data = self.build_policy(self.evidence_commit)
        self.digest = canonical_digest(self.data)
        self.write_policy(self.data)
        self.git("add", "-A")
        self.git("-c", "user.email=t@example.invalid", "-c", "user.name=fixture",
                 "commit", "-q", "-m", "fixture policy")

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], check=True,
                              capture_output=True, text=True, encoding="utf-8")

    def build_policy(self, evidence_commit):
        data = json.loads((REPO / POLICY_REL).read_text(encoding="utf-8"))
        data["approved_research"]["evidence_commit"] = evidence_commit
        data["approved_research"]["matrix_raw_sha256"] = sha(
            (self.root / MATRIX_REL).read_bytes())
        for b in data["bindings"]:
            raw = (self.root / b["origin_file"]).read_bytes()
            b["origin_raw_sha256"] = sha(raw)
            b["origin_byte_length"] = len(raw)
            if "origin_line" in b:
                lines = raw.splitlines(keepends=True)
                b["origin_line_raw_sha256"] = sha(lines[b["origin_line"] - 1])
            if b["kind"] == "ALREADY_ABSENT_PATH":
                rel = self.TARGETS[b["id"]]
                b["target_abs"] = str(self.root / rel)
                b["target_normalized"] = norm(self.root / rel)
            elif b["kind"] == "PRESERVE_ROOTS":
                for target, rel in zip(b["targets"], self.APPDATA_TARGETS):
                    target["abs"] = str(self.root / rel)
                    target["normalized"] = norm(self.root / rel)
        return data

    def write_policy(self, data):
        path = self.root / POLICY_REL
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")

    def scan(self, digest=None):
        with mock.patch.object(guard, "RESIDUAL_RUNTIME_IDENTITY_DIGEST",
                               self.digest if digest is None else digest):
            return guard.scan_repo_declarations(str(self.root), str(self.ws))


class ProductionScan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index, cls.scanned = guard.scan_repo_declarations(str(REPO), WORKSPACE_ROOT)

    def test_all_seven_errors_are_resolved(self):
        self.assertEqual(self.index.errors, [])
        self.assertEqual(len(residual_warnings(self.index)), 7)
        self.assertTrue(all(w["file"] in ORIGINS for w in residual_warnings(self.index)))

    def test_user_data_root_is_now_protected(self):
        for suffix in ("catalog", "data", "derived"):
            hits = self.index.evaluate(norm(APPDATA_ROOT + "/" + suffix))
            self.assertTrue(hits, "expected protection for %s" % suffix)

    def test_no_wildcard_or_temp_expansion(self):
        leaked = [root for root in self.index.protected
                  if "p19-ac2" in root or "/temp/.tmp" in root
                  or root.endswith("/.tmp")]
        self.assertEqual(leaked, [])

    def test_protection_set_did_not_shrink(self):
        with mock.patch.object(
                guard, "_apply_residual_runtime_identity",
                lambda index, scanned: guard._finish_declaration_scan(index, scanned)):
            before, _ = guard.scan_repo_declarations(str(REPO), WORKSPACE_ROOT)
        self.assertEqual(len(before.errors), 7)
        missing = [root for root in before.protected if root not in self.index.protected]
        self.assertEqual(missing, [])
        self.assertGreater(len(self.index.protected), len(before.protected))


class FixtureBehaviour(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="rri-")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.fixture = FixtureRepo(self.tmp)

    def test_fixture_baseline_is_the_seven_errors_without_the_stage(self):
        with mock.patch.object(
                guard, "_apply_residual_runtime_identity",
                lambda index, scanned: guard._finish_declaration_scan(index, scanned)):
            before, _ = guard.scan_repo_declarations(str(self.fixture.root),
                                                     str(self.fixture.ws))
        self.assertEqual(sorted(e["code"] for e in before.errors),
                         ["DECL_DESTINATION_UNRESOLVED", "DECL_ENV", "DECL_ENV",
                          "DECL_ENV", "DECL_ENV", "DECL_RELATIVE_AMBIGUOUS",
                          "DECL_UNKNOWN_DISPOSITION"])

    def test_fixture_resolves_to_zero_errors(self):
        index, _ = self.fixture.scan()
        self.assertEqual(index.errors, [])
        self.assertEqual(len(residual_warnings(index)), 7)

    def test_wrong_digest_fails_closed(self):
        index, _ = self.fixture.scan(digest="1" * 64)
        self.assertEqual(len(index.errors), 8)
        self.assertEqual(index.errors[-1]["code"], "POLICY_DIGEST_MISMATCH")

    def test_origin_drift_fails_closed(self):
        path = self.fixture.root / "doc/tasks/P19.md"
        path.write_bytes(path.read_bytes() + b"\n")
        index, _ = self.fixture.scan()
        self.assertEqual(len(index.errors), 8)
        self.assertEqual(index.errors[-1]["code"], "SOURCE_DRIFT")

    def test_present_absent_target_fails_closed(self):
        (self.fixture.root / "worktrees" / "P19-AC3-1").mkdir(parents=True)
        index, _ = self.fixture.scan()
        self.assertEqual(len(index.errors), 8)
        self.assertEqual(index.errors[-1]["code"], "RESIDUAL_TARGET_PRESENT")

    def test_missing_preserve_target_fails_closed(self):
        shutil.rmtree(self.fixture.root / "appdata/data")
        index, _ = self.fixture.scan()
        self.assertEqual(len(index.errors), 8)
        self.assertEqual(index.errors[-1]["code"], "RESIDUAL_TARGET_MISSING")

    def test_unbound_error_blocks_the_stage(self):
        extra = self.fixture.root / "doc/tasks/EXTRA.md"
        extra.write_text("## Resource Manifest\n\n"
                         "| resource_type | source_path | disposition | "
                         "destination_path | process_check |\n"
                         "|---|---|---|---|---|\n"
                         "| temp | %TEMP%/unrelated | DELETE_SAFE | - | x |\n",
                         encoding="utf-8")
        self.fixture.git("add", "-A")
        index, _ = self.fixture.scan()
        # seven adjudicated + one new DECL_ENV from EXTRA.md + ERROR_MISMATCH
        self.assertEqual(len(index.errors), 9)
        self.assertEqual(index.errors[-1]["code"], "ERROR_MISMATCH")

    def test_tampered_policy_body_fails_closed(self):
        data = json.loads((self.fixture.root / POLICY_REL).read_text(encoding="utf-8"))
        data["bindings"][0]["provenance"] += "!"
        self.fixture.write_policy(data)
        self.fixture.git("add", "-A")
        index, _ = self.fixture.scan()
        self.assertEqual(len(index.errors), 8)
        self.assertEqual(index.errors[-1]["code"], "POLICY_DIGEST_MISMATCH")


if __name__ == "__main__":
    unittest.main()
