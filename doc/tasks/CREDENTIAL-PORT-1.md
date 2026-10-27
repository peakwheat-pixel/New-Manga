---
id: CREDENTIAL-PORT-1
title: Host 凭据管理器端口（解除 credential_put/clear BLOCKED）
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_goal_auto_except_recommended
suggested_owner: core-admin-rca
owner: null
reviewer: dsh
depends_on: []
base_commit: e30149258
branch: task/CREDENTIAL-PORT-1
worktree: G:/CODEX/New Manga.workspace/worktrees/CREDENTIAL-PORT-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/CREDENTIAL-PORT-1
allowed_paths:
  - doc/tasks/CREDENTIAL-PORT-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/CREDENTIAL-PORT-1/**
  - G:/CODEX/New Manga.workspace/task-envs/CREDENTIAL-PORT-1/**
  - G:/CODEX/New Manga.workspace/worktrees/CREDENTIAL-PORT-1/**
---

# CREDENTIAL-PORT-1：Host 凭据管理器端口

## 背景

NS-WIRE-B2 中 `credential_put`/`credential_clear` **BLOCKED**：Core 只有 `BindProfileCredential`/`ClearProfileCredential` 绑定面；旧壳是「Host OS 凭据存储（Windows Credential Manager）+ 交互输入」两段式；Avalonia Host 无凭据端口（旧实现 `settings_bridge.rs:288-350`）。

## Acceptance Criteria

- [ ] **AC1 端口设计**：定义 Host 凭据端口（ICredentialStore 抽象 + Windows 实现：Win32 CredWrite/CredRead/CredDelete 或 DPAPI），记录与 Core `Bind/ClearProfileCredential` 的两段式协议。
- [ ] **AC2 接线**：`credential_put`/`credential_clear` 接线：写入 OS 凭据存储 → Core 绑定 ref；清除时清理两端；失败 typed 且不留孤儿凭据。
- [ ] **AC3 安全**：不落明文到日志/DB；凭据不出进程（Core 只拿 ref）；错误信息不泄露 secret。
- [ ] **AC4 真机/单测**：真实写入→读取→绑定→清除全链；单测覆盖（fake store）；对冻结 sidecar 真实执行断言。
- [ ] **AC5 回归/门禁**：test.ps1 全绿；pytest 无新增失败；check.ps1 -TaskPath PASS；64-hex pin；Handoff。

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER、`verification/CREDENTIAL-PORT-1/**`、workspace。

## 禁止范围

不改 Python Core 语义/协议/旧壳、不 push、不 gc/prune；不得把 secret 写日志/DB/测试快照；不得伪造成功。
