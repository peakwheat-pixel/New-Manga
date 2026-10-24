# Task Index

仅导航；DAG 以 [Plan](../REBASELINE_PLAN.md) 为准，运行以 [STATUS](../STATUS.md) 为准。当前 Lead / Architect / Integrator：DeepSeek Harness（2026-10-25 接管，见[接管记录](../GOVERNANCE_TAKEOVER_2026-10-25.md)）。

- 当前 Task：[GIT-CLEAN-PUBLICATION-1](GIT-CLEAN-PUBLICATION-1.md) `in_review`；候选 root `e34a90d00`，push-gate 新 Appointment 独立 Review 后由 DSH 执行安全 push。
- Rust：[GIT-CLEAN-RUST-ISOLATION-1](GIT-CLEAN-RUST-ISOLATION-1.md) `in_review`（1829a38；默认并发双过；饱和 0/32，DSH r2 blocked 保留）。
- 容量设计：[GIT-CLEAN-RUST-CAPACITY-DESIGN-1](GIT-CLEAN-RUST-CAPACITY-DESIGN-1.md) `ready`（ZCode，仅设计）。
- 诊断：[GIT-CLEAN-PUBLICATION-DIAG-1](GIT-CLEAN-PUBLICATION-DIAG-1.md) `approved`（仅诊断，不集成、不 done）。
- 环境：[GIT-CLEAN-CORE-ENV-2](GIT-CLEAN-CORE-ENV-2.md) `proposed`（V2–V5 未冻结，不运行）。
- 全审：[NEW-MANGA-V1-FULL-AUDIT](NEW-MANGA-V1-FULL-AUDIT.md) `blocked`（resume=in_progress；私有素材不传播）。
- 发布签核：[V1-RELEASE-SIGNING-1](V1-RELEASE-SIGNING-1.md) `in_review`（待证书/发布签核，无当前执行）。
- READY：以 Plan 声明为准；当前为 `GIT-CLEAN-RUST-CAPACITY-DESIGN-1`。不得据历史导航重开或释放已完成 Task。

## 历史导航（不构成当前授权）

- [PROJECT-ROADMAP-RELEASE](PROJECT-ROADMAP-RELEASE.md)：历史路线恢复与 Gate 复核。
- [P22-REBASE-1](P22-REBASE-1.md)：done / integrated，非下一实施切片；原 P22/P04 来源与阻塞按原记录保留。
- [P02-MAINLINE-INTEGRATION](P02-MAINLINE-INTEGRATION.md)：历史产品收口；P02 总入口限定关闭。
- 其它历史 Task 不按旧 ready/in_progress 激活；不再释放 Legacy 实施。
