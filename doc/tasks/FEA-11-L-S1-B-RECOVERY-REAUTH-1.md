---
id: FEA-11-L-S1-B-RECOVERY-REAUTH-1
title: App 显式恢复/重授权入口（B1：撤销→再注册→重导入；零契约、App-only）
kind: implementation
governance_version: 3
status: done
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH」；权威 scope review `doc/reviews/FEA-11-L-S1-B-RECOVERY-REAUTH-1-scope-r1.md`（fresh subagent `7d2a572e-…`，**READY-WITH-UNFREEZE**；拆卡：**B1 = READY-TO-FREEZE（App-only，零契约 0/18 pins）**；B2（wire 可用性投影）/ B3（扫描侧投影）暂缓）；Codex 不可用（product limit）→ 按用户授权 ZCode 故障转移裁决（记录见卡）；DSH 裁决 D-1…D-10（见下）
suggested_owner: zcode
owner: l-s1b-impl
reviewer: 独立上下文 fresh subagent（未参与实现/返修/scope review）：r1 `84562d6a-…`（approved P0=0/P1=0/P2=2→已修）/ r2 `8df55bef-…`（approved P0=0/P1=0/P2=1→已修）/ r3 `2e178b6d-…`（**approved P0=0/P1=0/P2=0/P3=3 非阻断**；reviewed_head `80d2799de`）；报告 `doc/reviews/FEA-11-L-S1-B-RECOVERY-REAUTH-1-r{1,2,3}.md`
depends_on:
  - FEA-11-L-S1-REGISTRY-RESILIENCE-1
  - FEA-11-L-S4-LOCATION-AUTH-REFRESH-1
base_commit: 3d97e3b18
branch: null
worktree: null
integration_commit: 80d2799de7195ccdec6954b523eea6830f315335
delivery_head: 80d2799de7195ccdec6954b523eea6830f315335
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1
allowed_paths:
  - doc/tasks/FEA-11-L-S1-B-RECOVERY-REAUTH-1.md
  - doc/reviews/FEA-11-L-S1-B-RECOVERY-REAUTH-1-*.md
  - doc/handoffs/FEA-11-L-S1-B-RECOVERY-REAUTH-1-*.md
  - verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/**
  - apps/desktop-avalonia/src/NewManga.App/Services/SourceImportModels.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/SourceRecoveryModels.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/NullHostController.cs
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/ImportDockViewModel.cs
  - apps/desktop-avalonia/src/NewManga.App/Views/V2/Library/ImportDockView.axaml
  - apps/desktop-avalonia/tests/NewManga.App.Tests/SourceRecoveryUiTests.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/FakeHostController.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRecoveryIpcTests.cs
out_of_scope:
  - Host/Avalonia Host 源（`apps/desktop-avalonia/src/NewManga.Host/**`）、CoreClient、`IHostController.cs`、Core/Python
  - C-16/C-15/C-17/任何契约字节；新命令/能力/错误码/字段；C-07 inventory 变化
  - `quarantine_path`（绝对路径）展示；自动重新授权/自动重建 identity/撤销后自动放行
  - B2（`source_list_roots` 可用性投影，需 C-16 v1.5）/ B3（扫描侧投影）；folder 身份键（L-S4-2）；真实用户数据；push
---

# FEA-11-L-S1-B-RECOVERY-REAUTH-1（B1）：App 显式恢复/重授权入口

> **状态：`ready`（App-only，零契约 0/18 pins）。** 来源：`FEA-11-L-S1-REGISTRY-RESILIENCE-1` scope review B 面——恢复路径今天不存在：`source_reset_registry`/`source_revoke_root` App 侧 0 调用；被替换根同路径重导入因复用失效条目而**永久失败**。

## 来源与裁决（2026-11-07）

- 权威 scope review：`doc/reviews/FEA-11-L-S1-B-RECOVERY-REAUTH-1-scope-r1.md` → **READY-WITH-UNFREEZE**，拆卡：**B1（本卡）= READY-TO-FREEZE（App-only，零契约）**；B2（`source_list_roots` 可用性投影，C-16 v1.5，1 pin）暂缓；B3（扫描侧投影）暂缓。
- 关键事实：`source_revoke_root`/`source_register_root` 均为 C-16 v1.4 既有命令，Host handler 与 Core ACK（允许空 grant_ids）已实现，App 只是 0 接线；「撤销失效条目 → 按登记 root 再注册 → 重导入」今天即可走通；闭环依赖 L-S4 A 的原地刷新（已 done）。
- **DSH 裁决 D-1…D-10**：
  - **D-1** 拆 B1/B2/B3：**B1 本轮释放（App-only 零契约）**；B2/B3 暂缓另卡。
  - **D-2** **C-16 v1.5 版本号一次性保留**给「B2 wire 可用性投影 + L-S4-B 零交互恢复枚举」的单一批量载体（避免两卡各自宣称 v1.5）；本卡与 L-S4-B 均不得单独占用。
  - **D-3** B1 写域严格 App-only：Host/Core/契约/`IHostController` 零字节。
  - **D-4** 红线 R-1：**禁止**把 `FindOrRegisterRootAsync` 改为「mint 失败就重注册」（=自动重新授权）；AC-LSB-5 判别。
  - **D-5** Owner：采用 DSH Agent Teams teammate（`l-s1b-impl`）；ZCode 建议记为可用候选。
  - **D-6** AC 采用 AC-LSB-1…10（见下）。
  - **D-7** `source_reset_registry` 返回的 `quarantine_path` 为绝对路径，与 C-16 §7.3 冲突 → **B1 不得展示/记录/渲染**；AC-LSB-7 判别。
  - **D-8** AC-LSB-9 须有 1 条 gated 真实 IPC（闭环：typed 失败→显式重授权→再预览成功→刷新→枚举新代次）。
  - **D-9** allowed_paths 按 scope review §5.2（App 5 文件 + 2 新测试文件 + FakeHostController；不含 `IHostController.cs`）。
  - **D-10** STATUS 测试基线更新为 **3317/10、1570/0/92**（本 closeout 同批）。

## In（冻结）

1. `SourceImportModels.cs`：`ISourceImportController` 增加恢复面（探测/重授权/重置）；展示文案细化（零新码）。
2. `SourceRecoveryModels.cs`（新增）：恢复编排 + 结果模型 + 分流判定。
3. `HostController.cs`/`NullHostController.cs`：实现新成员（复用既有 `HostCommandDispatcher` 路径；不扩 `IHostController`）。
4. `ImportDockViewModel.cs` + `ImportDockView.axaml`：显式命令 + 状态 + 披露文案（脱敏）。
5. 测试：`SourceRecoveryUiTests.cs`（VM 级计数/文案/顺序/幂等/fail-closed）、`FakeHostController.cs` 扩展、`SourceRecoveryIpcTests.cs`（gated 真实 IPC 闭环）。
6. 证据/Handoff/卡面。

## Out

- Host/Avalonia Host 源、CoreClient、`IHostController.cs`、Core/Python；契约/新命令/能力/错误码/字段；`quarantine_path` 展示；自动重授权/自动重建 identity/撤销后自动放行；B2/B3；folder 身份键；真实用户数据；push。

## Acceptance Criteria（v3）

- [x] **AC-LSB-1 入口仅显式**：预览以 `SOURCE_REGISTRY_UNAVAILABLE` 失败时，只暴露「重新授权此来源」/「重置源授权存储」两个显式动作；未点击前 revoke/register/reset 调用计数均为 **0**。 证据：VM 例 `FailedPreview_ExplicitReauthorize_OnlyOffersThatOneAction_AndWritesNothingYet`（失败后仅 1 次只读探针；`SourceReauthorizeCalls=0`、`SourceResetCalls=0`、`SourceResetConfirms` 空）；真实 IPC `registry_unchanged_after_failure=true`；r1 P2-01：批量/歧义**不发探针、不给动作**（`MultiSelectionBlocked_*`）；判别性 B1/B5（恢复挂进失败分支 / 改回批量 → RED）`logs/app-unit.log`/`logs/discrimination.log`/`logs/ipc-closed-loop.json`。 <<MET>>
- [x] **AC-LSB-2 分流正确**：只读 `source_list_roots` 探针——探测抛 `SOURCE_REGISTRY_UNAVAILABLE` → 只给「重置」；探测成功 + 铸造失败 → 只给「重授权」；探测抛其它码 → 不给任何恢复动作，只显示该码。 证据：`FileLevelProbeFailure_OffersResetOnly_AndWritesNothing`、`OtherProbeCode_OffersNoRecoveryAction_AndDisplaysOnlyThatCode`（实跑 `CORE_CAPABILITY_MISSING`/`SOURCE_REGISTRY_BUSY`）、`CoreSideFailureOrAnotherPreviewCode_OffersNothing_AndNeverProbes`、`ReadableStorageWithStaleEntries_OffersReauthorizeOnly_*`、`ReadableStorageWithoutAnyStaleEntry_OffersNothing`、VM `FailedPreview_FileLevel_*`/`FailedPreview_OtherTypedCode_*`（探测码被显示、动作数 0）、`Reset_RequiresConfirmation_*`；r1 P2-01 批量/歧义 → `MultipleSources` 无动作且不探针；r1 P3-04 folder → `FolderSource` 无动作（`FolderTarget_OffersNoAction_AndTheActionRefuses`）；**r2 P2-01**：批量/歧义（HostController pin 0 targets + ambiguous=true）**仍到达** `MultipleSources` 提示（`AmbiguousBatchWithNoTargets_*`、`HostControllerAmbiguityPath_*`、VM `AmbiguousBatch_ReachesTheRealDiagnosis_*`），零 wire。 <<MET>>
- [x] **AC-LSB-3 撤销→注册顺序与幂等**：同一路径 2 条 stale 非撤销条目都被撤销（generation+1、`revoked_at` 非空），随后只新增 1 条非撤销条目；重复执行不产生重复条目。 证据：`Reauthorize_RevokesEverySamePathEntryFirst_ThenRegistersExactlyOnce`（帧序 `source_list_roots→source_revoke_root×2→source_register_root`；两条均 generation+1/revoked；恰 1 条 active；无关路径不动）、`Reauthorize_RepeatedExecution_KeepsExactlyOneActiveEntry`、`Reauthorize_UsesTheRegisteredRootString_NotTheCallerSpelling`；判别性 B2（只撤首条→RED）/B3（先注册后撤销→RED）`logs/discrimination.log`。 <<MET>>
- [x] **AC-LSB-4 部分失败 fail-closed**：撤销成功但注册失败 → 明确「已撤销、未重新授权」+ typed 码；不得显示成功、不得隐式回滚 `revoked_at`；可重试。 证据：`Reauthorize_RegisterFailure_ReportsRevokedNotReauthorized_WithNoRollback`（`RevokedButNotRegistered`、消息含「已撤销…未重新授权（SOURCE_ACCESS_DENIED）」、旧条目仍 revoked、无回滚、清除故障后重试成功）、`Reauthorize_PartialOutcomeRetry_FinishesTheRegisterLegFromTheRevokedRoot`、`Reauthorize_RevokeFailure_AbortsBeforeAnyRegistration`（撤销失败即中止、零注册）、VM `PartialFailure_ShowsRevokedNotReauthorized_AndStaysRetryable`。 <<MET>>
- [x] **AC-LSB-5 不自动重授权（安全核心）**：铸造失败后不自动注册/不自动换候选；`FindOrRegisterRootAsync` 复用选择器语义不变（首个非 revoked 匹配）。 证据：`PlanAndMintPath_NeverInvokesARecoveryCommand_OnlyTheExplicitActionDoes`（`SourceImportModels.cs` 中 `source_register_root`/`source_list_roots` 各 1 处、revoke/reset 0 处）、`ReuseSelector_StillSkipsRevokedEntries_AndNeverFallsBackOnAFailedMint`（选择器抽出为纯函数、语义逐字不变）、`Reauthorize_WithNothingToRevoke_WritesNothing`、`Reauthorize_ReadOnlyHost_WritesNothing`；真实 IPC「typed 失败后 registry 长度不变、条目仍非 revoked」；r1 P2-01：`LastPlanFailureSource` + `AttributeFailedSource` 只指向唯一失败源，批量在任何 wire 调用前被拒、健康源零撤销/零注册（`AttributedFailure_LeavesTheHealthySiblingCompletelyUntouched`）；判别性 B1/B5 `logs/discrimination.log`。 <<MET>>
- [x] **AC-LSB-6 授权面不扩大**：重授权只使用条目已登记 `roots[0]`；恢复成员**无**任意路径入参；`HostCommandRegistry.All` 数量不变；恢复成员不在 `IHostController` 上（C-07 pin 不变）。 证据：`RecoveryMembers_LiveOnTheSeparatePort_AndNeverOnTheFrozenHostController`、`RecoveryMembers_AcceptNoPathOrOpaqueSourceArgument`（参数仅 `bool`/`CancellationToken`）、`RecoverySurface_AddsNoWireCommand_AndKeepsTheFrozenCommandCount`（`HostCommandRegistry.All.Count == 111` 冻结、无 recover/reauthor 命令、4 条既有 root 命令不变）、`Reauthorize_UsesTheRegisteredRootString_NotTheCallerSpelling`；`generate_api_inventory.py --check` EXIT=0；`logs/gates-governance.log`。 <<MET>>
- [x] **AC-LSB-7 脱敏**：恢复文案/通知/日志只含叶子名/typed 码/计数；不含绝对路径/`quarantine_path`；gated IPC 断言 wire/stderr 中 fixture 根路径 0 命中。 证据：VM 全量 `AllVisibleText` 断言 `C:\manga` 0 命中 + `quarantine` 0 命中（含失败/成功/重置三态）；`Reset_RequiresConfirmation_AndNeverSurfacesTheQuarantinePath`（脚本 Host 响应**故意带** `quarantine_path` 也不得泄漏）；真实 IPC（r1 P2-02 修正为可观测断言）：wire **77 帧** fixture 根路径 **0 命中**、`[REDACTED]` 帧 **7**（证明脱敏实际发生）、`wire_quarantine_hits=0`、`stderr_path_hits=0`、恢复文案 path-free；判别性 B4（渲染 quarantine_path → RED）。 <<MET>>
- [x] **AC-LSB-8 零漂移/门禁**：Host/CoreClient/doc-plan/src 零 diff；API inventory PASS；pins 18/18；check（默认+`-TaskPath`）PASS；全量 pytest/.NET 不降（基线 **3317/10、1570/0/92**）。 证据：`logs/build.log`（0/0）、`logs/app-unit.log`（**47/0/0**）、`logs/host-ipc.log`（1/0/0）、`logs/feature.log`（74 passed）、`logs/full-pytest.log`（**3317 passed / 10 skipped** = 基线）、`logs/full-dotnet.log`（**1617 / 0 / 93** = 基线 1570/0/92 +47 本卡测试 +1 新增 opt-in skip）、`logs/gates-governance.log`（pins 18/18、check PASS(3w)×2、API EXIT=0）、`scope-validation.log`（全变更路径 ALLOWED、forbidden=0、禁止面 11 项 ZERO_DIFF；1 项并发非交付（ac528828b）显式标注、`CORE_PROTOCOL_MINOR=3`）；跑后 `git checkout -- verification/FEA-09` → CLEAN。 <<MET>>
- [x] **AC-LSB-9 闭环证据（gated 真实 IPC 1 条）**：注册→同路径替换→预览 typed 失败→显式重授权→再预览成功→重新导入后 `source_locations.registry_id/generation` 原地刷新（L-S4 A）→ `source_list_scan_targets` 返回新代次。 证据：`logs/host-ipc.log`（`NEWMANGA_FEA11_IPC=1`，PASS 1/0/0）+ `logs/ipc-closed-loop.json`/`.txt`：phase A 真实**同路径替换**（typed 失败 → 显式重授权 revoked=1/registered=1 → 再预览成功 → 重新导入 Completed → 枚举返回新 registry/gen；替换=新物理身份 → 新 source，旧行留在只读投影由 Host fail-closed 丢弃）；phase B 同物理身份 + 新 registry 的 **L-S4-A 原地刷新**（同一 `location_id`、`registry_id` 换新、`last_verified_at` 非空、枚举 gen=1）。 <<MET>>
- [x] **AC-LSB-10 边界/不夸大**：只承诺 **file-source 同路径恢复**；folder 变体受 L-S4-2、重定位走新源；L-S4-1 零交互恢复仍开放；不得写「零交互自愈/根级问题全解」。 证据：EV.md §5/§6、Handoff §3、本卡「已知 limitation」原文；明写「只承诺 file-source 同路径恢复」「L-S4-1/L-S4-2/B2/B3 保留」「C-17 journal 撤销撕裂仅登记」；未出现「零交互自愈/根级问题全解/自动恢复」承诺。 <<MET>>


## 已知 limitation（本卡）

- **B2**（`source_list_roots` 可用性投影）未做 → 多根健康/逐条管理不可见；**B3**（扫描侧投影）未做。
- **L-S4-1**（零交互自动恢复枚举，需 C-16 v1.5 批量载体）仍开放；**L-S4-2**（folder 身份键）未修。
- 只覆盖 file-source 同路径恢复；重定位（换路径）走「重新导入成新源」。
- `source_reset_registry` 的 `quarantine_path` 不展示（C-16 §7.3 冲突，未来随 UNFREEZE 澄清）。
- **同路径替换后的 Core 侧语义（如实登记）**：替换改变物理身份 → 重新导入会写**新的** `source_locations` 行（旧物理身份行仍在只读 Core 投影里，Host 调度器按撤销 registry fail-closed 丢弃）；L-S4-A 的**原地刷新**只在「同物理身份 + 新 registry」成立（gated IPC phase B 实测同一 `location_id` 刷新）。**不宣称**替换场景也算「原地刷新」。
- **C-17 journal 撤销撕裂（仅登记，不处理）**：B1 给了用户第一个撤销入口；撤销后，绑定旧 `registry_id` 的 C-17 apply/journal 重试会永久失败（锚 `HostOperationOrchestrator.cs:112-133`；scope review `:87/:249/:263`）。B1 不修复该影响面（需 B2/L-S4-B 批量设计），文案不得承诺「重试自动恢复」。
- **多选/歧义不给恢复（r1 P2-01）**：恢复面只针对**唯一失败来源**（`LastPlanFailureSource`）；一批选择若无法唯一归因，不提供动作、不探针、不写注册表，只在 UI 提示「请只选择一个来源重新预览」。
- **folder 源不给恢复（r1 P3-04）**：folder 根进入恢复面时被拒绝并给出说明（本卡只承诺 file-source；folder 身份键 L-S4-2 另案）。
- **重复显式恢复累积 revoked 行（r1 P3-03）**：registry 只置位不删除（Host 既有行为）；每次重复恢复新增一条 revoked 行 + 一条 active，**active 恒 1**（「幂等」= 恰 1 条 active，不是无副作用）。
- **revoke ACK 失败的计数口径（r1 P3-11）**：Host 先持久化撤销再等 Core ACK；ACK 失败时计数只含已确认成功的条目（文案写「已确认 N 条（实际可能多一条）」）；无回滚。
- **真实 `HostController` 恢复接缝无端到端测试（r1 P3-05，接受）**：HostController 需可启动 HostRuntime/sidecars；以生产代码级归因单测（`LastPlanFailureSource`/`AttributeFailedSource`）+ 真实 IPC 预览失败链路覆盖，pin 生命周期剩余部分由静态审查覆盖。


## 测试要求

| 场景/AC | 命令 | 预期 | 证据 |
|---|---|---|---|
| VM 级（LSB-1/2/3/4/5/7） | `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests -c Release --filter "FullyQualifiedName~SourceRecovery"` | 全绿；破坏点 RED | `logs/app-unit.log`、`logs/discrimination.log` |
| gated 真实 IPC（LSB-9） | `NEWMANGA_FEA11_IPC=1 dotnet test ... --filter "FullyQualifiedName~SourceRecoveryIpc"` | 1 passed（闭环） | `logs/host-ipc.log` |
| 门禁 | 全量 pytest/.NET、pins、check、API、scope | 不降/不漂移 | `logs/gates.log` |

## 交付记录（Owner 回填；不改 status）

- Owner：`l-s1b-impl`（DSH Agent Teams teammate；Lead `lead`）；交付日期 2026-11-07（Asia/Shanghai）。
- 起点：`e0b37622b`（`main`，工作树 clean，实测）→ **delivery_head=`0fdde2de8953ffcfd847471fdf8c6d82bf507257`**。
- commit 链（仅本卡字节，显式 pathspec；未 push、未建 worktree）：
  - `be3b0c242` — `feat(fea-11-l-s1b)`：恢复面（`SourceRecoveryModels.cs` 新增 + `ISourceImportController` 恢复成员 + `HostController`/`NullHostController` 实现）+ `ImportDockViewModel`/`ImportDockView.axaml` 两个显式动作与二次确认。
  - `0fdde2de8` — `test(fea-11-l-s1b)`：判别性恢复测试（编排级 + VM/View 级 + 冻结命令域守卫）与 1 条 gated 真实 IPC 闭环；**`delivery_head`**。
  - 文档提交（本卡 / `doc/handoffs/FEA-11-L-S1-B-RECOVERY-REAUTH-1-0fdde2de8.md` / `verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/**`）随后同批提交，均在 `allowed_paths` 内。
- **共享工作树披露**：`main` 同期由 Lead 写入 `ac528828b`（`doc/handoffs/DSH-PROGRESS-2026-11-07.md`，docs-only，非本卡字节）；本卡 scope 按**自有 commit 链**计算，禁止面零 diff。
- **门禁实测**（`delivery_head=0fdde2de8`；均真跑）：`dotnet build apps/desktop-avalonia/NewManga.sln -c Release` **成功 0 warning / 0 error**；定向 `FullyQualifiedName~SourceRecovery` **34 passed / 0 failed / 0 skipped**；gated `NEWMANGA_FEA11_IPC=1 ...~SourceRecoveryIpc` **1 passed / 0 / 0**；定向 Core 回归 `pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` **74 passed**（基线 74）；全量 `pytest tests -q` **3317 passed / 10 skipped**（= 基线）；全量 `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` **1604 / 0 / 93**（首轮 head 实测；r1/r2 返修后的实测数字见对应记录）（基线 1570/0/92：+34 本卡测试、+1 新增 opt-in IPC skip；已知 flaky `FluentResidual2VisualEvidenceTests` 未命中）；`verify_pins` **18/18 PASS**；`check.ps1`（默认 + `-TaskPath`）**PASS(3 warnings)** ×2；API inventory **EXIT=0**；scope **PASS**（changed=12 全 ALLOWED、forbidden=0、禁止面 11 项 ZERO_DIFF；1 项并发非交付（ac528828b）显式标注、`CORE_PROTOCOL_MINOR=3`）；判别性 **4/4 RED_AS_EXPECTED + 4/4 字节级 RESTORED + final rebuild EXIT 0**；跑后 `git checkout -- verification/FEA-09`（CLEAN）。
- **limitation（保留）**：见下「已知 limitation」——B2/B3 未做；**L-S4-1**（零交互恢复）仍开放、**L-S4-2**（folder 身份键）未修；只承诺 **file-source 同路径恢复**；`quarantine_path` 不展示；**C-17 journal 撤销撕裂仅登记不处理**。
- **未解决/未宣称**：不写「零交互自愈」「根级问题全解」「自动恢复/撤销后自动放行」；替换场景不称作「原地刷新」（phase B 才是 L-S4-A 原地刷新）。


## Review r1 返修记录（Owner 回填；不改 status）

- 依据：独立上下文 r1 `doc/reviews/FEA-11-L-S1-B-RECOVERY-REAUTH-1-r1.md`（**approved，P0=0/P1=0/P2=2/P3=11**）。
- 新 commit 链（在首轮 `710e749a9` 之上；仅本卡字节，未 push、未建 worktree）：
  - `019feeb6e` — `fix(fea-11-l-s1b)`：**P2-01** 单源归因（`LastPlanFailureSource` + `AttributeFailedSource`；批量/歧义在任何 wire 调用前拒绝，健康源零撤销/零注册）+ **P3-04** folder 拒绝 + **P3-07** 新预览清 outcome + **P3-11** revoke ACK 文案。
  - `e9e1132a5` — `test(fea-11-l-s1b)`：P2-01 多选/归因/健康源/folder/生产 pin 归因测试；P2-02 真实 wire 断言（0 命中 + `[REDACTED]` 帧）；P3-06 仅按钮命令驱动的 View 测试；P3-10 夹具 gate 关闭不启 Core；**`delivery_head`**。
  - r1 卡/Handoff（`doc/handoffs/FEA-11-L-S1-B-RECOVERY-REAUTH-1-e9e1132a5.md`，supersedes `…-0fdde2de8.md`）/证据为同批文档提交。
- **门禁实测（r1 head，均真跑）**：build **0/0**；定向 `~SourceRecovery` **43 / 0 / 0**；gated IPC **1 / 0 / 0**（`wire_frame_count=77 wire_path_hits=0 wire_redacted_frames=7`）；定向 pytest **74**；全量 pytest **3317 / 10**（= 基线）；全量 .NET **1613 / 0 / 93**（基线 1570/0/92：+43 本卡、+1 新增 opt-in skip）；pins **18/18**；check **PASS(3w)×2**；API **EXIT=0**；scope **PASS**（禁止面 11 项 ZERO_DIFF、`CORE_PROTOCOL_MINOR=3`）；判别性 **5/5 RED_AS_EXPECTED + 5/5 RESTORED + final rebuild EXIT 0**（新增 **B5** 批量归因回归点）；跑后 `git checkout -- verification/FEA-09` CLEAN。
- **P3 处置**：P3-01/02/08 修正证据数字、scope 快照口径与卡面构建命令；P3-03/11 登记 limitation（revoked 行累积、ACK 计数口径）；P3-04/06/07/10 FIXED；P3-05 部分修复（生产 pin 归因单测）并登记接受；P3-09 discrimination 日志改为一次干净重跑并标注早期探索性失败。


## Review r2 返修记录（Owner 回填；不改 status）

- 依据：独立上下文 r2 窄面复审 `doc/reviews/FEA-11-L-S1-B-RECOVERY-REAUTH-1-r2.md`（**approved，P0=0/P1=0/P2=1/P3=3**）。
- 新 commit 链（在 r1 `5dd6f7bb5` 之上；仅本卡字节，未 push、未建 worktree）：
  - `f1272f29a` — `fix(fea-11-l-s1b)`：**R2-P2-01** 歧义分支可达——`DiagnoseAsync` 把 `ambiguous` 判定移到「空 targets」守卫**之前**（多选无法归因时 HostController pin 0 targets + `ambiguous=true`，旧顺序会先返回 `NotApplicable`，卡/Handoff 承诺的「请只选择一个来源」提示不可达）；歧义分支仍**零 wire/零撤销/零注册**；非歧义的空列表仍 `NotApplicable`。
  - `80d2799de` — `test(fea-11-l-s1b)`：歧义判别测试（orchestrator 的 null/空 targets、反向用例、HostController 两调用组合路径、VM + **真实** `SourceRecoveryCoordinator` 端到端提示与零 wire）；**`delivery_head`**。
  - r2 卡/Handoff（`doc/handoffs/FEA-11-L-S1-B-RECOVERY-REAUTH-1-80d2799de.md`，supersedes `…-e9e1132a5.md`）/证据为同批文档提交。
- **门禁实测（r2 head，均真跑）**：build **0/0**；定向 `~SourceRecovery` **47 / 0 / 0**；gated IPC **1 / 0 / 0**；定向 pytest **74**；全量 pytest **3317 / 10**（= 基线）；全量 .NET **1617 / 0 / 93**（基线 1570/0/92：+47 本卡、+1 新增 opt-in skip）；pins **18/18**；check **PASS(3w)×2**；API **EXIT=0**；scope **PASS**（全变更路径 ALLOWED、forbidden=0、禁止面 11 项 ZERO_DIFF、`CORE_PROTOCOL_MINOR=3`、1 项并发非交付标注）；判别性 **6/6 RED_AS_EXPECTED + 6/6 RESTORED + final rebuild EXIT 0**（新增 **B6** 守卫顺序回归点）；跑后 `git checkout -- verification/FEA-09` CLEAN。
- **r2 P3 残留处置**：①AC-LSB-8 证据数字改为实测 **47/1617/+47**；②scope 快照按**最终 docs commit** 重算并保留 `concurrent` 披露；③卡内全量测试命令统一为 `apps/desktop-avalonia/NewManga.sln`。

## Canonical Evidence

| evidence_id | AC | 路径 | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC-LSB-8/9 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/EV.md | 80d2799de | 4771837927afa34bcd34c3cf6d194960f2aa51786a51b17cedeb25e23a7437bc | CANONICAL |
| EV-02 | AC-LSB-9 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/logs/ipc-closed-loop.json | 80d2799de | 95288edeb73bc292525d7a43f6f2701eda11c21123adead144fd694c11e6a7b4 | CANONICAL |
| EV-03 | AC-LSB-9 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/logs/ipc-closed-loop.txt | 80d2799de | 406f68d7f76030446f4af3bd1d7edadfc5d2e4c00acf1356e4f62c8112f25a6b | CANONICAL |
| EV-04 | AC-LSB-8 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/logs/build.log | 80d2799de | 78dea3f0034dffef7aa03e06ad96e6af0a04cd43e37d23723921bd552f1b9a25 | CANONICAL |
| EV-05 | AC-LSB-1/2/3/4/5/6/7 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/logs/app-unit.log | 80d2799de | 807d02f78669217283b92e1b0720f2149a68950c8d0027c4183ef8f31a212a5e | CANONICAL |
| EV-06 | AC-LSB-9 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/logs/host-ipc.log | 80d2799de | 635cf1f003460016cf682d3ce0d36b56293fa12869563dd36ce559caa7e04af2 | CANONICAL |
| EV-07 | AC-LSB-8 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/logs/feature.log | 80d2799de | 1910f19a42189eb0ce363873955d88889e7ae094bf7616c67499eedb75893581 | CANONICAL |
| EV-08 | AC-LSB-8 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/logs/full-pytest.log | 80d2799de | e8dbe3b2a1b04d27a3f92cf951b0bf6cc62efe65f9fbd69c54be44617df731ad | CANONICAL |
| EV-09 | AC-LSB-8 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/logs/full-dotnet.log | 80d2799de | 9566604c26f1f7b897ed2b7e66772a5f77caf3e37a9d13933a51c0f63dd38817 | CANONICAL |
| EV-10 | AC-LSB-8 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/logs/gates-governance.log | 80d2799de | fab572f3eea5c0b6d1ebd8fc715e351250cb134e28d53c92ba61e1b79315e31f | CANONICAL |
| EV-11 | AC-LSB-1/3/5/7 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/logs/discrimination.log | 80d2799de | d323976af9d69f33a4681337160e29aa469d03baa13ccd880357caa4f09f7870 | CANONICAL |
| EV-12 | AC-LSB-8 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/scope-validation.log | 80d2799de | 5a871cfe502410e08fb32df5a3fea7c4c6d17ccb4bd55e3092778dd4f8634413 | CANONICAL |
| EV-13 | AC-LSB-8 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/changed-files.txt | 80d2799de | f999eb39e1d53980360ee2565f864d131dea23f5b6bbc2063ba53c057a330484 | CANONICAL |
| EV-14 | AC-LSB-8 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/RESOURCE-MANIFEST.json | 80d2799de | 145f01e5d678d2cd75047e1bd100933c9ec3529acee70b468fd36ca0643ca27b | CANONICAL |

> 证据树逐文件 sha256 以本表为准；`logs/` 中 `.txt`/`.json`/`.log` 均为实跑原始输出。

## Resource Manifest

| resource_type | 资源 | disposition | 目标 | 完整性 | 引用/进程检查结果 |
|---|---|---|---|---|---|
| 无删除/移动/归档 | - | NOT_APPLICABLE | - | - | 本卡仅改 App 源/测试 + 卡/Handoff/证据；仓内 0 删除/0 移动/0 归档；仓外隔离根 `G:/CODEX/New Manga.workspace/FEA-11-L-S1-B-RECOVERY-REAUTH-1/` PRESERVE_REFERENCED（IPC 夹具/判别性备份/日志，无独有产品数据；详见 `RESOURCE-MANIFEST.json`） |

## Review（r1→r2→r3）处置（DSH，2026-11-07；append-only）

- **r1 `84562d6a-…` approved（P0=0/P1=0/P2=2/P3=11）**：R-P2-01 多选恢复面过宽/归因错误、R-P2-02 gated IPC 空转断言 → Owner 返修（`019feeb6e`/`e9e1132a5`/`5dd6f7bb5`）：单源归因、真实 wire 0 命中 + `[REDACTED]` 断言；P3×11 处置（数字/scope/folder/View/清空/构建命令/标注/skip/limitation）。
- **r2 `8df55bef-…` approved（P0=0/P1=0/P2=1/P3=3）**：R2-P2-01 歧义提示不可达（空 targets 守卫先于 ambiguous）→ Owner 返修（`f1272f29a`/`80d2799de`/`8a249538a`）：歧义判定前移，`MultipleSources` 与单选提示可达且零 wire，加 B6 判别；P3 残留（卡数字/scope 快照/build 命令）已修。
- **r3 `2e178b6d-…` approved（P0=0/P1=0/P2=0/P3=3）**：R2-P2-01 关闭；B6 独立 RED→恢复；无回归/红线保持；新 P3 为**证据/清单记数残留**（EV.md 旧 head/1613、Manifest `repo_head_at_generation` 指向 pre-amend docs commit、discrimination 头部 5 vs 6）→ **登记接受**（不改变产品语义/门禁/安全结论；后续维护批可清理，不重开本卡）。
- 不改变实现/测试字节（`80d2799de`）与 AC-LSB-1…10 MET 判定。

## Canonical Evidence

| evidence_id | AC | 路径 | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC-LSB-8/9 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/changed-files.txt | 8a249538a | f999eb39e1d53980360ee2565f864d131dea23f5b6bbc2063ba53c057a330484 | CANONICAL |
| EV-02 | AC-LSB-8/9 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/EV.md | 8a249538a | 4771837927afa34bcd34c3cf6d194960f2aa51786a51b17cedeb25e23a7437bc | CANONICAL |
| EV-03 | AC-LSB-8/9 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/logs/app-unit.log | 8a249538a | 807d02f78669217283b92e1b0720f2149a68950c8d0027c4183ef8f31a212a5e | CANONICAL |
| EV-04 | AC-LSB-8/9 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/logs/build.log | 8a249538a | 78dea3f0034dffef7aa03e06ad96e6af0a04cd43e37d23723921bd552f1b9a25 | CANONICAL |
| EV-05 | AC-LSB-8/9 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/logs/discrimination.log | 8a249538a | d323976af9d69f33a4681337160e29aa469d03baa13ccd880357caa4f09f7870 | CANONICAL |
| EV-06 | AC-LSB-8/9 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/logs/feature.log | 8a249538a | 1910f19a42189eb0ce363873955d88889e7ae094bf7616c67499eedb75893581 | CANONICAL |
| EV-07 | AC-LSB-8/9 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/logs/full-dotnet.log | 8a249538a | 9566604c26f1f7b897ed2b7e66772a5f77caf3e37a9d13933a51c0f63dd38817 | CANONICAL |
| EV-08 | AC-LSB-8/9 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/logs/full-pytest.log | 8a249538a | e8dbe3b2a1b04d27a3f92cf951b0bf6cc62efe65f9fbd69c54be44617df731ad | CANONICAL |
| EV-09 | AC-LSB-8/9 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/logs/gates-governance.log | 8a249538a | fab572f3eea5c0b6d1ebd8fc715e351250cb134e28d53c92ba61e1b79315e31f | CANONICAL |
| EV-10 | AC-LSB-8/9 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/logs/host-ipc.log | 8a249538a | 635cf1f003460016cf682d3ce0d36b56293fa12869563dd36ce559caa7e04af2 | CANONICAL |
| EV-11 | AC-LSB-8/9 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/logs/ipc-closed-loop.json | 8a249538a | 95288edeb73bc292525d7a43f6f2701eda11c21123adead144fd694c11e6a7b4 | CANONICAL |
| EV-12 | AC-LSB-8/9 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/logs/ipc-closed-loop.txt | 8a249538a | 406f68d7f76030446f4af3bd1d7edadfc5d2e4c00acf1356e4f62c8112f25a6b | CANONICAL |
| EV-13 | AC-LSB-8/9 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/RESOURCE-MANIFEST.json | 8a249538a | 145f01e5d678d2cd75047e1bd100933c9ec3529acee70b468fd36ca0643ca27b | CANONICAL |
| EV-14 | AC-LSB-8/9 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/scope-validation.log | 8a249538a | 5a871cfe502410e08fb32df5a3fea7c4c6d17ccb4bd55e3092778dd4f8634413 | CANONICAL |

> 证据树逐文件 sha256 以本表为准；r3 独立复算 EV 14/14 一致。review/handoff 不在 evidence_dir，按卡面/Handoff 引用。

## Resource Manifest

| resource_type | 资源 | disposition | 目标 | 完整性 | 引用/进程检查结果 |
|---|---|---|---|---|---|
| 无删除/移动/归档 | - | NOT_APPLICABLE | - | - | 本卡仅改 App 源/测试 + 卡/Handoff/证据；仓内 0 删除/0 移动/0 归档；仓外隔离根 `G:/CODEX/New Manga.workspace/FEA-11-L-S1-B-RECOVERY-REAUTH-1/` 保留（IPC 夹具/日志/备份，无独有产品数据） |

## Closeout Record（2026-11-07）

- **状态**：`done`；`delivery_head`/`integration_commit` = `80d2799de7195ccdec6954b523eea6830f315335`（r1 基线 `0fdde2de8` → r1 返修 `e9e1132a5` → r2 返修 `80d2799de`；docs/evidence `8a249538a`）。
- **AC 判定**：AC-LSB-1…AC-LSB-10 **全 MET**；无 PARTIAL/BLOCKED。
- **Review 处置**：r1 approved（P2×2 已修）→ r2 approved（P2×1 已修）→ **r3 approved（P0=0/P1=0/P2=0/P3=3 非阻断，登记接受）**。
- **门禁数字（before → after；Lead 实测）**：全量 pytest **3317/10 → 3317/10**；全量 .NET **1570/0/92 → 1617/0/93**（+47 本卡 App 测试、+1 opt-in skip）；定向 App `SourceRecovery` **47/0/0**；gated 真实 IPC **1/0/0**（wire 77 帧、根路径 0 命中、`[REDACTED]` 7、quarantine 0）；pins **18/18**；check（默认+`-TaskPath`）PASS；API inventory PASS；scope **changed=29 全 ALLOWED**、禁止面零 diff、`CORE_PROTOCOL_MINOR=3`；判别性 **6/6**；全量后恢复 `verification/FEA-09`。
- **limitations（保留）**：B2/B3 未做；L-S4-1（零交互恢复）/L-S4-2（folder 身份键）；**C-17 journal 撤销撕裂（仅登记）**；`quarantine_path` 不展示；重复恢复累积 revoked 行（active 恒 1）；revoke ACK 失败计数口径；只承诺 file-source 同路径恢复；L-R1 未全修；不宣称自动恢复/根级问题全解。
- **Resource Manifest / 资源处置**：仓内删除/移动/归档 0；仓外隔离根 PRESERVE_REFERENCED。
- **指针清理**：STATUS 无活动 Task；PLAN 本节点 done；TASK_LEDGER 重生成。
- **push**：Lead 统一 push（PRE/POST/AHEAD 记录见状态文件）。
