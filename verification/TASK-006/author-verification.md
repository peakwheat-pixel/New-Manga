# TASK-006 作者验证记录

- 日期：2026-09-15（Asia/Shanghai）
- 作者：ZCode；被测 commit：`ba1e7695a1ad806a2640fe077811ade95d3b90d4`
- 环境：Windows 11 专业版 Build 26200 x64；Python 3.12.3（`G:/CODEX/New Manga.task-envs/TASK-005-py312`，TASK-005 建立的任务环境，pytest 9.1.1；本 Task 未新增任何依赖，全部使用 stdlib `sqlite3`）

## 实际执行命令与结果

| # | 命令（工作目录 = TASK-006 worktree 根） | 退出码 | 结果 |
|---|---|---|---|
| 1 | `python -m pytest tests/storage -v`（任务计划命令；`G:/CODEX/New Manga.task-envs/TASK-005-py312/Scripts/python.exe -m pytest tests/storage -v`） | 0 | **29 passed in 0.73s**（AC-ART/REV/DB + 失败矩阵 + Unicode + 迁移/备份） |
| 2 | `PYTHONPATH=src python -m pytest tests`（全量回归：TASK-005 core 守卫 + TASK-006 storage） | 0 | **35 passed in 1.30s**（core 6 + storage 29；架构守卫不被新代码破坏） |
| 3 | `git diff --check fb29dfe ba1e769 --`（实现范围 whitespace） | 0 | PASS |
| 4 | `git status --short`（变更范围核对） | 0 | 仅 `src/ports/**`、`src/infrastructure/**`、`tests/storage/**`（允许路径）；`src/domain`、`src/ui`、`src/bootstrap`、`tests/core` 零触碰 |

## 开发过程中发现并修复的问题（供 Review 参考）

1. `SchemaTooNewError` 定义于 `connection.py`，`migrator.py` 首版遗漏 import（运行时才会 NameError）——已修复，测试 `test_newer_schema_is_rejected_and_readonly` 覆盖该路径。
2. `_verify_checksum` 最初对未建表的 v0 库直接查询 `schema_migrations` 导致 OperationalError——已改为表存在且有记录时才对比 checksum（`test_checksum_mismatch_detects_edited_history` 验证篡改检测仍然有效）。
3. 首次 v0→v1 迁移前的 pre-migration 备份无法写 `backup_records`（表由 v1 创建）——实现为「表存在才写记录，备份文件始终产出」，并以 `test_pre_migration_backup_created_before_first_ddl` + `test_post_schema_backup_is_recorded` 固化两种场景语义。

## NOT_RUN / N/A

| 项 | 状态 | 理由 |
|---|---|---|
| WAL 多连接并发/busy_timeout 实际竞争 | NOT_RUN | 本切片单连接测试；真实并发属 Pipeline 执行切片（TASK-011）与集成验证 |
| v1→v2 升级链与迁移失败恢复端到端 | NOT_RUN | 当前仅 v1；迁移端到端由 TASK-021 补足（Task 文件已声明） |
| Restore / 回收 / 清理对 current/pinned 的保护执行 | N/A | 清理器与恢复流程属 TASK-021；本切片提供 pinned 字段、完整性字段与备份入口 |
| 大数据量 / 性能 | N/A | 无性能 AC；D07 数值留 Benchmark |
| Region/Constraint Revision、StepResultCandidate 持久化 | N/A（范围决策） | 本切片无使用方：Region 属 TASK-008，PipelineRun/StepRun 属 TASK-011；表结构契约已在 TASK-002 冻结待后续切片实现 |

## 修订轮（R-101～R-106，reviewed_head `e1d3e2c`）

按 DeepSeek Review（`047d8c3`，changes_requested）修订后在最终 head 复跑：

| # | 命令 | 退出码 | 结果 |
|---|---|---|---|
| 5 | `python -m pytest tests/storage`（3.12 任务环境；head `e1d3e2c`） | 0 | **31 passed**（新增 R-101 路径布局、R-106 清空/首版 NULL 双向等 3 项，移除 1 项被 R-102 取代的枚举覆盖测试） |
| 6 | `PYTHONPATH=src python -m pytest tests` | 0 | **37 passed**（core 6 + storage 31） |
| 7 | `git diff --check fb29dfe e1d3e2c --` | 0 | PASS |
| 8 | `git diff --name-only fb29dfe HEAD` 越界过滤（D03/D08/AGENTS/STATUS/其他 Task/TASK-005 代码/domain/ui/bootstrap/tests/core/requirements） | — | 0 命中 |

v1 DDL 变更说明：新增 `trg_media_artifacts_current_not_clearable` 触发器（R-106），`schema_migrations.checksum` 与代码内 `default_migrations()[0].checksum` 一致更新；被拒 head `ba1e769` 从未集成主线，无已应用迁移的 checksum 漂移。
