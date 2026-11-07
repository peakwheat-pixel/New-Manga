# FEA-11-SCAN-RH-1：SCAN-2 复核残余收口（Host-only，0 pin）— 证据（EV）

> 本 EV 只陈述**实跑/实改**事实。本卡修 **RH-1**（refresh pending 重放）与 **RH-2**（refresh 生命周期绑定/停机
> join）；**RH-4** 为文档口径订正（零代码）；**RH-3/RH-5 仅登记 limitation（不实现）**。**不声称** RH-3 已清理、
> RH-5 已补 fake-Core seam、SCAN-2 残余已全部解决；**不声称**满足 C-17 §6.2 零写基线或全库零写。

- Task：`doc/tasks/FEA-11-SCAN-RH-1.md`（`base_commit=ffcfab050`；**实施起点实测 `d09e91d1d`** = Lead 的
  docs-only 释放提交，仅改 `doc/handoffs/DSH-HANDOFF-2026-11-06.md`；`status` 由 Lead 维护）
- 交付 commit 链：`938d598ac`（实现）→ **`fb74b4ef7`（测试 = `delivery_head`）**；随后 docs/evidence 提交
- 环境：Windows 11 / PowerShell 7 / .NET SDK 10.0.401（目标 `net9.0`）/ .NET runtime 9.0.308 /
  CPython 3.14.6 / pytest 9.1.1；**零新依赖**、零 schema/wire/命令/能力/错误码/`PROTOCOL_MINOR`、零契约字节、
  零 App/UI、`HostRuntime.cs` **零 diff**（link 在 scheduler 内部完成）、未建 worktree、未 push、未改
  `status`、未自行 closeout。
- 交付字节 sha256：`SourceScanScheduler.cs` = `6b77d9ca362681cd48020f771d251db2d1b2c8208ea19f78dbea2e801e2768a6`；
  `SourceScanSchedulerTests.cs` = `e451526f22b5d16b003bc1317c354f949699a6d8b443790c37fa1a070fd97241`。

## 1. 改动内容与位置

| 文件 | 改动 | 说明 |
|---|---|---|
| `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs` | +124/−15 | AC-RH-1/AC-RH-2 实现（§2/§3） |
| `apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceScanSchedulerTests.cs` | +208/−12 | 3 个新用例 + `FakeTargetEnumerator` 扩展（`WaitFor` / `BlockUntilCancelled` / `CancellationObserved` / `Started` / `WaitForCallsAsync`；既有 `Block`/`Script` 语义不变） |
| `doc/tasks/FEA-11-SCAN-RH-1.md` | +66/−22 | AC 判定 `<<MET>>`（逐条行末）+ Limitation（RH-3/RH-4/RH-5）+ 交付记录 |
| `doc/tasks/FEA-11-SCAN-2.md` | **+1/−0** | closeout limitation **append-only 一行**（RH-4 三套表集与并集；原 AC 判词/EV 行字节未改） |
| `verification/FEA-11-SCAN-RH-1/**` | 新增 | 本 EV + `RESOURCE-MANIFEST.json` + `logs/**` |

**零 diff / 零漂移（实跑）**：`HostRuntime.cs`、`doc/contracts/**`、`src/**`、`apps/**` 其余文件、schema、依赖清单
全部 **0 字节**；`git diff --name-only -- ...` 输出为空（`logs/governance/scope-zero-drift.log`）。

## 2. AC 证据

### AC-RH-1（RH-1 refresh pending 重放）

- **实现**：`RefreshTargetsAsync` 拆为公开 wrapper + `RefreshTargetsPassAsync`（私有，单 pass）。pass 只在
  **完成一次枚举并释放单飞闸门之后**（成功或 typed unavailable；返回 `(Ran, Completed=true)`）才由 wrapper 触发
  一次 `ReplayPendingRefreshAsync`；被取消（OCE 上抛）或已 disposed / disabled 的提前返回返回
  `(false, false)`，**不重放**，pending 留给下一次 pass。`ReplayPendingRefreshAsync` 调用**非重放**的 pass →
  重放 pass 不会再次重放（**每 pass 至多一次、不递归**；重放期间新来的请求留在 `_refreshPending` 供下一次 pass）。
  `TickAsync` 既有「释放闸门 → refresh 重放 → hint 重放」语义与顺序**未改**。`RefreshTargetsAsync` XML 注释改为
  「coalesced and replayed after the in-flight pass」（同时删掉旧的 "merged, never queued" 表述）。
- **新增用例**：`RefreshDuringInFlightRefresh_IsReplayedAfterTheFirstPass_WithoutATick`（第二次 refresh 在第一次枚举
  在飞时 coalesced；第一次完成即发生第二次枚举并合并 `s2`，**全程不调用 `TickAsync`**，`executor.ScanCalls==0`）；
  `RefreshReplay_IsBoundedToOncePerCompletedPass`（重放 pass 内的第三次请求不递归触发第三 pass，留待下一次 pass，
  不丢）。
- **实跑**：`~SourceScan` 68/0/0 → **71/0/0**（`logs/dotnet-targeted-sourcescan-after-final.log`）。
- **判别性**：删掉重放（`_ = completed;`）→ 2 用例 **RED**（`logs/discriminative/M1-red-tests.log`，20 s 两处超时 =
  第二次枚举未发生）；复原交付字节（sha256 MATCH）→ **2 passed**（`M1-restored-green.log`）。

### AC-RH-2（RH-2 lifetime 绑定 + 停机有界 join）

- **实现**：新增 `_lifetimeCts`（scheduler 生命周期 CTS）与 `_activeRefreshes`/`_refreshIdle`（在飞 refresh 计数 +
  空闲信号）。`RefreshTargetsAsync` 的枚举 token = caller token ∪ `_lifetimeCts.Token` 的
  **`CreateLinkedTokenSource`**；`DisposeAsync` 顺序：置 `_disposed` → `Stop()` → **`_lifetimeCts.Cancel()`** →
  join loop → **有界 join 在飞 refresh（2 s，与 hint pass 同口径）** → join hint pass（2 s）→ 最后
  `_tickGate.Dispose()`（随后 `_lifetimeCts.Dispose()`）。disposed 后的 late refresh 直接返回 false；dispose 竞态下的
  wrapper 以 `catch (ObjectDisposedException) → false` 收口，**不产生任何 ObjectDisposed 日志**。
- **新增用例**：`DisposeAsync_WithInFlightRefresh_CancelsAndJoinsBeforeTeardown`（枚举阻塞 + `DisposeAsync` →
  枚举观察到 lifetime 取消（`CancellationObserved=true`）、`DisposeAsync` 有界完成（断言 < 5 s，实测 ms 级）、
  refresh 抛 `OperationCanceledException`、捕获日志中**无** `ObjectDisposedException`）。
- **实跑**：`~SourceWatcher` 19/0/0 不回归（`logs/dotnet-targeted-sourcewatcher-after-final.log`）；Host 单测 3 新用例
  23 ms 全绿（`M3-restored-green.log`）。
- **判别性**：改回 caller token（测试为默认 `CancellationToken.None`）+ 不 cancel lifetime + 不 join →
  `Assert.True(enumerator.CancellationObserved)` False → **RED**（`logs/discriminative/M2-red-tests.log`）；复原交付字节
  （sha256 MATCH）→ **3 passed**（`M3-restored-green.log`）。

### AC-RH-3（RH-4 文档订正，零代码）

- 本卡 `## Limitation` 的 **RH-4** 条目与 `doc/tasks/FEA-11-SCAN-2.md` closeout limitation 的 **append-only 一行**
  写清三套表集与并集，事实逐一核对源码/证据位置：
  **Core 14 表** = `tests/core/test_core_scan_target_commands.py:44-59`（`SNAPSHOT_TABLES`）；
  **Host 15 表** = `verification/FEA-11-SCAN-2/host-cold-start.json:15-32`（`db_tables`/`db_table_count=15`；
  `host-r2-cold-start.json` 同口径）；**C-17 §6.2 派生 16 表** = `tests/fea11/test_source_sync.py:588-606`
  （`_SNAPSHOT_TABLES`，注释 "card frozen rule 4: 16 tables"）。
  **Core 14 ∪ Host 15 = 17 表**；相对 16 表基线**缺** `pipeline_runs`/`pipeline_run_targets`/`step_result_candidates`，
  **多** `books`/`chapters`/`sources`/`book_cleanup_manifests`。
- **字节证明**：`git diff --numstat -- doc/tasks/FEA-11-SCAN-2.md` = **`1 0`**（纯追加一行，0 删除；见
  `logs/governance/scope-stat.log`）；不写「满足 C-17 §6.2 零写基线」「全库零写」（本卡与 SCAN-2 均无此表述）。

### AC-RH-4（RH-3/RH-5 登记）

- 本卡 `## Limitation` 逐条登记：**RH-3**（只增不减、无删除 API、`ApplyOutcome` 对 `Skipped` 无 backoff、预算稀释
  `(N+live)/8`、watch 每次 Sync 的 `source watch uncovered` WARN、**枚举省略≠删除**、正确清理需 Core 显式「已删除」
  信号 = C-17 additive → **Out 未实现**）；**RH-5**（时钟 seam 存在 `HostOptions.cs:111-112`、无 fake-Core seam
  （`HostRuntime.cs:1382-1403` 直接 `new`）、canonical 全量 .NET 日志 gated 用例 SKIP
  （`verification/FEA-11-SCAN-2/logs/host-r2-dotnet-full-3.log:105` 等 4 份）、EV-09 不能判别非阻塞、
  WATCH-1 卡 `:111/:129/:199/:213` 的「HostRuntime seam 无 fake-Core/注入时钟」按本卡口径订正理解但**不改其字节**）。
- 判别性：文档核对（本 EV §2/§5 + 上述源码位置；无测试）。

### AC-RH-5（门禁/证据/不夸大）

见 §4（全部实跑并留日志）；判别性见 §3。**不夸大**：本卡只实现 RH-1/RH-2；RH-3/RH-5 仅登记；未写
「RH-3 已清理 / RH-5 已补 seam / SCAN-2 残余已全部解决」。

## 3. 判别性（改回去 → RED → 逐字节复原 sha256 MATCH → 复绿）

| 变异 | 内容 | 结果 | 日志 |
|---|---|---|---|
| **M1（RH-1）** | 删掉 pass 完成后的重放（`if (completed) { await ReplayPendingRefreshAsync(...) }` → `_ = completed;`） | build 0/0；2 个 RH-1 用例 **2 failed / 0 passed / 20 s**（第二次枚举未发生） | `logs/discriminative/M1-*.log`、`M1-mutation.diff` |
| **M2（RH-2）** | 枚举 token 改回 caller token；`DisposeAsync` 不 cancel lifetime、不 join refresh | build 0/0；Dispose 用例 **1 failed / 0 passed**（`CancellationObserved` False） | `logs/discriminative/M2-*.log`、`M2-mutation.diff` |
| **复原** | `Copy-Item` 交付字节备份 + touch mtime（增量构建需要） | sha256 **2/2 MATCH**（`6b77d9ca…`），复绿 **2 passed / 3 passed**，随后 `~SourceScan` 71、`~SourceWatcher` 19 | `M1-restore-sha256.log`、`M3-final-restore-sha256.log`、`M1-restored-green.log`、`M3-restored-green.log` |

- 固定实现备份：`G:\CODEX\New Manga.workspace\FEA-11-SCAN-RH-1\SourceScanScheduler.fixed.cs`
  （sha256 `6b77d9ca362681cd48020f771d251db2d1b2c8208ea19f78dbea2e801e2768a6`）；未修改测试断言以适配 mutation。

## 4. 门禁（实跑；before → after）

| # | 项 | 命令 | before | after | 日志 |
|---|---|---|---|---|---|
| 1 | Release build | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` | 0 warning / 0 error（9.56 s） | **0 warning / 0 error** | `logs/build-before.log`、`logs/build-final.log` |
| 2 | 定向 SourceScan | `dotnet test ...NewManga.Host.Tests.csproj -c Release --no-build --filter "FullyQualifiedName~SourceScan"` | **68 passed / 0 / 0**（312 ms） | **71 passed / 0 / 0**（+3 新用例） | `logs/dotnet-targeted-sourcescan-before.log`、`-after-final.log` |
| 3 | 定向 SourceWatcher | 同上 `--filter "FullyQualifiedName~SourceWatcher"` | **19 passed / 0 / 0**（513 ms） | **19 passed / 0 / 0** | `logs/dotnet-targeted-sourcewatcher-before.log`、`-after-final.log` |
| 4 | 全量 .NET | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build` | **1680 passed / 0 failed / 96 skipped** | **1683 passed / 0 failed / 96 skipped**（+3） | `logs/dotnet-full-before.log`(+summary)、`logs/dotnet-full-after.log`(+summary) |
| 5 | 全量 pytest | `C:/Python314/python.exe -m pytest tests -q -p no:warnings --tb=no` | **3369 passed / 10 skipped**（247.68 s） | **3369 passed / 10 skipped**（251.18 s，不降） | `logs/pytest-full-before.log`、`logs/pytest-full-after.log` |
| 6 | pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | — | **PIN AUDIT: PASS (all 18)** | `logs/governance/pins.log` |
| 7 | check（默认） | `pwsh -NoProfile -File tools/governance/check.ps1` | — | **PASS (3 warnings)** | `logs/governance/check.log` |
| 8 | check（`-TaskPath`） | 同上 + `-TaskPath doc/tasks/FEA-11-SCAN-RH-1.md` | — | **PASS (3 warnings)** | `logs/governance/check-taskpath.log` |
| 9 | API inventory | `C:/Python314/python.exe tools/generate_api_inventory.py --check` | — | **EXIT=0** | `logs/governance/api-inventory.log` |
| 10 | scope | `git diff d09e91d1d..HEAD --name-only` / `--stat` / 零漂移路径 | — | 仅 allowed_paths；`HostRuntime.cs`/`doc/contracts`/`src/**`/schema/依赖 **0 字节** | `logs/governance/scope-name-only.log`、`scope-stat.log`、`scope-zero-drift.log`、`git-status.log`、`postcommit-commits.log` |

- 全量 .NET 跑后 `verification/FEA-09/logs/wire-redacted.ndjson` 被测试写脏 → 已 `git checkout -- verification/FEA-09`
  复原（`logs/dotnet-full-after-summary.log` 记录；`git status` 见 `git-status.log`）。
- 全量 .NET 的 Host 分片：**283 → 286 passed**（+3 新用例），skip 65 不变；全库 skip **96** 不变。

## 5. 不构成什么

- **不构成** RH-3 清理：`_targets` 仍只增不减、无删除 API、Skipped 仍无 backoff、预算稀释仍在；Core「已删除」信号
  （C-17 additive）未实现（Out）。
- **不构成** RH-5 修复：时钟 seam 本就存在（`HostOptions.SourceScanTimeProvider`），但 fake-Core seam 未加、sidecar
  bundle 未升级、CI fixture 未改；canonical 全量 .NET 中 gated 用例仍 SKIP。
- **不构成** SCAN-2 残余全部解决：本卡只做 RH-1/RH-2 实现 + RH-4 文档订正 + RH-3/RH-5 登记。
- **不构成**契约/协议变更：18 pins 不变、`PROTOCOL_MINOR`/命令/能力/错误码/依赖零改动；`HostRuntime.cs` 零 diff。
- **不构成**集成或 closeout：无独立 Review、无 Lead 集成验证、未 push、未改 `status`。

## 6. 复现（repo root，Windows / PowerShell 7）

```powershell
# 交付链（从 d09e91d1d 起）
git log --oneline d09e91d1d..HEAD

# 定向
dotnet build apps/desktop-avalonia/NewManga.sln -c Release
dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --no-build --filter "FullyQualifiedName~SourceScan"
dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --no-build --filter "FullyQualifiedName~SourceWatcher"
dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --no-build --filter "FullyQualifiedName~RefreshDuringInFlightRefresh|FullyQualifiedName~RefreshReplay_IsBounded|FullyQualifiedName~DisposeAsync_WithInFlightRefresh"

# 全量（.NET 跑后必须复原 FEA-09 测试写脏）
dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build
git checkout -- verification/FEA-09
C:/Python314/python.exe -m pytest tests -q -p no:warnings --tb=no

# 治理
pwsh -NoProfile -File tools/governance/verify_pins.ps1
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-SCAN-RH-1.md
C:/Python314/python.exe tools/generate_api_inventory.py --check
git diff --name-only d09e91d1d..HEAD
```

## 7. 证据文件清单

`verification/FEA-11-SCAN-RH-1/`：

- `EV.md`、`RESOURCE-MANIFEST.json`
- `logs/start-head.log`（实施起点 `d09e91d1d`、base、clean 状态）
- `logs/build-before.log`、`logs/build-final.log`
- `logs/dotnet-targeted-sourcescan-before.log`、`logs/dotnet-targeted-sourcescan-after-final.log`
- `logs/dotnet-targeted-sourcewatcher-before.log`、`logs/dotnet-targeted-sourcewatcher-after-final.log`
- `logs/dotnet-full-before.log`、`logs/dotnet-full-before-summary.log`
- `logs/dotnet-full-after.log`、`logs/dotnet-full-after-summary.log`
- `logs/pytest-full-before.log`、`logs/pytest-full-after.log`
- `logs/discriminative/SUMMARY.txt`、`M0-backup.txt`、`M1-mutation.diff`、`M1-build.log`、`M1-red-tests.log`、
  `M1-restore-sha256.log`、`M1-restore-build.log`、`M1-restored-green.log`、`M2-mutation.diff`、`M2-build.log`、
  `M2-red-tests.log`、`M3-final-restore-sha256.log`、`M3-final-build.log`、`M3-restored-green.log`
- `logs/governance/pins.log`、`api-inventory.log`、`check.log`、`check-taskpath.log`、`scope-name-only.log`、
  `scope-stat.log`、`scope-zero-drift.log`、`git-status.log`、`postcommit-commits.log`

> 说明：`check.log`/`check-taskpath.log`/`scope-*.log`/`git-status.log`/`postcommit-commits.log` 在 docs/evidence
> 提交之后于 committed 树上复跑（见 `postcommit-commits.log` 的 HEAD），以 committed 状态为准；其余日志产生于
> 提交前工作树（字节与提交一致，`git-status.log` 记录提交后 clean）。
