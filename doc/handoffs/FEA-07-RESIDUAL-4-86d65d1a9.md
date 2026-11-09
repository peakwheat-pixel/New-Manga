---
task_id: FEA-07-RESIDUAL-4
author: DSH（Lead / Integrator）
recipient: 独立上下文 Reviewer
base_commit: 77a7459ab
delivery_head: 86d65d1a9
status: delivered
---

# Handoff：FEA-07-RESIDUAL-4（legacy MainWindow.Show 真实 AppData 零写入）

## 交付结果

L-R4b-1 / D-R4b-7 已修复：默认 `NewManga.App.Tests` 中 16 处 legacy `MainWindow.Show()`（6 文件）全部改为显式隔离 `--log-dir`，真实 `%APPDATA%` 零写入。实现提交 **`86d65d1a9`**（base `77a7459ab`；冻结提交 `5ca20036c`）。

| 变更 | 内容 |
|---|---|
| `apps/desktop-avalonia/tests/NewManga.App.Tests/CredentialUiTests.cs` | 1 处默认 `AppOptions` → `LegacyUiTestOptions.Isolated()` |
| `.../F11HotkeyTests.cs` | 1 处（`NewWindow`） |
| `.../LegacyAppearanceSyncTests.cs` | 1 处（`CreateWindow`） |
| `.../ImportExportUiTests.cs` | 3 处（`OpenShell` / `OpenReaderWithExport` / `ExportWithoutTranslatedPages`） |
| `.../RegionWorkbenchUiTests.cs` | 1 处 |
| `.../ThemeRetirementR4Tests.cs` | 4 处（含 2 处 Show 站点） |
| `.../LegacyWindowIsolationTests.cs`（新增） | 隔离 helper（唯一临时根 + 进程退出清理）+ 源扫描守卫 + 真实 `Show()` 隔离判别 + 只读 AppData 比较 |
| `verification/FEA-07-RESIDUAL-4/**` | README / DEFECTS / evidence / logs / tools（harness） |

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC-R4-1 | 源扫描守卫 + `git grep "new MainWindow("` | `86d65d1a9` | 16 处 Show / 6 文件全部隔离；守卫测试通过 | `verification/.../README.md` |
| AC-R4-2 | harness `-Capture` → 全量 `App.Tests` → `-Verify`（静默树） | 同上 | **836 passed / 2 failed（既有）/ 11 skipped / 849**；**delta=0**（14544 → 14544） | `evidence/appdata-before.json`、`logs/appdata-isolation.log`、`logs/full-solution.log` |
| AC-R4-3 | `-SelfTest` | 同上 | 追加 1 行 → 检出 `delta=1` / EXIT 1；无变化 → EXIT 0 | `logs/appdata-isolation-selftest.log` |
| AC-R4-4 | `LegacyMainWindow_Show_WritesMaterialLogOnlyUnderIsolatedLogDir` | 同上 | 隔离目录 ≥1 行；真实 AppData 不变；cwd 无 `com.newmanga.desktop` | 测试通过日志见 full-solution.log |
| AC-R4-5 | `dotnet build sln`；全量 `NewManga.sln --no-build`；`check.ps1`；`verify_pins` | 同上 | build 0/0；sln **1799 passed / 2 failed（既有）/ 107 skipped**；check PASS；pins 18/18 | `logs/build.log`、`logs/full-solution.log`、`logs/governance.log` |
| AC-R4-6 | 卡 + `DEFECTS.md` + EV 表 + 本 Handoff | 同上 | 已登记 | 卡、`DEFECTS.md` |
| E3 定向 | 6 文件 + 新测试 `--filter` | 同上 | **46 passed / 0 failed** | 本次运行输出 |
| E8 pytest | L-R4b-5 单 node 隔离复跑（仅登记，不跑全量） | 同上 | `1 passed in 0.12s` | `DEFECTS.md` |

未跑项：全量 pytest（本卡零 Python diff）；真实进程/IPC（本卡零产品改动，不需要）；真实 DPI（AC5 豁免）。

## 既有失败说明（非本卡引入）

- `V2ConformanceTests.AppCSharp_OutsideShellLayout_HasNoRawDesignValues`（`Shell/V2/ImmersiveReaderWindow.cs` literal brush/color）
- `FluentPageTests.FluentShell_BreakpointsA11yShortcutsAndReducedMotion_AreExplicit`（Expected 17 / Actual 18）

两者在 base `a49311cbe` 上 `git stash` 全部改动后同样失败，改动前后计数完全相同（836/2/11/849）。建议另立回归修复卡；本卡 AC-R4-5 以「不新增失败」为准。

## 接收方式

- 分支 `main`；base `77a7459ab` → 实现 `86d65d1a9`；本 Handoff 在后续文档提交中引用实现 head。
- 复核命令：`git show --stat 86d65d1a9`；`git diff 5ca20036c..86d65d1a9 -- apps/desktop-avalonia/tests/NewManga.App.Tests`；按 README 的 harness 命令复跑。
- 关键检查点：`LegacyWindowIsolationTests` 守卫是否会因未来新增默认构造而 RED；harness 是否 fail closed；真实 AppData 是否仍 delta=0。

## 下一任务建议

见 `doc/STATUS.md` 与 `doc/REBASELINE_PLAN.md`（DSH 维护）；候选：`2C-RESIDUAL-1`（typed-stop 次序）/ README 对账；FEA-13 建卡。

## 风险与遗留

- 既有 2 个回归失败（见上）需另立修复卡，不属于本卡范围。
- `verification/FEA-09/logs/wire-redacted.ndjson` 在全量 sln 时被改写，已 `git checkout` 恢复（既有副作用）。
- L-R4b-2/3/4 与 L-R4a-3 已 re-home，未在本卡实现。
