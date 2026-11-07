---
task: FEA-11-L-S1-B-RECOVERY-REAUTH-1
title: 独立窄面复审 r2：B1 r1 返修（单源归因 / 真实 wire 断言 / P3 处置）
reviewer: fresh subagent（独立上下文；未参与实现/返修/r1 复核/scope review；除本报告外只做经备份并按字节恢复的复跑）
session: 8df55bef-e035-4161-ba9e-4474c2806227
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: subagent
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
reviewed_head: e9e1132a55d8a04617b7e69e9f93f043e08f450b
reviewed_evidence_head: 5dd6f7bb5ca99aea800c057a107f1d08d55f3d7c
verdict: approved
---

# FEA-11-L-S1-B-RECOVERY-REAUTH-1 独立窄面复审 r2

> **审查对象**：卡 `doc/tasks/FEA-11-L-S1-B-RECOVERY-REAUTH-1.md`；r1 `doc/reviews/FEA-11-L-S1-B-RECOVERY-REAUTH-1-r1.md`；Handoff `doc/handoffs/FEA-11-L-S1-B-RECOVERY-REAUTH-1-e9e1132a5.md`；证据 `verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/**`；代码/测试 `SourceRecoveryModels.cs`、`SourceImportModels.cs`、`HostController.cs`、`ImportDockViewModel.cs`、`SourceRecoveryUiTests.cs`、`FakeHostController.cs`、`SourceRecoveryIpcTests.cs`。
> **事实口径**：实现/测试字节以 **delivery head `e9e1132a5`**（fix `019feeb6e` + test `e9e1132a5`）为准；卡/Handoff/证据以 **docs head `5dd6f7bb5`** 为准；审查时 `main` HEAD `5dd6f7bb5`，工作树 clean。r1 基线 `0fdde2de8`/`710e749a9` 只用于差异对照。
> **只读/复跑声明**：本审查在仓库内新增的唯一字节是本报告；审查开始时工作树 clean。审查末尾共享工作树出现**非本审查产生的未提交**代码/测试/证据日志变更（见 §6.7），本审查未触碰/恢复/提交它们；除此以外未改实现/测试/契约/卡/证据，未 `git add`/`commit`/`push`，未写 `verification/FEA-09/**`。

## 0. 结论先行

**verdict：`approved`。P0 = 0 / P1 = 0 / P2 = 1 / P3 = 3（含 r1 R-P3-02 未完全关闭）。**

1. **R-P2-01 的安全核心已关闭**：恢复面从「全部选中」改为**单源归因**（`SourceImportCoordinator.LastPlanFailureSource` → `SourceRecoveryCoordinator.AttributeFailedSource`）；多源目标在 `DiagnoseAsync`/`ReauthorizeAsync` 中先于任何 wire 调用被拒绝；健康兄弟源零撤销/零注册有判别测试。我独立把恢复改回「全部选中」后，`Reauthorize_RefusesABatchBeforeAnyWireCall` **RED**，随后按原字节恢复并复核 sha256。
2. **但歧义分支的 UI 提示未落地（新 R2-P2-01，P2）**：`HostController` 对「多选且无法归因」pin 的是 **空 targets + `ambiguous=true`**；`DiagnoseAsync` 的第一个守卫是 `targets is not { Count: > 0 } → NotApplicable`，在检查 `ambiguous` 之前就返回，因此**永远到不了 `MultipleSources`**。卡/Handoff/limitation 承诺的「请只选择一个来源重新预览」在实际歧义路径不会出现。该路径仍零写、零撤销/零注册，不破红线，故为 P2 非阻断。
3. **R-P2-02 已关闭**：恒空的 `pathBearingCommands` 与「仅 RegisterSourceReadGrant」措辞已删除；改为 wire **77 帧、fixture 根路径 0 命中、`[REDACTED]` 帧 7**、quarantine 0、stderr 0 的可观测断言。我独立复跑 gated IPC，canonical `ipc-closed-loop.{json,txt}` 字节**完全一致**；并直接检查了本轮 wire 文件：77 行、根路径 0 命中、7 行 `[REDACTED]`、0 quarantine。
4. **P3 处置大体完成**：folder 双层拒绝、View 按钮直驱、`RecoveryOutcomeText` 清空、gated fixture skip 不启 Core、P3-03/11 limitation、P3-05 部分修复接受，均已核实。**仍有证据口径残留**：卡 AC-LSB-8 行仍写 34/1604/+34/changed=12（实际 43/1613/+43/27），scope 快照时间早于最终 docs commit，卡内全量测试命令仍写仓库根 `NewManga.sln`。均为 P3。
5. **安全红线不回归**：R-1/R-2/R-3/R-4 全部 PASS；Host/CoreClient/`IHostController.cs`/Core/contracts 零 diff；`HostCommandRegistry.All.Count == 111`；无新命令/码/字段。
6. **独立实跑**：build **0/0**；定向 `SourceRecovery` **43/0/0**；gated IPC **1/0/0**；定向 pytest **74 passed**；pins **18/18**；check（默认 + `-TaskPath`）**PASS(3w)×2**；API inventory **EXIT=0**。全量 pytest/.NET 我**未重跑**（Lead/交付日志交叉核对：3317/10、1613/0/93）。
7. **证据**：EV **14/14 sha256 全部匹配**；`discrimination.log` 5/5 记录与交付字节哈希一致（B5 我独立复跑）；scope 变更 **27 ALLOWED + 1 concurrent**、forbidden 0、禁止面 11 项 ZERO_DIFF、`CORE_PROTOCOL_MINOR=3`、C-16 pin `ad25fb3c89bb` 不变。

## 1. 审查基线

| 项 | 值 |
|---|---|
| 仓库/分支 | `G:\CODEX\New Manga` / `main` |
| 审查时 HEAD | `5dd6f7bb5ca99aea800c057a107f1d08d55f3d7c`（docs/evidence） |
| delivery head | `e9e1132a55d8a04617b7e69e9f93f043e08f450b`（fix `019feeb6e` + test `e9e1132a5`） |
| r1 基线 | `0fdde2de8953ffcfd847471fdf8c6d82bf507257` / docs `710e749a96789c2aaa8bbc1d6fc8b61ad68655af` |
| 工作树 | 审查开始 clean；结束时有并发未提交代码/测试/证据日志改动（非本审查，见 §6.7） |
| 契约 | C-16 仍 **v1.4**（pin `ad25fb3c89bb`）；`CORE_PROTOCOL_MINOR=3`；C-15/C-17/C-07 字节零 diff |
| 命令面 | `HostCommandRegistry.All.Count == 111`；无 recover/reauthor 命令；4 条既有 root 命令不变 |
| 写域 | 交付 diff（`e0b37622b..5dd6f7bb5`）28 路径 = 27 交付/证据 + 1 并发 docs（`ac528828b` 的 `doc/handoffs/DSH-PROGRESS-2026-11-07.md`） |

## 2. A–F 逐项核对

### A. R-P2-01 关闭与单源归因：**PASS（安全核心）/ FAIL（歧义 UI 提示）**

| 检查 | 判定 | 证据 |
|---|---|---|
| 单源归因 | **PASS** | `SourceImportCoordinator.LastPlanFailureSource` 在每个 source 的 `IssueGrantsAsync` 抛 typed 失败时记录**那一个** source（`SourceImportModels.cs:604-610`、`:623-643`）；`HostController.PinPendingSourceRecovery` 用 `AttributeFailedSource(sources, failedSource)` 只 pin 唯一 target（`HostController.cs:1645-1662`、`:1467`）；`Diagnose/Reauthorize` 只接收该 target（`:1667-1678`、`:1681-1705`）。 |
| 批量拒绝 | **PASS** | `DiagnoseAsync` 对 `targets.Count > 1` 返回 `MultipleSources`，在探针之前（`SourceRecoveryModels.cs:354-357`）；`ReauthorizeAsync` 对 `targets.Count > 1` 返回 `INVALID_REQUEST`，在任何 wire 调用之前（`:414-418`）。测试 `Reauthorize_RefusesABatchBeforeAnyWireCall`（`SourceRecoveryUiTests.cs:465`）通过，`host.Frames` 为空。 |
| 歧义拒绝 | **FAIL（UI 提示）** | `AttributeFailedSource` 在 `failed == null && selected.Count > 1` 时返回 **空 targets + Ambiguous=true**（`SourceRecoveryModels.cs:306-321`）；`HostController` 原样保存（`HostController.cs:1657-1659`）并传给 `DiagnoseAsync`（`:1676-1678`）。但 `DiagnoseAsync` 先执行 `targets is not { Count: > 0 } → NotApplicable`（`SourceRecoveryModels.cs:347-351`），**排在 `ambiguous` 检查之前**，因此空 targets 的歧义路径返回 `BlockReason=None`，VM 不会显示 `MultipleSourcesOffer()`。我的运行时复现：`production-mapping: targets=0 ambiguous=True` → `production-mapping-diagnosis: action=None block=None hasAction=False code=SOURCE_REGISTRY_UNAVAILABLE`；对照 `batch-two` → `block=MultipleSources`。该分支仍是零 wire、零动作（安全），故列为新 **R2-P2-01（P2）**。 |
| 健康兄弟零撤销/零注册 | **PASS（协调器级）** | `AttributedFailure_LeavesTheHealthySiblingCompletelyUntouched`（`SourceRecoveryUiTests.cs:485`）只撤销失败源、健康源 `Revoked=false`、generation 不变、wire 帧不出现健康 registry id；`AttributeFailedSource_TargetsOnlyTheFailingSource_AndNeverABatch`（`:425`）钉住「只取失败源」。生产 `HostController` 端到端仍无测试（r1 P3-05，登记接受）。 |
| 无任意路径入参（冻结端口） | **PASS** | `ISourceImportController` 三个恢复成员只收 `CancellationToken`/`bool`（`SourceImportModels.cs:86-106`）；`RecoveryMembers_AcceptNoPathOrOpaqueSourceArgument`，43 例实跑通过。**注**：`SourceRecoveryCoordinator` 的公开方法接收 `SourceRecoveryTarget(Path, IsFolder)`（App 内部编排值），但注册始终使用条目**已登记**的 `roots[0]`（`SourceRecoveryModels.cs:213-226`、`:574-585`），不构成 Host 授权面扩大；该点未新增 finding。 |
| B5 判别（独立） | **PASS** | 我把 `ReauthorizeAsync` 的批量守卫改为 `targets.Skip(1)` 逐个 `ReauthorizeSingleAsync`（还原「全部选中」语义），`Reauthorize_RefusesABatchBeforeAnyWireCall` **RED**（失败 1/0/0，exit 1）；原字节恢复后 sha256 `14243C77AE6EB838992AF268D43C8E7E4E387F493C6D7DEA7530BDAE1D9919BA`（= 交付字节），rebuild 0/0，43/0/0。日志：`G:\CODEX\New Manga.workspace\FEA-11-L-S1-B-RECOVERY-REAUTH-1\review-r2\b5-discrimination.log`。 |
| 无自动重授权 | **PASS** | 失败分支只调用 `DiagnoseSourceRecoveryAsync`（`ImportDockViewModel.cs:403-405`）；`PinPendingSourceRecovery` 只存 state；`FindOrRegisterRootAsync` 无「失败换候选/重注册」回退；B1 判别见交付 `discrimination.log` B1；本次 43 例与 B5 均绿/红符合预期。 |

**A 结论**：R-P2-01 的**安全核心已关闭**（单源、批量零写、健康兄弟不动、B5 RED）；**歧义路径的 `MultipleSources` UI 提示未实现**，作为新 P2 记录，不阻断集成。

### B. R-P2-02 关闭：**PASS**

| 检查 | 判定 | 证据 |
|---|---|---|
| 删除恒空断言与旧措辞 | **PASS** | `SourceRecoveryIpcTests.cs:213-228` 已无 `pathBearingCommands`；改为 `wirePathHits == 0` + `redactedFrames > 0`；仓库当前代码/证据中无「仅 RegisterSourceReadGrant」的现行主张（仅 r1 报告/历史说明保留该词）。 |
| 真实可观测断言 | **PASS** | `wirePathHits` 同时检查 raw/escaped fixture 根路径（`:219-225`）；`redactedFrames` 检查 `[REDACTED]`（`:226`）；断言 0 命中且脱敏确实发生（`:227-228`）。 |
| `ipc-closed-loop.json` 字段一致 | **PASS** | canonical：`wire_frame_count=77`、`sanitization.wire_path_hits=0`、`wire_redacted_frames=7`、`wire_quarantine_hits=0`、`stderr_path_hits=0`（`ipc-closed-loop.json:49-55`）；EV §2/§4、Handoff §2、卡 AC-LSB-7 均使用同一组数字。 |
| 独立 wire 核对 | **PASS** | 我复跑 gated IPC 后直接读取本轮 fixture `ipc-2ceb921d.../wire.ndjson`：**77 行、fixture 根路径 0 命中、`[REDACTED]` 7 行、`quarantine` 0 行**；`core.stderr.log` 根路径/quarantine 均 0。canonical JSON/TXT 与备份 sha256 完全一致（`95288ede…`/`406f68d7…`）。 |
| 旧 P2-02 影响范围 | **PASS** | 新断言仍不能证明「脱敏前哪些帧带路径」（该事实不可观测），但证据措辞已不再声称该更强主张；AC-LSB-7 的「fixture 根路径 0 命中」成立。 |

**B 结论**：R-P2-02 **CLOSED**。

### C. P3 处置核验：**PASS（除 R2-P3-01/02/03 证据口径）**

| P3 | 核验 | 判定 | 证据/说明 |
|---|---|---|---|
| **P3-01 数字** | EV/app-unit **43**、Handoff **+43**、禁止面 **11**、Manifest **3 新增 + 6 修改** | **PASS（原引用处）** | EV §2 `:39/:43/:49`；Handoff §2 `:33/:52/:57`；Manifest `note` 与 `resources[2]`；`git diff --name-status e0b..e9`：3 A + 6 M 代码/测试。**但**卡 AC-LSB-8 行 `:85` 仍写 34/1604/+34/changed=12 → **R2-P3-01**。 |
| **P3-02 scope 快照** | scope 快照是否覆盖最终树、`changed_count` 与卡面同口径 | **OPEN/PARTIAL** | `scope-validation.log`：27 ALLOWED + 1 concurrent、forbidden=0、11 项 ZERO_DIFF；但生成时间 10:59:20 早于最终 docs commit 11:00:16，且卡 `:85` 仍写 `changed=12`；Handoff/EV 的「按最终 docs commit 重算」与时间戳不符 → **R2-P3-02**。 |
| **P3-03 revoked 行累积** | limitation 是否登记 | **PASS** | 卡 `:100`、EV §5、Handoff §3；active 恒 1 的口径已写清。 |
| **P3-04 folder** | 诊断层/动作层双层拒绝 | **PASS** | `DiagnoseAsync` 对 `target.IsFolder` 返回 `FolderUnsupported` 且不探针（`SourceRecoveryModels.cs:359-363`）；`ReauthorizeAsync` 对 folder 返回 `INVALID_REQUEST`（`:420-424`）；`FolderTarget_OffersNoAction_AndTheActionRefuses`（`SourceRecoveryUiTests.cs:515-532`）实跑绿；VM `FolderSourceBlocked_*` 显示 file-source 提示。 |
| **P3-05 HostController 接缝** | 部分修复并接受 | **ACCEPTED** | 新增 `LastPlanFailureSource` / `AttributeFailedSource` 生产代码级测试（`SourceRecoveryUiTests.cs:425/535`）；真实 controller 端到端仍需 runtime，卡 `:102`/EV §5/Handoff §3 登记接受。 |
| **P3-06 View 按钮** | 只经按钮命令驱动 | **PASS** | `View_RendersTheReauthorizeActionFromRealControls` 已删显式 VM 兜底，只 `reauthorize.Command!.Execute(null)`（`SourceRecoveryUiTests.cs:1069-1092`）；reset 同理（`:1095-1121`）；43 例绿。 |
| **P3-07 outcome 清空** | 新预览清 `RecoveryOutcomeText` | **PASS** | `ClearSourceRecoveryState` 清 `_recoveryOutcomeText`（`ImportDockViewModel.cs:661-666`）；`NewPreviewClearsThePreviousRecoveryOutcome` 绿；成功重授权在自动重预览后发布 outcome（`:581-594`）。 |
| **P3-08 构建命令** | 卡面构建命令路径 | **PARTIAL** | 卡 `:122` 的 build 已改为 `dotnet build apps/desktop-avalonia/NewManga.sln -c Release`；但同句全量测试仍写 `dotnet test NewManga.sln -c Release`（仓库根无 `NewManga.sln`）→ **R2-P3-03**。 |
| **P3-09 discrimination 日志** | 干净重跑 + 早期失败标注 | **PASS** | `discrimination.log:1-3` 头部说明；5/5 `RED_AS_EXPECTED` + 5/5 `RESTORED`；源哈希 `2134897F…`/`14243C77…` 与交付字节一致。 |
| **P3-10 gated fixture skip** | gate 关闭不启 Core | **PASS** | `InitializeAsync` 在 `NEWMANGA_FEA11_IPC != 1` 时直接返回（`SourceRecoveryIpcTests.cs:372-378`）；`DisposeAsync` 对 `Client is null` 短路（`:437-442`）；全量日志 `SourceRecoveryIpcTests... [SKIP]`。 |
| **P3-11 revoke ACK 计数** | 文案 + limitation | **PASS** | `RevokeFailedUnknownTail`（`SourceRecoveryModels.cs:175-181`）用于撤销失败；卡 `:101`/EV §5/Handoff §3 登记「已确认 N 条，实际可能多一条」。 |
| 未处置项登记 | B2/B3/L-S4-1/L-S4-2/C-17 journal/quarantine_path | **PASS** | 卡 `:90-102`、EV §5、Handoff §3 均保留；无「零交互自愈/自动恢复」承诺（仅 limitation 语境出现 L-S4-1）。 |

**C 结论**：功能/测试类 P3 基本关闭；**卡面数字与 scope 口径仍有 P3 残余**。

### D. 安全红线复核（不回归）：**PASS**

| 红线 | 判定 | 证据 |
|---|---|---|
| **R-1 不自动重授权** | **PASS** | 失败分支只读探针；`PinPendingSourceRecovery` 不写；`FindOrRegisterRootAsync` 无失败回退；B1 判别（交付日志）与 B5 独立 RED；`ReauthorizeSourceAsync` 仅在显式命令后调用。 |
| **R-2 不重建 identity** | **PASS** | `FindOrRegisterRootAsync`/`SelectReusableRoot` 语义未改（`SourceImportModels.cs:818-859`）；恢复只按条目已登记 `roots[0]` 注册，不生成新 identity。 |
| **R-3 撤销后不放行** | **PASS** | 注册失败 → `RevokedButNotRegistered`，不回滚 `revoked_at`；撤销失败 → 零注册；无自动放行/自动恢复。 |
| **R-4 不扩授权面** | **PASS** | `git diff --stat e0b37622b e9e1132a5 -- apps/desktop-avalonia/src/NewManga.Host apps/desktop-avalonia/src/NewManga.CoreClient .../IHostController.cs src tests doc/plan doc/contracts doc/STATUS.md doc/REBASELINE_PLAN.md doc/TASK_LEDGER.md .../ImportDockView.axaml.cs` **空**；`HostCommandRegistry.All.Count == 111`（43 例中的守卫通过）；无 recover/reauthor 命令；API inventory EXIT=0；`SourceRecoveryTarget` 仅 App 内部编排值，恢复成员端口仍 path-free。 |

**D 结论**：R-1…R-4 全部 PASS；未发现新的授权面/身份/自动放行回归。

### E. 独立实跑：**PASS**

| 场景 | 命令 | 实测 |
|---|---|---|
| 构建 | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` | **0 warning / 0 error，EXIT 0** |
| 定向 App | `dotnet test .../NewManga.App.Tests.csproj -c Release --filter "FullyQualifiedName~SourceRecovery"` | **43 passed / 0 failed / 0 skipped，EXIT 0** |
| gated IPC | `NEWMANGA_FEA11_IPC=1 dotnet test .../NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~SourceRecoveryIpc"` | **1 passed / 0 / 0，EXIT 0**；canonical `ipc-closed-loop.{json,txt}` 与备份字节一致（`95288ede…`/`406f68d7…`） |
| 定向 Core 回归 | `C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | **74 passed, 1 warning，EXIT 0**（10.53s） |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PIN AUDIT: PASS (all 18)，EXIT 0**；C16 `ad25fb3c89bb` |
| 治理（默认） | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS (3 warnings)，EXIT 0** |
| 治理（本卡） | `... -TaskPath doc/tasks/FEA-11-L-S1-B-RECOVERY-REAUTH-1.md` | **PASS (3 warnings)，EXIT 0** |
| API inventory | `C:/Python314/python.exe tools/generate_api_inventory.py --check` | **EXIT 0**；IHostController 54 成员、合计 61 |
| 独立 B5 | 改回「全部选中」→ 目标用例 | **RED_AS_EXPECTED（失败 1/0/0，EXIT 1）**；恢复 sha `14243C77…`，rebuild 0/0，43/0/0 |
| 歧义复现 | 临时 console（`review-r2/AmbiguousRepro`） | production-mapping `targets=0 ambiguous=True` → `block=None`；batch-two → `MultipleSources` |

**未运行（如实）**：全量 `pytest tests -q`、全量 `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` 我未重跑；交叉核对交付日志：full-pytest **3317 passed / 10 skipped**（`full-pytest.log:101`），full-dotnet **1613/0/93**（21+38+253+117+31+223+167+763 = 1613；skip 62+24+7 = 93；`full-dotnet.log`）。全量 .NET 会把 `verification/FEA-09/logs/wire-redacted.ndjson` 写脏的既有行为本次未触发（我未跑全量）；工作树最终 clean。

### F. 证据/不夸大：**PASS（带 P3 口径 residual）**

> 本节哈希/日志均取自审查时 **HEAD `5dd6f7bb5` 的已提交字节**；报告末尾出现的并发未提交改写不在本节结论内（见 §6.7）。

- **EV 逐文件 sha256**：14/14 与卡表一致：EV-01 `0b4d1a9b…`、EV-02 `95288ede…`、EV-03 `406f68d7…`、EV-04 `07761dc5…`、EV-05 `637b37ab…`、EV-06 `c6afc880…`、EV-07 `ba5ea9cf…`、EV-08 `e39aceef…`、EV-09 `73edce96…`、EV-10 `8e17edc6…`、EV-11 `ee9c7b36…`、EV-12 `deaeac42…`、EV-13 `33087a9c…`、EV-14 `1c8d5bbf…`（全部 MATCH）。
- **`discrimination.log`**：5/5 `RED_AS_EXPECTED` + 5/5 `RESTORED`（sha256 一致）+ `final_rebuild exit_code=0`；B1 的 `2134897F…` 与 B2-B5 的 `14243C77…` 均等于交付源字节；B5 我独立复跑 RED 并恢复。
- **scope**：`git diff --name-only e0b37622b 5dd6f7bb5` 28 路径 = 27 ALLOWED + 1 concurrent（`ac528828b`）；forbidden=0；11 项禁止面 ZERO_DIFF；`CORE_PROTOCOL_MINOR=3`；C-16 pin `ad25fb3c89bb` 不变；`HostCommandRegistry.All.Count=111`。
- **闭环语义**：`ipc-closed-loop.json` 的 `physical_identity_changed_new_source=true` 明示 phase A 替换=新 source；phase B 才是同 `location_id` 的 L-S4-A 原地刷新；EV/Handoff 已明示，未见「替换场景=原地刷新」表述。
- **保留项**：B2/B3、L-S4-1、L-S4-2、C-17 journal 撤销撕裂、`quarantine_path` 不展示均在卡/EV/Handoff limitation 中；无「零交互自愈/根级问题全解/自动恢复/撤销后自动放行」承诺（L-S4-1 仅在「仍开放」语境出现）。
- **附注（不阻断）**：`RESOURCE-MANIFEST.json` 的 `repo_head_at_generation=52b16bbd6` 是最终 docs commit 之前的一次 docs 提交（后由 `5dd6f7bb5` 取代），`delivery_head` 与文件哈希正确；建议下次写最终 docs head，避免读者把它误当最终 HEAD。`Handoff`/`EV` 的「NOT_RUN：无」应读作「无必需门禁未跑」；P3-05 的 HostController 接缝仍以 accepted limitation 单列，二者不矛盾但建议措辞更精确。

## 3. r1 findings 逐条状态

| r1 ID | 级别 | 状态 | 核验/残余 |
|---|---|---|---|
| **R-P2-01** | P2 | **CLOSED（安全核心；UI 残余 R2-P2-01）** | 单源归因、批量零 wire、健康兄弟零撤销/零注册、B5 RED 均成立；但歧义空 targets 的 `MultipleSources`/UI 提示未落地 → **R2-P2-01**。 |
| **R-P2-02** | P2 | **CLOSED** | 旧断言/措辞删除；新断言 0 命中 + `[REDACTED]` 帧；独立 77/0/7 与 canonical 字节一致。 |
| **R-P3-01** | P3 | **CLOSED（原引用处）** | EV/Handoff/Manifest 已改为 43/+43/11/3+6；卡 `:85` 同类数字仍旧 → **R2-P3-01**。 |
| **R-P3-02** | P3 | **OPEN** | scope 日志 27 ALLOWED 与最终路径集一致；但卡 `:85` 仍 `changed=12`，且日志时间 10:59:20 早于最终 docs commit 11:00:16，「最终 docs commit 后重算」不成立 → **R2-P3-02**。 |
| **R-P3-03** | P3 | **CLOSED** | limitation 明写 revoked 行累积、active 恒 1。 |
| **R-P3-04** | P3 | **CLOSED** | folder 诊断/动作双层拒绝 + 测试；文案改为 file-source only。 |
| **R-P3-05** | P3 | **ACCEPTED** | 生产代码级归因测试 + 真实 IPC；真实 HostController 端到端仍无测试，卡/EV/Handoff 登记接受。 |
| **R-P3-06** | P3 | **CLOSED** | 两个 View 测试只经按钮命令驱动；43 例绿。 |
| **R-P3-07** | P3 | **CLOSED** | `ClearSourceRecoveryState` 清 outcome；新预览清空测试绿。 |
| **R-P3-08** | P3 | **CLOSED（build；test cmd 残余 R2-P3-03）** | 卡 `:122` build 路径已修；同句全量 `dotnet test NewManga.sln` 仍指向不存在的根 solution → **R2-P3-03**。 |
| **R-P3-09** | P3 | **CLOSED** | discrimination 日志一次干净 5/5，头部说明早期探索性 B4；源哈希匹配。 |
| **R-P3-10** | P3 | **CLOSED** | gate 关闭 `InitializeAsync` 直接返回，`DisposeAsync` 短路；全量 skip 不启 Core。 |
| **R-P3-11** | P3 | **CLOSED** | `RevokeFailedUnknownTail` 文案 + limitation；行为保持 fail-closed 可重试。 |

## 4. 新 findings

| ID | 级别 | 位置 | 触发与影响 | 复现/证据 | 建议 |
|---|---|---|---|---|---|
| **R2-P2-01** | **P2** | `HostController.cs:1657-1659`、`:1676-1678`；`SourceRecoveryModels.cs:306-321`、`:347-357`；`ImportDockViewModel.cs:525-537` | **歧义多选路径永远不会得到 `MultipleSources` 诊断**：`AttributeFailedSource` 对「无 attribution + 多选」返回空 targets + `Ambiguous=true`，`HostController` 原样传入；`DiagnoseAsync` 先判 `targets.Count == 0` 返回 `NotApplicable`，VM 的 `BlockReason` 为 `None`，因此卡/Handoff/limitation 承诺的「请只选择一个来源重新预览」不会显示。该路径仍零 wire、零撤销/零注册，不破 R-1/R-4，故非阻断。 | 运行时复现：`production-mapping: targets=0 ambiguous=True` → `production-mapping-diagnosis: action=None block=None hasAction=False code=SOURCE_REGISTRY_UNAVAILABLE`；对照 `batch-two` → `block=MultipleSources`。生产可达性：`SourceReadCoordinator.cs:651` 的 `plan_import_references` null response 抛 `SourceAccessException("SOURCE_REGISTRY_UNAVAILABLE")`，在 per-source loop 之外，故 `failed=null`。现有测试 `MultiSelectionBlocked_Shows...` 直接脚本化 diagnosis，`MultiSelectionBlocked_Offers...` 直接传 2 targets，均未覆盖该生产路径。 | 将 `ambiguous` 检查移到 `targets.Count == 0` 之前（在 `hostSideMintFailure` 闸门之后），使空 targets + ambiguous 返回 `MultipleSources`；增加「空 targets + ambiguous=true」单测与 `HostController` pin 路径测试。 |
| **R2-P3-01** | P3 | `doc/tasks/FEA-11-L-S1-B-RECOVERY-REAUTH-1.md:85` | **卡 AC-LSB-8 证据行仍是首轮数字**：`logs/app-unit.log` 写 34（实际 43）、`full-dotnet` 1604/0/93（实际 1613/0/93）、`+34`（实际 +43）、`scope changed=12`（实际 27）。与卡自身 r1 记录 `:134`（43/1613/5/5）及 canonical 日志矛盾，误导复现。 | 实测 43/0/0；full-dotnet 汇总 1613/0/93；scope `changed_count=27`；卡 `:85` 原文。 | 改为 43 / 1613 / +43 / changed=27；保留首轮 `34/1604/+34` 只在 `:122` 的首轮记录中出现。 |
| **R2-P3-02** | P3 | `verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/scope-validation.log:2`、`:31`；`doc/handoffs/...-e9e1132a5.md:57`；`doc/tasks/...:85` | **scope 快照与「最终 docs commit 后重算」不一致**：日志生成于 `10:59:20`，最终 docs commit `5dd6f7bb5` 为 `11:00:16`；卡仍写 `changed=12`，而日志是 `27 ALLOWED + 1 concurrent`。路径集本身与最终树一致（27/1/0），实质归属结论不变，但证据时间/口径不自洽。 | 日志第 2 行时间戳；final commit `%ci`；`changed_count=27`；卡 `:85`。 | 在最终 docs commit 后重跑 scope 并更新卡面为 27（或明确 12 是「不含 review/evidence 的交付子集」口径）；Handoff 去掉「最终 docs commit 后」的绝对表述。 |
| **R2-P3-03** | P3 | `doc/tasks/FEA-11-L-S1-B-RECOVERY-REAUTH-1.md:122` | **卡内全量测试命令仍指向仓库根不存在的 solution**：`dotnet test NewManga.sln -c Release`；仓库根 `Test-Path NewManga.sln = False`，实际为 `apps/desktop-avalonia/NewManga.sln`。r1 P3-08 只修了同句的 build 命令。 | `Test-Path` 结果；卡 `:122`；Handoff/EV 的正确命令。 | 改为 `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` 或注明在 `apps/desktop-avalonia` 下执行。 |

> **不列入 finding 的观察**：`SourceRecoveryTarget` 是公开 record 且带 `Path`，但它是 App 内部编排值，冻结端口 `ISourceImportController` 仍 path-free，注册只用条目已登记 root，不构成 R-4 扩大；建议后续把 target 收 internal 或补一条「coordinator 不接收任意未登记路径」的守卫。`Handoff`/`EV` 的「NOT_RUN：无」与 P3-05 accepted limitation 的措辞歧义，不单独计 finding。

## 5. 最终 verdict

- **`approved`**：P0=0 / P1=0；核心安全（单源归因、批量/歧义零写、健康兄弟不动、不自动重授权、不扩授权面）成立；P2 仅 **R2-P2-01（歧义 UI 提示）**，非阻断；P3 为证据口径/命令路径残余。
- **建议 closeout 前处置**（不要求返修本卡实现即可集成；若 Lead 要求证据零残留，建议同批修文档）：
  1. **R2-P2-01**：调整 `DiagnoseAsync` 守卫顺序，补空 targets + ambiguous 测试；或至少把 limitation 改为「歧义时只有通用失败提示，不显示单选引导」，不要声称 `MultipleSources` 已生效。
  2. **R2-P3-01/02/03**：更新卡 `:85` 数字、`changed=27`、scope 时间/口径说明、全量测试命令路径。
- 若 Lead 认为「歧义提示」属于本卡承诺必须修复，可按 **changes_requested（仅 R2-P2-01）** 处理；本 Review 不自行改实现。

## 6. 真实性声明

1. 本报告由**独立上下文 fresh subagent** 产出（session `8df55bef-e035-4161-ba9e-4474c2806227`，父会话 `session-5f1e719c-f1f3-4193-8393-caf4d0936e4a`），**未参与** `FEA-11-L-S1-B-RECOVERY-REAUTH-1`（含 B1）的实现、返修、r1 复核或 scope review。
2. 代码/测试事实来自 `e9e1132a5` 字节；卡/Handoff/证据事实来自 `5dd6f7bb5` 字节；未把卡面/Handoff 自述当作实现事实。
3. **实跑**：build；定向 43 例；gated IPC 1 例；定向 pytest 74；pins；check 默认+TaskPath；API inventory；独立 B5（备份→RED→逐字节恢复→sha 复核→rebuild→43 绿）；歧义 production-mapping 复现。**NOT_RUN**：全量 pytest、全量 .NET（我未重跑；交付日志 3317/10、1613/0/93 仅交叉核对）。
4. **字节卫生**：B5 备份到 `.workspace/FEA-11-L-S1-B-RECOVERY-REAUTH-1/review-r2/`；B5 恢复当时 `SourceRecoveryModels.cs` sha256 `14243C77…`；gated IPC 前备份 canonical，复跑后 JSON/TXT 哈希 `95288ede…`/`406f68d7…` 与备份一致。审查开始及中途 `git status --porcelain` 均为 0 行；报告写入后发现非本审查产生的未提交代码/测试/证据日志改动（见 §6.7）。本审查未写 `verification/FEA-09/**`；`FEA-09/logs/wire-redacted.ndjson` 的 M 是并发全量 .NET 的既有写脏行为，非本审查。未触碰真实用户数据/AppData/回收站。
5. 本审查未修改任何生产代码、测试、契约、冻结记录、Task 卡、STATUS/REBASELINE_PLAN/TASK_LEDGER 或 canonical evidence 的最终字节；未执行 `git add`/`git commit`/`git push`。本审查在仓库内新增的唯一字节是本报告；工作树另有非本审查的并发未提交变更（见 §6.7）。工作区夹具/日志/临时 console 均在 `.workspace/FEA-11-L-S1-B-RECOVERY-REAUTH-1/review-r2/` 与既有 `fixtures/`。
6. **不夸大**：本报告只确认显式、单源、file-source 同路径恢复的最小闭环；B2/B3、L-S4-1/L-S4-2、C-17 journal 撤销撕裂、`quarantine_path` 展示均保持开放/登记；不写「零交互自愈」「根级问题全解」「自动恢复/撤销后自动放行」。
7. **并发工作树披露**：本审查开始时工作树 clean；报告写入后（11:26:43 起）共享工作树出现**非本审查产生的未提交变更**：`SourceRecoveryModels.cs`（`ambiguous` 守卫重排 + r2 P2-01 注释，sha256 `8E0F3414…`，mtime 11:28:30）、`SourceRecoveryUiTests.cs`（+109 行，mtime 11:27:32），`verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/logs/{app-unit,build,discrimination,feature,host-ipc}.log`（并发复跑，mtime 11:28:49–11:29:02），以及 `verification/FEA-09/logs/wire-redacted.ndjson`（并发全量 .NET 的既有写脏行为）。`git status --porcelain` 最终为：8 个并发 `M` + 本报告 `??`。本审查未触碰、未恢复、未提交这些文件；被审 head 仍是 `e9e1132a5`，HEAD 仍是 `5dd6f7bb5`，上述未提交变更不进入本报告结论。**仅作观察**：对 `SourceRecoveryModels.cs` 候选做只读 build + 同一歧义 repro，`ambiguous-empty` 与 `production-mapping` 均变为 `block=MultipleSources`（日志 `review-r2/ambiguous-repro-after-concurrent-fix.log`）——这只说明候选可修此点；候选未提交、测试/证据正在并发改动、未跑全量，不能据此批准。若它是 Lead 的修复尝试，需要另行提交 + 测试/证据 + 新 head 复审（r3）。
