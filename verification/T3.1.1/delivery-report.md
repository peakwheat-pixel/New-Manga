# T3.1.1 Delivery Report — SQLite Reading Progress & Export History Persistence

**Date:** 2026-09-22 (Asia/Shanghai)  
**Agent:** Antigravity (Implementation Agent)  
**Task ID:** T3.1.1  
**Base Commit:** `e771179`  
**Branch:** `agent/antigravity/T3.1.1-storage-sqlite`  
**Worktree:** `G:/CODEX/New Manga.worktrees/T3.1.1-antigravity-storage-sqlite`  
**Python Environment:** `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312` (Python 3.12.3)

---

## 1. 目标与实现概述

本任务消除了 `reading_progress.json` 与 `export_history.json` 两个旧生产文件写入点，将阅读进度与导出历史完全接入集中式 SQLite 数据库（Schema Version 4），作为生产唯一的写入真相源；原有遗留 JSON 文件仅在初次启动时执行一次性只读安全导入，导入状态通过 `application_metadata` 标记持久化记录，损坏或结构非法的遗留数据提供明确诊断并严格保护原始文件不被覆写或删除。

### 核心变更列表

- **`src/infrastructure/sqlite/schema.py`**:
  - 增加 `SCHEMA_VERSION_V4 = 4` 与 `MIGRATION_V4_NAME = "v4__reading_export_storage"`。
  - 新增 `reading_progress` 表（含 `UNIQUE(book_id, chapter_id, mode)` 约束、外键关联、级联删除与 `idx_reading_progress_book` 索引）。
  - 新增 `export_history` 表（含状态 `CHECK` 约束、`idx_export_history_created_at`、`idx_export_history_book` 索引）。
  - 严格保持 v1/v2/v3 Migration SQL 字符完全未变，确保历史 SHA-256 校验和完全匹配。
- **`src/infrastructure/sqlite/reading_export.py`** (新建):
  - 实现 `SqliteReadingProgressStore`（满足 `ProgressDocumentStore` 协议）。
  - 实现 `SqliteExportHistoryStore`（满足 `HistoryDocumentStore` 协议）。
  - 提供命名对齐别名 `SqliteProgressDocumentStore` 与 `SqliteHistoryDocumentStore`。
  - 实现 `import_legacy_reading_progress` 与 `import_legacy_export_history`：支持只读解析、原子导入、持久化标记、空/缺失跳过与损坏/非法诊断。
  - 定义类型化诊断异常：`LegacyImportError`、`LegacyCorruptJsonError`、`LegacyInvalidStructureError`、`LegacyInvalidRecordError`。
- **`src/infrastructure/sqlite/__init__.py`**:
  - 导出上述 Adapter 与导入工具。
- **`src/bootstrap/app.py`**:
  - `assemble_services` 在连接数据库并执行 migration 之后，先执行一次性 legacy 数据导入（带持久化 marker 检查）。
  - 注入 `SqliteReadingProgressStore(conn)` 与 `SqliteExportHistoryStore(conn)` 到 `ReadingService` 与 `ExportService`，切断对 JSON 文件写入路径的依赖。
- **`tests/core/test_bootstrap.py`**:
  - 对齐 diagnostics 中的 `schema_version` 断言至 4。
- **`tests/storage/test_backup_restore.py`**:
  - 对齐活动数据库 `schema_version` 断言至 4。
- **`tests/storage/test_schema_migration.py`**:
  - 对齐 `LATEST_KNOWN = 4`、应用迁移版本列表 `[1, 2, 3, 4]`、新版本拒绝测试（针对 v5）及 pre-migration 备份记录断言。
- **`tests/reading_export/test_sqlite_reading_export.py`** (新建):
  - 20 项自动化测试，全面覆盖 AC1～AC6。
- **`verification/T3.1.1/run_probes.py`** (新建):
  - 4 个综合场景黑盒 Probe：覆盖遗留导入与幂等性、损坏诊断与文件防篡改、生产装配零 JSON 写入、事务回滚一致性。

---

## 2. 验收标准（Acceptance Criteria）逐项对照

| AC 编号与名称 | 验收要求 | 实际实现与验证事实 | 状态 |
|---|---|---|---|
| **AC1: SQLite Schema & Migration** | 新增 `reading_progress` 与 `export_history` 表；schema 版本升至 4；索引完整；历史 v1/v2/v3 migration hash 不变；支持向前迁移 | `schema.py` 增设 v4 migration；创建两表及所需索引和约束；`tests/storage/test_schema_migration.py` 与 Probe 1 全绿 | **PASS** |
| **AC2: 读写完整性与并发安全** | 完整支持进度字段 round-trip（含 offset、reading_time 等）；支持 original/translated 独立进度；导出历史完整字段与倒序排序；共享连接事务隔离 | `reading_export.py` 严格实现两协议；`(book_id, chapter_id, mode)` 唯一约束与 upsert 语义；导出历史支持按时间倒序与状态过滤；测试覆盖多 mode 独立存储与重启恢复 | **PASS** |
| **AC3: 遗留 JSON 安全导入与幂等性** | 首次启动自动安全导入；导入后持久化标记；后续启动不重复导入；缺失时记录 marker 不报错；原始 JSON 严格保持只读，不修改、不删除 | `import_legacy_*` 实现原子导入并向 `application_metadata` 写入标记；Probe 1 与自动化测试校验导入后文件 hash 及 mtime 严格不变；重复调用立即 no-op 返回 True | **PASS** |
| **AC4: 损坏/非法输入诊断与数据保护** | JSON 语法损坏、根结构非 list/dict、必要字段非法时抛出明确类型化异常；绝不破坏已有数据库；绝不删除或改写损坏的原始文件 | 实现 `LegacyCorruptJsonError`、`LegacyInvalidStructureError`、`LegacyInvalidRecordError`；Probe 2 注入格式错误，校验异常准确抛出且源文件与 DB 完整未损 | **PASS** |
| **AC5: 生产装配与零 JSON 写入** | `src/bootstrap/app.py` 注入 SQLite Adapter；业务层接口契约完全兼容；生产运行零 JSON 写入 | `assemble_services` 组装 `SqliteReadingProgressStore` 与 `SqliteExportHistoryStore`；Probe 3 与自动化测试跟踪文件系统，确认无任何 `.json` 进度/历史文件创建或写入 | **PASS** |
| **AC6: 故障与回滚保护** | 导入过程中若发生 DB 故障或异常，事务自动回滚；数据库状态保持干净，不留下半吊子数据与 marker | 导入逻辑置于短事务内（或 savepoint/rollback）；Probe 4 注入触发器回滚故障，确认回滚后数据库表空且 marker 未写，原文件无损 | **PASS** |

---

## 3. 验证结果汇总

| 验证项 | 测试命令 / 脚本 | 被测 Commit / 环境 | 结果 | 日志路径 |
|---|---|---|---|---|
| **AC 综合 Probes** | `python verification/T3.1.1/run_probes.py` | `agent/antigravity/T3.1.1-storage-sqlite` / Py3.12.3 | **PASS** (4/4 场景全部通过) | `verification/T3.1.1/probes.log` |
| **针对性测试套件** | `pytest tests/reading_export tests/storage -q` | 同上 | **PASS** (220 passed in 26.09s) | `verification/T3.1.1/focused-reading-storage.log` |
| **Core 模块测试** | `pytest tests/core -q` | 同上 | **PASS** (49 passed in 6.56s) | `verification/T3.1.1/core.log` |
| **字节码编译** | `python -m compileall -q src tests` | 同上 | **PASS** (ExitCode: 0) | `verification/T3.1.1/compileall.log` |
| **Bootstrap 冒烟** | `python -m bootstrap.app --smoke-test --data-root <temp>` | 同上 | **PASS** (ExitCode: 0) | `verification/T3.1.1/smoke-test.log` |
| **全量回归测试** | `pytest tests -q -p no:cacheprovider -rs` | 同上 | **1229 passed, 6 skipped, 1 known failure** | `verification/T3.1.1/full-suite.log` |

> **说明（已知环境限制）：**
> 全量回归套件中唯一的 1 个失败用例为 `tests/providers/test_registry_readiness.py:193`（`AssertionError: PyTorch is not available: No module named 'torch'`），该项为当前开发虚拟环境中未安装 PyTorch 所致，属于既有已知环境限制（在 `doc/STATUS.md` 与基线日志中已有明确记载），不属于 T3.1.1 的代码缺陷或回退。
