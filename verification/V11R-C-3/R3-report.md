
# V11R-C-3 R3 — 生产文件迁移完成（旧主题依赖清零）

- 执行时间：2026-10-30T03:32:01+08:00
- R1 tag：`v11r-pre-retire` = df883f2ce（基线）
- 迁移文件（10）：Pages.cs、MainWindow.axaml.cs、ReaderWorkbenchPages.cs、ProfileSections.cs、
  ImportExportPanels.cs、CredentialSection.cs、ProviderBindingsSection.cs、MainViewModels.cs、
  App.axaml.cs、AppOptions.cs。

## 做法（legacy 降级为可启动）

- 新增 `apps/desktop-avalonia/src/NewManga.App/Views/Legacy/LegacyChrome.cs`：App-local 兼容词汇
  （`LegacyLayoutProfile/LegacyLayoutProfiles/LegacyChrome.Brush` 等），只解析 DS `Nm.*` 令牌 + 中性 fallback；
  **不读取、不重实现 NewManga.Theme**。新壳/Theme Studio 不引用该命名空间。
- 旧壳固定 Sonoma 布局：`ThemePack` 布局包切换、主题中心列表、macOS chrome 逻辑全部退役；
  设置页只保留“外观（浅/暗）”切换并显示“主题已退役，请使用 Theme Studio”；`--shell=legacy` 仍可启动。
- `--theme` 兼容：AppOptions 保留参数；App 启动时经 `LegacyThemeMigration` 映射到 `newmanga-default`
  （Trace 记录），不再调用旧 ThemePackService。
- 旧主题 UI 的 `Brush("token")` 改为 `LegacyChrome.Brush`，由 DS 设计令牌解析。

## 验证

- 依赖图（R3 重跑）：**legacy-shell-production = 0 文件 / 0 引用**；DELETE-WITH-C3 83（旧项目源）、
  REPLACE-BEFORE-DELETE 218（旧测试，R4 删除）、EVIDENCE 87、new-architecture/假阳性照旧。
- `dotnet build src/NewManga.App/NewManga.App.csproj -warnaserror`：通过（0W/0E）；随后 R4 删除旧测试后全量 build/test 绿（见 R4 日志）。
- 未改动 ThemeEngine/DesignSystem 语义。
