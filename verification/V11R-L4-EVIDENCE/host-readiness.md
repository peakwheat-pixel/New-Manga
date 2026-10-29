# Host 就绪真实性核查（V11R-L4-EVIDENCE 追加项）

- 日期：2026-10-30（UTC 2026-10-29）
- 分支：`v11r/core-bridge`，核查时 HEAD `287705e653d490941c6acf310d1acc2304355f05`（已含 INT-0/INT-1 与 A-6 自检）
- 核查人：`core-bridge`（Owner，未自审）
- 结论：**两个独立缺陷叠加**，不是单一"环境问题"：
  1. **P0：v2 壳（当前默认 `--shell=v2`）从不启动 Host**——不调用 `IHostController.StartAsync()`，因此
     没有 `host.log`、不创建 `--data-root`、状态栏永远"Host 未就绪：等待 Core sidecar"，进程 exit 0。
  2. **P1：CLI 只接受 `--key=value`，`--key value` 被静默误解析**——Lead 复现命令里
     `--sidecar-dir "G:\...\core-sidecar"` 被解析成 `sidecar_dir="true"`、后续路径 token 被忽略；
     `--data-root`/`--log-dir` 同样变成字符串 `true`（相对目录），所以指定目录不存在，反而在
     `<app cwd>\true\host.log` 出现日志。两者都没有任何 `InvalidReason` 报错。
- 用正确写法（`--key=value`）+ 同一 AGPL sidecar + legacy 壳 → **Host 真实就绪**（截图/日志见 §3）。
  A-6 自检不是原因：正确启动时自检为 `Degraded`（ReadWrite），没有 `ReadOnlyReason` 降级。

## 1. 复现与证据（全部真实执行）

### 1.1 Lead 的写法（空格分隔值）→ 静默误解析

```powershell
dotnet run --project src/NewManga.App --no-build -- --shell=legacy --exit-after=6000 `
  --data-root "C:\temp\l4\data" --log-dir "C:\temp\l4\logs" `
  --sidecar-dir "G:\CODEX\New Manga.workspace\task-envs\AGPL-RELEASE-1\out\NewManga-0.1.0-win-x64\app\core-sidecar"
```

实测（exit 0）：

- `C:\temp\l4\data` / `C:\temp\l4\logs` **不存在**；
- 日志实际落在 `apps/desktop-avalonia/true/host.log`（`--log-dir` 被解析成相对目录 `true`），内容：
  - `mode=ReadWrite ... data_root=true`
  - `ERROR code=SidecarBundleMissing ... no sidecar directory with core_service.exe and host_bridge.exe found in 3 candidate locations`
- 证据：`logs/host-readiness/space-form-true-host.log`

根因：`AppOptions.Parse` 只用 `=` 切分（`AppOptions.cs:78-84`），无 `=` 的 `--key` 被当作
`--key=true`，后续独立 token（如引号包住的路径）不以 `--` 开头，被直接忽略；没有 InvalidReason。

### 1.2 正确写法（`--key=value`）+ AGPL sidecar

| 壳 | exit | 窗口 | host.log | Host 就绪 | data-root 创建 |
|---|---:|---|---|---|---|
| `--shell=legacy` | 0 | 有（"New Manga"） | 有 | **是**（`core_service ready` + `mode=ReadWrite` + `self-check status=Degraded`） | 是 |
| `--shell=v2`（默认） | 0 | 有 | **无** | **否**（状态栏"Host 未就绪：等待 Core sidecar"） | 否 |

- legacy 截图：`screens/host-readiness-legacy.png`（右上角 **Host 就绪**，底部"Core 返回空书架"）
- v2 截图：`screens/host-readiness-v2.png`（左下角"Host 未就绪：等待 Core sidecar"）
- legacy host.log：`logs/host-readiness/legacy/host.log`（含 core_service/host_bridge ready、host-control
  session、`self-check status=Degraded code=- detail=core_protocol=2.3 required_minor=3`）
- 机器可读汇总：`host-readiness.json`

### 1.3 空 `--log-dir=`（边界）→ 启动错误被二次崩溃掩盖

`--log-dir=`（空值）时：HostLog 构造 `Directory.CreateDirectory("")` 抛 `ArgumentException`，legacy 壳的
`async void OnLoaded` 未捕获 → Avalonia 生命周期抛出 → `Program.Main` catch → `Program.WriteFatal` 又对空
路径 `Directory.CreateDirectory` → **未处理异常**，进程 `exit=-532462766`，没有任何 fatal 日志。
证据：`logs/host-readiness/writefatal-empty-logdir.log`。

## 2. 确切失败点（代码定位）

### 2.1 v2 壳不启动 Host（P0）

启动链路：

1. `App.axaml.cs:63-66` 创建 `HostController` 后按 `UseV2Shell` 选择壳；
2. v2：`CreateV2Shell` → `AppShellV2.CreateRoot`（`App.axaml.cs:101-103`）；
3. `AppShellV2.OnAttachedToVisualTree` → `InitializeWithDeepLinkAsync`（`AppShellV2.axaml.cs:120-147`）；
4. `AppShellViewModel.InitializeCoreAsync`（`ViewModels/V2/Shell/AppShellViewModel.cs:573-577`）
   只调用 `Library.InitializeAsync()`；
5. `LibraryViewModel.InitializeAsync`（`ViewModels/V2/Library/LibraryViewModel.cs:516-525`）→ `RefreshAsync`
   → `_controller.RefreshBooksAsync(...)`；
6. `HostController.RefreshBooksAsync`（`Services/HostController.cs:66-70`）在 `_runtime is null` 时**直接返回**；
7. 全代码库中 `_controller.StartAsync()` 的唯一调用点是 legacy 壳
   `Views/MainWindow.axaml.cs:764-766`（`OnLoaded`）。

结论：v2 初始化路径没有任何 `StartAsync()`；Host 永远不会启动。INT-1 把 v2 设为默认后，默认安装即
"窗口能开、数据面全不可用"，且没有错误提示（状态栏停留在 Starting 文案）。

**建议修复（需产品代码，本卡不改）**：在 v2 初始化中显式启动一次 Host，例如
`AppShellViewModel.InitializeCoreAsync` 开头 `await _controller.StartAsync();`（或
`App.axaml.cs` 建窗后启动），失败时把 `HostViewSnapshot.State/ErrorCode/ReadOnlyReason` 呈现到状态栏；
并补一条 headless 测试断言"v2 初始化后 Snapshot.State != Starting 且 host.log 存在"。

### 2.2 CLI 空格分隔值被静默忽略（P1）

`AppOptions.Parse`（`AppOptions.cs:76-84`）把 `raw` 按第一个 `=` 拆成 key/value；无 `=` 时
`value = "true"`。`--sidecar-dir "C:\path"` 是两个 argv：`--sidecar-dir` → `SidecarDirectory="true"`，
`"C:\path"` 不以 `--` 开头 → `continue` 丢弃。`--data-root`/`--log-dir` 同理 → `DataRoot="true"`、
`LogDirectory="true"`（相对 cwd）。全程无 InvalidReason、无警告。

**建议修复**：要么支持 `--key value` 形式，要么对"无 `=` 的已知选项"和"未知位置参数"设置
`InvalidReason` 并以 exit 2 失败（`Program.Main` 已有 invalid-arguments 分支），避免静默降级。

### 2.3 data-root 创建时机（解释 Lead 的目录缺失）

`HostRuntime.StartInternalAsync`：先 `new HostLog(options.LogDirectory)`（HostLog 构造里
`Directory.CreateDirectory(logDirectory)`，`HostLog.cs:14-25`）→ 然后 `SidecarLocator.Locate`
（`HostRuntime.cs:512-521`）→ 通过后才 `Directory.CreateDirectory(derived/managed/catalog)`
（`HostRuntime.cs:523-528`）。所以 sidecar 定位失败时：**日志目录会建**（在解析出的路径上），
**data-root 不会建**。Lead 看到的"目录完全没建"是 §2.2 误解析（实际建在 `true\`）叠加 §2.1（v2 根本不启动）
的结果。

### 2.4 A-6 自检未参与本次故障

正确写法下自检输出 `self-check status=Degraded code=- detail=core_protocol=2.3 required_minor=3`，
写入保持开启（`mode=ReadWrite`），无 `ReadOnlyReason`；因此不是自检降级导致未就绪。

### 2.5 观察：v2 的 `--variant` 无视觉差异

六组矩阵中 dark/light 截图 **SHA-256 完全相同**（`launch-matrix.json`/`screens/`），v2 壳下
`--variant=dark|light` 没有可见差异（legacy 壳走 ThemePackService 会应用）。可能属于 DS 主题栈
尚未接 `StartupVariant`（`App.axaml.cs:52-61` 只把它传给 `DesignSystemThemeManager.Initialize`），
建议 owner（design-platform / ui-shell）核实；本卡仅记录，不判定为缺陷。

## 3. 结论（给 Lead）

| 项 | 结论 |
|---|---|
| Lead 的 AGPL sidecar 是否可用 | **可用**：`=` 写法 + legacy 壳 → Host 就绪、data-root 创建、自检 Degraded/ReadWrite |
| 为什么窗口能开但未就绪 | ① v2 默认壳从不启动 Host（P0）；② Lead 命令的空格写法被静默误解析（P1） |
| 是否需要产品修复 | **需要**：v2 启动 Host（P0，阻断默认壳全部数据功能）；CLI 误解析静默失败（P1）；`WriteFatal` 空路径二次崩溃（P2） |
| 本卡是否改产品代码 | **没有**（边界只允许 tools/e2e 与 verification）；缺陷已列给 Lead 指派 owner |
| A-6 自检是否误降级 | 否（Degraded，写入开启） |

## 4. 证据清单

```
verification/V11R-L4-EVIDENCE/
  host-readiness.md                      （本文件）
  host-readiness.json                    （legacy/v2 对比：exit/窗口/host.log/ready/data-root）
  persistence-check.json                 （重启持久化：NOT_RUN + 原因，见 README §4）
  logs/host-readiness/space-form-true-host.log   （空格写法误解析证据：data_root=true + SidecarBundleMissing）
  logs/host-readiness/writefatal-empty-logdir.log（空 --log-dir= 的二次崩溃）
  logs/host-readiness/legacy/host.log    （真实 Host 就绪日志：core_service/host_bridge/self-check）
  logs/host-readiness/v2/                （空：v2 壳没有产生任何 Host 日志 = 未启动证据）
  screens/host-readiness-legacy.png      （Host 就绪）
  screens/host-readiness-v2.png          （Host 未就绪）
```
