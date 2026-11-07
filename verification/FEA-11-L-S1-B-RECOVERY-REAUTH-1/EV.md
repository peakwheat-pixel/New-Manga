# FEA-11-L-S1-B-RECOVERY-REAUTH-1 Canonical Evidence（B1：App 显式恢复/重授权入口；App-only、零契约、0/18 pins）

> 结论先行：本卡给产品装上**第一个显式**的根级恢复入口，并且只做 App 侧接线。产品内原本**没有任何**恢复路径：被替换/缺失根的**同路径重导入永久失败**（复用选择器只按「同 registry 路径串 + 非 revoked」挑条目，被替换条目永远排在复用位置；Host mint 侧逐请求重核根身份 → typed `SOURCE_REGISTRY_UNAVAILABLE`），`source_revoke_root`/`source_register_root`/`source_reset_registry` 在 App 侧 **0 调用**。本卡新增：①`ISourceImportController` 的**恢复面**（只读诊断探针 + 显式重授权 + 显式重置，**无任何路径/registry_id 入参**）；②`SourceRecoveryModels.cs` 编排（**先只读探针分流** → 文件级只给「重置」/根级只给「重授权」/其它码不给动作；重授权 = **先撤销该路径全部非撤销 stale 条目、再按条目已登记 `roots[0]` 注册一次**、部分失败 fail-closed 可重试、重复执行恒 1 条 active）；③ImportDock 的**两个显式命令** + 二次确认 + 脱敏文案（叶子名/typed 码/计数，**不显示 `quarantine_path`**）。**红线 R-1 保持**：mint/导入路径一行未改语义（复用选择器抽出为纯函数、语义逐字不变），任何错误分支**都不**调用 revoke/register/reset。**不夸大**：只承诺 **file-source 同路径恢复**；folder 身份键（L-S4-2）、零交互自动恢复枚举（L-S4-1，需 C-16 v1.5）、B2（roots 可用性投影）/B3（扫描侧投影）**仍开放**；撤销会让绑定旧 `registry_id` 的 C-17 journal 重试永久失败——**仅登记，不处理**。独立 Review 由 Lead 指派（本会话不自审）。

| 项 | 值 |
|---|---|
| task | `FEA-11-L-S1-B-RECOVERY-REAUTH-1`（冻结卡 `doc/tasks/FEA-11-L-S1-B-RECOVERY-REAUTH-1.md`；卡面 `status` 未改，仍为 `ready`） |
| Owner | `l-s1b-impl`（DSH Agent Teams teammate；Lead `lead`） |
| base | 卡 `base_commit=3d97e3b18`；实现起点 `e0b37622b`（工作树 clean，实测）；交付期间同批并发 docs 提交 `ac528828b`（仅 `doc/handoffs/DSH-PROGRESS-2026-11-07.md`，非本卡字节） |
| 本次 delivery_head | `0fdde2de8953ffcfd847471fdf8c6d82bf507257`（实现 `be3b0c242` + 测试 `0fdde2de8`；卡/Handoff/证据为同批文档提交） |
| 分支/工作树 | `main` / `G:\CODEX\New Manga`（未创建 linked worktree、未 push） |
| 隔离根 | `G:\CODEX\New Manga.workspace\FEA-11-L-S1-B-RECOVERY-REAUTH-1\`（IPC 夹具 `fixtures/ipc-*`、判别性备份 `tmp/discrimination/`、全量日志）；**未写** `verification/FEA-09/**` |
| 契约字节 | **零变更**：`doc/plan/**`、`doc/contracts/**` 零 diff；C-16 仍 v1.4（pin `ad25fb3c89bb`）；`CORE_PROTOCOL_MINOR=3` |
| C-07 API inventory | **零变更**（`generate_api_inventory.py --check` EXIT=0）：恢复成员只在 `ISourceImportController`，不在 `IHostController` |
| 依赖/schema | **零新增** |
| 解释器/环境 | Windows 11 / PowerShell 7.6.8 / CPython 3.14.6 / .NET SDK（net9.0） |

## 1. 交付 commit 链（起点 `e0b37622b` → delivery_head `0fdde2de8`）

```text
0fdde2de8 test(fea-11-l-s1b): discriminative recovery tests + one gated real-IPC closed loop
be3b0c242 feat(fea-11-l-s1b): App explicit source recovery/re-authorization face (B1; App-only, zero contract)
ac528828b docs(progress): 记录 L-S1-B1 裁决（D-1…D-10 + ZCode APPROVE 附 C-17 journal 补登）   ← 并发非本卡
e0b37622b （本卡实现起点，工作树 clean）
```

## 2. 门禁实测（均真跑；`delivery_head=0fdde2de8`）

| Gate | 命令 | 结果 | 日志 |
|---|---|---|---|
| 构建（AC-LSB-8） | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` | **成功 0 warning / 0 error（EXIT 0）** | `logs/build.log` |
| VM/编排级（AC-LSB-1/2/3/4/5/6/7） | `dotnet test .../NewManga.App.Tests --filter "FullyQualifiedName~SourceRecovery"` | **PASS 33 / 0 failed / 0 skipped** | `logs/app-unit.log` |
| gated 真实 IPC（AC-LSB-9） | `NEWMANGA_FEA11_IPC=1 dotnet test .../NewManga.Host.Tests --filter "FullyQualifiedName~SourceRecoveryIpc"` | **PASS 1 / 0 / 0**；隔离 receipt：`logs/ipc-closed-loop.txt` + `logs/ipc-closed-loop.json` | `logs/host-ipc.log` |
| 定向 Core 回归（AC-LSB-8） | `python -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | **PASS 74 passed**（基线 74，不降） | `logs/feature.log` |
| 全量 Python（AC-LSB-8） | `python -m pytest tests -q` | **PASS 3317 passed / 10 skipped**（= 基线 3317/10，零漂移） | `logs/full-pytest.log` |
| 全量 .NET（AC-LSB-8） | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` | **PASS 1604 / 0 failed / 93 skipped**（基线 1570/0/92：**+34** 本卡 App 测试、**+1** 新增 opt-in IPC skip） | `logs/full-dotnet.log` |
| 治理（AC-LSB-8） | `verify_pins.ps1` / `check.ps1`（默认 + `-TaskPath`）/ `generate_api_inventory.py --check` | **PIN AUDIT PASS（18/18）** / **PASS(3 warnings)** ×2 / **EXIT=0** | `logs/gates-governance.log` |
| 范围（AC-LSB-8） | scope 校验（见 `scope-validation.log`） | **PASS**：changed=12 全 ALLOWED、forbidden=0、禁止面 11 项 ZERO_DIFF；1 项并发非交付（ac528828b）显式标注、`CORE_PROTOCOL_MINOR=3` | `scope-validation.log`、`changed-files.txt` |
| 判别性（AC-LSB-1/3/5/7） | `discrimination.ps1`（4 破坏点 → 1 目标用例变红 → 原字节恢复） | **4/4 RED_AS_EXPECTED + 4/4 RESTORED（sha256 一致）+ final rebuild EXIT 0** | `logs/discrimination.log` |

**数字口径（诚实记录）**：
- 全量 .NET **1604/0/93**：基线 **1570/0/92**；差额 = **+34**（本卡 `FullyQualifiedName~SourceRecovery` 34 例，全在 `NewManga.App.Tests` 程序集）+ **+1 skipped**（新增 gated IPC 用例在未设 `NEWMANGA_FEA11_IPC=1` 时 skip）。
- 全量 pytest **3317/10** = 卡基线，**零 Python 改动**；跑后 `git checkout -- verification/FEA-09` → `FEA09_STATUS=0`（CLEAN）。
- 已知 flaky `FluentResidual2VisualEvidenceTests` **本次未命中**（全量 1604/0 无失败），未重跑凑绿。

## 3. 判别性验证（4 破坏点；删掉/改坏实现必须变红）

`discrimination.ps1` 对**已提交字节**做一次最小破坏 → 构建 → 只跑**一个**目标用例 → 必须失败 → 按原字节恢复并复核 sha256 → 最后重建。实测全部 `RED_AS_EXPECTED` + `RESTORED`：

| Case | 破坏点 | 目标用例 | 实测 |
|---|---|---|---|
| **B1**（AC-LSB-1/5 安全核心） | 把 `ReauthorizeSourceAsync()` 挂进**预览失败分支**（= 自动重授权） | `FailedPreview_ExplicitReauthorize_OnlyOffersThatOneAction_AndWritesNothingYet` | **RED_AS_EXPECTED + RESTORED**（写入端口计数 > 0） |
| **B2**（AC-LSB-3） | 只撤销**首条**同路径 stale 条目（`stale.Take(1)`） | `Reauthorize_RevokesEverySamePathEntryFirst_ThenRegistersExactlyOnce` | **RED_AS_EXPECTED + RESTORED**（第二条仍 active） |
| **B3**（AC-LSB-3） | **先注册后撤销**（顺序反转） | 同上 | **RED_AS_EXPECTED + RESTORED**（frame 顺序断言失败） |
| **B4**（AC-LSB-7） | 读取并渲染响应的 `quarantine_path`（绝对路径泄漏） | `Reset_RequiresConfirmation_AndNeverSurfacesTheQuarantinePath` | **RED_AS_EXPECTED + RESTORED** |

## 4. AC 矩阵（测试 → 证据映射）

| AC | 判定 | 关键测试/证据 |
|---|---|---|
| AC-LSB-1 入口仅显式 | **MET** | `FailedPreview_ExplicitReauthorize_OnlyOffersThatOneAction_AndWritesNothingYet`（失败后 `SourceReauthorizeCalls=0`/`SourceResetCalls=0`；仅 1 次只读探针）+ 真实 IPC `registry_unchanged_after_failure=true` |
| AC-LSB-2 分流正确 | **MET** | `FileLevelProbeFailure_OffersResetOnly_AndWritesNothing`、`OtherProbeCode_OffersNoRecoveryAction_AndDisplaysOnlyThatCode`（实跑 `CORE_CAPABILITY_MISSING`/`SOURCE_REGISTRY_BUSY`）、`CoreSideFailureOrAnotherPreviewCode_OffersNothing_AndNeverProbes`、`ReadableStorageWithStaleEntries_OffersReauthorizeOnly_*`、VM `FailedPreview_*` 三例 |
| AC-LSB-3 撤销→注册顺序与幂等 | **MET** | `Reauthorize_RevokesEverySamePathEntryFirst_ThenRegistersExactlyOnce`（2 条 stale 均 generation+1/revoked、帧序 `list→revoke→revoke→register`、恰 1 条 active）、`Reauthorize_RepeatedExecution_KeepsExactlyOneActiveEntry`、`Reauthorize_UsesTheRegisteredRootString_NotTheCallerSpelling`；B2/B3 判别 |
| AC-LSB-4 部分失败 fail-closed | **MET** | `Reauthorize_RegisterFailure_ReportsRevokedNotReauthorized_WithNoRollback`（typed 码 + 「已撤销…未重新授权」+ 无回滚 + 可重试）、`Reauthorize_PartialOutcomeRetry_FinishesTheRegisterLegFromTheRevokedRoot`、VM `PartialFailure_ShowsRevokedNotReauthorized_AndStaysRetryable` |
| AC-LSB-5 不自动重授权 | **MET** | 计划/mint 路径零恢复命令（`PlanAndMintPath_NeverInvokesARecoveryCommand_OnlyTheExplicitActionDoes` 源码守卫）、`ReuseSelector_StillSkipsRevokedEntries_AndNeverFallsBackOnAFailedMint`、`Reauthorize_WithNothingToRevoke_WritesNothing`、B1 判别、真实 IPC 「failure 后 registry 长度不变」 |
| AC-LSB-6 授权面不扩大 | **MET** | `RecoveryMembers_LiveOnTheSeparatePort_AndNeverOnTheFrozenHostController`、`RecoveryMembers_AcceptNoPathOrOpaqueSourceArgument`、`RecoverySurface_AddsNoWireCommand_AndKeepsTheFrozenCommandCount`（`HostCommandRegistry.All.Count == 111` 冻结 + 无 recover/reauthor 命令）、`Reauthorize_UsesTheRegisteredRootString_*`；API inventory EXIT=0 |
| AC-LSB-7 脱敏 | **MET** | 全部 `SourceRecoveryText`/VM 文案断言无绝对路径 & 无 `quarantine`；`Reset_RequiresConfirmation_AndNeverSurfacesTheQuarantinePath`（脚本响应**带** `quarantine_path` 也不得泄漏）；真实 IPC「wire 无 quarantine、含路径帧仅 `RegisterSourceReadGrant` 基线、stderr 0 命中」；B4 判别 |
| AC-LSB-8 零漂移/门禁 | **MET** | 见 §2：build 0/0、pins 18/18、check PASS×2、API EXIT=0、scope PASS（禁止面全 ZERO_DIFF）、全量 pytest 3317/10、全量 .NET 1604/0/93 |
| AC-LSB-9 闭环证据 | **MET** | `logs/ipc-closed-loop.json`：phase A（同路径替换 → typed 失败 → 显式重授权 → 再预览成功 → 重新导入 Completed → `source_list_scan_targets` 返回新 registry/gen）；phase B（L-S4-A **原地刷新**：同 `location_id`、`registry_id` 换新、`last_verified_at` 非空、枚举 gen=1） |
| AC-LSB-10 边界/不夸大 | **MET** | 本文件 + Handoff §3 + 卡「已知 limitation」原文：仅 file-source 同路径恢复；folder（L-S4-2）/L-S4-1/B2/B3 保留；C-17 journal 撤销撕裂仅登记 |

## 5. 已知 limitation（closeout 必须保留）

- **B2 / B3 未做**：`source_list_roots` 可用性投影（需 C-16 v1.5）与扫描侧投影未做 → 多根健康/逐条管理不可见、扫描状态不可见。
- **L-S4-1**（零交互自动恢复枚举）仍开放（需 C-16 v1.5 批量载体）；**L-S4-2**（folder 身份键）未修 → 只承诺 **file-source 同路径恢复**；重定位（换路径）走「重新导入成新源」。
- **C-17 journal 撤销撕裂（仅登记，不处理）**：B1 给了用户第一个撤销入口；撤销后绑定旧 `registry_id` 的 C-17 apply/journal 重试会永久失败（锚 `HostOperationOrchestrator.cs:112-133`；scope review `:87/:249/:263`）。B1 不修复该影响面（需 B2/L-S4-B 批量设计），文案不承诺「重试自动恢复」。
- **`quarantine_path` 不显示**：`source_reset_registry` 响应里的绝对路径与 C-16 §7.3 冲突；本卡**不读、不返回、不渲染**该字段（契约面澄清留 UNFREEZE）。
- **同路径替换后的 Core 侧语义（如实登记）**：替换改变物理身份 → 重新导入会写**新的** `source_locations` 行（旧物理身份行仍在只读 Core 投影里，Host 调度器按撤销 registry fail-closed 丢弃）；L-S4-A 的**原地刷新**只在「同物理身份 + 新 registry」成立（IPC phase B 实测同 `location_id` 刷新）。**不宣称**替换场景也算「原地刷新」。
- **NOT_RUN**：无。本卡要求的 4 条门禁（build/定向/gated IPC/回归）+ 全量均实跑；无任何未运行项被写成 PASS。

## 6. 真实性声明

1. 本卡所有门禁数字都来自本文件 `logs/**` 的实跑输出（`delivery_head=0fdde2de8`），未把未跑项写成 PASS。
2. IPC 用例是**真实 Python Core stdio**（`C:/Python314/python.exe`，`sys.path` 指向本仓 `src`）：生产 `CoreServiceClient` → 生产 `HostCommandDispatcher`（Host-local 路由）→ 生产 `SourceReadCoordinator`/`SourceAccessRegistry` → 生产 `SourceImportCoordinator`/`SourceRecoveryCoordinator`；无 fake controller、无 in-process 替身。
3. phase B 的「registered root 身份不再匹配」用 **Passthrough protector 的隔离 registry** 改写条目录入的 volume/file id 来构造（文件本身不动）；这是**测试夹具**手段，用于命中 L-S4-A「同物理身份」的刷新分支；真实替换路径（文件物理身份变化）由 phase A 覆盖。两者都在本文件与 Handoff 明示。
4. 未修改 Host/CoreClient/`IHostController.cs`/Core/契约/STATUS/PLAN/LEDGER；未 push；未创建 worktree。
5. 独立 Review 由 Lead 指派（本实现会话不自审）。
