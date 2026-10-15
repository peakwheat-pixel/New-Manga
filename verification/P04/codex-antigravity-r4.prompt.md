你正在 New Manga 项目中执行 P04 Owner R4 修正。请先阅读仓库 `AGENTS.md`、`doc/09_COLLABORATION.md`、`doc/tasks/P04.md`、`verification/P04/dsh-p04-owner-review-r3.stdout.md` 与现有 R2 Handoff，再按以下冻结范围工作。

## 任务与基线

- Task：P04 生产命令族与同通道桥接并发定向验证，修复独立 R3 Review 的 R3-1 与 R3-4。
- Owner：Antigravity。独立 Reviewer：DeepSeek Harness。Integrator：Codex。
- 当前工作区：`G:/CODEX/New Manga.worktrees/P04-prod-command-concurrency-antigravity`
- 分支：`agent/antigravity/P04-prod-command-concurrency`
- 当前 HEAD：`5ea8304ae1670e079b7a496e08fbdea6f656156f`。此 commit 已归档 R2 Review；R3 审阅的实现交付是 `ec44a4891d624c88e89abfe2c13d9e7e072b9e5e`，本次以当前 HEAD 为代码基线。
- R3 总结：`CHANGES_REQUESTED`，0 P0 / 0 P1 / 3 P2 / 1 P3。P04 整体仍 `blocked`，`blocked_by: [P22]`。

## 唯一写入范围

1. `apps/desktop/src-tauri/src/library_bridge.rs`：只给 `same_channel_concurrent_round_trips_keep_response_ownership` 这个确定性 AC3 负向诊断测试加 `#[ignore = "..."]`，并采用清晰简短的原因说明。生产代码和其他测试不得改动。
2. `verification/P04/antigravity-owner-revision-r2.handoff.md`：修正 R3-4 指出的错误安全描述。准确说明 `recv_timeout` 仅限制 mpsc 接收等待；sidecar `read_line` 或线程 `join` 仍可能无界等待，所以 `Drop` 的 5 秒超时并不能保护该挂起路径。只修事实与调用说明，不增加 watchdog 或产品范围。

可以将最终交付报告写到新的 `verification/P04/antigravity-owner-revision-r3.handoff.md`；不得覆盖任何现有文件。除上述两处源/交付路径及这个新报告外，不得修改其他文件。特别不得改 `doc/tasks/P04.md`、共享计划/状态、P22、DSH/Codex 证据、sidecar、生产逻辑或其他未跟踪文件。

## 验收

- 负向诊断不再进入普通 Cargo 默认测试集合；Handoff 说明仅能在 P02 明确批准且准备好 `M2RC1_PYTHON` 的隔离环境中，通过明确 ignored 选择器有意运行，例如目标过滤器加 `-- --ignored`。不要执行此 Cargo 命令。
- Handoff 精确描述 `recv_timeout` 与无界 `read_line` / `join` 的边界。
- 未改变生产行为、IPC、schema、依赖或 P02 Build Gate 状态。
- 只运行 `git diff --check` 和 Git 静态状态/差异核对；禁止 Cargo、Rust 编译/测试、Tauri、sidecar、GUI、任何 build、Sandbox 或宿主写权限探测。
- 仅暂存以上两个已授权文件并创建一个固定 commit，提交前确认 staged path list 完全匹配；不触碰已有未提交 Task 记录或未跟踪证据。
- 提交后提供 commit SHA、变更路径、静态检查实际结果、未运行项和更新后的 Handoff 路径。不要声称 P04 完成或 Gate 通过。
