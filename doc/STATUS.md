# Current Development Status

状态刷新：2026-10-16；主控 dsh（epoch 6，唯一 Active Coordinator，用户 17:10 裁决）。

## 当前 Task

- 当前 Task：[ARCH-DOC-REBASELINE](tasks/ARCH-DOC-REBASELINE.md) **ready / integrated**（AC1–AC3=PARTIAL、AC4–AC6=NOT_RUN、AC7 逐消费者裁决待做）。
- 本轮完成：[UI-DESIGN-1](tasks/UI-DESIGN-1.md) **done**（四页设计基线冻结 W1–W32/24 真缺口，I1 收敛，集成 `9e1221e1b`）；[ENV-BUNDLE-1-FU1](tasks/ENV-BUNDLE-1-FU1.md) **closed_with_limitations**（frozen bundle 驱动 6/6）；[P12](tasks/P12.md) **done**（Shell+书架+导入 UI；前端 173/173、构建 exit 0；**无头环境未跑真实 GUI e2e**）；[HOST-TTL-BOUNDARY-1](tasks/HOST-TTL-BOUNDARY-1.md) **done**（两侧 issuer 留 1 s 裕量、Core 守卫未动，集成 `23587397e`）；[EVENTS-FWD-1](tasks/EVENTS-FWD-1.md) **done**（§6.4 六类事件转发面、生产命令面仍 18；I1 收敛，集成 `22920f8db`；AC4 端到端触发如实 `BLOCKED`）。
- **在飞/待派发**：[EXPORT-REVEAL-1](tasks/EXPORT-REVEAL-1.md)（Review **approved**，AC4-③ 如实 BLOCKED；待并入新 main 解冲突后集成）；[RUN-IPC-1](tasks/RUN-IPC-1.md)（dsh 自任 Owner，实现+证据完成，待交付）。
- **待用户裁决**：P18 产品发布门槛。**下一批候选**：G21–G25（P15 前置）、P18 像素上限/KO 权重、BL-12、BL-13。
- DIR-2：Task Owner=codex（至额度耗尽）；DIR-3：只保留一个 Active Coordinator。
- Coordinator=dsh，epoch=6，lease=9ce79020a36e4fab8970e8ae6de5fb10（LEASE_VALID）；用户 19 项 dirty 未变，无 EXTERNAL_CHANGE。
- 恢复点：verification/PROJECT-ORCHESTRATION-20261016/checkpoint-r9.md（当前 rolling checkpoint；上一稳定边界 checkpoint.md）；日志 `.orchestrator/{INFLIGHT.json,OPLOG.ndjson,BACKLOG.md,RUNTIME_DIRECTIVES.md}`。

## Gate 与保留项

P02新时点验收/AC6恢复/主线集成完成，父P02限定关闭。Technical Gate=NOT_SATISFIED；private_registry_absence=UNPROVABLE；Owner Risk Acceptance=APPROVED；Disposition=WAIVED_BY_OWNER。旧H1/P2-1/13项缺失、BC-AC5 PARTIAL、缓存与产品backlog保留。用户dirty/untracked/旧worktree保留，不push或删除资源。

## 当前权威指针

- DAG：[REBASELINE_PLAN](REBASELINE_PLAN.md)；READY=ARCH-DOC-REBASELINE、EXPORT-REVEAL-1、RUN-IPC-1。
- 本轮证据：P12 [Review](../verification/P12/dsh-review-r1.md)；UI-DESIGN-1 [Review](../verification/UI-DESIGN-1/dsh-review-r1.md)；ENV-BUNDLE-1-FU1 [Review](../verification/ENV-BUNDLE-1-FU1/dsh-review-r1.md)。