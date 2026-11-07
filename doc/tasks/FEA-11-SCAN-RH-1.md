---
id: FEA-11-SCAN-RH-1
title: SCAN-2 复核残余收口：refresh pending 重放 + refresh 生命周期绑定（Host-only，0 pin）；RH-3/RH-4/RH-5 口径登记
kind: implementation
governance_version: 3
status: proposed
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH，无需用户介入」；独立 scope review `doc/reviews/FEA-11-SCAN-RH-scope-r1.md`（fresh subagent session `c50bc2b0…`；verdict **recommended**：一张 Host-only 小卡，0 pin）；**DSH 裁决（2026-11-07）**：采纳 D-1 重放修复 / D-2 允许 SCAN-2 卡 append-only limitation 订正 / D-3 单卡 `FEA-11-SCAN-RH-1` / D-4 RH-3/RH-5 仅登记；**待 L-R11 实现收口后释放**
suggested_owner: zcode
owner: null
reviewer: null
depends_on:
  - FEA-11-SCAN-2
  - FEA-11-WATCH-1
base_commit: a969f405f
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-SCAN-RH-1
allowed_paths:
  - doc/tasks/FEA-11-SCAN-RH-1.md
  - doc/reviews/FEA-11-SCAN-RH-1-*.md
  - doc/handoffs/FEA-11-SCAN-RH-1-*.md
  - verification/FEA-11-SCAN-RH-1/**
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceScanSchedulerTests.cs
  - doc/tasks/FEA-11-SCAN-2.md
out_of_scope:
  - RH-3 的 target 清理 / RemoveTarget / `_targets` 收缩；Core 侧「源已删除」信号（C-17 additive）
  - RH-5 的 fake-Core seam / HostOptions 注入点 / sidecar bundle 升级 / CI fixture
  - 大库冷启动预算标定、folder/encrypted 导入 E2E、L-S1、L-S4、L10、AC11-1
  - 契约字节（C-17 v1.1 / C-16 v1.7 / C-15 / C-06 / M2-C1 / ADJ-001）、schema/wire/命令/能力/错误码/`PROTOCOL_MINOR`、依赖
  - App/UI、WATCH-1 done 卡字节、SCAN-2 的 AC 判词与 EV 行（仅允许 append-only limitation 一行）
  - STATUS/REBASELINE_PLAN/TASK_LEDGER（Lead 维护）；push（Lead 统一）
---

# FEA-11-SCAN-RH-1：SCAN-2 复核残余收口（Host-only，0 pin）

> **状态：`proposed`（DSH 已裁决采纳 scope review 推荐；待 `FEA-11-L-R11-GATE-UNIFY-1` 收口后释放）。**
> 依据：`doc/reviews/FEA-11-SCAN-RH-scope-r1.md`（recommended；RH-1…RH-5 事实表与卡面草案 §3.3）+
> `doc/tasks/FEA-11-SCAN-2.md:252`（RH-1…RH-5 原始登记）。

## 目标

修 **RH-1**（refresh 在途时第二次 Refresh 只在下一次 tick 重放 → 延迟最多 900 s）与 **RH-2**（refresh 用
`CancellationToken.None`、停机不取消不 join → `ObjectDisposedException` 逃逸日志）；**RH-4** 做文档口径订正；
**RH-3/RH-5 仅登记 limitation**（不实现）。全部 Host 进程内，**0 pin、无 UNFREEZE**。

## Acceptance Criteria（冻结时定稿；依据 scope review §3.3）

- [ ] **AC-RH-1（RH-1 重放修复）**：`RefreshTargetsAsync` 在完成一次枚举并释放单飞闸门后（成功或 typed unavailable；
  被取消/已 disposed 的提前返回不重放），若 `_refreshPending` 为真则**重放一次**；重放有界（每 pass 至多一次、不递归）；
  `TickAsync` 既有重放语义与顺序（refresh 在 hint 之前）不变；XML 注释改为 "coalesced and replayed after the
  in-flight pass"。判别性：refresh 在飞时第二次 refresh → 第一次完成后立即第二次枚举并合并新 target（不调用
  `TickAsync`）；删重放 → 红。 <<PENDING>>
- [ ] **AC-RH-2（RH-2 lifetime 绑定 + 停机 join）**：scheduler 内持有 lifetime CTS；枚举 token 与调用方 token、
  lifetime token link；`DisposeAsync` 先取消 lifetime、再有界 join 在飞 refresh（与 hint pass 同口径，建议 ≤2 s），
  随后才 `_tickGate.Dispose()`；不得出现 `ObjectDisposedException` 逃逸日志。判别性：枚举阻塞 + Dispose →
  枚举观察取消、Dispose 有界完成、无 ObjectDisposed 日志；改回 `CancellationToken.None` 且不 join → 红。 <<PENDING>>
- [ ] **AC-RH-3（RH-4 文档订正，零代码）**：本卡 limitation 与 `FEA-11-SCAN-2.md` closeout limitation（**append-only
  一行**）写清三套表集与并集（Core 14 表 / Host 15 表 / C-17 §6.2 派生 16 表；并集 17 表；与 16 表基线相比缺
  `pipeline_runs`/`pipeline_run_targets`/`step_result_candidates`，多 `books`/`chapters`/`sources`/`book_cleanup_manifests`）；
  **禁止**写「满足 C-17 §6.2 零写基线」或「全库零写」。判别性：文档核对。 <<PENDING>>
- [ ] **AC-RH-4（RH-3/RH-5 登记）**：limitation 逐条写明 RH-3（只增不减、无删除 API、Skipped 无 backoff、预算稀释
  `(N+live)/8`、watch 每次 Sync 的 uncovered WARN、**枚举省略≠删除**、清理需 C-17 变更 Out）与 RH-5（时钟 seam 存在
  `HostOptions.cs:111-112`、无 fake-Core seam、canonical 全量日志 gated 用例 SKIP、EV-09 不能判别非阻塞、
  WATCH-1 卡 `:111/:129/:199/:213` 的「无注入时钟」按本卡口径订正理解但**不改其字节**）。判别性：文档核对。 <<PENDING>>
- [ ] **AC-RH-5（门禁/证据/不夸大）**：定向 `--filter "FullyQualifiedName~SourceScan"`（起点 **68 passed/0/0**）与
  `~SourceWatcher`（起点 **19 passed/0/0**）+ 新增用例全绿；全量 .NET **1680/0/96 不降**（跑后
  `git checkout -- verification/FEA-09`）；全量 pytest **3363/10 不降**；`check.ps1` PASS；`verify_pins.ps1` **18/18**；
  scope diff ⊆ `allowed_paths`；EV 逐条可复算。**禁止**表述为「RH-3 已清理 / RH-5 已补 seam / SCAN-2 残余已全部解决」。 <<PENDING>>

## 依赖与下一步

- 依赖：`FEA-11-SCAN-2`（done）、`FEA-11-WATCH-1`（done）；释放等 `FEA-11-L-R11-GATE-UNIFY-1` 收口（避免并发
  `HostRuntime.cs` 写域冲突——L-R11 为 Core-only，实际不冲突，仅排期）。
- Release 后走：实现 → 独立 Review（fresh subagent，复跑判别性与门禁）→ closeout → push。
