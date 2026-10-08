# P08 可恢复检查点

时间：2026-10-09 00:34（Asia/Shanghai）；Agent=Codex；TaskStatus=in_progress；ExecutionState=ACTIVE（R6已批准；链接守卫窄范围修订和状态纠错已完成；主线两个validator与whitespace检查EXIT=0；当前是新delivery固定前的恢复点，HEAD仍为`e9795470ac0d2a02604509895dc4a37e45fe0d57`）。新delivery提交后，Codex须在派发R7前另行保存绑定真实delivery/worktree的post-delivery恢复点。

## 当前事实

- 唯一仓库=`G:/CODEX/New Manga`；branch=`main`；当前HEAD=`e9795470ac0d2a02604509895dc4a37e45fe0d57`（修订尚未提交）；common-dir=`G:/CODEX/New Manga/.git`。
- P08 Task基线=`ab2f813c0ce311a6712002cafd852b9e7a258380`；原R6交付/reviewed head=`ecb3b520ce68c2ddcc0c5ec94596e2f50a17f369`，base=`af1ddeec1b998f2ddaf121a85f5fd382561aae1e`。精确R6 worktree=`G:/CODEX/New Manga.worktrees/P08-dsh-review-ecb3b520-r6`，detached、clean、HEAD正确、common-dir正确。
- DSH R6正式结论=`approved`；native session=`session-44947a36-b277-4118-8f82-635e1e803dd1`，CLI EXIT=0，报告=`verification/P08/review-dsh-ecb3b520-r6.md`，SHA256=`7E486D1EC46CD0EBF3BEC280EDDDB837CE600715549E2E528027FF2FEB883C28`；与`verification/P08/dsh-r6.stdout.md`逐字节相同，session已挂载至New Manga workspace。R5-01/R5-02 closed；0未闭合P0/P1/P2。DSH自身shell/git/python检查因Win32 5为`NOT_RUN`/`NOT_VERIFIED`，不能记为DSH PASS。
- R6-01（非阻断P3）已在post-delivery commit=`547894f59dc2e9ab89812d27efc511d432c6b6a9`修正；DSH确认无需为该修正重开R6 head。R6-O1/O2/O3为P4信息观察，详见canonical报告。
- Codex集成预检首轮`verify_scope.py` EXIT=1：canonical R6 Review报告及原始stdout含示例目标`[…]`，旧链接检查将它当作真实相对路径。不得修改报告或raw stdout（会破坏证据/hash）。已在`verification/P08/verify_scope.py`增加窄范围规则：跳过目标恰为`…`或`...`的展示占位，其他相对链接仍须存在。R6原批准不延伸至该修改，因此须生成新delivery head并由DSH独立复审（R7）。
- 修改后的当前main工作区：`python -B -X utf8 verification/P08/verify_scope.py` EXIT=0（193 AC、AC-SMOKE、12 Gate、链接、用户裁决、受保护路径与33个提交差量路径allowlist通过）；`python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py` EXIT=0（196历史节点、105 ancestry、21规划节点及依赖图/链接通过）；`git diff --check ab2f813c0ce311a6712002cafd852b9e7a258380` EXIT=0。均为Codex实测。产品pytest/cargo/vitest/GUI/build/model=`NOT_RUN`（Task未改产品源码/测试）。
- 当前P08状态=`in_progress`，P09–P20均proposed/未释放。D1–D7已确认。Architecture Documentation Rebaseline Task尚未登记：AC-DOC-001..003须先于P09；stack-specific映射须先于P18/P20相应Gate。产品验收仍`NOT_RUN`。
- 必须保护且不得stage/覆盖/stash/reset/clean：`.qoder-credits/report.json` modified、`.qoder-credits/通路探测__8602db50.canvas.tsx` untracked、`verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/antigravity-dispatch.json`及`.stderr.log` untracked；`verification/P08/dsh-r4.*`、`dsh-r5.*`、`dsh-r6.*`原始stdout/stderr均不纳入正式提交。R6 canonical报告应提交为正式证据；DSH原始日志保留未跟踪。
- 用户要求P08任务完成后关机并保存下次续跑提示。P08仍在`in_progress`、R7未review，所以现在不可关机；只有R7独立Review、Codex集成Gate、`done`状态和最终Resume均落盘后才执行已授权关机。下一候选P03在本次P08收口前不释放。

## 下一条可直接执行的指令

1. 检查`git status --short --branch`、HEAD/common-dir和本恢复点；保留所有列出的外部dirty/raw文件。核对`doc/tasks/P08.md`为`in_progress`，Plan、Status、索引与路线图状态一致。
2. 本检查点中的Task/Handoff/导航状态修订已完成；主线`verify_scope.py`、`verify_plan.py`、`git diff --check ab2f813c0ce311a6712002cafd852b9e7a258380`均EXIT=0。仅显式stage P08授权文档、Plan/Status/导航、派生路线图文件及canonical R6报告；不stage任何raw stdout/stderr或其他dirty。提交固定新delivery，记下真实full hash。
3. 以新delivery创建精确detached、clean的R7 Review worktree并在其中复跑两个validator、fixed base/head diff-check、受保护路径差量和身份检查。然后在delivery之后保存R7 Prompt/Handoff和新的RESUME，写入真实base/head/worktree及所有验证边界。
4. 按`dsh-dispatch`技能从精确worktree派发DSH只读正式Review，保存真实stdout/stderr/session/CLI exit/hash，按session ID挂载；R7报告canonical文档须与stdout逐字节/hash一致。R7批准只覆盖固定head。
5. R7 approved且无未闭合阻断finding后，Codex执行集成Gate：复核R7 worktree身份/clean、两个validator、固定base/head diff-check、受保护路径差量、主线状态/链接、raw/report hash与Task AC。若reviewed head有任何内容变化，重新Review。通过后记录integration_commit，更新Task=`done`、Plan/Status/依赖图/RESUME和下一候选建议，并提交最终checkpoint。
6. 最终P08 checkpoint完成后生成下次继续自动推进的完整提示词；遵守用户已授权的“P08完成后关机”，关闭前核实最终HEAD/恢复点/验证证据已保存并列明保留的外部dirty。下次从实时Git与RESUME出发，按权威Plan重新核对并正式注册、冻结、分配和启动适合的下一项；P03仅为当前候选，未释放，Owner=Antigravity、非作者Reviewer=DSH仍须写入正式Task。

## 下次恢复自动推进提示词

请从`G:/CODEX/New Manga`的实时Git与`verification/P08/RESUME.md`恢复，持续自动推进已授权路线。先核对`doc/REBASELINE_PLAN.md`、`doc/00_INDEX.md`、`doc/STATUS.md`、`doc/09_COLLABORATION.md`、当前Task、branch/HEAD/common-dir和本检查点；不要依据聊天记录推断完成，也不要重做已完成全库审计。

P08当前`in_progress`：DSH R6已批准固定head=`ecb3b520ce68c2ddcc0c5ec94596e2f50a17f369`（session=`session-44947a36-b277-4118-8f82-635e1e803dd1`，报告SHA256=`7E486D1EC46CD0EBF3BEC280EDDDB837CE600715549E2E528027FF2FEB883C28`，报告与stdout逐字节相同且session已挂载）。R6-01已在`547894f59dc2e9ab89812d27efc511d432c6b6a9`修正。集成预检发现Review报告中展示用`[…]`链接令旧验证器误报；`verify_scope.py`最小修订已在工作区，主线两验证器和diff-check现均EXIT=0。该修订超出R6 fixed head，必须提交新delivery并派发正式DSH R7复审，不能把R6批准当成R7批准。

严格遵守项目授权：Owner与Reviewer不同；Qoder已退出，绝不分配；保护用户数据、Lock、current/pinned Revision、密钥、`.qoder-credits`、其他Agent dirty及R4/R5/R6 raw输出。仅显式stage P08授权文件；不伪造Review/PASS/DONE。P09–P20未释放；D1–D7不再询问；目标架构文档重基线Gate仍须在P09及P18/P20相关工作前完成。P08所有AC、Review、Codex集成Gate和恢复点完成后，按用户明确授权保存最终checkpoint并关闭计算机；P08未done或仍有Gate时不得关机。之后从Plan选择下一依赖满足Task，正式建Task、冻结范围、分配不同Owner/Reviewer并继续。
