---
id: FEA-GOV-11
title: 冻结执行待命（等待用户 4 项裁决）
kind: governance
governance_version: 3
status: done
approval: follow_up_of_FEA-GOV-10_2026-11-01
suggested_owner: dsh
owner: dsh-lead
reviewer: 独立上下文 Review：`doc/reviews/FEA-DOC-RECONCILE-1-r1.md`、`-review.md`、`-r2.md`、`-r3.md`（均非本会话自审；r2/r3 为 approved）
depends_on:
  - FEA-GOV-10
base_commit: f9eb0f859
branch: null
worktree: null
integration_commit: c22aea60c
delivery_head: c22aea60c
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-GOV-11
allowed_paths:
  - doc/tasks/FEA-GOV-11.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/plan/FEA-CONTRACT-FROZEN-*.md
  - verification/FEA-GOV-11/**
---

# FEA-GOV-11：冻结执行待命（等待用户 4 项裁决）

## 来源

FEA-GOV-10 完成：**11 份已起草契约全部 `approved`**（C-01b/C-02/C-03/C-04b/C-05/C-06/C-07/C-08/C-09/C-11/C-12），冻结矩阵 `approved`。本 Task 是**待命状态**：等用户回 4 项裁决后，DSH 按冻结矩阵 §2 的 8 步执行。

## 待用户裁决（阻塞本 Task 的唯一输入）

1. **`R`** —— AD-002 责任表/哨兵口径（C-01b 冻结前置③）
2. **U-04** —— Fluent 视觉 per-scheme 例外（C-02 V-05）
3. **U-05a** —— 外观持久化纳动效三态/三类（C-03）
4. **U-05b** —— （C-03 附带项，见晨报）

裁决后 DSH 动作：按 [FEA-CONTRACT_FREEZE_MATRIX](../plan/FEA-CONTRACT_FREEZE_MATRIX.md) §2 执行 C-01b → C-05/C-12 → C-02 → C-03/C-11 → … 每步产出 `doc/plan/FEA-CONTRACT-FROZEN-<ID>.md`。

## 验收标准

- [x] **AC1 冻结 C-01b**：用户回 `R` 后，C-01b 冻结记录落盘（4 条条件逐条勾选）。 <<MET>>
- [x] **AC2 冻结 C-02/C-03/C-11**：U-04/U-05a/U-05b 裁决后冻结。 <<MET>>
- [x] **AC3 释放第一个实现候选**：按 C-11 §7 选候选 → 建卡 → 派独立 Review。**7 份契约已冻结，C-11 已可用**；候选选择待 DSH 提名 + 用户确认（FEA-01/FEA-04b 涉及产品取舍）。 <<MET>>

## 禁止范围

- 未裁决前不冻结、不释放实现 Task、不改契约字节、不 push。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 冻结 + `check.ps1` | 用户裁决 | NOT_RUN | 待补 |
| AC2 | 同上 | 用户裁决 | NOT_RUN | 待补 |
| AC3 | 建卡 + Review | 冻结完成 | NOT_RUN | 待补 |

## Canonical Evidence

进入收口前逐项填写（当前为空）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-GOV11-ADJ | AC1,AC2 | `doc/reviews/ADJ-2026-11-01-FEA-DECISIONS.md` | `-` | `d7e02d5970430c180f564103dc761a1af20f7559b5ab6576a4c8be5abc3675d7` | CANONICAL |
| EV-GOV11-C01B | AC1 | `doc/plan/FEA-CONTRACT-FROZEN-C01b.md` | `-` | `6623a6ac299192b4ff73aa4a2aedf99dac1ef8d3b5aeaa9956f02f32e971615b` | CANONICAL |
| EV-GOV11-C02 | AC2 | `doc/plan/FEA-CONTRACT-FROZEN-C02.md` | `-` | `ffe2585df9475e60dcd0e10e903937cca099d5b46c9f4cd7d57916b8153cb552` | CANONICAL |
| EV-GOV11-C03 | AC2 | `doc/plan/FEA-CONTRACT-FROZEN-C03.md` | `-` | `2927dca3f9dd68cb8edfaf3f65e77cf2b6ff11aa6fcac239733982a6fa4acbf7` | CANONICAL |
| EV-GOV11-C11 | AC2,AC3 | `doc/plan/FEA-CONTRACT-FROZEN-C11.md` | `-` | `beff813bcbe9b8ecbd5aaf268403dd07f2bf6499793515c8e9a37799bb617b5a` | CANONICAL |
| EV-GOV11-IMPL | AC3 | `doc/tasks/FEA-02-CORE.md` | `-` | `78d8a4881e4b6639fdbf8826e25a4c088eb005559b72daf971bfbcb73947cd94` | CANONICAL |

## Resource Manifest

治理 Task：无 worktree、无临时产物；资源处置在收口时登记。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| doc-only | — | NOT_APPLICABLE | — | — | 本卡只改仓库内文档/代码，未创建仓外 worktree、task-env、临时目录或用户数据；2026-11-17 补登表格 |
## Closeout Record

- Closeout date / DSH：待关闭时填写。
- **2026-11-09 / DSH（FEA-DOC-RECONCILE-1 对账关闭）**：4 项待裁决输入已全部由 [ADJ-2026-11-01](../reviews/ADJ-2026-11-01-FEA-DECISIONS.md) 裁决并落盘——`R` = C1=D 零字节 / C3=是；U-04 = 批准（per-scheme + 令牌强制）；U-05a = 纳入（三态三类）；U-05b = 保留（转只读）。C-01b / C-02 / C-03 / C-11 冻结记录均已产出：`doc/plan/FEA-CONTRACT-FROZEN-C01b.md:38`、`FEA-CONTRACT-FROZEN-C02.md:34`、`FEA-CONTRACT-FROZEN-C03.md:35`、`FEA-CONTRACT-FROZEN-C11.md`。AC3 已由 `FEA-01-FREEZE-1`（集成 `bf1c8eb00`）及其后续实现线（FEA-02…FEA-12 done）实际完成。测试表 `NOT_RUN` 为 2026-11-01 当时记录，原字节保留；本轮不改写历史字节。状态 `done` 依据：AC1–AC3 均 MET，且冻结矩阵 §2 的 8 步已由各冻结记录与实现线取代执行。
- **证据更正（2026-11-09，Review REC-08）**：AC3「首个实现候选」的主证据应为 **`FEA-02-CORE`**（独立 Review + 集成 `135479270`，按 [ADJ-2026-11-01](../reviews/ADJ-2026-11-01-FEA-DECISIONS.md) U-12）；`FEA-01-FREEZE-1`（`bf1c8eb00`）是冻结链末环/前置，不是实现候选。以上为本轮新增更正，不改写前句字节。


