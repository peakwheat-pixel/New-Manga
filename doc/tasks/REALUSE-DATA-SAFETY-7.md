---
id: REALUSE-DATA-SAFETY-7
title: SAFETY-6 Review P2 收尾——并发 NRE、证据 pin 规范化、日志格式
kind: quality
governance_version: 3
status: ready
approval: follow_up_of_REALUSE-DATA-SAFETY-6_review_2026-11-01
suggested_owner: dsh
owner: null
reviewer: null
depends_on:
  - REALUSE-DATA-SAFETY-6
base_commit: d3bcf9f94
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/REALUSE-DATA-SAFETY-7
allowed_paths:
  - doc/tasks/REALUSE-DATA-SAFETY-7.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/handoffs/REALUSE-DATA-SAFETY-7-handoff.md
  - doc/reviews/REALUSE-DATA-SAFETY-7-*.md
  - apps/desktop-avalonia/src/**
  - apps/desktop-avalonia/tests/**
  - verification/REALUSE-DATA-SAFETY-7/**
  - .gitattributes
---

# REALUSE-DATA-SAFETY-7：SAFETY-6 Review 的 3 条 P2

## 来源

[REALUSE-DATA-SAFETY-6 独立 Review](../reviews/REALUSE-DATA-SAFETY-6-review.md)（`approved`，P0/P1=0，P2×3 open）在集成后保留的 3 条 P2。本 Task 承接，不重复 SAFETY-6 的范围。

## 逐条说明

1. **R-001（并发 NRE）**：关闭阅读浮层与在途保存并发时，镜像回调在 `ReaderOverlayViewModel.cs:377-379` 解引用已置 null 的 `_book`，抛未捕获 NRE，且关闭时权威重读被跳过。Reviewer 已在仓外副本用 gate 门控用例真实复现（NRE 堆栈 `:377 ← GoToAsync :308`，EXIT 1）。属实现引入的并发缺陷；Core 已提交的保存不受影响，无数据丢失。
2. **R-002（证据 pin 漂移）**：SAFETY-6 的 11 条 Canonical Evidence pin 以 CRLF 工作树字节为基准，worktree 一致 10/11、blob 一致 6/11；`E-GOV-CHECK` pin 与当前字节不符。
3. **R-003（日志格式）**：`ac1-progress-refresh-test-log.txt` 缺 EXIT 码与完整命令，负向对照为散文摘要（Q-009 口径）。

## 验收标准

- [ ] **AC1 R-001 修复**：等待保存前局部固化 book/chapter/page 值，不再解引用可能为 null 的字段；`CloseAsync` 在 `_isSaving` 时仍保证一次权威重读；新增并发用例（关闭 + 在途保存）证明不再 NRE 且刷新发生。 <<PARTIAL: 待实现>>
- [ ] **AC2 R-002 规范化**：为 `verification/**` 增加 `.gitattributes` eol 规则（或等价手段），使 pin 基准稳定；重算 SAFETY-6 的 11 条 pin 并在任务卡登记 new/old 对照。 <<PARTIAL: 待实现>>
- [ ] **AC3 R-003 日志格式**：测试日志含完整命令、EXIT 码与时间戳；负向对照给出可复现步骤而非散文。 <<PARTIAL: 待实现>>

## 禁止范围

- 不改冻结契约；不动用户数据；不 push 远端；不重写 SAFETY-6 的历史证据字节（只允许在 SAFETY-7 的 evidence 中登记对照）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | `dotnet test --filter FullyQualifiedName~LibraryProgressRefreshTests`（含新增并发用例） | net9.0 | NOT_RUN | 待补 |
| AC1 负向 | 无修复时并发用例失败（对照） | net9.0 | NOT_RUN | 待补 |
| AC2 | `Get-FileHash` 对照 11 条 pin | 只读 | NOT_RUN | 待补 |
| AC3 | 日志含 EXIT/命令/时间戳 | 只读 | NOT_RUN | 待补 |

## Canonical Evidence

进入独立审查前逐项填写（当前为空）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

本 Task 尚未开 worktree；资源处置在实现完成后登记。

## Closeout Record

- Closeout date / DSH：待关闭时填写。
