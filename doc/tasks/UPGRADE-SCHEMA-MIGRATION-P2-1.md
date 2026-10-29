---
id: UPGRADE-SCHEMA-MIGRATION-P2-1
title: 合成旧 schema 迁移测试的 4×P2 补齐（NULL 列、额外行、结构全量、冻结 v1 列）
kind: chore
governance_version: 3
status: in_review
approval: user_authorized_2026-10-29_p2_closeout
suggested_owner: dsh
owner: dsh-lead
reviewer: region-workbench-owner
depends_on: [UPGRADE-SCHEMA-MIGRATION-1]
base_commit: 7598e1c40
branch: task/UPGRADE-SCHEMA-MIGRATION-P2-1
worktree: G:/CODEX/New Manga.workspace/worktrees/UPGRADE-SCHEMA-MIGRATION-1
integration_commit: d03f6e115264aa6196270ba76c15ab1b0de0d6ae
delivery_head: d03f6e115264aa6196270ba76c15ab1b0de0d6ae
canonical_evidence_status: complete
resource_closeout_status: complete
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

- [x] **AC1 全列 EXPECTED**：seed 后 `_record_full_rows` 用 `SELECT *` 记录整行（含 NULL/默认值列），升级后逐列断言。<<MET>>
- [x] **AC2 额外行检测**：`_assert_no_extra_rows` 断言每个 seed 表行数 == EXPECTED 记录数；`book_tags` 单独断言（v2+ 起点）。<<MET>>
- [x] **AC3 结构检查全量**：全部 14 张 `LATEST_TABLES` 断言有列且有主键；关键索引/外键检查保留。<<MET>>
- [x] **AC4 冻结 v1 列**：`FROZEN_V1_COLUMNS`（books/chapters/pages 的 v1 列集合）在 v1 建库后断言。<<MET>>
- [x] **AC5 回归与证据**：单测 11 passed；全量 2623 passed / 0 failed；check PASS；unit/full/summary 均带 5 行命令头。<<MET>>

## 禁止范围

不改 `src/**` 产品代码、迁移 SQL、既有历史测试；不 push main。

## 交付与验证

- 修改 `tests/storage/test_upgrade_schema_data.py`：`_record_full_rows`（全列 EXPECTED）、`_assert_no_extra_rows`（额外行检测）、
  `_assert_latest` 全表结构检查（14 表列+主键）、`FROZEN_V1_COLUMNS`（v1 列集合）。
- 单测 **11 passed**（`unit-tests.log` 带头）；全量 **2623 passed / 10 skipped / 0 failed**（`pytest-full.log` 带头）。
- 集成：main `d03f6e115`。证据：`verification/UPGRADE-SCHEMA-MIGRATION-P2-1/`。

## Review

- 实施与自查：DSH（Lead）。独立复核：**待补**（region-workbench-owner 轻量复核 4 项 P2 修复与无回归）。
- 独立复核（region-workbench-owner，reviewed_head `d03f6e115`）：**PASS**（P0=0，P1=0；11 passed、全列 EXPECTED 已覆盖 NULL/默认值、seed 表额外行可捕获、14 表结构检查、FROZEN_V1_COLUMNS 与实际 v1 列一致、3/3 pin/5 行头/check PASS、仅测试+证据；剩余 3×P2：未 seed 后续表额外行范围、book_tags 仅计数、更多 v1 表列冻结，均为可选增强）。详见 [`doc/reviews/UPGRADE-SCHEMA-MIGRATION-P2-1.md`](../reviews/UPGRADE-SCHEMA-MIGRATION-P2-1.md)。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| unit-tests | AC1–AC4 | verification/UPGRADE-SCHEMA-MIGRATION-P2-1/unit-tests.log | d03f6e115 | b54967fa956e9e032751ee6f567e197d1cfde53b31c9730d659e810baba35ec4 | CANONICAL |
| pytest-full-log | AC5 | verification/UPGRADE-SCHEMA-MIGRATION-P2-1/pytest-full.log | d03f6e115 | 38c33d2abad122effaf0760f20b9d99ec497d3e086b176afee9ae5c85426bb88 | CANONICAL |
| pytest-full-summary | AC5 | verification/UPGRADE-SCHEMA-MIGRATION-P2-1/pytest-full-summary.txt | d03f6e115 | 60661a57b177a5b4e622625a3ebe33cac8e8d0c44976727d832b2cfd6f11635a | CANONICAL |

## Closeout Record

- 待独立复核通过后填写（target: done）。
