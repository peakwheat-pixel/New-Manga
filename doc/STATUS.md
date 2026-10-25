# Current Development Status

状态：2026-10-25 起 DeepSeek Harness（DSH）接任 Lead / Architect / Integrator；用户授权与字节保留见[接管记录](GOVERNANCE_TAKEOVER_2026-10-25.md)。

## 当前 Task

- 当前 Task：[UIUX-V2-RUNTIME-REALCORE-1](tasks/UIUX-V2-RUNTIME-REALCORE-1.md) `proposed`（真实 Tauri+Core 端到端，解除上一 Task 的 HUMAN_VERIFY；**未释放**，需用户裁决是否投入构建）。DAG 无 READY。
- 最近完成：[UIUX-V2-RUNTIME-1](tasks/UIUX-V2-RUNTIME-1.md) `done`（四页真实 IPC + 设置页 + 单一 UI；集成 `af421b9e6`；r1→r2 approved；tsc 0；vitest 60/564；真机 11 张；真实 Core=HUMAN_VERIFY）。
- 发布线（绕开）：[GIT-CLEAN-PUBLICATION-1](tasks/GIT-CLEAN-PUBLICATION-1.md) `in_review`（root `e34a90d00`；push-gate approved；AC4/AC5 未过）。
- Rust：[ISOLATION-1](tasks/GIT-CLEAN-RUST-ISOLATION-1.md) `in_review`（1829a38；默认并发双过；饱和 0/32，DSH r2 blocked 保留；Reviewer=ZCode）；[CAPACITY-DESIGN-1](tasks/GIT-CLEAN-RUST-CAPACITY-DESIGN-1.md) `ready`（仅设计；Reviewer=ZCode）。
- 诊断/环境：DIAG-1 `approved`；CORE-ENV-2 `proposed`；FULL-AUDIT `blocked`；V1-RELEASE-SIGNING-1 `in_review`（无执行）。
- 更早完成：DESIGN-V2-IMPL-1 `done`（`e1fd738a7`）；GUI-PLUGIN-SANDBOX-SMOKE-1、TOOL-SOFTWARE-SMOKE-1 `done`。
- Reviewer 改派（2026-10-25）：用户停用 Antigravity/agy，两 Rust Task Reviewer 改 ZCode；Owner 冲突已在 Task 卡登记，不授权自审。

## 保留与已知限制

- WORKSPACE-CONSOLIDATION-1：`closed_with_limitations`（r212）；不得再清理/GC/prune。
- v1 收口（2026-10-21，HEAD `239b165c2`）：ACL 已修；source150/0/1、packaged12/0、前端327、pytest106、NSIS exit0、Sandbox 安装/卸载 PASS；签名待证书。
- ARCH-DOC-REBASELINE `closed_with_limitations`；P18 4/8；P20 6/7；DETECT-* / SEC-* / PDF-* / P09-AC3-* 等 `closed_with_limitations`。
- Task 台账：TASK_LEDGER（8 个非终态）；DIR-4 同一失败上限 2 次；DIR-5 goal 轮次上限 1000。
- 干净快照 push 前置：材料隔离 AC1–AC3 已 MET；发布 Gate 未通过，不得宣称。
- UIUX 运行时：真实 Core 端到端未跑（HUMAN_VERIFY）；次级面板仅令牌桥接；`?view=legacy` 保留历史容器。

## Gate 与保留项

Technical Gate=NOT_SATISFIED；private_registry_absence=UNPROVABLE；Owner Risk Acceptance=APPROVED；Disposition=WAIVED_BY_OWNER。P20 发布 Gate 已实测通过。此前授权只覆盖「干净源码快照新分支」push，不是 main 推送、不是产品发布验收。**2026-10-25 UIUX push 裁决：未执行**（main 含历史材料、干净快照 Gate 未清；本地提交已完成）。

## 当前权威指针

- DAG 与节点状态：[REBASELINE_PLAN](REBASELINE_PLAN.md)（唯一权威）。
- 治理主线分支：`main`（见 [WORKSPACE_GOVERNANCE](WORKSPACE_GOVERNANCE.md)）。
- 恢复点：UIUX-V2-RUNTIME-1 交付 head 与审查 Appointment 见其 Task 卡；旧父任务恢复点 [checkpoint](../verification/GIT-CLEAN-PUBLICATION-1/checkpoint.md) 仅用于发布线。
