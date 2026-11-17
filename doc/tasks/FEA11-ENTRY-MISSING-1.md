---
id: FEA11-ENTRY-MISSING-1
title: SOURCE_ENTRY_MISSING 归因（部分）—— 已排除种子/路径，被兜底映射掩盖
kind: evidence
governance_version: 3
status: closed_with_limitations
disposition: "剩余失败无法定论：MapMintFailure 的 _ => 兜底丢弃了内层异常类型"
approval: DSH 2026-11-15
suggested_owner: DSH
owner: DSH
reviewer: reviewer-fea11（DSH 子 agent，独立上下文，未参与实现；2026-11-17 收口复核）
depends_on:
  - FEA11-SEED-PIXEL-1
base_commit: 414e3e8d1
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA11-ENTRY-MISSING-1
allowed_paths:
  - doc/tasks/FEA11-ENTRY-MISSING-1.md
  - doc/reviews/FEA11-ENTRY-MISSING-1-*.md
  - doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/GOAL-PROGRESS-2026-11-02.md
  - verification/FEA11-ENTRY-MISSING-1/**
---

# FEA11-ENTRY-MISSING-1（blocked：无法定论）

## 结论

失败点在 `SourceReadCoordinator.DescribeContainer` 的 `FileStream` 打开处，
但**内层异常类型被 `MapMintFailure` 的 `_ =>` 兜底丢弃**，因此"文件不存在 / 无权限 / 其它"不可区分。

**已排除**：种子未生成 `new_zip`、路径非绝对、schema 版本不符。
**未定论**：`FileStream` 打开的具体失败原因。

## 为什么标 blocked

要定论需要**内层异常类型**，而它被产品代码丢弃。**不是我缺实物，也不是环境缺失**，
而是**产品诊断信息不足**导致的"证据不可得"。

已给出的建议（未实施）：
1. 产品侧 `MapMintFailure` 保留 `innerException` / 在兜底分支保留原始类型（**诊断性**改动，不改错误码语义）；
2. 测试侧先 `Assert.True(File.Exists(newZip))` 并打印路径，把"文件不存在"从"其它"里分离。

## 边界

- 带 opt-in 三类基线仍 **12 passed / 1 failed**。
- 条件 3 仍不判 MET。

## Acceptance Criteria

- [x] **AC1 失败点定位**：定位失败发生在 `SourceReadCoordinator.DescribeContainer` 的 `FileStream` 打开处，并排除「种子未生成 `new_zip` / 路径非绝对 / schema 版本不符」。 <<MET>>
- [x] **AC2 诊断能力**：产品侧能区分内层异常类型（`FileNotFound` / `Unauthorized` / 其它）—— 由 `MINT-FAILURE-DIAG-1`（commit `c68a67216`）交付：`SourceAccessException.OriginalExceptionType`，`Message` 仍严格等于 `Code`；`MapMintFailureDiagnosticsTests` 3 facts 实测 3 passed / EXIT=0。 <<MET>>
- [x] **AC3 复现复核**：触发本卡的 `Fea11Residual4AIpcTests.ProductionDispatcherFullSyncChain_NewKeyOldDigestConserved`（opt-in `NEWMANGA_FEA11_IPC=1`）在当前 head 连续 3 次通过（2026-11-17，各 EXIT=0）。 <<MET>>
- [x] **AC4 不虚报**：不声称历史失败根因已定位（当前仅「不可复现」）；不声称条件 3 MET 或产品无缺陷。 <<MET>>

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) | sha256_basis |
|---|---|---|---|---|---|---|
| EV-FE11-01 | AC1/AC3 归因与复现 | verification/FEA11-ENTRY-MISSING-1/README.md | 9818e7bad | 9bc1fd03cc047acd81b28fc52082327e936d0d5193a3c5cc552dc0e06a29f660 | CANONICAL | BLOB |
| EV-FE11-02 | AC3 三次复跑 | verification/FEA11-ENTRY-MISSING-1/opt-in-rerun-2026-11-17.log | 9818e7bad | 19942321d4fa3b318a2b06c2d11d9ea30c509a640dcdf55329aee72e904b4efd | CANONICAL | BLOB |
| EV-FE11-03 | AC2 诊断能力来源 | verification/MINT-FAILURE-DIAG-1/README.md | c68a67216 | a7c041269c7a73184e639190e376c2722ad786f0870659cd16a73c469e146f5d | SOURCE_PIN | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/FEA11-ENTRY-MISSING-1/ | NOT_APPLICABLE | — | — | 2 个证据文件已登记于 Canonical Evidence；无迁移/归档/删除 |

## Closeout Record（2026-11-17，DSH）

- canonical_evidence_status：`complete`；resource_closeout_status：`complete`；删除/迁移/归档：**0**。
- **收口依据**：本卡 `blocked` 的唯一前提是「`MapMintFailure` 的 `_ =>` 兜底丢弃内层异常类型」。该前提已被 `MINT-FAILURE-DIAG-1`（`c68a67216`）解除；且触发本卡的 opt-in 测试在当前 head 连续 3 次通过。
- **限制清单**：
  1. **L-FE11-1｜历史根因未复现**：基线 `414e3e8d1` 的那次失败在当前 head 无法复现，**根因未定位**；本卡只登记「不可复现」，不声称已修复某缺陷。
  2. **L-FE11-2｜结论已被超越**：卡面「结论 / 为什么标 blocked / 边界」三节是 2026-11-15 时点记录，保留原字节；当前事实以本节与 AC 为准。
  3. **L-FE11-3｜不改条件 3**：本卡不解条件 3 的其余缺口（人眼/AGENT 视觉裁定、真机走查）。
- **边界**：`Technical Gate=NOT_SATISFIED` 不变。
