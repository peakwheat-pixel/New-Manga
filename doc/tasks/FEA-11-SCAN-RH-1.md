---
id: FEA-11-SCAN-RH-1
title: SCAN-2 复核残余收口：refresh pending 重放 + refresh 生命周期绑定（Host-only，0 pin）；RH-3/RH-4/RH-5 口径登记
kind: implementation
governance_version: 3
status: ready
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH，无需用户介入」；独立 scope review `doc/reviews/FEA-11-SCAN-RH-scope-r1.md`（fresh subagent session `c50bc2b0…`；verdict **recommended**：一张 Host-only 小卡，0 pin）；**DSH 裁决（2026-11-07）**：采纳 D-1 重放修复 / D-2 允许 SCAN-2 卡 append-only limitation 订正 / D-3 单卡 `FEA-11-SCAN-RH-1` / D-4 RH-3/RH-5 仅登记；**已于 2026-11-08 释放（L-R11 收口后）**
suggested_owner: zcode
owner: scan-rh-impl
reviewer: null
depends_on:
  - FEA-11-SCAN-2
  - FEA-11-WATCH-1
base_commit: a969f405f
branch: null
worktree: null
integration_commit: null
delivery_head: fb74b4ef7
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

- [x] **AC-RH-1（RH-1 重放修复）**：`RefreshTargetsAsync` 在完成一次枚举并释放单飞闸门之后（成功或 typed unavailable；被取消/已 disposed 的提前返回不重放），若 `_refreshPending` 为真则重放一次；重放有界（每 pass 至多一次、不递归）；`TickAsync` 既有重放语义与顺序（refresh 在 hint 之前）不变；`RefreshTargetsAsync` 的 XML 注释改为 "coalesced and replayed after the in-flight pass"。判别性：refresh 在飞时第二次 refresh → 第一次完成后立即第二次枚举并合并新 target（不调用 `TickAsync`）；删重放 → 红。 <<MET>>
- [x] **AC-RH-2（RH-2 lifetime 绑定 + 停机 join）**：scheduler 内持有 lifetime CTS；枚举 token 与调用方 token、lifetime token link；`DisposeAsync` 先取消 lifetime、再有界 join 在飞 refresh（与 hint pass 同口径，建议 ≤2 s），随后才 `_tickGate.Dispose()`；不得出现 `ObjectDisposedException` 逃逸日志。判别性：枚举阻塞 + Dispose → 枚举观察取消、Dispose 有界完成、无 ObjectDisposed 日志；改回 `CancellationToken.None` 且不 join → 红。 <<MET>>
- [x] **AC-RH-3（RH-4 文档订正，零代码）**：本卡 limitation 与 `FEA-11-SCAN-2.md` closeout limitation（**append-only 一行**）写清三套表集与并集（Core 14 表 / Host 15 表 / C-17 §6.2 派生 16 表；并集 17 表；与 16 表基线相比缺 `pipeline_runs`/`pipeline_run_targets`/`step_result_candidates`，多 `books`/`chapters`/`sources`/`book_cleanup_manifests`）；**禁止**写「满足 C-17 §6.2 零写基线」或「全库零写」。判别性：文档核对。 <<MET>>
- [x] **AC-RH-4（RH-3/RH-5 登记）**：limitation 逐条写明 RH-3（只增不减、无删除 API、Skipped 无 backoff、预算稀释 `(N+live)/8`、watch 每次 Sync 的 uncovered WARN、**枚举省略≠删除**、清理需 C-17 变更 Out）与 RH-5（时钟 seam 存在 `HostOptions.cs:111-112`、无 fake-Core seam、canonical 全量日志 gated 用例 SKIP、EV-09 不能判别非阻塞、WATCH-1 卡 `:111/:129/:199/:213` 的「无注入时钟」按本卡口径订正理解但**不改其字节**）。判别性：文档核对。 <<MET>>
- [x] **AC-RH-5（门禁/证据/不夸大）**：定向 `--filter "FullyQualifiedName~SourceScan"`（起点 **68 passed/0/0**）与 `~SourceWatcher`（起点 **19 passed/0/0**）+ 新增用例全绿；全量 .NET **1680/0/96 不降**（跑后 `git checkout -- verification/FEA-09`）；全量 pytest **3363/10 不降**；`check.ps1` PASS；`verify_pins.ps1` **18/18**；scope diff ⊆ `allowed_paths`；EV 逐条可复算。**禁止**表述为「RH-3 已清理 / RH-5 已补 seam / SCAN-2 残余已全部解决」。 <<MET>>

## Limitation（RH-3/RH-4/RH-5 登记；本卡不实现）

- **RH-4（零写表集口径；文档订正，零代码）**：SCAN-2 的「零写」快照存在**三套互不等的表集**：
  Core 分片 **14 表**（`tests/core/test_core_scan_target_commands.py:44-59`：`books`/`chapters`/`pages`/`page_bindings`/
  `sources`/`source_locations`/`source_versions`/`source_entries`/`source_sync_plans`/`source_operations`/
  `source_binding_publications`/`source_revision_lineage`/`book_cleanup_manifests`/`reading_progress`）；
  Host 分片 **15 表**（`verification/FEA-11-SCAN-2/host-cold-start.json:15-32`：Core 的 12 表子集 +
  `regions`/`region_revisions`/`rendition_cache`，不含 `reading_progress`/`book_cleanup_manifests`；
  `host-r2-cold-start.json` 同口径）；C-17 §6.2 派生 **16 表**基线（`tests/fea11/test_source_sync.py:588-606`）。
  **Core 14 ∪ Host 15 = 17 表**；相对 16 表基线**缺** `pipeline_runs`/`pipeline_run_targets`/`step_result_candidates`，
  **多** `books`/`chapters`/`sources`/`book_cleanup_manifests`。因此 AC-S2-8 的零写只覆盖 Core∪Host **17 表**，
  **不等于**「满足 C-17 §6.2 零写基线」，**不构成**「全库零写」；本卡**禁止**任何文档写这两种表述。订正落点：本段 +
  `doc/tasks/FEA-11-SCAN-2.md` closeout limitation 的 append-only 一行；SCAN-2 原 AC 判词与 EV 行字节未改。
- **RH-3（targets 只增不减；不修，仅登记）**：`_targets` 只有 `RegisterTarget` 覆盖写与 `MergeTargetsLocked` 的
  add/update，**无 `RemoveTarget`/删除 API**；撤销 root（`source_revoke_root`）后条目仍保留（`SourceAccessRegistry.Revoke`
  只 bump generation + `RevokedAt`），每轮转重试为 typed skip 且 `ApplyOutcome` 对 `Skipped` **不设 backoff**（永久占用
  每 tick `MaxTargetsPerTick`（默认 8）预算；N 个 stale 时 live 源扫描周期约放大约 `(N+live)/8` 倍）；watch 每次 Sync
  对每个 stale target 打一条 `source watch uncovered` WARN。**关键陷阱：Core 枚举省略 ≠ 源已删除**——Core 会因 missing
  location facts / 未知 kind / `project_ids` 0 或 >20 而合法省略；Host 若按「不在本次枚举结果里就删」清理会静默丢
  target。正确清理需 Core 侧显式「已删除」信号（C-17 additive）→ **Out，未实现**。
- **RH-5（证据强度/门禁覆盖；仅登记）**：时钟 seam **存在**——`HostOptions.SourceScanTimeProvider`
  （`HostOptions.cs:111-112`，默认 `TimeProvider.System`）已注入 scheduler loop/executor/watcher/identity cache；缺的是
  **fake-Core seam**——`HostRuntime` 内部直接 `new` 具体 `HostSourceScanExecutor`/`HostSourceScanTargetEnumerator`
  （`HostRuntime.cs:1382-1403`），`HostOptions` 无注入口，HostRuntime 级「成功枚举 / Ready 非阻塞」只能靠 gated 真 IPC；
  canonical 全量 .NET 日志中这些 gated 用例**全部 SKIP**（`verification/FEA-11-SCAN-2/logs/host-r2-dotnet-full-3.log:105`
  等 4 份）；EV-09 来自 fixture 可用环境的单独运行（`host-r2-runtime-enumeration.log`：1 passed），
  `enumeration_present_immediately_after_start=true` **不能**判别「非阻塞」。WATCH-1 卡 `:111/:129/:199/:213` 的
  「HostRuntime seam 无 fake-Core/注入时钟」按本卡口径订正理解（时钟 seam 存在，缺的是 HostRuntime 级 fake-Core/枚举器
  注入口），**不改其任何字节**。本卡**未**补 fake-Core seam、未升级 sidecar bundle、未改 CI fixture。

## 依赖与下一步

- 依赖：`FEA-11-SCAN-2`（done）、`FEA-11-WATCH-1`（done）；释放等 `FEA-11-L-R11-GATE-UNIFY-1` 收口（避免并发
  `HostRuntime.cs` 写域冲突——L-R11 为 Core-only，实际不冲突，仅排期）。
- Release 后走：实现 → 独立 Review（fresh subagent，复跑判别性与门禁）→ closeout → push。

## 交付记录（Owner 回填；不改 status）

- **交付完成（2026-11-08）**：`delivery_head=fb74b4ef7`；commit 链 `938d598ac`（实现 `SourceScanScheduler.cs`：
  RH-1 refresh pending 重放 + RH-2 lifetime CTS/link/Dispose 有界 join；`HostRuntime.cs` **零 diff**）→ `fb74b4ef7`
  （测试 `SourceScanSchedulerTests.cs`：3 个新用例 + `FakeTargetEnumerator` 扩展）。随后同批 docs/evidence 提交
  （本卡面 / `doc/tasks/FEA-11-SCAN-2.md` append-only 一行 / Handoff / `verification/FEA-11-SCAN-RH-1/**`）。
  实施起点实测 `d09e91d1d`（Lead 的 docs-only 释放提交；派发说明给定交付基准 `ffcfab050`，卡面 front matter
  `base_commit=a969f405f` 为冻结时点、早 8 个提交），实现/测试提交落在 `d09e91d1d` 之上。
- **AC 判定**：AC-RH-1…AC-RH-5 **全 MET**（逐项行末 `<<MET>>`；证据见 `verification/FEA-11-SCAN-RH-1/EV.md`）。
- **实跑门禁（before → after）**：Release build **0 warning / 0 error**；定向 `--filter "FullyQualifiedName~SourceScan"`
  **68/0/0 → 71/0/0**（+3 新用例）、`~SourceWatcher` **19/0/0 → 19/0/0**（不回归）；全量 .NET
  **1680/0/96 → 1683/0/96**（+3、0 failed、skip 不变；跑后 `git checkout -- verification/FEA-09` 已复原）；全量 pytest
  **3369 passed/10 skipped → 3369/10**（不降；Python 零改动）；`verify_pins.ps1` **18/18**；`check.ps1` 默认 +
  `-TaskPath` **PASS(3 warnings)×2**；API inventory **EXIT=0**；scope：`git diff d09e91d1d..<交付>` 仅
  `SourceScanScheduler.cs` + `SourceScanSchedulerTests.cs` + 本卡 allowed 的 docs/evidence；`HostRuntime.cs` /
  `doc/contracts` / `src/**` / schema / 依赖 **0 字节**（详见 EV §4）。以派发基准 `ffcfab050` 计，额外 1 个路径
  `doc/handoffs/DSH-HANDOFF-2026-11-06.md` 属 Lead 的 `d09e91d1d`（docs-only 释放提交），**非本卡写入**。
- **判别性**：**2/2 RED_AS_EXPECTED + 复原 sha256 2/2 MATCH + 复绿**（RH-1 删重放 → 2 用例 RED；RH-2 改回 caller
  token / 不 cancel lifetime / 不 join → Dispose 用例 RED；固定实现备份 sha256 `6b77d9ca…`，逐字节复原 MATCH 后
  3/3 复绿；`verification/FEA-11-SCAN-RH-1/logs/discriminative/**`）。
- **Limitation 保留（如实登记，不实现）**：**RH-3**（targets 只增不减、无删除 API、Skipped 无 backoff、预算稀释
  `(N+live)/8`、watch 每次 Sync 的 uncovered WARN、**枚举省略≠删除**、清理需 C-17 additive → **Out，未实现**）；
  **RH-4**（三套表集 Core 14 / Host 15 / C-17 派生 16，并集 17，相对 16 表基线缺 3 多 4；已在本文 limitation +
  `FEA-11-SCAN-2.md` append-only 一行订正；**禁止**写「满足 C-17 §6.2 零写基线」「全库零写」）；**RH-5**（时钟 seam
  `HostOptions.cs:111-112` 存在、无 fake-Core seam、canonical gated 用例 SKIP、EV-09 不能判别非阻塞、WATCH-1 卡
  `:111/:129/:199/:213` 按本卡口径订正理解但**不改其字节**）。
- **不夸大**：本卡**未**清理 RH-3、**未**补 fake-Core seam、**未**解决 SCAN-2 全部残余；RH-1/RH-2 仅指本卡实现的
  refresh pending 重放与 refresh 生命周期绑定（不是 SCAN-2 全部残余的修复）。证据/Handoff 已给出，**实现 ≠ 集成**，
  待独立 Review 与 Lead 集成门禁。
- **证据目录**：`verification/FEA-11-SCAN-RH-1/`（`EV.md`、`RESOURCE-MANIFEST.json`、`logs/**`）。未 push、未建
  worktree；`status` 未改（由 Lead 维护）；未自行 closeout；未创建 STATUS/PLAN/LEDGER 变更。
