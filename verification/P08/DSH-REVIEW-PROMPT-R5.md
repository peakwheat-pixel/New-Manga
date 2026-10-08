# P08 DSH 正式 Review Prompt（R5）

你是 P08 Task 的非作者 Reviewer。本轮只读审查固定交付；不要修改、创建或删除任何项目文件，不要 stage/commit/checkout，不得根据聊天记录推断项目事实。

## 固定范围

- 仓库：`G:/CODEX/New Manga`
- 精确审查 worktree：`G:/CODEX/New Manga.worktrees/P08-dsh-review-af1ddeec-r5`
- base：`16fb07a973b36b0b129945bc3a85f9ae51234982`
- reviewed head：`af1ddeec1b998f2ddaf121a85f5fd382561aae1e`
- common-dir 应为：`G:/CODEX/New Manga/.git`
- 当前 worktree 预期 detached、clean；若命令失败或无法核验，明确记`NOT_RUN`/`NOT_VERIFIED`，不要降格成PASS。
- R4正式报告：`verification/P08/review-dsh-16fb07a9-r4.md`，SHA256=`9259F9B0B1BED6C8AF0640E45CF3860308BFEC89E5757B233942A16FDDDE0AF6`。
- R4结果：固定head `16fb07a973b36b0b129945bc3a85f9ae51234982`获`approved`；N-07 P2、N-08 P3已独立关闭；新增R4-01..03为三个open/non-blocking P3。本轮需核实这三项作者修订并对新head给出独立结论。

## 审查目标

1. 以文件/Git证据确定`16fb07a..af1ddeec`固定差量，逐项检查`doc/STATUS.md`、`doc/handoffs/P08-490f9bd9.md`、`doc/tasks/P08.md`、`verification/P08/verify_scope.py`。确认没有越权文件或范围扩大；R5 Prompt/Handoff在post-delivery提交中，不属于被审head。
2. 逐项审查R4-01：`doc/STATUS.md`的P01–P21编号说明是否只说明编号、不再声称所有节点都`proposed / 未释放`，且实时状态有明确权威来源。
3. 逐项审查R4-02：`verify_scope.py`是否对固定`BASE..HEAD`的**已提交**差量实施正向allowlist；路径集合是否精确对应P08允许路径；路径谓词是否同时测试允许与拒绝样例；嵌套/外部文档和非P08 handoff是否会被拒绝。说明用`BASE..HEAD`而非脏工作树差量能否避免把主工作区原作者未提交修改归入P08；是否仍存在会漏过的路径边界。
4. 逐项审查R4-03：R1 Handoff是否指向实际报告`verification/P08/review-dsh-490f9bd.md`，并明确`doc/reviews/**`为受保护只读路径。
5. 检查N-07/N-08及R1/R2历史Finding closure无回退；D1–D7仍是用户已确认决定，不要重开或自行改写。
6. 检查D08逐项覆盖、四个一级页面、目标架构边界、共享契约/源文件保护、Architecture Documentation Rebaseline Gate及未释放的P09–P20没有被绕过。

## 独立验证

在精确 worktree 尝试执行，并记录实际环境、完整命令、EXIT和原始错误：

- `git rev-parse HEAD`
- `git status --porcelain=v1 --branch`
- `python -B -X utf8 verification/P08/verify_scope.py`
- `python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py`
- `git diff --check 16fb07a973b36b0b129945bc3a85f9ae51234982 af1ddeec1b998f2ddaf121a85f5fd382561aae1e -- <P08允许检查范围>`
- `git diff --name-only 16fb07a973b36b0b129945bc3a85f9ae51234982 af1ddeec1b998f2ddaf121a85f5fd382561aae1e -- <受保护源码/契约路径>`

不要把Codex在`validation.log`中记录的EXIT结果冒称为DSH亲自执行。若Windows ACL仍报`SetNamedSecurityInfoW` Win32 5，按真实边界记录`NOT_RUN`，不提权；仍可完成文件层只读Review，但将clean tree/命令证据限制如实写出。产品pytest/cargo/vitest/GUI/build/model不属于文档修订范围；无产品变更时记`NOT_RUN`。

## 正式报告格式

中文完整报告，遵循`doc/templates/REVIEW.md`，至少包括：frontmatter（Task/Reviewer/Author/base/reviewed_head/decision）、范围与依据、Architecture结论、Verification矩阵、R4-01..03逐项处置与复现证据、历史Finding回归、`NOT_RUN`/`NOT_VERIFIED`边界、风险与结论、符合`doc/09_COLLABORATION.md §5.1`的下一任务建议及可直接转发指令。

只有对被审head的实际证据支持时才标`approved`。P0/P1或关键验证缺失不得批准；任何新的P2及以上问题须明确决策和影响。非阻断P3也逐项列明。报告精确绑定上述固定head；不修改项目文件。
