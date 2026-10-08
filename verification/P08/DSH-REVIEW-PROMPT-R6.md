# P08 DSH 正式 Review Prompt（R6）

你是P08 Task的非作者Reviewer。本轮只读审查固定交付；不要创建、修改、删除或暂存任何项目文件，不要checkout或commit，不得根据聊天记录推断事实。中文返回完整Review报告。本Prompt与R6 Handoff是delivery之后追加的审查材料，保存在主工作区；它们不属于固定交付，也不应复制进或要求存在于干净的Review worktree。CLI会收到本Prompt全文。

## 固定审查范围

- 仓库：G:/CODEX/New Manga
- 精确审查worktree：G:/CODEX/New Manga.worktrees/P08-dsh-review-ecb3b520-r6
- base：af1ddeec1b998f2ddaf121a85f5fd382561aae1e
- reviewed head：ecb3b520ce68c2ddcc0c5ec94596e2f50a17f369
- common-dir应为：G:/CODEX/New Manga/.git
- 预期worktree：detached、clean，HEAD严格等于reviewed head。命令无法执行时如实记NOT_RUN/NOT_VERIFIED，不要记PASS。
- P08 Task基线仍为：ab2f813c0ce311a6712002cafd852b9e7a258380
- R5报告：verification/P08/review-dsh-af1ddeec-r5.md；SHA256=2EA2ADA0A2CA99FC881FD9ADFC9F180461A3B427980635EFF05613A833A3B7EF；DSH session=session-14106c72-634b-4f94-a8d4-c72c91119d8f；CLI exit=0，decision=approved。
- 本Prompt与R6 Handoff读取位置：主工作区 `G:/CODEX/New Manga/verification/P08/DSH-REVIEW-PROMPT-R6.md` 与 `G:/CODEX/New Manga/doc/handoffs/P08-ecb3b520-dsh-r6.md`。仅固定worktree内的`base..reviewed head`是本轮受审交付。

## 复核目标

1. 以文件/Git证据审查固定base..head差量，检查是否仅在P08授权路径内；Prompt与本R6 Handoff是delivery之后追加，不属于被审head。确认没有产品、测试、共享契约、Schema、依赖、冻结需求或用户数据改动。
2. 逐项复核R5-01：verification/P08/verify_scope.py的allowed()自检是否明确断言拒绝非P08 Handoff（如doc/handoffs/M2-x.md）和doc/reviews/**（如doc/reviews/x.md）；既有正向allowlist是否仍约束固定BASE..HEAD已提交差量且排除他人未提交dirty。
3. 逐项复核R5-02：本地Markdown链接解析循环是否包含doc/handoffs/P08-*.md；其余链接范围是否正确，固定head中所有P08 Handoff链接是否可解析；R6 Handoff为delivery后追加，不要求它出现在固定worktree或base..head差量中。
4. 检查R4-01/R4-02/R4-03、N-07/N-08及此前P0/P1/P2 Finding是否回退；D1–D7保持用户已确认事实，不作为Reviewer裁决。
5. 检查文档状态、Task、Plan及派生路线图：固定delivery head `ecb3b520`中的P08 frontmatter与Plan快照仍记为`in_progress`，属于交付时的前置状态；delivery之后追加的主工作区状态同步把P08更新为`in_review`、绑定reviewed_head=`ecb3b520`、review_session=`pending`。这两个时间点不应混为矛盾。可从上述主工作区绝对路径读取post-delivery状态文档；报告需列明来源和提交边界。P09–P20仍未释放；R5-01/R5-02在R6独立确认前保持open；架构文档重基线Gate仍未绕过。
6. 独立复算这两项P3修订，不沿用作者自述。记录实际读取/命令、环境、head、EXIT和覆盖边界；区分DSH自身执行和Codex evidence。

## 结果格式

返回固定base/head、decision（approved/changes_requested）、Finding ID/级别/文件与位置/影响/证据/处置；分列DSH实际执行、NOT_RUN、NOT_VERIFIED。无发现也需描述实际覆盖和未覆盖风险。不要将Codex命令记录写成DSH结果，也不要把NOT_RUN或NOT_VERIFIED写成PASS。
