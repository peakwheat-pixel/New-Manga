# Current Development Status

状态刷新：2026-10-16；主控 dsh（epoch 6，唯一 Active Coordinator，用户 17:10 裁决）。

## 当前 Task

- 当前 Task：[ARCH-DOC-REBASELINE](tasks/ARCH-DOC-REBASELINE.md) **ready / integrated**（AC1–AC3=PARTIAL、AC4–AC6=NOT_RUN、AC7 逐消费者裁决待做）。
- 本轮完成：[ENV-BUNDLE-1](tasks/ENV-BUNDLE-1.md) **closed_with_limitations**（bundle 已重建对齐协议 2.3）；[UI-DESIGN-1](tasks/UI-DESIGN-1.md) **done**（Review R1 **approved**、I1 收敛；集成 `9e1221e1b`）——四页 UI 设计基线已冻结，见 [设计基线](design/AD001_FOUR_PAGE_UI_BASELINE.md)（W1–W32 绑定 / 24 条真缺口）。
- **待用户裁决**：P18 产品发布门槛（JA/KO 达到何种程度才声明支持）。
- 本轮完成：[ENV-BUNDLE-1-FU1](tasks/ENV-BUNDLE-1-FU1.md) **closed_with_limitations**（Review `a88242d5f` approved；**packaged 六项由真实 frozen bundle 驱动并 6/6 通过**；AC3 HostControl `REF_EXPIRED` 受阻，已转 HOST-TTL-BOUNDARY-1）。
- **在飞**：[P12](tasks/P12.md)（antigravity；书架导入 UI 实现）。
- **新释放待派发**：[HOST-TTL-BOUNDARY-1](tasks/HOST-TTL-BOUNDARY-1.md) —— **已确认的关键路径产品缺陷**：host 把 import grant 的 TTL 取在 Core 验证窗口的**精确上限**（`host_issuer.rs:152` = `now+300.0`，Core `import_source_refs.py:153` 拒绝 `> now+300`），导致 `RegisterImportSource` 间歇 `REF_EXPIRED`；`library_import_file`（P12 导入 UI 依赖）走的正是这条路径。
- **下一批候选**：G17（事件转发面，P14 前置）、G20（open-folder host command，P17 前置）、G21–G25（P15 前置）、P18 像素上限与 KO 权重、BL-12。
- 用户指令 DIR-2：Task Owner=codex（至额度耗尽）；DIR-3：只保留一个 Active Coordinator。
- Coordinator=dsh，epoch=6，lease=9ce79020a36e4fab8970e8ae6de5fb10（LEASE_VALID）。
- 用户 dirty/untracked 与既有 worktree 全程保留（19 项 tracked dirty 未变，无 EXTERNAL_CHANGE）。
- 恢复点：verification/PROJECT-ORCHESTRATION-20261016/checkpoint.md；日志 `.orchestrator/{INFLIGHT.json,OPLOG.ndjson,BACKLOG.md,RUNTIME_DIRECTIVES.md}`。

## Gate 与保留项

P02新时点验收/AC6恢复/主线集成完成，父P02限定关闭。Technical Gate=NOT_SATISFIED；private_registry_absence=UNPROVABLE；Owner Risk Acceptance=APPROVED；Disposition=WAIVED_BY_OWNER。旧H1/P2-1/13项缺失、BC-AC5 PARTIAL、缓存与产品backlog保留。用户dirty/untracked/旧worktree保留，不push或删除资源。

## 当前权威指针

- DAG：[REBASELINE_PLAN](REBASELINE_PLAN.md)；READY=ARCH-DOC-REBASELINE、P12、HOST-TTL-BOUNDARY-1。
- 本轮证据：UI-DESIGN-1 [Review](../verification/UI-DESIGN-1/dsh-review-r1.md)；ENV-BUNDLE-1 [Review](../verification/ENV-BUNDLE-1/dsh-review-r1.md)；HOST-ISSUER-1 [Review](../verification/HOST-ISSUER-1/dsh-review-r1.md)。