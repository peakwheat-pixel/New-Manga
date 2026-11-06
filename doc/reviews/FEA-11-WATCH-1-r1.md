---
task: FEA-11-WATCH-1
title: FEA-11-WATCH-1 独立 Review r1（fresh subagent；Host-only watcher hint → 全量重枚举）
reviewer: fresh subagent（独立上下文；未参与 FEA-11/WATCH-1 任何实现或返修）
session: 48af6d93-b456-4c17-9478-a694fb7bbb10
parent_session: session-8db9dae5-49df-4d09-ac62-696f0805a95c
date: 2026-11-06
timezone: Asia/Shanghai
repo: G:\CODEX\New Manga
branch: main
worktree: clean（review 结束时）
base: 919c9aa1e
implementation_commit: e60105cf9
docs_backfill_commit: cf0ef2206
reviewed_head: 83142efab39666dc4783e045ab029582c4e0f407
decision: CHANGES
---

# FEA-11-WATCH-1 独立 Review r1

> **结论先行：`CHANGES`。**
>
> 实现主体、门禁、脱敏、单飞/退避/pause/命令集合、overflow/根删除/上限、gated HostRuntime 接线大多是可靠的；
> 但两个**可复现的 AC 语义缺口**不能按 `MET` 收口：
>
> 1. **P1（阻断）**：当 scheduler 的 budget 游标非 0 时，hint 触发的 tick 可能**不扫描被 hint 的 source**；
>    hint 仍在 due 集合中（`HintPending=true`），但不会再排下一次 tick，只能等下一个 900s 周期（或下一次别的 hint）。
>    这违反 AC-W2「hint → 该 source 的全量 `ScanSourceSync`，不等待完整周期」与 AC-W4「hinted 优先」。
> 2. **P2（需处置）**：target 已 arm 后被撤销时，如果一次成功的 refresh 没有 add/update 任何 target，
>    `RefreshTargetsAsync` 不触发 `TargetSetChanged`，watcher 不会重新复核 registry → 已撤销 target 的 watcher 保持 armed，
>    与 `doc/reviews/FEA-11-WATCH-1-scope-r1.md` AC-W1 判别测试 #2「refresh 后已 arm 的撤销项被拆」及 L-W3「窗口有界」不符。
>
> 其余为 P3 级证据/测试质量/残余竞态观察，不单独构成阻断。修复后需要重跑门禁并重新 Review；当前不得 closeout。
>
> 本 review 未修改仓库、未 commit、未 push；所有复核产物写在 `G:\CODEX\New Manga.workspace\FEA-11\review-watch-1\`。

---

## 1. 只读核验基线

| 项 | 事实 | 证据 |
|---|---|---|
| HEAD / 被审 head | `83142efab39666dc4783e045ab029582c4e0f407`（`docs(fea-11-watch-1): 卡面 in_review 集成…`） | `git rev-parse HEAD` |
| 实现交付 | `e60105cf9`（feat）→ `cf0ef2206`（docs 回填）→ `4fa2151cd`/`83142efab`（Lead 指针/卡面集成） | `git log --oneline -8` |
| 代码与交付一致 | `git diff --stat e60105cf9..HEAD -- apps/desktop-avalonia/src apps/desktop-avalonia/tests` = 空 | 实跑 |
| 工作树 | clean（本 review 全部门禁跑完后 `git status --porcelain` 为空） | 实跑 |
| 未 push | `git branch -r --contains e60105cf9` / `83142efab` 均为空；`origin/main` 在 `b1c1f5a56`（本地 main 领先，符合项目集成流程） | 实跑 |
| 契约/schema | `git diff --name-only 919c9aa1e..HEAD -- doc/plan doc/contracts src/` = 0 行；`verify_pins.ps1` = 18/18 PASS | 实跑 |
| 依赖 | `git diff --stat 919c9aa1e..HEAD -- '*.csproj' '*.props' '*.targets' '*.json' …` 仅命中 verification 的 `host-watch-runtime.json`；无 csproj/props/lock 变化 | 实跑 |
| App 改动 | `git diff --stat 919c9aa1e..HEAD -- .../NewManga.App .../NewManga.App.Tests` 为空 | 实跑 |
| AC11-1 | `doc/tasks/FEA-11.md:103` 仍 `- [ ]`，状态表仍 `PARTIAL`；本卡未回填 | 只读 |
| 卡状态 | `status: in_review`；`delivery_head: e60105cf9`；`integration_commit: null`；canonical/resource closeout 均 `pending` | 只读 |

---

## 2. AC-W1…AC-W5 判定（独立复核，不以卡面为准）

| AC | 判定 | 独立依据 |
|---|---|---|
| **AC-W1 生命周期/范围** | **PARTIAL** | arm-time 范围规则、registry 复核（撤销/缺失/不可读）、typed uncovered、Start/Stop 幂等、Stop 后事件零 hint、gated Ready→armed 均通过；但 **scope review AC-W1 判别测试 #2 的「refresh 后已 arm 的撤销项被拆」未实现**（见 §5 P2）。卡面 AC-W1 的 arm-time 子项可判 MET，冻结 scope 的该子项不能。 |
| **AC-W2 hint 语义/去抖** | **FAIL** | N→1 去抖、注入时钟零 sleep、hint 不写 changed/deleted、`last_result=ok`、脱敏、未知 source 忽略均通过；但 **hint 触发的 pass 不能保证扫描被 hint 的 source**：10 targets / budget 4、先跑一个 tick（游标=4）后 hint `s9`，hint pass 实际扫描 `s3,s4,s5,s6`，`s9` 未扫描，`HintPending=true`；下一 tick 要等 900s（见 §4 P1）。这与 scope review AC-W2「hint 只触发一次 full `ScanSourceSync`（该 source 的全量重枚举）」不符。 |
| **AC-W3 overflow/根删除/上限** | **MET（有测试质量 P3）** | overflow / Error / 根删除均不崩；overflow 全 target due，受 budget 跨 tick（10 targets/budget 4 实测）；`OverflowCount/Degraded/Uncovered` 计数；re-arm 或 uncovered；MaxWatches=1 的 cap 用例、Options 边界/夹紧用例通过。P3：`RootLost_IsDegraded_AndReArmsOrCountsUncovered` 的 `Assert.True(status.Uncovered >= 1 || status.Active >= 0)` 第二项恒真，不足以判别「re-arm vs uncovered」；没有断言 `InternalBufferBytes` 实际传到 FSP handle；没有 watcher 级 generation-drift 用例。 |
| **AC-W4 与 SCAN-1 协同** | **FAIL** | 单飞合并、在飞 hint replay≤1、backoff 不提前、pause 0 次、命令集合精确 `{ScanSourceSync}`、无 plan/apply/journal、零 Core 业务写均通过；**hinted 优先不成立**：`TickCoreAsync` 先按 hinted 重排，但仍用 `start = _budgetCursor % targetCount` 起点；游标非 0 时 hinted 项先被跳过（见 §4 P1）。M3 变异只覆盖了「游标=0」的新 scheduler，未覆盖该场景。 |
| **AC-W5 资源/隐私/门禁** | **MET（有证据 P3）** | 本 review 独立实跑：Host 单测 179/0/55；gated 1/0/0；全量 .NET 复跑 1521/0/86（首跑触发已知 App flaky，复跑绿；两轮后均恢复 `verification/FEA-09`）；全量 pytest 3212 passed/10 skipped；pins 18/18；check PASS（3 既有 warnings）；API inventory EXIT 0；scope diff 0；无新依赖；watcher status/日志无路径/secret/grant（watcher 行只有 source_id/计数/typed code）。P3：canonical `logs/pytest-full.log` 本身没有结束 summary（见 §5 P3-2），以及 gated `host.log` 里有既有的 `host_session` 行（不是 WATCH-1 新增行），卡面「日志无 session」表述过宽。 |

**净判定**：AC-W1/W2/W4 不能按卡面 `MET` 定稿；AC-W3/W5 可判 MET（证据/测试质量另记）。因此 `CHANGES`。

---

## 3. 独立复跑（非引用 Owner 日志）

全部命令在 `G:\CODEX\New Manga` 实跑；Host 项目用 Release 现有构建（源码 mtime 16:32:51 < DLL 16:32:53，构建与 HEAD 代码一致；且 §4 的独立复制构建复核了同一行为）。

| 复核项 | 命令 | 结果 |
|---|---|---|
| Watcher 过滤用例 | `dotnet test ...NewManga.Host.Tests.csproj -c Release --no-build --no-restore --filter "FullyQualifiedName~Watcher"` | 16 total / **15 passed / 0 failed / 1 skipped**（skipped = gated `Fea11WatchHostRuntimeTests`，无 sidecar env） |
| SourceWatcherTests 全类 | 同上过滤类 | 15/0/0（与卡面 15 例一致） |
| SourceScanSchedulerTests 全类 | `--filter "FullyQualifiedName~SourceScanSchedulerTests"` | **57 / 0 / 0** |
| Host 全量 | `dotnet test ...NewManga.Host.Tests.csproj -c Release --no-build --no-restore` | **234 total / 179 passed / 0 failed / 55 skipped**（与卡面 179/0/55 一致） |
| gated HostRuntime watcher（真实 sidecar） | `NEWMANGA_CORECLIENT_SIDECAR_DIR=...\build\sidecar\core-sidecar\core-sidecar`，`NEWMANGA_EVIDENCE_DIR=<workspace>\gated-evidence` | **1 / 0 / 0**；独立重写的 `host-watch-runtime.json` 与 EV-02 字段一致：ready=true、watcher_attached=true、armed=true、active_watches=1、hint_count=1、overflow_count=0、redacted=true |
| 全量 .NET RUN1 | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build --no-restore` | **1520 passed / 1 failed / 86 skipped**；失败：`NewManga.App.Tests.FluentResidual2VisualEvidenceTests.Captures_Residual2_Visual_Inventory_Only_When_Opted_In`（expected `""`，actual `M verification/FEA-09/logs/wire-redacted.ndjson`）。根因是既有的跨项目测试隔离问题：`NewManga.CoreClient.Tests/WireLogSourceRedactionTests.PersistedNdjsonContainsOnlyRewrittenBytes` 写 tracked `verification/FEA-09/logs/wire-redacted.ndjson`，与 App 用例的「git status 前后一致」断言竞争。**不是 WATCH-1 引入**；但不能复现卡面「RUN1/RUN2 均 0 failed」。 |
| 全量 .NET RUN2（首跑 flaky 后复跑） | 同上 | **1521 passed / 0 failed / 86 skipped**（与卡面基线一致）；跑后 `git checkout -- verification/FEA-09`，工作树 clean |
| 全量 pytest | `C:/Python314/python.exe -m pytest tests -q -p no:cacheprovider --tb=no` | **3212 passed / 10 skipped / 10 warnings in 233.29s**（与卡面/引用基线一致；本卡零 Python 改动） |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PIN AUDIT: PASS (all 18)** |
| check | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-WATCH-1.md` | **PASS**（3 既有 warnings） |
| API inventory | `C:/Python314/python.exe tools/generate_api_inventory.py --check` | **EXIT 0 / PASS** |
| 范围 diff | `git diff --name-only 919c9aa1e..HEAD -- doc/plan doc/contracts src/` | **0 行** |

### 3.1 Evidence 哈希核对

对 `verification/FEA-11-WATCH-1/**` 全 17 个文件计算 SHA256，与卡面 `EV-01…EV-17` 逐项一致（包括 `host-watch-runtime.json`、`record.md`、`changed-files.txt`、`scope-validation.log`、`logs/watcher-*.log`、`logs/dotnet-full-1/2.log`、`logs/mutation-m*.log`、`logs/pytest-full.log`、`logs/pins.log`、`logs/check*.log`、`logs/api-inventory.log`、`logs/gates.log`）。证据文件的字节未被篡改。

---

## 4. 独立判别变异（至少 2 项，实做 3 项）

为不修改仓库，复制 `apps/desktop-avalonia/src/NewManga.Host`、`src/NewManga.CoreClient`、`Directory.Build.props` 和两个测试文件到仓外
`G:\CODEX\New Manga.workspace\FEA-11\review-watch-1\mut\`，用独立 `Mut.Tests.csproj` 编译/运行；未触碰仓库源码。

| 变异 | 我做的改动 | 结果 | 与 Owner 日志对照 |
|---|---|---|---|
| **M1 去抖/合并移除** | `SourceWatcher.QueueHint` 改为每事件立即 `_scheduler.HintSource(sourceId)`，删除 `_debounce` 合并路径 | `Debounce_MergesManyEventsIntoOneHint_AndOneFullRescan` **红**：Expected 1 / Actual 2 | Owner `mutation-m1-debounce.log` 同样 Expected 1 / Actual 2；可复现 |
| **M2 overflow 全 due 移除** | 删除 `OnWatchError` 中的 `_scheduler.HintAllTargets(CodeOverflow);` | `Overflow_HintsAllTargets_Degrades_AndNeverCrashes` **红**：Expected 2 / Actual 0 | Owner `mutation-m2-overflow.log` 同样 Expected 2 / Actual 0；可复现 |
| **M3 hinted 优先移除** | `TickCoreAsync` 中 `var hinted = _targets.Keys.Where(_ => false)` | `HintedTarget_IsScannedFirst_WithinTheSameBudget` **红**：Expected `"s9"` / Actual `"s0"` | Owner `mutation-m3-priority.log` 同样 s9 vs s0；可复现 |

**方法学注记**：复制目录恢复源码后若直接 `dotnet test --no-build`，MSBuild 可能因恢复文件 timestamp 早于变异构建的 DLL 而继续使用旧（变异）二进制；我在最终探针前使用 `dotnet build --no-incremental` 强制重建，避免该假象。这不影响上表结论（每个变异都在改动后重新编译）。

**结论**：M1/M2/M3 的变异判别性成立；Owner 日志内容与独立复做一致。但 M3 只覆盖「新 scheduler、游标=0」的场景，**没有覆盖 §4.1 的游标非 0 场景**，因此卡面的「hinted 优先」证据不充分。

### 4.1 P1：hint pass 跳过被 hint 的 source（阻断）

**独立探针**（仓外 copy；`SourceScanScheduler` 原样）：
- 10 targets `s0…s9`，`MaxTargetsPerTick=4`；
- 第一次 `TickAsync` → `s0,s1,s2,s3`（游标=4）；
- `HintSource("s9")` → `HintIdleAsync()`。

**实际输出**：
```text
tick1=s0,s1,s2,s3
hintPass=s3,s4,s5,s6 pending=True
s9Scanned=False
```

**机制**：`apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs`

- 第 780-788 行把 hinted 项排到 `ordered` 最前；
- 第 801 行仍是 `var start = _budgetCursor % targetCount;`；
- budget 循环从 `start` 开始，所以游标非 0 时先扫 rotation 中的旧位置，hinted 项被跳过；
- 第 830 行「只有实际 scan 才移除 due bit」使 `s9` 保持 `_hintedSources`，但 **`_hintTask` 已完成、没有后续 tick**；
- 下一次机会是 900s 周期 tick（`IntervalSeconds` 默认 900）或另一个 hint。对用户而言，hint 的延迟收益在这类 source 上失效，等价于「等待完整周期」。
- 这也解释了为什么 `HintPending=true` 却没有任何 pending 执行：`HintPending` 只是状态，不是调度。

**AC 影响**：
- AC-W2：hint 没有导致「该 source 的 full `ScanSourceSync`」；
- AC-W4：hinted 项在 hint pass 中没有优先被扫；
- 与 scope review AC-W4 判别测试 #2「10 targets/budget=4，hint 第 10 个 → 第一个 tick 扫描它」在游标非 0 时直接冲突。

**我验证过的最小修复**（仅仓外 copy，未落仓库）：
```csharp
var start = _hintedSources.Count > 0 ? 0 : _budgetCursor % targetCount;
```
强制重建后同一探针输出：
```text
tick1=s0,s1,s2,s3
hintPass=s9,s0,s1,s2 pending=False
```
说明修复方向有效。更精细的实现可以先扫 hinted（至多 budget），再从原游标继续剩余 budget，避免重扫；但无论哪种，**必须把该场景做成仓库内测试**（例如 `HintAfterPriorRotation...`），并重新跑 §3 门禁。

### 4.2 P2：arm 后撤销 + 无新增 refresh 不拆除 watcher

**独立探针**（仓外 copy）：
1. 临时隔离根注册 exact file root，注册 enumerated target；
2. watcher.Start → `Active=1`；
3. `Registry.Revoke(registryId)`；
4. `await scheduler.RefreshTargetsAsync()`，enumerator 返回成功的空集合（真实 SCAN-2 在撤销后会跳过该 source，同样可能 added=updated=0）；
5. 读取 `watcher.Status().Active`。

**实际输出**：
```text
refresh=True active=1
```
即已撤销 target 的 watcher 仍 armed。

**机制**：`SourceScanScheduler.RefreshTargetsAsync` 第 619-622 行仅在 `added + updated > 0` 时 `NotifyTargetSetChanged()`；`SourceWatcher` 只在 `TargetSetChanged`/overflow/root lost/Start 时 `Sync()` 复核 registry。撤销不会新增/更新 target，因此不会触发 Sync；下一次 refresh 也不会触发，窗口并不是 scope L-W3 所说的「refresh/同步」有界。

**AC 影响**：
- 冻结 scope AC-W1 判别测试 #2「refresh 后已 arm 的撤销项被拆」未满足；
- 卡面 `Owner 交付记录` / `record.md:1.1` 的「target 消失/撤销/替换 → 拆 watcher」与现状不符；
- 安全影响有限（watcher 不读内容；scan 执行器在扫描时会再次 typed skip），但资源/状态与 limitation 文本不诚实，不能按 MET 收口。

**我验证过的最小修复**（仓外 copy）：将 `if (added + updated > 0)` 改为 `if (result.Ok)`（成功 refresh 总是通知 watcher 复核），同一探针：
```text
refresh=True active=0
```
如果 Lead 选择不改行为，则必须把 AC-W1/limitation 明确降级为「arm-time 复核；撤销后直到下一次 target-set 变化才拆除」，并修改卡面/记录中「refresh 拆除」的表述，不能当前文本 + MET。

---

## 5. 其余发现（P3；不单独阻断，但应在 closeout 前处置或如实登记）

### P3-1 Stop/Dispose 后零 hint 存在窄竞态（未能确定性复现，代码路径实核）

`SourceWatcher.OnDebounceElapsed`（`SourceWatcher.cs:801-818`）在 `lock` 内检查 `_started`、移除 debounce 并递增 count，然后**在锁外**调用 `_scheduler.HintSource(sourceId)`；`Stop()`（`:237-266`）可以在两者之间把 `_started=false` 并返回。类似地，`OnWatchError`（`:676-705`）在 `check started` 之后、`HintAllTargets` 之前也可能被 Stop 插入。结果是 `Stop()` 返回后仍可能有一次 hint 进入 scheduler。现有 `StartTwice_StopTwice...` 只覆盖「Stop 后再 raise 事件」的时序，不覆盖 timer callback 在飞。建议至少在调用 scheduler 前再做一次 `_started` 检查，或由 scheduler 端接受 watcher 的 stopped 状态；至少记为残余竞态，不要声称绝对零 hint。

### P3-2 canonical pytest 证据日志不完整

`verification/FEA-11-WATCH-1/logs/pytest-full.log`（EV-13，sha `da630caf…`）只有 140 行：进度到 `[ 84%]`，随后全是 QML stderr，**没有 `3212 passed, 10 skipped` 的结束 summary**。`gates.log` 写了 3212/10，我的独立全量 pytest 也确实是 **3212 passed / 10 skipped / 10 warnings in 233.29s**，但 canonical 文件本身不能证明完成。closeout 前应重跑并保存带 summary 的完整日志，更新 EV-13 及哈希（或补一份明确标注的 runner log）；不要把该文件继续作为「已完成」的唯一证据。

### P3-3 测试质量缺口（会漏掉 P1/P2）

- `RootLost_IsDegraded_AndReArmsOrCountsUncovered`：`Assert.True(status.Uncovered >= 1 || status.Active >= 0)` 第二项恒真；建议断言具体 `Uncovered` 增量或 `Failed factory.Create` 计数。
- 无 watcher 级 generation-drift 用例（代码有检查，但未像 revoked/missing 那样被 discriminator 覆盖）。
- 无断言 `SourceWatchOptions.InternalBufferBytes` 实际到达 `ISourceWatchHandle`（`FakeWatchHandle` 已保存 `InternalBufferSize`，但未 assert）；AC-W5 的「buffer 64 KiB 可注入并验证」目前是 options 边界测试而非注入验证。
- 无「先跑一个 budget tick 再 hint」的用例（P1）；无「arm 后 revoke + refresh（空枚举）」用例（P2）。
- `Overflow_RespectsBudget...` 未断言最终 `HintPending=false`（只断言 10 个 source 都扫过）；建议补。

### P3-4 卡面/记录的 redaction 口径过宽

AC-W5 / Owner 记录写「状态/日志无 session」。watcher/scheduler 新增行确实只有 source_id/计数/typed code；但 gated `host.log` 含既有 `host-control session opened (host_…)` 行，`credentials/grants` 目录也存在。这不是 WATCH-1 新增泄漏，但验收表述应限定为「WATCH-1 新增的 watcher/scheduler 行与 `SourceScanWatcherStatus` 无路径/secret/grant/session」，否则表述与证据不一致。

### P3-5 `Sync()` 中 `IntersectWith` + `UnionWith` 等价于只 Union

`SourceWatcher.cs:371-372`：
```csharp
pair.Value.SourceIds.IntersectWith(plan.SourceIds);
pair.Value.SourceIds.UnionWith(plan.SourceIds);
```
交集后再并上同一集合 = 并集；被移除 source 的旧 id 会留在 slot 的 `SourceIds` 中。`HintSource` 会对已不存在 target 返回 false，故无功能破坏，但这段不是「删除不再需要的 source」的实现，建议改为 `IntersectWith`（或直接赋值）。

### P3-6 `DisposeAsync` 未等待在飞 hint task

`SourceScanScheduler.DisposeAsync` 设置 `_disposed`、停 loop、`await loop` 后直接 `_tickGate.Dispose()`；若 `_hintTask` 正在 `TickAsync` 内，Release 可能抛 `ObjectDisposedException`（`HintedTickAsync` 捕获，不崩，但语义上未 join）。建议 dispose 前 await/observe `_hintTask`，或明确记录为 limit。

---

## 6. 范围/纪律核验

| 项 | 结论 |
|---|---|
| Owner 两 commit 是否只在 allowed_paths | **是**。`e60105cf9` 只改 Host src/tests + 卡/Handoff/verification；`cf0ef2206` 只改卡/Handoff/`check-post-commit.log`；无 App/UI/Core/契约/schema/依赖/STATUS/PLAN/LEDGER/reviews。 |
| Lead 集成 commit | `4fa2151cd`/`83142efab` 改 STATUS/REBASELINE_PLAN/TASK_LEDGER/卡面，属 Lead/DSH 职责，不按 Owner allowed_paths 计；代码未变。 |
| 无 App 改动 | `git diff --stat 919c9aa1e..HEAD -- .../NewManga.App .../NewManga.App.Tests` 为空；Handler/Tests 全在 Host 侧。 |
| 无新依赖 | 无 csproj/props/lock 变化；仅 BCL `System.IO.FileSystemWatcher`。 |
| 契约/schema/pins | `doc/plan`/`doc/contracts`/`src/` diff 0；pins 18/18；C-01b/C-17 字节未改（`verify_pins.ps1` + scope diff）。 |
| 未 push / 工作树 clean | 远程分支不含 `e60105cf9`/`83142efab`；review 结束时 `git status` clean；跑全量后已 `git checkout -- verification/FEA-09`。 |
| AC11-1 不回填 | `doc/tasks/FEA-11.md:103` 仍 `[ ]`，状态表 `PARTIAL`；本卡卡面与 record 均声明不自动回填。 |
| L10 | 未解决；没有新增 RENDITION 实现/任务（只读检索 STATUS/PLAN/FEA-11 无 RENDITION）。 |
| RH-3 | 未修；target 集仍只增不减，与 limitation 一致。 |
| 资源 manifest | `temp/FEA-11-WATCH-1` 与 `agent-output/fea11-watch-1` 当前为空/不存在（closeout 时按实际字节数核销）；未触碰真实用户数据/AppData/外部卷/回收站。 |

---

## 7. AC11-1 口径（供 Lead 裁决，不代裁）

- 本卡完成 **watcher 生产者/消费者 + hint 通道**，但不做启动全量扫描；AC11-1 仍 **PARTIAL**，不得因本卡自动改 `MET`。
- 按 scope review 的口径，WATCH-1 兑现 C-01b SC-25 的「目录 watcher hint」；AC11-1 终态仍需对「启动/访问前检查」解释和「watcher 已兑现」组合做显式裁决。
- 本 review 的两项 P1/P2 修复不改变 AC11-1 的 PARTIAL 状态；closeout 时仍应保留 `<<PARTIAL>>` 与 limitation。

---

## 8. Closeout 建议（当前不适用；修复后）

**不建议现在 closeout。** 修复 P1（必须）与 P2（修复或显式 limitation 降级）后：

1. **P1 最小修复**：`SourceScanScheduler.TickCoreAsync` 在 `_hintedSources.Count > 0` 时让 budget 从 hinted 段开始（最小改动 `start = 0`，或 hinted-first + 原游标剩余）；新增确定性测试：10 targets / budget 4，先跑一个 tick，再 hint 最后一个 source，断言该 source 在 hint pass 被扫且 `HintPending=false`。
2. **P2 处置**：要么在成功 refresh 后通知 watcher 复核（最小 `if (result.Ok) NotifyTargetSetChanged();`，已在仓外 copy 验证 `Active=0`），要么把 AC-W1/L-W3 改成「arm-time 复核；撤销后到下一次 target-set change 前可能仍有 watcher」，并修改卡面/record 中「refresh 拆除」的表述。
3. 补 P3 测试：RootLost 判别断言、buffer 注入断言、generation drift、hint-after-prior-rotation、revoke-after-arm+refresh。
4. 重跑并更新 canonical 证据：Host 179（或修复后新数）/0/55；gated 1/0/0；全量 .NET（首跑 flaky 记录 + 复跑 1521/0/86）；pytest 3212/10 的**带 summary** 日志；pins 18/18；check/API/scope；每轮恢复 `verification/FEA-09`。
5. 重新生成 `record.md`/EV 哈希、卡面 AC 判定与 EV/limitation；`delivery_head` 取修复后的实现 commit（若新增修复 commit，不要沿用 e60105cf9 作为最终交付头）；`integration_commit` 由 DSH 集成后填写；不 push（Owner 不得 push）。
6. 保持 AC11-1 PARTIAL、L10 不解决、RH-3 不修；不把 P3 竞态/证据问题写成「已完全消除」。

若 Lead 认为 P2 可作为显式 limitation 接受，必须在卡面/record/scope-validation 中记录「refresh 不保证拆除」并得到 AC-W1 的显式降级裁决；但 P1 不能以 limitation 放行，因为它使 hint 的核心语义在常见 scheduler 状态下失效。

---

## 9. 证据位置

- 独立复跑日志：`G:\CODEX\New Manga.workspace\FEA-11\review-watch-1\`（`host-full.log`、`dotnet-full-reviewer*.log`、`pytest-reviewer.log`、`gated-reviewer.log`、`mut-*.log`、`probe-extra*.log`）。
- 独立 gated evidence：`G:\CODEX\New Manga.workspace\FEA-11\review-watch-1\gated-evidence\host-watch-runtime.json`。
- 独立变异/探针源码（仓外，未提交）：`...\review-watch-1\mut\`。
- 被审证据：`G:\CODEX\New Manga\verification\FEA-11-WATCH-1\**`（17 个 EV 文件，SHA 与卡面一致）。
- 本 review 未修改仓库、未 commit、未 push；仅测试运行产生的 tracked `verification/FEA-09` 变更已用 `git checkout -- verification/FEA-09` 恢复。

WATCH-1-R1-REVIEW: CHANGES
