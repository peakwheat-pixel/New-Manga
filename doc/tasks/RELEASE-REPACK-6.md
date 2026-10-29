---
id: RELEASE-REPACK-6
title: 重建发布包 0.1.1（含旧布局迁移修复 sidecar + NSIS 安装包）
kind: release
governance_version: 3
status: ready
approval: user_authorized_2026-10-29_repack_011
suggested_owner: dsh
owner: dsh-lead
reviewer: region-workbench-owner
depends_on: [REAL-USER-UPGRADE-1, UPGRADE-LEGACY-LAYOUT-1, NSIS-INSTALLER-1, AGPL-RELEASE-1]
base_commit: 6862a4f95
branch: task/RELEASE-REPACK-6
worktree: G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-6
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/RELEASE-REPACK-6
allowed_paths:
  - doc/tasks/RELEASE-REPACK-6.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/src/NewManga.App/NewManga.App.csproj
  - verification/RELEASE-REPACK-6/**
  - G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-6/**
  - G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-6/**
---

# RELEASE-REPACK-6：重建发布包 0.1.1

## 来源

`REAL-USER-UPGRADE-1` 发现：**官方 0.1.0 安装包 sidecar 为 `bde2d866…`（旧 HEAD `7f0d1daef`）不含旧布局迁移修复**；
含修复的 sidecar 为 `d08e0951…`（HEAD `474d57b02`）。用户 2026-10-29 指定重建发布包 0.1.1。

## 目标

用 main HEAD（`6862a4f95`，含 `UPGRADE-LEGACY-LAYOUT-1` 修复）重建：
1. Python Core sidecar（含权重：detector/ocr/sfx）；
2. Avalonia App（single-file self-contained）；
3. 发布包 stage + ZIP（`-models` 变体）；
4. NSIS 安装包 `NewManga-0.1.1-setup.exe`；
5. 重新验收（安装/卸载/数据根保留 + 真实旧布局升级演练）；
6. 替换发布构件（GitHub Release 资产）。

## Acceptance Criteria

- [ ] **AC1 版本**：App `<Version>` = 0.1.1；VERSION.json / installer / 安装包版本一致。
- [ ] **AC2 sidecar 修复**：重建 sidecar `core_service.exe` SHA ≠ `bde2d866…`，含旧布局迁移（HEAD 记录到 VERSION.json sidecar_build）。
- [ ] **AC3 包构建**：base + models stage/ZIP 生成、大小在预算内、许可证文件齐全（AGPL 声明同 0.1.0）。
- [ ] **AC4 NSIS 安装包**：`NewManga-0.1.1-setup.exe` 生成；静默安装/卸载成功、数据根保留、卸载项清理。
- [ ] **AC5 真实升级验收**：用新安装包在真实数据副本（A）与真实旧布局备份（B）上验证：A 数据字节一致；B 迁移 + 书架 1 本。
- [ ] **AC6 发布构件**：新安装包 + SHA256SUMS 替换/更新 GitHub Release 资产（不 push main）。
- [ ] **AC7 证据**：构建日志、SHA256、install-smoke、升级验收、卡与 pin；check PASS。

## 禁止范围

不 push 产品主分支（main）；禁止 `git add -A`；不改 Core 语义；不处理 SignPath 签名（审核中，另行）。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Closeout Record

- 待实施后填写。
