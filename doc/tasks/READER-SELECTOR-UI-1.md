---
id: READER-SELECTOR-UI-1
title: book/chapter 选择器（替代手填 id）
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_goal_auto_except_recommended
suggested_owner: saber-ui-spec
owner: null
reviewer: dsh
depends_on: []
base_commit: 49c9e7f24
branch: task/READER-SELECTOR-UI-1
worktree: G:/CODEX/New Manga.workspace/worktrees/READER-SELECTOR-UI-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/READER-SELECTOR-UI-1
allowed_paths:
  - doc/tasks/READER-SELECTOR-UI-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/READER-SELECTOR-UI-1/**
  - G:/CODEX/New Manga.workspace/task-envs/READER-SELECTOR-UI-1/**
  - G:/CODEX/New Manga.workspace/worktrees/READER-SELECTOR-UI-1/**
---

# READER-SELECTOR-UI-1：book/chapter 选择器（替代手填 id）

## 背景
SETTINGS-PROFILE-UI-1 的「Provider 绑定」scope=book/chapter 仍需手填 id；书架/阅读器已有真实书与章节数据。

## Acceptance Criteria
- [ ] **AC1 书选择**：scope=book/chapter 时提供书本下拉（来自 `library_list_books`）与章节下拉（`list_chapters`），显示书名/章名而非裸 id。
- [ ] **AC2 联动**：选书→加载章节；切换 scope 类型时重置选择；未选时禁用 bindings 提交并提示。
- [ ] **AC3 测试**：Headless 覆盖「选书→章节加载→bindings 参数含真实 id」；空库空态。
- [ ] **AC4 回归**：test.ps1 全绿（≥210）；vitest 60/567；pytest 无新增失败。
- [ ] **AC5 门禁**：check.ps1 -TaskPath PASS；64-hex pin；Handoff。

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER、`verification/READER-SELECTOR-UI-1/**`、workspace。

## 禁止范围

不改 Python Core 语义/协议/Host 契约/旧壳、不 push、不 gc/prune；不得伪造结果；不显示/记录 secret。
