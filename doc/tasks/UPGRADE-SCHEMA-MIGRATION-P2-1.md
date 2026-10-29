---
id: UPGRADE-SCHEMA-MIGRATION-P2-1
title: 合成旧 schema 迁移测试的 4×P2 补齐（NULL 列、额外行、结构全量、冻结 v1 列）
kind: chore
governance_version: 3
status: ready
approval: user_authorized_2026-10-29_p2_closeout
suggested_owner: dsh
owner: dsh-lead
reviewer: region-workbench-owner
depends_on: [UPGRADE-SCHEMA-MIGRATION-1]
base_commit: 7598e1c40
branch: task/UPGRADE-SCHEMA-MIGRATION-P2-1
worktree: G:/CODEX/New Manga.workspace/worktrees/UPGRADE-SCHEMA-MIGRATION-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/UPGRADE-SCHEMA-MIGRATION-P2-1
allowed_paths:
  - doc/tasks/UPGRADE-SCHEMA-MIGRATION-P2-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - tests/storage/test_upgrade_schema_data.py
  - verification/UPGRADE-SCHEMA-MIGRATION-P2-1/**
  - G:/CODEX/New Manga.workspace/worktrees/UPGRADE-SCHEMA-MIGRATION-1/**
  - G:/CODEX/New Manga.workspace/task-envs/UPGRADE-SCHEMA-MIGRATION-P2-1/**
---

# UPGRADE-SCHEMA-MIGRATION-P2-1：合成旧 schema 迁移测试 4×P2 补齐

## 来源

`UPGRADE-SCHEMA-MIGRATION-1` round 3 复审 PASS 时记录的 4 个非阻塞 P2（
`doc/reviews/UPGRADE-SCHEMA-MIGRATION-1.md` Round 3 Findings）：
1. `region_revisions.source_run_id` 等 NULL 列未纳入 EXPECTED（只断言写入的列）。
2. 未检测升级后**额外行**（表里多出的行可通过）。
3. `_assert_latest` 结构检查非全量（只查部分表/列）。
4. 旧库仍由生产 `MIGRATIONS` 合成（无冻结 v1 列/结构对照；`FROZEN_V1_TABLES` 仅表集合）。

用户 2026-10-29 指定补齐。

## Acceptance Criteria

- [ ] **AC1 全列 EXPECTED**：每个 seed 行用 `SELECT *` 记录**整行**（含 NULL/默认值列），升级后逐列断言。
- [ ] **AC2 额外行检测**：每个 seed 表断言升级后行数 == EXPECTED 记录数（多出行即失败；复合键 `book_tags` 单独断言）。
- [ ] **AC3 结构检查全量**：对全部 `LATEST_TABLES` 断言主键列存在（`PRAGMA table_info`），关键索引/外键检查保留。
- [ ] **AC4 冻结 v1 列**：`FROZEN_V1_COLUMNS`（books/chapters/pages 的 v1 列集合）断言，防迁移定义改 v1 DDL。
- [ ] **AC5 回归与证据**：单测 11 passed；全量 pytest 无新增失败；check PASS；证据日志带命令头。

## 禁止范围

不改 `src/**` 产品代码、迁移 SQL、既有历史测试；不 push main。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Closeout Record

- 待实施后填写。
