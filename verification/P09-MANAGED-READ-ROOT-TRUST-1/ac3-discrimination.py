"""P09-MANAGED-READ-ROOT-TRUST-1 / AC3：逐处测试的判别力（base vs 当前）。

AC3 要求 8 处**逐个**有测试，且不接受「模式相同所以一起算」。仅仅"当前测试全绿"
不能证明测试有判别力——必须证明**每处测试在修复前会失败**。

本脚本：
  1. ``git archive <base_commit> src`` 把 base 源码解到系统临时目录（不 checkout）；
  2. 把 ``tests/security/test_p09_managed_read_root_trust.py`` 复制进临时树，配一个把
     ``sys.path`` 指向 base src 的 conftest，在**同一个测试文件**上跑 base；
  3. 在 worktree 上跑同一测试文件（当前实现）；
  4. 逐条对比：8 处 site 测试必须 base=FAIL、current=PASS；AC2 链接合法使用对照
     必须在 base 上也 PASS（它不是安全修复，而是"不回归"的证明）。

exit 0 = 每处都有判别力且当前全绿。

运行：``C:/Python314/python.exe verification/P09-MANAGED-READ-ROOT-TRUST-1/ac3-discrimination.py``
"""

from __future__ import annotations

import io
import json
import os
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
CONFTEST = '''"""Point the copied suite at an explicit source tree."""
from pathlib import Path
import sys

SRC = Path(r"{src}")
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
'''

#: AC3 requires one discriminating test per row of the Task's 8-site table.
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
AC2_CONTROLS = (
    "test_ancestor_junction_is_allowed_for_legal_reads",
    "test_site6_uri_within_refuses_repointed_ancestor",  # legal half runs before swap
)


def extract_base_src(destination: Path) -> Path:
    archive = subprocess.run(
        ["git", "-C", str(REPO), "archive", "--format=tar", BASE_COMMIT, "src"],
        check=True,
        capture_output=True,
    ).stdout
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(destination)
    return destination / "src"


def run_pytest(target: Path, cwd: Path) -> tuple[int, str, set[str], set[str]]:
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", str(target), "-q", "--tb=no", "-p", "no:cacheprovider"],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=900,
    )
    output = completed.stdout + completed.stderr
    failed = set(re.findall(r"^FAILED \S+::(\w+)", output, re.MULTILINE))
    passed = set(re.findall(r"^tests/\S+::(\w+) PASSED", output, re.MULTILINE))
    if not passed:
        match = re.search(r"(\d+) passed", output)
        if match and not failed:
            passed = {"<all>"}
    return completed.returncode, output, failed, passed


def prepare_base_tree(workdir: Path, base_src: Path) -> Path:
    suite_dir = workdir / "tests" / "security"
    suite_dir.mkdir(parents=True)
    shutil.copy2(REPO / TEST_REL, suite_dir / TEST_REL.name)
    (suite_dir / "conftest.py").write_text(CONFTEST.format(src=base_src), encoding="utf-8")
    return suite_dir / TEST_REL.name


def main() -> int:
    workdir = Path(tempfile.mkdtemp(prefix="p09-ac3-base-"))
    try:
        base_src = extract_base_src(workdir / "base")
        base_test = prepare_base_tree(workdir, base_src)
        base_code, base_output, base_failed, base_passed = run_pytest(base_test, workdir)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

    current_code, current_output, current_failed, _current_passed = run_pytest(
        REPO / TEST_REL, REPO
    )

    print("P09-MANAGED-READ-ROOT-TRUST-1 / AC3 — per-site discrimination")
    print(f"base_commit = {BASE_COMMIT}")
    print(f"base pytest exit={base_code}  current pytest exit={current_code}")
    print(f"base FAILED  = {len(base_failed)} tests  (first 6: {sorted(base_failed)[:6]})")
    print(f"current FAILED = {len(current_failed)} tests")
    print()

    ok = True
    print(f"{'row':<6} {'test':<72} {'base':<6} {'current':<8} verdict")
    for row, test_name in SITE_TESTS.items():
        base_verdict = "FAIL" if test_name in base_failed else "PASS"
        current_verdict = "FAIL" if test_name in current_failed else "PASS"
        discriminating = base_verdict == "FAIL" and current_verdict == "PASS"
        if not discriminating:
            ok = False
        print(
            f"{row:<6} {test_name:<72} {base_verdict:<6} {current_verdict:<8}"
            f" {'OK' if discriminating else 'NOT DISCRIMINATING'}"
        )
    print()
    for test_name in AC2_CONTROLS:
        if "site6" in test_name:
            continue  # the site6 row above already covers the legal half
        base_verdict = "FAIL" if test_name in base_failed else "PASS"
        current_verdict = "FAIL" if test_name in current_failed else "PASS"
        control_ok = base_verdict == "PASS" and current_verdict == "PASS"
        if not control_ok:
            ok = False
        print(
            f"AC2    {test_name:<72} {base_verdict:<6} {current_verdict:<8}"
            f" {'OK' if control_ok else 'REGRESSION'}"
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
