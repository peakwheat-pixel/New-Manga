---
id: CHAPTER-SELECTOR-1
title: 多章选择器 + 多书入口
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_followups_batch_a1
suggested_owner: avalonia-spike
owner: null
reviewer: dsh
depends_on: []
base_commit: 230164c5c
branch: task/CHAPTER-SELECTOR-1
worktree: G:/CODEX/New Manga.workspace/worktrees/CHAPTER-SELECTOR-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/CHAPTER-SELECTOR-1
allowed_paths:
  - doc/tasks/CHAPTER-SELECTOR-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/CHAPTER-SELECTOR-1/**
  - G:/CODEX/New Manga.workspace/task-envs/CHAPTER-SELECTOR-1/**
  - G:/CODEX/New Manga.workspace/worktrees/CHAPTER-SELECTOR-1/**
---

# CHAPTER-SELECTOR-1：多章选择器

## 背景

READER-LIBRARY-WIRE-1 完成书库接线，但固定第一本书第一章；多章用户无法切换。

## Acceptance Criteria

- [ ] **AC1 书目/章节选择**：阅读器页提供章节列表（`list_chapters`），可切换章节并渲染对应页；当前书/章状态可见。
- [ ] **AC2 多书**：书架上多本书时，从任一本书进入阅读器都打开对应书（不再固定第一本）。
- [ ] **AC3 测试**：Headless 覆盖「切章更新页数/投影」「多书分别打开」；真机用 BOOK-FIXTURE 数据根验证（可复制成两本书）。
- [ ] **AC4 回归**：`scripts/test.ps1` 全绿；vitest 60/567；pytest 无新增失败。
- [ ] **AC5 门禁**：`check.ps1 -TaskPath` PASS；64-hex pin；Handoff。

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER、`verification/CHAPTER-SELECTOR-1/**`、workspace。

## 禁止范围

不改协议/Host 契约语义、不改 Python Core、不改旧壳、不 push、不 gc/prune。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/CHAPTER-SELECTOR-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/CHAPTER-SELECTOR-1 | 待填 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
