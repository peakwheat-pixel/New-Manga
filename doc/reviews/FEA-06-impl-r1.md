---
task_id: FEA-06
reviewer: subagent_zcode
reviewer_kind: subagent
author: codex
base_commit: 3c7f311d88b24bde462a61690e15d2c66f8c4683
reviewed_head: b0388df9ae2bb087649b44cf25a0921b2116934e
decision: changes_requested
counts: { P0: 0, P1: 1, P2: 9 }
---

# FEA-06 实现复核 r1（Fluent 四页 + 设计系统组件）

| 字段 | 值 |
|---|---|
| Task | `doc/tasks/FEA-06.md`（`in_review`；owner=Codex，用户 2026-11-02 指派 W-10） |
| base_commit | `3c7f311d88b24bde462a61690e15d2c66f8c4683`（卡 front matter 一致） |
| reviewed_head | `b0388df9ae2bb087649b44cf25a0921b2116934e`（`feat(fea-06): … 1030/0/57`；37 路径 +7035/−232） |
| 其后文档 head | `966cedeac`（仅卡/STATUS/PLAN/LEDGER/handoff/3 日志，`git diff --name-only b0388df9a..HEAD` 证实零实现代码改动；工作树代码 == 被审 head 代码） |
| reviewer | **subagent_zcode**——DSH Lead 经 `subagent_zcode` 派发的**独立上下文子代理**；与 Codex 实现会话无共享上下文，未参与 FEA-06 的任何起草、范围处置、实现或返修，符合 2026-10-31 上下文独立裁决 |
| 日期 | 2026-11-02 |
| 结论 | **changes_requested（P0=0 / P1=1 / P2=9）**——实现主体质量与诚实度高、全量回归逐位复现；唯一 P1 为 CANONICAL 证据（组件登记表）声称了不存在的令牌 `Nm.Space.S1` 且样式悬空引用，须最小返修后方可进 DSH 集成验证 |

---

## 0. 方法与只读声明

- 只读核查被审 head；除本报告外未修改任何文件、未 commit/push。工作树全程保持 clean（复跑全量测试后 `git status --short` 仍为空）。
- 行号基于 `b0388df9a` 实测（实现代码在 b0388df9a..966cedeac 之间零改动，工作树行号即被审行号）。
- 本轮独立复跑（不采信实现者日志）：
  - `git rev-parse HEAD` = `966cedeac…`；`git status --short` 空；`git log --oneline -5` 链一致。
  - `dotnet build apps\desktop-avalonia\NewManga.sln --nologo` → **0 警告 / 0 错误**。
  - `dotnet test …NewManga.sln --no-build --settings …NewManga.runsettings` → **1030 passed / 0 failed / 57 skipped**（Appearance 21/0/0、Host 51/0/28、ThemeEngine 253/0/0、DesignSystem 87/0/0、ApplicationCore 31/0/0、CoreClient 128/0/22、App 459/0/7）——**与卡 AC8 声明逐位一致**；57 skip 分布（Host 28 + CoreClient 22 + App 7）与 PREREQ-2 基线完全相同，`skip-analysis.md` 归因（`NEWMANGA_CORECLIENT_SIDECAR_DIR` 未设置）成立。
  - TokenGen `-- --check` → up to date（292 rows）；ThemeGen `-- --check` → up to date（含 Material 主题层派生）。
  - `check.ps1` → **PASS（3 warnings：9 非终态 Task / STATUS 80% / PLAN 80%——与 scope-r3 轮完全相同，非本实现引入）**；`verify_pins.ps1` → **PASS（all 15）**。
  - 四页 PNG 复跑前后 SHA-256 **逐位一致**（`FluentPages_RenderHeadlessPngEvidence` 重渲染与提交版本相同，`verification/FEA-06/runtime/` 未产生）。

---

## 1. 逐 AC 判定（AC1–AC10）

| AC | 卡判定 | 复核判定 | 证据（文件:行号 / 实测） |
|---|---|---|---|
| AC1 Shell+响应式 | PARTIAL | **诚实，成立** | TopBand/NavRail/StatusBand 全令牌化（`Controls.Fluent.axaml:5-25`：`Nm.Size.TopBand`/`TreeWidth`/`StatusBandPage`）；断点 1024/1280/1600 经 `ShellLayout.Breakpoint*` → `NmKeys.Size.Breakpoint.*`（`FluentShell.axaml.cs:156-160`，`ShellLayout.cs:17-19`）；**17 快捷键**由测试硬断言（`FluentPageTests.cs:85` `Assert.Equal(17, …HasGesture)`）且 `ExecuteCommand` 全分支可达（`FluentShell.axaml.cs:319-357`）；折叠/memento/200% DPI 缺失与卡声明一致。附注：P2-3（Narrow 命名错位）、P2-4（控制台空间映射）、P2-5（`[`/`]` 工作台未接） |
| AC2 Shelf | PARTIAL | **诚实，成立** | 网格/列表（`ShelfPageView.cs:253-260`）、搜索筛选（`:93-95` FilteredBooks）、Ctrl 多选（`:304-311`）、拖入预览确认（`:409-444`）；6 卡骨架（`:201-208`）、错误卡+重试（`:209-214`）、只读警示+按钮禁用（`:215-220`、`:281-284`）；回收站空 Drawer 附诚实说明（`:65-68`，Host 无回收站端口）与卡声明一致。附注：P2-2（错误卡缺控制台入口）、P2-6（空态主按钮动作偏差）；Shift 区间多选、双击打开未实现且未在卡内逐项点名（归入 P2-2 粒度问题） |
| AC3 Workbench | PARTIAL | **诚实，成立** | Draft 7 方法全部经注入 `IHostController`（`FluentPageViewModels.cs:520/546/611/646/681/699/734/760`，接口面 `Services/IHostController.cs:422-458`）；**17+2 错误码映射与冻结契约逐码一致**（`DraftErrorMap`（`FluentPageViewModels.cs:830-860`）19 键 vs `FEA-05_DRAFT_WIRE_CONTRACT.md:41-63` 17 码 + INTERNAL/UNKNOWN 兜底，category 全对）；`pageBindingVersion` 缺失 fail-closed（`:599-605` 置 ReadOnly + 说明；View 层 Tooltip `WorkbenchPageView.cs:200-203`）；未决确认模态 保存/丢弃/取消 + flush 失败留旧页（`WorkbenchPageView.cs:112-129`、`:297-306`）；冲突条/只读/骨架（`:157-184`）；Run 投影条仅占位、BatchMatrix 未绑定（`:86-89`）与卡声明一致。附注：P2-2（冲突态缺「查看对照」、满态缺未保存圆点） |
| AC4 Reader | PARTIAL | **诚实，成立** | 页导航/翻页（`ReaderPageView.cs:178-216` ←/→/PgUp/PgDn/F/Esc + 滚轮 `:53-57`）、缩放 +/-/0（`:190-204`）、方向 memento（`ReaderViewModel.ReverseDirection` 壳级实例保留）、进度写回经 `SaveReadingProgressAsync`（`FluentPageViewModels.cs:952-960`，写失败提示不阻塞）；空/错误/部分（缺页「页面未就绪」）状态（`ReaderPageView.cs:135-148`）；双页第二图/滚动模式/自动隐藏/只读警示缺失与卡声明一致 |
| AC5 Settings | PARTIAL | **诚实，成立** | 外观保存**唯一经 `AppearanceCoordinator.SaveAsync`**（`FluentPageViewModels.cs:1143-1189`，无第二写者，grep 证实 src/ 仅组合根两处构造）；冻结字段逐字覆盖：visualThemeId/frontendId/mode/contrast/motion.mode/motion.categories 三类/corners/material/layout.*/followSystemAccent/schemaVersion（`SettingsPageView.cs:218-283`，与 `08-page-settings.md:41-58` 逐项对齐）+ Provider/网络/备份/关于分组（`:285-415`）；Fluent 材质 Current 下禁用+原因 Tooltip（`:250-263`）=「部分」态；网络契约缺口在页面文字如实声明（`:345`）；只读全禁用+Tooltip（`:181-194`）；危险操作二次确认+默认焦点取消（`:480-499`）。附注：P2-9（缺离开未保存确认/Esc 取消） |
| AC6 组件 | PARTIAL | **诚实，但证据质量有 P1** | 登记表 20 项 + 6 支撑组件、逐项列令牌/状态缺口（`component-registry.md`）；状态覆盖缺口（SurfaceCard 三态、RegionBox pressed/locked/conflict 等）如实登记。**但 TabStrip 行令牌列写 `Nm.Space.S1`——该键不存在**（见 P1-1）；页面归属列多处失实（P2-1） |
| AC7 a11y/动效 | PARTIAL | **诚实，成立** | `AutomationProperties.Name` 经工厂全覆盖（`FluentUi.cs:33/59/66/72/80/89/99/134/148`）；进度 LiveSetting=Polite（`SettingsPageView.cs:456`、`ReaderPageView.cs:133`）；reduce-motion 经 `MotionResolver` + `ThemeManager.SetReducedMotion` + `motion-reduced` 类（`FluentShell.axaml.cs:440-447`、`FluentPageViewModels.cs:1349-1365`）；高对比经 `SetContrast`（`:1359-1361`）；焦点环令牌未消费、页面切换动画未实现、无原生验证与卡声明一致 |
| AC8 回归 | MET | **成立（复跑逐位一致）** | 本轮独立复跑 1030/0/57；相对基线 1022/0/57 新增 8（App +7=FluentPageTests、DesignSystem +1=FluentComponentsTests）；无测试删除/削弱（FluentShellTests 改动为断言随 W-6 行为更新：Reader 移出左导航，V2/legacy 分派断言保留） |
| AC9 证据 | MET | **成立** | 27 条 CANONICAL/SOURCE_PIN 全部在场；PNG 为真实 headless 渲染（`CaptureRenderedFrame`，`FluentPageTests.cs:154-160`；1180×780、唯一色 600–935、复跑逐位一致）；UIUX finalize **PARTIAL（exit 11）如实保留**（`task-result.json` status=PARTIAL）；skip 归因属实 |
| AC10 范围纪律 | MET | **成立** | 37 路径逐一核对全部落在卡 `allowed_paths`（见 §3）；未 push（`git branch -r --contains b0388df9a` 为空，origin/main tip=`b1c1f5a56`）；无新增依赖/资产（无 csproj/Assets/字体路径） |

**AC1–AC7 的 PARTIAL 判定全部诚实**：每项缺失声明均与实现事实吻合，未发现把缺失说成完成的虚报；反向亦未发现已完成却谎报缺失的低报。

---

## 2. P1–P7 与 W-1…W-12 符合性

| 项 | 判定 | 证据 |
|---|---|---|
| P1 Shell | ✓（基础层） | 顶条/左导航/状态条/命令条 + 空间作用域导航（`FluentShell.axaml.cs:255-265`）；17 键位 + 三断点实现；折叠/memento 缺=卡声明 |
| P2 Shelf | ✓（基础层） | BookCard/BookRow/ChapterList 组件面/筛选/选择/拖入确认/回收站入口；回收站操作=端口缺失，卡声明属实 |
| P3 Workbench | ✓（基础层） | Region 列表/画布 RegionBox/Inspector/FilmStrip（按钮承载）/Draft 7 方法/17 码映射；Run 端口与矩阵绑定缺=卡声明 |
| P4 Reader | ✓（基础层） | 页导航/缩放/全屏/键盘滚轮/方向 memento/进度写回；双页/滚动/自动隐藏缺=卡声明 |
| P5 Settings | ✓ | 五分组 + 冻结字段逐字 + 唯一写者 + 校验（frontendId/visualThemeId 值域白名单 `FluentPageViewModels.cs:1338-1343`） |
| P6 设计系统 | ✓（基础层） | 15 控件 + 全令牌样式 + 登记表；全组件状态覆盖不足=卡声明（登记表逐行缺口如实） |
| P7 证据 | ✓ | `verification/FEA-06/**` 27 文件 + 命令/exit 记录 + PNG + 登记表 + UIUX |
| W-1 设计基线 | ✓ | 唯一输入 fluent-v1.0.0；零改 `doc/design/fluent-v1/**`（37 路径无命中） |
| W-2 Draft 接入 | ✓ | 全部经 `IHostController`；typed error 映射见 §1 AC3 |
| W-3 页面拆分 | ✓（类级）/ P2-8（文件级） | 四 View/VM 类独立、Shell 只做导航/键盘/命令面板/对话框宿主；四 VM 同居 1373 行文件（P2-8） |
| W-4 视觉实现 | ✓ | 令牌 + ThemeEngine/DesignSystem 既有（Skeleton/AlertBanner/Drawer/SearchField/SegmentedControl 复用，无第二套系统） |
| W-5 Fluent 激活 | ✓ | 零改 selector/组合根（37 路径无 `App.axaml.cs`）；只实现壳内四页 |
| W-6 空间映射 | ⚠️ 基本符合 / P2-4 | 顶栏空间 1/2/3 ✓；左导航随空间（Library=书架/回收站/导入）✓；Reader 不新增 SpaceId（`_pageBeforeReader` 保留返回、无导航按钮）✓；但第三空间按钮「控制台」导航到**设置页**（`FluentShell.axaml.cs:245`、`:222` "console"→Settings）——Fluent 壳无控制台页面承载，空间↔内容映射折中（P2-4） |
| W-7 令牌归属 | ✓ | 本卡零改生成物；TokenGen/ThemeGen `--check` 复跑 up to date |
| W-8 状态清单 | ✓（覆盖大头）/ P2-2 | 四页 9 行状态各有承载（见 §1）；细粒度缺口 3 处未逐项声明（P2-2） |
| W-9 写域 | ✓ | 37 路径全在 `allowed_paths`；未触组合根（W-9 明文排除项） |
| W-10 Owner/交付 | ✓ | 单一实现 commit；未 push；DSH 保留 Review/集成/push（本报告即 Appointment 产物） |
| W-11 证据口径 | ✓ | 每页 ≥1 headless 状态测试 + PNG + 登记表 + 命令/exit 日志 |
| W-12 注入预置 | ✓ | 只读属性三件（`FluentShell.axaml.cs:134-136`）仅消费；**grep `new HostController|new AppearanceCoordinator|new AppearanceStore` 于 src/ 仅组合根 `App.axaml.cs:66/77` 两处**——无第二实例/第二写者；ViewModel 全部经构造注入（`:108-111`） |

**令牌纪律（01 §3 判据①）**：`Controls.Fluent.axaml` 354 行逐一检查，除 P1-1 的 `Nm.Space.S1` 外全部为有效 `{DynamicResource Nm.*}` 引用，**零裸值**（无字面量颜色/CornerRadius/BoxShadows）。引用键存在性逐一核实：结构键在 `Tokens.Global.axaml`，颜色变体键在 `Tokens.Light/Dark/HighContrast.axaml`，`Nm.Material.Acrylic.Base/Tint` 在 ThemeGen 派生的主题层（`fluent-dark.nmtheme`，`theme-gen.log` "derived: Fluent acrylic material colours"）、`Opacity/Mica.Enabled` 在 Global（`:50-51`）。附注：`Nm.Elevation.1/2/3` 冻结键存在但在 Fluent 样式层**零消费**（全部以 1px 边框替代阴影，P2-7）。

---

## 3. 范围与安全审计

- `git show --name-only b0388df9a` 37 路径 vs 卡 `allowed_paths`：App 代码 8（Controls 1/ViewModels 1/Views 6）、DesignSystem 3、测试 3、`verification/FEA-06/**` 23——**全部在写域内，无越界路径**。
- 禁改面零触碰：`App.axaml.cs`、`FrontendSelector`、Core/**、契约、schema、生成物（`NmKeys.g.cs`/`Tokens.Global.axaml`/`TokenMap.md`/`*.nmtheme`）、`doc/design/fluent-v1/**`、Current V2（Shell/V2、AppShellV2 等路径零命中）。
- 依赖/资产：无 csproj、无 `Assets/**`、无字体/图标新增（图标全部复用 `NmIcon`，`ShelfPageView.cs:328` 等）——符合 r2-P2-6 资产边界。
- push：`git branch -r --contains b0388df9a` 空；origin/main tip=`b1c1f5a56`（2026-11-02 push 记录的既有点位）——**未 push ✓**。
- 用户数据/源文件：零写入（无 DB/文件系统产品路径触及；测试 AppearanceStore 只读 Reload）。

---

## 4. 测试与证据可信度

- 全量 **1030/0/57 独立复跑成立**（分解见 §0），新增 8 测试确认为真覆盖：`FluentPageTests` 7 个对四页状态/Shell 键盘/断点/空间导航/PNG 渲染断言具体值（非空断言，如 `:85` 17 键位、`:87-91` Ctrl+2/Tab/文本聚焦排除）；`FluentComponentsTests` 验证 15 控件类标识 + Dialog/Drawer 开关态 + SegmentedControl 两选项。既有断言无削弱（`FluentShellTests` 改动为随 W-6 行为更新的断言迁移，V2/legacy 分派与 Assert.Same 三件保留在场）。
- 57 skip 与基线同分布（Host 28/CoreClient 22/App 7），归因 `NEWMANGA_CORECLIENT_SIDECAR_DIR` 未设置成立；无新增/移除/放宽 skip。
- 四页 PNG 真实 headless 渲染：1180×780、600–935 唯一色、`CaptureRenderedFrame` 产物、**复跑前后 SHA-256 逐位一致**（与卡内 EV-FEA06-SCREEN-* 四条 pin 相同）——非空白/占位。
- UIUX finalizer **PARTIAL（exit 11）如实保留**（独立 Review/L4 设计 Review/流程图/NATIVE_APP 未补），证据链未粉饰。
- 证据侧瑕疵即 P1-1/P2-1（登记表口径），其余日志（build/full-test/token/theme/governance/pins）与实测一致。

---

## 5. 可维护性与架构

- 四页 View/ViewModel 独立、单一路径依赖注入、Shell 只做导航/键盘/命令面板/对话框宿主——W-3 类级满足；`FluentPageViewModels.cs` 1373 行四 VM 单文件建议拆分（P2-8）。
- 无重复实现第二 Host/Coordinator/ThemeManager；主题写路径唯一（SettingsViewModel.ApplyToThemeManager 经注入 ThemeManager）。
- 轻量死代码/未接线组件：`ChapterList`、`TabStrip`（以及既有 `SegmentedControl`）未被任何页面实际引用（BatchMatrix/RunProjectionBar 为占位且已声明）——见 P2-1。
- `ShelfPageView.Render()` 由任意 PropertyChanged 全量重绘（`:83`）——功能正确、性能粗放，可后续优化（不入发现清单）。

---

## 6. 发现分级与最小返修建议

### P1-1（返修，责任方：Codex；DSH 处置）

**`Nm.Space.S1` 悬空令牌引用 + CANONICAL 证据登记失实。**
`Controls.Fluent.axaml:241`（`fluent-tab-strip` 样式）`Spacing="{DynamicResource Nm.Space.S1}"`——冻结令牌族为 `Nm.Space.0…Nm.Space.8`（`Tokens.Global.axaml` 实测），**`Nm.Space.S1` 不存在于任何生成物/主题层**（Avalonia 运行时静默回退默认值 0）。同时 `component-registry.md:28`（EV-FEA06-AC6 CANONICAL 证据）将 `Nm.Space.S1` 登记为 TabStrip 令牌依赖——证据声称了不存在的令牌。功能影响为零（TabStrip 未被页面使用），但违反 G-1/01 §3「令牌依赖如实」判据，与 PREREQ-2 impl-r1 R1-P1-1（allowed_paths 回填失实）同级。
**最小修复**：①样式改用既有键（建议 `Nm.Space.1` 或与相邻组件一致的 `Nm.Space.2`）；②`component-registry.md` TabStrip 行令牌列同步。单次小提交，全量回归预期 1030/0/57 不变。

### P2（9 条，建议处置；不阻塞返修主链）

| # | 位置 | 问题 | 建议 |
|---|---|---|---|
| P2-1 | `component-registry.md` 页面列 / `FluentComponents.cs` | 登记表页面归属失实：TabStrip「Workbench/Settings」、SegmentedControl「Shelf/Workbench」、ChapterList「Shelf」实际均未被页面引用（页面用普通按钮/StackPanel）；构成轻量死代码 | 随 P1-1 返修同步修正登记表（「已实现未接线」口径）或补接线；DSH 裁决去留 |
| P2-2 | 卡 AC2/AC3 缺失清单粒度 | 09 矩阵细粒度缺口未逐项点名：书架/工作台错误卡缺「控制台入口」（09:11）、工作台满态缺「未保存圆点」（09:12）、冲突态缺「查看对照」动作（09:14） | 卡内补记或并入后续 Task 验收；不属虚报（「状态矩阵未全实现」已概括） |
| P2-3 | `FluentShell.axaml.cs:278-284` | 响应式档位命名错位：实现把 1024–1279 标 `Narrow`，设计 04 §2 该区间为 Medium（Narrow=<1024 折叠导航）。行为正确（<1024 隐藏 rail + `MinWidth=1024`），仅枚举名/状态条文案错位 | 枚举改名或文案对齐设计术语（1 行级） |
| P2-4 | `FluentShell.axaml.cs:245/:222` | 第三空间按钮「控制台」导航到设置页（Fluent 壳无控制台页承载）；W-6 硬约束（不新增 SpaceId/第五页）未破，但空间↔内容映射与 04:13 语义有偏差 | DSH 裁决：暂禁用+原因提示更诚实，或登记后续 Task 承载控制台页 |
| P2-5 | `FluentShell.axaml.cs:341-342` | 全局 `[`/`]`（page.next/previous）只接阅读器翻页；工作台页内翻页（06 §6）未接线，工作台按 `]` 无效果 | 后续接线 `_workbenchModel`（当前 SelectedPage 切换） |
| P2-6 | `ShelfPageView.cs:229-237` | 书架空态主按钮为「新建作品」，设计 05 §3 为「导入文件/文件夹」——因 Host 导入端口要求先选章节（`ImportFilesAsync` 需 `SelectedChapter`），空态直接导入不可达；实现选择与端口能力一致的诚实路径，但卡内未声明该偏差 | 卡内补记偏差原因；或后续 Host 端口演进时对齐 |
| P2-7 | `Controls.Fluent.axaml` 全文 | `Nm.Elevation.1/2/3`（01 §2.3 冻结、10 清单多组件令牌列）在 Fluent 样式层零消费（卡片/对话框全部 1px 边框替代阴影）；登记表亦未声明该取舍 | 登记表补「Elevation 未消费（边框替代）」或后续补阴影样式 |
| P2-8 | `FluentPageViewModels.cs`（1373 行） | 四 ViewModel 同居单文件；W-3 类级满足、文件级建议拆分 | 后续重构切四文件（纯移动，零行为变化） |
| P2-9 | `SettingsPageView.cs` | 缺 08 §5「离开页面未保存确认（保存/丢弃/取消）」与 `Esc` 取消编辑；重置外观无二次确认（重置仅改草稿、需手动保存，风险低） | 后续补导航前 IsDirty 检查 + Esc 处理 |

另附注（不计级）：`FluentPageTests.RenderHeadlessPngEvidence` 直接写 `verification/FEA-06/screens/`——本机已证渲染逐位确定，但异机环境复跑可能因渲染差异产生工作树 dirty；后续可考虑输出重定向或显式标注为采证专用测试。

---

## 7. 结论与建议

1. **AC1–AC7 PARTIAL 判定诚实且范围受限可信，可接受进入返修/集成轨道**；AC8–AC10 MET 经独立复跑成立。
2. **最小返修集 = P1-1 一项**（样式 1 行 + 登记表 1 行；P2-1 登记表页面列三处可随同一提交顺手修正）。返修后全量回归预期不变，无需重跑 UIUX。
3. **可否进入 DSH 集成验证：P1-1 返修闭合后即可进入**。若 DSH 选择带 P1 直接集成（代码行为零风险，仅证据口径），须在 adjudication 中显式登记处置并要求登记表修正于 closeout 前补齐——不建议作为默认路径。
4. P2 九条均不阻塞：P2-1/P2-7（登记表口径）建议随返修或 closeout 处理；P2-3/P2-5/P2-9 为 1 行~小片级后续；P2-4 需 DSH 空间映射裁决；P2-2/P2-6/P2-8 登记后归后续 Task。

---

## 8. 边界声明

本报告只审实现、证据与范围符合性：不审 fluent-v1.0.0 设计数值本身（FROZEN，FEA-04b r5 approved）；不执行 UI 像素级/原生桌面验收（headless 证据按 W-11 口径采信并已注明 SIMULATED 边界）；`check.ps1`/`verify_pins` 为只读参考。未修改实现、测试、契约、设计、生成物、组合根/selector、Current V2；未 push；除本报告外未写任何文件。行号基于 `b0388df9a` 实测；判据未为放行降低，亦未为挑错虚构。本报告不构成集成授权；集成与终态由 DSH adjudication 决定。
