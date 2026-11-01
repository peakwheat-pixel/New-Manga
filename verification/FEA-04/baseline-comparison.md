# FEA-04 AC2 基线对照（DSH 实测，2026-11-02）

## 基线 commit 68c72ba57（范围冻结 v3，实现前）
命令：`dotnet build apps/desktop-avalonia/NewManga.sln` + `dotnet test apps/desktop-avalonia/NewManga.sln --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings`
结果：**EXIT=0（全绿）**

| 工程 | passed | failed | skipped | total |
|---|---|---|---|---|
| NewManga.Host.Tests | 51 | 0 | 28 | 79 |
| NewManga.ThemeEngine.Tests | 235 | 0 | 0 | 235 |
| NewManga.DesignSystem.Tests | 85 | 0 | 0 | 85 |
| NewManga.CoreClient.Tests | 116 | 0 | 25 | 141 |
| NewManga.ApplicationCore.Tests | 31 | 0 | 0 | 31 |
| NewManga.App.Tests | 396 | 0 | 7 | 403 |
| **合计** | **914** | **0** | **60** | **974** |

## 实现 head eat/fea-04（Codex + DSH 返修）
同命令：**EXIT=0（全绿）**

| 工程 | passed | failed | skipped | total |
|---|---|---|---|---|
| NewManga.Host.Tests | 51 | 0 | 28 | 79 |
| NewManga.ThemeEngine.Tests | 235 | 0 | 0 | 235 |
| NewManga.DesignSystem.Tests | 85 | 0 | 0 | 85 |
| NewManga.CoreClient.Tests | 116 | 0 | 25 | 141 |
| NewManga.ApplicationCore.Tests | 31 | 0 | 0 | 31 |
| NewManga.App.Tests | 412 | 0 | 7 | 419 |
| **合计** | **930** | **0** | **60** | **990** |

## 判定（AC2）
- 既有工程 passed 全部 ≥ 基线；failed 均为 0；skipped 不变。
- App.Tests 419 = 基线 403 + 新增 FEA04CurrentAdapterTests 17 项（16 计划 + 1 个 IMPL-02 回归测试），新增项全通过。
- **无既有测试被删除或弱化**（新增测试仅追加）。
