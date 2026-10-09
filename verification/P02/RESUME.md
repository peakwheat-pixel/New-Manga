# P02 恢复点

## 当前检查点：scope r1–r4 完成；释放提交已本地 FF；post-FF Gate PASS；待关闭Checkpoint并派发Owner

- Timestamp：2026-10-09T03:31:30Z。Live root=`G:/CODEX/New Manga`；branch=`main`；HEAD/release commit=`3c3e4687785e65f668f1146052e78c3da074ba99`；scope branch=`codex/P02-harness-scope` 已在同一提交，scope worktree=`G:/CODEX/New Manga.worktrees/P02-harness-scope`。common-dir=`.git` / `G:/CODEX/New Manga/.git`。
- `3c3e4687` 是 P02 scope/release 文档与治理提交，父 commit=`241ff3b70b6fc0490ea238efd486cc707f849031`；P02 Task 的 `base_commit=241ff3b...`仍是固定源码/行为基线，`integration_commit=null`仍表示 P02 实现未集成。Live main 对 origin ahead 1247；本轮未 push。
- Release前与 post-FF 都以 P01 frozen manifest SHA=`b41835453b693b4e62818216e4d67801c01eca6e33450f8d3d3dd72849d578e7`复核原作者24项 dirty/untracked：24 entries、24 live paths、0 mismatch；本地 release 的28个路径与保护清单交集0。原始24项仍存在并保留。Post-FF 证据=`release-post-ff-check.txt`；root 当前多了 Codex 自己的 post-FF closeout 文件/修改，不属于冻结的24项，须与原作者差量分别保护。
- Post-FF Gate=`PASS`：`git diff --check 241ff3b... 3c3e468...` EXIT=0；固定规划 validator EXIT=0；两项路线状态突变拒绝 probe EXIT=0；P02 Task/RESUME Markdown 本地链接12项、破损0；`src/apps/tests/packaging` 产品/测试/build路径差量0；路线图与 Plan 状态一致。P02 AC1–AC7、产品 build、Vitest、真实 WebView2/GUI 均仍`NOT_RUN`。
- P02 Task=`ready`，唯一 Active/released Task。Owner=`ZCode`；正式非作者实现 Reviewer=`DeepSeek Harness`；Integrator=`Codex`。Owner branch=`agent/zcode/P02-real-webview-harness`，worktree 预定为 `G:/CODEX/New Manga.worktrees/P02-real-webview-harness-zcode`；尚未创建/派发。Task源代码基线=`241ff3b70b6fc0490ea238efd486cc707f849031`；创建 Owner worktree 时从 post-FF closeout 集成后的 Live main 实际HEAD起步，并在 Owner Handoff 记录真实 start HEAD。Task prompt=`zcode-task.prompt.md`。Qoder已退出，绝不分配。
- Scope review：r1 `changes_requested`、r2 `approved`（AC/Owner allowlist SHA=`27DC31A8CF3304ABA6783E243F36895FFE4AAA3CCBCA76D58E8B766C403E1425`）、r3 `changes_requested`、r4 `approved`并关闭`P02-SCOPE-R3-01`。r4审查固定Hash与范围见 [`scope-review-r4.md`](scope-review-r4.md)。范围批准不扩大Owner allowlist，也不替代正式DSH实现Review。
- 本恢复点待提交的 Codex post-FF closeout 改动仅4条 Task-local path：`doc/tasks/P02.md`、`verification/P02/RESUME.md`、`verification/P02/NEXT-AUTOPROGRESS-PROMPT.md`、`verification/P02/release-post-ff-check.txt`；前3项为release后执行/恢复记录更新，最后一项为集成证据。root 原作者24项不在本次stage范围。
- DSH headless availability probe exit 0仅证明CLI可达，不代表Task已实际派发或正式Review；session=`session-915691c6-4075-4867-b331-e3ea55f1b451`已挂载，Web/Desktop可见性未验证。不得续用任何一次性关机授权；不push/发布/部署。

## 下一条直接执行指令

复核上列4个 Codex-owned release-closeout 路径，确认与 P01 manifest 的保护路径无交集，仅显式stage并本地commit；commit前再核实原作者24项逐路径/hash未变。随后确认 Owner分支与worktree目标路径不存在，使用实际Live main HEAD创建 `agent/zcode/P02-real-webview-harness` linked worktree；验证分支、common-dir、clean status与HEAD，保存Owner启动checkpoint和真实dispatch结果。按 `zcode-dispatch` skill将 `verification/P02/zcode-task.prompt.md`实际派发给ZCode；只有确认接单后才将Task置为`in_progress`。跟踪真实Tauri/WebView2 AC1–AC7、正式DeepSeek Harness Review、修订及Codex集成Gate。P01不重做，不触碰原作者24项，不关机、不push、不发布、不部署。
