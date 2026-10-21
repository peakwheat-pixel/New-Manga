"""P09-MANAGED-READ-ROOT-TRUST-1 / AC3：逐处测试的判别力（base vs 当前）。

AC3 要求 8 处**逐个**有测试，且不接受「模式相同所以一起算」。仅仅"当前测试全绿"
不能证明测试有判别力——必须证明**每处测试在修复前会失败**。

本脚本（R-002 修订后）：
  1. ``git archive <base_commit> src`` 把 base 源码解到
     ``G:/CODEX/New Manga.workspace/temp/P09-MANAGED-READ-ROOT-TRUST-1/``（R-004：不用系统 %TEMP%），
     不 checkout、不改仓库；
  2. 把 ``tests/security/test_p09_managed_read_root_trust.py`` 复制进临时树，配一个把
     ``sys.path`` 指向 base src 的 conftest，在**同一个测试文件**上跑 base；
  3. 在 worktree 上跑同一测试文件（当前实现）；
  4. 门槛（R-002 修订）：
     - **pytest 退出码**：base 必须非 0、current 必须为 0；
     - 每条列出的测试必须出现在**实际的 PASSED/FAILED 集合**中（用 ``-v`` 解析），
       "未出现在失败集合"不再直接判 PASS；
     - 8 处 site 测试：base=FAILED 且 current=PASSED；AC2 对照：两边都 PASSED；
     - R-001/R-002 补充测试：current 必须 PASSED（base 结果记录，不参与判别力判定）。

exit 0 = 每处都有判别力且当前全绿。

运行：``C:/Python314/python.exe verification/P09-MANAGED-READ-ROOT-TRUST-1/ac3-discrimination.py``
"""

from __future__ import annotations

import io
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

BASE_COMMIT = "b8a1e519703f13af73b320dded117004b4bb189a"
REPO = Path(__file__).resolve().parents[2]
TEST_REL = Path("tests/security/test_p09_managed_read_root_trust.py")
SCRATCH_ROOT = Path("G:/CODEX/New Manga.workspace/temp/P09-MANAGED-READ-ROOT-TRUST-1")
CONFTEST = '''"""Point the copied suite at an explicit source tree."""
from pathlib import Path
import sys

SRC = Path(r"{src}")
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
'''

SITE_TESTS = {
    "site1": "test_site1_read_original_page_reader_refuses_repointed_ancestor",
    "site2": "test_site2_resolve_page_resource_refuses_repointed_ancestor",
    "site3": "test_site3_checked_managed_path_refuses_repointed_ancestor",
    "site4": "test_site4_protected_export_target_uses_frozen_managed_baseline",
    "site5": "test_site5_image_state_refuses_repointed_ancestor",
    "site6": "test_site6_uri_within_refuses_repointed_ancestor",
    "site7": "test_site7_page_image_source_decodes_verified_handle_bytes",
    "site8": "test_site8_resolve_namespace_identity_refuses_swap_between_walk_and_open",
}
#: AC2 controls: legal usage must work BOTH before and after the fix.
AC2_CONTROLS = ("test_ancestor_junction_is_allowed_for_legal_reads",)
#: R-001/R-002 review additions: current implementation must pass them.
REVIEW_ADDITIONS = (
    "test_directory_substitution_is_refused_by_the_opened_handle",
    "test_site3_export_hash_refuses_repointed_ancestor",
    "test_site3_lazy_export_provider_refuses_repointed_ancestor",
)
_TEST_LINE = re.compile(r"^tests[/\\]\S+::(\w+)\s+(PASSED|FAILED|ERROR|SKIPPED)")


def extract_base_src(destination: Path) -> Path:
    archive = subprocess.run(
        ["git", "-C", str(REPO), "archive", "--format=tar", BASE_COMMIT, "src"],
        check=True,
        capture_output=True,
    ).stdout
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(destination)
    return destination / "src"


def run_pytest(target: Path, cwd: Path) -> tuple[int, str, dict[str, str]]:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            str(target),
            "-v",
            "--tb=no",
            "-p",
            "no:cacheprovider",
        ],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=900,
    )
    output = completed.stdout + completed.stderr
    outcomes: dict[str, str] = {}
    for line in output.splitlines():
        match = _TEST_LINE.match(line.strip())
        if match:
            outcomes[match.group(1)] = match.group(2)
    return completed.returncode, output, outcomes


def prepare_base_tree(workdir: Path, base_src: Path) -> Path:
    suite_dir = workdir / "tests" / "security"
    suite_dir.mkdir(parents=True)
    shutil.copy2(REPO / TEST_REL, suite_dir / TEST_REL.name)
    (suite_dir / "conftest.py").write_text(CONFTEST.format(src=base_src), encoding="utf-8")
    return suite_dir / TEST_REL.name


def main() -> int:
    SCRATCH_ROOT.mkdir(parents=True, exist_ok=True)
    run_root = Path(tempfile.mkdtemp(prefix="ac3-", dir=str(SCRATCH_ROOT)))
    try:
        base_src = extract_base_src(run_root / "base")
        base_test = prepare_base_tree(run_root, base_src)
        base_code, base_output, base_outcomes = run_pytest(base_test, run_root)
    finally:
        shutil.rmtree(run_root, ignore_errors=True)

    current_code, current_output, current_outcomes = run_pytest(REPO / TEST_REL, REPO)

    print("P09-MANAGED-READ-ROOT-TRUST-1 / AC3 — per-site discrimination")
    print(f"base_commit  = {BASE_COMMIT}")
    print(f"scratch_root = {SCRATCH_ROOT}")
    print(f"base pytest exit={base_code}  current pytest exit={current_code}")
    print(f"base outcomes:    {len(base_outcomes)} tests observed")
    print(f"current outcomes: {len(current_outcomes)} tests observed")
    print()

    ok = True
    if base_code == 0:
        ok = False
        print("FAIL: base run exited 0 -- the base snapshot is not expected to pass the suite")
    if current_code != 0:
        ok = False
        print("FAIL: current run did not exit 0")
    expected_count = len(SITE_TESTS) + len(AC2_CONTROLS) + len(REVIEW_ADDITIONS)
    if len(current_outcomes) < expected_count:
        ok = False
        print("FAIL: current run did not report every expected test (parsed PASSED/FAILED lines)")

    def outcome(outcomes: dict[str, str], name: str) -> str:
        return outcomes.get(name, "MISSING")

    print(f"{'row':<6} {'test':<70} {'base':<10} {'current':<10} verdict")
    for row, test_name in SITE_TESTS.items():
        base_verdict = outcome(base_outcomes, test_name)
        current_verdict = outcome(current_outcomes, test_name)
        discriminating = base_verdict == "FAILED" and current_verdict == "PASSED"
        if not discriminating:
            ok = False
        print(
            f"{row:<6} {test_name:<70} {base_verdict:<10} {current_verdict:<10}"
            f" {'OK' if discriminating else 'NOT DISCRIMINATING'}"
        )
    print()
    for test_name in AC2_CONTROLS:
        base_verdict = outcome(base_outcomes, test_name)
        current_verdict = outcome(current_outcomes, test_name)
        control_ok = base_verdict == "PASSED" and current_verdict == "PASSED"
        if not control_ok:
            ok = False
        print(
            f"AC2    {test_name:<70} {base_verdict:<10} {current_verdict:<10}"
            f" {'OK' if control_ok else 'REGRESSION'}"
        )
    print()
    for test_name in REVIEW_ADDITIONS:
        base_verdict = outcome(base_outcomes, test_name)
        current_verdict = outcome(current_outcomes, test_name)
        addition_ok = current_verdict == "PASSED"
        if not addition_ok:
            ok = False
        print(
            f"R-001/2 {test_name:<69} {base_verdict:<10} {current_verdict:<10}"
            f" {'OK' if addition_ok else 'CURRENT FAILED'}"
        )
    print()
    if not ok:
        print("base output tail:")
        print("\n".join(base_output.splitlines()[-40:]))
        print("current output tail:")
        print("\n".join(current_output.splitlines()[-40:]))
    print("RESULT =", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
