# Current Development Status

状态刷新：2026-10-21；主控 Codex（epoch 9，唯一 Active Coordinator；用户确认 dsh 已停止写入）。

## 当前 Task

- 当前 Task：**[GIT-MAINLINE-CONVERGENCE-1](tasks/GIT-MAINLINE-CONVERGENCE-1.md)**（`blocked`；保护边界已明确，32残余声明错误与STATUS/r212禁令保留）。
- 技术前置：[GOV-PATH-HEADER-COMPAT-1](tasks/GOV-PATH-HEADER-COMPAT-1.md) `done`，独审78fc0cba2、集成9cae94142；77→32错误，新增410保护根，未清理。
- 收敛基线97/135；当前98本地分支/136工作树（新增并保留工具Task）；**尚未达到只剩main**。

- 发布保留：**[V1-RELEASE-SIGNING-1](tasks/V1-RELEASE-SIGNING-1.md)**（`in_review`：用户接受未签名 v1，待发布签核）。声明修复 done（`bb7887442`，76 残余）；WORKSPACE/P09 已 done。
- **WORKSPACE-CONSOLIDATION-1 已关闭**：`closed_with_limitations`（r212 批准）；18 资源 limitation；不得再清理/GC/prune；工具修复未实施。
- **v1 收口（2026-10-21，HEAD `239b165c2`）**：recycle-bin ACL 已修；source 150/0/1、packaged 12/0、前端 327、pytest 106、NSIS 重建 exit 0；Sandbox 安装/卸载 PASS；签名待证书（`release-readiness.md`）。
- **[ARCH-DOC-REBASELINE](tasks/ARCH-DOC-REBASELINE.md)**：`closed_with_limitations`（r37 的 7+1：7 Gate 达成 + AC-CONSUMPTION `PARTIAL`，6/8 消费者已处置；**ZCode 设计 Gate 与第二环境无活动 Task**）。
- `DETECT-TILING-1` / `DETECT-MEMORY-GUARD-1` / `SEC-FMT-IMPL-1` / `PDF-STREAM-FIX-1` 均 `closed_with_limitations`。
- `P09-AC3-DELETE-1`/`HARDEN-1` `closed_with_limitations`；**`P18` 4/8**（AC2 门槛、AC5 阻塞）；`P20` 6/7；`P16`/`P17` `done`。
- **[GOV-DEBT-CLEANUP-1](tasks/GOV-DEBT-CLEANUP-1.md)**：`superseded`；**[RUST-ENV-BASELINE-1](tasks/RUST-ENV-BASELINE-1.md)**：`closed_with_limitations`（v1 证据）。
- **Task 台账**：实时计数见 [TASK_LEDGER](TASK_LEDGER.md)；11 个非终态历史未跟踪草稿原样保留，状态字段不证明活性，不批量关闭。
- DIR-4：同一失败上限 2 次；DIR-5：goal 轮次上限 1000。Coordinator=codex，epoch=9，lease=e06e91c0a6b94d309c2af578256551d8（LEASE_VALID）。

## Gate 与保留项

Technical Gate=NOT_SATISFIED；private_registry_absence=UNPROVABLE；Owner Risk Acceptance=APPROVED；Disposition=WAIVED_BY_OWNER。H1/P2-1/13缺项、BC-AC5 PARTIAL、backlog 保留。用户未提交内容保留，不push/删除。**P20 发布 Gate 已实测通过**（`bundle==resource`；四页可达）。

## 当前权威指针

- DAG 与节点状态：[REBASELINE_PLAN](REBASELINE_PLAN.md)（唯一权威）。
- **治理主线分支**：`main`（2026-10-21 起；见 [WORKSPACE_GOVERNANCE](WORKSPACE_GOVERNANCE.md)）。
- 恢复点：[当前 checkpoint](../verification/GIT-MAINLINE-CONVERGENCE-1/checkpoint.md)；旧 checkpoint-r12/INFLIGHT 已漂移，不恢复旧作业。
