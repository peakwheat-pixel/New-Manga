# V11R-INT-2 证据：v2 默认壳 Host 启动 P0 + 真实空态叠印 P1 + `--variant` 修复

- Task: `doc/tasks/V11R-INT-2.md`（发布前硬阻塞；Owner `ui-shell`）
- 日期：2026-10-30
- 分支：`v11r/ui-shell`（基于 main L4 后 HEAD；未 push）
- 前端：Avalonia 11 + DS 令牌；真实窗口证据使用真实 AGPL sidecar（`build/sidecar/core-sidecar/core-sidecar`）
- CLI 约定：**必须 `--key=value`**（`--sidecar-dir=` / `--data-root=` / `--log-dir=`）；空格形式会被解析为 `"true"`（core-bridge 另行修，本任务按正确形式取证）

## 1. P0：v2 默认壳从不启动 Host（已修）

修复前：`verification/V11R-L4-EVIDENCE/host-readiness.md` 记录 v2 链路无任何 `StartAsync()`，Host 永远 Starting，无 host.log / data-root，状态栏常驻“Host 未就绪”，默认安装数据面全不可用。

修复：
- `AppShellViewModel.InitializeCoreAsync` 现为 **Start → 数据读取**：先 `await _controller.StartAsync(...)`（v2 唯一启动点），再 `Library.InitializeAsync()`；`HostController.StartAsync` 幂等（`StartRequests` 计数、单次 `_startTask`），legacy 仍只启动一次。
- 失败不吞：`HostViewSnapshot.State/ErrorCode/ErrorMessage/ReadOnlyReason` 呈现在状态栏（`HostStatusLine` / `HasHostFailure` / `StatusBandState`）；`StartAsync` 抛出的 typed 异常也会显示为“Host 启动失败（…）”并保持壳可用。
- StatusBand 改为**始终可见**的就绪通道：有 Run 显示 Run，有导入显示导入，否则显示 Host 状态（“Host 就绪”/失败/只读原因）。这取代 B-1 的“仅活动时显形”行为（见 DEVIATIONS D-INT2-1）。
- `HostController.Changed` 始终 marshal 到 UI 线程（真实窗口曾因此抛 `Call from invalid thread`，导致 Host 实际就绪但状态栏显示失败）。

真实窗口证据（真实 sidecar，Host 实际 ready）：
- `screens/int2-real-sidecar-host-ready-dark.png`（深色；左下角 “● Host 就绪”）
- `screens/int2-real-sidecar-host-ready-light.png`（浅色；同一真实 sidecar）
- `logs/dark/host.log`、`logs/light/host.log`：含 `core_service ready`、`host_bridge ready`、`host-control session opened`、`self-check status=Degraded code=- detail=core_protocol=2.3 required_minor=3`
- data-root 在启动后创建（命令见 BUILD_TEST §4）

> 窗口截图 1567×1009：请求 `--width=1600 --height=1000`，但本机桌面可用宽度只有 1567，Windows 将窗口钳制到屏幕；这是环境限制，不是 UI 回归（headless 证据仍为 1600×1000）。

## 2. P1：资料柜空态多块同时可见并叠印（已修）

缺陷：`LibraryView.axaml` 原 4 个 `<Grid IsVisible=...>` 兄弟节点（HostNotReady / IsEmptyLibrary / HasError / HasNoResults）可同时为 true，Host 未就绪 + 空库时正文/标题叠印。

修复：
- 状态选择器严格互斥（优先级）：`ShowHostNotReadyState` → `ShowLoadingState` → `ShowErrorState` → `ShowEmptyLibraryState` → `ShowNoResultsState` → `ShowBooksGrid`；`HostNotReady` 时不再显示空库；筛选无结果仅在 Host ready + 有数据时成立。
- XAML 改为**一个状态容器** `LibraryCenterStateHost`（`ShowEmptyState` 控制可见性），内部 4 个块由互斥属性控制；加载骨架改用 `ShowLoadingState`。任意组合下恰有一个空态/骨架/错误块。
- 测试 `Int2_LibraryCenterState_HasExactlyOneVisibleBlock_ForEveryCombination` 逐组合断言渲染树中可见 `EmptyState` 数量（作用域=状态容器）：HostNotReady+空库→仅 Host 空态；Ready+空库→仅书架空态；Loading→0 空态+同尺寸骨架；Error→仅错误块；有数据+筛选无结果→仅无结果。
- 修复前参考图：`screens/pre-fix-host-not-ready-multi-empty-state-l4.png`（来自 `verification/V11R-L4-EVIDENCE/screens/host-readiness-v2.png`，可见多串文字叠印；本任务真实窗口修复后只显示一个“书架还是空的”）。

## 3. P1：`--variant` 不生效（已修）

原因：`AppShellV2` 构造时用 VM 默认外观覆盖了 DS manager 已应用的 startup appearance；且 Theme Studio 服务异步应用 persisted 设置后再次覆盖、且未回写壳标签。

修复：
- `AppShellV2` 构造时 `AdoptAppearance(_themeManager.Appearance == Dark)`（不强制默认）。
- `App.CreateV2Shell` 在 Theme Studio `InitializeAsync` 完成后，若显式 `--variant` 存在则重新 `SetAppearance(requested)`（显式启动参数优先于 persisted 默认），并同步壳标签。
- 测试 `Int2_VariantDarkAndLight_ResolveDifferentTokensAndScreenshots`：dark/light 两态下 `Nm.Color.Bg.App` 解析值不同、截图 SHA-256 不同；真实窗口 dark/light 证据亦为不同哈希。

## 4. 测试

- 5 条 INT-2 测试全绿：启动顺序/就绪、启动失败状态栏、dark/light 令牌与截图哈希、启动调用点唯一性、空态互斥（5 组合）。
- V2 全量 150 条全绿；全量 `dotnet test NewManga.sln -m:1` 绿（见 BUILD_TEST.md）。

## 5. 证据文件

| 文件 | 内容 |
|---|---|
| `screens/Int2_*--01..06-*.png` | headless 真渲染：Host 就绪 / 启动失败 / dark / light / 空库单块 / loading 单块 |
| `screens/int2-real-sidecar-host-ready-dark.png` / `-light.png` | 真实窗口 + 真实 sidecar，Host 就绪；dark/light 差异 |
| `screens/pre-fix-host-not-ready-multi-empty-state-l4.png` | 修复前 L4 证据（多空态叠印参考） |
| `logs/dark/host.log`、`logs/light/host.log` | 真实 sidecar 启动日志（ready、self-check） |
| `curate.ps1` | R-19 唯一证据生成入口（保留手工真实窗口图，重生成 headless 截图） |
| `BUILD_TEST.md` / `build.log` / `test.log` | 命令、exit code、计数 |
| `AC_COVERAGE.md` / `DEVIATIONS.md` / `NOT_WIRED.md` | AC 映射 / 偏差 / 边界 |

## 6. 复现命令

```powershell
cd apps/desktop-avalonia
dotnet build NewManga.sln -warnaserror
dotnet test NewManga.sln -m:1 --no-build

# headless INT-2 证据（真实窗口图与 pre-fix 参考图保留）
pwsh -NoProfile -File ../../verification/V11R-INT-2/curate.ps1

# 真实 sidecar（--key=value 形式；路径按本机）
dotnet run --project src/NewManga.App --no-build -- --shell=v2 --variant=dark --width=1600 --height=1000 `
  --sidecar-dir="G:\CODEX\New Manga\apps\desktop-avalonia\build\sidecar\core-sidecar\core-sidecar" `
  --data-root="$env:TEMP\int2-data" --log-dir="$env:TEMP\int2-logs" --exit-after=150000
```

## 7. 边界

- 未改 Theme Studio 内容、Studio Batch、legacy 壳行为；legacy 仍单次启动 Host（代码扫描测试守护）。
- CLI 空格形式解析属 core-bridge；本证据使用 `--key=value`。
- L4 实机矩阵复跑由 Lead/INT-1 在合入后执行（本证据提供真实 sidecar 启动与 dark/light 真实窗口图）。
