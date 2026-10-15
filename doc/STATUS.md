# Current Development Status

状态刷新：2026-10-15（R1–R6 恢复 + P11 全循环完成）；主控 dsh（epoch 5）。

## 当前 Task

- 当前 Task：[ARCH-DOC-REBASELINE](tasks/ARCH-DOC-REBASELINE.md) **ready / integrated**（唯一非终态 READY）：AC1–AC3=PARTIAL、AC4–AC6=NOT_RUN、AC7 逐消费者裁决待做；消费者 P09/P18/P20/P16/P17 均 `proposed` 未冻结。
- 本轮完成：[P11](tasks/P11.md) 长任务生命周期契约 **done**：交付 head=`c7922ae1`、独立 Review=`09797eab`（approved_with_conditions）、集成 merge=`ceca5721`。产出 [P11 契约](contracts/P11_LONG_TASK_LIFECYCLE_CONTRACT.md)：§1 逐条来源映射、§4 状态机与非法转换拒绝清单、§7.1 单一 scheduler 所有权、§8 现状对照（实证 4 项实现缺口）、§9 P13/P14 消费边界、§10 静态 PASS + runtime/UI `NOT_RUN`。
- 已释放待认领：[P10](tasks/P10.md) 凭据与配置通道契约 **ready**（base=`9aa4ff4b`，Owner/Reviewer 待路由）；范围见 P08 SCOPE_DRAFT 第 37 行与工作包第 76 行，不受 AC-DOC Gate 约束。
- 已关闭：[P04](tasks/P04.md)（merge=7bfcf16a）、[P22-REBASE-1](tasks/P22-REBASE-1.md)（merge=4e5c71d9）、[PROJECT-ROADMAP-RELEASE](tasks/PROJECT-ROADMAP-RELEASE.md)。
- **P09 释放前置（BL-2）**：需用户选定首发输入格式与最小目标（SCOPE_DRAFT 第 75 行）。
- Coordinator=dsh，epoch=5，lease=264c2000541748298000f93fb25a52de（LEASE_VALID）。
- 用户 dirty/untracked 与既有 worktree 全程保留（19 项 tracked dirty 未变，无 EXTERNAL_CHANGE）。
- 恢复点：verification/ARCH-DOC-REBASELINE/recovery-r1-r6-20261015.md；运行日志 `.orchestrator/INFLIGHT.json`、`OPLOG.ndjson`；队列 `.orchestrator/BACKLOG.md`。

## Gate 与保留项

P02新时点验收/AC6恢复/主线集成完成，父P02限定关闭。Technical Gate=NOT_SATISFIED；private_registry_absence=UNPROVABLE；Owner Risk Acceptance=APPROVED；Disposition=WAIVED_BY_OWNER。旧H1/P2-1/13项缺失、BC-AC5 PARTIAL、缓存与产品backlog保留。用户dirty/untracked/旧worktree保留，不push或删除资源。

## 当前权威指针

- DAG：[REBASELINE_PLAN](REBASELINE_PLAN.md)；READY=ARCH-DOC-REBASELINE（唯一非终态）；下一释放候选=P10。
- 本轮证据：P11 [Review](../verification/P11/dsh-review-r1.md)、[契约](contracts/P11_LONG_TASK_LIFECYCLE_CONTRACT.md)、[Handoff](../doc/handoffs/P11-codex-b7fb6773.md)；ARCH-DOC [R1 Review](../verification/ARCH-DOC-REBASELINE/dsh-review-r1.md)、[恢复核验](../verification/ARCH-DOC-REBASELINE/recovery-r1-r6-20261015.md)。
