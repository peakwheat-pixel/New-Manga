
# V11R-C-3 R5 — 删除旧主题项目与工程引用

- 执行时间：2026-10-30T03:33:56+08:00
- 删除：`src/NewManga.Theme/`（`ThemePack.cs` + `NewManga.Theme.csproj`）。
- 工程：`NewManga.sln` 移除 NewManga.Theme 项目及配置；`src/NewManga.App/NewManga.App.csproj`
  移除 NewManga.Theme ProjectReference（保留 NewManga.ThemeEngine / NewManga.DesignSystem）。
- `--theme` 启动参数保留为兼容映射（AppOptions.StartupThemeId → LegacyThemeMigration → newmanga-default），
  不恢复旧 ThemePackService。
- 验证：`dotnet build NewManga.sln -warnaserror` 0W/0E；`dotnet test NewManga.sln` 0 失败
  （App 271+7skip、ThemeEngine 229、DS 82、Host 49+28skip、CoreClient 116+25skip）。
- 日志：`R5-build.log`、`R5-test.log`。
