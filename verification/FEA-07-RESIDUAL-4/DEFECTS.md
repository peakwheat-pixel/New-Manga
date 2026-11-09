# FEA-07-RESIDUAL-4 缺陷与残余登记

- Task：`FEA-07-RESIDUAL-4`（L-R4b-1-only；scope review r1 缩窄）
- Base：`77a7459ab`（冻结申请；冻结提交 `5ca20036c`）
- 日期：2026-11-09

## D-R4b-7（本卡修复目标）— **resolved**

- **现象（修复前）**：默认 `NewManga.App.Tests` 中 16 处 legacy `MainWindow.Show()` 使用默认 `AppOptions`（无 `--log-dir`），`MainWindow.ResolveDiagnosticsRoot` 回退真实 `%APPDATA%\com.newmanga.desktop\logs`，每轮稳定追加约 16 行 `window-material.log`（`FEA-07-RESIDUAL-3` 实测 `14340 → 14356`）。
- **关键纠正**：仅补 `--data-root` 不能隔离该文件；诊断根只读 `LogDirectory`（`AppOptions.cs:343-348`）。
- **修复**：6 个既有测试文件的 11 处构造改为 `LegacyUiTestOptions.Isolated()`（唯一临时根 + `--data-root` + `--log-dir` + `--theme-home`）；新增 `LegacyWindowIsolationTests.cs`（剥离注释的源扫描守卫 + helper 目录断言 + 真实 `Show()` 隔离判别）。
- **判别证据**：
  - 交付全量 `NewManga.App.Tests`：**836 passed / 2 failed（既有）/ 11 skipped / 849**；真实 `%APPDATA%` 两棵树 `delta=0`（`window-material.log` 14544 → 14544；`startup.log` 不存在）。
  - base（去掉本卡新增的 3 个测试）：**833 passed / 2 failed / 11 skipped / 846**（全量 sln **1796/2/107** → 交付 **1799/2/107**）。
  - harness 自检：子进程对「追加 1 行」的隔离根返回真实 **EXIT 1**；对新基线返回 **EXIT 0**。
  - 证据：`evidence/appdata-before.json`、`logs/appdata-isolation.log`、`logs/appdata-isolation-selftest.log`、`logs/full-solution.log`。

## 既有失败（base 对照，**非本卡引入**）

| 用例 | 失败 | 依据 |
|---|---|---|
| `V2ConformanceTests.AppCSharp_OutsideShellLayout_HasNoRawDesignValues` | `Shell/V2/ImmersiveReaderWindow.cs` 存在 literal brush/color（`ImmersiveReaderWindow.cs:23`） | `git diff a49311cbe..HEAD` 对 `V2ConformanceTests.cs`、`ImmersiveReaderWindow.cs` 为空；`5108c6640` 是 base 祖先；HEAD 复现同消息 |
| `FluentPageTests.FluentShell_BreakpointsA11yShortcutsAndReducedMotion_AreExplicit` | `Expected: 17 / Actual: 18`（`FluentPageTests.cs:132`） | 同上（`FluentShell.axaml.cs`/`FluentShellSurface.axaml.cs` 零 diff） |

- **处置**：本卡为纯测试隔离，不修上述产品/测试断言（App 源码与 `FluentPageTests` 不在本卡 `allowed_paths`）。**建议另立回归修复卡**（`FEA-07-V2-F11-1` 之后的既有回归债务）。
- **本卡 AC-R4-5 口径**：以「**不新增失败**」为准——base 833/2/11/846 → 交付 836/2/11/849（新增 3 个测试通过，失败数与跳过数不变）。

## R-LEGACY-GUARD（回归保护 follow-up，本卡不做）

- **现状**：本卡守卫只覆盖被实测的 6 个 legacy-show 文件；全仓仍存在 15 处「构造 `MainWindow` 但从不 `Show()`」的默认 `AppOptions` 用法（`ReaderChapterSelectorTests.cs`、`ReaderLibraryTests.cs`、`ReaderProgressTests.cs` 等），以及 `AppOptions.Parse(Array.Empty<string>())` / `AppOptionsStore.Current` 等别名形态。
- **风险**：未来在这些文件加 `Show()` 或新增测试文件使用默认构造，会绕过本卡守卫。
- **处置**：登记为 follow-up（repo-wide construction guard：扫描全仓 `new MainWindow(` 并要求 options 实参显式隔离）；不在本卡 `allowed_paths` 内（需改本卡外文件）。

## L-R4b-5（pytest 未登记 flake）— 已登记，**零代码**

- node id：`tests/fea09/test_referenced_flow.py::test_replay_conflicting_fingerprint_rejected`
- 观测错误：`sqlite3.InterfaceError`（`tests/fea09/conftest.py:33-44` 的 `:memory:` 共享连接跨 worker 线程提交）
- 隔离复跑（本卡实测）：`1 passed in 0.12s`（2026-11-09）
- 与 `test_plugin_sandbox.py::test_sandbox_job_kills_grandchildren` 为**不同** flake，不合并登记。
- 未跑全量 pytest（本卡零 Python diff）；不得把「隔离复跑绿」写成全量 PASS。

## L-R4b-2 / L-R4b-3 / L-R4b-4 / L-R4a-3 —— 本卡不实现

| residual | 处置 | 去向 |
|---|---|---|
| L-R4b-2（候选证据弱） | SPLIT | 候选证据强化卡（生产 `pipeline_runs`/`step_runs` 父行；最终表名 `step_result_candidates`） |
| L-R4b-3（未过 HostRuntime；真实 DPI） | SPLIT + DEFER | HostRuntime gated 强化卡（可选）；真实 DPI 按 AC5 豁免 `NOT_RUN` |
| L-R4b-4（并发写 verification 假红） | DEFER | 运行纪律（静默树/串行/证据后写）+ 测试卫生另案 |
| L-R4a-3（规模性能 p95） | DROP（移出） | 产品性能卡/维持只记录 |
