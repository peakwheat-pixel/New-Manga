# Current Development Status

状态：2026-10-25 起 DeepSeek Harness（DSH）接任 Lead / Architect / Integrator；用户授权与字节保留见[接管记录](GOVERNANCE_TAKEOVER_2026-10-25.md)。目标：不传播私有素材，完成干净源码快照的安全 push。

## 当前 Task

- 当前 Task：[GIT-CLEAN-PUBLICATION-1](tasks/GIT-CLEAN-PUBLICATION-1.md) `in_review`（root `e34a90d00`；push-gate 独立 Review approved；已推 `origin/codex/clean-source-snapshot`，远端 SHA=e34a90d00；DSH r1 blocked 保留；产品 AC4/AC5 未过；[checkpoint](../verification/GIT-CLEAN-PUBLICATION-1/checkpoint.md)）。
- Rust：[ISOLATION-1](tasks/GIT-CLEAN-RUST-ISOLATION-1.md) `in_review`（1829a38；默认并发双过；饱和 0/32，DSH r2 blocked 保留；Reviewer 改派 Antigravity）。
- 容量设计：[CAPACITY-DESIGN-1](tasks/GIT-CLEAN-RUST-CAPACITY-DESIGN-1.md) `ready`（ZCode，仅设计；Reviewer 改派 Antigravity）。
- 诊断/环境：[DIAG-1](tasks/GIT-CLEAN-PUBLICATION-DIAG-1.md) `approved`（仅诊断，不集成/不 done）；[CORE-ENV-2](tasks/GIT-CLEAN-CORE-ENV-2.md) `proposed`（V2–V5 未冻结）。
- 全审/签核：[FULL-AUDIT](tasks/NEW-MANGA-V1-FULL-AUDIT.md) `blocked`（resume=in_progress）；[V1-RELEASE-SIGNING-1](tasks/V1-RELEASE-SIGNING-1.md) `in_review`（无当前执行）。
- 最近完成：GUI-PLUGIN-SANDBOX-SMOKE-1、TOOL-SOFTWARE-SMOKE-1 `done`；插件运行线 SANDBOX-1/2、CAPABILITY-1、PACKAGED-PYTHON-1 approved。

## 保留与已知限制

- WORKSPACE-CONSOLIDATION-1：`closed_with_limitations`（r212）；不得再清理/GC/prune。
- v1 收口（2026-10-21，HEAD `239b165c2`）：ACL 已修；source150/0/1、packaged12/0、前端327、pytest106、NSIS exit0、Sandbox 安装/卸载 PASS；签名待证书。
- ARCH-DOC-REBASELINE `closed_with_limitations`；P18 4/8；P20 6/7；DETECT-* / SEC-* / PDF-* / P09-AC3-* 等 `closed_with_limitations`。
- Task 台账：TASK_LEDGER（7 个非终态）；DIR-4 同一失败上限 2 次；DIR-5 goal 轮次上限 1000。
- 干净快照 push 前置：材料隔离 AC1–AC3 已 MET；Core 3 组参数失败为环境 ACL 限制（DIAG 冻结）；Rust 默认并发为测试共享状态（r2 证据）；产品发布 Gate 未通过，不得宣称。

## Gate 与保留项

Technical Gate=NOT_SATISFIED；private_registry_absence=UNPROVABLE；Owner Risk Acceptance=APPROVED；Disposition=WAIVED_BY_OWNER。P20 发布 Gate 已实测通过。本次只授权并执行「干净源码快照新分支」push，不是 main 推送、不是产品发布验收。

## 当前权威指针

- DAG 与节点状态：[REBASELINE_PLAN](REBASELINE_PLAN.md)（唯一权威）。
- 治理主线分支：`main`（见 [WORKSPACE_GOVERNANCE](WORKSPACE_GOVERNANCE.md)）。
- 恢复点：[父任务 checkpoint](../verification/GIT-CLEAN-PUBLICATION-1/checkpoint.md)；旧 checkpoint-r12/INFLIGHT 不恢复。
