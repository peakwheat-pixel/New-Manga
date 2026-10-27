# READER-LIBRARY-WIRE-1 Handoff（阅读器接真实书库 + 沉浸入口）

- Task: `doc/tasks/READER-LIBRARY-WIRE-1.md`（team task-21）
- Branch: `task/READER-LIBRARY-WIRE-1`；Worktree: `G:/CODEX/New Manga.workspace/worktrees/READER-LIBRARY-WIRE-1`
- Base: `377736213`（BOOK-FIXTURE-1 集成提交）
- Delivery head: `cd4500dcc`（实现+证据提交；任务卡 Canonical Evidence 的 pin 均指向它）
- 未 push；未改协议/Host 契约（wire 契约不变）；未改 Python Core；未改旧壳；fixture 回退保留。

## 1. 交付摘要

| AC | 结论 | 证据 |
|---|---|---|
| AC1 书库接线 | **MET** | `ListBooks` → `list_chapters` → `GetReaderProjection` + 资源通道页面字节 → 阅读器渲染真实书；真机截图 02；空态 + `NEWMANGA_READER_SOURCE=fixtures` 回退有测试 |
| AC2 沉浸入口 | **MET** | 工具栏「沉浸模式 (Esc/H/F)」+ 双击 → `ReaderWindow`（全屏）；Esc/H 真机截图 03/04/05；headless 测试 8 项覆盖创建/关闭/H/F/方向键 |
| AC3 真机验证 | **MET** | BOOK-FIXTURE 数据根（book `14340dd…`/8 页）；截图 01–05 + `live-evidence.json` + `runtime-logs/{host.log,wire/*}` |
| AC4 webtoon 工作集 | **MET** | 8 页 webtoon_vertical 渲染并可滚动（截图 06）；工作集峰值 **395.1 MB ≤1536 MB**（83 样本/22s） |
| AC5 回归 | **MET** | test.ps1 **110/110**；vitest **60/567**；pytest **3F/2739P/9S**（0 新增）；check.ps1 PASS；pin；本 Handoff |

## 2. 代码改动（全部在 `apps/desktop-avalonia/**`）

| 文件 | 改动 |
|---|---|
| `src/NewManga.CoreClient/CoreServiceClient.cs` | 新增 `ListChaptersAsync` / `GetReaderProjectionAsync` / `ResolvePageResourceAsync` + 4 个 typed record（protocol 2.3 读面，复用 `SendAsync`） |
| `src/NewManga.Host/HostRuntime.cs` | 新增 `ListChaptersAsync` / `GetReaderProjectionAsync` / `ReadPageImageAsync`：Core resolve → host_bridge issue/resolve grant → `TileChannel` 单 tile 整文件 SHA-256 校验读取；严格一问一答管道用信号量串行化；路径/摘要不出 Host |
| `src/NewManga.App/Services/ReaderLibrary.cs`（新） | `ReaderBookData` / `ReaderPageData`（按需 `LoadImageAsync`，不含 OS 路径/摘要） |
| `src/NewManga.App/Services/IHostController.cs` / `HostController.cs` / `NullHostController.cs` | 新增 `LoadReaderBookAsync()`（组合三命令；空库/失败返回 null → UI 空态 + fixture 回退） |
| `src/NewManga.App/Views/ReaderWorkbenchPages.cs` | `ReaderPage.LoadLibrary/SetLibraryEmpty/PrepareLibraryWebtoon/WaitForPageAsync`（逐页串行解码）；`ReaderWindow` 新增库中书构造 + `TryHandleKey`（Esc/H/F/方向键）+ `EscapeCount`；`ImmersiveRequested` 事件 + 按钮/双击入口；fixture 构造路径保持不变 |
| `src/NewManga.App/Views/MainWindow.axaml.cs` | 进入阅读器页/Host 就绪时 `EnsureReaderLoadedAsync()`；`OpenImmersiveReader()`；`NEWMANGA_READER_SOURCE=fixtures` 回退开关；空态提示 |
| `tests/NewManga.App.Tests/ReaderLibraryTests.cs`（新） | 8 项 Avalonia.Headless：库中书分页/长条渲染、空态、沉浸请求、Window 创建/Show/Esc 关闭、H/F/→ 状态、MainWindow 载入+沉浸、fixture 回退、空库空态 |
| `tests/NewManga.App.Tests/FakeHostController.cs` | 新增 `ReaderBook` / `LoadReaderBookAsync` 测试桩 |

## 3. 真机证据（task-env，不提交仓库中过大件）

- 发布件：`task-envs/READER-LIBRARY-WIRE-1/pkg/app`（Release single-file + `core-sidecar`）
- 数据根：`task-envs/BOOK-FIXTURE-1/isolated-data`（book `14340ddad0ed472fbe687fe12340c5d8`，8 页 1200×1660）
- 启动：`NewManga.App.exe --data-root="<数据根>"`（AppOptions 只认 `--data-root=<path>` 等号形式）
- 截图：`verification/READER-LIBRARY-WIRE-1/screens/01..06-*.png`
- 汇总：`verification/READER-LIBRARY-WIRE-1/live-evidence.json`
  （含 host.log 的 `data_root=` 行、wire 计数：ListBooks/list_chapters/GetReaderProjection/
  resolve_page_resource 27 次/page-original 59 次/host_bridge issue/resolve/revoke 各 25 次）
- 工作集：`verification/READER-LIBRARY-WIRE-1/working-set-samples.json`（峰值 395.1 MB，limit 1536 MB，within_limit=true）

## 4. 回归

| 门 | 结果 |
|---|---|
| `scripts/test.ps1` | **110/110 passed, 0 skipped**（原 102 + 新 8） |
| 旧壳 vitest | **60/60 文件、567/567 用例** |
| pytest | **3F/2739P/9S**（与基线相同失败集合，0 新增） |
| 治理 | `check.ps1 -TaskPath` PASS；pin 见任务卡 |

## 5. Record Decision / 说明

1. **为什么页面字节走 host_bridge 资源通道而不是直接读 managed 文件**：ADR-0002 资源通道是
   既有安全边界（catalog 授权、grant、文件身份/大小/摘要校验）；App 只拿字节，不拿路径。
2. **为什么 Host 侧串行化**：host_bridge/core_service 是严格 request/response 的单管道；并发读会导致
   响应串帧（本轮首版真机即复现：8 页并行 → resolve 响应错位 → 页面空白）。改为 Host 级信号量 +
   ReaderPage 逐页串行后修复，真机复验通过。
3. **fixture 回退保留**：`ReaderFixtureLocator`、旧构造 `ReaderPage(vm, paths, tileDir)` 与
   `ReaderWindow(vm, paths, tileDir)` 全部保留；`NEWMANGA_READER_SOURCE=fixtures` 可强制回退（测试覆盖）。
4. **空态**：`ListBooks` 为空或读取失败 → 阅读器页显示空态提示并继续展示 fixture（不崩溃）。

## 6. 遗留 / NOT_RUN

1. 阅读进度（`SaveReadingProgress`）仍未接线（S4 NS 批 PLANNED；本卡范围外）。
2. 未加全局沉浸快捷键（F11 等）；入口为阅读器页按钮 + 双击（AC2 允许三选一）。
3. 工作集为单次运行 22s/83 样本测量（8 页 webtoon 滚动），非长时压测。
4. 未做老书（多章）选择器：当前打开第一本书的第一章（AC1 范围；多章导航后续 Task）。
5. 需独立 Review（Owner 不得自审）。
