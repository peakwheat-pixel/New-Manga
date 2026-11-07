---
id: FEA-11-L-S1-B-RECOVERY-REAUTH-1
title: App 显式恢复/重授权入口（B1：撤销→再注册→重导入；零契约、App-only）
kind: implementation
governance_version: 3
status: ready
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH」；权威 scope review `doc/reviews/FEA-11-L-S1-B-RECOVERY-REAUTH-1-scope-r1.md`（fresh subagent `7d2a572e-…`，**READY-WITH-UNFREEZE**；拆卡：**B1 = READY-TO-FREEZE（App-only，零契约 0/18 pins）**；B2（wire 可用性投影）/ B3（扫描侧投影）暂缓）；Codex 不可用（product limit）→ 按用户授权 ZCode 故障转移裁决（记录见卡）；DSH 裁决 D-1…D-10（见下）
suggested_owner: zcode
owner: l-s1b-impl
reviewer: 独立上下文 fresh subagent（未参与实现/返修；只读交付 head；session 见 `doc/reviews/FEA-11-L-S1-B-RECOVERY-REAUTH-1-r1.md`）
depends_on:
  - FEA-11-L-S1-REGISTRY-RESILIENCE-1
  - FEA-11-L-S4-LOCATION-AUTH-REFRESH-1
base_commit: 3d97e3b18
branch: null
worktree: null
integration_commit: null
delivery_head: 0fdde2de8953ffcfd847471fdf8c6d82bf507257
canonical_evidence_status: pending
resource_closeout_status: pending
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

- [x] **AC-LSB-1 入口仅显式**：预览以 `SOURCE_REGISTRY_UNAVAILABLE` 失败时，只暴露「重新授权此来源」/「重置源授权存储」两个显式动作；未点击前 revoke/register/reset 调用计数均为 **0**。 证据：VM 例 `FailedPreview_ExplicitReauthorize_OnlyOffersThatOneAction_AndWritesNothingYet`（失败后仅 1 次只读探针；`SourceReauthorizeCalls=0`、`SourceResetCalls=0`、`SourceResetConfirms` 空）；真实 IPC `registry_unchanged_after_failure=true`；判别性 B1（把恢复挂进失败分支 → RED）`logs/app-unit.log`/`logs/discrimination.log`/`logs/ipc-closed-loop.json`。 <<MET>>
- [x] **AC-LSB-2 分流正确**：只读 `source_list_roots` 探针——探测抛 `SOURCE_REGISTRY_UNAVAILABLE` → 只给「重置」；探测成功 + 铸造失败 → 只给「重授权」；探测抛其它码 → 不给任何恢复动作，只显示该码。 证据：`FileLevelProbeFailure_OffersResetOnly_AndWritesNothing`、`OtherProbeCode_OffersNoRecoveryAction_AndDisplaysOnlyThatCode`（实跑 `CORE_CAPABILITY_MISSING`/`SOURCE_REGISTRY_BUSY`）、`CoreSideFailureOrAnotherPreviewCode_OffersNothing_AndNeverProbes`、`ReadableStorageWithStaleEntries_OffersReauthorizeOnly_*`、`ReadableStorageWithoutAnyStaleEntry_OffersNothing`、VM `FailedPreview_FileLevel_*`/`FailedPreview_OtherTypedCode_*`（探测码被显示、动作数 0）、`Reset_RequiresConfirmation_*`。 <<MET>>
- [x] **AC-LSB-3 撤销→注册顺序与幂等**：同一路径 2 条 stale 非撤销条目都被撤销（generation+1、`revoked_at` 非空），随后只新增 1 条非撤销条目；重复执行不产生重复条目。 证据：`Reauthorize_RevokesEverySamePathEntryFirst_ThenRegistersExactlyOnce`（帧序 `source_list_roots→source_revoke_root×2→source_register_root`；两条均 generation+1/revoked；恰 1 条 active；无关路径不动）、`Reauthorize_RepeatedExecution_KeepsExactlyOneActiveEntry`、`Reauthorize_UsesTheRegisteredRootString_NotTheCallerSpelling`；判别性 B2（只撤首条→RED）/B3（先注册后撤销→RED）`logs/discrimination.log`。 <<MET>>
- [x] **AC-LSB-4 部分失败 fail-closed**：撤销成功但注册失败 → 明确「已撤销、未重新授权」+ typed 码；不得显示成功、不得隐式回滚 `revoked_at`；可重试。 证据：`Reauthorize_RegisterFailure_ReportsRevokedNotReauthorized_WithNoRollback`（`RevokedButNotRegistered`、消息含「已撤销…未重新授权（SOURCE_ACCESS_DENIED）」、旧条目仍 revoked、无回滚、清除故障后重试成功）、`Reauthorize_PartialOutcomeRetry_FinishesTheRegisterLegFromTheRevokedRoot`、`Reauthorize_RevokeFailure_AbortsBeforeAnyRegistration`（撤销失败即中止、零注册）、VM `PartialFailure_ShowsRevokedNotReauthorized_AndStaysRetryable`。 <<MET>>
- [x] **AC-LSB-5 不自动重授权（安全核心）**：铸造失败后不自动注册/不自动换候选；`FindOrRegisterRootAsync` 复用选择器语义不变（首个非 revoked 匹配）。 证据：`PlanAndMintPath_NeverInvokesARecoveryCommand_OnlyTheExplicitActionDoes`（`SourceImportModels.cs` 中 `source_register_root`/`source_list_roots` 各 1 处、revoke/reset 0 处）、`ReuseSelector_StillSkipsRevokedEntries_AndNeverFallsBackOnAFailedMint`（选择器抽出为纯函数、语义逐字不变）、`Reauthorize_WithNothingToRevoke_WritesNothing`、`Reauthorize_ReadOnlyHost_WritesNothing`；真实 IPC「typed 失败后 registry 长度不变、条目仍非 revoked」；判别性 B1 `logs/discrimination.log`。 <<MET>>
- [x] **AC-LSB-6 授权面不扩大**：重授权只使用条目已登记 `roots[0]`；恢复成员**无**任意路径入参；`HostCommandRegistry.All` 数量不变；恢复成员不在 `IHostController` 上（C-07 pin 不变）。 证据：`RecoveryMembers_LiveOnTheSeparatePort_AndNeverOnTheFrozenHostController`、`RecoveryMembers_AcceptNoPathOrOpaqueSourceArgument`（参数仅 `bool`/`CancellationToken`）、`RecoverySurface_AddsNoWireCommand_AndKeepsTheFrozenCommandCount`（`HostCommandRegistry.All.Count == 111` 冻结、无 recover/reauthor 命令、4 条既有 root 命令不变）、`Reauthorize_UsesTheRegisteredRootString_NotTheCallerSpelling`；`generate_api_inventory.py --check` EXIT=0；`logs/gates-governance.log`。 <<MET>>
- [x] **AC-LSB-7 脱敏**：恢复文案/通知/日志只含叶子名/typed 码/计数；不含绝对路径/`quarantine_path`；gated IPC 断言 wire/stderr 中 fixture 根路径 0 命中。 证据：VM 全量 `AllVisibleText` 断言 `C:\manga` 0 命中 + `quarantine` 0 命中（含失败/成功/重置三态）；`Reset_RequiresConfirmation_AndNeverSurfacesTheQuarantinePath`（脚本 Host 响应**故意带** `quarantine_path` 也不得泄漏）；真实 IPC：`wire_quarantine_hits=0`、含路径的 wire 帧仅既有 `RegisterSourceReadGrant`（基线，显式断言）、`stderr_path_hits=0`、恢复文案 path-free；判别性 B4（渲染 quarantine_path → RED）。 <<MET>>
- [x] **AC-LSB-8 零漂移/门禁**：Host/CoreClient/doc-plan/src 零 diff；API inventory PASS；pins 18/18；check（默认+`-TaskPath`）PASS；全量 pytest/.NET 不降（基线 **3317/10、1570/0/92**）。 证据：`logs/build.log`（0/0）、`logs/app-unit.log`（34/0/0）、`logs/host-ipc.log`（1/0/0）、`logs/feature.log`（74 passed）、`logs/full-pytest.log`（**3317 passed / 10 skipped** = 基线）、`logs/full-dotnet.log`（**1604 / 0 / 93** = 基线 1570/0/92 +34 本卡测试 +1 新增 opt-in skip）、`logs/gates-governance.log`（pins 18/18、check PASS(3w)×2、API EXIT=0）、`scope-validation.log`（changed=12 全 ALLOWED、forbidden=0、禁止面 11 项 ZERO_DIFF；1 项并发非交付（ac528828b）显式标注、`CORE_PROTOCOL_MINOR=3`）；跑后 `git checkout -- verification/FEA-09` → CLEAN。 <<MET>>
- [x] **AC-LSB-9 闭环证据（gated 真实 IPC 1 条）**：注册→同路径替换→预览 typed 失败→显式重授权→再预览成功→重新导入后 `source_locations.registry_id/generation` 原地刷新（L-S4 A）→ `source_list_scan_targets` 返回新代次。 证据：`logs/host-ipc.log`（`NEWMANGA_FEA11_IPC=1`，PASS 1/0/0）+ `logs/ipc-closed-loop.json`/`.txt`：phase A 真实**同路径替换**（typed 失败 → 显式重授权 revoked=1/registered=1 → 再预览成功 → 重新导入 Completed → 枚举返回新 registry/gen；替换=新物理身份 → 新 source，旧行留在只读投影由 Host fail-closed 丢弃）；phase B 同物理身份 + 新 registry 的 **L-S4-A 原地刷新**（同一 `location_id`、`registry_id` 换新、`last_verified_at` 非空、枚举 gen=1）。 <<MET>>
- [x] **AC-LSB-10 边界/不夸大**：只承诺 **file-source 同路径恢复**；folder 变体受 L-S4-2、重定位走新源；L-S4-1 零交互恢复仍开放；不得写「零交互自愈/根级问题全解」。 证据：EV.md §5/§6、Handoff §3、本卡「已知 limitation」原文；明写「只承诺 file-source 同路径恢复」「L-S4-1/L-S4-2/B2/B3 保留」「C-17 journal 撤销撕裂仅登记」；未出现「零交互自愈/根级问题全解/自动恢复」承诺。 <<MET>>


## 已知 limitation（本卡）

- **B2**（`source_list_roots` 可用性投影）未做 → 多根健康/逐条管理不可见；**B3**（扫描侧投影）未做。
- **L-S4-1**（零交互自动恢复枚举，需 C-16 v1.5 批量载体）仍开放；**L-S4-2**（folder 身份键）未修。
- 只覆盖 file-source 同路径恢复；重定位（换路径）走「重新导入成新源」。
- `source_reset_registry` 的 `quarantine_path` 不展示（C-16 §7.3 冲突，未来随 UNFREEZE 澄清）。
- **同路径替换后的 Core 侧语义（如实登记）**：替换改变物理身份 → 重新导入会写**新的** `source_locations` 行（旧物理身份行仍在只读 Core 投影里，Host 调度器按撤销 registry fail-closed 丢弃）；L-S4-A 的**原地刷新**只在「同物理身份 + 新 registry」成立（gated IPC phase B 实测同一 `location_id` 刷新）。**不宣称**替换场景也算「原地刷新」。
- **C-17 journal 撤销撕裂（仅登记，不处理）**：B1 给了用户第一个撤销入口；撤销后，绑定旧 `registry_id` 的 C-17 apply/journal 重试会永久失败（锚 `HostOperationOrchestrator.cs:112-133`；scope review `:87/:249/:263`）。B1 不修复该影响面（需 B2/L-S4-B 批量设计），文案不得承诺「重试自动恢复」。


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
- **门禁实测**（`delivery_head=0fdde2de8`；均真跑）：`dotnet build NewManga.sln -c Release` **成功 0 warning / 0 error**；定向 `FullyQualifiedName~SourceRecovery` **34 passed / 0 failed / 0 skipped**；gated `NEWMANGA_FEA11_IPC=1 ...~SourceRecoveryIpc` **1 passed / 0 / 0**；定向 Core 回归 `pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` **74 passed**（基线 74）；全量 `pytest tests -q` **3317 passed / 10 skipped**（= 基线）；全量 `dotnet test NewManga.sln -c Release` **1604 / 0 / 93**（基线 1570/0/92：+34 本卡测试、+1 新增 opt-in IPC skip；已知 flaky `FluentResidual2VisualEvidenceTests` 未命中）；`verify_pins` **18/18 PASS**；`check.ps1`（默认 + `-TaskPath`）**PASS(3 warnings)** ×2；API inventory **EXIT=0**；scope **PASS**（changed=12 全 ALLOWED、forbidden=0、禁止面 11 项 ZERO_DIFF；1 项并发非交付（ac528828b）显式标注、`CORE_PROTOCOL_MINOR=3`）；判别性 **4/4 RED_AS_EXPECTED + 4/4 字节级 RESTORED + final rebuild EXIT 0**；跑后 `git checkout -- verification/FEA-09`（CLEAN）。
- **limitation（保留）**：见下「已知 limitation」——B2/B3 未做；**L-S4-1**（零交互恢复）仍开放、**L-S4-2**（folder 身份键）未修；只承诺 **file-source 同路径恢复**；`quarantine_path` 不展示；**C-17 journal 撤销撕裂仅登记不处理**。
- **未解决/未宣称**：不写「零交互自愈」「根级问题全解」「自动恢复/撤销后自动放行」；替换场景不称作「原地刷新」（phase B 才是 L-S4-A 原地刷新）。

## Canonical Evidence

| evidence_id | AC | 路径 | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC-LSB-8/9 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/EV.md | 0fdde2de8 | 8d41ea51ed0aaf76a061f69215b4e191a026d651308b174790a54fad8712520d | CANONICAL |
| EV-02 | AC-LSB-9 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/logs/ipc-closed-loop.json | 0fdde2de8 | 7dd15bd1dc10330e1370adc40197553169ccc9e3eff3d6b0424ee426800e1330 | CANONICAL |
| EV-03 | AC-LSB-9 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/logs/ipc-closed-loop.txt | 0fdde2de8 | edfae3e84624268fb60da0b01e7eed948a91dce86dfae7ecc546a6cc4e885d37 | CANONICAL |
| EV-04 | AC-LSB-8 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/logs/build.log | 0fdde2de8 | fc162b065e31a18d5fb50408183fcc51c237450b3699251e37234ff0e03483ee | CANONICAL |
| EV-05 | AC-LSB-1/2/3/4/5/6/7 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/logs/app-unit.log | 0fdde2de8 | c32e58df0082c1552c3e5fba89244c06e80f355790f65d7d1f256e4ded1bc054 | CANONICAL |
| EV-06 | AC-LSB-9 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/logs/host-ipc.log | 0fdde2de8 | 68e2148fb74cd7d5307913c8c147dda414d4fdd03c1076cf9a6d807b290eb89a | CANONICAL |
| EV-07 | AC-LSB-8 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/logs/feature.log | 0fdde2de8 | 3ff92a94ec46c8b9940b7f82b99a8ebb578c4ed597c993c774f7a86d9ea7ba84 | CANONICAL |
| EV-08 | AC-LSB-8 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/logs/full-pytest.log | 0fdde2de8 | 5baa9dde17fbccc44ad103c93c157b99e6c96abf9134811cc005cafc056211aa | CANONICAL |
| EV-09 | AC-LSB-8 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/logs/full-dotnet.log | 0fdde2de8 | c57a3df110f16aceb0dc48884254ba2dc93356cbb7182be5c7a33a1146e98204 | CANONICAL |
| EV-10 | AC-LSB-8 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/logs/gates-governance.log | 0fdde2de8 | dde96fffe39beef4aa1f4fe80d16fd05b8847c4546fa3478939ec54590ee1855 | CANONICAL |
| EV-11 | AC-LSB-1/3/5/7 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/logs/discrimination.log | 0fdde2de8 | e75b479286df4e0afa903e6d5382cf8c2d6e0aad4aed88a8dd7f81dc29ed0830 | CANONICAL |
| EV-12 | AC-LSB-8 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/scope-validation.log | 0fdde2de8 | de0fdf85ba6062d4f713cbd6ab7842cd0ae9c24644c9559c4efb1818dc0440db | CANONICAL |
| EV-13 | AC-LSB-8 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/changed-files.txt | 0fdde2de8 | 2a42faac036cf717b4ee4f653b38f208e3b400df4548cdbcda4ebc184afc76d7 | CANONICAL |
| EV-14 | AC-LSB-8 | verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/RESOURCE-MANIFEST.json | 0fdde2de8 | b74a38daabbeb81c61fa83b6ac77667aa8edace5e45ce0eb4e19cdc2f0da8637 | CANONICAL |

> 证据树逐文件 sha256 以本表为准；`logs/` 中 `.txt`/`.json`/`.log` 均为实跑原始输出。

## Resource Manifest

| resource_type | 资源 | disposition | 目标 | 完整性 | 引用/进程检查结果 |
|---|---|---|---|---|---|
| 无删除/移动/归档 | - | NOT_APPLICABLE | - | - | 本卡仅改 App 源/测试 + 卡/Handoff/证据；仓内 0 删除/0 移动/0 归档；仓外隔离根 `G:/CODEX/New Manga.workspace/FEA-11-L-S1-B-RECOVERY-REAUTH-1/` PRESERVE_REFERENCED（IPC 夹具/判别性备份/日志，无独有产品数据；详见 `RESOURCE-MANIFEST.json`） |

