# V11R-INT-0 构建与测试记录

执行目录：`apps/desktop-avalonia`；本目录 `build.log` / `test.log` 为下述命令原样输出。

## 1. 构建

```
dotnet build NewManga.sln -warnaserror --nologo
```

- exit code：**0**；`0 个警告，0 个错误`

## 2. 测试

```
dotnet test NewManga.sln -m:1 --no-build --nologo
```

- exit code：**0**；串行 `-m:1` 为本仓库可复现绿色基线（并行项目会偶发争用临时 SQLite `-shm`，与本次改动无关）

| 测试项目 | 通过 | 跳过 | 失败 | 总计 |
|---|---|---|---|---|
| NewManga.Host.Tests | 42 | 24 | 0 | 66 |
| NewManga.DesignSystem.Tests | 67 | 0 | 0 | 67 |
| NewManga.ThemeEngine.Tests | 229 | 0 | 0 | 229 |
| NewManga.App.Tests | 254 | 6 | 0 | 260 |
| NewManga.CoreClient.Tests | 42 | 25 | 0 | 67 |

## 3. 本任务测试

```
dotnet test tests\NewManga.App.Tests\NewManga.App.Tests.csproj --filter "FullyQualifiedName~Int0_"
```

- 5 条全绿：
  - `Int0_CreateRoot_BuildsStandaloneWindow_WithBuiltInWorkspaces`：CreateRoot 窗口标题/尺寸/MinWidth、三内置工作区注册、初始化完成
  - `Int0_StudioSpace_RendersRealSurface_TabStaysInStudio`：Studio 真实表面可见；Tab 由 Studio 消费并同步 shell StudioMode；返回 Library 后 selection 保持
  - `Int0_ThemeStudio_OpensAsHonestPlaceholder_AndEscCloses`：表面栈打开、未注册占位文案、Esc 关闭、上下文不变
  - `Int0_StatusBand_UsesSharedRunMonitor_AndHidesWithoutRun`：共享 monitor 单次快照/投影读取（R-24）、StatusBand 文案、无 Run 隐藏
  - `Int0_UnregisteredStudio_ShowsHonestPlaceholder_NoFakeWorkspace`：反注册后诚实占位、无 Studio 内容
- V2 回归：`FullyQualifiedName~V2` 共 95 条全绿（B-1/B-2/B-3 I2c 集成面不回归）

## 4. 证据生成（R-19）

```
pwsh -NoProfile -File verification/V11R-INT-0/curate.ps1
```

- 普通测试只写 `%TEMP%/newmanga-evidence/V11R-INT-0/`；仅 `NEWMANGA_EVIDENCE_SYNC=1`/`NEWMANGA_EVIDENCE_DIR` 显式时镜像仓库。
- 截图唯一命名 `<TestName>--<name>.png`；IO 失败重试且不使测试失败。

## 5. NOT RUN

| 项 | 原因 |
|---|---|
| `MainWindow` 默认入口切换 / 应用启动链路 | 归 V11R-INT-1（Lead） |
| 真实 Core sidecar 端到端（Studio 载入真实页/图） | 本机无隔离 sidecar；测试用 `FakeHostController` + 真实 DTO/调用记录 |
| Theme Studio 7 分区内容 | 归 V11R-C-2 / INT-1，本任务只提供 `ISurfaceWorkspace` seam 与占位 |
