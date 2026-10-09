# P02 Antigravity Owner 接单握手 r1

这是只读接单与 start-intent 握手，不是产品实现阶段。请先只读核对本消息和当前 worktree 状态；不得编辑、暂存、提交、运行测试/构建、切换分支/worktree、调用其他 Agent 或读取用户漫画库/生产数据。握手结果由 Codex 保存与登记；在 Codex 正式发送实现启动消息前，不开始实现。

## 当前 Task 与固定对象

- Task：`doc/tasks/P02.md`，真实 Workbench Tauri/WebView2 行为验证 harness。
- Owner：Antigravity；非作者实现 Reviewer：DeepSeek Harness；Integrator：Codex。Qoder已退出，不得分配。
- 当前工作目录：`G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity`
- branch：`agent/antigravity/P02-real-webview-harness`
- 预期干净 start head：`3c651f502d49de32f5b050cfefc1ea056354f663`
- 预期 tree：`f8e32f9b64b0f0b1dbcfc14c74f2649c61629f7f`
- 行为验证基线：`241ff3b70b6fc0490ea238efd486cc707f849031`
- 已冻结 P02 产品/Owner scope contract SHA-256：`27DC31A8CF3304ABA6783E243F36895FFE4AAA3CCBCA76D58E8B766C403E1425`。scope r1–r4 已通过，不要重新冻结或扩大范围。

## 接受后所承担的已释放范围

实现范围仅为已冻结 Task 的 AC1–AC7：证明测试目标是当前源码构建出的真实 Tauri/WebView2；验证 Workbench 导航与输入、300ms quiet-period 和 page 失效、retype/undo/restore 写后刷新、Workbench 键盘与焦点，以及真实 WebView computed color/token mapping/contrast 数据；按固定证据格式登记 PASS/FAIL/BLOCKED/NOT_RUN 与 findings。测试报告必须明确真实或模拟 IPC 层；普通 Chrome/Vite、JSDOM、SSR、mock、旧 EXE 或 fake timers 都不能冒充真实 WebView2/Core 证据。观察到产品缺口只登记 finding，不修产品 UI、样式、token、debounce、键盘/焦点或性能。

Owner 允许路径严格以 P02 Task 为准：

- `apps/desktop/frontend/e2e/**`：仅 Workbench WebView 驱动和断言。
- `verification/P02/**`：仅本 Task runner、合成 fixture、证据/截图/日志与恢复材料。
- `apps/desktop/frontend/dist/**`、`verification/P02/cargo-target/**`：仅 Task 命令新生成、可重建且不提交的构建输出；开跑前须检查目标存在状态，不得覆盖来源不明内容。
- `doc/handoffs/P02-*.md` 与 `doc/tasks/P02.md`：按 Task 允许的交接及实际状态/执行记录。

禁止修改 `apps/desktop/frontend/src/**`、前端依赖清单、`apps/desktop/src-tauri/**` 源码、Python Core、SQLite schema/migration、共享 IPC/Schema、依赖清单、已打包 EXE、P03 runner 与设计 token/契约；不得读取/更改用户数据、人工编辑、Lock、current/pinned Revision 或凭据。新增依赖需要先由 Codex 冻结最小 scope delta。

## 构建前置限制

当前前置调查发现 Tauri `build.rs`/`tauri_build::try_build` 会写源码树，且当前固定版本缺少受信 sidecar 输入。不得在本 Owner worktree 运行 Cargo/Tauri/sidecar build。Codex 必须先登记具体 scratch worktree、隔离生成目录、synthetic/可信 sidecar 来源及准确命令，并由非作者 Reviewer 独立批准后，才可使用该隔离构建路径。此限制只约束技术执行安全，不改变既有产品验收范围。

## 请只返回接单声明

请明确 `ACCEPT` 或 `DECLINE`。若 `ACCEPT`，请确认 Owner、scope SHA、允许/禁止路径、构建限制，并给出本地观察到的 branch/HEAD/tree/clean 状态作为 start checkpoint，以及你将在 Codex 正式启动实现后执行的第一步（仅描述，不执行）。若工作目录/hash 不符或你无法接受任何约束，请 `DECLINE` 并说明具体差异。请再明确确认握手期间 `files_changed=[]`、`staged_changes=[]`，没有运行测试或构建。
