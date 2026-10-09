# P02 自动续跑提示词

从 `G:/CODEX/New Manga` 自动继续 P02，并随后按权威路线推进依赖满足、范围已冻结的任务；持续至已授权工作完成或出现必须由用户决定的产品问题。默认简体中文。P01 已完成，绝不重做。本提示不授权关机、push、发布或部署；此前一次性关机授权已消费，不得延伸。

## 恢复规则

先读取 `AGENTS.md`、`doc/REBASELINE_PLAN.md`、`doc/00_INDEX.md`、`doc/STATUS.md`、`doc/09_COLLABORATION.md`、`doc/tasks/P02.md` 与 `verification/P02/RESUME.md`；核对 Live Git、root dirty/untracked、所有 P02 worktree、当前 Task 与证据。以项目文档、Git 和实测为事实，不依据聊天推测任务完成。保护用户数据、人工编辑、Lock、current/pinned Revision、密钥及其他 Agent 的未提交文件。

## 当前 P02 路径

- P02 的 AC/Owner allowlist、真实/Mock 边界和验收退出条件已由 scope r1–r4 冻结并释放。不得重新冻结或扩大产品范围。
- Live main 在本检查点=`4b54f304dc201d129d4ba1c62d0368252e6301b1`；P02 仍为 `ready / IDLE`、原 Owner=ZCode，尚无 Owner 接单。Antigravity 是治理故障转移候选，必须等 Task fixed-head DSH Review 的必需条件和 Codex 集成 Gate 都通过并快进后才生效。当前审查、findings 与最新 fixed head 见 P02 RESUME。
- P02 行为基线=`241ff3b70b6fc0490ea238efd486cc707f849031`，产品契约 SHA=`27DC31A8CF3304ABA6783E243F36895FFE4AAA3CCBCA76D58E8B766C403E1425`；Reviewer=DeepSeek Harness，Integrator=Codex。旧 ZCode worktree `G:/CODEX/New Manga.worktrees/P02-real-webview-harness-zcode` 为 `DRIFT_DETECTED`，不得复用、清理、改写或集成。
- root 原作者保护 manifest 有24项，上次核验 SHA=`b41835453b693b4e62818216e4d67801c01eca6e33450f8d3d3dd72849d578e7`；快进前必须重新逐项核对。root 其他所有dirty/untracked也全部保护。只同步经审查的两份本任务 recovery 文件，不碰其他路径。
- Tauri `build.rs` 会改写源码树生成文件，`CARGO_TARGET_DIR` 不能隔离；Codex建立且独立审查通过的 scratch build 方案尚不存在。不得在 Owner worktree 运行 Cargo/Tauri/sidecar build。

## 持续执行顺序

1. 从 RESUME 指向的最新 candidate head 开始，关闭 DSH r7/后续 Review 的必需 findings；重算 Task bytes、LF 与 Git blob 摘要，保留历史 Review/hash 绑定，不伪造复审。补齐链接和文档建议后复跑治理 Gate、路径/manifest保护检查并提交 fixed head。
2. 由 DeepSeek Harness 对准确 fixed head 做非作者 Task Review；独立 Agent 审查集成差量。Review 条件全部闭合后，快进前将两份 Task recovery 文件同步到 root，逐哈希确认、重跑 P01 manifest 和路径交集 Gate。任何漂移或冲突时停止集成、保留现场。
3. Codex `--ff-only` 集成并进行 post-FF Gate。随后从最终 release HEAD 创建全新 Antigravity Owner worktree；先派发只读 acceptance/start-intent handshake。只有真实 conversation ID、接单与 start checkpoint 都保存后，才将 Task 改为 `in_progress`。
4. Owner 严格按 AC1–AC7 与 allowlist 开发真实 Tauri/WebView2 harness，运行安全的前端控制组。Chrome、Vite、JSDOM、mock 或旧 EXE 不能冒充真实 WebView。所有测试数据限 synthetic。未解决的 build side-effect blocker 只能保持 `BLOCKED/NOT_RUN`，不能绕过。
5. 交付 Handoff 后由非作者 DSH 正式 Review，按 findings 修订和复审；Codex 完成验收、path、hash、测试证据和 root 保护 Gate 后才可集成并按 Plan 更新 Task 状态。完成后自动选择下一项已满足依赖的授权 Task，不等待用户说“下一步”。

出现必须由用户决定的产品取舍时，继续所有不依赖它的安全工作，再一次性列出具体问题和影响范围。不得自行决定产品行为；不得将 `NOT_RUN` 说成 PASS。