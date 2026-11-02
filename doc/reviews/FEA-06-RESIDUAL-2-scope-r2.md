---
task_id: FEA-06-RESIDUAL-2
reviewer: DSH 独立子 agent（独立上下文 Scope Reviewer，scope-r2）
reviewer_kind: subagent
author: DSH（范围 v2 作者 / Lead）
base_commit: 669a4ae02bf8bf9d7dbdda01c4b2b9de71cb1431
reviewed_head: bff3eee662ebbf40b2f221b510cf68cf1431c015
decision: changes_requested
verdict: changes_requested
p0: 0
p1: 3
p2: 12
provenance:
  agent: DSH 独立子 agent
  dispatch: checkpoint §122（`doc/checkpoints/GOAL-PROGRESS-2026-11-02.md:799-804`，workflow job workflow-5e8f74838a2149cc）+ 用户本轮 scope-r2 复核指令
  implementation_participation: none
  subagents: none
  mode: read_only_review_except_this_report
  date: 2026-11-03
---

# Review：FEA-06-RESIDUAL-2 范围 v2（scope-r2）

**changes_requested：P0=0 / P1=3 / P2=12。** v2 的方向性重写基本成立：IN-1 三子项与 `02-motion.md:47-51` 同名同参数，共同约束覆盖了 `reduce` / `auto`+系统关 / `category=关` 降级、失焦暂停、自动化全关、无泄漏与真实帧源；IN-2A 从 v1 的一句「等」变为 17 组枚举；IN-2B / OUT / BLOCKED 分离，BLOCKED 补齐了数据端口格；证据形式写明默认零写入与 opt-in `visuals/**`；`allowed_paths` 给出收窄落点。**但范围仍不可冻结**：

1. **AlertBanner（IN-2A 第 17 组）仍是条件分支**——「按 DSH 裁定枚举」，两种裁定对应不同的组件状态集合与不同证据数，冻结文本不能把裁决留给实施期（R2R-001）；
2. **`allowed_paths 说明` 给了实现者单方面「移入 OUT」的阀门**，且 IN-1.3 与部分 IN-2A 格的可实现性未被证明（`EmptyState` 无图标槽、`FluentUi.Empty` 在写域外、TabItem hover 样式在 `Themes/Controls` 域外）（R2R-002）；
3. **「穷尽」声明不成立**——矩阵当前快照 `:55` 的 TopBand/NavRail/StatusBand 逐像素格未落入 IN/OUT/BLOCKED 任一分类，`:63` 的 StreamingThumb 未点名（R2R-003）。

其余 12 项 P2 中，5 项是 scope-r1 已列 P2 的未闭合（R2S-006/008/009/010/011 残项），7 项是 v2 自身的精确性或证据可复核性缺口。**本报告不批准在处置 3 项 P1 前冻结实施。**

## 范围与依据

被审对象：`doc/tasks/FEA-06-RESIDUAL-2.md` 在 `bff3eee66` 的全文（frontmatter `:1-32`、来源 `:36-39`、范围 v2 `:41-99`）。工作树干净，卡面仅 `bff3eee66` 一条 v2 改写提交（`git diff 54c063405 HEAD -- doc/tasks/FEA-06-RESIDUAL-2.md` 即 v2 增量），故 `reviewed_head` 字节与工作树一致；`base_commit` 取卡面 `:13` 的 `669a4ae02`（RESIDUAL-1 集成/证据 head）。

已读（只读）：

- scope-r1：`doc/reviews/FEA-06-RESIDUAL-2-scope-r1.md` 全文（R2S-001…011、附录 A/B）。
- 前序卡与证据：`doc/tasks/FEA-06-RESIDUAL-1.md:110-122`（AC1–AC5、禁止范围）、`:160-196`（Batch A/B、D-7/D-8/D-10/D-9、Closeout）；`verification/FEA-06-RESIDUAL-1/current-evidence-index.md`（`:4`、`:13`、`:15`、`:31`）；`component-state-matrix.md:45-78`（当前快照逐行）；`ac-coverage.md`；`integration-verification.log:17-24`（逐程序集）。
- 冻结设计：`02-motion.md:38-68`；`03-accessibility.md:42-64`；`10-component-inventory.md:1-66`；`05-page-shelf.md:29-50`；`06-page-workbench.md:44-45`；`07-page-reader.md:41`；`01-design-tokens.md:24-56`；`doc/design/redesign-v1/40-fusion/DESIGN_SYSTEM.md:176`。
- 代码支点：`Status.cs:11-22`；`Feedback.cs:11-40`；`App/Controls/FluentUi.cs:126-136`；`Themes/Controls/TabItem.axaml:44-60`；`Themes/Controls/Button.axaml:44-57`；`Styles/Controls.Selection.axaml:41-46`；`ViewModels/Fluent/MotionTimings.cs:13-57`；`TestAppBuilder.cs:12`；`FluentPageTests.cs:240-302`。
- 治理/指针：`doc/REBASELINE_PLAN.md:22`、`:36-39`；`doc/STATUS.md:7`、`:10`；`doc/templates/TASK.md:30-58`；`doc/templates/REVIEW.md`；`tools/governance/check.ps1`、`verify_pins.ps1`（只读运行）。

未审：任何实现（尚不存在）；原生 DPI/a11y/桌面（B-5/D-1 无硬件）；本轮未重跑 build/test（理由见「验证」），基线取自既有 canonical 集成日志并复算。本会话未参与该 Task 范围编制、实现或返修；唯一持久交付为本文件；未改源码/Task/证据/冻结设计，未 commit/push；落盘前 `git status --porcelain` 为空。

## 逐条核验（用户清单）

| # | 核验项 | 结论 | 依据 |
|---|---|---|---|
| 1 | IN-1 三子项的共同约束/降级/暂停/无泄漏/真实帧源/视觉签署 | **PARTIAL** | `:45` 共同约束、`:47-51` 三列降级、`:53` 视觉签署齐备；但暂停/全关/无泄漏/reduce 无不可见占位未落为断言与证据行（R2R-005） |
| 2 | IN-2A 17 组逐格 | **PARTIAL** | `:57` 逐组枚举；第 4 组 `PrimaryButton(disabled)` 已 EFFECTIVE（R2R-012），第 17 组仍条件化（R2R-001），期望令牌未冻结（R2R-013） |
| 3 | IN-2B 像素格 | **PARTIAL** | `:61` 给出组件集合与「每组件每状态 1 张」；未逐图命名/计数，未点名视口与主题，遗漏矩阵 `:55` 三组件（R2R-003、R2R-006、R2R-015） |
| 4 | OUT 理由 | **PASS（带注）** | `:64-65` 三项均写理由；`:65` 的「任何需新增组件状态/设计资产的项」是策略性兜底，须与 `:84` 的自助移出条款一并收紧（R2R-002） |
| 5 | BLOCKED 表 | **PARTIAL** | `:69-76` 六行含 B-1/B-2/B-3/B-6/B-7 与 B-5/D-1，逐项恢复条件；StreamingThumb 未点名（R2R-003） |
| 6 | 证据形式默认零写入 + opt-in visuals | **PASS** | `:79` 零写入 + `NEWMANGA_CAPTURE_RESIDUAL2_PNGS=1` + 禁写 `verification/FEA-06/**`；`:80` 逐图元数据 |
| 7 | allowed_paths 落点 | **FAIL** | `:83-84` 选收窄方案，但 `:84`「若某格无法在域内实现，移入 OUT 并在 Handoff 说明」= 实现者单方面缩范围（R2R-002） |
| 8 | D-10 承接 | **FAIL** | 卡面全文 0 次提及 D-10；`current-evidence-index.md:31` 仍记「ZCode 视觉复核保留」（R2R-008） |
| 9 | R4-001 承接 | **FAIL** | 卡面未写证据权威链（`current-evidence-index.md` 为当前入口、旧四表 1233/1213/1197 为历史、R4-001 已处置）（R2R-009） |
| 10 | PLAN 活文本滞后及 v2 外登记 | **FAIL** | PLAN `:22`/`:39` 仍停在 RESIDUAL-1 in_progress/1195；STATUS `:10` 仍写「无 READY 节点」与 `:7` 矛盾；`466fc98b3..HEAD` 对 PLAN/STATUS 为空，checkpoint §122 也未登记滞后（R2R-010） |
| 11 | 范围穷尽互斥 / 开放集合 | **PARTIAL** | 未发现「等」式开放枚举（全文仅「等价」「等于」，`Select-String '等'` 无列举式命中）；但 `:41` 的「穷尽」被 R2R-003 推翻，`:84` 与 `:65` 提供两条自助移出路径 |
| 12 | 是否混入数据端口格 | **PASS** | IN-1/IN-2A/IN-2B 无 FEA-09…13 数据端口格；BatchMatrix/RunProjectionBar/ReaderPage 双页/RegionBox 冲突/满态统计/Console 投影均在 BLOCKED |
| 13 | 视觉证据可复核 | **PARTIAL** | 独立上下文 Reviewer 逐图签署、未签署=NOT_RUN（`:53`）；但签署表格式/文件、视口尺寸、主题取值、IN-2B 适用范围未冻结（R2R-006） |
| 14 | 是否新增设计资产/颜色/组件 | **PASS（带注）** | `:39`、`:45`、`:65` 明文禁止；仅用既有 `NmIcon`；但 IN-1.3 仍用「插画」一词，与 `DESIGN_SYSTEM.md:176`「EmptyState…禁止插画」的口径未登记（R2R-004） |

## Architecture（scope 层，executed）

**分层方向正确**：IN-1/IN-2 均落在表现层（Fluent 视图、DesignSystem `Styles|Theming`、测试、本卡证据目录），`allowed_paths:21-31` 不含 Core/契约/schema/生成物/Current V2/组合根/`FrontendSelector`/FEA-07 seam，`evidence_dir` 已入域，符合 TASK 模板对 `allowed_paths` 的硬要求。数据端口未被混入 IN，BLOCKED 表逐项写了恢复条件——这是 v2 相对 v1 的实质进步。

**写域仍未冻结**：

- `:84` 的「若某格无法在域内实现，移入 OUT 并在 Handoff 说明」把缩范围权交给实现者，且不需要 DSH 登记；同句只对「扩域/改共享控件」要求 DSH 登记。冻结范围不得保留这种单向阀门（R2R-002）。
- 该阀门不是纯理论风险：IN-1.3 的自然落点 `EmptyState`（`Feedback.cs:11`，类注释明写 *No illustrations*）没有图标/插画槽，工厂 `App/Controls/FluentUi.cs:126` 在 `allowed_paths` 之外，而设计 `05-page-shelf.md:40` 要求空态含图标；IN-2A 的 `TabStrip/TabItem（hover）` 期望样式位于 `Themes/Controls/TabItem.axaml:52`（域外），`PrimaryButton` 类基础态在 `Themes/Controls/Button.axaml:44-57`（域外）。卡面既未证明这些格能在 `Views/Fluent/**` + `Styles|Theming` 内实现，也未在冻结时把它们移出 IN（R2R-002）。

**Architecture 结论**：分层与写域骨架可用；冻结前必须把「哪些格确需域外文件」在冻结时裁决（扩域或移 OUT），并删除实现期自助移出条款。

## Standards（可选视角，executed）

对照 `doc/templates/TASK.md`：v2 仍缺「禁止范围」独立节（`:40-42`）、「测试要求」表（`:44-48`）与 AC 清单节；`:97-99` 的「实现约束」只覆盖 FEA-07 seam/共享契约/Current V2/组合根/`FrontendSelector`/生成物/冻结设计，缺 Core/IPC/schema/共享 `KeyMap`/`IPresentation*`/真实 `%APPDATA%`/模拟数据的显式禁令，也未复刻 RESIDUAL-1 `:116-122` 的完整禁止范围（R2R-011）。验收段 `:86-95` 有命令但无「planned/NOT_RUN」测试要求表，实施后无法按模板登记逐项实际结果。

对照 `doc/templates/REVIEW.md` 证据纪律：v2 的基线只写总数 1245/0/57，未写逐程序集、未写「禁止过滤口径替代」、未写 57 skip 逐条原因、未要求测试日志带 shell/EXIT，也未写 RESIDUAL-1 的当前证据权威链（R2R-009）。`:78` 的「（R1-006 口径）」为误引：RESIDUAL-1 impl-r1 的 R1-006 是 `FluentShellSurface.axaml.cs` 的 `Appearance` 订阅泄漏（`FEA-06-RESIDUAL-1-impl-r1.md:61`），与证据形式无关；证据零写入/opt-in 口径实际来自 RESIDUAL-1 的 I-7（scope v3）与 R3-002。

对照 `AGENTS.md`「不得以声明/不可复现测试计 PASS」：v2 `:53` 明写「不得以类/样式/动画对象存在计 PASS」，方向正确；该禁则应同样覆盖 IN-2A 的「解析后属性」证据（属性断言本身不是声明，可接受，但需按 R2R-013 冻结期望值）。

治理与冻结 pin：`check.ps1` PASS（3 既有 warnings，CHECK_EXIT=0）；`verify_pins.ps1` PIN AUDIT PASS（15/15，PINS_EXIT=0）。

## Spec（executed）：scope-r1 findings 的 v2 处置

| r1 ID | r1 级别 | v2 处置 | 结论 | 去向 |
|---|---|---|---|---|
| R2S-001 | P1 | IN-2A 17 组枚举 + IN-2B + OUT + BLOCKED（含数据端口） | **大体闭合**；穷尽性仍有缺口 | R2R-003 |
| R2S-002 | P1 | `:57` 仍写「按 DSH 裁定枚举；若采用 `StatusKind` 九值…」 | **未闭合**：裁决分支留到冻结之后 | R2R-001 |
| R2S-003 | P1 | `:45` 既有令牌/`NmIcon`/禁新资产；`:51` 「`NmIcon` 派生」 | **部分闭合**：渐变停点与具体令牌、装饰时长入令牌表、插画口径未写 | R2R-004 |
| R2S-004 | P1 | `:45` 含三态降级/失焦暂停/自动化全关/detach 停帧/真实帧源 | **部分闭合**：要求未落为断言与证据行 | R2R-005、R2R-014 |
| R2S-005 | P1 | `:53` 独立签署、未签=NOT_RUN、禁以存在计 PASS | **大体闭合**：签署表格式与 IN-2B 适用范围未冻结 | R2R-006 |
| R2S-006 | P2 | 无空态分工文字 | **未处置** | R2R-007 |
| R2S-007 | P2 | `:83-84` 选收窄方案，但附实现期自助移出 | **部分闭合并引入新缺口** | R2R-002（升 P1） |
| R2S-008 | P2 | 卡面 0 次提及 D-10 | **未处置** | R2R-008 |
| R2S-009 | P2 | `:37`/`:95` 写 1245/0/57、只增不减；`evidence` 段写零写入/opt-in | **部分闭合**：权威链、逐程序集、禁过滤、skip、shell/EXIT 缺；引用误标 R1-006 | R2R-009 |
| R2S-010 | P2 | 未刷新 PLAN/STATUS，也未在卡外登记滞后 | **未处置** | R2R-010 |
| R2S-011 | P2 | `:97-99` 实现约束 + `:95` 不 push | **部分闭合**：无禁止范围节，禁令集合不完整，缺测试要求/AC 表 | R2R-011 |

**Spec 小结**：scope-r1 的 5 项 P1 中，2 项（R2S-003/004）已实质改善但未落到可判定断言，1 项（R2S-002）未闭合，1 项（R2S-007）以「实现期移出」替代冻结期裁决，只有 R2S-001/005 大体闭合；6 项 P2 中 4 项未处置、2 项部分闭合。v2 的改写是有效进展，但尚未达到「可冻结」标准。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| R2R-001 | P1 | `doc/tasks/FEA-06-RESIDUAL-2.md:57`、`:64-65`；`doc/design/fluent-v1/10-component-inventory.md:16`；`src/NewManga.DesignSystem/Controls/Status.cs:11-22` | IN-2A 第 17 组的验收对象仍是条件分支。设计写 Toast/InfoBar = info/warn/error/success 四态；实现 `AlertBanner.Severity` 为 `StatusKind` 九值（queued/running/done/failed/blocked/stale/skipped/notstarted/locked）。若裁「按设计四态」，组件不存在这四个 severity 值，新增值属组件变更，按卡面 `:65` 应走 v1.1 重冻结或 OUT；若裁「按 `StatusKind` 九值」，则除 Blocked 外要新增八组断言。两分支的范围与证据数不同，冻结文本不能留待裁。 | 读 `:57`；`10:16` 四态；`Status.cs:11-22` 九值；全文无其他 severity 枚举。 | 冻结时二选一并写死：推荐按实现枚举 `StatusKind` 九值，逐值点名（Blocked 已有断言，其余八值补齐），并把与设计 `10:16` 四态的偏差登记为新的 D 项；删除「按 DSH 裁定」。 | open |
| R2R-002 | P1 | `doc/tasks/FEA-06-RESIDUAL-2.md:84`、`:45`、`:51`；`App/Controls/FluentUi.cs:126`；`DesignSystem/Controls/Feedback.cs:11`；`Themes/Controls/TabItem.axaml:52`；`Themes/Controls/Button.axaml:44-57`；`05-page-shelf.md:40`；`DESIGN_SYSTEM.md:176` | `:84` 允许实现者把「无法在域内实现」的格自行移入 OUT 并只在 Handoff 说明——冻结范围被改成实现者可调的集合，且与「DSH 负责范围冻结/findings 处置」冲突。具体风险不是假设：IN-1.3 的空态落点 `EmptyState` 无图标/插画槽（类注释 *No illustrations*），工厂 `FluentUi.Empty` 在 `App/Controls`（域外），而设计 `05:40` 要求空态含图标；IN-2A `TabItem(hover)` 的期望样式在 `Themes/Controls`（域外），Button 基础态同样在 `Themes/Controls`（域外）。卡面未证明这些格可在 `Views/Fluent/**`+`Styles|Theming` 内实现，也未在冻结时点名移出。 | 逐行读 `:84`；`Feedback.cs:11`、`FluentUi.cs:126`；`TabItem.axaml:52`、`Button.axaml:44-57`；`05:40`；`DESIGN_SYSTEM.md:176`。 | 删除「移入 OUT 并在 Handoff 说明」；改为「若确无法域内实现 → 停止并交 DSH 裁决，不得自行改分类」。同时在冻结时二选一：(a) 显式扩域 `App/Controls/FluentUi.cs`、`DesignSystem/Controls/Feedback.cs`、`Themes/Controls/**` 并按 `:84` 自己要求登记理由；或 (b) 冻结 IN-1.3 只在 `Views/Fluent/**` 组合既有 `NmIcon`（点名页面/空态）并把只能改 `Themes/Controls` 的格在冻结时移 OUT。另登记「插画=既有图标」与 `DESIGN_SYSTEM.md:176` 的关系。 | open |
| R2R-003 | P1 | `doc/tasks/FEA-06-RESIDUAL-2.md:41`、`:61`、`:69-76`；`verification/FEA-06-RESIDUAL-1/component-state-matrix.md:55`、`:63` | 卡面 `:41` 声明「穷尽、互斥、可验证」，但矩阵当前快照 `:55` 的 TopBand/NavRail/StatusBand「逐像素视觉 NOT_RUN」不落在 IN-2A、IN-2B、OUT、BLOCKED 任一分类（卡面全文 0 次提及这三个组件）；`:63` 的 StreamingThumb 也未点名（BLOCKED 只写 BatchMatrix/RunProjectionBar 与语义不明的「Console 投影/9 行数据」）。I-4 视觉残项会静默丢失一行，冻结后的验收集合与卡面自述不一致。 | `Select-String` 卡面 `TopBand|NavRail|StatusBand|StreamingThumb` 无命中；矩阵 `:55`/`:63` 原文；设计 `10:10-12` 给出三组件状态，`:30` 给出 StreamingThumb。 | 补一张「矩阵当前快照行 → IN-2A/IN-2B/OUT/BLOCKED」映射表；把 TopBand/NavRail/StatusBand 像素格加入 IN-2B（固定视口），或在 OUT/BLOCKED 写理由；StreamingThumb 明确归 BLOCKED 并写恢复条件。映射表入卡面证据。 | open |
| R2R-004 | P2 | 卡面 `:45`、`:49`、`:51`；`02-motion.md:47-51`、`:65`；`05-page-shelf.md:40`；`10:17`；`Feedback.cs:11`；`DESIGN_SYSTEM.md:176`；`MotionTimings.cs:13-34` | R2S-003 残项：IN-1 的视觉本体只约束到「既有令牌 + `NmIcon`」，未点名书架渐变的停点/具体 `Nm.Color.Bg.*` 令牌；装饰时长 8s/400ms/6s 未要求进入 `MotionTimings`（该表当前只有 240/180/200/160/120/90/150，`MotionTimings.cs:16-34`），与设计 `02:65`「不得散落魔法数」有缺口；IN-1.3 仍称「插画」，与 `DESIGN_SYSTEM.md:176`「EmptyState…禁止插画」未登记口径；`05:40`（书架首空）与 `06:44`（工作台未选章节）都含图标，卡面未点名 2 张证据覆盖哪个空态。 | 读 `:45`/`:49`/`:51`、`02:47-51`/`:65`、`05:40`、`06:44`、`10:17`、`MotionTimings.cs:13-34`、`DESIGN_SYSTEM.md:176`。 | 点名渐变的 2–3 个停点及令牌；要求装饰时长常量进 `ViewModels/Fluent/MotionTimings.cs`（域内）；写「空态插画=既有图标」并记录与 `DESIGN_SYSTEM.md:176` 的关系；点名 IN-1.3 场景（建议书架首次空态，`05:40`）。 | open |
| R2R-005 | P2 | 卡面 `:45` 与 `:47-51`；`02-motion.md:57`、`:66-68` | R2S-004 残项：失焦暂停、自动化全关、无计时器/帧回调泄漏、`reduce` 不创建动画对象只写在共同约束，三子项的「断言」列没有对应行，证据段也未要求这些断言进入日志；「自动化可全关」未点名开关（复用哪个 env/设置）；设计 `:66`「`reduce` 下不保留不可见占位」未写入任一条。核心 AC（D-8 降级/暂停）因此缺少可判定的证据入口。 | 对照 `:45` 与 `:47-51` 三列；`02:57`、`:66-68`；证据段 `:79-81` 无对应字段。 | 在 `:47-51` 增加暂停、全关、无泄漏、无不可见占位四类断言行，并在证据段要求测试日志/用例名；点名全关开关（建议独立 env，如 `NEWMANGA_DISABLE_MOTION=1`）；补「`reduce` 不留不可见占位」。 | open |
| R2R-006 | P2 | 卡面 `:53`、`:59-61`、`:80` | R2S-005 残项：署名协议写在 A 节 IN-1 表之后，`:59` 标题虽写「像素 PNG + 视觉签署」，但未把「逐图签署、未签=NOT_RUN」明文套到 IN-2B；签署表格式/文件未冻结（r1 A.5 要求含图名/场景/mode/结论）；`:61` 只写「固定视口/主题」，未给具体视口与主题取值，视觉证据不可确定性复核。 | 读 `:53`、`:59-61`、`:80`。 | 把视觉签署协议提为独立小节并声明适用于 IN-1 与 IN-2B；冻结签署表路径与字段；点名视口尺寸与主题（light 必做、dark 可选或两者都做）。 | open |
| R2R-007 | P2 | 卡面 `:51`、`:61`；`component-state-matrix.md:59` | R2S-006 未处置：IN-1.3「空态插画漂浮」与 IN-2B「EmptyState 像素格」在空态上重叠，卡面未写分工——谁负责静态空态视觉、谁只负责漂浮、是否允许 IN-1.3 改文案/布局。可能重复认领或互相推诿，且实施时可能改动空态布局。 | 卡面两项均覆盖空态；矩阵 `:59` EmptyState 逐像素 NOT_RUN。 | 按 RESIDUAL-1 的 I-13/I-14 先例写分工：IN-1.3 只对「漂浮」负责且不改空态文案/布局；空态静态像素格归 IN-2B。 | open |
| R2R-008 | P2 | 卡面全文；`doc/tasks/FEA-06-RESIDUAL-1.md:192`；`current-evidence-index.md:31` | R2S-008 未处置：D-10 三项（浮层退出 160ms / pressed 90ms / badge 150ms）已由 Codex 交付，但当前证据索引仍记「ZCode 视觉复核保留」；本卡 owner 正是 ZCode 且是视觉残项卡，却 0 次提及 D-10，既可能重复实现，也可能让该视觉复核继续悬空。 | `Select-String` 卡面 `D-10` 0 命中；`RESIDUAL-1:192`；`index:31`。 | 二选一并写死：(a) 在本卡视觉验收集把三项列为只读证据行（不改码、不改既有断言，仅补签署）；(b) 明确转出并写 Owner/恢复条件。同时写「D-10 不重复实现」。 | open |
| R2R-009 | P2 | 卡面 `:37`、`:78-81`、`:95`；`current-evidence-index.md:4`、`:13`、`:15`、`:18-22`；`component-state-matrix.md:47`；`integration-verification.log:17-24` | R2S-009 残项：基线数字正确（`index:13` 1245；日志逐程序集 21+38+51+253+97+31+128+626=1245，skip 28+22+7=57），但卡面未写逐程序集、未写「禁止过滤口径替代」、未要求 57 skip 逐条原因、未要求测试日志带 shell/EXIT，也未写「RESIDUAL-1 当前证据权威=current-evidence-index；旧四表 1233/1213/1197 为历史；R4-001 已由该索引处置」。此外 `:78` 的「R1-006 口径」误引（R1-006=Appearance 订阅泄漏），正确来源应为 RESIDUAL-1 I-7/R3-002。 | 读卡面与三份证据；复算集成日志；`FEA-06-RESIDUAL-1-impl-r1.md:61`。 | 加「基线与权威」段：逐程序集、只增不减、禁止过滤、skip 逐条原因、日志 shell/EXIT、权威链与 R4-001 处置；把误引改为 I-7/R3-002。 | open |
| R2R-010 | P2 | `doc/REBASELINE_PLAN.md:22`、`:36-39`；`doc/STATUS.md:7`、`:10`；`doc/checkpoints/GOAL-PROGRESS-2026-11-02.md:799-804` | R2S-010 未处置：PLAN `:22` 仍把 RESIDUAL-1 写成 1195/0/57 与「I-4 剩余状态/审查待续」；`:39` 仍写「下一节点 FEA-06-RESIDUAL-1（in_progress…Batch B 待派）」，与同文件 `:36-37` READY RESIDUAL-2 矛盾；STATUS `:10` 仍写「无 READY 节点」，与 `:7` 的 RESIDUAL-2 `ready` 矛盾。`466fc98b3..HEAD` 对 PLAN/STATUS 为空，checkpoint §122 只记 v2 改写与 scope-r2 派发，未登记该滞后。 | 逐行读；`git diff --stat 466fc98b3 HEAD -- doc/REBASELINE_PLAN.md doc/STATUS.md` 为空。 | 冻结本卡时刷新 PLAN `:22`/`:39` 与 STATUS `:10`（历史段不动）；若本轮不刷新，在 checkpoint 登记滞后的原因、Owner 与刷新时点。 | open |
| R2R-011 | P2 | 卡面 `:97-99`、`:95`；`doc/templates/TASK.md:36-48`；`doc/tasks/FEA-06-RESIDUAL-1.md:116-122` | R2S-011 残项：无独立「禁止范围」节；`:98` 只列 FEA-07 seam/共享契约/Current V2/组合根/`FrontendSelector`/生成物/冻结设计，缺 Core/IPC/schema/共享 `KeyMap`/`IPresentation*`/真实 `%APPDATA%`/模拟数据；`:95` 只有「不 push」一句。模板要求的「测试要求」表与 AC 清单节也缺失。 | 读卡面与模板；对照 RESIDUAL-1 `:116-122`。 | 补「禁止范围」节（逐条路径/语义）与「测试要求」表（场景/命令/前提/planned/NOT_RUN/证据）与 AC 清单；保留现有实现约束。 | open |
| R2R-012 | P2 | 卡面 `:57`；`component-state-matrix.md:23`、`:66` | IN-2A 第 4 组 `PrimaryButton（disabled）` 不是残项：矩阵 `:23` 已把 disabled=Opacity.Disabled 且 `IsEffectivelyEnabled=false` 记为 EFFECTIVE，当前快照 `:66` 也把「禁用透明度及零命令」列为既有；该组剩余的是像素格（属 IN-2B）。把它计入 17 组会虚增残项集并可能重复/改写既有断言。 | 读矩阵 `:23`、`:66` 与卡面 `:57`。 | 从 IN-2A 删除该组（保留在 IN-2B 像素格），或明文标为「重断言」并说明理由；随后复核 17 组计数（与 R2R-001 的裁定联动）。 | open |
| R2R-013 | P2 | 卡面 `:55`、`:57`；`10-component-inventory.md:42-53`；`01-design-tokens.md:48-56`；`03-accessibility.md:57-64` | IN-2A 的 PASS 定义为「解析后属性等于设计令牌」，但冻结设计只给组件级令牌与状态名，未给逐状态期望值（如 SurfaceCard hover/selected/disabled、SegmentedControl hover/pressed、TabItem hover）；`01-design-tokens §2.3` 只是阴影层次。实施者必须自选期望令牌，测试会把实现选择固化成「设计令牌」，形成循环证据（与 D-8 暂缓理由同源）。 | 逐行对照 `10:42-53`、`01:48-56`、`03:57-64` 与卡面 `:55`/`:57`。 | DSH 在卡面或证据附录冻结「17 组 × 状态 → 期望令牌」表；或把 PASS 改为「解析值等于矩阵当前快照已登记的令牌」并要求同步更新矩阵。二者择一，不得留空由实现者自定。 | open |
| R2R-014 | P2 | 卡面 `:45-51`、`:39`；`03-accessibility.md:61-62` | IN-1 无高对比/对比度断言：`03 §4` 要求正文 ≥4.5:1、高对比下材质退化为不透明表面色、阴影→1px 边框；书架背景渐变是内容背后的大面积 Brush 改动，卡面只要求「只改 Brush/Opacity、不重排、内容区无位移」，未定义高对比下渐变如何处理、是否需对比度断言，也未给 IN-1.3 图标的对比度/图标规则。 | 读 `:45-51` 与 `03:61-62`。 | 增补高对比/对比度断言：渐变仅由令牌构成且在 HC 下退化为不透明表面或暂停；正文对比度断言或复用既有对比测试；IN-1.3 图标满足 `03 §4`/`§5` 图标规则。 | open |
| R2R-015 | P2 | 卡面 `:61`、`:80-81`；scope-r1 附录 A.6 | 证据自包含性不足：旧 PNG 只给 8 位前缀并写「完整值见 scope-r1 附录 A.6」，冻结验收值依赖另一份 Review 的字节；IN-2B 只写「每组件每状态 1 张」，未给逐图命名/计数，AlertBanner 分支（R2R-001）会改变图数，Reviewer 无法按清单核对缺图/多图。 | 读 `:61`、`:80-81`；`Get-FileHash verification/FEA-06/screens/*.png` 四值与附录 A.6 全值一致（reader `8533c263…78b2`、settings `fd30b166…a162`、shelf `307f8f67…8b0a`、workbench `d5d878bb…e2df`）。 | 内联四条完整 SHA-256（已复算匹配）；在卡面或证据附录给 IN-2B 图像清单（组件/状态/mode/主题/视口/文件名/期望张数）。 | open |

未发现 P0：本卡无数据/安全/契约风险；上述均为范围可判定性与写域纪律。

## 验证

环境：Windows，PowerShell Core（`pwsh -NoProfile`），仓库 `G:\CODEX\New Manga`，branch `main`，`reviewed_head=bff3eee66`。全部操作为只读检查；未 build/test（理由见下表），未写 PNG/证据，未 push。

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 固定被审字节 | `git rev-parse HEAD`；`git status --porcelain`；`git log --oneline -3 -- doc/tasks/FEA-06-RESIDUAL-2.md`；`git diff --stat 466fc98b3 HEAD`；`git diff 54c063405 HEAD -- doc/tasks/FEA-06-RESIDUAL-2.md` | `bff3eee66` | PASS | HEAD=bff3eee66；工作树空；卡面仅 `bff3eee66` 的 v2 改写；diff 仅含卡面/scope-r1/checkpoint 三文件 |
| 治理 | `pwsh -NoProfile -File tools\governance\check.ps1` | 同上 | PASS（3 既有 warnings） | `CHECK_EXIT=0`；warnings：9 非终态 Task、STATUS 80%、PLAN 80% |
| 冻结契约 pin | `pwsh -NoProfile -File tools\governance\verify_pins.ps1` | 同上 | PASS | `PINS_EXIT=0`；15/15 |
| 基线复算 | 逐行读 `integration-verification.log:17-24`；算术复核 | 同上（历史运行） | PASS（对照） | 21+38+51+253+97+31+128+626=1245；skip 28+22+7=57；总 1302 |
| 旧 PNG SHA | `Get-FileHash verification\FEA-06\screens\*.png -Algorithm SHA256` | 同上 | PASS | 四值与 scope-r1 A.6 全值一致 |
| 设计参数 | 读 `02-motion.md:38-68`；对照卡面 `:47-51` | 同上 | PASS | 三场景名称/时长一致（8s/400ms/6s）；§4 四条约束原文核对 |
| 矩阵穷尽性 | 读 `component-state-matrix.md:45-78`；`Select-String` 卡面 `TopBand|NavRail|StatusBand|StreamingThumb` | 同上 | FAIL | 卡面无命中；矩阵 `:55`/`:63` 的残项无归属（R2R-003） |
| Toast severity 三方 | 读 `10:16`、`Status.cs:11-22`、卡面 `:57` | 同上 | FAIL | 设计四态 vs `StatusKind` 九值 vs「按 DSH 裁定」（R2R-001） |
| 空态可实现性 | 读 `Feedback.cs:11-40`、`FluentUi.cs:126-136`、`05:40`、`DESIGN_SYSTEM.md:176` | 同上 | FAIL | `EmptyState` 无图标槽且注释 *No illustrations*；工厂在 `App/Controls` 域外（R2R-002） |
| 样式写域 | `Select-String` `Themes/Controls/*.axaml`、`Styles/*.axaml` 的 `pointerover|disabled` | 同上 | FAIL | TabItem hover=`Themes/Controls/TabItem.axaml:52`；Button disabled=`Themes/Controls/Button.axaml:51`（域外）；ToggleSwitch disabled=`Styles/Controls.Selection.axaml:45`（域内） |
| 装饰时长令牌 | 读 `ViewModels/Fluent/MotionTimings.cs:13-57` | 同上 | FAIL | 仅有 240/180/200/160/120/90/150ms，无 8s/400ms/6s（R2R-004） |
| 权威链 / D-10 | 读 `current-evidence-index.md:4`、`:13`、`:15`、`:31`；`Select-String` 卡面 `D-10|R4-001|current-evidence-index` | 同上 | FAIL | 0 命中（R2R-008、R2R-009） |
| PLAN/STATUS 滞后 | 读 `PLAN:22`、`:36-39`；`STATUS:7`、`:10`；`git diff 466fc98b3 HEAD --` 两文件 | 同上 | FAIL | diff 为空；PLAN `:39` in_progress 与 `:36` READY 矛盾；STATUS `:10`「无 READY 节点」与 `:7` 矛盾（R2R-010） |
| 开放集合 | `Select-String` 卡面 `等` | 同上 | PASS | 仅「等价」「等于」，无列举式「等」 |
| 模板对齐 | 读 `TASK.md:30-58`；对照卡面 `:97-99`、`:86-95` | 同上 | FAIL | 缺禁止范围节、测试要求表、AC 清单（R2R-011） |
| build / 全量 test / 生成器 | 未执行 | 同上 | NOT_RUN | 本卡无实现增量；基线取自 canonical 集成日志并复算；重跑不改变范围判定。不得据此写「本轮已复跑」 |
| 原生视觉/DPI/a11y | 未执行 | B-5/D-1 | BLOCKED | 无硬件；不伪造 |

**证据纪律说明**：上表命令均实际执行；治理与 pin 检查为只读（执行后 `git status` 仍为空）；报告落盘前工作树唯一新增项为本文件（untracked）。未将 NOT_RUN/BLOCKED 计 PASS。

## 结论与复审

**verdict = changes_requested（P0=0 / P1=3 / P2=12）。范围 v2 不可冻结。** 肯定进展：IN-1 三子项与设计参数对齐、降级/暂停/泄漏/真实帧源进入共同约束；IN-2A 由开放集合改为 17 组枚举；IN-2B/OUT/BLOCKED 分离且 BLOCKED 补齐数据端口；证据形式写明零写入与 opt-in；`allowed_paths` 有了明确落点。但三项 P1 决定「冻结后验收集合是否可判定」：AlertBanner 仍留待裁分支（R2R-001）；写域给了实现者单方面缩范围的阀门，且 IN-1.3/部分 IN-2A 格的域内可行性未证（R2R-002）；「穷尽」声明与矩阵当前快照矛盾（R2R-003）。因此**不得据文字自述放行**。

**必须修改项（冻结前）**：

1. **冻结 AlertBanner 口径**：二选一写死并逐值点名；推荐按 `StatusKind` 九值（Blocked 已有断言，其余八值补齐），把与设计 `10:16` 四态的偏差登记为新 D 项；删除「按 DSH 裁定」。
2. **关闭写域阀门**：删除 `:84` 的「移入 OUT 并在 Handoff 说明」，改为「无法域内实现 → 停止并交 DSH 裁决」；并在冻结时二选一：显式扩域（`FluentUi.cs`/`Feedback.cs`/`Themes/Controls/**`，登记理由）或点名把只能改 `Themes/Controls` 的格移 OUT；同时冻结 IN-1.3 的落点与「插画=既有图标」口径（`DESIGN_SYSTEM.md:176`）。
3. **补穷尽映射**：矩阵当前快照行 → IN-2A/IN-2B/OUT/BLOCKED 的映射表；TopBand/NavRail/StatusBand 像素格与 StreamingThumb 必须各有归属与理由。

**最小缩减方案（若 DSH 本轮只能做最小改动）**：先完成上述 3 项 P1；P2 至少修 R2R-004/005/006/007/008/009/010/011/012/013/014/015 中与冻结直接相关的 5 项——IN-1 断言与证据行（暂停/全关/泄漏/无占位）、签署表格式与视口主题、空态分工、D-10 只读行、基线权威链 + 逐程序集 + 禁过滤 + skip + shell/EXIT、PLAN `:22`/`:39` 与 STATUS `:10` 刷新（或登记推迟）。其余（17 组去重、期望令牌表、HC/对比度、SHA 内联与图像清单）可在冻结时并行补齐，但不得留白到实施期。

**复审要求**：新 head 固定后再次由独立上下文复核，逐条给 R2R-001…015 处置；范围若仍含不可达格、条件化验收对象或实现者自助移出条款，不得 approved。**本 Review 不批准 D-8 在无独立视觉签署下的实施，也不批准把数据端口残项并入本卡。**

**推荐下一步**：Task=`FEA-06-RESIDUAL-2`，范围 v2 返修（scope-r2 处置），Agent=DSH；启动条件=接收本报告。Recovery point=`G:\CODEX\New Manga`、main、同一 worktree，base=`669a4ae02`，reviewed_head=`bff3eee66`。可直接转发给 DSH：

> 在 `G:\CODEX\New Manga` 的 main 接收 `doc/reviews/FEA-06-RESIDUAL-2-scope-r2.md`：**changes_requested，P0=0 / P1=3 / P2=12**。先核对 HEAD/工作树（应为 `bff3eee66`、干净）。按 R2R-001 冻结 AlertBanner 枚举（推荐 `StatusKind` 九值并登记设计四态偏差），按 R2R-002 删除 `allowed_paths 说明` 里的实现期自助移 OUT 条款并在冻结时裁决扩域或点名移出（IN-1.3 落点、`Themes/Controls` 相关格），按 R2R-003 补「矩阵行 → IN/OUT/BLOCKED」映射并把 TopBand/NavRail/StatusBand、StreamingThumb 归类。随后处置 P2：IN-1 暂停/全关/泄漏/无占位断言与证据行、签署表格式与视口主题、IN-1.3 与 IN-2B 空态分工、D-10 只读证据行、基线权威链（`current-evidence-index` 为当前、旧四表为历史、逐程序集 1245/0/57、禁过滤、skip 逐条、shell/EXIT、修 R1-006 误引）、PLAN `:22`/`:39` 与 STATUS `:10` 刷新（或登记推迟）、补禁止范围/测试要求/AC 表、17 组去重（`PrimaryButton(disabled)` 已 EFFECTIVE）与期望令牌表、HC/对比度断言、内联 4×SHA 与 IN-2B 图像清单。返修后交 scope-r3 独立复核；未冻结前不实施、不 push。

## 附录 A：本报告实际执行的只读检查（输出摘要）

```text
HEAD=bff3eee662ebbf40b2f221b510cf68cf1431c015
git status --porcelain = (empty, before writing this report)
git diff --stat 466fc98b3 HEAD = 3 files (checkpoint +6, scope-r1 +198, task +79/-13)
git diff --stat 466fc98b3 HEAD -- doc/REBASELINE_PLAN.md doc/STATUS.md = (empty)
check.ps1 = PASS (3 warnings); CHECK_EXIT=0
verify_pins.ps1 = PIN AUDIT: PASS (all 15); PINS_EXIT=0
integration log: Appearance 21/0/0; Presentation 38/0/0; Host 51/28; ThemeEngine 253/0/0;
  DesignSystem 97/0/0; ApplicationCore 31/0/0; CoreClient 128/22; App 626/7
  => passed 1245, skipped 57, total 1302
old PNG SHA-256:
  reader    8533c263c79bd53cefa68a21d2aabe6501556fd62218ebf653b528c9cbec78b2
  settings  fd30b166e30aec7a43e4d82ecd1fefb14dffef3bebe2f5f952e41d45e324a162
  shelf     307f8f6748522d1cdb3226135a3f733961744a3b2aa5d410f89aad3fde138b0a
  workbench d5d878bbba9e47e2b59d9dd03816a370688a7afebec6d6e00016f262a46e2df5
card mentions: TopBand/NavRail/StatusBand/StreamingThumb = 0; D-10/R4-001/current-evidence-index = 0
PLAN:22 still RESIDUAL-1/1195; PLAN:39 still "下一节点 FEA-06-RESIDUAL-1（in_progress…Batch B 待派）"
STATUS:10 still "下一步：无 READY 节点" while STATUS:7 says RESIDUAL-2 ready
```

报告落盘后，工作树唯一新增项应为 `doc/reviews/FEA-06-RESIDUAL-2-scope-r2.md`（untracked）；未 commit/push。
