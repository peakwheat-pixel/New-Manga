---
id: THEME-MACOS-2
title: macOS 风主题重做（独立分支）
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-28_goal_all_authorized
suggested_owner: saber-ui-spec
owner: null
reviewer: dsh
depends_on: []
base_commit: d2f66a19e
branch: task/THEME-MACOS-2
worktree: G:/CODEX/New Manga.workspace/worktrees/THEME-MACOS-2
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/THEME-MACOS-2
allowed_paths:
  - doc/tasks/THEME-MACOS-2.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/src/NewManga.Theme/**; apps/desktop-avalonia/src/NewManga.App/**; apps/desktop-avalonia/tests/**
  - verification/THEME-MACOS-2/**
  - G:/CODEX/New Manga.workspace/task-envs/THEME-MACOS-2/**
  - G:/CODEX/New Manga.workspace/worktrees/THEME-MACOS-2/**
---

# THEME-MACOS-2：macOS 风主题重做（独立分支）

## 背景
`THEME-MACOS-1` 由外部会话直接在 main 工作树编辑，反复出现半成品提交导致构建红；该卡复核已暂缓。本任务在**独立分支**重做，避免并发污染。

## Acceptance Criteria
- [ ] **AC1 主题可见可切换**：`macos-sonoma`（中文名「macOS 风」）出现在设置页主题列表；`ThemePacks.Default` 仍为 `saber-purple`；既有主题不受影响。
- [ ] **AC2 Light/Dark 渲染**：同一 pack 内嵌 Light/Dark 两套 token；真机截图 4 张（书架/设置页 × Light/Dark）。
- [ ] **AC3 热切换**：p95 ≤100ms（沿用现有测量机制，给数字）。
- [ ] **AC4 对比度**：正文 ≥4.5:1、次要 ≥3:1（给计算）。
- [ ] **AC5 字体许可**：仅 OFL 等兼容字体；不随包商业/系统字体。
- [ ] **AC6 回归**：干净 worktree 上 `scripts/test.ps1` 全绿（≥241）；vitest 60/567；pytest 无新增失败。
- [ ] **AC7 门禁**：`check.ps1 -TaskPath` PASS；64-hex pin；Handoff + Record Decision。

## 允许修改范围
`apps/desktop-avalonia/src/NewManga.Theme/**`、主题所需最小 `src/NewManga.App/**`、`tests/**` 主题测试、`verification/THEME-MACOS-2/**`、本卡/STATUS/PLAN/LEDGER、workspace。

## 关键约束
- **必须**在自己的 `git worktree`（`task/THEME-MACOS-2`）里工作；**禁止**在主工作树直接编辑/提交
- 只 `git add` 自己的显式路径；禁止 reset/stash/删他人 worktree

## 禁止范围

不改 Python Core 语义/协议/Host 契约/旧壳、不 push、不 gc/prune；不得伪造结果；**禁止 `git add -A`（主工作树有其它会话改动）**。
