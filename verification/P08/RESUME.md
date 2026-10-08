# P08 可恢复检查点

时间：2026-10-09 00:02（Asia/Shanghai）；Agent=Codex；TaskStatus=in_review；ExecutionState=ACTIVE（R6 Review材料已备妥，正式DSH派发待执行）。

## 当前事实

- 唯一仓库：`G:/CODEX/New Manga`；主工作区branch=`main`；R6准备文档/状态同步checkpoint commit=`547894f59dc2e9ab89812d27efc511d432c6b6a9`；common-dir=`G:/CODEX/New Manga/.git`。R6固定交付head=`ecb3b520ce68c2ddcc0c5ec94596e2f50a17f369`；恢复时以实时Git为准。
- R6精确Review worktree=`G:/CODEX/New Manga.worktrees/P08-dsh-review-ecb3b520-r6`；已现场核验detached、clean、HEAD=`ecb3b520ce68c2ddcc0c5ec94596e2f50a17f369`、common-dir正确、`git diff --exit-code HEAD -- .` EXIT=0。
- R6 base=`af1ddeec1b998f2ddaf121a85f5fd382561aae1e`，reviewed_head=`ecb3b520ce68c2ddcc0c5ec94596e2f50a17f369`；正式Prompt=`verification/P08/DSH-REVIEW-PROMPT-R6.md`，post-delivery Handoff=`doc/handoffs/P08-ecb3b520-dsh-r6.md`；预期报告=`verification/P08/review-dsh-ecb3b520-r6.md`。DSH native session当前为pending，尚未派发。
- R6固定head已由Codex在精确worktree验证：`verify_scope.py` EXIT=0（193项D08 AC、AC-SMOKE、12 gates、31个allowlist差量文件、5份head内P08 Handoff链接/whitespace覆盖）；`verify_plan.py` EXIT=0（196历史节点、105 ancestry、21计划节点及依赖图/链接）；base..head `git diff --check` EXIT=0；受保护产品/契约路径差量为空；clean worktree身份检查EXIT=0。证据在`verification/P08/validation.log`，均为Codex结果，不是DSH结果。产品pytest/cargo/vitest/GUI/build/model=`NOT_RUN`（本Task没有产品代码/测试修改）。
- DSH R5正式Review：base=`16fb07a973b36b0b129945bc3a85f9ae51234982`，reviewed_head=`af1ddeec1b998f2ddaf121a85f5fd382561aae1e`，session=`session-14106c72-634b-4f94-a8d4-c72c91119d8f`，CLI exit=0，decision=`approved`；报告=`verification/P08/review-dsh-af1ddeec-r5.md`，SHA256=`2EA2ADA0A2CA99FC881FD9ADFC9F180461A3B427980635EFF05613A833A3B7EF`，stdout与canonical report逐字节一致，session已挂载到New Manga workspace。R5关闭R4-01..03、N-07/N-08；R5-01/R5-02为两项非阻断P3，Codex已在ecb3b520修订，仍open至R6独立确认。
- 权威状态：P08=`in_review`；D1–D7已确认，不再询问；P09–P20均`proposed / 未释放`。Architecture Documentation Rebaseline Task尚未登记，AC-DOC-001..003仍须先于P09释放，stack-specific目标等价映射须先于P18/P20对应Gate。所有新架构产品验收仍`NOT_RUN`。
- 必须保护且不暂存/覆盖/stash/reset/clean：原作者`.qoder-credits/report.json`修改、`.qoder-credits/通路探测__8602db50.canvas.tsx`未跟踪、`verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/antigravity-dispatch.json`与`antigravity-dispatch.stderr.log`未跟踪；P08原始`dsh-r4.*`、`dsh-r5.*`日志也不提交。只显式暂存已授权P08/导航/派生Checkpoint文件。R6 Prompt/Handoff及Task导航修订属于本任务；DSH正式报告与session hash核对后再归档。
- 不恢复Qoder分配。不得外推Review或验证范围，不得把NOT_RUN/NOT_VERIFIED记为PASS；不得发布或部署。用户明确授权的关机仅在整个项目目标完成、无待处理Task/Review/Gate/阻塞时执行；若产品裁决阻塞则保存checkpoint并保持开机。

## 下一条可直接执行的指令

1. 复核`git status --short --branch`、HEAD、common-dir及本文件；准备提交`547894f59dc2e9ab89812d27efc511d432c6b6a9`已保存R6 Prompt/Handoff与状态导航，确认受保护dirty文件仍未stage。
2. 读取`verification/P08/DSH-REVIEW-PROMPT-R6.md`，从精确worktree`G:/CODEX/New Manga.worktrees/P08-dsh-review-ecb3b520-r6`派发正式只读DSH Review。按`dsh-dispatch`技能保存stdout/stderr，记录CLI exit；成功后核实唯一新session、按session ID挂载，并将原文SHA256与canonical report逐字节核对。
3. R6返回后分别记录DSH实际执行/NOT_RUN/NOT_VERIFIED与Codex Gate。若approved且无未关闭Finding，继续Codex集成Gate；若changes_requested，按允许路径修订、固定新head并再次独立Review。不得把ecb3b520上的批准延伸到新head。
4. P08满足所有AC、Review、集成和集成后验证后，更新Task/Plan/Status/依赖图/RESUME。再按`doc/REBASELINE_PLAN.md`和`doc/STATUS.md`选择依赖已满足、范围冻结的下一Task，创建正式Task、核对共享范围、登记释放状态并指定不同Owner/Reviewer，然后继续自动推进。

## 下次恢复自动推进提示词（复制整段使用）

请从G:/CODEX/New Manga的实时Git与`verification/P08/RESUME.md`恢复，持续自动推进已授权的项目路线，直至完整项目目标达成，或遇到必须由我决定的产品问题。先核对branch/HEAD/status/common-dir、`doc/REBASELINE_PLAN.md`、`doc/00_INDEX.md`、`doc/STATUS.md`、`doc/09_COLLABORATION.md`、当前Task和恢复点；不要依聊天记录判断完成，也不要重做已完成的全库审计。

当前固定点：P08=`in_review`；R5对`af1ddeec1b998f2ddaf121a85f5fd382561aae1e`正式approved，R5-01/R5-02作者修订固定于`ecb3b520ce68c2ddcc0c5ec94596e2f50a17f369`。R6 base/head、精确worktree、Prompt/Handoff、Codex验证和R5报告/session见本文件。R6尚待派发；先确认准备元数据已提交，再按固定Prompt做DSH正式非作者Review并挂载真实session。绝不重派R5、伪造Review或把Codex验证说成DSH结果。R6通过后做Codex集成Gate；P08完成后按权威Plan正式登记/释放下一项依赖已满足的工作并继续。

用户已授权修改项目文件、读取/恢复检查点、创建任务/分支/worktree、使用合适Skill与Agent、运行适当检查、提交及集成通过Review/Gate的工作。Owner与Reviewer必须不同；Qoder已退出，绝不分配。每个Task完成后检查验收、测试证据、独立Review、集成Gate并更新Task/Plan/Status/依赖图/Resume，再自动选取下一项；不因常规实现细节或已裁决D1–D7询问用户。

严格保护用户数据、人工修改、Lock、current/pinned Revision、密钥、原作者及其他Agent的未提交内容。只显式暂存当前Task获准文件；禁止误stage/reset/stash/覆盖/清理保护路径。不得实施未授权的删除、外部发布、生产部署或其他影响项目外部状态的不可逆操作。遇到真实产品取舍时继续独立可做的工作，一次性说明具体问题、选项及影响，暂停依赖该选择的Task并保持关机授权不触发。

仅当完整项目目标已完成，且没有待处理Task、Review、Gate或阻塞时，才按用户已给授权保存最终Checkpoint并关闭计算机；工作仍进行或等待用户裁决时不要关机，不要再询问是否关机。

恢复安全：R6尚未派发，P08未done，P09–P20未释放；DSH执行与Codex验证分别记录；所有状态以仓库当前文档和现场命令为准。
