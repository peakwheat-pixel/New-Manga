# Current Development Status

状态刷新：2026-10-16；主控 dsh（epoch 6，**唯一 Active Coordinator**，用户 17:10 裁决）。**注意：曾有第二个共享同一 lease(epoch 5) 的 dsh 会话（进程已退出/空闲）；同一时刻只应有一个 Active Coordinator。**

## 当前 Task

- 当前 Task：[ARCH-DOC-REBASELINE](tasks/ARCH-DOC-REBASELINE.md) **ready / integrated**（AC1–AC3=PARTIAL、AC4–AC6=NOT_RUN、AC7 逐消费者裁决待做）。
- 本轮完成：P13/P13-C1/P16/P16-C1/P12-C1/P09-FU2/[HOST-CORE-1](tasks/HOST-CORE-1.md)/[HOST-ISSUER-1](tasks/HOST-ISSUER-1.md) **done**；[P18](tasks/P18.md)、[ENV-BUNDLE-1](tasks/ENV-BUNDLE-1.md) **closed_with_limitations**（评审 `8250b420`、集成 `7b9cbbe6`、closeout `814d3fb4`：bundle 已重建对齐协议 2.3，frozen `core_service.exe` smoke `overall PASS`）。
- **待用户裁决**：P18 产品发布门槛（JA/KO 达到何种程度才声明支持）。
- **并行执行中（两条独立线路，worktree 与写入路径互不重叠）**：
  - [UI-DESIGN-1](tasks/UI-DESIGN-1.md) — owner=**zcode**（job `pwsh-60`）：四页 UI/UX 设计基线，解 P12/P14/P15/P17 的 UI 前置 → 通往 P19/P20 的关键路径。
  - [ENV-BUNDLE-1-FU1](tasks/ENV-BUNDLE-1-FU1.md) — owner=**codex**：packaged 驱动验收，闭环 ENV-BUNDLE-1 AC4 严格口径（2.3 bundle 仅存在于 ENV-BUNDLE-1 worktree，主仓仍为 10-14 旧版）。
- **下一批候选**：P18 像素上限与 KO 权重、BL-12（是否入库需用户/Codex 定夺）、P12/P14/P15/P17 实现（待 UI-DESIGN-1 设计冻结）。
- 用户指令 DIR-2：后续 Task Owner=codex（至额度耗尽）；UI/UX 主责按 AGENTS.md 归 ZCode。
- Coordinator=dsh，epoch=6，lease=9ce79020a36e4fab8970e8ae6de5fb10（LEASE_VALID）；epoch 5 旧 lease 已 `STALE_COORDINATOR`。
- 用户 dirty/untracked 与既有 worktree 全程保留（19 项 tracked dirty 未变，无 EXTERNAL_CHANGE）。
- 恢复点：verification/PROJECT-ORCHESTRATION-20261016/checkpoint.md；日志 `.orchestrator/{INFLIGHT.json,OPLOG.ndjson,BACKLOG.md,RUNTIME_DIRECTIVES.md}`。

## Gate 与保留项

P02新时点验收/AC6恢复/主线集成完成，父P02限定关闭。Technical Gate=NOT_SATISFIED；private_registry_absence=UNPROVABLE；Owner Risk Acceptance=APPROVED；Disposition=WAIVED_BY_OWNER。旧H1/P2-1/13项缺失、BC-AC5 PARTIAL、缓存与产品backlog保留。用户dirty/untracked/旧worktree保留，不push或删除资源。

## 当前权威指针

- DAG：[REBASELINE_PLAN](REBASELINE_PLAN.md)；READY=ARCH-DOC-REBASELINE、UI-DESIGN-1、ENV-BUNDLE-1-FU1。
- 本轮证据：ENV-BUNDLE-1 [Review](../verification/ENV-BUNDLE-1/dsh-review-r1.md)；HOST-ISSUER-1 [Review](../verification/HOST-ISSUER-1/dsh-review-r1.md)；HOST-CORE-1 [Review](../verification/HOST-CORE-1/dsh-review-r1.md)；P18 [Review](../verification/P18/dsh-review-r1.md)；P16 [Review](../verification/P16/dsh-review-r1.md)。
