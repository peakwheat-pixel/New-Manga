---
id: FEA-C10-DRAFT
title: C-10 交互契约起草（手势优先级/移动阈值/快捷键作用域/可编辑态/需求追溯）
kind: contract
governance_version: 3
status: in_progress
approval: user_instruction_2026-11-01_autonomous_queue_C10_draft
suggested_owner: dsh
owner: dsh-lead
reviewer: c01b-reviewer
depends_on: []
base_commit: 500aa6b27
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-C10
allowed_paths:
  - doc/tasks/FEA-C10-DRAFT.md
  - doc/plan/FEA-C10_INTERACTION_DRAFT.md
  - doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md
  - doc/plan/FEA-01_CONTRACT_DRAFT.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/**
  - doc/reviews/FEA-C10-*.md
  - verification/FEA-C10/**
---

# FEA-C10-DRAFT：C-10 交互契约起草

## 来源

用户 2026-11-01 指令：起草 **C-10 交互契约**（契约线最后一份未起草的契约）。**前置**：U-03 = B 已裁（draft owner 模型，[ADJ-2026-11-01](../reviews/ADJ-2026-11-01-FEA-DECISIONS.md)）；C-13（编辑层保护/草稿）、C-08（Run 快照）、C-05（页可见性）均已冻结可引用。

声明范围（`doc/plan/FEA-01_CONTRACT_DRAFT.md:59`）：手势优先级与移动阈值、快捷键作用域、可编辑态、draft owner 规则；「需求→能力→Task→AC→证据」矩阵。R7-07 记「手势阈值 / 可编辑态仍缺」；方案 `:854` 明写「具体数值、状态表与冲突处理由 FEA-01 逐项冻结」。

**本 Task 的交付 = 草案 + 独立复核；冻结不在本 Task 范围**（冻结须用户裁定未定项，见草案 §10）。不实现、不改代码、不改任何已冻结契约字节。

## 验收标准

- [ ] **AC1 草案落盘**：`doc/plan/FEA-C10_INTERACTION_DRAFT.md` 覆盖 C-10 声明范围（手势优先级 / 移动阈值 / 快捷键作用域 / 可编辑态 / draft owner 引用 / 需求追溯矩阵 / 不覆盖面）；**每条条款都有可执行验证判据**；引用已冻结契约（C-05/C-13/C-08/C-02）**不复写**；无权威来源的具体数值显式标注为「待裁定」，不得声称已冻结。
- [ ] **AC2 独立复核**：`doc/reviews/FEA-C10-r1.md`（必要时 r2）判 `approved`（P0/P1 = 0）；findings 逐条处置。
- [ ] **AC3 冻结字节未动**：13 份受 pin 契约字节 0 改动；`verify_pins.ps1` 13/13 且 pin 值不变；**本 Task 不冻结 C-10**。

## 禁止范围

- **不冻结 C-10**（冻结留待用户在线裁定：阈值数值 + 条款终稿）。
- 不改任何已冻结契约字节（C-01b…C-14）；不改 M2-C1；不改 C-13 草案正文。
- 不实现、不改代码、不动用户数据、不 push、不释放实现 Task（`G-DELETE-IMPL` 仍 OPEN）。
- 不得声称覆盖了草案 §9 明确不覆盖的面向。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 逐条对照 C-10 声明范围与草案条款/判据 | 文档 | NOT_RUN | 待补 |
| AC1 | 检查草案是否复写已冻结契约（应只引用） | 文档 | NOT_RUN | 待补 |
| AC2 | 独立复核 | 只读 | NOT_RUN | 待补 |
| AC3 | 13 份 pin 契约前后对比 | 只读 | NOT_RUN | 待补 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

文档 Task：仓库内无 worktree、无 task-env、无构建产物；仓外一次性脚本与 2026-11-01 契约线共用同一批残留（`G:\CODEX\New Manga.workspace\tmp\`），逐项 sha256 见共享清单 `verification/FEA-D06-GAP/workspace-tmp-manifest.md`，处置 `PRESERVE_UNKNOWN`（不删除，保留冻结字节可复现性）。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| doc-task | - | NOT_APPLICABLE | - | - | 仓库内无 worktree/task-env/artifact/build/temp；未访问用户数据 |
| temp-scripts | ..\New Manga.workspace\tmp | PRESERVE_UNKNOWN | ..\New Manga.workspace\tmp | verification/FEA-D06-GAP/workspace-tmp-manifest.md | 共享清单 32 项；无进程占用、不在 git 跟踪内；delete/move/migrate/archive 均为 0 |

## Closeout Record

- 收口中（2026-11-01）：AC1 草案已落盘（v2，处置 R1 的 P1×3 + P2×7）；AC2 独立复核进行中；AC3 待冻结字节核验。
- **provenance 留痕（R1 P2-006）**：草案最初实际落盘于 `500aa6b27`（当时本卡尚未建立，`FEA-CONTRACT-WRAP-1` 的 `allowed_paths` 未含 `doc/plan/FEA-C10_INTERACTION_DRAFT.md`）；本卡建立时（`f9420a750`）已把该路径纳入 `allowed_paths`，未留下未登记的权威面。后续「起草先于建卡」应避免。
