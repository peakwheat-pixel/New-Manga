# Current Development Status

状态刷新：2026-10-20；主控 dsh（epoch 8，唯一 Active Coordinator）。

## 当前 Task

- 当前 Task：[WORKSPACE-CONSOLIDATION-1](tasks/WORKSPACE-CONSOLIDATION-1.md) **`in_review`**（r210=`approved_with_conditions`，仅批准 F-01..F-04 处置、不批准关闭：132 worktree、93 分支（19 未合并均已归档）、18 个保护资源受影响；P03 已保全；49.48 GiB 为删除收据逻辑字节；AC1/2/3/6/7/9 PARTIAL；详见 Task 与 codex-review-r210.md）。最近收口：[M2-PROD-DETECT-ENV-1](tasks/M2-PROD-DETECT-ENV-1.md)（`closed_with_limitations`：检测链路本机已可用，`tests/providers` 442 passed；原「离线」为误判）。
- **WORKSPACE-CONSOLIDATION-1**：r208/r209=`changes_requested` → r210=`approved_with_conditions`；Task 未 done；F-01 系统 Temp 演练自我裁定保留原状；残余风险与 ignored 缺口待用户/Reviewer 裁决；不得再清理/GC/prune。
- **[ARCH-DOC-REBASELINE](tasks/ARCH-DOC-REBASELINE.md)**：`closed_with_limitations`（r37 的 7+1：7 Gate 达成 + AC-CONSUMPTION `PARTIAL`，6/8 消费者已处置；**ZCode 设计 Gate 与第二环境无活动 Task**）。
- `DETECT-TILING-1` / `DETECT-MEMORY-GUARD-1` / `SEC-FMT-IMPL-1` / `PDF-STREAM-FIX-1` 均 `closed_with_limitations`。
- `P09-AC3-DELETE-1`/`HARDEN-1` `closed_with_limitations`；**`P18` 4/8**（AC2 门槛、AC5 阻塞）；`P20` 6/7；`P16`/`P17` `done`。
- **[GOV-DEBT-CLEANUP-1](tasks/GOV-DEBT-CLEANUP-1.md)**：`blocked`（待用户裁决）。**[RUST-ENV-BASELINE-1](tasks/RUST-ENV-BASELINE-1.md)**：`proposed`。**两者均在 Plan 内**（r38 更正）。
- **Task 全量对账（2026-10-20 实算，可复算）**：`doc/tasks/` 共 **317** 个文件；终态 **276**（`done` 248 + `closed_with_limitations` 27 + `cancelled` 1）；**非终态 40**（`blocked` 10、`proposed` 10、`in_review` 5、`approved` 5、`ready` 4、`changes_requested` 4、`in_progress` 2）。**其中 3 个在 Plan 内，37 个不在。**
- **r38 裁定**：状态字段只说明生命周期记录，**不能单独证明 Task 仍活跃或已僵死**；不批量改状态；**4 个旧栈 `ready` Task 不能据此开工**；需建立可复算台账（尚未建）。
- DIR-4：同一失败上限 2 次；DIR-5：goal 轮次上限 1000。Coordinator=dsh，epoch=8，lease=39640ba370ec4a7cade35c1abd67f234（LEASE_VALID）。

## Gate 与保留项

Technical Gate=NOT_SATISFIED；private_registry_absence=UNPROVABLE；Owner Risk Acceptance=APPROVED；Disposition=WAIVED_BY_OWNER。H1/P2-1/13缺项、BC-AC5 PARTIAL、backlog 保留。用户未提交内容保留，不push/删除。**P20 发布 Gate 已实测通过**（`bundle==resource`；四页可达）。

## 当前权威指针

- DAG 与节点状态：[REBASELINE_PLAN](REBASELINE_PLAN.md)（唯一权威）。
- **治理主线分支**：`antigravity/P09-AC3-DELETE-HARDEN-1`（见 [WORKSPACE_GOVERNANCE](WORKSPACE_GOVERNANCE.md)）。
- 恢复点：[checkpoint-r12](../verification/PROJECT-ORCHESTRATION-20261016/)；日志 `.orchestrator/{INFLIGHT,OPLOG}`。
