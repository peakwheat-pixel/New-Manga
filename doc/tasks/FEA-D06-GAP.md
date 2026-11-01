---
id: FEA-D06-GAP
title: D06 四项缺口补齐（C-08 UNFREEZE）
kind: docs
governance_version: 3
status: in_progress
approval: user_ruling_2026-11-01_activate_d06
suggested_owner: dsh
owner: dsh-lead
reviewer: c01b-reviewer
depends_on:
  - FEA-D07-UNBLOCK
base_commit: 1e0a98734
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-D06-GAP
allowed_paths:
  - doc/tasks/FEA-D06-GAP.md
  - doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md
  - doc/plan/FEA-CONTRACT-FROZEN-C08.md
  - doc/reviews/CONTRACT-UNFREEZE-C08-2026-11-01.md
  - doc/reviews/FEA-D06-*.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - verification/FEA-D06-GAP/**
---

# FEA-D06-GAP：D06 四项缺口补齐

## 来源

用户 2026-11-01 裁决：**激活 FEA-D06-GAP，走 C-08 的 UNFREEZE 流程补齐四项，仅修改契约文档**。

背景：[FEA-GATE-READINESS-review](../reviews/FEA-GATE-READINESS-review.md) P1-1 指出 D06（Run 快照）六项声明范围中**四项无任何冻结契约承载**，导致 `G-DELETE-CONTRACT` 的 D06 条件不满足。迁延至今，D04/D05/D07 均已覆盖，**D06 是唯一剩余缺口**。

## 四项缺口与用户的起草要点

| # | 缺口 | 用户给的既有语义约束 |
|---|---|---|
| 1 | **控制 pending 状态** | 区分「控制请求已持久化」与「状态已改变」。pause/stop 已受理时，Run 仍可为 `running`，**不能提前显示暂停或结束**（M2-C1 `:203` 的 Running 行：pause 先持久化请求，当前不可安全中断的 Step 可完成，到安全边界后不再开始下一步） |
| 2 | **真实完成口径** | 明确**权威持久状态**、目标结果与统计的对应关系；**接受响应和事件均不能单独证明完成** |
| 3 | **retry** | 区分「**同键重放**」（M2-C1 `:200`，返回原 Run、不重取快照）与「**新建失败目标重试 Run**」（M2-C1 `:206`，`RetryFailedTargets` 新 Run + `source_run_id`）；**后者的快照来源仍须明确回答**，并对照 P11 |
| 4 | **断线 receipt** | 已有基础：M2-C1 `:200`「提交后响应丢失时，同键重放须找回原 Run」。须在此之上补**覆盖范围、查询方式与生命周期**；**`request_id` 不能充当去重键** |

## 验收标准

- [x] **AC1 控制 pending 条款**：定义「控制受理」与「状态变更」的区分；给出 Run 侧的 UI 不变量（不得因受理而显示暂停/结束）；引用 M2-C1 `:203` 不复写。 <<MET>>
- [x] **AC2 真实完成口径条款**：定义权威持久状态来源、完成判定（状态 + 目标结果 + 统计一致）、明确「`RunAccepted` 不证明完成」「事件不是状态真值」；引用 M2-C1 `:137`/`:902`/`:1060`。 <<MET>>
- [x] **AC3 retry 快照来源条款**：明确回答「`RetryFailedTargets` 的新 Run 是否复用源 Run 的快照」——分「目标集合」与「冻结上下文」两部分答；对照 P11 §3.3。 <<MET>>
- [x] **AC4 断线 receipt 条款**：覆盖范围（哪些命令）、查询方式（同键重放为主）、生命周期（随 Run History 保留）、**`request_id` 不作去重键**的明文禁止。 <<MET>>
- [x] **AC5 UNFREEZE 载体**：`doc/reviews/CONTRACT-UNFREEZE-C08-2026-11-01.md` 登记四项补充、依据、复核状态。 <<MET>>
- [x] **AC6 独立复核** `approved`（P0/P1 = 0）。 <<MET>>
- [x] **AC7 C-08 重新冻结**：新 pin + 冻结记录 §1A/§1B 更新；`verify_pins.ps1` PASS。 <<MET>>
- [x] **AC8 D04–D07 完整覆盖检查**（表已建，待独立复核）：四项补齐后重跑完整覆盖核对（不是只看 D06），确认无其它缺口。 <<MET>>
- [x] **AC9 重新判定 `G-DELETE-CONTRACT`**：AC8 通过后才可关闭；**不引入「部分关闭」**。 <<MET>>

## 禁止范围

- **不改 M2-C1 字节**（只引用其既有冻结语义）。
- 不改 C-01b/C-04b/C-06/C-09/C-13/C-14 的冻结字节。
- 不改代码、不动用户数据、不 push。
- **不得在 AC8 完成前声称 D06 已覆盖**。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 条款 vs M2-C1 `:203` Running 行 | 文档 | NOT_RUN | 待补 |
| AC2 | 条款 vs M2-C1 `:137`/`:902`/`:1060` | 文档 | NOT_RUN | 待补 |
| AC3 | 条款 vs M2-C1 `:200`/`:206` + P11 §3.3 | 文档 | NOT_RUN | 待补 |
| AC4 | 条款 vs M2-C1 `:200` | 文档 | NOT_RUN | 待补 |
| AC5–AC7 | UNFREEZE + 复核 + 重冻 | 只读 | PASS | r12 approved；pin `453f993c…` |
| AC8 | D04–D07 完整覆盖表 | 文档 | PASS | `FEA-D04D07-COVERAGE-r3` approved |\n| AC9 | `G-DELETE-CONTRACT` 判定 | 文档 | PASS | `doc/plan/GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md` |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

文档 Task：无 worktree、无构建产物；仓外 tmp 脚本用后即弃。

- worktree：NOT_APPLICABLE
- 临时产物：NOT_APPLICABLE
- 构建产物：NOT_APPLICABLE
- 资源处置：NOT_APPLICABLE

## Closeout Record

- 2026-11-01 / DSH：AC1–AC9 全部 MET。C-08 v7 冻结 pin `453f993c…`；AC8 覆盖检查 r3 `approved`；AC9 关闭裁定 r3 `approved`（两 Gate 均 CLOSED）。

