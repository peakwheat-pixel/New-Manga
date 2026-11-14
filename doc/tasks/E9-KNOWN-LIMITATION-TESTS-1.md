---
id: E9-KNOWN-LIMITATION-TESTS-1
title: 按 ZCode 裁决改造 FullSyncChain 测试为 typed 拒绝（KNOWN-LIMITATION-E9）
kind: test
governance_version: 3
status: done
disposition: "执行 E9-PRODUCT-ADJUDICATION 的测试口径：ACK 成功期望从未可达，改为断言精确拒绝码"
approval: DSH 2026-11-15
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - E9-PRODUCT-ADJUDICATION
base_commit: aa20202b7
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/E9-KNOWN-LIMITATION-TESTS-1
allowed_paths:
  - doc/tasks/E9-KNOWN-LIMITATION-TESTS-1.md
  - doc/reviews/E9-KNOWN-LIMITATION-TESTS-1-*.md
  - doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/GOAL-PROGRESS-2026-11-02.md
  - verification/E9-KNOWN-LIMITATION-TESTS-1/**
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11Residual4AIpcTests.cs
---

# E9-KNOWN-LIMITATION-TESTS-1

## 交付

按 ZCode 裁决把 `ProductionDispatcherFullSyncChain_NewKeyOldDigestConserved` 的
"ACK 成功"期望改为**断言 typed 拒绝**，并**新增** 3 条断言（状态无损 / 幂等 / catalog 空）。

## 结果

| 口径 | 前 | 后 |
|---|---|---|
| 带 opt-in 三类 | 12 / 1 | **13 / 0** |
| 无夹具 Host 全量 | 325 / 0 / 74 / 399 | **325 / 0 / 74 / 399** |

## 为什么不是放宽

旧 `acknowledged` 期望**从未可达**（修复前同样失败，只是错误码被兜底成 `SOURCE_ENTRY_MISSING`）。
本改造**收紧**（精确码）+ **扩容**（+3 断言），未删除任何 scan/plan/apply 段的 wire 级断言。

## 我犯的两个错（已写进测试注释）

1. 异常类型猜成 `CoreOperationException`，实际是 `SourceAccessException`；
2. 猜"没发布所以旧 binding 仍 `healthy`"，实测 **`superseded`** —— supersede 在 **core-commit** 发生，不是 ACK。

**两处都是"猜而没有先测"**。

## 边界

**没有修好 E-9。** 它仍是能力限制：非 folder 来源的 sync 完成链不可用，现在失败 **typed 且可解释**。
解锁路径 = mint-time DPAPI 路径映射（后续 Task），**未做**。

**"13/0" 是测试口径与产品能力声明对齐，不是"恢复功能可用"。**
