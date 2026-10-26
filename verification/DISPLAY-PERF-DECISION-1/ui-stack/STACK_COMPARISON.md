# 非 Web 前端技术栈选型验证：Avalonia / WinUI 3 / Qt 6 QML / Flutter / Compose Desktop

> 任务：`DISPLAY-PERF-DECISION-1` / `task-5`（父任务用户裁决：**前端不要 Web UI，要效果好、能换主题/皮肤、内置主题中心**）
> 作者：`ui-stack-research`（DSH 协作 Agent）｜基线 HEAD `191824529`｜工作树：`G:\CODEX\New Manga`
> 性质：**只读研究 + 本机实测**。本文件是唯一产物目录 `verification/DISPLAY-PERF-DECISION-1/ui-stack/`，未改动任何产品代码/配置/契约/AD-001。

**证据分级（全文统一使用）**

| 标记 | 含义 |
|---|---|
| **[实测]** | 本次在本机跑出来的数字（命令、SDK 版本、产物已落盘可复核） |
| **[源码]** | 本仓库代码 / 上游一手源码文件（给了路径与行号） |
| **[一手文档]** | 官方文档 / 官方 API 参考（给了 URL） |
| **[推断]** | 我基于上述事实的工程判断，不是文档原话 |
| **[未核实]** | 本次未取得一手资料，**不得当结论使用** |

---

## 0. 结论（先说答案）

| 裁决 | 技术栈 | 一句话理由 |
|---|---|---|
| **主选** | **C# / .NET 9 + Avalonia 11.3.x**（XAML + Skia/D3D11） | 唯一同时满足：真 Mica/Acrylic、**运行时**换肤（ResourceDictionary/ControlTheme/DynamicResource）、内置 Transitions+Keyframe、HarfBuzz 文本、**单文件 exe 实测 34.24 MB**、Win32 原生对话框/UIA/PerMonitor DPI；且保留 `NativeControlHost` 逃生口，将来可接原生 GPU 面。 |
| **备选** | **WinUI 3（Windows App SDK 1.8.x）** | Mica 是平台原生能力、视觉最"Windows"；但**官方明确不能出单文件 exe**，且 `Application.RequestedTheme` **运行期设置会抛异常** → 主题中心需绕道；换肤深度=替换每个控件的 ControlTemplate；且 Windows-only。 |
| **不推荐** | **Qt 6 / QML（C++ 或 PySide6）**、**Flutter**、**Compose Desktop** | 共同硬伤：QML 样式**官方明确「QML 类型注册后不能改」**→ 运行时换肤要靠自建主题层；PySide6 走 GPL/LGPL 且把 UI 与 47k 行 Core 塞进同一 Python 进程；Flutter/Compose 的 Windows **IME 有一手 open issue**（中文/日文输入是刚需）。 |

**不要误读的一句话**：换栈**不能**解决"成品页竖排排版"。Avalonia 的竖排 advance（VVAR/vmtx）仍在**未合并 PR**（Part 11/17）；WinUI3/QML/Flutter/Compose 的 CJK 竖排本次**未核实**。→ 竖排排版必须留在 Core（Python/Skia+HarfBuzz）以**图片**形式交付给 UI，任何栈都一样。这与父任务 `routes/ROUTES.md` 的结论一致，不因换栈而改变。

---

## 1. 现状事实（决定迁移成本的分母，全部本机实测）

| # | 事实 | 证据 |
|---|---|---|
| S1 | 前端 **105 个 `.tsx` / 28,602 行**；**52 个 `.ts` / 8,734 行**；合计 157 文件 / 37,336 行；**60 个测试文件** | [实测] `Get-ChildItem apps/desktop/frontend/src -Recurse` + `Measure-Object -Line` |
| S2 | 四页：Reader 827 / Settings 362 / Shelf 1019 / Workbench 1452 = **3,660 行** | [实测] 同上 |
| S3 | 后端 host：**9 个 `.rs` / 16,926 行**；**57 个 `#[tauri::command]`** | [实测] `Select-String '#\[tauri::command\]'` |
| S4 | 前端 `invoke(` **184 处**：**生产 83 / 测试 101**；生产集中在 6 个 domain client（settings 36、library 14、App.tsx 13、region 7、ac1 5、reader 4、resourceChannel 2、AppShell 1、workbench 1） | [实测] 按 `*.test.*` 分流统计 |
| S5 | Python Core：**217 个 `.py` / 47,065 行** | [实测] |
| S6 | 本机 SDK：**.NET SDK 9.0.308 / 10.0.401**，运行时 9.0.11；Python 3.14.6；Node v24.15.0 | [实测] `dotnet --list-sdks` |
| S7 | 已存在设计令牌层：`src/design/tokens.css` 154 行（37 色 + 4 档字号 + 4 档圆角 + 间距）+ `src/theme/tokens.ts` 183 行镜像 | [源码] `apps/desktop/frontend/src/design/tokens.css`、`src/theme/tokens.ts`（其头部注释即声明"唯一真相源"） |
| S8 | 现有"亚克力/Mica"是 **CSS 仿制**，窗口不透明、无 DWM backdrop | [源码] 父任务 `routes/ROUTES.md` F6（引 `src/design/base.css:113-118`、`tauri.conf.json:11-24`） |
| S9 | 资源通道 `m2res` 自定义 scheme：**每个 chunk 请求都重新向 Core resolve + 打开文件 + 顺序读全文件算 SHA-256**，`no-store` + CORS | [源码] `apps/desktop/src-tauri/src/resource_protocol.rs:1-34`（文件头管道说明）、`:40 CHUNK_SIZE=16MiB`、`:41 MAX_RESOURCE_BYTES=256MiB`、`:439 Sha256::new()` |
| S10 | Core 通信已是 **stdio JSON-lines** 双通道：① 资源控制面 wire v1（`core_bridge.rs`，`issue/resolve/revoke`，grant 带 `sha256/volume_serial/file_index`）② Core protocol **2.3**（`library_bridge.rs`） | [源码] `core_bridge.rs:1-20`、`:133 pub fn spawn`、`:173 spawn_packaged`、`:219 fn round_trip`；`library_bridge.rs:17-29` |
| S11 | sidecar 启动已做 `CREATE_NO_WINDOW`；打包模式直接起 PyInstaller sidecar exe（无系统 Python 回退） | [源码] `core_bridge.rs:159-160`、`:194-195`、`:173-180` |
| S12 | 已知编码坑：PyInstaller 冻结的 sidecar 在 Windows 用 **ANSI 代码页 cp936** 解 stdin（`PYTHONIOENCODING/PYTHONUTF8` 被忽略），故 host 必须把非 ASCII 转 `\uXXXX` | [源码] `library_bridge.rs:17-29`（注释含实测：`雾港来信` → `闆炬腐鏉ヤ俊`） |

> **对迁移成本的直接影响（S4）**：184 处 `invoke` 里 **101 处在测试**，生产只剩 83 处且集中在 6 个 client 模块 → 端口面不是"184 处散落调用"，而是 **57 个命令契约 + 6 个 typed service 接口**。这显著降低 C# 重写风险（[推断]，依据见 §6）。

---

## 2. 对比矩阵

评分口径：★越多越好；"—"＝该栈不存在此能力；"未核实"＝无一手资料。

| 维度 | **Avalonia 11.3 (C#/.NET9)** | **WinUI 3 (WinAppSDK 1.8)** | **Qt6/QML (C++/PySide6)** | **Flutter** | **Compose Desktop** |
|---|---|---|---|---|---|
| 非 Web 程度 | ★★★★☆ XAML+Skia 自绘，无 WebView | ★★★★★ 原生 Windows 控件 | ★★★★☆ QPA 原生控件 | ★★★★☆ Skia 自绘 | ★★★☆☆ Skia/Skiko + JVM |
| 换肤自由度（运行时） | ★★★★★ `ThemeDictionaries`+`DynamicResource`+`ControlTheme`+`ThemeVariantScope`，可整树替换 | ★★★☆☆ 逐控件换 `ControlTemplate`；`Application.RequestedTheme` 运行期**抛异常** | ★★☆☆☆ QML style **注册后不能改**，须自建主题层 | ★★★☆☆ 主题即 Dart 数据，需重建 widget 树 | ★★★☆☆ 同 Flutter 路线 |
| 材质/视觉效果 | ★★★★☆ `TransparencyLevelHint`: Mica(Win11)/AcrylicBlur(Win10 1803+)；`WinUIComposition` 合成；Effects/Composition animations/自定义渲染 | ★★★★★ 平台原生 `MicaBackdrop`/`DesktopAcrylicBackdrop`，降级规则完善 | ★★★★★ `ShaderEffect`/粒子/任意 GPU 效果 | ★★★★☆ 自绘，效果好但要自建材质 | ★★★★☆ 同 Flutter |
| 大图渲染上限 | ★★★★☆ Skia/D3D11(ANGLE)；单纹理 16384 上限→必须分块；`NativeControlHost` 可接原生面 | ★★★☆☆ XAML `Image` 会整图解码；自绘需 Win2D/Composition（**未核实**具体上限） | ★★★★★ 自带 SceneGraph/纹理，Qt Quick 分块成熟 | ★★★★★ Impeller/Skia | ★★★★☆ Skiko |
| CJK 文本 | ★★★★☆ HarfBuzz 8.3.1.3 + Skia 3.119.4（[源码] 依赖清单）；**竖排 advance 未合并**（PR #22184 open, 11/17） | ★★★★☆ DirectWrite，系统级 CJK 好；竖排 未核实 | ★★★★☆ 系统字体栈强；**竖排 未核实** | ★★★☆☆ 自绘文本，CJK 分词/回退需自管 | ★★★☆☆ 同 Flutter |
| IME / 无障碍 | ★★★★☆ Win32 UIA 无障碍；IME 有实装，候选窗位置曾修（PR #18759） | ★★★★★ 系统级 TSF/UIA，最稳 | ★★★★☆ 原生 IME | ★★☆☆☆ Windows IME 有 **open issue**（见 §4.4） | ★★☆☆☆ IME 长期问题域 |
| 打包体积/签名 | ★★★★★ **实测**：单文件自包含 34.24MB / 单文件框架依赖 23.44MB(5文件) / 未裁剪单文件 90.88MB | ★★☆☆☆ 官方：**不能出单文件 exe**，WinAppSDK 原生依赖必须散落 | ★★☆☆☆ PySide6 wheel 百 MB 级，PyInstaller 后更大 | ★★★☆☆ 自包含体积中等 | ★★☆☆☆ JVM 运行时 |
| 学习/人力成本 | ★★★★☆ C#+XAML，项目里已有 TS/React 心智可平移 | ★★★☆☆ WinUI 生态资料多但坑多（模板/打包） | ★★☆☆☆ 要么 C++，要么 Python(UI)与 Core 同进程 | ★★☆☆☆ Dart 新语言 | ★★☆☆☆ Kotlin/JVM 新语言 |
| 迁移工作量（四页+57 命令+184 调用点+60 测试） | **200–400 人日**（§6，[推断]） | 同量级 + 打包/更新链更贵 | 同量级或更高（多语言） | 同量级 | 同量级 |
| 许可证风险 | ★★★★★ MIT（Avalonia 仓库 license=MIT，[一手] NuGet/GitHub API） | ★★★★★ 微软 SDK | ★★☆☆☆ **PySide6 = LGPL-3.0 / GPL**（PyPI `license` 字段）；Qt 商业授权另议 | ★★★★★ BSD | ★★★★☆ Apache-2.0 |

**矩阵读法**：Avalonia 与 WinUI3 在"视觉/材质"上都能达标，差距在**换肤机制（运行时）**与**打包形态（单文件）**；QML 在"极致视觉"上最强但换肤与许可/进程模型拖后腿；Flutter/Compose 的桌面短板集中在 **IME 与原生集成**，恰是输入密集的翻译工作台最不能容忍的。

---

## 3. 逐项核查（对应任务清单 1–7）

### 3.1 Avalonia 11

**① Windows `TransparencyLevelHint` 的 Mica/Acrylic 与版本要求 —— ✅ 已核实**

- `WindowTransparencyLevel` 枚举含 `None / Transparent / Blur / AcrylicBlur / Mica`，源码注释明确：`Mica` "will only work on Windows 11"。[源码] <https://raw.githubusercontent.com/AvaloniaUI/Avalonia/main/src/Avalonia.Controls/WindowTransparencyLevel.cs>
- 官方 Windows 平台指南给出**最低版本**与用法：
  - `Transparent` Win7+；`AcrylicBlur` **Win10 1803+**；`Mica` **Windows 11**；
  - 必须 `Background="Transparent"` 才生效；`ActualTransparencyLevel` 可在运行时读取实际生效级别；不可用时按列表顺序回退；
  - 警告：省电模式/RDP/虚拟会话下 **OS 可能直接抑制透明**，必须准备不透明回退；
  - 合成模式 `WinUIComposition` 需 **Win10 build 17134+** 且 `RenderingMode` 含 `AngleEgl`；另有 `DirectComposition`(Win8+)、`LowLatencyDxgiSwapChain`(FL11_3, Win8.1+，低输入延迟但无透明/模糊)、`RedirectionSurface`(兜底)。
  [一手文档] <https://raw.githubusercontent.com/AvaloniaUI/avalonia-docs/refs/heads/main/docs/platform-specific-guides/windows.md>
- **结论**：Mica 需 **Win11**（比父任务引用的 DWM `22621+` 更宽松地写在"Windows 11"，具体 build 门槛以 DWM backdrop API 为准 [推断]）；Win10 走 `AcrylicBlur` 或纯色回退。渲染路径 = **Skia → ANGLE → D3D11**，非 GPU 环境自动软渲染回退。

**② ControlTemplate / ResourceDictionary 是否支持运行时动态换肤 —— ✅ 已核实（这是 Avalonia 最强项）**

- `ThemeDictionaries`（`Light`/`Dark`/`Default` 键）+ `{DynamicResource}` 是官方换肤机制；`RequestedThemeVariant` 可在 `Application`/`Window`/`ThemeVariantScope` 任一层级覆盖，**默认跟随系统**并可运行时改；`ThemeVariantScope` 支持子树单独换。[一手文档] <https://docs.avaloniaui.net/docs/styling/theme-variants>
  - ⚠️ 官方 caution：`ThemeDictionaries` 里的资源**只对 `DynamicResource` 可见**，`StaticResource` 会抛异常。
- `ControlTheme`：**"Unlike regular styles … a control theme can be replaced entirely"**（可整体替换），存于 `ResourceDictionary`，通过 `x:Key` 全局命中（`{x:Type Button}`）或单实例 `Theme="{StaticResource ...}"`；内部可嵌套 `Style Selector="^:pointerover"` 描述交互态。[一手文档] <https://docs.avaloniaui.net/docs/styling/control-themes>
- **结论**：主题中心 = 每套皮肤一个 `ControlTheme` 字典 + 颜色令牌字典；切换 = 换 `RequestedThemeVariant` 或替换资源字典，**不需要重启**。这正是用户要的"内置主题中心"的技术底座。**且现有 `tokens.css`（37 色/字号/圆角/间距）可 1:1 转成 C# `ResourceDictionary`**（[推断]，S7 依据：令牌已是声明式数据）。

**③ 内置 Transitions / Animations —— ✅ 已核实**

- `Transitions`（CSS 风格，监听属性变化做补间）：官方列出 13 种 transition 类型（`DoubleTransition`/`BrushTransition`/`ColorTransition`/`TransformOperationsTransition`/`BoxShadowsTransition`…），支持 `Easing`、`Delay`、`Duration`，也可挂在 Style 的 Setter 上；README 级示例即 `:pointerover` 悬停补间。[一手文档] <https://docs.avaloniaui.net/docs/graphics-animation/control-transitions>
- 文档站点同时提供 `Animations` / `Keyframe Animations` / `Page Transitions` / `Composition Animations` / `Easing Functions` / `Effects` / `Custom rendering` / `Bitmap blend modes` 等页（同一导航树可见），说明动画体系完整。[一手文档] 导航项见上页；具体页 <https://docs.avaloniaui.net/docs/graphics-animation/animations>

**④ 文本栈（HarfBuzz?）与 CJK/竖排 —— ⚠️ 一半核实**

- **HarfBuzz 确认**：Avalonia 仓库中央包管理文件含 `HarfBuzzSharp 8.3.1.3`、`SkiaSharp 3.119.4`、`Silk.NET.Direct3D11`、`Avalonia.Angle.Windows.Natives`。[源码] <https://raw.githubusercontent.com/AvaloniaUI/Avalonia/main/Directory.Packages.props>
  → 文本 shaping 走 HarfBuzz（复杂脚本/连字/字距），光栅化走 Skia。**这是相比 Pillow 无 Raqm 的实质提升**（父任务 AC5 已证 Pillow 侧缺 kerning/ligature）。
- **竖排（tategaki）不可用**：`[Text] Glyph Outline Part 11/17 - VVAR vertical advances` **state=open、merged=false**（created 2026-09-08，updated 2026-10-19，additions 1028），PR 正文明确 "Vertical text is where a variable font without VVAR goes wrong: **tategaki CJK**, Mongolian and classical layouts get default-instance advance heights"，且整条工作流是 17 个 PR 的堆叠。[一手] <https://github.com/AvaloniaUI/Avalonia/pull/22184>（API 实测 `state=open`, `merged=false`）
- **结论（重要）**：**不要指望任何 UI 栈做日文竖排排版**。成品页竖排继续由 Core（Skia+HarfBuzz 或 Pillow+Raqm）渲染成图，UI 只负责显示图 —— 这条约束在 Avalonia/WinUI/QML 上都一样，写进架构约束而不是选型缺点。

**⑤ `dotnet publish -p:PublishSingleFile` 体积 —— ✅ 已本机实测（本报告最有说服力的数字）**

测试工程：`_spike/avalonia-size/`（Avalonia 11.3.22，`net9.0`，`UsePlatformDetect`，FluentTheme，含 `TransparencyLevelHint=Mica`，仅用于测量）。SDK：.NET 9.0.308。RID：`win-x64`。

| 发布形态 | 文件数 | 总大小 | 主产物 |
|---|---|---|---|
| `-p:PublishSingleFile=true --self-contained false`（框架依赖） | 5 | **23.44 MB** | `avalonia-size.exe` 7.55 MB + `libSkiaSharp.dll` 8.98 + `av_libglesv2.dll` 5.17 + `libHarfBuzzSharp.dll` 1.72 |
| `-p:PublishSingleFile=true --self-contained true -p:IncludeNativeLibrariesForSelfExtract=true` | 2 | **90.89 MB** | 单 exe 90.88 MB |
| `--self-contained true -p:PublishTrimmed=true`（未单文件） | 75 | 41.32 MB | exe + coreclr 4.57 + System.Private.CoreLib 2.74 + Skia 8.98 |
| **`--self-contained true -p:PublishSingleFile=true -p:PublishTrimmed=true`（推荐形态）** | **2** | **34.24 MB** | **单个 exe 34.23 MB** |

[实测] 完整命令与输出：`_spike/publish-log.txt`、`_spike/publish-log2.txt`
- 裁剪告警（可接受但需登记）：`IL2026`（Built-in COM 不支持裁剪）、`IL2104`（`Avalonia.DesignerSupport` 产生裁剪告警）。→ 生产要用 `TrimMode=partial` + 保留 `Avalonia.Themes.*`，[推断] 全量裁剪（`TrimMode=full`）有 XAML/反射风险，需 spike 验证真实页面的绑定是否存活。
- **对比 WinUI3**：官方文档明写 *"`dotnet publish` … **cannot produce a single-file EXE for WinUI 3 apps** — the native Windows App SDK runtime dependencies must remain as separate files"*。[一手文档] <https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/self-contained-deploy/deploy-self-contained-apps>
- 版本事实：NuGet 索引实测 **11.x 最新 = 11.3.22**，且 **12.x 已发布至 12.1.4**。[实测] <https://api.nuget.org/v3-flatcontainer/avalonia/index.json> → 结论：起步用 **11.3.22**（生态/文档/第三方控件最成熟，[推断]），**12.x 是否上要在 spike 里单独决策**（文档站已有 "Breaking changes in Avalonia 12" 页：<https://docs.avaloniaui.net/docs/avalonia12-breaking-changes>）。任务卡写的"Avalonia 11"在当前时点仍成立，但**不是最新大版本**，需 Lead 知情。

**⑥ IME / 高 DPI / StorageProvider 文件对话框 —— ✅ 基本核实**

- 高 DPI：`DpiAwareness` 默认 **`PerMonitorDpiAware`**（跨屏自动换缩放），布局全程设备无关像素；`Screen.Scaling` 可读；位图自动选 `@2x`。[一手文档] 同 windows.md
- 文件对话框：**Win32 原生 `IFileDialog`**，支持类型过滤/初始目录/多选；剪贴板、OLE 拖放、`Launcher` 同为 Win32 实现。[一手文档] 同 windows.md；Avalonia 的跨平台抽象层为 `IStorageProvider`（文档：<https://docs.avaloniaui.net/docs/services/storage/storage-provider>）
- 无障碍：Windows 上暴露 **UI Automation**，内置控件自带 automation peer，Narrator/NVDA 可读。[一手文档] 同 windows.md
- IME：存在已合并的 IME 相关实现（`Windows IME (#7007)` commit：<https://github.com/AvaloniaUI/Avalonia/commit/d518202d9b2455762321d5f2c6c044c30496ad1c>）与 **拼音 IME 候选窗位置修复 PR #18759**（<https://github.com/AvaloniaUI/Avalonia/pull/18759>）。→ 有 IME，且曾有过候选窗定位缺陷 → **spike 必须实测微软拼音/日语 IME**（见 §7 第 7 项）。
- 逃生口：`NativeControlHost` 可嵌 HWND 原生控件（**但它不参与 Avalonia 正常 z 序、不支持透明/变换，裁剪受宿主边界限制** [一手文档] 同 windows.md）→ 若将来阅读器要自研 GPU 面（父任务 B 路线），Avalonia 有正规入口，不必换栈。

**⑦ GPU 渲染后端 —— ✅** 默认 `AngleEgl`（Skia→ANGLE→D3D11），可选 `Wgl`/`Vulkan`/`Software`；合成可选 `WinUIComposition`/`DirectComposition`/`LowLatencyDxgiSwapChain`/`RedirectionSurface`。[一手文档] windows.md

### 3.2 WinUI 3（Windows App SDK）

**① Mica 原生 —— ✅**
`Window.SystemBackdrop = new MicaBackdrop()`，`MicaKind.Base/BaseAlt`；`DesktopAcrylicBackdrop`（Win10 17763+）；材质在 RDP / 显存不足 / 系统关"透明效果" / 高对比度下**自动回退**（Mica 不受省电模式影响，Desktop Acrylic 受影响）；`SystemBackdropElement` 可给单个元素加材质但 **需 Windows App SDK 2.0**。[一手文档] <https://learn.microsoft.com/en-us/windows/apps/develop/ui/materials>
额外坑：`AcrylicBrush` 是 **in-app acrylic**（只模糊应用内内容），UWP 的 `BackgroundSource=HostBackdrop` **在 WinUI 3 不可用** —— 想要"透桌面"只能用 `SystemBackdrop`。

**② 深度换肤（重写控件模板）的实际可行性 —— ⚠️ 可行但摩擦大（一半有文档支撑）**

- **硬约束（已核实）**：`FrameworkElement.RequestedTheme` 可以**运行时改**；但 `Application.RequestedTheme` **运行期设置会抛异常**（"throws an exception if you try to set it while the app's running"）；且 `ElementTheme.Default` 在 Windows 上**恒等于 Dark**。[一手文档] <https://learn.microsoft.com/en-us/windows/windows-app-sdk/api/winrt/microsoft.ui.xaml.frameworkelement.requestedtheme?view=windows-app-sdk-1.7>
  → 主题中心若想"一键切整套皮肤"，必须给根元素/每个窗口设 `RequestedTheme`，或维护自己的资源字典集合；**不能**走 App 级属性。跨窗口（多窗/弹出层）时容易漏。
- **推断**：默认控件样式由框架 `generic.xaml` 提供，要做到"完全不像 WinUI"必须为**每个用到的控件**提供整份 ControlTemplate（不能只改颜色）。微软官方没有一句话承诺"任意深度换肤"的简单路径 —— **这一条我给 [推断]，不给一手结论**。这也是我把 WinUI3 放"备选"而非"主选"的核心原因。

**③ 打包/运行时依赖 —— ❌ 单文件不可行（已核实）**
`WindowsAppSDKSelfContained=true` 可把 WinAppSDK 框架包内容释放到输出目录，`.NET` 也要一并 self-contained；但**原生 WinAppSDK 运行时依赖必须保持为独立文件**，`dotnet publish` 做不出单文件 exe（原文见 §3.1⑤ 同一链接）。→ 安装包/更新链比 Avalonia 贵。

**④ 与 .NET 9 兼容 —— [未核实]**
Avalonia 仓库自身把 `Microsoft.WindowsAppSDK` 钉在 `1.8.260209005`（[源码] Directory.Packages.props），说明 1.8 是当前稳定线；但 **"WinAppSDK 1.8 + .NET 9" 的组合本次未取得官方兼容矩阵，也未本机验证** → 标 [未核实]，列入 spike。

### 3.3 Qt 6 / QML（C++ 或 PySide6）

- **ShaderEffect / 动画**：`ShaderEffect` 是 Qt Quick 官方 QML 类型（GLSL 片段着色器，可做任意后处理）；Qt Quick 还有粒子系统、`PropertyAnimation`/状态机动画。视觉效果上限**最高**。[一手] <https://doc.qt.io/qt-6/qml-qtquick-shadereffect.html>（类型存在已确认；具体条目**未逐页摘录**）
- **主题切换（决定性短板，已核实）**：`QQuickStyle::setStyle()` 官方两处 Note：*"The style must be configured **before** loading QML that imports Qt Quick Controls. It is **not possible to change the style after the QML types have been registered**."* + *"QQuickStyle is not supported when using compile-time style selection."* [一手文档] <https://doc.qt.io/qt-6/qquickstyle.html>
  → 运行时"换一整套控件外观"必须自建主题层（QML 单例 + 属性注入 + 每个控件显式读主题），等于**自己实现一遍你想要的换肤系统**，且不能复用 Qt 自带 style 实现。
- **打包体积/坑**：PySide6 在 6.12.0 的 `requires_dist` = `PySide6_Essentials` + `PySide6_Addons` + `PySide6_WebEngine` + `PySide6_Pdf`；历史 win_amd64 wheel 单个 156.6 MB（6.2.4）。[一手] <https://pypi.org/project/PySide6/> → PyInstaller 产出必然 ≥150–300 MB 量级（[推断]，本次未实测）。
- **许可证（必须写进决策）**：PyPI 的 `license` 字段为 **`LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only`**（同上链接）。Qt 商业授权另议。→ 若选 PySide6，**LGPL 的"可重链接"义务 + Qt 动态库分发合规**要法务过一遍；这不是"技术上不行"，是"要额外背合规"。
- **CJK 竖排 —— [未核实]**：本次未取得 Qt 官方对 tategaki 的一手说明，**不得假设有**。
- **进程模型风险（[推断]，但基于本仓库事实）**：PySide6 UI ⇒ UI 与 47,065 行 Core 同进程（GIL 争用 + 一个崩溃全崩），而这套产品的卖点之一是"Core 崩溃可恢复"（见 S10/S11 的 sidecar 设计）。

### 3.4 Flutter / Compose Desktop —— 一句话结论

**Flutter**：Windows 端 CJK **输入法**存在一手 open issue —— `[Windows][IME] Composition stops after the Flutter view regains focus`（<https://github.com/flutter/flutter/issues/190042>）、`[Windows][Desktop][IME] IME is activated and shows popup when no Flutter TextField has focus`（<https://github.com/flutter/flutter/issues/181313>）；桌面原生集成（菜单/托盘/文件对话框/无障碍）需大量插件补。→ **输入密集的翻译工作台不适用**。
**Compose Desktop**：同属 Skia 自绘 + JVM 运行时；IME/输入法是长期问题域（本次仅取到 `PlatformTextInputMethodRequest` 相关 PR <https://github.com/JetBrains/compose-multiplatform-core/pull/2122>，**未核到"已修复"的一手结论**）→ 结论同上，且多背一个 JVM。

### 3.5 大图渲染：4000×60000 在 Skia 自绘栈里的可行路径

**先算三个硬数字**

1. **像素量**：4000 × 60000 = **2.4 亿 px**；RGBA8888 = **960 MB**（单张全解码常驻内存）。若再算 DPR2 的渲染目标与双缓冲，不可接受。
2. **单纹理上限（这是死线）**：D3D11 Feature Level 11 的 **`D3D11_REQ_TEXTURE2D_U_OR_V_DIMENSION = 16384`** —— **任一维不能超过 16384**；同时单资源大小上限为 `min(max(128, 0.25×VRAM), 2048) MB`。[一手文档] <https://learn.microsoft.com/en-us/windows/win32/direct3d11/overviews-direct3d-11-resources-limits>
   → 60000 ≫ 16384，**"一张纹理画完"在 D3D11 上不可能**，与 UI 框架无关。
3. **现有产品上限**：host 侧 `MAX_RESOURCE_BYTES = 256 MiB`（[源码] `resource_protocol.rs:41`），且 chunk 16 MiB 逐块 fetch。4000×60000 的无损 PNG 很容易顶到上限 → 通道本身也要改。

**可行路径（三栈通用，差异只在 API 入口）**

- 路径 = **分块（tile）+ 视口内按需解码 + LRU 缓存**：
  - `4000×60000` 切成 `4000×2048` 的带 → 30 块，每块 RGBA ≈ 32.8 MB（4B/px），视口内常驻 3–5 块 ≈ 100–165 MB（[推断]，按视口高 2048 估）；
  - **关键难点在"解码"**：JPEG/PNG 的 `decode` 基本是整图解码（Pillow/Skia 都不擅长任意区域解码 [推断]），所以 960 MB 的瞬时峰值躲不掉 → **必须由 Core 侧预切块/建金字塔**（Pyramid/TIFF 风格），UI 侧只按需读块文件。这与"翻译成品页由 Core 渲染"的既有架构天然契合。
- **Avalonia**：自定义 `Control` 重写 `Render(DrawingContext)`，用 `DrawImage(IImage, srcRect, destRect)` 逐块画；`RenderOptions.BitmapInterpolationMode` 控制采样（文档有 "Image interpolation" 页）。若要零拷贝/零重采样，可上 `NativeControlHost` 挂原生面，或走 `CustomPlatformGraphics`（windows.md 有该选项）。**上限由上面 16384 决定，不由 Avalonia 决定**。可行 ✓
- **WinUI 3**：XAML `Image`/`BitmapImage` 是**整图解码**语义（对 960MB 的图是灾难 [推断]）；要分块自绘得引 **Win2D / `Microsoft.UI.Composition`**，其纹理上限同样是设备 16384（D3D11 级）—— 具体 API 上限**本次未核实**（标 [未核实]）。可行但**比 Avalonia 多一层依赖**。
- **Qt/QML**：Qt Quick 的 `Texture`/`QSGTexture` + 分块 item 是成熟套路，且 `ShaderEffect` 可做高质量重采样。可行 ✓（但 Qt 已因换肤/许可被排除）
- **结论**：**大图渲染不是"选栈的决定因素"，而是"必须自建分块渲染器"的工程项**。决定性因素是"该栈有没有低摩擦的自绘/原生面入口" → Avalonia 有 `Render` + `NativeControlHost` 双入口，WinUI3 需要 Win2D 外挂。

### 3.6 迁移成本：105 个 `.tsx`/28.6k 行 + 57 命令/184 invoke → C#/Avalonia 区间

**依据（全部可复核）**

| 输入 | 数值 | 来源 |
|---|---|---|
| `.tsx` | 105 文件 / 28,602 行 | [实测] S1 |
| `.ts`（含 client/state/工具） | 52 文件 / 8,734 行 | [实测] S1 |
| 前端合计 | 37,336 行 | [实测] |
| 测试文件 | 60 个（其中 101 处 `invoke` 在测试内） | [实测] S1/S4 |
| 四页 | 3,660 行 | [实测] S2 |
| 命令契约 | 57 个 | [实测] S3 |
| 生产 invoke 站点 | 83 处 / 6 个 client 模块 | [实测] S4 |
| 可复用资产 | `tokens.css` 37 色 + 字阶/圆角/间距（声明式，可直接转 ResourceDictionary） | [实测] S7 |

**换算模型（[推断]，给出公式便于审阅者改参数）**

- UI 重写：`37,336 行 × 折算系数 0.6–1.0（C#/XAML 等效行）÷ 吞吐 120–200 行/人日` ≈ **112–311 人日**
  - 折算系数<1 的理由：XAML 布局比 CSS 冗长，但 MVVM 绑定 + 无 CSS 调试往返；且令牌层可搬。
- IPC 适配：`57 命令 × 0.3–0.8 人日` ≈ **17–46 人日**（生产侧只有 6 个 client 需重写为 typed service；**测试要用 60 个前端测试的断言语义重写**）
- 主题中心 + 材质 + 动效：**15–30 人日**（任何栈都要做，Avalonia 因 `ControlTheme`/`Transitions` 可少做"造轮子"部分）
- 大图/分块渲染器（阅读器+工作台）：**25–50 人日**（§3.5；含与 Core 的切块契约）
- 平台适配（IME/DPI/原生对话框/无障碍/单文件打包/签名/自动更新）：**15–30 人日**
- 回归与 parity（57 命令 × 184 调用点 + 60 测试文件 + 四页视觉基线）：**25–50 人日**

**合计：200–400 人日**（中位 ≈ 290）。与父任务 `routes/ROUTES.md` 给出的 C 路线 **180–320 人日** 同量级；我的**上界更高**，因为我显式计入了 **60 个测试文件的重写、主题中心、平台适配、安装/更新链** —— 这四项在原估算里没有单列。**不给单值：这是工程判断，不是测量。**

**一个降本事实（[推断]）**：`invoke` 的 101/184 在测试里、生产只剩 83 处并集中在 6 个模块（S4）→ 重写的**接口面**远比"184 处散落调用"小；真正贵的是 **60 个测试文件的断言语义**和**四页交互细节**。

### 3.7 与 Python Core 接线（含"离开 WebView 后能删什么"）

**现状（[源码]，见 S10–S12）**
- 已有 **两条 stdio JSON-lines 通道**：资源控制面 (wire v1) + Core protocol **2.3**；请求形如 `{"id":1,"method":...,"params":...}` 单行 JSON，响应取 `result` 或 `error.code`。
- spawn 已处理 Windows 无窗口（`CREATE_NO_WINDOW`）与打包模式（直接起 PyInstaller sidecar，无系统 Python 回退）。
- **已知坑必须继承**：冻结 sidecar 用 **cp936** 解 stdin，host 侧必须把非 ASCII 转 `\uXXXX`（`library_bridge.rs:17-29`，注释里有实测 mojibake）。

**三种接线方案对比（C# host ↔ Python Core）**

| 方案 | C# 实现 | 复用现有契约 | 新增风险面 | 复杂度 | 结论 |
|---|---|---|---|---|---|
| **A. stdio JSON-lines（推荐）** | `System.Diagnostics.Process` + `StandardInput/Output`（现有 Rust 逻辑可 1:1 搬） | **100% 复用** protocol 2.3 与 wire v1 | 无端口、无认证面；子进程生命周期由 host 管 | **低** | **主选** |
| B. Windows 命名管道 | `NamedPipeServerStream/ClientStream` | 需新增 Python 端管道路由（`win32pipe`/`pywin32` 或 asyncio pipes） | 需 ACL 收敛到当前用户；多客户端需自己仲裁 | **中** | 仅当要多进程/多窗口共享一条 Core 通道时才值得 |
| C. 本地 HTTP（+gRPC） | Kestrel + `Grpc.Net.Client` / `HttpClient` | 需给 Core 加 HTTP/gRPC 层与 protobuf/序列化 | **端口占用 + 防火墙/杀软误报 + 必须 loopback-only + token**；gRPC 还要 protobuf 与 Python 依赖 | **高** | 不推荐：纯增面，无收益 |

**离开 WebView 后应删除的面（这是本次裁决的实质收益，[推断] + [源码] 支撑）**

1. **`m2res` 自定义 scheme 整条**：`http://m2res.localhost/m2id/<43字符id>?chunk=n`、CORS、`Cache-Control: no-store`、opaque-ID 间接层 —— 全部只因**存在"不可信 Web 内容"这一消费者**而存在（[源码] `resource_protocol.rs:1-34`、`resourceChannel/client.ts:1-11`）。
2. **每请求全量 SHA-256**：`resource_protocol.rs` 在**每次** chunk 请求上"顺序读全文件算摘要"（`:439`），父任务 AC2 实测该哈希占 657KB 页端到端 **22.9 ms 中的 4.65 ms（20.4%）**。原生 host 里字节不再跨信任边界 → 可降级为**廉价身份校验**（`volume_serial + file_index + size`，已在 grant 里）+ 仅在加载时校验一次摘要。
   - ⚠️ **不要**连身份校验一起删：grant 与读取之间文件仍可能被本机其它进程替换，`volume_serial/file_index/size` 三件套是几乎零成本的第一道锁（[推断]）。**威胁模型从"防 Web 内容"变成"防本机并发改写"，风险降低但不归零。**
3. **16 MiB chunk + 拼 Blob**：前端逐 chunk fetch 再拼 `Blob`（`client.ts:81-101`）是为浏览器 `<img>` 服务的；原生侧可直接 `SKBitmap.Decode(stream)` 或按块加载，**预取/复用/缓存**都变成普通代码。
4. 顺带可删：WebView2 runtime 依赖与 Evergreen 版本回归风险（父任务 `routes/ROUTES.md` 已登记 #5752/#5642/#5426 三个 open issue）。

**保留不动的**：57 个命令的**名称与 DTO**（避免"契约变了但 UI 没变"的双向漂移）、Core protocol 2.3 版本号、`CREATE_NO_WINDOW`、ASCII-escape 规则（**除非**重打 sidecar —— 那是另一个任务）。

---

## 4. 推荐与路由裁决

### 4.1 主选：C#/.NET 9 + Avalonia 11.3.x

**三条决定性理由**
1. **"换主题/皮肤 + 内置主题中心"是本次需求的头号新增项，而 Avalonia 是唯一把"运行时整体替换控件外观"做成官方一等机制的栈**（`ControlTheme` 可整体替换 + `ThemeDictionaries`/`DynamicResource` + `ThemeVariantScope` 子树覆盖）。WinUI3 被 `Application.RequestedTheme` 运行期抛异常卡住；QML 被"注册后不能改 style"卡死。
2. **单文件分发实测 34.24 MB**（自包含+裁剪+单文件），而 WinUI3 官方明说做不出单文件 exe —— 这直接决定安装/更新/签名的工程量。
3. **技术底座正好补上现产品最痛的两处**：Skia+D3D11+ANGLE 的 GPU 渲染（父任务 F9 长条滚动 avg 17.53 ms/p95 33.3 ms 的掉帧），以及 HarfBuzz shaping（父任务 AC5 证 Pillow 侧无 kerning/ligature 的排版欠账）。

**三条必须同时成立的前置条件（写进裁决，别当默认）**
- **C1**：竖排/成品页排版**留在 Core 渲染成图**，UI 不承诺原生竖排（§3.1④）。
- **C2**：大图必须走 **Core 预切块 + UI 分块贴图**（§3.5），不允许 `Image` 整图直读。
- **C3**：主题中心用 `ControlTheme` 字典 + 令牌字典实现，**不押注任何"第三方主题包"**；11.3.22 vs 12.x 的版本选择在 spike 第 1 周内定（§7）。

### 4.2 备选：WinUI 3

**在什么条件下才翻牌**
- 用户明确要求 **100% Windows 原生观感**（系统控件、系统菜单、系统 IME 行为），且接受 **Windows-only**；
- 接受**不能单文件**（安装包里散落 WinAppSDK 原生依赖）+ 安装/更新链成本上升；
- 接受**主题中心降级设计**：主题 = 一组 `ResourceDictionary` + 每个窗口设 `RequestedTheme`，深度皮肤需为每个控件提供 ControlTemplate（[推断]）。
- 触发方式：主选 spike 第 1 周的 **IME / 大图 / 主题切换** 任何一项硬失败，且 Avalonia 侧无合理 workaround（如 IME 候选窗问题在本机复现且 upstream 未修）→ 才启动 WinUI3 的 3–5 人日对照 spike。

### 4.3 明确不推荐

| 栈 | 不推荐的硬理由（全部有据） |
|---|---|
| **Qt 6 / QML** | ① 运行时换肤被官方文档否决（`QQuickStyle` 注册后不可改）；② 若走 PySide6 则 **UI 与 47k 行 Core 同 Python 进程**（GIL/崩溃隔离丢失）+ **LGPL-3.0/GPL 合规成本** + 百 MB 级打包；③ 若走 C++ 则引入第二语言/构建系统，人力成本再上台阶；④ CJK 竖排 [未核实]。 |
| **Flutter** | Windows **IME 有 open issue**（#190042 / #181313），输入密集场景不可接受；桌面原生集成靠插件。 |
| **Compose Desktop** | 同上 + JVM 运行时；IME 修复状态 [未核实]。 |

---

## 5. 与 Python Core 的接线方案（落地版）

```
┌──────────────────────────── C# Host (Avalonia, .NET 9) ─────────────────────────────┐
│  UI 层：Shelf / Workbench / Reader / Settings / ThemeCenter                          │
│    ↕ (typed services, 1:1 对应现有 57 命令)                                          │
│  Host 服务层：LibraryService / SettingsService / RegionService / ReaderService /     │
│               ResourceService(分块贴图) / ThemeService                               │
│    ↕                                                                                 │
│  CoreClient（**stdio JSON-lines，复用 protocol 2.3 + wire v1**）                      │
│    · Process + RedirectStandardInput/Output；CREATE_NO_WINDOW                         │
│    · 请求：{"id":N,"method":"...","params":{...}}\n（非 ASCII → \uXXXX，保 cp936 兼容） │
│    · 响应：{"result":...} 或 {"error":{"code":"..."}}                                 │
└───────────────────────────────────┬──────────────────────────────────────────────────┘
                                    │ stdio（无端口、无认证面）
┌───────────────────────────────────▼──────────── Python Core（既有，217 文件/47k 行）───┐
│  SQLite / OCR / 翻译 / 修复 / 渲染 / 切块输出（新增：页级 tile 金字塔）                │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

**实施顺序（与风险对齐）**
1. **先搬协议，不搬业务**：C# 写 `CoreClient`（spawn + 单行 JSON 往返 + 错误码透传 + ASCII escape），跑通 `ping` 与 `list_books`。**验收：中文书名往返不变 mojibake**（否则复刻 S12 事故）。
2. **再搬 57 命令**：按现有 domain client 的 6 个模块分组（settings / library / region / reader / resourceChannel / workbench）。
3. **最后删面**：在资源通路切换为"Core 给 tile 文件路径 → C# 直接读"之后，一次性删除 `m2res` scheme、CORS、`no-store`、每请求 SHA-256（保留 grant 三件套身份校验）。
4. **保留**：`CREATE_NO_WINDOW`、ASCII escape、`MAX_RESOURCE_BYTES` 之类的上限（换成 tile 尺寸上限）。

---

## 6. 第一周 spike 验收清单（可测量；每条给判定阈值与测法）

> 原则：**一周内只验证"能不能"，不铺开重写**。任一项硬失败 → 触发 §4.2 备选评估。全部产物落 `ui-stack/spike-<n>/`。

| # | 验收项 | 阈值（判定） | 测法 | 当前状态 |
|---|---|---|---|---|
| 1 | 单文件发布 | **1 个 exe ≤ 45 MB**，双击可启动 | `dotnet publish -c Release -r win-x64 -p:PublishSingleFile=true --self-contained -p:PublishTrimmed=true`；`Get-ChildItem` 统计 | **已预跑：34.24 MB ✅**（空壳工程，需在真实页面复测裁剪存活） |
| 2 | 冷启动 | 进程创建→窗口可见 **p50 ≤ 600 ms**（对照现栈 558 ms 中位） | 3 次冷启，ETW/`Process.Start` 时间戳 + 截图首帧 | 待测 |
| 3 | Mica 真机可见 + 回退 | Win11 22621+：`ActualTransparencyLevel == Mica` 且截图取色证明非纯色；Win10：回退不透明、无黑边 | 真机 + 截图；`ActualTransparencyLevel` 打日志 | 待测 |
| 4 | 运行时换肤 | 主题中心 **3 套主题**（dark/light/1 套自定义）切换 ≤ **100 ms**（P95），全窗截图差分 **<0.1% 像素残留旧色**，不重启 | 自动截图差分脚本 | 待测 |
| 5 | 大图分块渲染 | 4000×60000 真实页切成 4000×2048 tile：滚动 **p95 ≤ 16.7 ms @DPR2**，内存峰值 **≤ 1.5 GB**，首块可见 **≤ 120 ms** | 自定义 `Control` + `DrawImage(srcRect,dstRect)`；ETW/GC 计数 | 待测（阈值 [推断]） |
| 6 | 竖排交付路径 | Core 渲染的竖排页（PNG）在 Avalonia 中 **1:1 像素显示**（无重采样：`BitmapInterpolationMode=None` 且 DPR2 截图像素比对一致） | 与 Core 输出图逐像素比对 | 待测 |
| 7 | IME | 微软拼音 + 日语 IME 各输入 20 字：**无丢字、候选窗位置正确**（含 PR #18759 行为） | 手工 + 截图 | 待测 |
| 8 | sidecar 复用 | C# `CoreClient` 跑通 `ping` + `list_books` + 取 1 页资源；**中文书名往返零 mojibake**；sidecar 无控制台窗口 | 对现有打包 sidecar exe 实测 | 待测 |
| 9 | 无障碍 | Narrator 可读出书架前 5 个条目的**名称与角色** | 手工 Narrator | 待测 |
| 10 | 安装/更新链 | 产出可签名安装包 **≤ 150 MB**，且能自动更新一次 | MSIX / Squirrel / Installer 任选一条 | 待测 |
| 11 | 版本决策 | 明确 **11.3.22** 还是 **12.1.4**，并记录 12 的 breaking change 影响面 | 读 <https://docs.avaloniaui.net/docs/avalonia12-breaking-changes> + 最小工程编译 | 待测 |

**spike 停止条件（省时间用）**：第 3、4、7 任一硬失败且上游无近期修复 → 停 Avalonia，转 WinUI3 对照 spike（3–5 人日）。

---

## 7. 风险登记

| # | 风险 | 等级 | 缓解 |
|---|---|---|---|
| R1 | **竖排排版被误当成"换栈就解决"** | 高 | 写进裁决 C1：竖排留在 Core，以图交付；spike #6 钉死"1:1 像素"即可 |
| R2 | 一次性重写引入回归（200–400 人日面） | 高 | 分阶段：先 CoreClient → 再 57 命令 → 再四页；60 个前端测试作为规格逐个迁移 |
| R3 | 裁剪（Trim）让 XAML/绑定在真实页面失效 | 中 | spike #1 用真实页面复测；必要时回退 `TrimMode=partial` → 体积上到 ~41 MB（多文件）或 90 MB（单文件未裁剪，实测） |
| R4 | IME 候选窗/输入法边界 | 中 | spike #7；失败则备选 WinUI3 |
| R5 | 主题中心做成"只有两套固定色"（没达到"皮肤"） | 中 | 用 `ControlTheme` 整体替换 + 令牌字典；spike #4 要求"自定义主题"一套 |
| R6 | 大图 tile 契约改动牵动 Core（切块/金字塔） | 中 | 先做"整页解码 + 视口分块绘制"保底，再上 Core 预切块；阈值分期 |
| R7 | Avalonia 版本线（11.3 vs 12）选错 | 低 | spike #11 一周内定；11.3.22 是 11.x 最新补丁（实测 NuGet） |
| R8 | **许可证**：Saber-Translator 是 **GPL-3.0** | 高（合规） | 见 §8，硬红线 |

---

## 8. GPL-3.0 硬标注（Saber-Translator）

**Saber-Translator 采用 GPL-3.0。** 本报告与后续实现只允许：

- ✅ **借鉴架构与流程**（例如"Flask/服务化分层、Pipeline 阶段划分、任务队列/状态机的心智模型"这类**思想**）；
- ❌ **不得拷贝其代码、文件、注释、资源**进本仓库（GPL-3.0 的 copyleft 会要求衍生作品整体以 GPL 发布，与本项目分发模型冲突）；
- ❌ 不得把其代码作为依赖、不得粘贴片段"再改改"；
- ✅ 若确需某算法思路，必须**独立实现**并在 Task 里记录"独立实现 + 参考的是公开思路而非代码"。

**本报告未包含 Saber-Translator 的任何代码。** 同理：若将来评估 PySide6，需法务确认 **LGPL-3.0 的可重链接义务**（§3.3），那是另一条独立合规线。

---

## 9. 外部资料核实表

| # | 事实 | 状态 | 来源 URL |
|---|---|---|---|
| E1 | `WindowTransparencyLevel` 含 Mica，注释"will only work on Windows 11" | 已核实（源码） | <https://raw.githubusercontent.com/AvaloniaUI/Avalonia/main/src/Avalonia.Controls/WindowTransparencyLevel.cs> |
| E2 | Windows 上 `TransparencyLevelHint` 全支持；Mica=Win11；AcrylicBlur=Win10 1803+；需 `Background=Transparent`；`ActualTransparencyLevel` 可查；省电/RDP 会抑制；`WinUIComposition`=Win10 17134+；`RenderingMode` 默认 AngleEgl；`DpiAwareness` 默认 PerMonitor；文件对话框=Win32 `IFileDialog`；无障碍=UIA；`NativeControlHost` 限制 | 已核实（一手文档） | <https://raw.githubusercontent.com/AvaloniaUI/avalonia-docs/refs/heads/main/docs/platform-specific-guides/windows.md> |
| E3 | Avalonia 依赖 HarfBuzzSharp 8.3.1.3、SkiaSharp 3.119.4、Silk.NET.Direct3D11、ANGLE | 已核实（源码） | <https://raw.githubusercontent.com/AvaloniaUI/Avalonia/main/Directory.Packages.props> |
| E4 | 运行时换肤：`ThemeDictionaries` + `{DynamicResource}` + `RequestedThemeVariant` + `ThemeVariantScope`；`StaticResource` 找不到主题字典资源 | 已核实（一手文档） | <https://docs.avaloniaui.net/docs/styling/theme-variants> |
| E5 | `ControlTheme` "can be replaced entirely"，可 `{x:Type}` 全局或 `Theme=` 单实例 | 已核实（一手文档） | <https://docs.avaloniaui.net/docs/styling/control-themes> |
| E6 | `Transitions` 13 种类型 + `Easing`/`Delay`/`Duration`，可挂 Style Setter | 已核实（一手文档） | <https://docs.avaloniaui.net/docs/graphics-animation/control-transitions> |
| E7 | Animations / Keyframes / Page transitions / Composition animations / Effects / Custom rendering 等页存在 | 已核实（文档导航） | <https://docs.avaloniaui.net/docs/graphics-animation/animations> |
| E8 | 竖排 advance（VVAR）PR **open、未合并**，Part 11/17，正文点名 tategaki CJK | 已核实（GitHub API：`state=open`,`merged=false`） | <https://github.com/AvaloniaUI/Avalonia/pull/22184> |
| E9 | 拼音 IME 候选窗位置修复 PR | 已核实（PR 存在） | <https://github.com/AvaloniaUI/Avalonia/pull/18759> |
| E10 | Avalonia `IStorageProvider` 文档 | 已核实（页面存在） | <https://docs.avaloniaui.net/docs/services/storage/storage-provider> |
| E11 | Avalonia 版本：11.x 最新 **11.3.22**；12.x 最新 **12.1.4** | 已核实（NuGet 索引） | <https://api.nuget.org/v3-flatcontainer/avalonia/index.json> |
| E12 | Avalonia 12 breaking changes 页存在 | 已核实（导航 + 页面） | <https://docs.avaloniaui.net/docs/avalonia12-breaking-changes> |
| E13 | WinUI 材质：`MicaBackdrop`(Win11)/`DesktopAcrylicBackdrop`(Win10 17763+)/`SystemBackdropElement`(需 WinAppSDK **2.0**)/`AcrylicBrush` 仅 in-app；降级规则 | 已核实（一手文档） | <https://learn.microsoft.com/en-us/windows/apps/develop/ui/materials> |
| E14 | WinUI3 自包含部署；**不能产出单文件 exe**（原文引用） | 已核实（一手文档） | <https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/self-contained-deploy/deploy-self-contained-apps> |
| E15 | `Application.RequestedTheme` 运行期设置**抛异常**；`ElementTheme.Default` 在 Windows 恒为 Dark | 已核实（一手文档） | <https://learn.microsoft.com/en-us/windows/windows-app-sdk/api/winrt/microsoft.ui.xaml.frameworkelement.requestedtheme?view=windows-app-sdk-1.7> |
| E16 | D3D11 FL11 `Texture2D U/V dimension = 16384`；单资源上限 `min(max(128,0.25×VRAM),2048) MB` | 已核实（一手文档） | <https://learn.microsoft.com/en-us/windows/win32/direct3d11/overviews-direct3d-11-resources-limits> |
| E17 | `QQuickStyle::setStyle` 必须在加载 QML 前；"not possible to change the style after the QML types have been registered"；不兼容 compile-time style | 已核实（一手文档） | <https://doc.qt.io/qt-6/qquickstyle.html> |
| E18 | Qt Quick `ShaderEffect` 类型存在 | 已核实（页面存在，未逐条摘录） | <https://doc.qt.io/qt-6/qml-qtquick-shadereffect.html> |
| E19 | PySide6 6.12.0 依赖 Essentials+Addons+WebEngine+Pdf；license=`LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only`；历史 win_amd64 wheel 156.6 MB(6.2.4) | 已核实（PyPI JSON） | <https://pypi.org/project/PySide6/> |
| E20 | Flutter Windows IME open issues（失焦后 composition 中断；无 TextField 焦点时 IME 仍激活弹窗） | 已核实（issue 标题） | <https://github.com/flutter/flutter/issues/190042>、<https://github.com/flutter/flutter/issues/181313> |
| E21 | Compose MP 文本输入相关 PR（**未核实是否修复 IME**） | 部分核实 | <https://github.com/JetBrains/compose-multiplatform-core/pull/2122> |
| E22 | WinUI3 深度换肤"每个控件都要整份 ControlTemplate" | **[推断]** | 依据 E15 + WinUI 资源模型；无官方"一句话"结论 |
| E23 | WinAppSDK 1.8 + .NET 9 官方兼容矩阵 | **[未核实]** | 旁证：Avalonia 自钉 1.8.260209005（E3） |
| E24 | Qt / WinUI3 / Flutter / Compose 的 **CJK 竖排**能力 | **[未核实]** | 未取得一手资料，不得当结论 |
| E25 | Win2D / `Microsoft.UI.Composition` 的具体纹理上限 | **[未核实]** | 底层受 E16 约束 [推断] |

---

## 10. 本目录证据清单

| 路径 | 内容 |
|---|---|
| `STACK_COMPARISON.md` | 本报告 |
| `_spike/avalonia-size/avalonia-size.csproj`、`Program.cs` | 体积测量用最小 Avalonia 11.3.22 工程（`net9.0`，含 `TransparencyLevelHint=Mica`）。**非产品代码**，`bin/obj` 已在测量后删除 |
| `_spike/publish-log.txt` | 3 种发布形态的完整命令与输出（23.44 / 90.89 / 41.32 MB） |
| `_spike/publish-log2.txt` | 单文件+裁剪形态（**34.24 MB**） |

复现命令（任一路径）：
```pwsh
dotnet publish _spike/avalonia-size -c Release -r win-x64 -o <out> `
  --self-contained true -p:PublishSingleFile=true `
  -p:IncludeNativeLibrariesForSelfExtract=true -p:PublishTrimmed=true -p:TrimMode=partial
```

---

## 11. 需要用户/Lead 裁决的点

1. **D1 是否接受"竖排留在 Core 以图交付"**（C1）。这是主选能成立的前提；若不接受（要求 UI 原生竖排排版），则**目前没有任何候选栈能达成** [依据 E8 + E24]。
2. **D2 是否接受 200–400 人日区间**（§3.6），以及是否采用"分阶段迁移（CoreClient → 57 命令 → 四页）"。
3. **D3 版本线**：11.3.22 起步，还是直接评估 12.1.4（spike #11）。
4. **D4 发行形态**：单文件 exe（34 MB）+ 安装器，还是 MSIX（需签名/证书链）。
5. **D5 是否授权第一周 spike**（§6 的 11 项）——不铺开重写，只出"能不能"的结论。
6. **D6 Win10 用户策略**：Mica 不可用 → AcrylicBlur 还是纯色回退（与父任务 D5 同一决策）。
