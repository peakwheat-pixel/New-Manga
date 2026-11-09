# FEA-15-PREREQ-2 证据索引：集成验收基线核对

- Task：`FEA-15-PREREQ-2`（FEA-15 集成验收前置：全量基线核对）
- Base：`25c0a1ecc`；日期：2026-11-09；本卡**零代码改动**（仅测试/证据/STATUS）

## 全量基线（当前 head）

### pytest（`python -m pytest -q`，299.94s，EXIT 0）

| 项 | 值 |
|---|---|
| collected | **3456** |
| passed | **3446** |
| failed | **0** |
| skipped | **10** |
| 日志 | `logs/pytest-full.log`（第 102 行汇总） |

### .NET（8 个项目，逐项目 `dotnet test --no-build`，全部 EXIT 0）

| 项目 | passed | failed | skipped |
|---|---|---|---|
| NewManga.App.Tests | 838 | 0 | 11 |
| NewManga.Appearance.Tests | 21 | 0 | 0 |
| NewManga.ApplicationCore.Tests | 31 | 0 | 0 |
| NewManga.CoreClient.Tests | 167 | 0 | 24 |
| NewManga.DesignSystem.Tests | 117 | 0 | 0 |
| NewManga.Host.Tests | 305 | 0 | 72 |
| NewManga.Presentation.Avalonia.Tests | 72 | 0 | 0 |
| NewManga.ThemeEngine.Tests | 253 | 0 | 0 |
| **合计** | **1804** | **0** | **107** |

日志：`logs/dotnet-<项目>.log`（各含命令头/EXIT）。

## 与 STATUS 旧基线对比

| 项 | 旧记录 | 本次实测 | 差异 |
|---|---|---|---|
| pytest | 3395 通过 / 10 跳过 | **3446 / 10** | +51 通过，0 失败 |
| .NET | 1794 / 0 / 107 | **1804 / 0 / 107** | +10 通过，0 失败 |

**结论：全绿基线，无新增失败。** 两个具体失败（App.Tests 的 V2Conformance / FluentPage）已在 `FEA-15-PREREQ-1` 修复；pytest 的 10 个 skipped 为既有 skip（非未登记 flake）。

## 说明

- pytest 日志尾部有 legacy QML（`src/ui/qml`）的 `TypeError` 运行时告警（stderr），属已退役 UI 时代既有输出，不影响退出码（EXIT 0）。
- 本卡不修任何代码；若后续出现失败，另立修复卡。
- STATUS 的「测试基线」行已按本卡实测更新。
