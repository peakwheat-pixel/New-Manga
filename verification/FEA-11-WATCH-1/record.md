# FEA-11-WATCH-1 实现记录（Host-only 目录 watcher hint → 全量重枚举）

- base_commit：`919c9aa1e`
- Owner：`fea12-core-host`（DSH Agent Teams；实现者）
- 依据：`doc/tasks/FEA-11-WATCH-1.md`（scope 冻结；scope review NECESSARY）、C-01b SC-25、C-17 v1.1:18。
- 结论：AC-W1…AC-W5 全部 MET（证据见 §5）；**不**回填 AC11-1、不做启动全量扫描；不 push。

## 1. 实现摘要

### 1.1 新文件 `Sources/SourceWatcher.cs`

- `SourceWatchOptions`：`Enabled`、`MaxWatches`（默认 256，范围 1–4096）、`InternalBufferBytes`（默认 65536，夹紧 [4096, 65536]）、`DebounceMilliseconds`（默认 2000，范围 [250, 60000]）；`Normalized()` 对非法值 fail-safe 回落默认，绝不使 Host 启动失败。
- `ISourceWatchHandle` / `ISourceWatchFactory`：最小 watch seam；生产 `FileSystemSourceWatchFactory` 包装 BCL `FileSystemWatcher`（无新依赖），测试用 fake adapter（确定性事件/overflow，零 sleep）。
- `SourceWatcher`：
  - 只 watch `SourceScanScheduler.TargetSnapshot()` 中的目标；每次 arm 前用 `SourceAccessRegistry.List()` 复核（enumerated：registry_id/未撤销/generation 相等/root readable；legacy：存在 readable root 包含 path）；registry 不可读 → `SOURCE_REGISTRY_UNAVAILABLE` typed 降级（L-S1 口径，不崩）。
  - file target：仅当 path 是文件时 watch 父目录（非递归、`Filter`=精确文件名、事件名再做一次大小写不敏感精确匹配）；声明 file 但 path 是目录 → 不 watch、`uncovered`（不猜文件名）。folder target：watch 目录递归。
  - 一个 normalized path 至多 1 个 watcher；同 path 多 source 合并 source 集；同 source 重复注册/refresh 不增加 watcher；target 消失/撤销/替换 → 拆 watcher。
  - 事件 → 仅置 per-source due bit（2000ms 去抖窗口内 N 事件合并为 1 次；`TimeProvider.CreateTimer` 注入时钟，测试零 sleep）；**不**把 path/change type 传给 scheduler 或状态。
  - `Error`/`InternalBufferOverflowException`/根删除 → 不崩；`OverflowCount`/`Degraded`/`Uncovered` 计数（无路径），全部 target due（经 `scheduler.HintAllTargets`），丢弃并尝试 re-arm，失败计 `uncovered`；周期扫描仍兜底。
  - `Status()`：closed `SourceScanWatcherStatus`（Enabled/Armed/Active/Uncovered/OverflowCount/Degraded/LastHintAt/HintCount/DebouncedEvents/PendingHints），由 `scheduler.SetWatcherStatus` 投影进 `SourceScanStatus.Watcher`。
- 生命周期：`Start` 幂等；`Stop`/`Dispose` 幂等，注销回调、取消全部 debounce timer、拆所有 handle → Stop 后零 hint。

### 1.2 `SourceScanScheduler.cs`（增量，不重写 SCAN-1）

- `TargetSetChanged` 事件（`_gate` 外触发；逐 handler 隔离，watcher 异常不破坏注册/枚举）+ `TargetSnapshot()`（含 path，Host-only）。
- `HintSource(sourceId)`：仅对已注册 target 置 due bit，随后调度一次 hinted pass；`HintAllTargets(reasonCode)`：全部 target due（overflow/根删除）。
- 单飞与合并：hint 在 tick 在飞时置 `_hintReplayPending`，tick 释放 `_tickGate` 后最多重放 **1** 次（`HintedTickAsync`；不排队、不并发、不链式）；`HintIdleAsync()` 测试 seam。
- 顺序：hinted target 同预算内优先；其余保持原 AC-S3 rotation 顺序；hint 只由**实际扫描结果**消费（backoff/budget-deferred 保留 due bit；paused 保留）。
- 预算/退避/pause/零写语义完全沿用 SCAN-1；命令仍只有 `ScanSourceSync`；`Snapshot()` 增加 `Watcher`。
- hint 不写 `last_result`；内容未变的 hint 扫描结果仍是 `ok`，绝不写成 `changed`。

### 1.3 `HostRuntime.cs` / `HostOptions.cs`

- 新增 `SourceWatchEnabled`（默认 true）、`SourceWatchMaxWatches`、`SourceWatchInternalBufferBytes`、`SourceWatchDebounceMilliseconds`。
- Ready 后、scheduler 创建并 `Start()` 之后 arm watcher（先于冷启动枚举，使枚举 merge 回调可 re-arm；arming 只读、不阻塞 Ready）。
- 停机顺序：`Stop/Dispose` 先 `StopSourceWatcher()`（同步 disarm）→ `StopSourceScanSchedulerAsync()` → host session/Core；`Watcher` 属性随后为 null。

### 1.4 `SourceScanStatus.cs`

- 新增 closed `SourceScanWatcherStatus` 与 `SourceScanStatus.Watcher`（无路径/grant/session；`Disabled` 时 Watcher=null）。

## 2. AC-W 映射

| AC | 判定 | 关键证据 |
|---|---|---|
| AC-W1 生命周期与范围 | MET | `SourceWatcherTests.Start_ArmsFileAndFolderTargets_WithFrozenScopeRules` / `RepeatedRegistration_DoesNotGrowWatchers` / `RegistryRevokedOrMissing_IsUncovered_NotArmed` / `DeclaredFileTargetOnDirectory_IsUncovered_AndNeverGuessesFileName` / `StartTwice_StopTwice_IsIdempotent_AndStopProducesZeroHints`；gated `Fea11WatchHostRuntimeTests`（Ready→arm→Active=1→hint→Dispose disarm）；**r2 P2**：成功 refresh（含空枚举）后撤销 target 被拆除（`RevokedTargetAfterSuccessfulRefresh_IsDisarmed_AndStaleHandleCannotHint`）；generation drift 不 arm（`GenerationDrift_IsUncovered_NotArmed`） |
| AC-W2 hint 语义与去抖 | MET | `Debounce_MergesManyEventsIntoOneHint_AndOneFullRescan`（5 事件→1 hint→1 scan；窗口后第 2 次）、`HintIsNotAChangedVerdict_AndStatusIsRedacted`（`last_result=ok`、状态/日志无路径）、`EventForOtherFile_Name_IsIgnored_ForFileKindWatches`、`HintForUnknownSource_IsIgnored_AndNothingIsScanned`；真实文件树 `RealFileSystemWatcher_DetectsIsolatedFileChange`；**r2 P1**：rotation 游标非 0 后 hint 仍在同一 pass 被扫（`HintAfterPriorRotation_IsScannedInTheSamePass_AndPendingClears`） |
| AC-W3 overflow/根删除/降级 | MET | `Overflow_HintsAllTargets_Degrades_AndNeverCrashes`、`Overflow_RespectsBudget_AndCompletesAcrossTicks`（10 目标/预算 4→跨 tick，pending 清零）、`RootLost_IsDegraded_AndReArmsOrCountsUncovered`、`MaxWatchesCap_LeavesUncovered_AndSchedulerStillScansEverything`、`OptionsNormalization_ClampsBoundaries_AndFallsBackOnIllegalValues` |
| AC-W4 与 SCAN-1 协同 | MET | `SourceScanSchedulerTests.HintedTarget_IsScannedFirst_WithinTheSameBudget` / `HintDuringInFlightTick_IsMerged_AndReplayedAtMostOnce`（单飞、每 source ≤2 次、无并发）/ `HintedBackoffTarget_IsNotScannedEarly_ThenScannedAfterBackoff` / `HintedPausedScheduler_ScansNothing_AndResumeScans` / `HintTriggeredPass_UsesOnlyScanSourceSync_AndNeverMarksChanged` / **r2 P1** `HintAfterPriorRotation_IsScannedInTheSamePass_AndPendingClears`（start=0，预算仍 ≤4，pending 清空） |
| AC-W5 资源/隐私/门禁 | MET | `OptionsNormalization...` + `InternalBufferBytes_IsPassedToTheWatchFactory`；脱敏断言（**限定 WATCH-1 产生的 status 与 watcher/scheduler 日志行**；既有 host.log `host_session` 行不在本卡范围）；全量 .NET **1527/0/86**（基线 1521/0/86 不降）；pytest **3212 passed / 10 skipped**（实跑，summary 见 `logs/pytest-summary.txt`，零 Python 改动）；pins 18/18、API PASS、check PASS、scope diff 空 |

### 2.1 判别变异（AC 要求“删掉实现必须变红”，实跑后恢复）

| 变异 | 结果 | 日志 |
|---|---|---|
| M1 去掉去抖/合并（每事件立即 hint） | `Debounce_MergesManyEventsIntoOneHint_AndOneFullRescan` 红（期望 1 次扫描，实际 2） | `logs/mutation-m1-debounce.log` |
| M2 overflow 不触发全目标 due | `Overflow_HintsAllTargets_Degrades_AndNeverCrashes` 红（期望 2 次扫描，实际 0） | `logs/mutation-m2-overflow.log` |
| M3 去掉 hinted 优先排序 | `HintedTarget_IsScannedFirst_WithinTheSameBudget` 红（期望 s9 先扫，实际 s0） | `logs/mutation-m3-priority.log` |

恢复后重跑：`SourceScanScheduler` 57/0/0、`SourceWatcherTests` 15/0/0（`logs/watcher-unit.log`）。

## 3. 测试与证据（隔离根/注入时钟，零真实用户数据）

- `SourceWatcherTests`（新增 15 例）：fake watch factory + `ManualTimeProvider`（零 sleep）；1 例真实 `FileSystemWatcher` 隔离文件树 smoke（仅 temp 目录）。
- `SourceScanSchedulerTests`（新增 6 例）：hint 优先/单飞 replay/backoff/pause/命令集合/未知 source。
- gated `Fea11WatchHostRuntimeTests`（`[HostSidecarFact]`）：真实 HostRuntime + 真实 sidecar 包：Ready→watcher armed→注册隔离目标→`Active=1`→真实文件事件→`HintCount=1`→Dispose 后 watcher/scheduler 均 null；证据 `host-watch-runtime.json`。
- Host 测试总量：**179 passed / 0 failed / 55 skipped**（基线 158/54；+21 新测试、+1 gated skip）。

## 4. 门禁实跑

| Gate | 结果 | 证据 |
|---|---|---|
| `pytest tests -q -p no:cacheprovider` | **3212 passed / 10 skipped**，EXIT 0（与引用基线一致；本卡零 Python 改动，仍实跑记录；结束 summary 另存 `logs/pytest-summary.txt`） | `logs/pytest-full.log` |
| 全量 .NET RUN1/RUN2 | **1527 passed / 0 failed / 86 skipped / 1613**，EXIT 0（r1 基线 1521/0/86；r2 +6 passed=新增回归测试） | `logs/dotnet-full-1.log`、`logs/dotnet-full-2.log` |
| `check.ps1 -TaskPath doc/tasks/FEA-11-WATCH-1.md` | **PASS**（3 既有 warnings：非终态 Task 数 / STATUS 80% / REBASELINE_PLAN 80%） | `logs/check.log` |
| `verify_pins.ps1` | **18/18 PASS** | `logs/pins.log` |
| `generate_api_inventory.py --check` | **PASS**（C-07 未变） | `logs/api-inventory.log` |
| scope diff `919c9aa1e..HEAD -- doc/plan doc/contracts src/` | **空（0 行）** | `scope-validation.log` |

全量 .NET 每轮后已 `git checkout -- verification/FEA-09`，检查干净；本轮首跑即 0 failed（未出现需要隔离复跑的 flaky；SCAN-2 已知 flaky 本轮未触发）。

## 5. 证据 sha256

| file | sha256 |
|---|---|
| `host-watch-runtime.json` | `25baaac0fa55785a1d6062f6f7c28dcd20566ac0103a0bb45a330e99d323dfb6` |
| `logs/watcher-unit.log` | `b8115d599b34b39a70c95cb04748c65a9f7282b527727767d1c1bbce187f7a1c` |
| `logs/watcher-runtime.log` | `d6fe979a8bd84967865b02f96672f2d5405037bbd816fff4457cd1c6b3071699` |
| `logs/dotnet-full-1.log` | `c465cf513543bbe68037fb82be6416565d38047c0f7f84cae778b66c146cd4a0` |
| `logs/dotnet-full-2.log` | `55d157671b724fab4e5b11af1243255d95e48ba79e2d7f1292e57d65c6164faf` |
| `logs/pytest-full.log` | `db330f47621dea6279c67dd34c7fee3a15e72074d9aae5a17bf09d05e0fdca9e` |
| `logs/pytest-summary.txt` | `57d272daf80a9a56714bf383494800ed650af9fb09727a54372be35e1c8eb7de` |
| `logs/r2b-rootlost-isolated.log` | `3d17ea5007724239a2a41a3fba8b3c5c9599dd4ff31d117daede038d7d387049` |
| `logs/mutation-m1-debounce.log` | `5f4560d20c9fc43d2492fa578e63a650a4449d30b4dfc371a6d001e15fd62355` |
| `logs/mutation-m2-overflow.log` | `8d7336cd899a74fcdc43137d6bc34fd97b81ff65a1d73a7d081ff445e3837f52` |
| `logs/mutation-m3-priority.log` | `d045f86351fb7668bcb3dd272486a0ec4993b6687ab3fe7792a4e96245197324` |
| `logs/check.log` | `2afe8d249b29eadcd4a931fb9da6ca58bc0b66b5cd5faabeb02824c5f7a66fab` |
| `logs/pins.log` | `f198eda409309d359a700135e0ecb1d56c6b3df8f0bed0cfcef6f7427a7336db` |
| `logs/api-inventory.log` | `b4b9e68e1f7fce0dc4aeecfae9d887da0c0661b346a9434930ae62b3a2270c47` |
| `logs/gates.log` | `4bbb3da7f436a0fb2be7f10204fc1cbfdd3690a51642083762058d36b2a8ebb9` |

全部日志文件与 sha 见 `logs/gates.log`（同目录）；`changed-files.txt`、`scope-validation.log` 在 evidence 根。

## 6. 残余风险与 limitation（如实）

1. **漏事件/设备差异**：watcher 只是延迟优化；网络盘/某些卷类型/句柄失效可能漏事件或 error，正确性由 SCAN-1 周期扫描兜底（非正确性依赖）。
2. **根目录过宽**：只 arm 已注册 target 的根（file 精确文件/folder 递归），folder 内任意层事件均映射为“该 source due”，不做增量 diff——符合冻结语义，但大目录可能产生额外全量重枚举（IO 放大，受预算限制）。
3. **target 集只增不减**（SCAN-2 RH-3 不修）：已撤销/替换 target 由 arm 时 registry 复核与 refresh 拆除覆盖；内存 target 集本身仍只增不减。
4. **HostRuntime seam 无 fake Core/注入时钟**：gated 用例证明生产 wiring/真实 OS 事件；确定性去抖/overflow/预算断言在组件级。
5. **AC11-1 不回填**：本卡不做启动全量扫描；AC11-1 终态由 DSH 后续裁决。
6. **测试时序**：watcher 真实树测试依赖 OS 事件（gated/上限轮询 10–20s），理论上可能 flaky；本轮两次全量均 0 failed。
## 7. r2 返修（r1 Review CHANGES 处置）

r1 Review：`doc/reviews/FEA-11-WATCH-1-r1.md`（P0=0 / **P1=1** / P2=1 / P3=6）。r2 最小修复如下。

### 7.1 P1（阻断，AC-W2/W4）：hint pass 被非零预算游标跳过

- 根因：`TickCoreAsync` 虽把 hinted target 排到 `ordered` 最前，但仍 `start = _budgetCursor % targetCount`；rotation 先跑过 s0..s3 后 cursor=4，hint s9 的 pass 从 index 4 起 → 扫 s3..s6、s9 未扫，`HintPending=true` 直至下一周期（900s）。
- 修复：`var start = hasHints ? 0 : (_budgetCursor % targetCount);`（`hasHints` 在 `_gate` 内由 `hinted.Count > 0` 计算）。普通 tick 的 rotation 顺序/预算不变。
- 判别测试：`SourceScanSchedulerTests.HintAfterPriorRotation_IsScannedInTheSamePass_AndPendingClears`——先普通 tick（s0..s3，cursor=4），再 `HintSource("s9")` → 断言 hint pass 含 s9、本 pass ≤4、`HintPending=false`（修复前该用例红）。
- 预算/去重/优先语义：原有 57 例全绿（含 `HintedTarget_IsScannedFirst...`、`HintDuringInFlightTick...`）。

### 7.2 P2（AC-W1/L-W3）：撤销后成功 refresh（空枚举）不拆除 watcher

- 根因：`RefreshTargetsAsync` 仅 `added + updated > 0` 才 `NotifyTargetSetChanged()`；撤销 target 被枚举器跳过时 added=updated=0 → watcher 不复核，`Active` 仍=1。
- 修复：成功 refresh（`result.Ok`）**总是**通知 target-set 变化，watcher 重新 arm 复核（撤销/漂移 → 拆 watcher，`Active=0`、`Uncovered≥1`）。
- 判别测试：`SourceWatcherTests.RevokedTargetAfterSuccessfulRefresh_IsDisarmed_AndStaleHandleCannotHint`——arm 后 revoke，成功空 refresh → Active=0；随后旧 handle 的迟到事件被 slot 有效性检查拦截（零 hint/零 scan）。
- 附带加固：`OnFileEvent` 在 `_gate` 内校验 slot 仍是当前 armed slot；`OnDebounceElapsed` 在 `_gate` 内、`_started` 为真时发出 hint（`HintAllIfStarted` 同理），修复 P3-1 的 Stop 后窄竞态。

### 7.3 P3 同批处置

| P3 | 处置 | 证据/说明 |
|---|---|---|
| P3-1 Stop/Dispose 后零 hint 窄竞态 | **已修**：hint/HintAll 在 watcher `_gate` 内且 `_started` 为真时发出；Stop 持有同一 gate → Stop 返回后不可能再有在飞 timer callback 发出 hint；`OnFileEvent` 增加 slot 有效性校验 | `Stop_WithPendingDebounceTimer_ProducesNoHints`（Stop 时有 pending debounce → 推进时钟后 0 hint/0 scan） |
| P3-2 canonical pytest 日志缺 summary | **已修**：重跑全量 pytest 并保留完整日志；summary 另存 `logs/pytest-summary.txt`（`3212 passed, 10 skipped`） | `logs/pytest-full.log`、`logs/pytest-summary.txt` |
| P3-3 RootLost 恒真断言 / 缺测试 | **r2b 才落地**（r2 commit message 曾误称已修，实际该行仍是恒真断言）：RootLost 断言改为 `Assert.Equal(0, status.Active); Assert.True(status.Uncovered >= 1);`，并在末行 Tick 前 `await HintIdleAsync()` 排空 root-lost hint pass（见 §7.5）；generation-drift、buffer 注入、hint-after-rotation、revoke-after-refresh 用例已在 r2 落地；overflow 用例补 `HintPending=false` | `SourceWatcherTests`、`SourceScanSchedulerTests`；`logs/r2b-rootlost-isolated.log` |
| P3-4 redaction 口径过宽 | **已收窄**：卡面/记录改述为「WATCH-1 产生的 status 与 watcher/scheduler 日志行」；测试只断言 `source watch*` / `source scan*` 行；gated `host.log` 既有 `host_session` 行不属于本卡 | `HintIsNotAChangedVerdict_AndStatusIsRedacted` |
| P3-5 Sync Intersect+Union | **已简化**：改为 `Clear()+UnionWith(desired)`（desired 为权威集合，移除不再需要的 source id） | `SourceWatcher.Sync` |
| P3-6 DisposeAsync 不 join 在飞 hint task | **已修**：dispose 前 `await _hintTask.WaitAsync(2s)`（超时/取消吞掉，不崩）；新增用例验证不抛不挂 | `DisposeAsync_WithInFlightHintPass_CompletesWithoutThrowing` |

### 7.4 r2 门禁（HEAD 含本返修）

| Gate | 结果 | 证据 |
|---|---|---|
| Host 单测全量 | **185 / 0 / 55**（r1 179/55；+6 回归） | `logs/watcher-unit.log` |
| gated HostRuntime watcher | **1 / 0 / 0** | `logs/watcher-runtime.log` |
| 全量 .NET RUN1/RUN2 | **1527 / 0 / 86** 两轮（r1 基线 1521/0/86 不降） | `logs/dotnet-full-1.log`、`logs/dotnet-full-2.log` |
| 全量 pytest | **3212 passed / 10 skipped**（实跑；summary 已存） | `logs/pytest-full.log`、`logs/pytest-summary.txt` |
| check / pins / API / scope | PASS（3 既有 warnings）/ 18/18 / PASS / 0 行 | `logs/check.log`、`logs/pins.log`、`logs/api-inventory.log`、`scope-validation.log` |

每轮全量后均 `git checkout -- verification/FEA-09`；两轮 0 failed（未触发 flaky）。

### 7.5 r2b 返修（r2 窄面复审 P2：测试真实性）

r2 窄面复审报告：`doc/reviews/FEA-11-WATCH-1-r2.md`（P0=0/P1=0/P2×2；产品代码 P1/P2 已被独立探针证实真修）。r2b 仅改测试与证据：

- **P2-1**：`SourceWatcherTests.RootLost_IsDegraded_AndReArmsOrCountsUncovered` 原断言 `Uncovered>=1 || Active>=0` 恒真（r2 commit message/record/卡面/Handoff 四处曾误称已改）。r2b 改为严格断言：`Assert.Equal(0, status.Active); Assert.True(status.Uncovered >= 1);`——根删除后 watcher 拆除且计入 uncovered，re-arm 不可能（目录已不存在）。
- **P2-2**：同一用例隔离运行稳定红（5/5），根因是根删除后 `HintAllIfStarted` 的 hint pass 占住单飞 gate，末行 `Assert.True(await TickAsync())` 合法返回 false（产品语义正确）。r2b 在末行前加 `await fixture.Scheduler.HintIdleAsync();`（与 overflow 用例一致），再断言周期 Tick 仍可运行。
- **P3**：P3-3 严格断言随 P2-1 落地；record/卡面/Handoff 的“已修”表述已与实际字节对齐（r2 commit message 中的误述无法改写，故在此显式更正）；P3-1/P3-6 登记为 smoke（Stop 窄竞态与 DisposeAsync join 已有用例，但非确定性 race 复现）。
- **r2b 验证**：①该用例隔离重跑 **5/5 全绿**（`logs/r2b-rootlost-isolated.log`）；②Host 全量 **185/0/55**；③全量 .NET RUN1/RUN2 **1527/0/86** 各（两轮 0 failed；每轮后恢复 `verification/FEA-09`）；④check PASS（3 既有 warnings）、pins 18/18、API PASS、scope diff 0。