# V11R-C-2 设计系统合规自检（自动 grep，2026-10-30，复审 r1 整改后）

范围与口径与 `V2ConformanceTests` 一致：
- XAML：`Views/V2/**` + `Shell/V2/**` 全部 `.axaml`（8 类正则）。
- C#：conformance 的 `OwnedCSharpDirectories`（**已包含 `ViewModels/V2/ThemeStudio`、`Views/V2/ThemeStudio`**，复审 C2-P2-1 整改）+ 7 类正则。
- 允许清单（单一令牌解析模块，理由与 ui-shell `ShellLayout` 相同）：`Shell/V2/ShellLayout.cs`、`ViewModels/V2/ThemeStudio/ThemeStudioMetrics.cs`。

## 1. XAML 裸样式数值

**PASS**：8 类正则在整个 V2 XAML 树（39 个文件）中 0 命中。

## 2. C# 裸设计值（ThemeStudio 已纳入扫描）

**PASS**：7 类正则覆盖 71 个 C# 文件（含 ThemeStudio 的 ViewModels/Views/Shell 三个目录）0 命中；允许的令牌解析模块仅 2 个。

## 3. ThemeStudio 几何来源（复审 C2-P2-1）

| 值 | 来源 |
|---|---|
| 卡片间距 | `ThemeStudioMetrics.CardGap` → `Nm.Space.4`（12） |
| 卡片默认宽度 | `ThemeStudioMetrics.CardWidthDefault` → `Nm.Size.InspectorExpanded`（320） |
| 断点 | `ThemeStudioMetrics.BreakpointFull/Compact` → `Nm.Size.Breakpoint.Full/Compact`（1600/1280） |
| 最小卡片宽度 | `ThemeStudioMetrics.CardMinWidth` = (Full − TreeWidth − InspectorExpanded − 2·S7 − 3·S4) / 4（≈249，纯令牌推导） |
| 列数 4/3/2 | THEME_STUDIO_SPEC §3.1 冻结的结构计数（非几何值） |

无新增数值例外；`DEVIATIONS.md` 的「例外申请」已同步为「无（C2-P2-1 通过令牌解析解决）」。

## 4. 圆角 / 阴影 / 渐变 / 状态编码
- 圆角：全部 `Nm.Corner.None/Sm/Md`（0/2/3px）；编辑器输入 0–3 校验，超界由 `ThemeValidator` 拒绝。
- 阴影/渐变/模糊：0 命中（见 §1 forbidden effect）。
- 状态非纯颜色：符号来自 `Nm.Color.Status.*` + `NmStatusInfo.Symbol`，并配文字（`通过`/`未通过`、`明暗均支持` 等）。

## 5. 回归门（复审整改后）
- `V2ConformanceTests`（XAML + C# 扫描，含 ThemeStudio）：6/6 通过。
- `V2ConformanceTests + V2StudioConformanceTests`：10/10 通过。
- 全量串行：`dotnet test NewManga.sln --no-build -m:1` → 0 失败（`test.log`，`TEST_EXIT=0`）。
