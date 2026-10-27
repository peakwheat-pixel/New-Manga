---
id: F11-HOTKEY-1
title: 全局 F11 快捷键（沉浸/全屏切换）
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_followups_batch_a2
suggested_owner: saber-ui-spec
owner: null
reviewer: dsh
depends_on: []
base_commit: 171529b5d
branch: task/F11-HOTKEY-1
worktree: G:/CODEX/New Manga.workspace/worktrees/F11-HOTKEY-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/F11-HOTKEY-1
allowed_paths:
  - doc/tasks/F11-HOTKEY-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/F11-HOTKEY-1/**
  - G:/CODEX/New Manga.workspace/task-envs/F11-HOTKEY-1/**
  - G:/CODEX/New Manga.workspace/worktrees/F11-HOTKEY-1/**
---

# F11-HOTKEY-1：全局 F11 快捷键（沉浸/全屏切换）

## 背景

READER-LIBRARY-WIRE-1 的沉浸入口目前只有工具栏按钮 + 双击；遗留项要求 **F11** 全局快捷键（在应用任意页面均可切换）。

## Acceptance Criteria

- [ ] **AC1 快捷键**：应用内按 **F11** 切换沉浸/全屏（非阅读器页进入时打开当前书的沉浸？或先进入阅读器再沉浸——行为需在 Record Decision 中定并测试）；Esc 退出后回到原页面。
- [ ] **AC2 不干扰输入**：搜索框/文本框聚焦时 F11 不吞字、不误触发；与现有键位（H/F/方向键）无冲突。
- [ ] **AC3 测试**：Avalonia.Headless 覆盖「按 F11 进入/退出」「焦点在输入框时不触发」；真机一次（截图/窗口状态）。
- [ ] **AC4 回归**：`scripts/test.ps1` 全绿；vitest 60/567；pytest 基线 3F/2739P/9S 无新增失败。
- [ ] **AC5 门禁**：`check.ps1 -TaskPath` PASS；64-hex pin；Handoff + Record Decision（快捷键注册方式/冲突策略）。

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER、`verification/F11-HOTKEY-1/**`、workspace。

## 禁止范围

不改协议/Host 契约语义、不改 Python Core、不改旧壳、不 push、不 gc/prune；不得引入全局系统级热键抢占其他应用（应用内 F11 即可，除非 Record Decision 明确）。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/F11-HOTKEY-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/F11-HOTKEY-1 | 待填 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
