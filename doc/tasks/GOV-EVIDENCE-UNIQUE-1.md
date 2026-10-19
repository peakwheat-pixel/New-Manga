---
id: GOV-EVIDENCE-UNIQUE-1
title: AC 证据覆盖核验（原「AC7 唯一最终证据判定」，按 r18 修订）
kind: governance
governance_version: 2
status: in_review
approval: codex_r14_scope_draft; dsh_release_2026-10-20_after_GOV-DEBT-CLEANUP-2_closeout
suggested_owner: dsh
owner: dsh
reviewer: Antigravity
depends_on: [GOV-DEBT-CLEANUP-2]
base_commit: 6ee8c87b1
branch: null（只读盘点，主线直接执行）
worktree: null（只读，不建 linked worktree）
integration_commit: null
delivery_head: 3b62f7937
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-EVIDENCE-UNIQUE-1
allowed_paths:
  - doc/tasks/GOV-EVIDENCE-UNIQUE-1.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/handoffs/
  - doc/reviews/
  - verification/GOV-EVIDENCE-UNIQUE-1/
---

# GOV-EVIDENCE-UNIQUE-1：AC 证据覆盖核验

> **目标已于 2026-10-20 按 Codex r18 授权修订。** 原名「AC7 唯一最终证据判定」。
>
> 修订理由（r18 §二原文意译）：证据可由日志、退出码、环境记录、交付说明等组成；
> 一次 AC 也可能依赖多个测试面，候选集还包含不同尝试。**唯一性不能推出充分性**，
> 单文件判定会把证据的组合结构压扁，也会把「没有一份文件独自证明 AC」误写成证据缺失。
>
> 本 Task 因此改为：**对每个已释放 AC，核实其证据**是否充分覆盖**，并指出缺口。**
> 允许一项 AC 对应多份互补证据，也允许一份证据支持多个 AC。

## 来源与目标

承接 `GOV-DEBT-CLEANUP-2` AC7 未完成部分。只读审查 `verification/GOV-DEBT-CLEANUP-2/ac7-evidence-dir-files.md` 列出的 61 个文件，并按原 AC/来源 Task 判断每项是否为某个已释放 AC 的唯一最终证据。不得因本 Task 而恢复或改写已关闭 Task 的状态、AC、Review、Canonical Evidence 或历史 pin。主证据入口：
- `doc/tasks/GOV-DEBT-CLEANUP-2.md` 与 `doc/reviews/GOV-DEBT-CLEANUP-2-94c8dcdab-antigravity-r2.md`
- `verification/GOV-DEBT-CLEANUP-2/ac7-evidence-dir-files.md`
- `doc/09_COLLABORATION.md` §4.1 / §4.2 / §5

## Acceptance Criteria

> 修订依据：Codex r18 §二。五条 AC 的边界由 r18 逐条给出，本节按其原文落实。

- [x] **AC1 — 61 项逐项记录**：对冻结的 61 项逐项记录路径、内容 Hash、存在性、内容类型、
  可能关联的来源 Task/AC、**在证据组中的作用**及限制；**不能按文件名推断证明力**。
- [x] **AC2 — 以 AC 为单位的覆盖核验**：以每个已释放 AC 为单位，核实其 Canonical Evidence
  与本次冻结候选的覆盖关系；允许一项 AC 对应多份互补证据，也允许一份证据支持多个 AC。
  分别标明证据集合及角色、是否充分、实际缺口和不确定性。
  **不得把「存在候选」当成「AC 已满足」。**
- [x] **AC3 — 只读保护**：不改来源 Task、Review、Canonical Evidence/pin、61 项源文件或生产文件；
  本 Task **不补登记来源 pin、不处置文件**。
- [x] **AC4 — 可复核交付与 Review**：入库逐项结果、来源 commit/hash、方法与未决项；
  按**AC 覆盖结果**报告，而不是要求每个 AC 恰有一份根证据；生成 Handoff；
  由 Antigravity 对固定 delivery head 独立 Review。
- [ ] **AC5 — 生命周期与 closeout**：完成 Task/Review/Plan/STATUS 生命周期、
  Canonical Evidence 与 Resource Manifest；更新 integration 字段并如实登记集成拓扑；
  运行治理检查。**任何 `BLOCKED`、`NOT_RUN`、`UNKNOWN` 均不得记为通过。**

## 结果枚举（r18 §二指定）

| 枚举 | 含义 |
|---|---|
| `COVERED` | 证据组充分支持 AC 达成 |
| `PARTIAL` | 有相关证据但 AC 要求未被完整覆盖 |
| `EVIDENCE_GAP` | 候选范围内没有相关证据 |
| `UNKNOWN` / `BLOCKED` | 材料缺失、不可访问或无法判断 |
| `NOT_RELEASED` | 来源 Task 非终态，AC 未释放 |
| `NOT_APPLICABLE` | 该 AC 不要求文件级证据（如纯过程性 AC） |

## 核验口径（r18 §二）

- 测试/构建的**多次尝试**应保留其时间和结果关系；报告**哪次是最终判定所依赖的结果**，
  以及失败尝试是否被后续有效运行取代。
- **命令、环境、日志、退出码**作为**一组关联材料**核验。
- 若 AC 明确要求「原始日志与退出码」，**只有日志而无可复核退出码**时应记为
  `PARTIAL` 或 `UNKNOWN`，**不能按文件数判为覆盖**。

## 允许修改范围

- `verification/GOV-EVIDENCE-UNIQUE-1/`：只读判定矩阵、复核记录、运行输出。
- 本 Task 自身文件、Handoff、Review 及 Codex 管理的 Plan/STATUS 指针元数据。

## 禁止事项

- 不改 `verification/GOV-DEBT-CLEANUP-2/`、任何来源 Task/Review/evidence、历史 pin、`.gitattributes`、`.gitignore`、`tools/`、`src/`、`tests/` 或其他生产路径。
- 不把建议 pin 写回来源 Task；不执行物理处置；不扫描并裁定与 61 项无关的未入库文件。
- 不把 `closed_with_limitations` 来源 Task 改成 `done`，不重开 AC，也不把 `UNKNOWN/BLOCKED/NOT_RUN` 写成 PASS。

## 测试与验证

本 Task 为只读证据判定，不运行产品测试。planned：对 61 行逐行核对、重算文件 hash、核查来源提交含文件、对照来源 Task 的 AC/pin，并运行 `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-EVIDENCE-UNIQUE-1.md` 与全局 checker。按命令、PowerShell 版本、结果、stdout/stderr、exit code 记录；不得把未跑项标为通过。

## Canonical Evidence

登记 AC1–AC5 判别力矩阵、Handoff、Review 和 checker 输出；每项记录仓库相对路径、含文件 commit、SHA-256、class。Review 必须绑定精确 `reviewed_head`。

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| EVID-AC1-FREEZE | AC1 | `verification/GOV-EVIDENCE-UNIQUE-1/ac1-input-freeze-and-criteria.md` | `c41a40a09` | `a339dd41c030d1af2ea3e1a52a550d85dbecd042ec8d29c9a56ffb636d3e7f5e` | `CANONICAL` |
| EVID-AC1 | AC1 | `verification/GOV-EVIDENCE-UNIQUE-1/ac1-matrix-v2.md` | `c41a40a09` | `2942b273afb820c7edc1cd85cf8856633263a32afd78d41e9aa299523abfbcfa` | `CANONICAL` |
| EVID-AC1-JSON | AC1 | `verification/GOV-EVIDENCE-UNIQUE-1/ac1-matrix-v2.json` | `c41a40a09` | `ac54944b703d0fccc37d4b17a90b260280ec664b5493e5b87e79de47dbdcee2f` | `CANONICAL` |
| EVID-AC2-MAP | AC2 | `verification/GOV-EVIDENCE-UNIQUE-1/ac2-ac-mapping-and-uniqueness.md` | `c41a40a09` | `09450278df57ad7b24e2da249a1bb7dd074e9e5581b7735d3f4761946b04df8f` | `CANONICAL` |
| EVID-AC2-B1 | AC2 | `verification/GOV-EVIDENCE-UNIQUE-1/ac2-coverage-batch1.md` | `c41a40a09` | `926e6675e6c99e48a4f9a0ddca3c1e6846048cf7f22d1425856367439b043059` | `CANONICAL` |
| EVID-AC2-B2 | AC2 | `verification/GOV-EVIDENCE-UNIQUE-1/ac2-coverage-batch2.md` | `c41a40a09` | `82c9523862aed6071e6e3bdeb8b979c3c50697811e6f9cfefff7fed9b5644241` | `CANONICAL` |
| EVID-AC2-B3 | AC2 | `verification/GOV-EVIDENCE-UNIQUE-1/ac2-coverage-batch3-and-summary.md` | `EF4AADFEE` | `81b2cdf78064c7de375a0734f5bfc0f148222e915fc7fca50a19793f3c45b2a6` | `CANONICAL` |
| EVID-AC3 | AC3 | `verification/GOV-EVIDENCE-UNIQUE-1/ac3-readonly-verification.md` | `c41a40a09` | `89d92ef4084d88cfd63ade5ea4f836719b00788b6b0bbb3313db77f87c7d581c` | `CANONICAL` |
| EVID-REVIEW | AC4 | `doc/reviews/GOV-EVIDENCE-UNIQUE-1-3b62f7937-antigravity-r1.md` | `c41a40a09` | `a9abc01e6514ddf786476dc369467a29afd787898a07de063f467781da7c83ed` | `CANONICAL` |

## Resource Manifest

冻结 ready 前登记实际 Task worktree 路径；task-env、dataset、artifact、temp、agent-output、exchange 逐项核实。不适用需有目录核实依据；未知、dirty、被引用或用户数据一律保留。

## 本次修订记录

- 修订日期：2026-10-20
- 授权来源：Codex r18 —— `verification/P09-GOVERNANCE-DEBT-20261019/codex-adjudicate-evidence-unique-r18.md`
- 修订前状态：`status: in_progress`，AC1/AC2 部分完成，产出 `YES 1 / NO 5 / UNKNOWN 55` 的文件级矩阵
- 修订内容：目标由「唯一最终证据判定」改为「AC 证据覆盖核验」；AC1–AC5 按 r18 §二 重写；
  新增结果枚举与核验口径两节
- **明确作废**：r18 §三 要求「不得将已有 `YES 1 / NO 5 / UNKNOWN 55` 的文件级矩阵
  包装为 AC 覆盖结论」。该矩阵**仅作为内容特征记录保留**，不作结论使用。
- 两个来源 Task（`EXPORT-REVEAL-1` 0/7、`P15` 0/6）的「done 但 AC 全未勾选」异常，
  按 r18 §一 继续按 `status` 纳入已释放 AC，同时**在 limitation 中单列**，不补勾、不重判。

## Closeout Record

- 状态：`proposed`。尚未释放、无 owner 认领、无交付。
- 释放条件（Codex r14 §5）：登记真实 worktree 路径、base/head、Plan/STATUS 指针后，
  由 Codex 置 `ready` 并派发。
- 本 Task 的产出是只读判定矩阵，不修改任何证据文件、pin 或生产代码。
