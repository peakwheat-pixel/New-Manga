---
id: RELEASE-SMOKE-1
title: 新包真机全流程快检
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_round_2_5
suggested_owner: core-admin-rca
owner: null
reviewer: dsh
depends_on: []
base_commit: 13cf26f6c
branch: task/RELEASE-SMOKE-1
worktree: G:/CODEX/New Manga.workspace/worktrees/RELEASE-SMOKE-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/RELEASE-SMOKE-1
allowed_paths:
  - doc/tasks/RELEASE-SMOKE-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/scripts/**; apps/desktop-avalonia/docs/**
  - verification/RELEASE-SMOKE-1/**
  - G:/CODEX/New Manga.workspace/task-envs/RELEASE-SMOKE-1/**
  - G:/CODEX/New Manga.workspace/worktrees/RELEASE-SMOKE-1/**
---

# RELEASE-SMOKE-1：新包真机全流程快检

## 背景
REPACK-2 包（base 102,981,645B / models 724,989,976B）已产出；UI 导入/导出入口已接。需要一次全新安装→使用→导出的真机验收。

## Acceptance Criteria
- [ ] **AC1 安装**：全新目录安装最新 models 包（install.ps1 / 安装 smoke 流程）→ 启动应用（无 console 窗口、sidecar 随包）。
- [ ] **AC2 全流程**：书架→（导入 fixture 书）→阅读器→翻页/进度→沉浸 Esc/H→导出（ZIP）→打开导出目录；每步截图 + 关键耗时。
- [ ] **AC3 稳定性**：运行中无残留进程；卸载后目录干净、无系统残留（凭据/注册表项列清）。
- [ ] **AC4 真机 5 项快检**：Mica 取色、4K@200% DPI、工作集、IME（用户确认）、Esc/H；其中 IME 标注需用户确认。
- [ ] **AC5 门禁**：check.ps1 -TaskPath PASS；64-bit pin；Handoff；不 push、不删旧包。

## 允许修改范围

`apps/desktop-avalonia/scripts/**; apps/desktop-avalonia/docs/**`、本卡、STATUS/PLAN/LEDGER、`verification/RELEASE-SMOKE-1/**`、workspace。

## 禁止范围

不改协议/Host 契约/旧壳、不 push、不 gc/prune；不得伪造结果；**不得把任何 API key/secret 写入仓库、日志或证据**。
