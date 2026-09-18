---
task_id: TASK-053
author: ZCode
recipient: Codex
base_commit: 8bf8da3f988cdeffce83ad251a15c22ce862dd1a
delivery_head: f4aa66b
status: delivered
---

# Handoff：TASK-053 TASK-044 遗留收口（R-03 pipeline_runs 累积 / R-04 不可重试孤儿文件）

## 交付结果

- **R-04（孤儿文件 → 可重试）**：`src/application/maintenance/trash.py` 的 `purge_batch` 在**任何破坏性步骤之前**把文件清扫清单持久化进 manifest 的 `pending_purges` 段（`{batch_id, targets}`）；行删除与批次出账后逐文件删除，**全部成功才清除** pending 条目；任一文件失败即抛出（可诊断），条目保留 → 孤儿始终可发现。新增入口：
  - `retry_pending_purges() -> int`（清除的条目数）——文件删除幂等（`ManagedFileStorage.remove_managed` 对缺失文件静默跳过，已核），已消失的文件视为完成；
  - `pending_purge_count() -> int`（可诊断视图）。
  - manifest 写入沿用原子替换；旧 manifest（无 `pending_purges` 段）按 `get(..., [])` 兼容，无迁移。
- **R-03（无 target run 累积 → 保留 + 清理入口）**：**策略=明确保留**（TASK-044 裁决理由成立：run 跨页，级联删除会破坏其它页共享的审计；`purge_pages` 本就只删 `pipeline_run_targets/step_runs/pipeline_tasks` 的相关行而保留 run 行——修前探针证实），**不传播删除**。新增端口 `RunLedgerMaintenance`（`src/application/maintenance/ports.py`）与实现 `SqliteRunLedgerMaintenance`（`src/infrastructure/sqlite/pipeline.py`）：
  - `count_targetless_runs()`：`pipeline_runs` 中 `NOT EXISTS (pipeline_run_targets)` 的行数；
  - `purge_targetless_runs() -> int`：删除无 target 且 **status NOT IN ('running','paused')** 的 run（活动 run 即便无 target 也保留——启动恢复路径可能仍引用，TASK-048）；FK 全链 `ON DELETE CASCADE`（tasks/step_runs/step_result_candidates），`PRAGMA foreign_keys=ON` 保持开启。
- **AC ④（TRIGGER 纪律）**：`sqlite_master` 的 trigger 集在修前树与本切片全部操作前后枚举一致＝`{trg_media_artifacts_current_not_clearable, trg_regions_current_not_clearable}`（`schema.py:136,271`，均只护 current 指针列，与 run/manifest 清理面无交集）→ 清理语句不被触发器拒绝；证据＝探针输出 + `TestTriggerDiscipline` 用例（操作前后集合相等）。
- **白名单核对**：改动仅 `src/application/maintenance/{ports,trash}.py`、`src/infrastructure/sqlite/pipeline.py`（追加类）、`tests/storage/{conftest,test_run_files_leak}.py`、Task/Handoff/verification——全部在 Task 允许范围；零 Schema/migration、零依赖、零 `AGENTS.md`/其他 Task/QML、无放宽断言、无新增 skip。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC ① 修前取证 | `git archive c9e0675` 解 TEMP 树 → `python verification/TASK-053/r03_r04_probe.py <tree>` | 修前树（master c9e0675），Git-Bash + TASK-012-py312，PYTHONDONTWRITEBYTECODE=1、QT_QPA_PLATFORM 未设 | **PASS（REPRODUCED，EXIT=0）**：R-04 失败后 manifest 仅 `batches` 段、孤儿在盘、无持久化清单；R-03 run 行残留且 targets=0、无维护入口；TRIGGER 两条枚举在案 | `verification/TASK-053/prefix-probe.log` |
| AC ① 修后对照 | 同一探针指向本分支树 | 本分支 | **NOT REPRODUCED**（缺陷状态消除）：manifest 含 `pending_purges`、孤儿可发现；维护入口存在 | `verification/TASK-053/postfix-probe.log` |
| AC ② 删除失败→重试成功 | `pytest tests/storage/test_run_files_leak.py`（`FlakyRemover` 首删抛错→断言 pending 条目/目标清单/孤儿在盘→retry 成功清除） | 本分支 | **PASS**：7 例全过；**判别力声明**——`test_file_failure_leaves_retryable_pending_entry` 对修前树必失败（`pending_purge_count` 在修前不存在 ⇒ AttributeError；且修前 manifest 无该段），R-03 侧 `test_targetless_run_survives_page_purge_by_policy` 为**钉住既有行为**（声明不计判别力），其余新用例防回归 | `tests/storage/test_run_files_leak.py` |
| AC ③ 清理入口语义 | `test_purge_targetless_runs_reclaims_and_cascades`（存活 target 的 run 幸存）、`test_active_targetless_run_is_never_reclaimed`（running 保留、failed 回收） | 本分支 | **PASS** | 同上 |
| AC ④ TRIGGER 纪律 | `TestTriggerDiscipline`：操作前后枚举 `sqlite_master` trigger 集相等 | 本分支 | **PASS** | 同上 |
| AC ⑤ 全仓 ≥5 次 | `pytest -q -rs -p no:cacheprovider` ×5 | 本分支 | **PASS ×5：880 passed / 0 skipped，EXIT=0**（41.97–43.29s；=873 基线 + 7 新用例；无新增 skip/xfail、既有断言零改动——diff 删除行 0） | `verification/TASK-053/full-suite-run{1..5}.log` |
| 既有面无回归 | `pytest tests/storage tests/core` | 本分支 | PASS（72+ 新增面全绿，见全仓） | 会话记录 |

口径：同一 shell（Git Bash）+ 同一 venv（`TASK-012-py312`）+ `PYTHONDONTWRITEBYTECODE=1` + `-p no:cacheprovider`，`QT_QPA_PLATFORM` 未设；退出码 + passed/skipped 逐次分列。

## 接收方式

- 分支 `agent/zcode/TASK-053-run-files-leak`，worktree `G:/CODEX/New Manga.worktrees/TASK-053-zcode`。
- 复现：`pytest tests/storage/test_run_files_leak.py -q -p no:cacheprovider`；探针：`python verification/TASK-053/r03_r04_probe.py <tree>`。
- 前置：master 已含 TASK-046/048/054/055（开工 merge master `c9e0675`）。

## 风险与遗留

- **R-03 的清理入口是显式操作**：不自动执行；生产接线（谁调用 `purge_targetless_runs`——设置页/维护命令）属后续装配/UI 面，本切片交付端口与实现。
- **pending_purges 清单在 manifest 内**：manifest 损坏退化重建的既有语义（F-7）不覆盖 pending 段——极端情况下 pending 条目丢失退回 R-04 修前形态（孤儿不可发现）；概率与影响与既有 F-7 面一致，未扩大。
- **单文件删除部分成功**：条目内多文件时第 N 个失败会留下前 N-1 个已删（重试幂等，无危害）。
- **回退**：`git revert <实现提交>` 即可（语义追加、无既有行为改变）。
