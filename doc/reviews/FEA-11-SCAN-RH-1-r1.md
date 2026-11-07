---
task: FEA-11-SCAN-RH-1
title: SCAN-2 复核残余收口（refresh pending 重放 + refresh 生命周期绑定）— 独立 Review（r1）
reviewer: fresh subagent
session: e14e3d88-2057-40ca-a73a-16796f21ae54
reviewer_kind: 独立实现 Review（fresh context / 只读被审 head；未参与本卡实现、返修、scope review，也未参与 SCAN-1/SCAN-2/WATCH-1）
date: 2026-11-08
repo: G:\CODEX\New Manga
branch: main
reviewed_head: fb74b4ef7
repo_head_at_review: 33c1dd66f
delivery_head: fb74b4ef7
verdict: approved
p0: 0
p1: 0
p2: 0
p3: 8
review_scope: AC-RH-1…AC-RH-5 逐条 + 回归风险（单飞/递归/风暴/死锁/线程安全）+ 交付完整性 + 门禁复跑 + 判别性独立复现 + 证据抽样
---

# FEA-11-SCAN-RH-1：独立实现 Review（r1）

> 只读审查。我未参与本卡实现/返修/scope review，也未参与 FEA-11-SCAN-1 / SCAN-2（含 PREREQ/C-17）/ WATCH-1 的实现或复核。
> 本次唯一写入仓库的文件是本报告；判别性复跑用的临时变异已逐字节复原并 `touch` mtime，结束时工作树除本报告外 clean、
> `verification/FEA-09` 无残留；未 `git add`/`commit`/`push`；未改 `status`/STATUS/PLAN/LEDGER；未建 worktree。
> 仓外临时/日志仅写入 `G:\CODEX\New Manga.workspace\SCAN-RH\review\`。

## 0. 结论

**verdict：approved（P0 = 0，P1 = 0，P2 = 0，P3 = 8）。**

- AC-RH-1…AC-RH-5 **全部成立**（逐条见 §2–§6）；实现、测试、文档、证据与卡面/EV/Handoff 的陈述一致，无夸大。
- 递归判定：**无递归**。`ReplayPendingRefreshAsync` 调用的是**非重放**的 `RefreshTargetsPassAsync`，不是会触发重放的
  `RefreshTargetsAsync`；重放 pass 自身不含重放逻辑 → 每完成 pass 至多一次，第三次请求留 `_refreshPending` 到下一次 pass。
- 风暴判定：**无自激枚举风暴**（单次请求最多触发一次即时额外枚举；无「重放 pass 再重放」链路）。
- 死锁判定：**无锁内 await、无嵌套 single-flight**；refresh/hint join 均有 2 s 上界（loop join 无界属**既有**行为，P3-7）。
- 单飞语义**零回归**：`_tickGate` 获取/释放仍严格配对；`TickAsync` 结构与「refresh 重放 → hint 重放」顺序未变；
  定向 `~SourceScan` **71/0/0**、`~SourceWatcher` **19/0/0** 全绿。
- `HostRuntime.cs` **确实零 diff**（`git diff --stat d09e91d1d..33c1dd66f -- .../HostRuntime.cs` 为空）；token link 在 scheduler
  内部完成，不依赖 Host 传递——`HostRuntime` 仍传 `CancellationToken.None`，lifetime 由 scheduler 自己的 `_lifetimeCts` 提供，
  停机路径因此成立。
- P3 均为**非阻塞**的边界/证据/口径项（§8），其中 P3-1（极窄 ODE 窗口）与 P3-3（「join」半边判别为竞态性）建议 Lead 在
  closeout 或后续小修中知悉；不构成返修要求，不影响 approved。

## 1. 被审对象与核对口径

| 项 | 值 |
|---|---|
| 卡 | `doc/tasks/FEA-11-SCAN-RH-1.md`（`status: ready`，Owner `scan-rh-impl`；closeout 字段 pending，Lead 维护） |
| delivery_head | `fb74b4ef7`（实现 `938d598ac` → 测试 `fb74b4ef7`；`git diff --stat d09e91d1d..fb74b4ef7` = 仅 2 个代码文件，+332/−27） |
| docs/evidence 链 | `1a769c9cc`（卡/EV/Handoff/Manifest + SCAN-2 append-only）→ `86c5b053a`（post-commit 门禁/scope 日志）→ `327b299e6` → `33c1dd66f`（均为 docs-only 口径澄清） |
| 实施起点 | 实测 `d09e91d1d`（Lead 的 docs-only 释放提交，仅 `doc/handoffs/DSH-HANDOFF-2026-11-06.md` +11 行；`start-head.log` 一致） |
| 依据 | `doc/reviews/FEA-11-SCAN-RH-scope-r1.md`（§2 事实表、§3.3 卡面/AC、§7 基线）、`doc/tasks/FEA-11-SCAN-2.md:252` |
| 证据 | `verification/FEA-11-SCAN-RH-1/`（EV.md、RESOURCE-MANIFEST.json、`logs/**`） |
| 审查基准 | 本报告以 `fb74b4ef7` 的代码/测试字节 + `33c1dd66f` 的文档/证据字节为准；两者之间只追加 docs/evidence |

**关于任务书提到的「scope review §2.7」**：该文档**不存在** §2.7（只有 §2 事实表与 §2.1 三问）。对应的 RH-4 事实在
`scope-r1.md:49`（§2 表 RH-4 行）与 `:66-69`（§2.1「RH-4」问答）、AC 要求在 `:137`（§3.3 AC-RH-3）。本 Review 按这三处核对，
内容一致（见 §4）。

## 2. AC-RH-1（RH-1 重放修复）— **MET**

### 2.1 重放时机（完成枚举 + 释放闸门之后）

`RefreshTargetsAsync`（`:702-757`）拆为 wrapper + `RefreshTargetsPassAsync`（`:765-871`）：

1. wrapper 在 `_gate` 内判 `_disposed` 并 `_activeRefreshes++`，取 `_lifetimeCts.Token`；
2. `CreateLinkedTokenSource(caller, lifetime)`（`:720`，`using` 正确释放）；
3. `(ran, completed) = await RefreshTargetsPassAsync(linked.Token)`；
4. **仅当 `completed`** 才 `await ReplayPendingRefreshAsync(linked.Token)`（`:734-738`）；
5. `finally` 递减 `_activeRefreshes` 并唤醒 `_refreshIdle`（锁内维护，`TrySetResult` 幂等）。

`RefreshTargetsPassAsync` 的返回语义（`:765-871`）逐条核对：

| 路径 | 返回值 | 是否释放闸门 | 是否重放 |
|---|---|---|---|
| `enumerator == null`（无能力） | `(false, false)` | 从未获取 | 否（typed `CORE_CAPABILITY_MISSING` 已落快照） |
| 抢不到 `_tickGate`（在飞） | `(false, false)`，并置 `_refreshPending = true`（`:780-794`） | 未获取 | 否（留给在飞 pass 的完成方） |
| 抢到闸门后 `_disposed` / `!Enabled` | `(false, false)`（`:800-808`） | **是**（`finally` Release） | 否 |
| 枚举成功 / typed unavailable（core/access/sidecar/IO/unknown） | `(result.Ok, true)`（`:852-865`） | 是 | **是，一次** |
| 枚举抛 `OperationCanceledException` | 上抛（`:814-817`） | 是（`finally`） | 否（`completed` 未赋值） |
| 枚举后 `_disposed` | `(false, false)`（`:841-846`） | 是 | 否 |

结论：**只有「完成枚举并释放闸门」的 pass 才重放**；取消/已 disposed/抢不到闸门的提前返回均不重放，pending 保留
（抢不到闸门的那一支显式置位）。与 AC 文本逐字一致。

### 2.2 有界不递归（关键判定）

- `ReplayPendingRefreshAsync`（`:929-957`）：锁内取走 `_refreshPending` 并清零 → 调用 **`RefreshTargetsPassAsync`**（`:945`），
  即**非重放** pass。`RefreshTargetsPassAsync` 内部**不含**任何 `ReplayPendingRefreshAsync` 调用（`:765-871` 全文核对）。
  因此「重放 → 再重放」链路不存在：**无递归**。
- 重放 pass 完成（成功或 unavailable）后返回，不会再检查 pending；重放期间到来的第三次请求在 `:780-794` 抢不到闸门，
  `_refreshPending` 重新为 true，**留待下一次 pass**（下一次 `TickAsync` 完成或下一次 wrapper 完成）。
- 判别用例 `RefreshReplay_IsBoundedToOncePerCompletedPass`（`:1631-1670`）用 `enumerator.Calls` 精确断言：重放期间第三次请求
  不产生第 3 次枚举（`Assert.Equal(2, ...)`）、随后 `TickAsync` 消费它恰好一次（`Assert.Equal(3, ...)`），且 target 已合并。
  若实现误用 `RefreshTargetsAsync` 递归，该断言会变 3——**测试具备判别力**。

### 2.3 `TickAsync` 顺序未变

`:991-997`：`ReplayPendingRefreshAsync(cancellationToken)` → `ReplayPendingHintAsync(cancellationToken)`，与修复前
（scope review 所述 `:912-917`）同序。`~SourceWatcher` 19/0/0 不回归，hint 语义未动。

### 2.4 XML 注释

`RefreshTargetsAsync` 注释（`:691-701`）已写 "coalesced and replayed after the in-flight pass — never queued unboundedly,
and the replayed pass itself never replays again"，并删除了旧的 "merged, never queued" 表述；`ReplayPendingRefreshAsync`
注释（`:922-928`）明确「at most one replay per completed pass, never recursive」。与实现一致。

### 2.5 实跑与判别

- `~SourceScan`：**71 passed / 0 failed / 0 skipped，317 ms**（我独立实跑，§7 #2）；EV 的 before 68 → after 71 与日志一致
  （`dotnet-targeted-sourcescan-before.log` = 68、`-after-final.log` = 71）。
- 判别性 M1（我独立复现）：删掉 `if (completed) { await ReplayPendingRefreshAsync(...); }` → **2 failed / 0 passed / 20 s**
  （两用例均卡在第二次枚举的 10 s 等待）；逐字节复原 sha256 `6b77d9ca…` **MATCH=True**、`touch` 后重编译、复绿
  **3 passed / 23 ms**、`~SourceScan` 仍 71。与 `SUMMARY.txt` 的 M1 记录一致（§7 #6）。

## 3. AC-RH-2（RH-2 lifetime 绑定 + 停机 join）— **MET（附 P3-1 理论窗口）**

### 3.1 lifetime 与 linked token

- `_lifetimeCts`（`:366`）为 scheduler 自有；`RefreshTargetsAsync` 取 `lifetime = _lifetimeCts.Token`（锁内，`:715`），
  枚举 token = `CreateLinkedTokenSource(cancellationToken, lifetime)`（`:720`），`using var linked` 正确 Dispose（`:720`）。
- `_activeRefreshes`/`_refreshIdle`（`:370-371`）在 `_gate` 内维护（++ `:714`、-- `:744-755`），用于 Dispose 的 refresh join。

### 3.2 DisposeAsync 顺序（逐项对照）

`DisposeAsync`（`:1135-1188`）实际顺序 = **置 `_disposed` → 取 loop/refreshIdle 快照 → `Stop()` → `_lifetimeCts.Cancel()`
→ join loop → 有界 join 在飞 refresh（`WaitAsync(2 s)`）→ 有界 join hint（`2 s`）→ `_tickGate.Dispose()` →
`_lifetimeCts.Dispose()`**。与 AC 要求的「先取消、再有界 join、最后 Dispose 闸门」一致；`Cancel`/`Dispose` 的
`ObjectDisposedException` 已就地 catch（`:1157-1158`）；`_refreshIdle` 的创建与等待均在锁外，**无锁内 await、无死锁**。

### 3.3 无 ODE 逃逸（主路径）

已核对的收口点：

1. disposed 后 late refresh：锁内 `if (_disposed) return false`（`:709-712`），不接触 gate/token；
2. dispose 竞态下 pass 内 `WaitAsync`/`Release` 的 ODE：wrapper `catch (ObjectDisposedException) → false`（`:727-732`），
   且 `ReplayPendingRefreshAsync` 同样 catch（`:950-952`）；
3. hint pass 的 ODE：`HintedTickAsync`/`ReplayPendingHintAsync` 各自 catch（`:648-650`、`:682-684`）；
4. 反射/日志：`RefreshTargetsAsync` 的 ODE 分支**不写日志**（注释明确「a disposal detail never reaches the Host log」）。

判别用例 `DisposeAsync_WithInFlightRefresh_CancelsAndJoinsBeforeTeardown`（`:1678-1706`）断言：枚举观察到 lifetime 取消
（`CancellationObserved=true`）、refresh 抛 `OperationCanceledException`、Dispose 有界（< 5 s，实测 ms 级）、三类日志均无
`ObjectDisposedException`。该用例在 M2 变异（caller token + 不 cancel + 不 join）下 RED，复原后 3 passed（EV + 我的复核）。

### 3.4 停机时调用方行为（HostRuntime 零 diff 的配套确认）

`HostRuntime.RefreshSourceScanTargetsAsync`（`HostRuntime.cs:227-242`）已 catch `OperationCanceledException`（静默）与
其余异常（WARN）。因此 lifetime 取消导致的 OCE **不会**变成 unobserved task exception，也不会产生 WARN。

### 3.5 P3-1（记录，不影响 MET）

`CreateLinkedTokenSource` 在 `:720`，其外层的内层 `try` 只从 `:723` 开始——即 ODE catch **不覆盖** `:720`。
若线程 T1 在 `_activeRefreshes++`（`:714`）之后、`:720` 之前被 OS 抢占/进程挂起超过「loop join + 2 s + 2 s」，则
`DisposeAsync` 会先执行 `_lifetimeCts.Dispose()`（`:1187`），T1 恢复后在已 Dispose 的 CTS 上 Register 抛
`ObjectDisposedException`，逃逸到 `HostRuntime` → `source scan refresh failed: ObjectDisposedException`。
该窗口需要「抢占恰好落在两行无 await 的同步代码之间」且持续 ≥ 两个 2 s 预算，现实中极窄；即便发生，后果也与修复前
一致（一条 WARN，不崩溃/不丢数据）。建议（非阻塞）：把 `CreateLinkedTokenSource` 及其 `.Token` 的取得移入
`:723` 的内层 `try`（或在锁内构造 linked），一行级加固即可把 AC 字面的「不得出现 ODE」闭合到 100%。

## 4. AC-RH-3（RH-4 文档订正）— **MET**

- **append-only**：`git diff 1a769c9cc^ 1a769c9cc --numstat -- doc/tasks/FEA-11-SCAN-2.md` = **`1 0`**（我独立实跑，§7 #5）；
  新增行为 `:255`，原 `:252` 残余登记行与 AC/EV 字节未改（我核对了 diff hunk：`@@ -252,3 +252,4 @@`，仅追加）。
- **表集事实**（我逐项读了四"个"源位置）：
  - Core 14 表 = `tests/core/test_core_scan_target_commands.py:44-59`（`SNAPSHOT_TABLES`，14 项）✓；
  - Host 15 表 = `verification/FEA-11-SCAN-2/host-cold-start.json:15-32`（`db_table_count=15`；含
    `regions`/`region_revisions`/`rendition_cache`，不含 `reading_progress`/`book_cleanup_manifests`）✓；
  - C-17 §6.2 派生 16 表 = `tests/fea11/test_source_sync.py:588-605`（`_SNAPSHOT_TABLES`，16 项）✓；
  - 并集：14 ∪ 15 = **17**（12 公共 + 2 Core 独有 + 3 Host 独有）✓；
  - 与 16 表基线相比：**缺** `pipeline_runs`/`pipeline_run_targets`/`step_result_candidates`，**多**
    `books`/`chapters`/`sources`/`book_cleanup_manifests` ✓（我逐表比对，4 多 3 缺，17−3+…= 16 的集合关系成立）。
- **禁止表述**：卡面、EV、Handoff、SCAN-2 中所有「满足 C-17 §6.2 零写基线」「全库零写」「RH-3 已清理 / RH-5 已补 seam /
  SCAN-2 残余已全部解决」的出现**全部**位于「禁止/不声称/不等于/不构成」的否定语境（`git grep` 逐条核对），无一处正向断言。
- 落点正确：卡面 `## Limitation` RH-4（`:62-72`）+ SCAN-2 append-only 一行；SCAN-2 的 AC-S2-8 判词与 EV 行未动。

## 5. AC-RH-4（RH-3/RH-5 登记）— **MET**

逐条对照 scope review §3.3 AC-RH-4（`:138`）与 scope §2.1 的事实：

| 要求 | 卡面落点 | 核对 |
|---|---|---|
| RH-3 只增不减 / 无删除 API | `:73-79` | ✓（`RegisterTarget` 覆盖写 + `MergeTargetsLocked` add/update，无 Remove；我已 grep 实现） |
| `Skipped` 无 backoff | `:75-76`、`:1352-1359` | ✓（`ApplyOutcome` 对 `Skipped` 显式 `Failures=0`、`BackoffUntil=null`） |
| 预算稀释 `(N+live)/8` | `:76` | ✓（`DefaultMaxTargetsPerTick=8` 与 `_budgetCursor` 轮转一致） |
| watch 每次 Sync 的 uncovered WARN | `:77` | ✓（WATCH-1 既有行为，本卡未改 Watch） |
| **枚举省略 ≠ 删除** | `:77-79` | ✓（明确写出 Core 因 missing location facts/未知 kind/`project_ids` 0 或 >20 合法省略；Host 若 diff-removal 会静默丢 target） |
| 清理需 C-17 additive → Out | `:79` | ✓ |
| 时钟 seam 存在 `HostOptions.cs:111-112` | `:80-81` | ✓（我读 `HostOptions.cs:111-112` 为 `SourceScanTimeProvider`，默认 `TimeProvider.System`） |
| 无 fake-Core seam（`HostRuntime.cs:1382-1403` 直接 `new`） | `:82-83` | ✓（我读 `HostRuntime.cs:1382-1403`：`new HostSourceScanExecutor` / `new HostSourceScanTargetEnumerator` / `new SourceScanScheduler`，无 `HostOptions` 注入口） |
| canonical 全量日志 gated 用例 SKIP | `:84-85` | ✓（`verification/FEA-11-SCAN-2/logs/host-r2-dotnet-full-3.log:105` 等；EV 抽样一致） |
| EV-09 不能判别非阻塞 | `:85-86` | ✓（`enumeration_present_immediately_after_start=true`） |
| WATCH-1 卡 `:111/:129/:199/:213` 按新口径理解但**不改字节** | `:86-88` | ✓（`git diff --stat d09e91d1d..HEAD -- doc/tasks/FEA-11-WATCH-1.md` 为空；最后改动是历史的 `3127932b3`；行内容与「无 fake-Core/注入时钟」表述对应） |

无「RH-3 已清理 / RH-5 已补 seam」字样（§4 已核）。登记完整、措辞与 scope 裁决一致。

## 6. AC-RH-5（门禁/证据/不夸大）— **MET**

- 全部数字经我独立实跑或日志复算（§7）：build 0/0、`~SourceScan` 71/0/0、`~SourceWatcher` 19/0/0、pins 18/18、
  check ×2 PASS(3 warnings)、API EXIT=0；全量日志 8 个 assembly 合计 **1683/0/96**（before 1680/0/96，Host 分片
  283→286，skip 96 不变）——我逐行相加核对，与 EV/Handoff 一致；pytest **3369 passed / 10 skipped**（before/after 同，
  日志尾部行核对）。
- 卡面 AC 的 pytest 基线写 **3363/10**（冻结时点数字），交付记录与 EV 用 **3369/10**（实测，不降）。两者都如实、不冲突，
  仅口径时点不同（P3-6）。
- 无夸大表述（§4 已核）；EV §5「不构成什么」逐条成立。

## 7. 独立实跑（本会话确切实测）

| # | 命令 | 结果 | 日志 |
|---|---|---|---|
| 1 | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` | **0 warning / 0 error**，5.40 s，EXIT=0 | `workspace\SCAN-RH\review\build.log` |
| 2 | `dotnet test ...NewManga.Host.Tests.csproj -c Release --no-build --filter "FullyQualifiedName~SourceScan"` | **71 passed / 0 failed / 0 skipped**，317 ms，EXIT=0 | `targeted-sourcescan.log` |
| 3 | 同上 `~SourceWatcher` | **19 / 0 / 0**，518 ms，EXIT=0 | `targeted-sourcewatcher.log` |
| 4 | 全量 .NET | **未跑**（按任务书由 Lead 跑；避免 `verification/FEA-09` 写脏）。日志复算：8 assembly = 1683 / 0 / 96 | — |
| 5 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PIN AUDIT: PASS (all 18)**，EXIT=0 | `pins.log` |
| 6 | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS (3 warnings)**，EXIT=0 | `check.log` |
| 7 | 同上 `-TaskPath doc/tasks/FEA-11-SCAN-RH-1.md` | **PASS (3 warnings)**，EXIT=0 | `check-taskpath.log` |
| 8 | `C:/Python314/python.exe tools/generate_api_inventory.py --check` | **EXIT=0** | `api-inventory.log` |
| 9 | 全量 pytest | **未跑**；日志复算 `3369 passed, 10 skipped`（before 247.68 s / after 251.18 s） | — |
| 10 | `git diff --check` | **EXIT=0** | — |

## 8. 判别性独立复现（M1；临时变异 → RED → 逐字节复原 → 复绿）

| 步骤 | 操作 | 实测 |
|---|---|---|
| 0 | 备份交付字节到仓外 | `6b77d9ca362681cd48020f771d251db2d1b2c8208ea19f78dbea2e801e2768a6`（与 EV/M0 一致） |
| 1 | 变异：删除 `if (completed) { await ReplayPendingRefreshAsync(...); }` → `_ = completed;` | 变异后 sha256 `e0b80bd4…`；`git diff --stat` = 1 file，+2/−5 |
| 2 | `dotnet build -c Release` | **0 warning / 0 error**，3.81 s |
| 3 | `--filter "~RefreshDuringInFlightRefresh\|~RefreshReplay_IsBounded"` | **失败 2 / 通过 0 / 总计 2，20 s**（两处 10 s 等待超时）→ **RED_AS_EXPECTED** |
| 4 | `Copy-Item` 复原 + sha256 + `touch` mtime | `RESTORED_SHA256=6b77d9ca…`，**MATCH=True**；`TOUCHED_MTIME=2026-11-08T01:40:16+08:00` |
| 5 | `dotnet build -c Release`（确认非 stale） | 0/0，3.56 s；`NewManga.Host.Tests.dll` mtime `01:40:20` **晚于**源文件 mtime |
| 6 | 3 个新用例复跑 | **3 passed / 0 failed**，23 ms |
| 7 | `~SourceScan` 复跑 | **71 passed / 0 failed** |
| 8 | 工作树 | `git status --porcelain` **空**；`verification/FEA-09` 无残留 |

M2（RH-2 组合变异）未由我重跑；EV/M2 日志的变异内容（caller token + 不 cancel + 不 join）与 RED 结论逻辑成立，
且其判据（`CancellationObserved=false`）与我读到的实现一致。M1 足以独立验证「重放确实存在且被测试抓住」。

## 9. 证据抽样（sha256 / 日志）

- **sha256 复算 6 条**：
  1. 工作树 `SourceScanScheduler.cs` = `6b77d9ca…`（EV/Handoff/Manifest/M0/M1/M3 全部一致）**MATCH**；
  2. 工作树 `SourceScanSchedulerTests.cs` = `e451526f…`（EV §0）**MATCH**；
  3. 仓外备份 `SourceScanScheduler.fixed.cs` = `6b77d9ca…` **MATCH**；
  4. `git cat-file` 的交付 blob（**LF**）`SourceScanScheduler.cs` = `fcc5f765…`；
  5. 同 blob `SourceScanSchedulerTests.cs` = `97979b8e…`；
  6. 工作树归一化 CRLF→LF 后 = `fcc5f765…`（与 #4 一致，证明差异仅换行）。
- **CRLF 口径**：`core.autocrlf=true`，工作树 CRLF（`103,664 B`）、blob LF（`101,166 B`）。EV 的 sha256 是**工作树字节**口径
  （备份 `Copy-Item` 保留 CRLF），因此在 Windows 干净 checkout 上可复算 MATCH；在 Linux/`core.autocrlf=false` 环境复算会
  得到 `fcc5f765…` 而非 EV 值 → 属**口径未注明**（P3-4），不是虚报。
- **日志核对**：before 定向 68 / 19、after 71 / 19；全量 8 个 assembly 逐行相加 = 1683/0/96（before 1680/0/96，
  Host 283→286）；pytest 3369/10；pins 18/18；`start-head.log` = `d09e91d1d` 与卡面一致；`git-status.log` 为提交前
  untracked 记录，最终树 clean（我复核）。
- **RESOURCE-MANIFEST.json**：`closeout_counts` 全 0；仓外仅保留 backup（`PRESERVE_REFERENCED`，sha256 与 EV 一致），
  与实际目录内容一致。

## 10. 交付完整性与 scope

- **delivery_head = `fb74b4ef7` 合理**：`git diff --stat d09e91d1d..fb74b4ef7` = 仅
  `SourceScanScheduler.cs`（+124/−15）与 `SourceScanSchedulerTests.cs`（+208/−12），即「实现 + 测试」头；docs/evidence
  在其后。与项目惯例（L-R11：delivery `86cd1d124` + docs `1e339f30a`）一致，且交付头本身可 build/可测。
- **scope ⊆ allowed_paths**：`git diff --name-only d09e91d1d..33c1dd66f` 共 **44 个路径**，我逐条比对 `allowed_paths`：
  全部落在卡面 8 条 allowed（含 `verification/FEA-11-SCAN-RH-1/**`、`doc/handoffs/FEA-11-SCAN-RH-1-*`、
  `doc/reviews/FEA-11-SCAN-RH-1-*`、SCAN-2、两个代码文件）内，**零 outside**。
- **以派发基准 `ffcfab050` 计**：仅额外 `doc/handoffs/DSH-HANDOFF-2026-11-06.md`，属 Lead 的 `d09e91d1d`（docs-only 释放提交，
  仅 1 文件 +11 行），**非本卡写入**；不构成 scope 违规。
- **零漂移**：`HostRuntime.cs`、`doc/contracts/**`、`src/**`、schema、依赖清单 0 字节（`scope-zero-drift.log` + 我的
  `git diff --name-status` 双向核对）；`HostRuntime.cs` 零 diff 已确认为**事实**，且 scheduler 内部 link 不依赖 Host 传递。
- **未改** `status`（仍 `ready`）、`integration_commit`（null）、`reviewer`（null）、`canonical_evidence_status` /
  `resource_closeout_status`（pending）——符合「Lead 维护」。未 push、未建 worktree。

## 11. 回归风险逐项判定

| 风险 | 判定 | 依据 |
|---|---|---|
| 单飞语义回归 | **无** | `_tickGate.WaitAsync(0)`/`Release()` 仍严格配对；`TickAsync`/`HintedTickAsync` 结构未动；71 + 19 全绿 |
| 无限递归 / 重放风暴 | **无** | `ReplayPendingRefreshAsync` → 非重放 pass；pass 内无重放入口；单次请求至多一次即时额外枚举；无自激链 |
| Dispose 死锁（持锁 join） | **无** | `DisposeAsync` 锁内只做快照，全部 await 在锁外 |
| `_activeRefreshes`/`_refreshIdle` 线程安全 | **正确** | 全在 `_gate` 内维护；`TrySetResult` 幂等；disposed 后新调用不再计数 |
| 与 `_tickGate` 竞争 | **正确** | 计数与闸门解耦；coalesced 调用也计数，使 Dispose 等等待完整调用链 |
| 取消传播 | **符合** | OCE 从枚举经 pass 上抛到 wrapper（不吞），HostRuntime 已 catch OCE；lifetime 取消使空闲枚举立即结束 |
| ODE 逃逸 | **主路径已闭合** | wrapper/pass/重放/hint 四处 catch；判别用例断言日志无 ODE；残留 P3-1 理论窗口（§3.5） |
| 枚举风暴 | **无** | 合并语义固定 `_refreshPending` 单布尔；重放 pass 抢不到闸门时只置位不重试 |

## 12. Findings

**P0 = 0，P1 = 0，P2 = 0。**

| # | 级别 | 项 | 说明 / 建议 |
|---|---|---|---|
| P3-1 | 低 | `CreateLinkedTokenSource` 的 ODE 理论窗口 | `:720` 在内层 `try`（`:723`）之外；若线程在 `:714` 与 `:720` 之间被挂起 ≥ 两个 2 s 预算，`_lifetimeCts.Dispose()` 后 Register 抛 ODE → HostRuntime WARN。建议一行级加固（把 linked 构造移入内层 try）。**非阻塞** |
| P3-2 | 低 | 重放 pass 被取消时 pending 丢失 | `ReplayPendingRefreshAsync` 先清零 `_refreshPending`（`:932-936`）再运行 pass；若重放 pass 因 caller/lifetime token 已取消而在 `WaitAsync` 抛 OCE（被 `:947-949` 吞），该次合并请求丢失，需等下一 tick。实际调用方（HostRuntime）恒传 `None`，影响仅限取消场景；与 AC「pending 留待下一次 pass」在重放路径上有口径差 |
| P3-3 | 低 | 「join」半边的判别是竞态性的 | 现用例对「不 cancel」确定 RED；对「仅不 join」是否 RED 取决于 `_tickGate.Dispose()` 与 pass `Release()` 的竞争（若不 join，Release 可能抛 ODE → wrapper 返回 false，`ThrowsAnyAsync<OCE>` 失败 → RED，但不稳定）。建议未来补「忽略取消的 hung 枚举」用例，使 join 缺失**稳定**变红 |
| P3-4 | 低 | EV sha256 口径未注明 | EV 的 `6b77d9ca…`/`e451526f…` 是**工作树 CRLF** 字节；Git blob（LF）为 `fcc5f765…`/`97979b8e…`。Windows（`core.autocrlf=true`）可复算 MATCH，跨平台复算不 MATCH。建议在 EV 注明「工作树字节（CRLF）」 |
| P3-5 | 低 | 治理日志时点陈旧 | `scope-from-dispatch-base.log` 在 `33c1dd66f` 仅被 `git mv` + 改 5 行，路径列表仍是 `327b299e6` 时点（含已不存在的 `scope-from-card-base.log`、缺自身新名）；`scope-stat.log`/`check*.log` 停在 `1a769c9cc`，未覆盖后两个 docs-only 提交。我已在 HEAD 复跑 check=PASS，结论不受影响；建议 closeout 时重跑覆盖该日志 |
| P3-6 | 低 | pytest 基线数字两处 | 卡面 AC-RH-5 写冻结基线 `3363/10`，交付记录/EV 写实测 `3369/10`；均如实（不降），仅时点不同。可在 closeout 时统一为实测口径 |
| P3-7 | 低（既有） | loop join 无界 | `DisposeAsync` 对 `_loopTask` 的 join 无超时（`:1160-1164`）；executor 卡死时停机可能挂起。**本卡未引入**，AC-RH-2 只要求 refresh 有界；登记备查 |
| P3-8 | 低（既有） | hint pass 不绑 lifetime | `HintedTickAsync` 用 `CancellationToken.None`（`:639`），停机只靠 2 s 有界 join + ODE catch 兜底。**本卡未引入**；若未来统一生命周期，可把 hint 也接入 `_lifetimeCts` |

> 上述 P3 均不改变 AC 判定、不阻塞集成；P3-1/P3-3 建议由 Lead 决定是否在本卡 closeout 前做一行级加固，其余可在后续小修/文档刷新中处理。

## 13. 真实性声明

- **独立性**：我是 fresh subagent（session `e14e3d88-2057-40ca-a73a-16796f21ae54`），未参与 FEA-11-SCAN-RH-1 的实现、返修、
  scope review，也未参与 SCAN-1/SCAN-2/WATCH-1；未与 Owner 共享上下文。
- **写入范围**：本报告是唯一写入仓库的文件；仓外仅 `G:\CODEX\New Manga.workspace\SCAN-RH\review\`（build/测试/判别性日志、
  交付字节备份 `SourceScanScheduler.delivered.cs`、blob 抽样）。判别性临时变异已 `Copy-Item` 复原、sha256 MATCH、`touch`
  mtime 并按非 stale 的 DLL 复绿；结束时 `git status --porcelain` 仅本报告 untracked，`verification/FEA-09` 无残留。
  未 `git add`/`commit`/`push`，未改任何卡/契约/STATUS/PLAN/LEDGER。
- **实测 vs 引用**：§7 的 build/定向测试/pins/check/API/diff-check 与 §8 的 M1 判别是我本会话实测；全量 .NET、全量 pytest、
  M2 判别为**日志复算/引用**（已注明），不是我的实跑。EV 的 1683/0/96、3369/10 我做了逐行相加/尾部行核对，未重跑全量。
- **不夸大**：本报告不声称 RH-3 已清理、RH-5 已补 seam、SCAN-2 残余已全部解决；approved 仅表示本卡 AC 与门禁成立、
  P0/P1=0，不代表已集成或已 closeout（`status`、`integration_commit` 仍由 Lead 维护）。
