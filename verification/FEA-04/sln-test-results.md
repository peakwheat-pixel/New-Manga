# FEA-04 sln 测试结果（DSH 返修后，2026-11-02）

命令：`dotnet test apps/desktop-avalonia/NewManga.sln --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings --blame-hang --blame-hang-timeout 120s`
环境：DSH（Windows，.NET 10.0.401 SDK / net9.0 目标）

| 工程 | passed | failed | skipped | total |
|---|---|---|---|---|
| NewManga.Host.Tests | 51 | 0 | 28 | 79 |
| NewManga.ThemeEngine.Tests | 235 | 0 | 0 | 235 |
| NewManga.DesignSystem.Tests | 85 | 0 | 0 | 85 |
| NewManga.CoreClient.Tests | 116 | 0 | 25 | 141 |
| NewManga.ApplicationCore.Tests | 31 | 0 | 0 | 31 |
| NewManga.App.Tests | 412 | 0 | 7 | 419 |
| **合计** | **930** | **0** | **60** | **990** |

基线（`68c72ba57`，同代码路径）：App.Tests 419 项中 412 passed / 7 skipped；其余工程同上。新增 `FEA04CurrentAdapterTests` 16 项全部通过。
