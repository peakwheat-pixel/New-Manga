# 当前开发状态

更新日期：2026-09-16（Asia/Shanghai）

| 项目 | 状态 |
|---|---|
| 阶段 | TASK-001～TASK-014、TASK-028 设计、TASK-029、TASK-030 与 TASK-031 已完成并集成；TASK-013 生产 Pipeline seam 与 R-1 Workbench 装配已集成；TASK-016 已完成并以 `integration_commit=9bf85f5` 收口；TASK-015 按既有授权保持 ready；TASK-017～TASK-027 及其他业务功能继续冻结 |
| 当前授权 | TASK-011、TASK-012、TASK-013、TASK-031 已完成独立 Review 与串行集成；TASK-030 已按用户授权完成独立 Review、R-001～R-003 收口与 Codex 集成；TASK-013 原工作台固定 base=`46646d5`、integration=`f0814a8`，生产 seam 固定 base=`126bab5`、reviewed_head=`e5b58e7`、Review=`8f7c454`、integration=`49c72fdf`，R-01/R-02 已关闭，R-03 已由 R-1 关闭；R-1 固定 base=`7c889cf`、reviewed_head=`7f3be54`、Review=`r1-review-7f3be54`、integration=`734d5b3`，已完成生产装配与集成；TASK-015 依赖已满足，固定 base=`1000ac8`、Owner=`ZCode`、Reviewer=`DeepSeek Harness`，状态=`ready`；TASK-016 固定 base=`f9edd68`、reviewed_head=`f544261`、Review=`878ac16`、integration=`9bf85f5`、Owner=`DeepSeek Harness`、Reviewer=`Codex`，状态=`done`；TASK-017～TASK-027 及其他业务功能仍冻结，不得释放其他冻结 Task |
| 接管审核 | approved |
| 用户审核记录 | 2026-09-15：TASK-008 已按批准范围完成 Review 与 Codex 集成；TASK-028 统一 SQLite 持久化设计冻结；随后授权的 TASK-029 已由 ZCode 实施、DSH approved Review、Codex 集成收口；TASK-009 已释放、完成独立 Review 并集成收口；本次批准释放 TASK-014；本次继续批准释放 TASK-010；本次批准 TASK-012 与 TASK-010 并行执行；TASK-010 已完成独立 Review 与串行集成收口；TASK-011、TASK-013、TASK-015～TASK-027 与其他业务功能继续冻结。2026-09-16：按 §6.6 集成 TASK-012；关闭 R-001/R-002；批准建立独立 TASK-030 装配切片，保持 BLOCKED/未释放，不释放 TASK-013/TASK-015；随后授权 Codex 实施 TASK-031 生产 ImageDecoder/Managed Copy 适配器，已完成独立 Review、R-001～R-003 关闭与串行集成；本次再授权释放 TASK-030，登记为 READY 并创建其专用 ZCode 分支/worktree；TASK-013/TASK-015 及其他冻结 Task 仍不释放。 |
| 目标基线冻结 | 未冻结；见 Gap Analysis |
| 应用源代码 / 可执行测试 | TASK-005 最小入口与守卫、TASK-006 持久化与 Artifact 基础、TASK-007 书架领域与本地图片导入、TASK-008 Region 编辑/Revision/人工保护、TASK-009 Provider 配置/网络策略/凭据边界、TASK-010 约束/TM/Context、TASK-011 命令计划/任务调度/可恢复进度、TASK-012 四页导航与书架 UI、TASK-013 工作台与任务进度及生产 Pipeline seam、TASK-014 渲染切片、TASK-029 统一 SQLite v2 持久化、TASK-030 生产入口装配、R-1 生产 Workbench 装配已入库；尚无完整产品功能 |
| 项目 Git 分支 / 当前 Task 基线 | master；TASK-009 base=`3de750a`，reviewed_head=`b42fc32`，implementation merge=`dea1dee`，integration_commit=`6c732be`，Owner=`ZCode`，Reviewer=`DeepSeek Harness`；TASK-010 base=`2bdfd6f`，reviewed_head=`cd76d30`，implementation merge=`1ea9c80`，integration_commit=`a225790`，Owner=`ZCode`，Reviewer=`DeepSeek Harness`，branch=`agent/zcode/TASK-010-translation-context`；TASK-012 base=`2cceb1e`，reviewed_head=`ca5848b`，implementation merge=`b324d4b`，integration_commit=`78987c8`，Owner=`ZCode`，Reviewer=`DeepSeek Harness`，branch=`agent/zcode/TASK-012-navigation-library-ui`；TASK-014 base=`29592c9`，reviewed_head=`72cb2be`，implementation merge=`a61216a`，integration_commit=`a943297`；TASK-029 base=`79529bc`，reviewed_head=`5abc173`，implementation merge=`2ea5445`，integration_commit=`0b0b855`；TASK-030 base=`087da45`，reviewed_head=`c3f1893`，implementation merge=`a58ff84`，integration_commit=`fef9dd3`，Owner=`ZCode`，Reviewer=`DeepSeek Harness`，branch=`agent/zcode/TASK-030-main-bootstrap-assembly`，worktree=`G:/CODEX/New Manga.worktrees/TASK-030-zcode`；TASK-031 base=`29b146f`，reviewed_head=`c67a105`，implementation merge=`0b44b83`，integration_commit=`e9d5185`，Owner=`Codex`，Reviewer=`DeepSeek Harness`，branch=`agent/codex/TASK-031-production-import-adapters`；TASK-011 base=`1668cd5`，reviewed_head=`6a2016b`，implementation merge=`053d253`，integration_commit=`369e95f`，Owner=`Codex`，Reviewer=`DeepSeek Harness`，status=`done`，branch=`agent/codex/TASK-011-command-scheduler`，worktree=`G:/CODEX/New Manga`；TASK-013 base=`46646d5`，reviewed_head=`da1daf1`，implementation_merge=`32a1eb5`，integration_commit=`f0814a8`，Owner=`ZCode`，Reviewer=`DeepSeek Harness`，status=`done`，branch=`agent/zcode/TASK-013-workbench-task-progress`，worktree=`G:/CODEX/New Manga.worktrees/TASK-013-zcode`；TASK-013 生产 Pipeline seam base=`126bab5`，reviewed_head=`e5b58e7`，Review=`8f7c454`，integration_commit=`49c72fdf`，Owner=`Codex`，Reviewer=`DeepSeek Harness`；R-1 base=`7c889cf`，reviewed_head=`7f3be54`，Review=`r1-review-7f3be54`，integration_commit=`734d5b3`，Owner=`Codex`，Reviewer=`DeepSeek Harness`，status=`done` |
| TASK-001 交付 / 集成 | 首次 615a073；Review 修订 cdc736c；integration_commit a1cb24c |
| Git remote | 未配置 |
| 文档版本状态 | TASK-003 reviewed head `9c6a73b` 由 `db269e9` 集成；TASK-004 reviewed head `181a356` 由 `a501372` 集成；TASK-005 reviewed head `f343008` 由 `6607f75` 集成；TASK-005 集成审计文档收口 `9fa6835` 由 `79b7621` 合并；TASK-006 reviewed head `e1d3e2c` 由 `32a7314` 收口；TASK-007 reviewed head `6ea4dd9` 由 `2b64b0f` 收口；TASK-008 reviewed head `1f373ac` 由 `06ba2e7` 收口；TASK-009 reviewed head `b42fc32`，实现合并 `dea1dee`，Review/集成收口 `6c732be`；TASK-010 reviewed head `cd76d30`，实现合并 `1ea9c80`，Review/集成收口 `a225790`，取证 `05effee` 由 `014231f` 合并；TASK-012 reviewed head `ca5848b`，实现合并 `b324d4b`，Review/集成收口 `78987c8`；TASK-014 reviewed head `72cb2be`，实现合并 `a61216a`，Review/集成收口 `a943297`；TASK-028 reviewed head `e7f9e41` 由 `509de66` 收口；TASK-029 reviewed head `5abc173`，实现合并 `2ea5445`，Review/集成收口 `0b0b855`；TASK-030 reviewed head `c3f1893`、Review `dba2637` approved，实现合并 `a58ff84`、R-001～R-003 修订 `a29f02e`、integration `fef9dd3`，已 done；TASK-031 reviewed head `c67a105`、Review `0509003` approved，实现合并 `0b44b83`、integration `e9d5185`，已 done；TASK-011 reviewed head `6a2016b`、Review `36f874a` approved，实现合并 `053d253`、integration `369e95f`，已 done。 |
| 任务分派 / 执行 | TASK-001～TASK-014、TASK-028、TASK-029、TASK-030、TASK-031、R-1、TASK-016：done；TASK-015：ready，等待 ZCode 认领；TASK-017～TASK-027 保持 proposed/frozen |
| ZCode / DeepSeek Harness 连接 | TASK-008、TASK-009、TASK-010、TASK-011、TASK-012、TASK-013、TASK-014、TASK-029、TASK-030 与 TASK-031 已交付并集成；TASK-013 工作台 integration=`f0814a8`，生产 seam Review=`8f7c454`、integration=`49c72fdf`，R-01/R-02 已关闭，R-03 由 R-1 关闭；R-1 Review=`r1-review-7f3be54`、integration=`734d5b3`；TASK-015 已释放给 ZCode、DeepSeek Harness 负责独立 Review；TASK-016 已由 DeepSeek Harness 交付，Codex Review=`878ac16`、integration=`9bf85f5` |
| 本次 Review | TASK-007、TASK-008、TASK-009、TASK-010、TASK-011、TASK-012、TASK-013、TASK-014、TASK-028、TASK-029、TASK-030、TASK-031、TASK-016 Review 均已按 STATUS 记录 approved；TASK-011 Review=`36f874a`、集成复验见 `verification/TASK-011/integration-369e95f6.md`；TASK-013 原工作台 Review=`9fbfa48`、集成复验见 `verification/TASK-013/integration-f0814a8.md`，生产 seam Review=`8f7c454`、集成复验见 `verification/TASK-013/integration-49c72fdf.md`；TASK-030 Review=`dba2637`、集成复验见 `verification/TASK-030/integration-fef9dd3.md`；TASK-031 Review=`0509003`、集成复验见 `verification/TASK-031/integration-e9d5185.md`；TASK-016 Review=`878ac16`、集成复验见 `verification/TASK-016/integration-9bf85f5.md` |
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
| 2026-09-16 | Codex | TASK-016 按 §6.6 集成：来源 `reviewed_head=f544261` 保留为 merge parent，创建 `integration_commit=9bf85f5`；Review `878ac16` 为 approved；集成后协议测试 5 passed/0 skipped，默认与 model-run 探测均 30 BLOCKED，反例仍强制三项离线开关为 1；更新 TASK-016、STATUS、索引、Roadmap 与验证证据并标记 done；保留 TASK-015 ready，不释放 TASK-015 或其他冻结 Task，未 push | Codex 集成收尾记录 |
