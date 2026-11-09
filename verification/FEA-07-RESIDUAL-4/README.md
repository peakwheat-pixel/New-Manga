# FEA-07-RESIDUAL-4 证据索引

- Task：`FEA-07-RESIDUAL-4`（L-R4b-1-only；scope review r1：`doc/reviews/FEA-07-RESIDUAL-4-scope-r1.md`）
- Base：`77a7459ab`（冻结申请；冻结提交 `5ca20036c`）
- 环境：Windows 11 / pwsh 7.6 / .NET SDK（目标 net9.0）/ Python 3.14.6
- 日期：2026-11-09

## 结论摘要

| 断言 | 结果 |
|---|---|
| 默认套件已知 legacy `MainWindow.Show()` 站点全部显式隔离 | 16 处 / 6 文件 → 11 处构造改为 `LegacyUiTestOptions.Isolated()`（`--log-dir` + `--data-root` + `--theme-home`）；守卫测试覆盖这 6 个文件（剥离注释后匹配） |
| 全量 `NewManga.App.Tests` 前后真实 `%APPDATA%` 零写入 | **delta=0**（`com.newmanga.desktop` 与 `NewManga` 两棵树文件集/长度/`window-material.log` 行数/`startup.log` 存在性全同；14544 → 14544） |
| harness 非空断言 | 自检以**子进程**验证：隔离副本追加 1 行 → `-Verify` 真实 **EXIT 1**；以新基线再比较 → **EXIT 0** |
| 真实 `MainWindow` + 隔离 `--log-dir` + `Show()` | `<temp>/window-material.log` ≥1 行；真实 `%APPDATA%` 行数不变；cwd 未出现 `com.newmanga.desktop` |
| 不新增失败 | 交付 `App.Tests`：**836 passed / 2 failed（既有）/ 11 skipped / 849**；base（无新增 3 测试）：**833 / 2 / 11 / 846**；全量 `sln`：**1799 / 2 / 107** |

> 守卫范围说明：仅覆盖被实测的 6 个 legacy-show 文件；全仓 `new MainWindow(...)` 默认构造守卫登记为 follow-up（`R-LEGACY-GUARD`，见 `DEFECTS.md`），不把本守卫读成全仓证明。

## 证据文件

| 文件 | 内容 |
|---|---|
| `evidence/appdata-before.json` | 全量测试前的两棵 AppData 树快照（路径集 + 长度 + 材质行数 + startup.log 存在性） |
| `logs/appdata-isolation.log` | `-Capture` 与 `-Verify` 完整输出（命令头、before/after、`ZERO-WRITE OK`、EXIT） |
| `logs/appdata-isolation-selftest.log` | `-SelfTest`：子进程对脏根 EXIT 1、对新基线 EXIT 0 |
| `logs/build.log` | `dotnet build NewManga.sln -c Debug`（0 warning / 0 error） |
| `logs/full-solution.log` | 全量 `NewManga.sln` 回归（8 个项目汇总） |
| `logs/governance.log` | `check.ps1`（默认 + `-TaskPath`）、`verify_pins`（18/18）输出与 EXIT |

## 命令

```powershell
# AC-R4-2：快照 → 全量 → 比较
pwsh -NoProfile -File verification/FEA-07-RESIDUAL-4/tools/appdata-isolation-check.ps1 -Capture verification/FEA-07-RESIDUAL-4/evidence/appdata-before.json -LogPath verification/FEA-07-RESIDUAL-4/logs/appdata-isolation.log
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --no-build
pwsh -NoProfile -File verification/FEA-07-RESIDUAL-4/tools/appdata-isolation-check.ps1 -Verify verification/FEA-07-RESIDUAL-4/evidence/appdata-before.json -LogPath verification/FEA-07-RESIDUAL-4/logs/appdata-isolation.log

# AC-R4-3：自检（子进程真实退出码）
pwsh -NoProfile -File verification/FEA-07-RESIDUAL-4/tools/appdata-isolation-check.ps1 -SelfTest -LogPath verification/FEA-07-RESIDUAL-4/logs/appdata-isolation-selftest.log
```

## 说明

- 既有 2 个失败在 base `a49311cbe` 上同样存在（输入未变 + `5108c6640` 祖先 + HEAD 复现同消息），非本卡引入；详见 `DEFECTS.md`。
- 运行纪律：全量测试在静默树执行（运行期间不写 `verification/**`），证据在运行结束后落盘。
- 本卡零 Python diff；pytest 只做 L-R4b-5 单 node 隔离复跑登记（`DEFECTS.md`），未跑全量。
