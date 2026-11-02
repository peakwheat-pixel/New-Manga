---
task_id: FEA-06-RESIDUAL-1
reviewer: Codex CLI（fresh independent scope review r2；model gpt-6.1-sol, reasoning effort high）
reviewer_kind: agent
author: DSH
base_commit: 82529a3d5864a39f362e414b67bca774d743f862
reviewed_head: 04d7c79e3
decision: changes_requested
counts:
  P0: 0
  P1: 3
  P2: 3
---

# FEA-06-RESIDUAL-1 scope-r2：范围 v2 冻结复核

## Reviewer 身份与来源

本报告由用户直接委派的 fresh Codex CLI 独立上下文产出，reviewer_kind=agent；未参与本卡范围编制、scope-r1、实现或返修。Appointment 来源为本次用户指令及被审 Task 的 Review Appointment（143–145 行）。报告署名按本次委派的格式记录。未派发子 agent，未进入其他 worktree，不承担范围作者、实现者或 DSH 的处置/集成权限。

唯一编写的仓库文件为本报告。未改代码、测试、Task、状态、设计、旧 Review 或 evidence pin；未 commit/push、未启动产品或访问真实 APPDATA。指定构建/测试使用既有工具的 bin/obj 与测试临时产物；未另存日志、创建 worktree 或修改测试配置。检查记录直接写在本报告中。

下文 Task 行号均指 `doc/tasks/FEA-06-RESIDUAL-1.md` 在 **04d7c79e39a75acc3dadefc663b87af89d3453a5** 的内容；其他文件行号也以该 head 为准。scope-r1 原报告保持原字节。

## 范围与 Reality Check

- 实际仓库 `G:\CODEX\New Manga`，branch=`main`，common directory=`.git`；HEAD=`04d7c79e39a75acc3dadefc663b87af89d3453a5`。起始 `git status --short` 为空。
- 已实跑用户指定的 `git rev-parse HEAD`、`git status --short`、`git log --oneline -8`、`git diff --stat 0e52c9daa..HEAD`、`git diff --name-only 0e52c9daa..HEAD`，均成功。diff 为 **5 files changed / 293 insertions / 54 deletions**，仅 `doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、当前 checkpoint、scope-r1 报告和本 Task，未改代码/测试/冻结设计。
- 最近八个提交依次为 `04d7c79e3`、`0e52c9daa`、`82529a3d5`、`cb1a4bede`、`527a7ec37`、`91de6a345`、`ebda36be9`、`563f248c7`。
- `base_commit` 可解析；`git diff --name-only 82529a3d5..04d7c79e3 -- apps/desktop-avalonia` 无输出。`b26840acd`、`aedc7251c` 均为 HEAD 祖先，FEA-06/07 代码依赖已在当前主仓。
- 已读取 AD-002 当前架构边界、STATUS、Plan 当前 DAG、Task、scope-r1、rolling checkpoint 最新处置、协作协议 §4/§5.1，以及本次指定的冻结设计与实际 Fluent/DesignSystem/测试代码。未扫描历史 verification；前序全量结果引用 scope-r1 已保存记录，不冒充本轮结果。

### 实跑记录与全量命令限制

| 命令 | EXIT | 结果 |
|---|---:|---|
| `dotnet build apps\desktop-avalonia\NewManga.sln --nologo` | 0 | PASS，0 warnings / 0 errors |
| 指定的无 filter 全量 `dotnet test ... --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings` | 未执行 | **NOT_RUN**：包含会无条件覆盖旧证据的 PNG 测试，与本轮唯一允许写报告的硬边界冲突 |
| `dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings --filter 'FullyQualifiedName!~FluentPages_RenderHeadlessPngEvidence'` | 0 | **1137 passed / 0 failed / 57 skipped；另排除 1 项**，不是全量 1138/0/57 |
| `dotnet run --project apps/desktop-avalonia/src/NewManga.DesignSystem/tools/NewManga.DesignSystem.TokenGen -- --check` | 0 | PASS，292 rows，生成物逐字节一致 |
| `dotnet run --project apps/desktop-avalonia/src/NewManga.ThemeEngine/tools/NewManga.ThemeEngine.ThemeGen -- --check` | 0 | PASS，generated theme artifacts up to date |
| `pwsh -NoProfile -File tools/governance/check.ps1` | 0 | PASS，3 warnings：9 个非终态 Task、STATUS/Plan 达 80% 预算 |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 0 | PASS，15/15 |

排除依据是 `tests/NewManga.App.Tests/FluentPageTests.cs:240–278`：该测试没有 opt-in，直接把四页 PNG 写到 `verification/FEA-06/screens/`，AppearanceStore 也指向旧 Task runtime。未为凑齐基线执行后再恢复文件。四张 PNG 的 `git hash-object` 与 `git rev-parse 04d7c79e3:<path>` 分别相等：shelf=`0bb73dd7…`、workbench=`dfc35e78…`、reader=`6a8acfbf…`、settings=`4607bc38…`；检查后工作区仍干净。

scope-r1 第 39–44 行保存的 **1138/0/57** 是同一应用代码的前序执行结果。本轮实跑只证明除上述 1 项外的回归通过，不能写“本轮全量通过”。这是审查证据限制，不是新代码回归，也不是单独的范围阻塞项。I-7 落地后应恢复安全的无 filter 全量验证。

| 程序集 | passed | failed | skipped |
|---|---:|---:|---:|
| Appearance | 21 | 0 | 0 |
| ApplicationCore | 31 | 0 | 0 |
| CoreClient | 128 | 0 | 22 |
| Host | 51 | 0 | 28 |
| DesignSystem | 87 | 0 | 0 |
| ThemeEngine | 253 | 0 | 0 |
| Presentation.Avalonia | 38 | 0 | 0 |
| App（排除 PNG 1 项） | 528 | 0 | 7 |
| 合计 | **1137** | **0** | **57** |

57 个 skip 的程序集分布、方法与 scope-r1 附录一致，直接原因仍为 `NEWMANGA_CORECLIENT_SIDECAR_DIR` 未设置，sidecar fixture 前置拒绝；CoreClient 的 `Support/SidecarFixture.cs:17,30–35` 与 Host 对应 fixture 可核对。它们未到真实 Core/Host 集成，不计 PASS。被 filter 排除的 PNG 用例不算第 58 个 skip。

## scope-r1 S-001…S-006 闭环表

| 原 finding | Verdict | v2 证据与剩余问题 |
|---|---|---|
| S-001 / P1：R-9 假阻塞 | **CLOSED（原问题）** | Task:64,81 已将 R-9 纳入 I-8，承认令牌存在；DS `Themes/Tokens.Global.axaml:16–21` 有 Elevation 与焦点键。不再以令牌缺失阻塞。I-8 新增的 reduce 阴影回退违背设计，另列 R2-003，不倒称原假阻塞仍在。 |
| S-002 / P1：IN 验收不可判定 | **PARTIAL，仍阻塞** | Task:74–83,110–114 增加了字段/断言，memento 生命周期、PNG、dirty 圆点更清晰。但 I-3 未覆盖保存离开及保存失败；I-5 用 full/reduced/disabled 代替设计模式，auto/分类开关优先级无明确判据；R-7 焦点环只剩泛称“焦点”。见 R2-001。 |
| S-003 / P1：IN/OUT 非穷尽互斥 | **PARTIAL，仍阻塞** | I-9/I-10、R-8a/8b 已拆；没有发现同一明确子 ID 直接同时列 IN 与 BLOCKED。但 D-1…D-5 仍混入真实 blocker 理由；R-4 警示本体、R-3 状态行的纯 UI 部分无唯一归属，不能据 10/6/5 个编号宣称穷尽。见 R2-002。 |
| S-004 / P2：写域过宽 | **PARTIAL，非阻塞** | Task:24–30 已移除整 App/Services/Shell 授权，118–120 明确禁止 FEA-07 seam 与影响 Current 的全局改动，实质改善。DS 三目录仍宽；且 `Styles/FluentUi.cs` 路径不存在，真实 helper 在 `Controls/FluentUi.cs`。见 R2-004。 |
| S-005 / P2：R-8 丢 PNG opt-in | **CLOSED** | Task:79–80,113 分别规定 I-6=1408 行拆分、I-7=显式 opt-in/禁止覆盖旧 pin，且均为必做，不再可随意“完成或转后续”。实际 VM 仍 1408 行，PNG 风险真实。实施时须保留非文件型行为断言。 |
| S-006 / P2：治理缺口 | **PARTIAL，非阻塞** | Task:11–13,126–145 已分本批依赖/未来承接，scope-r2 与 impl-r1 Appointment 有承载，canonical/resource pending 合理。但 Manifest:149 仍缺若干必列类别/NOT_APPLICABLE；Plan:22 仍把未来端口列为本卡依赖，STATUS:7/Plan:39 仍称 scope-r1 进行中。见 R2-005。 |

## IN / DEFERRED / BLOCKED 穷尽性与可行性

这里判定的是“能否冻结为可实施、可验收范围”，不是宣称新行为已实现。现存代码没有随文档提交变化。

| 子项 | 真实代码/设计差距 | 分类与可行性判断 |
|---|---|---|
| I-1 / R-1a | Shelf/Workbench 当前为缓存 view/VM，Shelf ScrollViewer 在 `ShelfPageView.cs:149–155`，Workbench 在 `WorkbenchPageView.cs:141–175`；现有缓存树有复用基础 | **IN 可行**。三字段及 same-run/new-window 默认已明确；设计 `04-layout-responsive.md:41–44` 要求跨页保留、不写业务数据，未要求本批将此 UI 状态落盘。不能误改 FEA-07 已独立落盘的窗口几何 memento。应在非默认选中/滚动且 layout 完成后断言，避免仅检查仍为同一对象。 |
| I-2 / R-1b | 现有详情/inspector 为固定布局，无完整用户折叠/恢复入口；冻结设计 04 §2/§3 有断点、栏位和主内容下限 | **IN 可行**。在 Fluent views 内处理即可；具体哪些栏位与断点需对照冻结设计固定到证据矩阵，不把手动折叠等同完成所有响应式规格。折叠须移出焦点序、恢复入口始终可达。 |
| I-3 / R-5a | `FluentShellSurface.axaml.cs:197–235` 当前直接导航，488–498 的 Esc 仅关 Shell 浮层/Reader；设置 VM 已有 SaveAsync/dirty 与唯一 Appearance 写者 | **IN 可行，验收未闭合**。设计 `08:75–77` 为保存/丢弃/取消；Task 只写确认丢弃/取消。必须固定保存失败留页留稿、嵌套对话框 Esc、重入导航，不能用新的退出协调器替换 FEA-07。 |
| I-4 / R-6 | DS `Styles/Controls.Fluent.axaml` 有部分按钮 hover/pressed/disabled；各组件状态不统一 | **IN 可行，存在验证弱点**。现有 DS 样式可局部补齐；“设计 01/04 的组件集”未准确引用实际清单 `10-component-inventory.md`。所有组件统一套 pressed 并不符合适用状态，须列 N/A 原因。见 R2-006。 |
| I-5 / R-7 motion | `FluentShellSurface.axaml.cs:509–515` 仅消费导航 enabled 与全局 reduced class；这不是三类实际动画覆盖 | **IN 技术可行，口径须修**。既有 MotionResolver/平台源可只读复用，UI 动画可在授权 Fluent/DS 路径增加。设计模式为 auto/full/reduce，disabled 是分类/测试关闭结果，不能新增持久化第四种模式或把 reduce 全部等同禁用。 |
| I-6 / R-8a | `FluentPageViewModels.cs` 实际 **1408 行**；四 VM 起点 68/431/863/1029，共享基类/枚举同文件 | **IN 可行**。VM glob 覆盖新增/移动，SDK csproj 默认纳入 C# 文件；无需改 sln/csproj。保持 `NewManga.App.ViewModels.Fluent` namespace、public API、Changed/订阅与异步生命周期；测试引用须同步，不能为了移动降低行为测试。行数目标尚未给数字，属实施前细化，不据此单列阻塞。 |
| I-7 / R-8b | FluentPageTests 默认写旧 PNG；DS `VisualEvidenceTests.cs:29–34,82–86,390–395` 默认另写临时 PNG | **IN 可行**。Task 的“默认全量不写任何 PNG”比只改 FluentPageTests 更广，须一并核对 DS 测试（已在授权测试目录）。正常渲染/颜色/状态断言留在内存执行，仅文件导出 opt-in；不得通过整项提前 return 维持表面通过数。 |
| I-8 / R-9 | Elevation 键真实存在；Fluent surface/dialog/settings 样式仍以 Hairline 边框表达 | **IN 可行，但冻结内容错误**。reduce 不撤阴影；只有高对比回退边框。仅验证 Views/V2 无 diff 不能证明 Current 无视觉变化，DS 全局样式仍可影响 Current。见 R2-003。 |
| I-9 / R-3b | VM:482 的 `HasUnsavedDraft`、1070 的 `IsDirty` 已存在，设计 `06-page-workbench.md:48` 明定标题圆点与底部文案 | **IN 可行，确实无新端口依赖**。绑定真实属性/PropertyChanged 即可；“等页面”宜替为准确页面及指示位置。保存/丢弃/取消、切换失败/回滚需测，不能另造 dirty 真值。 |
| I-10 / R-4b | ReaderPageView:70–104 已有上下条，无自动隐藏；事件/计时属于 view | **IN 可行，确实无新数据端口依赖**。必须按 `07:23` 的 2s、页面中部切换、reduce 直接显示/隐藏；`07:62` 宽屏浮动条常显可隐藏要与上下条区分，不能所有 bar 一刀切。隐藏控件退出 Tab 序，计时在离页/解绑时停止。 |
| D-1 / R-2 控制台入口 | `FluentShellSurface:284–294` 已可 NavigateSpace(Console)，Workbench:190–200 已有真实控制台占位并诚实披露未接 Run | **纯导航可 DEFERRED**，但 Task:91“入口导航依赖 Run 端口”不成立。实时日志关联部分才可 BLOCKED；不能把延后入口的预算决定写成技术阻塞。 |
| D-2 / R-2 满态统计 | Task:92 写需要真实统计数据面，同时又归“本卡可做” | 必须拆 UI 统计展示与缺失统计投影，说明哪些现有 Host 字段可用、哪些待 FEA-12；现在尚不能证明全部统计都依赖回收站。若确实缺端口，应 BLOCKED。 |
| D-3 / R-3 冲突对照 | Task:93 以冲突投影数据未落地为理由 | 未落地对照数据可 BLOCKED 到 FEA-10；已有冲突状态上的入口/呈现若可做而分批延期可 DEFERRED。当前未细分，不能据此生成假对照。 |
| D-4 / R-3 九状态 | Task:94 明写“数据驱动部分”，B-2 覆盖 Run/Batch 绑定 | 数据驱动与纯 UI 是不同子项；前者和 B-2 边界需明确，后者未进入 I/D/B 任一具体格。无证据支持全部九行视为已实现。 |
| D-5 / R-5 网络字段/错误部分态 | SettingsPageView:345–346 明说冻结 Profile 无超时/并发字段；435–450 已能消费 Error/ReadOnly，部分禁用原因也不都需新端口 | 缺字段是实际 blocker，不能与可实现错误/部分呈现一起笼统 DEFERRED 到 FEA-13。需分别列契约承接者/恢复条件与可用现有状态的呈现项。 |
| D-6 / R-4 源不可用恢复 | Task:96 仅登记“可交互恢复”；VM:891,977–1014 已有 IsSourceUnavailable/失败状态，ReaderView:134–147 只有通用错误/缺页卡 | 恢复真数据面可后续处理，但原 R-4 的“源不可用只读警示”本体未归类。警示与恢复动作须分开，不能假定有通用错误卡即满足设计 `07:46` 顶部警示/缺页及写进度保护。 |
| B-1 / R-2 回收站/扫描 | 恢复/删除与逐项真实进度依赖未接端口 | **BLOCKED 方向诚实**；按 FEA-12/10 分明每个数据责任和恢复条件，禁止模拟恢复/删除成功。 |
| B-2 / R-3 Run/Batch | 实际运行投影/暂停停止/BatchMatrix 真数据未就绪 | **BLOCKED 成立**；与 D-4 的数据驱动部分需消除语义重叠。状态样式本身不天然等于 Run 绑定。 |
| B-3 / R-4 双页/滚动 | 当前只有一个 Image，未完成第二图/滚动数据面 | **BLOCKED 可保留**到 FEA-09/11，I-10 只消费现有上下条，不依赖这些能力。恢复条件应写端口可调用且契约冻结/相应 Task 集成，不能仅写端口名称。 |
| B-4 / R-5 备份目录频率 | 当前仅既有备份包 surface，无目录/频率字段的授权扩展 | **BLOCKED 成立**到 FEA-13；不在本卡扩 schema。与 D-5 网络字段不能混为同一字段责任。 |
| B-5 / 原生验证 | FEA-07 原生双屏/DPI/a11y 证据受硬件限制；headless 不能证明真实屏幕阅读器行为 | **BLOCKED 成立**，保留原状态。表中“D-1（无硬件）”是历史硬件限制，与本卡 D-1 控制台编号重名，宜注明完整来源；waiver 不是实测 PASS。 |

**穷尽性结论：尚未成立。** 已列子项数量完整不等于原残项逐条完备。没有要求将所有 DEFERRED 本批实现；必须诚实分清“可做而延后”和“尚缺数据面”，保留未释放需求且不给它们记 MET。D 行已有后续 Task/时点，但未细分到子项责任；B 表虽有依赖名，B-3/B-4 的可恢复判据仍应具体化。

## allowed_paths / base_commit 核对

1. **base 可继续使用**：`82529a3d5864a39f362e414b67bca774d743f862` 包含前序 closeout；其后到被审 head 无应用代码变化。范围复审绑定新文档 head 即可，不能因为文档提交较新就虚构代码 base 失效。实施前仍需重新 Reality Check。
2. **App 主路径足够覆盖基本实现**：Views/Fluent 与 ViewModels/Fluent glob 覆盖 R-1/R-2 UI、R-4 工具条、R-5 导航/Esc、R-8 VM 新增移动；测试路径覆盖 App 与 DS。未发现本批必须改组合根、共享 KeyMap、IPresentation*、FEA-07 协调器或 schema 的证据。
3. **FluentUi 路径笔误是真实问题**：Task:27 允许 `NewManga.App/Styles/FluentUi.cs`，但实际为 `NewManga.App/Controls/FluentUi.cs:10`，不被当前两个 Fluent glob 覆盖。不得为使用错误 allowlist 新建同名第二 helper。DS `Controls/FluentComponents.cs` 也未授权；其既有 surface/IsOpen 语义可复用，样式与页内行为可在现有写域完成，所以不据此认定必须放开整个 Controls。
4. **DS 写域仍应按必要文件收敛**：Styles/Controls.Fluent.axaml、Theming/FocusRing.cs 或新的 Fluent opt-in helper 是可讨论的目标；整 Accessibility/Styles/Theming 包含全局主题资源管理。Task:118–120 的语义禁改约束有效，不能把 glob 当成重写 DesignSystemThemeManager 或全局焦点的授权。共享行为如确需改动，按原卡先交 DSH。
5. **Current 保护必须是行为验证**：Current 页面源码无 diff 只是静态条件。新增 Fluent selector/attached behavior 需按 frontend+visualTheme 正确激活，并在同一进程切回 Current 后检查有效资源/焦点环/动画不被污染，尤其不能只依赖全局 SetReducedMotion。
6. evidence/Handoff/Review 写域已列；STATUS/Plan/LEDGER 在 allowlist 不代表 Owner 获得 DSH 生命周期权。Canonical/closeout 在 ready 阶段 pending 正确，不能预填完成。

## AC 判定口径

AC1–AC5 可以作为第一批关闭骨架，但当前文字仍不足以冻结。以下是需由 DSH 写实的最低判据，不是 Reviewer 自行释放新范围。

| AC | 可判定部分 | 必须补齐/实施证据 |
|---|---|---|
| AC1 | I-1 两种往返/三字段/新窗口默认；I-2 折叠键盘；I-9 dirty；I-10 超时唤醒 | 具体栏位与冻结断点；Reader 上下条/浮动条、2s、中部点击及隐藏 Tab 序；DEFERRED/BLOCKED 完整原残项映射。IN 完成不代表原 FEA-06 AC1–AC7 全 MET。 |
| AC2 | 组件功能状态、motion 需矩阵已明确 | 引用 10 的实际组件/适用状态；R-7 普通 2px/offset1/高对比3px、焦点移入/回还、隐藏不可聚焦；motion auto/full/reduce+系统开/关+分类关闭+旧值迁移，验证真实动画消费。 |
| AC3 | dirty→离开、取消留稿、丢弃、退出保护 | 保存成功才离开、失败/只读/取消留旧页旧稿；内层 Esc 只关当前浮层，外层取消编辑；枚举返回/空间切换/Reader 等入口与连续导航处理。必须与设计 08 §5 对齐。 |
| AC4 | 拆分与 PNG 分列，现有 Elevation 可用 | 拆分保留 namespace/API/订阅和既有测试；默认不导出 PNG 但继续真实渲染断言；opt-in 输出本卡或临时目录；reduce 阴影不变，高对比回退，Current 有效视觉对照。 |
| AC5 | 1138/0/57 起点、两生成器、治理/pins、临时根 | 基线 1138 是既有集合，新增测试另计；禁止减少覆盖/无理由增加 skip。固定 delivery head、逐项证据与 hash、实际 FEA-07 方法/矩阵、独立 impl Review 与 DSH 集成验证；不能以总数替代行为判别。 |

FEA-07 最低非回归集合应保留实际测试语义：`PresentationHostCompositionTests.RealContentRoundTrips_KeepOneStableWindowAndTheirState`、隐藏 production tree/ThemeStudio draft 阻断关闭；`PresentationWindowTests` 的 staging 不可交互、Loaded/layout 失败回滚、promote 后失败/取消全屏补偿、排队拒绝不恢复过期窗口模式；`PresentationInputRoutingTests` 的仅已提交树接收输入；`SettingsDraftSyncTests` 的 frontend-only 合并/重复通知/切换回滚不清 dirty draft。结合既有 Workbench Draft save/discard 与 Reader progress 测试，不弱化断言。

本轮这些程序集通过不证明新增 I 项达成。无 filter 1138/0/57 本轮 NOT_RUN 的原因已经披露，不能拿前序数字替代新实现交付验证。原生矩阵仍 BLOCKED。

## 风险与实施顺序

- **I-4 hover/pressed**：v2 如实承认只做 selector 存在性+设计核对，没有冒充原生视觉通过，这是改善。但存在性不能验证 selector 匹配、优先级、模板部件或最终 brush；headless 可验证有效属性与交互。至少用真实输入/伪类驱动断言有效值；无法可靠驱动的格写 NOT_RUN/静态核对及限制，不泛化为“headless 都不可测”。
- **I-5 motion**：可以通过注入系统偏好、可控时钟与检查实际 Animation/Transition 验证；full 必须覆盖系统关，auto 跟随系统，reduce 导航为 0、反馈不缩放/抖动、decorative 不创建/停止；分类关闭相互独立，旧值迁移后反馈颜色过渡也为 0。只验 MotionResolver/class 或“每类至少一个断言”不能覆盖这些结果。离页/解绑/不可见/失焦后不能留循环。
- **I-1 内存 memento**：与本批跨页/同运行期消费缓存树一致，无需新增持久化。不要混同窗口 geometry 或 Core reading_progress；不要为恢复滚动重载业务数据并清掉人工草稿。
- **I-6 拆分**：纯移动最好先独立提交，保留 namespace/测试引用、public API 与通知语义，再做 UI 逻辑。Task:85 同时写每批一个 delivery commit、I-6 可并行，单 Agent 实施时应解释为独立可追溯阶段，不必引入并行 Agent。
- **I-9/I-10**：已有 dirty 属性和 Reader 条控件足以支撑；不需要 FEA-10 或 FEA-09/11 先落地，也不能借机生成真实 Run/第二页假数据。

建议顺序：DSH 修订并冻结范围/验收 → I-6 纯移动基线 → Batch A 的状态/确认/工具条与 dirty 指示 → I-7 安全采证 → Batch B 的组件/焦点/motion/Elevation → 固定交付 head、无 filter 全量及 FEA-07 矩阵 → fresh 独立 impl Review → DSH 集成/资源核销。单 Codex 实现 Agent 在上述范围澄清后具备可行路径；当前 P1 未消除前，不能直接宣布 Batch A/B 可按 v2 完成冻结验收。

## Findings

以下为 6 个独立计数项，均 open，处置交 DSH；前文重复说明不另计。P2 可作为实施期处置项，不单独阻塞冻结；三项 P1 必须先修订范围文档。

| ID | 级别 | 证据（04d7c79e3） | 问题与影响 | 最小建议 |
|---|---|---|---|---|
| R2-001 | **P1** | Task:76–78,110–112；设计 `08-page-settings.md:75–77,93`、`02-motion.md:10–18,53–68`、`03-accessibility.md:42–62`；ShellSurface:488–515 | **S-002 未闭环。** I-3 的确认只有丢弃/取消，遗漏冻结设计保存分支/失败保护；I-5 将 auto/full/reduce 简化成 full/reduced/disabled，未固定系统优先级与分类关；R-7 ring 没有明确子项/几何和焦点恢复判据。交付部分行为即可字面通过 AC2/3，不能确定冻结目标。 | 对齐三分支及失败留稿/导航/Esc 优先级；明确 mode 与解析状态区别，冻结设计02的实际消费矩阵；明确 R-7 headless ring 的 IN 归属及 2/1/3px、隐藏/浮层焦点断言。若有意延期须逐项诚实登记，不暗改设计。 |
| R2-002 | **P1** | Task:58–60,68,91–106；ShellSurface:284–294；SettingsPageView:345–346,435–450；VM:891,977–1014；Reader 设计:46 | **S-003 未闭环。** D-1 的入口存在可用导航却写端口依赖；D-2…D-5 的“可做”分类与缺数据理由矛盾；D-4 只覆盖数据驱动部分、D-6 只覆盖恢复动作，漏掉纯状态 UI/源不可用警示本体。关闭时无法唯一追踪剩余义务。 | 原残项逐子项映射：能做而延期保留 DEFERRED+责任 Task/时点；真缺字段/投影转 BLOCKED+恢复条件；为 Reader 警示和九状态纯 UI 定唯一归属；D-4/B-2 仅保留一个数据绑定归属。无需为解决此 finding 扩大本批实现。 |
| R2-003 | **P1** | Task:46,81,118,121；`01-design-tokens.md:48–56`、`03-accessibility.md:62`；DS Tokens.Global:16–18 | **I-8 引入与 FROZEN 基线相反的验收。** 要求“高对比/减弱模式下回退1px边框”，冻结设计却明确 reduce 阴影不变。按 Task 实现会违反禁止改变设计的要求。 | 删除 reduce/减弱回退条件；仅高对比退边框，增加 standard+reduce 阴影仍为原令牌的断言，保留 Current 对照。若确需改设计须另走 DSH/设计重冻结，不属于本批。 |
| R2-004 | **P2** | Task:27–30,118–120；实际 `App/Controls/FluentUi.cs:10`；DS `Controls/FluentComponents.cs`、`Styles/Focus.axaml` | 写域虽已明显收窄，仍含全局 DS 整目录；显式 helper 路径错误且真正 helper 未覆盖，容易建立第二 helper 或越界。 | DSH 将错误路径纠正为必要的真实 helper；限定必要 Fluent 样式/opt-in 文件或明确逐文件停等规则；继续禁止影响 Current 的全局修改。现有视图/样式路径可完成基本方案，不据此要求开放整个 Controls/Services。 |
| R2-005 | **P2** | Task:10–13,143–159；Plan:22,39；STATUS:7,10；协作协议 §4.2 | Appointment/依赖/pending 已有骨架，但 Plan 仍混未来依赖、当前状态摘要仍指 r1；Manifest 未逐类登记 task-env、dataset/model/test-material、temp、agent-output、exchange 等适用性。恢复与关闭资源口径不完整。 | DSH 更新当前指针与本批/未来依赖区分；补完整 Manifest，每类填当前状态或 NOT_APPLICABLE，实施产生资源后再补实路径；保留 canonical/closeout pending。不得改写历史 checkpoint/Review 来消除旧状态。 |
| R2-006 | **P2** | Task:77,111；设计 `10-component-inventory.md` §1–3；DS `Styles/Controls.Fluent.axaml` | I-4 披露验证限制是诚实的，但 selector 存在可在不匹配/被覆盖时仍通过；按01/04泛称组件集，也不能确定各控件适用状态。 | 实施期先固化真实组件×适用状态表；关键 hover/pressed 断言有效 Background/BorderBrush/Opacity/Transform 与资源引用，disabled 验命令零触发，浮层验焦点移入回还；无法验证的视觉格明确 NOT_RUN，不以字符串存在计视觉 PASS。 |

## 结论、最小返修集与交接

**Decision：changes_requested；P0=0 / P1=3 / P2=3。范围 v2 当前不可冻结实施。** 原 S-001/S-005 已闭环，S-002/S-003 仍有 P1 缺口；S-004/S-006 部分闭环并保留为 P2。新增 I-8 reduce 阴影规则与冻结设计冲突。未发现需要等待全部未来端口才能实施纯 UI 的依据；问题是范围与验收口径，不是要求先写实现或新增设计。

最小返修集：①补齐设置三分支、motion 正确模式/优先级/分类矩阵与 R-7 焦点环明确判据；②修正 DEFERRED/BLOCKED 的事实分类和漏项、消除数据绑定重复归属；③恢复 I-8“reduce 阴影不变”的冻结设计口径。P2 在 DSH 处置/实施记录中逐项跟踪；无须先清偿未来端口或原生硬件限制才能复审。

推荐下一步：**DSH 处理本轮 findings，固定范围 v3 文档 head，再 Appointment fresh Codex CLI 做 scope-r3；本会话不参与返修或实现。** 这是下一步建议，不代替 DSH 任务释放。可直接转发：

> Task：FEA-06-RESIDUAL-1 scope-r2 处置与范围 v3；Agent：DSH（Lead/范围作者）。Recovery point：`G:\CODEX\New Manga`，main 主仓，common `.git`，base=`82529a3d5864a39f362e414b67bca774d743f862`，被审 head=`04d7c79e39a75acc3dadefc663b87af89d3453a5`。先 Reality Check，保留 scope-r1/r2 原字节。仅在已有治理授权内修改本 Task、当前 STATUS/Plan/rolling checkpoint 与处置/Handoff 文档；不改代码/测试、契约/schema、生成物、冻结设计、Current V2、用户数据及旧证据，不 push。交付逐 R2-001…006 disposition、范围 v3 精确文档 head、修订后的 I/D/B 映射/AC 和 scope-r3 Appointment。优先修三项 P1：设置保存/丢弃/取消与失败保护、auto/full/reduce 与分类/系统矩阵及焦点环判据；残项穷尽互斥/真实依赖分类；I-8 reduce 保留阴影。P2 修正 helper 路径、当前指针/Manifest，安排组件有效视觉属性验证。运行 `pwsh -NoProfile -File tools/governance/check.ps1` 和 `pwsh -NoProfile -File tools/governance/verify_pins.ps1`，核实代码无漂移；本轮安全回归为1137/0/57+排除PNG 1项，不能声称无filter全量已复跑，旧1138/0/57仅为前序同代码基线。范围复审 P0/P1=0 且 DSH 冻结后才派新 Codex 实现会话，交付时必须用安全输出机制恢复全量1138起点及新增测试、FEA-07矩阵、fresh impl Review、DSH集成验证和资源核销 Gate。
