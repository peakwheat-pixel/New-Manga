# M2-C2 contract-revision release — 2026-09-26

- Authorization: 用户于 2026-09-26 批准首选方案——登记并释放 M2-C2 Typed IPC Contract 修订 Task，把 M2-S1 §7 阈值裁决（T1–T7）与 M2-S2 的映射 ID/句柄校验结论落入 [M2-C1 Typed IPC Contract](../../doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md) 修订版，作为大媒体 runtime Task 的需求基线。用户同时采纳「Owner 改派 ZCode」的改派选项；Codex（额度恢复前由代行会话）保留范围冻结与集成职责。
- Owner: ZCode。Reviewer: DeepSeek Harness（非作者）。Integrator: Codex。
- Dependencies: M2-C1 `done`（Contract blob `4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3`）；M2-S1 `done`（merge `4103493f`）；M2-S2 `done`（integration `bf1d1230`）；阈值裁决与安全验证结论均已集成（收尾治理 commit `3f468e6e`）。
- Release base: `3f468e6eb791ab112e38afaff50f511eb2ebc0c9`（`master`，M2-S2 集成收尾提交）。
- Owner branch: `agent/zcode/M2-C2-typed-ipc-contract-revision`，worktree `G:/CODEX/New Manga.worktrees/M2-C2-zcode`，由 Codex 于本次释放基于 release base 创建。
- Scope: 契约文档原位修订（`1.0`→`1.1`）：§10 增补 T1–T7 阈值与安全语义条款（句柄校验解析、映射 ID 保密、类型化错误码最小集、权重独立通道）、§11 DEFERRED 表 large-media 行处置更新、版本与修订记录。修订不得放松既有保护语义，不得宣称已实现；§1–§9/§12 默认不动。
- Owner allowed paths: `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`、`doc/tasks/M2-C2.md`、one new `doc/handoffs/M2-C2-*.md`、`verification/M2-C2/**`。
- Excluded: `src/**`、`tests/**`、`packaging/**`、`src-tauri/**`、React/QML、dependencies、Schema、其它 `doc/contracts/**`、AD-001、M2-S1/M2-S2 工件（裁决文档只读）、治理导航与任何其它 Task。Reviewer report path: `doc/reviews/M2-C2-<reviewed-head>.md`（DeepSeek Harness 专属）。
- Gate at release: `ready / CONTRACT_REVISION_RELEASED`；Owner 修订、独立 Review 与集成均未开始。本 Task 完成不授权 runtime 实现；M2-S1 §8.1 条件性建议与 §8.3 前置条件继续有效；runtime Task 需另行释放。
- Dispatch: 可转发 Owner 指令由 Codex 在本次治理提交的会话回复中提供；Owner 开工前须完成 C2-AC1 基线自检并发现不一致即停。
