# P08 DSH 正式 Review Prompt（R7）

你是P08 Task的非作者Reviewer。本轮只读审查固定交付；不得创建、修改、删除或暂存项目文件，不得checkout或commit，不得根据聊天记录推断事实。请用简体中文返回完整Review报告。CLI会收到本Prompt全文。本Prompt与R7 Handoff为delivery之后材料，位于主工作区；不属于固定交付，也不要求出现在精确Review worktree中。

## 固定审查范围

- 仓库：`G:/CODEX/New Manga`
- 精确Review worktree：`G:/CODEX/New Manga.worktrees/P08-dsh-review-fe222464-r7`
- base：`ecb3b520ce68c2ddcc0c5ec94596e2f50a17f369`
- reviewed head：`fe222464616152e9c95208e06c248565f2fd86a6`
- common-dir应为：`G:/CODEX/New Manga/.git`
- 预期worktree：detached、clean，HEAD严格等于reviewed head。无法执行时如实记录`NOT_RUN`/`NOT_VERIFIED`，不得记PASS。
- P08 Task原始基线：`ab2f813c0ce311a6712002cafd852b9e7a258380`
- R6已审head：`ecb3b520ce68c2ddcc0c5ec94596e2f50a17f369`；R6 base=`af1ddeec1b998f2ddaf121a85f5fd382561aae1e`；DSH session=`session-44947a36-b277-4118-8f82-635e1e803dd1`；CLI EXIT=0，decision=`approved`。
- R6 canonical report：`verification/P08/review-dsh-ecb3b520-r6.md`；SHA256=`7E486D1EC46CD0EBF3BEC280EDDDB837CE600715549E2E528027FF2FEB883C28`。R6报告与本机保存的raw stdout hash相同且逐字节相等；raw stdout不属于R7固定head。
- R7 Prompt/Handoff位于主工作区：`G:/CODEX/New Manga/verification/P08/DSH-REVIEW-PROMPT-R7.md`、`G:/CODEX/New Manga/doc/handoffs/P08-fe222464-dsh-r7.md`。本CLI任务已收到完整Prompt；这些delivery后文件只提供上下文，不属于base..reviewed head。

## 复核目标

1. 独立读取精确worktree中的`base..reviewed head`完整差量与P08 Task/依据，不只看Prompt摘要。确认范围仅在P08允许的Task/Plan/Status/导航、`verification/P08/**`、P08自有Handoff及派生路线图范围；确认没有产品源码、测试、打包、共享契约/Schema/依赖、冻结需求或用户数据变更。
2. 复核新增的本地Markdown链接规则：`verification/P08/verify_scope.py`应只对去除尖括号与fragment后的精确目标`…`或`...`跳过文件存在检查；所有其他具体相对链接仍须指向存在文件。检查没有用包含/前缀规则放宽检查，并确认同一固定head的P08 Task、所有P08 verification Markdown、所有`doc/handoffs/P08-*.md`链接均有效。
3. 检查R6 canonical报告作为本head新增证据文件的内容、SHA声明和与Task/Handoff历史的内部一致性；R5-01/R5-02仍由R6独立关闭，R6-01已于post-delivery `547894f59dc2e9ab89812d27efc511d432c6b6a9`修正。不能把R6对旧head的批准延伸到R7。
4. 检查D1–D7仍为已确认事实；P08在交付head快照中为`in_progress`、R7尚未完成，P09–P20仍proposed/未释放；Architecture Documentation Rebaseline对P09及P18/P20相应Gate的先决关系没有被绕过。主工作区delivery后metadata会把Task绑定本reviewed_head并设为`in_review`，不要把它错误归入fixed delivery差量。
5. 独立复核作者列出的范围和证据。若命令可运行，可执行：`python -B -X utf8 verification/P08/verify_scope.py`、`python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py`、`git diff --check ecb3b520ce68c2ddcc0c5ec94596e2f50a17f369 fe222464616152e9c95208e06c248565f2fd86a6`。报告须记录实际执行的shell、head和EXIT；DSH命令若受Windows ACL限制失败，应如实记`NOT_RUN`/`NOT_VERIFIED`，Codex日志不作为DSH执行结果。
6. 产品pytest/cargo/vitest/GUI/build/model不属于本次文档/验证器修订范围；没有实际执行时明确记`NOT_RUN`。不得从文档validator通过推断产品Gate通过。

## 报告格式

给出固定base/head与decision（`approved`或`changes_requested`）；Architecture与Verification覆盖；逐项列Finding ID、级别、文件/行、影响、证据与建议；区分DSH实际执行、`NOT_RUN`与`NOT_VERIFIED`。无问题时明确写“在记录范围内未发现问题”，并列出未覆盖风险。不要修改项目文件，不要把Codex验证写作DSH结果，也不要把未运行写成PASS。
