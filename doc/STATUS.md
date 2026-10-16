# Current Development Status

状态刷新：2026-10-16；主控 dsh（epoch 5）。

## 当前 Task

- 当前 Task：[ARCH-DOC-REBASELINE](tasks/ARCH-DOC-REBASELINE.md) **ready / integrated**（唯一非终态 DAG READY）：AC1–AC3=PARTIAL、AC4–AC6=NOT_RUN、AC7 逐消费者裁决待做；消费者 P09/P18/P20/P16/P17 均未冻结。
- 本轮完成：[P13-C1](tasks/P13-C1.md) IPC 契约修订 **done**（`c61d8f8c`）；[P13](tasks/P13.md) 后台恢复 **done**（实现 `78b0d439`、评审 `58c0c462`、集成 `8d7cad13`）：durable 幂等、快照冻结、跨进程 scheduler owner、AC4 四项破坏性修正、重试边界、启动恢复、投影与四类事件；协议 major 2.0；`tests/core` 340 passed。
- 本轮完成：P06（`d3342895`）、P10（`c46c0df0`）、P11（`ceca5721`）、P09 导入 Core（`c6a7339f`，`closed_with_limitations`：AC3 受限=产品无项目级永久删除操作）、P09-FU1 测试基线（`860f6cda`）。
- 本轮完成：[P16-C1](tasks/P16-C1.md) 契约 rev 2.1 **done**（`27622aa3`）；[P16](tasks/P16.md) 阅读与输出授权 Core **done**（实现 `e2c07fa9`、评审 `338a7c5c`、集成 `e1be3082`）：Reader 投影/进度、五格式导出、`ExportTargetRef` 六类拒绝 + 原子消费 + 源零写；`tests/core` 352 passed。
- 已释放待认领：[P18](tasks/P18.md) 真实 JA/KO 质量资格方案 **ready**（Owner 按 DIR-2=codex；路径 `experiments/P18/**` + `verification/P18/**`；不得编造统一通过率、不改产品代码）。
- 遗留：**Tauri host 的 `ExportTargetRef` issuer** 须由其自身 Task 实现（P17 前）。
- 用户指令 DIR-2：后续 Task Owner=codex（至额度耗尽）。
- 已解决：BL-1（codex 空 ref）、BL-3（沙箱 `-c windows.sandbox=unelevated`）、BL-8（测试基线）。
- Coordinator=dsh，epoch=5，lease=264c2000541748298000f93fb25a52de（LEASE_VALID）。
- 用户 dirty/untracked 与既有 worktree 全程保留（19 项 tracked dirty 未变，无 EXTERNAL_CHANGE）。
- 恢复点：verification/PROJECT-ORCHESTRATION-20261016/checkpoint.md；日志 `.orchestrator/{INFLIGHT.json,OPLOG.ndjson,BACKLOG.md,RUNTIME_DIRECTIVES.md}`。

## Gate 与保留项

P02新时点验收/AC6恢复/主线集成完成，父P02限定关闭。Technical Gate=NOT_SATISFIED；private_registry_absence=UNPROVABLE；Owner Risk Acceptance=APPROVED；Disposition=WAIVED_BY_OWNER。旧H1/P2-1/13项缺失、BC-AC5 PARTIAL、缓存与产品backlog保留。用户dirty/untracked/旧worktree保留，不push或删除资源。

## 当前权威指针

- DAG：[REBASELINE_PLAN](REBASELINE_PLAN.md)；READY=ARCH-DOC-REBASELINE、P13。
- 本轮证据：P13 契约 [tasks/P13](tasks/P13.md)；P11 [Review](../verification/P11/dsh-review-r1.md)；P09 [Review](../verification/P09/dsh-review-r1.md)；ARCH-DOC [R1](../verification/ARCH-DOC-REBASELINE/dsh-review-r1.md)。