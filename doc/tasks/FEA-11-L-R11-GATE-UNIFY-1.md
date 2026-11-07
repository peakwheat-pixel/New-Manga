---
id: FEA-11-L-R11-GATE-UNIFY-1
title: L-R11 两读面 publication gate 统一（Core 单谓词；legacy open / 新同步链缺行 fail-closed；全链检测）
kind: implementation
governance_version: 3
status: proposed
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH，无需用户介入」；独立 scope review `doc/reviews/L-R11-GATE-UNIFY-scope-r1.md`（session `5aa2c0cf…`；recommended；方案 C 单谓词 + 全链）；**DSH 裁决（2026-11-07）**：先 `FEA-11-L-R11-GATE-UNIFY-PREREQ-1`（C-16 v1.7，1 pin）→ 本卡（Core-only，0 pin）；`added` relation 缺行检测与写面/章级面 **Out**（登记 limitation）
suggested_owner: zcode
owner: null
reviewer: null
depends_on:
  - FEA-11-RENDITION-1
  - FEA-11-RUN-GRANT-2C
  - FEA-11-L-R11-GATE-UNIFY-PREREQ-1
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-L-R11-GATE-UNIFY-1
allowed_paths:
  - doc/tasks/FEA-11-L-R11-GATE-UNIFY-1.md
  - doc/reviews/FEA-11-L-R11-GATE-UNIFY-1-*.md
  - doc/handoffs/FEA-11-L-R11-GATE-UNIFY-1-*.md
  - verification/FEA-11-L-R11-GATE-UNIFY-1/**
  - src/infrastructure/sqlite/source_sync.py
  - src/bootstrap/core_assembly.py
  - src/bootstrap/core_service.py
  - tests/fea11/test_source_gate_unify.py
out_of_scope:
  - 契约字节（PREREQ 卡负责；实现期 18 pins 零改动）
  - schema/迁移（`schema.py` 零 diff）、wire/命令/能力/错误码/`PROTOCOL_MINOR`、依赖
  - `apps/**`、App/UI、Host 接线、Run wire
  - RENDITION-1 的 provider/选择语义；`managed_original_ref` 混合页取舍（L-R5）
  - 写面 `_refuse_pending_gate_writes` / 章级 `_refuse_pending_gate_chapter` 的 pending-only 语义（L-R11-b）
  - `relation='added'` 缺行检测（plan receipt / 新持久标记；L-R11-a）
  - 损坏 publication 行的自动修复/重建（L-R11-d）
  - C-04b/SCAN-RH/UI P3；STATUS/PLAN/LEDGER；push
---

# FEA-11-L-R11-GATE-UNIFY-1：L-R11 两读面 publication gate 统一（Core-only）

> **状态：`proposed`（未释放；依赖 PREREQ `FEA-11-L-R11-GATE-UNIFY-PREREQ-1`（C-16 v1.7）与 2C closeout；DSH 冻结后释放）。**
> 依据：`doc/reviews/L-R11-GATE-UNIFY-scope-r1.md`（recommended；已复现 L-R11 一跳形态、发现两跳链两面均放行、
> `added` 缺行不可检测）+ C-17 §3.3（`:171-173`）+ C-16 §2.4（PREREQ 澄清后）。

## 目标

统一 Core 内 publication gate 判定为**唯一谓词**：healthy + 行状态 + **全链**检测；**旧 v7 legacy 无行 open**；
**新同步链缺 publication 行 fail-closed**；由 `core_assembly.read_gate`、`core_service._assert_source_sync_gate` 与
`AuthorizeSourceReadForRun` 的 per-page 路径共同消费。修复 L-R11 一跳分歧与 scope review 新发现的**两跳链**
（B3/B2 无行、B1 有行时两面均放行，违反 C-17 §3.3 全链 fail-closed）。

## 候选范围

- **In**：`src/infrastructure/sqlite/source_sync.py`（或 `SourceSyncLineageFacts` 所在模块）实现单谓词（返回
  `open`/`pending`/`unavailable`/`corrupt_chain`，组装层把 `corrupt_chain` 映射既有 `unavailable`）；`core_assembly.read_gate`
  委托；`core_service._assert_source_sync_gate` 委托；`AuthorizeSourceReadForRun` per-page 经 `catalog.source_gate_reader`
  消费同一谓词；新增 `tests/fea11/test_source_gate_unify.py`（真实 v7→v8 migration fixture、真实 grant、真实
  assembly；含 legacy / 一跳 / 两跳 / pending/open 回归 + 判别性）。
- **Out**：见 frontmatter `out_of_scope`。

## Acceptance Criteria（草案，冻结时定稿）

- [ ] **AC-1 单谓词唯一**：Core 内只存在一处 publication-gate 判定；`read_gate`、`_assert_source_sync_gate`、
  `AuthorizeSourceReadForRun` per-page 都消费它；静态断言无第二份「一跳 previous」判定；`read_gate` docstring 过期
  「无行即 open」表述同步修正。判别性：复制判定或删委托 → 新用例红。 <<PENDING>>
- [ ] **AC-2 legacy 零回归**：真实 v7→v8 migration 库中，无 publication、previous NULL 的 healthy binding →
  `read_gate == "open"`；resolve/provider/target/commit/`AuthorizeSourceReadForRun` 行为与修复前一致（真实 grant 可读图）。
  判别性：把「无行即 corrupt」→ 红。 <<PENDING>>
- [ ] **AC-3 L-R11 一跳 fail-closed**：v8 库 B1（publication open）+ B2（healthy、无行、previous=B1）→ `read_gate` 拒绝；
  resolve `SOURCE_ACCESS_DENIED`；provider 在 read byte 前拒绝（0 次解码/0 次 read）；`create_run` `TARGET_NOT_FOUND`；
  commit guard 拒绝；`AuthorizeSourceReadForRun` 整请求 typed 拒绝且零映射。判别性：分支改回 open → 红。 <<PENDING>>
- [ ] **AC-4 全链检测（两跳）**：B3/B2 无行、B1 有行 → 同样 fail-closed。判别性：改回只查一跳 → 红。 <<PENDING>>
- [ ] **AC-5 零漂移**：18 pins 零改动（PREREQ 后 C-16 v1.7 与实现一致）；`schema.py`/`apps/**`/依赖零 diff；无新错误码/
  命令/能力/`PROTOCOL_MINOR`；`src/**` diff ⊆ `allowed_paths`。判别性：scope diff 检查。 <<PENDING>>
- [ ] **AC-6 门禁/证据/不夸大**：定向 pytest（新用例 + `tests/fea11` 全量基线 + `test_source_run_grant.py`/
  `test_source_resolve.py`/`test_source_rendition_*`）；全量 `pytest tests` 不降（卡面重测起点）；`check.ps1` PASS；
  `verify_pins.ps1` 18/18；API inventory PASS；scope diff；EV/Handoff 完整；卡面登记 `L-R11-a…e` limitation；
  **不得**写「C-17 §3.3 已完全实现 / L-R11 全部关闭」。 <<PENDING>>

## 预登记 limitation（实现时如实保留）

- **L-R11-a**：`relation='added'` 的新同步 binding 缺 publication 行（previous NULL）时，链检测不可见，无法与 v7
  legacy 区分；C-17 §3.3 的 plan receipt 检测未实现。本卡只覆盖 previous 链可检测的损坏子集。
- **L-R11-b**：写面与章级面仍 pending-only；损坏链形态下编辑/章级预检仍放行，直到逐页 resolve 拒绝。
- **L-R11-c**：损坏状态映射既有 `unavailable`/`TARGET_NOT_FOUND`/`INVALID_INPUT`/`SOURCE_ACCESS_DENIED`，无专用诊断码
  （C-17 §8 禁止新增码）。
- **L-R11-d**：不提供损坏 publication 行的自动修复/重建。
- **L-R11-e**：优先真实 `MigrationRunner(..., MIGRATIONS[:7])` 造 v7 再升级；若只用 v8 内 legacy 形态须在卡面写明。

## 依赖与下一步

- 依赖：`FEA-11-L-R11-GATE-UNIFY-PREREQ-1`（C-16 v1.7，done 后 DSH 冻结释放）；`FEA-11-RUN-GRANT-2C`（done，共享
  `tests/fea11/test_source_run_grant.py` 基线）。
- Release 后走实现 → 独立 Review → 集成门禁 → closeout → push。
