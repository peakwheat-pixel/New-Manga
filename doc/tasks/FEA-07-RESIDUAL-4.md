---
id: FEA-07-RESIDUAL-4
title: 默认套件 legacy MainWindow.Show() 真实 AppData 零写入（L-R4b-1 / D-R4b-7）
kind: implementation
governance_version: 3
status: ready
approval: scope review r1（`doc/reviews/FEA-07-RESIDUAL-4-scope-r1.md`，独立上下文；verdict **NOT_RECOMMENDED（现卡按现文，6 项混装）→ 缩窄为 L-R4b-1-only 后 READY-TO-FREEZE**）+ DSH 2026-11-09 冻结裁决：按该报告 §3/§4/§10 缩窄；L-R4b-2/3/4 拆分或降级、L-R4b-5 仅登记、L-R4a-3 移出；base `77a7459ab`
suggested_owner: dsh
owner: null
reviewer: null
depends_on:
  - FEA-07
  - FEA-07-RESIDUAL-3
base_commit: 77a7459ab
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-07-RESIDUAL-4
allowed_paths:
  - doc/tasks/FEA-07-RESIDUAL-4.md
  - doc/reviews/FEA-07-RESIDUAL-4-*.md
  - doc/handoffs/FEA-07-RESIDUAL-4-*.md
  - verification/FEA-07-RESIDUAL-4/**
  - apps/desktop-avalonia/tests/NewManga.App.Tests/CredentialUiTests.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/F11HotkeyTests.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/LegacyAppearanceSyncTests.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/ImportExportUiTests.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/RegionWorkbenchUiTests.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/ThemeRetirementR4Tests.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/LegacyWindowIsolationTests.cs
out_of_scope:
  - App 生产文件零 diff：`AppOptions.cs`、`Views/MainWindow.axaml.cs`、`App.axaml`、`App.axaml.cs`、`Services/StartupDiagnostics.cs`、`NewManga.sln`（共享组合根仅 DSH 单点提交，且本卡不需要）
  - `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`、`doc/tasks/README.md`、`doc/00_INDEX.md`、`doc/12_ROADMAP.md` 由 DSH 生命周期写入，Owner 不回写
  - `doc/plan/**`、`doc/contracts/**`、18 pins、`tools/governance/**`、`src/**`（Python）、`tests/**`（Python）零 diff
  - L-R4b-2 / L-R4b-3 / L-R4b-4 / L-R4a-3 的实现或修复不在本卡（见 §re-home）
---

# FEA-07-RESIDUAL-4：默认套件 legacy `MainWindow.Show()` 真实 AppData 零写入

## 来源与现状

- 来源：`FEA-07-RESIDUAL-3` closeout 的 **L-R4b-1 / D-R4b-7**（2026-10-27 起既有，非 R4b 引入）。
- **现状（scope review r1 核实，2026-11-09）**：默认 `NewManga.App.Tests` 仍有 **16 处** legacy `MainWindow.Show()` 不传 `--log-dir`（6 文件；清单见 review §2.1），`MainWindow.ResolveDiagnosticsRoot`（`MainWindow.axaml.cs:1041-1047`）在无 `--log-dir` 时回退真实 `%APPDATA%\com.newmanga.desktop\logs`，每次 `Show()` 追加 1 行材质行 → 既有实测 **+16 行/轮**。
- **关键纠正（P1/S-03）**：仅补 `--data-root` **不能**隔离 `window-material.log`，诊断根只看 `LogDirectory`（`AppOptions.cs:343-348`）；修复必须显式 `--log-dir`（测试侧）。
- 反例可复用：`F11HotkeyTests.cs:244-245` 已使用 `--log-dir`。

## 范围（冻结）

**做**：给 6 个既有测试文件中的 16 处 `MainWindow.Show()` 站点注入隔离 `--log-dir`（建议同时 `--data-root`）；新增 `LegacyWindowIsolationTests.cs` 提供统一 `IsolatedLegacyOptions()`、源扫描守卫与真实 `Show()` 隔离判别测试；建立真实 `%APPDATA%` 零写入的度量 harness 与证据。

**不做**：不改产品日志解析；不改 `--log-dir` 语义；不改任何断言语义（仅构造参数）；不修 FEA-06 视觉证据测试；不跑/不修 Python。

## Acceptance Criteria（6 条，实现完成后按 v3 标记）

- [ ] **AC-R4-1（站点完整）**：默认套件中所有真实 `MainWindow.Show()` 站点（当前 16 处 / 6 文件）都使用显式隔离 `--log-dir`；新增源扫描守卫，出现「默认 `AppOptions` + `Show()`」即 **RED**。
- [ ] **AC-R4-2（真实 AppData 零写入，强断言）**：默认 `NewManga.App.Tests` 整轮前后，真实 `%APPDATA%\com.newmanga.desktop` 与 `%APPDATA%\NewManga` 的递归快照（相对路径集合、字节长度、`logs/window-material.log` 行数、`logs/startup.log` 存在性）delta=0；harness delta≠0 → exit 1，采集失败 → fail closed，不得 skip。
- [ ] **AC-R4-3（harness 自检可判别）**：对隔离临时文件追加 1 行必须报 `delta=1`/exit 1，不追加 exit 0；自检全程不碰真实 AppData。
- [ ] **AC-R4-4（产品契约仍成立）**：真实 `MainWindow` + `--log-dir=<temp>` + `Show()` → `<temp>/window-material.log` 恰好 1 行；cwd 无 `com.newmanga.desktop`；真实 `%APPDATA%` 行数不增长（只读比较）；**禁止**用「去掉 `--log-dir`」做变异。
- [ ] **AC-R4-5（回归/门禁）**：diff ⊆ `allowed_paths`；`out_of_scope` 零 diff；build 0 warning/0 error；`NewManga.App.Tests` 0 failed 且 skipped 不增；全量 .NET 0 failed（给出总数/差值）；`check.ps1`（默认 + `-TaskPath`）PASS；pins 18/18；`git status` 仅预期文件。
- [ ] **AC-R4-6（residual 处置/证据）**：卡与 `verification/FEA-07-RESIDUAL-4/DEFECTS.md` 明确 D-R4b-7 resolved（含 head、delta=0）；L-R4b-2 `SPLIT`、L-R4b-3 `SPLIT/DEFER`、L-R4b-4 `DEFER（运行纪律）`、L-R4b-5 `已登记`、L-R4a-3 `DROP（另案）`；EV 表 + Resource Manifest + Handoff 齐全；Owner 不翻 `status`。

## 证据计划

| # | 类别 | 命令/步骤 | 判别 | 证据 |
|---|---|---|---|---|
| E1 | 静态 | `git grep -n "new MainWindow(" -- apps/desktop-avalonia/tests/NewManga.App.Tests` + `--list-tests`（只列不跑） | 26 构造 / 16 Show / 6 文件 | `logs/mainwindow-sites.txt` |
| E2 | headless | `dotnet build apps/desktop-avalonia/NewManga.sln -c Debug` | 0 warning / 0 error | `logs/build.log` |
| E3 | headless | 目标 6 文件 + 新增测试的定向 `dotnet test --filter` | 0 failed | `logs/app-tests-targeted.log` |
| E4 | headless（核心） | 默认 `NewManga.App.Tests` 全轮 + harness 前后快照（静默树、串行、证据后写） | 0 failed；两棵树 delta=0；`startup.log` 不出现 | `logs/app-tests-full.log`、`evidence/appdata-isolation.json` |
| E5 | headless（回归） | 全量 `dotnet test apps/desktop-avalonia/NewManga.sln --no-build`（静默树/串行；前 clean，后 `git checkout -- verification/FEA-09`） | 0 failed；总数不低于既有基线 | `logs/full-solution.log` |
| E6 | harness 自检 | `verification/FEA-07-RESIDUAL-4/tools/appdata-isolation-check.ps1 -SelfTest` | 追加→delta=1/exit 1；不追加→exit 0 | `logs/appdata-isolation-selftest.log` |
| E7 | 治理 | `check.ps1`（默认 + `-TaskPath`）、`verify_pins`、`git status --short`、`git diff --name-only` | EXIT 0；pins 18/18；diff ⊆ allowed_paths | `logs/governance.log`、`logs/pins.log` |
| E8 | pytest | **NOT_RUN**（本卡零 Python diff；L-R4b-5 仅登记） | 不得写成 PASS | `DEFECTS.md` |
| E9 | 真实进程/IPC | **不需要**；可选复用 R4b `--shell=legacy` + 隔离 `--log-dir` 交叉核对 | 不得写真实 AppData | 可选日志 |

## 运行纪律（L-R4b-4 规避）

E4/E5 必须在**静默树**执行：运行前完成所有文档/证据写入；运行期间不编辑 `verification/**`、不并发跑其它 Agent/门禁；harness 快照在内存或仓外完成；`verification/FEA-07-RESIDUAL-4/**` 的日志与 JSON 在运行**结束后**落盘。若命中既有 `FluentResidual2VisualEvidenceTests` 假红，保留首轮日志、判定是否仅并发写入、静默树复跑；不得改该断言。

## 风险与回退

| 风险 | 缓解 | 中止/回退 |
|---|---|---|
| 红线：漏改站点 → 真实 AppData +1 行/Show | 先 E1 枚举 + AC-R4-1 守卫；E3 先小后大；harness fail closed | delta>0 立即停；**不删除**该行（删除又是一次写），登记并重设基线后重跑 |
| 并发写 `verification/` 假红 | 静默树/串行/证据后写 | 复跑，不改断言 |
| `verification/FEA-09/logs/wire-redacted.ndjson` 被改写 | E5 前后 clean/restore | 按既有 flaky 处置 |
| 测试计数漂移 | 基线固定，新增 passed 计入并解释；skipped 不得新增 | 出现新 skip → 回 DSH |
| 临时目录泄漏 | 每处唯一 GUID 目录 + `IDisposable` 清理 | 清理失败只记 warning |
| 产品侧 scope creep | 生产文件零授权 | 需要改产品 → 停止，回 DSH 重新冻结 |

**回退**：仅测试改动，revert 测试 commit 即可；不涉及数据迁移、不删用户数据、不改 pins/契约。

## re-home（本卡不实现）

| residual | 处置 | 去向 |
|---|---|---|
| L-R4b-2（候选证据弱，`region_candidates` 不存在） | **SPLIT** | 候选证据强化卡（生产 `pipeline_runs`/`step_runs` 父行 + 真实陈旧候选；注意最终表名 `step_result_candidates`） |
| L-R4b-3（未过 HostRuntime；真实 DPI 未断言） | **SPLIT + DEFER** | HostRuntime gated 强化卡（可选）；真实 DPI 按 AC5 豁免 `NOT_RUN` |
| L-R4b-4（并发写假红） | **DEFER** | 本卡运行纪律规避；测试卫生另案 |
| L-R4b-5（pytest 未登记 flake） | **登记** | 本卡 `DEFECTS.md` 记完整 node id/错误/隔离复跑；STATUS 更新由 DSH 决定 |
| L-R4a-3（n50/200/500 p95 超 1000ms） | **DROP（移出）** | 产品性能卡/维持只记录，由 DSH/用户决定 |

## 禁止范围

- 不得改契约字节、pins、`doc/plan/**`、`doc/contracts/**`、`tools/governance/**`。
- 不得改产品文件（日志解析、CLI 语义、启动逻辑）。
- 不得把 `NOT_RUN`/`SPLIT`/`DEFER` 写成 PASS/MET；不得删除真实 AppData 中已产生的行。
- 不得自审：Reviewer 必须为独立上下文（非实现会话/实例）。
- 不 push（由 DSH 统一）。

## 门禁（完成时）

`check.ps1`（默认 + `-TaskPath`）PASS、`verify_pins` 18/18、`git diff --name-only ⊆ allowed_paths`、`out_of_scope` 零 diff、全量 .NET 0 failed、`NewManga.App.Tests` 0 failed 且 skipped 不增、AC-R4-2 delta=0。
