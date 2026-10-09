# P02 自动续跑提示词

从 `G:/CODEX/New Manga` 持续推进权威路线图。P01=`done`，绝不重做；P02 的 AC/Owner 范围已由 scope r1–r4 冻结并释放，不重复冻结。默认简体中文；无新增授权时不关机、不push、不发布、不部署；此前一次性关机授权已消费。

## 恢复 Reality Check

读取根 `AGENTS.md`、Plan、Index、Status、协作协议、正式 P02 Task、本文件及 `verification/P02/RESUME.md`。核对 live root、所有相关 worktree/branch、dirty/untracked、Task状态和恢复点。项目文档、Git与实际验证是事实来源。保护用户数据、人工编辑、Lock、current/pinned Revision、密钥和其他Agent未提交内容。

## 当前固定检查点

- Live main=`4b54f304dc201d129d4ba1c62d0368252e6301b1`，P02仍`ready / IDLE`、Owner=ZCode；Owner转移尚未快进生效。
- Candidate branch=`codex/P02-owner-transfer-integration`，worktree=`G:/CODEX/New Manga.worktrees/P02-owner-transfer-integration-codex`，fixed head=`ec207865348be65c7aa8abb7da163938fccb353d`，tree=`856d71e30cd568b9599392eae5ccb51d79cdc330`。Task候选Owner=Antigravity、Reviewer=DeepSeek Harness、Integrator=Codex。P02 base=`241ff3b70b6fc0490ea238efd486cc707f849031`，r2范围契约SHA=`27DC31A8CF3304ABA6783E243F36895FFE4AAA3CCBCA76D58E8B766C403E1425`。
- DSH r7 reviewed `c2cbee43d4917bca385c9b0fa81ee49fc696ea9e`，decision=`approved_with_conditions`。Task hash历史/当前口径、r6 Review直链和Plan标点已在`ec207865`修订，Codex路线检查通过。DSH r7 C-2要求快进前同步两份本任务recovery并留存root hashes/status及fresh P01 manifest核验。完整证据和下一步见P02 RESUME及`verification/P02/owner-transfer-r7-gate.log`。
- root有38项dirty/untracked；P01保护manifest24项，上次重核24/24、0 mismatch，SHA=`b41835453b693b4e62818216e4d67801c01eca6e33450f8d3d3dd72849d578e7`。候选与manifest无交集，候选/root唯二路径交集是`RESUME.md`和本提示词。不得stage/stash/覆盖/清理其他root内容。
- 旧ZCode Owner worktree为`DRIFT_DETECTED`，原地保留其生成文件行尾差异、cargo-target及`cdp_probe.py`，不得复用。Tauri build.rs会写源码树生成文件，`CARGO_TARGET_DIR`不能隔离；scratch构建方案尚未独立审查验证前禁止Cargo/Tauri/sidecar build。AC1–AC7、Vitest、构建、真实WebView/GUI/对比度均`NOT_RUN`。

## 持续执行

1. 对`ec207865348be65c7aa8abb7da163938fccb353d`派发DSH正式只读Task Review；保存实际prompt、report、exit、session及mount。获取固定head决策后由非作者Agent独立复核整个集成差量。
2. 关闭DSH r7 C-2：将最终候选的`verification/P02/RESUME.md`和`verification/P02/NEXT-AUTOPROGRESS-PROMPT.md`同步至root，记录两文件同步前后hash和status；重新逐项复核P01 manifest24/24、root dirty交集、精确候选allowlist及`git diff --check`。保护其他36项root现场。任何意外冲突或manifest漂移时停下并保留数据。
3. Codex Integration Gate全部通过后仅`--ff-only`快进，不push；复跑post-FF路线、manifest及工作区保护校验。再从release HEAD建立全新Antigravity Owner worktree并发送只读acceptance/start-intent handshake。没有真实接单/conversation ID与start checkpoint时，不改Task到`in_progress`。
4. Owner按既有Task实现真实Tauri/WebView2 harness和AC1–AC7；Chrome/Vite/JSDOM/mock/旧EXE不能冒充真实WebView。严守allowlist与synthetic数据。若构建副作用没有安全审查方案，如实`BLOCKED/NOT_RUN`，继续其他独立允许项。
5. 交付后由非作者DSH正式Review，处理findings并复审；Codex核实Task AC、测试证据、allowlist、hash、manifest和Integration Gate后才集成/更新done。之后自动选择依赖已满足、范围已冻结的下个Task，不等用户催促。

必须由用户决定的产品取舍需一次性列明问题与影响；独立安全工作继续推进。