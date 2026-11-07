---
task: FEA-11-SCAN-RH
title: FEA-11-SCAN-2 复核残余 RH-1…RH-5：scope review（r1）
reviewer: fresh subagent（独立上下文）
session: c50bc2b0-52e4-4d23-a60e-22115ea29a3a
reviewer_kind: 独立 scope review（fresh context / read-only / 未参与 SCAN-1、SCAN-2、WATCH-1 的实现或复核）
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
reviewed_head: 28a2826af
reviewed_head_note: 任务书给定 `28a2826af`；评审期间 main 前进到 `63b95abda`（C-04b residual docs-only delivery `698ac9524` + closeout `63b95abda`）。`git diff --name-only 28a2826af..HEAD` 仅 `doc/**` 与 `verification/FEA-12-CORE-C04B-RESIDUAL-1/**`，零 `src/`、`apps/`、`tests/` 变化，本报告事实不受影响
verdict: recommended
verdict_scope: 推荐**一张** Host-only 小卡（implementation，0 pin）：RH-1/RH-2 实施修复 + RH-4 文档口径订正 + RH-3/RH-5 仅登记 limitation；明确**不做** RH-3 targets 清理与 RH-5 fake-Core seam；优先级排在 L-R11 实现之后，可穿插（C-04b residual 评审期间已 done）
---

# FEA-11-SCAN-RH：scope review（r1）

> 只读 scope review。我未参与 FEA-11-SCAN-1 / SCAN-2（含其 PREREQ/C-17）/ WATCH-1 的任何实现、返修、契约起草或复核；本次未修改生产代码、测试、契约或任何任务卡；未 `git add`/`commit`/`push`。本文件是本次唯一写入仓库的文件，运行日志在仓外 `G:\CODEX\New Manga.workspace\SCAN-RH\scope-review\`。
> **本报告不声称任何 RH 项已修复**；它只回答「各项当前是什么行为、值不值得做、以什么形态做、按什么顺序做」。

## 0. 结论先行

1. **RH-1 是「真行为 + 半句假注释」**：`_refreshPending` 只在 `TickAsync` 结束时重放（`SourceScanScheduler.cs:914`），`RefreshTargetsAsync` 自己的 `finally`（`:791-794`）不重放；而该方法的 XML 注释（`:846-849`）写着 "Called after a tick (or a refresh)"。后果是「refresh 在途时来的第二次 Refresh」最坏要等到下一个 tick（默认 900 s）或下一次 watcher hint 才生效——不丢，但延迟一个周期。**缺陷级别：低（Host-only，无 UI 消费者）**。
2. **RH-2 是真实生命周期缺口**：`HostRuntime.RefreshSourceScanTargetsAsync` 用 `CancellationToken.None`（`HostRuntime.cs:231`），scheduler 侧没有 lifetime CTS，`DisposeAsync` 只 join loop 与 hint pass、随后立刻 `_tickGate.Dispose()`（`:1050-1079`）。停机时在飞 refresh 既不被取消、也不被 join，其 `finally` 的 `Release()` 会在已 Dispose 的信号量上抛 `ObjectDisposedException`（静态推断，未写判别测试），最终被 fire-and-forget 的外层 catch 记一条 WARN。**缺陷级别：低（噪声/竞态，不崩溃）**。
3. **RH-3 是设计取舍，不建议修**：Host 的 `_targets` 只增不减且**没有任何删除 API**；撤销 root（`source_revoke_root` 可达）后该 target 每轮转都被重试为 typed skip 且**无 backoff**，永久占用每 tick 的 8 个预算槽（按 `MaxTargetsPerTick` 计算，N 个 stale 时 live 源的扫描周期被放大约 `(N+live)/8` 倍）。但**「Core 枚举省略」≠「源已删除」**——Core 会因 missing location facts / 未知 kind / `project_ids` 0 或 >20 而合法省略，Host 若做 diff-removal 会误删本应保留的 target；要正确清理必须新增 Core 侧「已删除」信号（C-17 变更）。r1（`:212`）与 WATCH-1 r2/r3（`:210`/`:186`）已裁决「不修」，本 review 维持。
4. **RH-4 是纯文档口径**：它**不是** wirelog/grant 表问题（那是 AC-S2-8 的另一半，C-16 §7 口径）。它指 SCAN-2 两个分片的零写快照用了**两套不同表集**：Core 分片 14 表（含 `book_cleanup_manifests`/`reading_progress`）、Host 分片 15 表（含 `regions`/`region_revisions`/`rendition_cache`）；两者并集 17 表，且与 `tests/fea11/test_source_sync.py:588-606` 的 **16 表** C-17 §6.2 派生基线不等价。需要一次精确的文档订正，不需要改实现。
5. **RH-5 是证据强度/门禁覆盖问题，不是缺陷**：`HostOptions.SourceScanTimeProvider` 是**真实 seam**（`:111-112`，已注入 scheduler/executor/watcher/identity cache）；缺的是 **fake-Core seam**——`HostRuntime` 内部 `new` 具体 `HostSourceScanExecutor`/`HostSourceScanTargetEnumerator`（`HostRuntime.cs:1382-1403`），无注入点，HostRuntime 级的「成功枚举 / 非阻塞」只能靠 gated 真 IPC。而 canonical 全量 .NET 日志中这些 gated 用例**全部 SKIP**（`logs/host-r2-dotnet-full-3.log:105` 等 4 份），EV-09 来自 fixture 可用环境的单独运行（`logs/host-r2-runtime-enumeration.log`：1 passed）。**不建议为它改生产装配**；订正措辞 + 登记即可。
6. **判定**：RH-1、RH-2 值得修（极小，同文件同机制）；RH-4 值得订正（零代码）；RH-3、RH-5 只登记。五项合成**一张**卡是合适的——它们是同一个子系统的同一条 limitation 带，拆卡只会增加生命周期成本。**不建议**把 RH-3/RH-5 立项。
7. **优先级**：L-R11 实现（进行中，READY）→ **SCAN-RH-1（本推荐，可穿插）**。C-04b residual 已在评审期间完成（`698ac9524` delivery + `63b95abda` closeout，卡 `status: done`），不再占队列；B2 延后；UI P3 已由 `FEA-12-UI-RESIDUAL-1` done 收口。

## 1. 核对范围与方法

**已读（只读）**
- Host 实现：`apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs`（2389 行，逐段核对 refresh/targets/tick/backoff/dispose/枚举映射）、`HostRuntime.cs`（scheduler 装配、`RequestSourceScanRefresh`、refresh helper、stop）、`HostOptions.cs`、`Sources/SourceScanStatus.cs`、`Sources/SourceAccessRegistry.cs`、`Sources/SourceWatcher.cs`、`Sources/SourceReadCoordinator.cs`（`source_revoke_root` 分支）。
- Core 实现：`src/application/sources/scanner.py`（`list_scan_targets`）、`src/infrastructure/sqlite/source_sync.py`（`list_scan_target_candidates`、`get_source_location_current`）、`src/bootstrap/core_service.py`（`source_list_scan_targets` 分发、`RegisterSourceReadGrant`）。
- 测试：`apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceScanSchedulerTests.cs`、`SourceScanExecutionRecoveryTests.cs`、`Fea11Scan2HostRuntimeTests.cs`、`Fea11ScanIpcTests.cs`、`Support/HostFixture.cs`/`HostSidecarFactAttribute.cs`；`tests/core/test_core_scan_target_commands.py`、`tests/fea11/test_source_sync.py`（仅零写表集部分）。
- 卡/评审/证据：`doc/tasks/FEA-11-SCAN-2.md`（AC、EV、Closeout `:244-254`）、`doc/reviews/FEA-11-SCAN-2-r1.md`（`:29/:46/:83/:188/:212`）、`-r2.md`（`:168-200/:209-225`）、`doc/tasks/FEA-11-WATCH-1.md`（limitation `:111/:129/:149/:199/:213`）、`doc/reviews/FEA-11-WATCH-1-r2.md:210`、`-r3.md:186`、`doc/reviews/DSH-PROGRESS-2026-11-07.md:12/:19`、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`（HEAD 版）、`verification/FEA-11-SCAN-2/host-cold-start.json`、`host-r2-cold-start.json`、`logs/host-r2-*.log`。
- 历史 scope 口径：`doc/reviews/FEA-11-RUN-GRANT-2-scope-r1.md:294-296`、`doc/reviews/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1-scope-r1.md:536`、`doc/reviews/FEA-11-SCAN-2-scope-r1.md`。

**未读/未覆盖**：`doc/**` 全量历史、`verification/**` 全量 EV（只抽 EV-05/EV-09 与相关日志）、App/UI 层真实导入链、真实用户数据。运行与未跑项见 §7.1–§7.2。

## 2. RH-1…RH-5 事实表

| # | 当前实际行为（文件:行） | 触发条件 | 影响 | 现成覆盖 | 性质 |
|---|---|---|---|---|---|
| **RH-1** | `RefreshTargetsAsync` 抢不到 `_tickGate` 时只置 `_refreshPending` 并返回 false（`SourceScanScheduler.cs:704-717`）；重放只发生在 `TickAsync` 尾部（`:912-914` → `:850-878`）；refresh 自己的 `finally` 只 `Release()`（`:791-794`）。注释却写 "Called after a tick (or a refresh)"（`:846-849`），方法注释仍写 "merged, never queued"（`:685-687`，r2 P3-7 未落） | 一次 refresh 在飞（枚举进行中）时又来了第二次 refresh（例：连续两次导入完成） | 第二次枚举延迟到下一 tick 或下一 hint；默认 interval 900 s，可配 60–86400 s。不丢、不重复、无写；目标集晚一个周期收敛（首次扫描可能再晚一个 tick） | `RefreshRequestedDuringTick_IsReplayedAfterTickCompletes`（`SourceScanSchedulerTests.cs:1292-1325`）覆盖「tick 在飞 + refresh 到达」；**无**「refresh 在飞 + refresh 到达」用例 | 缺陷（低）+ 注释与实现不一致（文档债） |
| **RH-2** | `HostRuntime.RefreshSourceScanTargetsAsync` 固定传 `CancellationToken.None`（`HostRuntime.cs:227-231`），cold-start（`:1441`）与 App refresh（`:223`）共用；scheduler 无 lifetime CTS（字段区 `:348-384` 只有 `_loopCts`）；`DisposeAsync` 先 join loop、再等 hint ≤2 s、然后 `_tickGate.Dispose()`（`:1050-1079`），**不 join 在飞 refresh** | Host 停机/重启时恰有一次 refresh 在飞（冷启动枚举或导入后刷新） | 枚举不被取消；`Release()` 命中已 Dispose 信号量抛 `ObjectDisposedException`（静态推断：`SemaphoreSlim.Release` 在 `Dispose` 后抛），被 `HostRuntime` 外层 catch 记 `source scan refresh failed: ObjectDisposedException`；后台任务在 CoreClient 销毁期间继续跑（异常均被吞）。不崩溃、不丢数据、不影响下次启动 | `DisposeAsync_WithInFlightHintPass_CompletesWithoutThrowing`（`:1493-1510`）只覆盖 hint pass；**无** refresh 用例 | 缺陷（低，生命周期/竞态）+ 测试缺口 |
| **RH-3** | `_targets` 只有 `RegisterTarget` 覆盖写（`:480-496`）与 `MergeTargetsLocked` 的 add/update（`:797-819`）；**无** `_targets.Remove`/`RemoveTarget`/`Unregister`（grep 为空）。Core 枚举排除软删源（`src/infrastructure/sqlite/source_sync.py:92` `WHERE s.deleted_at IS NULL`）；Host 侧撤销 root（`SourceReadCoordinator.cs:761-778` → `SourceAccessRegistry.Revoke` `:100-110`，只 bump generation + `RevokedAt`，**不删条目**）后 target 仍在集合内，`ApplyOutcome` 对 `Skipped` **不设 backoff**（`:1243-1250`），每轮转都被重试 | i) 撤销 root / 重授权前后 generation 漂移；ii) Core 因 missing location facts、未知 kind、`project_ids` 0 或 >20 而合法省略该源；iii) 未来若出现 `sources.deleted_at` 写入（当前 `src/**` 无该 UPDATE，grep 零命中） | 预算稀释（每 tick 8 槽被占；N 个 stale 时 live 源扫描周期约 × `(N+live)/8`）× 永久；每 tick 每 stale target 1 次 `Registry.List()`（整文件读 + 解密）与 1 条 info 日志；`_recent` 每 tick 追加跳过行（上限 50，内存有界）；watch 侧每次 Sync 对每个 stale target 打一条 `source watch uncovered` WARN（`SourceWatcher.cs:331-339`）。**无正确性破坏**（零写、不伪造 missing） | 无测试；WATCH-1 r2 `:210`/r3 `:186`、SCAN-2 r1 `:212` 均已裁决「不修」 | 设计取舍 + 已裁决 limitation（非缺陷） |
| **RH-4** | AC-S2-8 正文写「枚举与扫描前后 **14 表**快照逐行相等」（`doc/tasks/FEA-11-SCAN-2.md:100`），带「14/15 表口径见 r2」限定；实际三套表集：Core 分片 14 表（`tests/core/test_core_scan_target_commands.py:44-59`）、Host 分片 15 表（`verification/FEA-11-SCAN-2/host-cold-start.json:15-32`，`host-r2-cold-start.json` 同）、C-17 §6.2 派生 16 表（`tests/fea11/test_source_sync.py:588-606`）。14∪15 = 17 表，与 16 表基线相比**缺** `pipeline_runs`/`pipeline_run_targets`/`step_result_candidates`，**多** `books`/`chapters`/`sources`/`book_cleanup_manifests` | 任何引用 AC-S2-8「零写」的读者/后续卡 | 口径不可操作：读者无法判断「零写」到底覆盖哪些表；若有人写「满足 C-17 §6.2 零写基线」即为**不实陈述**。无运行时影响 | r2 review `:179`「14 vs 15 表集合不同（并集覆盖）」、`:192` P3-6、`:221`/`:223`；**没有一处**写出具体差异与并集规模 | 文档口径（非缺陷、非测试缺口） |
| **RH-5** | `HostOptions.SourceScanTimeProvider` 是真实 `TimeProvider` seam（`HostOptions.cs:111-112`，默认 `TimeProvider.System`），已传入 scheduler loop（`Task.Delay(..., _timeProvider)` `SourceScanScheduler.cs:1125`）、executor、watcher、identity cache。但 HostRuntime 内部直接构造具体 `HostSourceScanExecutor`/`HostSourceScanTargetEnumerator`（`HostRuntime.cs:1382-1403`），`HostOptions` **无** enumerator/executor 注入点；HostRuntime 级测试只能整机起真 sidecar（`Fea11Scan2HostRuntimeTests.cs:28 [HostSidecarFact]`，`:20-24` 自述 limitation） | 需要 HostRuntime 级「成功枚举」「非阻塞」判别证据时 | 证据强度：canonical 全量 .NET 日志中 `Fea11Scan2HostRuntimeTests.Ready_StartsBackgroundEnumeration_WithoutBlocking` 为 `[SKIP]`（`logs/host-r2-dotnet-full-1/2/3.log`、`gates-r2-integration.log:294`），`Fea11ScanIpcTests` 三个真 IPC 用例同样 SKIP（opt-in `NEWMANGA_FEA11_IPC=1`，`Fea11ScanIpcTests.cs:22`）；EV-09 由单独一次 fixture 可用运行产出（`host-r2-runtime-enumeration.log`：1 passed），且 `enumeration_present_immediately_after_start=true` 使其**不能**判别「非阻塞」（r2 P3-9 已指出）。成功路径语义由组件级真实 Core E2E（EV-05/06/07/08）+ r2 审查者独立复现补足 | 有 gated 用例（可选环境）；默认门禁不覆盖 | 测试强度/门禁覆盖缺口 + 文档措辞（非缺陷） |

### 2.1 补充事实（逐项回答任务书的三个特别核实点）

**RH-3：是否真的只增不减？软删/移除根后是否 stale target 反复枚举？有现成清理 API 吗？**
- 是，只增不减：唯一写入点是 `RegisterTarget`（覆盖同一 `source_id`）与 `MergeTargetsLocked`（`TryGetValue` → 覆盖；否则新增）。没有任何删除/收缩路径。
- 撤销 root 后：`SourceAccessRegistry.Revoke` 只把 generation+1 并写 `RevokedAt`（条目保留），`List()` 仍返回该条目（`SourceAccessRegistry.cs:60` 注释明说「包括 root 当前不可用/被替换的条目」）；于是 `VerifyEnumeratedTarget` → `SelectEnumeratedEntry` 给出 typed skip，**每轮转一次**、无 backoff。
- 软删源：Core SQL 排除，但 `src/**` 中**没有**写 `sources.deleted_at` 的代码（grep 零命中），所以当前产品流程里「Core 软删源」尚无生产者；可达的触发是「撤销 root / generation 漂移 / Core 枚举 typed skip（missing location facts、未知 kind、project_ids 0 或 >20）」。
- 现成清理 API：**没有**。可用的只有 `RegisterTarget` 覆盖、`SourceAccessRegistry.Reset`（整库）与 `Revoke`（不删条目）。若要删单个 target，需要新 API。
- 关键陷阱：**枚举省略 ≠ 删除**。Core 的 `list_scan_targets` 对同一源可能因 typed 原因（`missing_location_facts`/`unknown_source_kind`/`project_ids_empty`/`project_ids_over_limit`，`scanner.py:128-155`）而省略它；Host 若按「不在本次枚举结果里就删」清理，会在源临时不可枚举时**静默丢 target**（下次需要用户再导入或重启才回来），比现在的预算稀释更糟。正确清理需要 Core 侧「这个源已删除」的显式信号（C-17 additive）。

**RH-5：`HostOptions.SourceScanTimeProvider` 是真实 seam 吗？「无 fake-Core seam」意味着什么缺口？gated 真 IPC 能否补足？**
- 时钟 seam 真实存在且全链注入（scheduler loop 的 `Task.Delay` 用 `_timeProvider`，状态时间戳同源；WATCH-1 的 debounce 同源）。它**不解决**成功枚举问题。
- 「无 fake-Core seam」= `HostRuntime` 的 scan 切片装配写死具体类型（executor/enumerator），`HostOptions` 没有工厂/注入口，也没有 `InternalsVisibleTo` 式的测试钩子（HostRuntime 里现有 seam 只属于 2C 的 renewal 面）。因此 HostRuntime 级测试**要么**整机起真 sidecar（受 bundle 版本与 fixture 环境限制），**要么**不测。
- gated 真 IPC 能补足**语义**（真实 Core 上枚举成功、五命令白名单、15 表零写、`source_id` 权威），但补不了**两个**东西：① 默认门禁覆盖（opt-in + fixture 环境，canonical 日志里 SKIP）；② 「Ready 非阻塞」的判别力（现有断言在 StartAsync 返回后立刻取状态，实测枚举已解析，无法区分阻塞/非阻塞；要判别必须注入一个可控延迟的枚举器——正是缺的那个 seam）。

**RH-4：14/15 表并集口径具体指什么？是否已记录？需文档更正还是实现变更？**
- 不是 wirelog，也不是 grant 表。是**同一个 Core 业务库的两套零写快照表集**：Core 分片与 Host 分片各自挑了不同子集断言「前后逐行相等」。并集 17 表；与 `tests/fea11/test_source_sync.py:588` 注释所称的 "C-17 §6.2 zero-write comparison set（card frozen rule 4: 16 tables）" 也不同——即项目里同时存在 **14 / 15 / 16** 三套零写表集口径。
- 已记录但不可操作：卡 `:100` 有「14/15 表口径见 r2」，r2 `:179`/`:192`/`:221`/`:223` 说「并集覆盖、非同一口径」，但全项目没有任何一处列出两套集合的具体差异、并集规模与 16 表基线的关系。
- **只需文档更正**，不需要实现变更：枚举是单条 SELECT（`source_sync.py:82-112`）；扫描的写入只发生在既有的 `ScanSourceSync` 通道（source 系表），与快照表集口径无关；把表集口径写清即可。**不要**为了统一表集去改实现或改 C-17 字节（后者要 UNFREEZE，收益为零）。

## 3. 判定与建议

### 3.1 逐项判定

| # | 是否值得建卡修 | 形态 | 契约/pin | 预计成本 | 风险 | 判别性测试思路 |
|---|---|---|---|---|---|---|
| RH-1 | **值得（小）** | implementation（也可退化为 documentation：只改注释 + 登记）。推荐实现 | 0 pin，无 UNFREEZE | 1 文件 ~15-25 行 + 1 单测 | 触碰单飞闸门：重放时机错会与 WATCH-1 hint 重放叠加（`TickAsync` 尾部已有 `ReplayPendingRefreshAsync` + `ReplayPendingHintAsync` 两段） | 阻塞 enumerator 的第一次 refresh → 在飞时发起第二次 refresh（返回 false）→ 释放第一次 → 断言**无需调用 TickAsync** 就发生第二次枚举且新 target 已合并；删掉重放调用 → 红。再加一条「重放期间第三次 refresh 不导致无限递归」 |
| RH-2 | **值得（小）** | implementation | 0 pin | 1 文件 ~20-30 行（lifetime CTS + link + Dispose join）+ 1 单测 | 同上；Dispose 顺序改错可能与 hint join 的前 2 s 预算冲突 | 阻塞 enumerator → `DisposeAsync()` → 断言 enumerator 观察到 token 取消、Dispose 有界完成、`RefreshTargetsAsync` 不抛、无 `ObjectDisposedException` 日志；改回 `CancellationToken.None` 且不 join → 红（永不取消/Dispose 提前完成） |
| RH-3 | **不值得** | 仅 limitation | —（若要 Core「已删除」信号则需 C-17 additive → UNFREEZE，本项 Out） | 若强做：1 文件 + 1 新 API + 决策（删/不删语义）≥ 半天 | 高：diff-removal 会误删 typed-skip target；与 WATCH-1「target 集只增不减不修」的既有裁决冲突 | 若未来做：枚举返回空不得导致 targets 收缩；只有显式删除信号才收缩 |
| RH-4 | **值得（零代码）** | documentation | 0 pin | 1-2 个 doc 文件、append-only 一行 + 新卡 limitation 一段 | 若改 done 卡的 AC 判词会污染历史证据 → **只允许 append-only limitation 订正** | 文档核对（无测试）：三套表集逐项列出、并集 17、与 16 表基线差异四条 |
| RH-5 | **不值得修** | 仅 limitation + 措辞订正 | —（在 `HostOptions` 加注入口属生产装配变更；升级 sidecar bundle 属打包任务） | 若强做：1 生产文件 + 1 测试基建 + sidecar 版本/CI 改动，成本远大于收益 | 中：为测试改生产装配，且仍不能解决 bundle 版本 | 若未来做：注入可控延迟 enumerator，断言 `StartAsync` 在枚举未完成时已返回 Ready |

### 3.2 是否合并成一张卡

**合并为一张卡是合适的**，理由：
1. 五项是同一子系统（`SourceScanScheduler` + HostRuntime 装配）的同一条 limitation 带，出现在同一段 closeout 记录（`FEA-11-SCAN-2.md:252`）；
2. 真正要动代码的只有 RH-1/RH-2，且**同一文件、同一机制**（单飞闸门 + 生命周期）；拆两张卡会重复冻结、审查、门禁各一次；
3. RH-4/RH-3/RH-5 是文档 AC，不引入实现面；放在同一卡里可以让「改了什么/没改什么」在一份证据里闭合；
4. 反面方案（五项各一卡）违反最小生命周期原则；把 RH-1/RH-2 并入 L-R11 或 C-04b 则是跨域污染（L-R11 是 Core-only，C-04b 是契约文档）。

### 3.3 推荐卡面（草案，供 DSH 冻结）

```yaml
id: FEA-11-SCAN-RH-1
title: SCAN-2 复核残余收口：refresh pending 重放 + refresh 生命周期绑定（Host-only，0 pin）；
       RH-3/RH-4/RH-5 口径登记
kind: implementation
governance_version: 3
status: proposed
approval: 待 DSH 裁决（scope review = doc/reviews/FEA-11-SCAN-RH-scope-r1.md recommended）
suggested_owner: codex（或 zcode；Host 小改动，独立上下文 Review）
owner: null
reviewer: null
depends_on:
  - FEA-11-SCAN-2
  - FEA-11-WATCH-1
base_commit: <冻结时 clean main head>
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
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs      # 仅 token 传递；若在 scheduler 内部 link 则保持零 diff
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceScanSchedulerTests.cs
  - doc/tasks/FEA-11-SCAN-2.md                                  # 仅 append-only limitation 订正；禁改 AC 判词/EV
out_of_scope:
  - RH-3 的 target 清理 / RemoveTarget / _targets 收缩；Core 侧「源已删除」信号（C-17 additive）
  - RH-5 的 fake-Core seam / HostOptions 注入点 / sidecar bundle 升级 / CI fixture
  - 大库冷启动预算标定、folder/encrypted 导入 E2E、L-S1、L-S4、L10、AC11-1
  - 契约字节（C-17 v1.1 / C-16 v1.7 / C-15 / C-06 / M2-C1 / ADJ-001）、schema/wire/命令/能力/错误码/PROTOCOL_MINOR、依赖
  - App/UI、WATCH-1 done 卡字节、SCAN-2 的 AC 判词与 EV 行
  - STATUS/REBASELINE_PLAN/TASK_LEDGER（Lead 保留）；push
```

**Acceptance Criteria（5 条，冻结时定稿）**

- **AC-RH-1（RH-1 修复：幂等重放，不依赖下一次 tick）**：`RefreshTargetsAsync` 在**完成一次枚举并释放单飞闸门之后**（成功或 typed unavailable；被取消 / 已 disposed 的提前返回不重放，pending 留待下一次 pass），若 `_refreshPending` 为真则重放一次；重放有界（每完成一个 pass 至多一次，不得递归无界）；`TickAsync` 既有重放语义与顺序（refresh 在 hint 之前）不变；`RefreshTargetsAsync` 的 XML 注释改为 "coalesced and replayed after the in-flight pass"（落 r2 P3-7）。判别性：新增「refresh 在飞时第二次 refresh → 第一次完成后立即发生第二次枚举并合并新 target（不调用 TickAsync）」；删掉重放 → 红。
- **AC-RH-2（RH-2 修复：lifetime 绑定 + 停机 join）**：scheduler 内部持有 lifetime CTS；`RefreshTargetsAsync` 的枚举 token 与调用方 token、lifetime token link；`DisposeAsync` 先取消 lifetime、再有界 join 在飞 refresh（与 hint pass 同口径，建议 ≤2 s），随后才 `_tickGate.Dispose()`；不得出现 `ObjectDisposedException` 逃逸到日志（若发生，视为未修）。判别性：新增「枚举阻塞 + DisposeAsync → 枚举观察到取消、Dispose 有界完成、无 ObjectDisposed 日志」；改回 `CancellationToken.None` 且不 join → 红。
- **AC-RH-3（RH-4 文档订正，零代码）**：在本卡 limitation 与 `FEA-11-SCAN-2.md` closeout limitation（append-only 一行）写清三套表集与并集：Core 14 表、Host 15 表、C-17 §6.2 派生 16 表；并集 17 表；与 16 表基线相比缺 `pipeline_runs`/`pipeline_run_targets`/`step_result_candidates`、多 `books`/`chapters`/`sources`/`book_cleanup_manifests`；**禁止**任何文档写「满足 C-17 §6.2 零写基线」或「全库零写」。判别性：文档核对。
- **AC-RH-4（RH-3/RH-5 登记）**：本卡 limitation 逐条写明——RH-3：只增不减、无删除 API、Skipped 无 backoff、预算稀释 `(N+live)/8`、watch 每次 Sync 的 uncovered WARN、**枚举省略≠删除**、清理需 C-17 变更（Out）；RH-5：时钟 seam 存在（`HostOptions.cs:111-112`）、无 fake-Core seam、canonical 全量日志中 gated 用例 SKIP、EV-09 不能判别非阻塞、WATCH-1 卡 `:111/:129/:199/:213` 的「无注入时钟」表述按本卡口径订正理解（**不改其字节**）。判别性：文档核对。
- **AC-RH-5（门禁 / 证据 / 不夸大）**：定向 `--filter "FullyQualifiedName~SourceScan"`（起点 **68 passed/0/0**）与 `~SourceWatcher`（起点 **19 passed/0/0**）+ 新增用例全绿；全量 .NET **1680/0/96 不降**（跑后 `git checkout -- verification/FEA-09`）；全量 pytest **3363/10 不降**；`tools/governance/check.ps1` PASS；`verify_pins.ps1` **18/18**；scope diff ⊆ `allowed_paths`；EV 逐条可复算。禁止把本卡表述为「RH-3 已清理」「RH-5 已补 seam」「SCAN-2 残余已全部解决」。

### 3.4 「仅登记」替代（若 Lead 选择不做）

- **RH-3、RH-5 一律走此路径**（理由见 §3.1）。登记位置：本卡 limitation + 保留 `doc/tasks/FEA-11-SCAN-2.md:252` 的既有登记 + 在 `FEA-11-WATCH-1` 的后续引用中按订正口径理解（不改 done 卡字节）。
- **RH-4** 若也降级为仅登记：现有 `:100` 的「14/15 表口径见 r2」+ r2 `:179` 已足以让读者找到方向，但**并集规模与 16 表基线关系仍缺**；若完全不做，任何后续卡引用 AC-S2-8 时必须自行重算，属于可接受但明确的债。
- **RH-1/RH-2** 若降级为仅登记：**最低限度必须改那两句注释**（`:685-687`、`:846-849`），否则代码在文档层面持续撒谎——这是零风险的 documentation 改动，不应留。
- **不得声称已修**：无论走哪条路径，后续 STATUS/卡/Handoff 都不得写「RH-1 已修复」「RH-2 已解决」「SCAN-2 残余清零」；只能写「已登记/已订正口径」。

### 3.5 Lead 裁决点（附推荐）

| # | 问题 | 推荐 | 影响 |
|---|---|---|---|
| D-1 | RH-1 取「重放修复」还是「仅改注释 + limitation」？ | **重放修复**（~15-25 行 + 1 测试） | 决定是否有一条行为 AC |
| D-2 | 是否允许对 done 卡 `FEA-11-SCAN-2.md` 做 append-only limitation 订正？ | **允许**（只改 closeout limitation 一行，禁改 AC 判词/EV） | 决定 RH-4 的登记落点 |
| D-3 | 卡 id / owner / 是否并入其它卡？ | **`FEA-11-SCAN-RH-1` 单卡**；owner 建议 codex（Host 小改动）或 zcode；不并入 L-R11/C-04b | 决定生命周期 |
| D-4 | RH-3/RH-5 确认只登记？ | **确认**（与 r1 `:212`、WATCH-1 r2/r3 裁决一致） | 防止范围膨胀 |

## 4. 契约与 pin 判定

- **RH-1/RH-2：0 pin，无 UNFREEZE**。全部在 Host 进程内（scheduler 单飞/生命周期），不碰 wire、不碰 Core、不碰 C-17/C-16 字节。
- **RH-3：0 pin（仅登记）**。若要「Core 已删除信号」，必须新增 C-17 命令/DTO/capability（additive）→ 需 UNFREEZE + 独立字节复核；本项 **Out**，本卡不得触发。
- **RH-4：0 pin**。只改 `doc/**`（新卡 + done 卡 limitation append）；不得改 C-17 §6.2 文本（改契约要 UNFREEZE，且无收益）。
- **RH-5：0 pin（仅登记）**。若未来加 `HostOptions` 注入口，属生产装配变更但仍 0 pin；升级 sidecar bundle 是打包/发布面，另卡。
- 冻结前后必须 `pwsh -NoProfile -File tools/governance/verify_pins.ps1` = **18/18**；本卡不允许任何 `doc/plan`、`doc/contracts`、`src/infrastructure/sqlite/schema.py` 的 diff。

## 5. 影响面、风险与回退

**影响面（推荐卡面）**
- 生产代码：`SourceScanScheduler.cs`（1 文件；`HostRuntime.cs` 可选、若改只限 token 传递）。
- 测试：`SourceScanSchedulerTests.cs` +2 用例（refresh-in-flight replay、dispose-in-flight refresh）。
- 文档/证据：新卡 1、Review 1、Handoff 1、`verification/FEA-11-SCAN-RH-1/**`、SCAN-2 卡 limitation append-only 一行。
- 零 schema / 零 wire / 零 Core / 零 App / 零依赖。

**风险**
1. **单飞与重放叠加**（中）：`TickAsync` 尾部已有 refresh 重放 + hint 重放两段（`:912-917`）；在 refresh 出口再加一段重放，必须保证「每个 pass 至多一次」「不与 hint `_hintTask` 争用」，否则可能出现重放风暴。缓解：只在 refresh 的 `finally` 之后调用一次、用同一 `_refreshPending` 布尔清零、并加「重放期间再来 refresh 不递归」测试。
2. **Dispose 顺序**（中）：`DisposeAsync` 现在先 join loop、再等 hint ≤2 s、再 Dispose gate。插入 refresh join 后必须保持「先取消、再 join、最后 Dispose」；否则 `Release` 抛 `ObjectDisposedException` 的老问题只是换了个位置。缓解：判别测试直接断言"无 ObjectDisposed 日志"。
3. **误伤 WATCH-1**（低-中）：hint 用同一个 `_tickGate`；回归由 19 个 `~SourceWatcher` 测试 + `SourceScanSchedulerTests` 中的 hint 用例兜底。
4. **文档越界**（低）：RH-4 若误改 done 卡 AC 判词，会污染历史证据；缓解：append-only 限制写进 allowed_paths 注释与 AC。

**回退**：单 commit revert 即可；无 schema/迁移/契约/数据影响，回退只恢复「refresh 延迟到下一 tick」与「停机 WARN」两个已登记 limitation 的现状。

## 6. 优先级

| 顺位 | 项 | 状态/依据 | 建议 |
|---|---|---|---|
| ① | **FEA-11-L-R11-GATE-UNIFY-1**（Core-only，0 pin） | `status: ready`（`doc/tasks/FEA-11-L-R11-GATE-UNIFY-1.md:6`）；评审期间 `src/bootstrap/core_assembly.py`、`core_service.py`、`src/infrastructure/sqlite/source_sync.py` 有**未提交改动**（属该卡 allowed_paths），说明实现正在进行 | **不打断**；SCAN-RH 不得抢占其门禁/审查窗口 |
| ② | **FEA-12-CORE-C04B-RESIDUAL-1**（docs-only，0 pin） | **已完成**：`698ac9524` delivery + `63b95abda` closeout；卡 `status: done`、独立 r1 approved | 已不占队列（PLAN `:49` READY 行与 `STATUS.md:7` 已同步更新） |
| ③ | **FEA-11-SCAN-RH-1**（本推荐） | 本报告 | **可穿插，当前队列里下一个可实现的候选**：与 L-R11 文件面零冲突（Host vs Core），建议在 L-R11 收口后释放，避免同窗口两线并审 |
| ④ | **UI P3** | `FEA-12-UI-RESIDUAL-1` done（`REBASELINE_PLAN.md:55` 当前 DAG 行） | 已收口，无排队项 |
| ⑤ | B2（roots UI） | `REBASELINE_PLAN.md:55`「B2 延后（无消费者）」 | 维持延后 |

**一句话排队**：L-R11 → **SCAN-RH-1（可穿插，不抢窗口）**；C-04b 已 done、UI P3 已收、B2 延后。

## 7. 实跑与证据

### 7.1 实测（本次会话，read-only）

| # | 命令 | 结果 | 证据 |
|---|---|---|---|
| 1 | `git log --oneline -3 -- apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs` | `8709d6159`（L-S4-B-1 枚举 target 自身 live registry）/ `3ccb0509e`（L-S4-B）/ `aa0a5562b`（RUN-GRANT-2A） | 终端记录 |
| 2 | 同上 `-- HostRuntime.cs` | `7c95bb3c4`（2C r1 返修）/ `c40489b5d`（2C 接线）/ `f6b5a761a`（L-S4-B-2） | 终端记录 |
| 3 | 同上 `-- src/application/sources/scanner.py` | `20faf062a`（SCAN-2 r2 P2-2）/ `0cb5177ca`（SCAN-2 Core 分片）/ `b4ad109da` | 终端记录 |
| 4 | 同上 `-- doc/tasks/FEA-11-SCAN-2.md` | `919c9aa1e` / `cc35abc1c` / `555f57b8d` | 终端记录 |
| 5 | `C:/Python314/python.exe -m pytest tests/fea11 -q -k 'scan or scheduler'` | **14 passed, 192 deselected, 8 warnings, 0.75 s，EXIT=0** | `workspace\SCAN-RH\scope-review\pytest-fea11-scan.log` |
| 6 | `dotnet test tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj --no-build -c Release --filter 'FullyQualifiedName~SourceScan'` | **68 passed / 0 failed / 0 skipped，310 ms，EXIT=0** | `workspace\SCAN-RH\scope-review\dotnet-host-sourcescan.log` |
| 7 | 同上 `--filter 'FullyQualifiedName~SourceWatcher'` | **19 passed / 0 / 0，521 ms，EXIT=0** | `workspace\SCAN-RH\scope-review\dotnet-host-sourcewatcher.log` |
| 8 | `git status --porcelain` / `git rev-list --count origin/main..HEAD` | 我零改动；工作树含**其他 Agent** 的未提交改动（`doc/reviews/FEA-12-CORE-C04B-RESIDUAL-1-r1.md`、`src/bootstrap/core_assembly.py`、`src/bootstrap/core_service.py`、`src/infrastructure/sqlite/source_sync.py`）；期间 C-04b residual 两次提交（`698ac9524`／`63b95abda`，docs-only），HEAD 从 `28a2826af` 前进到 `63b95abda`，`origin/main..HEAD` = 2 | 终端记录 |

**构建有效性说明**：`.NET` 用 `--no-build` 跑既有 Release 产物；`tests\...\NewManga.Host.Tests.dll`（21:29:42）与 `src\NewManga.Host\bin\Release\net9.0\NewManga.Host.dll`（21:33:50）均晚于 `SourceScanScheduler.cs`（15:55:35）的最后修改，故对当前 Host 代码有效；Core Python 的并发未提交改动不影响该过滤（Host 单测不加载 Python）。

**口径提示**：第 5 项 pytest 运行时工作树含其他 Agent 对 `src/bootstrap/*.py`、`src/infrastructure/sqlite/source_sync.py` 的未提交改动（L-R11 实现），因此它不是「HEAD 干净树」的历史基线，只能作为「当前树 + 该改动下 14 个 scan/scheduler 用例仍绿」的证据。

### 7.2 未跑（明确声明）

- **全量 pytest / 全量 .NET**：未跑，采信 `doc/STATUS.md:20` 的 **pytest 3363/10、.NET 1680/0/96**（2026-11-07 2C closeout + 独立 r2 复核）。
- **gated 真 IPC**：未跑（需 `NEWMANGA_FEA11_IPC=1` + `NEWMANGA_CORECLIENT_SIDECAR_DIR` 指向 sidecar fixture；本会话未配置，且属 opt-in）。
- **变异/红绿验证**：未做（推荐卡尚不存在，判别性设计只在 §3.1 给出）。
- **EV 58 行 sha256 全量复算**：未做；只抽读 EV-05/EV-09 与相关日志。
- **审查者独立设备上的「软删源 + 已核实基线 + 文件消失」是否会在 Core 侧产生 missing 写**：未验证，属假设，本报告不作结论（见 RH-3 行：当前无 `sources.deleted_at` 生产者）。
- 未 `fetch` 远端；`origin/main` 只用于本地 ahead 计数。

### 7.3 登记检索（RH 关键词）

- `RH-1…RH-5` 只在 `doc/tasks/FEA-11-SCAN-2.md:252`（残余风险/limitation）与 `doc/reviews/FEA-11-SCAN-2-r2.md:199/:221/:223`、`doc/reviews/FEA-11-WATCH-1-r2.md:210/:269/:279`、`doc/reviews/FEA-11-WATCH-1-r3.md:186/:252/:269`、`doc/tasks/FEA-11-WATCH-1.md:111/:129/:149/:199/:213`、`doc/handoffs/DSH-HANDOFF-2026-11-06.md:42/:75/:95/:107/:227/:239`、`doc/handoffs/DSH-PROGRESS-2026-11-07.md:12/:19` 出现；`doc/TASK_LEDGER.md` **无** SCAN-RH 条目（即：尚未建卡）。`doc/tasks/FEA-11-SCAN-2.md:252` 已登记 RH-1…RH-5，因此「仅登记」路径**无需新写**登记，只需订正措辞（RH-4/RH-5）。
- `doc/REBASELINE_PLAN.md`（HEAD `63b95abda`）`:49` READY 行现只列 `FEA-11-L-R11-GATE-UNIFY-1`（C-04b 已 done 并移出）；`doc/STATUS.md:7` 已把「下一候选」改为 **SCAN-RH（scope review 中）**，与本报告的排队建议一致。

### 7.4 观测到的仓库状态偏差（只报告，不裁决）

- `doc/STATUS.md:23` 写「main 已于 2026-11-07 push 至 `07a7d746a`、AHEAD=0」，而当前 HEAD 是 `63b95abda`（`07a7d746a` 是 HEAD 祖先）、`origin/main..HEAD`=2（C-04b 两次 docs-only 提交未 push）。属 STATUS 指针滞后，建议 Lead 在 L-R11 closeout 时顺手订正；不影响本报告的 RH 事实与建议。

## 8. 真实性声明

- **写入范围**：本次唯一写入仓库的文件是本报告 `doc/reviews/FEA-11-SCAN-RH-scope-r1.md`；仓外临时/日志仅写入 `G:\CODEX\New Manga.workspace\SCAN-RH\scope-review\`（3 个运行日志）。未修改任何生产代码、测试、契约、任务卡、`verification/**`；未 `git add`/`commit`/`push`；未触碰工作树中其他 Agent 的未提交改动（评审期间亲眼见其变化：`src/bootstrap/core_assembly.py`、`core_service.py`、`src/infrastructure/sqlite/source_sync.py`、C-04b 卡/证据，HEAD 从 `28a2826af` 前进到 `63b95abda`）。
- **独立性**：我是 fresh subagent（session `c50bc2b0-52e4-4d23-a60e-22115ea29a3a`），未参与 SCAN-1/SCAN-2/WATCH-1 的实现、返修或复核；本报告只读 reviewed_head `28a2826af`（+ 已核对 `698ac9524`/`63b95abda` 均为 docs-only 前进）。
- **不夸大**：本报告**不声称任何 RH 项已修复或已解决**；RH-3/RH-5 建议不修，RH-1/RH-2 的建议修复尚未实现、尚无判别测试；所有成本/风险为估算而非实测。文中标注「静态推断」的结论（RH-2 的 `ObjectDisposedException` 路径、RH-3 的预算稀释倍数）未经运行验证。
- **未跑项**见 §7.2；**实测数字**见 §7.1（均带 EXIT 与日志路径）。若后续实现卡落地，本报告自动降为历史记录。
