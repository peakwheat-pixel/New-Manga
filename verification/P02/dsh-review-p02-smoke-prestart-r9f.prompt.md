# DSH exact-head review：P02 R9F evidence citation corrections

请作为非作者 Reviewer，对下列固定提交作独立 exact-head review。不要修改工作树。

- Repository/review worktree：`G:\CODEX\New Manga.worktrees\P02-process-isolation-review-dsh-r7` (detached, clean)
- Candidate worktree：`C:\Users\49745\.codex\worktrees\p02-process-isolation-plan\New Manga`
- Branch：`codex/P02-process-isolation`
- Base：`5fe19efbedf6d46407c92fa7b73897e6794863e2`
- Fixed Delivery HEAD：`d90dd8f1d44dd022314bb63a305b013dcadb6a44`
- Fixed tree：`ad67989bee362c29fdedaa0fb44bf4864de693c7`
- Review scope：仅 `git diff 5fe19efbedf6d46407c92fa7b73897e6794863e2..d90dd8f1d44dd022314bb63a305b013dcadb6a44`；产品源码、依赖、shared contract/schema 均不在范围内。

先验证 `git rev-parse HEAD` 和 `git show -s --format=%T HEAD` 与上述固定值一致。然后检查该 commit 是否完整修复 R9 follow-up Review 新增的三个 findings：

1. R9F-01/P2：所有 artifact/self-test 引用指向 commit 内已提交的完整日志路径，checkpoint 的 delivery/review 状态边界准确。
2. R9F-02/P3：route/diff 证据是 `5fe19efbedf6d46407c92fa7b73897e6794863e2` 上真实生成并随交付提交的输出；没有继续引用来自 amend 前、非祖先 HEAD 的旧日志。
3. R9F-03/P3：R2 artifact validation 与 synthetic self-test 的 revision 用完整文件名区分，无 `R5/R4` 之类歧义简称。

同时检查 Task、Plan、Status、Index、checkpoints 彼此一致，证据引用可解析，产品 Gate 状态仍准确保持 blocked/not-run。checkpoint 中的 R3 precommit route/diff 日志不得误称为 exact-head 结果；请在固定 HEAD 上独立运行只读路线 validator 与 `git diff HEAD^ HEAD --check` 并报告其 exit code，不要更改文件。

禁止读取、枚举、扫描或哈希 HostFolder 内容；不要运行 HostFolder recheck/scanner、`wsb start`、Windows Sandbox、guest command、Build、runner、Vitest、GUI、WebView、Cargo 或产品测试。不得将 UNKNOWN/BLOCKED/NOT_RUN 记为 PASS。

请按固定 Review 模板返回：`APPROVED` / `APPROVED_WITH_CONDITIONS` / `CHANGES_REQUESTED` / `BLOCKED`，列出 P0/P1/P2/P3 数量、每项的文件与行号、证据、是否阻断，以及你实际执行的命令和 exit code。只有无 open finding 且上述 exact HEAD/tree 确认后才可 APPROVED。
