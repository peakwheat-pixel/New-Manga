---
task_id: FEA-06-RESIDUAL-2
reviewer: DSH 独立子 agent（独立上下文 Scope Reviewer，D-9 派发）
reviewer_kind: subagent
author: DSH（范围草案作者 / Lead）
base_commit: 669a4ae02bf8bf9d7dbdda01c4b2b9de71cb1431
reviewed_head: 466fc98b33041c5828d33e41d02899723797f6ee
decision: changes_requested
verdict: changes_requested
p0: 0
p1: 5
p2: 6
provenance:
  agent: DSH 独立子 agent
  session_id: workflow-c3e9f8b4f92341d4
  appointment: 用户本轮 scope 复核指令 + doc/checkpoints/GOAL-PROGRESS-2026-11-02.md §121（D-9）
  implementation_participation: none
  subagents: none
  mode: read_only_review_except_this_report
  date: 2026-11-03
---

# Review：FEA-06-RESIDUAL-2 范围草案（scope-r1）

**changes_requested：P0=0 / P1=5 / P2=6。** 草案方向正确：IN-1 的三场景（书架背景渐变 8s、阅读器翻页粒子 400ms、空态插画漂浮 6s）与冻结设计 `02-motion.md` §2.3 逐行同名同参数，`reduce`/分类关的降级语义也有既有 resolver 支点。但**范围尚不可冻结**：

1. **IN-2 不是逐格清单**，且把「数据端口格」与「实现中不存在的状态」混进 IN，BLOCKED 只列 B-5；
2. **「Toast 其余 severity、loading/checked 等」三方不一致**（设计四态 / 实现 `StatusKind` 九值 / `loading` 根本不存在），验收对象无法判定；
3. **IN-1 的视觉本体冻结设计未定义**（渐变颜色与停点、粒子形状与颜色、插画造型均无），卡面却写「仅消费冻结 02-motion.md 参数」，实施必然自由创作；
4. **IN-1 漏 `02-motion.md` §4 硬约束**（失焦/不可见暂停、自动化可全关）与判据①（reduce 下不创建动画对象），且「真实播放」「无布局/层级变化」未定义甚至自相矛盾；
5. **视觉验收权威未指定**，也未明文禁止「选择器/声明存在」计 PASS——这正是 D-8 当初暂缓的原始理由。

附录 A 给出可直接冻结的缩减方案（IN-1.1…1.3、IN-2A 逐格、IN-2B 像素格、OUT、BLOCKED、证据形式、allowed_paths 增减、验收命令）。**本报告不批准任何「无视觉验收的 D-8 实施」，也不批准把数据端口残项塞进本卡。**

## 范围与依据

被审对象：`doc/tasks/FEA-06-RESIDUAL-2.md` 在 `466fc98b3` 的全文（frontmatter `:1-32`、范围草案 `:39-42`、验收草案 `:44-46`）。该文件自释放提交 `54c063405` 起零修改（`git log --oneline -4 -- doc/tasks/FEA-06-RESIDUAL-2.md` 仅 1 条；`git diff --stat 54c063405 HEAD --` 该文件与 PLAN/STATUS 均为空），故 `reviewed_head` 与草案字节一致。`base_commit` 取卡面 `:13` 的 `669a4ae02`（RESIDUAL-1 集成/证据 head）。

已读（只读）：

- 关闭卡 `doc/tasks/FEA-06-RESIDUAL-1.md`：AC1–AC5 `:110-114`、禁止范围 `:116-122`、Batch A 事故记录 `:160`（默认全量曾覆盖 `verification/FEA-06/screens/*.png`，后按 HEAD 字节恢复）、Batch B NOT_RUN `:168-169`、D-8 `:190`、D-10 `:192`、Canonical Evidence `:172-185`、Closeout Record `:194-196`。
- 独立 Review：`FEA-06-RESIDUAL-1-impl-r1.md`（P1×5/P2×4，R1-001…009）、`-impl-r2.md`（P1×3/P2×3，R2-001…006）、`-impl-r3.md`（P1×1，R3-001）、`-impl-r4.md`（approved，P2×1，R4-001）、`-scope-r3.md`（approved，P2×4，R3-001…004）。
- 证据：`verification/FEA-06-RESIDUAL-1/current-evidence-index.md`（1245/0/57，当前入口）、`component-state-matrix.md`（`:47` 的 1233 快照 + `:53-77` 的 NOT_RUN 行）、`ac-coverage.md`（`:28-30`、`:40-42`）、`integration-verification.log`（逐程序集计数）。
- 冻结设计：`02-motion.md` §1–§3（`:8-61`）与 §4（`:63-68`）、`03-accessibility.md` §3–§4（`:42-64`）、`10-component-inventory.md` §1–§3（`:6-53`）、`07-page-reader.md`（`:8-24`、`:37-46`、`:64-69`）、`05-page-shelf.md` §2–§3。
- 代码支点：`MotionTimings.cs:42-62`、`MotionResolver.cs:82-85`、`WindowsMotionPreferenceSource.cs:39`、`FluentShellSurface.axaml.cs:680-706`（`motion-decorative` 类）、`FluentFrameAnimation.cs`（有限帧、detach Finish）、`ManualFluentMotionClock.cs`、`NewManga.App/AssemblyInfo.cs:5`（`InternalsVisibleTo`）、`TestAppBuilder.cs:12` 与 `FluentPageTests.cs:244-308`（headless + Skia 的 `CaptureRenderedFrame`）。
- workspace 预研：`G:\CODEX\New Manga.workspace\FEA-06-RESIDUAL-2\scope-input-analysis.md` 与 `scope-review-prompt.md`。

未审：任何实现（尚不存在）；原生 200% DPI/原生桌面/原生 a11y（B-5/D-1 无硬件）；美学质量（需视觉签署，见 R2S-005）。本轮不重跑 build/test（理由见「验证」），基线取自既有 canonical 集成日志并复算。

本会话为独立上下文子 agent，未参与该 Task 范围编制、实现或返修；唯一持久交付为本文件；未改源码/Task/证据/冻结设计，未 commit/push。起始与落盘前 `git status --porcelain=v1` 均为空。

## Architecture（scope 层，executed）

**分层方向正确**：IN-1/IN-2 全部落在表现层（Fluent 视图、DesignSystem 样式、测试、本卡证据目录），不触 Host/IPC/Schema/Core/持久化；allowed_paths `:21-31` 不包含 Core/契约/生成物/Current V2/组合根/FEA-07 seam；视觉证据目录 `verification/FEA-06-RESIDUAL-2/**` 已入域，符合 TASK 模板「allowed_paths 必须显式包含 evidence_dir」。

**但写域与禁止语义未冻结**：

- 卡面没有 RESIDUAL-1 式「禁止范围」段（R2S-011），只有验收草案 `:46` 一句「不改 Current V2/生成物/冻结设计」；缺少 Core/契约/schema/共享 `KeyMap`/`IPresentation*`/组合根/`FrontendSelector`/FEA-07 seam/真实 `%APPDATA%`/模拟数据/不 push 的显式禁令。
- IN-1 与 IN-2 的最自然落点有若干在 allowed_paths 之外：`App/Controls/FluentUi.cs:126-136`（`FluentUi.Empty` 构造 `EmptyState`，无插画位）、`DesignSystem/Controls/Feedback.cs:11-40`（`EmptyState` 只有 Title/Hint/Action，无图标/插画槽）、`DesignSystem/Controls/FluentComponents.cs:13-36`（`FluentDialog` 无危险/加载变体）、`DesignSystem/Themes/Controls/Button.axaml:44-57`（基础控件态样式在 `Themes/`，而 allowed_paths 只有 `Styles/**`）。这会导致实施者要么漏做、要么越界（R2S-007）。
- 数据端口不得越界：草案 BLOCKED `:42` 只有 B-5，未把矩阵中依赖 FEA-09…13 的格列为 BLOCKED，若这些格留在 IN 即构成越界或假实现（R2S-001）。

**Architecture 结论**：分层与写域骨架可用，但「哪些格属本卡、哪些属端口/硬件」的边界未冻结；冻结前必须按附录 A 重写 IN/BLOCKED 与禁止范围。

## Standards（可选视角，executed）

对照 `doc/templates/TASK.md`：草案缺「禁止范围」（模板 `:40-42`）与「测试要求」表（模板 `:44-48`）；缺的「Canonical Evidence / Resource Manifest / Closeout Record」在 `ready` 阶段可留待 `in_review`/关闭时填写，不作为本轮 finding。对照 `doc/templates/REVIEW.md` 的证据纪律：草案未写日志需带 shell/EXIT、57 skip 逐条原因、单次计数与差值解释（并入 R2S-009）。对照 `AGENTS.md`「不得以声明/不可复现测试计 PASS」：草案未把该禁则写进本卡（R2S-005）。

未发现工具已强制的 formatter/linter/类型问题（本卡无代码变更）。无硬性标准违规之外的 smell 判断项需要另列。

## Spec（executed）：范围 vs 来源

**IN-1（D-8）**：与 `02-motion.md:47-51` 三行逐条同名同值（8s 循环 / 400ms / 6s 循环），穷尽性成立（设计仅此三场景）；`reduce` 与分类关的语义有真实支点——`MotionResolver.cs:82-85` 把 `decorative = !reduce && flag`，`auto`+系统关经 `WindowsMotionPreferenceSource.cs:39` 落到 `Reduce`，`FluentShellSurface.axaml.cs:700` 已把 `motion-decorative` 写到 shell 类上。**但**：

- 设计只定义时长/循环，未定义视觉本体；`05-page-shelf.md` §2 无背景渐变、`07-page-reader.md` §2 无粒子层、`05-page-shelf.md:33` 空态只有「图标」，且现有 `EmptyState` 连图标都没有。卡面 `:40` 称「仅消费冻结 02-motion.md 参数」与实际需要（新建视觉元素）不符 → R2S-003。
- 设计 `02-motion.md:63-68` 的两条硬约束（失焦/不可见暂停；截图/自动化环境可关闭全部动效）与判据①（`:57`「reduce → 动画对象时长为 0 / 不创建」）未进验收；「真实播放」未定义（生产帧源 vs 手动时钟）；「无布局/层级变化」与「新增装饰层」自相矛盾（装饰层必然改变视觉树层级）→ R2S-004。
- 「可复核视觉证据」未指定签署者，且未禁止「选择器/声明存在」计 PASS → R2S-005。

**IN-2（I-4 视觉格）**：草案 `:41` 只给「Toast 其余 severity、loading/checked 等」，不是逐格清单；矩阵 `:53-77` 实际有 22 行 NOT_RUN/DECLARED，其中：(a) 普通 headless 可断言的有效属性格（impl-r2/r3 明确反对统称硬件阻塞）；(b) 依赖数据端口的格（BatchMatrix 七状态/吸顶、RunProjectionBar 投影 → B-2；ReaderPage 双页/滚动 → B-3；RegionBox 冲突 → B-7；满态统计 → B-6；Console 投影 → B-1/B-2）；(c) 原生/逐像素格（B-5/D-1）；(d) 实现中不存在状态的格（`loading`、Dialog 危险/加载、CommandPalette loading）。四类被混成一句「纯视觉格」→ R2S-001、R2S-002。

**BLOCKED**：仅 B-5，遗漏数据端口格 → R2S-001。

**与既有 Review 的承接**：R4-001 已由 `current-evidence-index.md` 处置（旧四表 1233/1213/1197 为历史快照），本卡未写该权威链 → R2S-009；D-10 三项（浮层退出 160ms / pressed 90ms / badge 150ms）已完成实现与回归、`current-evidence-index.md:31` 仍记「ZCode 视觉复核保留」，本卡未提 → R2S-008。其余 impl-r1…r4 的 P2（R1-006/007/008、R2-004/006）均已 FIXED 并有回归，无需本卡承接。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| R2S-001 | P1 | `doc/tasks/FEA-06-RESIDUAL-2.md:41`、`:42`；`verification/FEA-06-RESIDUAL-1/component-state-matrix.md:53-77` | IN-2 用「等」开放集合，未给逐格清单；同时把依赖 FEA-09…13 的格（BatchMatrix 七状态/吸顶、RunProjectionBar 投影、ReaderPage 双页/滚动、RegionBox 冲突、满态统计、Console 投影）留在「纯视觉格」语义内，而 BLOCKED 只列 B-5。实施者只能漏做、越界或造假数据，范围不可验收，也违反「数据端口不得越界」。 | 矩阵逐行列出上述格及归属（B-2/B-3/B-6/B-7/B-1）；卡面 BLOCKED 仅 B-5；卡面 `:41` 无编号、无计数、无矩阵行映射。 | 冻结逐格表：IN-2A（headless 有效属性断言，17 组）、IN-2B（像素 PNG 格，固定清单）、OUT（实现中无该状态）、BLOCKED（B-5 + 数据端口格，逐项写恢复条件）。见附录 A。 | open |
| R2S-002 | P1 | 卡面 `:41`；`doc/design/fluent-v1/10-component-inventory.md:16`；`src/NewManga.DesignSystem/Controls/Status.cs:11-22`；`src/NewManga.DesignSystem/Controls/Feedback.cs:89-105`；`src/NewManga.DesignSystem/Controls/FluentComponents.cs:13-36`；`src/NewManga.DesignSystem/Themes/Controls/Button.axaml:44-57` | 「Toast 其余 severity」三方不一致：设计写 Toast/InfoBar = info/warn/error/success；实现是 `AlertBanner.Severity: StatusKind`（九值 queued/running/done/failed/blocked/stale/skipped/notstarted/locked）；「loading」在 Button/Dialog 均无该状态（无 loading 类、无 loading 变体）。验收对象无法判定，且「补 loading」实为新增组件状态（功能变更），不是视觉格。 | 设计 `10:16` 与 `Status.cs:11-22` 枚举逐值比对；`FluentComponents.cs:13-36` 只有 `IsOpen`；`Button.axaml:44-57` 只有 pointerover/pressed/disabled；grep `loading` 无按钮态样式。 | DSH 先裁定口径：按实现枚举（`StatusKind` 逐值，记录与设计四态的偏差）或按设计四态（组件不存在 → OUT/另卡）。逐值点名写入 IN-2A；无该状态者移 OUT 并写理由。 | open |
| R2S-003 | P1 | 卡面 `:40`；`doc/design/fluent-v1/02-motion.md:47-51`；`05-page-shelf.md:13-33`；`07-page-reader.md:26-35`；`src/NewManga.App/Controls/FluentUi.cs:126-136`；`src/NewManga.DesignSystem/Controls/Feedback.cs:11-40` | 设计只定义三类装饰动画的时长/循环，未定义渐变颜色与停点、粒子形状/数量/颜色、插画造型；`05` 的空态只有「图标」且实现连图标都没有（`EmptyState` 只有 Title/Hint/Action）。卡面「仅消费冻结参数」与实际「必须新建视觉元素」不符，实施必然自由创作——与 D-8 暂缓理由（无独立视觉评审下自创不可复核）直接冲突。 | `02-motion.md:47-51` 全表无颜色/形状；`05-page-shelf.md:33` 仅「图标」；`FluentUi.Empty` 不构造任何图标/插画；`EmptyState` 构造器只加 Title/Hint/Action。 | 冻结「最小确定性实现」：仅用既有令牌（`Nm.Color.Bg.*`、`Nm.Material.*`、`Nm.Opacity.*`、`Nm.Elevation.*`）与既有 `NmIcon`；不新增图片/字体/新颜色/新几何资产；空态「插画」= 既有 `NmIcon` + 漂浮 Transform；书架背景 = 既有 Bg 令牌的两/三停渐变，不改内容区；超出即走 `fluent-v1` v1.1 重冻结。 | open |
| R2S-004 | P1 | 卡面 `:40`、`:45`；`doc/design/fluent-v1/02-motion.md:57`、`:63-68`；`07-page-reader.md:23-24` | 验收漏 `02-motion.md` §4 两条硬约束（长循环失焦/不可见暂停；截图/自动化环境可关闭全部动效）与判据①（reduce 下动画对象不创建/时长 0）；未要求「无计时器/帧回调泄漏」；「真实播放」未定义（生产 `FluentRenderClock` 真实时间 vs `ManualFluentMotionClock`）；「无布局/层级变化」与新增装饰层自相矛盾，且未写「不拦截命中、不遮挡内容、reduce 不留不可见占位」。核心 AC 因此不可判定。 | `02-motion.md:67` 原文「长时间循环动效（decorative）在窗口失焦/不可见时暂停」；`:68`「自动化测试环境必须可关闭全部动效」；`:57` 判据①；卡面只写「reduce 禁用」「可复核视觉证据」。 | 验收补：(a) 失焦/不可见暂停（真实窗口 deactivate/隐藏后帧不再推进）；(b) 自动化全关开关；(c) reduce/auto-关/category-关下不创建动画对象 + 无计时器/帧回调泄漏（detach 后停止）；(d) 真实播放=生产帧源 + 单调时钟采样首/中/尾，手动时钟只做边界；(e) 装饰层 `IsHitTestVisible=false`、不重排、不遮挡、reduce 无不可见占位；(f) 明确 `auto`+系统关与 reduce 等价。 | open |
| R2S-005 | P1 | 卡面 `:45`；`doc/tasks/FEA-06-RESIDUAL-1.md:190`；`AGENTS.md`「不得以声明/不可复现测试计 PASS」 | 「可复核视觉证据」未指定谁签署、按什么标准签署；也未明文禁止以「样式/选择器存在」或「动画对象已创建」计 PASS。D-8 当初暂缓的原始理由正是「在无独立视觉 Review 前提下由 DSH 自创会引入不可复核风险」；照草案实施会重现同一问题，违反用户「禁止把 D-8 留给无视觉验收实现」。 | 卡面 `:45` 仅「可复核视觉证据」；RESIDUAL-1 `:190` 原文即该理由；卡面无「NOT_RUN 不得计 PASS」条款。 | 冻结视觉验收协议：实现者（ZCode）不自签；由 DSH Appointment 的独立上下文 Reviewer（或用户）逐图签署，签署表含图名/场景/mode/结论；未签署格 = NOT_RUN；新增明文「不得以选择器/声明/配置存在计 PASS」「D-8 未签署不得写 MET」。 | open |
| R2S-006 | P2 | 卡面 `:40-41`；`05-page-shelf.md:33`；`07-page-reader.md:41`；`FluentUi.cs:126-136` | IN-1「空态插画漂浮」与 IN-2「EmptyState 逐像素视觉」在空态上重叠，未写分工；易出现同一视觉被两边重复认领或互相推诿（RESIDUAL-1 的 I-13/B-2、I-14/B-3 均有明文分工先例）。 | 卡面两项均覆盖空态；矩阵 `:59` 把 EmptyState 列为「逐像素视觉 NOT_RUN」。 | 明文分工：动画/降级/暂停归 IN-1.3；空态静态视觉格（标题/提示/按钮/图标布局与对比）归 IN-2B；IN-1.3 只对「漂浮」负责，不改空态文案与布局。 | open |
| R2S-007 | P2 | 卡面 `:21-31`；`FluentUi.cs:126-136`；`Feedback.cs:11-40`、`:89-105`；`FluentComponents.cs:13-36`；`Themes/Controls/Button.axaml:44-57` | allowed_paths 与 IN 落点不匹配：空态插画最自然落点 `FluentUi.Empty`/`EmptyState` 在域外；AlertBanner 的 severity 视觉若需改组件也在域外；基础控件（TabItem/Button 等）的态样式在 `Themes/Controls/**`，而 allowed_paths 只有 `Styles/**`。实施者被迫漏做或越界。 | 逐文件比对 allowed_paths `:21-31` 与上述路径；`Themes/` 与 `Styles/` 是两个目录（`ls src/NewManga.DesignSystem`）。 | 二选一由 DSH 裁决：(a) 不加域，则冻结「只在 `Views/Fluent/**` + `DesignSystem/Styles/**` 内以 Fluent 类包装/覆盖」，并把不能这样实现的格移 OUT；(b) 显式扩域（逐条列出 `App/Controls/FluentUi.cs`、`DesignSystem/Controls/Feedback.cs`、`DesignSystem/Themes/Controls/**`），扩域需在 Task 登记理由与禁止项。 | open |
| R2S-008 | P2 | 卡面全文；`doc/tasks/FEA-06-RESIDUAL-1.md:192`；`verification/FEA-06-RESIDUAL-1/current-evidence-index.md:31` | D-10 三项（浮层退出 160ms / feedback pressed 90ms / badge 150ms）已完成实现与回归，但 `current-evidence-index.md:31` 仍记「ZCode 视觉复核保留」。新卡未提，存在两种风险：重复实现（浪费并可能改动已冻结测试）或让该视觉复核无限悬空。 | RESIDUAL-1 `:192` 与 current-evidence-index `:31` 原文；新卡无 D-10 字样。 | 明文「D-10 不重复实现」；并二选一：本卡视觉验收集把三项列为**只读证据行**（不改码、不改既有断言，仅补签署），或明确转出并写恢复条件/Owner。 | open |
| R2S-009 | P2 | 卡面 `:44-46`；`integration-verification.log`；`current-evidence-index.md:9-16`、`:18-22`；`component-state-matrix.md:47`；`ac-coverage.md:28` | 基线/证据权威链未写：只写「1245/0/57」，未写逐程序集（App 626、Appearance 21、Presentation 38、Host 51/28、ThemeEngine 253、DS 97、ApplicationCore 31、CoreClient 128/22）与「不得以过滤口径替代」「57 skip 逐条原因」「单次计数与差值」；未写 `current-evidence-index.md` 已取代旧四表（1233/1213/1197 为历史）、R4-001 已由该索引处置。复核者/实施者可能引用旧 1233 或用过滤口径。 | 集成日志逐程序集与 1245/0/57 复算一致；矩阵 `:47` 与 ac `:28` 仍自述「当前 1233」，与新索引 `:4`、`:18-22` 冲突。 | 冻结基线段：唯一基线 1245/0/57（逐程序集列出）、只增不减、禁止过滤口径替代、skip 逐条原因、日志带 shell/EXIT；并写「RESIDUAL-1 当前证据权威 = current-evidence-index.md；旧四表为历史快照，不得作当前入口」。 | open |
| R2S-010 | P2 | `doc/REBASELINE_PLAN.md:22`、`:39`；`:36-37`；`doc/STATUS.md:5` | 权威指针滞后：PLAN 当前 DAG 段 `:39` 仍写「下一节点 FEA-06-RESIDUAL-1（in_progress…Batch B 待派）」，与同文件 `:36-37`（READY：FEA-06-RESIDUAL-2）和 STATUS `:5` 矛盾；PLAN `:22` 的 RESIDUAL-1 行仍停在 `4388e50bb`/1195。属 scope-r3 R3-001 同类复发，冻结前 Reality Check 会读到矛盾状态。 | `git diff 54c063405 HEAD -- doc/REBASELINE_PLAN.md doc/STATUS.md` 为空，说明释放时未刷新活文本段；逐行读取确认。 | DSH 冻结本卡时刷新 PLAN 活文本段（`:22`、`:39`）为 RESIDUAL-1 closed / RESIDUAL-2 ready 事实；历史快照段不动。 | open |
| R2S-011 | P2 | 卡面 `:21-31`、`:44-46` | 无「禁止范围」段：只有验收一句「不改 Current V2/生成物/冻结设计」，缺 Core/契约/schema/共享 `KeyMap`/`IPresentation*`/组合根/`FrontendSelector`/FEA-07 seam/真实 `%APPDATA%`/模拟数据/不 push 的显式禁令（RESIDUAL-1 `:116-122` 有完整先例）。视觉任务仍可能以「样式需要」为由改共享 seam，或用假数据构造视觉格。 | 卡面无该节；TASK 模板 `:40-42` 要求该节；RESIDUAL-1 `:116-122` 为对照。 | 补禁止范围段（逐条列路径与语义禁令），并写「确需共享辅助改动先停等 DSH 裁决」。 | open |

未发现 P0：本卡无数据/安全/契约风险；上述问题均为范围可验证性与写域纪律。

## 验证

环境：Windows（`Microsoft Windows NT 10.0.26300.0` 由既有日志；本轮 shell 为 PowerShell Core，`pwsh -NoProfile`），仓库 `G:\CODEX\New Manga`，branch `main`，`reviewed_head=466fc98b3`。全部操作为只读检查；未 build/test（理由见下表末行），未写 PNG/证据，未 push。

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 固定被审字节 | `git rev-parse HEAD`；`git status --porcelain=v1`；`git log --oneline -4 -- doc/tasks/FEA-06-RESIDUAL-2.md`；`git diff --stat 54c063405 HEAD -- doc/tasks/FEA-06-RESIDUAL-2.md doc/REBASELINE_PLAN.md doc/STATUS.md` | `466fc98b3` | PASS | HEAD=466fc98b3；工作树空；卡片仅 `54c063405` 一条提交，diff 为空 ⇒ 卡面即被审草案 |
| 治理 | `pwsh -NoProfile -File tools\governance\check.ps1` | 同上 | PASS（3 既有 warnings） | CHECK_EXIT=0；warnings：9 非终态 Task、STATUS 80%、PLAN 80% |
| 冻结契约 pin | `pwsh -NoProfile -File tools\governance\verify_pins.ps1` | 同上 | PASS | PINS_EXIT=0；15/15 |
| 基线复算 | 读 `verification/FEA-06-RESIDUAL-1/integration-verification.log` 逐程序集，算术复核 | 同上（历史运行，`4091ca253`） | PASS（对照） | 21+38+51+253+97+31+128+626=1245；skip 28+22+7=57；总 1302 |
| 设计穷尽性 | 逐行对照 `02-motion.md:47-51` 与卡面 `:40` 三场景；`grep decorative doc/design/fluent-v1` | 同上 | PASS（名称/时长一致） | 设计仅三场景；`02:67-68` 的 §4 约束未被卡面覆盖 |
| 降级支点 | 读 `MotionResolver.cs:82-85`、`WindowsMotionPreferenceSource.cs:39`、`FluentShellSurface.axaml.cs:700` | 同上 | PASS | `decorative=!reduce&&flag`；系统关→`Reduce`；`motion-decorative` 类已挂 shell |
| 视觉采证可行性 | 读 `TestAppBuilder.cs:12`、`FluentPageTests.cs:244-308`、`NewManga.App/AssemblyInfo.cs:5`、`ManualFluentMotionClock.cs` | 同上 | PASS | headless+Skia `CaptureRenderedFrame` 已用于 Fluent 四页；`IFluentMotionClock` 可注入（`InternalsVisibleTo`） |
| 组件/状态事实 | 读 `Feedback.cs:11-40`、`:89-105`；`FluentComponents.cs:13-36`；`Status.cs:11-22`；`Themes/Controls/Button.axaml:44-57`；`FluentUi.cs:126-136` | 同上 | PASS | `EmptyState` 无图标/插画槽；`AlertBanner.Severity` 为九值 `StatusKind`；`FluentDialog` 无危险/加载；基础控件态在 `Themes/` |
| 矩阵/台账现状 | 读 `component-state-matrix.md:47-77`、`ac-coverage.md:26-42`、`current-evidence-index.md:1-31` | 同上 | PASS（记录冲突） | 旧表自述 1233「当前」，新索引声明其历史；R4-001 已由新索引处置 |
| build / 全量 test / 生成器 | 未执行 | 同上 | NOT_RUN | 本卡无实现增量；基线取自 canonical 集成日志并复算；重跑不改变范围判定。不得据此写「本轮已复跑」 |
| 原生视觉/DPI/a11y | 未执行 | B-5/D-1 | BLOCKED | 无硬件；不伪造 |

**证据纪律说明**：上表命令均实际执行；`check.ps1`/`verify_pins.ps1` 为只读（执行后 `git status` 仍为空）。本轮未产生可入库运行日志（scope 复核不改证据面）；报告内的输出摘要即实际结果。未将 NOT_RUN/BLOCKED 计 PASS。

## 结论与复审

**verdict = changes_requested（P0=0 / P1=5 / P2=6）。范围草案不可冻结。** 理由：IN-2 非逐格且混入端口/不存在状态（R2S-001/R2S-002）；IN-1 的视觉本体与验收语义不可判定（R2S-003/R2S-004/R2S-005）；写域与禁止语义未冻结（R2S-007/R2S-011）；承接与指针未对齐（R2S-008/R2S-009/R2S-010）。这些问题不改变 IN-1 的**方向**（三类 decorative 全部 IN 是正确的），只要求把「做什么/证据是什么/谁签署/写哪里」写死。

**可冻结缩减方案（最小返修集）**：

1. 按附录 A 重写卡面范围：IN-1.1…1.3、IN-2A（逐格）、IN-2B（像素格）、OUT、BLOCKED；BLOCKED 至少含 B-5/D-1 与全部数据端口格（B-1/B-2/B-3/B-6/B-7），逐项写恢复条件（端口 Task done + 契约冻结）。
2. 写死「最小确定性实现」与「视觉验收协议」：令牌/既有图标约束、真实帧源、失焦暂停、自动化全关、reduce 不创建动画对象、无泄漏、`IsHitTestVisible=false`、独立 Reviewer 逐图签署、未签署=NOT_RUN、不得以选择器存在计 PASS。
3. 冻结证据形式：默认运行零仓库写入；显式 opt-in 才写 `verification/FEA-06-RESIDUAL-2/visuals/**`；逐图元数据；旧 FEA-06 四 PNG SHA 对照（pin 值见附录 A）；日志带 shell/EXIT/逐条 skip；基线 1245/0/57 逐程序集、只增不减、禁止过滤口径替代。
4. 补禁止范围段；allowed_paths 二选一（收窄实现方式或显式扩域）。
5. 承接 R4-001（current-evidence-index 为权威、旧四表为历史）与 D-10（不重复实现；视觉复核二选一）。

**复审要求**：新 head 固定后由独立上下文复核，逐条给 R2S-001…011 disposition；范围若仍含不可达格或以声明计 PASS，不得 approved。**本 Review 不批准 D-8 在无视觉验收下的实施，也不批准把数据端口残项并入本卡。**

**推荐下一步**：Task=`FEA-06-RESIDUAL-2`，范围 v2 冻结处置，Agent=DSH；启动条件=接收本报告。Recovery point=`G:\CODEX\New Manga`、main、同一 worktree，base=`669a4ae02`，reviewed_head=`466fc98b3`。可直接转发给 DSH：

> 在 `G:\CODEX\New Manga` 的 main 接收 `doc/reviews/FEA-06-RESIDUAL-2-scope-r1.md`：**changes_requested，P0=0 / P1=5 / P2=6**。先核对 HEAD/工作树（应为 `466fc98b3`、干净）。按附录 A 把 FEA-06-RESIDUAL-2 范围改写为 v2：IN-1.1…1.3（三类 decorative，含真实帧源/失焦暂停/自动化全关/reduce 不创建动画对象/无泄漏/独立视觉签署）；IN-2A 逐格（17 组，headless 有效属性断言，不以选择器存在计 PASS）+ IN-2B 像素格；OUT（loading/Dialog 危险加载/CommandPalette loading）；BLOCKED（B-5/D-1 + BatchMatrix/RunProjectionBar/ReaderPage 双页滚动/RegionBox 冲突/满态统计/Console 投影，逐项写恢复条件，禁止越界 FEA-09…13）。补禁止范围段与测试要求表；allowed_paths 二选一（限定 Views/Fluent + Styles 内实现，或显式扩域 FluentUi.cs/Feedback.cs/Themes/Controls）。写死证据形式（默认零写入、opt-in 写 verification/FEA-06-RESIDUAL-2/visuals、逐图元数据、旧 FEA-06 四 PNG SHA 对照）与基线 1245/0/57 逐程序集。承接 R4-001（current-evidence-index 为当前权威，旧四表为历史）与 D-10（不重复实现，视觉复核二选一）；刷新 PLAN `:22`/`:39` 活文本段。范围 v2 冻结后再派 ZCode 实施，实施后由独立上下文 Reviewer 做视觉与实现复核；未冻结前不实施、不 push。

## 附录 A：建议冻结的逐格方案（可直接抄入 Task v2）

### A.1 IN-1（D-8 decorative，全部 IN，3 子项）

共同约束（写入每子项）：仅用既有令牌（`Nm.Color.Bg.*`、`Nm.Material.*`、`Nm.Opacity.*`、`Nm.Elevation.*`）与既有 `NmIcon`；不新增图片/字体/新颜色/新几何资产；装饰层 `IsHitTestVisible=false`、不触发重排、不遮挡内容；`reduce` / `auto`+系统关 / `category=关` 三态等价降级（书架=静态背景且不创建动画对象；粒子=不创建；漂浮=静态）；窗口失焦/不可见暂停；自动化开关可全关；detach 后停帧、无计时器/帧回调泄漏；真实播放以生产 `FluentRenderClock` 采样首/中/尾，`ManualFluentMotionClock` 只做边界断言。

| 子项 | 场景 | full/auto(系统开) | reduce / auto(系统关) / category-off | 断言 | 视觉证据 |
|---|---|---|---|---|---|
| IN-1.1 | 书架背景渐变 | 8s 循环 | 静态背景、不创建动画对象 | 时长=8s、循环、只改 Brush/Opacity；不重排；像素对比内容区无位移 | 3 张（full 首/中、reduce）+ 真实帧源采样 |
| IN-1.2 | 阅读器翻页装饰粒子 | 400ms（翻页触发一次） | 不创建粒子层 | 400ms 内结束、不拦截命中、不遮挡页面图、可读性断言通过 | 2 张（full 中帧、reduce） |
| IN-1.3 | 空态插画漂浮 | 6s 循环 | 静态插画 | 6s 循环、仅 Transform/Opacity；空态标题/提示/主按钮可点；`NmIcon` 派生 | 2 张（full 中帧、reduce）+ 交互断言 |

视觉签署：独立上下文 Reviewer（非实现者）逐图签署；未签署 = NOT_RUN；不得以「类/样式/动画对象存在」计 PASS。

### A.2 IN-2A（headless 有效属性断言，17 组；PASS=解析后属性等于设计令牌）

SurfaceCard（hover/selected/disabled）、BookCard（disabled）、BookRow（disabled）、PrimaryButton（disabled）、SecondaryButton（disabled）、DangerButton（disabled）、IconButton（hover/checked）、ToggleSwitch（disabled）、Slider（normal/hover/disabled）、SegmentedControl（selected/unselected/hover/pressed）、TabStrip/TabItem（hover）、SearchField（focus）、SettingsField（error/disabled）、RegionBox（hover）、ContextMenu（disabled item）、Tooltip（opened）、AlertBanner（按 DSH 裁定的枚举逐值；若按 `StatusKind` 九值，则 Blocked 已有断言、其余八值补齐）。

### A.3 IN-2B（像素 PNG + 视觉签署；每组件每状态 1 张，固定视口/主题）

IN-2A 全部组 × 状态 + EmptyState/ErrorState/Skeleton + ChapterList/PageThumbStrip + ReaderPage/ReaderProgressBar（单页 only）+ Dialog/Drawer 开合 + CommandPalette 空/结果；`reduce` 对照仅对 IN-1 三场景强制。像素格不得替代 A.2 的属性断言。

### A.4 OUT（不在本卡，须写理由）

PrimaryButton `loading`、Dialog 危险/加载（组件无变体，新增属功能/组件变更）、CommandPalette `loading`（无异步数据源，加假 loading = 假数据）、任何需要新增组件状态的项。

### A.5 BLOCKED（逐项写恢复条件）

| 格 | 阻塞 | 恢复条件 |
|---|---|---|
| BatchMatrix 七状态/吸顶表头 | FEA-10（B-2） | Run/批量端口 done + 契约冻结 |
| RunProjectionBar 投影态 | FEA-10（B-2） | 同上 |
| ReaderPage 双页第二图/滚动模式 | FEA-09/11（B-3） | 阅读器数据面端口 done |
| RegionBox 冲突态 | FEA-10（B-7） | 冲突投影端口 done |
| 书架满态统计 | FEA-12（B-6） | 真实统计数据面 |
| Console 投影/9 行数据 | FEA-10/12（B-1/B-2） | 对应端口 done |
| 完整 Tab 遍历、原生 a11y、200% DPI、原生桌面/截图 | B-5/D-1 | 硬件可用或用户书面 waiver |

### A.6 证据形式与 allowed_paths 建议

- 默认测试运行**零仓库写入**（`git status` 干净）；`NEWMANGA_CAPTURE_RESIDUAL2_PNGS=1`（名称可改，须唯一且显式）才写 `verification/FEA-06-RESIDUAL-2/visuals/**`；禁止写 `verification/FEA-06/**`。
- 逐图元数据：head、场景/组件/状态、mode（full/reduce/auto-关/category-关）、视口尺寸、帧位置（首/中/尾）、主题（light/dark）、生成命令与 EXIT。
- 旧 FEA-06 四 PNG SHA-256（与 pin 一致，作对照基线）：reader `8533c263c79bd53cefa68a21d2aabe6501556fd62218ebf653b528c9cbec78b2`；settings `fd30b166e30aec7a43e4d82ecd1fefb14dffef3bebe2f5f952e41d45e324a162`；shelf `307f8f6748522d1cdb3226135a3f733961744a3b2aa5d410f89aad3fde138b0a`；workbench `d5d878bbba9e47e2b59d9dd03816a370688a7afebec6d6e00016f262a46e2df5`。
- allowed_paths 保留现有；二选一：(a) 不加域 → 冻结「只在 `Views/Fluent/**` + `DesignSystem/Styles/**` 内以 Fluent 类包装/覆盖」，并把无法这样实现的格移 OUT；(b) 显式扩域 `apps/desktop-avalonia/src/NewManga.App/Controls/FluentUi.cs`、`apps/desktop-avalonia/src/NewManga.DesignSystem/Controls/Feedback.cs`、`apps/desktop-avalonia/src/NewManga.DesignSystem/Themes/Controls/**`（需 DSH 登记理由）。
- 验收命令建议：`dotnet build apps\desktop-avalonia\NewManga.sln --nologo`；`dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings --nologo`（无过滤，基线 1245/0/57 只增不减）；`NEWMANGA_CAPTURE_RESIDUAL2_PNGS=1` 同上（生成 PNG 后 `git status` 只允许 evidence 目录内新增）；TokenGen/ThemeGen `--check`；`check.ps1`；`verify_pins.ps1`；旧 PNG SHA 对照 + 禁止路径 diff。

## 附录 B：本报告实际执行的只读检查（输出摘要）

```text
HEAD=466fc98b33041c5828d33e41d02899723797f6ee
git status --porcelain=v1 = (empty)
git log --oneline -4 -- doc/tasks/FEA-06-RESIDUAL-2.md = 54c063405 (only)
git diff --stat 54c063405 HEAD -- doc/tasks/FEA-06-RESIDUAL-2.md doc/REBASELINE_PLAN.md doc/STATUS.md = (empty)
check.ps1 = PASS (3 warnings); CHECK_EXIT=0
verify_pins.ps1 = PIN AUDIT: PASS (all 15); PINS_EXIT=0
baseline = 21+38+51+253+97+31+128+626 = 1245 passed; 28+22+7 = 57 skipped; total 1302
```

报告落盘后，工作树唯一新增项应为 `doc/reviews/FEA-06-RESIDUAL-2-scope-r1.md`（untracked）；未 commit/push。
