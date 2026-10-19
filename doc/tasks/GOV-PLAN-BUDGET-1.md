---
id: GOV-PLAN-BUDGET-1
title: Plan 预算上限扩容
kind: governance
governance_version: 2
status: done
approval: user_decision_1_2026-10-19; codex_scope_release_integration-closeout-r3
suggested_owner: dsh
owner: dsh
reviewer: Antigravity
depends_on: []
base_commit: 960188271d62bf40db4b3646b6fa02ab869bade0
branch: GOV-PLAN-BUDGET-1
worktree: G:/CODEX/New Manga/.agents/worktrees/GOV-PLAN-BUDGET-1
integration_commit: c131b1ae114d00c17e734a51f38263d92fe6f198
delivery_head: 126f9f31c857a728c5818b01aab91071dc7ed273
canonical_evidence_status: complete
resource_closeout_status: complete
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
- [x] AC1：只改 Path 为 doc/REBASELINE_PLAN.md 的预算项 Bytes=7000、Lines=64。STATUS 3200/45、其它预算、比较条件、warning/error 逻辑和提示不变；diff 可逐行证明。
- [x] AC2：Owner只改上述两个值、本 Task、Handoff、evidence_dir。Plan/STATUS/导航仅由 Codex维护生命周期指针；不得登记或修改 29 个暂缓 Task、GOV-DEBT-CLEANUP-2 状态/AC/证据。
- [x] AC3：隔离 fixture 验证 7000 bytes/64 lines 内通过、7001 bytes 与 65 lines 分别超限、80% warning 不变。记录 fixture、命令、PowerShell 版本、stdout/stderr/exit code；不覆盖 Plan。
- [x] AC4：固定交付 head 执行全局检查和 TaskPath 检查，保存完整输出/exit code，warnings 如实记录。
- [x] AC5：DSH 固定 base/delivery 并交 Handoff；Antigravity 独立 Review；Codex集成后验证与资源/evidence closeout，全部完成才 done。

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
| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| EVID-BUDGET-AC1AC3 | AC1、AC3 | `verification/GOV-PLAN-BUDGET-1/ac1-ac3-budget-and-boundary.md` | `126f9f31c` | `137c472a84c7626289528a75eb1c38082151b14494be1495c3852167c1935978` | `CANONICAL` |
| EVID-BUDGET-AC4 | AC4 | `verification/GOV-PLAN-BUDGET-1/ac4-governance-output.txt` | `126f9f31c` | `ed62e77eaee076377cf9a4e0b25dfd72e675ca0a14e5a3157fd002b64ef1d988` | `CANONICAL` |
| EVID-BUDGET-HANDOFF | AC5 | `doc/handoffs/GOV-PLAN-BUDGET-1-126f9f31c.md` | `ab925051b` | `42151b3d65c3531bb447f595f6fc1c54a4116cf8edaa1b21d78868fa8541b4dd` | `CANONICAL` |
| EVID-BUDGET-REVIEW | AC5 | `doc/reviews/GOV-PLAN-BUDGET-1-126f9f31c-antigravity-r1.md` | `126af54e7` | `15d221d1c869e92f514801ece980c67627af4bf8d06bc19eb4c0bad73ae486a4` | `CANONICAL` |

## Resource Manifest
| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| governance checker | `tools/governance/check.ps1` | `PRESERVE_REFERENCED` | `tools/governance/check.ps1` | `b7e68f96b8fca6977721b557b6b19721c3ece8bee84532df5ff0dc7de4cd3c56` | 唯一被修改的实现文件；集成后仍受 `.gitattributes` 的 `text eol=lf` 保护 |
| task worktree | `G:/CODEX/New Manga/.agents/worktrees/GOV-PLAN-BUDGET-1` | `PRESERVE_UNKNOWN` | `G:/CODEX/New Manga/.agents/worktrees/GOV-PLAN-BUDGET-1` | `663cbeebafb68ddef1047f8fbd19e865506328a6cb707a54ed01083ae540c97b` | 已集成；worktree 保留未删。内含 33 个为复现检查环境而镜像的未入库文件，非本 Task 交付物 |
| evidence dir | `verification/GOV-PLAN-BUDGET-1/` | `PRESERVE_REFERENCED` | `verification/GOV-PLAN-BUDGET-1/` | `137c472a84c7626289528a75eb1c38082151b14494be1495c3852167c1935978` | 2 份证据已入库，均为本 Task 的 AC 直接产物 |
| agent output | 仓外 agent-output，非本 Task 产物 | `NOT_APPLICABLE` | — | — | 本 Task 未产生需归档的仓外派生产物 |

## Closeout Record

- 关闭：2026-10-19。Owner=dsh，Reviewer=Antigravity（`doc/reviews/GOV-PLAN-BUDGET-1-126f9f31c-antigravity-r1.md`，APPROVED）。
- 交付：`check.ps1` L127 的 Plan 预算 `2500/35` → `7000/64`；delivery_head `126f9f31c`。
- 集成：`c131b1ae1`（`git merge --no-ff GOV-PLAN-BUDGET-1`，无冲突）。
- 边界证据：7000/64 仅 WARN、7001 与 65 行均 FAIL、80% 阈值移至 5600 bytes
  （`verification/GOV-PLAN-BUDGET-1/ac1-ac3-budget-and-boundary.md`）。
- 集成后治理：全局与 `-TaskPath` 均 **PASS (1 warnings)**；余下 1 条为 `doc/STATUS.md`
  已达 80% 的既有提示，非本 Task 引入。
- 删除 / 迁移 / 归档：**0 项**。
- 未关闭项：无（本 Task 无未完成 AC）。
