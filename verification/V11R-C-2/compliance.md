# V11R-C-2 设计系统合规自检（自动 grep，2026-10-30）

范围：`Views/V2/**` + `Shell/V2/**` 全部 XAML（含本任务 `ThemeStudio` 三个目录；不含测试/沙箱 fixture）。
口径与 `V2ConformanceTests` 的 8 类正则一致。

## 1. 裸样式数值（契约 §2.2 硬规则）

**PASS**：8 类 conformance 正则在整个 V2 XAML 树（41 个文件）中 0 命中。

## 2. 圆角上界（>3px 视为违规）
PASS：样式全部经 `Nm.Corner.None/Sm/Md`（0/2/3px）；编辑器输入受 0–3 校验，超界由引擎 `ThemeValidator` 拒绝。

## 3. 阴影 / 渐变 / 模糊（DESIGN_SYSTEM §1、§9 反面清单）
PASS：无阴影 / 渐变 / 模糊 / backdrop（§1 forbidden effect 0 命中）。

## 4. 令牌使用面

- V2 XAML 中 `{DynamicResource Nm.*}` 引用总数：**856**
- 主题层由引擎 `ThemePaletteComposer` 产出（59 键）；本任务不新增令牌、不发明第二套真值。
- 未申请任何裸值例外（见 `DEVIATIONS.md`「例外申请：无」）。

## 5. 状态编码（禁止仅颜色）
- 状态符号来自 `Nm.Color.Status.*` + `NmStatusInfo.Symbol`（`● ◐ ✗ ▨ · – ▲ ▮ ○`），UI 不新造符号。
- 对比度同时显示数值（如 `14.19:1（≥7:1）`）与文字结论（`通过` / `未通过`）。
- 主题卡明暗支持为文字徽标（`明暗均支持` / `仅浅色` / `仅深色`）。

## 6. 回归门（合入 main 后）
- 静态合规测试：`dotnet test --filter "FullyQualifiedName~V2ConformanceTests|FullyQualifiedName~V2StudioConformanceTests"` → **10/10 通过**。
- 触发修正：`MyThemesSectionView.axaml` 的 `ListBox BorderThickness="0"` 字面量已删除（改用控件默认 0；截图复跑视觉无变化），记录见 `DEVIATIONS.md` CONFORMANCE-1。
- 全量串行测试：`dotnet test NewManga.sln --no-build -m:1` → 0 失败（`test.log`，`TEST_EXIT=0`）。
