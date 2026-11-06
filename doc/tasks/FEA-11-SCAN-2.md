---
id: FEA-11-SCAN-2
title: FEA-11 冷启动全源扫描目标枚举（B1：Core 只读枚举 + Host registry 核验/铸 grant）
kind: implementation
governance_version: 3
status: in_review
approval: 用户 2026-11-06「让 Codex 判断下一部任务，由 DSH 执行」→ Codex `NEXT-TASK=FEA-11-SCAN-2`（先独立 scope review、优先 B1）；scope review `doc/reviews/FEA-11-SCAN-2-scope-r1.md` = **READY-WITH-UNFREEZE/B1**；DSH 裁决 B1 采纳 / S-1 选项②（file-root 缺失 typed `SOURCE_REGISTRY_UNAVAILABLE`，不宣 missing，L-G 保留）/ S-2 采纳（Core 枚举 source_id 为唯一权威，App 只触发刷新）/ S-4 登记 limitation；前置契约 **C-17 v1.1 已重冻**（`FEA-11-SCAN-2-PREREQ-1` done，delivery `7451bfaaa`，pins 18/18）；DSH 2026-11-06 冻结本卡并释放
suggested_owner: dsh（Agent Teams 分片：Core Python + Host/App .NET；Lead 集成）
owner: fea12-core-py（Core 分片）、fea12-core-host（Host/App 分片）；Lead 集成
reviewer: 独立上下文 fresh subagent（r1 session `32e815ef-4423-4c77-8be9-1f100d6479de`；报告 `doc/reviews/FEA-11-SCAN-2-r1.md`；CHANGES P0=0/P1=1/P2=5/P3=6；未参与实现）
depends_on:
  - FEA-11-SCAN-1
  - FEA-11-SCAN-2-PREREQ-1
base_commit: 703d9eb12   # PREREQ-1 closeout 后 main head（释放点）
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-SCAN-2
allowed_paths:
  - doc/tasks/FEA-11-SCAN-2.md
  - doc/reviews/FEA-11-SCAN-2-*.md
  - doc/handoffs/FEA-11-SCAN-2-*.md
  - verification/FEA-11-SCAN-2/**
  - src/application/sources/scanner.py
  - src/application/sources/ports.py
  - src/application/sources/__init__.py
  - src/infrastructure/sqlite/source_sync.py
  - src/infrastructure/sqlite/source_read_refs.py
  - src/bootstrap/core_service.py
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanStatus.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostOptions.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/NullHostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/SourceImportModels.cs
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/ImportDockViewModel.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs
  - tests/core/**
  - tests/fea09/**
  - tests/fea11/**
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/**
  - apps/desktop-avalonia/tests/NewManga.App.Tests/**
out_of_scope:
  - C-17 v1.1 / C-16 / C-15 / C-06 / M2-C1 / ADJ-001 冻结字节（已重冻；只读引用）
  - SQLite schema/migration/索引；新依赖
  - watcher、扫描算法重写、plan/apply/删除/GC、通知/attention/UI 页面
  - Host 直连 Core DB 或建立第二套 Book/Page 数据库；自动重新授权
  - 真实用户数据/AppData/外部卷/回收站；push
---

# FEA-11-SCAN-2：冷启动全源扫描目标枚举（B1 实现）

> **状态：`ready`（scope 已冻结；C-17 v1.1 已重冻 `7451bfaaa`；待 Owner 认领实施）。**
> 承接 `FEA-11-SCAN-1`（done，`7080167e1`）的 L-A（重启后目标集为空）与 L-G（首次成功扫描前 missing fail-closed）；**不解决** L10（真实 referenced 图源/rendition），**不**把 AC11-1 整体标 MET。

## 来源与依据

1. Codex 裁决：`G:\CODEX\New Manga.workspace\FEA-12\codex-next-task.md`（NEXT-TASK=SCAN-2；先 scope review、优先 B1）。
2. Scope review：`doc/reviews/FEA-11-SCAN-2-scope-r1.md`（fresh subagent；READY-WITH-UNFREEZE；B1 可行；B2 不推荐；S-1/S-2/S-4）。
3. 契约：`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md` v1.1（`aefa0fa5…`；命令 `source_list_scan_targets`、DTO `ScanTarget/ScanTargets`、capability `source.sync.enumerate/1` 只进 `core.ping.capabilities`）；冻结记录 `doc/plan/FEA-CONTRACT-FROZEN-C17.md`；UNFREEZE 载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-06-C17.md`。
4. 现状：SCAN-1 `SourceScanScheduler`/`HostSourceScanExecutor`（`apps/desktop-avalonia/src/NewManga.Host/Sources/`）、Host `SourceAccessRegistry`（持久化 registry/generation/roots/locator）、Core `sources/source_locations/page_bindings`。

## 目标

Host 冷启动后**无需用户再次导入**即可获得可扫描目标集：Core 只读枚举权威目标（B1），Host 核验持久 registry 授权并铸造新会话 grant，沿用 SCAN-1 的只读周期触发（仅 `ScanSourceSync`、零 Core 业务写、不建 plan/apply）。

## Scope（冻结）

### In
1. **Core**：新增只读命令 `source_list_scan_targets`（wire 见 C-17 v1.1 §5.1/§5.2；application 面、closed shape、零写）；capability `source.sync.enumerate/1` 仅进 `core.ping.capabilities`。
2. **Host**：Ready 后异步调用枚举（先 probe capability；缺失 → typed fail-closed，不阻塞启动）；`ScanTargets` 与 SCAN-1 内存目标按 `source_id` 合并/去重；对每 target 用持久 `SourceAccessRegistry` 核验 `registry_id/generation/revoked` 并铸造 live grant，再交既有 `ScanSourceSync`；首轮受预算限制、单飞/退避/停机取消沿用 SCAN-1。
3. **App**：只有「引用导入 Completed」触发一次 Host Refresh；**不再**用 `StableSourceId`/folder `registry_id` 作为扫描目标权威（S-2）；不新增 UI 页面。
4. **测试/证据**：真实重启 Host/Core（无 App 注册）+ 真实 IPC；wire 命令白名单、零写快照、脱敏、注入时钟零 sleep。

### Out
- watcher（WATCH-1）、扫描算法重写、plan/apply/删除/GC、通知/UI 页面、Host 直连 Core DB、第二套书库、自动重新授权、真实用户数据、新依赖。

## 实现语义（DSH 冻结）

- **B1 权威**：`source_id` 唯一来自 Core `sources`（`src-<uuid>`）；`source_kind`/`registry_id`/`generation`/`identity_digest`/`project_ids` 来自 Core 只读枚举；Host 只对既有 registry 做**授权核验**，不自行发明 target。
- **S-2**：App 的导入完成只触发 Host 刷新；禁止用 `StableSourceId`/folder registry_id 冒充 target；实现必须含「真实导入 → 枚举 → target.source_id == Core sources.source_id」判别测试。
- **S-1 选项②**：生产 file-root 缺失/替换导致 `SOURCE_REGISTRY_UNAVAILABLE` → 该轮枚举/扫描 fail-closed（typed），**不得**输出 `missing`；L-G 保持。
- **P3-3 决策（C-17 不改字节）**：`source_kind` 在 v1.1 DTO 为 ID；实现必须对未知 kind **fail-closed**（typed skip + 计数），不得猜测；如需五值枚举，另走 additive。
- **P3-4 决策（C-17 不改字节）**：`project_ids` 沿用 C-17 §5 的 1..20；共享源 book 去重数 >20 时该 target **不进入 targets**（typed skip + 计数日志），**不静默截断、不回退 current 语义**；AC-S2-6 按此冻结。
- **零写**：枚举与扫描均不写 Core 业务表（14 表快照）；不建 plan/apply/operation/receipt/grant/journal（Host grant 为会话内存/既有持久授权核验）。

## Acceptance Criteria

- [x] **AC-S2-1 冷启动枚举（真实重启）**：新 Host 进程 Ready 后（无 App 注册、无用户交互）调用 `source_list_scan_targets` 并得到 targets；wire 命令白名单恰含 `{core.ping, OpenHostSession, source_list_scan_targets, RegisterSourceReadGrant, ScanSourceSync}`（顺序不敏感）；无 plan/apply/删除命令帧。 <<MET>>
- [x] **AC-S2-2 与会话导入合并/去重**：App 导入 Completed 触发 Refresh；枚举结果与 SCAN-1 内存目标按 `source_id` 合并去重；重复 Refresh 幂等、targets 不增长。 <<MET>>
- [x] **AC-S2-3 Core source_id 权威（S-2 判别）**：真实导入一本书 → 枚举 → `target.source_id == Core sources.source_id`（`src-<uuid>`），且 ≠ `StableSourceId`；判别测试必须能在 App 误用 StableSourceId 时转红。 <<MET>>
- [x] **AC-S2-4 registry 授权核验**：target 的 `registry_id/generation` 与 Host 持久 registry 匹配才铸 grant；registry 缺失/撤销/代次漂移 → typed skip（不扫描、不自动重新授权、不泄露路径）；撤销后同 target 不再扫描。 <<MET>>
- [x] **AC-S2-5 启动前缺失/删除（S-1②）**：生产 file-root 缺失/替换 → typed `SOURCE_REGISTRY_UNAVAILABLE` fail-closed，**不是** `missing`；该轮不产生 `ScanSourceSync` 帧；L-G 口径保留。 <<MET>>
- [x] **AC-S2-6 共享源 project_ids 边界（P3-4）**：共享源 `project_ids` 去重数 ≤20 时正常进 targets；>20 时该 target 不进入且 typed skip 计数，不静默截断/不回退 current。 <<MET>>
- [x] **AC-S2-7 预算/单飞/退避/取消**：首轮枚举+扫描受 SCAN-1 预算（8 目标/256MiB）且不阻塞 Host Ready；枚举与 tick 单飞不重叠；停机取消在安全检查点；可注入时钟（零 sleep）。 <<MET>>
- [x] **AC-S2-8 零写/脱敏**：枚举与扫描前后 14 表快照逐行相等（Core 业务库零写）；wire/日志/错误无路径、无 secret、无 grant/session 原文；缺 location facts → typed skip 不伪造 identity。 <<MET>>
- [x] **AC-S2-9 门禁与回归**：`pytest tests/core tests/fea09 tests/fea11`、全量 pytest（基线 **3203/10** 不降）、全量 .NET（基线 **1486/0/82** 不降；首跑 flaky 复跑并记录；跑后 `git checkout -- verification/FEA-09`）、`python tools/generate_api_inventory.py --check` PASS、`verify_pins.ps1` **18/18**、`check.ps1 -TaskPath` PASS、scope diff 仅本卡 allowed_paths（C-17/C-16/C-15/C-06/M2-C1/ADJ-001 零 diff）、AC11-1 仍 PARTIAL、L10 不解决。 <<MET>>

## 预期行为变更（Review 不判回归）

1. 冷启动后（原 SCAN-1 目标集为空）现在会自动扫描已注册且仍授权的旧源；本卡目标行为。
2. App 的扫描目标注册语义改为「Completed 后触发 Host Refresh」，不再以 App 计算 id 作为权威（S-2）；SCAN-1 既有单测中依赖 App 注册 id 的断言需按新语义调整。
3. 生产 file-root 缺失/替换从「未覆盖」变为 typed `SOURCE_REGISTRY_UNAVAILABLE`（S-1②）；不产生 missing。
4. 共享源 >20 books 的 target 不进枚举结果（typed skip），不截断、不回退 current。

## 允许修改范围

frontmatter `allowed_paths` 为准；分片 A（Core Python）与分片 B（Host/App .NET）写域互不相交；Lead 保留 STATUS/PLAN/LEDGER/reviews/契约/冻结记录。

## 禁止范围

不改已重冻的 C-17 v1.1 与其他 17 冻结契约/ADJ-001 字节；不改 schema/migration/依赖；不碰真实数据/回收站；不建第二套 Book/Page 库；不自动重新授权；不 push；实现者不得自审。

## 测试要求

| 计划测试 | 命令/方法 | 环境 | 期望 | 证据路径 |
|---|---|---|---|---|
| Core 枚举单测 | `pytest tests/core -q -p no:cacheprovider` | 隔离 DB | PASS（closed shape/只读/排序/去重/上限/unknown kind fail-closed） | `verification/FEA-11-SCAN-2/logs/pytest-core.log` |
| 真实重启 IPC | 新 Host 进程 + 真实 Core + 隔离 DataRoot（无 App 注册） | 隔离 | PASS（命令白名单、14 表零写、typed 缺失） | `verification/FEA-11-SCAN-2/logs/restart-ipc.log` |
| 全量 Python | `pytest tests -q -p no:warnings --tb=no` | 仓库根 | **PASS 3212 passed/10 skipped**（r2 集成；基线 3203/10，+9 新增，0 回归） | `logs/core-pytest-full.log`、`logs/gates-integration.log` |
| 全量 .NET | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build` | 仓库根 | **PASS 1500 passed/0 failed/85 skipped**（r2 集成复跑；分片侧 RUN1/2/3 与 flaky 记录见 host-r2-dotnet-full-*.log、host-r2-flaky-*.log） | `logs/gates-integration.log`、`logs/host-dotnet-full-3.log` |
| API inventory / pins / check | `python tools/generate_api_inventory.py --check`；`verify_pins.ps1`；`check.ps1 -TaskPath` | 仓库根 | PASS；18/18；PASS | `logs/gates.log` |
| 范围 diff | `git diff --name-only 703d9eb12..HEAD -- doc/plan doc/contracts src/infrastructure/sqlite/schema.py` | 仓库根 | 空 | `logs/scope-diff.log` |

## 依赖、风险与阻塞

- 依赖：SCAN-1 done（`7080167e1`）；PREREQ-1 done（C-17 v1.1，`7451bfaaa`，pins 18/18）；真实 registry/grant 能力。
- 风险/limitation：**L-S1** registry resilience（file-root 缺失整库 `SOURCE_REGISTRY_UNAVAILABLE`，另立缺陷卡）；**L-S4** `refresh_source_location_auth` 死代码（撤销/重注册后 Core location auth 不更新，只读切片无法恢复）；L-A/L-G 承接；大库 IO/冷启动预算未标定；枚举只读但不解决 L10 referenced 图源；**AC11-1 仍 PARTIAL**（watcher/访问前策略未承接；WATCH-1 不同时释放）。
- 阻塞：无（契约已重冻、scope 已冻结）。

## r1 Review 处置（DSH，2026-11-06）

- 结论：**CHANGES**（P0=0 / **P1=1** / P2=5 / P3=6；报告 `doc/reviews/FEA-11-SCAN-2-r1.md`，session `32e815ef…`）。
- **P1-1（阻断，必修）**：`HostSourceScanExecutor.ScanAsync/ScanMissingAsync` 硬编码 `scope="current"` 并携带全部 `target.ProjectIds`；C-17/Core 规定 scope=current 恰好 1 个 project（`scanner.py:267-269`），多 book 共享源 target 永远 `INVALID_REQUEST` → 每轮 error/退避。修复：按 `ProjectIds.Count` 选 `current`/`all` + frame 级判别测试（2-book→all、1-book→current）+ 真实 IPC 共享源用例。
- **P2-1**：tick 运行中 App Refresh 被 `WaitAsync(0)` 直接丢弃 → 导入新源本会话不再枚举。修：pending/coalesce 重放（或在 tick 结束后补一次枚举）。
- **P2-2**：Core 枚举产出 `project_ids=[]` 的 target（C-17 §5 规定 1..20）；Core 侧应 skipped/不产出 + 测试。
- **P2-3**：AC-S2-3 真实导入 E2E 未跑（seed 合成 "s1"）；补 gated 真实导入链 E2E，或降级受限 MET；本卡先降 **PARTIAL**，修复后恢复。
- **P2-4（Lead 记录）**：`6c8b4cb2b` 修改 `apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/LibraryViewModel.cs` 不在冻结 `allowed_paths`（编译必需连带修改）。**DSH 记录为 allowlist 例外，不回退代码**；shard record 中“均在 allowed_paths”表述由实现者更正。AC-S2-9 修复后恢复。
- **P2-5**：AC-S2-1 “新 Host 进程 Ready”仅组件级；补 gated HostRuntime 冷启动用例，或降级限定 MET。本卡先降 **PARTIAL**。
- P3×6：记录于报告，按最小修复/登记 limitation 处置。
- 派发：Core 分片（fea12-core-py）修 P2-2；Host/App 分片（fea12-core-host）修 P1-1/P2-1/P2-3/P2-5；完成后 r2 窄面复审。

## r2 返修与集成（2026-11-06）

- **P1-1 已修**（`196793e01`）：`ResolveScanScope(target)` 按 `ProjectIds.Count` 选 `current`(1)/`all`(>1)，scan 与 missing 帧统一 payload builder；单测 3 例 + 真实共享源 IPC 判别（同一 PNG 导入两 book：单 book 帧 `scope=current`、共享源帧 `scope=all` 且 project_ids 恰两 book）。
- **P2-1 已修**：`_refreshPending` coalesce + Tick 后重放；竞争窗口测试证明 tick 中 Refresh 不丢、新 target 随后被扫描。
- **P2-2 已修**（Core `20faf062a`）：空 `project_ids` → typed skip（不进入 targets、计数日志），与 C-17 1..20 一致；变异转红。
- **P2-3 已修**：gated 真实导入→枚举 E2E（真实 Core + 生产 `SourceImportCoordinator`，真实 PNG 导入 book1/book2）：Core 真实 `src-b1e32669…` == target.source_id 且 ≠ StableSourceId `src-d902593b…`；两 book 集合一致、Refresh 幂等、15 表零写。
- **P2-4 已记录**：`LibraryViewModel.cs` 为编译必需连带修改（allowlist 例外），shard record/changed-files 已明示。
- **P2-5 已处置**：gated HostRuntime Ready→后台枚举（真实 sidecar）：Ready 非阻塞、枚举状态/typed fail-closed/Refresh/tick 正常；limitation 已登记（无 fake-Core/时钟 seam；成功枚举由组件级真实 Core E2E 补足）。
- P3 同批：HostRuntime 注释、generation-drift retryable 注释、VM 测试名清理。
- r2 集成门禁（HEAD `196793e01`，日志 `verification/FEA-11-SCAN-2/logs/gates-r2-integration.log`）：全量 pytest **3212/10**（EXIT 0）、`tests/fea11` **108**、全量 .NET **1500/0/85**（EXIT 0；分片 RUN1/2 各 1 次已知/环境 flaky，隔离复跑 PASS，RUN3 1500/0/85 PASS）、check/check-TaskPath PASS、pins **18/18**、API inventory PASS、scope diff 空。
- AC 恢复：AC-S2-1/3/6/9 → MET（r2 证据）。
- 待 r2 窄面复审；通过后 closeout。AC11-1 仍 PARTIAL；L10 不解决；L-S1/L-S4 保留。

## 交付与运行记录（Lead 集成，2026-11-06）

- 分片 A（Core Python）：`0cb5177ca`；`scanner.list_scan_targets`、`SourceSyncStore.list_scan_target_candidates`、`core_service` 命令路由与 capability；8 条新测试 + 4 变异判别。
- 分片 B（Host/App .NET）：`6c8b4cb2b`（+ docs `3e6e35b19`）；`RefreshTargetsAsync`/`HostSourceScanTargetEnumerator`/registry 核验/typed skip/`SOURCE_REGISTRY_UNAVAILABLE` fail-closed/App Completed→Refresh（无参，去除 StableSourceId 权威）/CoreClient `ListSourceScanTargetsAsync`。
- 集成门禁（HEAD `3e6e35b19`，日志 `verification/FEA-11-SCAN-2/logs/gates-integration.log`）：
  - 全量 pytest **3211 passed / 10 skipped**（EXIT 0；基线 3203/10）
  - `pytest tests/fea11` **108 passed**（EXIT 0）
  - 全量 .NET **1496 passed / 0 failed / 83 skipped**（EXIT 0；分片侧 RUN1 1495/1/83、RUN2 1494/2/83 flaky、RUN3 1496/0/83 PASS 均如实记录）
  - `check.ps1 -TaskPath` PASS、`check.ps1` PASS（3 warnings）、`verify_pins.ps1` **18/18 PASS**、`python tools/generate_api_inventory.py --check` PASS
  - `git diff 703d9eb12..HEAD -- doc/plan doc/contracts src/infrastructure/sqlite/schema.py` **空**
- 跨分片判别证据：真实重启 IPC（`host-cold-start.json/txt`）：无 App 注册、真实 Core+DB；`target.source_id == Core sources.source_id`（"s1"）且 ≠ StableSourceId；wire 精确五命令；**15 表快照逐行相等**；脱敏。
- 未运行/保留：App 真实导入→枚举 E2E（Host 侧判别已覆盖，seed source_id 为合成 "s1"）；HostRuntime Ready/Dispose 级单测（代码审查 + 组件级真实 IPC）；**AC11-1 仍 PARTIAL**；L10 不解决；L-S1 registry resilience、L-S4 死代码保留。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC-S2-1/3/6/8 | verification/FEA-11-SCAN-2/core-shard-record.md | - | 0354fc333c62ebe062914933521ba594f0c3f14031e71eaa6e01a68ac05b877f | CANONICAL |
| EV-02 | Gate | verification/FEA-11-SCAN-2/host-changed-files.txt | - | a575f79fc1d8f65b773319af4680b692731b5fdd5ae3bb720825ce5ba32fedf6 | CANONICAL |
| EV-03 | Gate | verification/FEA-11-SCAN-2/host-cold-start.json | - | b1c1ae4dc5d77c4b39b3f5a0f17a08ff7230a9085afc849f75539a6616f07d37 | CANONICAL |
| EV-04 | Gate | verification/FEA-11-SCAN-2/host-cold-start.txt | - | d6d316f1a1dc05cd025b642e33dad141dce3aa6855551715683ee3d1e503e739 | CANONICAL |
| EV-05 | AC-S2-1 | verification/FEA-11-SCAN-2/host-r2-cold-start.json | - | b1c1ae4dc5d77c4b39b3f5a0f17a08ff7230a9085afc849f75539a6616f07d37 | CANONICAL |
| EV-06 | AC-S2-1 | verification/FEA-11-SCAN-2/host-r2-cold-start.txt | - | 9b7b241c7fc869af4bfdc5b19b0ff43bbf1c9de9d4112623c7a58c07b1c06ac2 | CANONICAL |
| EV-07 | AC-S2-3 | verification/FEA-11-SCAN-2/host-r2-import-e2e.json | - | 29672d5f7110162f1209d8d5dbb9c0bdd1ca579ef613abe29ac3ec3d0fe72378 | CANONICAL |
| EV-08 | AC-S2-3 | verification/FEA-11-SCAN-2/host-r2-import-e2e.txt | - | bc489cfe6c598bba9986b51c87a4ce55ad0a4fcffd76dfb32621810b519fdf81 | CANONICAL |
| EV-09 | AC-S2-5 | verification/FEA-11-SCAN-2/host-r2-runtime-enumeration.json | - | fc692a69c304c4522445163e76e24f2263b72f5278273b966ae0cc1032135cec | CANONICAL |
| EV-10 | Gate | verification/FEA-11-SCAN-2/host-r2-scope-validation.log | - | 45138c709e0c0e0bbd1e6969a905c943dd36f7ab5497a43da5e88a97866fc413 | CANONICAL |
| EV-11 | Gate | verification/FEA-11-SCAN-2/host-scope-validation.log | - | cdd72d4f67d8880f264e8b5d11657c2bcdd509195313601f778ed842709211f2 | CANONICAL |
| EV-12 | AC-S2-1/2/4/5/7 | verification/FEA-11-SCAN-2/host-shard-record.md | - | 7578442cd56f24c5c9e9a6722488a3cf5254f34ef7db44784fed97adb5a6963e | CANONICAL |
| EV-13 | Gate | verification/FEA-11-SCAN-2/logs/core-api-inventory.log | - | 4a5cf7c48f8da2e1540c1cbe0e61a5d6d57a24f98ead4fc887ebacbf6883cec2 | CANONICAL |
| EV-14 | Gate | verification/FEA-11-SCAN-2/logs/core-check.log | - | 6e28f045cfc97a2d4146db9f5543aa206d5d256b409befa20397aa5d809574c4 | CANONICAL |
| EV-15 | Gate | verification/FEA-11-SCAN-2/logs/core-mutation.log | - | ff57b0b3573e8ab1fe0dba23ea6ba73338e8daddca92469afc75e0e881e74a68 | CANONICAL |
| EV-16 | Gate | verification/FEA-11-SCAN-2/logs/core-pins.log | - | 5163d4739e181e5a372fa7685d11b6b41ebb174d8cc180ac0bb929fac79564bb | CANONICAL |
| EV-17 | Gate | verification/FEA-11-SCAN-2/logs/core-pytest-core-fea09.log | - | 79df1826b70ad3990c2db61694e4a7a1e77cee1e41d9c22b329d7ef33ac14cbc | CANONICAL |
| EV-18 | Gate | verification/FEA-11-SCAN-2/logs/core-pytest-core.log | - | 3f63c84162354aca53b6a0b6954816f4289810168a95ff63bd304097c43a9982 | CANONICAL |
| EV-19 | Gate | verification/FEA-11-SCAN-2/logs/core-pytest-fea09.log | - | 7f71def53c6929c0e87875816910febbb9a7fbe96eabb83b6c30b8a8c6ee68da | CANONICAL |
| EV-20 | Gate | verification/FEA-11-SCAN-2/logs/core-pytest-full.log | - | 66fae3a65d9c8f75e5998e38a035929107405b0d7736cea6f815db95e0e46155 | CANONICAL |
| EV-21 | Gate | verification/FEA-11-SCAN-2/logs/core-r2-api-inventory.log | - | 797d5d0ecaad94f984e21d4d506a700fe5cda5cb04ff0b30e2a2251a785a4f1f | CANONICAL |
| EV-22 | Gate | verification/FEA-11-SCAN-2/logs/core-r2-check.log | - | 1ec3f0ac7c4ee0b923d0080b7920e44a131289c915d9876e55115b53644d5ff2 | CANONICAL |
| EV-23 | Gate | verification/FEA-11-SCAN-2/logs/core-r2-mutation.log | - | 236f55c6e1564ea051c0bc0803a63d512471d05d84f41ca0bce1d8b17ac7fa4b | CANONICAL |
| EV-24 | Gate | verification/FEA-11-SCAN-2/logs/core-r2-pins.log | - | e5c0197168aafcf20696f237ba74f1215978d117e132d146806cba4e2c475bc9 | CANONICAL |
| EV-25 | Gate | verification/FEA-11-SCAN-2/logs/core-r2-pytest-core-fea09.log | - | 3dee7a6ada8ee8882b67338e96f31342c7fb1a7b7b4c9d1452328e72d6343c27 | CANONICAL |
| EV-26 | Gate | verification/FEA-11-SCAN-2/logs/core-r2-pytest-core.log | - | 87a3d53732cab59089fc441f5b8ac45587b9f9cfb697024207031c2f1e578721 | CANONICAL |
| EV-27 | Gate | verification/FEA-11-SCAN-2/logs/core-r2-pytest-fea09.log | - | 84f372f874d549bfa23973c61a46ff63db3836164cef976f1cadaa1e718bdae5 | CANONICAL |
| EV-28 | Gate | verification/FEA-11-SCAN-2/logs/core-r2-pytest-full.log | - | 39feb434f68f9cd9fb05ee3eb0c03b16c12a2eaed26aef8e375499a4dc4f223d | CANONICAL |
| EV-29 | Gate | verification/FEA-11-SCAN-2/logs/core-r2-scope-diff.log | - | b27f6124fd36b95a8b39f02411ca7f69d3beeade46b78dd28e9ad47abada4d34 | CANONICAL |
| EV-30 | Gate | verification/FEA-11-SCAN-2/logs/core-scope-diff.log | - | 4d14dce6a0fe4891583098678b95359b3a461b78e971bc0eece302f71a6dc028 | CANONICAL |
| EV-31 | Gate | verification/FEA-11-SCAN-2/logs/gates-integration.log | - | 8436f3c631e35f01b55e0a554b57597bbc8e0e09dc880292b0808e5f015ace1b | CANONICAL |
| EV-32 | Gate | verification/FEA-11-SCAN-2/logs/gates-r2-integration.log | - | 292e1e6a867b853f8bf643a7fa8e64f6262eb80e79ab29acef4a16acfdb20a75 | CANONICAL |
| EV-33 | Gate | verification/FEA-11-SCAN-2/logs/host-api-inventory.log | - | b4b9e68e1f7fce0dc4aeecfae9d887da0c0661b346a9434930ae62b3a2270c47 | CANONICAL |
| EV-34 | Gate | verification/FEA-11-SCAN-2/logs/host-app-refresh.log | - | 32c67251abf8c233ee055d601a17b4163c8e02c34bde3d029f908ff273c121b0 | CANONICAL |
| EV-35 | Gate | verification/FEA-11-SCAN-2/logs/host-check.log | - | b7822e3c851d010f7a0bc1a57a1ef270ede87595fd7d6d6056e0d4393365a3f4 | CANONICAL |
| EV-36 | Gate | verification/FEA-11-SCAN-2/logs/host-dotnet-baseline.log | - | 438d1adc838a4c9e18e67163046c295831daa3514aad493cb989fa9eeb4c8eec | CANONICAL |
| EV-37 | Gate | verification/FEA-11-SCAN-2/logs/host-dotnet-full-1.log | - | 522b4b55400aa2f7e15bc38a0b6a6420eefed6e67e5bb3f2b73140bedc85f1ba | CANONICAL |
| EV-38 | Gate | verification/FEA-11-SCAN-2/logs/host-dotnet-full-2.log | - | 6d8c9861f2849d355a4bf4192d32f147b12a5a1825b1faaf418ac8c4622e0f39 | CANONICAL |
| EV-39 | Gate | verification/FEA-11-SCAN-2/logs/host-dotnet-full-3.log | - | 9b032c03f5c2f9a11d8865487d79f90087add06c5e6d6895c9c423dc7de450c5 | CANONICAL |
| EV-40 | Gate | verification/FEA-11-SCAN-2/logs/host-flaky-fluent-rerun.log | - | dc9bd907d80b5aa5fb858a5c1579928336fe92b010fda751316a4f25323c2668 | CANONICAL |
| EV-41 | Gate | verification/FEA-11-SCAN-2/logs/host-flaky-fluent-rerun2.log | - | 25ea1a387b9b87a34e4f4d19024a4ebcc2b0c2d0a4ac08c0a20e7d70c9fb5214 | CANONICAL |
| EV-42 | Gate | verification/FEA-11-SCAN-2/logs/host-flaky-tilechannel-rerun.log | - | 0e440494feb268bbb8a94b89fc447aea731186471ebec58ad95cb968241d0346 | CANONICAL |
| EV-43 | Gate | verification/FEA-11-SCAN-2/logs/host-pins.log | - | f198eda409309d359a700135e0ecb1d56c6b3df8f0bed0cfcef6f7427a7336db | CANONICAL |
| EV-44 | Gate | verification/FEA-11-SCAN-2/logs/host-r2-api-inventory.log | - | b60105ac624c7e4d681a36cb45129471c16a4ed72e7751076bed4bbe818ba758 | CANONICAL |
| EV-45 | Gate | verification/FEA-11-SCAN-2/logs/host-r2-app-refresh.log | - | 9e1d385bb978299dba9f90a3ba2d69dd4160d188044efaf7403e38265279ac2f | CANONICAL |
| EV-46 | Gate | verification/FEA-11-SCAN-2/logs/host-r2-check.log | - | f46f843311c6f817f96a28792f48a75374ffe56a47b408b7c35def2c1d0a3fbb | CANONICAL |
| EV-47 | Gate | verification/FEA-11-SCAN-2/logs/host-r2-dotnet-full-1.log | - | 297626c1fbbbd29430c9569c432ec716832e3c2ac9b64223f05391ad23b1c794 | CANONICAL |
| EV-48 | Gate | verification/FEA-11-SCAN-2/logs/host-r2-dotnet-full-2.log | - | 2f5483099e8a5424af3e7595dd08f65beeaa917801d07a3dc223450e22cf6d61 | CANONICAL |
| EV-49 | Gate | verification/FEA-11-SCAN-2/logs/host-r2-dotnet-full-3.log | - | 8bd2cc10a7ea7d7ad29f9c260641d1c7b103fc4b6f6425c78777f7e95da98ee6 | CANONICAL |
| EV-50 | Gate | verification/FEA-11-SCAN-2/logs/host-r2-flaky-fluent-rerun.log | - | 25ea1a387b9b87a34e4f4d19024a4ebcc2b0c2d0a4ac08c0a20e7d70c9fb5214 | CANONICAL |
| EV-51 | Gate | verification/FEA-11-SCAN-2/logs/host-r2-flaky-runbinding-rerun.log | - | 20f8ba2824fe3e1165524a4d8f5f129f6c6534d80a298d09adbff6d1e93efdcb | CANONICAL |
| EV-52 | Gate | verification/FEA-11-SCAN-2/logs/host-r2-pins.log | - | f198eda409309d359a700135e0ecb1d56c6b3df8f0bed0cfcef6f7427a7336db | CANONICAL |
| EV-53 | Gate | verification/FEA-11-SCAN-2/logs/host-r2-pytest-fea11.log | - | da2fa25e398c7d5a3357a7b536963ee88477278f3e2ac4a26f0e3f6ee619c6a0 | CANONICAL |
| EV-54 | Gate | verification/FEA-11-SCAN-2/logs/host-r2-real-ipc.log | - | 471442c12c67bafd36b1200eb23d3c840485fe7a091ade4c5707c136378ba9c0 | CANONICAL |
| EV-55 | Gate | verification/FEA-11-SCAN-2/logs/host-r2-runtime-enumeration.log | - | f1a42bacf6507e19b570638e55e24d587cfb8b0ff1d36871cc222381115cf0e7 | CANONICAL |
| EV-56 | Gate | verification/FEA-11-SCAN-2/logs/host-r2-unit.log | - | 247c870678ef152f96dd36cf7a18e3903877a8f8e35c72cf431efcc990ac43b3 | CANONICAL |
| EV-57 | Gate | verification/FEA-11-SCAN-2/logs/host-restart-ipc.log | - | f34eb3a52608fe31ba3cd5fde09e6b45f96cbbcab1846ee8f60005cb65f48b48 | CANONICAL |
| EV-58 | Gate | verification/FEA-11-SCAN-2/logs/host-unit.log | - | ec1c5eb450b9540fa770ac17158e36e272b04c5cfd4ad2e45c53653d7cff7950 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（main 工作树实施） | NOT_APPLICABLE | — | — | 未创建独立 worktree |
| temp | `G:\CODEX\New Manga.workspace\temp\FEA-11-SCAN-2\` | DELETE_SAFE | — | verification/FEA-11-SCAN-2/logs/gates.log | 仅隔离 IPC/测试临时根；closeout 删除并记录字节数 |
| agent-output | `G:\CODEX\New Manga.workspace\agent-output\fea11-scan-2\` | PRESERVE_REFERENCED | `G:\CODEX\New Manga.workspace\agent-output\fea11-scan-2` | verification/FEA-11-SCAN-2/logs/gates.log | 过程日志副本；保留不清理 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：L-S1/L-S4、L-A/L-G、AC11-1 仍 PARTIAL、L10 不解决。
- 当前指针清理：待 DSH closeout 时更新 STATUS / Plan / TASK_LEDGER 或说明无需更新。
