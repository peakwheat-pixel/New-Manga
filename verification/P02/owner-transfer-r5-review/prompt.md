请以 DeepSeek Harness 的身份对 New Manga 项目 P02 Owner 故障转移提案作固定head、只读独立范围审查。你不是该提案作者，不要修改任何仓库文件，不要启动产品/构建/测试进程，也不要声称 WebView、构建或产品 Gate 已通过。

固定输入：
- review base=`a37f11baa287ba27eb9f5c2e75dce7472b88caa8`
- reviewed head=`0b95c6a1024f89ae341c637c0d531611175acdc5`
- branch=`codex/P02-fallback-scope`
- worktree=`G:/CODEX/New Manga.worktrees/P02-fallback-scope-codex`
- fixed proposal=`verification/P02/scope-owner-transfer-r5.md`
- current formal Task=`doc/tasks/P02.md`
- prior P02 scope reviews=`verification/P02/scope-review-r2.md`, `scope-review-r4.md`
- current P02 recovery/evidence=`verification/P02/RESUME.md`, `verification/P02/antigravity-dispatch-r1.interruption.md`, `verification/P02/zcode-dispatch-r1.exit`
- project rules=`AGENTS.md`, `doc/09_COLLABORATION.md`, `doc/REBASELINE_PLAN.md`, `doc/STATUS.md`

请自行读取这些文件和固定 diff。核对Owner与Reviewer不同、项目fallback授权、真实ZCode失败和Antigravity未接单事实是否准确、Task是否仍ready/IDLE、提出的新branch/worktree是否能隔离旧dirty worktree、所有AC/allowlist/数据保护/产品禁写范围是否保持不变，以及是否需要重新审批。原scope r2/r4批准不得被夸大成已批准此次Owner变更；旧worktree里的未提交内容也不得推荐清理或集成。

输出一份简体中文审查报告，固定字段：Task/Review ID=`P02 owner transfer r5`、reviewer、base、reviewed_head、worktree、Decision=`approved|changes_requested|blocked`、P0/P1/P2/P3计数；Architecture与Verification两面结论；逐条finding（严重级别、路径/证据、影响、最小处置）；所读输入与实际只读检查、未运行的命令和局限；若approved，明确批准只覆盖Owner故障转移和新worktree隔离，不覆盖任何P02 AC/build/GUI结果或未来Owner交付。无finding也需明确写0项及所覆盖范围。不要引用聊天作为项目事实。
