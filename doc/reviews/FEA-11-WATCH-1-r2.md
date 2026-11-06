---
task: FEA-11-WATCH-1
title: FEA-11-WATCH-1 r2 窄面复审（fresh subagent；r1 CHANGES 返修核销）
reviewer: fresh subagent（独立上下文；未参与 FEA-11/WATCH-1 任何实现或 r1 复核）
session: 6600e84b-c4eb-497a-918e-fa64f7971d9a
parent_session: session-8db9dae5-49df-4d09-ac62-696f0805a95c
date: 2026-11-06
timezone: Asia/Shanghai
repo: G:\CODEX\New Manga
branch: main
worktree: clean（review 结束时）
base: 919c9aa1e
implementation_chain: e60105cf9（r1 feat）→ 19a2af7f3（r2 fix）
docs_backfill_commit: 579e44350
integration_commit: 1ee79fbd8（Lead r2 集成：STATUS/PLAN/LEDGER/卡面）
reviewed_head: 1ee79fbd8807bf27f6557598a6b2e1ba87e1870b
decision: CHANGES
---

# FEA-11-WATCH-1 r2 窄面复审

> **结论先行：`CHANGES`（P0=0 / P1=0 / P2=2 / P3=5 观察项）。**
>
> r1 的 **P1（阻断）与 P2（需处置）确实已修，且可判别**：我把两处修复分别回退到 r1 形态后，
> 新回归用例与我的独立探针都转红；恢复后全绿。普通 rotation/预算/去重语义未变。
>
> 但 **P3-3 的 `RootLost` 严格断言并未落地**：`SourceWatcherTests.cs:605` 仍是
> `Assert.True(status.Uncovered >= 1 || status.Active >= 0)`（第二项恒真），而卡面 r2 段、`record.md §7.3`、
> Handoff §8 与 r2 commit message 都写「已修：RootLost 断言改为 Active==0 && Uncovered>=1」。
> 同一用例还**在单用例隔离运行下稳定失败**（仓内原始工程 5/5 红）：根删除后 `HintAllIfStarted`
> 调度的 hint pass 占住单飞 gate，`Assert.True(await TickAsync())` 被合并返回 false；全量运行只是靠
> 调度偶然为绿。这两点都需要在 closeout 前做**最小返修**（2 行断言 + 1 行等 hint idle + 重跑取证），
> 否则 `AC-W3` 的「re-arm 或 uncovered」没有可判别的证据，且证据包与代码不一致。
>
> 本 review 只读：未修改仓库源码、未 commit、未 push；全部复核产物写在
> `G:\CODEX\New Manga.workspace\FEA-11\review-watch-1-r2\`。

---

## 1. 只读核验基线

| 项 | 事实 | 证据 |
|---|---|---|
| HEAD / reviewed_head | `1ee79fbd8807bf27f6557598a6b2e1ba87e1870b`（`docs(fea-11-watch-1): r2 集成…`） | `git rev-parse HEAD` |
| 实现链 | `e60105cf9`（feat）→ `19a2af7f3`（r2 fix）→ `579e44350`（docs 回填）→ `1ee79fbd8`（Lead 集成） | `git log --oneline -8` |
| r2 代码与 HEAD 一致 | 工作树 clean；`SourceScanScheduler.cs` / `SourceWatcher.cs` 工作区 SHA256 与我仓外副本逐字节一致 | SHA256 对照 |
| 构建与源码一致 | 我先做了一次 `dotnet build apps/desktop-avalonia/NewManga.sln -c Release --no-incremental`（0 warnings / 0 errors），随后所有 `--no-build` 运行都基于该构建 | 实跑 |
| 契约/schema/依赖 | `git diff --name-only 919c9aa1e..HEAD -- doc/plan doc/contracts src/` = 0 行；依赖类 diff 仅命中 `verification/FEA-11-WATCH-1/host-watch-runtime.json`（非依赖）；无 `*.csproj/*.props/*.targets/*.sln/*.lock` 变化 | 实跑 |
| App/UI 改动 | r2 两 commit 文件清单只有 Host src/tests + 卡/Handoff/verification；无 App/Core/契约/schema | `git show --name-only` |
| 未 push | `git branch -r --contains 19a2af7f3` / `1ee79fbd8` 均为空；`origin/main = b1c1f5a56`（本地领先，符合集成流程） | 实跑 |
| 工作树 | review 结束时 `git status --porcelain` 为空（全量 .NET 每轮后已 `git checkout -- verification/FEA-09`） | 实跑 |
| AC11-1 | `doc/tasks/FEA-11.md:103` 仍 `- [ ]`，仍带 `<<PARTIAL…>>`；本卡未回填 | 只读 |
| 卡状态 | `status: in_review`；`delivery_head: 19a2af7f3`；`integration_commit: null`；canonical/resource 均 `pending` | 只读 |
| L10 | 未解决；`919c9aa1e..HEAD` 无 RENDITION 文件/任务新增 | 只读检索 |
| 审查者独立性 | 我与实现者（`fea12-core-host`）、r1 审查会话（`48af6d93…`）均为不同上下文；未参与任何实现/返修 | 本会话 |

---

## 2. r1 findings 核销（独立验证，不以 Owner 日志为准）

### 2.1 P1（r1 阻断）：hint pass 被非零 budget 游标跳过 —— **已修，可判别**

**代码**（`apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs`）：

- `TickCoreAsync` 在 `lock (_gate)` 内计算 `hasHints = hinted.Count > 0`（第 768/788 行）；
- 第 804 行 `var start = hasHints ? 0 : _budgetCursor % targetCount;`；
- `ordered` 仍是 hinted（Ordinal）在前 + remaining（Ordinal）在后；预算循环 `for (index = start; index < targetCount && attempted < MaxTargetsPerTick; index++)` 与 `_budgetCursor` 更新逻辑未变（第 807-837 行）。

**独立探针**（仓外副本，与 HEAD 源码逐字节一致的编译产物）：

```text
PROBE-P1 tick1=s0,s1,s2,s3
PROBE-P1 hintPass=s9,s0,s1,s2 pending=False     （10 targets / budget 4，先普通 tick 再 hint s9）
PROBE-P1b pass=s8,s9,s0,s1 pending=False        （同时 hint s8+s9：hinted 逐个在前，≤4）
PROBE-DEDUP pass=s2,s0,s1,s3 pending=False      （同 source 两次 due bit → 只扫 1 次）
```

普通 rotation 独立断言（无 hint）：tick1 `s0..s3` → tick2 `s4..s7` → tick3 `s8,s9` → tick4 `s0..s3`，与 SCAN-1 AC-S3 一致。

**变异（回退到 r1 起点）**：把 `hasHints ? 0 :` 改回 `_budgetCursor % targetCount` 后：

```text
Probe_P1_HintAfterPriorRotation...        FAIL（Collection ["s3","s4","s5","s6"] 不含 s9）
Probe_P1_HintPassOrdersHintedFirst...     FAIL（pass=s2,s3）
SourceScanSchedulerTests.HintAfterPriorRotation_IsScannedInTheSamePass_AndPendingClears  FAIL
```

恢复后 78/78 绿。**结论：P1 修复真实生效，回归用例可判别旧缺陷。**

### 2.2 P2（r1 需处置）：撤销后成功 refresh（空枚举）不拆 watcher —— **已修，可判别**

**代码**（`SourceScanScheduler.RefreshTargetsAsync` 第 619-626 行）：`if (result.Ok) { NotifyTargetSetChanged(); _info?.Invoke(...); }`——成功 refresh 一律通知（含 `added=updated=0` / 空枚举），通知在 `_gate` 外、`_tickGate` 内（`NotifyTargetSetChanged` 本身逐 handler 隔离，第 668-687 行；`RegisterTarget` 的通知也在锁外）。

**独立探针**：

```text
PROBE-P2 armed active=1 handles=1
PROBE-P2 refresh=True active=0 uncovered=1 enumeratorCalls=1
PROBE-P2 lateEvent hints=0 scans=0        （旧 handle 迟到 Created 事件：0 hint / 0 scan）
```

**变异（回退为 `added + updated > 0` 才通知）**：

```text
SourceWatcherTests.RevokedTargetAfterSuccessfulRefresh_IsDisarmed_AndStaleHandleCannotHint  FAIL（Active Expected 0 / Actual 1）
Probe_P2_RevokedTargetAfterSuccessfulRefresh_IsDisarmed                                     FAIL（同上）
```

恢复后绿。**结论：P2 修复真实生效；`OnFileEvent` 的 slot 有效性校验同时拦住了已拆 handle 的迟到事件。**

### 2.3 P3（r1 六项）逐项核销

| r1 P3 | r2 声明 | 独立核验 | 判定 |
|---|---|---|---|
| **P3-1** Stop 后零 hint 窄竞态 | hint/HintAll 在 watcher `_gate` 内且 `_started` 为真时发出；Stop 持同一 gate；`OnFileEvent` 加 slot 校验；新测试 `Stop_WithPendingDebounceTimer_ProducesNoHints` | 代码路径实核：`OnDebounceElapsed` 在 `lock(_gate)` 内 `_started` 检查后直接 `_scheduler.HintSource`（第 809-824 行）；`HintAllIfStarted` 同 gate（第 830-841 行）；`Stop()` 先持 gate 清空 `_debounce`/`_slots` 再拆 timer/handle（第 240-266 行）→ **修复语义成立**。但新用例**非判别**：变异 C（把 hint 移回闸外，重建 r1 形态）后该用例与我的独立探针仍绿（见 §3.3） | 代码已修；测试仅覆盖 Stop 取消 timer 的既有行为，**记为证据局限** |
| **P3-2** canonical pytest 日志无 summary | 重跑全量并保留 `logs/pytest-summary.txt`（3212/10） | `logs/pytest-summary.txt` 实存且哈希与卡面 EV-14 一致；但 `logs/pytest-full.log`（EV-13）末尾仍是 QML stderr，**仍不含 summary 行**；我的独立全量 pytest 为 `3212 passed, 10 skipped, 10 warnings in 250.70s`（EXIT 0） | 可接受（r1 允许补 runner log）；建议在 record 里把 EV-13/EV-14 的关系写清 |
| **P3-3** RootLost 恒真断言 / 缺测试 | 「已修：RootLost 断言改为 `Active==0 && Uncovered>=1`」+ generation-drift/buffer 注入/overflow pending | **未实现**：`SourceWatcherTests.cs:605` 仍是 `Assert.True(status.Uncovered >= 1 || status.Active >= 0)`（第二项恒真）。generation-drift（`GenerationDrift_IsUncovered_NotArmed`）、buffer 注入（`InternalBufferBytes_IsPassedToTheWatchFactory` 断言 8192 到 handle）、overflow `Assert.False(HintPending)` 均已落地 | **finding（P2-1）**：声明与代码不一致 |
| **P3-4** redaction 口径过宽 | 收窄到 WATCH-1 status + `source watch*` / `source scan*` 日志行 | 测试改为过滤前缀行（`SourceWatcherTests.cs:490-500`）；卡面 AC-W5 与 record 明示「gated `host.log` 既有 `host_session` 行不在本卡范围」 | ✓ |
| **P3-5** `Sync` 的 `IntersectWith+UnionWith` | 改 `Clear()+UnionWith(desired)` | `SourceWatcher.Sync` 第 371-374 行已改；同锁内 OnFileEvent 复制 sourceIds，无撕裂 | ✓ |
| **P3-6** `DisposeAsync` 未 join 在飞 hint | dispose gate 前 `await _hintTask.WaitAsync(2s)`（吞超时/取消）+ 用例 | 代码已在 `_tickGate.Dispose()` 前 join（第 910-921 行）；用例 `DisposeAsync_WithInFlightHintPass_CompletesWithoutThrowing` 存在但**非判别**：变异 D（删掉 join）后仍绿（见 §3.3） | 代码已修；测试为 smoke，**记为证据局限** |

---

## 3. 独立复跑与变异（全部实跑，非引用 Owner 日志）

### 3.1 方法与仓外副本

- 仓内原始工程：`dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/... --no-build --no-restore`。
- 仓外副本（不触碰仓库源码）：`G:\CODEX\New Manga.workspace\FEA-11\review-watch-1-r2\mut\`
  - `src/NewManga.Host`、`src/NewManga.CoreClient` 从 HEAD 复制（`rg` 排除 bin/obj）；
  - `tests/SourceWatcherTests.cs`、`tests/SourceScanSchedulerTests.cs` 与仓内逐字节一致（SHA256 相同）；
  - 我的独立探针 `tests/ReviewProbeTests.cs`（P1/P1b/rotation/HintAll/P2/P3/dedup/RootLost 复刻）自写，不使用实现者的断言；
  - 变异全部只改副本，改后重建；每次恢复后核对 `SourceScanScheduler.cs` / `SourceWatcher.cs` 与仓内 SHA256 一致（`0E8E3DDB…`、`52CF4575…`）。
- 副本基线：`SourceWatcherTests + SourceScanSchedulerTests` **78/78 绿**（19+59，与卡面「19 例 / 59 例」一致）；独立探针 **7/7 绿**。

### 3.2 判别变异（3 项实做 + 1 项对照）

| 变异 | 改动 | 结果 |
|---|---|---|
| **A（P1）** | `start = hasHints ? 0 : cursor` → 恒 `cursor` | 仓内新用例 `HintAfterPriorRotation…` 红；我的两个 P1 探针红；探针输出复现 r1 现象 `hintPass=s3,s4,s5,s6`、`s9` 缺失 |
| **B（P2）** | 通知条件回退为 `added+updated>0` | 仓内 `RevokedTargetAfterSuccessfulRefresh…` 红（Active 0 vs 1）；我的 P2 探针红 |
| **C（P3-1 对照）** | 把 `HintSource` 移回 watcher `_gate` 外（r1 形态） | `Stop_WithPendingDebounceTimer_ProducesNoHints` **仍绿**；我的 P3 探针（真实时钟，事件后立即 Stop）**仍绿** → 该用例不能判别窄竞态（记录为证据局限） |
| **D（P3-6 对照）** | 删除 `DisposeAsync` 的 `await _hintTask.WaitAsync(2s)` | `DisposeAsync_WithInFlightHintPass_CompletesWithoutThrowing` **仍绿** → 该用例为 smoke，不能判别 join 是否实现（记录为证据局限） |

### 3.3 RootLost 复刻探针（新发现的实质问题）

我按 `SourceWatcherTests.RootLost_IsDegraded_AndReArmsOrCountsUncovered` 的步骤独立复刻：

```text
PROBE-ROOTLOST start active=1
PROBE-ROOTLOST afterRaise degraded=True uncovered=2 active=0 hintPending=True
PROBE-ROOTLOST tick=False hintPending=True      ← 仓内用例最后一行的断言在此场景为 false
```

- 根删除后 `HandleRootLost` → `RemoveSlot(countUncovered:true)`（+1）→ `HintAllIfStarted` 调度一个 hint pass（`HintPending=true`）→ `Sync()` 再次评估不可覆盖（`_uncovered` 再 +1）→ **`Active=0, Uncovered=2`**（这证明「严格断言」若要实现是可行的，且会通过）。
- 但 `Assert.True(await fixture.Scheduler.TickAsync())`（`SourceWatcherTests.cs:608`）与刚调度的 hint pass 抢 `_tickGate`：hint pass 先拿到即返回 `false`（I-3 单飞合并，属正常产品语义）。

**可复现性**（仓内原始测试工程，未改动）：

| 运行方式 | 结果 |
|---|---|
| 只跑该单用例（连续 5 次） | **5/5 失败**（`rootlost-single-5x.log`） |
| 只跑 `SourceWatcherTests` 整类 | 仓内 19/19 绿（`rootlost-class-isolation.log`）；仓外副本同一整类 **18/19 红**（`mut-watcher-isolation.log`） |
| 全量 Host 工程 / 全量 .NET | 185/0/55、1527/0/86 均绿（靠线程池负载下调度偶然） |

即：该用例**依赖调度时序**，在隔离运行时稳定红。它不是 r2 新引入（r1 形态同样存在），但 r2 的「P3-3 已修」声明没有覆盖它，且 AC-W3 的判别证据正引用这个用例。

### 3.4 其余独立探针结果

| 探针 | 输出 | 结论 |
|---|---|---|
| `Probe_Rotation_WithoutHints_IsUnchanged` | 4 个 tick 的顺序断言全过 | 普通 rotation 未被 P1 修复改变 |
| `Probe_HintAll_DrainsAcrossTicks_WithoutPendingLeft` | `pass1=s0..s3 pending=True`；再 2 个 tick 后 `total=10 个 distinct, pending=False` | HintAll 跨 tick 清空 due bit；注：生产 tick 间隔 900s，见 §7 P3-2 |
| `Probe_P3_StopWithPendingDebounce_ProducesNoHints` | `hints=0 pending=0 scans=0` | Stop 后零 hint（行为正确；但见变异 C 的判别性说明） |
| `Probe_P2_…` | `active=0 uncovered=1`，迟到事件 0/0 | P2 语义正确 |
| `Probe_Dedup_…` | `pass=s2,s0,s1,s3 pending=False` | 去重语义未变 |

---

## 4. 门禁独立复跑

| 门禁 | 卡面声明 | 我的独立结果 |
|---|---|---|
| Host 单测全量 | 185/0/55 | **185 / 0 / 55（240）**，8s（`host-full.log`） |
| gated HostRuntime watcher | 1/0/0 | **1 / 0 / 0**，真实 sidecar（`gated-reviewer.log`）；我重跑的 `host-watch-runtime.json` 字段与 EV-02 一致（ready=true / watcher_attached=true / armed=true / active_watches=1 / hint_count=1 / overflow_count=0 / redacted=true） |
| 全量 .NET | 1527/0/86（RUN1/RUN2） | **RUN1 1527/0/86**、**RUN2 1527/0/86**（0 failed；各工程 21+38+253+117+31+185+167+715；skipped 55+24+7=86）；两轮均未触发 r1 记录的 App/CoreClient `verification/FEA-09` flaky；每轮后 `git checkout -- verification/FEA-09`（RUN1 后确实出现 `M verification/FEA-09/logs/wire-redacted.ndjson`，已恢复；结束时工作树 clean） |
| 全量 pytest | 3212/10（实跑） | **3212 passed / 10 skipped / 10 warnings in 250.70s**，EXIT 0（`pytest-reviewer.log`） |
| `check.ps1 -TaskPath` | PASS（3 既有 warnings） | **PASS (3 warnings)**：9 个非终态 Task / STATUS 80% / REBASELINE_PLAN 80% |
| `verify_pins.ps1` | 18/18 | **PIN AUDIT: PASS (all 18)** |
| `generate_api_inventory.py --check` | PASS | **EXIT 0** |
| 范围 diff `919c9aa1e..HEAD -- doc/plan doc/contracts src/` | 空 | **0 行** |
| EV-01…EV-18 sha256 | 卡面 18 行 | **18/18 逐项重算一致**（含 r2 重抓的 `pytest-full.log` `db330f47…`、`pytest-summary.txt` `57d272da…`、`watcher-unit.log` `be9d1f71…`、`dotnet-full-1/2.log` `aa645ea2…`/`0efca82d…`、`record.md` `b21f5ce7…`、`scope-validation.log` `3168f245…`） |

> 说明：RUN1/RUN2 的 per-project 合计与卡面一致；我没有复现 r1 记录的 flaky（两轮 0 failed），也未复现卡面「首跑即绿」之外的异常。卡面「r1 基线 1521/0/86 不降」成立（r2 +6 用例 → 1527）。

---

## 5. 范围与纪律核验

| 项 | 结论 |
|---|---|
| r2 commit 是否只在 allowed_paths | **是**。`19a2af7f3`：Host `SourceScanScheduler.cs`/`SourceWatcher.cs`、Host 测试 2 文件、卡/Handoff/verification；`579e44350`：卡/Handoff/`check-post-commit.log`。无 App/UI/Core/契约/schema/依赖/STATUS/PLAN/LEDGER/reviews 改动。 |
| Lead 集成 commit | `1ee79fbd8` 只改 `doc/STATUS.md`、`doc/TASK_LEDGER.md`、卡面，属 DSH 职责；代码未变。 |
| 契约/schema/pins | `doc/plan`/`doc/contracts`/`src/` diff 0；pins 18/18 PASS；C-01b/C-17 字节未动。 |
| 依赖 | 无 csproj/props/targets/sln/lock 变化；仍只有 BCL `System.IO.FileSystemWatcher`。 |
| 未 push | 远程分支不含 `19a2af7f3`/`1ee79fbd8`；`origin/main=b1c1f5a56`。 |
| 工作树 | review 结束时 clean；未创建 worktree。 |
| AC11-1 | 未回填；`doc/tasks/FEA-11.md:103` 仍 `- [ ]` + `<<PARTIAL…>>`；卡面/record 均声明不回填。 |
| L10 | 未解决；无 RENDITION 实现/任务新增。 |
| RH-3 | 未修（target 集只增不减），与 limitation 一致。 |
| 真实数据/资源 | 我的门禁用例只用隔离 temp 根与 gated 隔离 evidence；未触碰用户数据/AppData/外部卷；仓外产物只在 `G:\CODEX\New Manga.workspace\FEA-11\review-watch-1-r2\`。 |

---

## 6. AC-W 判定（独立，不以卡面为准）

| AC | 我的判定 | 依据 |
|---|---|---|
| **AC-W1 生命周期/范围** | **MET** | arm 规则/registry 复核/typed skip/Stop 零 hint/幂等均通过；scope review 判别 #2「refresh 后已 arm 的撤销项被拆」现由 P2 修复满足（变异 B 证明旧代码不满足）。 |
| **AC-W2 hint 语义/去抖** | **MET** | N→1 去抖、hint 非 changed、`last_result=ok`、脱敏、未知 source 忽略均通过；P1 修复后 hint 在被 hint 的 pass 内被扫且 `HintPending=false`（探针 + 变异 A）。 |
| **AC-W3 overflow/根删除/上限** | **MET（证据有 P2 缺陷）** | overflow/根删除/上限/边界均不崩、typed 降级、计数正确；`Uncovered/Active` 的实际值我已独立确认（根删除后 `Active=0, Uncovered=2`）。但该 AC 的「re-arm 或 uncovered」判别用例仍是恒真断言且隔离运行红 → 见 §7 P2-1/P2-2。 |
| **AC-W4 与 SCAN-1 协同** | **MET** | 单飞合并、replay≤1、backoff 不提前、pause 0 次、命令集合 `{ScanSourceSync}`、零写均通过；hinted 优先在游标非 0 时也成立（P1 探针）。 |
| **AC-W5 资源/隐私/门禁** | **MET** | 我独立复跑 185/0/55、gated 1/0/0、1527/0/86×2、3212/10、pins 18/18、check PASS、API PASS、scope diff 0、EV 18/18；脱敏限定口径与测试一致。 |

---

## 7. Findings 与最小返修点

### P2-1（必须处置）`RootLost` 严格断言未实现，且声明为「已修」

- 位置：`apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceWatcherTests.cs:605`
  ```csharp
  Assert.True(status.Uncovered >= 1 || status.Active >= 0);   // 第二项恒真
  ```
- 声明：卡面「r2 返修」段、`record.md §7.3` P3-3 行、Handoff §8、`19a2af7f3` commit message 均写「RootLost 断言改为 `Active==0 && Uncovered>=1`」。
- 最小修复（实测该场景 `Active=0, Uncovered=2`，断言会通过）：
  ```csharp
  Assert.Equal(0, status.Active);
  Assert.True(status.Uncovered >= 1);
  ```
- 若 DSH 裁决按 limitation 接受，则必须把上述四处「已修」改为「未实现/limitation」，并从 AC-W3 判别证据里移除该断言，不能维持现有表述。

### P2-2（必须处置）`RootLost_IsDegraded_AndReArmsOrCountsUncovered` 隔离运行稳定红

- 位置：同文件第 608 行 `Assert.True(await fixture.Scheduler.TickAsync());`
- 机制：`HandleRootLost` 内的 `HintAllIfStarted` 已经调度 hint pass（`_hintTask` 在飞，占住 `_tickGate`），随后测试立刻 `TickAsync()` → 单飞合并返回 `false`（产品语义正确）。
- 复现：只跑该用例 5/5 红；只跑整类在仓外副本 18/19 红（仓内整类偶然绿）；全量运行靠调度偶然绿。
- 最小修复：像同文件的 `Overflow_RespectsBudget_AndCompletesAcrossTicks` 一样先等 hint idle，再断言：
  ```csharp
  await fixture.Scheduler.HintIdleAsync();
  Assert.True(await fixture.Scheduler.TickAsync());
  ```
- 验证要求：修复后至少跑一次「单用例」与「整类」；再跑 Host 185/0/55 与全量 .NET 1527/0/86，并按新证据重签 EV-16/EV-17（+卡面 EV 表）。

### P3 观察项（不单独阻断，建议在 closeout 说明中处置或登记）

1. **P1 修复的残余成本未披露**：hint pass 从 index 0 开始，10 targets/budget 4 的探针里 `hintPass=s9,s0,s1,s2`，即每次 hint 会重扫最多 `budget-1` 个刚扫过的 target（每次都是完整 `ScanSourceSync`）。这是 r1 建议的最小修复，行为可接受，但卡面/record 只写「普通 rotation/预算语义不变」，未写「hint pass 会重扫」。建议在 limitation 里补一句，避免后期被误读为「零额外扫描」。
2. **overflow/根删除的「跨 tick」在生产是 900s 间隔**：测试用手动 tick 证明 10 目标/budget 4 跨 tick 完成；生产 loop 的 tick 间隔默认 900s（`IntervalSeconds`），hint 耗尽后不会额外调度。建议 limitation 写明「跨 tick 的实际延迟由周期决定（默认 900s/tick）」，与「不漏事件」区分。
3. **P3-1 / P3-6 的回归用例不具备判别性**（变异 C/D 均绿）。代码修复本身我已实核成立；建议把这两个用例在 record 里标注为 smoke/行为覆盖，不要写成「证明竞态/join 已修」，或补可判别测试（可用测试内 hook/延迟 executor 构造确定性窗口）。
4. **EV-13 仍不含 summary**：`logs/pytest-full.log` 末尾仍是 QML stderr；summary 在 EV-14。建议在 record §4/§5 明示「EV-13 为过程日志、EV-14 为 summary 证据」，避免重复 r1 P3-2 的歧义。
5. **卡面「测试要求」表未同步 r2**：第 104 行仍写「全量 pytest（引用）… 非重跑」，与实际 r2 实跑并保留 summary 不一致（AC-W5 与 record 已更新）。建议一并修正，保持单一声明源。

---

## 8. AC11-1 口径（供 Lead 裁决，不代裁）

- 本卡完成 watcher 生产者/消费者与 hint 通道，但**不做启动全量扫描**；AC11-1 仍 **PARTIAL**，不得因本卡自动改 MET。
- 本 r2 复审的结论（含 P2-1/P2-2 返修）不改变 AC11-1 的 PARTIAL 状态；closeout 仍应保留 `<<PARTIAL>>` 与 limitation。
- L10 未解决、RH-3 不修、watcher 漏事件依赖周期兜底——均与现有 limitation 一致，closeout 时应原样保留。

---

## 9. Closeout 建议（当前不适用，返修后）

1. **返修**：按 §7 P2-1/P2-2 做最小测试修复；不需要改产品代码。
2. **重跑**：Host 单测 185/0/55（用例数不变）、gated 1/0/0、全量 .NET RUN1/RUN2 1527/0/86（跑后 `git checkout -- verification/FEA-09`）、pytest 3212/10（或引用基线，本卡零 Python）；pins/check/API/scope diff 复跑。
3. **重签证据**：`logs/watcher-unit.log`（EV-16）、`record.md`（EV-17）、卡面 EV 表与 `logs/gates.log`；若同时改了卡面结论文字，`check.ps1 -TaskPath` 需复跑。
4. **定稿口径**：AC-W1…W5 按本 review 的独立判定可定稿 MET（AC-W3 以修复后的严格断言为证据）；`delivery_head` 取返修后的实现链头（若只有测试/证据提交，说明 `delivery_head` 与 `integration_commit` 的差异）；`integration_commit` 由 DSH 填写（当前 `1ee79fbd8` 只集成文档）。
5. **limitation 保留**：漏事件周期兜底、folder 事件=该 source due（无增量 diff、受预算/单飞约束）、hint pass 重扫成本、跨 tick 延迟由 900s 周期决定、无 fake-Core/注入时钟 seam、SCAN-2 RH-3 不修、AC11-1 PARTIAL、L10 不解决。
6. **不 push 的边界**：Owner 不 push；push 由 DSH 在 closeout 后执行。

---

## 10. 复核产物位置（仓外）

- 报告：`G:\CODEX\New Manga.workspace\FEA-11\review-watch-1-r2\FEA-11-WATCH-1-r2.md`
- 门禁日志：`host-full.log`、`gated-reviewer.log`、`gated-evidence\host-watch-runtime.json`、`dotnet-full-run1.log`、`dotnet-full-run2.log`、`pytest-reviewer.log`
- 变异/探针：`mut-repo-tests-baseline.log`、`probes-pass.log`、`mut-a.log`（P1 回退）、`mut-b.log`（P2 回退）、`mut-c.log`（P3-1 对照）、`mut-d.log`（P3-6 对照）、`probe-dedup.log`、`probe-rootlost.log`、`rootlost-single-5x.log`、`rootlost-class-isolation.log`、`mut-watcher-isolation.log`
- 仓外副本：`mut\`（HEAD 源码 + 我的独立探针；两处源码与仓内 SHA256 一致，未提交）

WATCH-1-R2-REVIEW: CHANGES
