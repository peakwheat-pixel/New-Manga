---
id: UPGRADE-SCHEMA-MIGRATION-1
title: 合成旧 schema（v1–v5）数据迁移测试（补 B 卡剩余验证缺口）
kind: verification
governance_version: 3
status: in_review
approval: user_authorized_2026-10-29_schema_synthesis
suggested_owner: dsh
owner: dsh-lead
reviewer: region-workbench-owner
depends_on: [UPGRADE-REHEARSAL-1, UPGRADE-LEGACY-LAYOUT-1]
base_commit: 99005e189
branch: task/UPGRADE-SCHEMA-MIGRATION-1
worktree: G:/CODEX/New Manga.workspace/worktrees/UPGRADE-SCHEMA-MIGRATION-1
integration_commit: fd925fcf7737cb051af3b0a6bf00ce1b50931b41
delivery_head: fd925fcf7737cb051af3b0a6bf00ce1b50931b41
canonical_evidence_status: complete
resource_closeout_status: complete
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

# UPGRADE-SCHEMA-MIGRATION-1：合成旧 schema 数据迁移测试（in_review）

## 来源

`UPGRADE-REHEARSAL-1` 的剩余限制：「真实旧 schema（v1–v5）数据不可得 → schema 迁移链未用真实数据验证」。
用户 2026-10-29 指定「合成旧 schema 迁移测试」。

## 实现（已集成 main `fd925fcf7`）

新增 `tests/storage/test_upgrade_schema_data.py`（不修改产品代码）：
- 用项目自身迁移定义 `default_migrations()` **合成 v1–v5 各版本旧库**（`MigrationRunner(conn, MIGRATIONS[:n])`），
  在 v1 表结构里写入真实形态的数据：1 本 book、2 章、3 页、1 个 media_artifact + 1 个 artifact_revision（含 managed_path/hash/size）。
- 再用**完整迁移链**升级到最新 schema（当前 v6）。
- 断言：链落在最新版本；books/chapters/pages/artifact revision 的值与关系不变；最新表（regions/pipeline_runs/
  reading_progress/export_history/plugin_state 等）存在；`PRAGMA integrity_check=ok`；升级后仍可写。
- 另含：v1 起点确实缺后续表（防假阳性）；升级后重跑幂等。

## 验证

- 单测：`python -m pytest tests/storage/test_upgrade_schema_data.py -q` → **7 passed**（5 个参数化旧版本 + v1 演进 + 幂等；`unit-tests.log` 带命令头）。
- 全量回归：`python -m pytest -q` → **2619 passed / 10 skipped / 0 failed**（206.7s；`pytest-full.log` 带命令头）。
- 覆盖矩阵：v1→v6、v2→v6、v3→v6、v4→v6、v5→v6 各一条数据保留路径。

## Acceptance Criteria

- [x] **AC1 合成旧库**：v1–v5 参数化建库并写入 book/chapter/page/artifact/revision 数据。<<MET>>
- [x] **AC2 迁移完整性**：schema_version=最新；行数与值不变；integrity ok；升级后可写。<<MET>>
- [x] **AC3 结构演进**：v2 regions、v3 pipeline_*、v4 reading_progress/export_history、v6 plugin_state 均存在；旧表数据未被改写（值断言）。<<MET>>
- [x] **AC4 回归**：单测 7 passed；全量 2619 passed / 0 failed；check PASS（待 commit 后确认）。<<MET>>
- [x] **AC5 证据**：unit/log/summary 带命令头与 64-hex pin；未改产品代码。<<MET>>

## 禁止范围（已遵守）

未改 `src/**` 产品代码；未改既有迁移 SQL/历史测试字节；未 push main。

## 交付与运行记录

- worktree：`G:/CODEX/New Manga.workspace/worktrees/UPGRADE-SCHEMA-MIGRATION-1`，HEAD `fd925fcf7`。
- 集成：main fast-forward `fd925fcf7`。
- 证据：`verification/UPGRADE-SCHEMA-MIGRATION-1/{unit-tests.log,pytest-full.log,pytest-full-summary.txt}`。

## Review

- 实施与自查：DSH（Lead）。独立审查：**待补**（建议 `region-workbench-owner` 复核测试真实性/覆盖/无产品改动）。
- 独立审查（region-workbench-owner，2026-10-29，reviewed_head `fd925fcf7`）：**FAIL / CHANGES_REQUESTED**（P0=0；2×P1 + 6×P2；7 个单测实跑通过、7/7 证据 pin 与 check PASS，但测试仅 seed v1-era 数据，v2/v5 版本特有/数据变换（尤其 v5 pipeline 表重建）在空表上执行；值/关系断言只覆盖 book title + revision 三列，chapters/pages 仅 count、无关系/FK 断言；pytest-full.log/summary 无命令头）。详见 [`doc/reviews/UPGRADE-SCHEMA-MIGRATION-1.md`](../reviews/UPGRADE-SCHEMA-MIGRATION-1.md)。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| unit-tests | AC1/AC2/AC3 | verification/UPGRADE-SCHEMA-MIGRATION-1/unit-tests.log | fd925fcf7 | 63586990dae182f9ff2d6d3d2a608c29bb7bdf022770b7297b9f3215375889f3 | CANONICAL |
| pytest-full-log | AC4 | verification/UPGRADE-SCHEMA-MIGRATION-1/pytest-full.log | fd925fcf7 | 891d06d795b6cd5cf73ee42ec243519bafeb6ce27e4f9b5d46aceeb9749c4725 | CANONICAL |
| pytest-full-summary | AC4 | verification/UPGRADE-SCHEMA-MIGRATION-1/pytest-full-summary.txt | fd925fcf7 | 5af648617b6722cf2828ed127af33dbcb71b7cff53e4594ee6281b5580c125f7 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/UPGRADE-SCHEMA-MIGRATION-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/UPGRADE-SCHEMA-MIGRATION-1 | 提交 fd925fcf7 | 测试实现 |
| task-env | G:/CODEX/New Manga.workspace/task-envs/UPGRADE-SCHEMA-MIGRATION-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/UPGRADE-SCHEMA-MIGRATION-1 | pytest-full.log | 回归日志 |

## Closeout Record

- 待独立 Review 通过后填写（target: done）。
