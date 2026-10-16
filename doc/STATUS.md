# Current Development Status

状态刷新：2026-10-16；主控 dsh（epoch 5）。

## 当前 Task

- 当前 Task：[ARCH-DOC-REBASELINE](tasks/ARCH-DOC-REBASELINE.md) **ready / integrated**（唯一非终态 DAG READY）：AC1–AC3=PARTIAL、AC4–AC6=NOT_RUN、AC7 逐消费者裁决待做。
- 本轮完成：P13/P13-C1/P16/P16-C1/P12-C1/P09-FU2 均 **done**；P18 **closed_with_limitations**（AC2 待用户门槛）—— 详见各 Task 与 [REBASELINE_PLAN](REBASELINE_PLAN.md)。
- 已释放待认领：[HOST-CORE-1](tasks/HOST-CORE-1.md) **ready**（Core 侧 HostControl handler 实现；契约 §12 授权范围内；解 HOST-ISSUER-1 的第二次阻塞；Owner 按 DIR-2=codex）。
- [HOST-ISSUER-1](tasks/HOST-ISSUER-1.md) **blocked**：契约 rev 2.3 已冻结但 **Core handler 未实现**（`core_service.py` HostControl 命中数 0）；Coordinator 已备案自身规划疏漏与 prompt 约束错误。
- 仍待解阻：BL-11b（bundle 与协议 2.3 不匹配，主仓同现）、P18 检测像素上限与 KO 权重。
- [HOST-ISSUER-1](tasks/HOST-ISSUER-1.md) **blocked**：Owner 实证可信 host **无通道**把 grant 注册进运行中的 Core（`_register_*` 无 dispatcher 路由、registry 为内存态、`host_bridge` 不持有）；且 `cargo build/test` exit 101（构建前置缺失，登记 BL-11）。
- 仍待解阻：P18 检测像素上限、KO detector 权重；P14/P15/P17 需 ZCode 设计 Task。
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
