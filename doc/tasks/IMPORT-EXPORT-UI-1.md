---
id: IMPORT-EXPORT-UI-1
title: 导入/导出 UI 入口（选择器+进度+历史+取消）
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_goal_auto_except_recommended
suggested_owner: route-research
owner: null
reviewer: dsh
depends_on: []
base_commit: 49c9e7f24
branch: task/IMPORT-EXPORT-UI-1
worktree: G:/CODEX/New Manga.workspace/worktrees/IMPORT-EXPORT-UI-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/IMPORT-EXPORT-UI-1
allowed_paths:
  - doc/tasks/IMPORT-EXPORT-UI-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/IMPORT-EXPORT-UI-1/**
  - G:/CODEX/New Manga.workspace/task-envs/IMPORT-EXPORT-UI-1/**
  - G:/CODEX/New Manga.workspace/worktrees/IMPORT-EXPORT-UI-1/**
---

# IMPORT-EXPORT-UI-1：导入/导出 UI 入口

## 背景
命令面 66/0 已全实现；`library_import_file/folder`（grant 链）与 `library_start_export/cancel/get_export_snapshot/get_export_history`（EXPORT-E2E-CLOSE-1 已验证真跑）均无 UI 入口。

## Acceptance Criteria
- [ ] **AC1 导入**：书架/工作台提供「导入文件」「导入文件夹」入口（系统文件选择器）→ 调 `library_import_file/folder` → 进度/结果提示 + 刷新书架。
- [ ] **AC2 导出**：阅读器可对当前书发起导出（`library_start_export`）→ 显示快照进度（`get_export_snapshot`）、历史（`get_export_history`）、可取消（`cancel_export`）；完成后「打开导出目录」（`library_reveal_export_folder`）。
- [ ] **AC3 测试**：Headless 覆盖命令调用参数与状态迁移（fake controller）；真机截图一次。
- [ ] **AC4 回归**：test.ps1 全绿；vitest 60/567；pytest 无新增失败。
- [ ] **AC5 门禁**：check.ps1 -TaskPath PASS；64-hex pin；Handoff。

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER、`verification/IMPORT-EXPORT-UI-1/**`、workspace。

## 禁止范围

不改 Python Core 语义/协议/Host 契约/旧壳、不 push、不 gc/prune；不得伪造结果；不显示/记录 secret。
