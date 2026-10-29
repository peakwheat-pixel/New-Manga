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
integration_commit: 3f32bb503
delivery_head: 3710e001474407919fb4ec8cf971f945095736ed
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

# UPGRADE-SCHEMA-MIGRATION-1：合成旧 schema 数据迁移测试（in_review / round 2）

## 来源

`UPGRADE-REHEARSAL-1` 的剩余限制：「真实旧 schema（v1–v5）数据不可得 → schema 迁移链未用真实数据验证」。
用户 2026-10-29 指定「合成旧 schema 迁移测试」。

## 实现（round 2，已集成 main `3f32bb503`，代码 `3710e0014`）

新增 `tests/storage/test_upgrade_schema_data.py`（不修改产品代码）：
- **逐版本合成**：用 `default_migrations()` 逐条应用迁移，并在**每一代**seed 该版本的数据——
  v1：books/chapters/pages/media_artifacts/artifact_revisions；v2：books/chapters/pages 新列 + tags/book_tags + regions/region_revisions；
  v3：pipeline_runs/pipeline_run_targets/pipeline_tasks；v4：reading_progress/export_history；v5：book_cleanup_manifests。
- **v5 重建数据存活**：v3 seed 的 pipeline_run_targets/pipeline_tasks（v5 用 `INSERT ... SELECT` + `DROP TABLE` 重建）在升级后逐列断言。
- **全字段/关系断言**：books/chapters/pages/media_artifacts/artifact_revisions/tags/book_tags/regions/region_revisions/
  pipeline_* /reading_progress/export_history/book_cleanup_manifests 的完整列值与关联；`PRAGMA foreign_key_check` 为空。
- **结构演进**：v1 起点缺后续表（14 张清单全查）；升级后全部存在；integrity ok；升级后可写；逐版本幂等。

## 验证（round 2）

- 单测：**11 passed**（5 个参数化旧版本 + v1 演进 + 5 个参数化幂等；`unit-tests.log` 带 COMMAND/CWD/PYTHON/AT 头）。
- 全量回归：**2623 passed / 10 skipped / 0 failed**（190.2s；`pytest-full.log` 带命令头 + `pytest-full-summary.txt`）。

## Acceptance Criteria

- [x] **AC1 合成旧库**：v1–v5 逐版本建库并 seed 各代数据（含 v2 列扩展、v3 pipeline、v4 阅读/导出、v5 manifest）。<<MET>>
- [x] **AC2 迁移完整性**：schema_version=最新；全字段值与关系不变（含 v5 重建表数据）；integrity ok；外键检查空；升级后可写。<<MET>>
- [x] **AC3 结构演进**：v2 regions/region_revisions、v3 pipeline_*、v4 reading_progress/export_history、v5 book_cleanup_manifests、v6 plugin_state/plugin_events 均存在且旧数据未被改写。<<MET>>
- [x] **AC4 回归**：单测 11 passed；全量 2623 passed / 0 failed；check PASS。<<MET>>
- [x] **AC5 证据**：日志带命令头与 64-hex pin；未改产品代码。<<MET>>

## 禁止范围（已遵守）

未改 `src/**` 产品代码；未改既有迁移 SQL/历史测试字节；未 push main。

## 交付与运行记录

- worktree：`G:/CODEX/New Manga.workspace/worktrees/UPGRADE-SCHEMA-MIGRATION-1`，HEAD `3710e0014`（round 1 `fd925fcf7` → round 2）。
- 集成：main `3f32bb503`（含 round 1 review 文档 + round 2 测试）。
- 证据：`verification/UPGRADE-SCHEMA-MIGRATION-1/{unit-tests.log,pytest-full.log,pytest-full-summary.txt}`。

## Review

- 实施与自查：DSH（Lead）。
- 独立审查 round 1（region-workbench-owner，reviewed_head `fd925fcf7`）：**FAIL**（2×P1 + 6×P2：只 seed v1-era 表、v5 重建在空表上执行、断言不足、日志头缺失）。
- **round 2 返修**：逐项处理——按版本 seed（v2/v3/v4/v5 数据，v5 重建表有数据）；全字段/关系断言 + `PRAGMA foreign_key_check`；
  防假阳性 14 张表清单；幂等逐版本参数化；日志头修正（COMMAND/CWD/PYTHON/AT + EXIT）。
- 复审：**待 region-workbench-owner 再审 `3f32bb503`**。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| unit-tests | AC1/AC2/AC3 | verification/UPGRADE-SCHEMA-MIGRATION-1/unit-tests.log | 3710e0014 | c7ccbbdb9d589d4ebdb0540fb813af04dd25785f2813ed602e256b03879902fd | CANONICAL |
| pytest-full-log | AC4 | verification/UPGRADE-SCHEMA-MIGRATION-1/pytest-full.log | 3710e0014 | d493abc87842b650f230ac3748e61b31b1bbc253ce7e37824d45077202f9633a | CANONICAL |
| pytest-full-summary | AC4 | verification/UPGRADE-SCHEMA-MIGRATION-1/pytest-full-summary.txt | 3710e0014 | e03113ad46963113b4660ec2e37f94821c2e44df3300bd0d640353233cb226c7 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/UPGRADE-SCHEMA-MIGRATION-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/UPGRADE-SCHEMA-MIGRATION-1 | 提交 3710e0014 | 测试实现（round 2） |
| task-env | G:/CODEX/New Manga.workspace/task-envs/UPGRADE-SCHEMA-MIGRATION-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/UPGRADE-SCHEMA-MIGRATION-1 | pytest-full.log | 回归日志 |

## Closeout Record

- 待 round 2 复审 PASS 后填写（target: done）。
