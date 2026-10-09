# P02 自动续跑提示词

请在 `G:/CODEX/New Manga` 中自动继续 P02，并按权威路线推进所有依赖已满足、范围已冻结的后续工作，直到已授权工作完成或出现必须由我决定的产品问题。默认使用简体中文。本提示不授权关机、push、发布或部署。

## 恢复规则

1. 先读取当前仓库 `AGENTS.md`、`doc/REBASELINE_PLAN.md`、`doc/00_INDEX.md`、`doc/STATUS.md`、`doc/09_COLLABORATION.md`、`doc/tasks/P02.md` 和 `verification/P02/RESUME.md`。核对 Live main、所有 worktree/branch/common-dir、Task状态、固定基线、正式 Review与实际dispatch。若状态与恢复点不一致，先记录证据并按项目治理处理，不从聊天推断完成。
2. P01 已完成，不重做。root 原作者24项 dirty/untracked 必须与 `verification/P01/root-dirty-manifest-pre-ff.txt` 逐项核对并保护；不得 stage、stash、覆盖或清理。任何Agent未提交内容同样受保护。
3. 当前 P02 scope/release commit=`3c3e4687785e65f668f1146052e78c3da074ba99`，已从父=`241ff3b70b6fc0490ea238efd486cc707f849031` 本地 fast-forward 到 Live `main`；r1–r4范围治理Review完成，r4 approved关闭`P02-SCOPE-R3-01`。post-FF Gate和恢复证据见 `verification/P02/release-post-ff-check.txt`、`verification/P02/RESUME.md`。release commit只集成范围和治理文档，不代表任何P02产品AC通过。root原作者24项dirty/untracked必须继续保护；manifest SHA=`b41835453b693b4e62818216e4d67801c01eca6e33450f8d3d3dd72849d578e7`。
4. P02 scope/release 与 post-FF Gate 已完成并提交。当前只待提交Codex-owned恢复点更新；仅stage `verification/P02/RESUME.md` 与 `verification/P02/NEXT-AUTOPROGRESS-PROMPT.md` 两条路径，并核对与P01 manifest无交集。不要stage root中其他内容。
5. checkpoint提交后重新核对 P01 manifest及Live main，再核对指定 Owner branch=`agent/zcode/P02-real-webview-harness` 与path=`G:/CODEX/New Manga.worktrees/P02-real-webview-harness-zcode`不存在；基于最新Live main实际HEAD创建并验证ZCode linked worktree。使用 `verification/P02/zcode-task.prompt.md` 和已安装 `zcode-dispatch` skill真实派发，保存真实CLI命令、prompt、session、handoff、exit与checkpoint。availability probe不等于实际派发；Owner接单后才可改`TaskStatus=in_progress`。ZCode不可用时按 `AGENTS.md` 顺序故障转移至Antigravity，绝不分配给Qoder。
7. 每到 start、handoff、review、integration状态边界更新 `verification/P02/RESUME.md`。按 Task AC1–AC7执行固定源码HEAD上的真实 Windows Tauri/WebView2验证，分清真实Core/SQLite、真实WebView2+mock IPC/Core、JSDOM/Vitest。不得用Vite/Chrome、JSDOM、mock、SSR、fake timers或runner存活检查冒称真实Workbench验收。环境/驱动不可用时记录精确`BLOCKED`和命令，然后做其他安全可执行工作。
8. 不改产品UI、颜色、键盘交互、debounce、共享契约或依赖；观察到的产品缺陷只记录证据，再按Plan决定是否另释后继Task。继续使用已确认F设计契约4.5:1/3.0:1，不重做P08 D1–D7。保护用户库、人工编辑、Lock、current/pinned Revision、凭据和生产数据。
9. P02完成前逐项核对AC、PASS/FAIL/BLOCKED/NOT_RUN及证据、非作者DeepSeek Harness正式实现Review、Codex集成Gate和集成后检查；更新Task、Plan、Status、依赖图、RESUME和NEXT提示。完成后自动从权威Plan选择依赖已满足且范围已冻结的下一Task，落实Owner/Reviewer分离并继续。只在必须用户裁决或全部已授权工作完成时暂停。

## 本检查点的下一步

1. 核对并仅提交2个Codex-owned恢复点路径；保护原作者24项dirty/untracked。
2. 对最新Live main再次核对P01 24项manifest，检查ZCode worktree目标与branch未占用。
3. 创建指定ZCode linked worktree并从正式`zcode-task.prompt.md`真实dispatch P02；保存接单证据后再更新Task为`in_progress`。
4. 跟踪Owner实现、真实AC1–AC7、DeepSeek Harness正式Review、修订和Codex集成Gate直至Task完成，并从权威路线自动推进下一项已释放工作。
