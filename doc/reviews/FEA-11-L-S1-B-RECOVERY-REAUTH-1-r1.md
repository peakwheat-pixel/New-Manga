---
task: FEA-11-L-S1-B-RECOVERY-REAUTH-1
title: 独立实现 Review r1：App 显式恢复/重授权入口（B1；App-only、零契约）
reviewer: fresh subagent（独立上下文；未参与本卡实现/返修/scope review；只读）
session: 84562d6a-dd69-4f34-8300-cbbb30a2667b
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: subagent
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
reviewed_head: 0fdde2de8953ffcfd847471fdf8c6d82bf507257
reviewed_evidence_head: 710e749a96789c2aaa8bbc1d6fc8b61ad68655af
verdict: approved
---

# FEA-11-L-S1-B-RECOVERY-REAUTH-1 独立实现 Review r1

> **审查对象**：卡 `doc/tasks/FEA-11-L-S1-B-RECOVERY-REAUTH-1.md`；scope review `doc/reviews/FEA-11-L-S1-B-RECOVERY-REAUTH-1-scope-r1.md`；Handoff `doc/handoffs/FEA-11-L-S1-B-RECOVERY-REAUTH-1-0fdde2de8.md`；证据 `verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/**`。
> **事实口径**：实现/测试字节以 `0fdde2de8`（实现 `be3b0c242` + 测试 `0fdde2de8`）为准；卡/Handoff/证据以 `710e749a9` 为准。审查时 `main` HEAD `710e749a9`（docs-only 冻结提交），工作树 clean；`0fdde2de8` 之后源码/测试字节无变化，卡/Handoff/证据由 `710e749a9` 冻结。
> **只读声明**：本报告是本次审查唯一写入的仓库文件；未改实现/测试/证据/卡/契约，未 `git add`/`commit`/`push`。

## 0. 结论先行

**verdict：`approved`。P0 = 0 / P1 = 0 / P2 = 2 / P3 = 11（全部非阻断）。**

1. **安全核心成立**：恢复只从两个用户显式命令进入；预览失败分支只做一次**只读** `source_list_roots` 探针（`SourceRecoveryModels.cs:251-281`、`:425-431`），不 revoke/register/reset；`FindOrRegisterRootAsync` 的选择器抽出为纯函数、语义逐字不变，没有“mint 失败就重注册/换候选”的回退（`SourceImportModels.cs:830-859`、`:799-820`）。我的独立破坏点 B1（把恢复挂进失败分支）与 B2（只撤首条）均 RED，随后按原字节恢复并 sha 复核。
2. **顺序/幂等/部分失败符合 AC**：同路径全部 stale 非撤销条目先撤销（generation+1、`revoked_at`），再按条目**自己的** `roots[0]` 注册一次；撤销失败即中止、零注册；注册失败报告「已撤销、未重新授权」+ typed 码、不回滚、可重试；重复执行保持恰好 1 条 active（`SourceRecoveryModels.cs:297-384`、`SourceRecoveryUiTests.cs:237-403`）。
3. **授权面/脱敏成立**：恢复成员无任意路径/registry_id 入参；`IHostController.cs`/Host/CoreClient/Core/契约零 diff；`HostCommandRegistry.All.Count == 111`；App 内 `source_revoke_root`/`source_reset_registry` 的运行时调用只出现在恢复编排（`SourceRecoveryModels.cs:436`、`:408`）；`quarantine_path` 不被读取/渲染；gated IPC 的 wire/stderr 对 fixture 根路径 0 命中。
4. **独立实跑全部符合**：build 0 warning/0 error；定向 `SourceRecovery` **34/0/0**；gated 真实 IPC **1/0/0**（重跑产出的 `ipc-closed-loop.{json,txt}` 与 canonical 字节**完全一致**，sha256 `7dd15bd1…`/`edfae3e8…`）；定向 pytest **74 passed**；全量 pytest **3317/10**；全量 .NET **1604/0/93**；pins **18/18**；`check.ps1` 默认 + `-TaskPath` **PASS(3 warnings)**；API inventory **EXIT=0**。
5. **证据/门禁一致**：EV 14 个文件逐文件 sha256 全部匹配卡表；`discrimination.log` 最终块 **4/4 RED_AS_EXPECTED + 4/4 RESTORED**；scope 的 26 个交付路径中 25 个在 `allowed_paths` 内、1 个为已披露的并发 docs 提交（`ac528828b`），禁止面零 diff、`CORE_PROTOCOL_MINOR=3`、C-16 pin `ad25fb3c89bb` 不变。
6. **两个 P2（非阻断，建议 closeout 前处置）**：
   - **R-P2-01 多选导入的恢复面过宽/归因错误**：`HostController` 在预览失败时 pin 的是**全部选中** sources（`:1647`），诊断按全部选中路径挑选、用 `stale[0]` 的叶子名作为「该来源」（`SourceRecoveryModels.cs:277-280`），动作会撤销/重注册**所有选中路径**的匹配条目（`:336-378`）。单选（卡面全部测试场景）正确；多选时可能把健康源命名为失败源，并对其做无专门披露的撤销/重注册。
   - **R-P2-02 gated IPC 的「含路径帧仅 RegisterSourceReadGrant」断言空转**：`WireLog.Add` 在存帧前把所有绝对路径重写为 `[REDACTED]`（`WireLog.cs:84-88`、`:139-140`），所以 `SourceRecoveryIpcTests.cs:217-227` 的 `pathBearingCommands` 恒为空、`Assert.All` 恒过；`ipc-closed-loop.json` 的 `wire_path_frames_only_register_grant=true` 及 EV/Handoff/卡面的「含路径帧仅 RegisterSourceReadGrant」与事实不符。**真正被验证且成立的是**：wire 中 fixture 根路径 0 命中（77 行实跑 wire，0 路径命中，7 行 `[REDACTED]`）。AC-LSB-7 的 0 命中要求仍成立，问题在证据措辞与一个空转断言。
7. **P3 主要是文档/证据口径与测试强度**：EV 写 app-unit 33（实际 34）、Handoff 写 +33（实际 +34）与禁止面 10（实际 11）、Manifest 写「2 新增 + 7 修改」（实际 3 新增 + 6 修改）；scope 快照生成于卡面最终编辑之前（`changed_count=11` vs 卡面 12）；重复恢复会累积 revoked 行而 limitation 未登记；folder 根也会进入同一恢复面而文案写「仅限 file-source」；真实 `HostController` 恢复接缝无测试；View 按钮测试二次调用 VM 方法掩盖接线判别；`RecoveryOutcomeText` 在新预览时不清空；卡面构建命令路径写错；`discrimination.log` 含较早 B4 `INVALID_BUILD_FAILED` 未标注；gated fixture 在 skip 时仍启动真实 Core（沿用 FEA-09 既有模式）；revoke ACK 失败时 App 撤销计数可能少算一条。

## 1. 审查基线

| 项 | 值 |
|---|---|
| 仓库/分支 | `G:\CODEX\New Manga` / `main` |
| 审查时 HEAD | `710e749a96789c2aaa8bbc1d6fc8b61ad68655af`（docs-only 冻结：卡 + Handoff + 证据） |
| 任务起点/实现起点 | 卡 `base_commit=3d97e3b18`；实现起点 `e0b37622b` |
| delivery head | `0fdde2de8953ffcfd847471fdf8c6d82bf507257`（实现 `be3b0c242` + 测试 `0fdde2de8`） |
| 工作树 | 审查开始/结束均 clean；源码/测试字节等于 `0fdde2de8` |
| 契约 | C-16 still **v1.4**（pin `ad25fb3c89bb`）；C-15/C-17/C-07 零 diff；`CORE_PROTOCOL_MINOR=3` |
| 写域 | 交付 diff：9 个 `apps/desktop-avalonia/**` 文件 + 卡 + Handoff + 14 个证据文件；另 1 个并发 docs 提交 `ac528828b`（非本卡） |

## 2. A–G 逐项核对

### A. 入口仅显式（AC-LSB-1/5）：**PASS**

- **静态**：`PlanReferencedImportAsync` 的 catch 只做 `SetLastError` 与 `PinPendingSourceRecovery`（`HostController.cs:1454-1468`），不调用任何 Host 命令；`PinPendingSourceRecovery` 只记录 App 自己的选中路径与失败码（`:1636-1650`）。VM 失败分支只调用 `DiagnoseSourceRecoveryAsync`（`ImportDockViewModel.cs:394-403`）；诊断只调用 `source_list_roots`（`SourceRecoveryModels.cs:425-431`）；两个写动作仅由 `ReauthorizeSourceCommand`/`ConfirmResetSourceRegistryCommand` 触发（`ImportDockViewModel.cs:92-94`）。
- **测试**：`FailedPreview_ExplicitReauthorize_OnlyOffersThatOneAction_AndWritesNothingYet` 断言失败后 `SourceRecoveryDiagnoseCalls=1`、`SourceReauthorizeCalls=0`、`SourceResetCalls=0`、`SourceResetConfirms` 为空（`SourceRecoveryUiTests.cs:739-764`）；`FailedPreview_FileLevel_*`、`FailedPreview_OtherTypedCode_*` 同样零写（`:766-794`）。
- **真实 IPC**：失败后 `registry_unchanged_after_failure=true`（`SourceRecoveryIpcTests.cs:80-85`）。
- **判别性**：我独立把 `ReauthorizeSourceAsync` 挂进 VM 的预览失败分支，目标用例 RED（§4）。
- **选择器语义**：`SelectReusableRoot` 是原循环的逐字抽取（`SourceImportModels.cs:830-859`），`FindOrRegisterRootAsync` 仅在无复用条目时走正常的显式注册腿（`:799-820`）；`ReuseSelector_StillSkipsRevokedEntries_AndNeverFallsBackOnAFailedMint`（`SourceRecoveryUiTests.cs:107-130`）与源码守卫 `PlanAndMintPath_NeverInvokesARecoveryCommand_OnlyTheExplicitActionDoes`（`:87-105`）钉住。**未发现“失败即自动重授权/换候选”路径。**
- **保留**：多选导入的过宽问题见 R-P2-01；真实 `HostController` 接缝无测试见 R-P3-05。

### B. 分流（AC-LSB-2）：**PASS**

- `DiagnoseAsync` 先用失败码 + Host 侧铸造失败 + 非空选中路径做闸门（`SourceRecoveryModels.cs:251-262`），再做只读探针；探针 typed `SOURCE_REGISTRY_UNAVAILABLE` → 只给 Reset（`:269-275`）；探针成功且有 stale → 只给 Reauthorize（`:277-280`）；其它探针码 → `NotApplicable` 并显示该码（`:271-275`）；探针成功但无 stale → 无动作（`:278-280`）。**文件级只给重置、根级只给重授权、其它码只显示码** 三条均落地。
- **测试**：`FileLevelProbeFailure_OffersResetOnly_AndWritesNothing`、`OtherProbeCode_OffersNoRecoveryAction_AndDisplaysOnlyThatCode`（实跑 `CORE_CAPABILITY_MISSING`/`SOURCE_REGISTRY_BUSY`）、`CoreSideFailureOrAnotherPreviewCode_OffersNothing_AndNeverProbes`、`ReadableStorageWithStaleEntries_OffersReauthorizeOnly_WithLeafNameAndCount`、`ReadableStorageWithoutAnyStaleEntry_OffersNothing`（`SourceRecoveryUiTests.cs:152-232`）；VM 三例失败分支（`:739-794`）。
- `CoreSideFailureOrAnotherPreviewCode...` 断言 `host.Frames` 为空 —— 非 Host 铸造失败/其它码时连探针都不打，符合 scope review 的「Core 侧失败不探针」。
- **保留**：多选时 `stale[0]` 可能不是真正失败的源（R-P2-01）。

### C. 顺序/幂等/部分失败（AC-LSB-3/4）：**PASS**

- **顺序**：先对 `SelectStaleEntries` 的全部条目逐个 `source_revoke_root`，全部成功后才进入 `roots` 去重注册循环（`SourceRecoveryModels.cs:335-378`）；撤销异常在注册循环之前返回（`:336-350`），**零注册**。
- **注册目标**：每个 distinct 已登记 root 一次（`StringComparer.OrdinalIgnoreCase`，`:355-360`），payload 用条目自己的 `roots[0]`（`SourceRecoveryPayloads.RegisterRoot`，`:161-170`）；有测试 `Reauthorize_UsesTheRegisteredRootString_NotTheCallerSpelling`。
- **幂等**：重复执行时第二次会撤销它自己刚创建的那 1 条 active，再注册 1 条，active 恒 1（`Reauthorize_RepeatedExecution_KeepsExactlyOneActiveEntry`，`:292-311`）；**但不是严格无副作用幂等**——每次重复都会新增一条 revoked 行（见 R-P3-03）。
- **部分失败**：注册失败返回 `RevokedCount>0, RegisteredCount=0` 的 `RevokedNotRegistered` 消息 + typed 码，不回滚 `revoked_at`，测试继续可重试并成功（`Reauthorize_RegisterFailure_ReportsRevokedNotReauthorized_WithNoRollback`，`:315-345`）；retry 腿从已撤销条目的 root 补注册（`Reauthorize_PartialOutcomeRetry_FinishesTheRegisterLegFromTheRevokedRoot`，`:380-403`）；撤销失败即中止、无注册（`:347-361`）。
- **真实 IPC**：2 条条目场景在 orchestration 测试里覆盖；IPC 覆盖 1 条 stale → gen+1、恰 1 条 active（`SourceRecoveryIpcTests.cs:106-113`）。

### D. 授权面/脱敏（AC-LSB-6/7）：**PASS（带证据措辞 P2）**

- **无路径入参**：`ISourceImportController` 三个恢复成员只有 `CancellationToken`/`bool`（`SourceImportModels.cs:76-105`）；反射测试 `RecoveryMembers_AcceptNoPathOrOpaqueSourceArgument`（`SourceRecoveryUiTests.cs:49-65`）。
- **不在冻结面**：`RecoveryMembers_LiveOnTheSeparatePort_AndNeverOnTheFrozenHostController`（`:36-47`）；`IHostController.cs` 对 `be3b0c242`/`0fdde2de8`/`710e749a9` 零 diff；`HostCommandRegistry.All.Count == 111` 由 `RecoverySurface_AddsNoWireCommand_AndKeepsTheFrozenCommandCount` 钉住（`:67-85`，实跑通过），无 recover/reauthor 命令；`generate_api_inventory.py --check` EXIT=0。
- **脱敏**：恢复文本只由叶子名/typed 码/计数构成（`SourceRecoveryModels.cs:92-136`）；`quarantine_path` 在 Reset 响应里**不被读取**（`:405-417` 的注释与实现）；VM 全文本断言 `C:\manga` 与 `quarantine` 0 命中（`SourceRecoveryUiTests.cs:713-724`、`:760-764`、`:875-890`）；`Reset_RequiresConfirmation_AndNeverSurfacesTheQuarantinePath` 的脚本响应**故意带** quarantine path（`:539-540`、`:632-640`）。
- **gated IPC**：wire/stderr 对 fixture 根路径 0 命中（`SourceRecoveryIpcTests.cs:192-234`；我实跑 77 行 wire：0 路径命中、7 行 `[REDACTED]`；stderr 0 命中）。
- **保留**：R-P2-02 的「含路径帧仅 RegisterSourceReadGrant」措辞与空转断言；R-P3-04 的 folder 边界。

### E. 独立实跑：**PASS**

| 场景 | 命令 | 结果 |
|---|---|---|
| 构建 | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` | **成功 0 warning / 0 error，EXIT 0** |
| 定向 App | `dotnet test .../NewManga.App.Tests.csproj -c Release --filter "FullyQualifiedName~SourceRecovery"` | **34 passed / 0 failed / 0 skipped**（534 ms） |
| gated IPC | `NEWMANGA_FEA11_IPC=1 dotnet test .../NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~SourceRecoveryIpc"` | **1 passed / 0 / 0**（846 ms）；`ipc-closed-loop.{json,txt}` 重跑字节与 canonical **完全一致**（sha256 `7dd15bd1…`、`edfae3e8…`） |
| 定向 Core 回归 | `C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | **74 passed, 1 warning**（10.36s） |
| 全量 Python | `C:/Python314/python.exe -m pytest tests -q` | **3317 passed / 10 skipped / 11 warnings**（262.17s，EXIT 0） |
| 全量 .NET | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` | **1604 passed / 0 failed / 93 skipped**（程序集汇总 21+38+253+117+31+223+167+754 = 1604；skip 0+0+0+0+0+62+24+7 = 93） |
| 治理 | `verify_pins.ps1` / `check.ps1`（默认 + `-TaskPath`）/ `generate_api_inventory.py --check` | **18/18 PASS** / **PASS(3 warnings) ×2** / **EXIT=0** |

- **运行卫生**：全量 .NET 会把 `verification/FEA-09/logs/wire-redacted.ndjson` 写脏（既有测试行为），我立即 `git checkout -- verification/FEA-09`，`git status --porcelain` 归零；gated IPC 运行前我把 canonical `ipc-closed-loop.{json,txt}` 备份到 `.workspace/FEA-11-L-S1-B-RECOVERY-REAUTH-1/review-backup/`，运行后哈希与备份一致（仍按备份恢复并复核），最终卡表内 sha 不变。
- **注意**：卡面构建命令写的是仓库根 `dotnet build NewManga.sln -c Release`，仓库根没有 `NewManga.sln`（实际在 `apps/desktop-avalonia/NewManga.sln`）；Handoff/EV 用的是正确路径。见 R-P3-08。
- **未运行/未覆盖**：真实 `HostController` 恢复接缝（无测试，见 R-P3-05）；多选/ folder 恢复场景（无测试，见 R-P2-01/R-P3-04）；本节未把未跑项写成 PASS。

### F. 证据/判别性：**PASS（带 P2/P3 口径）**

- **EV 逐文件 sha256**：14/14 与卡表一致（EV-01 `8d41ea51…`、EV-02 `7dd15bd1…`、EV-03 `edfae3e8…`、EV-04 `fc162b06…`、EV-05 `c32e58df…`、EV-06 `68e2148f…`、EV-07 `3ff92a94…`、EV-08 `5baa9dde…`、EV-09 `c57a3df1…`、EV-10 `dde96fff…`、EV-11 `e75b4792…`、EV-12 `de0fdf85…`、EV-13 `2a42faac…`、EV-14 `b74a38da…`）。
- **`logs/discrimination.log`**：最终块 **4/4 RED_AS_EXPECTED + 4/4 RESTORED（sha256 一致）+ final rebuild EXIT 0**；`SourceRecoveryModels.cs` 最终块前后 sha `2FA1CB98…` 与交付字节一致，VM 文件 `B222C10F…` 与交付字节一致。**注意**：日志是 append 的，第一块有 B4 `INVALID_BUILD_FAILED`（较早的开发迭代），EV/卡面只写 4/4；最终块有效，见 R-P3-09。
- **`ipc-closed-loop.json`**：闭环真实——phase A 同路径替换 → typed 失败 → 显式重授权（revoked=1/registered=1）→ 再预览成功 → 重新导入 Completed → `source_list_scan_targets` 返回新 registry/gen；phase B 同物理身份 + 新 registry 的 L-S4-A 原地刷新（同 `location_id`、registry 换新、`last_verified_at` 非空）。EV/Handoff 明示 phase A 是**新 source**、phase B 才是原地刷新，未夸大。
- **scope**：交付 diff 26 个路径（9 code/test + 卡 + Handoff + 14 证据 + 1 并发 docs）中 25 个在 `allowed_paths` 内；唯一不在的是已披露的 `ac528828b`（Lead docs-only，非本卡字节）。禁止面 `apps/desktop-avalonia/src/NewManga.Host/`、`NewManga.CoreClient/`、`IHostController.cs`、`src/`、`tests/`、`doc/plan/`、`doc/contracts/`、`STATUS.md`、`REBASELINE_PLAN.md`、`TASK_LEDGER.md`、`ImportDockView.axaml.cs` 全部零 diff；`CORE_PROTOCOL_MINOR=3`；C-16 pin `ad25fb3c89bb` 不变；`HostCommandRegistry.All.Count=111`。
- **保留**：R-P2-02 的 wire-path 措辞；R-P3-02 的 scope 快照（`changed_count=11` vs 卡面 12）；R-P3-01 的数字不一致。

### G. 不夸大：**PASS**

- 卡/Handoff/EV 明写只承诺 **file-source 同路径恢复**；folder（L-S4-2）、L-S4-1（零交互恢复枚举）、B2（roots 可用性投影）、B3（扫描侧投影）、`quarantine_path`、C-17 journal 撤销撕裂均保留/仅登记（卡 `:90-97`、Handoff `:65-72`、EV `:72-79`）。
- 证据中没有「零交互自愈」「根级问题全解」「自动恢复/撤销后自动放行」承诺；phase A 未被称作原地刷新。
- **保留**：folder 实际会进入同一恢复面而文案写「仅限 file-source」（R-P3-04）；重复恢复的 revoked 行累积未登记（R-P3-03）。

## 3. AC-LSB-1…10 判定

| AC | 判定 | 依据（关键证据）与保留 |
|---|---|---|
| **AC-LSB-1 入口仅显式** | **MET** | 失败分支仅只读探针；VM 计数 0；IPC `registry_unchanged_after_failure=true`；我 B1 破坏点 RED。保留：多选过宽 R-P2-01；真实 controller 接缝 R-P3-05。 |
| **AC-LSB-2 分流正确** | **MET** | 探针 UNAVAILABLE → 只 Reset；探针成功 + stale → 只 Reauthorize；其它码 → 无动作只显示码；Core 侧失败不探针（`SourceRecoveryUiTests.cs:152-232`、`:739-794`）。保留：多选归因 R-P2-01。 |
| **AC-LSB-3 顺序/幂等** | **MET** | 帧序 `list→revoke×2→register`、两条 stale 均 gen+1/revoked、恰 1 条 active、无关路径不动、重复执行恒 1 active；用条目自己的 root（`SourceRecoveryUiTests.cs:237-311`）。保留：revoked 行累积未登记 R-P3-03。 |
| **AC-LSB-4 部分失败 fail-closed** | **MET** | 注册失败 → `RevokedButNotRegistered` + typed、无回滚、可重试；撤销失败中止零注册；retry 补注册（`:315-403`）。保留：revoke ACK 失败计数少算 R-P3-11（边缘）。 |
| **AC-LSB-5 不自动重授权** | **MET** | 选择器纯函数语义不变、无“失败换候选”回退；源码守卫 1×list + 1×register + 0 revoke/reset；`Reauthorize_WithNothingToRevoke_WritesNothing`；IPC `registry_unchanged_after_failure`；B1 判别 RED。 |
| **AC-LSB-6 授权面不扩大** | **MET** | 恢复成员无路径/ID 入参；不在 `IHostController`；命令数 111；API inventory EXIT=0；Host/Core/契约零 diff（`SourceRecoveryUiTests.cs:36-85`；实测）。 |
| **AC-LSB-7 脱敏** | **MET（带证据措辞 P2）** | 文案/通知 0 绝对路径、0 quarantine；`quarantine_path` 不读不渲染；gated wire/stderr 0 路径命中（77 行 wire 实测 0 命中）。**但**「含路径帧仅 RegisterSourceReadGrant」不成立且断言空转（R-P2-02）。 |
| **AC-LSB-8 零漂移/门禁** | **MET** | build 0/0；34/0/0；gated 1/0/0；pytest 74；全量 3317/10；.NET 1604/0/93；pins 18/18；check PASS(3w)×2；API 0；scope 25/26 allowed + 1 concurrent（R-P3-01/02 为文档/快照口径）。 |
| **AC-LSB-9 闭环** | **MET** | 真实 Core stdio 闭环；phase A 新 source、phase B L-S4-A 原地刷新；我重跑证据字节一致；无夸大。 |
| **AC-LSB-10 边界/不夸大** | **MET（带 P3 保留）** | limitations 齐全（B2/B3、L-S4-1/2、quarantine、C-17）；无“自动恢复”承诺。保留：folder 文案（R-P3-04）、revoked 行累积未登记（R-P3-03）。 |

## 4. 破坏性复跑记录（独立）

> 先备份原字节到 `G:\CODEX\New Manga.workspace\FEA-11-L-S1-B-RECOVERY-REAUTH-1\review-discrimination\`，每次修改后只跑**一个**目标用例，随后按原字节恢复并复核 sha256；最后重建并重跑 34 例。日志：`G:\CODEX\New Manga.workspace\FEA-11-L-S1-B-RECOVERY-REAUTH-1\review-discrimination\discrimination.log`。

| 破坏点 | 文件/改动 | 目标用例 | 结果 |
|---|---|---|---|
| **B1（AC-LSB-1/5）** | `ImportDockViewModel.cs`：在 `await DiagnoseSourceRecoveryAsync(code)` 后追加 `await ReauthorizeSourceAsync()`（自动恢复） | `FailedPreview_ExplicitReauthorize_OnlyOffersThatOneAction_AndWritesNothingYet` | **RED_AS_EXPECTED**（test_exit=1）；恢复后 sha256 `B222C10F4F02D5EBBF9CD72D435FD8766636F3835985F0266889EF0321073B67` = 原字节 |
| **B2（AC-LSB-3）** | `SourceRecoveryModels.cs`：`foreach (var entry in stale)` → `stale.Take(1)`（只撤首条） | `Reauthorize_RevokesEverySamePathEntryFirst_ThenRegistersExactlyOnce` | **RED_AS_EXPECTED**（test_exit=1）；恢复后 sha256 `2FA1CB98E74FF2CA1DD8AD9B622966A0EFE5ECE569269EC8D461FADB9FB841CD` = 原字节 |

- 恢复后 `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` **0 warning/0 error**，定向 `SourceRecovery` **34/0/0**；`git status --porcelain` **0 行**。
- 交付的 `discrimination.log` 最终块 4/4 与我的 B1/B2 现象一致；我未重跑交付的 B3/B4，但静态检查其破坏点（顺序反转、渲染 `quarantine_path`）与交付日志一致（见 R-P3-09 的日志说明）。

## 5. Findings

| ID | 级别 | 位置 | 触发与影响 | 复现/证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| **R-P2-01** | **P2** | `HostController.cs:1647`；`SourceRecoveryModels.cs:277-280`、`:336-378`；`ImportDockViewModel.cs:499-525`；`SourceImportModels.cs:621-624` | **多选导入时恢复面过宽/归因错误**。预览在第一个失败源处中止；`PinPendingSourceRecovery` 却 pin **全部选中** sources；`SelectStaleEntries` 按任一选中路径匹配、`stale[0]` 的叶子名作为「该来源」；动作撤销/重注册**所有选中路径**的匹配条目。若同批另有一个已登记且健康的源，其条目会被当作 stale：提议可能显示**健康源**的叶子名，单击后健康源也被撤销/重注册；若该文件在点击前消失，会进入「已撤销、未重新授权」。仅影响用户自己选中的路径（不是任意路径，未破 R-1/R-4），故 P2 非阻断。 | 代码走查；34 例全部单源（`FailPreviewAsync` 只选一个源）；IPC 也只一个源；无多选测试 | 只 pin 真正的失败路径（在 `SourceImportCoordinator.PlanAsync` 内部把失败 path 带进内部异常/结果，再在 `HostController` 映射），或先把恢复限制为 `sources.Count == 1` 并在文案中不写「此来源」；至少增加多选场景测试与披露 | open（非阻断） |
| **R-P2-02** | **P2** | `SourceRecoveryIpcTests.cs:217-227`、`:271`；`WireLog.cs:84-88`、`:139-140`；EV.md:67；Handoff:31；卡:84 | **wire-path 断言空转、证据措辞与事实不符**。`WireLog.Add` 在存帧前把任何绝对路径字符串写成 `[REDACTED]`；因此 `pathBearingCommands` 恒为空，`Assert.All(pathBearingCommands, …RegisterSourceReadGrant…)` 恒过；`wire_path_frames_only_register_grant=true` 与「含路径帧仅 RegisterSourceReadGrant」不成立。**0 命中**这条 AC-LSB-7 要求本身成立（77 行 wire 实测 0 路径命中、7 行 `[REDACTED]`；stderr 0 命中），但该断言无法证明「恢复面不新增路径帧」这一更强主张。 | 我实跑 fixture `ipc-be6dff61…`：77 行 wire，`New Manga.workspace` 0 命中，`RegisterSourceReadGrant` 4 行，`[REDACTED]` 7 行；`SourceRecoveryIpcTests` 的 path-bearing 集合为空 | 把字段改为/新增 `wire_path_hits=0`（并保留 `quarantine_hits=0`）；删掉「仅 RegisterSourceReadGrant」措辞；若确要证明恢复面零路径帧，检查**脱敏前**的原始请求或 Host-local 帧（注意 Host-local root 命令本来就带 root，属 Host API 而非 Core wire） | open（非阻断） |
| **R-P3-01** | **P3** | `EV.md:32`、`:42`；Handoff `:32`、`:49`、`:53`；`RESOURCE-MANIFEST.json:52` | **证据数字自相矛盾**：EV/app-unit 写 33（实际 34）；Handoff 的 AC-LSB-8 行写「+33」而同文件测试表写「34」、全量行写「+34」；Handoff 写「禁止面 10 项」而 scope/卡面是 11 项；Manifest 写「2 新增生产/测试文件 + 7 修改」而实际是 3 新增（`SourceRecoveryModels.cs`/`SourceRecoveryUiTests.cs`/`SourceRecoveryIpcTests.cs`）+ 6 修改。不影响实测结论，但会误导复现。 | 实测 34/0/0；`logs/app-unit.log` 34；1604 = 1570 + 34；目录/文件清单 | closeout 统一改为 34、+34、11 项、3 新增 + 6 修改 | open（非阻断） |
| **R-P3-02** | **P3** | `scope-validation.log:15`；`changed-files.txt`；卡:85 | **scope 快照早于卡面最终编辑**：脚本在 10:00:25 用 `git diff e0b..HEAD` + untracked 生成，卡面（tracked ` M`）未被计入，故 `changed_count=11`；卡面随后提交（`710e749a9`）并写「changed=12 全 ALLOWED」。最终交付 diff 的 25 个路径都在 `allowed_paths` 内、禁止面零 diff，实质结论不变；只是证据数字与最终树不一致。 | `git diff --name-only e0b37622b 710e749a9` 26 个路径；`git status` 在 10:00:25 含卡面修改；`changed_count=11` | 对最终 docs commit 重算（或把 tracked modification 纳入脚本），并让卡面/Handoff/日志使用同一口径 | open（非阻断） |
| **R-P3-03** | **P3** | `SourceRecoveryUiTests.cs:292-311`；`SourceAccessRegistry.cs:100-110`；卡 `:90-97`；EV `:72-79` | **重复恢复的 revoked 行累积未登记为 limitation**。重复点击不是严格幂等：第二次会撤销上一轮 active（`RevokedCount=1`）并追加一条新行；active 恒 1，但 registry 条目数每次 +1。scope review §3.1(d) 建议把「撤销条目清理」登记为 limitation，本卡/Handoff/EV 的 limitation 列表没有这一条。 | `Reauthorize_RepeatedExecution_KeepsExactlyOneActiveEntry` 第二轮的 `RevokedCount=1/RegisteredCount=1`；registry 只置位不删除（Host 既有行为） | 在 limitation 增加「撤销条目保留、重复显式恢复会累积 revoked 行；active 恒 1」；把「幂等」口径写清为「恰 1 条 active」 | open（非阻断） |
| **R-P3-04** | **P3** | `SourceRecoveryModels.cs:463-478`；`SourceRecoveryText.ReauthorizeOffer` `:97-100`；卡 `:94`；Handoff `:71` | **folder 根会进入同一恢复面**：`SelectStaleEntries` 只按单 root 路径匹配，不区分 file/folder；folder 源失败时同样会给出「重新授权此来源」并执行撤销/再注册（授予该文件夹当前内容读权）。卡面只承诺 **file-source 同路径恢复**，文案固定写「仅限 file-source 同路径恢复」，与实际可用面不一致；L-S4-2 未修。 | 代码走查（`ReferenceImportSource.IsFolder` 只影响 import kind，不进恢复判定）；无 folder 恢复测试 | 要么在恢复面过滤 folder 根（不提供动作，保持「只承诺 file」），要么把文案与 limitation 改为「单根条目（file/folder）恢复可用，folder 身份键 L-S4-2 仍开放」；补 folder 场景测试 | open（非阻断） |
| **R-P3-05** | **P3** | `HostController.cs:1422-1470`、`:1586-1710`；`SourceRecoveryUiTests.cs`（FakeHostController）；`SourceRecoveryIpcTests.cs`（直接 `SourceRecoveryCoordinator`） | **真实 `HostController` 恢复接缝无测试**：VM 测试用 `FakeHostController`，IPC 测试直接构造 `SourceRecoveryCoordinator`，没有测试走「真实 `HostController.PlanReferencedImportAsync` 失败 → pin → `Diagnose/Reauthorize/Reset`」；`hostSideMintFailure: ex is SourceAccessException` 的映射与 pending 生命周期只经静态审查（IPC 测试确实证明了真实预览失败抛 `SourceAccessException`/`SOURCE_REGISTRY_UNAVAILABLE`）。 | 全仓测试无 `HostController` 的这些恢复方法调用；IPC 测试显式 `new SourceRecoveryCoordinator(dispatcher)` | 增加 controller 级测试（可用真实 `HostCommandDispatcher` + fake core/host-local，或集成式），至少覆盖 `SourceAccessException` vs `CoreOperationException` 的 pin 分支与 pending 清理 | open（非阻断） |
| **R-P3-06** | **P3** | `SourceRecoveryUiTests.cs:922-944`、`:946-973` | **View 按钮测试强度不足**：`View_RendersTheReauthorizeActionFromRealControls` 先 `Command.Execute` 再显式 `await viewModel.ReauthorizeSourceAsync()`；若按钮命令是 no-op，显式调用仍会完成动作并让 `SourceReauthorizeCalls=1`，测试仍绿。reset 测试的 request 按钮由确认面板可见性间接证明，但 confirm 按钮同样被显式调用兜底。 | 代码走查；fake 的 `Task.FromResult` 同步完成使显式调用兜底成立 | execute 后先断言 `HasSourceRecoveryAction=false`/offer 清空再决定是否 await；或只通过命令驱动并用 `Dispatcher.RunJobs` 完成异步 | open（非阻断） |
| **R-P3-07** | **P3** | `ImportDockViewModel.cs:641-647`、`:981`；类注释 `:47-51` | **`RecoveryOutcomeText` 在新预览时不清空**：`ClearSourceRecoveryState()` 只清 diagnosis/offer/确认态，不清 outcome；只有 `Close()` 清。成功重授权后若用户改选源并再次预览失败，旧的「已重新授权…」仍显示在新失败/新 offer 之上；类注释称「successful preview 清除」与实际不符。 | `PreviewSuccess_ClearsAStaleRecoveryOffer` 只断言 offer，未断言 outcome；`ClearSourceRecoveryState` 代码 | 在 `PlanReferenceImportAsync`/`DiagnoseSourceRecoveryAsync` 入口清 `_recoveryOutcomeText`（或明确它只在 Close 清并改注释/测试） | open（非阻断） |
| **R-P3-08** | **P3** | 卡 `:117`；Handoff `:48`/`:53` | **卡面构建命令路径错误**：`dotnet build NewManga.sln -c Release` 在仓库根不存在；实际 solution 是 `apps/desktop-avalonia/NewManga.sln`（Handoff/EV 用对）。照卡面复现会 MSB1009。 | 我实跑根路径 → `MSB1009: 项目文件不存在`；`apps/desktop-avalonia/NewManga.sln` → 成功 | 卡面改为 `dotnet build apps/desktop-avalonia/NewManga.sln -c Release`，或注明在 `apps/desktop-avalonia` 下执行 | open（非阻断） |
| **R-P3-09** | **P3** | `verification/.../logs/discrimination.log`；EV.md:39/48-55；卡:117 | **判别性日志可读性**：日志 append 了三块；第一块 B4 `INVALID_BUILD_FAILED`，最终块 4/4 `RED_AS_EXPECTED` + `RESTORED`。最终块对交付字节（`2FA1CB98…`/`B222C10F…`）有效；但 EV/卡只写「4/4」而未标注早期失败块，读者可能误读为一次通过。 | `discrimination.log` 第一块 B4 `INVALID_BUILD_FAILED`；最终块 `SUMMARY cases=4 failures=0`，`sha256` 与交付文件一致 | 在 EV/卡注明「最终块为交付字节；日志含早期 B4 构建失败迭代」或把日志按 run 分文件 | open（非阻断） |
| **R-P3-10** | **P3** | `SourceRecoveryIpcTests.cs:37`、`:367-423`、`:593-602` | **gated 测试的 fixture 在 skip 时仍启动真实 Core**：`IClassFixture<RecoveryIpcContext>` 的 `InitializeAsync` 在测试方法 skip 判定之前执行；我全量 .NET（未设 `NEWMANGA_FEA11_IPC`）日志明确 `[SKIP]`，但同时在 10:23:18 产生 3 行 wire 的 fixture `ipc-aeb9d248…`（ping/OpenHostSession/ping 正是 `InitializeAsync`）。这与 FEA-09 既有 fixture 模式一致（同一轮 10:23:14/20 也产生 FEA-09 fixture），不是 B1 新类问题；但「opt-in only」措辞不精确，若机器无 Python，skipped 用例可能因 fixture 初始化失败而变成失败。 | 全量 .NET 日志 `[SKIP]` + 10:23:18 fixture；`Fea09UiImportIpcTests` 同模式 | 在 `InitializeAsync` 先检查 `NEWMANGA_FEA11_IPC=1`，非 gate 时直接返回（或把 Core 启动移到测试方法）；卡面/Handoff 写明 fixture 行为 | open（非阻断） |
| **R-P3-11** | **P3** | `SourceReadCoordinator.cs:627-644`；`SourceRecoveryModels.cs:335-350`；C-15 v1.5 `:315` | **revoke ACK 失败时撤销计数可能少算一条**：Host 先持久化撤销（generation+1、`revoked_at`）再发 Core `RevokeSourceReadGrant` 并等 ACK；ACK 失败时 Host 抛 typed 错误，App 的 `revoked` 计数只加成功返回的条目，于是「已撤销 N 条…未能完成全部撤销」可能把已持久化撤销的那条算作未撤销。行为是 fail-closed、可重试（重试腿会补注册），只是消息计数/语义在边缘情况下不精确。 | Host 代码顺序（`Registry.Revoke` 在 `SendHostControlAsync` 之前）；C-15 §5「ACK 失败 → 返回失败但持久化状态已撤销」；现有测试的 `SOURCE_REGISTRY_BUSY` 在持久化前抛出，未覆盖该边缘 | 文案改为「至少 N 条/共 N+…」或用失败后重列确认；若保持现状，在 limitation/测试注释登记「ACK 失败 edge」 | open（非阻断） |

> **P0/P1：无。** 两个 P2 均不触及 R-1/R-2/R-3/R-4 红线（无自动恢复、无任意路径、无身份回写、无新命令/码/能力）；属于多选边缘与证据准确性问题。P3 为文档/证据口径、测试强度与后续加固项。

## 6. 最终 verdict

- **`approved`**：AC-LSB-1…10 的**产品语义**与安全核心均成立；P0=0/P1=0；P2=2、P3=11，均不阻断集成。
- 建议 Lead 在 closeout 前（不必返修实现）至少处置：
  1. **R-P2-01**：把恢复限制为单源或只 pin 真正失败路径（否则多选行为与「此来源」文案不一致）；若选择暂不修，需在 limitation 明示「多选导入时恢复动作覆盖同批全部选中路径」。
  2. **R-P2-02**：修正 `ipc-closed-loop.json` 的 `wire_path_frames_only_register_grant` 与 EV/Handoff/卡面「含路径帧仅 RegisterSourceReadGrant」；把空转断言改为真正的 0 命中断言。
  3. **R-P3-01/02/08**：修正证据数字、scope 快照口径与卡面构建命令；**R-P3-03/04** 补 limitation/文案。
- 若 Lead 认为多选问题必须在 B1 内修掉，则可按「changes_requested（仅 P2-01）」处理；本 Review 不自行改实现。

## 7. 真实性声明

1. 本报告由**独立上下文 fresh subagent** 产出（session `84562d6a-dd69-4f34-8300-cbbb30a2667b`，父会话 `session-5f1e719c-f1f3-4193-8393-caf4d0936e4a`），**未参与** `FEA-11-L-S1-B-RECOVERY-REAUTH-1`（含 B1）的实现、返修、scope review 或任何前轮审查；全程只读（除本报告）。
2. 所有代码/测试事实来自 `0fdde2de8` 字节；卡/Handoff/证据事实来自 `710e749a9` 字节；未把卡面/Handoff 自述当作实现事实（引用卡面处已标注）。
3. **实测命令**（全部真跑，除注明 NOT_RUN）：`git rev-parse HEAD`/`status`/`log`/`show`/`diff`；`dotnet build apps/desktop-avalonia/NewManga.sln -c Release`；`dotnet test ...NewManga.App.Tests.csproj -c Release --filter "FullyQualifiedName~SourceRecovery"`；`NEWMANGA_FEA11_IPC=1 dotnet test ...NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~SourceRecoveryIpc"`；`C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q`；`C:/Python314/python.exe -m pytest tests -q`；`dotnet test apps/desktop-avalonia/NewManga.sln -c Release`；`verify_pins.ps1`；`check.ps1`（默认 + `-TaskPath`）；`generate_api_inventory.py --check`；以及我自己的 2 个破坏性复跑（B1/B2）。
4. **NOT_RUN / 未覆盖**：交付 `discrimination.ps1` 的完整 4 例重跑（我独立跑了 B1/B2，B3/B4 只静态核对交付日志与实现）；多选导入恢复场景；folder 根恢复场景；真实 `HostController` 恢复接缝（无现成测试）；真实用户数据/AppData/回收站（未触碰）。
5. **字节卫生**：gated IPC 运行前备份 canonical `ipc-closed-loop.{json,txt}` 到 `.workspace/.../review-backup/`；运行后哈希与备份一致，仍按备份恢复并复核；破坏性复跑前备份原字节，每次按字节恢复并复核 sha256；最终重建 0/0、34 例全绿、`git status --porcelain` 0 行。全量 .NET 写脏的 `verification/FEA-09/logs/wire-redacted.ndjson` 已用 `git checkout -- verification/FEA-09` 恢复并复核 clean。未写 `verification/FEA-09/**` 新夹具；IPC/破坏性夹具均在 `.workspace/FEA-11-L-S1-B-RECOVERY-REAUTH-1/`。
6. **未改**任何生产代码、测试、契约、冻结记录、Task 卡、STATUS/REBASELINE_PLAN/TASK_LEDGER 或 canonical evidence 字节；未执行 `git add`/`git commit`/`git push`。仓库内唯一新增/修改字节是本报告。
7. **不夸大**：本报告不写「零交互自愈」「根级问题全解」「自动恢复/自动放行」；只确认显式、单次、file-source 同路径恢复的最小闭环，且 B2/B3、L-S4-1、L-S4-2、C-17 journal 撤销撕裂、`quarantine_path` 未展示均保持开放/登记。
