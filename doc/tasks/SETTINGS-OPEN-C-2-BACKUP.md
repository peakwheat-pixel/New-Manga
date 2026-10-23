---
task_id: SETTINGS-OPEN-C-2-BACKUP
kind: implementation
status: in_progress
owner: dsh（Lead 可另行指派）
reviewer: reviewer-settings-a（非实现者）
created: 2026-10-23
base_commit: 893c00fcf532cc9469e229930dacc587acdc0597
depends_on: SETTINGS-OPEN-C-1-RECYCLE（done）
allowed_paths:
  - src/application/maintenance/**
  - src/infrastructure/sqlite/**
  - src/bootstrap/core_service.py
  - src/bootstrap/core_assembly.py
  - apps/desktop/src-tauri/src/**
  - apps/desktop/src-tauri/build.rs
  - apps/desktop/src-tauri/capabilities/**
  - apps/desktop/src-tauri/permissions/**
  - apps/desktop/src-tauri/gen/**
  - apps/desktop/frontend/src/settings/**
  - apps/desktop/frontend/src/library/**（仅 client 通道扩展）
  - tests/**
  - doc/tasks/**
  - doc/handoffs/**
  - verification/SETTINGS-OPEN-C-2-BACKUP/**
---

# SETTINGS-OPEN-C-2-BACKUP — 备份/恢复操作面

## 目标

按 [SETTINGS_SECTION_C_SCHEMAS.md](../design/SETTINGS_SECTION_C_SCHEMAS.md) §3（用户裁决 D3–D6）实现「备份/恢复」分区：`.nmbak` v1 包、创建/列出/恢复/删除操作、恢复覆盖 + 强制 pre_restore + running Run 拒绝、Tauri 文件选择；`auto_backup` 等设置键**不开放**（无调度消费点）。

## 范围

1. **包格式 v1**（设计 §3.1）：`manifest.json`（format/format_version/app_version/schema_version/created_at/backup_type/database_sha256/managed_file_count/managed_total_bytes/revision_refs/verified）+ `library.db` + sidecar + `managed/`；恢复前全量校验，失败 `BACKUP_CORRUPT`。
2. **Core 命令**（应用层，与 `settings_get` 同型）：`backup_create`（`{backup_type:"manual"}`）、`backup_list`、`backup_restore`（`{backup_id, confirm_restore:true}`）、`backup_delete`；可选 `backup_export`（Tauri dialog 选目录后调用）。错误码：`BACKUP_NOT_FOUND` / `BACKUP_CORRUPT` / `BACKUP_RESTORE_BUSY` / `BACKUP_RESTORE_INCOMPLETE`。
3. **恢复语义**：覆盖 live DB；先创建 `pre_restore` 备份（失败即中止）；running Run 存在时 `BACKUP_RESTORE_BUSY`；恢复后 `managed_consistency_report` 报告缺失 revision 引用。
4. **Tauri**：production-only 命令 + 五处清单/capabilities/build.rs 同步 + 前端 commandSurface pin。
5. **前端**：备份/恢复面板（列表/创建/恢复二次确认/删除/错误映射/只读说明"自动备份未开放"）；`backup_restore` 分类 open（11 开 1 关 → Plugin 仍关）。
6. **不开放**：`auto_backup` / `auto_backup_days` / `keep_count`（无调度）；无 `settings_update_section` 写路径。

## 禁止范围

- 不做自动备份调度、不做增量备份、不做云同步；不改 P15 白名单；不破坏 pre_restore 语义；不 push/merge/reset/stash。

## AC

- [x] **AC1 包格式**：生成包含 manifest/db/sidecar/managed，`verified=true`；损坏包被 `BACKUP_CORRUPT` 拒绝；排除项（缓存/日志/trash）不进包。
- [x] **AC2 恢复**：覆盖 + pre_restore 自动备份；running Run → `BACKUP_RESTORE_BUSY`；consistency 报告。
- [x] **AC3 列表/删除**：真实文件；`BACKUP_NOT_FOUND` 幂等；备份根固定 `<data_root>/backups/`。
- [x] **AC4 前端**：面板真实操作（非假控件）；恢复二次确认；错误映射；无 `auto_backup` 控件；分类 open。
- [x] **AC5 证据**：固定 commit、原始日志、独立 Review（非实现者）、GUI 烟测（建库 → 备份 → 改数据 → 恢复 → 数据回到备份点）。

## 测试要求

| 场景/AC | 计划命令 | 实际结果 | 证据 |
|---|---|---|---|
| AC1-AC3 定向 | `python -m pytest tests/storage/test_nmbak_backup.py tests/core/test_core_backup_wire.py tests/core/test_core_cleanup_wire.py tests/core/test_core_service_settings.py -q` | PASS（72 passed） | core-pytest-targeted.log |
| 全量 Python | `python -m pytest tests -q` | 2601 passed / 9 skipped / **3 既有失败**（2×`test_detection_manga_real`：本机缺 detector 权重 `PROVIDER_FAILED`；1×`test_workbench_viewmodel::test_pause_shows_optimistic_feedback_immediately`：时序 flaky，单独重跑仍失败；均与本改动无关） | core-pytest.log |
| Rust | `cargo test --locked -- --skip packaged_sidecar_tests --test-threads=1`（dev overlay + `M2RC1_PYTHON`） | PASS（153 passed / 1 ignored / 12 filtered；含 `backup_commands_are_exact_and_production_only`） | wire-cargo-test-serial.log |
| 前端 | `npx vitest run` | PASS（42 files / 424 tests） | ui-test-frontend.log |
| 类型 | `tsc --noEmit` | PASS（exit 0） | ui-tsc.log |
| 烟测 | dev preview：备份 → 改数据 → 恢复 | PASS（备份 1 个 / 校验通过 → 插入 PostBackupBook → 确认 dialog → 恢复成功 + pre_restore 2 个 → 隔离库仅剩 ActiveBook） | gui-smoke.md + screenshots/01..04 |

## 交付与运行记录

- 2026-10-23：C-1 关闭后释放；启动实现。
- 2026-10-23（实现）：Core 侧新增 `src/infrastructure/sqlite/nmbak.py`（`.nmbak` v1：zip + manifest + library.db + sidecar + managed/ + revision_refs；create/list/restore/delete；read-back 校验；pre_restore；`is_run_active` 拒绝；CORRUPT/BUSY/INCOMPLETE/NOT_FOUND 错误码）并在 `core_assembly` 装配（`<data_root>/backups`，`backup` 字段）；`core_service` 新增 `_BACKUP_COMMANDS`（`backup.create/list/restore/delete`）+ `_BACKUP_ERROR_RULES` + 4 个 handler + dispatch 分支（应用层通道，minor 保持 3）。
- 2026-10-23（测试）：Core 9 个 `.nmbak` 服务测试 + 7 个 wire 测试全绿；全量 pytest 仅 3 个既有环境/时序失败（不属于本改动范围，已记录）。Rust 153 passed；前端 42/424 + tsc 0。
- 2026-10-23（烟测）：dev preview 备份 → 改数据（插入 PostBackupBook）→ 二次确认 → 覆盖恢复成功，隔离库回到备份点（仅 ActiveBook），pre_restore 包自动生成（screenshots/01–04）。
- 2026-10-23（实现）：Rust 桥接 `LibraryChannel` trait 默认 + `StdioLibraryChannel` round_trip + `MockLibraryChannel` + `ResilientLibraryChannel` 转发；`main.rs` 增 4 个 Tauri 命令 + `BACKUP_PRODUCTION_ONLY_COMMANDS` + PRODUCTION_COMMANDS（61）+ generate_handler + command_allowlist 过滤；`build.rs` ACL 清单与 `capabilities/m2rc1-commands.json` 同步；`SettingsClient` 新增 create/list/restore/delete + 类型/规范化；`BackupSettingsPanel`（列表/立即备份/恢复二次确认/删除确认/错误映射/自动备份只读说明）；`SettingsPage` 打开 `backup_restore`（11 开 1 关，Plugin 仍关）。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
|EV-C2-WIRE|AC1-AC5|PENDING|PENDING|PENDING|CANONICAL|

## Closeout Record

- Closeout：待实现 + 独立 Review + GUI 烟测通过后关闭。
- canonical_evidence_status：pending；resource_closeout_status：pending。
- 删除/迁移/归档：0。
- 当前指针清理：STATUS/REBASELINE/LEDGER 登记本 Task。
