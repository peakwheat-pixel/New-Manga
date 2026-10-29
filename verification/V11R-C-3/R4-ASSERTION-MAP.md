# C-3-I1：R4 替代断言覆盖映射

C-3 R4 删除 5 个旧测试文件后新增了 5 条断言，但 r1 复审指出它们都构造旧 `MainWindow`，无法覆盖
新壳（`--shell=v2` 默认路径）。本文件给出“旧断言 → 新壳对应断言”的映射与残余 legacy-only 行为。

| 旧测试（删除） | R4 断言（legacy） | 新壳等价断言（v2） |
|---|---|---|
| `ThemeMacosAuditTests`：字体二进制审计 | `ThemeRetirementR4Tests.No_font_binaries_ship_with_the_application` | 与 shell 无关：扫描仓库 tracked 字体（C-3-I1 已修正 `training_data/` 假阳性） |
| `ThemeMacosTests`：窗口 chrome 只做视觉、不改窗口行为 | `Window_chrome_is_visual_only_and_keeps_real_window_behaviour` | v2 根窗口不设置任何 `SystemDecorations`/`CanResize` 覆盖；`AppShellV2.CreateRoot` 只设置背景与材质提示 |
| `ThemeMacosAuditTests`：材质 fallback | `Window_material_falls_back_to_opaque_on_unsupported_os` | `ThemeRetirementR4Tests.V2_shell_window_material_uses_the_same_os_fallback_policy`（`AppShellV2.CreateRoot` 已应用同一策略） |
| `S3ShellTests`：首帧非阻塞 | `Startup_does_not_block_first_frame` | `ThemeRetirementR4Tests.V2_shell_starts_with_first_frame_and_shares_the_design_system_manager`（`StartGate` 未放行时窗口可见、内容已挂载） |
| `S4ReaderWorkbenchTests` / `S3ShellTests`：外观/主题中心 | `Legacy_settings_page_retires_theme_center_and_points_to_theme_studio`；`LegacyAppearanceSyncTests` | `V2_shell_*` 外观断言（共享 manager、`Nm.Color.Bg.App` 切换）；v2 的主题入口是 Theme Studio：`V2ThemeStudioTests` 与 `verification/V11R-C-2` 证据 |

## legacy-only 行为说明

- 旧设置页的“主题中心（已退役）→ Theme Studio”提示、固定 Sonoma 布局、`LegacyChrome` 兼容词汇只存在于
  `--shell=legacy` 路径；该壳按 C-3 裁决保留一个版本周期后删除，因此只为它保留最小冒烟断言，不再扩展视觉语义。
- v2 壳的主题/外观/材质/首帧行为由上述 v2 断言覆盖；Theme Studio 的完整交互见 C-2 任务证据。
