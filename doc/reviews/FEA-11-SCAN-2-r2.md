---
task_id: FEA-11-SCAN-2
review: r2（窄面复审；独立上下文、只读）
reviewer: fresh subagent（未参与 SCAN-2 的实现、分片、r1 复核或 r2 返修；只读 reviewed_head）
reviewer_session: subagent-of-session-8db9dae5-49df-4d09-ac62-696f0805a95c（子会话，以 DSH 派发记录为准）
date: 2026-11-06
repo: G:\CODEX\New Manga（main）
reviewed_head: 555f57b8d138feba5154c12b3e61b1cf65a74392
reviewed_head_short: 555f57b8d
implementation_commits:
  - 0cb5177ca（r1 分片 A：Core 枚举）
  - 6c8b4cb2b（r1 分片 B：Host/App 接线；含 LibraryViewModel.cs 允许范围例外）
  - 20faf062a（r2 分片 A：P2-2 空 project_ids typed skip）
  - 196793e01（r2 分片 B：P1-1/P2-1/P2-3/P2-5 + P2-4 措辞）
integration_commit_reviewed: 555f57b8d（Lead r2 集成提交：卡/台账/门禁日志）
base_commit: 703d9eb12
contract: doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md v1.1
contract_sha256: aefa0fa5b17e0f10d9f23aebc3146c98c3c2bc170f2a18154d56a148e9701a59（与 pin 一致）
decision: approve
severity_counts: P0=0 P1=0 P2=0 P3=14（均为文档/证据口径与 closeout 建议，见 §6）
repo_state_at_end: clean（HEAD 555f57b8d；未 commit、未 push；变异仅临时改源码并 `git checkout --` 还原，`git diff` 为空）
review_workspace: G:\CODEX\New Manga.workspace\FEA-11\review-scan-2-r2\（logs/、mut-core/、evidence/；仓外）
---

# FEA-11-SCAN-2 r2 窄面复审（独立、只读）

## 0. 结论摘要

- **Decision: `APPROVE`（P0=0 / P1=0 / P2=0 / P3=14）。**
- r1 的 **P1-1（多 book 共享源被硬编码 `scope=current` 拒绝）已真实修复**：`ResolveScanScope` 按 `ProjectIds.Count` 选 `current`(1)/`all`(>1)，scan 与 missing 共用同一 payload builder；帧级测试 3 例齐全；我独立复跑真实 IPC，并从 wire 解析出同一真实源的两次 `ScanSourceSync`：单 book `scope=current`+1 个 project，共享源 `scope=all`+恰好两个 book，两次 Core 响应均 `source.status=ok`。**变异（改回硬编码 current）使 2 个 payload 单测与真实共享源 E2E 同时转红**。
- **P2-1 已修复**：`_refreshPending` coalesce + `TickAsync` 释放单飞门后重放；竞争窗口测试证明 tick 中 Refresh 不丢、新 target 随后被枚举/扫描。我以“删掉 pending 置位”变异使该测试转红（恢复 r1 丢弃行为）。
- **P2-2 已修复**：Core `list_scan_targets` 对去重后空 `project_ids` typed skip 并计数 `project_ids_empty`；我以“删除空 skip”变异使 2 条测试转红（与入库变异记录一致）。
- **P2-3 已由真实 E2E 核销**：真实 Python Core（`src` 当前源码、stdio）+ 生产 `SourceImportCoordinator` + 真实 PNG 导入两个 book；`target.source_id == Core sources.source_id`（`src-uuid`）且 `!= StableSourceId`；两 book 集合一致、Refresh 幂等、15 表快照前后相等。**不是 stub**；`wire.ndjson` 可独立复核。
- **P2-4 已按 r1 处置核销**：`LibraryViewModel.cs` 作为编译必需连带修改的 allowlist 例外已在卡面、`host-shard-record.md` §10.5、`host-changed-files.txt` 明示；r2 未再次改动它，代码未回退。
- **P2-5 已按 r1 的“补 gated HostRuntime 用例”分支处置**：新 gated 用例真实启动 `HostRuntime`（真实 sidecar），证明 Ready 后后台枚举确实执行、typed fail-closed（`CORE_CAPABILITY_MISSING`）、scheduler 启动、refresh/tick 可用；成功枚举路径由组件级真实 Core E2E 补足，limitation 已登记。措辞有一处不准确（“无……时钟 seam”，实际 `HostOptions.SourceScanTimeProvider` 存在时钟 seam），属 P3 文档修正，不改变结论。
- **门禁独立复跑全部通过**：全量 pytest **3212 passed / 10 skipped**（EXIT 0）、`tests/fea11` **108 passed**；全量 .NET **1500 passed / 0 failed / 85 skipped**（EXIT 0，**我这首跑即干净，无需 flaky 复跑**）；`check.ps1 -TaskPath` / `check.ps1` PASS（3 既有 warnings）、pins **18/18**、API inventory PASS、scope diff 空、**EV 58/58 sha256 MATCH**；工作树 clean、未 push。
- 剩余问题均为**文档/证据口径**（r2 证据表仍指 r1 日志、EV-09 的 AC 映射错、卡面引用了另一次 E2E 运行的随机 ID、P2-5 limitation 的时钟 seam 表述等），已列入 §6 的 closeout 最小收口清单；**不需要再改生产代码**。

## 1. r1 findings 核销（逐项独立核验）

| r1 ID | r1 内容 | r2 处置 | 我的核验 | 判定 |
|---|---|---|---|---|
| P1-1 | `ScanAsync/ScanMissingAsync` 硬编码 `scope="current"` + 全部 project_ids，多 book 共享源永远 `INVALID_REQUEST` | `ResolveScanScope`（`SourceScanScheduler.cs:949`）按 `ProjectIds.Count==1?current:all`；scan/missing 统一走 `WriteScanSyncFields`/`WriteScanMissingFields`；新增 3 个帧级测试 + 真实导入共享源 E2E | 代码审阅；单测复跑；真实 IPC 3/3 PASS；解析 wire 两次帧（见 §2.1）；变异转红 | **已核销** |
| P2-1 | tick 运行中 Refresh 被 `WaitAsync(0)` 丢弃 | `_refreshPending`（`SourceScanScheduler.cs:208`）+ `ReplayPendingRefreshAsync`（472-500）+ `TickAsync` wrapper（516-538）释放门后重放 | 竞争窗口测试复跑 PASS；删除 pending 置位的变异使测试转红 | **已核销**（一处 XML 注释过时，P3-7） |
| P2-2 | Core 枚举产出 `project_ids=[]`，违反 C-17 §5 1..20 | `scanner.py:147-155` typed skip + `project_ids_empty` 计数；新增 `test_source_without_bindings_is_typed_skipped` 并补既有用例 | 复跑 Core 9/9；删除空 skip 变异 → 2 failed / 7 passed，同时目测确认空 target 重新出现 | **已核销** |
| P2-3 | AC-S2-3 真实导入 E2E 未跑（seed 合成 "s1"） | 新 gated `RealImportThenEnumeration_SharedSource_UsesAllScope_AndCoreSourceId`（真实 Core + 生产 `SourceImportCoordinator`） | 独立复跑 1/0/0；检查 fixture 的 `wire.ndjson`、`import-e2e.json`、DB 查询；两 book 集合/幂等/15 表零写均被测试断言；**非 stub** | **已核销**（App VM→Host Runtime 触发链仍由 VM 单测覆盖，见 §2.4） |
| P2-4 | `LibraryViewModel.cs` 越界且 shard record 表述失实 | 卡面 r1 处置记录 allowlist 例外；shard record §1 改为“含 1 个编译必需连带文件”，§10.5 明示；changed-files 增 Allowlist exception 段；r2 未再改该文件 | 分类核对；确认该文件仍保留 r1 的编译必需修改、r2 commit 未触碰；未回退代码 | **已核销**（AC-S2-9 字面仍可加一 clause，P3-4） |
| P2-5 | AC-S2-1 “新 Host 进程 Ready”仅组件级 | 新 gated `Fea11Scan2HostRuntimeTests.Ready_StartsBackgroundEnumeration_WithoutBlocking`（`[HostSidecarFact]`，真实 sidecar） | 独立复跑 1/0/0；解析新生成的 `host-r2-runtime-enumeration.json`：ready=true、482ms、枚举执行、`CORE_CAPABILITY_MISSING`、redacted；limitation 已登记 | **已核销**（limitation 的“时钟 seam”表述需修正，P3-8；“非阻塞”证据强度，P3-9） |

**r1 P3 落实情况（概要）**：P3-3（HostRuntime 过期注释）已修；P3-4（VM 测试名）已改名并加 S-2 注释（未补“在途切换”动作，但 S-2 已移除 selection 语义，可接受）；P3-1（wirelog grant/session 与 AC-S2-8 措辞）与 P3-5（14 vs 15 表）**未处理**，见本报告 P3-5/P3-6；P3-2（targets 只增不减、refresh 无停机取消）**未登记为 limitation**，见 P3-13；P3-6（generation-drift 注释）已补，`RegisterSourceScanTarget` 仍无生产调用方（非阻断清理项）。

## 2. 窄面独立验证（我的实跑，不引用卡面结论）

### 2.1 P1-1：共享源 scope 选择与真实 IPC

**代码事实**
- `SourceScanScheduler.cs:946-950`：`ResolveScanScope(target) => target.ProjectIds.Count == 1 ? "current" : "all"`；`WriteScanSyncFields`（988）与 `WriteScanMissingFields`（1003）都调用它；`ScanAsync`（1132-1137）与 `ScanMissingAsync`（1254-1259）只调用对应 builder，无第二套 scope 字面量。
- `TryMap`（1570-1645）保留 Core 返回的 project_ids 顺序；Core 枚举按 `source_id`/project 排序，`scope=all` 的冻结引用集合等值判断成立（E2E 已实证）。

**独立真实 IPC 复跑**
- 命令：`$env:NEWMANGA_FEA11_IPC=1; dotnet test … --filter "FullyQualifiedName~Fea11ScanIpcTests"` → **3 passed / 0 failed / 0 skipped，EXIT 0**（`logs/r2-real-ipc.log`）。
- 我在**自己这一轮**生成的 fixture `scan-import-4a0203de…` 中解析 `wire.ndjson`（不是读入库证据）：
  - `ScanSourceSync` 恰 2 帧，同一真实源 `source_id=src-5e638e35b4604f618f44649afc6b493a`；
  - 第 1 帧：`scope=current`，`project_ids=[9d8fd3b39b0a48bc9efecbd3215d0445]`，`grant_ids=[source-d7a9e922…]`，Core 响应 `source.status=ok`；
  - 第 2 帧：`scope=all`，`project_ids=[67708f474ac246af8e9f963cd4818a00, 9d8fd3b39b0a48bc9efecbd3215d0445]`，Core 响应 `source.status=ok`，且响应的 `bases` 恰含两个 book；
  - 该 fixture 的 `source_list_scan_targets` 调用 3 次（Refresh 幂等），无 plan/apply/删除帧。
- fixture 的 `import-e2e.json`：`core_source_id=src-5e638e35…`、`stable_source_id=src-88c3c0a08d1349bc`、`books` 两个、`single_book_scope=current`、`shared_book_scope=all`、`db_snapshot_unchanged=true`。因每次运行随机 UUID 不同，ID 与入库证据不同属正常。

**变异（改回硬编码 current）**
- 临时把 `ResolveScanScope` 改为恒返回 `ScopeCurrent`，重建后：
  - 3 个 payload 单测：**2 failed / 1 passed**（`ScanPayload_SharedSource_…` 与 `MissingPayload_UsesSameScopeSelection_…` 的 `Assert.Equal` 失败）；
  - gated 真实共享源 E2E：**1 failed**（`Assert.NotEqual` 失败，即 tick 后 `LastResult == Error`，定位到 Core 以 `INVALID_REQUEST` 拒绝了 `scope=current` + 两 project 的帧，复现了 r1 的原始缺陷）；
- `git checkout --` 还原后重建、`git diff` 为空，工作树 clean。

### 2.2 P2-1：coalesce 与 Tick 后重放

- 代码：gate 竞争失败时在 `_gate` 下置 `_refreshPending`（354-367）；`TickAsync` 在 finally 释放 `_tickGate` 后 `await ReplayPendingRefreshAsync`（524-537）；重放读取并清 pending，再跑一次 `RefreshTargetsAsync`，异常只记 typed 日志（472-500）。
- 独立复跑 `RefreshRequestedDuringTick_IsReplayedAfterTickCompletes`：**PASS**；该测试用真实 `SourceScanScheduler` + 阻塞 `FakeScanExecutor`，tick 持门时 Refresh 返回 false 并入队，tick 完成后 `enumerator.Calls==1`、新 target 出现并在下一 tick 实际扫描（`ScannedSourceIds` 含 `s2`）。
- 变异：删除 gate-busy 分支的 `_refreshPending = true`（恢复 r1 丢弃行为）→ 该测试 **1 failed**；还原后 clean。
- 观察（P3-13）：若在**另一个 Refresh**（而非 tick）在途时收到 Refresh，`_refreshPending` 会在该 Refresh 结束后保留，直到**下一次 tick 的 wrapper** 才重放；不会永久丢失（周期 tick 必然重放），但最多延迟一个 interval。r1 的最小修复正是“Tick 后重放”，当前实现符合；建议 closeout 记 limitation 或后续把重放也挂到 Refresh 完成处。

### 2.3 P2-2：Core 空 project_ids typed skip

- 代码：`scanner.py:140-155` 先对 `candidate["project_ids"]` 去重排序，空集合 `project_ids_empty += 1` 后 `continue`，不进入 targets；stderr 仅在有 skip 时输出计数行。
- 独立复跑 `pytest tests/core/test_core_scan_target_commands.py`（隔离副本）：**9 passed**。
- 变异（删除空 skip 块）：**2 failed / 7 passed**——空源以 `project_ids=[]` 重新出现，`test_typed_skips_…` 与 `test_source_without_bindings_is_typed_skipped` 均红；与入库 `logs/core-r2-mutation.log` 的 `2 failed, 7 passed` 一致；还原后副本文件 sha256 与原文件一致。

### 2.4 P2-3：真实导入 → 枚举 E2E 的真实性

**装置真实性（逐项）**
- 真实 Core：`CoreServiceClient.StartAsync` 以 `C:/Python314/python.exe -X utf8 -c "sys.path.insert(0, <repo>/src); import bootstrap.core_service as m; raise SystemExit(m.main())"` 启动真实 Core 进程；有独立 DataRoot/DB、`core.stderr.log`、`wire.ndjson`。
- 生产导入器：`SourceImportCoordinator` 位于生产代码 `apps/desktop-avalonia/src/NewManga.App/Services/SourceImportModels.cs:538`（非测试 fake）；E2E 走 `PlanImportReferences` → `StartImportReferences` → `GetImportReceipt` 的真实操作链。
- 真实源：写入一个 1×1 PNG（base64 解码为真实文件），同一物理文件先后导入 book1/book2。
- Core 权威：`QuerySingleSourceId` 直接只读查询真实 `library.db` 的 `sources` 表；断言恰好 1 个 `src-uuid`，且 `target.source_id` 等于它、不等于 App 侧 `ExpectedStableSourceId(path)`。
- 两 book 集合：`QueryBookIdsForSource` 从 `page_bindings` join `pages/chapters` 读出两个 book，断言恰为两本。
- 幂等：第 3 次 `RefreshTargetsAsync` 后仍 `Single(target)`。
- 15 表零写：`QueryScanTables` 列 15 张 C-17 相关表（含 `source_sync_plans`/`source_operations`/`regions`/`rendition_cache` 等），`QueryScanSnapshot` 序列化全部行，Refresh+scan 前后 `Assert.Equal`。
- `db_snapshot_unchanged=true` 且 `wire.ndjson` 中 ScanSourceSync 只有两帧、无 plan/apply/delete 业务帧（导入自身的 Plan/Start 帧属预期）。
- 变异判别：见 §2.1，硬编码 current 时该 E2E 直接失败，说明它不是“恒真”的装饰测试。

**口径说明（不构成阻断）**
- E2E 直接驱动生产 `SourceImportCoordinator` 与 `SourceScanScheduler`，未经过 App 的 `ImportDockViewModel`→`HostController`→`HostRuntime.RequestSourceScanRefresh` 这条 UI 触发链；该链由既有 VM 单测（5 例）覆盖。AC-S2-3 的核心语义（source_id 权威 + ≠ StableSourceId）已被真实 Core E2E 覆盖。
- 只覆盖单文件 PNG，不覆盖 folder/加密源（卡面 §10.9 已如实登记）。

### 2.5 P2-4：allowlist 例外记录

- `LibraryViewModel.cs` 在 `6c8b4cb2b` 中被修改（删除 `bookId:` 传参），该文件**不在**冻结 `allowed_paths`；r2 的 `196793e01` **没有**再改它（`git log 6c8b4cb2b..HEAD -- <file>` 为空）。
- 证据位置：
  - 卡面 `doc/tasks/FEA-11-SCAN-2.md` §“r1 Review 处置” P2-4（Lead 记录 allowlist 例外，不回退代码）；
  - `verification/FEA-11-SCAN-2/host-shard-record.md` §1（“含 1 个编译必需连带文件”）与 §10.5（明确“不在冻结 allowed_paths”）；
  - `verification/FEA-11-SCAN-2/host-changed-files.txt` 的 `## Allowlist exception (r1 P2-4, recorded by Lead)`。
- 代码未回退：`git diff 703d9eb12..HEAD -- LibraryViewModel.cs` 仍保留 r1 的编译必需修改。**P2-4 已核销。**

### 2.6 P2-5：gated HostRuntime 用例与 limitation

- 新测试 `Fea11Scan2HostRuntimeTests.Ready_StartsBackgroundEnumeration_WithoutBlocking`（`[HostSidecarFact]`，需要 `NEWMANGA_CORECLIENT_SIDECAR_DIR`）真实启动 `HostRuntime.StartAsync`，断言 `Result.IsReady`、`ScanScheduler` 非空、枚举状态最终非空、typed code 非空（旧 sidecar 为 `CORE_CAPABILITY_MISSING`）、`RequestSourceScanRefresh()` 被接受、随后 tick 可运行、序列化状态无绝对路径。
- 我独立复跑（sidecar：`apps/desktop-avalonia/build/sidecar/core-sidecar/core-sidecar`）：**1 passed / 0 failed / 0 skipped，EXIT 0**（`logs/r2-runtime-enumeration.log`）；独立生成证据：
  `ready=true, start_elapsed_ms=482, enumeration_present_immediately_after_start=true, enumeration_available=false, enumeration_error_code=CORE_CAPABILITY_MISSING, scheduler_started=true, redacted=true`。
- 与入库 `host-r2-runtime-enumeration.json`（`enumeration_available=false`、`CORE_CAPABILITY_MISSING`）语义一致；**成功枚举**由组件级真实 Core E2E（`host-r2-cold-start.json` 与我复跑的一致：枚举 available=true、target=s1、五命令、15 表相等）与 §2.4 的真实导入 E2E 补足。
- **limitation 措辞问题（P3-8）**：shard record §10.4/卡面写“无 fake-Core/注入时钟 seam”。实际上 `HostOptions.SourceScanTimeProvider`（`HostOptions.cs:110-111`）是公开时钟 seam，HostRuntime 也把它传给 scheduler；不成立的是 **fake-Core seam**（`HostRuntime` 内部 `SidecarLocator`/`CoreServiceClient.StartAsync` 装配，无 client 注入口）。建议 correct 为“无 fake-Core seam；时钟 seam 存在但不解决成功枚举（仍受 sidecar 版本限制）”。
- **证据强度观察（P3-9）**：提交的 JSON 显示 `enumeration_present_immediately_after_start=true`，即 `StartAsync` 返回时枚举已完成；因此该用例证明“Ready 后枚举执行 + typed fail-closed”，而“非阻塞”主要由代码路径（Ready 末尾 fire-and-forget、`Start()` 之后 `_ = RefreshSourceScanTargetsAsync`）支撑，不是该 JSON 判别的。limitation 未声称相反事实，故不阻断；建议 closeout 措辞避免把“非阻塞”归因给该用例。

## 3. 独立复跑门禁（我的实跑）

命令均在仓根 `G:\CODEX\New Manga`；日志在仓外 `G:\CODEX\New Manga.workspace\FEA-11\review-scan-2-r2\logs\`。

| # | 命令 | 结果 | 日志 |
|---|---|---|---|
| 1 | `C:\Python314\python.exe -m pytest tests -q -p no:cacheprovider --tb=short` | **3212 passed / 10 skipped / 10 warnings，243.33s，EXIT 0** | `r2-pytest-full.log` |
| 2 | `python -m pytest tests/fea11 -q -p no:cacheprovider` | **108 passed，8 warnings，5.51s，EXIT 0** | `r2-pytest-fea11.log` |
| 3 | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` | **0 warning / 0 error，EXIT 0** | `r2-dotnet-build.log` |
| 4 | `dotnet test …NewManga.sln -c Release --no-build` | **1500 passed / 0 failed / 85 skipped，EXIT 0**；分程序集：Appearance 21、Presentation 38、ThemeEngine 253、DesignSystem 117、ApplicationCore 31、Host 158+54 skip、CoreClient 167+24 skip、App 715+7 skip；**首跑干净，无 flaky，无需复跑**；跑后已 `git checkout -- verification/FEA-09` | `r2-dotnet-full.log` |
| 5 | `NEWMANGA_FEA11_IPC=1 dotnet test … --filter "FullyQualifiedName~Fea11ScanIpcTests"` | **3 passed / 0 failed / 0 skipped，EXIT 0**（含真实导入共享源 E2E、冷启动、周期扫描） | `r2-real-ipc.log` |
| 6 | `NEWMANGA_CORECLIENT_SIDECAR_DIR=… dotnet test … --filter "FullyQualifiedName~Fea11Scan2HostRuntimeTests"` | **1 passed / 0 failed，EXIT 0** | `r2-runtime-enumeration.log`、`evidence/host-r2-runtime-enumeration.json` |
| 7 | `dotnet test … --filter "FullyQualifiedName~SourceScanScheduler"` | **51 passed / 0 failed / 0 skipped，EXIT 0** | `r2-host-unit.log` |
| 8 | `dotnet test … --filter "FullyQualifiedName~Fea11ScanRefreshVm"` | **5 passed / 0 failed / 0 skipped，EXIT 0** | `r2-app-refresh.log` |
| 9 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-SCAN-2.md` | **PASS（3 既有 warnings），EXIT 0** | `r2-check-task.log` |
| 10 | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS（3 既有 warnings），EXIT 0** | `r2-check.log` |
| 11 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PIN AUDIT: PASS (all 18)，EXIT 0**；C17 pin `aefa0fa5b17e` | `r2-pins.log` |
| 12 | `python tools/generate_api_inventory.py --check` | **PASS，EXIT 0**（C-07 未变） | `r2-api.log` |
| 13 | `git diff --name-only 703d9eb12..HEAD -- doc/plan doc/contracts src/infrastructure/sqlite/schema.py` | **空（0 文件），EXIT 0** | 见 §4 |
| 14 | EV 58 行 sha256 复算 | **58/58 MATCH**；C-17 文件 sha256 = `aefa0fa5…1a59`（pin 一致） | 见 §4 |

- 每轮全量 .NET 后已执行 `git checkout -- verification/FEA-09`；Review 结束时 `git status --porcelain` 为空。
- 我的全量 .NET 首跑即 1500/0/85，未出现卡面 RUN1/RUN2 的 `RunBindingFixTests`/`FluentResidual2VisualEvidenceTests` flaky；这也说明 r2 的分片 flaky 记录是环境/时序问题，不是 r2 代码缺陷。

## 4. 证据、范围与纪律

**Canonical Evidence**
- 卡面 58 行 EV（EV-01…EV-58）逐行复算 sha256：**58/58 MATCH**，无缺失、无错配。
- C-17 v1.1 文件 sha256 = `aefa0fa5b17e0f10d9f23aebc3146c98c3c2bc170f2a18154d56a148e9701a59`，与 pinned 值一致。
- 新 r2 证据文件的字节与对应 EV 一致（如 `host-r2-import-e2e.json` = EV-07、`host-r2-runtime-enumeration.json` = EV-09、`gates-r2-integration.log` = EV-32）。
- 我另外独立生成了 fresh fixture（`scan-import-4a0203de…` 真实导入 E2E、`scan-284f7251…` 冷启动）与自有 `host-r2-runtime-enumeration.json`，与入库证据语义一致；这些 fresh 产物全部在仓外 workspace，未写入仓库。

**范围（`git diff --name-only 703d9eb12..HEAD` 逐文件分类）**
- r2 两个实现提交：
  - `20faf062a`：`src/application/sources/scanner.py`、`tests/core/test_core_scan_target_commands.py`、`verification/FEA-11-SCAN-2/core-shard-record.md` + `logs/core-r2-*` → 均在 `allowed_paths`。
  - `196793e01`：`HostRuntime.cs`、`SourceScanScheduler.cs`、`Host.Tests/Fea11Scan2HostRuntimeTests.cs`、`Fea11ScanIpcTests.cs`、`SourceScanSchedulerTests.cs`、`App.Tests/FakeHostController.cs`、`host-*` 证据 → 均在 `allowed_paths`（`tests/**` 与 `verification/**` 范围内）。
  - `555f57b8d`：`doc/TASK_LEDGER.md`、`doc/tasks/FEA-11-SCAN-2.md`、`gates-r2-integration.log` → Lead 保留的指针/卡/证据（卡面 §允许修改范围明确 Lead 保留 STATUS/PLAN/LEDGER/reviews/契约）。
- 全范围唯一不在 `allowed_paths` 的实现文件是 `apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/LibraryViewModel.cs`，属 r1 已记录、r2 未再改的 allowlist 例外；`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md` 属 Lead 保留指针。**无新增越界。**
- `doc/plan`、`doc/contracts`、`src/infrastructure/sqlite/schema.py` 相对 `703d9eb12..HEAD` 零 diff；无新依赖、无 schema/migration/索引改动；无真实用户数据/回收站访问。
- 未 push：本地 `main` 相对 `origin/main`（未 fetch）领先 969，Review 期间无任何 push 操作；工作树 clean。

**纪律**
- Review 全程只读；仅在变异测试中临时修改 `SourceScanScheduler.cs`（P1-1/P2-1 各一次）与仓外副本 `scanner.py`（P2-2），每次均 `git checkout --` / 副本 `.orig` 还原；结束时 `git diff` 为空、`git status` clean、HEAD 仍为 `555f57b8d`。Core 变异在仓外 `mut-core/` 副本执行，副本还原后与仓内原文件 sha256 一致。
- 未修改任务卡/STATUS/PLAN/LEDGER/verification 证据字节；所有日志/变异在仓外。

## 5. AC 与 Limitation 判定

| AC | 判定 | 依据/限定 |
|---|---|---|
| AC-S2-1 冷启动枚举 | **MET（限定）** | 组件级真实 Core 冷启动：枚举 available=true、target 与五命令白名单、15 表零写（EV-05/06，我复跑一致）；HostRuntime 级 gated 用例证明 Ready 后枚举执行与 typed fail-closed（EV-09），但**成功得到 targets 的 HostRuntime 运行级证据仍由组件级 E2E 补足**；limitation 已登记（见 P3-8/P3-9 的措辞修正） |
| AC-S2-2 合并/去重/幂等 | **MET** | Refresh 按 source_id 覆盖/新增；重复 Refresh 幂等；P2-1 竞争窗口已修复并有判别测试；App Completed 恰一次 Refresh（VM 5 例）。观察：Refresh 在途时的 pending 重放要等下一次 tick wrapper（P3-13） |
| AC-S2-3 source_id 权威（S-2） | **MET** | 真实导入 E2E：`src-5e638e35…` == target.source_id，≠ `src-88c3c0a08d1349bc`；两 book 集合、幂等、15 表零写；真实 Core + 生产 `SourceImportCoordinator`；App VM→Host 触发链由 VM 单测覆盖，未纳入同一 E2E |
| AC-S2-4 registry 授权核验 | **MET** | r1 已核验；r2 未改相关逻辑；`TryMap` 与 `VerifyEnumeratedTarget` 双重点验，撤销/代次漂移 typed skip；真实 IPC 通过 |
| AC-S2-5 启动前缺失/替换（S-1②） | **MET** | r1 已核验；`SOURCE_REGISTRY_UNAVAILABLE` fail-closed、不发 ScanSourceSync、不伪造 missing；L-S1 保留 |
| AC-S2-6 共享源 project_ids 边界 | **MET** | >20 两端 typed skip（Core `project_ids_over_limit`、Host `TryMap`）；=0 Core 新增 typed skip；≤20 共享源现在真实可扫描（scope=all，E2E 验证）；不截断/不回退 current |
| AC-S2-7 预算/单飞/退避/取消 | **MET** | 8 目标/256MiB、单飞、Skipped 不 backoff、注入时钟零 sleep；r2 未破坏；refresh 的 `CancellationToken.None` 与 targets 只增不减仍是既有 P3 limitation（P3-14） |
| AC-S2-8 零写/脱敏 | **MET（限定：措辞）** | 15 表逐行相等；日志/状态无路径/凭据/secret；但 wirelog 保留 `grant_id`/`host_session_id`/`core_session_id`/`signature` 原文（C-16 §7 口径），AC 字面“无 grant/session 原文”严格不成立；14 vs 15 表集合不同（并集覆盖）；建议 closeout 加限定语（P3-5/P3-6，r1 P3-1/P3-5 未处理） |
| AC-S2-9 门禁与回归 | **MET（限定：范围口径）** | 我独立复跑全部门禁 PASS；scope diff 空；但 AC 字面“scope 仅本卡 allowed_paths”未涵盖已记录的 `LibraryViewModel.cs` allowlist 例外（P3-4）；测试要求表仍指 r1 日志（P3-2）；EV-09 的 AC 映射错（P3-3） |
| AC11-1 | **PARTIAL（维持）** | `doc/tasks/FEA-11.md` 仍为 `closed_with_limitations` 且 AC11-1 PARTIAL；本卡只闭合冷启动枚举半边，watcher/访问前策略未承接；不借本卡回填 |
| L10 | **不解决（维持）** | 真实 referenced 图源/rendition 留待后续卡 |
| L-S1 / L-S4 | **保留（维持）** | registry 整库不可读的韧性、`refresh_source_location_auth` 死代码；卡面已登记 |

## 6. P3 / closeout 最小收口清单（不阻断代码，均为文档/证据口径）

1. **P3-1（E2E 随机 ID 与 canonical EV 不一致）**：卡面 §r2 与 `host-shard-record.md` §10.3 引用了 `src-b1e32669…`/`src-d902593b…`（来自 11:36 的一次 fixture `scan-import-b1ef6577…`），而 canonical EV-07/08（`host-r2-import-e2e.json/.txt`）是 11:47 另一次运行（`src-073de0ab…`/`src-21a8ffeb…`）；两者都真实但不应把非 canonical 的随机 ID 写成证据。建议 closeout 改为引用 EV-07 的值，或写“运行期随机 `src-<uuid>`（形如 …）”。
2. **P3-2（r2 门禁证据指针过时）**：卡面“测试要求”表（全量 Python 3212 / 全量 .NET 1500 行）仍指向 r1 的 `logs/core-pytest-full.log`、`logs/gates-integration.log`、`logs/host-dotnet-full-3.log`；应改指 `logs/core-r2-pytest-full.log`、`logs/gates-r2-integration.log`（EV-32）、`logs/host-r2-dotnet-full-3.log`。
3. **P3-3（EV-09 AC 映射错）**：卡面把 `host-r2-runtime-enumeration.json`（P2-5 HostRuntime typed fail-closed）标为 `AC-S2-5`；AC-S2-5 的证据应是 unit 测试/host-shard-record（EV-12）或另补 S-1② 证据。建议把 EV-09 改为 `AC-S2-1/Gate` 或重标。
4. **P3-4（AC-S2-9 字面口径）**：AC-S2-9 仍写“scope diff 仅本卡 allowed_paths”，未提已记录的 `LibraryViewModel.cs` 例外；closeout 建议加“（含已记录 allowlist 例外 `LibraryViewModel.cs`，编译必需、未回退）”。
5. **P3-5（AC-S2-8 措辞）**：wire NDJSON 按 C-16 §7 保留 grant/session ID；建议 AC 改为“无路径/凭据/secret 原文；grant/session ID 按 C-16 §7 冻结口径”。
6. **P3-6（14 vs 15 表）**：Core 14 表集合与 Host 15 表集合不同（并集覆盖）；卡面写清“并集覆盖、非同一口径”。
7. **P3-7（注释过时）**：`SourceScanScheduler.RefreshTargetsAsync` 的 XML 注释仍写 “an overlapping request is merged, never queued”，与 r2 的 pending/队列语义矛盾；改为“coalesced and replayed after the in-flight pass”。
8. **P3-8（P2-5 limitation 的时钟 seam）**：`HostOptions.SourceScanTimeProvider` 是存在的时钟 seam，HostRuntime 已注入；不成立的是 fake-Core seam。建议把“无 fake-Core/注入时钟 seam”改为“无 fake-Core seam；时钟 seam 存在但不解决成功枚举（sidecar 版本限制）”。
9. **P3-9（“Ready 非阻塞”证据强度）**：提交的 `host-r2-runtime-enumeration.json` 显示 `enumeration_present_immediately_after_start=true`（枚举在 StartAsync 返回前已解析），该用例不能用来判别“非阻塞”；非阻塞由代码路径支撑。建议 closeout 不把该用例表述为“非阻塞判别证据”。
10. **P3-10（scope 证据头部过时）**：`host-r2-scope-validation.log` 写 “HEAD at r2 delivery: 20faf062a”，实际 Host 分片交付是 `196793e01`（`20faf062a` 是 Core r2）；建议修正或注明。
11. **P3-11（shard record 交叉引用/拼写）**：§1 写“见 §2 P2-4 例外”，实际 P2-4 讨论在 §10.5；`host-r2-scope-validation.log` 的 “ookId” 应为 “bookId”（纯排版）。
12. **P3-12（STATUS/PLAN 未更新）**：`doc/STATUS.md` 仍引用 r1 数字（pytest 3211、.NET 1496）并写“独立 Review 中”；r2 集成提交未更新 STATUS/REBASELINE_PLAN。closeout 必须更新当前 Task 状态/r2 数字/AC 指针（Lead 保留文件）。
13. **P3-13（limitation 候选）**：Refresh 在途时收到的 Refresh 只在**下一次 tick** 重放（不丢失但可能延迟一个 interval）；`RefreshSourceScanTargetsAsync` 用 `CancellationToken.None`，停机不取消在途枚举；targets 只增不减；建议一并登记为 limitation（r1 P3-2 未处理）。
14. **P3-14（App 触发链）**：P2-3 的 E2E 直接调用 `SourceImportCoordinator`/`SourceScanScheduler`，未覆盖 App `ImportDockViewModel`→`HostController`→`HostRuntime` 的完整 UI 链；该链由 5 个 VM 单测覆盖，closeout 记录“真实导入 E2E 为组件级生产编排，App UI 触发母由 VM 覆盖”。

## 7. 复核边界

- 本 Review 只读 reviewed_head `555f57b8d`；所有独立运行在仓外 workspace 生成；变异仅临时改源码并已还原（`git diff` 空、工作树 clean），Core 变异在仓外副本执行。
- 未复核：真实 Avalonia UI 手工导入、真实用户数据/AppData、旧 Core 兼容矩阵实跑（仅 capability 缺失/旧 sidecar 路径由既有测试覆盖）、folder/加密源的真实导入 E2E、多轮真实重启的长期稳定性。
- 未 fetch 远端；`origin/main` 引用仅用于说明本地领先，不能作为远端事实；Review 期间无 push。
- 我的独立日志：`G:\CODEX\New Manga.workspace\FEA-11\review-scan-2-r2\logs\r2-*.log`；变异日志：`r2-mut-p11-unit.log`、`r2-mut-p11-e2e.log`、`r2-mut-p21.log`、`r2-mut-core-p22.log`、`r2-mut-core-baseline.log`；独立证据：`evidence/host-r2-runtime-enumeration.json`、fresh fixtures 见 §2。

## 8. Closeout 建议

- **Decision 基础上可 closeout**；无 P0/P1/P2 代码返修点。
- `delivery_head`：建议 **`555f57b8d`**（最终 r2 交付，含实现合并、证据重签、卡与台账；实现 commit 链 `0cb5177ca`/`6c8b4cb2b`/`20faf062a`/`196793e01`）。
- `integration_commit`：建议 **`555f57b8d`**（Lead r2 集成提交；若项目惯例要求“集成=最终 closeout 提交”，则在 closeout 提交后再更新为那个 hash，并在卡面区分 `delivery_head` 与 closeout 提交）。
- `canonical_evidence_status`：closeout 时重跑/核对 EV 58 行（当前 58/58 MATCH）→ `complete`；若 closeout 改卡/证据字节，必须重签受影响 EV。
- `resource_closeout_status`：按 Resource Manifest 清理 `G:\CODEX\New Manga.workspace\temp\FEA-11-SCAN-2\`（DELETE_SAFE，记录字节数）；`agent-output/fea11-scan-2` 保留（PRESERVE_REFERENCED）；无 worktree。
- **AC 定稿建议**：
  - AC-S2-1：`MET（限定：HostRuntime Ready→后台枚举由 gated 用例证明；成功得到 targets 由组件级真实 Core 冷启动 E2E 补足；HostRuntime 运行级成功路径未纳入）`。
  - AC-S2-3：`MET（真实导入 E2E：真实 Core + 生产 SourceImportCoordinator；App UI 触发链由 VM 单测覆盖；单文件 PNG 口径）`。
  - AC-S2-6：`MET`（0 空集合 skip + ≤20 shared scope=all 可扫描 + >20 typed skip）。
  - AC-S2-9：`MET（含已记录 allowlist 例外 LibraryViewModel.cs）`；同时修正 §6 P3-2 证据指针与 P3-3 EV 映射。
  - AC-S2-8：`MET（限定：wirelog grant/session ID 按 C-16 §7 口径；14/15 表并集覆盖）`。
  - 其余 AC 维持 MET；**AC11-1 仍 PARTIAL**、**L10 不解决**、**L-S1/L-S4 保留**。
- **limitation（closeout 应保留/新增）**：L-S1、L-S4、L-A/L-G、L10、AC11-1 PARTIAL；新增/明确：HostRuntime 运行级成功枚举未证明（组件级补足）、真实导入 E2E 仅单文件 PNG 且未含 App UI 触发链、Refresh 在途 pending 重放到下一 tick、refresh 不绑定停机 token、targets 只增不减、14/15 表快照并集口径、wirelog grant/session ID 按 C-16 §7。
- 文档小修（P3-1…P3-4/P3-7/P3-8/P3-9/P3-10/P3-11/P3-12）可在同一 closeout docs 提交完成；不需要再开代码任务。
- **不要**把本卡当作 AC11-1 的完整闭合，也不要回填 L10；不要 push 直到 DSH 按授权执行（本 Review 未 push）。

SCAN-2-R2-REVIEW: APPROVE (P0=0 P1=0 P2=0 P3=14; P1-1 共享源 scope=all 真实修复并经真实 IPC+变异验证；P2-1 coalesce/重放、P2-2 空 project_ids typed skip、P2-3 真实导入 E2E、P2-4 allowlist 例外记录、P2-5 gated HostRuntime 用例均已核销；门禁独立复跑 pytest 3212/10、fea11 108、.NET 1500/0/85、check/pins/API/EV 58/58 全 PASS；工作树 clean、未 push；剩余为文档/证据口径 P3 与 closeout 建议)
