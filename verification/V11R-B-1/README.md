# V11R-B-1 证据：新外壳 + Library 空间

- Task: `doc/tasks/V11R-B-1.md`（task-5，Owner `ui-shell`）
- Branch: `v11r/ui-shell`（worktree `V11R-UI-SHELL`；main 已合入 V11R-D-1 M0 `819eea0d3` 与 V11R-A-1 `CreateChapterAsync`）
- 设计/交互权威: `doc/plan/V11R_SCREEN_SPECS.md` §0/§1/§2、`doc/plan/V11R_AVALONIA_CONTRACT.md` §2/§3/§6、`40-fusion/{FUSION_SPEC,DESIGN_SYSTEM,tokens}.json`
- 渲染方式: Avalonia Headless + Skia（`AvaloniaHeadlessPlatformOptions { UseHeadlessDrawing = false }`），`[AvaloniaFact]` 真窗口 `CaptureRenderedFrame()`；**不是占位图**（每张 PNG > 4KB 断言，见测试）。

## 1. 交付内容

### Shell（`Shell/V2/`、`Views/V2/Shell/`）

| 文件 | 说明 |
|---|---|
| `Shell/V2/ShellState.cs` | **唯一状态源**：`CurrentSpace` / `StudioMode` / `Selection{book,chapter,page,region,multiPage}` / 每空间（Studio 按模式）滚动与筛选 / 覆盖表面栈 `ThemeStudio`·`ReaderOverlay`；切换不重建 VM |
| `Shell/V2/KeyMap.cs` | 契约 §6.3 全量快捷键单一注册表（Ctrl+1/2/3、Tab、Ctrl+K、Ctrl+P、Ctrl+E、Ctrl+,、F1、F5、Ctrl+Shift+F、Esc、J/K、`[`/`]`、Shift+`[`/`]`），冲突检测 + 启动断言 `KeyMap.EnsureValid()` |
| `Shell/V2/ShellCommands.cs` | 命令定义（含「空间 · 模式 · 作用域」标注、可用性与「能力待接入」原因）；命令面板由此生成，不漂移 |
| `Shell/V2/ShellDeepLink.cs` | `?space=&mode=&book=&chapter=&page=&region=` 深链接解析/回写（供证据与 V11R-INT-1）；`AppShellV2.DeepLinkFromEnvironment()` 读 `NEWMANGA_V2_DEEPLINK` |
| `Shell/V2/PinyinIndex.cs` | 中文 + 拼音首字母搜索（本地常用字表；未覆盖字符退化为原字匹配，见偏差 D-7） |
| `Shell/V2/AppShellV2.axaml(.cs)` | Row0 TopBand 36px / Row1 空间内容 / Row2 StatusBand；四个全局浮层；深浅外观经 `DesignSystemThemeManager` 切换（不重建窗口） |
| `Views/V2/Shell/{TopBand,SpaceTabs,Breadcrumb,ScopeSelector,AttentionMenu,StatusBand,V2WorkspaceHost}.axaml` | 顶带与路由组件 |
| `Views/V2/Shell/{CommandPaletteOverlay,JumpOverlay,HelpOverlay,ConfirmModal}.axaml` | Ctrl+K / Ctrl+P / F1 / 危险确认 Modal（默认焦点在「取消」） |
| `Views/V2/Shell/{StudioPendingView,ConsolePendingView,ThemeStudioPendingView}.axaml` | 非本任务范围的诚实占位（工位=B-3/B-4、控制台=B-2、主题工作室 7 分区=C-2） |

### Library（`ViewModels/V2/Library/`、`Views/V2/Library/`）

| 文件 | 说明 |
|---|---|
| `LibraryViewModel.cs` | 书架数据经 `RefreshBooksAsync/Snapshot`、章节 `ListChaptersAsync`、页 `ListChapterPagesAsync`、进度 `LoadReaderBookAsync`；搜索/排序/筛选；驻留详情；真实 `CreateChapterAsync`（V11R-A-1）与 `TryCreateBookAsync`；多选批量条；回收站视图开关 |
| `ImportDockViewModel.cs` | 导入 dock：文件逐文件调用 `ImportFilesAsync`（**每文件真实状态**：已导入/跳过重复/失败+错误码）、文件夹单次 `ImportFolderAsync`（聚合结果）、部分失败「重试失败/跳过失败」、**无章节时就地「新建章节」真实入口**（关闭审计 F011） |
| `ReaderOverlayViewModel.cs` | 阅读浮层：分页 RTL/LTR + Webtoon 纵向；双模态进度（页码 + 百分比）；`Esc` 退出；`SaveReadingProgressAsync` 真实保存并映射 typed 结果 |
| `LibraryItems.cs` | Book/Chapter/Page 行、筛选 Chip、导入行、阅读页；行内命令回写 `ShellState` |
| `Views/V2/Library/{LibraryView,BookDetailPanel,ImportDockView,RecycleBinView,ReaderOverlay}.axaml` | 布局与状态呈现（idle/loading/ready/empty/error/partial 就地） |

### 并发状态合并后处理（Lead 指令）

- DS M0 合入后已 **删除** 预置的 `Views/V2/Shell/Theme/{V2TokensFallback,V2FallbackStyles}.axaml`（临时令牌与替代样式），令牌/标准控件样式全部来自 `NewManga.DesignSystem`。
- 保留的本地控件（DS 自定义控件 M0 集尚未交付）：`Kbd`、`StatusBadge`（七态符号+文字）、`AlertBanner`、`EmptyState`，位于 `Views/V2/Shell/Controls/`，样式集中在 `Theme/V2LocalStyles.axaml`；DS 交付后按契约 §3.2 上收。
- `V2LocalStyles.axaml` 只保留 DS 尚未覆盖的 gap-fill（ComboBox/CheckBox/ListBoxItem/ProgressBar）与外壳语义类（spacetab/crumb/chip/bookcard/detailrow/topband…），**不再重定义任何 DS 标准控件样式**。

## 2. 截图（`screens/`，真实 headless 渲染）

| 文件 | 证明 |
|---|---|
| `01-library-dark-1600x1000.png` | 1600×1000 基准：TopBand（空间/面包屑/作用域/需要我处理/命令/主题/F1）+ Library（搜索/排序/筛选 Chip/4 列书卡/驻留详情/章节账本/页/进度） |
| `02-library-light-1600x1000.png` | 同一视觉树切换浅色令牌（`DesignSystemThemeManager`），选择/滚动未丢失 |
| `03-library-context-retained.png` | 空间/模式来回切换后 selection、搜索、滚动、多选保持 |
| `04-command-palette.png` | Ctrl+K 命令面板：每条带「空间 · 模式 · 作用域」+ 键位；↑↓/Enter/Esc |
| `05-quick-jump.png` | Ctrl+P 跳转（作品/章节/页；Region 需工位） |
| `06-import-dock-partial-retry.png` | 导入 dock：每文件真实状态、部分失败重试、汇总、无路径泄漏 |
| `07-recycle-danger-confirm.png` | 回收站危险动作二次确认：默认取消、确认被禁用并给出「能力待接入」原因 |
| `08-reader-overlay.png` | 阅读浮层：分页/Webtoon、RTL/LTR、双模态进度、进度保存状态 |
| `09-studio-pending.png` | 工位路由 + 页面/批次模式切换（内容属 V11R-B-3/B-4，不伪造） |
| `10-console-pending.png` | 控制台路由（9 分区属 V11R-B-2） |
| `11-library-1280x800.png` | 1280×800：3 列书卡、详情 340px、不崩 |
| `12-library-1024x700.png` | 1024×700：紧凑模式（隐藏次要标签）、仍可读、无横向整页滚动 |

## 3. 命令与证据文件

```
cd apps/desktop-avalonia
dotnet build NewManga.sln -warnaserror          # 见 BUILD_TEST.md
dotnet test NewManga.sln --no-build             # 见 BUILD_TEST.md

# 重新生成截图与 conformance 清单
$env:NEWMANGA_EVIDENCE_DIR = "<repo>/verification/V11R-B-1"
dotnet test tests/NewManga.App.Tests/NewManga.App.Tests.csproj --filter "FullyQualifiedName~V2"
```

| 证据 | 内容 |
|---|---|
| `BUILD_TEST.md` + `build.log` + `test.log` | 构建/测试命令、exit code、摘要 |
| `conformance/v2-tokens-and-classes.json` | 用到的全部 `Nm.*` 键（与 `NmKeys.All` 校验）与 `Classes` 词表清单 |
| `NOT_WIRED.md` | 未接入能力清单（诚实降级，全部有 UI 标记） |
| `DEVIATIONS.md` | 与规格的偏差及理由 |
| `AC_COVERAGE.md` | AC1–AC7 → 代码/测试/截图映射 |

## 4. 测试（`tests/NewManga.App.Tests`）

- `V2ShellCoreTests.cs`：ShellState（上下文保留/选择唯一/表面栈/多选共享）、KeyMap（无冲突/全量快捷键/作用域）、DeepLink、拼音搜索。
- `V2ShellUiTests.cs`（`[AvaloniaFact]` 真渲染）：三空间路由、上下文不重建 VM、命令面板/跳转/F1/Esc、IME 让位、主题切换不丢选择、导入逐文件状态 + 重试、无章节→真实新建章节→导入、回收站危险确认可取消且不写、阅读浮层双模态进度 + 保存 + Esc 退出、1600/1280/1024 三档渲染与截图。
- `V2ConformanceTests.cs`：V2 XAML 无裸色值/裸字号/裸尺寸/阴影/渐变/模糊/圆角>3px；所有 `Nm.*` 引用均存在于 DS；生成令牌/Classes 清单；预置兜底文件已删除。
