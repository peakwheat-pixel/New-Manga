# P02 恢复点

## 当前检查点：P02范围已正式释放；main集成与post-FF Gate通过；ZCode Owner worktree已创建并同步，待真实派发

- Timestamp：2026-10-09T03:37:42Z。Live root=`G:/CODEX/New Manga`，branch=`main`；最后验证的main checkpoint parent HEAD=`9c88165e0cb3fb1437bf711e3c770e7c8f917034`，随后仅有恢复点提交到达`1cb54d82f0e261924866245da52ed01ef02092b0`。当前本次Owner-worktree checkpoint仍待提交；恢复时先以Git解析实际Live HEAD。scope branch=`codex/P02-harness-scope`在release commit=`3c3e4687785e65f668f1146052e78c3da074ba99`，scope worktree干净；root与linked worktrees共用`G:/CODEX/New Manga/.git`。
- P02 scope/release commit=`3c3e4687785e65f668f1146052e78c3da074ba99`，父=`241ff3b70b6fc0490ea238efd486cc707f849031`，已本地 fast-forward 到 main。post-FF closeout commit=`cb389fd933304778eb7829da2da6df1a80b4c5ad`，正式报告=`release-post-ff-check.txt`。P02 Task的`base_commit=241ff3b...`仍为代码/行为基线，`integration_commit=null`表示Owner实现尚未集成。
- P01 frozen manifest SHA=`b41835453b693b4e62818216e4d67801c01eca6e33450f8d3d3dd72849d578e7`；原作者24个 dirty/untracked 每次复核均24/24、0 mismatch，release差量与它们交集0。当前root `git status`应只有该24项（本checkpoint未提交文件可能额外出现；不得把它们当作原作者文件清理）。不得 stage、stash、覆盖或清理 manifest 中任何项。
- P02是唯一Active/released Task，`status=ready`、ExecutionState=`IDLE`。Owner=`ZCode`；正式非作者实现Reviewer=`DeepSeek Harness`；Integrator=`Codex`。Owner branch=`agent/zcode/P02-real-webview-harness`，path=`G:/CODEX/New Manga.worktrees/P02-real-webview-harness-zcode`。已于main `9c88165e0cb3fb1437bf711e3c770e7c8f917034`创建，随后仅快进同步至main checkpoint parent `1cb54d82f0e261924866245da52ed01ef02092b0`；创建时及同步后均clean，common-dir正确。尚未dispatch，Task保持ready；派发前应记录最新实际HEAD。正式指令=`verification/P02/zcode-task.prompt.md`。Qoder已退出，绝不分配。
- AC/Owner allowlist r2 SHA=`27DC31A8CF3304ABA6783E243F36895FFE4AAA3CCBCA76D58E8B766C403E1425` approved；r3发现 `P02-SCOPE-R3-01`，逐一状态校验修订后由独立Reviewer r4 `approved`并关闭。r4报告=`scope-review-r4.md`，固定输入SHA见报告及Task。该批准只覆盖scope/governance，不是产品验收或正式DSH实现Review。
- 释放 Gate：28个授权路径、0越界；validator、两项route mutation拒绝probe、12个Task-local Markdown链接均通过；release commit无 `src/apps/tests/packaging` 产品/build/test路径。post-FF `git diff --check`、validator、probe、本地链接、原作者manifest均PASS；详见`scope-path-allowlist.log`、`release-post-ff-check.txt`。P02 AC1–AC7、前端build、Vitest和真实WebView/GUI仍`NOT_RUN`。
- DSH availability probe exit 0仅证明CLI可用，不等于dispatch或Review；session=`session-915691c6-4075-4867-b331-e3ea55f1b451`已挂载，Web/Desktop可见性未验证。禁止对外push、发布、部署或关机。

## 下一条直接执行指令

先仅stage并提交本恢复点及NEXT提示词这两条Task-local路径；确认它们与P01 manifest无交集并逐项重核24项status/hash。随后读取新Live main真实HEAD，把已存在的clean Owner worktree仅快进同步到该HEAD，核对branch/common-dir/HEAD/status；不得重复创建或清理worktree。实际调用`zcode-dispatch`将`zcode-task.prompt.md`派发到该Owner worktree，保存CLI命令、会话、退出码及回答；Owner必须确认接单并记录start checkpoint，之后才可将Task改为`in_progress`。继续追踪AC1–AC7、正式DeepSeek Harness Review、修订及Codex Integration Gate；若ZCode不可用则按AGENTS故障转移到Antigravity，绝不分配Qoder。保护root原24项，不重做P01，不关机、不push、不发布、不部署。
