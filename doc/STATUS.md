# Current Development Status

状态刷新：2026-10-23；主控 dsh（epoch 10，lease `37230d78…`）。本次用户直接授权 Codex 实施。

## 当前 Task

- 当前 Task：[TOOL-SOFTWARE-SMOKE-1](tasks/TOOL-SOFTWARE-SMOKE-1.md) `in_review`（分层软件检查工具；实现 `963ff5e6f`，独立 Review 待执行）。保留项：[GUI-PLUGIN-SANDBOX-SMOKE-1](tasks/GUI-PLUGIN-SANDBOX-SMOKE-1.md) `blocked`（证据已存）、[V1-RELEASE-SIGNING-1](tasks/V1-RELEASE-SIGNING-1.md) `in_review`。
- 插件运行线完成：SANDBOX-1 `41d7abeb`、SANDBOX-2 `127c5111`、CAPABILITY-1 `0d3bbe49`、PACKAGED-PYTHON-1 `a1f05450`（均 approved）。
- 最近完成：PLUGIN-RUNTIME-2 `done`（r3 approved；111 passed）；SETTINGS-OPEN-C-3-PLUGIN `done`（`657c18d4..85128cd2`）；C-2-BACKUP、C-1-RECYCLE、C-1-DESIGN、B-1、A-1 均 done；DEV-PREVIEW-1 done `8ac00b97b`。
- 父任务：GIT-MAINLINE-CONVERGENCE-1 `done`（r3 approved `6997733bf`）。

## 保留与已知限制

- WORKSPACE-CONSOLIDATION-1：`closed_with_limitations`（r212）；不得再清理/GC/prune。
- v1收口（2026-10-21，HEAD `239b165c2`）：ACL 已修；source150/0/1、packaged12/0、前端327、pytest106、NSIS exit0、Sandbox 安装/卸载 PASS；签名待证书。
- ARCH-DOC-REBASELINE `closed_with_limitations`（7 Gate + AC-CONSUMPTION PARTIAL）。
- DETECT-TILING-1 / DETECT-MEMORY-GUARD-1 / SEC-FMT-IMPL-1 / PDF-STREAM-FIX-1 / P09-AC3-DELETE-1 / P09-AC3-HARDEN-1：`closed_with_limitations`。
- P18 4/8（AC2 门槛、AC5 阻塞）；P20 6/7；P16/P17 done；GOV-DEBT-CLEANUP-1 `superseded`；RUST-ENV-BASELINE-1 `closed_with_limitations`。
- Task 台账：TASK_LEDGER；11 条 P02 历史线归档 historical；当前 3 个非终态 Task。
- DIR-4 同一失败上限 2 次；DIR-5 goal 轮次上限 1000。Coordinator=dsh，epoch=10，lease=37230d7822a141fcae8f46acd7841890（LEASE_VALID）。

## Gate 与保留项

Technical Gate=NOT_SATISFIED；private_registry_absence=UNPROVABLE；Owner Risk Acceptance=APPROVED；Disposition=WAIVED_BY_OWNER。H1/P2-1/13 缺项、BC-AC5 PARTIAL、backlog 保留；未提交积压已入库（GOV-UNTRACKED-BACKLOG-DISPOSITION-1），不 push。P20 发布 Gate 已实测通过。

## 当前权威指针

- DAG 与节点状态：[REBASELINE_PLAN](REBASELINE_PLAN.md)（唯一权威）。
- 治理主线分支：`main`（见 [WORKSPACE_GOVERNANCE](WORKSPACE_GOVERNANCE.md)）。
- 恢复点：[父任务 checkpoint](../verification/GIT-MAINLINE-CONVERGENCE-1/checkpoint.md)；旧 checkpoint-r12/INFLIGHT 不恢复。
