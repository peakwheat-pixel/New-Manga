# FEA-15-PREREQ-1 证据索引

- Task：`FEA-15-PREREQ-1`（修复既有 2 个 App.Tests 失败；FEA-15 集成验收前置）
- Base：`417d9c442`；日期：2026-11-09；证据批次：`fea-15-prereq-1`（日志头 batch 与之一致）

## 修复口径

| 测试 | 修复 |
|---|---|
| `V2ConformanceTests.AppCSharp_OutsideShellLayout_HasNoRawDesignValues` | `ImmersiveReaderWindow.cs` 的 `Background = Brushes.Black;` → `this[!BackgroundProperty] = new DynamicResourceExtension("Nm.Color.Bg.Canvas");`（设计系统 token，视觉不变） |
| `FluentPageTests.FluentShell_BreakpointsA11yShortcutsAndReducedMotion_AreExplicit` | 过期期望 17 → 权威值 **18**；并新增 gesture 去重断言（`SelectMany(Gestures).Distinct()`） |

两者均为既有回归（非 FEA-13 引入），是 FEA-15「全量 .NET 绿」的硬前置。

## 判别证据

| AC | 结果 | 证据 |
|---|---|---|
| AC1 V2Conformance | 通过（无 literal brush/colour） | `logs/dotnet-test-two.log`（2 passed） |
| AC2 FluentPage | 通过（18 + 去重断言） | 同上 |
| AC3 构建与全量 | `dotnet build` 0/0；App.Tests 全量 **838 passed / 0 failed / 11 skipped** | `logs/dotnet-build.log`、`logs/dotnet-test-app-full.log` |
| AC4 门禁 | `check.ps1` 默认 + `-TaskPath` PASS；pins 18/18 | 卡/Handoff |
| 变异判别 | ①恢复 literal brush（`Background = Brushes.Green;`）→ V2Conformance **1 failed**；②断言改回 17 → FluentPage **1 failed**；复原 + `-t:Rebuild` 后复绿 | `logs/mutation-literal-brush.log`、`logs/mutation-stale-count.log` |

## 命令

```powershell
dotnet build apps/desktop-avalonia/NewManga.sln -c Debug --nologo
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --no-build --nologo
```

## 说明

- 阅读器视觉不变：`Nm.Color.Bg.Canvas` 即全屏阅读器的画布底色。
- 若未来再增/删快捷键，`FluentPageTests` 的 18 需显式更新（已在测试注释标明）。
- 未跑全量 .NET 解决方案（Host.Tests 等），本次只涉及 App.Tests 两个测试；build 覆盖全 solution。
