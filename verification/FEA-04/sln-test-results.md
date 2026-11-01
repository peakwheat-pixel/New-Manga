# FEA-04 sln 测试结果（DSH 返修 r2 后，2026-11-02）

命令：`dotnet test apps/desktop-avalonia/NewManga.sln --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings`
环境：DSH（Windows，.NET SDK 10.0.401，目标 net9.0）

结果：**EXIT=0，931 passed / 0 failed / 60 skipped**（991 项）。

| 工程 | passed | failed | skipped | total |
|---|---|---|---|---|
| NewManga.Host.Tests | 51 | 0 | 28 | 79 |
| NewManga.ThemeEngine.Tests | 235 | 0 | 0 | 235 |
| NewManga.DesignSystem.Tests | 85 | 0 | 0 | 85 |
| NewManga.CoreClient.Tests | 116 | 0 | 25 | 141 |
| NewManga.ApplicationCore.Tests | 31 | 0 | 0 | 31 |
| NewManga.App.Tests | 413 | 0 | 7 | 420 |
| **合计** | **931** | **0** | **60** | **991** |

基线 68c72ba57 实测：914 passed / 0 failed / 60 skipped（App 396/403）。新增 FEA04CurrentAdapterTests 17 项。
`git diff --check 68c72ba57..HEAD` → **rc=0**。
