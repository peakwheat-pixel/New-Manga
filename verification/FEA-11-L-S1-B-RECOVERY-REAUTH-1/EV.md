# FEA-11-L-S1-B-RECOVERY-REAUTH-1 Canonical Evidence（B1：App 显式恢复/重授权入口；App-only、零契约、0/18 pins）

> 结论先行：本卡给产品装上**第一个显式**的根级恢复入口，并且只做 App 侧接线。产品内原本**没有任何**恢复路径：被替换/缺失根的**同路径重导入永久失败**（复用选择器只按「同 registry 路径串 + 非 revoked」挑条目，被替换条目永远排在复用位置；Host mint 侧逐请求重核根身份 → typed `SOURCE_REGISTRY_UNAVAILABLE`），`source_revoke_root`/`source_register_root`/`source_reset_registry` 在 App 侧 **0 调用**。本卡新增：①`ISourceImportController` 的**恢复面**（只读诊断探针 + 显式重授权 + 显式重置，**无任何路径/registry_id 入参**）；②`SourceRecoveryModels.cs` 编排（**先只读探针分流** → 文件级只给「重置」/根级只给「重授权」/其它码不给动作；重授权 = **先撤销该路径全部非撤销 stale 条目、再按条目已登记 `roots[0]` 注册一次**、部分失败 fail-closed 可重试、重复执行恒 1 条 active）；③ImportDock 的**两个显式命令** + 二次确认 + 脱敏文案（叶子名/typed 码/计数，**不显示 `quarantine_path`**）。**红线 R-1 保持**：mint/导入路径一行未改语义（复用选择器抽出为纯函数、语义逐字不变），任何错误分支**都不**调用 revoke/register/reset。
>
> **r1 返修（本 head）**：**P2-01** 恢复面改为**单源归因**（`SourceImportCoordinator.LastPlanFailureSource` → `AttributeFailedSource` → 唯一 target；批量/歧义在任何 wire 调用前被拒绝、健康源零撤销/零注册；folder 源拒绝并给出说明）；**P2-02** gated IPC 的「含路径帧仅 RegisterSourceReadGrant」空转断言改为真实断言（wire 存储前已脱敏为 `[REDACTED]`，可验证事实是 **fixture 根路径 0 命中 + `[REDACTED]` 帧存在**）；P3-01/02/03/04/05/06/07/08/09/10/11 逐项处置（见 §7）。**不夸大**：只承诺 **file-source 同路径恢复**；folder 身份键（L-S4-2）、零交互自动恢复枚举（L-S4-1，需 C-16 v1.5）、B2（roots 可用性投影）/B3（扫描侧投影）**仍开放**；撤销会让绑定旧 `registry_id` 的 C-17 journal 重试永久失败——**仅登记，不处理**。

| 项 | 值 |
|---|---|
| task | `FEA-11-L-S1-B-RECOVERY-REAUTH-1`（冻结卡 `doc/tasks/FEA-11-L-S1-B-RECOVERY-REAUTH-1.md`；卡面 `status` 未改，仍为 `ready`） |
| Owner | `l-s1b-impl`（DSH Agent Teams teammate；Lead `lead`） |
| base | 卡 `base_commit=3d97e3b18`；实现起点 `e0b37622b`（工作树 clean，实测）；首轮交付 head `0fdde2de8`（docs `710e749a9`） |
| 本次 delivery_head | `e9e1132a55d8a04617b7e69e9f93f043e08f450b`（r1 修复 `019feeb6e` + r1 测试 `e9e1132a5`；r1 卡/Handoff/证据为同批文档提交） |
| 首轮交付 | `0fdde2de8`（实现 `be3b0c242` + 测试 `0fdde2de8`）+ docs `710e749a9`；r1 审查 approved with P2/P3 |
| 独立 Review | r1 `doc/reviews/FEA-11-L-S1-B-RECOVERY-REAUTH-1-r1.md`：**approved（P0=0/P1=0/P2=2/P3=11）**；本 head 处置 P2×2 + P3×11 |
| 分支/工作树 | `main` / `G:\CODEX\New Manga`（未创建 linked worktree、未 push） |
| 隔离根 | `G:\CODEX\New Manga.workspace\FEA-11-L-S1-B-RECOVERY-REAUTH-1\`（IPC 夹具 `fixtures/ipc-*`、判别性备份 `tmp/discrimination/`、全量日志）；**未写** `verification/FEA-09/**` |
| 契约字节 | **零变更**：`doc/plan/**`、`doc/contracts/**` 零 diff；C-16 仍 v1.4（pin `ad25fb3c89bb`）；`CORE_PROTOCOL_MINOR=3` |
| C-07 API inventory | **零变更**（`generate_api_inventory.py --check` EXIT=0）：恢复成员只在 `ISourceImportController`，不在 `IHostController` |
| 依赖/schema | **零新增** |
| 解释器/环境 | Windows 11 / PowerShell 7.6.8 / CPython 3.14.6 / .NET SDK（net9.0） |

## 1. 交付 commit 链（起点 `e0b37622b` → delivery_head `e9e1132a5`）

```text
e9e1132a5 test(fea-11-l-s1b): r1 P2-01 multi-select/folder/attribution discriminators + P2-02 real wire assertion
019feeb6e fix(fea-11-l-s1b): r1 P2-01 per-source recovery attribution + P3-04/P3-07/P3-11 fail-closed wording
710e749a9 docs(fea-11-l-s1b): 首轮交付卡/Handoff/证据（r1 基线）
0fdde2de8 test(fea-11-l-s1b): 首轮测试 + gated 真实 IPC 闭环（首轮 delivery_head）
be3b0c242 feat(fea-11-l-s1b): App 显式恢复/重授权入口（首轮实现）
ac528828b docs(progress): 记录 L-S1-B1 裁决（并发 Lead docs-only 提交，非本卡字节）
e0b37622b （本卡实现起点，工作树 clean）
```

## 2. 门禁实测（均真跑；`delivery_head=e9e1132a5`）

| Gate | 命令 | 结果 | 日志 |
|---|---|---|---|
| 构建（AC-LSB-8） | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` | **成功 0 warning / 0 error（EXIT 0）** | `logs/build.log` |
| VM/编排级（AC-LSB-1/2/3/4/5/6/7） | `dotnet test .../NewManga.App.Tests --filter "FullyQualifiedName~SourceRecovery"` | **PASS 43 / 0 failed / 0 skipped** | `logs/app-unit.log` |
| gated 真实 IPC（AC-LSB-9） | `NEWMANGA_FEA11_IPC=1 dotnet test .../NewManga.Host.Tests --filter "FullyQualifiedName~SourceRecoveryIpc"` | **PASS 1 / 0 / 0**；隔离 receipt `logs/ipc-closed-loop.{json,txt}`（**wire_path_hits=0 / wire_redacted_frames=7 / wire_frame_count=77**） | `logs/host-ipc.log` |
| 定向 Core 回归（AC-LSB-8） | `python -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | **PASS 74 passed**（基线 74，不降） | `logs/feature.log` |
| 全量 Python（AC-LSB-8） | `python -m pytest tests -q` | **PASS 3317 passed / 10 skipped**（= 基线 3317/10，零漂移） | `logs/full-pytest.log` |
| 全量 .NET（AC-LSB-8） | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` | **PASS 1613 / 0 failed / 93 skipped**（首轮基线 1570/0/92：**+43** 本卡 App 测试、**+1** 新增 opt-in IPC skip） | `logs/full-dotnet.log` |
| 治理（AC-LSB-8） | `verify_pins.ps1` / `check.ps1`（默认 + `-TaskPath`）/ `generate_api_inventory.py --check` | **PIN AUDIT PASS（18/18）** / **PASS(3 warnings)** ×2 / **EXIT=0** | `logs/gates-governance.log` |
| 范围（AC-LSB-8） | scope 校验（见 `scope-validation.log`） | **PASS**：全变更路径 ALLOWED、forbidden=0、禁止面 11 项 ZERO_DIFF、`CORE_PROTOCOL_MINOR=3`；1 项并发非交付显式标注 | `scope-validation.log`、`changed-files.txt` |
| 判别性（AC-LSB-1/3/5/7 + r1 P2-01） | `discrimination.ps1`（5 破坏点 → 1 目标用例变红 → 原字节恢复） | **5/5 RED_AS_EXPECTED + 5/5 RESTORED（sha256 一致）+ final rebuild EXIT 0** | `logs/discrimination.log` |

**数字口径（诚实记录）**：
- 全量 .NET **1613/0/93**：基线 **1570/0/92**；差额 = **+43**（本卡 `FullyQualifiedName~SourceRecovery` 43 例，全在 `NewManga.App.Tests` 程序集）+ **+1 skipped**（新增 gated IPC 用例在未设 `NEWMANGA_FEA11_IPC=1` 时 skip）。
- 全量 pytest **3317/10** = 卡基线，**零 Python 改动**；跑后 `git checkout -- verification/FEA-09` → CLEAN。
- 已知 flaky `FluentResidual2VisualEvidenceTests` **本次未命中**（全量 1613/0 无失败），未重跑凑绿。
- **P3-10（r1）**：gated IPC 夹具在 `NEWMANGA_FEA11_IPC != 1` 时 `InitializeAsync` 直接返回，不再为 skipped 用例启动真实 Core。

## 3. 判别性验证（5 破坏点；删掉/改坏实现必须变红）

`discrimination.ps1` 对**已提交字节**做一次最小破坏 → 构建 → 只跑**一个**目标用例 → 必须失败 → 按原字节恢复并复核 sha256 → 最后重建。实测全部 `RED_AS_EXPECTED` + `RESTORED`：

| Case | 破坏点 | 目标用例 | 实测 |
|---|---|---|---|
| **B1**（AC-LSB-1/5 安全核心） | 把 `ReauthorizeSourceAsync()` 挂进**预览失败分支**（= 自动重授权） | `FailedPreview_ExplicitReauthorize_OnlyOffersThatOneAction_AndWritesNothingYet` | **RED_AS_EXPECTED + RESTORED** |
| **B2**（AC-LSB-3） | 只撤销**首条**同路径 stale 条目（`stale.Take(1)`） | `Reauthorize_RevokesEverySamePathEntryFirst_ThenRegistersExactlyOnce` | **RED_AS_EXPECTED + RESTORED** |
| **B3**（AC-LSB-3） | **先注册后撤销**（顺序反转） | 同上 | **RED_AS_EXPECTED + RESTORED** |
| **B4**（AC-LSB-7） | 读取并渲染响应的 `quarantine_path`（绝对路径泄漏） | `Reset_RequiresConfirmation_AndNeverSurfacesTheQuarantinePath` | **RED_AS_EXPECTED + RESTORED** |
| **B5**（r1 P2-01） | 把恢复改回「对**全部选中** sources 执行」（`targets.Skip(1)` 批量重授权） | `Reauthorize_RefusesABatchBeforeAnyWireCall` | **RED_AS_EXPECTED + RESTORED** |

> **P3-09（r1）**：日志为最终一次**干净重跑**（头部注明：早期 B4 探索性注入曾产生不可达代码 `INVALID_BUILD_FAILED`，已改为可达注入后重跑）；最终块 sha256 与交付字节一致。

## 4. AC 矩阵（测试 → 证据映射）

| AC | 判定 | 关键测试/证据 |
|---|---|---|
| AC-LSB-1 入口仅显式 | **MET** | `FailedPreview_ExplicitReauthorize_OnlyOffersThatOneAction_AndWritesNothingYet`（失败后 `SourceReauthorizeCalls=0`/`SourceResetCalls=0`；仅 1 次只读探针）+ 真实 IPC `registry_unchanged_after_failure=true` + 判别 B1 |
| AC-LSB-2 分流正确 | **MET** | `FileLevelProbeFailure_OffersResetOnly_AndWritesNothing`、`OtherProbeCode_OffersNoRecoveryAction_AndDisplaysOnlyThatCode`、`CoreSideFailureOrAnotherPreviewCode_OffersNothing_AndNeverProbes`、`ReadableStorage*`；**r1 P2-01**：`MultiSelectionBlocked_OffersNoAction_AndNeverProbes`（批量/歧义 → 无动作、连探针都不发）+ VM `MultiSelectionBlocked_ShowsTheSingleSelectionHint_AndOffersNoAction`；**r1 P3-04**：`FolderTarget_OffersNoAction_AndTheActionRefuses` |
| AC-LSB-3 撤销→注册顺序与幂等 | **MET** | `Reauthorize_RevokesEverySamePathEntryFirst_ThenRegistersExactlyOnce`（帧序 `list→revoke→revoke→register`）、`Reauthorize_RepeatedExecution_KeepsExactlyOneActiveEntry`（active 恒 1；revoked 行累积已登记 limitation）、`Reauthorize_UsesTheRegisteredRootString_*`；判别 B2/B3 |
| AC-LSB-4 部分失败 fail-closed | **MET** | `Reauthorize_RegisterFailure_*`（typed 码 + 「已撤销…未重新授权」+ 无回滚 + 可重试）、`Reauthorize_PartialOutcomeRetry_*`、`Reauthorize_RevokeFailure_AbortsBeforeAnyRegistration`、`RecoveryTransportFailures_BecomeTypedResults_AndNeverEscapeIntoTheUi`、VM `PartialFailure_*`；r1 P3-11 文案改为「已确认撤销 N 条（ACK 失败可能多一条持久化撤销）」 |
| AC-LSB-5 不自动重授权 | **MET** | 计划/mint 路径零恢复命令守卫、`ReuseSelector_*`、`Reauthorize_WithNothingToRevoke_WritesNothing`、真实 IPC「失败后 registry 长度不变」；**r1 P2-01**：`AttributeFailedSource_TargetsOnlyTheFailingSource_AndNeverABatch`、`Reauthorize_RefusesABatchBeforeAnyWireCall`、`AttributedFailure_LeavesTheHealthySiblingCompletelyUntouched`、`PlanAttribution_RemembersTheExactFailingSource_*`；判别 B1/B5 |
| AC-LSB-6 授权面不扩大 | **MET** | `RecoveryMembers_*`（不在 `IHostController`、参数仅 `bool`/`CancellationToken`）、`RecoverySurface_AddsNoWireCommand_AndKeepsTheFrozenCommandCount`（`HostCommandRegistry.All.Count == 111` 冻结）、`Reauthorize_UsesTheRegisteredRootString_*`；API inventory EXIT=0 |
| AC-LSB-7 脱敏 | **MET** | 文案/VM 全文本 0 绝对路径 & 0 `quarantine`；`Reset_RequiresConfirmation_AndNeverSurfacesTheQuarantinePath`（脚本响应**带** `quarantine_path` 也不得泄漏）；**r1 P2-02 真实断言**：wire **77 帧** fixture 根路径 **0 命中**、`[REDACTED]` 帧 **7**（证明脱敏实际发生）、wire `quarantine` 0、stderr 0；判别 B4 |
| AC-LSB-8 零漂移/门禁 | **MET** | 见 §2：build 0/0、pins 18/18、check PASS×2、API EXIT=0、scope PASS（禁止面全 ZERO_DIFF）、全量 pytest 3317/10、全量 .NET 1613/0/93 |
| AC-LSB-9 闭环证据 | **MET** | `logs/ipc-closed-loop.json`：phase A（同路径替换 → typed 失败 → 显式重授权 → 再预览成功 → 重新导入 Completed → `source_list_scan_targets` 返回新 registry/gen）；phase B（L-S4-A **原地刷新**：同 `location_id`、`registry_id` 换新、`last_verified_at` 非空、枚举 gen=1） |
| AC-LSB-10 边界/不夸大 | **MET** | 本文件 §5 + Handoff §3 + 卡「已知 limitation」：仅 file-source 同路径恢复；多选/歧义**不给恢复**（须单选）；folder 不给动作；revoked 行累积；C-17 journal 撤销撕裂仅登记 |

## 5. 已知 limitation（closeout 必须保留）

- **B2 / B3 未做**：`source_list_roots` 可用性投影（需 C-16 v1.5）与扫描侧投影未做。
- **L-S4-1**（零交互自动恢复枚举）仍开放（需 C-16 v1.5）；**L-S4-2**（folder 身份键）未修 → 只承诺 **file-source 同路径恢复**；重定位（换路径）走「重新导入成新源」。
- **多选/歧义不给恢复（r1 P2-01 语义）**：恢复面**只针对唯一失败来源**；一批选择若无法唯一归因，不提供动作、不探针、不写注册表，只在 UI 提示「请只选择一个来源重新预览」。
- **folder 源不给恢复（r1 P3-04）**：folder 根进入恢复面时被拒绝并给出说明（本卡只承诺 file-source；folder 身份键 L-S4-2 另案）。
- **重复显式恢复会累积 revoked 行（r1 P3-03）**：registry 只置位不删除（Host 既有行为）；每次重复恢复新增一条 revoked 行 + 一条 active，**active 恒 1**（「幂等」口径 = 恰 1 条 active，不是无副作用）。
- **revoke ACK 失败的计数口径（r1 P3-11）**：Host 先持久化撤销再等 Core ACK；ACK 失败时 App 的计数只含已确认成功的条目，文案写明「已确认 N 条（实际可能多一条）」；无回滚。
- **C-17 journal 撤销撕裂（仅登记，不处理）**：撤销后绑定旧 `registry_id` 的 C-17 apply/journal 重试会永久失败（`HostOperationOrchestrator.cs:112-133`；scope review `:87/:249/:263`）；需 B2/L-S4-B 批量设计。
- **`quarantine_path` 不显示**：`source_reset_registry` 响应里的绝对路径与 C-16 §7.3 冲突；本卡**不读、不返回、不渲染**。
- **真实 `HostController` 恢复接缝无端到端测试（r1 P3-05，接受）**：`HostController` 需要可启动的 HostRuntime/sidecars；本卡以**生产代码级**单测覆盖 pin 分支（`SourceImportCoordinator.LastPlanFailureSource` 实测、`AttributeFailedSource` 矩阵）与真实 IPC 预览失败链路，`HostController` 的 pin 生命周期剩余部分由静态审查覆盖；登记接受。
- **同路径替换后的 Core 侧语义（如实登记）**：替换改变物理身份 → 重新导入写**新的** `source_locations` 行（旧行留在只读投影，Host 调度器按撤销 registry fail-closed 丢弃）；L-S4-A 的**原地刷新**只在「同物理身份 + 新 registry」成立（IPC phase B 实测同 `location_id` 刷新）。**不宣称**替换场景也算「原地刷新」。
- **NOT_RUN**：无。本卡要求的门禁（build/定向/gated IPC/定向回归）+ 全量均实跑；无任何未运行项被写成 PASS。

## 6. 真实性声明

1. 本卡所有门禁数字都来自本文件 `logs/**` 的实跑输出（`delivery_head=e9e1132a5`），未把未跑项写成 PASS。
2. IPC 用例是**真实 Python Core stdio**（`C:/Python314/python.exe`，`sys.path` 指向本仓 `src`）：生产 `CoreServiceClient` → 生产 `HostCommandDispatcher`（Host-local 路由）→ 生产 `SourceReadCoordinator`/`SourceAccessRegistry` → 生产 `SourceImportCoordinator`/`SourceRecoveryCoordinator`；无 fake controller、无 in-process 替身。
3. phase B 的「registered root 身份不再匹配」用 **Passthrough protector 的隔离 registry** 改写条目录入的 volume/file id 来构造（文件本身不动）；这是**测试夹具**手段，用于命中 L-S4-A「同物理身份」的刷新分支；真实替换路径（文件物理身份变化）由 phase A 覆盖。两者都在本文件与 Handoff 明示。
4. **r1 P2-02 修正**：Core wire 日志在存帧前把绝对路径重写为 `[REDACTED]`（`WireLog.cs:84-88/139-140`），因此「哪些帧带路径」不可观测；本 head 断言的是可观测事实（**0 命中 + `[REDACTED]` 帧存在**），不再声称「含路径帧仅 RegisterSourceReadGrant」。
5. 未修改 Host/CoreClient/`IHostController.cs`/Core/契约/STATUS/PLAN/LEDGER；未 push；未创建 worktree。
6. 独立 Review 由 Lead 指派（r1 已由独立上下文完成；本实现会话不自审）。

## 7. Review r1 处置（append-only）

r1 报告：`doc/reviews/FEA-11-L-S1-B-RECOVERY-REAUTH-1-r1.md`，**approved（P0=0/P1=0/P2=2/P3=11）**。本 head（`e9e1132a5`）逐项处置：

| Finding | 等级 | 处置 |
|---|---|---|
| **R-P2-01** 多选恢复面过宽/归因错误 | P2 | **FIXED**：`SourceImportCoordinator.LastPlanFailureSource` 记录使预览中止的源；`SourceRecoveryCoordinator.AttributeFailedSource` 映射为**唯一 target**；`DiagnoseAsync` 对批量/歧义返回 `MultipleSources` 且**不发探针**；`ReauthorizeAsync` 在任何 wire 调用前拒绝批量（零撤销/零注册）；VM 显示「请只选择一个来源」提示、不给动作；判别 B5。测试：`AttributeFailedSource_*`、`MultiSelectionBlocked_*`、`Reauthorize_RefusesABatchBeforeAnyWireCall`、`AttributedFailure_LeavesTheHealthySiblingCompletelyUntouched`、`PlanAttribution_*`。 |
| **R-P2-02** wire-path 断言空转/措辞不实 | P2 | **FIXED**：删掉恒空的 `pathBearingCommands` 断言；改为 `wire_path_hits == 0` + `redactedFrames > 0`（证明脱敏实际发生）+ `quarantine` 0 + Host-local frame 白名单；IPC evidence 字段改为 `wire_path_hits=0` / `wire_redacted_frames=7` / `wire_frame_count=77`；EV/Handoff/卡面措辞同步（不再声称「仅 RegisterSourceReadGrant」）。 |
| **R-P3-01** 证据数字矛盾 | P3 | **FIXED**：EV/app-unit **43**、Handoff **+43**、禁止面 **11** 项、Manifest **3 新增 + 6 修改**。 |
| **R-P3-02** scope 快照早于卡面最终编辑 | P3 | **FIXED**：对**最终 docs commit** 重算 `scope-validation.log`/`changed-files.txt`（含 tracked 修改），changed_count 与卡面同一口径。 |
| **R-P3-03** 重复恢复累积 revoked 行 | P3 | **登记**：limitation 明确「active 恒 1 ≠ 无副作用幂等；revoked 行累积」。 |
| **R-P3-04** folder 进入同一恢复面 | P3 | **FIXED**：folder target 在诊断/动作两层都被拒绝（`FolderSource` block + `INVALID_REQUEST` 文案），文案与 file-source 承诺一致；测试 `FolderTarget_OffersNoAction_AndTheActionRefuses` + VM hint。 |
| **R-P3-05** 真实 HostController 接缝无测试 | P3 | **部分修复 + 登记接受**：生产代码级覆盖 `LastPlanFailureSource` 与 `AttributeFailedSource`；HostController 端到端需可启动 runtime，登记接受（见 §5）。 |
| **R-P3-06** View 按钮测试强度不足 | P3 | **FIXED**：两个 View 测试只通过 `Button.Command.Execute` 驱动，删除 VM 显式兜底调用，并在点击后断言 offer 被消费/outcome 已发布。 |
| **R-P3-07** `RecoveryOutcomeText` 新预览不清空 | P3 | **FIXED**：`ClearSourceRecoveryState` 清 outcome；恢复成功在自动重预览**之后**发布 outcome；测试 `NewPreviewClearsThePreviousRecoveryOutcome`。 |
| **R-P3-08** 卡面构建命令路径错误 | P3 | **FIXED**：卡面改为 `dotnet build apps/desktop-avalonia/NewManga.sln -c Release`。 |
| **R-P3-09** discrimination 日志早期失败块 | P3 | **FIXED**：日志改为一次干净重跑并加头部说明（早期 B4 探索性 `INVALID_BUILD_FAILED` 已废弃）；最终块 sha256 与交付字节一致。 |
| **R-P3-10** skip 时 fixture 仍启动 Core | P3 | **FIXED**：`InitializeAsync` 在 gate 关闭时直接返回（Dispose 亦短路），不再为 skipped 用例启动真实 Core。 |
| **R-P3-11** revoke ACK 失败计数少算 | P3 | **登记 + 文案改进**：失败文案改为「已确认撤销 N 条（若 Host 已持久化但 ACK 失败，实际可能多一条）」；行为保持 fail-closed 可重试；limitation 登记。 |
