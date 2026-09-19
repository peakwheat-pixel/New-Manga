# 项目文档索引与 Source of Truth

2026-09-19 TASK-059 ND-1 用户裁决：候选方向选择 **A 的配色/视觉令牌与 IA + B 的几何比例（控件高度、行高、间距、字号、面板尺寸）**；不继承 B 的章节大卡 IA，也不启用 C 玻璃、D 顶栏或 E 命令面板。组合稿必须重新通过完整一致性审计后才能集成，C/D/E 未被选择。详见 [STATUS](STATUS.md) 当前台账。

2026-09-19 TASK-059 改派：按用户指示，设计重做 Task 的 Owner 由 Qoder 改为 **ZCode**；新的 branch=`agent/zcode/TASK-059-ui-redesign`、worktree=`G:/CODEX/New Manga.worktrees/TASK-059-zcode`，Reviewer 仍为 Codex。原 Qoder 分支/worktree 未实施且仅留档，不再作为开工工作区；AC、授权和范围不变。

2026-09-19 增量：用户指定 **Qoder 为 UI/UX、GUI 与 QML 视觉/交互设计责任方**；[TASK-047](tasks/TASK-047.md)（Owner=Qoder，仅设计）**已被用户否决 → `rejected`**（R-1 视觉方向 / R-2 布局与信息架构 / R-3 太保守；裁决记录见该 Task 末尾，分支 `agent/qoder/TASK-047-ui-ux-gui-design` @`980ae7d` 未合并保留）；设计门改由新立的 [TASK-059](tasks/TASK-059.md) 承接（**授权重画配色与布局**、要求 2–3 个实质不同的候选方向）。[TASK-047](tasks/TASK-047.md) 原计划交付设计规范与视觉参考，不写生产代码。TASK-022 保持 `proposed`，并改列 Qoder 为建议 Owner；TASK-047 `done` 且用户另行批准后才释放实现。

状态（2026-09-19 更新）：TASK-001～TASK-021（TASK-021 仅 trash 子集）、TASK-024、TASK-028～TASK-044 已完成并集成；TASK-041 已完成并集成（`7c4fae0`）；TASK-045 已完成并集成（`e2a8f01`）；TASK-046、TASK-048～TASK-056、TASK-058 已完成并集成（**ZCode 全权窗口 2026-09-19 W0–W11**）；TASK-057 交付待集成（分支 `agent/zcode/TASK-057-backup-restore` 冻结于 `50c4b1a`）；TASK-022、TASK-025～TASK-027 仍冻结（proposed）。**角色已恢复初始定位**：Codex=Lead/唯一主线写入与合并责任人、ZCode=独立 Feature、DeepSeek Harness=独立 Review（不得自审）、Qoder=独立 Feature（与 ZCode 同面，可作**非作者** Reviewer）；Review 须覆盖 Architecture+Verification，Standards/Spec 为可选视角。以下为历史细节：TASK-013 生产 Pipeline seam 已按 `integration_commit=49c72fdf` 集成，R-1 已按 `integration_commit=734d5b3` 完成生产 Workbench 装配并验证；TASK-016 已按 `integration_commit=9bf85f5` 完成集成；TASK-018 已完成 Mask/Inpainting 路线独立实验的**三轮**独立 Review 与集成——首轮 `integration_commit=4d189ce`（Review `doc/reviews/TASK-018-6c33e7f.md` approved），修订切片 `integration_commit=14b92e4`（Review `doc/reviews/TASK-018-5063315.md` approved），尾项切片 `integration_commit=5a9f5c8`（Review `doc/reviews/TASK-018-965bcd2.md` approved；R-001～R-007 与 R-101/R-102/R-103/R-104/R-201 全部 closed，无待处理 finding；学习型路线质量与 Mask 内部结构损伤仍 BLOCKED/NOT_RUN）；TASK-015 已按窗口条款收口 `done`（integration=`fa72cee`，Review=`approved_subagent`）；TASK-024 已按窗口条款收口 `done`（仅设计，integration=`61c33e2`，扩展边界设计见 [TASK-024 契约](contracts/extensions.md)，U-1 已取消网页导入；U-2 已选 PDFium via pypdfium2；U-3 已批准本地目录插件首版范围；U-4 已决定 Plugin Agent 不进入首版，二阶段另行裁决；U-5 已批准字体上传上限与许可提示；U-6 已批准 Sakura 监控限于健康探测和就绪状态、不做深度指标），TASK-017 已按窗口条款收口 `done`（integration=`c0cf3a1`，实验报告见 [doc/research/TASK-017.md](research/TASK-017.md)），其尾项修订切片（吸收 Review R-001/R-002/R-003）已由非作者独立 Review（`doc/reviews/TASK-017-971efe6.md` approved）后集成（`integration_commit=d36f724`；R-001/R-002/R-003/R-101 全部 closed；真实端点层仍 NOT_RUN），窗口三项目标（TASK-015/024/017）全部完成；三份外部 post-hoc Review 均 approved，findings 已由 `c7a02bd` 收口。**TASK-019 已完成并集成**（Owner=`DeepSeek Harness`、Reviewer=`Codex`（非作者）、base=`36242fb`、被审 head `726baf5`（元数据 `6c981c2`）、Review `doc/reviews/TASK-019-726baf5.md` approved（F-1～F-7）、`integration_commit=3755af9`；集成后 `tests/providers` 110 passed/0 skipped、`tests/pipeline`+`core`+`storage` 78 passed/0 skipped、全仓 640 passed/6 skipped；**尾项切片（Standards S-1/S-2 分层修正）** 经非作者 Review `doc/reviews/TASK-019-ab26601.md` approved 后以 `integration_commit=9a5486a` 集成，`application → infrastructure` 依赖为 **0** 并有回归守卫，S-1/S-2 已关闭）；TASK-019 的 **AC-RFULL-001 完整链仍 `BLOCKED`**（缺 `color`/`term_extract`/`render` handler），且 Review 登记了**跨 Task P0 缺陷 F-1**（默认 `sfx_policy='skip'` + planner 不看 `region_type` → 真实默认下整链被 `SKIP_POLICY` 跳过，待用户/Codex 裁决后另立 Task）。TASK-020～TASK-023、TASK-025～TASK-027 继续冻结。仓库现状见 [STATUS](STATUS.md)。2026-09-16 23:30 ～ 09-17 08:30（Asia/Shanghai）的 ZCode 全权窗口已于 2026-09-17 按用户指示归还撤销；条款存档见 [STATUS](STATUS.md)「ZCode 全权窗口授权」。【2026-09-17 23:12:28 ～ 2026-09-18 08:50（Asia/Shanghai）第二个 ZCode 全权窗口进展（执行中）】：W1 **TASK-037 已收口 `done`**（integration=`372c3bf`；已定性 flaky `test_reader_webtoon_swaps_in_vertical_viewer` 修复＋TASK-036 R-01 关闭；三份机制探针修正 TASK-036 定性（extent 批次回写 −0.0、timer 有触发但持久化了回写后的 0），Webtoon 用例夹具改 40x1000 高页＋`landed` 落点断言；Review approved_subagent `7c35277`）。W2 **TASK-033 已收口 `done`**（integration=`4d0f932`；完整链收口——`color`/`term_extract`/`render` 三 handler 接入＋渲染侧生产装配（`RenderService` 复用既有适配器＋`content_decoder` NMFR→PNG 桥）＋「单一写者」P0 约束解决（RenderService 为 `translated` 指针唯一写者，render handler `revision_updates={}`，三次 render 指针 `[1,2,3]` 无抖动）；**AC-RFULL-001 口径更新为 BLOCKED（handler 与生产装配面已打通；真实 OCR/翻译/修复能力仍缺）＋逐项解锁条件，未记 PASS**；Review approved_subagent `401d6d7`；遗留 R-001 P2＝`_clean_available` 继承缺陷（render-only 命令跨 run 规划 BLOCKED，planner 在切片路径外未修，移交 Codex）。W3 **TASK-020 已收口 `done`**（integration=`b738200`；Webtoon 分块处理与阅读——新建 `src/infrastructure/imaging/webtoon_tiles.py`（TileGrid 几何/TileCache LRU/TiledPageRasterizer 按需解码），ViewModel opt-in `tile_factory` 接线（未注入时整图路径不变），QML webtoon viewer tiled 分支；一 Page 原则、坐标回映、边界去重、跨会话恢复均有测试；**1600x200000px fixture 像素解码 BLOCKED（Qt PNG handler ≳300MB rgb32 硬限制、setClipRect 无效），几何层 PASS，未记 PASS**；首轮 Review changes_requested（R-001 P1 全页同步解码）修订收口后复审 approved_subagent `40f20e7`）。F-1（跨 Task P0）已全面关闭：规划面 TASK-032（`e3e055e`）＋渲染面 TASK-035（`bd0d030`）。TASK-034（integration `b6051e5`+`8ca4b23`）与 TASK-036（integration `2725324`）此前已集成。**全部窗口集成的 Review 均为 approved_subagent（用户授权的同体审查）——期满后强制 Codex + DeepSeek Harness 外部 post-hoc 复审（可推翻窗口内 done）。**仓库现状见 [STATUS](STATUS.md)。「当前状态」段的历史口径见本行前文与 [12 Roadmap](12_ROADMAP.md)；本行截至 TASK-019/F-1 待裁决为止，其后进展以上述窗口进展为准。【第二轮（同一 T1=08:50）进展】：W5 **TASK-038 已收口 `done`**（integration=`f835ac9`；`assemble_engine` 注册 `readerViewModel`/`exportViewModel`——export 双路径（路径 A=`readerViewModel.exportController`、路径 B=`exportViewModel` 独立窗口随 workbench 章节）写明并以测试锁定；`tile_factory` 注入（TASK-020 分块阅读生产可达）；`ImportDocumentsUseCase` 接线（TASK-023 PDF 可达、MOBI 仍 typed UNSUPPORTED）；新增 `_ManagedReaderCatalog`（Page→ReaderPage，translated 消费当前 artifact）；`test_qml_contract.py:224` 前提变化等价更新；Review approved_subagent `fcf791f`）。W6 **TASK-039 已收口 `done`**（integration=`c8024fe`；planner `_clean_available` 判据叠加可选 `clean_probe`——probe=None 与修前逐字节等价，根因/对照矩阵/判别力留证；**TASK-033 R-001 已关闭**；生产 probe 注入点（bootstrap）白名单外移交；Review approved_subagent `18c9834`）。W7 **TASK-021 自洽子集已收口 `done`**（integration=`5bc17f8`＋修订 `b940497`；Page 级软删除/同 batch 恢复/受控-only 永久删除——`deleted_at` 列本就存在故零 Schema/migration 变更；`remove_managed` 防逃逸；R-001 P2 修订闭环（复审复现验证回归钩子），其余三子集 frozen；Review approved_subagent `a9b4141`+`79ec0d2`）。**第二轮全部 Review 为 approved_subagent（同体审查）——T1 后 Codex + DSH 强制 post-hoc 复审（可推翻）。**第二轮统一证据口径＝powershell.exe（继承 PATH，openssl 可用）+ TASK-012-py312 → 全仓 N passed/0 skipped（基线 770 → 772 → 780 → **787**）。「当前状态」段第一轮口径（截至 TASK-023）保留于本行前文，第二轮进展如上。【2026-09-19 01:10 ～ 09:00（Asia/Shanghai）第三个 ZCode 全权窗口进展】：W0 **TASK-046**（解码面 overlap=0 / rewind 折叠；Qoder 非作者 Review）integration=`2b40085`；W1 **TASK-048**（§11 P-1 跨线程 SQLite + 生产路径端到端测试资产）`be558ca`；W2 **TASK-049**（§11 P-2 区域输入面：detect handler + Region 生产路径）`e94d5af`；W3 **TASK-050**（§11 P-3 非 UI：设置/provider 绑定注入）`21b7301`；W4 **TASK-051**（§11 P-6 工作台三档视图）`65d1e13`；W5 **TASK-052**（§11 P-4 命令失败可见化，provisional）`a1c8171`；W6 **TASK-053**（TASK-044 R-03/R-04）`cd57ee4`；W7 **TASK-054**（TASK-043 R-02 改名）`771dbf7`；W8 **TASK-055**（TASK-021 子集①日志/诊断）`0493ea9`；W9 **TASK-056**（子集②缓存·版本·模型清理）`11517ac`；W11 **TASK-058**（自建切片，§11 P-10 退出排空）`414a8e1`。**W10 TASK-057（子集③备份/恢复）交付未集成**（并行会话，冻结 `50c4b1a`）。窗口内 Review 除 W0（Qoder `approved`，用户把 Reviewer 由 DSH 改派）外**全部为 `approved_subagent`（同体审查）**——按协议不是独立批准，**已排 Codex + Qoder 外部 post-hoc 复审（可推翻；原 DSH 槽位 2026-09-19 按用户指示改派 Qoder）**。收口验证：全仓 **905 passed / 6 skipped（共 911 collected）exit 0**（openssl 可用口径 911/0），与 T0 基线 848 collected 相比 +63 例。第三窗口进展如上。所有路径均相对本文档；保留现有 doc 目录及 02 文件名末尾的下划线。

## 原始目标文档（已完整检查）

| 证据编号 | 文档 | 权威职责 | 当前性质 |
|---|---|---|---|
| D01 | [01 功能架构](01_FUNCTIONAL_ARCHITECTURE.md) | 产品能力范围、入口、扩展能力 | To-Be；§5 的旧代码引用不能证明本仓库实现 |
| D02 | [02 技术架构](02_TECHNICAL_ARCHITECTURE_.md) | 分层、技术选型、依赖边界、运行拓扑 | To-Be；TASK-005 仅实证最小 Python/PySide6 Core 入口与当前包边界 |
| D03 | [03 数据模型](03_DATA_MODEL.md) | 实体、字段、数据不变量、持久化归属 | To-Be；G06～G13 的最小实现契约由 TASK-002 冻结；TASK-006 已有 v1 SQLite 基础，统一 v2 设计见 TASK-028 |
| D04 | [04 用户流程](04_USER_FLOW.md) | 操作意图、用户流程、对象范围 | To-Be |
| D05 | [05 UI 映射](05_UI_MAPPING.md) | Screen、Panel、Window、动作与 ViewModel 映射 | To-Be；内含线框示意，非实际 QML |
| D06 | [06 Pipeline](06_TRANSLATION_PIPELINE.md) | 命令语义、DAG、Lock、失效、重试与进度协议 | To-Be；G06～G13 的最小执行契约由 TASK-002 冻结 |
| D07 | [07 非功能需求](07_NON_FUNCTIONAL_REQUIREMENTS.md) | 性能、容量、可靠性、安全、Windows 与打包 | 目标数值，未经 Benchmark 验证 |
| D08 | [08 验收标准](08_ACCEPTANCE_CRITERIA.md) | 验收预期、证据要求与发布 Gate | 验收规格，不是测试实现或 PASS 报告 |

TASK-001 已将 D03～D08“基于”列表里的历史长文件名改为上表实际文件；这只恢复当前项目导航，不证明与未提供的历史版本逐字一致。原始引用保存在基线 `496b4ed`。

## 接管与执行文档

| 文件 | 用途 / 何时阅读 |
|---|---|
| [AGENTS.md](../AGENTS.md) | 三 Agent 每次进入项目必读入口 |
| [STATUS](STATUS.md) | 当前授权、开发阶段、用户审核记录 |
| [09 协作协议](09_COLLABORATION.md) | 角色、Git、Task/Handoff/Review 生命周期 |
| [10 当前状态与 Gap Analysis](10_CURRENT_STATE_AND_GAPS.md) | 本次盘点、证据指纹、代码与目标差距、审核清单 |
| [11 架构与交互地图](11_ARCHITECTURE_MAPS.md) | 11 类接管基线视图；目标设计仍不得冒充 TASK-005 最小骨架的实际能力 |
| [12 Roadmap](12_ROADMAP.md) | 阶段 Gate、依赖和范围取舍 |
| [13 验收追踪](13_ACCEPTANCE_TRACEABILITY.md) | D08 条目到计划 Task 的映射；不代表已验收 |
| [14 接管验证](14_TAKEOVER_VERIFICATION.md) | 本次文档自检结果、复现命令与验证边界 |
| [接管自检脚本](verify_takeover.ps1) | 仅适用于初始接管快照；TASK-001 已修改文档与授权，其 Hash/冻结断言不再适用于当前工作区 |
| [TASK-001 检查](../verification/TASK-001/verify.ps1) | 验证文档引用、状态枚举、AC 编号/优先级及修改范围 |
| [TASK-002 最小契约](contracts/TASK-002_MINIMUM_DATA_EXECUTION_CONTRACT.md) | G06～G13、R-011 的冻结语义；后续 Schema/Pipeline/UI/测试共同输入 |
| [TASK-028 统一 SQLite 设计](contracts/TASK-028_UNIFIED_SQLITE_PERSISTENCE_DESIGN.md) | TASK-006/007/008 的 SQLite 收敛设计；实现由 TASK-029 承接 |
| [TASK-029 统一 SQLite 实现](tasks/TASK-029.md) | 按 TASK-028 实现 v2 migration、Library/Page/Region adapter 与原子 Revision seam；已集成 |
| [任务目录](tasks/README.md) | 62 个 Task 索引；单个文件是任务状态真值 |
| [Task 模板](templates/TASK.md) | 新任务创建 |
| [Handoff 模板](templates/HANDOFF.md) | 实现 / 实验交付、故障中断交接 |
| [Review 模板](templates/REVIEW.md) | 按固定 commit 独立审查和复审；**必须覆盖 Architecture / Verification 两面**；`code-review` 技能的 **Standards / Spec 为可选视角**（2026-09-18 用户决定取消其与 Spec 的"双轴"强制口径与并行/隔离要求）；建议标注各视角 `executed`/`N/A` |

handoffs、reviews、verification 已包含固定提交的真实交付；目录或文件名本身仍不等于审查/验证通过。

## Source of Truth 按问题区分

| 要回答的问题 | 事实来源 | 不能替代它的材料 |
|---|---|---|
| 当前实际做到了什么 | 当前项目 commit 的源代码、迁移、配置与同 commit 测试证据；工作区变化单独说明 | To-Be 图、旧项目能力表、Agent 自述 |
| 产品应该做什么 | D01/D04/D05；冲突提交用户决策并在相关权威文档修订 | 实现中的偶然行为、测试中的猜测 |
| 架构及数据怎么约束 | D02/D03/D06 按职责管理；已冻结缺口以对应 `doc/contracts/` 文件解释 | 任意 Agent 的私有笔记 |
| 什么算达标 | D07/D08 与可复现 verification 记录 | 仅有测试文件或“本地通过”口头描述 |
| 谁在做什么、可改哪里 | STATUS 的阶段授权 + 单个 Task 文件 | 看板截图、聊天中的认领 |
| 交付了什么 | Handoff 中固定 commit、文件与测试结果 | 分支名称本身、作者概述 |
| Review 是否完成 | 独立 Review 报告绑定的 base/head + Codex 集成验证 | 作者自查或对旧 head 的批准 |

不存在“代码永远胜过需求”或“编号越大越权威”的规则。代码回答实际行为，文档回答目标，两者差异记录为 Gap。D08 明确要求冲突先修订设计，不能用测试替代设计决策（D08 L15）。

冲突处理：记录双方文件/章节/行号 → 在 Gap/Task 标明影响 → Codex提出可审查修改 → 产品范围变化由用户决定 → 在权威文档修订并同步受影响图和 AC。当前发现的问题尚未自动裁决。

## 文档维护规则

- 新事实标明 As-Is（代码/测试）、To-Be（目标）、Proposal（本次建议）或 Unknown（无证据）。
- 原始 01～08 已保存在初始基线；后续仅按已授权 Task 修订。接管报告的 SHA256 是修订前指纹，不是当前文件必须保持的值。
- 架构图与矩阵是派生视图；出现实现后补充 source/test 路径与 commit，才能标为代码生成。
- 代码、测试和文档同一 Task 一起交付。涉及未分配的共享文档，先交 Codex协调写权限。
- 同一个结论只维护一个权威位置，其余位置使用链接；STATUS 管阶段，Task 管进度，Review 管审查结论。
