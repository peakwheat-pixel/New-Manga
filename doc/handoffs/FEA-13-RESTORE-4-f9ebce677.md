---
task_id: FEA-13-RESTORE-4
author: DSH（Lead / Integrator）
recipient: 独立上下文 Reviewer
base_commit: 0dc4ff85f
delivery_head: f9ebce677
status: delivered
---

# Handoff：FEA-13-RESTORE-4（merge restore + staging/commit marker + L-5）

## 交付结果

按冲突模型裁决 `ADJ-2026-11-09-FEA13-RESTORE-MODEL` 实现 merge restore：只读预览、默认 `defer`（不整库覆盖）、`UseBackup` 前保全、staging+commit marker、L-5 独占维护窗口。实现提交 **`f9ebce677`**（base `0dc4ff85f`）。

| 变更 | 内容 |
|---|---|
| `src/application/maintenance/restore_plan.py`（新） | `plan_rows`/`plan_managed`/`plan_restore`（只读 ATTACH 对比 7 表 + managed 文件，逐项 add/noop/conflict/keep）；`apply_restore`（`BEGIN IMMEDIATE` 内逐项隔离；defer 只应用 add；UseBackup 先 `_preserve_row` 再覆盖；缺 undo 区该项 fail-closed） |
| `src/infrastructure/sqlite/nmbak.py` | `extract_for_plan`（校验+解压到临时目录，零写 live）、`cleanup_plan`、`plan_undo_root`、`plan_staging_root`、`plan_marker_path`、`connection` 属性 |
| `src/bootstrap/core_service.py` | `handle_backup_restore` 支持 `mode`（overwrite/defer/use_backup）+ `_merge_restore`（staging 复制+sha 校验、marker `staging`→`committed`、维护锁）；`_RESTORE_LOCK_EXEMPT` + dispatch 入口 `RESTORE_IN_PROGRESS` fail-closed；`RESTORE_PLAN_STALE` 映射 |
| `tests/storage/test_nmbak_merge_restore.py`（新） | 4 例：预览零写+分类、defer 不覆盖、UseBackup 保全、缺 undo 区 fail-closed |
| `tests/core/test_core_restore_plan.py`（新） | 5 例：defer wire+marker committed、overwrite 旧行为、非法 mode、L-5 fail-closed+备份豁免、apply 崩溃 → marker staging + live 不变 + 锁释放 |
| `verification/FEA-13-RESTORE-4/**` | README + 4 日志（命令头/EXIT） |

## 验证证据

| AC | 命令/步骤 | 结果 | 证据 |
|---|---|---|---|
| AC1–AC3, AC5–AC6 | `python -m pytest <备份/恢复面 9 文件> -q` | **91 passed / 0 failed**（EXIT 0） | `logs/pytest-restore-suite.log` |
| 变异① | defer 也应用冲突 → `pytest tests/storage/test_nmbak_merge_restore.py` | **1 failed / 3 passed**（EXIT 1）；复原后 8 passed | `logs/mutation-defer-overwrites.log` |
| 变异② | 关闭 L-5 窗口 → `pytest tests/core/test_core_restore_plan.py` | **1 failed / 3 passed**（EXIT 1） | `logs/mutation-no-lock.log` |
| AC6 | `dotnet build NewManga.sln -c Debug` | **0 warning / 0 error**（EXIT 0） | `logs/build.log` |
| AC6 | `check.ps1`（默认 + `-TaskPath`）、`verify_pins` | PASS（3 warnings）/ 18/18 | 卡/Handoff |

**AC4 标 PARTIAL**：`RESTORE_PLAN_STALE` 已注册并映射，但「预览→换包→应用」端到端用例未做（登记后续）。

## 接收方式

- 分支 `main`；base `0dc4ff85f` → 实现 `f9ebce677`。
- 复核：`git show --stat f9ebce677`；按 README 复跑与变异。
- 关键检查点：defer 是否真的不写 conflict/keep；UseBackup 是否先保全后覆盖；marker 崩溃时是否保持 `staging` 且 live 不变；L-5 是否只豁免备份命令。

## 下一任务建议

FEA-13 片 5 `FEA-13-SCHED-5`（调度/保留/失败语义，含 D4 两条）；片 6 数据根迁移单列。

## 风险与遗留

- managed 文件在 merge 应用中被列为 deferred（staging 复制语义后续切片）；`UseBackup` 对 managed 项亦然。
- 真实进程 kill 崩溃注入未做（用 monkeypatch 模拟 apply 崩溃）；登记部署态验证。
- wire 文档（V11R `backup.restore` 行）未同步 `mode/entries`。
- 前一片 `FEA-13-ID-3` 的 C# 解析测试、`SC-B01 ④`（`FEA-13-SRC-6`）仍为后续。
