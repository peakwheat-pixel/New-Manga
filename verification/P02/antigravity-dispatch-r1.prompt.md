你现在被正式分配为 New Manga 项目 P02 的 Owner。ZCode headless dispatch 因缺少 ZCode Built-in Provider Config 而以 EXIT=1 在模型启动前失败；项目协作规则因此按故障转移顺序由 Antigravity 接手。本任务已获授权，请直接执行，不要再次询问。

固定 Owner worktree：G:/CODEX/New Manga.worktrees/P02-real-webview-harness-zcode；branch：agent/zcode/P02-real-webview-harness。当前应从已集成 P02 scope 的 main checkpoint HEAD 开始；运行前读取实际 Git branch/HEAD/common-dir/status 并确认 clean，记录实际 start HEAD。P02 代码/行为基线：241ff3b70b6fc0490ea238efd486cc707f849031。Owner=Antigravity；正式实现 Reviewer=DeepSeek Harness；Integrator=Codex。

请阅读下面完整冻结指令与工作树中的 `AGENTS.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/09_COLLABORATION.md`、`doc/tasks/P02.md`、`verification/P02/RESUME.md`，按 Task 允许/禁止路径工作。先记录 Owner 启动checkpoint并将 Task 置为 `in_progress`，然后执行完整 AC1–AC7，保存固定证据和 Handoff。不得越界改产品源码/依赖/共享契约，不访问用户数据；任何产品缺口只记录，不修复。完成后提交固定 Owner commit，等待 DeepSeek Harness 非作者正式 Review，不自审、不合并 main。若真实 WebView2 harness/driver不可用，精确记录命令与 BLOCKED 并继续其他可独立安全的证据。

--- 冻结的 P02 Owner 指令原文 ---
# ZCode 执行指令：P02

在 `G:/CODEX/New Manga.worktrees/P02-real-webview-harness-zcode` 的 linked worktree、branch `agent/zcode/P02-real-webview-harness` 中执行正式 Task `doc/tasks/P02.md`。Task 的代码/行为基线为 `241ff3b70b6fc0490ea238efd486cc707f849031`。开工先读取 `AGENTS.md`、Plan/Status、协作协议、P02 Task/RESUME 与本地代码；记录实际 worktree、common-dir、HEAD、dirty manifest。Owner 开工时把 Task 状态从 `ready` 更新为 `in_progress`，并保存启动 checkpoint。不得假设当前 HEAD；若工作区非空、common-dir 不符、不是指定 branch/worktree，先保护现场并报告 Codex，不清理或覆盖任何内容。

## 冻结范围与交付

按 AC1–AC7 实现并运行真实 Tauri/WebView2 Workbench 验证 harness，记录实环境、可见行为、时序、前景/背景与对比度，准确区分 `REAL_WEBVIEW`、`REAL_WEBVIEW_MOCK_IPC`、`REAL_WEBVIEW_REAL_CORE` 与 JSDOM/Vitest 辅助控制组。AC4 的 retype、undo、restore 在默认双 300ms 配置下都是必测项；任一未执行即保留 BLOCKED，不能满足 AC4 或关闭 Task。AC6 只要 computed 前景/合成背景能确定就必须计算 ratio；token unmapped 不得跳过。

只允许写：

- `apps/desktop/frontend/e2e/**`
- `apps/desktop/frontend/dist/**`（仅本 Task 可重建 build 输出，不提交；先检查既有目录内容）
- `verification/P02/**`（合成 fixture、驱动、原始日志、截图、结果与恢复点；`cargo-target/**` 仅 task-local build output，不提交）
- `doc/handoffs/P02-*.md`
- `doc/tasks/P02.md`（仅状态与实际执行/交付记录；不得改 AC/允许路径/范围；提出任何 scope delta 后先停该部分）

禁止修改产品源码 `apps/desktop/frontend/src/**`、package/lockfile、Tauri/Rust/Python Core、IPC/Schema/DB/依赖、设计契约/token、P03 runner 或已打包 EXE/dist；不得修复观察到的 UI/键盘/颜色/debounce 问题。不得访问用户漫画库、人工编辑、Lock、current/pinned Revision、凭据或生产数据。仅 synthetic 隔离数据。

不新增依赖。优先先证明当前机器可用的真实 Tauri/WebView2 自动化驱动；不要把普通 Chrome/Vite、JSDOM、SSR、fake timers 或 packaged app 进程存活检查冒称真实 Workbench UI Gate。若真实驱动不可用，记录命令/EXIT/原始错误并将受影响 AC 标 `BLOCKED`；继续不依赖该驱动的安全证据。

构建按 Task 记录：在前端目录执行 `npm run build -- --outDir dist`；在 worktree 根目录设置 `$env:CARGO_TARGET_DIR='verification/P02/cargo-target'` 后执行 `cargo build --manifest-path apps/desktop/src-tauri/Cargo.toml`。执行前检查输出目录；未知既有内容不得覆盖。测试结果需区分 PASS/FAIL/BLOCKED/NOT_RUN，逐项保存 shell/解释器、版本、CWD、完整命令、stdout/stderr、EXIT、HEAD、二进制 Hash 与原因。Vitest 仅为控制组。

交付固定 Owner commit、Task Handoff、Task-local evidence/checkpoint 与每项 AC 判定。至少记录真实 runtime 身份、driver 交互、截图、300ms 单调时钟与 IPC 顺序、retype/undo/restore 时序、computed color/token/contrast CSV 或 JSON、所有 skip/blocker 和产品 findings。产品结果 FAIL 不通过 UI 修复来消除；Harness/报告交付完整也不代表产品 UI 质量 PASS。提交后交给非作者 DeepSeek Harness 正式 Review，不要自审或合并主线；Codex 负责集成与后验 Gate。

直接从工作树中的正式 P02 Task、恢复点与此指令工作，不扩展边界。每个状态边界更新 `verification/P02/RESUME.md`。当前 root 有 24 项已核对的旧 dirty/untracked 文件，它们归原作者所有；不要动它们。
