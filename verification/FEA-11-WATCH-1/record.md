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
| AC-W1 生命周期与范围 | MET | `SourceWatcherTests.Start_ArmsFileAndFolderTargets_WithFrozenScopeRules` / `RepeatedRegistration_DoesNotGrowWatchers` / `RegistryRevokedOrMissing_IsUncovered_NotArmed` / `DeclaredFileTargetOnDirectory_IsUncovered_AndNeverGuessesFileName` / `StartTwice_StopTwice_IsIdempotent_AndStopProducesZeroHints`；gated `Fea11WatchHostRuntimeTests`（Ready→arm→Active=1→hint→Dispose disarm） |
| AC-W2 hint 语义与去抖 | MET | `Debounce_MergesManyEventsIntoOneHint_AndOneFullRescan`（5 事件→1 hint→1 scan；窗口后第 2 次）、`HintIsNotAChangedVerdict_AndStatusIsRedacted`（`last_result=ok`、状态/日志无路径）、`EventForOtherFile_Name_IsIgnored_ForFileKindWatches`、`HintForUnknownSource_IsIgnored_AndNothingIsScanned`；真实文件树 `RealFileSystemWatcher_DetectsIsolatedFileChange` |
| AC-W3 overflow/根删除/降级 | MET | `Overflow_HintsAllTargets_Degrades_AndNeverCrashes`、`Overflow_RespectsBudget_AndCompletesAcrossTicks`（10 目标/预算 4→跨 tick，pending 清零）、`RootLost_IsDegraded_AndReArmsOrCountsUncovered`、`MaxWatchesCap_LeavesUncovered_AndSchedulerStillScansEverything`、`OptionsNormalization_ClampsBoundaries_AndFallsBackOnIllegalValues` |
| AC-W4 与 SCAN-1 协同 | MET | `SourceScanSchedulerTests.HintedTarget_IsScannedFirst_WithinTheSameBudget` / `HintDuringInFlightTick_IsMerged_AndReplayedAtMostOnce`（单飞、每 source ≤2 次、无并发）/ `HintedBackoffTarget_IsNotScannedEarly_ThenScannedAfterBackoff` / `HintedPausedScheduler_ScansNothing_AndResumeScans` / `HintTriggeredPass_UsesOnlyScanSourceSync_AndNeverMarksChanged` |
| AC-W5 资源/隐私/门禁 | MET | `OptionsNormalization...`；状态/日志脱敏断言；全量 .NET 1521/0/86（基线 1500/0/85 不降）；pytest 3212/10（与引用基线一致，零 Python 改动）；pins 18/18、API PASS、check PASS、scope diff 空 |

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
| `pytest tests -q -p no:cacheprovider` | **3212 passed / 10 skipped**，EXIT 0（与引用基线一致；本卡零 Python 改动，仍实跑记录） | `logs/pytest-full.log` |
| 全量 .NET RUN1/RUN2 | **1521 passed / 0 failed / 86 skipped / 1607**，EXIT 0（基线 1500/0/85；+21 passed=新增测试，+1 skip=gated runtime） | `logs/dotnet-full-1.log`、`logs/dotnet-full-2.log` |
| `check.ps1 -TaskPath doc/tasks/FEA-11-WATCH-1.md` | **PASS**（3 既有 warnings：非终态 Task 数 / STATUS 80% / REBASELINE_PLAN 80%） | `logs/check.log` |
| `verify_pins.ps1` | **18/18 PASS** | `logs/pins.log` |
| `generate_api_inventory.py --check` | **PASS**（C-07 未变） | `logs/api-inventory.log` |
| scope diff `919c9aa1e..HEAD -- doc/plan doc/contracts src/` | **空（0 行）** | `scope-validation.log` |

全量 .NET 每轮后已 `git checkout -- verification/FEA-09`，检查干净；本轮首跑即 0 failed（未出现需要隔离复跑的 flaky；SCAN-2 已知 flaky 本轮未触发）。

## 5. 证据 sha256

| file | sha256 |
|---|---|
| `host-watch-runtime.json` | `25baaac0fa55785a1d6062f6f7c28dcd20566ac0103a0bb45a330e99d323dfb6` |
| `logs/watcher-unit.log` | `ed4145da78fa92b3e548812c235c628ac2ac410e4f042301d3ea88a01d82fd47` |
| `logs/watcher-runtime.log` | `d6fe979a8bd84967865b02f96672f2d5405037bbd816fff4457cd1c6b3071699` |
| `logs/dotnet-full-1.log` | `915f78a28237abae830c913aa1d9c841a96083af7aa7d14dd2326a9becf8e6fb` |
| `logs/dotnet-full-2.log` | `7a53f0b9d45ae685dd25cf751ff61a7f6b24f34e3a1a3a979e3910a1321516eb` |
| `logs/pytest-full.log` | `da630cafd6368946e3e9ddb8b8f4b5dbe6620b8bcaa299e5bb16d3d76e029125` |
| `logs/mutation-m1-debounce.log` | `5f4560d20c9fc43d2492fa578e63a650a4449d30b4dfc371a6d001e15fd62355` |
| `logs/mutation-m2-overflow.log` | `8d7336cd899a74fcdc43137d6bc34fd97b81ff65a1d73a7d081ff445e3837f52` |
| `logs/mutation-m3-priority.log` | `d045f86351fb7668bcb3dd272486a0ec4993b6687ab3fe7792a4e96245197324` |
| `logs/check.log` | `495afa593898d7c6175829fe709bc17d284d1f62dcc69d4b5cdc82e3659779e7` |
| `logs/pins.log` | `f198eda409309d359a700135e0ecb1d56c6b3df8f0bed0cfcef6f7427a7336db` |
| `logs/api-inventory.log` | `b4b9e68e1f7fce0dc4aeecfae9d887da0c0661b346a9434930ae62b3a2270c47` |

全部日志文件与 sha 见 `logs/gates.log`（同目录）；`changed-files.txt`、`scope-validation.log` 在 evidence 根。

## 6. 残余风险与 limitation（如实）

1. **漏事件/设备差异**：watcher 只是延迟优化；网络盘/某些卷类型/句柄失效可能漏事件或 error，正确性由 SCAN-1 周期扫描兜底（非正确性依赖）。
2. **根目录过宽**：只 arm 已注册 target 的根（file 精确文件/folder 递归），folder 内任意层事件均映射为“该 source due”，不做增量 diff——符合冻结语义，但大目录可能产生额外全量重枚举（IO 放大，受预算限制）。
3. **target 集只增不减**（SCAN-2 RH-3 不修）：已撤销/替换 target 由 arm 时 registry 复核与 refresh 拆除覆盖；内存 target 集本身仍只增不减。
4. **HostRuntime seam 无 fake Core/注入时钟**：gated 用例证明生产 wiring/真实 OS 事件；确定性去抖/overflow/预算断言在组件级。
5. **AC11-1 不回填**：本卡不做启动全量扫描；AC11-1 终态由 DSH 后续裁决。
6. **测试时序**：watcher 真实树测试依赖 OS 事件（gated/上限轮询 10–20s），理论上可能 flaky；本轮两次全量均 0 failed。
