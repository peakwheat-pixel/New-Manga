# P02 自动续跑提示词

从 G:/CODEX/New Manga 持续推进权威路线图。P01=done，绝不重做；P02 AC/Owner allowlist、真实/Mock边界和退出判据已由 scope r1–r4 冻结并释放，不重复冻结。用户授权自动推进已满足条件的项目任务，可读写项目文件、用 worktree、运行适当检查、提交并本地集成通过 Review/Gate 的工作。默认简体中文；没有新授权不关机、不push、不发布、不部署。

## 恢复 Reality Check

读取根 AGENTS.md、Plan、Index、Status、协作协议、P02正式Task、本文件和 verification/P02/RESUME.md。核对Live root及所有相关branch/worktree的HEAD/tree/status/dirty/untracked，并比较Task、Plan、Status、Gate log与恢复点。文档、Git和实际验证是事实来源。保护用户数据、人工编辑、Lock、current/pinned Revision、密钥和其他Agent未提交内容。P01已经done，不重做；P02范围r1–r4已经冻结，不重冻结。

## 历史固定对象和审查事实（不代表恢复时Live Git仍停在该处）

- Live main 最近记录为4b54f304dc201d129d4ba1c62d0368252e6301b1，P02 ready / IDLE、Owner=ZCode；root当时dirty/untracked=38。
- 候选branch=codex/P02-owner-transfer-integration，worktree=G:/CODEX/New Manga.worktrees/P02-owner-transfer-integration-codex。DSH r8 reviewed c4=55be5dab7b6d7bebf94c9ad6524f57c023616249，tree=f74afc39b307ca7f388bda8b3de8e73d23e00163，decision=approved_with_conditions，findings=0/0/0/2，session=session-5e8be65b-515f-41fc-b444-c80e22121c95。报告/prompt/mount位于verification/P02/owner-transfer-r8-review/。
- c5 aa404aaa的独立Review发现索引AA-01，已在f18720a修正。f18720a exact-head/tree=d2a6c3482d2842d6ffe79a324d6e7dae87cccf6a；独立review decision=approved_with_conditions，findings=0/0/0/0。报告分别为verification/P02/owner-transfer-integration-review-aa404aa.md与owner-transfer-integration-review-f18720a.md。
- DSH r8自身shell受Win32 5限制，未运行Git/hash/validator/manifest；Codex在c4实际补证，历史结果见owner-transfer-r7-gate.log。c4 tree/head已由Codex和独立Reviewer命令核验。最新候选可能已有新commit，恢复时先解析Live Git真实HEAD/tree/status再固定本轮对象。
- P02 behavior base=241ff3b70b6fc0490ea238efd486cc707f849031；scope contract SHA-256=27DC31A8CF3304ABA6783E243F36895FFE4AAA3CCBCA76D58E8B766C403E1425。候选Owner=Antigravity，Reviewer=DeepSeek Harness，Integrator=Codex；Live main快进前Owner=ZCode。Task AC/frontmatter/allowlist不得因治理集成而扩张。
- P01 protected manifest最近核验24/24、0 mismatch、body digest=b41835453b693b4e62818216e4d67801c01eca6e33450f8d3d3dd72849d578e7；root dirty/untracked=38；候选和manifest交集=0；和root交集仅两份P02 recovery。核验后两份恢复文件已执行一次C-2同步，但恢复点随后更新；该次同步记录于Gate log，只对当时的文件hash有效。C-2的最终closure必须重新比较Gate log最新final-sync行与候选和root现有两份文件hash/status，若不匹配则仍pending。
- 旧ZCode Owner worktree标记DRIFT_DETECTED，源码行尾差异、cargo-target和cdp_probe.py原地保护，不复用。Tauri build.rs会写源码树，Owner worktree构建前需要独立审查和登记scratch方案；其完成前不运行Cargo/Tauri/sidecar build。AC1–AC7、Vitest、构建、真实WebView/GUI/键盘焦点/对比度保持NOT_RUN。

## 自动持续推进

1. 从Live Git读取实际候选head/tree/status，读最新review和Gate log；P01、P02 frozen scope均不重做。让非作者Reviewer审查最新治理差量，特别核对Owner/Reviewer不同、精确head/tree、Task hash、根目录保护现场与C-2状态。
2. C-2按精确hash绑定：仅在Gate log最新review明确覆盖当前恢复文件后，同步verification/P02/RESUME.md和NEXT-AUTOPROGRESS-PROMPT.md到Live root；记录即时pre/post hash/status。逐项fresh-check P01 manifest 24/24、root dirty/untracked和候选交集。若恢复文件在审查后发生改变，再重审并重同步；不能用历史C-2 pass替代当前文件hash。
3. Codex Integration Gate与非作者集成Review均通过后，只在本机git merge --ff-only，不push。Post-FF重跑路线validator/mutation probe、manifest、dirty工作区和完整差量边界。
4. 从release HEAD创建全新干净agent/antigravity/P02-real-webview-harness worktree。按Antigravity dispatch Skill执行只读Owner acceptance/start-intent握手，记录实际conversation ID、CLI JSON、exit、session/mount和start checkpoint。无真实接单和checkpoint之前Task不得改为in_progress。
5. Owner实现真实Tauri/WebView2 harness及P02 AC1–AC7；Chrome/Vite/JSDOM/mock/旧EXE不是真实WebView。严守allowlist与synthetic data。先解决构建副作用隔离与任务范围授权；未能安全运行的gate如实为BLOCKED/NOT_RUN，并继续独立允许项。
6. 交付后由非作者DSH正式Review，修复并复审findings。Codex验证Task AC、测试、hash、manifest、allowlist与Integration Gate后才集成并更新Plan/Status/Task/依赖/恢复点。之后从权威路线图挑选依赖已满足且范围已冻结的下一Task并继续，不等用户催促。

只有必须由用户决定的真实产品取舍或外部不可逆动作才暂停询问；其他已授权、安全工作持续推进。