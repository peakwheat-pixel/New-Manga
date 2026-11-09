# FEA-07-RESIDUAL-4 证据索引

- Task：`FEA-07-RESIDUAL-4`（L-R4b-1-only；scope review r1：`doc/reviews/FEA-07-RESIDUAL-4-scope-r1.md`）
- Base：`a49311cbe`（冻结申请 `77a7459ab`；冻结提交 `5ca20036c`）
- 环境：Windows 11 / pwsh 7.x / .NET SDK（目标 net9.0）/ Python 3.14.6
- 日期：2026-11-09

## 结论摘要

| 断言 | 结果 |
|---|---|
| 默认套件 legacy `MainWindow.Show()` 全部显式隔离 | 16 处 / 6 文件 → 11 处构造改为 `LegacyUiTestOptions.Isolated()`；守卫测试 `AllDefaultSuiteLegacyWindowShows_AreExplicitlyIsolated` 通过 |
| 全量 `NewManga.App.Tests` 前后真实 `%APPDATA%` 零写入 | **delta=0**（`com.newmanga.desktop` 与 `NewManga` 两棵树文件集/长度/`window-material.log` 行数/`startup.log` 存在性全同；14544 → 14544） |
| harness 非空断言 | 自检：隔离副本追加 1 行 → 检出 `delta=1` / EXIT 1；无变化 → EXIT 0 |
| 真实 `MainWindow` + 隔离 `--log-dir` + `Show()` | `<temp>/window-material.log` ≥1 行；真实 `%APPDATA%` 行数不变；cwd 未出现 `com.newmanga.desktop` |
| 不新增失败 | 全量 `App.Tests`：**836 passed / 2 failed（既有，base 对照）/ 11 skipped / 849**；全量 `sln`：**1799 passed / 2 failed / 107 skipped**（同一既有失败） |

## 证据文件

| 文件 | 内容 |
|---|---|
| `evidence/appdata-before.json` | 全量测试前的两棵 AppData 树快照（路径集 + 长度 + 材质行数 + startup.log 存在性） |
| `logs/appdata-isolation.log` | `-Verify` 结果：`ZERO-WRITE OK`（delta=0） |
| `logs/appdata-isolation-selftest.log` | `-SelfTest`：追加行被检出（EXIT 1 by design）+ 无变化 EXIT 0 |
| `logs/build.log` | `dotnet build`（0 warning / 0 error） |
| `logs/app-tests-full.log` | 全量 `NewManga.App.Tests` 运行（含失败清单） |
| `logs/full-solution.log` | 全量 `NewManga.sln` 回归（Appearance 21、Presentation 72、ThemeEngine 253、DesignSystem 117、ApplicationCore 31、Host 302/72 skip、CoreClient 167/24 skip、App.Tests 836/2 fail/11 skip） |
| `logs/governance.log` / `logs/pins.log` | `check.ps1`（默认 + `-TaskPath`）/ `verify_pins`（18/18） |

## 命令

```powershell
# 快照 → 跑全量 → 比较（AC-R4-2）
pwsh -NoProfile -File verification/FEA-07-RESIDUAL-4/tools/appdata-isolation-check.ps1 -Capture verification/FEA-07-RESIDUAL-4/evidence/appdata-before.json
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --no-build
pwsh -NoProfile -File verification/FEA-07-RESIDUAL-4/tools/appdata-isolation-check.ps1 -Verify verification/FEA-07-RESIDUAL-4/evidence/appdata-before.json

# 自检（判别力）
pwsh -NoProfile -File verification/FEA-07-RESIDUAL-4/tools/appdata-isolation-check.ps1 -SelfTest
```

## 说明

- 既有 2 个失败在 base `a49311cbe` 上同样存在（`git stash` 对照复跑），非本卡引入；详见 `DEFECTS.md`。
- 运行纪律：全量测试在静默树执行（运行期间不写 `verification/**`），证据在运行结束后落盘。
- 本卡零 Python diff；pytest 只做 L-R4b-5 单 node 隔离复跑登记（`DEFECTS.md`），未跑全量。
