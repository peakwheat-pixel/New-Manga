---
task_id: FEA-11-SCAN-1
review: r1
reviewer: DSH fresh subagent（上下文独立；未参与实现/返修）
reviewer_session_id: 074cebe5-157b-4d75-833d-d0624f979fa6
reviewer_source: DeepSeek Harness Agent Teams 子 agent（fresh context）
repo: G:\CODEX\New Manga（main）
reviewed_head: a684c511d
implementation_commit: 73d01fd2b
base_commit: e0c370870
current_head_at_review_end: d867e5389
reviewed_at: 2026-11-06T02:42:00+08:00
decision: changes_requested
severity_counts: P0=0 P1=1 P2=5 P3=4
---

# FEA-11-SCAN-1 r1 独立 Review（只读、上下文独立）

## 0. 结论摘要

- **Decision: `changes_requested`（P0=0，P1=1，P2=5，P3=4）。**
- 本卡交付的 Host 只读周期扫描切片、证据、门禁与范围纪律总体**扎实**：全量 .NET 三次复跑均 `1437 passed / 0 failed / 81 skipped`；独立真实 IPC 复跑 `ok → missing → ok → changed` 通过，wire 精确为 `{core.ping, OpenHostSession, RegisterSourceReadGrant, ScanSourceSync}` 四命令；12 个 Canonical Evidence sha256 全部 MATCH；pins 18/18、API inventory PASS、`check.ps1 -TaskPath` PASS；实现 commit 全部落在 allowed_paths，无 Core/契约/STATUS/PLAN/LEDGER/reviews 改动，未 push。
- **阻断项 P1-1（AC-S4 未完全 MET）**：调度器在 `changed` 扫描后把 `_identityDigests` 覆盖成新内容的 identity；随后源被删除时，`MissingObservation` 发送的是这个“未被 Core 记录”的新 identity，Core `_verify_missing_observation` 用已记录 location identity 比对，返回 `SOURCE_PLAN_STALE`，状态为 `error` 而不是卡面要求的 `missing`。已用隔离 fixture + 真实 Python Core + 真实 `HostSourceScanExecutor` 复现（`ok → changed → deleted` ⇒ `error/SOURCE_PLAN_STALE`）。卡面 AC-S4 `<<MET>>` 对“源被删除”的表述过度，L-G 只覆盖“首次成功扫描前已消失”，未覆盖“changed 后刷新 baseline 再删除”。
- 其余问题为**不阻断**的测试强度/边界/规格偏差（P2）与 nit（P3），详见 §7。

---

## 1. 审查对象与仓库状态

- 被审实现：`73d01fd2b feat(fea-11-scan-1)`，26 files；base `e0c370870`；`reviewed_head = a684c511d`（仅 docs：卡/HANDOFF 记录 `delivery_head: 73d01fd2b`）。
- 审查结束时仓库 `HEAD = d867e5389`（FEA-11-MATCH-1 closeout，docs/Python 测试注释）；审查期间仓库 HEAD 发生推进（非本卡），**未触及任何 SCAN-1 文件**。`8e8aa5aaa`（STATUS/PLAN/LEDGER 指针）/`6e5e210a5`（Handoff check 记录）亦为 docs-only。
- 本报告以 `a684c511d`/`73d01fd2b` 的代码与证据为准；`d867e5389` 之后的仓库变化不属于本卡实现，但复跑门禁在**当前工作树**进行，结果已如实记录（§4）。
- Reviewer 身份：DSH fresh subagent，session `074cebe5-157b-4d75-833d-d0624f979fa6`；未参与实现、未参与返修、未改仓库、未 commit/push。

---

## 2. AC-S1…AC-S6 判定

| AC | 判定 | 依据（独立复核） |
|---|---|---|
| AC-S1 调度器生命周期与配置 | **MET**（P3 测试缺口） | 单 loop、`Start` 幂等、`Stop/Dispose` join、`Pause/Resume`、注入 `TimeProvider`、900s 默认、env `[60,86400]` 非法回落均有代码与 32 例定向测试；`HOST_SESSION_INVALID`/`CORE_SESSION_MISMATCH`/sidecar exit → paused。WARN 文案未断言；本卡未新增 HostRuntime 级测试，现有 `HostRuntimeIntegrationTests` 在三次全量中均 skip（`HostSidecarFact`），Ready/Dispose 接线仅靠代码审查（见 P3-2）。 |
| AC-S2 目标注册、单飞、只扫不写 | **MET**（P2-4/P2-5） | 单飞合并没有排队；tick 内串行；只经 `ISourceScanExecutor`；重复注册按 `source_id` 覆盖；App 注册只出现在 `Completed` 分支（`ImportDockViewModel.cs:428-431`），文件 id 与生产 `StableSourceId` 一致（`SourceImportModels.cs:786,920-924`），folder 无 registry 条目跳过、空 bookId 跳过均有测试。**ViewModel 端 Completed-only 无测试**（`FakeHostController.ScanTargetRegistrations` 未被任何测试使用）；registry 解析是 containment 而非卡面 I-2 的“精确匹配”。 |
| AC-S3 预算与退避 | **MET（caveat P2-1）** | 10 目标 budget=4 → 4/4/2；超限 `deferred` 非失败；Error 退避 60/120/240/480、成功清零；预算 8/256MiB/10000 常量存在。**`denied` 结果被当作成功清零退避**（与 `DeniedCodes` 注释“diagnostic, backoff”冲突）；退避上限 3600 与 denied 无测试。 |
| AC-S4 全量重枚举（真实链路） | **PARTIAL / 不得判 MET** | 真实 fixture 的 `ok → missing → ok → changed` 通过，DB 快照前后相同；但 **changed → deleted 实测 `error/SOURCE_PLAN_STALE` 而非 `missing`（P1-1）**。卡面 `<<MET>>` 与 AC-S4 line 135 的“源被删除 → result=missing”不成立。 |
| AC-S5 状态快照与脱敏 | **MET**（P2-2 潜在并发缺陷） | `SourceScanStatus` closed record、`recent≤50`、`ok` 不入 recent、脱敏测试（路径/`source-`/`host_session`/异常原文零命中）通过；`deferred` 不作为 result。**`_recent.Add`/`TargetState` 写在 `_gate` 外，Snapshot 在 `_gate` 内读取，存在数据竞争**（当前无 UI 消费者，未触发测试）。 |
| AC-S6 范围、冻结、回归与证据 | **MET**（P3-3/P3-4） | pins 18/18、API inventory PASS、`check.ps1 -TaskPath` PASS（3 既有 warnings）、pytest 3203/10、全量 .NET 三次 1437/0/81；EV-01…EV-12 sha256 全 MATCH；scope diff 仅 `src/application/sources/matcher.py`（MATCH-1 r2 `e8b0b2db8`，非本卡）。`changed-files.txt` 未落盘（scope-validation.log §3 有清单）。 |

**总判定**：AC-S1/S2/S5/S6 MET；AC-S3 MET with caveat；**AC-S4 PARTIAL** ⇒ 不能按当前卡面进入 done/closeout。

---

## 3. 证据与哈希核对（独立）

自动比对卡面 Canonical Evidence 表与实际文件：

| EV | 结果 | 实测 sha256 |
|---|---|---|
| EV-01 dotnet-host-scheduler.log | MATCH | `84dd749afd5bf07e10a097691aef3552b9ed7cb83aa90b27520dba6f26896d2d` |
| EV-02 fea11-scan-ipc.log | MATCH | `c6afc880f63345554d6fd26cafc33e8ee81ad583445a9857351b95f2833153a2` |
| EV-03 real-ipc.json | MATCH | `789336b7c1cfaf882e32f29d49ab780b2db86bccd71252e11202c450b2af22f1` |
| EV-04 real-ipc.txt | MATCH | `ddc3d73f3b226c8e4c44908708a2a7d05e44335b12401b91870e66f7621d1266` |
| EV-05 status-redaction.log | MATCH | `f5da210e610afa1d91d7bfcf6abbc1033b2c3ed2be732beda8cbe0e23806b689` |
| EV-06 dotnet-full-1.log | MATCH | `7338b774b579d240c36be5d1524c29746d8ea5052ceabcbc8ace7aff6c867e22` |
| EV-07 dotnet-full-2.log | MATCH | `3ff2b32c081e0eb56dc353fc421c01959f5637d740bdab44e5c0699f0703320f` |
| EV-08 pytest-full.log | MATCH | `69aa9605ad864ff138aa55d0586c342b40ed51b1a3d970a89a3a523604606345` |
| EV-09 pins.log | MATCH | `2ebcc2c24b9075f939b9beb027ed2decd273323581327db12b6097adb37c4d94` |
| EV-10 api-inventory.log | MATCH | `6d1e41178756c82c9500e141743fe5783c00f75d4ca09b4c6206323efb02e4b7` |
| EV-11 scope-validation.log | MATCH | `59f769c175fd815281069316fae568bcfc1b135220b2fadd273cf2e3531c69a0` |
| EV-12 gates.log | MATCH | `ae7bc562ec4a8bd35ed38ac3f0ef5eee7dc6ebf57a5fdf951ea26369e8de2648` |

EV-12 的 Summary 与三次独立复跑一致；EV-02/03/04 的真实 IPC 复跑另生成新鲜 fixture（见 §4/§5），原证据字节未被改写。

---

## 4. 独立复跑（命令、结果、flaky 口径）

所有命令在 `G:\CODEX\New Manga` 主工作树执行；未 commit/push。

| Gate | 独立命令 | 结果 |
|---|---|---|
| G1 定向 scheduler/registration | `dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --no-build --nologo --filter "FullyQualifiedName~SourceScanScheduler\|FullyQualifiedName~Fea11ScanRegistration"` | **PASS 32/0/0，EXIT 0**（两次：变更前与最终恢复重建后各一次） |
| G2 真实 IPC | `$env:NEWMANGA_FEA11_IPC=1; dotnet test ... --filter "FullyQualifiedName~Fea11ScanIpcTests"` | **PASS 1/0/0，EXIT 0**（变更前与最终恢复重建后各一次；新鲜 fixture `G:\CODEX\New Manga.workspace\FEA-11\fixtures\scan-*`） |
| G4 全量 .NET RUN1 | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build --nologo` | **1437 passed / 0 failed / 81 skipped / 1518，EXIT 0** |
| G4 全量 .NET RUN2 | 同上 | **1437 / 0 / 81 / 1518，EXIT 0**（`verification/FEA-09` 测试副作用已 `git checkout --` 恢复） |
| G4 全量 .NET RUN3（恢复重建后） | 同上 | **1437 / 0 / 81 / 1518，EXIT 0** |
| G5 pytest | `C:/Python314/python.exe -m pytest tests -q -p no:warnings --tb=no` | **3203 passed / 10 skipped / 244.31s，EXIT 0**（= 卡面基线；SCAN-1 commit 零 Python；当前 HEAD 的 MATCH-1 closeout 仅改 `tests/fea11/test_source_match.py` 注释，不计数） |
| G6 check | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-SCAN-1.md` | **PASS (3 warnings)，EXIT 0**（当前 HEAD 非终态 12；卡面记录时的 13 是 MATCH-1 closeout 前的旧数；其余 2 warning 为 STATUS/PLAN 80%） |
| G7 pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS 18/18，EXIT 0** |
| G8 API inventory | `C:/Python314/python.exe tools/generate_api_inventory.py --check` | **PASS，EXIT 0**（IHostController 54 成员不变） |
| G9 scope | `git diff --name-only e0c370870..HEAD -- doc/plan doc/contracts src/` | 仅 `src/application/sources/matcher.py`；归因 `e8b0b2db8`（FEA-11-MATCH-1 r2），**非本卡**；`apps/desktop-avalonia` diff 恰为 12 个卡内文件 |

**flaky 口径**：已知 `FluentResidual2VisualEvidenceTests` vs `WireLogSourceRedactionTests` 跨程序集证据写竞争在三次全量中**均未触发**；不据此宣称“稳定 PASS”，只记录三次未触发。每次全量后均执行/确认 `git checkout -- verification/FEA-09`，最终工作树 clean。日志：`G:\CODEX\New Manga.workspace\FEA-11\review-scan-1\dotnet-full-r{1,2,3}.log`、`pytest-review.log`。

---

## 5. 零写 / 只读 / wire 证据（独立核对）

1. **只调 `ScanSourceSync`**：调度器只依赖 `ISourceScanExecutor`（`SourceScanScheduler.cs:73-79`），生产实现 `HostSourceScanExecutor` 只做 `SourceReadCoordinator.IssueAsync`（发出既有 `RegisterSourceReadGrant`）与 `CoreServiceClient.SendHostControlAsync("ScanSourceSync", ...)`（`:677-727`）；无 plan/preview/confirm/apply/relink/repoint/resync。
2. **wire 精确集合**：独立真实 IPC 新鲜 fixture 的 `real-ipc.json` 记录 `wire_commands = [OpenHostSession, RegisterSourceReadGrant, ScanSourceSync, core.ping]`；`db_snapshot_unchanged=true`；steps `ok → missing → ok → changed`。与卡面/EV-03 一致。**注：测试代码本身只断言 `Contains(ScanSourceSync)` + forbidden 缺席（`Fea11ScanIpcTests.cs:123-139`），没有断言精确四元集合**（P2-3）。
3. **Core DB 零写**：真实 IPC 测试的 SQLite 快照覆盖 `page_bindings/source_versions/source_entries/sources/source_locations`，前后相同；独立复跑同结果。代码路径 `ScanSourceSync` 在 `scanner.py` 是 scan/live 语义，不写业务行。
4. **无新 Core 命令/capability/schema/wire/依赖**：`HostCommandRegistry`、`src/`、`.csproj`、schema/migration 均零 diff（`src/` 唯一条目为 MATCH-1 `matcher.py`）；本卡只新增 in-process `SourceScanStatus` 属性与 App 的独立接口方法 `RegisterCompletedImportScanTargets`（`IHostController`/C-07 未改，API inventory PASS）。
5. **PDF/watcher/通知/UI**：无新文件/命令/UI/设置项；PDF/CBZ/ZIP 仅沿用既有 `ScanSourceSync` 源类型；watcher/冷启动/通知持久化均未实现（登记 WATCH-1/SCAN-2）。
6. **脱敏**：调度器状态不含路径/grant/session/异常原文；日志仅 source_id/结果/计数/typed code；真实测试断言通过。

**`availableSources`/`isAvailable`**：本切片代码库中不存在这两个符号（grep 仅命中其他模块既有字段）；新增注册只走 `ISourceImportController`/`HostRuntime` in-process seam，未新增/改变任何 UI availability 分支，`NullHostController` 为显式 no-op。此项以“无此符号、不影响未实现分支”成立。

---

## 6. 范围 / 纪律

- **`73d01fd2b` 文件范围**：26 files，全部在卡 `allowed_paths`：Host 4 + App 5 + Host.Tests 2 + App.Tests `FakeHostController.cs` + 卡/Handoff + `verification/FEA-11-SCAN-1/**`；**无** `doc/plan`、`doc/contracts`、`src/`、`STATUS`、`PLAN`、`LEDGER`、`reviews`、`doc/handoffs` 之外越界文件。
- **后续 docs-only**：`a684c511d`（卡/Handoff）、`8e8aa5aaa`（STATUS/PLAN/LEDGER 指针）、`6e5e210a5`（Handoff check 记录）；`d867e5389` 为 MATCH-1 closeout，未触及 SCAN-1。
- **未 push**：本地 main 领先 origin/main（审查开始时 `origin/main...HEAD = 0 942`），本卡 commit 未推送。
- **工作树**：审查开始 clean；三次全量测试造成的 `verification/FEA-09/logs/wire-redacted.ndjson` 副作用已恢复；审查结束 `git status --porcelain` 为空（无他卡 WIP 遗留）。审查者未改仓库/未 commit/未 push。

---

## 7. Findings（按严重度；含最小返修点）

### P1-1（阻断）changed 扫描覆盖 missing baseline identity，导致“changed → 删除”报 `SOURCE_PLAN_STALE` 而非 `missing`

- **现象（已复现）**：隔离 fixture + 真实 Python Core + 真实 `HostSourceScanExecutor`：
  `tick1 unchanged → ok`；`tick2 同文件同名同大小重写 → changed`；`tick3 删除源 → error`，`recent.lastCode = SOURCE_PLAN_STALE`。
  原始日志：`G:\CODEX\New Manga.workspace\FEA-11\review-scan-1\probe-ok-changed-delete.log`；复现程序：`...\review-scan-1\probe-ok-changed-delete\`。
- **代码根因**：
  - `SourceScanScheduler.cs:799-814` 对所有非 missing/encrypted/unsupported 的 scan（包括 `changed`）执行 `_identityDigests[sourceId] = identityDigest`（`:809`）。
  - 删除路径要求 cached digest（`:738-742`），并把它作为 `expected_identity_digest` 发送（`:762`）。
  - Core `scanner.py:449-469` 的 `_verify_missing_observation` 用 `location["content_digest"]` 等已记录事实重算 identity 并逐项核对；changed 后的新内容 digest 与 location 记录不同 ⇒ `SOURCE_PLAN_STALE`。
- **违反**：AC-S4 line 135（“源被删除 → … result=missing”）；L-G 口径“首个 ok tick 缓存 identity”被实现改成“每次成功 scan 覆盖”；卡面 AC-S4 `<<MET>>` 过度宣称。
- **最小返修**：
  1. 只在**未变化/ok** 观察时写 `_identityDigests`（如 `counts is not { HasChange: true }`，或显式 `result == ok`）；changed 时保留首次 ok 的 recorded identity，直到未来 apply/重新导入更新 location（本切片不做 apply）。
  2. 在 `PeriodicScan_DetectsMissingThenChanged_WithZeroCoreWrites` 末尾追加一步：changed 之后再次删除 → 断言 `missing`（当前会 error；修复后通过）。这样正好覆盖真实路径。
  3. 更新 L-G 文案：changed 扫描不得覆盖 baseline identity；首次 changed 前从未 ok 时仍 fail-closed（`SOURCE_ENTRY_MISSING`，已有 R-9 口径）。
  4. 修复后重签 EV-02/03/04 / full logs，更新卡面测试表与 Handoff。
- **备注**：若 DSH 决定不修，必须把 AC-S4 从“源被删除 → missing”收窄，并在 L-G 明写“changed 后删除 → SOURCE_PLAN_STALE error（无法 attest missing）”，且不得保留 `<<MET>>` 的无条件表述。

### P2-1 `denied` 结果未退避，与注释/AC-S3 的“typed 失败退避”冲突

- `SourceScanScheduler.cs:138-143` 注释称 authorization refusals “diagnostic, backoff”；`:536-543` 却把 `Denied` 与 `Ok/Changed/Missing/Unsupported` 一起 `Failures=0; BackoffUntil=null`。
- 影响：`SOURCE_ACCESS_DENIED`/`SOURCE_GRANT_REVOKED` 等每个 interval 重试（default 900s，min 60s），`recent`/日志持续增长；无测试覆盖 Denied。
- 最小返修：把 Denied 按失败计入退避（保留 `LastResult=denied`），或若有意 retry 则删除 “backoff” 注释并补一条“denied 下一 tick 重试”的判别测试；二选一，不能保持现状。

### P2-2 快照与 tick 状态存在数据竞争（`_recent` / `TargetState`）

- `TickAsync` 在 `:331` 调用 `ApplyOutcome`（`_gate` 外）；`ApplyOutcome` 在 `:553-567` 写 `TargetState.LastScanAt/LastResult/Counts/Deferred` 并在 `:561` 对 `_recent` 做 `Add`。
- `Snapshot` 在 `:362-379` 持 `_gate` 读这些字段并 `_recent.ToArray()`；写方不持同一把锁。`List<T>.ToArray` 与 `Add` 并发可能抛异常/读到不一致；`DateTimeOffset?` 16 字节字段也不是原子写。
- 当前无 UI 消费者（L-D），故未触发；但 AC-S5 的“defensive snapshot”应无此竞争。
- 最小返修：把 `ApplyOutcome` 内的状态写入与 `_recent` 追加放入 `_gate`（内部无 await；日志回调移到锁外），或在专用 `_stateGate` 下做快照复制；补一条并发 Snapshot/Tick 的压力测试。

### P2-3 真实 IPC wire 断言弱于证据/卡面

- `Fea11ScanIpcTests.cs:123-139` 仅 `Assert.Contains("ScanSourceSync")` + forbidden 缺席；若未来 scan 路径多出一条非 forbidden 命令（如某读命令），测试仍绿，而 `real-ipc.json` 会多出来，证据与测试脱节。
- 最小返修：`Assert.Equal(new[] { "OpenHostSession", "RegisterSourceReadGrant", "ScanSourceSync", "core.ping" }, wireCommands)`（既有排序不变量），并保留 forbidden 断言。

### P2-4 App 端“仅 Completed 后注册”无测试；`FakeHostController.ScanTargetRegistrations` 未被使用

- 现有 2 例只测 `SourceImportCoordinator.RegisterCompletedScanTargets` 的派生/跳过（`Fea11ScanIpcTests.cs:436-494`），未测 `ImportDockViewModel` 的 Completed 分支（`:428-431`）、Failed/Cancelled 不注册、空 bookId 在 VM 层的行为；`FakeHostController.cs:748-756` 新增的 registration 列表无任何断言。
- 这是 requirement #3 的核心行为，建议补 headless VM 测试（可放 `Fea11ScanIpcTests.cs` 内用本地 fake，或由 DSH 把 App.Tests 的 `ReferencedImportUiTests.cs` 纳入窄批 allowed_paths），覆盖：Completed→1 次注册且 bookId/sources 正确；Failed/Cancelled→0；空 bookId→0；重复 Completed 由 scheduler 覆盖（已有 scheduler 测试）。

### P2-5 registry 解析用 containment 而非 I-2 的“精确匹配”

- `SourceScanScheduler.cs:838-856` 以 `SourceSecurity.Contains(root.Root, normalized)` + 最长 root 选择 entry；卡 I-2 line 96 要求“按 path 从 `SourceAccessRegistry.List()` **精确匹配**解析（不猜、不推断；匹配失败 → typed 失败）”。
- 生产文件导入把文件路径注册为 root，exact 可行；真实 IPC fixture 注册的是父目录 root（fixture identity 对齐所需），因此当前测试依赖 containment。风险：自身 entry 被 revoke/丢失时可静默回退到祖先 entry；missing 观察随后因 registry/generation 不匹配报 `SOURCE_PLAN_STALE`，而非在解析阶段 typed fail。
- 最小返修：先 exact root（大小写不敏感）匹配，未命中再按 containment 并显式记录/测试该回退；或把 I-2 文案改成“精确优先 + 受控 containment”，并加一条自身 entry revoked 的 typed-failure 测试。

### P3-1 bookId 在 receipt 完成时读取（选择切换竞态）

- `ImportDockViewModel.cs:458-459` 在 Completed 时调用 `_bookId()`；`LibraryViewModel` 传入 `SelectedBook?.BookId`。若导入期间用户切换选中书，plan/chapter 仍属旧书而注册的 `project_ids` 变成新书；后续 scan 会因 `scope=current` 项目不匹配持续 `SOURCE_PLAN_STALE`。
- 最小返修：在 Confirm/Start 时捕获 bookId 并用于完成时注册（或依据 receipt.ChapterId 映射）；低概率，非阻断。

### P3-2 测试缺口（非阻断）

- env 非法回落的 **WARN 未断言**（只测 `ResolveIntervalSeconds` 返回值）。
- `HostSourceScanExecutor.ProbeBudget` 的文件大小/folder 成员数阈值未单测（fake executor 的 `Budget` 只测调度路径）；默认 `8/256MiB/10000` 常量、退避上限 3600、`Stop()` 后手动 `TickAsync` 语义均无判别测试。
- 本卡未新增 HostRuntime 级测试；现有 `HostRuntimeIntegrationTests`（`HostSidecarFact`）在三次全量中均 skip（Host.Tests 50 skipped），Ready 后启动/Dispose/StopSidecars join 仅靠代码审查。
- 这些不影响当前 MET 判定，但建议在返修批次顺带补齐最关键的两项：WARN + ProbeBudget。

### P3-3 `changed-files.txt` 未落盘，但 AC-S6 文案列出该证据

- 卡 AC-S6 line 146 写“证据完整（EV/scope-validation/changed-files/dotnet-full/pins/check）”；`verification/FEA-11-SCAN-1/` 无 `changed-files.txt`（其他 FEA-11 卡有），清单仅存在于 `scope-validation.log` §3。建议补文件或把 AC-S6/Handoff 文案改为“scope-validation.log §3”。

### P3-4 `SourceScanStatus.Disabled` 的 `paused=true` 语义

- `SourceScanStatus.cs:22-24` 在“无 scheduler”时返回 `paused=true`；语义可解释为“not running”，但调用方可能把 paused 与 disabled 混淆。建议 `paused=false` 或加注释/判别测试；非阻断。

---

## 8. Limitation 核对（如实性）

| 项 | 判定 |
|---|---|
| L-A 仅本会话目标/重启丢失 | **如实**：`_targets` 仅内存，App 只在 import Completed 注册；重启清空。 |
| L-B watcher 仍缺 | **如实**：本卡无 FileSystemWatcher/通知；WATCH-1 承接。 |
| L-C 状态不持久 | **如实**：`recent/targets` 仅内存；配置从 HostOptions 恢复。 |
| L-D 无用户可见呈现 | **如实**：无 UI/通知；状态仅 in-process 属性。 |
| L-E 成本未标定 | **如实**：预算/退避默认值来自设计而非真实大库标定；R-1 已写。 |
| L-F 共享源 bases 单项目 | **如实**：注册 `project_ids=[bookId]`，单项目；SCAN-2 承接。 |
| L-G missing identity 依赖 | **部分如实**：fixture identity 对齐仅测试内（`Fea11ScanIpcTests.cs:51-60`），未改产品；首次 tick 前消失 fail-closed 已写。**但未覆盖 P1-1 的 changed-overwrite 场景**，需补 limitation 或修复。 |
| AC11-1 仍 PARTIAL | **如实**：卡/Handoff/STATUS/FEA-11.md 均写明仅闭合定时扫描半边；watcher/启动扫描登记 WATCH-1/SCAN-2，未宣称全绿。**但 AC-S4 的 `<<MET>>` 与本 review 的 changed→deleted 反例冲突，属卡面过度宣称，需随 P1 修正。** |

口径校正（对 review brief 的用词）：**L-B 是 watcher 缺失，不是“预算/退避未标定”**；预算/退避的成本标定属于 R-1/L-E。卡面 L-A…L-G 列表本身正确。

---

## 9. 变异 / 反证（至少 2 项，已执行）

| # | 变异 | 命令/针对测试 | 结果 | 恢复 |
|---|---|---|---|---|
| M1 | 移除每 tick 目标上限（`for` 条件去掉 `attempted < MaxTargetsPerTick`） | `dotnet test ... --filter Budget_RotatesTenTargetsIntoFourFourTwo` | **RED**：first tick 扫描 `s0..s9` 10 个，期望 `s0..s3`；`失败:1/通过:0`，EXIT 1。日志 `...\review-scan-1\mutation-m1-budget.log` | 源文件 SHA256 恢复为 `A0180372323B30BB0DF81CAFC0334CCA336FC3804432C3BDC9CEE1D0AA5759BB`，`-t:Rebuild` 重建 |
| M2 | 改 wire 探针：`ScanCommand = "ResyncSource"`（替换 `ScanSourceSync`） | `$env:NEWMANGA_FEA11_IPC=1; dotnet test ... --filter Fea11ScanIpcTests` | **RED**：first tick `ok` 变 `error`，`失败:1/通过:0`，EXIT 1。日志 `...\review-scan-1\mutation-m2-wire.log` | 同上恢复/重建；恢复后 focused 32/0/0 + real IPC 1/0/0 PASS |
| R1（额外反证，非变异） | 真实 `HostSourceScanExecutor` 序列 `ok → changed → deleted` | `review-scan-1\probe-ok-changed-delete`（真实 Python Core + 隔离 fixture） | **`error/SOURCE_PLAN_STALE`**（期望 `missing`）；即 P1-1。日志 `...\review-scan-1\probe-ok-changed-delete.log` | 仅改仓外 fixture（workspace），仓内无改动 |

M1/M2 均证明对应断言有效（不是“测试恒绿”）；恢复后源码 hash 与 `git status` clean 已复核。

---

## 10. Closeout 建议

1. **不要现在 done/closeout**：P1-1 未修且 AC-S4 不能判 MET。建议 Owner 按 §7 P1-1 最小修复（1 行缓存条件 + 1 个 real-IPC step + L-G 文案），或由 DSH 明确裁决“接受 changed→deleted 限制并收窄 AC-S4”。
2. **修复后交付**：新 commit（保持 `allowed_paths`），重签 EV-02/03/04 与全量日志，更新卡测试表/Canonical Evidence/Handoff；`delivery_head` 才可更新；`integration_commit` 由 DSH 填写。
3. **AC11-1 回填口径**：保持 **PARTIAL**；只写“Host 定时只读扫描生产者已交付并由真实 IPC 验证（ScanSourceSync 零写、ok/changed/missing 状态）”，同时保留 watcher（WATCH-1）与启动扫描（SCAN-2）缺失；不得写 AC11-1 MET。
4. **Review 落库**：本报告现位于仓外 `G:\CODEX\New Manga.workspace\FEA-11\review-scan-1\FEA-11-SCAN-1-r1.md`；DSH 可将其复制为 `doc/reviews/FEA-11-SCAN-1-r1.md`（卡 allowed_paths 允许）并记录 reviewer session `074cebe5-157b-4d75-833d-d0624f979fa6`。在 P1 修复前，状态应停在 `in_review`（或 `changes_requested`）。
5. **P2 处置建议**：P2-1/P2-2/P2-3 可在同批最小修复（改动小）；P2-4/P2-5 至少登记 follow-up（若不在本卡返修，需在 Handoff/卡 limitation 明示）。P3 可记录为技术债。
6. **证据/资源**：临时 fixture 均在 `G:\CODEX\New Manga.workspace\FEA-11\fixtures\scan-*`，无真实用户数据；复现日志/变异日志在 `...\review-scan-1\`，由 DSH 按 Resource Manifest 处理；`verification/FEA-09` 副作用已恢复。

---

## 11. Decision + 摘要

**Decision：`changes_requested`（P0=0，P1=1，P2=5，P3=4）。**

本卡的主干（Host 单实例只读 scheduler、900s/env/预算/退避/单飞、in-process 状态、App Completed 注册、真实 IPC 零写证据、范围与门禁）总体实现扎实且可复跑：三次全量 .NET 均 1437/0/81/1518，pytest 3203/10，pins 18/18，API/check PASS，12 个 EV sha256 全 MATCH，wire 仅四命令、DB 零写，scope 无越界；变异 M1/M2 均能正确变红且已还原。

阻断点是 **AC-S4 的 missing 语义**：`changed` 扫描把 cached identity 覆盖为新内容 identity，之后删除源时 Core 用已记录 location identity 校验，只能返回 `SOURCE_PLAN_STALE`（状态 `error`），无法产生卡面承诺的 `missing`；已在真实 Python Core + 真实 executor 上复现（`ok → changed → deleted ⇒ error`）。最小修复是“只在未变化/ok 观察时缓存 baseline identity”，并在 real-IPC 测试补 `changed → deleted → missing` 步骤；修复后本卡可重新提交 Review。其余 P2（denied 退避、快照竞争、wire 精确断言、App Completed 测试、registry exact-match）与 P3 建议按 §10 分批处置。
