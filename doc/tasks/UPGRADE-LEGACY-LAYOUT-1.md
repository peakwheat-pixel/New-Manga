---
id: UPGRADE-LEGACY-LAYOUT-1
title: 修复真实升级缺口——Core 启动时迁移旧布局 data/library.db → 根 library.db
kind: fix
governance_version: 3
status: ready
approval: user_authorized_2026-10-29_fix_upgrade_gap
suggested_owner: dsh
owner: dsh-lead
reviewer: region-workbench-owner
depends_on: [UPGRADE-REHEARSAL-1]
base_commit: af6d9e94d
branch: task/UPGRADE-LEGACY-LAYOUT-1
worktree: G:/CODEX/New Manga.workspace/worktrees/UPGRADE-LEGACY-LAYOUT-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
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

# UPGRADE-LEGACY-LAYOUT-1：修复真实升级缺口

## 来源

`UPGRADE-REHEARSAL-1`（2026-10-29）用真实升级前备份演练发现：`src/bootstrap/core_service.py:666` 固定读取
`data_root / "library.db"`（根），不识别旧布局 `data/library.db`（`git grep` 0 命中）→ 旧用户升级后
书架不可见。用户 2026-10-29 指示「立即修复升级缺口」。

## 目标

Core 启动时（`main()`）检测旧布局并迁移到新布局：
- 旧：`<root>/data/library.db`、`<root>/data/managed/`、`<root>/data/backups/`
- 新：`<root>/library.db`、`<root>/managed/`、`<root>/backups/`
- `catalog/`、`derived/`、`logs/` 新旧同路径，不动。

## Acceptance Criteria

- [ ] **AC1 迁移实现**：新增 `src/infrastructure/sqlite/upgrade_legacy_layout.py`（`migrate_legacy_layout(data_root)`），在 `core_service.main()` 的 `assemble_production_core` 前调用；只复制不删除、保留旧 `data/`（可回滚）、写操作日志。
- [ ] **AC2 幂等与守卫**：根 `library.db` 已存在 → 不覆盖（skip）；旧 `data/library.db` 不存在 → no-op；重复运行不重复复制（幂等）；迁移前对旧库做 `PRAGMA integrity_check`（损坏则报错不迁移）。
- [ ] **AC3 测试**：`tests/infrastructure/test_upgrade_legacy_layout.py` 覆盖：正常迁移（含 managed/backups）、根已存在 skip、无旧布局 no-op、幂等、损坏库拒绝；`python -m pytest tests/infrastructure -q` 与全量 pytest 回归无新增失败。
- [ ] **AC4 真实数据验证**：用 `UPGRADE-REHEARSAL-1` 的真实备份布局（`data/library.db` v6）跑迁移 → 根 `library.db` 出现且 SHA/完整性一致、`data/` 保留、可被 Core 读取（books=1）；证据落 `verification/UPGRADE-LEGACY-LAYOUT-1/`。
- [ ] **AC5 门禁**：`check.ps1` PASS；契约不变（仅启动时数据迁移）；Handoff。

## 禁止范围

不改命令面契约/DB schema；不删除旧数据；不修改 `UPGRADE-REHEARSAL-1` 历史记录字节；不 push main。

## 依赖与风险

- 依赖：UPGRADE-REHEARSAL-1（closed_with_limitations，含真实备份布局证据）。
- 风险：①迁移时机需早于任何 DB 读取（放在 `main()` 开头、`assemble_production_core` 前）；②`NEWMANGA_DATA_ROOT` 隔离环境同样生效（测试覆盖）；③Windows 文件被占用时的复制失败需清晰报错。

## 交付与运行记录

- 待实施。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/UPGRADE-LEGACY-LAYOUT-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/UPGRADE-LEGACY-LAYOUT-1 | verification/UPGRADE-LEGACY-LAYOUT-1/** | 待创建 |

## Closeout Record

- 待实施后填写。
