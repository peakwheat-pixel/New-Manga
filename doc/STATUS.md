# Current Development Status

状态刷新：2026-10-20；主控 dsh（epoch 8，唯一 Active Coordinator）。

## 当前 Task

- 当前 Task：[P20](tasks/P20.md) **ready**。**AC1/AC2/AC7 ✅**；**AC3 ✅**（455.1 MB，见 [P20-MEM-OPT-1](tasks/P20-MEM-OPT-1.md)）；**AC6 ✅**（[P20-ISOLATION-1](tasks/P20-ISOLATION-1.md)：12/12）；**AC4 ◐**（延迟 36.0 ms；帧率见 [P20-AC4-FPS-1](tasks/P20-AC4-FPS-1.md)）；**AC5 ✅**（76.54 ms、零残留）。
- READY：[ARCH-DOC-REBASELINE](tasks/ARCH-DOC-REBASELINE.md)（AC7 已完成；AC1–AC3 PARTIAL、AC4–AC6 属消费者责任，不标 done）。
- P20：[FPS-1](tasks/P20-AC4-FPS-1.md) 集成 `approved`；AC3 `NOT_RUN`（Coordinator），AC5 `NOT_VERIFIED_BY_RULING`；HARDEN-1 R4 → `closed_with_limitations`；**R4-01 由 [HARDEN-2](tasks/P20-CLOSE-BOUND-HARDEN-2.md) 承接完毕（`done`，7/7；AC5 桌面实测 54.48 ms 零残留）**；AC7 `NOT_RUN`。
- **新增**：[RUST-ENV-BASELINE-1](tasks/RUST-ENV-BASELINE-1.md) `proposed`（12 项 Rust 环境依赖失败）；**REBALANCE**：ZCode 遇 429 限流。
- **治理债已收束**：11 个 GOV-* Task 全部终态（9 `done`、2 `closed_with_limitations`；PIN-LINEAGE-1 按 r28 停改，checker 未改）。裁定 r20–r29 在 `verification/P09-GOVERNANCE-DEBT-20261019/`。
- **[GOV-DEBT-CLEANUP-1](tasks/GOV-DEBT-CLEANUP-1.md)**：`blocked`（待用户裁决）。
- **P09 已收口**：[P09-AC3-DELETE-1](tasks/P09-AC3-DELETE-1.md) `closed_with_limitations`（R3 `changes_requested`）。**P09 AC3 保持 `BLOCKED`。** **HARDEN-1 删除路径闭环；AC4 判 FAIL 转出。**
- **P02**：16 入库、3 恢复 HEAD、`report.json` 待裁决（见 P02-DOC-PROVENANCE-1）。
- **待裁决**：P18/G25/BL-12/13。
- DIR-2：Task Owner=codex；DIR-3：只保留一个 Active Coordinator；**DIR-4：同一失败上限 2 次，超限停手上报**（P20 两子项各经用户豁免 1 次）；DIR-5：goal 轮次上限 1000。
- Coordinator=dsh，epoch=8，lease=39640ba370ec4a7cade35c1abd67f234（LEASE_VALID）；20 份具名文件已按裁决处置，原件 20/20 备份于 `New Manga.workspace/P02-DOC-DISPOSAL-20261018/`。
- 恢复点：`verification/PROJECT-ORCHESTRATION-20261016/`（checkpoint-r12）；日志 `.orchestrator/{INFLIGHT,OPLOG}`。

## Gate 与保留项

Technical Gate=NOT_SATISFIED；private_registry_absence=UNPROVABLE；Owner Risk Acceptance=APPROVED；Disposition=WAIVED_BY_OWNER。H1/P2-1/13缺项、BC-AC5 PARTIAL、backlog 保留。用户未提交内容保留，不push/删除。**P20 发布 Gate 已实测通过**（`bundle==resource`；四页可达）。

## 当前权威指针

- DAG 与节点状态：[REBASELINE_PLAN](REBASELINE_PLAN.md)（唯一权威）。
- 当前 Active Task 与运行状态：见本文件「当前 Task」；Gate 与保留项：见本文件「Gate 与保留项」。
- 本轮证据：治理债 r20–r29 裁定见 `verification/P09-GOVERNANCE-DEBT-20261019/`。
- 恢复点：[checkpoint-r12](../verification/PROJECT-ORCHESTRATION-20261016/)；日志 `.orchestrator/{INFLIGHT,OPLOG}`。
