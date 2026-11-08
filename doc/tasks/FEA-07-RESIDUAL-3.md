---
id: FEA-07-RESIDUAL-3
title: FEA-07 收口 B（AC1 gated 真库 A03/ACK + AC3 跨进程崩溃 + AC4 真实入口/诊断 sink/矩阵）
kind: implementation
governance_version: 3
status: done
approval: 用户 2026-11-08 残余收口指令（R4）；scope 依据 = 独立 scope review `doc/reviews/FEA-07-RESIDUAL-2-scope-r1.md` §3/§4/§5.2（该评审已逐项覆盖 AC1/AC3/AC4 并给出最小方案与风险）；DSH 2026-11-08 裁决（ADJ §7.13）：0 pin、gated/进程级
suggested_owner: dsh
owner: fea07-residual3-impl
reviewer: 独立上下文 fresh subagent（不得由实现会话/实例自审）
depends_on:
  - FEA-07-RESIDUAL-2
base_commit: 8855baaac
branch: null
worktree: null
integration_commit: 8e9420f41
delivery_head: 8e9420f41
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-07-RESIDUAL-3
allowed_paths:
  - doc/tasks/FEA-07-RESIDUAL-3.md
  - doc/tasks/FEA-07.md
  - doc/reviews/FEA-07-RESIDUAL-3-*.md
  - doc/reviews/ADJ-2026-11-RESIDUAL-WAIVER.md
  - doc/handoffs/FEA-07-RESIDUAL-3-*.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea07Residual3IpcTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Support/**
  - apps/desktop-avalonia/tests/NewManga.App.Tests/**
  - apps/desktop-avalonia/src/NewManga.App/Services/StartupDiagnostics.cs
  - apps/desktop-avalonia/src/NewManga.App/App.axaml.cs
  - apps/desktop-avalonia/src/NewManga.App/Views/MainWindow.axaml.cs
  - verification/FEA-07-RESIDUAL-3/**
out_of_scope:
  - 原生 IME、AC5 双屏/拔屏/DPI 100–200% 矩阵、真实双屏 broker 落位（`NOT_APPLICABLE: 原生交互未执行（保留 NOT_RUN）+ 用户 2026-11-08 授权豁免`）
  - 冻结契约字节：`doc/plan/**`、`doc/contracts/**`、18 pins；不改 wire/命令集/错误码
  - 不改 `tools/e2e/**`、`apps/desktop-avalonia/scripts/**`（新脚本只放 `verification/FEA-07-RESIDUAL-3/tools/`）
  - 不改 `AppearanceCoordinator`/`FrontendSelector`/`Switching/**` 语义；不改 `NewManga.DesignSystem/**`、`NewManga.Appearance/**`；不改 `src/**`（Python）
  - `App.axaml.cs` 只允许 **≤5 行** `StartupDiagnostics` 接线，不得改组合根语义
  - 真实用户数据/AppData/外部卷/回收站；L3/L4 真机（NOT_RUN）
---

# FEA-07-RESIDUAL-3：FEA-07 收口 B（gated/进程级，0 pin）

> **状态 `ready`**（base `8855baaac`；0 pin）。承接 `FEA-07-RESIDUAL-2`（R4a）未覆盖的 AC1/AC3/AC4；**两卡都 MET 后 `FEA-07` 翻 done**。
> **前置事实**：R4a 已完成 AC2/AC6/AC8；本卡只做 AC1/AC3/AC4。

## Acceptance Criteria（冻结）

- [x] **AC-R4b-1（AC1 A03 真库 + ACK/Intent）**：gated（默认 skip + reason）真实 Host/Core：≥50 次前端往返切换前后，真实 `library.db` 的 `regions.text_json`、`current_revision_id`、`translation_locked`/`inpaint_locked`/`sfx_locked`、manual 位、`region_revisions` 行数、`region_candidates` 行数**逐列相同**（内嵌 Python 读库，**不引入 `Microsoft.Data.Sqlite`**）；ACK 丢失/重连同 idempotency key 只产生 1 个 run、旧结果仅 candidate；真实 Run/Intent 链路经生产 dispatcher。 <<MET>>
- [x] **AC-R4b-2（AC3 跨进程崩溃注入）**：外部驱动 `progress`：production 路径在 `beforeJournalCommit`（或 staging Loaded/Rendered）park → **独立进程** `GetProcessById().Kill(entireProcessTree:true)` 并断言真死（exit code 语义显式）→ **新进程** recover：终态 `RolledBack`、frontend=上一已提交、`appearance.FrontendId` 未被 target 污染、二次恢复零变化；「暂停期保护状态」两条断言（切换零写保护列 + 恢复采用最新状态、不回写旧快照）；**禁止** `Environment.FailFast`/同进程冒充/生产 backdoor。 <<MET>>
- [x] **AC-R4b-3（AC4 真实入口 + 诊断 sink + 矩阵）**：新增最小 `StartupDiagnostics`（`App/Services/StartupDiagnostics.cs` + `App.axaml.cs` ≤5 行接线，写 `<log-dir>/startup.log`）；真实进程 4 组参数（默认 / `--presentation-host=true` / `--shell=legacy` / 坏外观文档）→ `exit_code=0`、无 `fatal.log`、`startup.log` 含对应诊断行；**9 类 warning 逐项** fail-safe（坏 JSON / schemaVersion / corners.scale / appearance.mode / contrast / motion.mode / motion.categories / frontendId / visualThemeId）→ planner 强制 Current V2。 <<MET>>
- [x] **AC-R4b-4（证据/治理/翻转）**：EV/Resource Manifest/门禁日志；`FEA-07` AC1/AC3/AC4 **append-only** 回填（`[x] <<MET>>` 不带原因）+ 关账；`check.ps1` PASS、pins 18/18（0 pin）、全量 .NET 不降、pytest 既有 flaky 登记不恶化；`FEA-07` 翻 `done` 后 **4 节点全部 done**。 <<MET>>

## 实现口径

1. AC1 的 gated 用例放 `NewManga.Host.Tests`（`[HostSidecarFact]`/`ProductionIpcFact` 形态，默认 skip+reason）；读库用既有「.NET 内嵌 Python 脚本」先例（`Fea11RunGrantIpcTests.cs:1030-1109` 形态），**禁止新增 SQLite 依赖**。
2. AC3 驱动脚本 `verification/FEA-07-RESIDUAL-3/tools/crash-switch.ps1`（park/kill/recover 三阶段；`Process.Kill(entireProcessTree:true)`；显式 exit code 10/11/12/2 语义；证据 JSON）。被测 fact 用 env 开关（默认 skip）。
3. AC4 `StartupDiagnostics` 最小实现（写日志行 + `Trace` 兼容），`App.axaml.cs` 接线 ≤5 行；矩阵用例优先纯单元（`SafeStartupPlanner`），真实进程用例 gated（无桌面会话时 skip + reason）。
4. 提交显式 pathspec，禁 `git add -A`；含中文改动用 edit/Python UTF-8。

## 行文口径（红线）

- 不得写「FEA-07 完全实现 / AC5 达成 / 生产双屏可用」；只写「AC1/AC3/AC4 达成（gated/进程级）；AC5 与原生项 NA（NOT_RUN）；AC2/AC6/AC8 见 R4a」。
- `NOT_RUN` 不得写成 PASS；skip 不得写成 PASS。

## r1 返修（2026-11-08，独立 Review r1 approved P0=0/P1=0；DSH 把 P2-01 升格 P1）

> 本节只追加；不改上方 AC 冻结行与 `status`（由 DSH 关账）。

| # | finding | 修复 | 判别证据 |
|---|---|---|---|
| P1-01（升格） | 红线「不得触碰真实用户数据/AppData」：`--shell=legacy` 的 `window-material.log` 每次运行向真实 `%APPDATA%\com.newmanga.desktop\logs\` 追加 1 行（r1 度量 14,272→14,275），且两处注释称「不写真实 %APPDATA%」为假 | **DSH 裁决 A，授权扩域单文件**：`src/NewManga.App/Views/MainWindow.axaml.cs` 的 `WriteMaterialDiagnostics` 改为「显式 `--log-dir` 时 `LogDirectory` 拥有全部日志文件（含本文件）；无 `--log-dir` 保留历史每用户位置」（+5/−1：3 语义行 + 2 注释）。测试/脚本侧再注入隔离 `APPDATA`/`LOCALAPPDATA`/`USERPROFILE` 并用同一环境字典回读子进程值；两处注释改真 | 真实 `%APPDATA%` 行数 `14275 → 14275`（delta=0，gated fact 14/14 与 `startup-matrix.ps1` 4/4 各一次）；legacy 的 `window-material.log` 落隔离 `--log-dir`（1 行）；变异 M4/M4b RED（M4b 现场 `+1` 行）→ sha256 MATCH → 复绿 |
| P2-03 | AC3「暂停期采用最新状态」只改 `appearance.Mode`，未覆盖真实保护状态 | recover 前用**独立 sqlite 连接**改真实 `library.db`：新增 revision 3 设为 current + 翻转 `inpaint_locked`；恢复后断言仍是新值（不回写旧快照） | `logs/mutation-2-restored-green.log` / `evidence/crash-switch-r4b.json`（`recover.pausedRevisionId` / `pausedInpaintLocked` / `currentRevisionAfterRecovery`） |
| P3-01 | 卡面 `sfx_locked` 笔误 | erratum 登记：真实列为 `region_locked`（+ `translation_locked`/`inpaint_locked` + `sfx_policy`） | `DEFECTS.md` D-R4b-6、`README.md` §3/§6.5 |
| P3-02 | 回填脚本数字为「见下」占位 | 脚本内置实际数字（1791/0/107、3395/0/10）并改为幂等（已是 `- [x]` 时跳过不报错） | `tools/backfill-fea07.py` |
| P3-03 | `ResetForTests` 留下 `Trace.AutoFlush` 全局副作用 | 安装时保存调用前的值，`ResetForTests` 还原 | `StartupDiagnosticsTests.ResetForTests_RestoresTheProcessWideTraceAutoFlushFlag` |
| P3-05 | 崩溃证据未显式写 testhost 是否消失 | 证据 JSON 增 `kill.testhostGone`，`realDeathProven` = launcher/ testhost/ heartbeat 三者合取 | `evidence/crash-switch-r4b.json`、`README.md` §4 |

- 未改：`status`、AC 冻结行、契约/pins、禁止面；`FEA-07`/`FEA-07-RESIDUAL-3` 的 status 由 DSH 关账。

## r2 返修（2026-11-09，独立 Review r2 changes_requested P0=0/P1=1/P2=1/P3=4）

> 本节只追加；仍在 DSH 已授权的单文件（`MainWindow.axaml.cs`）范围内。

| # | finding | 修复 | 判别证据 |
|---|---|---|---|
| P1-01 | `MainWindow.axaml.cs` 的 `PropertyChanged`→`RenderScaling` 分支仍硬编码真实 `%APPDATA%`，**绕过 `--log-dir`**，与 r1 的注释/DEFECTS 口径矛盾 | 抽出 `internal static ResolveDiagnosticsRoot(AppOptions)`；材质行（`WriteMaterialDiagnostics`）与缩放行（新 `AppendScalingDiagnostics`）**共用**同一解析：显式 `--log-dir` → 该目录，无 → 历史每用户位置 | `MaterialDiagnosticsRoot_IsSharedByBothBranches`（纯函数）+ `ScalingDiagnosticsLandInTheIsolatedLogDirectory`（真实 `MainWindow` 驱动缩放写入口）；变异 M5（回退该分支为硬编码）→ RED 且真实日志 **+2 行** → sha256 MATCH → 复绿 |
| P2-01 | r1 的「env 注入 = 隔离保证」结论错误（App 实测 `GetFolderPath(ApplicationData)` 可为空 → 落 cwd 相对路径）；M4 的 RED 被描述成「双闸独立」 | env 注入降级为「App 侧实见环境」记录：`startup.log` 新增 `startup-diagnostics: isolation log-dir=… appdata=… cwd=…`；隔离断言改为 **App 可见**（install 行 + isolation 行 log-dir 一致、appdata 不被指向用例根、cwd 下无 `com.newmanga.desktop`、`window-material.log` 只在隔离目录、真实 `%APPDATA%` 行数不增长） | gated fact 16/16 与 `startup-matrix.ps1` 4/4 各 `delta=0`；脚本 `appdataSeen=` 为空（实证 App 侧解析为空而非隔离）；M4 的 RED 明确由「隔离目录断言 + `--log-dir` 契约」承担 |
| P3-01 | AC4 表基线 `14275` 与证据 `14340` 不一致 | README 表改为按轮次标注（`14275`/`14340`/`14406`/`14411`），逐轮标注 `delta=0` | `README.md` §5 |
| P3-02 | `mutation-4b` 日志缺 BEFORE/AFTER | 重跑 M4/M4b 并把 `real window-material.log lines BEFORE/AFTER … (delta=…)` 写入同一日志 | `logs/mutation-4b-p1-redline-regression.log` |
| P3-03 | 回填脚本 APPEND 不能生成当前尾部 | `APPEND` 更新为含 r1/r2 条目 + 实际数字，保持幂等（`- [x]` 时跳过） | `tools/backfill-fea07.py` |
| P3-04 | D-R4b-7 表述模糊、README「所有 r1 运行 delta=0」过宽 | D-R4b-7 精确为「`+16 行/轮 App.Tests`（对照实测）」；README 限定为「M4b 之后基线起」 | `DEFECTS.md` D-R4b-7、`README.md` §6.6/§6.7 |

- 未改：`status`、AC 冻结行、契约/pins、禁止面；扩域仍限 `MainWindow.axaml.cs` 的 `window-material` 两处写入分支。

## Closeout Record

- **Closeout date / DSH**：2026-11-09（会话内 2026-11-08 起）。
- **终态**：`done`；`integration_commit` = `delivery_head` = **`8e9420f41`**（r0 `c3e3d37b9` + r1 `219405b30` + r2 `8e9420f41`）。
- **Review 链**：r1 approved（P2-01 升 P1）→ r1 返修 → r2 **changes_requested（P1-01: RenderScaling 分支绕过 --log-dir）** → r2 返修 → **r3 approved（P0=0/P1=0/P2=0/P3=4）**。
- **AC 定稿**：AC-R4b-1…4 全 MET（含 DSH closeout 面）。
- **门禁（Lead 一手，head `8e9420f41`）**：build 0/0；全量 .NET **1794/0/107**；gated AC4 **16/16** 且真实 `%APPDATA%` **delta=0**；pytest **3395/0/10**；pins **18/18**；check PASS；API EXIT 0；diff 45 文件 ⊆ allowed_paths；禁止面零 diff；FEA-09 已恢复。
- **DSH 扩域留痕**：`apps/desktop-avalonia/src/NewManga.App/Views/MainWindow.axaml.cs`（+38/−10；`ResolveDiagnosticsRoot` 共用 + 缩放分支收口；授权依据：红线「不得触碰真实 AppData」、`--log-dir` 契约 W-9）。
- **重大质量收益**：真实进程测试与 `--log-dir` 契约闭环后，**gated AC4 真实 AppData delta=0**；捕获并修复两条既有硬编码日志路径（材质行、缩放行）。
- **limitation / re-home**：
  - **L-R4b-1（D-R4b-7）**：既有 headless UI 用例走 legacy `MainWindow` 且不传 `--log-dir`，**每轮 App.Tests 稳定 +16 行**真实 AppData（2026-10-27 起既有，非本卡引入）→ re-home 卡（给既有用例补 `--log-dir`）。
  - **L-R4b-2（D-R4b-1/P2-02）**：`region_candidates` 表不存在；「旧结果仅 candidate」以候选存量 0→0/零解析/陈旧 base 未进 current 表达，**证据强度弱**→ 后续候选/结果卡用生产 run/step 父行补强。
  - **L-R4b-3（D-R4b-5/P3-04）**：AC1 未过 `HostRuntime`/打包 sidecar；AC4 缩放「调用点」未被直接断言（headless 无法制造真实 DPI 变化）。
  - **L-R4b-4（D-R4b-8）**：全量运行期间若并发写 `verification/`，既有 `FluentResidual2VisualEvidenceTests` 会假红；关账/CI 需静默树。
  - **L-R4b-5**：pytest 未登记 flake `tests/fea09/test_referenced_flow.py::test_replay_conflicting_fingerprint_rejected`（`sqlite3.InterfaceError`；隔离/整文件复跑绿）。
- **行文**：不得写「FEA-07 完全实现 / AC5 达成 / 生产双屏可用」；只写「AC1/AC3/AC4 达成（gated/进程级）；AC5 与原生项 NA（NOT_RUN）；AC2/AC6/AC8 见 R4a」。

## Canonical Evidence

> `commit`：实现/测试文件填 `8e9420f41`（r2 最终）；证据填 `-`（sha 为工作树字节）。sha256 与工作树逐字节口径。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-R4B-01 | AC-R4b-1 | apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea07Residual3IpcTests.cs | 8e9420f41 | 74cdba4d250b936f9e16fcd641535e654e06eea588be6222453016293a39b0f2 | SOURCE_PIN |
| EV-R4B-02 | AC-R4b-2 | apps/desktop-avalonia/tests/NewManga.App.Tests/Fea07Residual3CrashTests.cs | 8e9420f41 | 90c5a87a8d7aa1a7e9a5c79ded3050f80dd3c01c7d558970c90546a80fe90551 | SOURCE_PIN |
| EV-R4B-03 | AC-R4b-3 | apps/desktop-avalonia/tests/NewManga.App.Tests/StartupDiagnosticsTests.cs | 8e9420f41 | 95d9741740954d4ec64c3ed88288bac23a8852b7db11ebf2bea84771a10dc17d | SOURCE_PIN |
| EV-R4B-04 | AC-R4b-3 | apps/desktop-avalonia/src/NewManga.App/Services/StartupDiagnostics.cs | 8e9420f41 | faa6edf2461a54fc3cf7358ca8a86fc3d655243249d33e6f27f5a18a49faa86e | SOURCE_PIN |
| EV-R4B-05 | AC-R4b-3 | apps/desktop-avalonia/src/NewManga.App/App.axaml.cs | 8e9420f41 | 07c93db9b979a16fbd2746383ede35f9535b6bd4012e11bb5dc52980f3ac2ce3 | SOURCE_PIN |
| EV-R4B-06 | AC-R4b-3/P1 | apps/desktop-avalonia/src/NewManga.App/Views/MainWindow.axaml.cs | 8e9420f41 | 0c4b818fb51d5cf32e24fb6094ff91d2b0bafa351e8c8730de7e127956eb3c9d | SOURCE_PIN |
| EV-R4B-07 | AC-R4b-4 | doc/tasks/FEA-07.md | 8e9420f41 | c64b6a97427ef8c37b1f40569d5182d0476dd2742e8a945bc3a3cf5fea40b3eb | SOURCE_PIN |
| EV-R4B-08 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/DEFECTS.md | - | db2c5671048aa3be8dbb89c0d93a3f0280c771ba2710d9d6a0d579dcedc66f25 | CANONICAL |
| EV-R4B-09 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/README.md | - | b12f5038a81bb4dc1884285770addfda92dcddbe4d4c94793cfe6c45cd0733be | CANONICAL |
| EV-R4B-10 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/RESOURCE-MANIFEST.json | - | d97f06178e2baf3c6ec712fb346a9fc9d88b6e2a06550290b6c8000a9f50244d | CANONICAL |
| EV-R4B-11 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/evidence/crash-switch-r4b.json | - | 03323ce17510e08b70d2eb667a15f4673ead76e05fc26260f74061c462705320 | CANONICAL |
| EV-R4B-12 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/evidence/startup-matrix-r4b.json | - | 733c52c94093b745ee92f38ed099e8b6f788a136f2ed47024758a59ea7b5dd61 | CANONICAL |
| EV-R4B-13 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/logs/a03-gated-ipc.log | - | 1d3652b19912d5859043cbd93241a57745baf4df15b762b18a00e8be4269e025 | CANONICAL |
| EV-R4B-14 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/logs/app-tests.log | - | 0baa913c6ea708a01514fa9693192f6300446ac4e88a82b0670a5d7473ed38f4 | CANONICAL |
| EV-R4B-15 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/logs/crash-switch.log | - | 7a6df8990674a0954c0834f9eb67b21d0d696ef1670d8c383e97edf36bc120cf | CANONICAL |
| EV-R4B-16 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/logs/full-solution-tests-first-run-concurrent-write.txt | - | 378315c77e5d5b53f1709f2b7818037d4973b2369930194a0f4d2e7d86661d40 | CANONICAL |
| EV-R4B-17 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/logs/full-solution-tests.log | - | 2cf663a859b8d083039383b9f2032736fcab11290eff64af6452fa6959d5653f | CANONICAL |
| EV-R4B-18 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/logs/governance.log | - | 25326406934ff93a66fd1ed7b57d018f1016db3c79e6763fb5aee80a6efa8ddf | CANONICAL |
| EV-R4B-19 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/logs/host-tests.log | - | 77d914e1ff64ff45e724fd444ad47d83a19ecb0d36348e1ee8ef396c2ac464eb | CANONICAL |
| EV-R4B-20 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/logs/mutation-1-a03-real-write.log | - | 05284977b5b9a22805471b5e6a47b17a19168a5fdfe8f413f651c16b32bdc192 | CANONICAL |
| EV-R4B-21 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/logs/mutation-1-restored-green.log | - | 3b7a7e23b34776ade3dd7b8142cfff838c75fc49d4d6f247cf004f6d0935427b | CANONICAL |
| EV-R4B-22 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/logs/mutation-1b-a03-assertion-removed.log | - | 64d60253dc04f001b6ba6de6a7cda8ee1065aca04e9cd43105856d8001ea4bdd | CANONICAL |
| EV-R4B-23 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/logs/mutation-2-ac3-adopt-target.log | - | a83977f686cdb3f5aa83a4aa2990a6ff82dad8a8f2e5cbba025f50078c369157 | CANONICAL |
| EV-R4B-24 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/logs/mutation-2-restored-green.log | - | 5332a3f6f362f20e8782677b8664393022213076f883816c7085b2df3ad126ec | CANONICAL |
| EV-R4B-25 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/logs/mutation-3-ac4-sink-removed.log | - | 3d5f7c0e3dfb369692503d33ed3b0025a49f8034b71951519c2fece9a3bced55 | CANONICAL |
| EV-R4B-26 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/logs/mutation-3-restored-green.log | - | 1b4e2fe64b8ff8f3ec556288f0e9220aabad56c1b2a28aaabbb6c0da82cba10f | CANONICAL |
| EV-R4B-27 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/logs/mutation-4-p1-appdata-isolation-removed.log | - | f102994cf666b4dc1c208431218d907726ca316a08aadf0070fa56b87bf94f0d | CANONICAL |
| EV-R4B-28 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/logs/mutation-4-restored-green.log | - | 273b3cc5710b3a2e8c81b944522551442f8652aceefb67a91e081d6aefa84886 | CANONICAL |
| EV-R4B-29 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/logs/mutation-4b-p1-redline-regression.log | - | 30ef875c862f1ebd3de5b65e21578fe2f802e3835f3462403a1afe0cf8767e6b | CANONICAL |
| EV-R4B-30 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/logs/mutation-5-r2-scalings-branch-hardcoded.log | - | 537af7b5f25bfef275f1637072b08889d8a982afe6e423e0c134b7a10e64cdf7 | CANONICAL |
| EV-R4B-31 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/logs/mutation-5-restored-green.log | - | ebd9a7b487073d0b41849c57e114037fbad5641b6941229545797a87939894bf | CANONICAL |
| EV-R4B-32 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/logs/pins.log | - | aedf5a6b579c255e4b1544ccc1479aaf8517d6cdd711f9e7a12018f08e6f118d | CANONICAL |
| EV-R4B-33 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/logs/pytest-r4b.txt | - | e65a83f5e4d26be88209775aecaec8efd27d1ec905aa9a73468fffefd506f905 | CANONICAL |
| EV-R4B-34 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/logs/startup-matrix-corrupt-appearance.log | - | 166bcafe2ff9eaaac7ca94da1e400304b6f73c7c1df92794d33cef03155bb44c | CANONICAL |
| EV-R4B-35 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/logs/startup-matrix-default.log | - | 252b8489c71b4fd73489d2b5b8be247a65156df4d35e31d2a5c46359d6687a64 | CANONICAL |
| EV-R4B-36 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/logs/startup-matrix-presentation-host.log | - | 4ed52f3ed419edb7060a8fde5e6f7149523344c15a8f8fc7e1aa258a33826a00 | CANONICAL |
| EV-R4B-37 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/logs/startup-matrix-shell-legacy.log | - | 9da3dfb4b056f634116a2e854603f8b53dd569d3cc304ef7907ff136aaba18c7 | CANONICAL |
| EV-R4B-38 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/logs/startup-matrix.log | - | e1c6737801ff665a5dceffc4e4386af787155a3f1f42ee86201f096d275ee01a | CANONICAL |
| EV-R4B-39 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/logs/startup-process-matrix-gated.log | - | 273b3cc5710b3a2e8c81b944522551442f8652aceefb67a91e081d6aefa84886 | CANONICAL |
| EV-R4B-40 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/mutation-selfcheck.md | - | 0cde329d155d17f0d7aeef4725054d6f2b725fe7c8cf61a9d6b0f4666259c1b9 | CANONICAL |
| EV-R4B-41 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/tools/backfill-fea07.py | - | 441f0dab1a2e300c0dd8921d2871ac3be5dec7b5c34b8f7acaf64c1f16a6c183 | CANONICAL |
| EV-R4B-42 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/tools/crash-switch.ps1 | - | 47fce57587b1953d7899181dd2e735fefa18cf73e4c09fcf875f729f7478c030 | CANONICAL |
| EV-R4B-43 | AC-R4b-4（证据） | verification/FEA-07-RESIDUAL-3/tools/startup-matrix.ps1 | - | e5884d25ebfc3a012f003a63ce9542e3866f7519c688fede7db481ace361bd1c | CANONICAL |
| EV-R4B-44 | Review 链 | doc/reviews/FEA-07-RESIDUAL-2-scope-r1.md | - | 8f549cabf0cea401e84a18366a00403aca36ce8c8b3a0843e4c7a93af03aec28 | CANONICAL |
| EV-R4B-45 | Review 链 | doc/reviews/FEA-07-RESIDUAL-3-r1.md | - | 4557430c85b8cf3f747665b45e09b5a61da5cf5d002cade60c992a2ac9c5dbcf | CANONICAL |
| EV-R4B-46 | Review 链 | doc/reviews/FEA-07-RESIDUAL-3-r2.md | - | f5f11b22e0597754fdac2e2ccef3ff98222a95b9a659b9a0a93f2a12b61bb7cd | CANONICAL |
| EV-R4B-47 | Review 链 | doc/reviews/FEA-07-RESIDUAL-3-r3.md | - | 03a2a5db8a218b7a46a3dd9c7d508156225b9d25809ad73cdd883e5dd0ba3594 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（main；base `852c6146c`，impl `8e9420f41`） | NOT_APPLICABLE | — | — | 未创建 linked worktree |
| temp | `G:\CODEX\New Manga.workspace\FEA-07-RESIDUAL-3\**`（gated 隔离数据根/崩溃驱动/启动矩阵） | PRESERVE_REFERENCED | `G:\CODEX\New Manga.workspace\FEA-07-RESIDUAL-3` | `verification/FEA-07-RESIDUAL-3/RESOURCE-MANIFEST.json` | 仓外隔离根；不触碰真实书籍/DB；保留供审计 |
| test-fixture | `tests/**` + gated fixtures | NOT_APPLICABLE | — | — | headless/临时根；无真实用户数据 |
| user-data | NOT_APPLICABLE（**例外已登记**） | NOT_APPLICABLE | — | — | 无真实书籍/DB 写入；真实 `%APPDATA%\com.newmanga.desktop\logs\window-material.log` 仅：①既有 D-R4b-7 每轮 +16 行（非本卡引入）②变异实验主动 +若干行（不删除、如实登记） |
| tracked-side-effect | `verification/FEA-09/logs/wire-redacted.ndjson` | NOT_APPLICABLE | — | — | 既有副作用；每次全量后 `git checkout -- verification/FEA-09` |
