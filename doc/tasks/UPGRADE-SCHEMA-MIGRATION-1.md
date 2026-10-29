---
id: UPGRADE-SCHEMA-MIGRATION-1
title: 合成旧 schema（v1–v5）数据迁移测试（补 B 卡剩余验证缺口）
kind: verification
governance_version: 3
status: ready
approval: user_authorized_2026-10-29_schema_synthesis
suggested_owner: dsh
owner: dsh-lead
reviewer: region-workbench-owner
depends_on: [UPGRADE-REHEARSAL-1, UPGRADE-LEGACY-LAYOUT-1]
base_commit: 99005e189
branch: task/UPGRADE-SCHEMA-MIGRATION-1
worktree: G:/CODEX/New Manga.workspace/worktrees/UPGRADE-SCHEMA-MIGRATION-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/UPGRADE-SCHEMA-MIGRATION-1
allowed_paths:
  - doc/tasks/UPGRADE-SCHEMA-MIGRATION-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - tests/storage/test_upgrade_schema_data.py
  - verification/UPGRADE-SCHEMA-MIGRATION-1/**
  - G:/CODEX/New Manga.workspace/task-envs/UPGRADE-SCHEMA-MIGRATION-1/**
  - G:/CODEX/New Manga.workspace/worktrees/UPGRADE-SCHEMA-MIGRATION-1/**
---

# UPGRADE-SCHEMA-MIGRATION-1：合成旧 schema 数据迁移测试

## 来源

`UPGRADE-REHEARSAL-1` 的剩余限制：「真实旧 schema（v1–v5）数据不可得 → schema 迁移链未用真实数据验证」。
用户 2026-10-29 指定「合成旧 schema 迁移测试」。

## 目标

用项目自身迁移定义（`src/infrastructure/sqlite/schema.py` 的 `default_migrations()`）**合成** v1–v5 各版本的旧库
（含 books/chapters/pages 等真实数据行），再用完整迁移器升级到 v6，断言数据与结构完整。

## Acceptance Criteria

- [ ] **AC1 合成旧库**：对 v1–v5 每个版本参数化：用 `default_migrations()[:n]` 建库并写入合成数据（book/chapter/page/artifact 等）。
- [ ] **AC2 迁移完整性**：完整 `default_migrations()` 迁移后 schema_version=6；books/chapters/pages 行数与标题不变；`PRAGMA integrity_check=ok`；迁移后仍可写（新增 book 成功）。
- [ ] **AC3 结构演进**：断言后续版本新增对象存在（如 v2 `regions`、v3 `pipeline_runs`、v4 `reading_progress`、v6 `plugin_state`），且旧表数据未被改写。
- [ ] **AC4 回归**：`pytest tests/storage/test_upgrade_schema_data.py` 全绿；全量 pytest 无新增失败；`check.ps1` PASS。
- [ ] **AC5 证据**：测试日志、卡与 64-hex pin；不修改产品代码。

## 禁止范围

不改 `src/**` 产品代码；不改既有迁移 SQL/历史测试字节；不 push main。

## 交付与运行记录

- 待实施。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/UPGRADE-SCHEMA-MIGRATION-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/UPGRADE-SCHEMA-MIGRATION-1 | verification/UPGRADE-SCHEMA-MIGRATION-1/** | 待创建 |

## Closeout Record

- 待实施后填写。
