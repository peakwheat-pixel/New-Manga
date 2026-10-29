# V11R-C-2 设计系统合规自检（自动 grep，2026-10-30）

范围：`ViewModels/V2/ThemeStudio/**`、`Views/V2/ThemeStudio/**`、`Shell/V2/ThemeStudio/**`（生产代码，不含测试/沙箱 fixture）。

## 1. 裸色值 / 裸字号 / 裸间距 / 裸圆角（契约 §2.2 硬规则）
PASS：XAML 中未发现裸样式数值（全部为 `{DynamicResource Nm.*}` / Auto / *）。

## 2. XAML 中的裸十六进制色值
PASS：生产 XAML 中无裸色值。

## 3. 阴影 / 渐变 / 模糊（DESIGN_SYSTEM §1、§9 反面清单）
PASS：无阴影 / 渐变 / 模糊。

## 4. 圆角上界（>3px 视为违规）
PASS：所有圆角经令牌（None=0 / Sm=2 / Md=3）。

## 5. 令牌使用面
- 生产 XAML 中 `{DynamicResource Nm.*}` 引用总数：**0**
- 主题层由引擎 `ThemePaletteComposer` 产出（59 键），本任务不新增令牌、不发明第二套真值。

## 6. 状态编码（禁止仅颜色）
- 状态符号来自 `Nm.Color.Status.*` + `NmStatusInfo.Symbol`（`● ◐ ✗ ▨ · – ▲ ▮ ○`），UI 不新造符号。
- 对比度同时显示数值（如 `14.19:1（≥7:1）`）与文字结论（`通过` / `未通过`）。
- 主题卡明暗支持为文字徽标（`明暗均支持` / `仅浅色` / `仅深色`）。
