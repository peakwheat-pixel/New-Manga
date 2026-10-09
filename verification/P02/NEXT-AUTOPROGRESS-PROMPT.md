# P02 自动续跑提示词

请在 `G:/CODEX/New Manga` 中自动继续 P02，并按权威路线推进所有依赖已满足、范围已冻结的后续工作，直到已授权工作完成或出现必须由我决定的产品问题。默认使用简体中文。本提示不授权关机、push、发布或部署。

## 恢复规则

1. 先读取当前仓库 `AGENTS.md`、`doc/REBASELINE_PLAN.md`、`doc/00_INDEX.md`、`doc/STATUS.md`、`doc/09_COLLABORATION.md`、`doc/tasks/P02.md` 和 `verification/P02/RESUME.md`。核对 Live main、所有 worktree/branch/common-dir、Task状态、固定基线、正式 Review与实际dispatch。若状态与恢复点不一致，先记录证据并按项目治理处理，不从聊天推断完成。
2. P01 已完成，不重做。root 原作者24项 dirty/untracked 必须与 `verification/P01/root-dirty-manifest-pre-ff.txt` 逐项核对并保护；不得 stage、stash、覆盖或清理。任何Agent未提交内容同样受保护。
3. 当前 scope 候选路径=`G:/CODEX/New Manga.worktrees/P02-harness-scope`，branch=`codex/P02-harness-scope`，父 HEAD=`241ff3b70b6fc0490ea238efd486cc707f849031`。AC/Owner allowlist r2已批准；r3 finding `P02-SCOPE-R3-01` 已经修订并由独立 r4 approved关闭。r4固定审查输入 Hash 与报告记在 `verification/P02/scope-review-r4.md` 及 `doc/tasks/P02.md`。路线校验和两项状态漂移拒绝探针通过；root manifest复核24/24；当前 release path allowlist 28 paths/0越界。完整 checkpoint看 `verification/P02/RESUME.md`。若本提示与Live Git/Plan/Status/Task冲突，先做Reality Check。
4. 完成最终 release Gate：检查所有链接、cached/uncached `git diff --check`、validator及突变探针、P02 Task和Plan/Status/ROADMAP一致性、精确changed-path allowlist。显式 stage 仅范围文档/证据路径与已批准 Codex-only validator；核对 staging 内容、不要带入其他 worktree/用户文件，然后提交本地 scope/release commit。
5. 提交前在 Live root重新确认 `main@241ff3b70b6fc0490ea238efd486cc707f849031` 和 frozen manifest SHA=`b41835453b693b4e62818216e4d67801c01eca6e33450f8d3d3dd72849d578e7`；再核验24项 status/hash完全匹配、候选差量与保护路径交集为0。然后仅本地 fast-forward集成，无push。保存 release SHA与post-FF验证恢复点。
6. 创建并核对 Owner linked worktree：Owner=`ZCode`，正式实现 Reviewer=`DeepSeek Harness`，Integrator=`Codex`；branch=`agent/zcode/P02-real-webview-harness`，path=`G:/CODEX/New Manga.worktrees/P02-real-webview-harness-zcode`，start HEAD取 release后的Live main实际HEAD。使用 `verification/P02/zcode-task.prompt.md` 和已安装 `zcode-dispatch` skill真实派发，保存真实CLI命令、prompt、session、handoff、exit与checkpoint。availability probe不等于实际派发；Owner接单后才可改 `TaskStatus=in_progress`。ZCode不可用时按 `AGENTS.md` 顺序故障转移至Antigravity，绝不分配给Qoder。
7. 每到 start、handoff、review、integration状态边界更新 `verification/P02/RESUME.md`。按 Task AC1–AC7执行固定源码HEAD上的真实 Windows Tauri/WebView2验证，分清真实Core/SQLite、真实WebView2+mock IPC/Core、JSDOM/Vitest。不得用Vite/Chrome、JSDOM、mock、SSR、fake timers或runner存活检查冒称真实Workbench验收。环境/驱动不可用时记录精确`BLOCKED`和命令，然后做其他安全可执行工作。
8. 不改产品UI、颜色、键盘交互、debounce、共享契约或依赖；观察到的产品缺陷只记录证据，再按Plan决定是否另释后继Task。继续使用已确认F设计契约4.5:1/3.0:1，不重做P08 D1–D7。保护用户库、人工编辑、Lock、current/pinned Revision、凭据和生产数据。
9. P02完成前逐项核对AC、PASS/FAIL/BLOCKED/NOT_RUN及证据、非作者DeepSeek Harness正式实现Review、Codex集成Gate和集成后检查；更新Task、Plan、Status、依赖图、RESUME和NEXT提示。完成后自动从权威Plan选择依赖已满足且范围已冻结的下一Task，落实Owner/Reviewer分离并继续。只在必须用户裁决或全部已授权工作完成时暂停。

## 本检查点的下一步

1. 核对scope branch staged tree：28个授权path，cached/uncached `git diff --check`、route validator、两项漂移probe、12个本地Markdown链接与保护manifest交集均已通过；若Git状态/恢复点漂移，先调查。
2. 提交本地scope/release commit，保存实际SHA。
3. 提交前再次逐项复核Live root仍为 `main@241ff3b70b6fc0490ea238efd486cc707f849031`、24项保护manifest 24/24匹配、候选改动与保护路径交集为0；然后只做本地`--ff-only`并记录post-FF证据。
4. 创建指定ZCode Owner linked worktree并基于真实Live main HEAD派发；跟踪AC1–AC7、DeepSeek Harness正式Review与Codex集成直至Task Gate完成。
