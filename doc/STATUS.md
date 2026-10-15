# Current Development Status

状态刷新：2026-10-15（R1–R6 恢复轮 + P11 释放）；主控 dsh（epoch 5）。

## 当前 Task

- **进行中**：[P11](tasks/P11.md) 长任务生命周期契约，**ready**（2026-10-15 释放）；Owner=codex、Reviewer=dsh（非 Owner、未参与实现）；base=3691ccba、branch=codex/P11-long-task-lifecycle-contract、worktree=G:/CODEX/New Manga.workspace/worktrees/P11-LONG-TASK-LIFECYCLE-CONTRACT。交付=可冻结的 durable accepted/快照/控制/恢复契约（不写 runtime、不造第二调度器），作 P13/P14 唯一契约输入。
- **挂起 READY**：[ARCH-DOC-REBASELINE](tasks/ARCH-DOC-REBASELINE.md) **ready / integrated**（未 done）：AC1–AC3=PARTIAL、AC4–AC6=NOT_RUN、AC7 逐消费者裁决待做；剩余项依赖 P09/P18/P20/P16/P17 冻结。已落库：交付 `70208144`、R1 Review `79ed01fd`、dirty 基线 `836a12c6`、集成 merge `4227e8b5`；AC7/C3 pin 已登记（8/8 blob 层 sha256 一致）。
- 已关闭：[P04](tasks/P04.md) done（merge=7bfcf16a）；[P22-REBASE-1](tasks/P22-REBASE-1.md) done（merge=4e5c71d9）；[PROJECT-ROADMAP-RELEASE](tasks/PROJECT-ROADMAP-RELEASE.md) done。
- 架构文档 Gate=PARTIAL/NOT_CLOSED，P09/P18/P20 映射仍 NOT_RUN。
- Coordinator=dsh，epoch=5，lease=264c2000541748298000f93fb25a52de（LEASE_VALID）。
- 冻结基线=4ef92f3d；用户 dirty/untracked 与既有 worktree 保留（10/10 pin 未被覆盖，无 EXTERNAL_CHANGE）。
- 恢复点：verification/ARCH-DOC-REBASELINE/recovery-r1-r6-20261015.md；运行日志 `.orchestrator/INFLIGHT.json`、`OPLOG.ndjson`。

## Gate 与保留项

P02新时点验收/AC6恢复/主线集成完成，父P02限定关闭。Technical Gate=NOT_SATISFIED；private_registry_absence=UNPROVABLE；Owner Risk Acceptance=APPROVED；Disposition=WAIVED_BY_OWNER。旧H1/P2-1/13项缺失、BC-AC5 PARTIAL、缓存与产品backlog保留。用户dirty/untracked/旧worktree保留，不push或删除资源。

## 当前权威指针

- DAG：[REBASELINE_PLAN](REBASELINE_PLAN.md)；READY=P11（进行中）+ ARCH-DOC-REBASELINE（挂起待消费者）。
- 本轮证据：P11 契约 [tasks/P11](tasks/P11.md)；ARCH-DOC R1 Review [dsh-review-r1](../verification/ARCH-DOC-REBASELINE/dsh-review-r1.md)；恢复核验 [recovery-r1-r6](../verification/ARCH-DOC-REBASELINE/recovery-r1-r6-20261015.md)；P04 R5 [dsh-p04-owner-review-r5](../verification/P04/dsh-p04-owner-review-r5.stdout.md)。
