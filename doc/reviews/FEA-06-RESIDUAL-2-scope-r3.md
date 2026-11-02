---
task_id: FEA-06-RESIDUAL-2
reviewer: ZCode CLI（独立上下文 Scope Reviewer，scope-r3）
reviewer_kind: agent
author: DSH（范围 v3 作者 / Lead）
base_commit: 669a4ae02bf8bf9d7dbdda01c4b2b9de71cb1431
reviewed_head: b201d44893a010f61758e750e37505eb091161d8
decision: approved
verdict: approved
p0: 0
p1: 0
p2: 7
provenance:
  agent: ZCode CLI fresh session
  appointment: checkpoint §123（doc/checkpoints/GOAL-PROGRESS-2026-11-02.md，job pwsh-684b8fa3d43b4063）+ 用户本轮 scope-r3 复核指令
  implementation_participation: none
  subagents: none
  mode: read_only_review_except_this_report
  date: 2026-11-03
---

# Review：FEA-06-RESIDUAL-2 范围 v3（scope-r3）

**approved：P0=0 / P1=0 / P2=7。范围 v3 可冻结实施。** scope-r2 的 3 项 P1 全部实质闭合，且每项都经本轮抽查原文/代码证实，非据文字自述：

1. **R2R-001（AlertBanner）闭合**——D-11 按 `StatusKind` 九值写死（Blocked 已有断言 + Done/Failed/Queued/Running/Stale/Skipped/NotStarted/Locked 八值补齐），设计四态↔StatusKind 映射写入证据，不新增组件变体、不改 `Feedback.cs`。本轮核验：`Status.cs:11-22` 九值枚举、`Feedback.cs:92-94` `Severity: StatusKind`、`StatusCatalog` 对九值逐一给出 `ColorKey`/`MutedColorKey`（NotStarted→`Nm.Color.Text.Disabled`、Locked 复用 Blocked 键），**每个值都有确定性令牌来源，逐值断言可判定、不需要任何组件/颜色新增**。若反方向按设计四态（`10-component-inventory.md:16` info/warn/error/success），实现中不存在这四个 severity 值，新增即组件变更，按卡面规则必然 OUT/v1.1——D-11 是唯一能保留验收对象且不触发组件变更的选项。**接受**。
2. **R2R-002（写域阀门）闭合**——`:87` 删除实现期自助移 OUT，改为「不可行格必须报告 DSH 裁决，先停该格、不得自行改分类或扩域」；IN-1.3 OUT（D-12）理由经代码核验属实（`Feedback.cs:8-9` 类注释明写 *No illustrations (DESIGN_SYSTEM §6.5)*、无图标/插画槽；`FluentUi.cs:126-136` `Empty` 不构造任何图标；新增槽位=组件变更）；D-13 两项扩域理由经代码核验属实（TabItem hover 期望样式确在 `Themes/Controls/TabItem.axaml:52-57`，Button 基础态确在 `Themes/Controls/Button.axaml:44-54`）。**IN-2A 其余 14 组样式落点逐一核验全部在既有域内**（SurfaceCard/BookCard/BookRow/RegionBox/SettingsField→`Styles/Controls.Fluent.axaml`；Segmented/SearchField/Slider→`Styles/Controls.Custom.axaml`；ToggleSwitch→`Styles/Controls.Selection.axaml`；ContextMenu/Tooltip→`Styles/Controls.Navigation.axaml`；AlertBanner 样式→`Styles/Controls.Feedback.axaml`）；IN-1.1/1.2 落点（`Views/Fluent/**` + `FluentUi.cs` 装饰层工厂 + `ViewModels/Fluent/MotionTimings.cs`）均在 allowed_paths 内。**无不可行格**。
3. **R2R-003（分类完整性）基本闭合**——TopBand/NavRail/StatusBand→IN-2B 像素格、StreamingThumb→IN-2B（懒加载态静态占位、无假数据）、数据端口格（BatchMatrix/RunProjectionBar/RegionBox 冲突/满态/Console 投影）全在 BLOCKED 并写恢复条件；互斥成立、无开放集合（卡面 `Select-String '等'` 无列举式命中）、无数据端口混入 IN。**唯一微残：SettingsGroup 无归属**（见 R3R-002）。

r2 的「最小缩减方案」5 项 P2 中：签署表格式与视口主题（`visual-inventory.md` + 七字段）✓、空态分工（IN-1.3 OUT 化后问题消失）✓、基线权威链 + 逐程序集 + 禁过滤 + skip + shell/EXIT + 4×SHA 全值内联（本轮 `sha256sum` 复算四值逐一匹配）✓、IN-1 断言（AC-1 点名三态降级/暂停/无泄漏 + HC 附加 `:129`）✓、D-10 转出 ✓（`033c8b4b9` 经 `git show` 核验为 R1-001 三项动画交付）。

剩余 7 项 P2 均为文本精度或实施期待办，不使验收集合不可判定；其中最重的是 PLAN/STATUS 三处权威文本矛盾（R3R-001），**建议与冻结 commit 一并刷新**（见结论附条件）。

## 范围与依据

被审对象：`doc/tasks/FEA-06-RESIDUAL-2.md` 在 `b201d4489` 的全文（frontmatter `:1-34`、范围 v2 主体 `:36-102`、范围 v3 决议 `:104-139`）。工作树干净；`git diff --stat bff3eee66 b201d4489` 仅 5 文件（PLAN +2、STATUS +2、checkpoint +12、scope-r2 报告落盘 +192、Task v3 +53），v3 增量即卡面决议节与 frontmatter。`base_commit` 取卡面 `:13` 的 `669a4ae02`（RESIDUAL-1 集成/证据 head）。

已读（只读）：

- 前两轮 scope review：`doc/reviews/FEA-06-RESIDUAL-2-scope-r1.md`（R2S-001…011、附录 A）、`-scope-r2.md`（R2R-001…015、逐条核验表）。
- 前序卡与证据：`doc/tasks/FEA-06-RESIDUAL-1.md`（AC/禁止范围/Batch/D-7…D-10/Closeout）；`verification/FEA-06-RESIDUAL-1/current-evidence-index.md`（`:31` D-10 尾巴）、`component-state-matrix.md`（当前快照 `:45-78`）。
- 冻结设计：`02-motion.md`（§2.3 `:47-51`、§4 `:63-68`）、`03-accessibility.md`（§4 `:57-64`）、`10-component-inventory.md`（§1–§3）、`07-page-reader.md`。
- 代码支点：`Controls/Status.cs:11-102`、`Controls/Feedback.cs:8-80`、`App/Controls/FluentUi.cs`、`Themes/Controls/TabItem.axaml`、`Themes/Controls/Button.axaml`、`Styles/Controls.{Fluent,Custom,Selection,Navigation,Inputs}.axaml`（选择器逐类定位）、`ViewModels/Fluent/MotionTimings.cs:16-34`。
- 治理/指针：`doc/REBASELINE_PLAN.md:20-40`、`doc/STATUS.md:5-12`、`doc/templates/REVIEW.md`、`check.ps1`/`verify_pins.ps1`（只读运行）。

未审：任何实现（尚不存在）；原生 DPI/a11y/桌面（B-5/D-1 无硬件）；本轮未重跑 build/test（无实现增量，基线取 canonical 集成日志并经 r2 复算；重跑不改变范围判定）。本会话为独立上下文，未参与该 Task 范围编制、实现或返修；唯一持久交付为本文件；未改源码/Task/证据/冻结设计，未 commit/push；落盘前 `git status` 除本文件外无新增。

## 逐条核验（用户清单）

| # | 核验项 | 结论 | 依据 |
|---|---|---|---|
| 1 | R2R-001：D-11 StatusKind 九值是否可接受；若按设计四态是否应 OUT/v1.1 | **PASS** | `:59` 写死九值+映射入证据+不改 Feedback.cs；`Status.cs:11-22`/`StatusCatalog:76-101` 九值令牌键齐全可断言；设计四态在实现中不存在（severity 通道只有 `StatusKind`），按四态=新增组件变体=按 `:68` 必然 OUT/v1.1。**维持 D-11** |
| 2 | R2R-002：扩域登记与落点可行性；是否仍有不可行格 | **PASS** | `:25-26` 两项扩域带理由；`TabItem.axaml:52-57`/`Button.axaml:44-54` 核验属实；其余 14 组样式落点全在 `Styles/**` 域内（逐类 grep 定位）；IN-1.1/1.2 落点域内；`:87` 阀门已删。**无不可行格** |
| 3 | R2R-003：分类完整性表覆盖矩阵所有行且互斥；无开放集合/数据端口混入 | **PASS（带注）** | TopBand/NavRail/StatusBand `:115`、StreamingThumb `:116` 均有归属；E 表 `:70-79` 数据端口全 BLOCKED；互斥成立；`Select-String '等'` 无列举命中。**SettingsGroup 未点名**（R3R-002） |
| 4a | 逐状态期望令牌冻结方式 | **PASS（附条件）** | `:57`「逐格期望令牌表由实施 Handoff 冻结并逐行核对」偏离 r2 建议的二选一，但有独立 Reviewer 核对关卡且锚点客观存在（既有样式声明 DynamicResource 键 / StatusCatalog / 矩阵 EFFECTIVE 值）；条件见 R3R-007 |
| 4b | IN-1 高对比/对比度断言 | **PASS** | `:129` 高对比下装饰层仅用令牌且无对比度回退（03 §4 引用正确）；对比度/可读性断言写入证据 |
| 4c | IN-2B 逐图清单与签署表格式 | **PASS** | `:126` `visual-inventory.md`，字段=文件名/组件/状态/mode/视口/主题/帧位置，逐图签署；AC-3 `:138` 未签署=NOT_RUN |
| 4d | 证据日志格式 | **PASS** | `:128` shell/host、head、命令、逐程序集（含 1245/0/57 与 57 skip 原因）、EXIT、差值、禁过滤冒充全量；`:127` 4×SHA 全值内联（本轮复算匹配） |
| 4e | D-10/R4-001 权威链与 PLAN/STATUS 一致性 | **PARTIAL** | `:110` D-10/R4-001 转出且 `033c8b4b9` 核验属实；但 PLAN `:22`/`:39`/STATUS `:10` 三处 r2 点名滞后未刷新、checkpoint §123 未登记推迟（R3R-001）；D-10「ZCode 视觉复核保留」尾巴无 Owner（R3R-006） |
| 5 | 新增设计资产/越界数据端口/allowed_paths 一致性/AC 可判定性 | **PASS** | `:41`/`:47` 明文禁止新组件/颜色/资产，扩域仅样式令牌层（`:26`「不改控件行为」）；E 表全部 BLOCKED 无混入；allowed_paths `:21-33` 与 IN 落点一致；AC-1…4 `:136-139` 均有 MET 条件，BLOCKED 不写达成 |

## Architecture（scope 层，executed）

写域骨架完整冻结：扩域两项（`FluentUi.cs` 装饰层工厂、`Themes/Controls/**` 令牌覆盖）均带 DSH 登记理由且与 IN 落点一一对应；禁止范围节 `:131-132` 覆盖 Core/契约/schema/用户数据/生成物/冻结设计字节/组合根/`FrontendSelector`/Current V2/FEA-07 seam/真实 `%APPDATA%`/push，与 RESIDUAL-1 `:116-122` 先例对齐；测试要求 `:133` 含「只增不减、无过滤 ≥1245/0/57、PNG 默认零写入、双证据并独立签署、NOT_RUN 不得计 PASS」。数据端口格全部留在 BLOCKED（B-1/B-2/B-3/B-6/B-7 + B-5/D-1），恢复条件逐项写明。分层无越界。

## Spec（executed）：scope-r2 findings 的 v3 处置

| r2 ID | 级别 | v3 处置 | 结论 |
|---|---|---|---|
| R2R-001 | P1 | D-11 写死九值 + 映射入证据 + 不改 Feedback.cs | **闭合** |
| R2R-002 | P1 | D-12 IN-1.3 OUT + D-13 扩域两项 + `:87` 删除自助移出 | **闭合** |
| R2R-003 | P1 | 分类完整性表 `:112-123` + IN-2B 补 TopBand/NavRail/StatusBand/StreamingThumb | **闭合**（SettingsGroup 微残→R3R-002） |
| R2R-004 | P2 | IN-1.3 插画口径随 OUT 消失；渐变停点与 MotionTimings 常量仍未点名 | **部分**（→R3R-005） |
| R2R-005 | P2 | AC-1 `:136` 点名三态降级/暂停/无泄漏 + `:129` HC 附加；全关开关名未点名 | **大部分闭合**（→R3R-005） |
| R2R-006 | P2 | `:126` visual-inventory.md 七字段 + 逐图签署 | **闭合** |
| R2R-007 | P2 | IN-1.3 OUT 后空态只剩 IN-2B 一方 | **闭合** |
| R2R-008 | P2 | `:110` D-10 转出 + `033c8b4b9` 交付核验属实；视觉复核尾巴无归属 | **部分**（→R3R-006） |
| R2R-009 | P2 | `:127-128` 权威链/逐程序集/禁过滤/skip/EXIT/差值/SHA 全值；`:81` R1-006 误引未修 | **大部分闭合**（→R3R-003） |
| R2R-010 | P2 | PLAN `:37`/STATUS `:7` 已刷新；PLAN `:22`/`:39`/STATUS `:10` 未刷新、未登记推迟 | **部分**（→R3R-001） |
| R2R-011 | P2 | `:131-139` 禁止范围/测试要求/AC 表 | **闭合** |
| R2R-012 | P2 | 16 组保留 PrimaryButton(disabled)，未去重未标注重断言 | **未闭合**（→R3R-004） |
| R2R-013 | P2 | `:57` Handoff 冻结期望令牌表 + Reviewer 逐行核对 | **附条件接受**（→R3R-007） |
| R2R-014 | P2 | `:129` HC/对比度断言 | **闭合** |
| R2R-015 | P2 | `:126-127` 清单 + 4×SHA 全值内联（复算匹配） | **闭合** |

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复核证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| R3R-001 | P2 | `doc/REBASELINE_PLAN.md:22`、`:39`；`doc/STATUS.md:10` | r2 R2R-010 三处点名位置未刷新：PLAN `:22` RESIDUAL-1 表格行仍写「Batch B 收尾 `4388e50bb`…1195/0/57；I-4 剩余状态/审查待续」（终态实为 closed_with_limitations/impl-r4 approved/`669a4ae02`/1245）；PLAN `:39` DAG 行仍写「下一节点 FEA-06-RESIDUAL-1（in_progress…Batch B 待派）」与同文件 `:36-37` READY RESIDUAL-2 矛盾；STATUS `:10` 仍写「下一步：无 READY 节点」与 `:7` 同文件矛盾。v3 commit 声称「PLAN/STATUS 同步」但只改了 `:37`/`:7` 各一行；checkpoint §123 未登记推迟理由。权威指针自相矛盾，冻结实施后 Reality Check 会读到矛盾状态，且为 r1/r2 连续第三轮同类滞后。 | `git diff bff3eee66 b201d4489 -- doc/REBASELINE_PLAN.md doc/STATUS.md` 仅 2×1 行；逐行读 `:22`/`:39`/`:10` 现状 | 与冻结 commit 一并刷新三处活文本段（历史快照段不动）；若推迟须在 checkpoint 登记 Owner 与刷新时点 | open |
| R3R-002 | P2 | 卡面 `:112-123`；`component-state-matrix.md:65` | 分类完整性表未点名 **SettingsGroup**：矩阵当前快照 `:65` 合并行「SettingsGroup / SettingsField」的尚未覆盖格写「错误/disabled全部有效外观格NOT_RUN」，v3 只归了 SettingsField（IN-2A error/disabled），SettingsGroup 的外观格无 IN/OUT/BLOCKED 归属。设计 `10:35` 对 SettingsGroup 无状态枚举（仅卡片分组），实际缺口可能为空，但卡面自称「分类完整性（R2R-003 闭合）」而表漏一行，穷尽性声明仍有缝隙。 | 读矩阵 `:65` 与卡面分类表逐行比对；`10:35-36` 状态列 | 实施清单或在卡面补一行「SettingsGroup 无状态枚举（设计 `10:35`），外观由 SettingsField/IN-2B 组承载」或按实际残格归入 IN-2B | open |
| R3R-003 | P2 | 卡面 `:81` | 「证据形式（R1-006 口径）」为 r2 R2R-009 已指出的误引（R1-006 是 `FluentShellSurface.axaml.cs` 的 Appearance 订阅泄漏，见 `FEA-06-RESIDUAL-1-impl-r1.md:61`；零写入/opt-in 口径实际来源为 RESIDUAL-1 的 I-7 与 scope v3 R3-002）。v3 未修正，实施者回溯证据来源会被误导。 | 读 `:81` 与 r2 R2R-009 原文 | 改为「（I-7 / R3-002 口径）」；冻结 commit 一并处理 | open |
| R3R-004 | P2 | 卡面 `:57`、`:59` | 两处精度问题：(a) IN-2A 第 4 组 `PrimaryButton（disabled）` 在矩阵 `:23` 与当前快照 `:66` 均已登记 EFFECTIVE（`Opacity.Disabled` + `IsEffectivelyEnabled=false`），保留为待断言组=重复认领既有断言格，r2 R2R-012 建议删除或标「重断言」未执行；(b) `:57` 标题「按 R2R-002 收窄为 16 组」引用错位——R2R-002 是写域阀门项，计数收窄实际关联 R2R-012/D-11。在「只增不减」约束下风险为虚增与可能重复测试，不破坏验收。 | 读矩阵 `:23`/`:66` 与 `:57`/`:59`；r2 R2R-012 | Handoff 中将该组标注「重断言（矩阵已 EFFECTIVE，回归保护）」或移除；引用改为 R2R-012/D-11 | open |
| R3R-005 | P2 | 卡面 `:47`、`:49-52`；`MotionTimings.cs:16-34`；`02-motion.md:65` | (a) 装饰时长常量（8s/400ms）未明文要求进入 `ViewModels/Fluent/MotionTimings.cs`（当前仅有 240/180/200/160/120/90/150ms），与设计 `02:65`「不得散落魔法数」存在实施期落实缺口；(b)「自动化可全关」仍未点名开关名（r2 建议 env 如 `NEWMANGA_DISABLE_MOTION=1`）。AC-1 已把暂停/无泄漏列为 MET 条件，可判定性不受影响，但实施者可能以字面量散落时长。 | 读 `MotionTimings.cs:16-34` 与 `:47`/`:49` | 实施时令 8s/400ms 进 MotionTimings 常量并由 Reviewer 核对；全关开关名写入 Handoff（复用既有测试环境开关或新增独立 env） | open |
| R3R-006 | P2 | 卡面 `:110`；`current-evidence-index.md:31` | D-10「ZCode 视觉复核保留」尾巴处置不完整：v3 写明三项动画已交付（`033c8b4b9` 核验属实）且本卡不重复认领，但 r2 R2R-008 建议 (b) 要求「明确转出并写 Owner/恢复条件」——保留的视觉复核归属无人认领也无转出记录，与 RESIDUAL-1 证据索引 `:31` 的悬空记载互相停留。 | 读 `:110` 与 `current-evidence-index.md:31` | 二选一写死：本卡 IN-2B 视觉签署集把三项动画相关浮层/按钮/badge 帧位列为只读证据行；或明确转出并写 Owner（建议随 v1.1 视觉线） | open |
| R3R-007 | P2 | 卡面 `:57` | 期望令牌表冻结方式为「实施 Handoff 冻结并逐行核对」，偏离 r2 R2R-013 的二选一（卡面冻结 / 改为对照矩阵已登记令牌）。该路径可接受的前提是期望值不得由实现者自造——锚点客观存在（既有样式声明 `Themes/Controls/*.axaml`、`Styles/*.axaml` 的 DynamicResource 键、`StatusCatalog` 逐值 ColorKey、矩阵 EFFECTIVE 已登记值），Reviewer 核对时须验证锚点而非只对数值。缺此前提会回到 D-8 同源的循环证据风险。 | 对照 `:57`、TabItem.axaml:53/56、Button.axaml:52、StatusCatalog:76-101 | 在 Handoff 模板要求期望令牌逐格注明锚点（样式文件:行 或 StatusCatalog/矩阵条目）；impl Review 逐行核对锚点存在性 | open（附条件接受） |

未发现 P0/P1：无数据/安全/契约风险；3 项 P1 已闭合；上表均为文本精度、权威指针同步与实施期待办。

## 验证

环境：Windows，Git Bash（`bash`）+ `pwsh -NoProfile`（治理脚本），仓库 `G:\CODEX\New Manga`，branch `main`，`reviewed_head=b201d4489`。全部操作只读；未 build/test（无实现增量，理由同 r1/r2；基线 1245/0/57 为 canonical 集成日志值并经 r2 逐程序集复算）；未写 PNG/证据，未 push。

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 固定被审字节 | `git rev-parse HEAD`；`git status --porcelain`；`git diff --stat bff3eee66 b201d4489` | `b201d4489` | PASS | HEAD=b201d4489；工作树净（落盘前）；增量仅 5 文件（PLAN/STATUS/checkpoint/scope-r2/Task v3） |
| 治理 | `pwsh -NoProfile -File tools\governance\check.ps1` | 同上 | PASS（3 既有 warnings） | `CHECK_EXIT=0`；warnings 与 r1/r2 相同（9 非终态 Task、STATUS 80%、PLAN 80%） |
| 冻结契约 pin | `pwsh -NoProfile -File tools\governance\verify_pins.ps1` | 同上 | PASS | `PINS_EXIT=0`；15/15（C12/C13/C14/FEA01 等） |
| 旧 PNG SHA | `sha256sum verification/FEA-06/screens/*.png` | 同上 | PASS | 四值与卡面 `:127` 全值逐一匹配（reader `8533c263…78b2`、settings `fd30b166…a162`、shelf `307f8f67…8b0a`、workbench `d5d878bb…e2df5`） |
| D-10 交付核验 | `git show --stat 033c8b4b9` | 同上 | PASS | 「fix(fea-06-residual-1): R1-001 补齐退出与反馈动画及可控帧测试」：FluentFeedbackMotion/FluentFrameAnimation/FluentShellSurface + 420 行 FluentAnimationCompletionTests，与 `:110` 声称一致 |
| AlertBanner 三方事实 | 读 `Status.cs:11-102`、`Feedback.cs:89-105`、卡面 `:59` | 同上 | PASS | `StatusKind` 九值 + `StatusCatalog` 逐值 ColorKey/MutedColorKey；`Severity` 类型为 `StatusKind`；设计四态无实现对应（R2R-001 闭合判定成立） |
| 扩域落点事实 | 读 `Themes/Controls/TabItem.axaml:52-57`、`Button.axaml:44-54`；`ls Themes/Controls Styles` | 同上 | PASS | TabItem pointerover 与 Button pointerover/pressed/disabled 基础态确在 `Themes/Controls/**`；扩域理由属实 |
| IN-2A 全组样式落点 | `grep -rln` 逐类定位 surface-card/book-card/book-row/region-box/settings-field/segmented/search-field/slider/toggle-switch/context-menu/tooltip 于 `Styles/*.axaml` | 同上 | PASS | 其余 14 组全在 `Styles/**` 域内；无域外不可行格 |
| IN-1.3 OUT 理由 | 读 `Feedback.cs:8-40`、`FluentUi.cs:126-136` | 同上 | PASS | EmptyState 注释 *No illustrations*、仅 Title/Hint/ActionText；`Empty` 不构造图标；OUT/v1.1 理由成立 |
| 矩阵行比对 | 读 `component-state-matrix.md:45-78` 对照卡面 `:112-123` | 同上 | FAIL（1 格） | SettingsGroup 无归属（R3R-002）；TopBand/NavRail/StatusBand/StreamingThumb 等其余行全有归属 |
| PLAN/STATUS 一致性 | 读 `REBASELINE_PLAN.md:20-40`、`STATUS.md:5-12`；`git diff bff3eee66 b201d4489 --` 两文件 | 同上 | FAIL | 仅 `:37`/`:7` 刷新；PLAN `:22`/`:39`/STATUS `:10` 三处滞后仍在（R3R-001） |
| 开放集合 | `grep '等' doc/tasks/FEA-06-RESIDUAL-2.md` | 同上 | PASS | 仅「等价/等于」类命中，无列举式「等」 |
| build / 全量 test / 生成器 | 未执行 | 同上 | NOT_RUN | 本卡无实现增量；基线取 canonical 集成日志（r2 已逐程序集复算）。不得据此写「本轮已复跑」 |
| 原生视觉/DPI/a11y | 未执行 | B-5/D-1 | BLOCKED | 无硬件；不伪造 |

**证据纪律说明**：上表命令均实际执行；治理与 pin 脚本只读（执行后 `git status` 仍净）；未将 NOT_RUN/BLOCKED 计 PASS；报告落盘后工作树唯一新增项为本文件（untracked）。

## 结论与复审

**verdict = approved（P0=0 / P1=0 / P2=7）。范围 v3 可冻结实施。** 依据：r2 的 3 项 P1 全部闭合且经代码级抽查证实（非据卡面自述）——AlertBanner 验收对象已写死且逐值有确定性令牌来源；写域阀门已删、扩域登记与落点一一核实、无不可行格；分类完整性覆盖矩阵行（除 SettingsGroup 一格微残）。验收集合可判定：AC-1…4 均有 MET 条件，视觉证据有独立签署协议，基线/证据格式有禁过滤与全值 SHA 约束。

**批准附条件（冻结 commit 或实施 Handoff 内完成，不阻塞冻结）**：

1. **R3R-001**：与冻结 commit 一并刷新 PLAN `:22`/`:39` 与 STATUS `:10` 三处活文本（或在 checkpoint 登记推迟理由、Owner 与刷新时点）——这是 r1/r2 连续点名的同类滞后，第三轮仍未全闭。
2. **R3R-007**：期望令牌表在 Handoff 冻结时逐格注明锚点（样式文件:行 / `StatusCatalog` / 矩阵 EFFECTIVE 条目）；impl Review 逐行核对锚点存在性，禁止无锚自造期望值。
3. R3R-002/003/004/005/006 在实施期处置（SettingsGroup 归属一行、R1-006 误引修正、PrimaryButton(disabled) 标注重断言、8s/400ms 进 MotionTimings、D-10 视觉复核尾巴归属）。

**复审要求**：若冻结 commit 修改卡面字节（含上述附条件落实），由实施后 impl Review 一并核对；若 P2 处置引入新的范围变更（如 SettingsGroup 发现真实残格需入 IN），须回 DSH 裁决。本 Review 不批准任何数据端口格并入本卡，不批准无独立视觉签署的 D-8 计 MET。

**推荐下一步**：Task=`FEA-06-RESIDUAL-2`，范围 v3 冻结并派实施，Agent=DSH（冻结动作）→ ZCode（实施 Owner，卡面 `:9` 已定）；启动条件=DSH 接收本报告。Recovery point=`G:\CODEX\New Manga`、main、同一 worktree，base=`669a4ae02`，reviewed_head=`b201d4489`。可直接转发给 DSH：

> 在 `G:\CODEX\New Manga` 的 main 接收 `doc/reviews/FEA-06-RESIDUAL-2-scope-r3.md`：**approved，P0=0 / P1=0 / P2=7**（附条件）。先核对 HEAD/工作树（应为 `b201d4489`、干净）。冻结 commit 一并做三件事：①刷新 PLAN `:22`/`:39` 与 STATUS `:10` 三处活文本（R3R-001）；②在卡面或 Handoff 模板落实「期望令牌逐格锚点 + Reviewer 核对锚点」（R3R-007）；③顺手修 R3R-003（`:81` R1-006 误引改 I-7/R3-002）与 R3R-002（SettingsGroup 归属一行）。随后按 allowed_paths 派 ZCode 实施（Owner 已定），实施 Handoff 记 R3R-004/005/006 处置；实施后独立上下文 Reviewer 做视觉与实现复核（逐图签署，未签署=NOT_RUN）；未完成附条件 ①② 前不转 in_progress；全程不 push。

## 附录：本报告实际执行的只读检查（输出摘要）

```text
HEAD=b201d44893a010f61758e750e37505eb091161d8
git status --porcelain = (empty, before writing this report)
git diff --stat bff3eee66 b201d4489 = 5 files (PLAN +2/-2 line-count ~1, STATUS ~1, checkpoint +12,
  scope-r2 report +192, task v3 +53/-8)
check.ps1 = PASS (3 warnings); CHECK_EXIT=0
verify_pins.ps1 = PIN AUDIT: PASS (all 15); PINS_EXIT=0
sha256sum verification/FEA-06/screens/*.png:
  8533c263c79bd53cefa68a21d2aabe6501556fd62218ebf653b528c9cbec78b2  reader.png
  fd30b166e30aec7a43e4d82ecd1fefb14dffef3bebe2f5f952e41d45d324a162  settings.png
  307f8f6748522d1cdb3226135a3f733961744a3b2aa5d410f89aad3fde138b0a  shelf.png
  d5d878bbba9e47e2b59d9dd03816a370688a7afebec6d6e00016f262a46e2df5  workbench.png
  => 与卡面 :127 内联全值一致
git show --stat 033c8b4b9 = fix(fea-06-residual-1): R1-001 补齐退出与反馈动画及可控帧测试
  (FluentFeedbackMotion.cs +77 / FluentFrameAnimation.cs +84 / FluentShellSurface.axaml.cs +73 / tests +420)
StatusKind enum (Status.cs:11-22) = Queued/Running/Done/Failed/Blocked/Stale/Skipped/NotStarted/Locked
StatusCatalog.ColorKey covers all nine (Status.cs:76-101; NotStarted=Text.Disabled, Locked=Status.Blocked)
TabItem hover = Themes/Controls/TabItem.axaml:52-57 (pointerover Foreground=Text.Primary, Bg=Bg.Raised)
Button base states = Themes/Controls/Button.axaml:44-54 (pointerover/pressed/disabled)
Other 14 IN-2A groups -> Styles/Controls.{Fluent,Custom,Selection,Navigation}.axaml + Inputs.axaml (in-domain)
EmptyState (Feedback.cs:8-40) = Title/Hint/ActionText only, "No illustrations (DESIGN_SYSTEM §6.5)"
MotionTimings.cs:16-34 = 240/180/200/160/120/90/150ms only (no 8s/400ms constants yet)
PLAN:22 still "1195/0/57; I-4 剩余状态/审查待续"; PLAN:39 still "下一节点 FEA-06-RESIDUAL-1（in_progress…）"
STATUS:10 still "下一步：无 READY 节点" vs STATUS:7 RESIDUAL-2 ready
open-set grep '等' on task card = no enumerative hits
```

报告落盘后，工作树唯一新增项应为 `doc/reviews/FEA-06-RESIDUAL-2-scope-r3.md`（untracked）；未 commit/push。
