# M2-S2 security-verification release — 2026-09-26

- Authorization: 用户于 2026-09-26 明确指令（因 Codex 额度耗尽，ZCode 会话代行 Codex 角色执行本次治理）：先取得 M2-S1 报告 §7 的产品阈值裁决，再以 `master=67c3d56e` 登记并释放 M2-S2，Owner=ZCode、Reviewer=Antigravity。裁决记录：[product-thresholds-ruling-67c3d56.md](../M2-S1/product-thresholds-ruling-67c3d56.md)。
- Dependencies: M2-S1 `done`（merge `4103493fd63c0133f62a659390d0367d1c2a98ab`）；M2-C1 `done`（Contract blob `4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3`）。
- Release base: `67c3d56ea77acd5b214877509bbcd1cffe5890f7`（`master`，M2-S1 集成收尾提交）。
- Owner: ZCode。Reviewer: Antigravity（非作者；本 Task 非 Antigravity 实现，符合协作协议独立性要求）。Integrator: Codex（后续额度恢复后由 Codex 或再次代行执行集成）。
- Owner branch: `agent/zcode/M2-S2-resource-channel-security`，worktree `G:/CODEX/New Manga.worktrees/M2-S2-zcode`，由 Codex 于本次释放基于 release base 创建；Owner 在该 worktree 将 `doc/tasks/M2-S2.md` 状态由 `ready` 推进为 `in_progress` 后开始实现。
- Scope: S1-B11（TOCTOU open-then-verify-from-handle 防护）与 S1-B12（Core 侧映射 ID 保密）的隔离原型验证；需求源为 M2-S1 §8.2 解除条件与本裁决 T5。研究/验证性质：不触碰产品代码。
- Owner allowed paths: `doc/tasks/M2-S2.md`、`doc/research/M2-S2_SECURITY_VERIFICATION_SPIKE.md`、one new `doc/handoffs/M2-S2-*.md`、`verification/M2-S2/**`。Owner 必须保留本释放记录。
- Excluded: `src/**`、`tests/**`、`packaging/**`、`src-tauri/**`、React/QML、dependencies、Schema、shared Contract（`doc/contracts/**`）、AD-001、M2-S1 工件（含裁决文档，只读）、治理导航与任何其它 Task 文件。Reviewer report path: `doc/reviews/M2-S2-<reviewed-head>.md`（Antigravity 专属）。
- Gate at release: `ready / SECURITY_VERIFICATION_RELEASED`；Owner 实现、独立 Review 与集成均未开始。本 Task 完成不解除 S1-B3/S1-B8 依赖的残留验证项，不构成产品安全保证，不授权大媒体 runtime 实现。
- Dispatch: 可转发 Owner 指令由 Codex 在治理提交的会话回复中提供；Owner 开工前须完成 S2-AC1 基线自检并发现不一致即停。
