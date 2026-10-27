---
id: CREDENTIAL-UI-1
title: 设置页凭据 UI（安全输入 → credential_put / clear）
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_goal_auto_except_recommended
suggested_owner: saber-ui-spec
owner: null
reviewer: dsh
depends_on: []
base_commit: 77eb7cfd6
branch: task/CREDENTIAL-UI-1
worktree: G:/CODEX/New Manga.workspace/worktrees/CREDENTIAL-UI-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/CREDENTIAL-UI-1
allowed_paths:
  - doc/tasks/CREDENTIAL-UI-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/CREDENTIAL-UI-1/**
  - G:/CODEX/New Manga.workspace/task-envs/CREDENTIAL-UI-1/**
  - G:/CODEX/New Manga.workspace/worktrees/CREDENTIAL-UI-1/**
---

# CREDENTIAL-UI-1：设置页凭据 UI

## 背景

CREDENTIAL-PORT-1 已交付 `credential_put`/`credential_clear` 命令面 + Windows vault 端口（parity 66/0），但 **App UI 未接线**：Avalonia 设置页还没有凭据输入/清除控件（旧壳用 CredUI 对话框）。

## Acceptance Criteria

- [ ] **AC1 安全输入**：设置页新增「凭据」区块——provider/proxy 目标选择 + 密码框（**掩码、不可复制明文**、关闭窗口即清空）；提交调 `credential_put`，清除调 `credential_clear`；成功/失败 typed 提示。
- [ ] **AC2 状态显示**：列表显示各目标 `configured / missing`（不显示 secret）；冲突（`CREDENTIAL_CONFLICT`）给明确 UI 提示（替换需二次确认）。
- [ ] **AC3 安全**：secret 不进日志/不落 DB/不进 UI 自动化树（PasswordBox 用 Avalonia `TextBox PasswordChar` 或等价）；关闭后内存中不留明文引用。
- [ ] **AC4 测试**：Headless 覆盖「输入→put 调用参数正确（fake store）」「清除→clear」「冲突提示」；真机截图一次（掩码状态）。
- [ ] **AC5 回归/门禁**：`scripts/test.ps1` 全绿（≥189）；vitest 60/567；pytest 无新增失败；`check.ps1 -TaskPath` PASS；64-hex pin；Handoff。

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER、`verification/CREDENTIAL-UI-1/**`、workspace。

## 禁止范围

不改 Python Core 语义/协议/Host 契约/旧壳、不 push、不 gc/prune；不得把 secret 写日志/证据/测试快照；不得用明文 TextBox。
