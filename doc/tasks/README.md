# Task Index

仅导航；DAG 以 [Plan](../REBASELINE_PLAN.md) 为准，运行以 [STATUS](../STATUS.md) 为准。当前 Lead / Architect / Integrator：DeepSeek Harness（2026-10-25 接管，见[接管记录](../GOVERNANCE_TAKEOVER_2026-10-25.md)）。

- 当前 Task：**无活动 Task**（以 STATUS 为准）。最近完成 [FEA-07-RESIDUAL-4](FEA-07-RESIDUAL-4.md) `done`（L-R4b-1 legacy `MainWindow.Show()` 真实 AppData 零写入；r2 approved）。
- 下一候选（待 DSH 裁决）：[FEA-11-HOST-AUTH-3](FEA-11-HOST-AUTH-3.md) `proposed`（C-17 崩溃恢复 grant 语义）；`README` 导航对账、`2C-RESIDUAL-1`（typed-stop 次序）为 DAG 指名候选。
- READY：以 Plan 声明为准；**当前无 READY 节点**。不得据历史导航重开或释放已完成 Task。

## 历史遗留非终态（不代表当前工作）

> 以下 Task 的状态字段只记录生命周期历史，**不证明活性**（r38）；逐项处置需独立证据，不得批量关闭。

- [GIT-CLEAN-PUBLICATION-1](GIT-CLEAN-PUBLICATION-1.md) `in_review`（历史：独立源码快照准备；候选 root `e34a90d00`）
- [GIT-CLEAN-RUST-ISOLATION-1](GIT-CLEAN-RUST-ISOLATION-1.md) `in_review`（历史：Rust 测试隔离；`1829a38`）
- [GIT-CLEAN-RUST-CAPACITY-DESIGN-1](GIT-CLEAN-RUST-CAPACITY-DESIGN-1.md) `ready`（历史：仅设计；**不在当前 READY DAG**）
- [GIT-CLEAN-PUBLICATION-DIAG-1](GIT-CLEAN-PUBLICATION-DIAG-1.md) `approved`（历史：仅诊断）
- [GIT-CLEAN-CORE-ENV-2](GIT-CLEAN-CORE-ENV-2.md) `proposed`（历史：V2–V5 未冻结）
- [NEW-MANGA-V1-FULL-AUDIT](NEW-MANGA-V1-FULL-AUDIT.md) `blocked`（resume=in_progress；私有素材不传播）
- [V1-RELEASE-SIGNING-1](V1-RELEASE-SIGNING-1.md) `closed_with_limitations`（v1 代码签名与发布签核；等待用户证书）

## 历史导航（不构成当前授权）

- [PROJECT-ROADMAP-RELEASE](PROJECT-ROADMAP-RELEASE.md)：历史路线恢复与 Gate 复核。
- [P22-REBASE-1](P22-REBASE-1.md)：done / integrated，非下一实施切片；原 P22/P04 来源与阻塞按原记录保留。
- [P02-MAINLINE-INTEGRATION](P02-MAINLINE-INTEGRATION.md)：历史产品收口；P02 总入口限定关闭。
- 其它历史 Task 不按旧 ready/in_progress 激活；不再释放 Legacy 实施。
