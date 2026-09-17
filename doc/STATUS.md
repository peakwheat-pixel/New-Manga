# 当前开发状态

更新日期：2026-09-17（Asia/Shanghai）

| 项目 | 状态 |
|---|---|
| 阶段 | TASK-001～TASK-017、TASK-024 与 TASK-028～TASK-031 已完成并集成（TASK-015/024/017 的窗口内 Review 为 approved_subagent，三份外部 post-hoc Review 均 approved，findings 已由 c7a02bd 收口）；TASK-018/019 blocked；TASK-020～TASK-023、TASK-025～TASK-027 继续冻结；尚未达到完整产品验收 |
| 当前授权 | TASK-011、TASK-012、TASK-013、TASK-031 已完成独立 Review 与串行集成；TASK-030 已按用户授权完成独立 Review、R-001～R-003 收口与 Codex 集成；TASK-013 原工作台固定 base=`46646d5`、integration=`f0814a8`，生产 seam 固定 base=`126bab5`、reviewed_head=`e5b58e7`、Review=`8f7c454`、integration=`49c72fdf`，R-01/R-02 已关闭，R-03 已由 R-1 关闭；R-1 固定 base=`7c889cf`、reviewed_head=`7f3be54`、Review=`r1-review-7f3be54`、integration=`734d5b3`，已完成生产装配与集成；TASK-015 已按窗口条款收口：base=`1000ac8`、实现=`488fafc`、Review 修订=`ac4ff19`、Review=`approved_subagent`（`doc/reviews/TASK-015-488fafc.md`，ZCode 子 agent 同体审查）、integration=`fa72cee`，状态=`done`，TASK-015/024/017 外部 post-hoc Review 均 approved，findings 已由 c7a02bd 收口；TASK-016 固定 base=`f9edd68`、reviewed_head=`f544261`、Review=`878ac16`、integration=`9bf85f5`、Owner=`DeepSeek Harness`、Reviewer=`Codex`，状态=`done`；TASK-018/019 已登记 blocked；TASK-020～TASK-023、TASK-025～TASK-027 继续冻结；2026-09-16 用户追加 9 小时 ZCode 全权窗口授权（T0=2026-09-16 23:30 ～ T1=2026-09-17 08:30 Asia/Shanghai，窗口目标 TASK-015/024/017）；2026-09-17 用户指示撤销该窗口授权并归还 Codex/DeepSeek Harness 职责——Codex 恢复唯一主线写入与集成责任人、DSH 恢复独立 Reviewer，窗口期交付的TASK-015/024/017 外部 post-hoc Review 均 approved，findings 已由 c7a02bd 收口，条款存档见下方「ZCode 全权窗口授权（2026-09-16）」（已失效）章节 |
| 接管审核 | approved |
| 用户审核记录 | 2026-09-15：TASK-008 已按批准范围完成 Review 与 Codex 集成；TASK-028 统一 SQLite 持久化设计冻结；随后授权的 TASK-029 已由 ZCode 实施、DSH approved Review、Codex 集成收口；TASK-009 已释放、完成独立 Review 并集成收口；本次批准释放 TASK-014；本次继续批准释放 TASK-010；本次批准 TASK-012 与 TASK-010 并行执行；TASK-010 已完成独立 Review 与串行集成收口；TASK-011、TASK-013、TASK-015～TASK-027 与其他业务功能继续冻结。2026-09-16：按 §6.6 集成 TASK-012；关闭 R-001/R-002；批准建立独立 TASK-030 装配切片，保持 BLOCKED/未释放，不释放 TASK-013/TASK-015；随后授权 Codex 实施 TASK-031 生产 ImageDecoder/Managed Copy 适配器，已完成独立 Review、R-001～R-003 关闭与串行集成；本次再授权释放 TASK-030，登记为 READY 并创建其专用 ZCode 分支/worktree；TASK-013/TASK-015 及其他冻结 Task 仍不释放。 |
| 目标基线冻结 | 未冻结；见 Gap Analysis |
| 应用源代码 / 可执行测试 | TASK-005 最小入口与守卫、TASK-006 持久化与 Artifact 基础、TASK-007 书架领域与本地图片导入、TASK-008 Region 编辑/Revision/人工保护、TASK-009 Provider 配置/网络策略/凭据边界、TASK-010 约束/TM/Context、TASK-011 命令计划/任务调度/可恢复进度、TASK-012 四页导航与书架 UI、TASK-013 工作台与任务进度及生产 Pipeline seam、TASK-014 渲染切片、TASK-029 统一 SQLite v2 持久化、TASK-030 生产入口装配、R-1 生产 Workbench 装配已入库；尚无完整产品功能 |
| 项目 Git 分支 / 当前 Task 基线 | master；TASK-009 base=`3de750a`，reviewed_head=`b42fc32`，implementation merge=`dea1dee`，integration_commit=`6c732be`，Owner=`ZCode`，Reviewer=`DeepSeek Harness`；TASK-010 base=`2bdfd6f`，reviewed_head=`cd76d30`，implementation merge=`1ea9c80`，integration_commit=`a225790`，Owner=`ZCode`，Reviewer=`DeepSeek Harness`，branch=`agent/zcode/TASK-010-translation-context`；TASK-012 base=`2cceb1e`，reviewed_head=`ca5848b`，implementation merge=`b324d4b`，integration_commit=`78987c8`，Owner=`ZCode`，Reviewer=`DeepSeek Harness`，branch=`agent/zcode/TASK-012-navigation-library-ui`；TASK-014 base=`29592c9`，reviewed_head=`72cb2be`，implementation merge=`a61216a`，integration_commit=`a943297`；TASK-029 base=`79529bc`，reviewed_head=`5abc173`，implementation merge=`2ea5445`，integration_commit=`0b0b855`；TASK-030 base=`087da45`，reviewed_head=`c3f1893`，implementation merge=`a58ff84`，integration_commit=`fef9dd3`，Owner=`ZCode`，Reviewer=`DeepSeek Harness`，branch=`agent/zcode/TASK-030-main-bootstrap-assembly`，worktree=`G:/CODEX/New Manga.worktrees/TASK-030-zcode`；TASK-031 base=`29b146f`，reviewed_head=`c67a105`，implementation merge=`0b44b83`，integration_commit=`e9d5185`，Owner=`Codex`，Reviewer=`DeepSeek Harness`，branch=`agent/codex/TASK-031-production-import-adapters`；TASK-011 base=`1668cd5`，reviewed_head=`6a2016b`，implementation merge=`053d253`，integration_commit=`369e95f`，Owner=`Codex`，Reviewer=`DeepSeek Harness`，status=`done`，branch=`agent/codex/TASK-011-command-scheduler`，worktree=`G:/CODEX/New Manga`；TASK-013 base=`46646d5`，reviewed_head=`da1daf1`，implementation_merge=`32a1eb5`，integration_commit=`f0814a8`，Owner=`ZCode`，Reviewer=`DeepSeek Harness`，status=`done`，branch=`agent/zcode/TASK-013-workbench-task-progress`，worktree=`G:/CODEX/New Manga.worktrees/TASK-013-zcode`；TASK-013 生产 Pipeline seam base=`126bab5`，reviewed_head=`e5b58e7`，Review=`8f7c454`，integration_commit=`49c72fdf`，Owner=`Codex`，Reviewer=`DeepSeek Harness`；R-1 base=`7c889cf`，reviewed_head=`7f3be54`，Review=`r1-review-7f3be54`，integration_commit=`734d5b3`，Owner=`Codex`，Reviewer=`DeepSeek Harness`，status=`done`；TASK-015 base=`1000ac8`，reviewed_head=`ac4ff19`（docs head=`a915d56`），Review=`approved_subagent`（doc/reviews/TASK-015-488fafc.md，窗口同体审查），integration_commit=`fa72cee`，Owner=`ZCode`（Review=ZCode 子 agent），branch=`agent/zcode/TASK-015-reader-export`，worktree=`G:/CODEX/New Manga.worktrees/TASK-015-zcode`，status=`done`；TASK-024 base=`116e682`，reviewed_head=`86072c3`，Review=`approved_subagent`（doc/reviews/TASK-024-design.md，窗口同体审查），integration_commit=`61c33e2`，Owner=`ZCode`（Review=ZCode 子 agent），branch=`agent/zcode/TASK-024-extension-boundaries-design`，worktree=`G:/CODEX/New Manga.worktrees/TASK-024-zcode`，status=`done`（仅设计；U-1 已取消网页导入，U-2 已选 PDFium via pypdfium2，U-3 已批准 Plugin 首版仅本地目录；U-4 已决定 Plugin Agent 不进首版、二阶段另行裁决；U-5/U-6 待裁决）；TASK-017 base=`348a48e`，reviewed_head=`ae74250`（实验=`6a330e1`），Review=`approved_subagent`（doc/reviews/TASK-017-protocol.md，窗口同体审查），integration_commit=`c0cf3a1`，Owner=`ZCode`（Review=ZCode 子 agent），branch=`agent/zcode/TASK-017-translation-protocol-experiment`，worktree=`G:/CODEX/New Manga.worktrees/TASK-017-zcode`，status=`done`（真实端点层 NOT_RUN） |
| TASK-001 交付 / 集成 | 首次 615a073；Review 修订 cdc736c；integration_commit a1cb24c |
| Git remote | 未配置 |
| 文档版本状态 | TASK-003 reviewed head `9c6a73b` 由 `db269e9` 集成；TASK-004 reviewed head `181a356` 由 `a501372` 集成；TASK-005 reviewed head `f343008` 由 `6607f75` 集成；TASK-005 集成审计文档收口 `9fa6835` 由 `79b7621` 合并；TASK-006 reviewed head `e1d3e2c` 由 `32a7314` 收口；TASK-007 reviewed head `6ea4dd9` 由 `2b64b0f` 收口；TASK-008 reviewed head `1f373ac` 由 `06ba2e7` 收口；TASK-009 reviewed head `b42fc32`，实现合并 `dea1dee`，Review/集成收口 `6c732be`；TASK-010 reviewed head `cd76d30`，实现合并 `1ea9c80`，Review/集成收口 `a225790`，取证 `05effee` 由 `014231f` 合并；TASK-012 reviewed head `ca5848b`，实现合并 `b324d4b`，Review/集成收口 `78987c8`；TASK-014 reviewed head `72cb2be`，实现合并 `a61216a`，Review/集成收口 `a943297`；TASK-028 reviewed head `e7f9e41` 由 `509de66` 收口；TASK-029 reviewed head `5abc173`，实现合并 `2ea5445`，Review/集成收口 `0b0b855`；TASK-030 reviewed head `c3f1893`、Review `dba2637` approved，实现合并 `a58ff84`、R-001～R-003 修订 `a29f02e`、integration `fef9dd3`，已 done；TASK-031 reviewed head `c67a105`、Review `0509003` approved，实现合并 `0b44b83`、integration `e9d5185`，已 done；TASK-011 reviewed head `6a2016b`、Review `36f874a` approved，实现合并 `053d253`、integration `369e95f`，已 done；TASK-015 reviewed head `ac4ff19`、Review `approved_subagent`（doc/reviews/TASK-015-488fafc.md），实现 merge `fa72cee`，已 done（窗口同体审查，外部 post-hoc Review `9b77685` approved，R-101 由 `c7a02bd` 收口）。 |
| 任务分派 / 执行 | TASK-001～TASK-014、TASK-028、TASK-029、TASK-030、TASK-031、R-1、TASK-016：done；TASK-018/019 blocked；TASK-020～TASK-023、TASK-025～TASK-027 保持冻结；2026-09-16/17 窗口期内：TASK-015 已收口 `done`（fac2ffe 首轮被 ZCode 全量重写为 `488fafc`，子 agent Review 首轮 changes_requested R-001..R-006、修订 `ac4ff19` 后复审 `approved_subagent`，docs=`a915d56`，integration=`fa72cee`，master 复验全仓 `536 passed, 0 skipped`、无 PySide6 解释器 `42 passed, 3 skipped`，NOT_RUN 项原样保留、不得视为通过）；TASK-024（仅设计）已收口 `done`（base=`116e682`、设计=`d840075`、Review 修订=`86072c3`、Review=`approved_subagent`（doc/reviews/TASK-024-design.md）、integration=`61c33e2`、master 复验 `536 passed`；U-1 已取消网页导入；U-2 已选 PDFium via pypdfium2；U-3 已批准 Plugin 首版仅本地目录（无市场/在线分发/自动更新）；U-4 已决定 Plugin Agent 不进首版、二阶段另行裁决；TASK-023 仍冻结，TASK-025 仍冻结（TASK-019/022 依赖未完成，AC/allowed_paths 尚待 Codex 明确），TASK-019/022 按各自 U-6/U-5 裁决前继续冻结）；TASK-017 已收口 `done`（base=`348a48e`、实验=`6a330e1`、Review=`approved_subagent`（doc/reviews/TASK-017-protocol.md，7×P2：R-001..R-004 处置、R-005/R-006 deferred）、integration=`c0cf3a1`、master 复验全仓 536 passed + 实验 15 passed；真实端点层 NOT_RUN 待用户提供端点；reading_export QML 低频 flaky 登记移交）；窗口三项目标全部完成，其余冻结 Task 不解冻；TASK-018/019 已按排除项登记 `blocked`（blocker=窗口授权不覆盖解冻，恢复条件=用户批准释放）；2026-09-17 用户指示归还 Codex/DSH 权限、撤销 ZCode 九小时窗口授权——自本提交起主线写入/集成回归 Codex、独立 Review 回归 DSH，窗口三交付的外部 post-hoc Review 均 approved，findings 已由 `c7a02bd` 收口，新增冻结 Task 解冻须走用户常规审批 |
| ZCode / DeepSeek Harness 连接 | TASK-008、TASK-009、TASK-010、TASK-011、TASK-012、TASK-013、TASK-014、TASK-029、TASK-030 与 TASK-031 已交付并集成；TASK-013 工作台 integration=`f0814a8`，生产 seam Review=`8f7c454`、integration=`49c72fdf`，R-01/R-02 已关闭，R-03 由 R-1 关闭；R-1 Review=`r1-review-7f3be54`、integration=`734d5b3`；TASK-015 已由 ZCode 交付并按窗口条款集成（子 agent Review=approved_subagent，integration=`fa72cee`；DeepSeek Harness 为期满补审外部 Reviewer）；TASK-016 已由 DeepSeek Harness 交付，Codex Review=`878ac16`、integration=`9bf85f5` |
| 本次 Review | TASK-007、TASK-008、TASK-009、TASK-010、TASK-011、TASK-012、TASK-013、TASK-014、TASK-028、TASK-029、TASK-030、TASK-031、TASK-016 Review 均已按 STATUS 记录 approved；TASK-011 Review=`36f874a`、集成复验见 `verification/TASK-011/integration-369e95f6.md`；TASK-013 原工作台 Review=`9fbfa48`、集成复验见 `verification/TASK-013/integration-f0814a8.md`，生产 seam Review=`8f7c454`、集成复验见 `verification/TASK-013/integration-49c72fdf.md`；TASK-030 Review=`dba2637`、集成复验见 `verification/TASK-030/integration-fef9dd3.md`；TASK-031 Review=`0509003`、集成复验见 `verification/TASK-031/integration-e9d5185.md`；TASK-016 Review=`878ac16`、集成复验见 `verification/TASK-016/integration-9bf85f5.md`；TASK-015 Review=`approved_subagent`（`doc/reviews/TASK-015-488fafc.md`，窗口授权同体审查，非协议 §1 独立批准；外部 post-hoc Review `9b77685` approved，R-101 由 `c7a02bd` 收口）、集成复验 master `536 passed, 0 skipped`；TASK-024 Review=`approved_subagent`（`doc/reviews/TASK-024-design.md`，同体审查；R-001..R-004 fixed、R-005 deferred）、集成复验 master `536 passed, 0 skipped`；TASK-017 Review=`approved_subagent`（`doc/reviews/TASK-017-protocol.md`，同体审查；7×P2，R-001..R-004 处置、R-005/R-006 deferred）、集成复验全仓 `536 passed` + 实验 `15 passed` |
| TASK-015/017/024 post-hoc Review | DSH：TASK-015 报告 `9b77685` approved（R-101 closed）；TASK-024 报告 `9454cec` approved（R-101～R-103 closed）；TASK-017 报告 `fb0bc40` approved（R-101 closed）。Codex 于 `c7a02bd` 收口 findings 与验证记录；复验：TASK-015 64 passed/0 skipped，TASK-017 协议 15 passed/0 skipped、CLI 1 passed/0 skipped，`git diff --check` exit 0。报告文件保留在 DSH 指定 review worktree/branch。 |
| TASK-016 集成对象 | `base_commit=f9edd68`；`reviewed_head=f544261`；metadata=`8153274`；Review=`878ac16`；`integration_commit=9bf85f5`；Owner=`DeepSeek Harness`；Reviewer=`Codex`；实验质量/性能未满足项保持 `BLOCKED`/`NOT_RUN` |
| 产品发布状态 | NOT READY；仅有最小启动骨架，无业务功能或可发布应用 |

接管审核入口：[接管审计与差距](10_CURRENT_STATE_AND_GAPS.md)、[路线图](12_ROADMAP.md)、[任务目录](tasks/README.md)。

已集成交付入口：[TASK-001 复审 Handoff](handoffs/TASK-001-cdc736c.md)，包含固定提交、Finding 处置、独立批准与集成结果。

已集成交付入口：[TASK-002 复审 Handoff](handoffs/TASK-002-885c9a9.md)，固定 `base_commit=b1b3f5d`、`reviewed_head=885c9a9`、`integration_commit=7927169`。

已集成交付入口：[TASK-003 Handoff](handoffs/TASK-003-9c6a73b.md)，固定 `reviewed_head=9c6a73b`、`integration_commit=db269e9`；[TASK-004 Handoff](handoffs/TASK-004-181a356.md)，固定 `reviewed_head=181a356`、`integration_commit=a501372`。

已集成交付入口：[TASK-005 Handoff](handoffs/TASK-005-f343008.md)，固定 `base_commit=d65901b`、`reviewed_head=f343008`、`integration_commit=6607f75`；[集成验证](../verification/TASK-005/integration-6607f75.md)记录主线复验。

已集成交付入口：[TASK-006 Handoff](handoffs/TASK-006-e1d3e2c.md)，固定 `base_commit=fb29dfe`、`reviewed_head=e1d3e2c`、`integration_commit=32a7314`；[集成验证](../verification/TASK-006/integration-32a7314.md)记录主线复验。

已集成交付入口：[TASK-007 Handoff](handoffs/TASK-007-6ea4dd9.md)，固定 `base_commit=6b123fe`、`reviewed_head=6ea4dd9`、`integration_commit=2b64b0f`；[独立 Review](reviews/TASK-007-6ea4dd9.md) 为 approved；[集成验证](../verification/TASK-007/integration-2b64b0f.md)记录主线复验。

已集成交付入口：[TASK-008 Handoff](handoffs/TASK-008-1f373ac.md)，固定 `base_commit=f129ae9`、`reviewed_head=1f373ac`、`integration_commit=06ba2e7`；[独立 Review](reviews/TASK-008-1f373ac.md) 为 approved；[集成验证](../verification/TASK-008/integration-06ba2e7.md)记录主线复验。

已集成交付入口：[TASK-028](tasks/TASK-028.md)，固定 `base_commit=4a1df8f`、`reviewed_head=e7f9e41`、`integration_commit=509de66`；[独立 Review](reviews/TASK-028-e7f9e41.md) 为 approved。该 Task 仅完成设计冻结，SQLite 实现仍未释放。

已集成交付入口：[TASK-029 Handoff](handoffs/TASK-029-5abc173.md)，固定 `base_commit=79529bc`、`reviewed_head=5abc173`、`integration_commit=0b0b855`；[独立 Review](reviews/TASK-029-5abc173.md) 为 approved；[集成验证](../verification/TASK-029/integration-0b0b855.md)记录主线复验。实现合并提交为 `2ea5445`。

已集成交付入口：[TASK-014 Handoff](handoffs/TASK-014-72cb2be.md)，固定 `base_commit=29592c9`、`reviewed_head=72cb2be`、`integration_commit=a943297`；[独立 Review](reviews/TASK-014-72cb2be.md) 为 approved；[集成验证](../verification/TASK-014/integration-a943297.md)记录主线复验。实现合并提交为 `a61216a`；F-01/F-02/F-04 收口提交为 `524d03f`，F-03/F-05 保留为遗留。

已集成交付入口：[TASK-009 Handoff](handoffs/TASK-009-b42fc32.md)，固定 `base_commit=3de750a`、`reviewed_head=b42fc32`、`integration_commit=6c732be`；首轮 Review `2da1a39` 为 changes_requested，复审报告 `d2fe13c` 为 approved；[集成验证](../verification/TASK-009/integration-6c732be.md)记录主线复验。实现合并提交为 `dea1dee`；R-011（D02 §2 stdlib 偏差）与 F-01（`openssl unavailable` 计数口径）已关闭，TLS 6 项保持 `NOT_RUN`。

已集成交付入口：[TASK-010 Handoff](handoffs/TASK-010-cd76d30.md)，固定 `base_commit=2bdfd6f`、`reviewed_head=cd76d30`、`integration_commit=a225790`；Review 报告 `008b101` 为 approved；[集成验证](../verification/TASK-010/integration-a225790.md)记录主线复验；取证报告 `05effee` 已由 `014231f` 合并。实现合并提交为 `1ea9c80`；F-01/F-02 已关闭，`tests/rendering` 顺序依赖已复现并定位为 offscreen `QGuiApplication` 单例污染；经用户授权，修复提交 `4e05e59` 已隔离 smoke 子进程并将默认 pytest 收集限定为 `tests`，详见 [修复验证](../verification/TASK-010/rendering-order-fix.md)。

TASK-006 Review 已完成：首轮报告 `doc/reviews/TASK-006-ba1e769.md` 为 changes_requested，复审报告 `doc/reviews/TASK-006-e1d3e2c.md` 为 approved；两个报告均已纳入 master。

TASK-003 Owner 工作区为 `G:/CODEX/New Manga.worktrees/TASK-003-deepseek`；分支 `agent/deepseek/TASK-003-verification-spec`。Task 已集成，工作区暂保留供审计。

TASK-004 Owner 工作区为 `G:/CODEX/New Manga.worktrees/TASK-004-zcode`；分支 `agent/zcode/TASK-004-windows-packaging`。Task 已集成，工作区暂保留供审计。

TASK-005 Owner 工作区为 `G:/CODEX/New Manga.worktrees/TASK-005-codex`，Reviewer 工作区为 `G:/CODEX/New Manga.worktrees/TASK-005-deepseek-review`；Task 已集成，两个 worktree 暂保留供审计。

TASK-006 Owner 工作区为 `G:/CODEX/New Manga.worktrees/TASK-006-zcode`；Reviewer 工作区为 `G:/CODEX/New Manga.worktrees/TASK-006-deepseek-review`；Task 已集成，两个 worktree 暂保留供审计。

TASK-007 Owner 工作区为 `G:/CODEX/New Manga.worktrees/TASK-007-zcode`；分支 `agent/zcode/TASK-007-library-import`；基线为 `6b123fe55f2e6373335b044fc5e5f169b5d108e0`。Task 已集成完成；Reviewer=DeepSeek Harness，Review worktree 为 `G:/CODEX/New Manga.worktrees/TASK-007-deepseek-review`，两个 worktree 暂保留供审计。

TASK-008 Owner 工作区为 `G:/CODEX/New Manga.worktrees/TASK-008-zcode`；分支 `agent/zcode/TASK-008-region-editing`；基线为 `f129ae96900fb567288f91a78d55c0ff4ecafe6d`；reviewed_head=`1f373ac`，状态 `done`，integration_commit=`06ba2e7`，Reviewer=DeepSeek Harness；Review worktree 为 `G:/CODEX/New Manga.worktrees/TASK-008-deepseek-review`。

统一 SQLite 持久化设计已冻结并完成 TASK-028 集成：[TASK-028 设计契约](contracts/TASK-028_UNIFIED_SQLITE_PERSISTENCE_DESIGN.md)。它采用共享连接、按消费契约拆分 Adapter、追加 v2 migration，并保留 v1 Artifact 语义；TASK-029 实现已在 `2ea5445` 合并，Review 报告与主线复验在 `0b0b855` 收口。R-201/R-202 继续作为 TASK-008 Review 的 noted/deferred finding 入档，不在 TASK-029 中裁决。

TASK-029 已完成并收口：[TASK-029](tasks/TASK-029.md) 固定 base=`79529bc`、reviewed_head=`5abc173`、implementation merge=`2ea5445`、integration=`0b0b855`；只实现 TASK-028 冻结的 v2 migration、Library/Page/Region adapter 与 Region 原子 Revision seam；TASK-010～TASK-027 与其他业务功能仍未启动。

TASK-009 已完成并收口：[TASK-009](tasks/TASK-009.md) 固定 `base_commit=3de750ab7558f4c90841b96005dbbe58b8064e71`、`reviewed_head=b42fc321b37562e9596ca3bb678be1f5cda22828`、实现合并 `dea1dee`、`integration_commit=6c732be`，Owner=`ZCode`，Reviewer=`DeepSeek Harness`；作者与 Reviewer worktree 暂保留供审计。

TASK-010 已完成并收口：[TASK-010](tasks/TASK-010.md) 固定 `base_commit=2bdfd6f82b67a550c0550ee930d49bdb12656322`、`reviewed_head=cd76d30`、实现合并 `1ea9c80`、`integration_commit=a225790`，Owner=`ZCode`，Reviewer=`DeepSeek Harness`；作者与 Reviewer worktree 暂保留供审计。移交项 `tests/rendering` 已由 ZCode 在 `05effee` 复现并由 Codex 以 `014231f` 纳入主线；经用户授权，Codex 以 `4e05e59` 修复根因，验证见 [rendering-order-fix.md](../verification/TASK-010/rendering-order-fix.md)，未修改 `tests/rendering`、业务实现或创建新 Task。

TASK-012 已完成并收口：[TASK-012](tasks/TASK-012.md) 固定 `base_commit=2cceb1e734c5079870662b7a28da316e46444810`、`reviewed_head=ca5848b`、实现合并 `b324d4b`、`integration_commit=78987c8`，Owner=`ZCode`，Reviewer=`DeepSeek Harness`；[Review](reviews/TASK-012-ca5848b.md) `report_commit=084db60` 为 approved；[集成验证](../verification/TASK-012/integration-78987c8.md)记录主线复验。R-001/R-002 已关闭；入口装配范围变更 TASK-030 已完成并收口。

TASK-030 已完成并收口：[TASK-030](tasks/TASK-030.md) 固定 `base_commit=087da45590c84227e9695eb829669e9cee805ef2`、`reviewed_head=c3f1893`、`implementation_merge=a58ff84`、`integration_commit=fef9dd3`、Owner=`ZCode`、Reviewer=`DeepSeek Harness`、branch=`agent/zcode/TASK-030-main-bootstrap-assembly`、worktree=`G:/CODEX/New Manga.worktrees/TASK-030-zcode`；生产路径为 `src/ui/qml/Main.qml` 与 `src/bootstrap/app.py`，R-001～R-003 与两项裁决已落地；不释放 TASK-013/TASK-015。

TASK-011 已完成并收口：[TASK-011](tasks/TASK-011.md) 固定 `base_commit=1668cd5daebf07ea89fb93b5261410a6cba1c033`、`reviewed_head=6a2016b`、`implementation_merge=053d253`、`integration_commit=369e95f`、Owner=`Codex`、Reviewer=`DeepSeek Harness`、branch=`agent/codex/TASK-011-command-scheduler`、worktree=`G:/CODEX/New Manga`；R-001～R-003 已登记收口，集成复验见 `verification/TASK-011/integration-369e95f6.md`；不释放 TASK-013/TASK-015。

TASK-013 已完成并收口：[TASK-013](tasks/TASK-013.md) 固定 `base_commit=46646d58b3f645fa30fe7e10fae050218f9c55bb`、`reviewed_head=da1daf11e65fdc80f20450bec1f5e87234b826c7`、`implementation_merge=32a1eb5`、`integration_commit=f0814a8`、Owner=`ZCode`、Reviewer=`DeepSeek Harness`、branch=`agent/zcode/TASK-013-workbench-task-progress`、worktree=`G:/CODEX/New Manga.worktrees/TASK-013-zcode`；原工作台 R-001～R-003 已关闭。随后生产 Pipeline seam 固定 `base_commit=126bab5`、`reviewed_head=e5b58e7378a9fa4e5737220e51a9000a19a21a4e`、Review=`8f7c454`、`integration_commit=49c72fdf`，R-01/R-02 已关闭；R-1 固定 `base_commit=7c889cf`、`reviewed_head=7f3be549d97d2b9858867f2e7f7f861e0542342e`、Review=`r1-review-7f3be54`、`integration_commit=734d5b39a3185bf612276dada6b089b55c9e574d`，已完成真实生产 Workbench 装配，R-03 已关闭；不释放 TASK-015 或其他冻结 Task。

TASK-031 已完成 Review 与集成：[TASK-031](tasks/TASK-031.md) 固定 `base_commit=29b146f`、`reviewed_head=c67a105`、`implementation_merge=0b44b83`、`integration_commit=e9d5185`、Owner=`Codex`、Reviewer=`DeepSeek Harness`；R-001～R-003 已关闭。TASK-030 已消费其生产 Qt 解码/Managed Copy 适配器并完成入口 smoke、真实 SQLite 导入探针与 DPI 证据收口。

TASK-014 已集成：[TASK-014](tasks/TASK-014.md) 固定 `base_commit=29592c929745410ef0045266da94f21ed97ffdcb`、`reviewed_head=72cb2be`、`integration_commit=a943297`，Owner=`ZCode`，Reviewer=`DeepSeek Harness`；作者与 Reviewer worktree 暂保留供审计。

TASK-028 Review 已归档：[首轮 Review `TASK-028-f9f2811`](reviews/TASK-028-f9f2811.md) 为 `changes_requested`；[复审 `TASK-028-e7f9e41`](reviews/TASK-028-e7f9e41.md) 固定 `reviewed_head=e7f9e41`、`report_commit=09108d1`，decision=`approved`。Codex 已以 `509de668ea9529e7b2a38abd2368df0ff02a64ae` 串行集成报告并将 TASK-028 置 `done`；TASK-029 已在其冻结设计上完成实现并独立复审通过。

TASK-029 Review 已归档：[首轮 Review `TASK-029-a2348e9`](reviews/TASK-029-a2348e9.md) 为 `changes_requested`；[复审 `TASK-029-5abc173`](reviews/TASK-029-5abc173.md) 固定 `reviewed_head=5abc173`、decision=`approved`。实现合并 `2ea5445`，Codex 主线复验 97 passed，Review/集成元数据以 `0b0b855` 收口。

TASK-014 Review 已归档：[Review `TASK-014-72cb2be`](reviews/TASK-014-72cb2be.md) 固定 `base_commit=29592c9`、`reviewed_head=72cb2be`、`report_commit=5276a18`、decision=`approved`。实现合并 `a61216a`，Review/集成收口 `a943297`，主线复验 153 passed；F-01/F-02/F-04 fixed，F-03/F-05 deferred。

TASK-009 Review 已归档：[首轮 Review `TASK-009-f1dd602`](reviews/TASK-009-f1dd602.md) 为 `changes_requested`；[复审 `TASK-009-b42fc32`](reviews/TASK-009-b42fc32.md) 固定 `base_commit=3de750a`、`reviewed_head=b42fc32`、`report_commit=d2fe13c`、decision=`approved`。实现合并 `dea1dee`，Review/集成收口 `6c732be`，固定 TASK-009 head 复验 91 passed/6 skipped、188 passed/6 skipped；6 项均因 `openssl unavailable`，TLS 保持 `NOT_RUN`。R-011 与 F-01 已关闭。

用户审核后，Codex在本文件追加日期、决定原文摘要和允许启动的 Task；再在相应 Task 记录 release、owner、base_commit。若仅同意接管，保持其余 Task 为 proposed。

## 审核记录

| 日期 | 决策人 | 决定及允许启动范围 | 证据 |
|---|---|---|---|
| 2026-09-13 | 用户 | 要求接管与规划，禁止直接开发新功能，完成后审核 | 本次指令已固化在 AGENTS.md 与协作协议；尚无后续批准 |
| 2026-09-13 | 用户 | 接管结果通过；允许提交初始 Git 基线并启动 TASK-001；其余 Task 和新功能保持冻结 | 用户本次审核指令 |
| 2026-09-13 | 用户 | TASK-001 审核通过；允许启动 TASK-002，仅冻结最小数据与执行契约；其他 Task 和功能开发继续冻结。TASK-002 后续设计取舍均批准，不再逐项询问 | 用户本次审核指令 |
| 2026-09-14 | 用户 | TASK-002 审核通过；允许启动 TASK-003，并在其范围内关闭 F-08；批准“单一权威验收规范 + Fixture Manifest + 现有文档回链”设计。其他 Task 和功能开发继续冻结 | 用户本次审核指令 |
| 2026-09-14 | 用户 | 允许 TASK-004 与 TASK-003 并行执行；其他 Task 和功能开发继续冻结 | 用户本次审核指令 |
| 2026-09-14 | 用户 | 澄清 TASK-004 应分派给 ZCode，而非 DeepSeek Harness；并行与冻结范围不变 | 用户本次纠正指令 |
| 2026-09-14 | 用户 | 批准 Codex 独立复审并串行集成 TASK-003、TASK-004；TASK-005 及其他 Task 继续冻结 | 用户本次批准指令 |
| 2026-09-14 | 用户 | 批准 Codex 基于 `e3c8de7` 仅修订文档与验证证据，关闭集成审计 P1 和两个文档 P2；暂不处理 pytest 单值参数化建议，不释放 TASK-005 | 用户本次批准指令 |
| 2026-09-14 | 用户 | 审核通过 TASK-003/004 集成收口；允许启动 TASK-005，仅建立最小工程入口与架构守卫；Codex 实施、DeepSeek Harness 独立 Review；TASK-006～TASK-027 与业务功能继续冻结 | 用户本次授权指令 |
| 2026-09-14 | 用户 | 批准 TASK-005 方案 A：Python 3.12 + requirements 精确锁定 + PySide6 Essentials 最小 QML 入口 + stdlib AST 架构守卫 | 用户本次设计决定 |
| 2026-09-14 | 用户 | TASK-005 书面规格审核通过；允许创建 worktree、编写实施计划并开始 TDD 实现；TASK-006～TASK-027 继续冻结 | 用户本次批准指令 |
| 2026-09-15 | 用户 | TASK-005 集成审计后的文档收口改由 ZCode 执行：合并 `9fa6835` 到 master 并更新 TASK-005/STATUS 元数据；TASK-006～TASK-027 与业务功能继续冻结，不释放 TASK-006 | 用户本次指令 |
| 2026-09-15 | 用户 | 审核通过 TASK-005 最终收口；批准释放 TASK-006，由 ZCode 承接、DeepSeek Harness 独立 Review；仅执行持久化与 Artifact 安全提交基础，TASK-007～TASK-027 与业务功能继续冻结 | 用户本次批准指令 |
| 2026-09-15 | 用户 | TASK-006 集成与收尾：固定 `base_commit=fb29dfe`、approved `reviewed_head=e1d3e2c`；纳入两份 Review 报告；关闭 F-01；不启动其他 Task | 用户本次集成指令 |
| 2026-09-15 | 用户 | 审核通过 TASK-006；允许启动 TASK-007，仅实现书架领域与本地图片导入，由 ZCode 实施、DeepSeek Harness 独立 Review；TASK-008～TASK-027 与其他业务功能继续冻结 | 用户本次批准指令 |
| 2026-09-15 | 用户 | TASK-007 集成与收尾：固定 `base_commit=6b123fe`、approved `reviewed_head=6ea4dd9`；纳入 Review 报告；关闭 F-01～F-04（F-04 按端口位置规则 deferred）；不启动 TASK-008～TASK-027 | 用户本次集成指令 |
| 2026-09-15 | 用户 | 批准释放 TASK-008，由 ZCode 实现 Region 编辑、Revision 与人工保护，DeepSeek Harness 独立 Review；TASK-009～TASK-027 与其他业务功能继续冻结 | 用户本次批准指令 |
| 2026-09-15 | 用户 | 要求按协作协议 §6 将 TASK-008 `reviewed_head=1f373ac` 与 approved Review（`report_commit=f9e5977`）串行集成 master；记录 `integration_commit=06ba2e7`，TASK-008 置 done，更新 STATUS 与验收追踪；建议协调统一 SQLite 持久化切片并将 R-201/R-202 随集成元数据入档 | 用户本次集成指令 |
| 2026-09-15 | 用户 | 冻结统一 SQLite 持久化设计：仅记录 TASK-006/007/008 的 SQLite 收敛方案、v2 Schema 方向、Adapter seam、事务不变量和实现边界；不修改业务代码/UI/现有规则，不释放实现 Task | 用户本次设计冻结指令；TASK-028 |
| 2026-09-15 | 用户 | 授权释放 TASK-029：按 TASK-028 冻结设计实现统一 SQLite 持久化；ZCode Owner、DeepSeek Harness 独立 Review；仅允许 Task 白名单，TASK-009～TASK-027 与其他业务功能继续冻结 | 用户本次授权指令 |
| 2026-09-15 | 用户 | 放弃插队及后续自动顺延编号制度，继续沿用现有 Task 序列；释放下一项 TASK-009，由 ZCode 实施、DeepSeek Harness 独立 Review；TASK-010～TASK-027 与其他业务功能继续冻结 | 用户本次继续项目任务指令 |
| 2026-09-15 | 用户 | 批准释放 TASK-014，由 ZCode 实现配色与文字排版渲染，DeepSeek Harness 独立 Review；TASK-009 先行，TASK-010～TASK-013、TASK-015～TASK-027 与其他业务功能继续冻结 | 用户本次批准指令 |
| 2026-09-15 | 用户 | 要求按协议 §6.6 串行集成 TASK-014：固定 `base_commit=29592c9`、approved `reviewed_head=72cb2be`、Review `report_commit=5276a18`；保留 merge 提交并记录 `integration_commit`；执行 F-01/F-02/F-04 收口、登记 F-03/F-05 遗留；不启动其他 Task、不释放 TASK-013/TASK-015、不 push | 用户本次集成指令 |
| 2026-09-15 | 用户 | 要求按协议 §6.6 串行集成 TASK-009：固定 `base_commit=3de750a`、approved `reviewed_head=b42fc32`、首轮报告 `2da1a39`、复审 `report_commit=d2fe13c`；完成 D02 §2 stdlib 偏差登记、F-01 计数勘误、文档 disposition 回填；不启动其他 Task、不释放冻结任务、不 push | 用户本次集成指令 |
| 2026-09-15 | 用户 | 批准释放 TASK-010；由 ZCode 实施、DeepSeek Harness 独立 Review；固定 base=`2bdfd6f`，仅执行 TASK-010 白名单，TASK-011～TASK-013、TASK-015～TASK-027 与其他业务功能继续冻结 | 用户本次批准指令 |
| 2026-09-15 | 用户 | 批准 TASK-012 与 TASK-010 并行执行；由 ZCode 实施、DeepSeek Harness 独立 Review；固定 base=`2cceb1e`，使用独立 worktree，仅执行 TASK-012 白名单，TASK-011、TASK-013、TASK-015～TASK-027 与其他业务功能继续冻结 | 用户本次批准指令 |
| 2026-09-15 | 用户 | 要求按协议 §6.6 串行集成 TASK-010：固定被审范围 `2cceb1e..cd76d30`、approved `reviewed_head=cd76d30`、Review `report_commit=008b101`；更正 F-01、登记 F-02、回填 decision/disposition；要求 rendering 顺序依赖最小复现且在此之前不改测试套件；不启动其他 Task、不释放冻结任务、不 push | 用户本次集成指令 |
| 2026-09-16 | 用户 | 要求 Codex 处置 TASK-010 的 rendering 顺序依赖移交项：指派 ZCode 补充最小复现；证据到位前维持 `NOT_REPRODUCED`，不改测试套件、不据此创建新 Task；临时 worktree 删除前必须保存精确命令与原始输出 | 用户本次取证指令 |
| 2026-09-16 | 用户 | 在取证确认根因后，授权修改 `experiments/**` 与 pytest 收集配置以修复 TASK-010 rendering 顺序依赖；不修改业务实现、`tests/rendering`、其他 Task 或依赖清单，不启动新 Task | 用户本次授权指令 |
| 2026-09-16 | 用户 | 授权 Codex 建立并实现 TASK-031：生产 ImageDecoder 与 Managed Copy 适配器；固定生产路径 `G:/CODEX/New Manga/src/infrastructure/importing.py` 与测试路径 `G:/CODEX/New Manga/tests/library/test_production_adapters.py`，Owner=Codex、Reviewer=DeepSeek Harness、base=`29b146f76b46682c6e9de3c40631fd7a5debed16`；不得修改 `Main.qml`/`bootstrap/app.py`、Schema、依赖清单、其他 Task，不释放 TASK-013/TASK-015；验收须覆盖 Qt 解码、D03 original 路径、Hash/Managed Copy 安全链与失败清理，并按通过数/skip 数分列记录 | 用户本次授权指令 |
| 2026-09-16 | 用户 | 授权释放 TASK-030：建立 `src/ui/qml/Main.qml` + `src/bootstrap/app.py` 的独立最小生产装配切片；Owner=ZCode、Reviewer=DeepSeek Harness、base=`087da45590c84227e9695eb829669e9cee805ef2`，branch=`agent/zcode/TASK-030-main-bootstrap-assembly`，worktree=`G:/CODEX/New Manga.worktrees/TASK-030-zcode`；先核实 TASK-031 `integration_commit=e9d5185` 已提供生产 Qt 解码与 Managed Copy，再实施入口装配；不得修改 TASK-012 已审实现、TASK-013/TASK-015 或其他冻结 Task | 用户本次授权指令 |
| 2026-09-16 | 用户 | 授权释放 TASK-011：实现命令计划、任务调度与可恢复进度；Owner=Codex、Reviewer=DeepSeek Harness、base=`1668cd5daebf07ea89fb93b5261410a6cba1c033`，branch=`agent/codex/TASK-011-command-scheduler`，worktree=`G:/CODEX/New Manga`；仅限 TASK-011 白名单，尚未启动实现；不释放 TASK-013/TASK-015 或其他冻结 Task | 用户本次授权指令 |
| 2026-09-16 | Codex | TASK-011 已完成 DSH 独立 Review（报告 `36f874a`，approved）并按 §6.6 串行集成；作者实现合并 `053d253`，integration_commit=`369e95f`；R-001 whitespace、R-002 状态元数据口径、R-003 进程内崩溃恢复证据边界已登记收口；Windows pipeline `27 passed, 0 skipped`，全量 `409 passed, 6 skipped`（均为 `openssl unavailable`）；不释放 TASK-013/TASK-015 或其他冻结 Task | Codex 集成收尾记录 |
| 2026-09-16 | 用户 | TASK-030 集成与收尾：固定 `base_commit=087da45`、approved `reviewed_head=c3f1893`、Review `report_commit=dba2637`；按 §6.6 串行集成并由 Codex填写 `integration_commit`，勾选 AC6；关闭 R-001（DPI 尺寸/结论/高分辨率补验）、R-002（清除预填 decision）、R-003（错误路径关闭连接）；按裁决在 D03/D07 登记数据根默认与修正 `QQuickWindow` 注释；不启动 TASK-013/TASK-015 或其他冻结 Task，不 push、不合并其他分支 | 用户本次集成指令 |
| 2026-09-16 | 用户 | 根据项目进度授权释放 TASK-013：实现工作台与任务进度交互；Owner=ZCode、Reviewer=DeepSeek Harness、base=`46646d58b3f645fa30fe7e10fae050218f9c55bb`，branch=`agent/zcode/TASK-013-workbench-task-progress`，worktree=`G:/CODEX/New Manga.worktrees/TASK-013-zcode`；TASK-011/TASK-012/TASK-014 依赖均已集成；仅限 TASK-013 白名单，不释放 TASK-015 或其他冻结 Task | 用户本次授权指令 |
| 2026-09-16 | Codex | TASK-013 按 §6.6 串行集成：实现合并 `32a1eb5`，Review 报告 `9fbfa48` approved，原工作台 integration_commit=`f0814a8`；关闭 R-001（移除/限定 terminate，持久化前须安全边界修复）、R-002（§3.6 元数据口径）、R-003（stepPage 下沉）；AC4 集成验证后勾选；Windows workbench `51 passed, 0 skipped`，全量 `460 passed, 6 skipped`，6 项均因 `openssl unavailable`；随后生产 Pipeline seam 以 base=`126bab5`、reviewed_head=`e5b58e7`、Review=`8f7c454`、integration_commit=`49c72fdf` 集成，关闭 R-01/R-02；R-1 以 base=`7c889cf`、reviewed_head=`7f3be54`、Review=`r1-review-7f3be54`、integration_commit=`734d5b3` 完成真实 Workbench 装配，关闭 R-03；不释放 TASK-015 或其他冻结 Task | Codex 集成收尾记录 |
| 2026-09-16 | Codex | TASK-013 按 §6.6 串行集成：实现合并 `32a1eb5`，Review 报告 `9fbfa48` approved，原工作台 integration_commit=`f0814a8`；关闭 R-001（移除/限定 terminate，持久化前须安全边界修复）、R-002（§3.6 元数据口径）、R-003（stepPage 下沉）；AC4 集成验证后勾选；Windows workbench `51 passed, 0 skipped`，全量 `460 passed, 6 skipped`，6 项均因 `openssl unavailable`；随后生产 Pipeline seam 以 base=`126bab5`、reviewed_head=`e5b58e7`、Review=`8f7c454`、integration_commit=`49c72fdf` 集成，关闭 R-01/R-02；R-1 以 base=`7c889cf`、reviewed_head=`7f3be54`、Review=`r1-review-7f3be54`、integration_commit=`734d5b3` 完成真实 Workbench 装配，关闭 R-03；不释放 TASK-015 或其他冻结 Task | Codex 集成收尾记录 |
| 2026-09-16 | 用户 | 批准释放 TASK-016 OCR 与检测路线独立实验；Owner=DeepSeek Harness、Reviewer=Codex、base=`f9edd68845d4a1ee5d42d9fdcf1a304dc3fa2f86`、branch=`agent/deepseek/TASK-016-ocr-detection-experiment`、worktree=`G:/CODEX/New Manga.worktrees/TASK-016-deepseek`；仅限 TASK-016 白名单，实验结论不自动成为产品需求；不释放 TASK-015、TASK-017～TASK-027 或其他冻结 Task | 用户本次批准指令 |
| 2026-09-16 | 用户 | 批准释放 TASK-016 OCR 与检测路线独立实验；Owner=DeepSeek Harness、Reviewer=Codex、base=`f9edd68845d4a1ee5d42d9fdcf1a304dc3fa2f86`、branch=`agent/deepseek/TASK-016-ocr-detection-experiment`、worktree=`G:/CODEX/New Manga.worktrees/TASK-016-deepseek`；仅限 TASK-016 白名单，实验结论不自动成为产品需求；不释放 TASK-015、TASK-017～TASK-027 或其他冻结 Task | 用户本次批准指令 |
| 2026-09-16 | 用户 | 批准同步释放 TASK-015 阅读器与五种成果导出及 TASK-016 OCR 与检测路线独立实验；TASK-015 Owner=ZCode、Reviewer=DeepSeek Harness、base=`1000ac82743b75df8b4b385bc7096a015e13f107`、branch=`agent/zcode/TASK-015-reader-export`、worktree=`G:/CODEX/New Manga.worktrees/TASK-015-zcode`；TASK-016 保持 Owner=DeepSeek Harness、Reviewer=Codex；两者使用独立 worktree、写集合不重叠，实现可并行，Review/集成仍按协议独立串行；不释放 TASK-017～TASK-027 或其他冻结 Task | 用户本次批准指令 |
| 2026-09-17 | ZCode（窗口授权代行） | TASK-015 窗口收口：首轮交付 fac2ffe 经复核不满足 AC 深度后全量重写（`488fafc`）；窗口内子 agent Review 首轮 `changes_requested`（P1×2、P2×4），修订 `ac4ff19` 后复审 `approved_subagent`（R-007 deferred 至 TASK-020）；按条款代行集成 master（merge=`fa72cee`，冲突仅 TASK-015.md 且分支版已覆盖授权表述）并完成集成后复验（全仓 `536 passed, 0 skipped`）；TASK-015 置 `done`；NOT_RUN（PDF 像素级、真实磁盘注入、装配接线）与 Webtoon 完整验收（TASK-020）保持不掩盖；TASK-024/017 依窗口条款解冻实施中 | 分支 `agent/zcode/TASK-015-reader-export` head `a915d56`；Review `doc/reviews/TASK-015-488fafc.md`；Handoff `doc/handoffs/TASK-015-488fafc.md`；验证 `verification/TASK-015/author-verification.md` |
| 2026-09-17 | ZCode（窗口授权代行） | TASK-024（仅设计）窗口收口：`done`——设计文档 `doc/contracts/extensions.md` 定义六条目边界/支持矩阵/授权失败边界/15 条 AC 草案与释放条件，Plugin Agent 保留条件 fail-closed，用户待决清单 U-1~U-6；子 agent Review `approved_subagent`（P2×5：R-001..R-004 fixed、R-005 deferred）；integration=`61c33e2`，master 复验 `536 passed`；权威文档需求裁决回写待用户批准，TASK-023/025/019/022 维持冻结直至批准 | 分支 `agent/zcode/TASK-024-extension-boundaries-design` head `86072c3`；Handoff `doc/handoffs/TASK-024-design-boundaries.md`；验证 `verification/TASK-024/author-verification.md` |
| 2026-09-17 | ZCode（窗口授权代行） | TASK-017（实验）窗口收口：`done`——OpenAI 兼容 mock Provider + RegionID 契约校验（5 类违约分类、§56 retryable、§57 payload hash 输入不变、§54 显式 fallback、§84 预算截断保 Region、术语一致性 3/3），15 例 pytest + S1~S8 results.json 全过；子 agent Review `approved_subagent`（7×P2，无 P0/P1）；integration=`c0cf3a1`；真实 Provider/Sakura/模型质量层 NOT_RUN（付费端点未配置且禁止自行配置，恢复方法已登记）；reading_export QML 低频 flaky 登记移交 | 分支 `agent/zcode/TASK-017-translation-protocol-experiment` head `ae74250`；Handoff `doc/handoffs/TASK-017-protocol-experiment.md`；报告 `doc/research/TASK-017.md`；验证 `verification/TASK-017/author-verification.md` |
| 2026-09-17 | ZCode（窗口授权代行） | TASK-018/019 按窗口排除项登记 `blocked`：解冻名单（TASK-015/024/017）不含二者，ZCode 无权解冻；恢复条件=用户批准释放（TASK-019 另需 TASK-018 解冻与 TASK-017 真实端点层输入） | 前状态 proposed；条款见 STATUS「ZCode 全权窗口授权」排除项 |
| 2026-09-17 | 用户 | 检查项目进度后指示：归还 Codex 与 DeepSeek Harness 权限、撤销 ZCode 九小时全权窗口授权。进度确认：窗口三项目标 TASK-015（integration=`fa72cee`）、TASK-024（`61c33e2`）、TASK-017（`c0cf3a1`）均已收口 `done`，TASK-018/019 已登记 `blocked`；自本决定起 Codex 恢复 Lead/唯一主线写入与集成职责，DSH 恢复独立 Reviewer 职责，窗口交付（Review 均为 `approved_subagent`）的外部 post-hoc 复审已提交 DeepSeek Harness，待结论；未决事项移交：TASK-024 U-1~U-6 用户裁决、reading_export QML 低频 flaky 跟踪、TASK-015 生产装配接线与进度/导出 SQLite 迁移、TASK-017 真实端点层（待用户提供端点） | 本收口提交；窗口章节失效登记见「ZCode 全权窗口授权（2026-09-16）」 |
| 2026-09-17 | 用户 | 已将 TASK-015/024/017 外部 post-hoc 复审提交 DeepSeek Harness，待 Review 报告与结论入库；固定范围：TASK-015 base=`1000ac82743b75df8b4b385bc7096a015e13f107`→head=`a915d5628ce732a7a0fd06bfdc60b6f99684e250`（`G:/CODEX/New Manga.worktrees/TASK-015-deepseek-posthoc`）；TASK-024 base=`116e6824749340155b83ba4025ae0682232454e0`→head=`86072c30a9587d5eced3daa14c555409d6917e6c`（`G:/CODEX/New Manga.worktrees/TASK-024-deepseek-posthoc`）；TASK-017 base=`348a48ee62f9c127c194ba02748d9d64c08bde60`→head=`ae74250a513bef13eaf46ed082bc018d5ff013b7`（`G:/CODEX/New Manga.worktrees/TASK-017-deepseek-posthoc`） | 用户本次说明；worktree HEAD 与仓库固定交付记录核对 |
| 2026-09-17 | 用户 | U-1 裁决：取消网页导入；AC-EXT-IMPORT-001/002 退役且编号不复用，TASK-023 范围调整为 PDF/MOBI。D01/D02、TASK-023、扩展契约、Roadmap 与验收追踪已同步；TASK-023 仍未释放，TASK-018/019 与其他冻结 Task 状态不变，U-2~U-6 继续待裁决 | 用户本次指示 |
| 2026-09-17 | 用户 | U-2 裁决：采用 PDFium via pypdfium2；遵循绑定包 Apache-2.0/BSD-3-Clause 及 PDFium 核心 BSD-style 许可，并在分发时附带相关依赖许可证文本。未更改依赖清单，未释放 TASK-023；U-3~U-6 继续待裁决 | 用户本次指示“按你的推荐” |
| 2026-09-17 | 用户 | U-3 裁决：批准 Plugin 首版仅支持本地目录插件，不做插件市场、在线分发或自动更新。TASK-025 仍未释放，U-4 及其依赖条件仍待处理；其他冻结 Task 状态不变 | 用户本次指示“按你的建议继续，批准” |
| 2026-09-17 | 用户 | U-4 裁决：Plugin Agent 不进入首版；待本地插件格式与权限机制实现并验收后，是否作为第二阶段引入须再次由用户裁决。首版范围不含 Agent；TASK-025 仍冻结，其他冻结 Task 状态不变 | 用户本次指示“按推荐进行下一步” |
| 2026-09-16 | Codex | TASK-016 按 §6.6 集成：来源 `reviewed_head=f544261` 保留为 merge parent，创建 `integration_commit=9bf85f5`；Review `878ac16` 为 approved；集成后协议测试 5 passed/0 skipped，默认与 model-run 探测均 30 BLOCKED，反例仍强制三项离线开关为 1；更新 TASK-016、STATUS、索引、Roadmap 与验证证据并标记 done；保留 TASK-015 ready，不释放 TASK-015 或其他冻结 Task，未 push | Codex 集成收尾记录 |
| 2026-09-16 | 用户 | 因额度限制批准 9 小时 ZCode 全权窗口（T0=2026-09-16 23:30 ～ T1=2026-09-17 08:30 Asia/Shanghai）：除已收口的 TASK-016 外所有任务由 ZCode 全权执行，自动批准其实施申请与行为；窗口目标 TASK-015（优先级 1）→ TASK-024（2）→ TASK-017（3），由 ZCode 自主解冻 TASK-024/017 并登记元数据；子 agent Review 登记 `approved_subagent`（用户授权的同体审查，不得记 approved），期满后补外部 post-hoc 复审；ZCode 代行主线集成；白名单内全权，产品需求/验收标准变更、发布 Gate 放宽、push 远端、依赖清单与 Schema 变更、触碰 TASK-016 及解冻名单外 Task 均排除；期满授权失效，未完成任务冻结现状 | 用户本次授权指令；完整条款见本文件「ZCode 全权窗口授权（2026-09-16）」章节 |

## ZCode 全权窗口授权（2026-09-16）【已失效——2026-09-17 经用户指示归还撤销】

> **失效与归还登记**：2026-09-17 用户指示撤销本窗口授权并归还 Codex（Lead/唯一主线写入与集成责任人）与 DeepSeek Harness（独立 Reviewer）的长期职责；窗口期内已完成的集成不回滚；窗口交付（TASK-015/024/017，窗口内 Review 均为 `approved_subagent`）的外部 post-hoc 复审当时仍待结论，后于 2026-09-17 完成且三份报告均 approved，findings 收口见 `c7a02bd`。以下条款仅作存档，不再具有效力。

生效窗口：T0=2026-09-16 23:30 ～ T1=2026-09-17 08:30（Asia/Shanghai），共 9 小时；T0 以本节随授权提交进入 master 的时刻为准。本授权由用户于 2026-09-16 批准，用于在 Codex/DeepSeek Harness 额度受限期间维持进度；窗口期满自动失效，长期角色与流程回归 [协作协议](09_COLLABORATION.md)。

### 范围与效力

1. 窗口期内所有任务由 ZCode 全权执行：用户自动批准 ZCode 的实施申请与行为，无需逐项请示；Codex 与 DeepSeek Harness 暂停参与。
2. 窗口目标三项，按优先级串行执行（前一项收口后进入下一项；时间不足时按优先级取舍）：
   - [TASK-015](tasks/TASK-015.md) 阅读器与五种成果导出（base=`1000ac8`，branch=`agent/zcode/TASK-015-reader-export`，worktree=`G:/CODEX/New Manga.worktrees/TASK-015-zcode`；2026-09-16 已实现 head=`fac2ffe` 并交付 handoff=`6917b0b`，状态 in_review；窗口内 Review 由 ZCode 子 agent 执行，结论登记 `approved_subagent` 后集成；分支正文中"通知 DeepSeek Harness 独立 Review"为窗口授权固化前的表述，以本章节为准）；
   - [TASK-024](tasks/TASK-024.md) 明确扩展能力及验收覆盖边界（仅设计）；
   - [TASK-017](tasks/TASK-017.md) Translation 与上下文输出协议实验。
3. ZCode 代行 Codex 的以下职责：窗口目标 Task 的解冻登记（proposed→ready，填写 owner/base_commit/branch/worktree；TASK-024/017 的 base 取解冻时 master HEAD，branch/worktree 按 `agent/zcode/TASK-xxx-slug` 新建）、主线写入与协作协议 §6 的串行集成（含 ZCode 自身实现的任务）、`doc/00_INDEX.md`、`doc/12_ROADMAP.md`、`doc/tasks/README.md` 与 STATUS 的元数据回填。
4. 每个窗口目标按完整生命周期执行：实施 → Review → 修订 → 集成 → STATUS/Task 收口；各 Task 白名单、依赖与验收标准不变。

### Review 定性（协议核心临时变更，经用户授权）

- 窗口期内 Review 由 ZCode 开子 agent 执行：必须使用 [Review 模板](templates/REVIEW.md)、固定 base_commit 与 reviewed_head、实际运行测试并在报告中 passed/skipped 分列、报告入库 `doc/reviews/`。
- 结论只能登记为 `approved_subagent` 或 `changes_requested`，**不得登记为 `approved`**。`approved_subagent` 是用户授权的同体审查（Owner 与 Reviewer 同为 ZCode 及其子 agent），不等同协作协议 §1 的跨 Agent 独立批准。
- 窗口期满后，用户应安排 Codex 或 DeepSeek Harness 对窗口期全部集成交付补一次外部 post-hoc 复审；该义务不因窗口关闭而消失，复审结论记入审核记录。

### 排除项（自动批准不覆盖，遇之即登记 `BLOCKED` 并等待用户）

- 产品需求与范围变更、D08 验收标准或发布 Gate 放宽；
- `git push`、配置远端、向外部服务发送内容；
- 依赖清单（requirements/pyproject）与 Schema 变更；
- 触碰 TASK-016 交付物（已于 `9bf85f5` 收口）及其 worktree/分支、他人 worktree 与未提交内容；
- 解冻窗口目标名单之外的 Task（TASK-018～TASK-027 中未列入目标者仍冻结）。

### 到期处置

- T1 后本授权失效：未完成任务冻结于当时状态（含 in_progress/in_review/blocked），等待用户安排；失效后不得凭本授权继续实施或集成。
- 窗口内已完成的集成不回滚；期满后第一件事为一次纯文档收口提交：审核记录登记失效、移除 09_COLLABORATION 与 AGENTS 的临时条款（仅元数据提交，无需重跑产品测试）。
