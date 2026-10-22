你是 New Manga 项目的独立 Reviewer DeepSeek Harness。请只读审查 P04 Owner Antigravity 对 DSH R3 Review 所作的 R4 修正。不得修改文件，不得运行测试、构建、Cargo、Rust、Tauri、sidecar、GUI、Sandbox 或宿主写权限探测。

## 固定对象

- Task：`doc/tasks/P04.md`，当前整体仍为 `blocked`、`blocked_by: [P22]`。
- Owner：Antigravity；Reviewer：DeepSeek Harness（你）；Integrator：Codex。
- 工作区：`G:/CODEX/New Manga.worktrees/P04-prod-command-concurrency-antigravity`
- 分支：`agent/antigravity/P04-prod-command-concurrency`
- 修正基线：`5ea8304ae1670e079b7a496e08fbdea6f656156f`
- 你的唯一待审 commit：`faea1a2c9e19f4817fd792290e91324f047529f9`
- 父 commit：`5ea8304ae1670e079b7a496e08fbdea6f656156f`
- tree：`eb0cc832531005a40d7a7294daf12cd0baa30a3d`
- Codex 复核的唯一差异路径：`apps/desktop/src-tauri/src/library_bridge.rs`、`verification/P04/antigravity-owner-revision-r2.handoff.md`。如无法独立读取 Git 元数据，请在报告中明确说明，不要假称核验过。
- R3 原报告：`verification/P04/dsh-p04-owner-review-r3.stdout.md`（总体 CHANGES_REQUESTED，包含待修 R3-1/P2 和 R3-4/P3）。

## 审查重点

1. R3-1：唯一目标测试 `same_channel_concurrent_round_trips_keep_response_ownership` 是否被准确标记为 `#[ignore]`，从默认 Cargo 集合排除；explicit ignored 命令是否仍只会在 P02 批准且设置 `M2RC1_PYTHON` 的隔离环境中执行；是否误改其他测试/生产逻辑。
2. R3-4：Handoff 是否准确区分 `recv_timeout` 只限制 mpsc 等待、`stdout.read_line` 与线程 `join` 仍可能无界挂起、此时 `Drop` 的 5 秒 budget 不可达；不得声称该问题已被修复或由 Drop 保护。变更是否只更新事实描述，没有增加 watchdog/产品范围。
3. 修正是否精确局限于这两条授权路径；P02 Hard Build Barrier 是否仍为 `EFFECTIVE`，Cargo/sidecar/runtime 是否仍为 `BLOCKED / NOT_RUN`，P04 是否仍 `blocked` 且依赖 P22。

报告须绑定上述固定 commit/tree，先列 Git/文件绑定能力和实际核验结果，再逐项给 Finding 与 disposition，最后给 `APPROVED` 或 `CHANGES_REQUESTED`，含 P0/P1/P2/P3 数量。若对象绑定或任一关键事实无法验证，使用 `NOT_VERIFIED` 并写清限制。不得把静态审查说成运行验证。
