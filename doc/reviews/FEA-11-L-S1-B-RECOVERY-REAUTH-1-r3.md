---
task: FEA-11-L-S1-B-RECOVERY-REAUTH-1
title: 独立窄面复审 r3：B1 r2 返修（歧义提示可达性 / 零 wire / P3 残留）
reviewer: fresh subagent（独立上下文；未参与实现/返修/r1/r2 复核/scope review；只读 + 经备份并按字节恢复的复跑）
session: 2e178b6d-36a3-4cf0-9ab2-723d8d691851
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: subagent
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
reviewed_head: 80d2799de
reviewed_evidence_head: 8a249538a
verdict: approved
---

# FEA-11-L-S1-B-RECOVERY-REAUTH-1 独立窄面复审 r3

> **审查对象**：r2 报告 `doc/reviews/FEA-11-L-S1-B-RECOVERY-REAUTH-1-r2.md`（approved，P0=0/P1=0/P2=1/P3=3）；卡 `doc/tasks/FEA-11-L-S1-B-RECOVERY-REAUTH-1.md`（r2 处置段、AC-LSB-8、limitation）；Handoff `doc/handoffs/FEA-11-L-S1-B-RECOVERY-REAUTH-1-80d2799de.md`；证据 `verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/**`；代码/测试 `SourceRecoveryModels.cs`、`HostController.cs`、`ImportDockViewModel.cs`、`SourceRecoveryUiTests.cs`。
> **事实口径**：实现/测试字节以 **delivery head `80d2799de`**（fix `f1272f29a` + test `80d2799de`）为准；卡/Handoff/证据以 **docs/evidence head `8a249538a`** 为准；审查开始时 `main` HEAD `8a249538a`、工作树 clean。r1 基线 `0fdde2de8`/`710e749a9`、r2 基线 `e9e1132a5`/`5dd6f7bb5` 只用于差异对照。
> **只读/复跑声明**：本审查在仓库内新增的唯一字节是本报告；未改实现/测试/证据/卡/契约，未 `git add`/`commit`/`push`，未写 `verification/FEA-09/**`。破坏性复跑前备份、变红后按原字节恢复并复核 sha256；gated IPC 复跑前备份 canonical `ipc-closed-loop.{json,txt}`，复跑后逐字节恢复。夹具在 `G:\CODEX\New Manga.workspace\FEA-11-L-S1-B-RECOVERY-REAUTH-1\review-r3\`。

## 0. 结论先行

**verdict：`approved`。P0 = 0 / P1 = 0 / P2 = 0 / P3 = 3（均为非阻断的证据/清单记数残留）。**

1. **R2-P2-01 已关闭（核心）**：`DiagnoseAsync` 的歧义判定已移到「空 targets」守卫**之前**（`SourceRecoveryModels.cs:357-368`，位于 `hostSideMintFailure` 闸门之后）；`HostController` 对「多选且无法归因」pin 的 **0 targets + `ambiguous=true`** 现在返回 `MultipleSources`，VM 的 `HasSourceRecoveryHint`/`RecoveryOfferText` 可见「请只选择一个来源重新预览…」，视图 `IsVisible` 绑定该属性；该分支仍**零 wire/零撤销/零注册**；非歧义空列表仍 `NotApplicable`（反向用例）。
2. **判别性 B6 独立成立**：我把守卫顺序改回「空 targets 先判」后，目标用例 `AmbiguousBatchWithNoTargets_StillReturnsTheSingleSelectionHint_AndNeverProbes` **RED**（1 failed / 0 passed / 0 skipped，EXIT 1）；按原字节恢复（sha256 `8E0F3414…` 复核）并强制全量重编后定向 **47/0/0**。
3. **r2 P3 残留已关闭**：卡 AC-LSB-8 已是实测 **47 / 0 / 0、3317/10、1617/0/93、+47（+1 opt-in skip）**；scope 快照按最终交付树重算为 **29 ALLOWED + 1 concurrent、forbidden=0、changed_count=29**，与 `git diff --name-only e0b37622b 8a249538a` 的 30 路径逐项一致，并发披露保留；卡内全量命令已是 `apps/desktop-avalonia/NewManga.sln`。
4. **无回归/红线保持**：R-1（不自动重授权）、R-2（不重建 identity）、R-3（撤销后不放行/fail-closed）、R-4（不扩授权面）仍成立；Host/CoreClient/`IHostController.cs`/`src`/`tests`/`doc/plan`/`doc/contracts`/STATUS/REBASELINE_PLAN/TASK_LEDGER/`ImportDockView.axaml.cs` **零 diff**；`HostCommandRegistry.All.Count == 111` 守卫实跑通过；无新命令/错误码/字段；r1/r2 已 CLOSED 项无回退。
5. **独立实跑**：build **0/0**；定向 `SourceRecovery` **47/0/0**；gated IPC **1/0/0**（wire **77** 帧、根路径 **0** 命中、`[REDACTED]` **7** 帧、quarantine **0**、stderr **0**）；定向 pytest **74 passed**；pins **18/18**（C-16 pin `ad25fb3c89bb` 不变）；check（默认 + `-TaskPath`）**PASS(3w)×2**；API inventory **EXIT=0**。全量 pytest **3317/10**、全量 .NET **1617/0/93** 由交付日志交叉核对（我未重跑）。
6. **证据**：EV **14/14 sha256 全部匹配**卡表；交付 `discrimination.log` **6/6 RED_AS_EXPECTED + 6/6 RESTORED**（含 B6；我独立复跑 B6）；scope 的 `CORE_PROTOCOL_MINOR=3`；B2/B3/L-S4-1/L-S4-2/C-17/quarantine 保留；无「自动恢复/零交互自愈」承诺。
7. **新 P3（非阻断）**：EV.md 三处仍写旧 `delivery_head=e9e1132a5` 且 AC 矩阵残留 1613；`RESOURCE-MANIFEST.json` 的 `repo_head_at_generation` 指向一个未进入 main 的 pre-amend docs commit、且仍有旧 head/5 破坏点字样；`discrimination.log`/`discrimination.ps1` 头部仍写 5 个破坏点（实跑 6）。均为证据/清单记数，不影响产品语义、门禁或安全结论。

## 1. 审查基线

| 项 | 值 |
|---|---|
| 仓库/分支 | `G:\CODEX\New Manga` / `main` |
| 审查时 HEAD | `8a249538a2f7ed632426d1adf388fbb52fd1bbda`（docs/evidence） |
| delivery head | `80d2799de7195ccdec6954b523eea6830f315335`（fix `f1272f29a` + test `80d2799de`） |
| r1 基线 | `0fdde2de8953ffcfd847471fdf8c6d82bf507257` / docs `710e749a96789c2aaa8bbc1d6fc8b61ad68655af` |
| r2 基线 | `e9e1132a55d8a04617b7e69e9f93f043e08f450b` / docs `5dd6f7bb5ca99aea800c057a107f1d08d55f3d7c` |
| 工作树 | 审查开始时 clean；审查末尾出现 **3 个 Lead 并发 docs `M`**（`doc/STATUS.md`、`doc/TASK_LEDGER.md`、本卡）+ 本报告 `??`；这些并发改动非本审查产生、未进入本报告结论（见 §6.7） |
| 契约 | C-16 仍 **v1.4**（pin `ad25fb3c89bb`）；`CORE_PROTOCOL_MINOR=3`；C-15/C-17/C-07 字节零 diff |
| 命令面 | `HostCommandRegistry.All.Count == 111`（守卫实跑通过）；无 recover/reauthor 命令 |
| 写域 | 交付 diff（`e0b37622b..8a249538a`）30 路径 = **29 ALLOWED + 1 concurrent**（`ac528828b` 的 `doc/handoffs/DSH-PROGRESS-2026-11-07.md`）；forbidden=0 |

## 2. A–E 逐项核对

### A. R2-P2-01 关闭：**PASS / CLOSED**

| 检查 | 判定 | 证据 |
|---|---|---|
| 歧义判定在空 targets 守卫之前 | **PASS** | `DiagnoseAsync` 先过 `failureCode`/`hostSideMintFailure` 闸门（`SourceRecoveryModels.cs:351-355`），随后 `if (ambiguous \|\| targets is { Count: > 1 }) → MultipleSources`（`:357-363`），然后才是 `if (targets is not { Count: > 0 }) → NotApplicable`（`:365-368`）；folder 守卫在 `:371-374`。顺序与 r2 建议一致。 |
| 生产 pin 组合 | **PASS** | `HostController.PinPendingSourceRecovery` 对「无法归因 + 多选」写 `_pendingRecoveryTargets = []`、`_pendingRecoveryAmbiguous = true`（`HostController.cs:1645-1662`）；`DiagnoseSourceRecoveryAsync` 把两者一起传入 `DiagnoseAsync`（`:1667-1679`）。静态链路闭合；真实 `HostController` 端到端仍受 r1 P3-05 accepted limitation 约束（本轮未新增真实 runtime 测试）。 |
| `ambiguous=true` + 空 targets → `MultipleSources` | **PASS** | 新测试 `AmbiguousBatchWithNoTargets_StillReturnsTheSingleSelectionHint_AndNeverProbes`（`SourceRecoveryUiTests.cs:465`）同时覆盖 `targets=null` 与 `targets=[]`，断言 `BlockReason=MultipleSources`、`HasAction=false`、`IsBlocked=true`；实跑 47 例全绿。 |
| VM 提示可见、无动作 | **PASS** | VM 把 `MultipleSources` 映射为 `SourceRecoveryText.MultipleSourcesOffer()`（`ImportDockViewModel.cs:525-529`），文本含「请只选择一个来源重新预览」（`SourceRecoveryModels.cs:144-146`）；`HasSourceRecoveryHint`（`:301`）+ `RaiseRecoveryDerived` 通知；视图 `IsVisible="{Binding HasSourceRecoveryHint}"`、`Text="{Binding RecoveryOfferText}"`（`ImportDockView.axaml:119-121`）。VM 测试 `AmbiguousBatch_ReachesTheRealDiagnosis_ShowsTheHint_AndNeverTouchesTheRegistry`（`:1214`）断言 hint 可见、文本命中、`HasSourceRecoveryAction=false`、`SourceReauthorizeCalls=0`、`SourceResetCalls=0`。 |
| 仍零 wire/零撤销/零注册 | **PASS** | 歧义分支在 `ListEntriesAsync` 探针之前返回（`SourceRecoveryModels.cs:376-379` 起才是探针）；orchestrator 测试断言 `host.Frames` 为空（`:465-536`）；VM/真实协调器测试断言 dispatcher `wireCalls` 为空、端口调用 0。 |
| 非歧义空列表仍 `NotApplicable` | **PASS** | 反向用例 `AmbiguousFalseWithNoTargets_StaysNotApplicable`（`:492`）断言 `BlockReason=None`、`IsBlocked=false`、`HasAction=false`、零帧。 |
| 判别性 B6（顺序改回 → RED） | **PASS（独立）** | 我把 `SourceRecoveryModels.cs` 的两个守卫换回「空 targets 先判」→ 目标用例 **RED**（1 failed / 0 passed / 0 skipped，EXIT 1）；按备份恢复后 sha256 `8E0F34143A2E4AD54803923EE25B0EE24AD426B0FEB9F5DF9A7D13F03A534BDE` = 交付字节；强制 `--no-incremental` 重编 0/0，定向 **47/0/0** 绿。日志：`.workspace/FEA-11-L-S1-B-RECOVERY-REAUTH-1/review-r3/b6-discrimination.log`。交付 `logs/discrimination.log:24-27` 的 B6 记录与我的现象一致。 |

**A 结论**：R2-P2-01 **CLOSED**。唯一保留说明：新测试 `HostControllerAmbiguityPath_YieldsTheSingleSelectionHint_WithZeroWire`（`:510`）复用的是 `AttributeFailedSource` + `DiagnoseAsync` 两个生产调用组合，并未实例化真实 `HostController`（与 r1 P3-05 accepted limitation 一致）；生产 pin 链路已由静态代码 + 该组合测试覆盖，未被夸大。

### B. P3 残留关闭：**PASS / CLOSED**

| 检查 | 判定 | 证据 |
|---|---|---|
| 卡 AC-LSB-8 数字与实际一致 | **PASS** | 卡 `:85`：定向 `logs/app-unit.log` **47/0/0**、全量 pytest **3317/10**、全量 .NET **1617/0/93**（基线 1570/0/92，+47 本卡测试 +1 新增 opt-in skip）。交付 `app-unit.log` 实测 47；`full-dotnet.log` 汇总 21+38+253+117+31+223+167+767=**1617**、skip 62+24+7=**93**、0 failed；`full-pytest.log:101` 为 **3317 passed / 10 skipped / 11 warnings**。 |
| scope 快照按最终 docs commit 重算 | **PASS（实质）** | `scope-validation.log`：`changed_count=29 concurrent_non_delivery=1 forbidden_count=0`，29 ALLOWED + 1 CONCURRENT，11 项 ZERO_DIFF，`CORE_PROTOCOL_MINOR=3`；`changed-files.txt` 恰 29 行。我重算 `git diff --name-only e0b37622b 8a249538a` 得 30 路径，与日志的 30 条逐项一致（并发项 `doc/handoffs/DSH-PROGRESS-2026-11-07.md` 保留披露）。日志生成时间 11:35:58 早于最终 docs commit 11:36:15，但快照路径集与最终树一致（且自我包含在提交内），作为「按最终交付树重算」成立；字面「commit 后」不精确，仅记为观察。 |
| 卡内全量命令路径 | **PASS** | 卡 `:122` 的 build 与全量测试均为 `apps/desktop-avalonia/NewManga.sln`；卡内无仓库根 `NewManga.sln` 的全量测试命令。 |
| 首轮历史数字 | 观察 | 卡 `:122` 的首轮记录仍写 `changed=12`；首轮快照（`710e749a9:.../scope-validation.log`）实为 `changed_count=11`，最终为 29。该行已标注「首轮 head 实测 / r1/r2 数字见对应记录」，不影响最终 AC-LSB-8 主张，不单列 finding，建议 closeout 时标注或更正。 |

**B 结论**：r2 的三项 P3 残余（卡数字、scope 快照、卡内命令）**CLOSED**；另有 3 条新的证据/清单记数 P3 见 §4。

### C. 无回归 / 红线：**PASS**

| 红线/项 | 判定 | 证据 |
|---|---|---|
| **R-1 不自动重授权** | **PASS** | 预览失败分支只调用 `DiagnoseSourceRecoveryAsync`（`ImportDockViewModel.cs:397-407`）；`HostController` 失败 catch 只 `PinPendingSourceRecovery`（`:1448-1469`）；`ReauthorizeSourceAsync` 仅由 `ReauthorizeSourceCommand` 触发（`:92`、`:559-570`），`ConfirmResetSourceRegistryAsync` 仅由确认命令触发（`:94`、`:627`）；判别 B1 在交付日志、B5/B6 在实跑/独立复跑中保持红绿关系。 |
| **R-2 不重建 identity** | **PASS** | r2 commit 只改 `SourceRecoveryModels.cs` 守卫/注释与测试（`git diff --numstat e9e1132a5 80d2799de`：16/5 与 109/0），`SourceImportModels.cs` 零 diff；复用选择器语义沿用 r1 结论（首个非 revoked 匹配、无失败回退），未发现新 identity 生成路径。 |
| **R-3 撤销后不放行** | **PASS** | `ReauthorizeSingleAsync` 仍是「撤销全部 stale → 失败即中止零注册 → 注册失败报 `RevokedButNotRegistered` 且不回滚」，本轮无改动；47 例（含 `Reauthorize_RegisterFailure_*`、`Reauthorize_RevokeFailure_AbortsBeforeAnyRegistration`）全绿。 |
| **R-4 不扩授权面** | **PASS** | Host/CoreClient/`IHostController.cs`/`src`/`tests`/`doc/plan`/`doc/contracts`/STATUS/REBASELINE_PLAN/TASK_LEDGER/`ImportDockView.axaml.cs` 全部 ZERO_DIFF（`git diff --name-only e0b37622b 8a249538a -- <path>` 空）；`HostCommandRegistry.All.Count == 111` 守卫在 47 例中通过；恢复成员仍只在 `ISourceImportController` 且只收 `bool`/`CancellationToken`；无新命令/错误码；API inventory EXIT=0。 |
| **r1/r2 CLOSED 项不回退** | **PASS** | P2-02 可观测断言仍在（`SourceRecoveryIpcTests.cs:213-230`：`wirePathHits==0` + `redactedFrames>0`），gated 实跑 77/0/7；P3-04 folder 双层拒绝仍在（`SourceRecoveryModels.cs:371-374`、`:432-435`；`FolderTarget_OffersNoAction_AndTheActionRefuses` 绿）；P3-06/07/10/11 的相关代码/测试未被 r2 改动（测试文件 109 行纯新增、0 删除；P3-11 文案在 `SourceRecoveryModels.cs` 中未变），P3-10 gate 关闭仍 `InitializeAsync` 直接返回（`SourceRecoveryIpcTests.cs:373-380`）；P3-03/05 limitation 仍在卡/EV/Handoff。 |

**C 结论**：R-1…R-4 全部保持；无新授权面/身份/自动放行回归；已关闭项未回退。

### D. 独立实跑：**PASS**

> 所有命令在 `G:\CODEX\New Manga` 实跑；日志在 `.workspace/FEA-11-L-S1-B-RECOVERY-REAUTH-1/review-r3/`。

| 场景 | 命令 | 实测 |
|---|---|---|
| 构建 | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` | **0 warning / 0 error，EXIT 0** |
| 定向 App | `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj -c Release --filter "FullyQualifiedName~SourceRecovery"` | **47 passed / 0 failed / 0 skipped，EXIT 0** |
| gated 真实 IPC | `NEWMANGA_FEA11_IPC=1 dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~SourceRecoveryIpc"` | **1 passed / 0 / 0，EXIT 0**；新夹具 `ipc-3be0c172…`：wire **77** 行、fixture 根路径 **0** 命中、`[REDACTED]` **7** 行、quarantine **0**、stderr 根路径 **0**；重跑产出的 canonical `ipc-closed-loop.{json,txt}` 与备份 sha256 **完全一致**（`95288ede…`/`406f68d7…`），已按备份逐字节恢复并复核 |
| 定向 Core 回归 | `C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | **74 passed, 1 warning，EXIT 0**（7.37s） |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PIN AUDIT: PASS (all 18)，EXIT 0**；C16 `ad25fb3c89bb` |
| 治理（默认） | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS (3 warnings)，EXIT 0** |
| 治理（本卡） | `... -TaskPath doc/tasks/FEA-11-L-S1-B-RECOVERY-REAUTH-1.md` | **PASS (3 warnings)，EXIT 0** |
| API inventory | `C:/Python314/python.exe tools/generate_api_inventory.py --check` | **EXIT 0** |
| 独立 B6 | 改回「空 targets 先判」→ 目标用例 | **RED（1 failed / 0 passed / 0 skipped，EXIT 1）**；恢复 sha `8E0F3414…`；强制 `--no-incremental` rebuild 0/0；定向 **47/0/0** |
| 全量交叉核对（未重跑） | 交付 `logs/full-pytest.log` / `logs/full-dotnet.log` | pytest **3317 passed / 10 skipped**（`:101`）；.NET 汇总 **1617 passed / 0 failed / 93 skipped**（21+38+253+117+31+223+167+767） |

**D 结论**：本卡要求的所有门禁均独立通过；全量两套与交付日志交叉核对一致（我未重跑全量，未把未跑项写成 PASS）。

### E. 证据/不夸大：**PASS（带 3 条 P3 记数残留）**

- **EV 逐文件 sha256**：14/14 与卡表一致（EV-01 `47718379…`、EV-02 `95288ede…`、EV-03 `406f68d7…`、EV-04 `78dea3f0…`、EV-05 `807d02f7…`、EV-06 `635cf1f0…`、EV-07 `1910f19a…`、EV-08 `e8dbe3b2…`、EV-09 `9566604c…`、EV-10 `fab572f3…`、EV-11 `d323976a…`、EV-12 `5a871cfe…`、EV-13 `f999eb39…`、EV-14 `145f01e5…`，全部 MATCH）。
- **判别性**：交付 `logs/discrimination.log` **6/6 `RED_AS_EXPECTED` + 6/6 `RESTORED`**（sha256 一致）+ `final_rebuild exit_code=0`，含 **B6**；我独立复跑 B6 得 RED 并恢复；B1/B2/B5 的现代码哈希（`2134897F…`/`8E0F3414…`）与交付字节一致，B3/B4 未独立重跑（静态核对交付日志与实现）。
- **scope ⊆ allowed_paths**：29 ALLOWED 全在卡 `allowed_paths`（含本报告类 `doc/reviews/...-*.md`）；1 项并发 `ac528828b` 显式标注；禁止面 11 项 ZERO_DIFF；`CORE_PROTOCOL_MINOR=3`；C-16 pin `ad25fb3c89bb` 不变；C-15/C-17 字节零 diff。
- **保留项**：B2/B3、L-S4-1、L-S4-2、C-17 journal 撤销撕裂、`quarantine_path` 不展示均在卡/EV/Handoff limitation；无「零交互自愈/根级问题全解/自动恢复/撤销后自动放行」承诺；替换场景未被称作原地刷新（phase A 新 source、phase B 才是 L-S4-A 原地刷新）。
- **P3 记数残留（不影响上述结论）**：见 §4 的 R3-P3-01/02/03。

**E 结论**：证据主体、哈希、判别性、scope、红线均 PASS；另有 3 条非阻断的文档/清单记数不一致。

## 3. r2 findings 逐条状态

| r2 ID | 级别 | 状态 | 核验 |
|---|---|---|---|
| **R2-P2-01** 歧义提示不可达 | P2 | **CLOSED** | 歧义判定先于空 targets 守卫；`ambiguous=true` + 空 targets → `MultipleSources`；VM hint 可见且零动作；零 wire/零撤销/零注册；反向空列表仍 `NotApplicable`；B6 独立 RED 并恢复。 |
| **R2-P3-01** 卡 AC-LSB-8 数字残留 | P3 | **CLOSED** | 卡 `:85` 改为 47/1617/+47；日志交叉一致；首轮历史行（`:122`）保留 34/1604/+34（已标注首轮 head）。 |
| **R2-P3-02** scope 快照早于最终 docs commit | P3 | **CLOSED（实质）** | `changed_count=29`、29 ALLOWED + 1 concurrent、forbidden=0、11 ZERO_DIFF；与最终树 30 路径逐项一致；并发披露保留。快照时间早 17s 但路径集一致，字面「commit 后」记为观察。 |
| **R2-P3-03** 卡内全量命令路径 | P3 | **CLOSED** | 卡 `:122` 已统一 `apps/desktop-avalonia/NewManga.sln`；仓库根无 `NewManga.sln` 的测试命令残留。 |

## 4. 新 findings

| ID | 级别 | 位置 | 事实与影响 | 证据 | 建议 |
|---|---|---|---|---|---|
| **R3-P3-01** | P3 | `verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/EV.md:24`、`:39`、`:105`、`:85` | EV 仍有 r1 残留：§1 标题、§2 标题、§6.1 真值声明写 `delivery_head=e9e1132a5`（本 head 是 80d2799de）；AC-LSB-8 行写「全量 .NET 1613/0/93」，而 §2/卡/Handoff/`full-dotnet.log` 是 **1617/0/93**。会让读者把 r2 门禁数字误归到 r1 head，并在 1613/1617 之间产生歧义。不影响日志原始字节与卡面结论。 | EV 原文行号；`full-dotnet.log` 汇总 1617；`app-unit.log` 47；卡 `:85` 1617。 | 将三处 head 改为 `80d2799de`，AC 矩阵 1613→1617；或明确标注该行为 r1 历史数字。 |
| **R3-P3-02** | P3 | `verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/RESOURCE-MANIFEST.json:7`、`:12`、`:33`、`:8` | `repo_head_at_generation=75c4679cc` 是一个**未被任何分支引用的同消息中间 docs commit**（其父也是 `80d2799de`，最终 docs head 是 `8a249538a`；形态上是后者的 pre-amend 版本）；`resources[0].source_path` 仍写「delivery head e9e1132a5」；children 注记仍写「5 个破坏点（B1..B5）」（现为 6 个，B6 备份存在）；note 仍写「including the r1 fix round」（本 head 含 r2 返修）。资源清单为 EV-14，读者按该 head 无法复现最终树。 | `git show -s 75c4679cc`（parents=80d2799de，ci 11:35:52）、`8a249538a`（ci 11:36:15）；`git branch --contains 75c4679cc` 空；`tmp/discrimination/B6_*.orig` 存在。 | 改为 `8a249538a`（最终 docs head）与 `80d2799de`；破坏点 5→6；note 写 r2。 |
| **R3-P3-03** | P3 | `verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/logs/discrimination.log:1`；`.workspace/.../tools/discrimination.ps1:6-7` | 日志/脚本头部仍写「final clean run; **5 destructive cases**」/「final 5 cases」，但 B6 已加入且日志实际有 6 个 case（`SUMMARY cases=6 failures=0`，B6 在第 24 行）。属记数文案残留，不影响 6/6 判别结果。 | `discrimination.log:1`、`:24-29`；脚本头部原文。 | 头部改为 6 cases（含 B6），保持一次干净重跑声明。 |

> **观察（不单列 finding）**：卡 `:122` 首轮历史记录 `changed=12` 与首轮快照 `changed_count=11` 不一致（已标注首轮 head，最终 AC-LSB-8 无此数字）；Handoff/卡「scope 按最终 docs commit 后重算」的快照时间早于 commit 17s，但路径集与最终树完全一致；`HostControllerAmbiguityPath_*` 是两调用组合测试而非真实 `HostController` runtime（r1 P3-05 accepted limitation）。上述均不影响本卡结论。

## 5. 最终 verdict

- **`approved`**：P0=0 / P1=0 / P2=0 / P3=3（均为证据/清单记数，非阻断）。
- **R2-P2-01 CLOSED**：歧义提示可达、仍零 wire、反向用例与 B6 判别成立；这是 r2 唯一 P2 的核心关闭。
- **R2-P3-01/02/03 CLOSED**：卡面数字、最终 scope 快照、卡内全量命令均已处置。
- **安全/红线**：R-1…R-4 保持；Host/CoreClient/`IHostController`/Core/契约零 diff；命令面 111 不变；无新码；r1/r2 CLOSED 项无回退；独立 build/47/1/74/pins/check/API/B6 全部符合。
- **建议**：本卡可进入集成/closeout；R3-P3-01/02/03 建议在 closeout 同一文档批修正（不要求返修实现，不影响本 verdict）。无需下一步代码返修。

## 6. 真实性声明

1. 本报告由**独立上下文 fresh subagent** 产出（session `2e178b6d-36a3-4cf0-9ab2-723d8d691851`，父会话 `session-5f1e719c-f1f3-4193-8393-caf4d0936e4a`），**未参与** `FEA-11-L-S1-B-RECOVERY-REAUTH-1`（含 B1）的实现、返修、r1/r2 复核或 scope review；除本报告外全程只读（破坏性复跑均备份并按字节恢复）。
2. 代码/测试事实来自 `80d2799de` 字节；卡/Handoff/证据事实来自 `8a249538a` 字节；未把卡面/Handoff 自述当作实现事实。审查开始时 `main` HEAD `8a249538a`、工作树 clean；审查末尾出现 Lead 并发 docs 修改（见 §6.7），未进入本报告结论。
3. **实跑**：build；定向 47；gated IPC 1；定向 pytest 74；pins 18/18；check 默认+`-TaskPath`；API inventory；独立 B6（备份→改回顺序→RED→按字节恢复→sha256 复核→强制 `--no-incremental` 重编 0/0→47 绿）；scope 重算；EV 14 文件哈希；判别性日志与 wire 夹具核对。**NOT_RUN**：全量 pytest（3317/10）、全量 .NET（1617/0/93）我未重跑，仅按交付日志汇总交叉核对；B1/B2/B3/B4/B5 未独立重跑（r1/r2 已覆盖 B1/B2/B5；B3/B4 静态核对交付日志/实现）；真实 `HostController` runtime 端到端未跑（r1 P3-05 accepted limitation）。
4. **字节卫生**：B6 备份 `review-r3/backup/SourceRecoveryModels.cs`，原始 sha256 `8E0F34143A2E4AD54803923EE25B0EE24AD426B0FEB9F5DF9A7D13F03A534BDE`；变异后 `B1E0ADE3…` → RED；恢复后复核回 `8E0F3414…`。**注意**：首次仅 `Copy-Item` 恢复时源文件 mtime 回退到 11:28:30（早于 11:47:33 的 DLL），默认增量构建未重编，3 个歧义用例短暂失败；随后 `dotnet build --no-incremental` 强制重编（0/0），47/0/0 全绿。gated IPC 前备份 canonical `ipc-closed-loop.{json,txt}`，复跑后字节完全一致，仍按备份恢复并复核 `95288ede…`/`406f68d7…`。审查开始时 `git status --porcelain` 0 行；结束时为 3 个 Lead 并发 `M`（STATUS/TASK_LEDGER/卡）+ 本报告 `??`（见 §6.7）；未写 `verification/FEA-09/**`；未触碰真实用户数据/AppData/回收站。
5. 本审查未修改任何生产代码、测试、契约、冻结记录、Task 卡、STATUS/REBASELINE_PLAN/TASK_LEDGER 或 canonical evidence 的字节；未执行 `git add`/`git commit`/`git push`。仓库内唯一新增字节是本报告；夹具/备份/日志在 `.workspace/FEA-11-L-S1-B-RECOVERY-REAUTH-1/review-r3/` 与 `fixtures/`。
6. **不夸大**：本报告只确认显式、单源、file-source 同路径恢复的最小闭环；B2/B3、L-S4-1/L-S4-2、C-17 journal 撤销撕裂、`quarantine_path` 展示均保持开放/登记；不写「零交互自愈」「根级问题全解」「自动恢复/撤销后自动放行」。
7. **并发工作树披露**：本审查开始时工作树 clean。审查末尾（约 11:55:12–11:55:15）共享工作树出现**非本审查产生的** 3 个未提交 docs 修改：`doc/STATUS.md`（1/1）、`doc/TASK_LEDGER.md`（6/7）、`doc/tasks/FEA-11-L-S1-B-RECOVERY-REAUTH-1.md`（49/5，含 `status: done`、`integration_commit=80d2799de`、Closeout Record 与 Canonical Evidence 重排）。这些是 Lead 的 closeout 并发编辑，本审查**未触碰/未恢复/未提交**，也不把它们当作本报告的事实来源；本报告所有卡/EV/Handoff 行号引用均针对**已提交 docs head `8a249538a`**。被审实现/测试仍是 `80d2799de`，HEAD 仍是 `8a249538a`；上述未提交改动不改变 §0–§5 的任何结论。若 Lead 的 closeout 提交改写了卡/证据字节，本报告的 R3-P3-01/02/03 仍以 `8a249538a` 的 EV/Manifest/discrimination 字节为准。
