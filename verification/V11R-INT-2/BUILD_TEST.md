# V11R-INT-2 构建与测试记录

执行目录：`apps/desktop-avalonia`；`build.log`/`test.log` 为下述命令原样输出。

## 1. 构建

```
dotnet build NewManga.sln -warnaserror --nologo
```

- exit code：**0**；`0 个警告，0 个错误`

## 2. 全量测试

```
dotnet test NewManga.sln -m:1 --no-build --nologo
```

- exit code：**0**
- `-m:1` 串行基线（并行项目会偶发临时 SQLite `-shm` 争用，既有基础设施问题）

| 测试项目 | 通过 | 跳过 | 失败 | 总计 |
|---|---|---|---|---|
| NewManga.Host.Tests | 49 | 28 | 0 | 77 |
| NewManga.DesignSystem.Tests | 82 | 0 | 0 | 82 |
| NewManga.ThemeEngine.Tests | 235 | 0 | 0 | 235 |
| NewManga.App.Tests | 279 | 7 | 0 | 286 |
| NewManga.CoreClient.Tests | 116 | 25 | 0 | 141 |

## 3. INT-2 专项

```
dotnet test tests\NewManga.App.Tests\NewManga.App.Tests.csproj --filter "FullyQualifiedName~Int2_"
```

5 条全绿：

| 测试 | 覆盖 |
|---|---|
| `Int2_V2Shell_StartsHostBeforeFirstDataRead_AndShowsHostReady` | v2 初始化先 `StartAsync` 再读取；`StartCalls==1`；`Snapshot.State==Ready`；LifecycleLog 中 start 先于 refresh；状态栏“Host 就绪”；重复 await Initialization 不重复启动 |
| `Int2_HostStartFailure_IsSurfacedInStatusBand_WithoutCrashing` | Fake 抛 typed 启动异常 → `HasHostFailure`、状态栏含“Host 启动失败 + 类型/码”，壳不崩 |
| `Int2_VariantDarkAndLight_ResolveDifferentTokensAndScreenshots` | dark/light 两 manager 下 `Nm.Color.Bg.App` 不同、截图 SHA-256 不同；壳标签同步 |
| `Int2_SingleHostStartup_CallSites_AreOnlyTheLegacyShellAndTheV2ViewModel` | 源码扫描：legacy `MainWindow` 1 处 `_controller.StartAsync(`、v2 VM 1 处、App 无直接启动 → legacy 不重复启动 |
| `Int2_LibraryCenterState_HasExactlyOneVisibleBlock_ForEveryCombination` | 5 组合下状态容器内可见 EmptyState 数：HostNotReady=1、Ready+空库=1、Loading=0（骨架≥4）、Error=1、筛选无结果=1 |

V2 全量回归：150 条全绿。

## 4. 真实 sidecar 取证命令（`--key=value`）

```powershell
cd apps/desktop-avalonia
dotnet build src/NewManga.App/NewManga.App.csproj
dotnet run --project src/NewManga.App --no-build -- --shell=v2 --variant=dark --width=1600 --height=1000 `
  --sidecar-dir="G:\CODEX\New Manga\apps\desktop-avalonia\build\sidecar\core-sidecar\core-sidecar" `
  --data-root="C:\Temp\int2-data-dark" --log-dir="C:\Temp\int2-logs-dark" --exit-after=150000
```

- Host ready 证据：`logs/dark/host.log`、`logs/light/host.log`（`core_service ready` / `host_bridge ready` / self-check Degraded / host-control session）
- 真实窗口截图：`screens/int2-real-sidecar-host-ready-dark.png`（1567×1009，桌面宽度上限）、`-light.png`
- data-root：启动后创建并由 Core 使用（路径见命令；日志 `data_root=` 行）

## 5. 证据生成（R-19）

```
pwsh -NoProfile -File verification/V11R-INT-2/curate.ps1
```

- 普通测试只写 `%TEMP%/newmanga-evidence/V11R-INT-2/`；显式 `NEWMANGA_EVIDENCE_SYNC=1` 才镜像仓库。
- 脚本只重生成 headless 截图（6 张）；真实窗口图与 L4 修复前参考图保留。

## 6. NOT RUN

| 项 | 原因 |
|---|---|
| L4 实机启动矩阵全量复跑（7 组合） | 本证据覆盖 v2 真实 sidecar 启动 + dark/light 真实窗口；矩阵由 Lead/INT-1 在合并后复跑 |
| 安装包/发布产物启动 | 发布流程归 Lead |
