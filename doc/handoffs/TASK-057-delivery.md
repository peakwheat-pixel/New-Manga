---
task_id: TASK-057
author: ZCode
recipient: Codex
base_commit: 8bf8da3f988cdeffce83ad251a15c22ce862dd1a
delivery_head: c5515fb
status: delivered
---

# Handoff：TASK-057 备份与恢复（TASK-021 冻结子集③）

## 交付结果

- **备份完整性（AC ①）**：既有 `SqliteBackupService.create_backup`（SQLite backup API）补齐两件——**sidecar 自描述清单**（`<id>.db.manifest.json`：schema_version / database_hash / app_version / created_at；原子写；即使备份 DB 之后被恢复覆盖，清单仍在）与**完成校验**（`verify_backup_file`：`PRAGMA integrity_check` + schema_migrations 可读，typed 失败）。`backup_records` 落记录（既有）。
- **恢复语义（AC ②）**：`restore_backup(backup_id)` = **覆盖**（SQLite backup API 把备份页复制进活连接）。顺序：解析记录（typed）→ 校验文件（存在/完整性/**sidecar 与 recorded hash 双比对**）→ **自动 `pre_restore` 备份**（文件+sidecar 在覆盖后幸存 ⇒ 恢复本身可回滚）→ 执行恢复 → 返回报告（restored_from / pre_restore_backup_id / schema_version 对 / **managed_consistency**）。**一致性报告**：恢复后逐条 `artifact_revisions.managed_path` 对照 managed root 文件存在性（缺失只报告不修复；未配置 managed root 时如实 skipped）。**覆盖语义推论**：恢复后 `backup_records` 回到备份时点（请求的 id 可能不在其中）⇒ 恢复入口以 sidecar 为兜底权威（DB 行缺失时按文件+sidecar 校验继续；文件也缺失才 typed `BACKUP_UNKNOWN`）——两次连续恢复同一备份可用。
- **安全边界（AC ③）**：备份/恢复只写 `backup_root`（managed root 内 `backups/`）；校验先行，任何 typed 失败发生在**任何写之前**（活库不动）；不留半成品（sidecar/备份均原子写；恢复为 backup API 单步）。
- **typed 失败（AC ④）**：`BackupVerificationError(code, detail)`——`BACKUP_UNKNOWN` / `BACKUP_FILE_MISSING` / `INTEGRITY_FAILED`（含 "file is not a database"）/ `SCHEMA_UNREADABLE` / `SIDECAR_UNREADABLE` / `SIDECAR_MISMATCH` / `HASH_MISMATCH`；重复操作用例（连续两次备份记录独立、连续两次恢复一致成功）。
- **白名单核对**：`src/infrastructure/sqlite/backup.py`（扩展，Task 明列既有材料）、`src/application/maintenance/backup.py`（新，消费侧 Protocol `BackupLedger`）、`tests/storage/test_backup_restore.py`（新 8 例）；零 Schema/migration、零依赖、零 QML/AGENTS/其他 Task；无放宽断言、无新增 skip。
- **判别力（AC ⑤）声明**：restore/verify/sidecar 为**新增能力**（修前树无恢复入口——声明不适用）；8 例均为安全/一致性/typed 语义的回归钉住；覆盖语义用**可观测状态变化**断言（恢复后漂移回滚、指针-文件一致、字节内容匹配）。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC ① 完整性 | `test_backup_writes_record_sidecar_and_passes_readback` | 本分支，Git-Bash + TASK-012-py312，PYTHONDONTWRITEBYTECODE=1、QT_QPA_PLATFORM 未设 | **PASS**：文件+sidecar+记录三件齐；integrity/schema 回读通过 | `tests/storage/test_backup_restore.py` |
| AC ② 覆盖语义+一致性 | `test_restore_overwrites_to_backup_point_and_consistency_holds` | 同上 | **PASS**：备份后漂移（第二 revision）被回滚；恢复指针的 managed 文件存在且字节匹配；consistency checked=1 missing=0 | 同上 |
| AC ②/④ 可回滚+重复 | `test_restore_creates_reusable_pre_restore_backup`、`test_backup_is_repeatable_with_distinct_records` | 同上 | **PASS**：pre_restore 文件可验证；连续两次恢复同一备份成功；两次备份记录独立 | 同上 |
| AC ④ typed 失败 | `test_unknown_backup_id_is_typed`、`test_corrupt_backup_file_is_typed_and_leaves_db_intact`、`test_hash_mismatch_is_typed` | 同上 | **PASS**：BACKUP_UNKNOWN / INTEGRITY_FAILED / HASH_MISMATCH；校验先于写 ⇒ 活库不动（revision 计数不变） | 同上 |
| AC ③ 安全边界 | `test_backup_does_not_touch_user_source`（+ remover 既有越界拒绝复用） | 同上 | **PASS**：user source 逐字节幸存 | 同上 |
| AC ⑤ 全仓 ≥5 次 | `pytest -q -rs -p no:cacheprovider` ×7 | 本分支（= master 至少 `1d41e00` + 本切片） | **run1 912/0；run2 `1 failed, 911 passed`＝`test_start_export_completes_and_updates_history`（export 面既有时序 flaky——TASK-034 R-05 已定性同域根因，非本切片面）；run3 EXIT=127 进程中断（环境异常，证据不完整如实保留）；run6/run7 912/0**；有效绿 4 次 + flaky 1 + 环境异常 1；912 = 904 基线 + 8 新用例；无新增 skip/xfail | `verification/TASK-057/full-suite-run{1,2,3,6,7}.log` |
| 相邻面 | `pytest tests/storage tests/core` | 同上 | **PASS**：97 passed / 0 skipped | 会话记录 |

口径：同一 shell + 同一 venv + `PYTHONDONTWRITEBYTECODE=1` + `-p no:cacheprovider`，`QT_QPA_PLATFORM` 未设；退出码 + passed/skipped 逐次分列。

## 接收方式

- 分支 `agent/zcode/TASK-057-backup-restore`，worktree `G:/CODEX/New Manga.worktrees/TASK-057-zcode`。
- 复现：`pytest tests/storage/test_backup_restore.py -q -p no:cacheprovider`。
- 前置：master 已含 TASK-053/056（maintenance 域）与 W0–W4/W6–W9（开工 merge master `1d41e00`）。

## 风险与遗留

- **`pre_restore` 备份记录随覆盖消失**（覆盖语义推论，已声明）：回滚凭据=文件+sidecar；`backup_records` 审计链的恢复后连续性属产品取舍（后续切片可加 sidecar 扫描重建入口）。
- **一致性报告只读不修**：缺失文件列入报告；修复面（重导入/失效）属后续装配/产品切片。
- **生产接线 NOT_RUN**：bootstrap 未注入（同 TASK-055/056 口径，装配切片统一）。
- **回退**：`git revert <实现提交>`。
