# P02 自动续跑提示词

从 G:/CODEX/New Manga 持续推进权威路线图。P01=done，绝不重做；P02 AC/Owner allowlist、真实/Mock边界和退出判据已由 scope r1–r4 正式冻结并释放，不重复冻结。默认简体中文；没有新的用户授权时不关机、不 push、不发布、不部署。用户授权自动推进项目任务、创建 worktree/分支、运行适当检查、提交和完成通过 Review/Gate 的本地集成。

## 恢复 Reality Check

读取根 AGENTS.md、doc/REBASELINE_PLAN.md、doc/00_INDEX.md、doc/STATUS.md、doc/09_COLLABORATION.md、正式 P02 Task、本文件及 verification/P02/RESUME.md。核对 Live root 和候选 branch/worktree 的 Git HEAD、tree、status、dirty/untracked、Task、Plan、Status 与恢复点。项目文档、Live Git 和实际验证是事实来源。P01 已完成，不重做。保护用户数据、人工编辑、Lock、current/pinned Revision、密钥及其他 Agent 未提交内容。

## 已知历史检查点（恢复时必须重新核对 Live Git）

- Live main 上次核验=4b54f304dc201d129d4ba1c62d0368252e6301b1，P02=ready / IDLE、Owner=ZCode；Owner 转移尚未快进生效。root 当时 dirty/untracked=38。
- Candidate branch=codex/P02-owner-transfer-integration，worktree=G:/CODEX/New Manga.worktrees/P02-owner-transfer-integration-codex。DSH r8 reviewed checkpoint c4=55be5dab7b6d7bebf94c9ad6524f57c023616249，tree=f74afc39b307ca7f388bda8b3de8e73d23e00163，decision=approved_with_conditions，findings P0/P1/P2/P3=0/0/0/2；session=session-5e8be65b-515f-41fc-b444-c80e22121c95，CLI exit=0，报告见 verification/P02/owner-transfer-r8-review/review.md。这个 head 是历史 Review 对象，不保证是恢复时的当前候选 head。先查询实际 branch HEAD/tree/status，再固定当前对象。
- DSH r8 shell 受 Win32 5 限制，未自行运行 Git/tree/hash/validator/manifest/test；Codex 已在 c4 实际补跑，结果和限制见 verification/P02/owner-transfer-r7-gate.log 的 r8 附录与 P02 RESUME。r8 的两个 P3 和独立 Reviewer 对旧 checkpoint 指针的 P3 已在当前治理 checkpoint 中显式登记及处置；实际 Git 当前状态仍需重核。
- P02 behavior base=241ff3b70b6fc0490ea238efd486cc707f849031；r2 scope contract SHA-256=27DC31A8CF3304ABA6783E243F36895FFE4AAA3CCBCA76D58E8B766C403E1425。候选 Owner=Antigravity、Reviewer=DeepSeek Harness、Integrator=Codex；Live main 快进前 Owner 仍为 ZCode。AC/Task/frontmatter/allowlist 已冻结，不能借治理集成扩展产品范围。
- 上次 P01 保护清单为24项；c4 前核验24/24 status/path/content SHA匹配、0 mismatch，记录摘要=b41835453b693b4e62818216e4d67801c01eca6e33450f8d3d3dd72849d578e7。候选路径与 manifest 交集=0；与 root dirty/untracked 交集仅两份 P02 recovery。以上均是检查点事实，继续之前和同步后都要重核；不得 stage/stash/覆盖/清理另外 36 项 root 现场。
- 旧 ZCode Owner worktree=G:/CODEX/New Manga.worktrees/P02-real-webview-harness-zcode@e1948466082b3cadbfde1da53b791319e359a10b 为 DRIFT_DETECTED，其中生成文件行尾差异、cargo-target、cdp_probe.py 必须原地保留，不复用。Tauri build.rs 会写源码树；CARGO_TARGET_DIR 不能隔离。经正式登记和独立审查的 scratch-build 方案完成前不运行 Cargo/Tauri/sidecar build。AC1–AC7、Vitest、构建、真实 WebView/GUI/键盘焦点/对比度仍 NOT_RUN。

## 持续执行

1. 从 Live Git 核对后固定当前实际候选 HEAD/tree/status。读取 r8 Review 与 Gate log；P01 和 P02 范围均不重做。让非作者 Reviewer 复核当前治理候选的准确差量、恢复指针和保护路径。
2. 按 DSH r7 C-2，在最终 recovery 内容经过 Review 后，只把 verification/P02/RESUME.md、NEXT-AUTOPROGRESS-PROMPT.md 同步至 Live root。记录同步前后两个文件的 SHA/status；同步后逐项重核 P01 manifest 24/24、root dirty count、候选/root 与 manifest intersections、允许路径和 git diff --check。若有超出两份 recovery 的意外差异或保护 manifest 漂移，立即保留现场并停止依赖该条件的快进。
3. Codex Integration Gate 与非作者集成差量 Review 均通过后，仅用 --ff-only 集成到 main；不 push。Post-FF 重新检查实际 HEAD、路线 validator/mutation probe、manifest、dirty 工作区和差量边界。
4. 从最终 release HEAD 创建全新干净 agent/antigravity/P02-real-webview-harness worktree，并按 Antigravity dispatch Skill 执行只读 acceptance/start-intent 握手。保存真实 CLI JSON、conversation ID、exit、session/mount 和 start checkpoint。没有真实接单和 start checkpoint，Task 不得变成 in_progress。
5. Owner 按 P02 Task 实现真实 Tauri/WebView2 harness 与 AC1–AC7；Chrome/Vite/JSDOM/mock/旧 EXE 不能冒充真实 WebView。严守 allowlist 和 synthetic data。先按治理规则解决构建副作用隔离，不能安全运行的产品 gate 如实留为 BLOCKED/NOT_RUN，同时继续其他独立允许工作。
6. Owner 交付后由非作者 DSH 正式 Review；修复并复审 findings；Codex 核验 Task AC、测试证据、hash、manifest、allowlist 与 Integration Gate后再集成、更新 Status/Plan/Task/checkpoint。随后从权威路线图选择依赖已满足、范围已冻结的下一项，继续执行，不等用户催促。

只有真实未决产品取舍或外部不可逆动作才询问用户；独立、安全且已授权工作继续推进。