# V11R-INT-0 证据：壳集成（CreateRoot / 内置工作区 / ThemeStudio 表面栈 / 共享 Run StatusBand）

- Task: `doc/tasks/V11R-INT-0.md`（task-14，Owner `ui-shell`）
- Branch: `v11r/ui-shell`；前置：B-1 I1、B-2、B-3 I2c（StudioWorkspaceView）、DS Breakpoint 令牌
- 本任务不切 `MainWindow`（INT-1 负责），只提供可独立承载的 `AppShellV2.CreateRoot(...)` 与全部集成 seam。
- 渲染：Avalonia Headless + Skia，`[AvaloniaFact]` 真窗口 `CaptureRenderedFrame()`；每张 PNG > 4KB 断言

## 1. 交付

| 项 | 实现 |
|---|---|
| `AppShellV2.CreateRoot(IHostController, AppOptions)` | 独立窗口工厂：`Title/Width/Height`（取 AppOptions）、`MinWidth = Nm.Size.Breakpoint.Narrow`、窗口背景走 `Nm.Color.Bg.App` 令牌；不依赖 MainWindow/App 启动流程 |
| 内置工作区注册 | `LibraryWorkspaceView`（B-1）、`ConsoleWorkspaceView`（B-2）、**`StudioWorkspaceAdapter`**（B-3 I2c 的 `StudioWorkspaceView`，`Activate/Deactivate/LoadAndRenderAsync/SwitchMode`）；三者各创建一次，切换只换可见性 |
| Studio 空间路由 | 真实 Studio 表面渲染；面包屑/选择来自共享 `ShellState.Selection`（`StudioSelection` 投影）；Tab 由 Studio 首拒绝并**同步** shell `StudioMode`（守卫感知）；J/K/[ ]/+/-/0 走 `StudioKeyboard`；空章节诚实空态 |
| ThemeStudio 表面栈 | `ISurfaceWorkspace` seam + `ShellState` 表面工作区注册表（Push/CloseTop/CloseSurfaces 调 OnActivated/OnDeactivated）；未注册时显示「主题中心 / 尚未注册：V11R-C-2 …」占位，不伪造编辑器；TopBand 入口 / Ctrl+, / Esc 可用 |
| 未注册工作区 | `IWorkspaceView` 未注册时显示「尚未注册」占位且不渲染内容（测试：反注册 Studio 后 Ctrl+2 验证） |
| StatusBand Run 源（R-24） | 新增 `RunStatusMonitor`：单一 1s poller + 单一快照/投影来源；StatusBand 与 Console 共用（Console 删除自己的 `DispatcherTimer`，`LoadRun` 由 monitor 共享首次读取，无重复请求）；无 Run 隐藏；Console 的 `IsRunPollingEnabled`/`StopRunPolling` 映射到共享 poller 的测试开关 |
| D-14 关闭 | `ShellLayout.BreakpointFull/Compact/Narrow` 改为读 `NmKeys.Size.Breakpoint.*`（DS token 1600/1280/1024），无本地字面量；conformance 断点测试改 `[AvaloniaFact]` 读 DS 源并断言 token key |
| 工作区上下文 | 三空间往返不重建 VM；selection/search/scroll 保持；Studio 加载不吞 shell 多选（R-16 显式选择优先，adapter 在加载/停用边界恢复） |

## 2. 截图（`screens/`，6 张，R-19 命名 `<TestName>--<name>.png`）

| 文件（含 TestName 前缀） | 证明 |
|---|---|
| `Int0_CreateRoot_BuildsStandaloneWindow_WithBuiltInWorkspaces--14-int0-create-root.png` | CreateRoot 独立窗口：三内置工作区注册、真实 Library 渲染 |
| `Int0_StudioSpace_RendersRealSurface_TabStaysInStudio--15-int0-studio-page.png` | Studio 真实表面（B-3 I2c）：页面模式、章节账本、空页面诚实态 |
| `Int0_StudioSpace_RendersRealSurface_TabStaysInStudio--19-int0-three-spaces-context.png` | Studio→Library 返回后上下文保持（不重建） |
| `Int0_ThemeStudio_OpensAsHonestPlaceholder_AndEscCloses--16-int0-theme-studio-placeholder.png` | ThemeStudio 未注册占位（不伪造内容），Esc 关闭 |
| `Int0_StatusBand_UsesSharedRunMonitor_AndHidesWithoutRun--17-int0-statusband-run.png` | StatusBand 显示共享 Run 快照（Run · 进行中 · 50% · run-1） |
| `Int0_UnregisteredStudio_ShowsHonestPlaceholder_NoFakeWorkspace--18-int0-studio-unregistered.png` | 反注册 Studio 后的诚实占位，无假工作区 |

## 3. 复现命令

```powershell
cd apps/desktop-avalonia
dotnet build NewManga.sln -warnaserror
dotnet test NewManga.sln -m:1 --no-build

# INT-0 仓库证据唯一入口（R-19，显式 NEWMANGA_EVIDENCE_SYNC=1）
pwsh -NoProfile -File ../../verification/V11R-INT-0/curate.ps1
```

| 证据 | 内容 |
|---|---|
| `BUILD_TEST.md` / `test.log` | 命令、exit code、计数、V2/INT-0 明细 |
| `screens/` | 6 张真渲染截图（上述） |
| `AC_COVERAGE.md` | INT-0 AC → 代码/测试/截图 |
| `DEVIATIONS.md` | D-14 关闭、R-24、Studio 模式同步、多选保留、Batch Run 共享 follow-up |
| `NOT_WIRED.md` | ThemeStudio（C-2）、MainWindow（INT-1）、真实 Core E2E |

## 4. 边界

- 未改 `MainWindow.axaml` / `App.axaml.cs`（INT-1 负责切换到 `CreateRoot`）。
- 未实现 Theme Studio 内容（C-2/INT-1 通过 `RegisterSurfaceWorkspace` 注册）。
- Studio Batch 的 Run 数据仍由 ui-studio 的 Batch VM 直接读 `IRunController`（B-4 所有权）；R-24 的共享 poller 已覆盖 StatusBand + Console，Batch 接入共享 monitor 列入 INT-1 统一轮询项。
