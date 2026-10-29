# V11R-INT-0 未接入能力清单（诚实降级，壳全部标注）

| # | 能力 | 现状 | UI 呈现 | 依赖 |
|---|---|---|---|---|
| 1 | Theme Studio 7 分区内容 | 壳只提供 `ISurfaceWorkspace` seam + 表面栈生命周期；C-2 尚未交付 | 打开表面显示「主题中心 / 尚未注册：V11R-C-2 …」，不显示伪造编辑器 | V11R-C-2 / INT-1 注册实现 |
| 2 | `MainWindow` 默认入口 | `CreateRoot` 已就绪；旧 `MainWindow.axaml`/`App.axaml.cs` 未改 | 本任务只提供独立窗口工厂与测试证据 | V11R-INT-1 |
| 3 | Studio Batch 的共享 Run poller（R-24 全覆盖） | StatusBand + Console 已共享 `RunStatusMonitor`；Batch 仍由其 VM 直接读取 `IRunController`（B-4 所有权） | Batch 显示自身真实 Run 投影（不伪造）；无重复 UI 数字 | INT-1 轮询统一 |
| 4 | 真实 Core sidecar 端到端（Studio 载入真实页/图、StatusBand 真实 Run） | 测试用 `FakeHostController`（真实 DTO/命令记录）；生产由 INT-1 启动链路提供 Host | Studio 空章节/无图显示诚实空态；StatusBand 无 Run 隐藏 | INT-1 E2E 冒烟 |
| 5 | 控制台/资料柜的表单级未接入项 | 见 `verification/V11R-B-1/NOT_WIRED.md`、`verification/V11R-B-2/NOT_WIRED.md` | 沿用其诚实标注 | 对应后端任务 |
| 6 | 主题表面深链接 | `ShellDeepLink` 已有 space/book/chapter/page；ThemeStudio 表面未纳入深链接 | 入口仅 TopBand/Ctrl+, | INT-1/C-2 可扩展 |
