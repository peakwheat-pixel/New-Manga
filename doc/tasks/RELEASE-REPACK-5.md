---
id: RELEASE-REPACK-5
title: 第五次重打包（含三布局主题合并）与安装验收
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-28_repack
suggested_owner: core-admin-rca
owner: null
reviewer: dsh
depends_on: []
base_commit: 679967c6e
branch: task/RELEASE-REPACK-5
worktree: G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-5
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/RELEASE-REPACK-5
allowed_paths:
  - doc/tasks/RELEASE-REPACK-5.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - packaging/**
  - apps/desktop-avalonia/scripts/**
  - apps/desktop-avalonia/docs/**
  - verification/RELEASE-REPACK-5/**
  - G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-5/**
  - G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-5/**
---

# RELEASE-REPACK-5：第五次重打包（含三布局主题）

## 背景
REPACK-4（repo_head 1b89c5e5）之后，main 已合并 **THEME-MACOS-2 三布局实现**（Sonoma/Launchpad/Split，superset，test 249/249，HEAD \$h\）。REPACK-4 包不含该主题，需要重新出包。

## Acceptance Criteria
- [ ] **AC1 重打包**：当前 HEAD 重打 base+models zip（记录 HEAD/新旧 sha256/大小；torch-free 断言）。
- [ ] **AC2 安装 + 主题验收**：全新安装 → 启动 → 设置页主题列表可见 **7 packs 且含 macOS 相关三套布局主题**（Sonoma/Launchpad/Split，按实际注册名为准）→ 切换主题生效（截图 2 张，含至少一套布局）。
- [ ] **AC3 冒烟**：书架 → 导入 → 阅读 → 沉浸 Esc/H → 导出 ZIP（记录产物 sha）；
- [ ] **AC4 门禁**：干净 worktree 	est.ps1 全绿（**≥249**）；pytest 无新增失败；check.ps1 -TaskPath PASS；64-hex pin；Handoff。
- [ ] **AC5 遗留**：Launchpad/Split 真机美观度仅截图记录，不做完整视觉验收（另行小卡）。

## 允许修改范围
packaging/**、pps/desktop-avalonia/scripts/**、pps/desktop-avalonia/docs/**、本卡、STATUS/PLAN/LEDGER、erification/RELEASE-REPACK-5/**、workspace。

## 禁止范围
不改 Core/协议/Host 契约/旧壳、不 push、不 gc/prune；不得复用旧 exe 冒充新构建；不伪造截图/数字；禁止 \git add -A\。
