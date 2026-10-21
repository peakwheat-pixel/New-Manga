# Current Development Status

状态刷新：2026-10-21；主控 dsh（epoch 8，唯一 Active Coordinator）。

## 当前 Task

- 当前 Task：**[P09-MANAGED-READ-ROOT-TRUST-1](tasks/P09-MANAGED-READ-ROOT-TRUST-1.md)**（`ready`，2026-10-21 用户释放；先交设计答案）。并发 READY：[WORKSPACE-CLEANUP-TOOL-HARDENING-1](tasks/WORKSPACE-CLEANUP-TOOL-HARDENING-1.md)。最近收口：[WORKSPACE-CONSOLIDATION-1](tasks/WORKSPACE-CONSOLIDATION-1.md)（`closed_with_limitations`）。
- **WORKSPACE-CONSOLIDATION-1 已关闭**：`closed_with_limitations`（r212 批准）；18 资源 limitation；不得再清理/GC/prune；工具修复未实施。
- **v1 收口（2026-10-21，HEAD `239b165c2`）**：修复 recycle-bin 生产 ACL 缺口；sidecar、Rust source 150/0/1、packaged 12/0、前端 327、pytest 106、NSIS 重建均 exit 0；见 `verification/V1-FINALIZE-20261021/`；Codex 复核 **approved**（最终收口 head `48cf5085a`）；Windows Sandbox 全新机器安装/卸载 **PASS**（`clean-install-sandbox/`）；签名待证书。
- **[ARCH-DOC-REBASELINE](tasks/ARCH-DOC-REBASELINE.md)**：`closed_with_limitations`（r37 的 7+1：7 Gate 达成 + AC-CONSUMPTION `PARTIAL`，6/8 消费者已处置；**ZCode 设计 Gate 与第二环境无活动 Task**）。
- `DETECT-TILING-1` / `DETECT-MEMORY-GUARD-1` / `SEC-FMT-IMPL-1` / `PDF-STREAM-FIX-1` 均 `closed_with_limitations`。
- `P09-AC3-DELETE-1`/`HARDEN-1` `closed_with_limitations`；**`P18` 4/8**（AC2 门槛、AC5 阻塞）；`P20` 6/7；`P16`/`P17` `done`。
- **[GOV-DEBT-CLEANUP-1](tasks/GOV-DEBT-CLEANUP-1.md)**：`superseded`；**[RUST-ENV-BASELINE-1](tasks/RUST-ENV-BASELINE-1.md)**：`closed_with_limitations`（v1 证据）。
- **Task 全量对账（2026-10-21 实算，可复算）**：`doc/tasks/` 共 **322** 个文件；终态 **309**（`done` 251 + `closed_with_limitations` 34 + `cancelled` 18 + `superseded` 6）；**非终态 13**（`ready` 2、`blocked` 7、`in_progress` 2、`in_review` 2；其中 11 个是未跟踪历史草稿，按原样保留、不并入提交）。
- **r38 裁定**：状态字段只说明生命周期记录，**不能单独证明 Task 仍活跃或已僵死**；不批量改状态；台账由 `tools/governance/task_ledger.py --write` 生成（已建）。
- DIR-4：同一失败上限 2 次；DIR-5：goal 轮次上限 1000。Coordinator=dsh，epoch=8，lease=39640ba370ec4a7cade35c1abd67f234（LEASE_VALID）。

## Gate 与保留项

Technical Gate=NOT_SATISFIED；private_registry_absence=UNPROVABLE；Owner Risk Acceptance=APPROVED；Disposition=WAIVED_BY_OWNER。H1/P2-1/13缺项、BC-AC5 PARTIAL、backlog 保留。用户未提交内容保留，不push/删除。**P20 发布 Gate 已实测通过**（`bundle==resource`；四页可达）。

## 当前权威指针

- DAG 与节点状态：[REBASELINE_PLAN](REBASELINE_PLAN.md)（唯一权威）。
- **治理主线分支**：`antigravity/P09-AC3-DELETE-HARDEN-1`（见 [WORKSPACE_GOVERNANCE](WORKSPACE_GOVERNANCE.md)）。
- 恢复点：[checkpoint-r12](../verification/PROJECT-ORCHESTRATION-20261016/)；日志 `.orchestrator/{INFLIGHT,OPLOG}`。
