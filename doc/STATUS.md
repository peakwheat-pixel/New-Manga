# Current Development Status

状态刷新：2026-10-16；主控 dsh（epoch 6，唯一 Active Coordinator，用户 17:10 裁决）。

## 当前 Task

- 当前 Task：[ARCH-DOC-REBASELINE](tasks/ARCH-DOC-REBASELINE.md) **ready / integrated**（AC1–AC3=PARTIAL、AC4–AC6=NOT_RUN、AC7 逐消费者裁决待做）。
- 本轮完成（8）：[UI-DESIGN-1](tasks/UI-DESIGN-1.md) done `9e1221e1b`（四页设计基线 W1–W32/24 缺口）；[ENV-BUNDLE-1-FU1](tasks/ENV-BUNDLE-1-FU1.md) closed_with_limitations `b474c09b`（frozen bundle 6/6）；[P12](tasks/P12.md) done `465e3001e`（Shell+书架+导入 UI；**未跑真实 GUI e2e**）；[HOST-TTL-BOUNDARY-1](tasks/HOST-TTL-BOUNDARY-1.md) done `23587397e`（双向 TTL 留 1 s 裕量）；[EVENTS-FWD-1](tasks/EVENTS-FWD-1.md) done `22920f8db`（§6.4 六类事件；AC4 端到端 `BLOCKED`）；[RUN-IPC-1](tasks/RUN-IPC-1.md) done `c3929bcc3`（Run 命令面）；[EXPORT-REVEAL-1](tasks/EXPORT-REVEAL-1.md) done `c9b113f96`（G20；**AC4-③ GUI 段 BLOCKED**）；[EXPORT-IPC-1](tasks/EXPORT-IPC-1.md) done `aaca5d1ea`（导出控制/查询 + **去路径白名单投影**；**P14 前置已齐备**；**修正了一处不可验证的 commit SHA**）。
- **在飞/待派发**：[READER-IPC-1](tasks/READER-IPC-1.md)（codex **已交付**，待独立 Review；**P17 前置**）。
- **待用户裁决**：P18 产品发布门槛。**下一批候选**：G21–G25（P15 前置）、P18 像素上限/KO 权重、BL-12、BL-13。
- DIR-2：Task Owner=codex（至额度耗尽）；DIR-3：只保留一个 Active Coordinator。
- Coordinator=dsh，epoch=6，lease=9ce79020a36e4fab8970e8ae6de5fb10（LEASE_VALID）；用户 19 项 dirty 未变，无 EXTERNAL_CHANGE。
- 恢复点：`verification/PROJECT-ORCHESTRATION-20261016/` → checkpoint-r10.md（rolling）、pause-checkpoint-20261016.md（**2026-10-16 用户重启的暂停点与恢复处置；已恢复**）、ui-chain-prerequisite-matrix.md（**UI 链前置完整性 + P14/P17 页面边界裁决**）；日志 `.orchestrator/{INFLIGHT,OPLOG,BACKLOG,RUNTIME_DIRECTIVES}`。

## Gate 与保留项

P02新时点验收/AC6恢复/主线集成完成，父P02限定关闭。Technical Gate=NOT_SATISFIED；private_registry_absence=UNPROVABLE；Owner Risk Acceptance=APPROVED；Disposition=WAIVED_BY_OWNER。旧H1/P2-1/13项缺失、BC-AC5 PARTIAL、缓存与产品backlog保留。用户dirty/untracked/旧worktree保留，不push或删除资源。

## 当前权威指针

- DAG：[REBASELINE_PLAN](REBASELINE_PLAN.md)；READY=ARCH-DOC-REBASELINE、READER-IPC-1。
- 本轮证据：P12 [Review](../verification/P12/dsh-review-r1.md)；UI-DESIGN-1 [Review](../verification/UI-DESIGN-1/dsh-review-r1.md)；ENV-BUNDLE-1-FU1 [Review](../verification/ENV-BUNDLE-1-FU1/dsh-review-r1.md)。