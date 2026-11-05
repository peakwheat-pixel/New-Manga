---
id: FEA-11-SCAN-1
title: FEA-11 源后台定时扫描（Host 进程内只读周期触发切片）
kind: implementation
governance_version: 3
status: ready
approval: scope 已按 ZCode SCOPE-ADJ-2026-11-05 冻结，**DSH 2026-11-06 释放（ready）**：承接 FEA-11 AC11-1 的「定时扫描生产者」延期项（L-3 半边）；释放时由 DSH 固定 base_commit、Owner 与上下文独立 Reviewer
suggested_owner: codex
owner: null
reviewer: null
depends_on:
  - FEA-11
base_commit: e0c370870   # 释放点 main head（MATCH-1 交付后）
branch: null
worktree: null
integration_commit: null
delivery_head: null
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

> **状态：`proposed`。本卡 scope 已按 ZCode SCOPE-ADJ-2026-11-05 冻结，待 Lead（DSH）释放；释放前不得实施、不得改卡面语义。**
>
> 冻结方案：**方案 A = Host 侧只读周期触发切片**（不做 Core 定时器、不做 watcher、不做通知持久化、不做自动 plan/apply）。范围事实基线：`main@604a2d343`。

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

- [ ] **AC-S1 调度器生命周期与配置（Host）**：
  - `SourceScanScheduler` 在 Host 内单实例；`Start` 幂等（重复调用不产生第二个循环）；`Stop`/`Dispose` 后不再 tick，`Stop` 可重入。
  - `Pause`/`Resume` 生效：暂停期间 tick 不产生 Core 调用，恢复后从下一 tick 继续；状态快照可见 `paused`。
  - 间隔默认 900s，由 `HostOptions` + env `NEWMANGA_SOURCE_SCAN_INTERVAL_SECONDS` 覆盖；合法范围 `[60, 86400]`；非法值 → 回落 900s + WARN（不使 Host 启动失败）；默认 enabled=true。
  - 时钟与 tick 可注入：测试用固定 `now` 调用 `TickAsync()`，**零 `Task.Delay`/`Sleep`**；生产循环用 `Task.Delay(interval, timeProvider, token)`。
  - Core 会话失效（`HOST_SESSION_INVALID`/`CORE_SESSION_MISMATCH`/sidecar exit）→ `paused`，不自行重开 host session。
  - 判别测试：fake clock + fake core；`Start×2 → 1 循环`；`TickAsync×3` 按注入 now 精确断言 `next_tick`；`Pause` 后 tick 0 调用；`Stop` 后 tick 0 调用；边界/非法配置；会话失效注入。
- [ ] **AC-S2 目标注册、单飞与“只扫不写”**：
  - App 在引用导入终态 `Completed` 成功后注册 `(source_id, path, kind='resync', project_ids=[bookId], version)`；重复注册按 `source_id` 覆盖（目标数不增长）；失败/取消不注册。
  - 同一 `source_id` 在飞期间再次触发 → 合并/跳过，不产生第二个 `ScanSourceSync`；不同 `source_id` 可顺序处理。
  - 一次 tick 中调度器只发送 `ScanSourceSync`；fake core 收到的命令集合**精确等于** `{ScanSourceSync}`（逐 tick 命令序列留证）。
  - 扫描失败不写任何 Core 状态（Core 侧 `scan()` 零写）；Host 侧只更新内存状态。
  - 后台检测 `kind` 固定 `resync`（`scanner.scan()` 只校验、不使用 kind）；不得据扫描结果创建 plan 或推断用户意图。
  - 判别测试：`TaskCompletionSource` 卡住第一次 scan → 再 tick → 该 source 仅 1 次调用；注册 2 源 → 1 tick 2 次调用；重复注册仍 1 次；命令集合断言无写命令。
- [ ] **AC-S3 预算与退避**：
  - 每 tick 目标数上限（默认 8）与每源大小上限（默认 256 MiB；folder 成员数上限）可注入；超限目标**顺延**下一 tick 并记 `deferred`，不算失败。
  - 连续 typed 失败 → 指数退避 `min(60×2^n, 3600)` 秒；成功清零；退避期内该目标跳过。
  - 可停用错误（`CORE_CAPABILITY_MISSING`、`HOST_ONLY_REQUIRED`、`INVALID_REQUEST`）→ 调度器 `paused`/`disabled`，不重试。
  - 前台隔离：慢 scan 在独立 Task；同一时刻 Host 的其他命令（fake 命令）仍能完成（断言并发完成时间 < scan 阻塞时间；不得 sleep 硬等）。
  - 判别测试：10 目标 budget=4 → 4/4/2 分三 tick；连续失败 4 次 → 退避序列 60/120/240/480（注入 clock）；成功后清零；注入 `CORE_CAPABILITY_MISSING` → disabled，后续 tick 0 调用。
- [ ] **AC-S4 全量重枚举（真实链路）**：
  - 每 tick 对目标执行完整 `ScanSourceSync`，不依赖任何 hint/缓存。
  - 真实 zip 在两次 tick 之间被重写（**同文件名、同大小、不同字节**）→ 下一次 tick 的 Scan 返回 `totals.changed ≥ 1` 且 `source.content_digest` 变化；状态记录 `result=changed`。
  - 无变化时状态不产生新记录（幂等/去噪）。
  - 源被删除 → Host 先 stat 失败，构造 `MissingObservation`（`registry_id/generation/expected_identity_digest` 来自 registry `identity_facts`，C-17 §5.3）再调用 `ScanSourceSync`；状态 `result=missing`；**不** tombstone、不删页、不把缺失说成“已删除”。
  - 真实 IPC 测试隔离：真实 Python Core + 真实 v8 库 + 真实 zip + 隔离 DataRoot（`G:/CODEX/New Manga.workspace/FEA-11-SCAN-1/`）；断言 `page_bindings` 前后快照未变（零写）。
- [ ] **AC-S5 状态快照与诊断脱敏（in-process，无新 wire）**：
  - `HostRuntime.SourceScanStatus` 返回 closed record：`{enabled, interval_seconds, paused, last_tick_at?, next_tick_at?, targets:[{source_id, last_scan_at?, last_result?, counts?, deferred?}], recent[≤50]}`；`last_result ∈ {ok, changed, missing, unsupported, denied, error}`；`deferred` 只表示本 tick 因预算顺延。
  - 快照**不含**绝对路径、grant、session、异常原文、凭据；日志同口径（只 `source_id`/计数/code）。
  - 重启后 `recent` 与 `targets` 为空（L-A/L-C），配置仍从 `HostOptions` 恢复。
  - 判别测试：fake clock 驱动 3 tick → 字段/顺序/上限 50 断言；`InMemoryLog` 捕获日志，断言不含隔离根路径子串、不含 `"source-"` grant id、不含 `host_session`。
- [ ] **AC-S6 范围、冻结、回归与证据**：
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
| AC-S1/S2/S3/S5 | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release --filter "FullyQualifiedName~SourceScanScheduler"` | fake clock/fake core；隔离；零 sleep | NOT_RUN（待释放） | `verification/FEA-11-SCAN-1/logs/dotnet-host-scheduler.log`（计划） |
| AC-S4 真实链路 | `$env:NEWMANGA_FEA11_SCAN_IPC=1; dotnet test ... --filter "FullyQualifiedName~Fea11ScanIpcTests"`（真实 Python Core + 真实 zip + 隔离 DataRoot） | 隔离根；真实 IPC；DB 前后快照 | NOT_RUN | `verification/FEA-11-SCAN-1/logs/fea11-scan-ipc.log`、`real-ipc.txt` |
| AC-S5 脱敏 | 同 AC-S1 测试集内 `InMemoryLog` 断言 | fake core | NOT_RUN | `logs/status-redaction.log` |
| AC-S6 回归 | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release`（全量，释放日基线 before/after 分列）；`check.ps1`；`verify_pins.ps1`；`python tools/generate_api_inventory.py --check` | 仓库根 | NOT_RUN | `logs/dotnet-full.log`、`pins.log`、`check.log`、`scope-validation.log` |

## 预期行为变更（Review 不判回归）

1. **App 导入接线**：`ISourceImportController`/`HostController`/`NullHostController`/`ImportDockViewModel` 可能新增目标注册所需上下文（`bookId`/注册调用）；`FakeHostController` 同步实现。属 App 内部非 C-07 接口变化，`generate_api_inventory.py --check` 必须仍 PASS。
2. **Host 新增后台循环**：`HostRuntime` 生命周期新增调度器 start/stop；Test 装配若未启用 `ReferencedImportEnabled` 则不运行，既有测试不应观察到命令差异。
3. **无用户可见变化**：本卡不新增 UI/通知/wire 命令；Review 不得以“没有用户可见功能”判实现不足（按冻结范围判定）。

## 依赖、风险与阻塞

- 硬依赖：`FEA-11`（closed_with_limitations；`ScanSourceSync`/Host grant/registry 已交付）。前置事实：host-control 会话、能力门禁 `source.sync.scan/1` + `source.read/1` 已在 `HostRuntime` 就绪。
- 并行边界：`FEA-11-MATCH-1`（Python scan/matcher）、`FEA-11-AC4-GAPS-1`（test-only）与本卡无文件交集；本卡不得顺手改 Core。
- 主要风险：
  - R-1 周期扫描成本 = Host 全量 hash + Core 全量读/解压（`SourceReadCoordinator.cs:71` + `scanner.py:244`）→ 每 tick 目标数/每源大小上限 + 默认 900s + `deferred` 状态；成本未在真实大库标定（L-E）。
  - R-2 扫描与 apply 并发 → scan 零写；apply 有 `BEGIN IMMEDIATE` + CAS；扫描结果只是提示，不参与 apply 判据。
  - R-3 Core 会话失效/重启 → typed 失败 → `paused`，不重开 session。
  - R-4 目标集重启丢失 → L-A；方案 B（SCAN-2）才解决。
  - R-5 状态无持久 → L-C；日志可回溯。
  - R-6 共享源多项目 → 只注册一个 project → `scope=current` 的 bases 只覆盖该项目；源级 diff 仍是全量（`scanner.py:219-229`），状态计数可信；如需全项目 bases → SCAN-2（L-F）。
  - R-7 用户误以为“已同步” → 卡/文案禁止“已修复/已同步”；呈现由 UI 切片负责（L-D）。
  - R-8 日志/状态泄露路径 → 脱敏断言（AC-S5）。
- 阻塞解除标准：scope 已冻结 → Lead 释放（固定 base/Owner/Reviewer；并确认 SC-B08 窄裁定与本卡的接口路径说明）→ 实施 → 证据齐备 → 独立 Review → DSH 集成 closeout。

## 残余 limitation（预登记 L-A…L-F）

- **L-A 冷启动无目标**：重启后目标集为空，直到用户再次导入；冷启动全源覆盖需 `FEA-11-SCAN-2`（Core 读命令或 Host 持久索引）。
- **L-B watcher 仍缺**：L-3 的 watcher 半边不关闭（`FEA-11-WATCH-1`）。
- **L-C 状态不持久**：`recent`/`targets` 仅内存，重启清空。
- **L-D 无用户可见呈现**：无 UI/通知；用户看不到“源已变化”。
- **L-E 成本未实测**：默认 900s/8 目标/256 MiB 未在真实大库标定。
- **L-F 共享源 bases 单项目**：见 R-6。

## 交付与运行记录

- Handoff：尚无（待释放/实施后新增 `doc/handoffs/FEA-11-SCAN-1-*.md`）。
- Review：尚无（独立上下文 Reviewer，须记录 session ID 与来源；作者不得自审）。
- 实际测试：尚无（当前 `status: proposed`，未实施、未跑本卡测试）。
- 后续实际记录包含日期、commit、环境、结果、遗留项；最终由 DSH 填写 `integration_commit` 并改 done。

## Canonical Evidence

进入 `in_review` 前逐项登记唯一当前证据；本卡尚未实施，表格为空。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（main 工作树；释放时由 DSH 固定） | NOT_APPLICABLE | — | — | 未创建 |
| temp | `G:\CODEX\New Manga.workspace\FEA-11-SCAN-1\`（预计隔离 fixture 根） | DELETE_SAFE（预计） | — | — | 未创建；实施后按实际登记 |
| agent-output | — | NOT_APPLICABLE | — | — | 本卡尚未产生 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：L-A…L-F（见上）；AC11-1 仍 PARTIAL（watcher/启动扫描未承接）。
- 当前指针清理：待 DSH closeout 时更新 STATUS / Plan / TASK_LEDGER 或说明无需更新。
