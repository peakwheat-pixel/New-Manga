---
id: FEA-C10-DRAFT
title: C-10 交互契约起草（手势优先级/移动阈值/快捷键作用域/可编辑态/需求追溯）
kind: contract
governance_version: 3
status: approved
approval: user_instruction_2026-11-01_autonomous_queue_C10_draft
suggested_owner: dsh
owner: dsh-lead
reviewer: c01b-reviewer
depends_on: []
base_commit: 500aa6b27
branch: null
worktree: null
integration_commit: null
delivery_head: b45658c17
canonical_evidence_status: complete
resource_closeout_status: complete
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

- [x] **AC1 草案落盘**：`doc/plan/FEA-C10_INTERACTION_DRAFT.md` 覆盖 C-10 声明范围（手势优先级 / 移动阈值 / 快捷键作用域 / 可编辑态 / draft owner 引用 / 需求追溯矩阵 / 范围边界）；**每条条款都有可执行验证判据**；引用已冻结契约（C-05/C-13/C-08/C-02）**不复写**；无权威来源的具体数值显式标注为「待裁定」，不得声称已冻结。 <<MET>>
- [x] **AC2 独立复核**：r1 `changes_requested`（P1×3 / P2×7）→ r2 `approved`（P0/P1 = 0；P2×5）→ v3 → r3 `approved`（P0/P1 = 0）；findings 逐条处置。 <<MET>>
- [x] **AC3 冻结字节未动**：13 份受 pin 契约字节 0 改动；`verify_pins.ps1` 13/13 且 pin 值不变；**本 Task 不冻结 C-10**。 <<MET>>

## 禁止范围

- **不冻结 C-10**（冻结留待用户在线裁定：阈值数值 + 条款终稿）。
- 不改任何已冻结契约字节（C-01b…C-14）；不改 M2-C1；不改 C-13 草案正文。
- 不实现、不改代码、不动用户数据、不 push、不释放实现 Task（`G-DELETE-IMPL` 仍 OPEN）。
- 不得声称覆盖了草案 §9 明确排除的面向。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 逐条对照 C-10 声明范围与草案条款/判据 | 文档 | PASS | 草案 §1 覆盖矩阵 + §3–§8 判据表；r2/r3 复核逐条确认 |
| AC1 | 检查草案是否复写已冻结契约（应只引用） | 文档 | PASS | §7 为纯指针（r2 逐句比对 C-13 `:59-62` 零复述）；C-05/C-13 SC-D02/D04/D09/C-02 均引用不复写 |
| AC2 | 独立复核（r1→r2→r3） | 只读 | PASS | `doc/reviews/FEA-C10-r2.md`（approved，0/0）、`FEA-C10-r3.md`（approved，0/0） |
| AC3 | 13 份 pin 契约前后对比 | 只读 | PASS | `verify_pins.ps1` 13/13；`git diff` 的 `doc/plan/` 受 pin 文件 0 改动 |

> 说明：草案 §§10 的冻结条件（用户裁定阈值 `T` 等）**不在本 Task 范围**；`T` 数值未定为**有意待裁决**，不因此扣 AC。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| E-C10-DRAFT | AC1 | `doc/plan/FEA-C10_INTERACTION_DRAFT.md` | `b45658c17` | `5bcb40f5c47b44ac976c6dc8325003e1cb4fc18061f42a226353880a93652d7f` | CANONICAL |
| E-C10-R2 | AC2 | `doc/reviews/FEA-C10-r2.md` | `b45658c17` | `9bb27a0cb01c315a39ec2834234cb1109563a4cbda8cb20ac91c9c19f11891b6` | CANONICAL |
| E-C10-R3 | AC2,AC3 | `doc/reviews/FEA-C10-r3.md` | `-` | `5d64431f96aab9ade3fb637af49d1aef42eae07b96356b94add7f3cbd1dabef3` | CANONICAL |
| E-RES-C10 | Res/Closeout | `verification/FEA-C10/closeout-note.md` | `-` | `c7c784b97d8d465f9a11bc93f3a5fa8a926aef4240d8ba66b9a8c5abc99839c7` | CANONICAL |

## Resource Manifest

文档 Task：仓库内无 worktree、无 task-env、无构建产物；仓外一次性脚本与 2026-11-01 契约线共用同一批残留（`G:\CODEX\New Manga.workspace\tmp\`），逐项 sha256 见共享清单 `verification/FEA-D06-GAP/workspace-tmp-manifest.md`，处置 `PRESERVE_UNKNOWN`（不删除，保留冻结字节可复现性）。

**偏离登记**：用户口头要求「Resource Manifest 用纯文本、不建表」；但 `check.ps1` 对 `done` Task 只接受非空 6 列表或 `verification/**` 单个 JSON，「纯文本无表」不可满足。故保留纯文本说明 + 真实表格（不虚构路径/哈希）。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| doc-task | - | NOT_APPLICABLE | - | - | 仓库内无 worktree/task-env/artifact/build/temp；未访问用户数据 |
| temp-scripts | ..\New Manga.workspace\tmp | PRESERVE_UNKNOWN | ..\New Manga.workspace\tmp | verification/FEA-D06-GAP/workspace-tmp-manifest.md | 共享清单 32 项；无进程占用、不在 git 跟踪内；delete/move/migrate/archive 均为 0 |

## Closeout Record

- 2026-11-01 / DSH：**C-10 草案 v3 完成**（`doc/plan/FEA-C10_INTERACTION_DRAFT.md`）。复核链：r1 `changes_requested`（P1×3 / P2×7）→ v2 → r2 `approved`（P2×5）→ v3 → r3 `approved`（P2×2）。AC1–AC3 全 MET。
- 状态：`status: approved`（非终态）；`integration_commit` **留空**——C-10 **未冻结、未集成**，冻结须用户裁定草案 §10 第 1 项（阈值 `T` 数值）+ 条款终稿，再走冻结记录 + pin。本 Task **不构成冻结**。
- 已知非阻断瑕疵：r3 的 **R3-001**（§8 表末与 `## 9.` 之间缺一个空行；GFM 渲染无碍）——按现字节记录为已知格式瑕疵；R3-002（closeout-note 版本滞后）已在本提交修正为 v3 + r3。
- **provenance 留痕（r1 P2-006）**：草案最初实际落盘于 `500aa6b27`（当时本卡尚未建立，`FEA-CONTRACT-WRAP-1` 的 `allowed_paths` 未含该路径）；本卡建立时（`f9420a750`）已把该路径纳入 `allowed_paths`，未留下未登记的权威面。后续「起草先于建卡」应避免。
- 证据口径：E-C10-DRAFT / E-C10-R2 为 commit 型（blob 与 worktree 同 hash）；E-C10-R3 / E-RES-C10 为 `-` commit + worktree sha256（评审报告在提交时一并入库，按 §4.1「或 SHA-256」分支合法）。
- 资源：仓库内无资源；仓库外 0 新增（共用共享清单）；未访问用户数据。
- 边界：不构成冻结；不构成实现授权；不构成远端 push 授权；不改变任何冻结契约字节（13/13）。
