# V11R 真机（real machine）实机清单执行报告

- 执行时间：2026-10-30 07:5x（Asia/Shanghai）
- 执行机器：Windows 10.0.26300（Windows 11 内核）、x64、交互桌面会话、2560×1440、显示缩放 100%
- 被测版本：main `9e9ae5d58`（build Debug/net9.0 与 Release 发布产物）
- 真实 sidecar：`apps/desktop-avalonia/build/sidecar/core-sidecar/core-sidecar`（core_service.exe + host_bridge.exe）
- 隔离原则：每次启动使用临时 `--data-root` / `--log-dir` / 唯一 mutex；**未触碰用户数据根**（仅一次主题持久化测试会写全局设置，见 §3，已恢复原状）
- 自动化方式：Win32/GDI 截图、UI Automation（UIA）真实 invoke/焦点、`SendKeys`/IME 真实键盘输入；**未使用 CUA、未伪造输入**

## 结论总表

| # | 清单项 | 结论 | 证据 |
|---|---|---|---|
| 1 | 真实窗口启动矩阵（1600/1280/1024 × dark/light + legacy） | **PASS 7/7** | `../launch-matrix.json`、`../screens/v2-*.png` |
| 2 | Host 真实就绪（v2 默认壳 + legacy 回滚） | **PASS 7/7** | `../host-readiness.md`、逐组 `logs/<case>/host.log` |
| 3 | **重启持久化 E2E**（UIA 真实点击应用 → 关闭 → 重启保持） | **PASS** | `theme-settings-after-change.json`、`restart-persisted-light.png` |
| 4 | **中文 IME 真实输入**（复合 → 上屏） | **PASS** | `ime-input.png`；输入序列：`abc123`→“按不出23”，`nihao`+空格→“…你好” |
| 5 | **DPI 感知**（PerMonitorV2 + 运行时 DPI） | **PASS（100%）**；150%/200% **NOT_RUN** | `app.manifest`（PerMonitorV2）、`GetDpiForWindow=96`；见 §5 限制 |
| 6 | **屏幕阅读器/可访问性**（UIA 树） | **PARTIAL / 发现 P2 缺陷** | `uia-tree.json`：71 元素、52 命名、**7 个按钮名称为类型名**（`Avalonia.Controls.StackPanel`×6、`Kbd` 类型泄漏×1） |
| 7 | **单文件自包含发布**（win-x64 single-file） | **PASS** | `published-singlefile-running.png`；93.5 MB 单 exe；窗口 + Host 就绪 + exit 0 |
| 8 | **Trimmed 发布**（PublishTrimmed） | **FAIL（默认）→ PASS（抑制分析后 smoke）** | `publish-trimmed.log`（IL2026 被 `TreatWarningsAsErrors` 升级为 error）；`publish-trimmed-suppressed.log`、`published-trimmed-*.png`（窗口/Host/Theme Studio 可用）；trim 安全性未分析 |
| 9 | **AOT 发布**（PublishAot） | **FAIL（默认）→ PASS（`PublishTrimmed=true` + 抑制后）** | `publish-aot.log`（“PublishTrimmed is implied … cannot be disabled”）；`publish-aot-final.log`；28.8 MB 原生 exe，窗口 + Host 就绪 + exit 0 |
| 10 | GitHub Actions 真实运行 | **NOT_RUN** | 无 runner；等价命令已在 A-4 干净克隆与本机执行 |

## 1. 启动矩阵与 Host 就绪

沿用并复跑 `tools/e2e/v2-launch-matrix.ps1`：7 组真实窗口全部 `exit_kind=natural`、`exit_code=0`、`host_ready=true`，截图 9 张。本轮未改动产品代码，仅补充下面的真机项。

## 2. 重启持久化 E2E（原 README §5 的 NOT_RUN → 已执行）

方法（真实 UIA 交互，非伪造）：
1. 启动 v2 壳（真实 sidecar，隔离 data-root），UIA 找到 `ThemeStudioButton`（`主题工作室`）→ `InvokePattern.Invoke()` 打开 Theme Studio；
2. 打开「外观」分区 → 点击「浅色」→ 点击该分区的「应用」；
3. 关闭窗口（`WM_CLOSE`，exit 0）；
4. 读取 `%APPDATA%\NewManga\theme-settings.json`（ThemeService 的持久化路径）→ `appearance="light"`；
5. 不带 `--variant` 重启 → 设置仍为 `light`，顶栏外观标签显示「浅色」，截图 `restart-persisted-light.png` 为浅色主题。

**重要发现（P2，测试/隔离缺陷）**：`theme-settings.json` 路径是 `Environment.GetFolderPath(ApplicationData)`，**不随 `--data-root` 隔离**（子进程 `APPDATA` 环境变量覆盖无效）。因此该 E2E 会写用户真实 `%APPDATA%`。
- 本次已把测试产生的文件备份到 `theme-settings-created-by-test.json` 并从真实路径删除（执行前该文件不存在 → 已恢复原状）；
- 建议 follow-up：为 ThemeService 增加 `--theme-settings <path>` 或 `NEWMANGA_THEME_SETTINGS` 覆盖，供 E2E/多实例隔离（已登记 `FOLLOW-UP-E2E-1`）。

## 3. 中文 IME 真实输入

在资料柜搜索框（UIA Edit）聚焦后用真实键盘事件输入：
- 首轮 `abc123`：系统当前为中文输入法，`abc` 被 IME 复合为「按不出」，结果 `按不出23`（证明按键进入 IME 复合而非被应用吞掉）；
- 切换输入法后输入 `nihao` + 空格上屏：值变为 `按不出23你好`。

结论：**Avalonia 文本框与中文 IME 复合/上屏链路正常**（`ime-input.png` 可见）。注：未覆盖日文/韩文/手写输入与候选窗定位；标记为后续可选。

## 4. 屏幕阅读器/可访问性（UIA）

`uia-tree.json` 保存了完整元素表。统计：71 个 UIA 元素，52 个有名称；类型分布 Text 34 / Button 18 / Custom 12 / List 3 / Pane 2 / ComboBox 1 / Edit 1。Theme Studio 打开后可见 主题库/预览/我的主题/主题编辑/外观/导入导出/恢复默认/应用/取消/返回 等可操作元素（可被读屏识别）。

**P2 缺陷（真实可访问性问题）**：7 个 Button 的 `Name` 是类型名而非可读文本：
- `Avalonia.Controls.StackPanel` × 6（自定义模板按钮的内容是 StackPanel，AutomationPeer 回退到类型名）；
- `NewManga.App.Views.V2.Shell.Controls.Kbd` × 1（Kbd 控件未提供名称）。
屏幕阅读器会把它们读成类名，违反可访问名称要求。建议：为这些控件设置 `AutomationProperties.Name`（或给自定义控件实现 `GetNameCore`），并为 Kbd 提供按键语义名。已登记 `FOLLOW-UP-A11Y-1`。

另观察到顶栏主题切换按钮可被 UIA 识别（`ThemeStudioButton` / `ThemeToggleButton` 有 AutomationId），说明命名体系可用，仅局部缺失。

## 5. DPI 与显示缩放

- `app.manifest`：`dpiAware=true/pm` + `dpiAwareness=PerMonitorV2`（WPF/Win32 正确声明）；
- 运行时 `GetDpiForWindow(hwnd)=96`、窗口 1616×1039（请求 1600×1000 + 边框）→ 当前 100% 缩放下布局正常（与 launch matrix 截图一致）。
- **150% / 200% NOT_RUN**：需要修改本机显示缩放（会影响用户桌面并在部分应用上要重新登录），本轮**未擅自更改系统设置**。复跑步骤：设置 → 系统 → 显示 → 缩放 150%/200%，再执行 `tools/e2e/v2-launch-matrix.ps1`（矩阵内窗口尺寸为逻辑像素，自动化会记录实际像素尺寸与截图）。

## 6. 发布形态（单文件 / Trimmed / AOT）

| 形态 | 命令要点 | 结果 | 产物 |
|---|---|---|---|
| 单文件自包含 | `-c Release -r win-x64 --self-contained true -p:PublishSingleFile=true` | **PASS**：窗口 + Host 就绪 + exit 0 | 93.5 MB 单 exe |
| Trimmed | 同上 + `-p:PublishTrimmed=true`（**默认**） | **FAIL**：`DesignSystemThemeManager.cs(482) IL2026 AvaloniaXamlLoader.Load(Uri,Uri)`，被 `NewManga.DesignSystem.csproj` 的 `TreatWarningsAsErrors=true` 升级为 error | `publish-trimmed.log` |
| Trimmed（抑制分析） | + `-p:SuppressTrimAnalysisWarnings=true` | **PASS（功能 smoke）**：窗口 + Host 就绪 + Theme Studio 打开（主题库/应用/外观/取消 元素齐全）+ exit 0；**trim 安全性未分析** | 22.0 MB exe / 37.9 MB 目录 |
| AOT | `-p:PublishAot=true`（默认） | **FAIL**：`PublishTrimmed is implied by native compilation and cannot be disabled`（csproj 显式 `PublishTrimmed=false` 条件冲突） | `publish-aot.log` |
| AOT（正确参数） | `-p:PublishAot=true -p:PublishTrimmed=true -p:SuppressTrimAnalysisWarnings=true` | **PASS**：28.8 MB 原生 exe + native libs（44.7 MB 目录）；窗口 + Host 就绪（ReadWrite）+ exit 0；仅 1 条 `IL3050 MicroCom` 警告 | `publish-aot-final.log`、`published-aot-running.png` |

结论：**发布推荐形态 = 单文件自包含（已验证）；AOT 可行但需固定参数组合并承认 trimming 分析被抑制；Trimmed 默认配置会失败，若要走 trim 需先补 trimming 配置/抑制策略并做真机回归。**

## 7. 环境限制与 NOT_RUN

| 项 | 原因 |
|---|---|
| DPI 150%/200% | 需改本机显示缩放（影响用户桌面），未擅自修改 |
| 真实屏幕阅读器（Narrator 实际朗读） | 无法自动化验证语音输出；已用 UIA 树做结构级验证并发现 P2 |
| 日/韩 IME、手写、候选窗定位 | 需对应输入法与人工观察 |
| GitHub Actions 真实运行 | 本机无 runner；等价命令已在干净克隆执行（A-4） |
| 多显示器/混合 DPI | 本机单屏 |
| 长时运行/大库压力（240 页批次等） | 需真实素材库与人工操作 |

## 8. 证据文件

```
real-machine/
  checklist.md                     （本文件）
  checklist.json                   （机器可读结果）
  uia-tree.json                    （UIA 元素表，71 项）
  theme-settings-before-change.json / after-apply / after-change / created-by-test.json
  after-apply-light.png / theme-studio-open.png / restart-persisted-light.png / ime-input.png
  published-singlefile-running.png / published-trimmed-running.png / published-trimmed-theme-studio.png / published-aot-running.png
  publish-singlefile.log / publish-trimmed.log / publish-trimmed-suppressed.log / publish-aot.log / publish-aot-final.log
```
