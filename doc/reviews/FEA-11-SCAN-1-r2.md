---
task_id: FEA-11-SCAN-1
review: r2
reviewer: DSH fresh subagent（上下文独立；未参与 r1 实现、未参与 r2 返修）
reviewer_session_id: 41de61d5-f944-49fc-9938-d9798e3059f2
reviewer_source: DeepSeek Harness Agent Teams 子 agent（parent session 8db9dae5-49df-4d09-ac62-696f0805a95c；fresh context、只读）
repo: G:\CODEX\New Manga（main）
reviewed_head: 9daa94a25
implementation_commit: 7080167e1
r1_delivery: a684c511d
r1_implementation_commit: 73d01fd2b
base_commit: e0c370870
current_head_at_review_end: 1596e1c72
reviewed_at: 2026-11-06T07:38:00+08:00
decision: approved
severity_counts: P0=0 P1=0 P2=0 P3=3
scope: r2 窄面复审（P1-1 修复 + P2×5/P3×4 同批处置 + 证据重签 + 门禁复跑）
---

# FEA-11-SCAN-1 r2 窄面独立 Review（只读、上下文独立）

## 0. 结论摘要

- **Decision: `approved`（P0=0，P1=0，P2=0，P3=3；P3 均为文档/规格对齐 nit，不阻断 closeout）。**
- **r1 P1-1 已修复并经独立判别验证**：`HostSourceScanExecutor.ProjectScanResult` 仅 `!changed && status=="ok"` 刷新 `_identityDigests`；独立真实 IPC 复跑得到 `unchanged(ok) → changed(changed) → changed-deleted(**missing**) → restored(ok) → changed-again(changed)`；**独立变异**（临时回退为 r1 前缀语义“任何 status 都覆盖”）后真实 IPC 立即变红 `Expected: "missing" / Actual: "error"`，恢复后复跑绿且源文件 sha256 与变异前逐字节相同（`6b1f2ad1…`），`git status` clean。
- **r1 P2×5 全部同批闭环**：denied 退避（60/120…，结果仍 denied、不暂停）、`ApplyOutcome` 状态+recent 写入全部在 `_gate` 内（Snapshot 同锁读取，日志回调锁外）、real-IPC wire 断言改为**精确四元集合**、App VM 级 5 例（仅 Completed 注册 / Failed·Cancelled·空 bookId 不注册 / bookId 在 confirm 捕获）、registry **exact-first + exact-revoked fail-closed + 受控 containment 回退**并有单测。P3-1/P3-3/P3-4 已修，P3-2 部分（ProbeBudget 单测补齐，WARN/HostRuntime 接线登记 follow-up）。
- **独立门禁复跑**：focused **37/0/0**、App VM **5/0/0**、real IPC **1/0/0**、全量 .NET **1447/0/81/1528 EXIT 0**（干净树首跑）；pins **18/18**、API inventory **PASS**、`check.ps1 -TaskPath` **PASS（3 既有 warning）**；17 个 Canonical Evidence sha256 **17/17 MATCH**；SCAN-1 三个 commit 0 域外。
- **P3（不阻断）**：① Handoff 的 Canonical Evidence 计数/编号与卡面 17 项不一致（写“15 个”，且 status-redaction/pytest/pins/api/scope/changed-files 的 EV 号错位）；② 卡 I-2 冻结文案仍写“精确匹配”，实现为“精确优先 + 受控 containment 回退”（处置表已说明，冻结文本未加注）；③ P3-2 残余 follow-up 未具名（无 Task ID/owner）。

---

## 1. 审查对象与仓库状态

- 被审范围：`7080167e1 fix(fea-11-scan-1)`（21 files，含 6 个源码/测试 + 卡/Handoff + 证据重签）与 `9daa94a25 docs(fea-11-scan-1)`（2 files：卡 + Handoff 记录 `delivery_head`）。base `e0c370870`；r1 实现 `73d01fd2b`（26 files）、r1 交付 `a684c511d`。
- 审查开始 `HEAD = 9daa94a25`、`git status` 为空。审查期间 Lead 在本工作树推进了 3 个 **FEA-12-UI docs-only** commit（`16285fecd`/`67c7c4f76`/`1596e1c72`，只改 `doc/REBASELINE_PLAN.md`/`doc/TASK_LEDGER.md`/`doc/tasks/FEA-12-UI.md`），并在审查后半段出现 **FEA-12-UI 未提交 WIP**（`RecycleBinView.axaml`/`LibraryView.axaml`/`BookDetailPanel.axaml`/`ShelfPageView.cs` 等，属另一卡，作者所有）。本报告以 `9daa94a25` 的 SCAN-1 内容为准；已核对 `git diff 9daa94a25..HEAD -- apps/ verification/ src/` 为空，SCAN-1 不受后续 docs commit 影响。
- 审查者身份：DSH fresh subagent，session `41de61d5-f944-49fc-9938-d9798e3059f2`；未参与 r1 实现、未参与 r2 返修；未 commit、未 push。除下述一次**受控变异及逐字节还原**外未改仓库内容。
- 审查产物（仓外）：`G:\CODEX\New Manga.workspace\FEA-11\review-scan-1-r2\`（各 gate 日志、mutation 日志/元数据、本报告）。为隔离并发 WIP 曾临时创建 `wt-9daa94a25` linked worktree 并在跑完后 `git worktree remove --force` + `prune`，主工作树未受影响。

---

## 2. r1 findings 核销（逐项，独立复核）

| r1 finding | r2 处置 | 独立核销结论 | 证据 |
|---|---|---|---|
| **P1-1（阻断）** changed 覆盖 `_identityDigests` → changed 后删除报 `SOURCE_PLAN_STALE/error` 而非 `missing` | `SourceScanScheduler.cs:847-858`：`var changed = counts is { HasChange: true };` + `if (!changed && status == "ok" && sourceId is not null && identityDigest is not null && IsLowerHex64(identityDigest)) _identityDigests[sourceId] = identityDigest;`；全文件 `_identityDigests` 仅此 1 处写入（另 1 处读取、1 处声明） | **FIXED**。真实 IPC 新增 `changed → changed-deleted → missing` 步并断言 `missing`（`Fea11ScanIpcTests.cs:107-113`）；我的独立 IPC 复跑与独立变异均确认（§4/§5） | EV-03/04/05、EV-06；本报告 §4 |
| **P2-1** denied 不退避 | `ApplyOutcome` 的 `Denied` 分支：`Failures+1`、`BackoffSeconds()`、`BackoffUntil=now+backoff`，`LastResult` 仍 `denied`，不 `Pause`；`DeniedCodes` 注释 “diagnostic, backoff” 与实现一致 | **FIXED**（`DeniedResult_IsBackedOff_AndKeepsDeniedResult`：59s 内不重扫、60s 后重扫、warn `backoff=60/120`、`Paused==false`） | `SourceScanScheduler.cs:566-573`；focused 37/0/0 |
| **P2-2** `_recent`/TargetState 写与 Snapshot 读跨 `_gate` | `ApplyOutcome` 整段（状态字段 + `_recent.Add` + 50 上限）在 `_gate` 内；warn/info 日志回调移到锁外；tick 内 `BackoffUntil` 读、`Deferred` 写、`_lastTickAt/_nextTickAt` 均持锁 | **FIXED**。逐处核对：Snapshot 读取的字段（`_targets`/`_recent`/`_paused`/`_lastTickAt`/`_nextTickAt`/`Enabled`）只在其写点持同一把锁；`_budgetCursor` 仅在单飞 tick 内读写、不被 Snapshot 读取。`ConcurrentSnapshotDuringTicks_DoesNotRaceOrThrow`（4 reader × 40 tick × 6 目标）通过 | `SourceScanScheduler.cs:542-613`；focused 37/0/0 |
| **P2-3** real-IPC wire 仅 `Contains` | `Assert.Equal(new[]{"OpenHostSession","RegisterSourceReadGrant","ScanSourceSync","core.ping"}, wireCommands)`（排序后比较）+ forbidden 断言保留 | **FIXED**。我另从**新鲜 fixture 的 `wire.ndjson`** 直接解码 16 个请求帧：`core.ping×6 / OpenHostSession×1 / RegisterSourceReadGrant×4 / ScanSourceSync×5`（distinct 恰为四元集合），无任何 plan/apply/write 命令 | `Fea11ScanIpcTests.cs:131-149`；本报告 §5 |
| **P2-4** App 端 Completed-only 无测试 | `FakeHostController.cs` 新增 `Fea11ScanRegistrationVmTests` 5 例（Completed 注册 1 次且 bookId/sources 正确；Failed/Cancelled 不注册；空 bookId 不注册；confirm 捕获 bookId，选中书切换后仍注册 book-1），`ScanTargetRegistrations` 被实际断言 | **FIXED**。VM 走真实 `ImportDockViewModel` + fake controller；`ImportDockViewModel.cs:434-441` 只在 `receipt.State == Completed` 调 `RegisterCompletedScanTargets` | VM 5/0/0（本报告 §4） |
| **P2-5** registry containment 而非 I-2 精确匹配 | `ResolveRegistryEntry` 改为：先 locator/root **等值（大小写不敏感）** 精确匹配；exact 命中但 `RevokedAt != null` → 返回 null（fail-closed）；无 exact 才用“受控 containment 回退”（只读 root、未撤销、最长 root） | **FIXED（留 P3 文案 nit）**。`RegistryResolution_PrefersExactMatch_AndFailsClosedOnRevokedExactEntry` 覆盖 exact 优先 / 无 exact 回退 / exact 已撤销 fail-closed / 全不匹配 null。生产文件导入以文件路径注册 root，exact 路径成立 | `SourceScanScheduler.cs:886-939`；focused 37/0/0；P3-② |
| **P3-1** bookId 在 receipt 完成时读取 | `_referenceBookId` 在 `ConfirmReferenceImportAsync` 开始时捕获、新 plan 时清空，注册优先使用；无捕获时才回退 live selection | **FIXED**（`ConfirmCapturesBookId_BeforeALaterSelectionSwitch` 通过） | `ImportDockViewModel.cs:41-43,296-299,328-331,464-470` |
| **P3-2** WARN/ProbeBudget/HostRuntime 接线测试 | 补 `ProbeBudget_UsesRealFileSizeAndFolderMemberLimits`（文件 64/64 未超、folder 3/3、缺失 → null）；WARN 文案与 HostRuntime Ready/Dispose 级测试登记 follow-up | **PARTIAL（已按 r1 允许口径登记）**：allowed_paths 确未含 HostRuntime 测试文件；代码审查：`StartSourceScanScheduler` 在 `Result.IsReady` 后、`DisposeAsync`/`StopSidecarsAsync` 均先 `StopSourceScanSchedulerAsync` 并 join；env 非法 → `ResolveIntervalSeconds` 返回 fallback + `_log.Warn`。残余 follow-up 未具名 → P3-③ | `SourceScanScheduler.cs:417-442`；`HostRuntime.cs` diff；P3-③ |
| **P3-3** `changed-files.txt` 缺失 | 已新增 `verification/FEA-11-SCAN-1/changed-files.txt`（r2 modified 9 条 + r1 12 条，含卡/Handoff/verification 分组） | **FIXED**（EV-17 存在且内容与两个 commit 的文件清单一致） | EV-17 |
| **P3-4** `Disabled.paused=true` | `SourceScanStatus.Disabled` 改为 `paused=false` 并加注释；`DisabledStatus_IsNotPaused` 覆盖 | **FIXED** | `SourceScanStatus.cs:21-29` |

**无新增 P0/P1/P2。** r1 要求的三项（缓存条件、real-IPC 步、L-G/证据/卡面）全部落地且可复现。

---

## 3. 独立复跑（命令、结果、时间）

命令均在 `G:\CODEX\New Manga`（main）执行，日志见 `...\review-scan-1-r2\*.log`；全量跑后均 `git checkout -- verification/FEA-09`。

| Gate | 命令 | 结果 |
|---|---|---|
| G1 focused | `dotnet test .../NewManga.Host.Tests.csproj -c Release --no-build --nologo --filter "FullyQualifiedName~SourceScanScheduler\|FullyQualifiedName~Fea11ScanRegistration"` | **37/0/0，EXIT 0**（`g1-focused.log`） |
| G2 App VM | `dotnet test .../NewManga.App.Tests.csproj -c Release --no-build --nologo --filter "FullyQualifiedName~Fea11ScanRegistrationVm"` | **5/0/0，EXIT 0**（`g2-appvm.log`） |
| G3 real IPC | `$env:NEWMANGA_FEA11_IPC=1; dotnet test .../NewManga.Host.Tests.csproj -c Release --no-build --nologo --filter "FullyQualifiedName~Fea11ScanIpcTests"` | **1/0/0，EXIT 0**；新鲜 fixture `scan-68473c7491d5436e84f923004e72dfa1`；序列 `ok → changed → missing → ok → changed`（`g3-realipc.log`） |
| G4 全量 .NET（干净树首跑） | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build --nologo` | **1447 passed / 0 failed / 81 skipped / 1528，EXIT 0**（07:24:50–07:28:07；`g5-full-run1.log`）。分程序集：Appearance 21/0/0；Presentation 38/0/0；ThemeEngine 253/0/0；DesignSystem 117/0/0；Host 144/0/50；ApplicationCore 31/0/0；CoreClient 167/0/24；App 676/0/7 |
| G4 全量 .NET（第二跑） | 同上 | **1446 / 1 / 81 / 1528，EXIT 1**：失败为 `NewManga.App.Tests.V2ConformanceTests.V2Xaml_UsesNoRawDesignValues_AndNoForbiddenEffects`（`RecycleBinView.axaml: raw padding/margin/spacing…`）。归因：**并发 FEA-12-UI 未提交 WIP**（该文件 mtime 07:28:35，晚于首跑结束 07:28:07），与本卡无关，**也不是**已知 `FluentResidual2VisualEvidenceTests` flaky（`g5-full-run2.log`） |
| G4' 干净 worktree 全量（补充） | 临时 worktree `wt-9daa94a25`（detached 9daa94a25）`dotnet test .../NewManga.sln -c Release`（含 build） | **1443 / 1 / 84 / 1528**：唯一失败 `SourceRegistryTests.EncryptedPersistenceGenerationCorruptionAndExplicitReset` → `InvalidOperationException: isolated repository not found`（linked worktree 的 `.git` 是文件，被该既有测试的 `Directory.Exists(".git")` 探测拒绝；同时 CoreClient 多 3 个 skip）。**属 worktree 环境限制，非 SCAN-1**；App.Tests 676/0/7、Host 其余全绿，SCAN-1 用例全通过。跑后已删除 worktree（`g5-clean-wt-full-run.log`） |
| G5 pytest（引用） | r1 日志 `3203 passed, 10 skipped`；r2 两个 commit 零 `.py` 改动（`git show --name-only 7080167e1 9daa94a25` 无 `.py`） | 引用基线成立，未虚假声称 r2 重跑 |
| G6 check | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-SCAN-1.md` | **PASS（3 warnings：非终态 Task 12 / STATUS 80% / REBASELINE_PLAN 80%），EXIT 0**（`check.log`） |
| G7 pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS 18/18，EXIT 0**（`pins.log`） |
| G8 API inventory | `C:/Python314/python.exe tools/generate_api_inventory.py --check` | **PASS，EXIT 0**（IHostController 54 成员不变） |

**flaky 口径（如实）**：已知 `FluentResidual2VisualEvidenceTests` 跨测试 git-status 证据写竞争在**我的两次主树全量中都未触发**（首跑 0 failed；第二跑失败是另一测试、另一原因）；提交证据里 EV-08 记录了实现者一次真实命中（`dotnet-full-2.log` 的 `[FAIL] FluentResidual2VisualEvidenceTests…`，App 675/1/7），并附隔离复跑 `flaky-fluent-residual2.log` PASS 1/0/0 与 RUN3 全量 1447/0/81。**不据此宣称“稳定 PASS”**；卡/Handoff/gates.log 的措辞也未宣称稳定。

---

## 4. 独立变异（判别力确认，已还原）

| # | 变异 | 命令 | 结果 | 还原 |
|---|---|---|---|---|
| M-P1 | 把 identity 缓存条件回退为 **r1 前缀语义**：`if (sourceId != null && identityDigest != null && IsLowerHex64(...)) _identityDigests[sourceId] = identityDigest;`（changed 也覆盖） | 重建 Host.Tests 后 `$env:NEWMANGA_FEA11_IPC=1; dotnet test ... --filter Fea11ScanIpcTests` | **RED（符合预期）**：`失败 1/通过 0`，`Expected: "missing" / Actual: "error"`，EXIT 1（`mutation-p1-real-ipc.log`） | `git checkout --` 后逐字节还原为审查前 LF 版；sha256 `6b1f2ad158cefafb6392be481bf09e07d6b004b603ed5c8da720805b42d2468c` 与变异前一致；重建后 G3 复跑 **1/0/0 绿**；`git status` clean（`mutation-meta.txt`、`g3-realipc-restored.log`） |

结论：`changed → deleted → missing` 断言不是恒绿断言，能真实区分 r1 缺陷与修复；修复本身在真实 Python Core 链路上生效。

---

## 5. 证据真实性（独立核对）

- **17 个 Canonical Evidence sha256 全部复算 MATCH（17/17）**：EV-01…EV-17 与卡面表逐项一致（修改前后各算一次，结果相同；EV 文件在 `9daa94a25` 后未被改动）。
- **real-ipc.json / real-ipc.txt / 日志一致性**：tracked 证据步骤 `unchanged,changed,changed-deleted,restored,changed-again` → 结果 `ok,changed,missing,ok,changed`；`identity_baseline_kept_after_changed=true`、`db_snapshot_unchanged=true`、`wire_commands=[OpenHostSession, RegisterSourceReadGrant, ScanSourceSync, core.ping]`、`scheduler_status.recent=3`（changed/missing/changed 三条，ok 不入 recent，自洽）。我的新鲜 fixture 同结构复现（仅 zip 字节随 seed 随机不同，符合 fixture 非确定性；`same_size_rewrite.size=358` 不变）。
- **wire 独立解码**：从新鲜 `wire.ndjson` 解出 16 帧请求，distinct 命令恰为四元集合；5 次 `ScanSourceSync` 对应 5 tick，其中 missing tick `grant_ids=[]` 且携带 `registry_id/generation/expected_identity_digest=841e72…`（来自最后一次 ok 观察，非 changed 内容），4 次有 grant 的 tick 与 `RegisterSourceReadGrant×4` 一一对应；payload `scope=current`、`kind=resync`、`project_ids=["b1"]`，无 plan/apply/relink/resync 命令。
- **flaky 分列**：EV-08 为真实 FAIL 日志（1446/1/81），EV-09 为复跑 PASS（1447/0/81），EV-10 为隔离单测 PASS；卡/Handoff 如实写明“不称稳定”。未见把 flaky 写成稳定 PASS 的表述。
- **门禁证据**：EV-12 pins 18/18、EV-13 API PASS、EV-14 scope、EV-15 gates、EV-16 脱敏、EV-17 changed-files 均与我的独立复跑/核对一致。

---

## 6. 范围 / 纪律

- `7080167e1`（21 files）与 `9daa94a25`（2 files）逐文件对照卡 `allowed_paths`：**0 域外**；`73d01fd2b`（26 files）同样 0 域外。无 `doc/plan`、`doc/contracts`、`src/**`、`STATUS`/`REBASELINE_PLAN`/`TASK_LEDGER`/`reviews` 改动（这些由 Lead 的独立 docs commit 承担）。
- 全区间 `e0c370870..9daa94a25` 的非 apps/doc/verification 文件仅 `src/application/sources/matcher.py` + `tests/fea11/test_source_match.py`，归 **FEA-11-MATCH-1**（`e8b0b2db8` 等），非本卡；`apps/` diff 恰为卡内 12 文件。
- **未 push**：`git rev-list --count origin/main..HEAD = 948`，本卡 commit 未推送。
- 工作树：审查开始 clean；审查结束后可见的未提交项均为 **FEA-12-UI 并发 WIP**（`RecycleBinView.axaml`、`LibraryView.axaml`、`TrashModels.cs`、`TrashUiTests.cs` 等）与 Lead docs commit，**非本卡产物、非审查者改动**；`verification/FEA-09` 测试副作用已恢复为 clean；`verification/FEA-11-SCAN-1/**` 与 SCAN-1 源码/测试/卡/Handoff 均 clean。审查者未 commit/push。

---

## 7. AC 判定、AC11-1 口径与 limitation

| AC | 判定 | 独立依据 |
|---|---|---|
| AC-S1 生命周期/配置 | **MET**（P3-② follow-up：WARN 文案与 HostRuntime 级测试仍仅代码审查） | 37 例含单 loop/幂等/Pause/Resume/注入时钟/边界；`HostRuntime` 在 Ready 后启动、Dispose/StopSidecars 先停并 join；env 非法 → 900s + WARN |
| AC-S2 注册/单飞/只扫不写 | **MET** | VM 5 例 + 精确命令集 + 单飞/覆盖/两源顺序测试；wire 独立解码证实只读 |
| AC-S3 预算/退避 | **MET**（r2 起 denied 也计入退避） | 4/4/2、60/120/240/480、成功清零、deferred、denied 60/120 且不暂停 |
| AC-S4 全量重枚举（真实链路） | **MET** | 真实 IPC `ok → changed → missing → ok → changed`，`changed→deleted` 断言 `missing`，DB 快照前后相同，wire 四命令；独立变异判别成立 |
| AC-S5 状态快照/脱敏 | **MET** | closed record、recent≤50、deferred 非 result、锁一致性、脱敏测试 0 命中 |
| AC-S6 范围/冻结/回归/证据 | **MET**（P3-① Handoff 编号为文档 nit） | pins 18/18、API PASS、check PASS、全量 1447/0/81、17/17 EV MATCH、0 域外、未 push |
| **AC11-1** | **PARTIAL（必须保持）** | 卡（`:61,:106,:275`）、Handoff（`:60,:75`）、`doc/STATUS.md:10`、`doc/tasks/FEA-11.md:238` 均写明只闭合“定时扫描”半边；watcher（WATCH-1）与启动扫描（SCAN-2）仍缺，未宣称全绿 |

**Limitation 真实性**：L-A…L-F 与卡一致；**L-G 已更新**为“changed 不污染 baseline；首次 ok/unchanged 之前源消失则 fail-closed `SOURCE_ENTRY_MISSING`（不伪造 missing）”，与代码（`ScanMissingAsync` 无 baseline → Error("SOURCE_ENTRY_MISSING")）和真实 IPC 行为一致。R-9 同步更新。

---

## 8. Findings（P3，不阻断；含最小返修点）

### P3-① Handoff 的 Canonical Evidence 计数/编号与卡面 17 项不一致

- 卡面为 **EV-01…EV-17**（17 项，我逐项 sha256 MATCH）；`doc/handoffs/FEA-11-SCAN-1-e0c370870.md` 仍写“**15 个** Canonical Evidence”（L18）、“Canonical Evidence EV-01…EV-15”（L20）、“⑦ 15 个 EV sha256”（L54）。
- EV 号错位（Handoff → 卡面应为）：status-redaction `EV-14`→**EV-16**（L30）；pytest `EV-09`→**EV-11**（L32）；pins `EV-10`→**EV-12**、api-inventory `EV-11`→**EV-13**、scope `EV-12`→**EV-14**、changed-files `EV-15`→**EV-17**（L33）。另 L31 的 full-1/2/3/flaky/gates = EV-07/08/09/10/15 与卡面一致，EV-09 在 L31 与 L32 被重复使用。
- 影响：Handoff 是 closeout 依据之一，错位 EV 号可能被 Ledger/集成记录沿用；卡面（权威）与 17 个 hash 本身无误。
- **最小返修**：只改 Handoff 的数字与编号（17、EV-16/11/12/13/14/17），或统一改为“路径 + 卡面 EV 号”并删除重复的 EV-09；属 allowed_paths，可与 closeout 同批 docs commit。

### P3-② 卡 I-2 冻结文案仍写“精确匹配”，实现为“精确优先 + 受控 containment 回退”

- 卡 `:96`（I-2）要求“从 `SourceAccessRegistry.List()` **精确匹配**解析”；实现（`ResolveRegistryEntry`）在 exact 全部未命中时回退到“最具体的未撤销 containing root”（为真实 IPC fixture 的父目录 root 与既有父目录注册形态服务），已在「r1 Review 处置」表与代码注释说明。
- 影响：规格文本与实现字面不一致，后续 Reviewer/集成者可能按“只允许 exact”复核而产生误解；行为本身有 exact-first、revoked fail-closed 与单测保护，且 containment 不命中时报 typed 失败。
- **最小返修**：在 I-2 该句后补“（精确优先；无 exact 命中时按受控 containment 回退，见 r2 处置）”，或由 DSH 在 closeout 记录该解释性修订；不改代码。

### P3-③ P3-2 残余 follow-up 未具名

- 卡 `:199`、Handoff `:36,:73` 均写“登记为 follow-up / 后续技术债”，但**没有 Task ID、没有 owner、没有进入任何 Task/债务清单**；WARN 文案断言与 HostRuntime Ready/Dispose 级接线测试仍只靠代码审查。
- **最小返修**：在 closeout 时把它挂到具名承接（如 `FEA-11-SCAN-2` 的前置说明，或 STATUS/LEDGER 的技术债行），便于后续释放时被看见。

---

## 9. Closeout 建议

1. **可 closeout（本 Review 判 approved）**：P0/P1/P2 = 0；P3-① 建议在 closeout 的 docs commit 内一并修正（Handoff 数字），P3-②/③ 可用一句规格注记/具名 follow-up 处理，无需再开实现返修轮。
2. **`delivery_head`**：保持 **`7080167e1`**（实现+证据+卡/Handoff）；`reviewed_head = 9daa94a25`（记录 delivery_head 的 docs commit）；`integration_commit` 由 DSH/Lead 在集成验证后填写（当前 null）。
3. **状态迁移**：`in_review` → `done`（或项目约定的 closeout 迁移）；`reviewer` 字段可填本报告 session `41de61d5-f944-49fc-9938-d9798e3059f2` 与来源“DSH fresh subagent（parent 8db9dae5…）”；`canonical_evidence_status`/`resource_closeout_status` 按 DSH 口径收口。
4. **Review 落库**：本报告现在仓外 `G:\CODEX\New Manga.workspace\FEA-11\review-scan-1-r2\FEA-11-SCAN-1-r2.md`；DSH 可复制为 `doc/reviews/FEA-11-SCAN-1-r2.md`（卡 allowed_paths 允许），历史 r1 字节保持不变。
5. **AC11-1**：继续 **PARTIAL**；closeout 文案只能写“Host 定时只读扫描生产者已交付并由真实 IPC 验证（ScanSourceSync 零写、ok/changed/missing）”，watcher/启动扫描仍缺（WATCH-1/SCAN-2），不得写 AC11-1 MET。
6. **集成验证建议**（DSH）：在干净树或稳定树复跑一次全量 .NET（期望 1447/0/81/1528）；若触发 `FluentResidual2VisualEvidenceTests`，按既有口径隔离复跑并分列；跑后 `git checkout -- verification/FEA-09`。**注意当前主工作树存在 FEA-12-UI 未提交 WIP，全量结果会被其污染（我已实测 `V2ConformanceTests` 因 WIP `RecycleBinView.axaml` 变红），建议等该卡收敛或在独立树复跑。**
7. **资源**：我的临时 fixture 在 `G:\CODEX\New Manga.workspace\FEA-11\fixtures\scan-*`（含 `scan-68473c…`），无真实用户数据，由 DSH 按 Resource Manifest 统一处置；review 日志在 `...\review-scan-1-r2\`；临时 worktree 已删除。
8. **后续 Task**：`FEA-11-WATCH-1` / `FEA-11-SCAN-2` 仍为 proposed（本卡未实现）；是否释放由 DSH 裁决。

---

## 10. 摘要

**`approved`。** r1 的 1 个 P1 与 5 个 P2 全部闭环且可独立复现判别：`changed` 不再覆盖 missing baseline（真实 IPC `ok→changed→deleted→missing` 通过；独立变异回退即 `Expected "missing"/Actual "error"` 变红，还原后复绿且源文件逐字节一致）；denied 退避、快照锁、wire 精确四元集合、App VM 级 Completed-only、registry exact-first/revoked fail-closed 均有代码与判别测试。独立门禁：focused 37/0/0、VM 5/0/0、real IPC 1/0/0、全量 .NET 1447/0/81/1528（干净树首跑）、pins 18/18、API PASS、check PASS、17/17 EV sha256 MATCH、SCAN-1 提交 0 域外、未 push。仅余 3 个 P3 文档/规格 nit（Handoff EV 编号与计数、I-2 冻结文案、follow-up 未具名），不影响 closeout。

SCAN-1-R2-REVIEW: APPROVE（P0=0/P1=0/P2=0/P3=3；reviewed_head 9daa94a25；delivery_head 7080167e1；AC-S1…S6 MET；AC11-1 保持 PARTIAL）
