---
id: RELEASE-REPACK-3
title: 第三次重打包（含 UI 收尾）与全流程复验
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_round_2_5
suggested_owner: core-admin-rca
owner: null
reviewer: dsh
depends_on: []
base_commit: 10273c9ce
branch: task/RELEASE-REPACK-3
worktree: G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-3
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/RELEASE-REPACK-3
allowed_paths:
  - doc/tasks/RELEASE-REPACK-3.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - packaging/**
  - apps/desktop-avalonia/scripts/**
  - apps/desktop-avalonia/docs/**
  - verification/RELEASE-REPACK-3/**
  - G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-3/**
  - G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-3/**
---

# RELEASE-REPACK-3：第三次重打包与全流程复验

## 背景
RELEASE-SMOKE-1 发现 REPACK-2 包 `repo_head=0f4b836a5` **早于** IMPORT-EXPORT-UI-1（`13cf26f6c`）→ 安装包无导入/导出 UI。当前 HEAD 已含全部 UI 收尾。

## Acceptance Criteria
- [ ] **AC1**：用当前 HEAD 重打 base+models zip；记录 HEAD/新旧 sha256/大小；torch-free 断言。
- [ ] **AC2**：全新安装 → 书架→导入→阅读→进度→沉浸 Esc/H→导出 ZIP→打开导出目录（+ PDF，若 PDF-EXPORT-UI-1 已合）；每步截图/耗时。
- [ ] **AC3**：Mica/DPI 复核——明确 OS 版本/build；验证 Mica（actual/取色）与 4K@200% DPI（环境不满足则如实 BLOCKED + 当前显示器状态）。此前 smoke 报告 Win10/100% 与 MICA-FIX-1 真机证据矛盾，需结论。
- [ ] **AC4**：0 残留、console 0、卸载干净；历史凭据残留上报不擅删。
- [ ] **AC5**：test.ps1 全绿（≥225，**须在干净 worktree 验证**，避免并发未提交改动干扰）；pytest 无新增；check.ps1 -TaskPath PASS；64-hex pin；Handoff。

## 允许修改范围
`packaging/**`、`apps/desktop-avalonia/scripts/**`、`apps/desktop-avalonia/docs/**`、本卡、STATUS/PLAN/LEDGER、`verification/RELEASE-REPACK-3/**`、workspace。

## 禁止范围
不改 Core 语义/Host 契约/旧壳、不 push、不 gc/prune；不得复用旧 exe 冒充新构建；不伪造截图/数字；**不要在含他人未提交改动的主工作树上跑门禁**（用干净 worktree）。
