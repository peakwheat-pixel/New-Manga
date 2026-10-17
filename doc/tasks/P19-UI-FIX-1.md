---
id: P19-UI-FIX-1
title: 修复两处 P1 用户可见缺陷：未开放分区可操作 + 导入作品无反应
kind: bugfix
governance_version: 2
status: ready
approval: coordinator_release_20261017_from_P19_D_acceptance_findings
suggested_owner: Codex
owner: null
reviewer: null
depends_on: [P15, P12]
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/P19-UI-FIX-1
---

# P19-UI-FIX-1：两处 P1 用户可见缺陷

## 来源（P19 D 验收的真实产出）
1. **AC4 缺陷**（Codex R2 判 FAIL）：设置页 9 个「未开放」分区实测 `enabled=True`、可 Invoke、点击后页面变化 → **不满足"可见但不可操作"**。证据：`verification/P19/d-run-v2/uia/04-settings.uia.txt`、`trace.log`、`codex-review-r2.md`。
2. **导入缺陷**（本轮实测）：书架 `导入作品` 点击后 **10 次采样无任何选择器/无错误/无反馈** → 用户无法导入。证据：`verification/P19/import-no-response-r4.md`。

## Acceptance Criteria
- [ ] **AC1 未开放分区真禁用**：9 个「未开放」分区控件在可访问性上**必须为 disabled**（UIA `IsEnabled=False` 或等价，DOM `disabled`/`aria-disabled` 且**不可 Invoke**），**保留可见性与「未开放」原因文案**；不得仅靠文字标注。
- [ ] **AC2 导入必须可用或明确反馈**：`导入作品` 点击后**必须**打开文件/文件夹选择器（并在取消/失败时给出可见反馈）；若该能力确未实现，**必须**给出可见的"未开放"反馈，**不得静默无反应**。
- [ ] **AC3 反例/回归测试**：前端为两项各加测试（未开放分区不可交互；导入点击触发选择器或可见反馈）；既有前端 274 测试**不得回归**。
- [ ] **AC4 真实 GUI 复验**：交付须附 **UIA 实测证据**（修复后 `04-settings` 转储中未开放分区 `en=False`；`导入作品` 点击后出现选择器或可见反馈），用 `verification/P19/run-d-acceptance-v2.ps1` 同类脚本采集。
- [ ] **AC5 交付**：固定 commit + Handoff + Canonical Evidence（`status: in_review`；BL-15/17/19/16(RV-P15-04)/18 同前）。

## 允许 / 禁止范围
- **允许**：`apps/desktop/frontend/**`（组件与测试）、`verification/P19-UI-FIX-1/**`、本 Task、`doc/handoffs/P19-UI-FIX-1-*.md`。
- **禁止**：改契约、Schema/依赖；改 `src/**`（若确需 Core/host 配合**先上报另立**）；**不得**用"去掉未开放分区"或"隐藏导入按钮"来规避缺陷（必须保留可见性）；不改 `doc/STATUS.md`/`doc/REBASELINE_PLAN.md`；不触碰用户 19 项 dirty。

## 测试与证据
- 前端：`npm test`（基线 **274 passed / 28 files**）、`npm run build` 须为 exit 0。
- 真实 GUI：按 `verification/P19/run-d-acceptance-v2.ps1` 同类方式采集 UIA 证据（须设隔离 `NEWMANGA_DATA_ROOT`）。
- 归档日志+退出码到 `verification/P19-UI-FIX-1/**`。

## 依赖、风险与阻塞
- **前置**：P15（设置页）、P12（书架导入面）。**被阻塞方**：P19 的 AC4/AC2。
- 风险：把"隐藏/删除"当修复 → AC1 明确禁止。

## 交付与运行记录
- 2026-10-17 Coordinator 释放（dsh, epoch 6）。Handoff/Review/测试：尚无。