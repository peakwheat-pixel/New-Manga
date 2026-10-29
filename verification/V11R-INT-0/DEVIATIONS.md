# V11R-INT-0 偏差记录

| ID | 规格/契约 | 实际实现 | 理由 | 影响 |
|---|---|---|---|---|
| INT-0-D1 | R-18 / D-14：断点来自 DS | `ShellLayout.BreakpointFull/Compact/Narrow` 改为 `Size(NmKeys.Size.Breakpoint.*)`，删除本地 1600/1280/1024 常量；conformance 断点测试改 `[AvaloniaFact]` 读资源并断言 token key | DS Breakpoint 令牌已合入 main（Lead 通知） | D-14 关闭；DS 改值时 UI 自动跟随 |
| INT-0-D2 | R-24：Run 快照同源、不重复轮询 | 新增 `RunStatusMonitor` 单实例（1s poller + snapshot/projection 缓存 + in-flight 合并）；StatusBand 与 Console 共享；Console 的 `IsRunPollingEnabled/StopRunPolling` 变为共享 poller 测试开关 | 避免 Console + StatusBand 两套 timer 双读 Host | Console Run 行为不变；Batch 的 Run 源仍独立（见 D4） |
| INT-0-D3 | 契约 §6.3 Tab = Studio 模式切换；R-17 工作区优先 | Studio adapter 消费 Tab：调用 `StudioWorkspaceView.SwitchMode`（守卫感知）成功后同步 `ShellState.SetStudioMode`；shell 侧 `ModeChanged` 再回写 Studio（单向防循环） | 两套模式表示需要单一事实源 | Tab 在 Studio 内生效；其它空间仍由 shell KeyMap 处理 |
| INT-0-D4 | R-24 与 Studio Batch | Batch 的 Run 数据仍由 B-3/B-4 `StudioBatchViewModel` 直接读 `IRunController`（其所有权）；本任务共享 poller 覆盖 StatusBand + Console | 不改 ui-studio 既有 Batch VM，避免跨 Owner 改动 | INT-1「轮询统一」再把 Batch 接入 `RunStatusMonitor`（已列为 TODO） |
| INT-0-D5 | AC2：切换不丢显式多选（R-16） | Studio 加载会按 book/chapter 重设 `ShellState.Selection`，adapter 在激活/停用/加载完成边界恢复进入时捕获的 MultiPage（仅在当前为空时） | `StudioSelection.SetContext` 会重建 selection，属 ui-studio 既有行为 | 多选不因进入 Studio 丢失；若用户在 Studio 内主动改选，以新选择为准 |
| INT-0-D6 | ThemeStudio 表面 | 未注册时显示「主题中心 / 尚未注册（V11R-C-2）」占位；实现通过 `ISurfaceWorkspace` + `RegisterSurfaceWorkspace` 注入；TopBand 入口/Ctrl+,/Esc 已可用 | C-2 尚未交付，不伪造主题编辑器 | INT-1/C-2 直接注册即可，不改壳 |
| INT-0-D7 | CreateRoot 与 MainWindow | 工厂不读 MainWindow、不启动 sidecar；窗口几何取 `AppOptions.WindowWidth/Height`（默认 1100×760），MinWidth 用 DS Narrow 令牌 | INT-1 负责切默认入口与启动链路 | 无；INT-1 可直接 `AppShellV2.CreateRoot(host, options)` |
| INT-0-D8 | 未注册工作区占位 | `V2WorkspaceHost` 对 Library/Console/Studio 都提供「未注册」占位；Studio 反注册测试覆盖 | B-1 只对 Library/Console 做过；Studio 由本任务补 | 无假工作区 |
| INT-0-D9 | 旧 StudioPendingView / ThemeStudioPendingView | 删除两个占位控件，代之以真实 ContentControl + WorkspacePlaceholderView | 占位由 shell 统一提供，避免第二套占位 | B-1 证据中的 09-studio-pending 为历史产物，INT-0 证据 15 起为真实 Studio |
| INT-0-D10 | 证据 | R-19：`curate.ps1` 唯一入口、截图唯一命名、temp-first；本目录 6 张截图 | Lead R-19 纪律 | 普通测试不写仓库 |
