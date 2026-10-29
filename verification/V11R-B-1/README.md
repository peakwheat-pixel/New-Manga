# V11R-B-1 证据：新外壳 + Library 空间（I1 返修版）

- Task: `doc/tasks/V11R-B-1.md`（task-5，Owner `ui-shell`）
- Branch: `v11r/ui-shell`（已合入 V11R-D-1 M0、A-1 `CreateChapterAsync`、A-2 `IRunController`）
- 视觉权威：DESIGN_SYSTEM.md + tokens.json（经 `NewManga.DesignSystem`）；屏幕规格：SCREEN_SPECS §1（Shell）+ §2（Library）
- 渲染：Avalonia Headless + Skia（`UseHeadlessDrawing=false`），`[AvaloniaFact]` 真窗口 `CaptureRenderedFrame()`；每张 PNG > 4KB 断言

## 1. 交付内容（I1 后的关键结构）

| 文件 | 说明 |
|---|---|
| `Shell/V2/ShellState.cs` | **唯一状态源**：CurrentSpace/StudioMode/Selection/每空间滚动筛选/表面栈 + **IWorkspaceView 注册表** |
| `Shell/V2/IWorkspaceView.cs` | 契约 §6.1 工作区接口：`Space/CreateContent/OnActivated/OnDeactivated` + R-17 `TryHandleKey` |
| `Shell/V2/ShellLayout.cs` | 单一布局令牌解析模块：`Nm.Size/Space` 令牌 + R-18 断点 1600/1280/1024（DS Breakpoint 令牌为 follow-up） |
| `Shell/V2/KeyMap.cs` + `ShellCommands.cs` | 契约 §6.3 全量快捷键单一注册表 + 启动冲突断言；命令定义（含待接入原因） |
| `Shell/V2/AppShellV2.axaml(.cs)` | Row0 TopBand 36px / Row1 空间内容 / Row2 StatusBand；四个全局浮层；`DesignSystemThemeManager` 深浅切换（不重建窗口） |
| `ViewModels/V2/Shell/AppShellViewModel.cs` | 空间切换/Studio 模式切换调用工作区 `OnDeactivated→OnActivated`；窗口键漏斗（工作区先拒绝→KeyMap）；命令面板/跳转/F1/确认 |
| `ViewModels/V2/Shell/WorkspaceAdapters.cs` | Library/Console 的 IWorkspaceView 实现（CreateContent 一次创建；滚动/筛选/选择双向交接） |
| `Views/V2/Shell/*` | TopBand（主题工作室入口 + 快速深浅切换两个语义）、Breadcrumb、ScopeSelector、AttentionMenu、StatusBand、WorkspaceHost、4 个浮层、未注册工作区占位 |
| `Views/V2/Library/*` | 搜索/排序/筛选、响应式书卡网格（≥1600 四列 / 1280–1599 三列 / <1280 覆盖式详情）、同尺寸加载骨架、驻留详情（章节账本/页/进度/操作）、多选批量条、ImportDock、回收站危险确认、阅读浮层 |
| `ViewModels/V2/Library/*` | 数据只经 `IHostController`（含 `CreateChapterAsync`）；真实滚动 offset 写回；搜索（中文+拼音首字母）；逐文件导入状态 |

## 2. I1 返修摘要（完整处置见 `AC_COVERAGE.md`）

- 证据目录清理：删除 115 个外任务文件（57 个 SHA-256 字节级重复 + 58 个外任务独有），仅保留本任务证据（`CLEANUP.md`）。
- 证据纪律 R-19：测试默认写 `%TEMP%/newmanga-evidence/<TASK>/`；仅显式 `NEWMANGA_EVIDENCE_SYNC=1`/`NEWMANGA_EVIDENCE_DIR` 才镜像仓库；`curate.ps1` 为唯一入口；文件名含测试名唯一化；IO 失败重试不炸测试。
- 新增 `IWorkspaceView` 与工作区激活/停用 hook；`TryHandleKey` 遵守 R-17。
- 滚动保留改为真实 `ScrollViewer.Offset` 写回/恢复。
- C# 裸设计值全部迁入 `ShellLayout`（令牌派生）；conformance 扫描扩到 C#。
- R-18 断点 1600/1280/1024，删除 1400/1200；<1280 详情覆盖式。
- loading 改为同尺寸骨架网格；ImportDock「新建章节」措辞改为真实 Core 写入。
- 顶带固定 36px；queued 符号按裁决为 `·`。

## 3. 截图（`screens/`，13 张，R-19 命名）

| 文件（以实际 TestName-- 前缀为准） | 证明 |
|---|---|
| `Shell_RendersAt1600x1000...--01-library-dark-1600x1000.png` | 1600×1000 基准：TopBand 36px、4 列书卡、驻留详情、章节账本 |
| `ThemeToggle...--02-library-light-1600x1000.png` | 同一视觉树浅色令牌切换（选择/滚动不丢） |
| `SpaceAndModeSwitch...--03-library-context-retained.png` | 空间/模式往返后 selection/search/筛选/多选保持 |
| `CommandPalette...--04-command-palette.png` | Ctrl+K：每条带「空间 · 模式 · 作用域」+ 键位 |
| `CommandPalette...--05-quick-jump.png` | Ctrl+P 跳转 |
| `ImportDock...--06-import-dock-partial-retry.png` | 逐文件真实状态、部分失败重试、汇总 |
| `RecycleBin...--07-recycle-danger-confirm.png` | 危险确认默认取消、阻断原因可见 |
| `ReaderOverlay...--08-reader-overlay.png` | 分页/Webtoon、RTL/LTR、双模态进度、真实保存 |
| `Shell_RendersStudioAndConsoleRouting...--09-studio-pending.png` | 工位路由 + 诚实占位（B-3/B-4 内容范围） |
| `Shell_RendersStudioAndConsoleRouting...--10-console-providers.png` | 控制台路由（9 分区属 B-2，另行交付） |
| `Shell_RendersAt1280And1024...--11-library-1280x800.png` | 1280：3 列、紧凑带 |
| `Shell_RendersAt1280And1024...--12-library-1024x700.png` | 1024：覆盖式详情、4 列主网格、无整页横向滚动 |
| `LoadingState...--13-library-loading-skeleton.png` | loading 同尺寸骨架（保留网格几何，无自证文案） |

## 4. 复现命令

```powershell
cd apps/desktop-avalonia
dotnet build NewManga.sln -warnaserror
dotnet test NewManga.sln -m:1 --no-build

# 仓库证据只由显式 curate 命令生成（R-19）
pwsh -NoProfile -File ../../verification/V11R-B-1/curate.ps1
```

| 证据 | 内容 |
|---|---|
| `BUILD_TEST.md` / `build.log` / `test.log` | 命令、exit code、汇总、known issue（并行 SQLite `-shm` 争用） |
| `CLEANUP.md` | 证据污染清理与防复发（P1） |
| `curate.ps1` | 唯一的仓库证据生成入口（R-19） |
| `conformance/v2-tokens-and-classes.json` | 用到的 `Nm.*` 令牌与 Classes 词表（XAML 静态扫描） |
| `NOT_WIRED.md` / `DEVIATIONS.md` / `AC_COVERAGE.md` | 未接入清单 / 偏差 / AC 与返修处置 |
