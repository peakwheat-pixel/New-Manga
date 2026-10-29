# V11R-B-1 验收标准覆盖（I1 返修后）

| AC | 要求 | 实现 | 证据 |
|---|---|---|---|
| AC1 | SCREEN_SPECS §1/§2 布局、组件、状态、数据源；无 Mock 冒充真实 | TopBand 36px（SpaceTabs/Breadcrumb/模式/Scope/Attention/命令/主题工作室入口/快速外观/F1）+ 空间内容 + StatusBand；Library 搜索/排序/筛选/书卡网格/驻留详情（章节账本/页/进度/操作）/多选批量条/ImportDock/回收站/阅读浮层；数据只经 `IHostController`（含已合入 `CreateChapterAsync`）；未接入项全部显示「能力待接入」（NOT_WIRED 15 条） | `screens/`（含 01 全屏、13 加载骨架）；`NOT_WIRED.md`；测试逐项断言 |
| AC2 | 空间/模式切换不重建 VM、不丢 selection/滚动/筛选 | `ShellState` 唯一状态源 + 每空间 `SpaceViewState`；`IWorkspaceView.OnDeactivated`→`OnActivated` 双向交接；三个 ViewModel 各创建一次；滚动是**真实 ScrollViewer.Offset**（ScrollChanged 写回 state，激活时恢复） | `V2WorkspaceIntegrationTests`（hook 顺序）；`V2ShellUiTests.SpaceAndModeSwitch_*`、`ScrollOffset_IsRealShellState_AndRestoredAcrossSpaceSwitches`（真实 Offset 往返断言）；03 截图 |
| AC3 | 状态完备：idle/loading/ready/empty/error/partial 就地呈现 | Library 五态就地；**loading 用与书卡同尺寸的骨架网格**（保留 4 列/缝隙几何，删除自证文案）；导入 partial 逐文件状态；阅读错误就地重试；状态徽章三通道 | 13 加载截图；01/06/08；`ImportDock_*`、`HasError/IsEmptyLibrary/HasNoResults` 断言 |
| AC4 | 无裸色值/字号/间距/阴影/渐变/模糊；全 `{DynamicResource Nm.*}`；`-warnaserror` 0 warning | 本任务 XAML/C# 全部使用 DS 令牌；C# 布局值经 `ShellLayout` 从 `Nm.Size/Space/Drawer/TreeWidth` 等令牌解析（唯一 allowlist `ShellLayout.cs`，其断点/比例常量有注释）；conformance 扫描扩到 C# 与 Magnitude 模式；build 0 warning | `V2ConformanceTests`（XAML+C# 扫描、令牌存在性、断点、清单）；`conformance/v2-tokens-and-classes.json`；`build.log` |
| AC5 | 键盘可达 + 焦点可见 + Esc 逐级退出 + IME 安全 | KeyMap 单一注册表+启动断言；Esc 逐级；输入框聚焦字母快捷键让位；**IWorkspaceView.TryHandleKey 先给工作区拒绝权**（R-17），shell 只在 false 时处理 | `V2KeyMapTests`、`V2ShellUiTests.ImeSafety_*`、`V2WorkspaceIntegrationTests.ActiveWorkspace_GetsFirstRefusalOnKeys_*`；确认/Esc 路径测试 |
| AC6 | 单测覆盖 VM/状态机/交互规则；`dotnet test` 绿；关键屏截图 | V2 共 85 条全绿（ShellState/KeyMap/DeepLink/Pinyin/Workspace/UI 真渲染/Conformance）；13 张真渲染截图 | `BUILD_TEST.md`、`test.log`、`screens/` |
| AC7 | 证据：构建/测试日志、截图、偏差与未接入清单 | 本目录：README/BUILD_TEST/AC_COVERAGE/DEVIATIONS/NOT_WIRED/CLEANUP、curate.ps1、build.log/test.log、screens/、conformance/ | 本目录全部文件 |

## I1 审查意见 → 处置

| 审查项 | 处置 |
|---|---|
| P1 证据目录污染 | 删除 115 个外任务文件（其中 57 个经 SHA-256 确认字节级重复），重建 20 个本任务证据；改用 R-19 temp-first + `curate.ps1` 显式生成；`CLEANUP.md` 记录可复核命令 |
| P2.2 IWorkspaceView 缺失 | 按契约 §6.1 定义 `Shell/V2/IWorkspaceView.cs`（`Space/CreateContent/OnActivated/OnDeactivated` + R-17 `TryHandleKey`）；Library/Console 由 `WorkspaceAdapters` 实现；`SwitchSpace`/`SetStudioMode` 严格先 deactivate 后 activate；工作区键盘优先 |
| P2.3 滚动保留是假的 | Library/Console 视图订阅 `ScrollChanged` 写回 `ShellState.SpaceViewState`，激活时恢复真实 `ScrollViewer.Offset`；测试断言真实 Offset 跨空间往返 |
| P2.4 C# 裸设计值 | 新增 `ShellLayout`（令牌解析+断点常量）；`PaletteWidth/ConfirmWidth/SearchBoxWidth/SortBoxWidth/DetailPanelWidth/Card*` 等全部改为令牌派生；conformance 扫描扩到 C#（Margin/Padding/Spacing/BorderThickness/Opacity/Brushes/4 值 CornerRadius/布局字面量） |
| P2.5 断点统一（R-18） | `ShellLayout.BreakpointFull=1600/Compact=1280/Narrow=1024`；删除 1400/1200；1280–1599 三列、<1280 覆盖式详情；conformance 断言禁用旧阈值 |
| P2.6 loading 骨架 | 同尺寸骨架网格替换旧「正在读取书架…」自证文案；13 截图 |
| P2.7 ImportDock 措辞 | 改为「请先新建章节（走 Core CreateChapter）」，类注释同步；NOT_WIRED 更新 |
| P2.8 证据强度 | 新增 `Assert.Equal(4, ColumnCount)`、`Assert.Equal(36, TopBand.Bounds.Height)`、滚动真实 Offset、工作区 hook 顺序等断言 |
| P2.9 queued 符号 | 代码 `b4a75d724` 已改 `·`；本目录 DEVIATIONS D-8 已更正并重生成证据 |
| P2.10 杂项 | 删除 `NotWiredCreateChapter` 死常量、AttentionMenu 隐藏假计数；主题管理器统一 `Initialize()`；TopBand 主题入口语义拆分（「主题工作室」+「深色/浅色」快速切换，tooltip 说明） |
| R-19 证据纪律 | 测试默认写 `%TEMP%`；仅显式 `NEWMANGA_EVIDENCE_DIR`/`NEWMANGA_EVIDENCE_SYNC=1` 镜像仓库；唯一文件名；失败重试不炸测试；`curate.ps1` 为仓库证据唯一入口；README 更新复现命令 |
| DS 主题状态共享 | 每个窗口测试前 `TestTheme.ResetToDefaults()`（R-19 补充），消除顺序相关失败 |
