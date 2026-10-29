# V11R-INT-0 验收覆盖（AC → 代码/测试/截图）

| AC | 要求 | 实现 | 证据 |
|---|---|---|---|
| AC1 | 壳可独立构造并承载（不依赖 MainWindow），INT-1 可直接切默认入口 | `AppShellV2.CreateRoot(IHostController, AppOptions)` 工厂：标题/尺寸取 AppOptions，MinWidth 读 `Nm.Size.Breakpoint.Narrow`，背景走 `Nm.Color.Bg.App`；构造即完成 DS 主题初始化 | 测试 `Int0_CreateRoot_*`；截图 14 |
| AC2 | 内置注册 Library/Console/Studio，Studio 用 ui-studio I2c 适配；未注册诚实占位 | `IWorkspaceView` 注册表 + `StudioWorkspaceAdapter`（`StudioWorkspaceView` + `Activate/Deactivate/LoadAndRenderAsync/SwitchMode`）；未注册显示「尚未注册」占位、无内容 | 测试 `Int0_StudioSpace_*`、`Int0_UnregisteredStudio_*`；截图 15/18/19 |
| AC3 | ThemeStudio 表面栈入口（TopBand + Ctrl+,）+ 未注册占位 | `ISurfaceWorkspace` seam + `ShellState` 表面工作区注册表（Push/CloseTop/CloseSurfaces 生命周期 hook）；AppShellV2 的 ThemeStudio 表面改为 ContentControl(注册实现) + 占位；TopBand 入口 / Ctrl+, / Esc 可用 | 测试 `Int0_ThemeStudio_*`；截图 16 |
| AC4 | StatusBand 接 `IRunController` 快照（无 Run 隐藏），与 Console/Batch 同源且不重复轮询（R-24） | `RunStatusMonitor` 拥有唯一 1s poller 与快照/投影缓存；StatusBand 与 Console 订阅同一实例；Console 删除私有 `DispatcherTimer`，LoadRun 共享首次读取（测试断言单次快照/投影请求）；无 Run → 隐藏 | 测试 `Int0_StatusBand_*`；截图 17；`V2ConsoleUiTests.Tasks_*`（R-24 请求计数） |
| AC5 | R-17 仲裁：Studio 空间 Tab/Esc/J/K/[ ]/+/-/0 交 Studio | `StudioWorkspaceAdapter.TryHandleKey` → `StudioKeyboard.Handle`；Tab 由 Studio 守卫感知切换并同步 `ShellState.StudioMode`；shell 仅在 false 时处理 | 测试 `Int0_StudioSpace_*`（Tab → Studio Batch + shell 模式同步）；B-3 I2c Studio 键盘测试 |
| AC6 | 三空间切换保上下文、不重建 VM | 内置工作区各创建一次；StudioSelection 投影 `ShellState.Selection`；Studio 加载不吞显式多选（adapter 加载/停用边界恢复）；scroll/filter 由 B-1/B-2 hooks 保持 | 测试 `Int0_StudioSpace_*`（返回 Library selection 保持）、`Int0_ThemeStudio_*`（上下文不变）；截图 19 |
| AC7 | D-14 关闭：断点来自 DS 令牌 | `ShellLayout.BreakpointFull/Compact/Narrow => Size(NmKeys.Size.Breakpoint.*)`；conformance `[AvaloniaFact]` 断言 1600/1280/1024 与 token key | `V2ConformanceTests.ResponsiveBreakpoints_ComeFromDesignSystemTokens_*`；`V2ShellUiTests` 1280/1024 布局断言 |
| AC8 | 证据（构建/测试/截图/偏差/未接入） | 本目录 + `curate.ps1`（R-19 唯一入口）+ 6 张真渲染截图 | 本目录全部 |

## 边界（与 INT-1 的分工）

- `MainWindow.axaml` / `App.axaml.cs` 未改；INT-1 将默认入口切到 `CreateRoot`。
- Theme Studio 7 分区内容未实现（C-2）；INT-1 通过 `RegisterSurfaceWorkspace` 注入。
- Studio Batch 的 Run 数据仍由 B-3/B-4 Batch VM 直接读 `IRunController`；R-24 共享 poller 已覆盖 StatusBand + Console，Batch 接入属 INT-1「轮询统一」。
