# P02 恢复点

## 当前检查点：P02范围已正式释放；main集成与post-FF Gate通过；待创建Owner worktree及真实派发

- Timestamp：2026-10-09T03:33:26Z。Live root=`G:/CODEX/New Manga`，branch=`main`，已验证的closeout parent HEAD=`cb389fd933304778eb7829da2da6df1a80b4c5ad`，`main...origin/main [ahead 1248]`；本恢复点自身是待提交的Task-local checkpoint更新，恢复时应先解析实际Live HEAD。scope branch=`codex/P02-harness-scope`在release commit=`3c3e4687785e65f668f1146052e78c3da074ba99`，scope worktree=`G:/CODEX/New Manga.worktrees/P02-harness-scope`干净；两个路径共用`G:/CODEX/New Manga/.git`。
- P02 scope/release commit=`3c3e4687785e65f668f1146052e78c3da074ba99`，父=`241ff3b70b6fc0490ea238efd486cc707f849031`，已本地 fast-forward 到 main。post-FF closeout commit=`cb389fd933304778eb7829da2da6df1a80b4c5ad`，正式报告=`release-post-ff-check.txt`。P02 Task的`base_commit=241ff3b...`仍为代码/行为基线，`integration_commit=null`表示Owner实现尚未集成。
- P01 frozen manifest SHA=`b41835453b693b4e62818216e4d67801c01eca6e33450f8d3d3dd72849d578e7`；原作者24个 dirty/untracked 每次复核均24/24、0 mismatch，release差量与它们交集0。当前root `git status`应只有该24项（本checkpoint未提交文件可能额外出现；不得把它们当作原作者文件清理）。不得 stage、stash、覆盖或清理 manifest 中任何项。
- P02是唯一Active/released Task，`status=ready`、ExecutionState=`IDLE`。Owner=`ZCode`；正式非作者实现Reviewer=`DeepSeek Harness`；Integrator=`Codex`。Owner branch=`agent/zcode/P02-real-webview-harness`，path=`G:/CODEX/New Manga.worktrees/P02-real-webview-harness-zcode`；预定从checkpoint文件提交后的最新Live main真实HEAD起步，记录实际start HEAD。Owner worktree与branch尚不存在，尚未dispatch。正式指令=`verification/P02/zcode-task.prompt.md`。Qoder已退出，绝不分配。
- AC/Owner allowlist r2 SHA=`27DC31A8CF3304ABA6783E243F36895FFE4AAA3CCBCA76D58E8B766C403E1425` approved；r3发现 `P02-SCOPE-R3-01`，逐一状态校验修订后由独立Reviewer r4 `approved`并关闭。r4报告=`scope-review-r4.md`，固定输入SHA见报告及Task。该批准只覆盖scope/governance，不是产品验收或正式DSH实现Review。
- 释放 Gate：28个授权路径、0越界；validator、两项route mutation拒绝probe、12个Task-local Markdown链接均通过；release commit无 `src/apps/tests/packaging` 产品/build/test路径。post-FF `git diff --check`、validator、probe、本地链接、原作者manifest均PASS；详见`scope-path-allowlist.log`、`release-post-ff-check.txt`。P02 AC1–AC7、前端build、Vitest和真实WebView/GUI仍`NOT_RUN`。
- DSH availability probe exit 0仅证明CLI可用，不等于dispatch或Review；session=`session-915691c6-4075-4867-b331-e3ea55f1b451`已挂载，Web/Desktop可见性未验证。禁止对外push、发布、部署或关机。

## 下一条直接执行指令

先完成并仅stage/提交本恢复点及更新后的NEXT提示词；确认该两路径与P01 manifest无交集并重核24项status/hash。然后基于新的Live main HEAD核实Owner path/branch不存在，创建指定ZCode linked worktree，验证common-dir、branch、start HEAD和clean状态。保存Owner启动恢复点并使用`zcode-dispatch`真实派发`zcode-task.prompt.md`；必须有实际接单证据才将Task切为`in_progress`。随后跟踪AC1–AC7、正式DeepSeek Harness Review、修订和Codex Integration Gate。若ZCode不可用按AGENTS故障转移顺序选Antigravity；不分配Qoder。保护根24项，不重做P01，不关机、不push、不发布、不部署。
