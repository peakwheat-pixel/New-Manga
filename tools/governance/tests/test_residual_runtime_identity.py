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
        # Ruling C（2026-11-16）：原先断言 `self.index.errors == []` —— 那是把「全仓零错误」
        # 当成 residual 层的不变量。真实仓库当前另有 154 条与 residual 层**无关**的历史声明债务
        # （Ruling B 的 B1/B2/B3 范围），它们**不应**阻塞本层，也**不应**被本层吞掉。
        # 改为断言本层真正保证的事：7 条裁定身份已全部降级、且不再以 error 形式出现。
        policy = json.loads((REPO / POLICY_REL).read_text(encoding="utf-8"))
        adjudicated = [e for b in policy["bindings"] for e in b["errors"]]
        for e in adjudicated:
            self.assertNotIn(e, self.index.errors,
                             "an adjudicated error identity is still fatal")
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
        # Ruling C（2026-11-16）：原先断言 `len(before.errors) == 7`（全仓恰好 7 条错误）——
        # 那是把「仓库长得刚好」当成不变量，仓库一增长就误报（实测已 161 条）。
        # 改为**成员不变量**：7 条被裁定的错误身份必须都存在于 pre-stage 索引中。
        policy = json.loads((REPO / POLICY_REL).read_text(encoding="utf-8"))
        adjudicated = [e for b in policy["bindings"] for e in b["errors"]]
        self.assertEqual(len(adjudicated), 7,
                         "the frozen policy must declare exactly seven error identities")
        for e in adjudicated:
            self.assertIn(e, before.errors,
                          "adjudicated error identity missing from the pre-stage index")
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
        # Ruling D（2026-11-16）：带行级身份的绑定以**行**为权威。原用例在文件**末尾**追加一个换行，
        # 那不会改变被绑定的行 —— 按新语义**本就不该**报漂移（改前它报的其实是整文件 sha 差异，
        # 属过宽绑定）。现在改为**改动被绑定的那一行**，这才是「origin 字节漂移」该测的东西。
        path = self.fixture.root / "doc/tasks/P19.md"
        bound = next(b["origin_line"] for b in self.fixture.data["bindings"]
                     if b["origin_file"] == "doc/tasks/P19.md")
        lines = path.read_bytes().splitlines(keepends=True)
        target = lines[bound - 1]
        eol = b"\r\n" if target.endswith(b"\r\n") else b"\n"
        lines[bound - 1] = target.rstrip(b"\r\n") + b" trailing-drift" + eol
        path.write_bytes(b"".join(lines))
        index, _ = self.fixture.scan()
        # Ruling C：不再断言「全仓恰好 8 条」这种绝对计数 —— 改动被绑定行本身会连带改变
        # 该行的声明语义（错误条目可能增减），拿总数当断言会把两种效应混在一起。
        # 断言真实意图：必须 fail-closed 到 SOURCE_DRIFT，且**没有任何身份被降级**。
        codes = [e["code"] for e in index.errors]
        self.assertIn("SOURCE_DRIFT", codes,
                      "changing the bound line must fail closed with SOURCE_DRIFT")
        self.assertEqual(len(residual_warnings(index)), 0,
                         "no identity may be downgraded while the origin has drifted")

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
        # Ruling C（2026-11-16）**行为变更**：与 residual 层无关的错误**不再阻塞**本层。
        # 原断言是「7 + 1 新 DECL_ENV + ERROR_MISMATCH = 9」——那正是绝对计数耦合的产物。
        # 新语义：7 条裁定身份照常被移除，EXTRA.md 引入的 DECL_ENV 原样留下继续报错（不静默吞掉），
        # 且不产生 ERROR_MISMATCH。
        codes = [e["code"] for e in index.errors]
        self.assertNotIn("ERROR_MISMATCH", codes,
                         "an unrelated error must not block the residual layer")
        self.assertEqual(len(residual_warnings(index)), 7,
                         "the seven adjudicated identities must still be resolved")
        self.assertEqual(codes, ["DECL_ENV"],
                         "the unrelated error must survive untouched (not swallowed)")

    def test_protection_set_regression_fails_closed(self):
        """AC6 第 7 类负例：**保护集合回退**必须 fail-closed（`PROTECTION_REGRESSION`）。

        该类此前只有正面断言（`ProductionScan.test_protection_set_did_not_shrink`），
        没有负例 —— 也就是说「守卫真的会拦」从未被证明过。本用例补上。

        注入的范围必须**严格限制在解释层内部**：`_register_protective` 也被更早的
        声明扫描阶段调用，若在全局范围内丢根，会先把 pre-stage 索引本身弄坏
        （实测 residual 阶段拿到的 protected 由 37 变 36，被丢的根根本不在里面，
        守卫自然不触发 —— 那样测的就是错的东西）。所以用一个 active 开关，
        只在 `_apply_residual_runtime_identity` 执行期间丢根，且丢的是**该函数自己
        收到的 pre-stage 保护集合**里的根。

        触发的是 `clean_workspace.py` 的两条 `PROTECTION_REGRESSION` 守卫
        （`all(root in staged.protected ...)` 与 `len(staged.protected) >= len(index.protected)`），
        不是绕开守卫去断言别的代码。
        """
        original_register = guard.ProtectionIndex._register_protective
        real_stage = guard._apply_residual_runtime_identity
        state = {"active": False, "dropped": None, "pops": 0}

        def regressing_register(index_self, declaration):
            original_register(index_self, declaration)
            if state["active"] and state["dropped"] is not None:
                if index_self.protected.pop(state["dropped"], None) is not None:
                    state["pops"] += 1

        def tracking_stage(index, scanned):
            # 进入解释层时，从它自己的 pre-stage 保护集合里挑一个根作为被丢掉的根
            state["dropped"] = sorted(index.protected)[0] if index.protected else None
            state["active"] = True
            try:
                return real_stage(index, scanned)
            finally:
                state["active"] = False

        with mock.patch.object(guard.ProtectionIndex, "_register_protective",
                               regressing_register), \
                mock.patch.object(guard, "_apply_residual_runtime_identity",
                                  tracking_stage):
            index, _ = self.fixture.scan()

        self.assertIsNotNone(state["dropped"],
                             "解释层的 pre-stage 保护集合不能为空，否则本负例无从退化")
        self.assertGreater(state["pops"], 0,
                           "退化注入必须真的生效过，否则本负例是空转")
        self.assertEqual(len(index.errors), 8)
        self.assertEqual(index.errors[-1]["code"], "PROTECTION_REGRESSION")

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
