---
id: GOV-PLAN-BUDGET-1
title: Plan 预算上限扩容
kind: governance
governance_version: 2
status: ready
approval: user_decision_1_2026-10-19; codex_scope_release_integration-closeout-r3
suggested_owner: dsh
owner: dsh
reviewer: Antigravity
depends_on: []
base_commit: 960188271d62bf40db4b3646b6fa02ab869bade0
branch: agent/deepseek/GOV-PLAN-BUDGET-1
worktree: G:/CODEX/New Manga.workspace/worktrees/GOV-PLAN-BUDGET-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-PLAN-BUDGET-1
allowed_paths:
  - tools/governance/check.ps1
  - doc/tasks/GOV-PLAN-BUDGET-1.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/handoffs/
  - doc/reviews/
  - verification/GOV-PLAN-BUDGET-1/
---

# GOV-PLAN-BUDGET-1：Plan 预算上限扩容

## 来源与目标
依用户 2026-10-19 裁决 1 与 r3 `4，将检查器中 Plan 预算调整到 7000 bytes / 64 lines。

## Acceptance Criteria
- [ ] AC1：只改 Path 为 doc/REBASELINE_PLAN.md 的预算项 Bytes=7000、Lines=64。STATUS 3200/45、其它预算、比较条件、warning/error 逻辑和提示不变；diff 可逐行证明。
- [ ] AC2：Owner只改上述两个值、本 Task、Handoff、evidence_dir。Plan/STATUS/导航仅由 Codex维护生命周期指针；不得登记或修改 29 个暂缓 Task、GOV-DEBT-CLEANUP-2 状态/AC/证据。
- [ ] AC3：隔离 fixture 验证 7000 bytes/64 lines 内通过、7001 bytes 与 65 lines 分别超限、80% warning 不变。记录 fixture、命令、PowerShell 版本、stdout/stderr/exit code；不覆盖 Plan。
- [ ] AC4：固定交付 head 执行全局检查和 TaskPath 检查，保存完整输出/exit code，warnings 如实记录。
- [ ] AC5：DSH 固定 base/delivery 并交 Handoff；Antigravity 独立 Review；Codex集成后验证与资源/evidence closeout，全部完成才 done。

## 允许修改范围
tools/governance/check.ps1 两个数值、本 Task、doc/handoffs/GOV-PLAN-BUDGET-1-*.md、verification/GOV-PLAN-BUDGET-1/**。Codex维护 Plan/STATUS/Task 导航元数据；Reviewer写独立 Review。allowed_paths 含 evidence_dir。

## 禁止范围与不做事项
不改两值外逻辑/预算；不改产品、Schema、依赖、接口；不登记暂缓 Task；不跑 AC 探针或产品测试；不移动/删除仓外资源或 worktree。范围需扩大先交 Codex裁定。

## 测试计划
| AC | 步骤 | 环境 | 结果 | 证据 |
|---|---|---|---|---|
| AC1 | 固定 head diff | Git | NOT_RUN | verification/GOV-PLAN-BUDGET-1/ |
| AC3 | 边界 fixture | PowerShell/Windows | NOT_RUN | 同上 |
| AC4 | 全局及 TaskPath checker | 固定 head | NOT_RUN | 同上 |
| AC5 | 固定 head Review/集成验证 | 固定 base | NOT_RUN | Handoff/Review |

## 依赖、风险与阻塞
先决：checker 纳入可复现基线，Codex登记 Plan/STATUS、固定 branch/worktree/base。Owner DSH；Reviewer Antigravity；不可与其它 checker 写入 Task 并行。

## 交付与运行记录
Handoff：doc/handoffs/GOV-PLAN-BUDGET-1-<short-head>.md；Review：doc/reviews/GOV-PLAN-BUDGET-1-<short-head>-antigravity.md。绑定实际 head，NOT_RUN/BLOCKED 不得记 PASS。

## Canonical Evidence
进入 in_review 前列出 AC1–AC5 当前 evidence 路径、commit/hash/class。
| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| 待交付 | AC1–AC5 | verification/GOV-PLAN-BUDGET-1/ | 待填 | 待填 | 待定 |

## Resource Manifest
| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | 据实记录 | PRESERVE_UNKNOWN | 原路径 | 待记录 | 待检查 |
| agent-output/exchange | 据实记录；无则核实 NOT_APPLICABLE | 据实记录 | 原路径 | 待记录 | 待检查 |

## Closeout Record
- Closeout date / Codex：待填。
- canonical_evidence_status / resource_closeout_status：pending。
- 删除、迁移、归档未授权前为 0。
- 未关闭项及保留原因逐项记录。
- 终态时 Codex更新指针并运行 Task 检查。
