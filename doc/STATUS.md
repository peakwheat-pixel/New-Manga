# Current Development Status

状态刷新：2026-10-22；主控 dsh（epoch 10，唯一 Active Coordinator，lease `37230d78…`；Codex epoch 9 已交接）。

## 当前 Task

- 当前 Task：**[SETTINGS-OPEN-C-1-RECYCLE](tasks/SETTINGS-OPEN-C-1-RECYCLE.md)** `in_progress`（设置页回收站查看+清空；复用既有 wire；待独立 Review + GUI 烟测）；保留项 [V1-RELEASE-SIGNING-1](tasks/V1-RELEASE-SIGNING-1.md)（`in_review`，待证书/发布签核）。
- 最近完成：**[SETTINGS-OPEN-C-1-DESIGN](tasks/SETTINGS-OPEN-C-1-DESIGN.md)** `done`（批次 C 设计 + 裁决 D1–D11）；**[SETTINGS-OPEN-B-2](tasks/SETTINGS-OPEN-B-2.md)** `done`（缓存清理；`0e2e623`）；**[SETTINGS-OPEN-B-1](tasks/SETTINGS-OPEN-B-1.md)** `done`（模型/GPU + 任务/并发；`b521ad27`）；**[SETTINGS-OPEN-A-1](tasks/SETTINGS-OPEN-A-1.md)** `done`（批次 A；`6a303a9`）。设置页 10 开 2 关（备份恢复/Plugin 待 C-2/C-3）。
- [DEV-PREVIEW-1](tasks/DEV-PREVIEW-1.md)：done，`8ac00b97b`。
- 最近完成：**[GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1](tasks/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1.md)** `done`；声明错误 7→0、APPDATA 用户数据受保护；A+B+C 收敛（2.6GiB 归档可恢复）。
- 父任务：**[GIT-MAINLINE-CONVERGENCE-1](tasks/GIT-MAINLINE-CONVERGENCE-1.md)** `done`，r3 approved `6997733bf`；历史运行身份已归零。
- 收敛结果：`refs/heads` 仅 `main`、worktree 1、`refs/archive/*` 21、声明审计 0 errors。

## 保留与已知限制

- **WORKSPACE-CONSOLIDATION-1**：`closed_with_limitations`（r212）；不得再清理/GC/prune。
- **v1收口（2026-10-21，HEAD `239b165c2`）**：ACL 已修；source150/0/1、packaged12/0、前端327、pytest106、NSIS exit0、Sandbox 安装/卸载 PASS；签名待证书。
- **ARCH-DOC-REBASELINE**：`closed_with_limitations`（7 Gate + AC-CONSUMPTION PARTIAL）。
- `DETECT-TILING-1`/`DETECT-MEMORY-GUARD-1`/`SEC-FMT-IMPL-1`/`PDF-STREAM-FIX-1`/`P09-AC3-DELETE-1`/`P09-AC3-HARDEN-1`：`closed_with_limitations`。
- **P18 4/8**（AC2 门槛、AC5 阻塞）；**P20 6/7**；P16/P17 done；GOV-DEBT-CLEANUP-1 `superseded`；RUST-ENV-BASELINE-1 `closed_with_limitations`。
- **Task 台账**：[TASK_LEDGER](TASK_LEDGER.md)；11 条 P02 历史线归档 `historical`；当前 2 个非终态 Task。
- DIR-4 同一失败上限 2 次；DIR-5 goal 轮次上限 1000。Coordinator=dsh，epoch=10，lease=37230d7822a141fcae8f46acd7841890（LEASE_VALID）。

## Gate 与保留项

Technical Gate=NOT_SATISFIED；private_registry_absence=UNPROVABLE；Owner Risk Acceptance=APPROVED；Disposition=WAIVED_BY_OWNER。H1/P2-1/13 缺项、BC-AC5 PARTIAL、backlog 保留；未提交积压已入库（`GOV-UNTRACKED-BACKLOG-DISPOSITION-1`），不 push。**P20 发布 Gate 已实测通过**。

## 当前权威指针

- DAG 与节点状态：[REBASELINE_PLAN](REBASELINE_PLAN.md)（唯一权威）。
- 治理主线分支：`main`（见 [WORKSPACE_GOVERNANCE](WORKSPACE_GOVERNANCE.md)）。
- 恢复点：[父任务 checkpoint](../verification/GIT-MAINLINE-CONVERGENCE-1/checkpoint.md)；旧 checkpoint-r12/INFLIGHT 不恢复。
