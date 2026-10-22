你是 New Manga 项目的非作者独立 Reviewer：DeepSeek Harness。请续接本会话之前对 P04 的 R2 Review，对 Antigravity 的 R2 修订执行只读 R3 复审。不要修改任何文件，不要运行 Cargo/Rust/Tauri/build/sidecar/产品测试/Sandbox/host inventory。

## 固定对象

- Task=P04；Owner=Antigravity；Reviewer=DeepSeek Harness；Integrator=Codex。
- 原始 Review base=`9ea4e312fa01470478946a557135791b5a044cb3`。
- 上轮 reviewed HEAD=`42b87f6bb6314fb42df3592f15a9fcd69866739b`，tree=`e642151118cebdbb21cc283afc86121345ee52e0`。
- 本轮 implementation head=`eedbda05ef42d61b35149c4d3d54ac0804b7b80d`；最新 handoff/delivery HEAD=`ec44a4891d624c88e89abfe2c13d9e7e072b9e5e`，tree=`864bfdf0368fb912b148021d5352258341fef362`。
- Owner linked worktree=`G:/CODEX/New Manga.worktrees/P04-prod-command-concurrency-antigravity`，branch=`agent/antigravity/P04-prod-command-concurrency`。
- DSH CLI 会话归属该 P04 worktree；Codex 已在本机独立验证上述 HEAD/tree、`42b87f6..ec44a489` 的变更路径只有 `library_bridge.rs`、P04 Task/Handoff 和测试 sidecar，且 `git diff --check 9ea4e312..HEAD` EXIT=0。你自己的 Git 命令若不可运行，请如实写 `BLOCKED / NOT_RUN`，不要据此猜测。

## 必须逐项复核 R2 findings

R2 decision=`CHANGES_REQUESTED`，P0/P1/P2/P3=`0/1/3/4`。请逐项重新打开实现、Task 与两份 Handoff，核验：

1. **R2-001 P1**：AC2 只能被标为 AC3 deterministic negative reproducer；`static_expected_behavior=FAIL` 是基于源代码推导，不是 runtime verdict；P04 保持 blocked、不请求集成；不得伪造 sidecar log。
2. **R2-002 P2**：Cargo exit 0 不得被描述为 response ownership PASS；诊断器不得假装是通过型 acceptance gate。
3. **R2-003 P2**：旧实现 Handoff 不再声称严格归属断言、Barrier、旧诊断文件名；准确记录 `#[cfg(test)]` hook。
4. **R2-004 P2**：Rust verdict artifact 与 Python sidecar logging 失败均显式传播，不再静默吞错。
5. **R2-005 P3**：不存在过时 `round_trip_with_phase_hook` 注释。
6. **R2-006 P3**：`recv_timeout` bounded wait 确实覆盖相关 channel wait，Handoff 准确说明剩余挂起/Drop 限制。
7. **R2-007 P3**：Task/Handoff/Review 状态记录不互相矛盾，运行仍 `BLOCKED / NOT_RUN`。
8. **R2-008 P3**：唯一诊断日志保留策略明确，不会通配符删除未知或旧文件。

## 评审要求

- 检查完整 `9ea4e312..ec44a489` 差异，重点读 `library_bridge.rs` 的真实 test seam 与时序、sidecar、Task、R1 implementation Handoff、R2 revision Handoff；只报告可执行且有代码/行证据的 finding。
- 审查 commit/tree、allowed paths、测试证据可用性与 P04 AC1–AC4。准确区分静态预期与运行状态。P02 Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`；Cargo AC1/AC2 与集成后验证必须保持 `BLOCKED / NOT_RUN`。
- 返回简体中文 Review：decision 仅取 `APPROVED | CHANGES_REQUESTED | NOT_VERIFIED | BLOCKED_BY_MISSING_EVIDENCE`；列 finding ID/严重级别/精确路径与行/根因/最小修复；列逐条关闭状态、AC 状态、覆盖与未覆盖范围、是否可集成及下一条动作。
- R2-001 的 AC3 负向复现分类不是 P04 完成；不得将 P04 标为 done，也不得解除 P02 Build Barrier。
- 输出最终报告到 `verification/P04/dsh-p04-owner-review-r3.stdout.md`。即便本会话已读过上轮报告，也请对新 fixed HEAD 重新核查。
