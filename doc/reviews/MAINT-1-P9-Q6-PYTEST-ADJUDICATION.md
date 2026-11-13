# Q6 裁决：pytest 16 failed（MAINT-1 P9，2026-11-14）

## 1. 事实

- 验收运行（`FEA-15-ACCEPT-1`，clean-tree）：`16 failed, 3515 passed, 12 skipped`（`verification/FEA-15-ACCEPT-1/pytest-full-retry.log` 末行）。
- 失败簇集中在**单一子系统**：插件沙箱。合并去重后 12 个唯一用例名，全部命中 `tests/infrastructure/test_plugin_sandbox.py`。

## 2. 复跑取证（本轮新增，决定性）

```
python -m pytest -q tests/infrastructure/test_plugin_sandbox.py
→ 16 passed in 26.23s
```

该文件 `^def test_` 计数恰为 **16**，与验收 16 failed 数目**精确吻合**，且包含全部失败用例名（`test_sandbox_*`、`test_network_capability_*`、`test_interpreter_acl_*`、`test_production_assembly_*`、`test_hook_child_*`）。

## 3. 裁决

**归因：环境性失败，非产品缺陷。** 失败原因是 clean-tree 运行的 Python/ACL/AppContainer profile 环境不满足插件沙箱用例前提（与 `FEA-15-ACCEPT-1` 已登记的「系统 Python ACL、AppContainer profile 维持 `PRESERVE_UNKNOWN`」「专用 venv 插件对照 6 passed/10 failed」一致）；在真实仓库 + 本机 Python 下同文件 16/16 通过。

**处置：不新开修复卡；登记为已归因的环境基线，不再计入"未归因失败"。**

**限制（必须同时记录）**：
- 本轮只复跑了该文件，**未复跑全量 pytest**（验收运行 228.86 s）。全量复跑列入下一轮，用于把 `V1_COMMITMENT_MANIFEST` 的「16 failed」更新为本轮实测值。
- 复跑环境为系统 `python`（`pytest 9.1.1`），与验收运行的 `C:\Python314`（无 pytest 模块）不同；差异本身即环境性证据之一。

## 4. 对 DoD §4 的影响

- `.NET`：已在轮次 2 实测 **1875/0/109 `EXIT=0`**。
- `pytest`：16 failed 已归因且真实环境不复现。
- 余下仅需**全量复跑**给出与本轮同一环境的干净数字；在此之前，DoD §4 仍标「有条件达成」，不写成全绿。

## 5. 全量复跑（2026-11-14，轮次 14）

`python -m pytest -q` → **`1 failed, 3536 passed, 10 skipped`**（292.07 s，`EXIT=1`）。
日志：`verification/MAINT-1-RELEASE-MONITOR/logs/pytest-full-2026-11-14.log`。

与验收基线对比：`3515 passed / 16 failed / 12 skipped` → 现 `3536 passed / 1 failed / 10 skipped`。
**16 个沙箱失败未复现**（归因结论再次得到支持）。

**唯一失败未归因**：`test_real_v7_import_fixture_degrades_then_pixel_matches_on_generation_two`。其 `scratch_dir` 指向 `G:/CODEX/New Manga.workspace/FEA-11/fixtures/...`（workspace 真实 fixture），本次未逐行定位根因，**不得读作已归因**。DoD §4 因此仍不写全绿。
