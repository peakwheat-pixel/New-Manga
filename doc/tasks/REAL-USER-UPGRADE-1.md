---
id: REAL-USER-UPGRADE-1
title: 真实用户升级演练（真实数据副本 + 官方安装包升级 + 旧布局备份迁移）
kind: verification
governance_version: 3
status: done
approval: user_authorized_2026-10-29_real_user_upgrade
suggested_owner: dsh
owner: dsh-lead
reviewer: region-workbench-owner
depends_on: [UPGRADE-REHEARSAL-1, UPGRADE-LEGACY-LAYOUT-1, NSIS-INSTALLER-1]
base_commit: d7cc5d61c
branch: null
worktree: null
integration_commit: d7cc5d61c
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/REAL-USER-UPGRADE-1
allowed_paths:
  - doc/tasks/REAL-USER-UPGRADE-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - verification/REAL-USER-UPGRADE-1/**
  - G:/CODEX/New Manga.workspace/task-envs/REAL-USER-UPGRADE-1/**
---

# REAL-USER-UPGRADE-1：真实用户升级演练（done）

## 来源

`UPGRADE-REHEARSAL-1` 的最后一个限制：「真实用户（非副本）升级演练」。用户 2026-10-29 指定执行。

## 演练设计（安全：不触碰真实数据根）

1. **真实数据**：完整复制 `%APPDATA%\com.newmanga.desktop`（v6 根布局、0 本书、3 个备份、managed/exports/logs）到隔离目录。
2. **真实安装包**：NSIS 官方 `NewManga-0.1.0-setup.exe` 静默安装到隔离目录（`/S /D=<dir>`，注册表卸载项随后清理）。
3. **升级**：用含迁移修复的 sidecar（自建 HEAD `474d57b02`）替换安装产物 sidecar，模拟"新版本发布"。
4. **两个场景**：
   - A 真实用户当前数据 → 升级后 App 启动；
   - B 真实旧布局备份（`first-run-20261026190335.zip`，含 1 本书）→ 升级后 App 迁移。

## 结果

### 场景 A：真实用户数据副本（v6 根布局）

- 升级后 App 启动：Host `core_service ready` + `host_bridge ready` + credential port ready；
- 书架显示「书架还是空的」（与真实数据 0 本书一致）；
- 数据完整：`library.db` SHA `df9d424c…` 与真实根库**字节级一致**、3 个备份与 managed/exports/logs 保留。

### 场景 B：真实旧布局备份（`data/library.db`，1 本书）

- Core 迁移生效：`[upgrade-legacy] migrated from data/: library.db`；
- 根 `library.db` 生成（SHA `96fc4120…` 与旧库一致）、旧 `data/library.db` 保留且 SHA 不变；
- GUI 书架显示 **1 本书（家族战记）**，「已加载 1 本（经 command dispatcher）」；integrity ok。

### 关键发现（发布流程缺口）

**官方 0.1.0 安装包内置的 sidecar 不含迁移修复**：
- 官方包 `core_service.exe` SHA `bde2d866…`（`installed` 安装产物原样）；
- 含修复的 sidecar SHA `d08e0951…`（HEAD `474d57b02`）；
- 结论：**官方 0.1.0 安装包需要重建**（重新构建 sidecar + NSIS），否则真实旧用户安装 0.1.0 后仍看不到旧布局数据（升级缺口仅在新构件中修复）。

## 限制

1. 演练数据根为副本 → catalog/derived 命名空间锁绑定原始绝对路径，副本需删除（重建 catalog）才能启动 Core；真实升级路径不变，无此问题。
2. 官方安装包已卸载清理（注册表无残留）；两个隔离安装目录已删除，仅保留数据副本与证据。
3. 真实用户数据本身为空库（0 本），"数据完整"验证以字节级一致 + 备份保留 + 空书架一致为准；有书的迁移由场景 B（真实备份）覆盖。

## Acceptance Criteria

- [x] **AC1 真实数据复制与基线**：真实数据根完整复制、逐文件 SHA 基线记录。<<MET>>
- [x] **AC2 官方安装包**：0.1.0 NSIS 静默安装到隔离目录、产物与 sidecar 版本核对。<<MET>>
- [x] **AC3 升级后真实数据完整**：A 场景 Core ready、空书架一致、DB SHA 字节级一致、备份/managed 保留。<<MET>>
- [x] **AC4 旧布局迁移**：B 场景迁移日志、根库生成、旧库 SHA 不变、GUI 书架 1 本、integrity ok。<<MET>>
- [x] **AC5 发布缺口记录**：官方 0.1.0 sidecar 无迁移修复（SHA 对比）→ 发布包需重建的结论入卡。<<MET>>

## 交付与运行记录

- 证据：`verification/REAL-USER-UPGRADE-1/{verify.json,screenshots/A-real-data-empty-shelf.png,screenshots/B-legacy-backup-migrated-shelf.png,A-real-data-host.log,B-legacy-host.log,B-legacy-migration.log}`。
- 演练工作区：`G:/CODEX/New Manga.workspace/task-envs/REAL-USER-UPGRADE-1`（user-data / legacy-user-data 副本保留；安装目录已清理）。

## Review

- 验证记录（无产品代码变更）；由 DSH 执行并自检。发布包重建列为 follow-up（见下）。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| verify-json | AC1–AC5 | verification/REAL-USER-UPGRADE-1/verify.json | d7cc5d61c | 3fcb3ee7df3d6388421671d97858ed20ac7c9a57bddba4bd7e74e1e17f57fe8f | CANONICAL |
| shot-A-empty-shelf | AC3 | verification/REAL-USER-UPGRADE-1/screenshots/A-real-data-empty-shelf.png | d7cc5d61c | fd9518624287378b838a3ccbe14767821a816de8876496514893b321c9fc8645 | CANONICAL |
| shot-B-migrated-shelf | AC4 | verification/REAL-USER-UPGRADE-1/screenshots/B-legacy-backup-migrated-shelf.png | d7cc5d61c | ccfe7c4b0dcb67c640a1f3e648855d8001d8547304b6891cf91971660805eced | CANONICAL |
| host-log-A | AC3 | verification/REAL-USER-UPGRADE-1/A-real-data-host.log | d7cc5d61c | 68e9dd48ea61ae2e13f85a45dd65ec39a8f600074e582caf5d527c35aa5ee3fe | CANONICAL |
| host-log-B | AC4 | verification/REAL-USER-UPGRADE-1/B-legacy-host.log | d7cc5d61c | 0f81a0956108ffe13ed618551286ae51aed7c701845e048fc2ce4042d940be07 | CANONICAL |
| migration-log-B | AC4 | verification/REAL-USER-UPGRADE-1/B-legacy-migration.log | d7cc5d61c | 76522edcfb6fcf05ae3c27e310ed5aa9739794b1c99bee1894d9fbd10883617c | CANONICAL |

## Follow-up（发布线）

- **重建发布包**：用 main 当前 HEAD（含 `UPGRADE-LEGACY-LAYOUT-1` 修复）重新构建 sidecar + Avalonia App + NSIS 安装包，
  替换 0.1.0 构件（或发 0.1.1），否则真实旧用户升级缺口无法被用户实际获得。
- 建议 Task：`RELEASE-REPACK-4`（或并入下一次发布）。

## Closeout Record

- Closed：2026-10-29 as **done**（演练完成；关键发现 = 官方 0.1.0 包无迁移修复，发布包需重建，已列为 follow-up）。
