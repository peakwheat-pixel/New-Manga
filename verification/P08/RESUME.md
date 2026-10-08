# P08 可恢复检查点

时间：2026-10-09 00:42（Asia/Shanghai）；Agent=Codex；TaskStatus=in_review；ExecutionState=ACTIVE（R7 delivery=`fe222464616152e9c95208e06c248565f2fd86a6`已固定；精确worktree验证通过；post-delivery state commit=`65a75e3dea387c0a0e09d0dd113d50eb1792e975`；DSH headless连通性探测EXIT=0并返回`收到`；正式R7 Review尚未派发）。当前main可能含dispatch-ready checkpoint，review目标固定不变。

## 当前事实

- 唯一仓库=`G:/CODEX/New Manga`；branch=`main`；R7 fixed delivery head=`fe222464616152e9c95208e06c248565f2fd86a6`；其后仅有delivery后状态/PROMPT/Handoff checkpoint metadata；common-dir=`G:/CODEX/New Manga/.git`。恢复时先读live HEAD及status，不将delivery后metadata提交误认作reviewed head变化。
- P08 Task基线=`ab2f813c0ce311a6712002cafd852b9e7a258380`；R7 base=`ecb3b520ce68c2ddcc0c5ec94596e2f50a17f369`。精确R7 worktree=`G:/CODEX/New Manga.worktrees/P08-dsh-review-fe222464-r7`，detached、clean、HEAD精确匹配、common-dir正确。R6原head=`ecb3b520ce68c2ddcc0c5ec94596e2f50a17f369`仅受R6批准。
- DSH R6正式结论=`approved`；native session=`session-44947a36-b277-4118-8f82-635e1e803dd1`，CLI EXIT=0，报告=`verification/P08/review-dsh-ecb3b520-r6.md`，SHA256=`7E486D1EC46CD0EBF3BEC280EDDDB837CE600715549E2E528027FF2FEB883C28`；与`verification/P08/dsh-r6.stdout.md`逐字节相同，session已挂载至New Manga workspace。R5-01/R5-02 closed；0未闭合P0/P1/P2。DSH自身shell/git/python检查因Win32 5为`NOT_RUN`/`NOT_VERIFIED`，不能记为DSH PASS。
- R6-01（非阻断P3）已在post-delivery commit=`547894f59dc2e9ab89812d27efc511d432c6b6a9`修正；DSH确认无需为该修正重开R6 head。R6-O1/O2/O3为P4信息观察，详见canonical报告。
- Codex集成预检首轮`verify_scope.py` EXIT=1：canonical R6 Review报告及原始stdout含示例目标`[…]`，旧链接检查将它当作真实相对路径。不得修改报告或raw stdout（会破坏证据/hash）。已将验证器改为仅跳过目标恰为`…`或`...`的展示占位，其他相对链接仍须存在。R6原批准不延伸至新delivery。
- R7精确head=`fe222464616152e9c95208e06c248565f2fd86a6`上的Codex验证：`verify_scope.py` EXIT=0（193 AC、AC-SMOKE、12 Gate、7项决策、34个授权BASE..HEAD路径、六份P08 Handoff和范围通过）；`verify_plan.py` EXIT=0（196节点、105 ancestry、21规划节点、链接和无环依赖通过）；`git diff --check ecb3b520ce68c2ddcc0c5ec94596e2f50a17f369 fe222464616152e9c95208e06c248565f2fd86a6` EXIT=0；受保护路径差量为空；精确worktree detached、clean且common-dir正确。证据为Codex实测，见`verification/P08/validation.log`。产品pytest/cargo/vitest/GUI/build/model=`NOT_RUN`。
- Delivery后同步路线图图标签时，主线`verify_scope.py`通过而`verify_plan.py`首次EXIT=1：图中P08显示`in_review / Review中`，不匹配既有`STATUS_LABELS['in_review']`；现已改为精确标签`in_review / DSH Review复审中`。该状态metadata不改变R7 delivery；随后主线复验两validator均通过，具体EXIT见`validation.log`。
- DSH headless连通性探测：在项目根目录执行`dsh --profile headless "只回复两个字：收到"`，CLI EXIT=0、stdout=`收到`、stderr为空；这是路由探测，不是P08 Review或正式Review session。
- 当前P08状态=`in_review`；DSH R7=`pending`，canonical目标`verification/P08/review-dsh-fe222464-r7.md`。P09–P20均proposed/未释放；D1–D7已确认。Architecture Documentation Rebaseline Task尚未登记：AC-DOC-001..003须先于P09；stack-specific映射须先于P18/P20相应Gate。产品验收仍`NOT_RUN`。
- 必须保护且不得stage/覆盖/stash/reset/clean：`.qoder-credits/report.json` modified、`.qoder-credits/通路探测__8602db50.canvas.tsx` untracked、`verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/antigravity-dispatch.json`及`.stderr.log` untracked；`verification/P08/dsh-r4.*`、`dsh-r5.*`、`dsh-r6.*`原始stdout/stderr均不纳入正式提交。R6 canonical报告应提交为正式证据；DSH原始日志保留未跟踪。
- 用户要求P08任务完成后关机并提供续跑提示。P08尚未`done`，R7未review，因此现在不可关机；只有R7独立Review、Codex集成Gate、`done`状态和最终Resume均落盘后才执行关机。P03在本次P08收口前不释放。

## 下一条可直接执行的指令

1. 检查`git status --short --branch`、live HEAD/common-dir和此RESUME；保护列出的外部dirty/raw文件。确认P08 Task=`in_review`，R7 delivery仍为`fe222464616152e9c95208e06c248565f2fd86a6`，精确review worktree未漂移，正式Review尚待派发。
2. 确认delivery后Task/Plan/Status/Handoff/Prompt/RESUME状态metadata已提交；如未提交，只显式stage授权清单，不stage raw输出或其他Agent内容。重跑主线`verify_scope.py`、`verify_plan.py`和基线diff-check，保持`in_review`状态一致。
3. DSH路由探测已EXIT=0。现在从精确R7 worktree执行`dsh --profile headless --json <R7 Prompt全文>`只读Review，使用`verification/P08/DSH-REVIEW-PROMPT-R7.md`全文。保存原始JSONL/stderr与真实exit，提取session event并按session ID mount；保留native session ID与raw/canonical hash。CLI失败时先诊断并记录，不伪造Review。
4. R7返回后把真实中文Review正文归档到`verification/P08/review-dsh-fe222464-r7.md`，与JSONL里的final answer比对；记录findings disposition。只有reviewed head未变、R7 approved、无未闭合P0/P1/关键验证缺失时才执行Codex集成Gate。
5. Codex集成Gate在精确R7 worktree和主线上复跑两个validator、固定base/head diff-check、受保护路径差量、HEAD/common-dir/clean、canonical/raw一致性及Task AC。若修订受审内容，重新建fixed head并DSH复审。通过后同步Task=`done`、Plan/Status/依赖图/RESUME，记录integration_commit及P03下一Task建议并提交最终checkpoint。
6. P08最终checkpoint和供下次续跑的完整提示词保存完毕后，按用户明确授权安排关机。关闭前核验最新Git状态、外部dirty保护清单和验证证据。下一次从live Git与RESUME恢复，重新核对权威Plan；P03仅为候选，需正式创建/冻结/分配并通过依赖核查后才可释放。

## 下次恢复自动推进提示词

请从`G:/CODEX/New Manga`的实时Git与`verification/P08/RESUME.md`恢复，持续自动推进已授权路线。先核对`doc/REBASELINE_PLAN.md`、`doc/00_INDEX.md`、`doc/STATUS.md`、`doc/09_COLLABORATION.md`、当前Task、branch/HEAD/common-dir和本检查点；不要依据聊天记录推断完成，也不要重做已完成全库审计。

P08当前`in_review`：R6只批准固定head=`ecb3b520ce68c2ddcc0c5ec94596e2f50a17f369`（session=`session-44947a36-b277-4118-8f82-635e1e803dd1`，报告SHA256=`7E486D1EC46CD0EBF3BEC280EDDDB837CE600715549E2E528027FF2FEB883C28`，报告与stdout逐字节相同且session已挂载）。R6-01已在`547894f59dc2e9ab89812d27efc511d432c6b6a9`修正。链接守卫修订delivery=`fe222464616152e9c95208e06c248565f2fd86a6`；R7精确worktree的两validator、diff-check与受保护路径检查均EXIT=0；正式DSH R7尚待派发。reviewed head不得被R6批准替代。

严格遵守项目授权：Owner与Reviewer不同；Qoder已退出，绝不分配；保护用户数据、Lock、current/pinned Revision、密钥、`.qoder-credits`、其他Agent dirty及R4/R5/R6 raw输出。仅显式stage P08授权文件；不伪造Review/PASS/DONE。P09–P20未释放；D1–D7不再询问；目标架构文档重基线Gate仍须在P09及P18/P20相关工作前完成。P08所有AC、Review、Codex集成Gate和恢复点完成后，按用户明确授权保存最终checkpoint并关闭计算机；P08未done或仍有Gate时不得关机。之后从Plan选择下一依赖满足Task，正式建Task、冻结范围、分配不同Owner/Reviewer并继续。
