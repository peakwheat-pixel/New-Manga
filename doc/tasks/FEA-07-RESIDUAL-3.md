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
