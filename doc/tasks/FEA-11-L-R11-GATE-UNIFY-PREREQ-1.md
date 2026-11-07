---
id: FEA-11-L-R11-GATE-UNIFY-PREREQ-1
title: C-16 v1.7：§2.4「无 publication 行」口径澄清（legacy open / 新同步链缺行 fail-closed）
kind: contract
governance_version: 3
status: ready
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH，无需用户介入」；独立 scope review `doc/reviews/L-R11-GATE-UNIFY-scope-r1.md`（fresh subagent session `5aa2c0cf…`；verdict **recommended**；方案 C：Core 单谓词 + 全链检测；**1/18 pin UNFREEZE**）；**DSH 裁决（2026-11-07）**：采纳 recommended，UNFREEZE 仅改 C-16 §2.4 `:90` 括注与 `:93` 过期陈述（同一 pin）；C-17 §3.3 `:171-173` 已冻结 fail-closed **零字节**；其余 17 pins 零改动；先契约后实现
suggested_owner: dsh
owner: dsh
reviewer: 独立上下文 fresh subagent（byte-level；不得参与本 UNFREEZE 起草；session 见 `doc/reviews/FEA-11-L-R11-GATE-UNIFY-PREREQ-1-r1.md`）
depends_on:
  - FEA-11-RENDITION-1
base_commit: 07a7d746a
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-L-R11-GATE-UNIFY-PREREQ-1
allowed_paths:
  - doc/tasks/FEA-11-L-R11-GATE-UNIFY-PREREQ-1.md
  - doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16-L-R11.md
  - doc/reviews/FEA-11-L-R11-GATE-UNIFY-PREREQ-1-*.md
  - doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md
  - doc/plan/FEA-CONTRACT-FROZEN-C16.md
  - doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md
  - verification/FEA-11-L-R11-GATE-UNIFY-PREREQ-1/**
out_of_scope:
  - 其它 17 份冻结契约字节（C-17/C-06/C-15/C-07/M2-C1 等零 diff）
  - wire 字段/命令集/能力/错误码/TTL/撤销语义/`PROTOCOL_MINOR=3`；schema/迁移/依赖
  - `src/**`、`apps/**`、`tests/**`（实现由 `FEA-11-L-R11-GATE-UNIFY-1` 负责）
  - L-R11 实现、`added` relation 缺行检测（plan receipt）、写面/章级面 gate 扩展
  - STATUS/PLAN/LEDGER（Lead 维护）；push（Lead 统一）
---

# FEA-11-L-R11-GATE-UNIFY-PREREQ-1：C-16 v1.7（§2.4 无 publication 行口径澄清）

> **状态：`ready`（DSH 已裁决 UNFREEZE 路径；本卡改 C-16 §2.4 两处行文（`:90` 口径 + `:93` 陈述）+ §0 版本面行
> + 头部状态/日期 + §10 条件 ⑨/变更记录（后三类为记录性），冻结记录/矩阵/载体，1/18 pin）。**
> `base_commit=07a7d746a`（本卡创建/释放时 HEAD；scope review 快照为 `3945e1f5c`）。
> 依据：`doc/reviews/L-R11-GATE-UNIFY-scope-r1.md`（独立 scope review，recommended）+ C-17 §3.3
> （`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md:171-173`，已冻结「新同步 binding 缺 publication 行属于损坏，
> fail-closed，不能当作 legacy 放行」）+ RENDITION-1 L-R11（`doc/tasks/FEA-11-RENDITION-1.md:159`）。

## 目标

消除 **C-16 §2.4 规范句与 C-17 §3.3 的字面冲突**：C-16 `:90` 现写「无 publication 行按既有 open 处理」，
而 C-17 §3.3 要求「新同步 binding 缺行 fail-closed」。本卡把 `:90` 括注改为：

> 「沿用 Run 目标/commit guard 的**同一** gate 谓词，C-17 §3.3；**旧未参与同步且无 publication 行的 v7 binding
> 按既有 open 处理；新同步 binding 缺 publication 行属于损坏，fail-closed（C-17 §3.3），不得当作 legacy 放行**」

并同步修正 `:93` 的过期陈述（「publication gate 的两读面既有差异（L-R11）不属于本命令语义」→ 由 L-R11
统一；仍不引入第三套 gate 判定）。**不改任何 wire 字段/命令集/能力/错误闭集/TTL/撤销语义/`PROTOCOL_MINOR`/schema。**

## 范围（In / Out）

- **In**：`doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md`（v1.6 → **v1.7**：§2.4 `:90` 括注 + `:93` 陈述 +
  §0 版本面行 + 头部状态/日期 + §10 条件 ⑨/变更记录）；
  `doc/plan/FEA-CONTRACT-FROZEN-C16.md`（版本/pin/§1B/§11 记录）；`doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`（C-16 行）；
  载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16-L-R11.md`；本卡/评审/证据。
- **Out**：其余 17 pins（C-17 §3.3 **零字节**——它已冻结正确语义）；`src/**`、`apps/**`、`tests/**`；实现
  （`added` relation 缺行检测需 plan receipt 或新持久标记，本卡不碰）；写面/章级面；STATUS/PLAN/LEDGER；push。

## Acceptance Criteria

- [ ] **AC-T1 载体与最小 diff**：C-16 v1.7 仅改 `:90` 括注与 `:93` 陈述；载体逐项落盘（改前/改后字节、理由、复核记录）；C-16 新 sha256 与 pin 一致。 <<PENDING>>
- [ ] **AC-T2 独立 byte-level 复核**：fresh subagent（独立上下文、未参与起草）对 C-16 v1.7 变更做 byte-level 复核并 `approved`（P0/P1=0）；报告入库。 <<PENDING>>
- [ ] **AC-T3 pins 18/18**：`verify_pins.ps1` **18/18 PASS**（C-16 新值，其余 **17 项 UNCHANGED** 实测）；`check.ps1`（默认 + `-TaskPath`）PASS。 <<PENDING>>
- [ ] **AC-T4 零漂移**：C-17/C-06/C-15/C-07/M2-C1 及其余契约 blob 零 diff；`src/**`、`apps/**`、`tests/**`、schema/迁移/依赖零 diff；无新错误码/命令/能力/`PROTOCOL_MINOR`。 <<PENDING>>
- [ ] **AC-T5 证据与不夸大**：EV（实跑数字）、Resource Manifest、卡面 closeout 完整；**不得**宣称实现已完成/`L-R11` 已关闭/C-17 §3.3 已满足（本卡只是让契约文本与 C-17 一致）。 <<PENDING>>

## 依赖与下一步

- 依赖：`FEA-11-RENDITION-1`（done，L-R11 登记来源）。
- 完成后：释放 `FEA-11-L-R11-GATE-UNIFY-1`（Core 单谓词实现，0 pin；depends_on 本卡 + `FEA-11-RUN-GRANT-2C`）。
- 预登记 limitation（实现卡承担，本卡仅登记）：`L-R11-a`（`relation='added'` 缺行链检测不可见 → plan receipt 未实现）、
  `L-R11-b`（写面/章级面仍 pending-only）、`L-R11-c`（映射既有错误 family，无专用码）、`L-R11-d`（不自动修复损坏行）、
  `L-R11-e`（优先真实 v7→v8 fixture）。
