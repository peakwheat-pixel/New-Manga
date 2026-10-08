# P08 可恢复检查点

时间：2026-10-08 23:42（Asia/Shanghai）；Agent=Codex；TaskStatus=in_progress；ExecutionState=ACTIVE（R5已独立批准；Codex集成与两项P3处置正在继续）。

## 当前事实

- 仓库：G:/CODEX/New Manga；Owner branch/worktree：main / G:/CODEX/New Manga。恢复核验前的提交HEAD=bfd70958（R5 Prompt/Handoff、状态和派发指令检查点）；R5 reviewed_head=af1ddeec1b998f2ddaf121a85f5fd382561aae1e，base=16fb07a973b36b0b129945bc3a85f9ae51234982。R5结果与导航同步尚未提交，恢复时以实时Git status为准。
- R5精确worktree=G:/CODEX/New Manga.worktrees/P08-dsh-review-af1ddeec-r5；review时detached、clean，HEAD与af1ddeec相等，common-dir=G:/CODEX/New Manga/.git。R5 Prompt=verification/P08/DSH-REVIEW-PROMPT-R5.md，Handoff=doc/handoffs/P08-af1ddeec-dsh-r5.md。
- DSH R5正式Review：session=session-14106c72-634b-4f94-a8d4-c72c91119d8f，CLI exit=0，decision=approved；报告=verification/P08/review-dsh-af1ddeec-r5.md，SHA256=2EA2ADA0A2CA99FC881FD9ADFC9F180461A3B427980635EFF05613A833A3B7EF，与原始stdout逐字节一致。session已通过mount_session.py --id挂入New Manga workspace，mount CLI exit=0；desktop下次启动可见，本轮未重启应用。
- R5独立关闭R4-01/R4-02/R4-03和历史N-07/N-08；无未闭合P0/P1/P2。新增R5-01与R5-02两个非阻断P3：分别要求allowlist谓词增加“非P08 Handoff”与doc/reviews拒绝样例，以及把doc/handoffs/P08-*.md纳入Markdown链接检查。Codex已修订两项，并将在固定新head后交DSH独立复审；不得把R5批准延用于新head。
- DSH文件层核对HEAD、detached和common-dir并执行文件Review；DSH自身shell/git/python/validator/diff-check因SetNamedSecurityInfoW Win32 5为NOT_RUN/NOT_VERIFIED。Codex验证独立记录。产品pytest/cargo/vitest/GUI/build/model=NOT_RUN（无产品代码或测试变更）。
- P08仍未done；Task现为in_progress，R5 P3修订待R6独立复核。D1–D7已由用户确认，不再询问。P09–P20均未释放。Architecture Documentation Rebaseline尚未登记，按Plan继续阻断P09与相应P18/P20目标架构Gate。
- 主工作区原作者/历史dirty必须保留、不可暂存/覆盖/stash/清理：.qoder-credits/report.json、.qoder-credits/通路探测__8602db50.canvas.tsx、verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/antigravity-dispatch.json、同目录antigravity-dispatch.stderr.log。P08 raw dsh-r4.stdout.md、dsh-r4.stderr.log、dsh-r5.stdout.md、dsh-r5.stderr.log均为任务临时原始输出，不提交；canonical R5报告才是正式证据。

## 接续步骤

1. 先检查实时branch/HEAD/status/common-dir、P08 Task状态、R5 canonical report hash以及DSH session记录；不要重跑R5。
2. 完成R5结果同步：Task/Plan/Status/依赖图/README/RESUME、R5 Handoff与validation.log标记R5 approved、R4-01..03 closed、R5-01/R5-02 open；将canonical report加入版本控制。只显式暂存Task授权路径；保护其他Agent和用户的dirty文件。
3. 核对两项R5 P3后，已按最小范围修改verification/P08/verify_scope.py：添加非P08 Handoff与doc/reviews拒绝例，并将P08 Handoff加入Markdown本地链接检查；扩展后validator已EXIT=0。固定交付前再次核对历史Handoff链接，不改写不必要的历史证据。
4. 更新P08 Task、状态导航、Handoff和validation.log至作者修订head；运行两项文档validator、该fixed head的git diff --check、正向allowlist和受保护路径差量检查。
5. 固定作者delivery后，为R6生成post-delivery Prompt/Handoff，指定DSH非作者只读复核R5-01/R5-02及既有Finding；R6返回前保持新Finding open，不集成、不标P08 done。
6. 新head复核通过后执行Codex集成Gate，更新Task/Plan/Status/依赖图/恢复点。随后从REBASELINE_PLAN选择依赖满足、范围冻结且正式释放的下一Task，继续自动推进。

## 下次恢复自动推进提示词（复制整段使用）

请从本项目实时状态继续持续自动推进，直到项目目标完成，或遇到必须由我决定的产品取舍。你已获明确授权读取/修改项目文件、使用适用Skill/Agent、恢复检查点、创建和使用分支/worktree、运行适当检查、提交变更，并按治理规则集成通过Review与Gate的工作。每个Task均核对验收、真实测试证据、独立Review、集成Gate与集成后验证，更新Task、Plan、Status、依赖图及恢复点，然后自动推进依赖满足、范围冻结并已正式释放的下一Task；不要只给计划，也不要等我逐项说“下一步”。

唯一仓库是G:/CODEX/New Manga。恢复先实测branch/HEAD/status/common-dir，核对AGENTS.md、doc/REBASELINE_PLAN.md、doc/00_INDEX.md、doc/STATUS.md、doc/09_COLLABORATION.md、当前Task和本恢复点。以仓库文件、代码和命令为事实，不凭聊天记录推断Task完成，不重复已完成的全库审计。

当前检查点：P08 D1–D7已确认；R5已对固定base 16fb07a973b36b0b129945bc3a85f9ae51234982与reviewed_head af1ddeec1b998f2ddaf121a85f5fd382561aae1e返回approved，DSH session=session-14106c72-634b-4f94-a8d4-c72c91119d8f、CLI exit=0，报告与SHA256见verification/P08/RESUME.md及P08 Task。DSH session已挂载。不要重派R5或伪造/改写其结果。R5关闭R4-01..03与N-07/N-08，新增R5-01/R5-02两个非阻断P3。按本恢复点的授权继续修复两项，固定新head后用dsh-dispatch派DSH做R6非作者复核；报告返回前保持Task未完成。R6通过后执行Codex集成Gate，再按权威Plan自动选择下一项。

严格保护原作者dirty、用户数据、人工修改、Lock、current/pinned Revision、密钥及其他Agent内容；禁止误stage/reset/stash/覆盖/清理上述路径和P08临时原始输出，只显式暂存授权文件。Qoder已退出，绝不分配。D1–D7不重问。遇到未决产品取舍时继续不依赖该选择的工作，并一次性向我列明问题和影响，暂停受影响工作。不得执行未获授权的部署、外部发布或不可逆数据操作。

我还明确授权：仅当本轮完整自动推进目标全部完成，且没有待处理Task/Review/Gate/阻塞时，才关闭计算机；工作仍在进行或因产品决定暂停时不要关机，也不要再次询问。

RESUME_SAFE。P08尚未done，P09–P20未释放。Review结论与Codex验证分别记录；NOT_RUN/NOT_VERIFIED不得记PASS。
