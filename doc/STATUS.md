# Current Development Status

状态刷新：2026-10-19；主控 dsh（epoch 8，唯一 Active Coordinator）。

## 当前 Task

- 当前 Task：[P20](tasks/P20.md) **ready**。**AC1/AC2/AC7 ✅**；**AC3 ✅**（455.1 MB，见 [P20-MEM-OPT-1](tasks/P20-MEM-OPT-1.md)）；**AC6 ✅**（[P20-ISOLATION-1](tasks/P20-ISOLATION-1.md)：12/12）；**AC4 ◐**（延迟 36.0 ms；帧率见 [P20-AC4-FPS-1](tasks/P20-AC4-FPS-1.md)）；**AC5 ✅**（76.54 ms、零残留）。
- READY：[ARCH-DOC-REBASELINE](tasks/ARCH-DOC-REBASELINE.md)（AC7 已完成；AC1–AC3 PARTIAL、AC4–AC6 属消费者责任，不标 done）。
- P20：[FPS-1](tasks/P20-AC4-FPS-1.md) 集成 `approved`；AC3 `NOT_RUN`（Coordinator），AC5 `NOT_VERIFIED_BY_RULING`；HARDEN-1 R4 `changes_requested` → 已 `closed_with_limitations`，R4-01 由 HARDEN-2 承接；AC7 `NOT_RUN`。
- **新增**：[RUST-ENV-BASELINE-1](tasks/RUST-ENV-BASELINE-1.md) `proposed`（12 项 Rust 环境依赖失败）；**REBALANCE**：ZCode 遇 429 限流。
- **READY 待派**：[GOV-DEBT-CLEANUP-1](tasks/GOV-DEBT-CLEANUP-1.md) `blocked`（待用户裁决）。HARDEN-1/2 `in_review`（HARDEN-1 待 Codex；HARDEN-2 仅 AC5 需人工）。
- **P09 已收口**：[P09-AC3-DELETE-1](tasks/P09-AC3-DELETE-1.md) `closed_with_limitations`（R3 `changes_requested`）。**P09 AC3 保持 `BLOCKED`。** **HARDEN-1 删除路径闭环；AC4 判 FAIL 转出。**
- **T2**：4 failed 中 3 项在 `HEAD~` 已失败；1 项由 `d9f7a628c` 引入（v5 断言）。
- **P02**：16 份入库、3 份恢复 HEAD、`report.json` 待裁决；见 [逐份评估](../verification/P02-DOC-PROVENANCE-1/per-file-verdict.md)。
- **待裁决**：P18/G25/BL-12/13。
- DIR-2：Task Owner=codex；DIR-3：只保留一个 Active Coordinator；**DIR-4：同一失败上限 2 次，超限停手上报**（P20 两子项各经用户豁免 1 次）；DIR-5：goal 轮次上限 1000。
- Coordinator=dsh，epoch=8，lease=39640ba370ec4a7cade35c1abd67f234（LEASE_VALID）；20 份具名文件已按裁决处置，原件 20/20 备份于 `New Manga.workspace/P02-DOC-DISPOSAL-20261018/`。
- 恢复点：`verification/PROJECT-ORCHESTRATION-20261016/`（checkpoint-r12）；日志 `.orchestrator/{INFLIGHT,OPLOG}`。

## Gate 与保留项

Technical Gate=NOT_SATISFIED；private_registry_absence=UNPROVABLE；Owner Risk Acceptance=APPROVED；Disposition=WAIVED_BY_OWNER。H1/P2-1/13缺项、BC-AC5 PARTIAL、backlog 保留。用户未提交内容保留，不push/删除。**P20 发布 Gate 已实测通过**（`bundle==resource`；四页可达）。

## 当前权威指针

- DAG：[REBASELINE_PLAN](REBASELINE_PLAN.md)；READY=ARCH-DOC-REBASELINE、P20；BLOCKED=GOV-DEBT-CLEANUP-1；`proposed`=MANAGED-READ-ROOT-TRUST-1；`in_review`=PREVIEW-LIFECYCLE-RECLAIM-1、P09-AC3-DELETE-HARDEN-1（轮次见 Task 的 Review 指针）、P20-CLOSE-BOUND-HARDEN-2。
- 本轮证据：P09 [R3](../verification/P09-AC3-DELETE-1/codex-review-r3.md) + [T2](../verification/P09-AC3-DELETE-1/t2-fullsuite-triage.md)；P20 [CB-R4](../verification/P20-CLOSE-BOUND-HARDEN-1/codex-review-r4.md) + [FPS-R4](../verification/P20-AC4-FPS-1/codex-review-r4.md)。
