
# V11R-C-3 R4 — 替代断言补齐 + 5 个旧测试删除

- 执行时间：2026-10-30T03:32:12+08:00
- 前置：R3（bc3dc1a）已清零生产旧符号引用。
- 新增测试：`apps/desktop-avalonia/tests/NewManga.App.Tests/ThemeRetirementR4Tests.cs`（5 例，覆盖
  DELETION_BATCHES §2 的 5 条“需新增”硬门）：
  1. `No_font_binaries_ship_with_the_application` — 二进制字体审计；
  2. `Window_chrome_is_visual_only_and_keeps_real_window_behaviour` — chrome 不改窗口行为（decorations/CanResize/关闭）；
  3. `Window_material_falls_back_to_opaque_on_unsupported_os` — Win11 Mica / Win10 与旧系统 opaque fallback；
  4. `Startup_does_not_block_first_frame` — 启动门未放行时窗口仍可见、内容已挂载；
  5. `Legacy_settings_page_retires_theme_center_and_points_to_theme_studio` — 旧设置页不再渲染 ThemePack 列表，
     只保留外观切换并指向 Theme Studio。
- 旧测试删除（5 文件，218 引用）：`ThemeMacosTests.cs`、`ThemeLayoutsTests.cs`、`ThemeMacosAuditTests.cs`、
  `S3ShellTests.cs`、`S4ReaderWorkbenchTests.cs`；`S3ShellTests` 内的共享 `Evidence` helper 原样
  保留为 `Evidence.cs`（其它保留测试仍使用）。
- 结果：`dotnet build NewManga.sln -warnaserror` 0W/0E；`dotnet test NewManga.sln` 0 失败：
  App 271(+7 skip)、ThemeEngine 229、DS 82、Host 49(+28 skip)、CoreClient 116(+25 skip)；新 5 例全绿。
- 日志：`R4-test.log`（全量）、`R4-replacement-tests.log`（5 例专项）。
