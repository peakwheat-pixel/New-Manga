---
id: UPGRADE-SCHEMA-MIGRATION-1
title: 合成旧 schema（v1–v5）数据迁移测试（补 B 卡剩余验证缺口）
kind: verification
governance_version: 3
status: done
approval: user_authorized_2026-10-29_schema_synthesis
suggested_owner: dsh
owner: dsh-lead
reviewer: region-workbench-owner
depends_on: [UPGRADE-REHEARSAL-1, UPGRADE-LEGACY-LAYOUT-1]
base_commit: 99005e189
branch: task/UPGRADE-SCHEMA-MIGRATION-1
worktree: G:/CODEX/New Manga.workspace/worktrees/UPGRADE-SCHEMA-MIGRATION-1
integration_commit: 61601dc8c
delivery_head: 43a76b2044847bfe3bcea23905b9830dfdc97bbe
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

# UPGRADE-SCHEMA-MIGRATION-1：合成旧 schema 数据迁移测试（in_review / round 3）

## 来源

`UPGRADE-REHEARSAL-1` 的剩余限制：「真实旧 schema（v1–v5）数据不可得 → schema 迁移链未用真实数据验证」。
用户 2026-10-29 指定「合成旧 schema 迁移测试」。

## 实现（round 3，已集成 main `61601dc8c`，代码 `43a76b204`）

`tests/storage/test_upgrade_schema_data.py`（不改产品代码）：
- **逐版本合成**：`default_migrations()` 逐条应用并逐代 seed：
  v1（books/chapters/pages/media_artifacts/artifact_revisions）；v2（books/chapters/pages 全部新列 + tags/book_tags + regions/region_revisions 含 JSON 列）；
  v3（pipeline_runs/pipeline_run_targets/pipeline_tasks + **step_runs/step_result_candidates**）；v4（reading_progress/export_history）；v5（book_cleanup_manifests）。
- **v5 四张重建表全覆盖**：`pipeline_run_targets`/`pipeline_tasks`/`step_runs`/`step_result_candidates` 都在 v5 前 seed，升级后逐列断言（空表重建无法通过）。
- **全列断言**：`EXPECTED` 记录每个 seed 行所有写入列，升级后逐列比较（含 JSON 字符串、时间、NULL、`step_run_ids_json` 关系）。
- **结构检查**：最新 schema 关键列（books/chapters/pages/regions/step_runs/pipeline_tasks/plugin_state）、索引（`idx_chapters_book_id`、`idx_step_runs_run`）、外键（chapters→books）；`PRAGMA integrity_check` + `foreign_key_check`。
- **防回归**：`FROZEN_V1_TABLES` 固定 v1 表集合；版本连续性守卫；14 张后续表存在性；逐版本幂等。

## 验证（round 3）

- 单测：**11 passed**（5 参数化旧版本 + v1 演进 + 5 参数化幂等；`unit-tests.log` 带 5 行命令头）。
- 全量回归：**2623 passed / 10 skipped / 0 failed**（190.2s；`pytest-full.log` 带命令头；`pytest-full-summary.txt` 含命令头与 RESULT/EXIT）。

## Acceptance Criteria

- [x] **AC1 合成旧库**：v1–v5 逐版本建库并 seed 各代数据（含 v2 列扩展、v3 pipeline + step 表、v4 阅读/导出、v5 manifest）。<<MET>>
- [x] **AC2 迁移完整性**：schema_version=最新；全部 seed 行全列值不变（含 v5 四张重建表、JSON 列、NULL、关系）；integrity ok；FK 空；升级后可写。<<MET>>
- [x] **AC3 结构演进**：v2 regions/region_revisions、v3 pipeline_* 与 step_*、v4 reading_progress/export_history、v5 book_cleanup_manifests、v6 plugin_state/plugin_events 均存在；关键列/索引/外键已断言。<<MET>>
- [x] **AC4 回归**：单测 11 passed；全量 2623 passed / 0 failed；check PASS。<<MET>>
- [x] **AC5 证据**：unit/full/summary 均带命令头与 64-hex pin；未改产品代码。<<MET>>

## 禁止范围（已遵守）

未改 `src/**` 产品代码；未改既有迁移 SQL/历史测试字节；未 push main。

## 交付与运行记录

- worktree：`G:/CODEX/New Manga.workspace/worktrees/UPGRADE-SCHEMA-MIGRATION-1`，HEAD `43a76b204`。
- 集成：main `61601dc8c`（round 3 + round 2 review 合并）。
- 证据：`verification/UPGRADE-SCHEMA-MIGRATION-1/{unit-tests.log,pytest-full.log,pytest-full-summary.txt}`。

## Review

- 实施与自查：DSH（Lead）。
- round 1（region-workbench-owner，`fd925fcf7`）：FAIL（只 seed v1-era；断言不足；日志头缺失）。
- round 2（`3710e0014`）：FAIL（v5 的 step_runs/step_result_candidates 仍空表；"全字段"断言不全；summary 无头）。
- **round 3 返修**：seed v3/v4 的 step_runs/step_result_candidates（含 `step_run_ids_json` 关系）→ v5 后逐列断言；`EXPECTED` 全列断言机制；
  `_assert_latest` 增列/索引/外键检查；`FROZEN_V1_TABLES` + 版本连续守卫；三份证据均带 5 行命令头。
- 复审：**待 region-workbench-owner 再审 `61601dc8c`**。
- 独立复审 round 3（region-workbench-owner，reviewed_head `43a76b204`）：**PASS**（P0=0，P1=0；11 passed、v5 四张重建表实测各 1 行且 EXPECTED 逐列断言、FROZEN_V1_TABLES 与实际 v1 表集合完全一致、3/3 pin、三份证据 5 行命令头、check PASS；剩余 4×P2：region_revisions.source_run_id NULL 未记录、未检测额外行、_assert_latest 结构检查非全量、旧库仍由生产 MIGRATIONS 合成）。详见 [`doc/reviews/UPGRADE-SCHEMA-MIGRATION-1.md`](../reviews/UPGRADE-SCHEMA-MIGRATION-1.md) 的 Round 3 Review。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| unit-tests | AC1/AC2/AC3 | verification/UPGRADE-SCHEMA-MIGRATION-1/unit-tests.log | 43a76b204 | 888a10b9258bdf2de42cba86188824ac090eb63c9bb9dda597cc12a0e228a58c | CANONICAL |
| pytest-full-log | AC4 | verification/UPGRADE-SCHEMA-MIGRATION-1/pytest-full.log | 43a76b204 | fee8d85a43f7caebfe324bc48c65c4c8765687ca5e680618f2790988dad637c9 | CANONICAL |
| pytest-full-summary | AC4/AC5 | verification/UPGRADE-SCHEMA-MIGRATION-1/pytest-full-summary.txt | 43a76b204 | be4cdad218b5720b2a89daf7bf5ed93713658a3e044261e48354999eb30e5102 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/UPGRADE-SCHEMA-MIGRATION-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/UPGRADE-SCHEMA-MIGRATION-1 | 提交 43a76b204 | 测试实现（round 3） |
| task-env | G:/CODEX/New Manga.workspace/task-envs/UPGRADE-SCHEMA-MIGRATION-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/UPGRADE-SCHEMA-MIGRATION-1 | pytest-full.log | 回归日志 |

## Closeout Record

- Closed：2026-10-29 as **done**（3 轮独立 Review：FAIL→FAIL→PASS；round 3 P0=0、P1=0、4×P2 不阻塞）。
- 交付：	ests/storage/test_upgrade_schema_data.py（11 用例）——v1–v5 逐版本合成旧数据库并逐代 seed；v5 四张重建表
  （pipeline_run_targets/pipeline_tasks/step_runs/step_result_candidates）全部有数据并逐列断言；全列 EXPECTED 断言；结构/索引/外键检查；
  FROZEN_V1_TABLES 防回归；逐版本幂等。
- 集成：main 61601dc8c（代码 43a76b204）。
- 剩余 P2（不阻塞，可后续补齐）：region_revisions.source_run_id 未纳入 EXPECTED、未检测额外行、_assert_latest 结构检查非全量、
  旧库仍由生产 MIGRATIONS 合成。
- 修复了 UPGRADE-REHEARSAL-1 的剩余验证限制（真实旧 schema 数据不可得 → 合成覆盖 v1–v5 迁移链）。
