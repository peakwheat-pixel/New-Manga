你是 New Manga 项目的 P04 Owner：Antigravity。请在现有 P04 branch/worktree 中按独立实现 Review R2 返修，生成新的固定交付 head 与 Handoff；Reviewer 仍是 DeepSeek Harness，不能自审。

## 固定 Task 与交付

- Task：`doc/tasks/P04.md`，ID=`P04`。
- 返修 base / 当前固定 owner delivery HEAD：`42b87f6bb6314fb42df3592f15a9fcd69866739b`，tree=`e642151118cebdbb21cc283afc86121345ee52e0`。
- 分支：`agent/antigravity/P04-prod-command-concurrency`。
- worktree：`G:/CODEX/New Manga.worktrees/P04-prod-command-concurrency-antigravity`。
- 独立 R2 Review 报告：`G:/CODEX/New Manga/verification/P04/dsh-p04-owner-review-r2.stdout.md`，decision=`CHANGES_REQUESTED`，unresolved P0/P1/P2/P3=`0/1/3/4`。如该绝对路径在沙箱不可见，按下列 finding 摘要执行，并明确披露。

## 冻结允许路径

- `apps/desktop/src-tauri/src/library_bridge.rs`：仅 `#[cfg(test)]` 测试、helper、同步/诊断设施；生产代码零改动。
- `verification/P04/**`。
- `doc/tasks/P04.md` 的运行/交付记录、对应 Handoff；不要改 frontmatter 状态。`STATUS`、`REBASELINE_PLAN`、`00_INDEX` 和新修复 Task 由 Codex 维护。

## 必须处理的 R2 findings

1. **R2-001 P1**：当前确定性交错静态上必然错配：Alpha 写后在 hook 阻塞；Beta 收到信号后写第二条请求并先拿 stdout 锁；sidecar 按 stdin 到达顺序回 Alpha、Beta 两条响应，因此 Beta 读到 Alpha 响应。该 P04 Task 禁止改生产行为，必须按 AC3 记录为确定性负向诊断，并由 Codex另立独立生产修复 Task。由于 Cargo 被 Build Barrier 禁止，当前只能写 `static_expected_behavior=FAIL`、`runtime=BLOCKED / NOT_RUN`；**不可**伪造实际 sidecar log，也不可把运行时 `behavior=FAIL`、AC2 或测试写成已实测。不要把 finding 标 CLOSED 或请求集成。
2. **R2-002 P2**：明确这是 AC3 diagnostic/reproducer，不是通过型回归测试；cargo exit 0 不能表示响应归属 PASS。保留可执行诊断路径，并在注释、Task 测试行和 Handoff 中清楚区分诊断输出与 AC PASS。不要添加与 AC3 冲突的“错配即 panic”断言。
3. **R2-003 P2**：更新 `antigravity-owner-implementation-r1.handoff.md` 过期 AC2 描述（严格归属断言、Barrier、旧日志名）；与现状和新 revision Handoff 一致。
4. **R2-004 P2**：判别力 verdict artefact 写入失败必须显式失败或标记该次运行不可用；不得吞掉 Rust 文件 open/write 错误或 sidecar 日志错误后仍留下可误读的 PASS。
5. **R2-005 P3**：更正 `round_trip_with_phase_hook` 过期代码注释。
6. **R2-006 P3**：在 Handoff 登记异常路径可能导致测试挂起；若可用最小 test-only bounded wait 处理，可实现并静态自检；否则明确 deferred/NOTED，不宣称已解决。
7. **R2-007 P3**：更新 P04 Task 运行/交付记录，引用真实 Owner Handoff、DSH Review 报告，并保持 Cargo tests=`BLOCKED / NOT_RUN`。
8. **R2-008 P3**：给唯一命名的每次诊断文件记录保留策略；不得清理/删除既有或来源不明文件。

## 安全与验收

- 不修改生产 `round_trip`、IPC/Schema/依赖或产品行为；P04 只交付 AC3 诊断/交付事实修正。Codex 会把 P04 置为 blocked 并建立独立修复 Task。
- 禁止运行 Cargo/Rust/Tauri/build/sidecar/产品测试、Sandbox、host inventory；Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`。可运行只读 `git diff --check`。
- 保护 worktree 中已有 7 项未跟踪 Antigravity/DSH 工件；不清理、不暂存、不覆盖。
- 自行提交时只 stage 冻结允许路径内由本次创建/修改的文件；不要 stage 其他未跟踪内容。
- 交付后给出固定 commit/head/tree、逐项 finding disposition、改动路径、`git diff --check` 命令/exit（若运行）、所有未运行检查状态、Handoff 路径。更新对应 Handoff 的 `implementation_head`；R2 reviewed head 不可冒充新 review head。Codex 将派 DSH 对新固定 head 做 R3 非作者复审。
