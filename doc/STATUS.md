# Current Development Status

状态刷新：2026-10-18；主控 dsh（epoch 8，唯一 Active Coordinator，用户裁决接管）。

## 当前 Task

- 当前 Task：[P20](tasks/P20.md) **ready**（Windows 发布）。**AC1/AC2/AC7 ✅**；**AC3 ✅**（455.1 MB ≤ 480 MB，见 [P20-MEM-OPT-1](tasks/P20-MEM-OPT-1.md)）；**AC6 ✅**（[P20-ISOLATION-1](tasks/P20-ISOLATION-1.md)：注入 12/12）；**AC4 ◐**（延迟 avg 36.0 ms；帧率见 [P20-AC4-FPS-1](tasks/P20-AC4-FPS-1.md)）；**AC5 ✅**（76.54 ms、零残留）。
- READY：[ARCH-DOC-REBASELINE](tasks/ARCH-DOC-REBASELINE.md)（AC7 已完成；AC1–AC3 PARTIAL、AC4–AC6 属消费者责任，不标 done）。
- **P20 子项**：[P20-AC4-FPS-1](tasks/P20-AC4-FPS-1.md) `approved` / 已集成（`16b995247`）；AC3 单页与 Webtoon 实测仍 `NOT_RUN`，由 Coordinator 执行，AC5 `NOT_VERIFIED_BY_RULING`。[P20-CLOSE-BOUND-HARDEN-1](tasks/P20-CLOSE-BOUND-HARDEN-1.md) 已交付 `35770fe91`，待 Codex R4 复审结论。
- **新增**：[RUST-ENV-BASELINE-1](tasks/RUST-ENV-BASELINE-1.md) `proposed`（12 项 Rust 环境依赖失败）；**REBALANCE**：ZCode 遇 429 限流，工作改派。
- **READY 待派**：[P09-AC3-DELETE-HARDEN-1](tasks/P09-AC3-DELETE-HARDEN-1.md)（Owner=Antigravity）；[GOV-DEBT-CLEANUP-1](tasks/GOV-DEBT-CLEANUP-1.md) `blocked`（待用户裁决）。
- **P09 已收口**：[P09-AC3-DELETE-1](tasks/P09-AC3-DELETE-1.md) `closed_with_limitations`（R3 `changes_requested`，DIR-4 上限）。**P09 AC3 保持 `BLOCKED`。**
- **T2**：4 failed 中 3 项在 `HEAD~` 已失败；1 项由 `d9f7a628c` 引入（v5 断言）。
- **P02**：16 份入库、3 份恢复 HEAD、`report.json` 待裁决；见 [逐份评估](../verification/P02-DOC-PROVENANCE-1/per-file-verdict.md)。
- **待裁决**：P18/G25/BL-12/13。
- DIR-2：Task Owner=codex；DIR-3：只保留一个 Active Coordinator；**DIR-4：同一失败上限 2 次，超限停手上报**（P20 两子项各经用户豁免 1 次）；DIR-5：goal 轮次上限 1000。
- Coordinator=dsh，epoch=8，lease=39640ba370ec4a7cade35c1abd67f234（LEASE_VALID）；20 份具名文件已按裁决处置，原件 20/20 备份于 `New Manga.workspace/P02-DOC-DISPOSAL-20261018/`。
- 恢复点：`verification/PROJECT-ORCHESTRATION-20261016/`（checkpoint-r12）；日志 `.orchestrator/{INFLIGHT,OPLOG}`。

## Gate 与保留项

P02 父项限定关闭。Technical Gate=NOT_SATISFIED；private_registry_absence=UNPROVABLE；Owner Risk Acceptance=APPROVED；Disposition=WAIVED_BY_OWNER。H1/P2-1/13缺项、BC-AC5 PARTIAL、backlog 保留。用户未提交内容保留，不push/删除。**P20 发布 Gate 已实测通过**（`bundle==resource`；四页可达）。

## 当前权威指针

- DAG：[REBASELINE_PLAN](REBASELINE_PLAN.md)；READY=ARCH-DOC-REBASELINE、P20、[P09-AC3-DELETE-HARDEN-1](tasks/P09-AC3-DELETE-HARDEN-1.md)；BLOCKED=GOV-DEBT-CLEANUP-1。
- 本轮证据：P09 [R3](../verification/P09-AC3-DELETE-1/codex-review-r3.md) + [T2](../verification/P09-AC3-DELETE-1/t2-fullsuite-triage.md)；P20 [CB-R3](../verification/P20-CLOSE-BOUND-HARDEN-1/codex-review-r3.md) + [FPS-R4](../verification/P20-AC4-FPS-1/codex-review-r4.md)。
