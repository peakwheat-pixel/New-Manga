---
task_id: SETTINGS-OPEN-C-2-BACKUP
kind: implementation
status: ready
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

- [ ] **AC1 包格式**：生成包含 manifest/db/sidecar/managed，`verified=true`；损坏包被 `BACKUP_CORRUPT` 拒绝；排除项（缓存/日志/trash）不进包。
- [ ] **AC2 恢复**：覆盖 + pre_restore 自动备份；running Run → `BACKUP_RESTORE_BUSY`；consistency 报告。
- [ ] **AC3 列表/删除**：真实文件；`BACKUP_NOT_FOUND` 幂等；备份根固定 `<data_root>/backups/`。
- [ ] **AC4 前端**：面板真实操作（非假控件）；恢复二次确认；错误映射；无 `auto_backup` 控件；分类 open。
- [ ] **AC5 证据**：固定 commit、原始日志、独立 Review（非实现者）、GUI 烟测（建库 → 备份 → 改数据 → 恢复 → 数据回到备份点）。

## 测试要求

| 场景/AC | 计划命令 | 实际结果 | 证据 |
|---|---|---|---|
| AC1-AC3 | `python -m pytest tests/core tests/application -q` | 待填 | 待填 |
| AC2 | `cargo test --locked -- --skip packaged_sidecar_tests --test-threads=1`（dev overlay） | 待填 | 待填 |
| AC4 | `npm --prefix apps/desktop/frontend test` + `tsc --noEmit` | 待填 | 待填 |
| 烟测 | dev preview：备份 → 改数据 → 恢复 | 待填 | 待填 |

## 交付与运行记录

- 2026-10-23：C-1 关闭后释放；等待启动。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
|EV-C2-WIRE|AC1-AC5|PENDING|PENDING|PENDING|CANONICAL|

## Closeout Record

- Closeout：待实现 + 独立 Review + GUI 烟测通过后关闭。
- canonical_evidence_status：pending；resource_closeout_status：pending。
- 删除/迁移/归档：0。
- 当前指针清理：STATUS/REBASELINE/LEDGER 登记本 Task。
