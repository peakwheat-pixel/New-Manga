---
id: UPGRADE-LEGACY-LAYOUT-1
title: 修复真实升级缺口——Core 启动时迁移旧布局 data/library.db → 根 library.db
kind: fix
governance_version: 3
status: in_review
approval: user_authorized_2026-10-29_fix_upgrade_gap
suggested_owner: dsh
owner: dsh-lead
reviewer: region-workbench-owner
depends_on: [UPGRADE-REHEARSAL-1]
base_commit: af6d9e94d
branch: task/UPGRADE-LEGACY-LAYOUT-1
worktree: G:/CODEX/New Manga.workspace/worktrees/UPGRADE-LEGACY-LAYOUT-1
integration_commit: 27de6fce3e6ad8a2d2da434fc67d3ac1da9d1f13
delivery_head: 27de6fce3e6ad8a2d2da434fc67d3ac1da9d1f13
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/UPGRADE-LEGACY-LAYOUT-1
allowed_paths:
  - doc/tasks/UPGRADE-LEGACY-LAYOUT-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - src/infrastructure/sqlite/upgrade_legacy_layout.py
  - src/bootstrap/core_service.py
  - tests/infrastructure/test_upgrade_legacy_layout.py
  - verification/UPGRADE-LEGACY-LAYOUT-1/**
  - G:/CODEX/New Manga.workspace/task-envs/UPGRADE-LEGACY-LAYOUT-1/**
  - G:/CODEX/New Manga.workspace/worktrees/UPGRADE-LEGACY-LAYOUT-1/**
---

# UPGRADE-LEGACY-LAYOUT-1：修复真实升级缺口（in_review / round 2）

## 来源

`UPGRADE-REHEARSAL-1` 用真实升级前备份演练发现：`core_service.py:666` 固定读取根 `library.db`，
不识别旧布局 `data/library.db` → 旧用户升级后书架不可见。用户 2026-10-29 指示「立即修复升级缺口」。

## 实现（round 2，已集成 main `27de6fce3`）

1. **新增 `src/infrastructure/sqlite/upgrade_legacy_layout.py`**：
   - `migrate_legacy_layout(data_root)`：检测 `<root>/data/library.db`（及 `data/managed/`、`data/backups/`）→ 迁移到根布局；
     库侧车 `-wal/-shm/-journal` 随库复制；`catalog/`、`derived/` 不动。
   - **原子迁移**：DB + 侧车 + managed + backups 全部复制到 `<root>/.upgrade-legacy-staging`，
     DB 经 `PRAGMA integrity_check` 验证；全部成功后统一 promote（目录先、DB 最后）；失败不落地；
     staging 始终清理。
   - **异常处理**：所有 I/O 失败（占用/权限）包装为 `LegacyLayoutError`；`main()` 捕获后打印 stderr 警告并继续启动。
   - **安全规则**：只复制不删除（旧 `data/` 保留可回滚）；当前库绝不覆盖；当前 `managed/backups` 缺失时补迁
     （修复上一轮部分迁移状态）。
2. **`src/bootstrap/core_service.py` `main()`**：`data_root` 计算后、任何 DB 使用前调用迁移。
3. **`tests/infrastructure/test_upgrade_legacy_layout.py`**：**10 个用例**（正常迁移含 managed/backups、当前库不覆盖+补迁、
   幂等、无旧布局 no-op、WAL/SHM/journal 侧车、损坏库拒绝、I/O 失败包装且根不动、
   部分失败（目录复制失败）DB 不 promote、仅旧目录迁移、日志记录）。

## 验证（round 2）

- 单测：`python -m pytest tests/infrastructure/test_upgrade_legacy_layout.py -q` → **10 passed**（`unit-tests.log`，带命令头）。
- 全量回归：`python -m pytest -q` → **2610 passed / 10 skipped / 0 failed**（208s，`pytest-full.log`，带命令头）。
- **真实数据首次迁移**（2026-10-26 first-run 备份，全新副本）：`migrated=true`、copied=`managed/, backups/, library.db`、
  源 SHA 未变、新库 SHA 与源一致（`96fc4120…`）、books=1、schema v6、`integrity_check=ok`、`data/` 保留（`real-data-first-migration.json`）。
- **幂等**：同一数据根第二次运行 `migrated=false`，`skipped_reason="current layout already present; legacy data left untouched"`（`real-data-second-run.json`）。

## Acceptance Criteria

- [x] **AC1 迁移实现**：独立模块 + `main()` 启动时调用；只复制不删除、保留旧 `data/`、写日志；原子 staging/promote。<<MET>>
- [x] **AC2 幂等与守卫**：当前库绝不覆盖；无旧布局 no-op；重复运行幂等；部分迁移可续迁；`integrity_check` 验证。<<MET>>
- [x] **AC3 测试**：10 用例（含 I/O 包装、部分失败、补迁、journal、隔离 root 传参）；单测 10 passed；全量 2610 passed。<<MET>>
- [x] **AC4 真实数据验证**：真实备份全新副本首次迁移 → SHA 一致、books=1、integrity ok；第二次幂等。<<MET>>
- [x] **AC5 门禁**：`check.ps1` PASS；契约不变（仅启动迁移）；Handoff `doc/handoffs/UPGRADE-LEGACY-LAYOUT-1-handoff.md`。<<MET>>

## 禁止范围（已遵守）

未改命令面契约/DB schema；未删除旧数据；未改历史 done 卡字节；未 push main。

## 交付与运行记录

- worktree：`G:/CODEX/New Manga.workspace/worktrees/UPGRADE-LEGACY-LAYOUT-1`，HEAD `27de6fce3`（round 1 `154f97a5c` → round 2 返修）。
- 集成：main fast-forward `154f97a5c`（round 1）→ `27de6fce3`（round 2 返修）。
- 证据：`verification/UPGRADE-LEGACY-LAYOUT-1/`（10 用例日志、全量日志、首次迁移/第二次运行 JSON、round 1 旧证据保留）。

## Review

- 实施与自查：DSH（Lead）。
- 独立审查（round 1，`region-workbench-owner`，reviewed_head `154f97a5c`）：**FAIL / CHANGES_REQUESTED**（P0=0；4×P1 + 6×P2；关键问题：unit-tests.log 证据内容是 “no tests ran”、real-data 证据只记录第二次运行、Windows I/O 失败未捕获会崩溃启动、DB 先 promote 目录后复制的部分失败不可自愈）。详见 [`doc/reviews/UPGRADE-LEGACY-LAYOUT-1.md`](../reviews/UPGRADE-LEGACY-LAYOUT-1.md)。
- **返修（round 2，HEAD `27de6fce3`）**：逐项处理 4×P1 + 4×P2：
  R-01 证据重生成（带 COMMAND/CWD/PYTHON/AT 头与 EXIT，10 passed）；
  R-02 全新副本首次迁移证据（`real-data-first-migration.json`）+ 第二次幂等证据（`real-data-second-run.json`）；
  R-03 所有 I/O 失败包装为 `LegacyLayoutError`（`main()` 捕获后继续）；
  R-04 原子 staging + 统一 promote（目录先、DB 最后）；
  R-05 当前库存在时补迁缺失 `managed/backups`；
  R-06 新增 I/O 包装/部分失败/补迁/仅目录/journal 用例（共 10）；
  R-07 全量日志带命令头；Handoff 已补。
- 复审：**待 region-workbench-owner 再审 `27de6fce3`**。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| unit-tests | AC3 | verification/UPGRADE-LEGACY-LAYOUT-1/unit-tests.log | 27de6fce3 | 4014b33493ec870bb7674777a929b206cc4f52212af7eae8a3e3d4cc1a5a4937 | CANONICAL |
| real-data-first-migration | AC4 | verification/UPGRADE-LEGACY-LAYOUT-1/real-data-first-migration.json | 27de6fce3 | 07051a0f1d68588c980c2554e804dabef695028ada0ae796a709080b0c9235cc | CANONICAL |
| real-data-second-run | AC4 | verification/UPGRADE-LEGACY-LAYOUT-1/real-data-second-run.json | 27de6fce3 | 7c5cf78c7fc69ed8f23f9b3f85ca8aab33e4eb96d5f736e4fee3f12777f16376 | CANONICAL |
| pytest-full-summary | AC3 | verification/UPGRADE-LEGACY-LAYOUT-1/pytest-full-summary.txt | 27de6fce3 | c20d516b3f5c230e7d30c11110ff2a4c817b1a444aedf74dd8aa5c3840d5e032 | CANONICAL |
| pytest-full-log | AC3 | verification/UPGRADE-LEGACY-LAYOUT-1/pytest-full.log | 27de6fce3 | 720f2e30fcc5bb1b8f9c81a2f2987b077c66904bf0b6af6a05614f597f975a1a | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/UPGRADE-LEGACY-LAYOUT-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/UPGRADE-LEGACY-LAYOUT-1 | 提交 27de6fce3 | 修复实现（round 2） |
| task-env | G:/CODEX/New Manga.workspace/task-envs/UPGRADE-LEGACY-LAYOUT-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/UPGRADE-LEGACY-LAYOUT-1 | real-data-fresh / pytest-full-v2.log | 真实数据验证工作区 |

## Closeout Record

- 待复审 PASS 后填写（target: done）；round 1 旧证据（`real-data-verify.json` / 旧日志）保留为历史。
