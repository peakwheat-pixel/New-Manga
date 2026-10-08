# P08 可恢复检查点

时间：2026-10-08 23:30（Asia/Shanghai）；Agent=Codex；TaskStatus=in_review；ExecutionState=ACTIVE（R4已approved；R4-01..03已修订并固定在R5审查head；R5交接材料待正式派发）。

## 当前事实

- 仓库：G:/CODEX/New Manga；Owner branch/worktree：main / G:/CODEX/New Manga；当前P08 delivery head：af1ddeec1b998f2ddaf121a85f5fd382561aae1e；R5固定base：16fb07a973b36b0b129945bc3a85f9ae51234982。
- R5只读worktree：G:/CODEX/New Manga.worktrees/P08-dsh-review-af1ddeec-r5。本次恢复核对：detached、clean，HEAD=af1ddeec1b998f2ddaf121a85f5fd382561aae1e，common-dir=G:/CODEX/New Manga/.git，git diff --exit-code HEAD -- . EXIT=0。
- R5 Prompt=verification/P08/DSH-REVIEW-PROMPT-R5.md；Handoff=doc/handoffs/P08-af1ddeec-dsh-r5.md。DSH CLI版本=0.1.7-rc.2。R5尚未派发；session、CLI exit和报告都不存在，不能写作已运行。
- R4正式结果：fixed head=16fb07a973b36b0b129945bc3a85f9ae51234982，DSH session=session-eafdd15a-13da-4abf-86fc-1cb444c715ff，CLI exit=0，decision=approved，报告=verification/P08/review-dsh-16fb07a9-r4.md，SHA256=9259F9B0B1BED6C8AF0640E45CF3860308BFEC89E5757B233942A16FDDDE0AF6。R4独立关闭N-07/N-08，未发现未闭合P0/P1/P2；DSH shell/git/python检查受Win32 5影响为NOT_RUN/NOT_VERIFIED，产品pytest/cargo/vitest/GUI/build/model=NOT_RUN。
- R4-01..03的作者修订已在af1ddeec固定；三项保持open直至R5独立确认。R5批准后仍需Codex集成Gate；只有验收、Review、集成及集成后验证都满足才能将P08置done。
- D1–D7均已由用户确认，不再询问。P08为文档/验收冻结Task；产品源码与测试未修改。P系列状态仍为0/21完成、P08 in_review、其他20项未释放。
- 主工作区原作者/历史dirty保留且未暂存：.qoder-credits/report.json、.qoder-credits/通路探测__8602db50.canvas.tsx、verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/antigravity-dispatch.json、同目录antigravity-dispatch.stderr.log；P08 R4临时输出verification/P08/dsh-r4.stdout.md、verification/P08/dsh-r4.stderr.log也仍未跟踪。任何恢复都不得误暂存、覆盖、stash或清理。
- 治理导航、ROADMAP图和本恢复点正校准为“R5材料已准备、待派发”。P08验证证据追加在verification/P08/validation.log。完整历史逐轮finding、命令和hash以P08 Task、各Review报告及validation.log为准，不重复全库审计。

## 本恢复点接下来要执行

1. 检查实时Git/Task状态、P08当前diff和原作者dirty路径；只暂存本Task明确允许的文档，不使用git add .。
2. 运行python -B -X utf8 verification/P08/verify_scope.py、python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py、对授权P08差量运行git diff --check；记录命令、环境、EXIT和未运行项。
3. 显式暂存并提交P08导航、Task、R5 Prompt/Handoff、验证日志与恢复点。
4. 使用已加载的dsh-dispatch skill，在精确R5 worktree执行Prompt中固定范围的只读正式Review；记录原始结果和错误输出，核验exit、报告内容及Hash。成功后按skill核实新session并显式挂载到New Manga workspace；不得挂载AUTH失败的空session。DSH session将在Desktop下次启动后显示，不要替用户重启应用。
5. 若R5提出发现，按授权范围最小修订，固定新head，再交不同Reviewer复审；若R5 approved，完成Codex集成Gate后更新Task/Plan/Status/依赖图/恢复点。随后依据唯一权威路线图与依赖/释放状态继续已满足条件的Task。Qoder已退出，绝不分配；产品取舍不得自行决定。

## 下次恢复自动推进提示词（复制整段使用）

请从本项目的实时状态继续持续自动推进，直到项目目标完成，或遇到必须由我决定的产品取舍。你已获明确授权读取/修改项目文件、使用合适的Skill和Agent、建立/恢复Task检查点、创建或使用分支/worktree、运行适当检查、提交变更，并按项目治理集成通过Review和Gate的工作。每完成一个Task就核验验收条件、实际测试证据、非作者Review、Codex集成Gate，更新Task、Plan、Status、依赖图和恢复点，并继续启动依赖已满足、范围已冻结且已正式释放的下一项工作；不要只给计划，也不要等我逐项说“下一步”。

唯一仓库是G:/CODEX/New Manga。恢复先实测Git branch/HEAD/status/common-dir，核对当前Task、Plan、STATUS、AGENTS.md、doc/09_COLLABORATION.md与本恢复点；以实时项目文件、代码和命令证据为准，从当前检查点继续，不重复已完成的全库审计，不凭聊天历史宣布完成。

当前精确检查点：P08 D1–D7已确认；R4固定head 16fb07a973b36b0b129945bc3a85f9ae51234982已由DSH独立approved，报告与SHA256见本文件。R4-01..03作者修订已固定于delivery head af1ddeec1b998f2ddaf121a85f5fd382561aae1e。R5只读worktree=G:/CODEX/New Manga.worktrees/P08-dsh-review-af1ddeec-r5，应为detached clean，common-dir=G:/CODEX/New Manga/.git。R5 Prompt=verification/P08/DSH-REVIEW-PROMPT-R5.md，Handoff=doc/handoffs/P08-af1ddeec-dsh-r5.md；检查当前P08恢复点了解是否已派发，若没有就完成文档同步和验证后，立即用dsh-dispatch正式派发R5，不要重跑R4。R5未实际返回前不得伪造session、exit、报告、批准或finding状态。R5报告返回后，核验、归档并hash报告；按结果修订/复审，或执行Codex集成Gate。P08通过全部Gate后才可done，并据权威Plan继续下一项。

严格保护原作者未提交文件、用户数据、人工修改、Lock、current/pinned Revision、密钥和其他Agent内容。不得stage/reset/stash/覆盖上述原作者dirty路径或P08 R4临时输出；只显式暂存授权路径。Qoder已退出，绝不分配Owner、Reviewer或设计工作。D1–D7不重问。若出现未解决产品取舍，继续所有不依赖该决定的工作，并一次性向我列出具体问题和影响，暂停受影响分支。未经明确范围授权，不执行生产部署、外部发布或不可逆数据操作。

我另已明确要求：只有本轮完整授权的自动推进目标确实全部完成，且没有待处理Task、Review、Gate或阻塞时，才关闭计算机。运行中或因产品决策暂停时不要关机，也不要再次询问这项授权。

## 状态约束

RESUME_SAFE。P08尚未done；后继产品Task未释放；R5当前待正式派发。恢复时先查live Git和本文件，不重跑已完成审计。Review意见与Codex验证分别记录，NOT_RUN/NOT_VERIFIED永不记为PASS。
