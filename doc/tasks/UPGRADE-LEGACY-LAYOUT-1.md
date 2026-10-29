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
integration_commit: 154f97a5c6a636b7ce319677b109e076b5ad33d3
delivery_head: 154f97a5c6a636b7ce319677b109e076b5ad33d3
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

# UPGRADE-LEGACY-LAYOUT-1：修复真实升级缺口（in_review）

## 来源

`UPGRADE-REHEARSAL-1` 用真实升级前备份演练发现：`core_service.py:666` 固定读取根 `library.db`，
不识别旧布局 `data/library.db` → 旧用户升级后书架不可见。用户 2026-10-29 指示「立即修复升级缺口」。

## 实现（已集成 main `154f97a5c`）

1. **新增 `src/infrastructure/sqlite/upgrade_legacy_layout.py`**：
   - `migrate_legacy_layout(data_root)`：检测 `<root>/data/library.db` → 复制到 `<root>/library.db`（含源存在的 `-wal/-shm`）；
     复制 `data/managed/`→`managed/`、`data/backups/`→`backups/`；`catalog/`、`derived/` 不动。
   - 安全规则：**只复制不删除**（旧 `data/` 保留可回滚）、当前库已存在则跳过（不覆盖）、
     staging 目录先验证（`PRAGMA integrity_check`）后原子 promote、损坏库抛 `LegacyLayoutError` 且不落地、
     staging 无论成败清理、写 `<root>/logs/upgrade-legacy.log`。
2. **`src/bootstrap/core_service.py` `main()`**：在 `data_root` 计算后、任何 DB 使用前调用迁移；
   `LegacyLayoutError` 只打印 stderr 警告（不阻塞启动）。
3. **`tests/infrastructure/test_upgrade_legacy_layout.py`**：7 个用例（正常迁移含 managed/backups、当前库优先、
   无旧布局 no-op、幂等、WAL 侧车迁移、损坏库拒绝、日志记录）。

## 验证

- 单测：`python -m pytest tests/infrastructure/test_upgrade_legacy_layout.py -q` → **7 passed**（`unit-tests.log`）。
- 全量回归：`python -m pytest -q` → **2607 passed / 10 skipped / 0 failed**（210s，`pytest-full.log`）。
- **真实数据验证**（2026-10-26 first-run 备份布局）：迁移后 `library.db` SHA 与源一致（`96fc4120…`）、
  源文件未修改、books=1、schema v6、`integrity_check=ok`、`data/` 保留、staging 清理（`real-data-verify.json`）。
- 幂等已验证：第二次运行 `skipped_reason="current library.db already present"`。

## Acceptance Criteria

- [x] **AC1 迁移实现**：独立模块 + `main()` 启动时调用；只复制不删除、保留旧 `data/`、写日志。<<MET>>
- [x] **AC2 幂等与守卫**：根库存在跳过；无旧布局 no-op；重复运行幂等；`PRAGMA integrity_check` 验证。<<MET>>
- [x] **AC3 测试**：7 用例覆盖（含 WAL/损坏/幂等）；单测 7 passed；全量 2607 passed。<<MET>>
- [x] **AC4 真实数据验证**：真实备份布局迁移 → SHA 一致、books=1、integrity ok、源未动。<<MET>>
- [x] **AC5 门禁**：`check.ps1` → **PASS**（3 warnings：非终态/PLAN 预算）；契约不变（仅启动迁移）；Handoff。<<MET>>

## 禁止范围（已遵守）

未改命令面契约/DB schema；未删除旧数据；未改历史记录字节；未 push main。

## 交付与运行记录

- worktree：`G:/CODEX/New Manga.workspace/worktrees/UPGRADE-LEGACY-LAYOUT-1`，HEAD `154f97a5c`。
- 集成：main fast-forward `154f97a5c`。
- 真实数据快照/验证：`verification/UPGRADE-LEGACY-LAYOUT-1/real-data-verify.json`。

## Review

- 实施与自查：DSH（Lead）。独立审查：**待补**（建议 `region-workbench-owner`：复核 `main()` 调用时机、
  Windows 文件占用边界、`NEWMANGA_DATA_ROOT` 隔离环境下行为）。Review 通过后转 `done`。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| unit-tests | AC3 | verification/UPGRADE-LEGACY-LAYOUT-1/unit-tests.log | - | 99853b0617920a93431e87b8fdaddd0a13da53cbe545d18db0e92cb1fb3b28f0 | CANONICAL |
| real-data-verify | AC4 | verification/UPGRADE-LEGACY-LAYOUT-1/real-data-verify.json | - | a676771122a6f9966785582fe615b5064d4adae0ae651d8561c0ad9a13ba7459 | CANONICAL |
| pytest-full-summary | AC3 | verification/UPGRADE-LEGACY-LAYOUT-1/pytest-full-summary.txt | - | 2581a7c643178733f0df410c3f42dba6a67442a5ba9f9310be7313be755df3f3 | CANONICAL |
| pytest-full-log | AC3 | verification/UPGRADE-LEGACY-LAYOUT-1/pytest-full.log | - | 674c590cf70bdde93e0658f585f9e6e5d3fe4e951b15503fd66673185809de9e | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/UPGRADE-LEGACY-LAYOUT-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/UPGRADE-LEGACY-LAYOUT-1 | 提交 154f97a5c | 修复实现与测试 |
| task-env | G:/CODEX/New Manga.workspace/task-envs/UPGRADE-LEGACY-LAYOUT-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/UPGRADE-LEGACY-LAYOUT-1 | real-data-root / pytest-full.log | 真实数据验证工作区 |

## Closeout Record

- 待独立 Review 通过后填写（target: done）。
