# V11R-INT-2 验收覆盖

| 项 | 要求 | 实现 | 证据 |
|---|---|---|---|
| INT2-AC1 | v2 默认壳必须启动 Host；唯一启动点、幂等；legacy 不重复启动 | `AppShellViewModel.InitializeCoreAsync` 先 `StartAsync` 再 `Library.InitializeAsync`；`HostController.StartAsync` 记录 `StartRequests` 并复用单个 `_startTask`；legacy `MainWindow.OnLoaded` 仍是唯一 legacy 调用点 | `Int2_V2Shell_StartsHostBeforeFirstDataRead_AndShowsHostReady`；`Int2_SingleHostStartup_CallSites_*`；真实窗口 + `logs/*/host.log` |
| INT2-AC2 | 启动失败/只读原因呈现在状态栏，不吞、不崩 | `HostStatusLine` 显示 `Failed` 的 `ErrorCode/ErrorMessage` 或 `ReadOnlyReason`；`HasHostFailure`；`StatusBandState` Failed/Blocked/Done；typed 抛出也被捕获并显示 | `Int2_HostStartFailure_IsSurfacedInStatusBand_WithoutCrashing`；`04-int2-host-start-failure` 截图 |
| INT2-AC3 | `--variant` dark/light 必须生效且不同 | 壳构造采用 DS manager 已应用外观；Theme Studio 异步 persisted 设置后重新应用显式 `--variant` 并同步标签 | `Int2_VariantDarkAndLight_ResolveDifferentTokensAndScreenshots`（token 值 + 截图哈希不同）；真实 dark/light 窗口图 |
| INT2-AC4 | 资料柜空态/骨架/错误块任意组合恰有一个可见，不叠印 | 互斥状态选择器 + 单一 `LibraryCenterStateHost` 容器；加载骨架 `ShowLoadingState`；HostNotReady 优先、错误优先于空态、无结果仅在 ready+有数据 | `Int2_LibraryCenterState_HasExactlyOneVisibleBlock_ForEveryCombination`（5 组合渲染树计数）；`05`/`06` 截图；`pre-fix-*` 旧图对照 |
| INT2-AC5 | 真实 sidecar 启动后“Host 就绪”证据 | 真实 AGPL sidecar + `--key=value` CLI；窗口截图左下角“Host 就绪”；host.log 显示 core_service/host_bridge ready 与 host-control session | `screens/int2-real-sidecar-*`；`logs/dark|light/host.log`；`host-ready.json` |
| INT2-AC6 | 全量测试/build 绿 | `dotnet build -warnaserror` 0W/0E；`dotnet test -m:1` 全绿（App 286 等） | `BUILD_TEST.md`；`build.log`/`test.log` |
| INT2-AC7 | 证据按 R-19 | `curate.ps1` 唯一入口；headless 6 张 + 真实窗口 2 张 + 修复前参考 1 张；temp-first | `curate.ps1`；本目录 |

## 与 B-1/B-2/INT-0 的回归

- V2 全量 150 条全绿（含 B-1/B-2/INT-0 及本任务新增）。
- B-1 的“StatusBand 仅活动时可见”被本任务 P0 要求取代（始终可见的就绪通道），`Int0_StatusBand_*` 与相关断言已按新语义更新。
- B-2 的 R-24 轮询/词表测试保持绿。
