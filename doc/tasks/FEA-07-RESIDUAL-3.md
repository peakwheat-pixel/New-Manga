---
id: FEA-07-RESIDUAL-3
title: FEA-07 收口 B（AC1 gated 真库 A03/ACK + AC3 跨进程崩溃 + AC4 真实入口/诊断 sink/矩阵）
kind: implementation
governance_version: 3
status: ready
approval: 用户 2026-11-08 残余收口指令（R4）；scope 依据 = 独立 scope review `doc/reviews/FEA-07-RESIDUAL-2-scope-r1.md` §3/§4/§5.2（该评审已逐项覆盖 AC1/AC3/AC4 并给出最小方案与风险）；DSH 2026-11-08 裁决（ADJ §7.13）：0 pin、gated/进程级
suggested_owner: dsh
owner: fea07-residual3-impl
reviewer: 独立上下文 fresh subagent（不得由实现会话/实例自审）
depends_on:
  - FEA-07-RESIDUAL-2
base_commit: 8855baaac
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
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

- [ ] **AC-R4b-1（AC1 A03 真库 + ACK/Intent）**：gated（默认 skip + reason）真实 Host/Core：≥50 次前端往返切换前后，真实 `library.db` 的 `regions.text_json`、`current_revision_id`、`translation_locked`/`inpaint_locked`/`sfx_locked`、manual 位、`region_revisions` 行数、`region_candidates` 行数**逐列相同**（内嵌 Python 读库，**不引入 `Microsoft.Data.Sqlite`**）；ACK 丢失/重连同 idempotency key 只产生 1 个 run、旧结果仅 candidate；真实 Run/Intent 链路经生产 dispatcher。 <<MET>>
- [ ] **AC-R4b-2（AC3 跨进程崩溃注入）**：外部驱动 `progress`：production 路径在 `beforeJournalCommit`（或 staging Loaded/Rendered）park → **独立进程** `GetProcessById().Kill(entireProcessTree:true)` 并断言真死（exit code 语义显式）→ **新进程** recover：终态 `RolledBack`、frontend=上一已提交、`appearance.FrontendId` 未被 target 污染、二次恢复零变化；「暂停期保护状态」两条断言（切换零写保护列 + 恢复采用最新状态、不回写旧快照）；**禁止** `Environment.FailFast`/同进程冒充/生产 backdoor。 <<MET>>
- [ ] **AC-R4b-3（AC4 真实入口 + 诊断 sink + 矩阵）**：新增最小 `StartupDiagnostics`（`App/Services/StartupDiagnostics.cs` + `App.axaml.cs` ≤5 行接线，写 `<log-dir>/startup.log`）；真实进程 4 组参数（默认 / `--presentation-host=true` / `--shell=legacy` / 坏外观文档）→ `exit_code=0`、无 `fatal.log`、`startup.log` 含对应诊断行；**9 类 warning 逐项** fail-safe（坏 JSON / schemaVersion / corners.scale / appearance.mode / contrast / motion.mode / motion.categories / frontendId / visualThemeId）→ planner 强制 Current V2。 <<MET>>
- [ ] **AC-R4b-4（证据/治理/翻转）**：EV/Resource Manifest/门禁日志；`FEA-07` AC1/AC3/AC4 **append-only** 回填（`[x] <<MET>>` 不带原因）+ 关账；`check.ps1` PASS、pins 18/18（0 pin）、全量 .NET 不降、pytest 既有 flaky 登记不恶化；`FEA-07` 翻 `done` 后 **4 节点全部 done**。 <<MET>>

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
