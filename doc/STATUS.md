# 当前开发状态

更新日期：2026-09-16（Asia/Shanghai）

| 项目 | 状态 |
|---|---|
| 阶段 | TASK-001～TASK-010、TASK-012、TASK-014、TASK-028 设计与 TASK-029 已完成并集成；TASK-031 生产 ImageDecoder/Managed Copy 适配器已交付待审；TASK-030 装配切片等待 TASK-031；其他业务功能继续冻结 |
| 当前授权 | TASK-012 已完成独立 Review 与串行集成；2026-09-16 用户明确授权 TASK-031，仅实施其白名单；TASK-030 尚未释放/实施；TASK-011、TASK-013、TASK-015～TASK-027 及其他业务功能仍冻结；不得释放 TASK-013/TASK-015 等冻结任务 |
| 接管审核 | approved |
| 用户审核记录 | 2026-09-15：TASK-008 已按批准范围完成 Review 与 Codex 集成；TASK-028 统一 SQLite 持久化设计冻结；随后授权的 TASK-029 已由 ZCode 实施、DSH approved Review、Codex 集成收口；TASK-009 已释放、完成独立 Review 并集成收口；本次批准释放 TASK-014；本次继续批准释放 TASK-010；本次批准 TASK-012 与 TASK-010 并行执行；TASK-010 已完成独立 Review 与串行集成收口；TASK-011、TASK-013、TASK-015～TASK-027 与其他业务功能继续冻结。2026-09-16：按 §6.6 集成 TASK-012；关闭 R-001/R-002；批准建立独立 TASK-030 装配切片但因生产 Qt 解码/Managed Copy 依赖缺失保持 BLOCKED，不释放 TASK-013/TASK-015；随后授权 Codex 实施 TASK-031 生产 ImageDecoder/Managed Copy 适配器，仍不释放 TASK-030 或其他冻结 Task。 |
| 目标基线冻结 | 未冻结；见 Gap Analysis |
| 应用源代码 / 可执行测试 | TASK-005 最小入口与守卫、TASK-006 持久化与 Artifact 基础、TASK-007 书架领域与本地图片导入、TASK-008 Region 编辑/Revision/人工保护、TASK-009 Provider 配置/网络策略/凭据边界、TASK-010 约束/TM/Context、TASK-012 四页导航与书架 UI、TASK-014 渲染切片、TASK-029 统一 SQLite v2 持久化已入库；尚无完整产品功能 |
| 项目 Git 分支 / 当前 Task 基线 | `agent/codex/TASK-031-production-import-adapters`（Codex 当前交付分支）；TASK-009 base=`3de750a`，reviewed_head=`b42fc32`，implementation merge=`dea1dee`，integration_commit=`6c732be`，Owner=`ZCode`，Reviewer=`DeepSeek Harness`；TASK-010 base=`2bdfd6f`，reviewed_head=`cd76d30`，implementation merge=`1ea9c80`，integration_commit=`a225790`，Owner=`ZCode`，Reviewer=`DeepSeek Harness`，branch=`agent/zcode/TASK-010-translation-context`；TASK-012 base=`2cceb1e`，reviewed_head=`ca5848b`，implementation merge=`b324d4b`，integration_commit=`78987c8`，Owner=`ZCode`，Reviewer=`DeepSeek Harness`，branch=`agent/zcode/TASK-012-navigation-library-ui`；TASK-014 base=`29592c9`，reviewed_head=`72cb2be`，implementation merge=`a61216a`，integration_commit=`a943297`；TASK-029 base=`79529bc`，reviewed_head=`5abc173`，implementation merge=`2ea5445`，integration_commit=`0b0b855`；TASK-030 base=`78987c8`，Owner=`ZCode`，Reviewer=`DeepSeek Harness`，status=`BLOCKED`；TASK-031 base=`29b146f`，Owner=`Codex`，Reviewer=`DeepSeek Harness`，status=`in_review` |
| TASK-001 交付 / 集成 | 首次 615a073；Review 修订 cdc736c；integration_commit a1cb24c |
| Git remote | 未配置 |
| 文档版本状态 | TASK-003 reviewed head `9c6a73b` 由 `db269e9` 集成；TASK-004 reviewed head `181a356` 由 `a501372` 集成；TASK-005 reviewed head `f343008` 由 `6607f75` 集成；TASK-005 集成审计文档收口 `9fa6835` 由 `79b7621` 合并；TASK-006 reviewed head `e1d3e2c` 由 `32a7314` 收口；TASK-007 reviewed head `6ea4dd9` 由 `2b64b0f` 收口；TASK-008 reviewed head `1f373ac` 由 `06ba2e7` 收口；TASK-009 reviewed head `b42fc32`，实现合并 `dea1dee`，Review/集成收口 `6c732be`；TASK-010 reviewed head `cd76d30`，实现合并 `1ea9c80`，Review/集成收口 `a225790`，取证 `05effee` 由 `014231f` 合并；TASK-012 reviewed head `ca5848b`，实现合并 `b324d4b`，Review/集成收口 `78987c8`；TASK-014 reviewed head `72cb2be`，实现合并 `a61216a`，Review/集成收口 `a943297`；TASK-028 reviewed head `e7f9e41` 由 `509de66` 收口；TASK-029 reviewed head `5abc173`，实现合并 `2ea5445`，Review/集成收口 `0b0b855`；TASK-030 已建立范围记录并等待 TASK-031；TASK-031 已授权、delivery_head=`c67a105`、处于 in_review。 |
| 任务分派 / 执行 | TASK-001～TASK-010、TASK-012、TASK-014、TASK-028、TASK-029：done；TASK-031：in_review（Codex，独立 Reviewer=DeepSeek Harness）；TASK-030：BLOCKED（已登记独立装配范围，未释放/未实施）；TASK-011、TASK-013、TASK-015～TASK-027 保持 proposed |
| ZCode / DeepSeek Harness 连接 | TASK-008、TASK-009、TASK-010、TASK-012、TASK-014 与 TASK-029 已交付并集成；作者与 Reviewer worktree 暂保留供审计；TASK-030 尚未创建分支/worktree；TASK-031 在 Codex 主工作路径实施，尚无 Reviewer worktree |
| 本次 Review | TASK-007、TASK-008、TASK-009、TASK-010、TASK-012、TASK-014、TASK-028、TASK-029 Review 均已按 STATUS 记录 approved；TASK-012 集成复验见 `verification/TASK-012/integration-78987c8.md`；TASK-031 已交付，尚未由 DeepSeek Harness Review |
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

TASK-012 已完成并收口：[TASK-012](tasks/TASK-012.md) 固定 `base_commit=2cceb1e734c5079870662b7a28da316e46444810`、`reviewed_head=ca5848b`、实现合并 `b324d4b`、`integration_commit=78987c8`，Owner=`ZCode`，Reviewer=`DeepSeek Harness`；[Review](reviews/TASK-012-ca5848b.md) `report_commit=084db60` 为 approved；[集成验证](../verification/TASK-012/integration-78987c8.md)记录主线复验。R-001/R-002 已关闭；入口装配范围变更建立为 TASK-030，因生产 Qt 解码/Managed Copy 依赖未就绪保持 BLOCKED。

TASK-030 已建立独立装配范围记录：[TASK-030](tasks/TASK-030.md) 固定 `base_commit=78987c8`、Owner=`ZCode`、Reviewer=`DeepSeek Harness`，生产路径为 `src/ui/qml/Main.qml` 与 `src/bootstrap/app.py`；当前依赖门禁 `BLOCKED`，不创建分支/worktree，不释放 TASK-013/TASK-015。

TASK-031 已获用户授权并交付待审：[TASK-031](tasks/TASK-031.md) 固定 `base_commit=29b146f`、`delivery_head=c67a105`、Owner=`Codex`、Reviewer=`DeepSeek Harness`，生产路径为 `src/infrastructure/importing.py`；当前只交付 Qt 解码与 Managed Copy 适配器及其测试，TASK-030 仍等待本切片 Review/集成后再决定是否解除门禁。

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
