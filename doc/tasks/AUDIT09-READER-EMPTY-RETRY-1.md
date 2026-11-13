---
id: AUDIT09-READER-EMPTY-RETRY-1
title: Reader 已选中零页章节 Retry 后仍提示先选择（AUDIT-09-CAND-001 P3）
kind: implementation
governance_version: 3
status: ready
resume_status: ready
approval: user_authorized_2026-11-14 (所有任务交 DSH、自动裁决/规划、全部授权、无需用户介入)
suggested_owner: DSH
owner: DSH
reviewer: "DSH auto-adjudication (2026-11-14 owner directive); independent sub-agent review optional"
depends_on: [AUDIT12-PUBLISH-OUTPUT-1]
base_commit: e3569bca3
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/AUDIT09-READER-EMPTY-RETRY-1
allowed_paths:
  - apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/**
  - tests/NewManga.Presentation.Avalonia.Tests/**
  - verification/AUDIT09-READER-EMPTY-RETRY-1/**
  - doc/tasks/AUDIT09-READER-EMPTY-RETRY-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
---

# AUDIT09-READER-EMPTY-RETRY-1：Reader 已选中零页章节 Retry 后仍提示先选择（AUDIT-09-CAND-001 P3）

## 来源与目标

`AUDIT-09-CAND-001`（P3，TRIAGED）：合成 UI 测试中，已选中的零页章节在 Retry 后仍提示“先选择章节”；单一路径可见不一致，根因与普遍性未知（见 `audit/V1-FULL-AUDIT/reports/AUDIT-09-UI-UX-2026-11-13.md`）。目标：先隔离复现（fixture 覆盖有页/零页/切换选择/Retry），确认后做窄范围修复；若当前基线不可复现，记录 limitation 并关闭，不伪造修复。

## Acceptance Criteria

- [ ] **AC1**：定位 Reader 选择/Retry 状态机与提示逻辑，记录锚点、当前行为与复现条件。
- [ ] **AC2**：在隔离 fixture 中复现（有页、零页、切换选择、Retry）；若不可复现，记录证据与 limitation，不修改产品代码。
- [ ] **AC3**：若复现，做窄范围修复并运行相关 UI/表现层测试（记录命令/EXIT）；真实 GUI 演练为 NOT_RUN。
- [ ] **AC4**：证据 pin、四项门禁、资源 closeout、DSH 自动裁决。

## 允许修改范围

- `apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/**`（Reader 选择/提示相关表现层）
- `tests/NewManga.Presentation.Avalonia.Tests/**`
- `verification/AUDIT09-READER-EMPTY-RETRY-1/**`
- 本 Task 卡、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`

## 禁止范围

Avalonia TestHost 阻塞项不解除；不修改 Host/Core 契约、Schema、依赖、真实用户数据、远端、发布。

## 测试要求

优先使用可运行的隔离 fixture/单测；Avalonia TestHost 已知 8/8 runner EXIT 1、TRX 0（BLOCKED-TESTHOST-ACCESS），不得写成通过；真实 GUI 为 NOT_RUN。
