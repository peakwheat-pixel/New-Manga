---
task_id: FEA-06
reviewer: subagent_zcode
reviewer_kind: subagent
author: codex
base_commit: 3c7f311d88b24bde462a61690e15d2c66f8c4683
reviewed_head: 7cf305fe2534272dc75295c4644661ddb73221af
decision: approved
counts: { P0: 0, P1: 0, P2: 1 }
---

# FEA-06 实现复核 r2（impl-r1 返修窄面复核）

| 字段 | 值 |
|---|---|
| Task | `doc/tasks/FEA-06.md`（`in_review`；owner=Codex） |
| base_commit | `3c7f311d88b24bde462a61690e15d2c66f8c4683`（卡 front matter 一致） |
| reviewed_head | **`7cf305fe2534272dc75295c4644661ddb73221af`**（`fix(fea-06): 处置 impl-r1 P1-1（令牌/登记表）+ W-13 控制台空间映射 + P2 登记`；27 路径 +894/−79） |
| 其后文档 head | `c878698ba`（仅 pin delivery_head/证据索引，零实现代码改动；`git log` 链一致，工作树代码 == 被审 head 代码） |
| reviewer | **subagent_zcode**——DSH Lead 经 `subagent_zcode` 派发的**独立上下文子代理**；与 Codex 实现会话（含 r1 返修会话 `01a19a5e-2490-7943-a8c5-6cc05e13a4cb`）无共享上下文，未参与 FEA-06 的任何起草、范围处置、实现或返修，符合 2026-10-31 上下文独立裁决 |
| 复核范围 | 窄面：r1 findings（P1-1、W-13、P2-1/2/3/5/6/7/8/9）处置闭环 + 新问题 + 范围；不重审 r1 已判定的 AC1–AC10 全貌 |
| 日期 | 2026-11-02 |
| 结论 | **approved（P0=0 / P1=0 / P2=1）**——P1-1 闭合、W-13 符合 DSH 裁决与设计基线、P2 处置全部落实、范围零越界、全量 1034/0/57 无退化；新发现 1 条 P2（TabStrip 选中态样式缺失 + 登记表半句失实），不阻塞集成，交 DSH 处置 |

---

## 0. 方法与只读声明

- 只读核查被审 head；除本报告外未修改任何文件、未 commit/push。全量复跑（含 PNG 采证测试）后 `git status --short` 仍为空。
- 行号基于 `7cf305fe2` 实测（其后 `c878698ba` 仅改文档，工作树行号即被审行号）。
- 独立复跑（不采信实现者日志）：

| 命令 | 结果 |
|---|---|
| `git rev-parse HEAD` / `git status --short` | `c878698ba…` / clean（全量复跑后复查仍 clean——PNG 重渲染与提交版本逐位一致） |
| `dotnet build apps/desktop-avalonia/NewManga.sln --nologo` | **0 警告 / 0 错误** |
| `dotnet test …NewManga.sln --no-build --settings …NewManga.runsettings` | **1034 passed / 0 failed / 57 skipped**（Appearance 21/0/0、Host 51/0/28、ThemeEngine 253/0/0、DesignSystem 87/0/0、ApplicationCore 31/0/0、CoreClient 128/0/22、App 463/0/7）——与卡/handoff 声明逐位一致；skip 分布（Host 28 + CoreClient 22 + App 7）与 PREREQ-2/r1 基线完全相同，归因 `NEWMANGA_CORECLIENT_SIDECAR_DIR` 未设置成立 |
| TokenGen `-- --check` / ThemeGen `-- --check` | 均up to date（292 rows / 主题生成物与冻结输入逐字节一致） |
| `check.ps1` / `verify_pins.ps1` | PASS（3 warnings：9 非终态 Task / STATUS 80% / PLAN 80%——与 r1 轮完全相同，非本轮引入）/ PASS（all 15） |
| 定向 `--filter FullyQualifiedName~FluentTokenResourceTests` | 1/1 PASS（守卫测试在场且真实执行） |

1034 相对 r1 的 1030 **+4**：`FluentTokenResourceTests`（守卫）1 + `ConsoleSpaceUsesWorkbenchConsoleAndSettingsRemainANonSpaceEntry`（W-13）1 + `WorkbenchPageShortcutsMoveThroughExistingPageSelection`（P2-5）1 + `Shelf_WiresSegmentedViewModeAndChapterList`（P2-1）1——与 handoff 声明一致。adjudication 预期「1030/0/57 不变」按「无退化」意图满足（新增测试正是处置要求③/W-13/P2-5 的守卫与行为测试，且诚实登记）。

---

## 1. P1-1 闭环核验（逐点实测）

| 要求 | 实测 | 判定 |
|---|---|---|
| ① `Nm.Space.S1` → 既有冻结键 | `Controls.Fluent.axaml:241` 现为 `Nm.Space.2`；`grep -rn "Nm.Space.S1"` 于 `apps/desktop-avalonia/src/**`（含 obj 排除后）**零命中**；该文件全部 `Nm.Space.*` 引用为 `.2`/`.3`（:90/:93/:179/:236/:237/:241），均在冻结族 `Nm.Space.0…8`（`Themes/Tokens.Global.axaml:97-105`）内；`Nm.Space.S1` 在 Global/Light/Dark/HighContrast/nmtheme/生成代码全层**零定义**（反证 r1 确为悬空引用） | ✓ |
| ② 登记表 TabStrip 令牌列同步 | `component-registry.md:28` 令牌列现为「`Nm.Space.2`（条间距）」——与代码一致（半句「选中态使用 `Nm.Color.Accent.*`」仍失实，见 §6 P2-R2-1） | ✓（主列） |
| ③ 令牌存在性守卫测试 | `FluentTokenResourceTests.cs`（新增 53 行）：扫描 `DesignSystem/Styles`、`App/Styles`、`App/Views/Fluent` 三目录全部 `.axaml`，正则 `\{DynamicResource\s+(?<key>Nm\.[^,\s}]+)` 提取引用，`DistinctBy` 键后逐一 `application.TryGetResource(key, null, out _)` 断言可解析；前置 `DesignSystemThemeManager.Initialize(AppearanceMode.Dark)` 把 Global/Dark 令牌合并进 `Application.Resources.MergedDictionaries`（`DesignSystemThemeManager.cs:254`），查询路径成立 | ✓（有效性判定见下） |
| ④ 全量无退化 | 1034/0/57（§0），skip 分布不变 | ✓ |
| ⑤ 单一 fix commit / 不 push | `7cf305fe2` 单一 commit 含代码+证据+卡；`git branch -r --contains 7cf305fe2` **空**（origin/main tip 仍在 `b1c1f5a56` 前） | ✓ |

**守卫测试有效性判定（不止「存在」）**：反证链闭合——r1 head 的 `Controls.Fluent.axaml:241` 含 `{DynamicResource Nm.Space.S1}`（`git show b0388df9a:…` 实证），该键全令牌层零定义，守卫测试的扫描目录覆盖此文件、正则可匹配 `Nm.Space.S1`、`TryGetResource` 必 false → **在 r1 状态下该测试必红**，对「S1 型悬空键」类问题具有真实判别力。定向复跑 1/1 PASS 确认其在回归中真实执行。

**守卫测试局限（附注，不计级）**：仅以 Dark 模式解析，若某键只在他模式层缺失而 Dark 层存在则漏检（非本轮问题面）；`FindRepositoryRoot` 以 `doc/tasks/FEA-06.md` 存在性定位仓库根，可行但与卡文件绑定（该文件为版本库长期文件，风险低）；扫描范围为 Fluent 壳三目录，不含组合根 `App.axaml`（冻结面，合理排除）。

---

## 2. W-13 行为核验（DSH 裁决 vs 实现）

| 裁决要求 | 实测 | 判定 |
|---|---|---|
| `SpaceId.Console` 不得映射 Settings | `FluentShell.axaml.cs`：`Navigate(page)` 的空间映射表已删除 `FluentPage.Settings => SpaceId.Console` 行；`NavigateSpace`（:273）的 Console 分支为 `Navigate(FluentPage.Workbench)` + `_currentSpace = SpaceId.Console` + `_workbenchView.SelectConsoleTab()`；旧 `"console" => FluentPage.Settings` 命令面板映射改为 `NavigateSpace(SpaceId.Console)`（:235 区域） | ✓ |
| 控制台 = Workbench 第三视图 | `WorkbenchPageView.cs:119` `BuildTabs` 三 Tab「页面/批量/控制台」（`WorkbenchViewTab` 枚举 Page/Batch/Console）；`SelectConsoleTab()`（:86）切换；`BuildConsoleLayout`（:188）承载 Run 投影条 | ✓ |
| 无数据时诚实空态、不造假 | `BuildConsoleLayout`：`RunProjectionBar` 内文字「当前没有运行中的任务」+ 说明「Run 状态与错误由 Host 投影提供；当前端口尚未接入」；错误入口仅在 `_viewModel.State == Error && Error 非空` 时出现（真实工作台错误，点击切回页面 Tab）——零构造数据 | ✓ |
| Settings 非空间入口（`08-page-settings.md:3`） | 设计基线原文：「**不新增 `SpaceId`，入口来自顶部命令条与左导航**」。实现：`FluentShell.axaml:18` 新增 `SettingsCommandButton`（顶部命令条「设置」，`FluentShell.axaml.cs:130` 接线）+ `NavSettings` 常驻左导航（`UpdateNavigationItems` 中 `IsVisible = true`）——**与设计条目逐字吻合** | ✓ |
| Shell 测试同步 | `FluentShellTests`：`Navigate("console")` → Workbench 页 + Console Tab 断言、`NavSettings` 可见断言、`SettingsCommandButton` 在场断言；`FluentPageTests.ConsoleSpace…`：Ctrl+3 → Workbench+Console Tab+三 Tab 数+空态文案+NavSettings 可见、SettingsCommandButton 点击 → Settings 页且 **SpaceConsole 仍 selected**（空间状态保持）；既有导航测试随行为更新（NavSettings 断言 False→True） | ✓ |
| 空间/页面状态无错乱 | 状态由 `_currentSpace` 单一事实源承载：Console→Settings 不改空间（测试断言 selected 保持）；Console 下 NavWorkbench 可见且 `Navigate(Workbench)` 回 Studio+Page Tab；`TabChanged` 事件同步 `_studioMode` 防回环（`SelectTab` 先置 `_activeTab` 再改 `IsBatch`，PropertyChanged handler 以 `_activeTab != Console` 守卫）；`StudioModeToggle/StudioPage/StudioBatch` 命令均经 `SelectTab` 同步视图 | ✓ |

**W-13 residual 如实登记**：Task 卡「Run 控制台仅呈现无任务状态和实际已有的工作台错误入口；完整 Run 数据/控制由 FEA-07/FEA-10 的 Host 端口承接」——与 DSH 裁决原文一致。**W-13 符合 DSH 裁决与设计基线。**

---

## 3. 其余 P2 处置抽查

| ID | 处置要求 | 实测 | 判定 |
|---|---|---|---|
| P2-1 | TabStrip/SegmentedControl/ChapterList 接线或如实改口径 | 三者**全部真接线**：Workbench 三视图 Tab 用 `TabStrip`（`WorkbenchPageView.cs:44` `FluentTabStrip` + `:119`）；Shelf 网格/列表切换用 `SegmentedControl`（`ShelfPageView.cs` 替换两按钮，SelectionChanged ↔ `IsGrid` 双向同步）；Shelf 详情宿主改 `ChapterList`（`:61` 构造、`:207/:274/:280` Render 中清空/填充）——非死代码；登记表三行页面列改 Workbench/Shelf 属实；附带 `BatchMatrix`（`:180`）与 `RunProjectionBar`（`:192`）由占位获得承载。测试 `Shelf_WiresSegmentedViewModeAndChapterList` 判别选项点击→IsGrid 翻转 | ✓ |
| P2-2 | 卡内补记 09 细粒度缺口 | Task 卡 residual 段逐项点名：Shelf/Workbench 错误卡缺控制台入口、Workbench 满态缺未保存圆点、冲突态缺「查看对照」，AC2/AC3 保持 PARTIAL | ✓ |
| P2-3 | Narrow/Medium 术语对齐 | 枚举改名 `BelowMinimum/Narrow`→`Narrow/Medium`；`GetResponsiveBand`：`<1024=Narrow`、`1024–1279=Medium`；状态条文案「Narrow · <1024 / Medium · 1024–1279 / Compact · 1280–1599 / Full · ≥1600」；行为不变（`_navRail.IsVisible = ResponsiveBand != Narrow` 即 <1024 折叠）；测试断言精确匹配文案 | ✓ |
| P2-5 | `[`/`]` 接线或 residual | **真接线**：`HandleKeyForTest` 在 Workbench 页（Studio/Console 空间）对无修饰 `[`/`]` 分派 `PageNext/PagePrevious` → `NavigatePage` → `WorkbenchPageView.MovePage`（:98，用既有 `Pages`/`SelectedPage`/`RequestPage`，含边界 Clamp）；**未动共享 `ShellCommands`/KeyMap**——首次尝试扩大默认 V2 KeyMap 被 `V2KeyMapTests.Tab_OnlyTogglesModeInsideStudio…` 冻结测试拦下（`rework-full-test-attempt1.log` 诚实保留，App 1 failed/EXIT 1），最终改为 Fluent Shell 内分派——范围纪律正确；测试用 FakeHostController 两页真实判别 `]`→page-2、`[`→page-1 | ✓ |
| P2-6 | 卡内登记 residual | 「空态主按钮仍为新建作品…当前 Host `ImportFilesAsync` 要求先选章节…待 Host 提供可达的空态导入入口后再对齐」 | ✓ |
| P2-7 | Elevation 未消费声明 | 登记表新增「`Nm.Elevation.1/2/3` 已冻结但当前 Fluent 样式未消费；组件以 1px 边框表达层级」+ Task 卡 residual | ✓ |
| P2-8 | 技术债登记 | Task 卡「四个 Fluent ViewModel 仍同居…后续纯移动拆分」 | ✓ |
| P2-9 | residual 登记 | Task 卡「离开未保存确认及 Esc 取消…留后续 UX Task」 | ✓ |

---

## 4. 无新问题核验

- **控制台映射行为回归**：无。新测试覆盖空间切换/命令面板/键盘三入口；旧断言随行为正确迁移，无测试削弱（`NavSettings` False→True 是 W-13 预期变更；断点断言从单值改精确文案+双档位，判别力更强）。
- **Settings 可达性**：命令条按钮 + 常驻左导航双入口，测试双断言；`ThemeStudio` 命令仍可进 Settings（既有路径保留）。
- **键盘/空间状态**：`_studioMode` 事件同步无回环；Console 空间下 `[`/`]` 工作台翻页可达；`NavigatePage` 的 Reader/Library 分支保留 r1 行为。
- **范围扩权**：无（§5）；共享 KeyMap 未动且有冻结测试实证拦截记录。
- **新 P0/P1**：未发现。新发现 1 条 P2 见 §6。

---

## 5. 范围与安全审计

- `git show --name-only 7cf305fe2` 27 路径 vs 卡 `allowed_paths`：App Views/Fluent 4、DesignSystem Styles 1（`Controls.Fluent.axaml` ∈ `NewManga.DesignSystem/**`）、App.Tests 3、`doc/tasks/FEA-06.md`、`doc/handoffs/FEA-06-*.md`、`verification/FEA-06/**` 17——**全部在写域内，无越界路径**。
- 禁改面零触碰：`App.axaml.cs`、`FrontendSelector`、Core/**、契约/schema、生成物（`NmKeys.g.cs`/`Tokens.*.axaml`/`*.nmtheme`——两 `--check` up to date 佐证）、`doc/design/fluent-v1/**`、Current V2（Shell/V2 路径零命中；V2 行为由 `V2KeyMapTests` 等冻结测试全绿佐证）。无新增依赖/资产/字体。
- push：`git branch -r --contains 7cf305fe2` 空——**未 push ✓**。
- 用户数据/源文件：零写入。
- 证据链：`evidence-index.md` 更新 component-registry/PNG 四张新 sha256 + rework 日志 11 条全登记；`verify_pins.ps1` PASS（all 15）；PNG 复跑逐位一致（全量复跑后工作树 clean）。

---

## 6. 发现分级（新发现）

### P2-R2-1（不阻塞；交 DSH 处置：随 closeout 一行修正或归后续样式 Task）

**TabStrip 选中态无视觉样式支撑 + 登记表「选中态使用 `Nm.Color.Accent.*`」半句失实。**
`WorkbenchPageView.BuildTabs`（:119）对 Tab 按钮设 `Classes.Set("selected", …)`，但按钮 class 为 `fluent-secondary`，而 `Controls.Fluent.axaml` 中 `Button.fluent-secondary` 仅有 base/`:pointerover`/`:pressed`/`:disabled` 四变体（:263–278），全文件无 `fluent-secondary.selected` 或 tab-strip 内 selected 选择器——**selected class 为视觉空操作**，W-13 引入的「页面/批量/控制台」三 Tab 无选中视觉区分（行为与 a11y Name 正确，headless 测试断言的是 class 标记非视觉）。同时 `component-registry.md:28` 令牌列「选中态使用 `Nm.Color.Accent.*`」声称了不存在的消费关系（同构 r1 P2-1，非 P1-1 级——令牌本身存在、无悬空引用、主令牌列 `Nm.Space.2` 正确）。
**最小修复**：补 `Button.fluent-secondary.selected` 样式（如 Accent 前景/边框）或将该半句改为「选中态仅 class 标记，视觉样式留后续样式 Task」。

（r1 附注的 PNG 采证直写 screens/ 已按处置口径保留并在 Task 卡登记；本轮未新增其他不计级附注。）

---

## 7. 结论

1. **P1-1 闭合**：令牌修复、登记表主列同步、守卫测试有效（反证链闭合）、全量无退化——五项要求全部满足。
2. **W-13 符合 DSH 裁决与设计**：Console 空间落 Workbench 第三视图、空态诚实零造假、Settings 非空间入口与 `08-page-settings.md:3` 逐字吻合、测试同步、无空间/页面状态错乱；residual（FEA-07/FEA-10 承接）如实登记。
3. **P2 处置全部落实**（P2-1/3/5 真接线、P2-2/6/7/8/9 与 W-13 residual 如实登记），attempt1 失败诚实保留且证明共享 KeyMap 冻结面未被触碰。
4. **可否进入 DSH 集成验证：可以**。唯一新发现 P2-R2-1 不构成阻塞——建议 DSH 二选一处置：随 closeout 一行修正（样式或登记表措辞），或登记 residual 归后续样式 Task。若要求返修，责任方 Codex、最小 1 行级（不触发全量预期变化）。
5. 范围零越界、未 push、证据链自洽（sha 更新 + pins 15/15 + PNG 复跑逐位一致）。

---

## 8. 边界声明

本报告只审返修、证据与范围符合性：不审 fluent-v1.0.0 设计数值本身（FROZEN，FEA-04b r5 approved）；不执行原生桌面/像素级验收（headless 证据按 W-11 口径采信并注明 SIMULATED 边界）；`check.ps1`/`verify_pins.ps1` 为只读参考。未修改实现、测试、契约、设计、生成物、组合根/selector、Current V2；未 push；除本报告外未写任何文件。行号基于 `7cf305fe2` 实测；判据未为放行降低，亦未为挑错虚构。本报告不构成集成授权；集成与终态由 DSH adjudication 决定。
