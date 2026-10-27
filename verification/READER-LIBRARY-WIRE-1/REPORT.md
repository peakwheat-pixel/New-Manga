# READER-LIBRARY-WIRE-1 报告：阅读器接真实书库 + 沉浸入口

- Task: `doc/tasks/READER-LIBRARY-WIRE-1.md`（team task-21）；Branch/Worktree:
  `task/READER-LIBRARY-WIRE-1` / `G:/CODEX/New Manga.workspace/worktrees/READER-LIBRARY-WIRE-1`；Base `377736213`
- 未 push；未改协议/Host 契约（新增的是 Host 内的消费方法，wire 契约不变）；未改 Python Core；未改旧壳；
  fixture 回退路径保留。

## 0. 结论

| AC | 判定 | 关键证据 |
|---|---|---|
| AC1 书库接线 | **MET** | 阅读器页经 Host/CoreClient 调 `ListBooks` → `list_chapters` → `GetReaderProjection` + `resolve_page_resource`/resource channel 渲染真实书；真机截图 `screens/02-reader-library.png`（书名/章/8 页/webtoon 长滚动，真实日漫页面）；空态 + `NEWMANGA_READER_SOURCE=fixtures` 回退有自动化测试 |
| AC2 沉浸入口 | **MET** | 阅读器页工具栏「沉浸模式 (Esc/H/F)」按钮 + 页面双击 → `new ReaderWindow(...)`；真机：沉浸窗全屏出现（`screens/03-immersive.png`）、H 隐藏 HUD（`screens/04-hud-hidden.png`）、Esc 关闭回阅读器（`screens/05-after-esc.png`）；headless 测试覆盖 Window 创建/关闭与 Esc/H/F/方向键状态（`ReaderLibraryTests` 8 项） |
| AC3 真机验证 | **MET** | BOOK-FIXTURE 数据根（book `14340dd…`，8 页）；`runtime-logs/host.log` 记录 `data_root=<隔离根>`；wire 计数：ListBooks/list_chapters/GetReaderProjection/resolve_page_resource 均出现；截图 01–05 |
| AC4 webtoon 工作集 | **MET** | 8 页 webtoon_vertical 全量渲染并可滚动（滚动条 PageDown 有效，`screens/06-webtoon-scrolled.png` 显示第 2/3 页内容）；工作集峰值（NewManga.App + core_service 合计）**395.1 MB ≤1536 MB**（`working-set-samples.json`，83 样本/22s） |
| AC5 回归 | **MET** | `scripts/test.ps1` 全绿（见 §4）；旧壳 vitest 60/567；pytest 3F/2739P/9S（0 新增）；`check.ps1 -TaskPath` PASS；64-hex pin；Handoff |

## 1. AC1 书库接线（实现）

- `NewManga.CoreClient/CoreServiceClient.cs`：新增 `ListChaptersAsync`、`GetReaderProjectionAsync`、
  `ResolvePageResourceAsync`（protocol 2.3 读面，复用现有 `SendAsync`；响应严格解析）。
- `NewManga.Host/HostRuntime.cs`：新增 `ListChaptersAsync` / `GetReaderProjectionAsync` /
  `ReadPageImageAsync`。页面字节走**既有资源通道**：Core `resolve_page_resource` →
  host_bridge `issue`/`resolve` grant → Host `TileChannel` 以单 tile 整文件 SHA-256 校验读取；
  路径/摘要不出 Host。host_bridge 是严格一问一答管道，故整段读取用 `SemaphoreSlim` 串行化。
- `NewManga.App/Services/ReaderLibrary.cs`（新）：`ReaderBookData` / `ReaderPageData`
  （按需 `LoadImageAsync`，不含 OS 路径/摘要）。
- `IHostController` + `HostController`：`LoadReaderBookAsync()` 组合三命令；失败/空库返回 null。
- `ReaderPage`：新增 `LoadLibrary(ReaderBookData)`、`SetLibraryEmpty(message)`、
  `PrepareLibraryWebtoon()`（真实 8 页纵向堆叠，逐页串行解码）、`WaitForPageAsync`；
  旧 fixture 构造路径与 `ReaderFixtureLocator` 原样保留。
- `MainWindow`：进入「阅读器」页 / Host 就绪时 `EnsureReaderLoadedAsync()`；空库或失败显示空态并
  **保留 fixture 回退**；`NEWMANGA_READER_SOURCE=fixtures` 强制回退（测试覆盖）。

## 2. AC2 沉浸入口（实现 + 自动化）

- 入口：阅读器页工具栏按钮「沉浸模式 (Esc/H/F)」（`ImmersiveButton`）+ 页面双击
  （`PointerPressed.ClickCount>=2`）→ `MainWindow.OpenImmersiveReader()` → `new ReaderWindow(...)`
  （库中书 / fixture 两种构造）。
- `ReaderWindow`：新增 `TryHandleKey(Key)`（Esc 关闭、H 切 HUD、F 循环 fit、方向键翻页），
  `OnKeyDown` 委托；`EscapeCount` 供测试断言；库中书 webtoon 打开时自动 `PrepareLibraryWebtoon()`。
- 自动化：`tests/NewManga.App.Tests/ReaderLibraryTests.cs`（8 项，Avalonia.Headless）——
  库中书分页/长条渲染、空态、沉浸请求、Window 创建/Show/Esc 关闭、H/F/→ 状态变化、
  MainWindow 库中书载入 + 沉浸窗打开、fixture 回退、空库空态。

## 3. AC3/AC4 真机证据（BOOK-FIXTURE 数据根）

发布件：`task-envs/READER-LIBRARY-WIRE-1/pkg/app`（Release single-file + `core-sidecar`，由
FINAL-VALIDATION-1 侧车复制 + 本次 publish 覆盖 exe）。启动：
`NewManga.App.exe --data-root="G:\CODEX\New Manga.workspace\task-envs\BOOK-FIXTURE-1\isolated-data"`。

| 截图 | 内容 |
|---|---|
| `screens/01-bookshelf.png` | 书架显示「BOOK-FIXTURE-1 日漫_JA 测试书 · 8 页」 |
| `screens/02-reader-library.png` | 阅读器页：标题「… · 第 1 章 · 8 页 · webtoon 长滚动」+ 真实日漫页面 |
| `screens/03-immersive.png` | 双击进入沉浸窗（无边框全屏「阅读器」，同书 8 页） |
| `screens/04-hud-hidden.png` | 按 H 后 HUD/工具栏隐藏（仅页面） |
| `screens/05-after-esc.png` | 按 Esc 后沉浸窗关闭，回到阅读器页（窗口列表 2→1） |
| `screens/06-webtoon-scrolled.png` | 滚动条 PageDown 后显示后续页面（webtoon 滚动有效） |

`live-evidence.json` 汇总：host.log 的 `data_root=` 行、截图清单、wire 计数
（ListBooks、list_chapters、GetReaderProjection、resolve_page_resource、page-original、bridge issue/resolve/revoke）。
`working-set-samples.json`：22s × 83 样本，峰值 **395.1 MB**（app+core 合计）≤ 1536 MB 目标。

## 4. AC5 回归（实测）

| 门 | 结果 |
|---|---|
| `apps/desktop-avalonia/scripts/test.ps1` | **TEST PASS (Debug): 110/110 passed, 0 skipped**（含新增 ReaderLibraryTests 8 项；`dotnet-all.log`） |
| 旧壳 vitest | **Test Files 60 passed (60) / Tests 567 passed (567)**（`vitest.log`） |
| `python -m pytest -q` | **3 failed, 2739 passed, 9 skipped**（与基线 3F/2739P/9S 相同失败集合，0 新增；`pytest.log`） |
| `check.ps1 -TaskPath` | PASS |
| 未污染真实 `%APPDATA%` | 真机运行使用隔离数据根（`--data-root`）；本卡只读 Core，未写生产数据 |

## 5. 遗留 / NOT_RUN

1. 沉浸入口为按钮/双击 + 键盘；未加全局快捷键（如 F11）——非本卡要求。
2. 阅读进度保存（`SaveReadingProgress`）仍未接线（S4 NS 批 PLANNED，本卡未扩大范围）。
3. 真实 `%APPDATA%` 生产数据只读策略未变（Host `ReadOnlyUntilParity`）；本卡只读读取。
4. 工作集测量为本次单机一次运行（83 样本），非长时压测；目标为「8 页 webtoon 可滚动 + ≤1.5GB」。
5. 需独立 Review（Owner 不得自审）。
