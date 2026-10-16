# Current Development Status

状态刷新：2026-10-16；主控 dsh（epoch 5）。

## 当前 Task

- 当前 Task：[ARCH-DOC-REBASELINE](tasks/ARCH-DOC-REBASELINE.md) **ready / integrated**（唯一非终态 DAG READY）：AC1–AC3=PARTIAL、AC4–AC6=NOT_RUN、AC7 逐消费者裁决待做。
- 本轮完成：[P12-C1](tasks/P12-C1.md) 导入侧 IPC 契约 **done**（评审 `18661dc4`、集成 `ed8e44e7`）：冻结 **rev 2.2** —— `ImportPages`、host 签发的只读 `ImportSourceRef`（无路径/bytes、300s 滑动续期、可撤销）、`ImportReport`；§12 授权导入 runtime。
- 本轮完成：[P13](tasks/P13.md)（集成 `8d7cad13`）、[P13-C1](tasks/P13-C1.md)（`c61d8f8c`）、[P16](tasks/P16.md)（`e1be3082`）、[P16-C1](tasks/P16-C1.md)（`27622aa3`）均 **done**；[P18](tasks/P18.md) **closed_with_limitations**（`44958159`，AC2 待用户门槛、AC5 待解阻）。
- **待用户裁决**：P18 的产品发布门槛（JA/KO 达到何种程度才声明支持）。
- **未解技术缺口**：检测像素上限 `11184810`、KO detector 权重缺失（导入侧 wire 由 P12-C1 处理）。
- 用户指令 DIR-2：后续 Task Owner=codex（至额度耗尽）。
- Coordinator=dsh，epoch=5，lease=264c2000541748298000f93fb25a52de（LEASE_VALID）。
- 用户 dirty/untracked 与既有 worktree 全程保留（19 项 tracked dirty 未变，无 EXTERNAL_CHANGE）。
- 恢复点：verification/PROJECT-ORCHESTRATION-20261016/checkpoint.md；日志 `.orchestrator/{INFLIGHT.json,OPLOG.ndjson,BACKLOG.md,RUNTIME_DIRECTIVES.md}`。

## Gate 与保留项

P02新时点验收/AC6恢复/主线集成完成，父P02限定关闭。Technical Gate=NOT_SATISFIED；private_registry_absence=UNPROVABLE；Owner Risk Acceptance=APPROVED；Disposition=WAIVED_BY_OWNER。旧H1/P2-1/13项缺失、BC-AC5 PARTIAL、缓存与产品backlog保留。用户dirty/untracked/旧worktree保留，不push或删除资源。

## 当前权威指针

- DAG：[REBASELINE_PLAN](REBASELINE_PLAN.md)；READY=ARCH-DOC-REBASELINE、P12-C1。
- 本轮证据：P18 [Review](../verification/P18/dsh-review-r1.md)；P16 [Review](../verification/P16/dsh-review-r1.md)；P13 [Review](../verification/P13/dsh-review-r1.md)；ARCH-DOC [R1](../verification/ARCH-DOC-REBASELINE/dsh-review-r1.md)。