---
id: FEA-11-SCAN-1
title: FEA-11 源后台定时扫描（Host 进程内只读周期触发切片）
kind: implementation
governance_version: 3
status: in_review
approval: scope 已按 ZCode SCOPE-ADJ-2026-11-05 冻结，**DSH 2026-11-06 释放（ready）**：承接 FEA-11 AC11-1 的「定时扫描生产者」延期项（L-3 半边）；释放时由 DSH 固定 base_commit、Owner 与上下文独立 Reviewer
suggested_owner: codex
owner: fea12-core-host
reviewer: null
depends_on:
  - FEA-11
base_commit: e0c370870   # 释放点 main head（MATCH-1 交付后）
branch: null
worktree: null
integration_commit: null
delivery_head: 7080167e1   # r2 返修 commit（含证据重签/卡/Handoff）；r1 实现 73d01fd2b
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-SCAN-1
allowed_paths:
  - doc/tasks/FEA-11-SCAN-1.md
  - doc/reviews/FEA-11-SCAN-1-*.md
  - doc/handoffs/FEA-11-SCAN-1-*.md
  - verification/FEA-11-SCAN-1/**
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanStatus.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostOptions.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/SourceImportModels.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/NullHostController.cs
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/ImportDockViewModel.cs
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/LibraryViewModel.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceScanSchedulerTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11ScanIpcTests.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/FakeHostController.cs
out_of_scope:
  - Core 侧调度器线程（src/application/sources/scheduler.py 等）：Core 无路径/无 project_ids/无 grant 铸造权，不可实现
  - 正式目录 watcher（FileSystemWatcher 生产者/消费者）：登记 FEA-11-WATCH-1
  - 冷启动全源目标枚举：登记 FEA-11-SCAN-2（需 Core 读命令或 Host 持久索引 + 契约/架构裁决）
  - 通知表/attention 状态/扫描结果持久化；新 Core 命令/capability/DTO/wire/schema/迁移
  - 自动建 plan / preview / confirm / apply / relink / repoint / resync / tombstone / 删除 / GC / 清理
  - UI 状态条/设置项/settings section/App 可见呈现（后续切片）
  - C-17/C-16/C-15/C-09/C-14/M2-C1/ADJ-001/FEA-01 任何字节；18 pins；IHostController/C-07 冻结面
  - 真实用户数据/AppData/外部卷/回收站；push；新依赖
---

# FEA-11-SCAN-1：源后台定时扫描（Host 进程内只读周期触发切片）

> **状态：`in_review`（2026-11-06 实施完成；r1 Review `changes_requested` 后已完成 r2 最小返修，待窄面复审）。本卡 scope 已按 ZCode SCOPE-ADJ-2026-11-05 冻结；方案 A = Host 侧只读周期触发切片（不做 Core 定时器、不做 watcher、不做通知持久化、不做自动 plan/apply）。**
>
> 范围事实基线：`main@e0c370870`（释放点）；r1 实施时 HEAD `869b6d5d5`（其间无 `apps/desktop-avalonia` 改动）；r1 交付 `73d01fd2b`（reviewed_head `a684c511d`）。r2 返修处置见「r1 Review 处置」；实现/证据 commit 见交付记录与 Handoff。

## 来源与目标

- 承接链：`doc/tasks/FEA-11.md:103` AC11-1（四路变化检测：启动/访问前检查、操作前强验证、目录 watcher 生产者、定时扫描）；`doc/reviews/FEA-11-r7-acceptance.md:20` L-3（定时扫描 + watcher 缺失）；`doc/tasks/FEA-11.md:139` DSH 裁决。
- 冻结依据：`G:\CODEX\New Manga.workspace\FEA-11\scope-review\FEA-11-SCAN-1-scope.md`（独立只读 scope review）+ ZCode SCOPE-ADJ-2026-11-05 裁决（Lead 2026-11-05 下发；含每卡必改项）。
- 已具备能力（复用，不重写）：`ScanSourceSync` 全链（`src/application/sources/scanner.py`；真实 IPC 测试 `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11SourceIpcTests.cs:143-190`）、Host grant 铸造/registry（`SourceReadCoordinator`、`SourceAccessRegistry`）、读取时强验证（`_resolve_grants` + strict read）。按需 scan 已实现但**无生产调用方**；启动扫描与 watcher 均未落地。
- 目标（一个可观察交付）：应用运行期间，对**本会话成功导入过的源**按固定周期（默认 900s）执行一次**只读** `ScanSourceSync` 全量重枚举；结果只落 Host 内存状态（`HostRuntime.SourceScanStatus` closed record）+ 脱敏日志，使“源已在外部变化”成为可诊断状态。**不写 Core DB、不建 plan、不 apply、不产生用户可见呈现。**
- 诚实口径：本卡是基础设施/可观测性切片，不是“同步完成”；用户看到“源已变化”须等后续 UI 切片消费 Host 状态。本卡 done 后 **AC11-1 仍为 PARTIAL**（只闭合“定时扫描”半边；watcher/启动扫描仍缺）。

## Scope（冻结）

### In（方案 A）

| # | 范围项 | 冻结说明 |
|---|---|---|
| I-1 | Host 侧单实例周期调度器 | 新增 `SourceScanScheduler`（`NewManga.Host/Sources/`）：`Start/Stop/Pause/Resume` 幂等；默认 enabled=true、间隔 900s；可注入 `TimeProvider`/`now` 与手动 `TickAsync()`；独立 `Task` + `CancellationToken`，生产用 `Task.Delay(interval, timeProvider, token)`；测试**零 sleep**；Host 已由 `SingleInstanceGuard` 全局互斥，不加第二把 lease |
| I-2 | 扫描目标注册（App → Host） | App 在引用导入进入终态 **`Completed`（成功）** 后注册 `(source_id, path, kind=resync, project_ids[1], version)`；按 `source_id` **覆盖**而非追加；目标集**仅内存**（重启后为空，L-A）；不猜 `source_id`/路径，全部来自导入链路与用户选择；`bookId` 由 `LibraryViewModel` 经 `ImportDockViewModel` 提供（`project_ids=[bookId]`） |
| I-3 | 单飞与去重 | 同一 `source_id` 同一时刻最多 1 个在飞扫描；重叠 tick 合并（不排队堆积）；tick 内串行；调度器**只调用** `ScanSourceSync`，绝不调用 plan/preview/confirm/apply/relink/repoint/resync |
| I-4 | 预算与退避 | 每 tick 目标数上限（默认 8）、每源大小上限（默认 256 MiB；folder 用成员数上限；估算用 `FileInfo`/registry 事实）可注入；超限目标**顺延**下一 tick 并记 `deferred`（不算失败）；typed 失败指数退避 `min(60×2^n, 3600)` 秒、成功清零；`CORE_CAPABILITY_MISSING`/`HOST_ONLY_REQUIRED`/`INVALID_REQUEST` → 停用调度器（fail-closed），不重试 |
| I-5 | 全量重枚举 | 每 tick 对每个目标做完整 `ScanSourceSync`（不依赖任何增量 hint）；这同时是“丢 hint/overflow 兜底”的正确性实现（FEA-00 `:442`：通知可能丢失，不能作为唯一真值） |
| I-6 | Host 内状态快照 + 脱敏日志 | `HostRuntime.SourceScanStatus`（in-process closed record）：`{enabled, interval_seconds, paused, last_tick_at?, next_tick_at?, targets:[{source_id, last_scan_at?, last_result?, counts?, deferred?}], recent[≤50]}`；`last_result ∈ {ok, changed, missing, unsupported, denied, error}`；`deferred` 只表示本 tick 因预算顺延（不是扫描结果）；**不新增 wire 命令**；日志只含 `source_id`/计数/错误 code，无绝对路径/grant/session/异常原文/凭据 |
| I-7 | 生命周期接线 | 在 `HostRuntime.StartInternalAsync` 的 host-control 会话与 `Sources` 就绪、`Result.IsReady` 后创建；`DisposeAsync`/`StopSidecarsAsync` 停止并 join；仅在 `ReferencedImportEnabled` 时运行；Core 会话失效 → `paused`，不自行重开 host session（会话管理只归 `HostRuntime`） |
| I-8 | 证据与回归 | 隔离 fixture 在 `G:/CODEX/New Manga.workspace/FEA-11-SCAN-1/`；1 条真实 IPC（真实 Python Core + 真实 zip + 隔离 DataRoot）；`dotnet test` 全量不减少；pins 18/18；范围 0 域外；无新依赖 |

### Out（明确不做）

| # | 不做项 | 理由（事实） |
|---|---|---|
| O-1 | Core 侧调度器线程（草案 `src/application/sources/scheduler.py`） | Core 无源路径、无 `project_ids`、无 grant 铸造权（grant 只能 Host 在 host-control 会话内签发，TTL ≤ 300s）→ 每 tick 都会 typed 失败 |
| O-2 | 目录 watcher（`FileSystemWatcher`）生产者/消费者 | 需 C# 实现 + 去抖/overflow 语义 + 新 hint 通道；本卡全量重枚举已覆盖“丢 hint”的正确性语义 → 登记 `FEA-11-WATCH-1` |
| O-3 | 通知表 / attention 状态 / 扫描结果持久化 | 无 notifications/attention 表、无 C-17 通知 DTO/命令；Scan 只活在内存 live-scan（TTL 300s）；持久“待确认”只能自动建 plan（等于代用户决策） |
| O-4 | 自动建 plan / preview / confirm / apply / relink / repoint / resync | 违反 C-17 §3.1 状态机与 §6 CAS；扫描必须保持零写 |
| O-5 | 自动删除 / tombstone / 回收站 / GC / 清理 | ADJ-001 PD-06/PD-07、C-14 SC-S07；本卡零删除 |
| O-6 | 新 Core 命令 / 新 capability / C-17/C-16/C-15 任何字节 | 复用已冻结 `ScanSourceSync` 与 `source.sync.scan/1` + `source.read/1`；方案 B 才需契约变更 |
| O-7 | schema / migration / 新依赖 | 无表变更；测试用内置 `TimeProvider` + 手写 fake，不引入 `Microsoft.Extensions.TimeProvider.Testing` |
| O-8 | UI / App 状态条 / 设置项 / `settings_update_section` 新 section | UI 后续切片；P15 §7 键域冻结，新增 scan section 需另立契约 |
| O-9 | 真实用户数据 / AppData / 外部卷 / 回收站 / push | 硬边界 |
| O-10 | 冷启动全源枚举 | 需新 Core 读命令（`source_id`↔`project_ids`）或 Host 持久目标索引 → 登记 `FEA-11-SCAN-2`（L-A） |

### 卡内冻结配置与状态面（防止实施歧义）

1. **默认值与覆盖**：`enabled=true`；`interval=900s`；`HostOptions.SourceScanIntervalSeconds`（或等价的 `SourceScanEnabled`/`SourceScanLimits` init 属性）可由环境变量 `NEWMANGA_SOURCE_SCAN_INTERVAL_SECONDS` 覆盖；合法范围 `[60, 86400]`；非法值（0/负数/非整数/超界）→ **回落 900s + WARN 日志**（fail-safe，不让 Host 启动失败）。**不新增 settings section**（`settings_update_section` 不扩）。
2. **目标注册键**：`(source_id, path, kind='resync', project_ids=[bookId], version)`；`version` 沿用导入 grant 的 `scope.version`（当前生产导入为 `"1"`）；`registry_id/generation` 由 Host 按 `path` 从 `SourceAccessRegistry.List()` 精确匹配解析（不猜、不推断；匹配失败 → 该目标本轮失败并按 AC-S3 typed 处理）。注册接口经既有 FEA-09-UI-1 独立接口族（`ISourceImportController`/`HostController`/`NullHostController`）落地，**不改 `IHostController`（C-07 冻结面）**。
3. **每 tick 顺序**：解析 registry/目标 → 预算筛选（deferred）→ 逐目标铸造 grant（`SourceReadCoordinator.IssueAsync`）→ `CoreServiceClient.SendHostControlAsync("ScanSourceSync", payload, timeout, HostSession, ct)` → 更新内存状态/日志 → 退避记账。tick 内串行。
4. **状态面**：只经 in-process 属性暴露，不登记 `HostCommandRegistry`、不新增 wire；状态结构为 closed record（字段见 I-6）；重启后 `targets`/`recent` 清空（L-A/L-C）。
5. **日志脱敏**：只允许 `source_id`、结果枚举、计数、typed code；禁止绝对路径、`source-` grant id、`host_session`、异常 `Message`/堆栈、凭据。
6. **零写**：调度器只发 `ScanSourceSync`；断言 fake core 每 tick 收到的命令集合**精确等于** `{ScanSourceSync}`（不含 `PlanSourceSync`/`Preview*`/`Confirm*`/`Apply*`/`Relink*`/`Repoint*`/`Resync*`/`Acknowledge*`/`Recover*`）。

### Appointment 说明（冻结，写入本卡即为范围依据）

- **SC-B08 窄裁定**：`doc/plan/FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md:146-153` 的“不得由 Host 独立起定时器（避免双 scheduler）”**仅约束自动备份等 Core 业务写**，不约束本卡的 Host 侧**只读**扫描触发；`C-09` 字节不动，不新增第二套调度语义。本裁定仅限本卡范围，不得引申为 Host 可发起任何业务写/自动 apply。
- **C-07/接口**：本卡**不改** `apps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs`、`RunContracts.cs`、`doc/plan/FEA-C07_API_INVENTORY.md` 或任何 pinned 契约字节。scope review §8.2 中列出的 `IHostController.cs` 系路径笔误：实际被扩展的是 FEA-09-UI-1 先例的**独立接口** `ISourceImportController`（`SourceImportModels.cs`）；`generate_api_inventory.py --check` 必须 PASS（门禁），18 pins 维持 18。
- **AC11-1 口径**：本卡 done 后 AC11-1 仍为 **PARTIAL**，只把“定时扫描”从 L-3 移出；watcher（`FEA-11-WATCH-1`）与启动扫描（`FEA-11-SCAN-2`）仍缺，不得在卡/Handoff/STATUS 宣称 AC11-1 全绿。
- **UI 边界**：本卡无用户可见入口；App 仅在导入成功后注册目标。状态读取留待后续 UI 切片。

## Acceptance Criteria

- [x] **AC-S1 调度器生命周期与配置（Host）** <<MET>>
  - `SourceScanScheduler` 在 Host 内单实例；`Start` 幂等（重复调用不产生第二个循环）；`Stop`/`Dispose` 后不再 tick，`Stop` 可重入。
  - `Pause`/`Resume` 生效：暂停期间 tick 不产生 Core 调用，恢复后从下一 tick 继续；状态快照可见 `paused`。
  - 间隔默认 900s，由 `HostOptions` + env `NEWMANGA_SOURCE_SCAN_INTERVAL_SECONDS` 覆盖；合法范围 `[60, 86400]`；非法值 → 回落 900s + WARN（不使 Host 启动失败）；默认 enabled=true。
  - 时钟与 tick 可注入：测试用固定 `now` 调用 `TickAsync()`，**零 `Task.Delay`/`Sleep`**；生产循环用 `Task.Delay(interval, timeProvider, token)`。
  - Core 会话失效（`HOST_SESSION_INVALID`/`CORE_SESSION_MISMATCH`/sidecar exit）→ `paused`，不自行重开 host session。
  - 判别测试：fake clock + fake core；`Start×2 → 1 循环`；`TickAsync×3` 按注入 now 精确断言 `next_tick`；`Pause` 后 tick 0 调用；`Stop` 后 tick 0 调用；边界/非法配置；会话失效注入。
- [x] **AC-S2 目标注册、单飞与“只扫不写”** <<MET>>
  - App 在引用导入终态 `Completed` 成功后注册 `(source_id, path, kind='resync', project_ids=[bookId], version)`；重复注册按 `source_id` 覆盖（目标数不增长）；失败/取消不注册。
  - 同一 `source_id` 在飞期间再次触发 → 合并/跳过，不产生第二个 `ScanSourceSync`；不同 `source_id` 可顺序处理。
  - 一次 tick 中调度器只发送 `ScanSourceSync`；fake core 收到的命令集合**精确等于** `{ScanSourceSync}`（逐 tick 命令序列留证）。
  - 扫描失败不写任何 Core 状态（Core 侧 `scan()` 零写）；Host 侧只更新内存状态。
  - 后台检测 `kind` 固定 `resync`（`scanner.scan()` 只校验、不使用 kind）；不得据扫描结果创建 plan 或推断用户意图。
  - 判别测试：`TaskCompletionSource` 卡住第一次 scan → 再 tick → 该 source 仅 1 次调用；注册 2 源 → 1 tick 2 次调用；重复注册仍 1 次；命令集合断言无写命令。
- [x] **AC-S3 预算与退避** <<MET>>
  - 每 tick 目标数上限（默认 8）与每源大小上限（默认 256 MiB；folder 成员数上限）可注入；超限目标**顺延**下一 tick 并记 `deferred`，不算失败。
  - 连续 typed 失败 → 指数退避 `min(60×2^n, 3600)` 秒；成功清零；退避期内该目标跳过。
  - 可停用错误（`CORE_CAPABILITY_MISSING`、`HOST_ONLY_REQUIRED`、`INVALID_REQUEST`）→ 调度器 `paused`/`disabled`，不重试。
  - 前台隔离：慢 scan 在独立 Task；同一时刻 Host 的其他命令（fake 命令）仍能完成（断言并发完成时间 < scan 阻塞时间；不得 sleep 硬等）。
  - 判别测试：10 目标 budget=4 → 4/4/2 分三 tick；连续失败 4 次 → 退避序列 60/120/240/480（注入 clock）；成功后清零；注入 `CORE_CAPABILITY_MISSING` → disabled，后续 tick 0 调用。
- [x] **AC-S4 全量重枚举（真实链路）** <<MET>>
  - 每 tick 对目标执行完整 `ScanSourceSync`，不依赖任何 hint/缓存。
  - 真实 zip 在两次 tick 之间被重写（**同文件名、同大小、不同字节**）→ 下一次 tick 的 Scan 返回 `totals.changed ≥ 1`；状态记录 `result=changed`。
  - **r2（r1 P1 修复）**：`changed` 观察不刷新 missing baseline identity；因此 `ok → changed → 删除` 仍产生 C-17 §5.3 `MissingObservation`（发出 Core 已记录的 location identity），状态 `result=missing`，不会退化为 `SOURCE_PLAN_STALE/error`。真实 IPC 测试显式包含 `changed → changed-deleted` 步并断言 `missing`。
  - 无变化时状态不产生新记录（幂等/去噪）。
  - 源被删除 → Host 先 stat 失败，构造 `MissingObservation`（`registry_id/generation/expected_identity_digest` 来自最后一次 **ok/unchanged** 观察；C-17 §5.3）再调用 `ScanSourceSync`；状态 `result=missing`；**不** tombstone、不删页、不把缺失说成“已删除”。
  - 真实 IPC 测试隔离：真实 Python Core + 真实 v8 库 + 真实 zip + 隔离 DataRoot（`G:\CODEX\New Manga.workspace\FEA-11\fixtures\scan-*`，seed 脚本冻结的隔离守卫）；断言 `page_bindings` 前后快照未变（零写）；wire 精确集合 `{OpenHostSession, RegisterSourceReadGrant, ScanSourceSync, core.ping}`。
- [x] **AC-S5 状态快照与诊断脱敏（in-process，无新 wire）** <<MET>>
  - `HostRuntime.SourceScanStatus` 返回 closed record：`{enabled, interval_seconds, paused, last_tick_at?, next_tick_at?, targets:[{source_id, last_scan_at?, last_result?, counts?, deferred?}], recent[≤50]}`；`last_result ∈ {ok, changed, missing, unsupported, denied, error}`；`deferred` 只表示本 tick 因预算顺延。
  - 快照**不含**绝对路径、grant、session、异常原文、凭据；日志同口径（只 `source_id`/计数/code）。
  - 重启后 `recent` 与 `targets` 为空（L-A/L-C），配置仍从 `HostOptions` 恢复。
  - 判别测试：fake clock 驱动 3 tick → 字段/顺序/上限 50 断言；`InMemoryLog` 捕获日志，断言不含隔离根路径子串、不含 `"source-"` grant id、不含 `host_session`。
- [x] **AC-S6 范围、冻结、回归与证据** <<MET>>
  - 不修改任何冻结契约字节（C-17/C-16/C-15/C-09/C-14/M2-C1/ADJ-001/FEA-01）；`verify_pins.ps1` **18/18 PASS**；`generate_api_inventory.py --check` PASS（C-07 未变）。
  - 不改 `src/**` Core 实现、schema/migration、依赖；若实施中发现必须改 → **停下报 DSH**（窄批）。
  - `dotnet test` 全量不减少（记录 before/after passed/failed/skipped 与 skip 原因；不得以历史数字代替实跑）。
  - 范围 diff 0 域外；`check.ps1` PASS；fixture 全部在 `G:/CODEX/New Manga.workspace/FEA-11-SCAN-1/`；证据完整（EV/scope-validation/changed-files/dotnet-full/pins/check）。
  - AC11-1 映射：本卡只承接“定时扫描生产者 + 丢 hint 后全量重枚举”；watcher 消费者与启动/访问前检查**不承接**，须继续登记 L-3 残余（见 Appointment 说明）。

## 允许修改范围

frontmatter `allowed_paths` 为准（`evidence_dir` 已显式列入）：

- 新增 Host：`NewManga.Host/Sources/SourceScanScheduler.cs`、`NewManga.Host/Sources/SourceScanStatus.cs`。
- 修改 Host：`NewManga.Host/HostOptions.cs`（interval/enabled/limits/clock 注入）、`NewManga.Host/HostRuntime.cs`（创建/启动/停止 + `SourceScanStatus` 属性）。
- 修改 App 接线：`NewManga.App/Services/SourceImportModels.cs`（`ISourceImportController` 注册目标/必要上下文；**默认不改既有方法语义**）、`HostController.cs`、`NullHostController.cs`、`ViewModels/V2/Library/ImportDockViewModel.cs`、`ViewModels/V2/Library/LibraryViewModel.cs`（提供 `bookId`）。
- 测试：`NewManga.Host.Tests/SourceScanSchedulerTests.cs`（新增）、`NewManga.Host.Tests/Fea11ScanIpcTests.cs`（新增）、`NewManga.App.Tests/FakeHostController.cs`（接口实现的必要同步）。
- 文档/证据：本卡、Handoff、Review、`verification/FEA-11-SCAN-1/**`。

## 禁止范围

- 不改 Core：`src/**`（含 `src/application/sources/scheduler.py`、`ports.py`、`__init__.py`、`src/bootstrap/core_assembly.py`、`tests/fea11/test_source_scheduler.py`）——这些是草案旧路径，本卡不适用、不创建。
- 不改 `apps/desktop-avalonia/src/NewManga.Host/**` 之外的 C# 项目（`NewManga.CoreClient/**`、`NewManga.DesignSystem/**` 等）；不改 `IHostController.cs`/`RunContracts.cs`/`FEA-C07_API_INVENTORY.md`/任何 pinned 契约字节。
- 不自动建 plan/preview/confirm/apply/relink/repoint/resync、不 tombstone/删除/GC/清理；不做 watcher/通知持久化/冷启动枚举/UI。
- 不改冻结契约字节 / schema / migration / 新依赖；不在日志/状态/wire 写绝对路径、grant、session、异常原文。
- 不得跨 tick 持有 lease/grant（grant TTL 300s）；不得把“扫描到变化”表述为“已同步/已修复”。
- 不得真实用户数据/`%APPDATA%`/外部卷/回收站；不得 push；不得删测试/放宽断言制造通过；不得自审。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC-S1/S2/S3/S5 | `dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --no-build --filter "FullyQualifiedName~SourceScanScheduler\|FullyQualifiedName~Fea11ScanRegistration"` | fake clock（手写 TimeProvider，可 Advance）/fake core；零 sleep | **PASS：通过 37 / 失败 0 / 跳过 0**，EXIT 0（r1 32 + r2 5：denied 退避、并发快照、ProbeBudget、registry 精确匹配、Disabled 语义） | `logs/dotnet-host-scheduler.log` |
| AC-S2 VM 级（r2） | `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj -c Release --no-build --filter "FullyQualifiedName~Fea11ScanRegistrationVm"` | fake controller + 真实 `ImportDockViewModel` | **PASS：通过 5 / 失败 0**，EXIT 0（Completed 注册一次；Failed/Cancelled/空 bookId 不注册；bookId 在 confirm 时捕获） | `logs/dotnet-app-vm-scan-registration.log` |
| AC-S4 真实链路 | `$env:NEWMANGA_FEA11_IPC=1; dotnet test ... --filter "FullyQualifiedName~Fea11ScanIpcTests"`（真实 Python Core + 真实 v8 库 + 真实 zip + 隔离 DataRoot） | 隔离根 `G:\CODEX\New Manga.workspace\FEA-11\fixtures\scan-*`（seed 脚本冻结的隔离守卫）；真实 IPC；DB 前后快照 | **PASS：通过 1 / 失败 0**，EXIT 0；r2 序列 `unchanged(ok) → changed(changed) → changed-deleted(missing) → restored(ok) → changed-again(changed)`；wire 精确集合 `{OpenHostSession, RegisterSourceReadGrant, ScanSourceSync, core.ping}`；DB 快照前后相同 | `logs/fea11-scan-ipc.log`、`real-ipc.json`、`real-ipc.txt` |
| AC-S4 判别（r2 mutation） | 临时把 identity 缓存条件回退为 r1 前缀语义（changed 也覆盖）→ 真实 IPC 测试 | 同上隔离根 | **PASS（按预期变红）**：`Expected: "missing" / Actual: "error"`（SOURCE_PLAN_STALE 路径），随后恢复修复并复跑绿 | `logs/mutation-p1-changed-identity.log` |
| AC-S5 脱敏 | `dotnet test ... --filter "FullyQualifiedName~StatusAndLogs_AreRedacted"`（InMemory 断言：路径/`source-` grant id/`host_session`/异常原文零命中） | fake core | **PASS：通过 1 / 失败 0**，EXIT 0 | `logs/status-redaction.log` |
| AC-S6 回归 | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build --nologo`（三次实跑）；`pytest tests -q`（引用基线）；`check.ps1 -TaskPath`；`verify_pins.ps1`；`python tools/generate_api_inventory.py --check` | 仓库根；HEAD b48c60a7e（上游无 .NET 变更） | 全 .NET **RUN1 PASS 1447/0/81/1528；RUN2 1446/1/81/1528（已知 flaky `FluentResidual2VisualEvidenceTests` 跨测试 git-status 证据写竞争，非本卡回归）；RUN3 复跑 PASS 1447/0/81/1528**；该 flaky 单测隔离复跑 PASS 1/0/0；pytest 引用 **3203 passed / 10 skipped**（本卡零 Python 改动）；check PASS（3 既有警告）；pins 18/18；API inventory PASS | `logs/gates.log`、`logs/dotnet-full-1.log`、`logs/dotnet-full-2.log`、`logs/dotnet-full-3.log`、`logs/flaky-fluent-residual2.log`、`logs/pytest-full.log`、`logs/pins.log`、`logs/api-inventory.log`、`logs/scope-validation.log` |

## 预期行为变更（Review 不判回归）

1. **App 导入接线**：`ISourceImportController` 新增 `RegisterCompletedImportScanTargets(bookId, sources)`（独立于冻结 C-07 `IHostController`），`HostController`/`NullHostController`/`FakeHostController` 实现；`ImportDockViewModel` 新增**可选** `bookId` 构造参数（既有构造不变），仅在引用导入终态 `Completed` 时注册；r2 起 bookId 在 confirm 时捕获（P3-1）。`generate_api_inventory.py --check` 实测 PASS（18 pins 不变）。
2. **Host 新增后台循环**：`HostRuntime` Ready 后启动 `SourceScanScheduler`，`DisposeAsync`/`StopSidecarsAsync` 停止并 join；默认 enabled=true、900s，首次 tick 在一个间隔之后（冷启动不枚举）。既有测试未观察到 command 差异（全量 .NET 两次 PASS）。
3. **无用户可见变化**：不新增 UI/通知/wire 命令；Review 不得以“没有用户可见功能”判实现不足（按冻结范围判定）。

## r1 Review 处置（r2 返修）

r1 Review：`doc/reviews/FEA-11-SCAN-1-r1.md`（session `074cebe5-157b-4d75-833d-d0624f979fa6`；`changes_requested`，P0=0/P1=1/P2=5/P3=4）。

| Review finding | r2 处置 | 验证 |
|---|---|---|
| **P1-1** changed 覆盖 `_identityDigests` → changed 后删除发出未记录 identity → `SOURCE_PLAN_STALE/error` 而非 `missing` | **修复**：仅 `ok/unchanged` 观察刷新 baseline；`changed` 不覆盖（`SourceScanScheduler.cs` `ProjectScanResult`） | 真实 IPC 增 `changed → changed-deleted` 步断言 `missing`（`logs/fea11-scan-ipc.log`）；mutation 回退即变红（`logs/mutation-p1-changed-identity.log`） |
| P2-1 denied 不退避 | **修复**：denied 计入失败与 60/120/…/3600 退避（结果仍 `denied`，不暂停调度器） | `DeniedResult_IsBackedOff_AndKeepsDeniedResult` |
| P2-2 `_recent`/TargetState 写与 Snapshot 读跨 `_gate` | **修复**：`ApplyOutcome` 状态变更 + recent 追加全部在 `_gate` 内（日志回调在锁外）；tick 读 backoff/deferred 标记同锁 | `ConcurrentSnapshotDuringTicks_DoesNotRaceOrThrow` |
| P2-3 real-IPC wire 仅 Contains | **修复**：改为精确集合断言 `{OpenHostSession, RegisterSourceReadGrant, ScanSourceSync, core.ping}`（顺序不敏感） | 真实 IPC 测试 |
| P2-4 App “仅 Completed 注册”缺 VM 级测试 | **修复**：新增 VM 级测试 5 例（`FakeHostController.ScanTargetRegistrations`） | `logs/dotnet-app-vm-scan-registration.log` |
| P2-5 registry 解析 containment 而非 I-2 exact match | **修复**：先 exact（locator/root 等值、大小写不敏感；exact 命中但已撤销 → fail-closed 返回 null），无 exact 时保留受控 containment 回退（fixture/父目录注册形态），并补单测 | `RegistryResolution_PrefersExactMatch_AndFailsClosedOnRevokedExactEntry` |
| P3-1 bookId 读取时序 | **修复**：confirm 时捕获 `_referenceBookId`，注册优先使用；新 plan 重置 | `ConfirmCapturesBookId_BeforeALaterSelectionSwitch` |
| P3-2 WARN/ProbeBudget/HostRuntime 接线测试 | **部分**：补 `ProbeBudget` 单测；WARN 文案与 HostRuntime Ready/Dispose 接线仍仅代码审查（HostRuntime 级测试受 allowed_paths 限制），登记为 follow-up | `ProbeBudget_UsesRealFileSizeAndFolderMemberLimits` |
| P3-3 changed-files.txt 缺失 | **修复**：新增 `verification/FEA-11-SCAN-1/changed-files.txt` | 文件本身 |
| P3-4 `Disabled.paused` 语义 | **修复**：`SourceScanStatus.Disabled` 的 `Paused=false` 并注释；单测覆盖 | `DisabledStatus_IsNotPaused` |

## 依赖、风险与阻塞

- 硬依赖：`FEA-11`（closed_with_limitations；`ScanSourceSync`/Host grant/registry 已交付）。前置事实：host-control 会话、能力门禁 `source.sync.scan/1` + `source.read/1` 已在 `HostRuntime` 就绪。
- 并行边界：`FEA-11-MATCH-1`（Python scan/matcher）、`FEA-11-AC4-GAPS-1`（test-only）与本卡无文件交集；本卡不得顺手改 Core。
- 主要风险：
  - R-1 周期扫描成本 = Host 全量 hash + Core 全量读/解压 → 每 tick 目标数/每源大小上限 + 默认 900s + `deferred`；成本未在真实大库标定（L-E）。
  - R-2 扫描与 apply 并发 → scan 零写；apply 有 `BEGIN IMMEDIATE` + CAS；扫描结果只是提示，不参与 apply 判据。
  - R-3 Core 会话失效/重启 → typed 失败 → `paused`，不重开 session。
  - R-4 目标集重启丢失 → L-A；方案 B（SCAN-2）才解决。
  - R-5 状态无持久 → L-C；日志可回溯。
  - R-6 共享源多项目 → 只注册一个 project → `scope=current` 的 bases 只覆盖该项目；源级 diff 仍是全量，状态计数可信；如需全项目 bases → SCAN-2（L-F）。
  - R-7 用户误以为“已同步” → 卡/文案禁止“已修复/已同步”；呈现由 UI 切片负责（L-D）。
  - R-8 日志/状态泄露路径 → 脱敏断言（AC-S5）。
  - R-9（r2 更新）C-17 §5.3 missing 观察需要 Core 已记录的 location identity 与 Host baseline 一致：现在 baseline **只在 ok/unchanged** 观察时刷新（changed 不覆盖，r1 P1 修复）；隔离 seed fixture 的合成 7/8/100 占位在 real-IPC 测试内以真实 file identity + Host registry id 对齐（fixture-only，产品代码不伪造）。若首次成功扫描前源已消失且无会话内 baseline，executor fail-closed 记 `error`（`SOURCE_ENTRY_MISSING`）而非伪造 `missing`。
  - R-10 Host 只在 App 导入完成后注册目标，测试/无 UI 场景不会自动产生目标（L-A 一致）。
- 阻塞解除标准：scope 已冻结 → Lead 释放 → 实施 → 证据齐备 → 独立 Review → DSH 集成 closeout。

## 残余 limitation（预登记 L-A…L-F）

- **L-A 冷启动无目标**：重启后目标集为空，直到用户再次导入；冷启动全源覆盖需 `FEA-11-SCAN-2`（Core 读命令或 Host 持久索引）。
- **L-B watcher 仍缺**：L-3 的 watcher 半边不关闭（`FEA-11-WATCH-1`）。
- **L-C 状态不持久**：`recent`/`targets` 仅内存，重启清空。
- **L-D 无用户可见呈现**：无 UI/通知；用户看不到“源已变化”。
- **L-E 成本未实测**：默认 900s/8 目标/256 MiB 未在真实大库标定。
- **L-F 共享源 bases 单项目**：见 R-6。
- **L-G（r2 更新）missing baseline 依赖会话内首次 ok 扫描**：changed 观察不再污染 baseline（r1 P1 已修）；但若源在首次 ok/unchanged tick 之前已消失、且 registry 无持久 identity facts，仍 fail-closed 为 `error`。持久 identity / 冷启动 missing 语义随 SCAN-2 解决。

## 交付与运行记录

- Handoff：`doc/handoffs/FEA-11-SCAN-1-e0c370870.md`（r1 交付、r2 返修、门禁、残余风险、下一步）。
- Review：r1 `doc/reviews/FEA-11-SCAN-1-r1.md`（changes_requested，P1=1/P2=5/P3=4）；r2 待独立复审（上下文独立 Reviewer，须记录 session ID 与来源；作者不得自审）。
- r1 实际测试（2026-11-06）：G1 32/0/0；G2 real IPC 1/0/0（ok→missing→ok→changed）；G3 redaction 1/0/0；G4 全量 .NET 两次 1437/0/81/1518；G5 pytest 3203/10；pins 18/18；API inventory PASS；check PASS。
- r2 实际测试（2026-11-06，同工作树 HEAD b48c60a7e；中断恢复后复跑）：G1 37/0/0；G2 VM 5/0/0；G3 real IPC 1/0/0（ok→changed→missing→ok→changed，wire 精确四命令，零写）；G4 mutation 预期变红后恢复绿；G5 全量 .NET RUN1 PASS 1447/0/81/1528、RUN2 1446/1/81/1528（已知 flaky `FluentResidual2VisualEvidenceTests` 跨测试 git-status 证据写竞争，隔离复跑 PASS，RUN3 全量 PASS 1447/0/81/1528——如实记录，不称稳定）；G6 pytest 引用 3203/10（零 Python 改动）；G7 pins 18/18；G8 API inventory PASS；G9 check PASS（3 既有 warning）；G10 scope 本卡 0 域外。
- 实施 commit：`73d01fd2b`（r1）+ r2 fix commit（见 frontmatter `delivery_head` 与 Handoff 的“交付提交”）。
- 后续由 DSH 填写 `integration_commit` 并改 done。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | G1/AC-S1,S2,S3,S5（r2） | `verification/FEA-11-SCAN-1/logs/dotnet-host-scheduler.log` | null | `3e2838c000a0e5710cc638ff12f98e0c3d60e4c3e97611240028dbbf2e7f8d8d` | CANONICAL |
| EV-02 | G2/AC-S2（r2 VM） | `verification/FEA-11-SCAN-1/logs/dotnet-app-vm-scan-registration.log` | null | `32c67251abf8c233ee055d601a17b4163c8e02c34bde3d029f908ff273c121b0` | CANONICAL |
| EV-03 | G3/AC-S4（r2 IPC） | `verification/FEA-11-SCAN-1/logs/fea11-scan-ipc.log` | null | `c6afc880f63345554d6fd26cafc33e8ee81ad583445a9857351b95f2833153a2` | CANONICAL |
| EV-04 | G3/AC-S4（r2 IPC 证据） | `verification/FEA-11-SCAN-1/real-ipc.json` | null | `8266644fef10733c2b5924fdb94b5dd4e26c253d163a6af8526035e9c352aca2` | CANONICAL |
| EV-05 | G3/AC-S4（r2 IPC 摘要） | `verification/FEA-11-SCAN-1/real-ipc.txt` | null | `b6699db9da9464e3ddc020b2fa85c210bbf374888177862c008eabdaeb1aeda6` | CANONICAL |
| EV-06 | G4/P1 判别 mutation | `verification/FEA-11-SCAN-1/logs/mutation-p1-changed-identity.log` | null | `ae9f5d4694c11e3fe4f00b5f0d09e71f1b1b95cc1ec7c8c8d2afc7f825d7f932` | CANONICAL |
| EV-07 | G5/AC-S6（full run1 PASS） | `verification/FEA-11-SCAN-1/logs/dotnet-full-1.log` | null | `085bc7fb1f2fbf0f8f230c2fd60745c4e6c77c98478f20e39272f8af2fdd9f25` | CANONICAL |
| EV-08 | G5/AC-S6（full run2 已知 flaky FAIL） | `verification/FEA-11-SCAN-1/logs/dotnet-full-2.log` | null | `7a83246a2ad714e0ff5434a8941367198151dc5f4560703c6245526f7a0c9b97` | CANONICAL |
| EV-09 | G5/AC-S6（full run3 复跑 PASS） | `verification/FEA-11-SCAN-1/logs/dotnet-full-3.log` | null | `73f97a5af63cafb56860b6aaee8f7b2def77b616d7ac6d57037a366912f1dd63` | CANONICAL |
| EV-10 | G5/AC-S6（flaky 单测隔离复跑） | `verification/FEA-11-SCAN-1/logs/flaky-fluent-residual2.log` | null | `25ea1a387b9b87a34e4f4d19024a4ebcc2b0c2d0a4ac08c0a20e7d70c9fb5214` | CANONICAL |
| EV-11 | G6/AC-S6（pytest 引用基线） | `verification/FEA-11-SCAN-1/logs/pytest-full.log` | null | `69aa9605ad864ff138aa55d0586c342b40ed51b1a3d970a89a3a523604606345` | CANONICAL |
| EV-12 | G8/AC-S6（pins） | `verification/FEA-11-SCAN-1/logs/pins.log` | null | `2ebcc2c24b9075f939b9beb027ed2decd273323581327db12b6097adb37c4d94` | CANONICAL |
| EV-13 | G9/AC-S6（API inventory） | `verification/FEA-11-SCAN-1/logs/api-inventory.log` | null | `b4b9e68e1f7fce0dc4aeecfae9d887da0c0661b346a9434930ae62b3a2270c47` | CANONICAL |
| EV-14 | G10/AC-S6（scope） | `verification/FEA-11-SCAN-1/logs/scope-validation.log` | null | `070960a4015c8511ae712cab21316c1e4c3b557fd9a87eb57380528f649bc3d3` | CANONICAL |
| EV-15 | Gate 记录（r2） | `verification/FEA-11-SCAN-1/logs/gates.log` | null | `6e825e8c45c60aa58d9580b6ca7730bc5038ec28970e1d217493213e922bc0bb` | CANONICAL |
| EV-16 | AC-S5（脱敏；r1 未变） | `verification/FEA-11-SCAN-1/logs/status-redaction.log` | null | `f5da210e610afa1d91d7bfcf6abbc1033b2c3ed2be732beda8cbe0e23806b689` | CANONICAL |
| EV-17 | P3-3（changed files） | `verification/FEA-11-SCAN-1/changed-files.txt` | null | `5dc392131d0849570f7775456d8da7b8dab317b0f2a8ef5a7641e625a1c97bdf` | CANONICAL |
## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（main 工作树实施） | NOT_APPLICABLE | — | — | 未创建独立 worktree |
| temp | `G:\CODEX\New Manga.workspace\FEA-11-SCAN-1\`（门禁/测试原始日志） | PRESERVE_REFERENCED | 同上 | 交付后由 DSH closeout 时登记 manifest | 原始日志为仓内 `logs/` 证据的上游副本；仓内证据已按 sha256 pin |
| temp | `G:\CODEX\New Manga.workspace\FEA-11\fixtures\scan-*`（隔离 IPC fixture，含真实 zip/v8 DB） | DELETE_SAFE（交付后） | — | — | 隔离根由冻结 seed 脚本守卫（只允许 FEA-11 fixtures 下 library.db）；无真实用户数据；DSH closeout 时删除 |
| agent-output | `G:\CODEX\New Manga.workspace\agent-output\fea11-scan-1\FEA-11-SCAN-1\`（check 日志等过程输出） | PRESERVE_REFERENCED | 同上 | 交付后由 DSH closeout 时登记 | check 日志避免仓内自指（FEA-12-PREREQ-1 R-003 先例） |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：L-A…L-F（见上）；AC11-1 仍 PARTIAL（watcher/启动扫描未承接）。
- 当前指针清理：待 DSH closeout 时更新 STATUS / Plan / TASK_LEDGER 或说明无需更新。
