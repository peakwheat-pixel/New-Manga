---
id: FEA-07-RESIDUAL-4
title: 默认套件 legacy MainWindow.Show() 真实 AppData 零写入（L-R4b-1 / D-R4b-7）
kind: implementation
governance_version: 3
status: in_review
approval: scope review r1（`doc/reviews/FEA-07-RESIDUAL-4-scope-r1.md`，独立上下文；verdict **NOT_RECOMMENDED（现卡按现文，6 项混装）→ 缩窄为 L-R4b-1-only 后 READY-TO-FREEZE**）+ DSH 2026-11-09 冻结裁决：按该报告 §3/§4/§10 缩窄；L-R4b-2/3/4 拆分或降级、L-R4b-5 仅登记、L-R4a-3 移出；base `77a7459ab`
suggested_owner: dsh
owner: dsh
reviewer: 待指派（必须独立上下文，不得为实现会话/实例）
depends_on:
  - FEA-07
  - FEA-07-RESIDUAL-3
base_commit: 77a7459ab
branch: null
worktree: null
integration_commit: null
delivery_head: 86d65d1a9
canonical_evidence_status: complete
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
- **现状（scope review r1 核实，2026-11-09）**：默认 `NewManga.App.Tests` 仍有 **16 处** legacy `MainWindow.Show()` 不传 `--log-dir`（6 文件），`MainWindow.ResolveDiagnosticsRoot`（`MainWindow.axaml.cs:1041-1047`）在无 `--log-dir` 时回退真实 `%APPDATA%\com.newmanga.desktop\logs`，每次 `Show()` 追加 1 行材质行 → 既有实测 **+16 行/轮**。
- **关键纠正（P1/S-03）**：仅补 `--data-root` **不能**隔离 `window-material.log`，诊断根只看 `LogDirectory`（`AppOptions.cs:343-348`）；修复必须显式 `--log-dir`（测试侧）。

## 实现记录（delivery `86d65d1a9`）

- 6 个既有测试文件的 **11 处** `new AppOptions()` → `LegacyUiTestOptions.Isolated()`（唯一临时根：`%TEMP%\nm-legacy-ui-<guid>` + `--data-root` + `--log-dir` + `--theme-home`；进程退出清理）。
- 新增 `LegacyWindowIsolationTests.cs`：`AllDefaultSuiteLegacyWindowShows_AreExplicitlyIsolated`（源扫描守卫：剥离注释后检查 6 个已知文件的默认构造；全仓守卫为 follow-up）、`IsolatedOptions_PointAtTemporaryDirectoriesOnly`、`LegacyMainWindow_Show_WritesMaterialLogOnlyUnderIsolatedLogDir`（隔离目录 ≥1 行、真实 AppData 只读不变、cwd 无标记）。
- 新增 `verification/FEA-07-RESIDUAL-4/tools/appdata-isolation-check.ps1`：两棵 AppData 树快照（文件集/长度/材质行数/startup.log 存在性）+ `-Verify`（delta≠0 或采集失败 → EXIT 1）+ `-SelfTest`（追加 1 行必须检出）。
- 结果：交付全量 `App.Tests` **836 passed / 2 failed（既有）/ 11 skipped / 849**（base 833/2/11/846），真实 AppData **delta=0**（14544 → 14544）；全量 `sln` **1799 passed / 2 failed / 107 skipped**（base 1796/2/107）。详见 `verification/FEA-07-RESIDUAL-4/`。

## Acceptance Criteria

- [x] **AC-R4-1（站点完整）**：默认套件已知 16 处 / 6 文件 legacy `MainWindow.Show()` 站点全部使用显式隔离 `--log-dir`；新增源扫描守卫覆盖这 6 个文件（剥离注释后匹配）；全仓构造守卫登记为 follow-up `R-LEGACY-GUARD`。 <<MET>>
- [x] **AC-R4-2（真实 AppData 零写入，强断言）**：默认 `NewManga.App.Tests` 整轮前后两棵 AppData 树（相对路径集合、字节长度、`window-material.log` 行数、`startup.log` 存在性）delta=0；harness delta≠0 → exit 1，采集失败 fail closed。 <<MET>>
- [x] **AC-R4-3（harness 自检可判别）**：以**子进程**对隔离根验证：追加 1 行 → `-Verify` 真实 EXIT 1；以新基线比较 → EXIT 0；全程不碰真实 AppData。 <<MET>>
- [x] **AC-R4-4（产品契约仍成立）**：真实 `MainWindow` + `--log-dir=<temp>` + `Show()` → `<temp>/window-material.log` ≥1 行；真实 `%APPDATA%` 行数不变；cwd 无 `com.newmanga.desktop`；未用「去掉 `--log-dir`」做变异。 <<MET>>
- [x] **AC-R4-5（回归/门禁）**：diff ⊆ `allowed_paths`；`out_of_scope` 零 diff；build 0/0；`NewManga.App.Tests` **不新增失败**（base 833/2/11/846 → 交付 836/2/11/849，新增 3 测试通过、失败/跳过数不变；2 个既有失败见 DEFECTS）；全量 `sln` base 1796/2/107 → 交付 1799/2/107；`check.ps1`（默认 + `-TaskPath`）PASS；pins 18/18；`git status` 仅预期文件。 <<MET>>
- [x] **AC-R4-6（residual 处置/证据）**：卡与 DEFECTS 明确 D-R4b-7 resolved；L-R4b-2 `SPLIT`、L-R4b-3 `SPLIT/DEFER`、L-R4b-4 `DEFER`、L-R4b-5 `已登记`、L-R4a-3 `DROP`；EV 表 + Resource Manifest + Handoff 齐全；Owner 不翻 `status`（由 DSH 收口）。 <<MET>>

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-R4-README | AC1–AC6 | `verification/FEA-07-RESIDUAL-4/README.md` | `86d65d1a9` | `a1b8bfc58004da49aaaccbdab890065cd38d91d83ad06f93d596066eed9c6314` | CANONICAL |
| EV-R4-DEFECTS | AC1–AC6 | `verification/FEA-07-RESIDUAL-4/DEFECTS.md` | `86d65d1a9` | `ce788bd5f2f50653eb0f435d8f339dc01ab0b6e40edbca5c515340d25941d58f` | CANONICAL |
| EV-R4-SNAPSHOT | AC2 | `verification/FEA-07-RESIDUAL-4/evidence/appdata-before.json` | `86d65d1a9` | `307d92f92f8521b2aa31ef8088d01e30374d92fa51990ec39fc4389df7136072` | CANONICAL |
| EV-R4-ZEROWRITE | AC2 | `verification/FEA-07-RESIDUAL-4/logs/appdata-isolation.log` | `86d65d1a9` | `7c2acb1b76bd9a3ee3a0de6b692a7d85dc895d06591505251e17e607cae920f4` | CANONICAL |
| EV-R4-SELFTEST | AC3 | `verification/FEA-07-RESIDUAL-4/logs/appdata-isolation-selftest.log` | `86d65d1a9` | `a53c6d054de6aa8f25c35441a1088e01b915d647d8ae16c6097bbb1b8eb7e6c1` | CANONICAL |
| EV-R4-BUILD | AC5 | `verification/FEA-07-RESIDUAL-4/logs/build.log` | `86d65d1a9` | `0ed88800078379243372886e43a3dc84e4f5a6fcd5dfe401dc4532f6de018e70` | CANONICAL |
| EV-R4-APPTESTS | AC2,AC5 | `verification/FEA-07-RESIDUAL-4/logs/full-solution.log` | `86d65d1a9` | `05b3dc8edca15a4f5bdb90b5fa31aa7d46a3f332d725fe23e0124cb80902a9ac` | CANONICAL |
| EV-R4-GOV | AC5 | `verification/FEA-07-RESIDUAL-4/logs/governance.log` | `86d65d1a9` | `7a5e93123406047778c4f909e269db9ba8d7b469bdbd73668ba388abb589a1eb` | CANONICAL |
| EV-R4-HARNESS | AC2,AC3 | `verification/FEA-07-RESIDUAL-4/tools/appdata-isolation-check.ps1` | `86d65d1a9` | `e1e73f1137b34e74035953ab562974e02a4918ed4df18391f4ce2ade63c955e5` | CANONICAL |

## 证据计划（原始计划，已执行）

| # | 类别 | 命令/步骤 | 结果 | 证据 |
|---|---|---|---|---|
| E1 | 静态 | `git grep -n "new MainWindow("` + 守卫测试 | 26 构造 / 16 Show / 6 文件；11 处已隔离 | 卡 + `LegacyWindowIsolationTests` |
| E2 | headless | `dotnet build NewManga.sln -c Debug` | 0 warning / 0 error（EXIT 0） | `logs/build.log` |
| E3 | headless | 6 文件 + 新测试定向 `--filter` | 46 passed / 0 failed | 见 Handoff |
| E4 | headless（核心） | 默认 `App.Tests` 全轮 + harness 前后快照（静默树） | 836/2（既有）/11/849；delta=0 | `logs/full-solution.log`、`evidence/appdata-before.json`、`logs/appdata-isolation.log` |
| E5 | headless（回归） | 全量 `NewManga.sln --no-build`（前后恢复 `verification/FEA-09`） | 1799 passed / 2 failed（既有）/ 107 skipped | `logs/full-solution.log` |
| E6 | harness 自检 | `-SelfTest` | 追加行检出（EXIT 1 by design）+ 无变化 EXIT 0 | `logs/appdata-isolation-selftest.log` |
| E7 | 治理 | `check.ps1` 默认 + `-TaskPath`；`verify_pins` | EXIT 0 / 0 / 18/18 | `logs/governance.log` |
| E8 | pytest | 仅 L-R4b-5 单 node 登记 | `1 passed in 0.12s`；未跑全量 | `DEFECTS.md` |
| E9 | 真实进程/IPC | **不需要**（本卡零产品改动） | NOT_RUN | — |

## 运行纪律

E4/E5 在静默树执行（运行期间不写 `verification/**`）；证据在运行结束后落盘。命中 `verification/FEA-09/logs/wire-redacted.ndjson` 既有改写，已 `git checkout` 恢复。

## 风险与回退

| 风险 | 缓解 | 结果 |
|---|---|---|
| 漏改站点 → 真实 AppData +1 行 | E1 枚举 + AC-R4-1 守卫 + harness fail closed | 未发生（delta=0） |
| 并发写 `verification/` 假红 | 静默树/串行/证据后写 | 未命中 |
| FEA-09 wire 文件被改写 | 运行后恢复 | 已恢复 |
| 测试计数漂移 | 记录基线并比对 | 836/2/11/849（新增 3 通过） |
| 既有 2 失败被误读为本卡回归 | base `git stash` 对照复跑 | 已证明既有（DEFECTS） |

**回退**：仅测试与证据改动，`git revert 86d65d1a9` 即可；不涉及数据迁移、不删用户数据、不改 pins/契约。

## re-home（本卡不实现）

| residual | 处置 | 去向 |
|---|---|---|
| L-R4b-2 | SPLIT | 候选证据强化卡（生产 `pipeline_runs`/`step_runs` 父行；最终表名 `step_result_candidates`） |
| L-R4b-3 | SPLIT + DEFER | HostRuntime gated 强化卡（可选）；真实 DPI 按 AC5 豁免 `NOT_RUN` |
| L-R4b-4 | DEFER | 运行纪律规避 + 测试卫生另案 |
| L-R4b-5 | 登记 | `DEFECTS.md`（完整 node id/错误/隔离复跑） |
| L-R4a-3 | DROP | 产品性能卡/维持只记录 |
| R-LEGACY-GUARD（全仓构造守卫） | follow-up | 另立回归保护卡：扫描全仓 `new MainWindow(` 并要求 options 显式隔离（本卡守卫仅覆盖 6 个已知文件） |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（main；base `77a7459ab`） | NOT_APPLICABLE | — | — | 未创建 worktree |
| temp | `%TEMP%\nm-legacy-ui-<guid>`（测试隔离根，进程退出清理） | NOT_APPLICABLE | — | — | 仅测试临时目录；进程退出删除 |
| build | `apps/desktop-avalonia/**/bin|obj`（既有构建产物） | NOT_APPLICABLE | — | — | 仓库既有 ignore；未额外归档 |
| user-data | 真实 `%APPDATA%` 只读比较 | NOT_APPLICABLE | — | — | 未写入；harness delta=0 |
| evidence | `verification/FEA-07-RESIDUAL-4/**` | PRESERVE_REFERENCED | 原位 | `README.md`/`DEFECTS.md` 内哈希 | 被本卡 EV 引用 |

## Closeout Record

- 待独立 Review 通过后由 DSH 填写。
