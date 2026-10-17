---
id: P19-UI-FIX-2
title: 修复顶栏「导入作品」静默无反馈（P19-UI-FIX-1 遗漏的入口）
kind: bugfix
governance_version: 2
status: in_progress
approval: coordinator_release_20261017_from_P19_r6_probe
suggested_owner: Codex
owner: codex
reviewer: DeepSeek Harness
depends_on: [P19-UI-FIX-1]
base_commit: 3a3eeab02114b0230fe27bb60396e720dada6d26
branch: codex/P19-UI-FIX-2
worktree: G:/CODEX/New Manga.workspace/worktrees/P19-UI-FIX-2
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/P19-UI-FIX-2
---

# P19-UI-FIX-2：顶栏「导入作品」静默无反馈

## 来源
`verification/P19/create-work-and-import-r6.md`：重建产品实测，**顶栏 `导入作品` `IsEnabled=True`，点击后无选择器/无错误/无反馈**（10 次窗口采样）；而空态那组按钮（`import-file-btn`/`import-folder-btn`）已由 P19-UI-FIX-1 修好。→ **修复遗漏了顶栏入口**。

## Acceptance Criteria
- [ ] **AC1**：顶栏 `导入作品` 点击后**必须**打开文件/文件夹选择器，**或**给出**可见文本反馈**（与空态一致口径：说明为何当前不可导入）；**不得静默无反应**。
- [ ] **AC2**：若存在多种导入入口（顶栏/空态/其它），**必须逐一检查**并保证**行为一致**（给 Feedback 或都打开选择器）。
- [ ] **AC3**：新增前端测试覆盖顶栏入口的反馈/选择器行为；既有 **274** 测试不回归；`npm run build` exit 0。
- [ ] **AC4 真实 GUI 复验**：用**重建产品**（`npm run build` + `build_sidecar.ps1 -Force` + `cargo build`，**bundle==resource hash 一致**）+ 隔离数据根，采集 UIA/窗口证据证明：点击顶栏 `导入作品` 后**出现选择器或可见反馈**。
- [ ] **AC5 交付**：固定 commit + Handoff + Canonical Evidence（`status: in_review`；BL-15/17/19/16/18）。

## 允许 / 禁止
- 允许：`apps/desktop/frontend/**`、本 Task、`doc/handoffs/P19-UI-FIX-2-*.md`、`verification/P19-UI-FIX-2/**`。
- 禁止：改契约/Schema/依赖、改 `src/**`（需 Core 配合先上报）；**不得**用"隐藏顶栏按钮"规避；不改 `doc/STATUS.md`/`doc/REBASELINE_PLAN.md`；不触碰用户 19 项 dirty。

## 依赖、风险与阻塞
- 前置：P19-UI-FIX-1（done）。**被阻塞方**：P19 的 AC2。
- 风险：把"隐藏按钮"当修复（AC2 明确禁止）。
- **注意**：本 Task **不**裁决"空书架是否应允许新建作品"（该产品取舍待用户）；仅修"点了没反馈"。

## 交付与运行记录
- 2026-10-17 Coordinator 释放（dsh, epoch 6）。
