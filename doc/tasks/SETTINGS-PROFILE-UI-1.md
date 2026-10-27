---
id: SETTINGS-PROFILE-UI-1
title: 设置页 profile 管理 UI（provider / network profile 表单）
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_goal_auto_except_recommended
suggested_owner: saber-ui-spec
owner: null
reviewer: dsh
depends_on: []
base_commit: dde7f50ee
branch: task/SETTINGS-PROFILE-UI-1
worktree: G:/CODEX/New Manga.workspace/worktrees/SETTINGS-PROFILE-UI-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/SETTINGS-PROFILE-UI-1
allowed_paths:
  - doc/tasks/SETTINGS-PROFILE-UI-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/SETTINGS-PROFILE-UI-1/**
  - G:/CODEX/New Manga.workspace/task-envs/SETTINGS-PROFILE-UI-1/**
  - G:/CODEX/New Manga.workspace/worktrees/SETTINGS-PROFILE-UI-1/**
---

# SETTINGS-PROFILE-UI-1：设置页 profile 管理 UI

## 背景

命令面已 66/0；凭据 UI 已就绪（CREDENTIAL-UI-1），但真实用户无法在 UI 内创建 provider/network profile 目标。相关命令（`settings_provider_profiles_create/update/delete`、`settings_network_profiles_create/update/delete/test/resolve`、bindings set/clear、default set/clear）均已实现但无 UI 入口。

## Acceptance Criteria

- [ ] **AC1 provider profile 表单**：列表 + 新建/编辑/删除（名称/类型/base_url/model 等字段按 P15 profile schema），成功/失败 typed 提示。
- [ ] **AC2 network profile 表单**：列表 + 新建/编辑/删除 + `test`（显示诊断结果）+ `resolve`（显示解析结果）。
- [ ] **AC3 绑定/默认**：把 profile 绑定到 slot（provider bindings set/clear）、设默认 network profile。
- [ ] **AC4 测试**：Headless 覆盖 CRUD 调用参数、错误提示、空态；真机截图一次。
- [ ] **AC5 回归/门禁**：test.ps1 全绿（≥198）；vitest 60/567；pytest 无新增失败；check.ps1 -TaskPath PASS；64-hex pin；Handoff。

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER、`verification/SETTINGS-PROFILE-UI-1/**`、workspace。

## 禁止范围

不改 Python Core 语义/协议/Host 契约/旧壳、不 push、不 gc/prune；不显示/记录任何 credential secret；不得伪造测试诊断结果。
