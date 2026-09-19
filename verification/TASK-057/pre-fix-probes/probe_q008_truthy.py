"""Q-008 前置② 判别探针：恒真断言 ``... or True`` 对真实回归零判别力。

场景：模拟「实现回归 —— 备份实现把 user-side 产物写进了 managed root」
（AC③ 安全边界的突破形态），然后直接调用真实测试
``TestBackupCompleteness.test_backup_does_not_touch_user_source``：

- 修前形态（断言 ``assert not (managed_root / "user-side").exists() or True``）：
  模拟回归发生，测试仍 PASS ⇒ 恒真断言抓不住真实回归；
- 修后形态（去掉 ``or True`` 的真实边界断言）：同一场景 FAIL ⇒ 判别力成立。

判别力 = 同一探针在修前/修后两树上 EXIT 翻转，两份日志并排即证：
- 修后树：断言抓到模拟回归 ⇒ DISCRIMINATING-FAIL 分支 ⇒ 探针 PASS，EXIT=0；
- 修前树（``or True`` 仍在）：回归溜过断言 ⇒ TRUTHY-PASS 分支 ⇒
  探针 FAIL，EXIT=1（review R-006：结论必须进 EXIT，恒真尾巴已删）。
其他异常照常抛出（EXIT≠0）。
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT / "tests" / "storage"))

import pytest  # noqa: E402

from test_backup_restore import backup_workspace  # noqa: E402,F401  (fixture)


def test_truthy_assertion_cannot_catch_simulated_regression(
    backup_workspace,
) -> None:
    # the real test class is imported *inside* the test body so pytest
    # cannot collect its (passing) members alongside this probe
    from test_backup_restore import TestBackupCompleteness

    # 模拟回归：备份实现把 user-side 目录写进了 managed root（AC③ 突破）
    simulated = backup_workspace["managed_root"] / "user-side"
    simulated.mkdir(parents=True, exist_ok=True)
    assert simulated.exists(), "probe setup: simulated regression not in place"

    caught = False
    try:
        TestBackupCompleteness().test_backup_does_not_touch_user_source(
            backup_workspace
        )
    except AssertionError as error:
        caught = True
        print(f"DISCRIMINATING-FAIL: assertion caught the simulated "
              f"regression ({error}) => discriminating power confirmed")
    else:
        print("TRUTHY-PASS: assertion passed despite the simulated "
              "regression => the `or True` truthy tail gives AC③ zero "
              "discriminating power (pre-fix shape)")
    assert caught, (
        "no discriminating power: the AC③ assertion passed despite the "
        "simulated regression (truthy-tail shape — pre-fix defect)")
