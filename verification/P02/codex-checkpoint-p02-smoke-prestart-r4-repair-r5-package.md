# 恢复点：P02 R4 finding 修复与 R5 exact-head Review 包

- 捕获时候选基线：HEAD=`3f243b1993dc577ea98aa8130c1a822ac57763a4`，tree=`7c1e4c3a180b268e3f8a6b10da913c869a25cfba`；branch=`codex/P02-process-isolation`；linked worktree=`C:\Users\49745\.codex\worktrees\p02-process-isolation-plan\New Manga`；common Git directory=`G:\CODEX\New Manga\.git`。
- 父 Task：P02 仍为 `in_progress / ACTIVE`。本切片 Owner/Integrator=Codex，非作者 Reviewer=DeepSeek Harness。用户授予的持续编排授权仍有效。
- 主工作区 Reality Check：`main@4183e7f7cf366c27aa8ad8a0bc7300af48783470`，common dir=`.git`，观察到 203 项既有 status entries；未修改主工作区文件。本 checkpoint 尚未重算 root manifest digest；集成前必须重新计算。
- 允许路径：`doc/00_INDEX.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/tasks/P02.md`、`verification/P02/**`。本切片不授权产品源码、契约/schema/依赖、HostFolder 写入/扫描、Sandbox start、Build、GUI 或产品测试。

## R4 finding 修复

- R4-01：R2/R3 `response_sha256` 表示提交后的 Git blob UTF-8 LF 字节 SHA；原始混合 EOL DSH worktree 字节哈希作为单独字段保留。Canonical hashes：R2=`9869F229DADD4A173C74B737321270AEF504C5266B2AA2A100CF999B41696612`；R3=`A07E7DE8DA8C2F1466763EDC037227C39E7E2C5900E616122B19CC3FB5D1A565`；R4=`A2F962B6494579C162F1D0FD36EE8985819108860967E189A3EA25B3BD04B3B4`。
- R4-02：Plan/Index 当前摘要不再把 R1 写成当前状态，并改为链接到本 R5 package checkpoint；R1–R4 的 Review 仍保留为历史证据。

## D10 验证与 R6 断言处置

以下结果均绑定候选 HEAD=`3f243b1993dc577ea98aa8130c1a822ac57763a4` / tree=`7c1e4c3a180b268e3f8a6b10da913c869a25cfba`：

- `r9f-current-prestart-route-validator-r6.stdout.log` 与 `.exit`：7/7 PASS，exit=0。
- `r9f-current-prestart-diff-check-r6.*`：base=`4183e7f7cf366c27aa8ad8a0bc7300af48783470` 到 HEAD，exit=0。
- `r9f-current-prestart-parent-diff-check-r6.*`：parent 到 HEAD，exit=0。
- `r9f-current-prestart-scope-assertions-r6.stdout.log`：103 tracked paths、out-of-scope=0；R2/R3/R4 blob hashes、原始哈希分离、R2 erratum、current pointers 均匹配。最后一项 `hard_build_barrier_preserved` 为 false，整体 `.exit=1`。独立只读 Review 未发现状态漂移：STATUS/Plan/Task/R4 checkpoint 使用 inline code 包裹状态值；Index 中写作裸文本 `Hard Build Barrier=EFFECTIVE`。R6 one-off checker 源码未留存，无法还原其确切字符串表达式。R6 必须保持 exit=1 的原始记录，不能改记为 PASS；屏障仍为 `EFFECTIVE`，Build 仍为 blocked。

## 当前 Gate 与下一步

当前 boundary=`R4_APPROVED / R4_P3_REPAIRED / R5_REVIEW_PENDING / NO_SANDBOX_START`。Smoke admission 仍只允许一次尝试；`wsb start=NOT_RUN`、Smoke=`NOT_RUN`、完整即时 preflight 未完成、Build Gate=`BLOCKED`、build=`NOT_AUTHORIZED / NOT_RUN`、hook/cache=`BLOCKED / NOT_VERIFIED`、AC1–AC7=`BLOCKED / NOT_RUN`、Hard Build Barrier=`EFFECTIVE`。

下一步：提交此 package；在提交后的固定 exact HEAD 上重新运行路线 validator、base/parent diff-check 和逐文件 scope/status 断言，新断言应接受状态值的裸文本及 inline-code 写法并报告每个文件的结果。随后从 detached worktree 派发 DSH R5 只读 Review。R5 Review 与所有新的即时准入检查通过前，Sandbox 必须保持未启动。