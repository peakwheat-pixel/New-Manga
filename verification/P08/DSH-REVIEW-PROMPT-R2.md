# P08 DSH 第二轮正式 Review

Task=P08：完整产品范围与验收冻结准备。请作为非作者 Reviewer，对下列固定交付做独立正式 Review。

- 仓库：`G:/CODEX/New Manga`
- 当前会话工作目录/精确Review worktree：`G:/CODEX/New Manga.worktrees/P08-dsh-review-31c2638`
- 基线：`ab2f813c0ce311a6712002cafd852b9e7a258380`
- 唯一被审查head：`31c263892605fdc984982b9ba1875fa6eb609cb6`
- 该worktree应保持detached、clean；不得切换或改动文件。
- Owner/作者：Codex。Reviewer：DeepSeek Harness。Integrator：Codex。

## 审查依据

完整审查 `git diff ab2f813c0ce311a6712002cafd852b9e7a258380 31c263892605fdc984982b9ba1875fa6eb609cb6`，并阅读：`AGENTS.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/09_COLLABORATION.md`、`doc/tasks/P08.md`、`verification/P08/SCOPE_DRAFT.md`、`verification/P08/AC_COVERAGE.md`、首轮报告 `verification/P08/review-dsh-490f9bd.md`、首轮Handoff `doc/handoffs/P08-490f9bd9.md`、`verification/P08/verify_scope.py`、`verification/PROJECT-ROADMAP-20261008/verify_plan.py` 及目标head包含的相关恢复和验证证据。

精确head验证由Codex在该clean worktree实际执行，命令为 `python -B -X utf8 verification/P08/verify_scope.py`、`python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py` 与完整Task/Plan/Status/P08/路线证据范围的 `git diff --check`，均EXIT=0。审查checkout中的validation.log可能只含更早checkpoint；新head验证证据会在主线的后续证据commit中追加，且明确绑定`reviewed_head=31c263892605fdc984982b9ba1875fa6eb609cb6`。如需读取，请用 `git show main:verification/P08/validation.log`；不要推进或变更本Review worktree的HEAD。若无法独立执行PowerShell命令，标记`NOT_RUN`并说明原因，不得将Codex结果写成DSH亲自运行。

## 首轮Finding逐项复核

首轮正式结论为`changes_requested`：0 P0、4 P1、6 P2及5项P3观察。请逐项对照首轮报告和本轮diff，判断修订是否完整、可追溯且没有引入新问题：

1. P1-1：验证日志是否绑定精确修订head、shell与PowerShell/Python绝对路径和版本、repo/branch/worktree、命令、EXIT；Task是否指向当前日志。
2. P1-2：Legacy 12条PASS与新架构`NOT_RUN`、ACG、§78草案AC、§74/75建议、§79 advisory的口径；AC-DOC-001..003在P09前的Gate；不得将建议或草案伪装成正式PASS。
3. P1-3：六项AC-WIN是否路由到ZCode负责的P12/P14/P15/P17 UI切片，P20仅负责平台/安装包验证；窗口/进程关闭行为的证据边界是否保留。
4. P1-4：D07/D08仍为Legacy基线的边界；stack-specific旧AC不能直接作为新架构PASS；D5数值及P0/P1保持不变；Architecture Documentation Rebaseline Gate正确登记为未编号、未释放的前置条件，没有虚构用户决策。
5. P2-1：STATUS同日矛盾是否被修正且Plan/Task状态一致。
6. P2-2：P09–P20依赖、P15备份暂停/排空关系、ZCode设计依赖与真实/拟议仓库路径是否一致。
7. P2-3：格式要求的临时权威位置、待单独文档重基线转录状态，以及TEXT生产安装包验证是否清楚。
8. P2-4：新架构验收`NOT_RUN`；用户选择PNG与D08单图语义区分；300ms页切换、4Hz/250ms TaskProgress、≤200ms暂停门槛均准确。
9. P2-5：D04来源引用是否准确，未推导其没有定义的`current`语义。
10. P2-6：只读保护路径、动态P08状态断言、全P08/Task治理空白检查是否有判别力。
11. P3观察：GATE-78顺序/表头、P20执行与Reviewer/Codex集成角色、第二轮prompt/Handoff固定head字段、保留Qoder历史但不恢复其资格。

## 用户已确认的产品范围

D1–D7均已确认，Reader基础能力已解冻，跨页联动与页缩略图仍延期。本轮不重新要求用户裁决，也不得扩大产品范围。D5现行P0/P1数值保持；不得自行变更D08、AD-001、doc/13，且不得把遗留栈PASS推成React/Tauri新架构PASS。P09–P20均未释放。

## 输出与边界

只读审查，不修改、stage或commit任何文件，不改动Git状态。直接在最终回答中提供可归档的完整Review报告，采用`doc/templates/REVIEW.md`字段：固定base/reviewed_head、Architecture与Verification结论、逐项finding（含ID/级别/路径和行/影响/证据/建议）、实际运行命令及环境/结果/EXIT、未运行检查及原因、结论`approved` / `changes_requested` / `blocked`。无问题时明确写未发现，不留模板占位。P0/P1未解决或关键验证缺失时不可批准；分别给出首轮finding closure状态，不能只给摘要。

如果发现新问题，引用目标head的具体文件/行和事实证据。不要自行修复；Codex会按Task授权闭环并建立新head复审。不要将你无法执行的检查写为PASS。
