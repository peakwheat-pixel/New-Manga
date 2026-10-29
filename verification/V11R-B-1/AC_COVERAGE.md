# V11R-B-1 验收标准覆盖（AC → 证据）

| AC | 要求 | 实现 | 证据 |
|---|---|---|---|
| AC1 | 按 SCREEN_SPECS §1/§2 的布局、组件、状态、数据源实现；**无 Mock 冒充真实** | TopBand 36px（SpaceTabs/Breadcrumb/模式/ScopeSelector/AttentionMenu/命令/主题/F1）+ 空间内容 + StatusBand；Library 搜索/排序/筛选/书卡 PageGrid/驻留详情/章节账本/页/进度/多选批量条/ImportDock/回收站/阅读浮层；数据只经 `IHostController`（36 方法 + `CreateChapterAsync`）；未接入项全部显示「能力待接入」（`NOT_WIRED.md` 15 条） | `01`–`12` 截图；`NOT_WIRED.md`；`V2ShellUiTests`（导入逐文件真实状态断言 `ImportFileCalls`、阅读保存断言 `Progress.Attempts`） |
| AC2 | 上下文保留：空间/模式切换不重建 VM、不丢 selection/滚动/筛选 | `ShellState` 唯一状态源 + 三个空间视图实例只切换可见性；Library VM 单例 | `V2ShellStateTests.SpaceAndModeSwitch_KeepSelectionFiltersAndScroll`、`StudioPageAndBatch_KeepIndependentScrollContext`；`V2ShellUiTests.SpaceAndModeSwitch_KeepsSelectionFiltersAndTheSameViewModels`（`Assert.Same` VM/集合 + selection/search/scroll/multi 断言）；`03` 截图 |
| AC3 | 状态完备：idle/loading/ready/empty/error/partial 就地呈现 | Library 五态就地（loading 骨架文案/错误+重试/未就绪+重试/空库/无结果）；导入 partial（部分失败 + 逐文件状态 + 重试/跳过）；阅读错误就地 + 重试；`StatusBadge` 九态符号+文字 | `01`、`06`、`08` 截图；`ImportDock_ReportsRealPerFileStatus_AndRetriesFailures`、`RecycleBin_*`、`HasError/IsEmptyLibrary/HasNoResults` 属性路径 |
| AC4 | 无裸色值/字号/间距/阴影/渐变/模糊；全部 `{DynamicResource Nm.*}`；`-warnaserror` 0 warning | V2 XAML 全部使用 `Nm.*`；本地控件样式也只用令牌；预置临时令牌/样式已删除（DS 为唯一视觉源） | `V2ConformanceTests.V2Xaml_UsesNoRawDesignValues_AndNoForbiddenEffects`、`EveryReferencedNmToken_ExistsInTheMergedDesignSystem`、`LocalFallbackTokenAndPreDsStyleFiles_AreGone`；`conformance/v2-tokens-and-classes.json`；`BUILD_TEST.md`（0 warning） |
| AC5 | 键盘可达 + 焦点可见 + Esc 逐级退出 + IME 安全 | `KeyMap` 单一注册表 + 启动断言；`AppShellViewModel.HandleKey` 统一隧道：Esc 逐级（确认→面板→跳转→帮助→阅读→主题→回收站→多选→页→章→书）；输入框聚焦时字母/方括号快捷键让位，Ctrl/F 键/Esc 仍生效；按钮/输入框焦点环来自 DS | `V2KeyMapTests`、`V2ShellUiTests.CommandPalette_JumpAndHelp_*`、`ImeSafety_LetterShortcutsYieldWhileTextInputIsFocused`、`RecycleBin_DangerConfirm_IsCancelable_*`（Esc 两级）、`ReaderOverlay_*`（Esc 退出） |
| AC6 | 单测覆盖 VM/状态机/交互规则；`dotnet test` 绿；关键屏截图 | 见 `BUILD_TEST.md` §3：33 条新增测试全绿；12 张真渲染截图 | `BUILD_TEST.md`、`test.log`、`screens/` |
| AC7 | 证据：构建/测试日志、截图、偏差与未接入清单 | 本目录全部文件 | `README.md`、`BUILD_TEST.md`、`build.log`、`test.log`、`screens/`、`DEVIATIONS.md`、`NOT_WIRED.md`、`conformance/` |

## 关键交互验收（SCREEN_SPECS §1/§2 表格 → 证据）

| 规格条目 | 证据 |
|---|---|
| 三空间切换保留 selection/滚动 | `V2ShellUiTests.SpaceAndModeSwitch_*` |
| `Tab` 切 Studio 模式保留 context | 同上 + `V2KeyMapTests.Tab_OnlyTogglesModeInsideStudio_*` |
| 命令面板覆盖全部已实现动作、带「空间·模式·作用域」+键位 | 命令面板由 `ShellCommands.Definitions` 生成，`V2KeyMapTests.PaletteCatalog_*`；`04` 截图 |
| `F1` 速查 | `05` 截图 + `CommandPalette_JumpAndHelp_*` |
| 窗口 1600/1280/1024 不崩 | `Shell_RendersAt1600x1000_*`、`Shell_RendersAt1280And1024_*`；`01`/`11`/`12` 截图；1600 四列 / 1280 三列断言 |
| Library 搜索（中文/拼音首字母） | `V2PinyinTests`；`V2ShellUiTests` SearchText 路径 |
| 排序 + 筛选 Chip | `FilterChipItem`/`SortIndex`（真实 `BookSummary` 字段） |
| 书卡 PageGrid 4/3/2 列响应式 | `LibraryViewModel.SetViewport` + `ColumnCount` 断言 |
| 驻留详情（作品/章节账本/页/进度/操作） | `BookDetailPanel.axaml`；`01` 截图 |
| 多选批量条（删除/导出/标记） | `LibraryView` 批量条；未接入动作有明确提示；选择数/摘要断言 |
| ImportDock 逐文件状态 + 部分失败重试/跳过 | `06` 截图；`ImportDock_ReportsRealPerFileStatus_*` |
| 无章节时就地「新建章节」真实可用（关闭 F011） | `ImportDock_WithoutChapter_*`（`CreateChapterCalls`/`CreateChapterRequests`/成功后导入目标章节断言） |
| 回收站恢复/永久删除二次确认 | `07` 截图；`RecycleBin_DangerConfirm_*`（确认被禁用 + 原因 + 取消/Esc + 不写数据） |
| 阅读浮层分页 RTL/LTR + Webtoon + 双模态进度 + Esc + 进度保存 | `08` 截图；`ReaderOverlay_ShowsDualProgress_*`（页码/百分比/保存次数/退出） |
