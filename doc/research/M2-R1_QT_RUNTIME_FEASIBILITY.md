# M2-R1 — Qt Runtime Feasibility Spike（研究报告与平台实测矩阵）

| 项 | 值 |
|---|---|
| Task | [M2-R1](../tasks/M2-R1.md)（`kind: research`，实验/研究；**不授权迁移实现**） |
| 规划依据 | [REBASELINE_PLAN](../REBASELINE_PLAN.md) M2 `FIRST_WAVE_RELEASED / BOUNDED_IMPLEMENTATION`；[AD-001](../AD-001_TARGET_DESKTOP_ARCHITECTURE.md) §23/§30/§34 |
| 解决目标 | [M2-D1 报告](M2-D1_HEADLESS_QT_COUPLING_AUDIT.md) 唯一 `UNVERIFIED` 项 **M2D1-22** |
| Owner | DeepSeek Harness（Reviewer/Integrator = Codex，禁止自审） |
| 固定代码 base | `6a68fdeb92d8a1c7903166a8076d6260bf8fa79a`（`master`） |
| Owner worktree HEAD（开工） | `5d989bab6c5c8a24a5112303f95c2b8eea356bdc`（`agent/deepseek/M2-R1-qt-runtime-feasibility`） |
| Delivery head | 本报告与 `verification/M2-R1/**` 随 Delivery commit 固定；准确 hash 与提交列表见本 Task 的 Handoff（`doc/handoffs/M2-R1-<delivery>.md`） |
| 实验日期 | 2026-09-25（Asia/Shanghai） |
| 被测环境 | **Python 3.12.3 + PySide6_Essentials 6.11.2 + shiboken6 6.11.2 + Qt 6.11.2 + Windows 11 专业版 10.0.26200（隔离 venv）** |
| 环境裁定 | **与生产口径匹配 → 结论有效**（不记 `BLOCKED`；依据见 §2） |
| 修改范围 | 仅本报告、`doc/tasks/M2-R1.md`、新 Handoff、`verification/M2-R1/**`。`src/**`、`tests/**`、打包、Schema、依赖清单、T3.2.1 证据**零修改** |
| 证据索引 | [verification/M2-R1/07-evidence-manifest.md](../../verification/M2-R1/07-evidence-manifest.md) |

## 0. 方法与证据口径

1. **只测真实生产适配器，不自造替身**：探针导入的正是生产类 `infrastructure.rendering.font_catalog.QtFontCatalog`、`infrastructure.rendering.qt_layout.QtTextLayoutEngine`、`infrastructure.rendering.qt_compositor.QtImageCompositor` 与端口 DTO `ports.rendering.ports.{LayoutRequest,RenderOp}`（只读导入，零修改）。
2. **版本对齐**：隔离 venv 内安装的是 `requirements.txt` 声明的同一版本口径（`PySide6_Essentials==6.11.2`、`shiboken6==6.11.2`，`01-environment.log:13-15`）。生产解释器（`C:\Python314`）与生产依赖清单从未被改动，也未向其安装任何包。
3. **平台经由真实 QPA 插件选择**：`QT_QPA_PLATFORM=windows|offscreen|minimal` 在 `import PySide6` **之前**写入环境变量；每次运行为**独立 OS 进程**，逐次记录退出码、墙钟时间与原始 stdout+stderr。
4. **无可见 GUI 不靠"没有截图"自证**：用 Win32 `EnumWindows` 枚举**本进程**的全部顶层 HWND，记录类名、标题、`IsWindowVisible`、是否最小化（`06-eventloop-and-window-census.log`）。
5. **量化文本渲染是否真的发生**：合成结果与输入基准图逐像素比较（`differing_pixels` / `non_white_pixels`），并保存两侧 PNG 供人眼复核；只报"PNG 非空"不足以证明字形渲染。
6. **确定性可复算**：输入基准 PNG 由探针内纯 `zlib`/`struct` 生成（每次运行字节一致，`a5f9021b…`），输出 PNG 记录 sha256；同进程重复合成与跨 3 次进程合成都比对 hash。
7. **隔离与只读**：`python -B` + `PYTHONDONTWRITEBYTECODE=1`；不导入 `bootstrap.app`、不打开 SQLite、不读写用户数据根；运行后 `src/**`、`tests/**` 内 `__pycache__` 计数为 **0**。
8. 本报告**不选择任何替代技术**，不构成实现授权（AD-001 §34）。

## 1. 执行摘要

**M2D1-22 由 `UNVERIFIED` 收敛为实测结论**：仓库测试夹具"offscreen 平台不带字体数据库"的陈述**成立且被量化**；但"无头完全不可行"**不成立**——真正的边界不是"能不能跑"，而是"跑出来的像素是不是产品语义的字形"。

1. **环境匹配生产口径，本 Task 不记 `BLOCKED`**：Python 3.12.3 + PySide6_Essentials 6.11.2 + Qt 6.11.2 + Windows 11 build 26200，QPA 插件 `qwindows/qoffscreen/qminimal` 齐备（`01-environment.log`）。
2. **平台字体库差异被实测确认**：`QFontDatabase.families()` = **windows 221 / offscreen 0 / minimal 0**；`hasFamily("Microsoft YaHei")` = `True / False / False`（`02/03/04-probe-*.log`）。
3. **三个平台都能装配并稳定运行，无可见 GUI**：`QGuiApplication` 构造、`QTimer`+`exec()` 事件循环、生产 text layout、生产 compositor 在 **3 平台 × 3 次独立进程**全部完成，`EXITCODE=0`，无异常、无挂起；同一平台 3 次运行的输出 PNG **sha256 完全相同**（逐字节确定性）。
4. **可见窗口证据**：windows 平台**可见窗口 0**（仅 3 个隐藏 HWND：`Qt6112ThemeChangeObserverWindow`、`Qt6112ScreenChangeObserverWindow`、`IME`），offscreen/minimal **HWND 总数为 0**。即"无可见 GUI 运行"在三个平台都成立。
5. **真正的差异在渲染语义**：offscreen/minimal 下 `QtFontCatalog` 回退到 `QFont().family()`（`Sans Serif`/`Helvetica`），`QFontMetrics` 退化为 `height=32(=pixel size)`、`descent=0`、`inFont("漫")=False`；compositor **仍会绘制并产出 PNG**，但字形是**实心替代方块（tofu）**——这是"成功返回，但输出不是可用译字"的典型形态，且**没有任何异常或非零退出码**提示。
6. **平台分级（AC3 要求区分部分可行组合）**：`windows` = **PASS**；`offscreen` = **PARTIAL**，且可经 `addApplicationFont` **补救为真实字形**；`minimal` = **PARTIAL 且不可补救**（字体注入完全无效）。
7. **任务禁止范围获得实测支持**：三平台结果**确实不同**（windows 真实字形 vs offscreen/minimal tofu），且 minimal 连补救都无效——把 offscreen 的成功推广为 windows/minimal 的成功会在本数据下直接产生错误结论。

## 2. 环境与隔离（AC1）

### 2.1 生产版本口径的来源（只读引用）

| 生产事实 | 值 | 证据 |
|---|---|---|
| 依赖清单声明的 Qt 栈 | `PySide6_Essentials==6.11.2`、`shiboken6==6.11.2` | `requirements.txt`（`01-environment.log:13-15`） |
| 生产 Python 口径 | Windows / Python 3.12（测试夹具与打包注释均以 3.12 为准） | `tests/rendering/conftest.py:3-6`、`tests/core/test_bootstrap.py:3-5`、`requirements.txt` torch 段注释 |
| 生产平台边界 | `windows`（QPA 默认） | `tests/rendering/conftest.py`、`tests/ui_shell/conftest.py`、`tests/workbench/conftest.py`、`src/infrastructure/rendering/font_catalog.py:15` |
| QPA 插件随包发布情况 | `qdirect2d.dll, qminimal.dll, qoffscreen.dll, qwindows.dll` | `01-environment.log:45` |

### 2.2 本次实验环境

| 项 | 值 |
|---|---|
| 解释器 | `C:\Users\49745\AppData\Local\Temp\M2-R1-venv\Scripts\python.exe` |
| Python | `3.12.3 (tags/v3.12.3:f6650f9, Apr 9 2024) [MSC v.1938 64 bit (AMD64)]` |
| PySide6 / shiboken6 | `6.11.2` / `6.11.2`（`cp310-abi3-win_amd64` wheel） |
| Qt runtime | `qVersion()=6.11.2`、`QLibraryInfo.version()=6.11.2` |
| OS | Microsoft Windows 11 专业版，`10.0.26200`，64 位 |
| 屏幕（windows 平台） | 2 个（主屏 `0,0,2560x1440`） |

### 2.3 隔离方式（未触碰生产）

- venv 建立在 `%TEMP%\M2-R1-venv`，由**独立 CPython 3.12.3** 创建；与生产解释器（`C:\Python314`，3.14.6，未安装 PySide6）完全分离。
- 生产仓库文件零改动：未改 `requirements*.txt`、未向任何生产 site-packages 安装、未生成 lock 文件。
- 探针不导入 `bootstrap.app`，不打开任何 SQLite 文件，不读写真实用户数据根；仅在本 Task 授权路径内写证据与临时 PNG。
- 运行后实测：`src/**`、`tests/**` 内 `__pycache__` 计数 **0**；`git status --porcelain` 仅 `?? verification/M2-R1/`（AC5 证据见 `08-delivery-scope-and-diff-check.log`）。

### 2.4 环境裁定

被测 Qt/PySide6/Python 版本与 `requirements.txt` 及测试夹具的 Windows/Python 3.12 口径**一致**，QPA 三插件均为真实随包版本，因此本 Task 结论**不记 `BLOCKED`**。

仍未覆盖的环境面（见 §6）：真实生产入口 `main()` 的 QML 装配、安装态打包（PyInstaller）、多显示器/高 DPI 交互、非本机 Windows 版本。它们不推翻本文结论，但限制其外推范围。

## 3. 平台实测矩阵（AC2 / AC3）

### 3.1 主矩阵（3 平台 × 3 次独立进程）

每个平台 3 次运行的**全部数值与 hash 完全一致**，下表为逐平台稳态值（原始 JSON 见 `verification/M2-R1/raw/<platform>/run{1,2,3}/probe.json`）。

| 观测项 | `windows` | `offscreen` | `minimal` |
|---|---|---|---|
| `QT_QPA_PLATFORM` | windows | offscreen | minimal |
| `QGuiApplication` 装配 | OK | OK | OK |
| `platformName()` | `windows` | `offscreen` | `minimal` |
| `screens()` 数量 / 几何 | 2 / `0,0,2560x1440` 等 | 1 / `0,0,800x800`（虚拟） | 1 / `0,0,240x320`（虚拟） |
| `QFontDatabase.families()` 数量 | **221** | **0** | **0** |
| `hasFamily("Microsoft YaHei")` | True | **False** | **False** |
| `hasFamily("Arial")` | True | False | False |
| `QFont().family()`（Qt 默认） | `Microsoft YaHei UI` | `Sans Serif` | `Helvetica` |
| `QFontMetrics(32px).height()` | **42** | **32** | **32** |
| `ascent` / `descent` | 34 / 8 | **32 / 0** | **32 / 0** |
| `horizontalAdvance("漫画排版")` | 128 | 128 | 128 |
| `horizontalAdvance("Manga")` | 107 | **160** | **160** |
| `inFont("漫")` | True | **False** | **False** |
| `QtFontCatalog.resolve("Source Han Sans K Bold")` | `Microsoft YaHei`（`available=False`，命中回退链） | `Sans Serif`（回退链全不命中 → `QFont()` 兜底） | `Helvetica`（同上） |
| 横向 layout：items / 宽度 / `fits` | 1 / 340 / True | 1 / 416 / True | 1 / 416 / True |
| 横向 layout：`font_available` | False | False | False |
| 竖向 layout：items / 宽度 / 高度 | 6 / 56 / 148 | 6 / 56 / 140 | 6 / 56 / 140 |
| `compose_page` 输出字节数 / sha256(前16) | 2689 / `a7768dd3e9980211` | 1095 / `656d0ac6e5aa7d28` | 1095 / `656d0ac6e5aa7d28` |
| `compose_page` 与输入不同像素 / 总像素 | 3601 / 120000 | 13583 / 120000 | 13583 / 120000 |
| `compose_region` 与输入不同像素 | 2762 | 10933 | 10933 |
| 同进程重复合成 sha256 相同 | True | True | True |
| 跨 3 次进程输出 sha256 相同 | True | True | True |
| 顶层 HWND 总数 / 可见数 | 3 / **0** | **0 / 0** | **0 / 0** |
| 探针退出码（run1/2/3） | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |

要点：

- **offscreen 与 minimal 的输出 PNG sha256 完全相同**（`656d0ac6…`）：两者的替代字形光栅化结果一致，**minimal 并不比 offscreen 提供更多字体能力**。
- 输出 sha 与 windows 不同是**预期且必要**的差异来源（字体不同 → 字形不同），这正是"不得把 offscreen 结果当作 windows 结果"的实测依据。
- `QtFontCatalog` 在三种平台都**不抛异常**：无字体时返回 `available=False` + 兜底 family。`LayoutResult.font_available=False` 是下游唯一可观测的告警信号，但它**不阻止** `QtImageCompositor` 继续出图。

### 3.2 视觉证据（原始 PNG 已入库）

| 平台 | 文件 | 观察 |
|---|---|---|
| windows | [`raw/windows/run1/output_page.png`](../../verification/M2-R1/raw/windows/run1/output_page.png) | 真实字形：`漫画排版テスト Manga` + 右起竖排 `縦書きテスト` |
| offscreen | [`raw/offscreen/run1/output_page.png`](../../verification/M2-R1/raw/offscreen/run1/output_page.png) | **实心方块（tofu）**，每个字符一个 em 方块；排版几何仍然正确（竖排位置/列序正确） |
| minimal | [`raw/minimal/run1/output_page.png`](../../verification/M2-R1/raw/minimal/run1/output_page.png) | 与 offscreen 逐字节相同（sha256 一致） |
| offscreen + `addApplicationFont` | [`raw/supp-offscreen-appfont/output_page_offscreen_appfont.png`](../../verification/M2-R1/raw/supp-offscreen-appfont/output_page_offscreen_appfont.png) | 恢复为真实字形 |
| offscreen + `QT_QPA_FONTDIR` | [`raw/supp-offscreen-fontdir/output_page_offscreen_fontdir.png`](../../verification/M2-R1/raw/supp-offscreen-fontdir/output_page_offscreen_fontdir.png) | 恢复为真实字形 |

结论：offscreen/minimal 的"能出图"**不等于**"能出正确文本"；方块的 advance 恰为 1 em（英文 5 字符 = 160 px = 5 × 32），与"缺字形即按像素尺寸占位"一致。

### 3.3 无可见 GUI 证据（AC2）

| 平台 | 事件循环 `exec()` 返回 | `timer_fired` | 墙钟 | 循环后顶层 HWND(可见) |
|---|---|---|---|---|
| windows | 0 | True | 0.307 s | 3 (0) |
| offscreen | 0 | True | 0.309 s | 0 (0) |
| minimal | 0 | True | 0.316 s | 0 (0) |

windows 平台那 3 个 HWND 经类名/标题/可见性核查（`06-eventloop-and-window-census.log`）：

```text
hwnd=0x810be6  class='Qt6112ThemeChangeObserverWindow'  title=''            visible=False
hwnd=0x4a0bb0  class='Qt6112ScreenChangeObserverWindow' title=''            visible=False
hwnd=0x11609e8 class='IME'                              title='Default IME' visible=False
```

全部为 Qt 内部通知窗口与 IME 消息窗口，**没有任何可见窗口**；offscreen/minimal 甚至不创建任何 HWND。因此"无可见 GUI 时运行 Qt 渲染栈"在本环境下成立（探针自身也从不创建或 `show()` 任何 `QWindow`）。

### 3.4 稳定性与退出码（AC3）

- **3 平台 × 3 次独立进程 = 9 次运行，`EXITCODE=0`，`errors=0`**（`02/03/04-probe-*.log` 每次运行的 `--- EXITCODE=0 ---` 段）。
- **逐字节确定性**：同平台 3 次进程的输出 PNG sha256 完全相同；同进程内重复 `compose_page` 亦相同。
- 事件循环 6 次运行（3 平台 × 2）全部按时退出（0.31 s 量级，预算 5 s），无挂起、无崩溃。
- **未观察到任何失败类型**：无 `ModuleNotFoundError`（对比 M2-D1 的无 PySide6 环境）、无 `QPA plugin could not be loaded`、无 `QFontEngine` 致命错误、无 Python 异常回溯。**这正是风险所在**：offscreen/minimal 的字体缺失是**静默的**，不表现为失败。

### 3.5 字体补救边界（补充探测，非主矩阵）

补充探针 [`probes/qt_font_remediation_probe.py`](../../verification/M2-R1/probes/qt_font_remediation_probe.py) 只有一个横向 op，故其 `differing_pixels` 与主矩阵（两个 op）不可横向比较；其余列可比。

| 条件 | `families()` | `hasFamily(YaHei)` | 解析 family | `fm.height` | `inFont("漫")` | 页 diff | 裁定 |
|---|---|---|---|---|---|---|---|
| offscreen 基线（对照） | 0 | False | `Sans Serif` | 32 | False | 10933 | tofu |
| offscreen + `QT_QPA_FONTDIR=C:\Windows\Fonts` | **68** | False | `Arial` | 36 | **True** | 2177 | **真实字形**（TTF 被收录；`msyh.ttc` 未进列表，故 YaHei 仍不可见） |
| offscreen + `addApplicationFont(C:\Windows\Fonts\msyh.ttc)` | **2** | **True** | `Microsoft YaHei` | **42** | **True** | 2735 | **真实字形，度量与 windows 完全一致** |
| minimal + `QT_QPA_FONTDIR=C:\Windows\Fonts` | 0 | False | `Helvetica` | 32 | False | 10933 | **无效**（无变化） |
| minimal + `addApplicationFont(msyh.ttc)` | 0（**返回 id=-1**） | False | `Helvetica` | 32 | False | 10933 | **无效**（平台不支持应用字体） |

事实层结论：

- **offscreen 的字体缺失是可补救的**（至少两种机制），且 `addApplicationFont` 补救后 `fm.height=42`、`advLatin=107` 与 windows 平台**数值一致**。
- **minimal 的字体缺失不可补救**：`addApplicationFont` 返回 `-1`，`QT_QPA_FONTDIR` 亦不生效；其 `QPlatformFontDatabase` 基础实现不提供字体引擎。
- 因此三平台**不是同一条可行性曲线**：`windows` ⊃ `offscreen(+显式字体)` ⊃ `offscreen 默认` ⊃ `minimal`。
- 本项**仅为可行性边界测量，不构成任何字体来源/打包方案选择**（AD-001 §34；M2D1-13/14 的技术选型仍待 Codex/用户裁决）。

## 4. M2D1-22 收敛（AC4）

### 4.1 逐条对照仓库原有陈述

| 仓库陈述（M2-D1 §3 M2D1-22 引用） | 本 Task 实测裁定 |
|---|---|
| `tests/rendering/conftest.py:3-6`「offscreen 平台不带字体」（`ships no fonts at all`） | **成立**：`families()==0`、`inFont("漫")==False`、输出为 tofu |
| `tests/ui_shell/conftest.py:3-5`「offscreen 无字体数据库，QML Controls 文本布局会 misbehave」 | 部分成立并可量化：字体库确为空（已实测）；**QML Controls 侧本次未测**（见 §6 保留项） |
| `tests/workbench/conftest.py:3-6` 同上 | 同上一行 |
| `tests/core/test_shutdown_drain.py:40-41`「默认 Windows 平台带字体数据库，offscreen 不带」 | **两侧都成立**：windows 221 families / offscreen 0 |
| `tests/core/test_bootstrap.py:3-5`「入口证据禁止强制 `QT_QPA_PLATFORM=offscreen`」 | **策略获得支持**：本 Task 的 `main()`/QML 未测，但 AppShell 所依赖的文本渲染在 offscreen 下默认输出非产品字形（tofu），故强制 offscreen 会改变被验证对象的语义 |

### 4.2 收敛结论

**M2D1-22 从 `UNVERIFIED` 收敛为「已实测的平台约束 + 一个更窄的保留项」**：

1. **已证实（不再 `UNVERIFIED`）**：`windows`/`offscreen`/`minimal` 三平台下 `QGuiApplication` + `QFontDatabase` + 生产 `QtTextLayoutEngine` + 生产 `QtImageCompositor` 均可装配执行、无可见窗口、可重复、可确定性退出（`EXITCODE=0`）。
2. **已证实（原陈述）**：`offscreen`/`minimal` 默认**无字体数据库**；文本渲染产出为替代方块，度量退化；该退化**不产生任何错误信号**（仅 `available=False`/`font_available=False`）。
3. **已证实（平台差异）**：`minimal` 在字体注入下**不可补救**，`offscreen` 可补救；二者默认输出逐字节相同。
4. **保留 `UNVERIFIED`（明确 blocker）**：**QML/QQuickWindow 装配在 offscreen/minimal 下的行为未测**。理由：本 Task 授权范围与实验目标限定为四项 Qt 组件的运行时行为；QML 装配属于生产入口路径（`bootstrap/app.py`），需在后续独立切片中以只读探针验证。**不得由本报告推断 QML 可用或不可用。**
5. **对 M2-D1 矩阵的建议（交 Codex，不自行改矩阵）**：M2D1-22 不应作为独立迁移切片留在 `UNVERIFIED`，建议改标为**已实测平台约束**，并作为 M2D1-13（`QtFontCatalog` REPLACE 候选）与 M2D1-14（`QtTextLayoutEngine` REPLACE 候选）的**输入证据与硬约束**（"字体来源必须显式、可注入、可诊断"）。

## 5. 对后续 Core / Qt adapter 边界的建议（AC4；**建议而非实现批准**）

以下均为研究结论派生的**建议**，不释放任何实现，也不选定技术：

1. **不要把 `offscreen`/`minimal` 当作文本渲染的验收平台**：在默认字体状态下，它们的"成功"输出是 tofu。若在 CI 或 headless 验收里用 offscreen，**必须**显式注入字体，并且**必须**校验字形真实性（例如 `QFontDatabase.hasFamily` / `QFontMetrics.inFont` 前置断言），否则会把"渲染成功但内容错误"记为 PASS。
2. **渲染端口实现必须自带字体来源，不能依赖 QPA 平台**：M2D1-13/14 的替代实现若沿用 `QFont().family()` 兜底，将在无头环境静默产生 tofu；建议把"平台无字体库"建模为**显式可诊断状态**（现有 `ResolvedFont.available` / `LayoutResult.font_available` 是正确方向的起点，但当前**不足以阻断**合成）。
3. **字形真实性需要独立校验手段**：本 Task 的 `differing_pixels`/`inFont()` 组合可作为基线做法；"退出码 0 + PNG 非空"**不能**作为文本渲染正确性的证据（本 Task 已用实测反例证明）。
4. **平台能力分级应写进未来的验收契约**：`windows` ⊃ `offscreen(+显式字体)` ⊃ `offscreen 默认` ⊃ `minimal`。任何"headless 运行"声明都必须附平台与字体条件，不得跨级外推。
5. **非文本的 headless 路径不受本结论影响**：SQLite、导入链、`imaging/streaming_png.py`、`webtoon_tiles.py` 等零 Qt 通路（M2D1-08/24）在本环境下与其无头可行性无关，仍可独立推进。
6. **`minimal` 不应被用作任何文本相关退路**：其应用字体注入返回 `-1`，是本环境下唯一"连补救都不成立"的平台。

## 6. 未验证与限制（照实记录）

- **QML / QQuickWindow / AppShell 在 offscreen/minimal 下的行为：`UNVERIFIED`**（本 Task 未测；见 §4.2 第 4 条）。
- **生产入口 `main()` 的三个模式**（正常启动、`--smoke-test`、`--screenshot`）在真实 Qt 环境下**未执行**；`bootstrap/app.py:1147-1148` 的 `grabWindow` 路径未验证。
- **真实文档渲染链未端到端执行**：本 Task 只驱动 `QtFontCatalog` + `QtTextLayoutEngine` + `QtImageCompositor` 三个适配器，未经过 `PipelineService`/provider/数据库（那属于生产数据路径，本 Task 禁触）。
- **字体覆盖仅按 fallback 链抽样**（`Source Han Sans K Bold`、`Microsoft YaHei`、`Arial`）；未穷举 221 个 family 的可用性或 CJK 覆盖差异。
- **DPI / 多显示器 / 缩放**只记录了屏幕几何（windows 2 屏），未测 `QT_SCALE_FACTOR`、per-monitor DPI 与高 DPI 光栅化一致性。
- **长期运行/内存**未测：事件循环仅 300 ms 量级；无 soak test。
- **`QImage` PNG 编解码**在 offscreen/minimal 下可用（本 Task 已实际解码/编码 120000 像素图并读回比较），但**其他 imageformats 插件（JPEG/WebP/TIFF 等）未测**。
- **字体补救结论受 Qt 6.11.2 实现约束**：`minimal` 的 `addApplicationFont` 返回 `-1` 是本版本实测事实，不保证跨 Qt 版本不变。
- **产品测试套件 `NOT_RUN`**：`src/**` 零修改，且实验环境只装了 Qt 栈（未装 `pytest`/`torch` 等），故未运行生产测试；按本 Task Gate **不得记为 PASS**。
- 本 Task **不改变** T3.2.1 Gate（`OPEN`/AC3 `BLOCKED`）与任何 M2 实现授权状态。

## 7. 证据索引

| 文件 | 内容 |
|---|---|
| `01-environment.log` | 固定点（worktree/branch/HEAD/common dir/干净状态）、生产依赖口径、OS、隔离 venv、PySide6/Qt 版本、QPA 插件清单 |
| `02-probe-windows.log` | windows 平台 3 次独立进程的完整原始 stdout+stderr 与退出码 |
| `03-probe-offscreen.log` | offscreen 同上 |
| `04-probe-minimal.log` | minimal 同上 |
| `05-supplementary-font-remediation.log` | 字体补救 5 个条件（offscreen/minimal × baseline/fontdir/appfont） |
| `06-eventloop-and-window-census.log` | 事件循环 3 平台 × 2 次 + 完整 HWND 普查 |
| `07-evidence-manifest.md` | 证据清单、覆盖表与 AC 对照 |
| `08-delivery-scope-and-diff-check.log` | 交付范围断言、`git diff --check`、`src/**`/`tests/**`/依赖零修改证明 |
| `probes/qt_platform_probe.py` | 主矩阵探针（生产适配器只读驱动 + 像素/hash/窗口度量） |
| `probes/qt_font_remediation_probe.py` | 字体补救边界探针 |
| `probes/qt_eventloop_probe.py` | 事件循环稳定性 + HWND 普查探针 |
| `raw/<platform>/run{1,2,3}/probe.json` | 每次运行的原始结构化结果（含全部数值、hash、错误列表） |
| `raw/<platform>/run{1,2,3}/*.png` | 输入基准图与合成输出图（视觉证据） |
| `raw/supp-*/probe.json`、`raw/loop-*/probe.json` | 补充探测原始结果 |
| `raw/smoke/` | 探针首次冒烟运行（**非矩阵证据**，仅证明探针可用） |

## 8. 复现方式

```powershell
Set-Location 'G:\CODEX\New Manga.worktrees\M2-R1-deepseek'

# 1) 隔离环境（不触碰生产解释器与 requirements）
$venv = Join-Path $env:TEMP 'M2-R1-venv'
& 'C:\Users\49745\AppData\Local\Programs\Python\Python312\python.exe' -m venv $venv
& "$venv\Scripts\python.exe" -m pip install 'PySide6_Essentials==6.11.2' 'shiboken6==6.11.2'

# 2) 平台矩阵（每平台 3 次独立进程）
$env:PYTHONDONTWRITEBYTECODE = '1'
foreach ($p in 'windows','offscreen','minimal') {
  foreach ($r in 1..3) {
    $raw = "verification\M2-R1\raw\$p\run$r"; New-Item -ItemType Directory -Force $raw | Out-Null
    & "$venv\Scripts\python.exe" -B verification\M2-R1\probes\qt_platform_probe.py `
        --platform $p --json "$raw\probe.json" --workdir $raw
    "EXIT=$LASTEXITCODE"
  }
}

# 3) 字体补救边界
& "$venv\Scripts\python.exe" -B verification\M2-R1\probes\qt_font_remediation_probe.py `
    --platform offscreen --mode appfont --json "$env:TEMP\p.json" --workdir "$env:TEMP"
& "$venv\Scripts\python.exe" -B verification\M2-R1\probes\qt_font_remediation_probe.py `
    --platform minimal --mode appfont --json "$env:TEMP\p2.json" --workdir "$env:TEMP"

# 4) 事件循环与窗口普查
& "$venv\Scripts\python.exe" -B verification\M2-R1\probes\qt_eventloop_probe.py `
    --platform windows --json "$env:TEMP\loop.json"
```

期望：步骤 2 的 9 次运行 `EXIT=0`；`windows` families=221、offscreen/minimal families=0；`windows` 可见窗口 0；offscreen/minimal 顶层 HWND 0。
