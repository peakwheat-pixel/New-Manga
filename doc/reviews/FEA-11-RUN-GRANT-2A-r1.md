---
task: FEA-11-RUN-GRANT-2A
title: FEA-11-RUN-GRANT-2A r1 独立 Review（生产版本通道 / 缓存矩阵 / 冷缓存 / R3-02 / 零漂移）
reviewer: fresh subagent（独立上下文；未参与实现/返修；只读被审 head）
session: fresh subagent（Lead 记录）
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: subagent
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
reviewed_head: a0bafc89ec74be08e3d6d721105639df01a140a7
verdict: approved
---

# FEA-11-RUN-GRANT-2A r1 独立 Review

> **结论先行：`approved`。P0=0 / P1=0 / P2=2（证据元数据 + 大目录覆盖上限，均不改变被审字节的 P0 修复正确性，见 §6）/ P3=6（非阻断观察）。AC-G1…AC-G8 全部 MET。**
>
> - **A（AC-G1 生产版本通道，P0）PASS**：Run 铸造的 `scope.version` 在**实现层只有一个来源**——`RunSourceRange.Resolve` 的 `identity.VersionId`（`HostRuntime.cs:1787-1799`），`target.Version` 在该函数内完全未使用；`new RunSourceScope` 全仓库生产端只有这一处。真实 IPC（不手工传 version，scan target 全为占位 `"1"`，`Fea11RunGrantIpcTests.cs:430-436`）我独立实跑 **4 passed**；自选破坏点 B1（版本回退 `"1"`）实跑 **RED**，失败消息为 Core 侧 `[SOURCE_ACCESS_DENIED] Run source-read authorization was refused`（`SourceReadCoordinator.AuthorizeRunAsync` ← `RunSourceAuthorizer.AuthorizeSliceAsync`），证明 Run 未 dispatch。
> - **B（AC-G2 缓存矩阵）PASS**：仅 `status=ok && 无 changed/added/missing/ambiguous` 可写入；`changed/encrypted/unsupported/missing/malformed/source_id 不匹配/entries 超界` 一律 **invalidate**（`SourceScanScheduler.cs:1750-1834` + `:1676-1704`）；有界 `MaxEntries=1024` / `MaxEntriesPerIdentity=4096` / `TTL=3600s`，`TryGet`/`Remember` 均裁剪（`:153-260`）；断言在 `SourceRegistryTests.cs:679-760`。B2 静态核对可信（`old` 片段唯一命中、目标用例存在、日志 RED+RESTORED）。
> - **C（AC-G3 冷缓存）PASS**：每切片最多 8 源、每源 1 次、30s 截止、`_onDemandGate` 串行化、失败/超时仅 warn 跳过；冷源只进 `ColdSources` 不铸造（`HostRuntime.cs:2032-2081`、`:1789-1794`）。用例 4 条（`SourceRegistryTests.cs:784-899`）；我独立复跑 B3、B4 **均 RED**。**判别 B3/B4 可信。**
> - **D（AC-G4 生产边界）PASS**：我在本机重跑的真实 IPC 见证（`G:\CODEX\New Manga.workspace\FEA-11-RUN-GRANT-2A\fixtures\ipc-e61e9a43…\run-grant-2a-version-channel.txt`）显示：`f1=svf1 entries=2`、`s1=sv1 entries=2`、`cold i1 -> on_demand_scans=1 cached=sv-img bound_pages=1`、image/folder/archive-first 三次 `resolve_page_resource` 全部 OK，archive second member → typed `SOURCE_ACCESS_DENIED`（L-G12② 保留）；卡/Handoff 未写「全场景可用/L-R1 全修」（卡 `:101-102`、Handoff `§3`）。
> - **E（AC-G5 managed 零回归）PASS**：RUN-GRANT-1 的 best-effort 用例全部保留并通过（`SourceRegistry` **29 passed**，基线 21，+8）；Core 面 `authorize_run_bindings` 对无 binding 的 managed 页 `continue`（`src/infrastructure/resource_channel/source_read_refs.py:504-507`），冷源跳过也不改变该语义；定向 pytest **50 passed** 不变。
> - **F（AC-G6 R3-02）PASS**：`SourceRegistryTests.cs:900-940` 通过真实 `HostRuntime.AcceptRunAsync` 判别委托行（反射注入 warm authorizer，断言 frozen command=`reocr_all` 且 typed 码原样上抛）；我独立删除委托行 → **RED**（落到「Core unavailable」），恢复 sha 一致。**B5 可信。**
> - **G（AC-G7 零漂移/证据）PASS**：`git diff --name-status 1b6152112..a0bafc89e` = **5 文件，全部 ⊆ allowed_paths**（与 `changed-files.txt` 一致）；`doc/plan`/`doc/contracts`/`schema.py`/`core_assembly.py`/依赖/`NewManga.App` 在该区间 **零 diff**；`CORE_PROTOCOL_MINOR=3`；Run wire 键集（`grant_ids/command/scope → bound_pages`）未改；`verify_pins` **18/18 PASS**、`check.ps1`（默认 + `-TaskPath`）**PASS(3 warnings)**、API inventory **EXIT=0**；EV **21/21 sha256** 我用脚本全量复算一致。
> - **H（AC-G8 不夸大/回归）PASS**：无测试删除/弱化（被删行均以「+ identities」形式保留原断言）；无新增 skip（新 IPC 用例复用既有 `NEWMANGA_FEA11_IPC` opt-in，skip 总数 89→90 的解释成立）；无未登记 wire/schema/依赖变更；日志只含计数/类型名，无路径泄密（IPC 自带 `wire/stderr path leak -> 0`）。残留问题见 §6（2 个 P2 + 6 个 P3）。
> - **范围注**：任务给出 `HEAD=5c95d96f2`；本次复核开始时共享工作树的 `HEAD` 已被并发会话推进到 **`44965532f`**（`29365bf3c`、`44965532f`，均为 `FEA-11-RUN-GRANT-2B-PREREQ-1` 的 closeout 文档提交）。这**不改变被审字节**：5 个实现/测试文件与 `a0bafc89e` 逐字节一致，`5c95d96f2..HEAD` 的全部差异都在 2B-PREREQ-1 的 `doc/plan`/`doc/reviews`/`doc/tasks`/`verification` 面。本报告以 `a0bafc89e` 的实现/测试字节 + `5c95d96f2` 的卡/Handoff/证据字节为准。

---

## 0. 复核对象、方法与边界

- 仓库 `G:\CODEX\New Manga`，`main`；复核开始 `HEAD=44965532f49ed3a1d325c88488c906607396efd8`（`git rev-parse` 实测），工作树仅有并发会话的 `doc/handoffs/DSH-PROGRESS-2026-11-07.md` 变更（非本卡面；我未触碰）。
- **只读事实以 `a0bafc89ec74be08e3d6d721105639df01a140a7` 的实现/测试字节为准**：复核前后两次 `git diff --stat a0bafc89e -- <5 个 scope 文件>` 均为空；sha256 与 `EV.md §5.1` 一致（`HostRuntime.cs 51dcd654…`、`SourceReadCoordinator.cs fb48aa2f…`、`SourceScanScheduler.cs c450b7c8…`、`Fea11RunGrantIpcTests.cs 4cb7238e…`、`SourceRegistryTests.cs 2b7ba4ba…`）。
- **本卡 scope 按自有 commit 链 `1b6152112..a0bafc89e` 计算**（`aa0a5562b` + `a0bafc89e`）；共享工作树同期落地的 `d8dcfc07a`（C-16 v1.4 UNFREEZE）/`923ce00fd`（其 closeout）/`29365bf3c`/`44965532f` **不属于本卡**，未计入、未修改、未引用为 2A 证据。
- 本 Review **未参与**该卡实现、返修、证据生成或 Handoff 编写；未 `git add`/`commit`/`push`；未修改实现/测试/证据/卡/契约；唯一仓库写入为本文件。
- **破坏性复跑**（4 次：B5/B4/B1/B3）：每次先把原文件**原始字节**备份到 `G:\CODEX\New Manga.workspace\FEA-11-RUN-GRANT-2A\review-r1\`，破坏 → 构建 → 只跑一个目标用例 → 恢复原始字节 → sha256 复核 → 重构；结束后 `git status --porcelain` 与复核前完全一致（仅并发会话那一个文件），`HostRuntime.cs` 仍是 `51dcd654…`。明细见 §4。
- 未运行 `verification/FEA-11-RUN-GRANT-2A/tools/discrimination.py` 全脚本（它会重写被审的 `logs/discrimination.log`）；改为静态逐点核对 6 个破坏点 + 独立复现 4 个（B1/B3/B4/B5）。
- **未重跑全量 pytest/.NET**（按任务约定由 Lead 实跑）：我核对 `logs/full-pytest.log`（`3281 passed, 10 skipped`，`EXIT=0`）与 `logs/full-dotnet.log`（逐程序集相加 = **1559 passed / 0 failed / 90 skipped**，`EXIT=0`）与 Handoff/EV/卡一致；定向门禁全部由我独立实跑（见 §5）。
- 运行副作用：真实 IPC 用例在仓外 `G:\CODEX\New Manga.workspace\FEA-11-RUN-GRANT-2A\fixtures\` 新增了若干 `ipc-<guid>` 夹具目录（未入库、不改写 `RESOURCE-MANIFEST.json` 的原始快照）；未写入真实用户数据/AppData/外部卷。

### 0.1 本 Review 实跑命令与结果（全部实测）

| # | 命令 | 实测结果 |
|---|---|---|
| 1 | `dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~SourceRegistry"` | **29 passed / 0 failed / 0 skipped**，EXIT=0 |
| 2 | `$env:NEWMANGA_FEA11_IPC=1; dotnet test … --filter "FullyQualifiedName~Fea11RunGrant"` | **4 passed / 0 / 0**，EXIT=0（4 s） |
| 3 | 同上但不设 env | **4 skipped / 0 / 0**，EXIT=0 |
| 4 | `C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | **50 passed** in 4.55s |
| 5 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `PIN AUDIT: PASS (all 18)`，EXIT=0 |
| 6 | `pwsh -NoProfile -File tools/governance/check.ps1`（默认） | `Governance check: PASS (3 warnings)`，EXIT=0 |
| 7 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-RUN-GRANT-2A.md` | `Governance check: PASS (3 warnings)`，EXIT=0 |
| 8 | `C:/Python314/python.exe tools/generate_api_inventory.py --check` | `EXIT=0`（rendered counts match FEA-C07） |
| 9 | EV.md 逐文件 sha256 复算（脚本 `review-r1/verify_ev.py`） | **rows=21 / OK=21 / MISMATCH=0 / MISSING=0**；`EV.md` 自身 sha256=`fd1b87eb49eb…` |
| 10 | `git diff --name-status 1b6152112..a0bafc89e` | **全区间只有 5 个 `M` 条目，全部 ⊆ allowed_paths**（因此 `doc/plan`、`doc/contracts`、`schema.py`、`core_assembly.py`、`src/**`、Python `tests/**`、依赖（`pyproject`/`requirements`/`*.csproj`）、`NewManga.App/**` 均零 diff） |
| 11 | `CORE_PROTOCOL_MINOR`（`src/bootstrap/core_service.py:320`） | `PROTOCOL_MINOR = 3`（`1b6152112` 与 `a0bafc89e` 两端一致）；C# `CoreProtocol.DefaultMinor = 3` |
| 12 | 判别性静态核对（6 个 `old` 片段 / 目标用例 / 日志 restore sha） | **6/6 `old` 各出现 1 次**；restore sha 与现行文件一致；`result=PASS breaks=6`、`final_rebuild exit_code=0` |
| 13 | **破坏性复跑 B5/B4/B1/B3**（备份→破坏→构建→目标用例→恢复→sha） | **4/4 RED_AS_EXPECTED**；4 次恢复 sha 全部 `51dcd654…` 一致；`final_rebuild=0` |
| 14 | `RESOURCE-MANIFEST.json` 核对（脚本） | 有效 UTF-8、中文完整、`file_count=76`、`fixtures/` 20 个抽样 sha 全匹配；**`delivery_head` 字段 = `923ce00fd…`（见 R2A-01）** |
| 15 | 真实 IPC 见证文件抽查（我自己运行产生的 `fixtures/ipc-e61e9a43…/run-grant-2a-version-channel.txt`） | `f1=svf1 entries=2`、`s1=sv1 entries=2`、`cold i1 -> on_demand_scans=1 cached=sv-img bound_pages=1`、image/folder/archive-first `resolve` OK、archive second member `SOURCE_ACCESS_DENIED`、path leak 0 |

---

## 1. 判定摘要

| 项 | 判定 |
|---|---|
| P0 | **0** |
| P1 | **0** |
| P2 | **2**（R2A-01 Manifest `delivery_head` 元数据错误；R2A-02 >4096 entry 源永不入缓存 + L-G8 措辞不覆盖该形态；均为文档/覆盖边界，不改变被审字节的 P0 修复） |
| P3 | **6**（R2A-03…R2A-08，非阻断，见 §6） |
| A. AC-G1 生产版本通道 | **PASS** |
| B. AC-G2 缓存矩阵 | **PASS（有 P3 残差 R2A-03）** |
| C. AC-G3 冷缓存 | **PASS（有 P3 精度观察 R2A-04）** |
| D. AC-G4 生产边界 | **PASS（有 P2 覆盖上限 R2A-02）** |
| E. AC-G5 managed 零回归 | **PASS** |
| F. AC-G6 R3-02 | **PASS** |
| G. AC-G7 零漂移/证据 | **PASS（Manifest 元数据见 R2A-01）** |
| H. 回归/新问题 | **PASS（无未登记行为变更；残差见 §6/§7）** |

### 1.1 AC 判定（MET / PARTIAL / NOT_MET）

| AC | 判定 | 关键依据 |
|---|---|---|
| **AC-G1** 生产版本通道（P0） | **MET** | 唯一来源 `identity.VersionId`（`HostRuntime.cs:1787-1799`；生产端 `new RunSourceScope` 仅此一处）；真实 IPC 4 passed；B1/B6 判别（B1 我独立复现 RED，失败于 Core typed 拒绝 → Run 未 dispatch） |
| **AC-G2** 缓存新鲜度/来源 | **MET** | `ReadSourceIdentity` 矩阵 + `ApplySourceIdentity`（`:1750-1846`）；`changed/missing/encrypted/unsupported/malformed/source 不匹配/超界` → invalidate；上界/TTL/断言齐备（`SourceRegistryTests.cs:679-760`）；B2 记录可信 |
| **AC-G3** 冷缓存策略 | **MET** | 8 源/切片、1 次/源、30s、串行 gate、失败/超时跳过不阻断；4 条用例 + B3/B4（我独立复现均 RED） |
| **AC-G4** 生产口径可用边界 | **MET** | 我本机真实 IPC：image 单 entry + folder 逐成员 + 归档首成员均 resolve OK；归档第 2 成员 typed `SOURCE_ACCESS_DENIED`；卡/Handoff/EV 明确「2B/L-R1 未闭环」（卡 `:101-102`、Handoff `§3`） |
| **AC-G5** managed 零回归 | **MET** | RUN-GRANT-1 best-effort 用例全保留（`SourceRegistry` 29 passed）；Core managed 页 skip（`source_read_refs.py:504-507`）；定向 pytest 50 passed 不变 |
| **AC-G6** R3-02 收口 | **MET** | `SourceRegistryTests.cs:900-940` 判别真实 `AcceptRunAsync` 委托行；删除委托 → RED（我独立复现） |
| **AC-G7** 零漂移 | **MET** | scope=5 全 ALLOWED；零漂移面全空；`PROTOCOL_MINOR=3`；Run wire 未改；pins 18/18；check×2 PASS；API inventory EXIT=0 |
| **AC-G8** 门禁/证据/不夸大 | **MET** | EV 21/21 sha 全匹配；全量数字与 Lead/日志一致；卡/Handoff 未宣称「全场景可用/L-R1 全修」；skip 无新增条件（+1 为既有 opt-in） |

> 说明：AC-G8 的 MET 指其**字面要求**（EV 每文件 sha256+commit、Handoff limitations、不夸大）全部满足；Manifest 的 `delivery_head` 字段错误不在 AC-G8 字面范围内，单列为 R2A-01（P2）要求 closeout 修正。

---

## 2. 必做核对 A–H 逐项

### A. AC-G1 生产版本通道（P0）— PASS

1. **唯一来源**：`RunSourceRange.Resolve` 只在 `identities.TryGet(target.SourceId, …)` 成功且 `VersionId` 非空时构造 `RunSourceScope(…, identity.VersionId)`（`HostRuntime.cs:1787-1799`）；`target.Version` 在该函数内**完全未被使用**（`grep target.Version HostRuntime.cs` 零命中；`"1"` 仅命中注释与 `RegisterSourceScanTarget` 的默认参数 `:173`）。生产端 `new RunSourceScope` 在 `apps/desktop-avalonia/src` 只命中这一处（`HostRuntime.cs:1795`；另一条 grep 命中是 `SourceReadCoordinator.cs:136` 的 `AuthorizeRunAsync(` 方法签名，不是铸造点）。
2. **常量 `"1"` 不在 Run 铸造路径**：`"1"` 仍存在于两处——(a) `HostRuntime.RegisterSourceScanTarget(..., string version = "1")` 的默认参数（`:169-183`，**scan target** 的占位版本，被 `ScanAsync` 用于**扫描 grant** 的 `scope.version`，见 R2A-05）；(b) 冷启动枚举目标 `SourceScanScheduler.cs:2179` 的 `"1"`。两者都不是 Run mint 的版本来源；`RunSourceRange` 对 `target.Version` 零引用。**结论：铸造路径无常量回退。**
3. **真实 IPC 不手工传 version**：`Fea11RunGrantIpcTests.ProductionScanVersionChannelDrivesImageFolderAndArchiveFirstMember`（`:366-536`）构造 3 个 scan target 时显式写 `"1"` 并 `Assert.All(targets, target => Assert.Equal("1", target.Version))`（`:430-436`）；缓存里的 `sv-img`/`svf1`/`sv1` 全部来自真实 `ScanSourceSync` 响应（`:441-456` 对 `f1`/`s1` 断言等于 seed receipt 的 Core 提交版本；冷 `i1` 走 1 次 on-demand 扫描后 `:485-486` 断言 `sv-img`）。随后 `authorize → bound_pages=1 → resolve_page_resource` 三源成功（`:487-508`），归档第 2 成员 typed 拒绝（`:510-518`）。
4. **实跑**：我独立执行 `$env:NEWMANGA_FEA11_IPC=1; dotnet test … --filter "FullyQualifiedName~Fea11RunGrant"` → **4 passed**（未设 env → **4 skipped**，skip 原因仍是既有 `NEWMANGA_FEA11_IPC` 门控，未新增 skip 条件）。
5. **判别性**：我自选 B1（把 `identity.VersionId` 改回 `"1"`）→ 目标 IPC 用例 **RED**，失败消息 `NewManga.CoreClient.Wire.CoreOperationException : [SOURCE_ACCESS_DENIED] Run source-read authorization was refused`，栈为 `SourceReadCoordinator.AuthorizeRunAsync ← RunSourceAuthorizer.AuthorizeSliceAsync` —— 即授权阶段被 Core typed 拒绝、Run 未 dispatch（§4）。

### B. AC-G2 缓存矩阵 — PASS（P3 残差 R2A-03）

- **写入门**：`ReadSourceIdentity` 依次拒绝 `malformed_result` / `source_id_mismatch` / `status_<x>` / `changed`（`totals.added/missing/changed/ambiguous > 0`）/ `version_missing` / `entries_missing` / `entry_malformed` / `entries_over_bound`（`SourceScanScheduler.cs:1750-1831`）；`ApplySourceIdentity` **cacheable → Remember，否则 Forget**（`:1837-1846`）；`ProjectScanResult` 对 malformed/无 `source` 的响应也先 `Forget`（`:1676-1704`）。→ 只缓存 `status=ok && 无变更`。
- **矩阵覆盖**：`SourceScanResponseRefreshesTheCacheOnlyWhenUnchangedAndOk`（`SourceRegistryTests.cs:711-760`）逐项断言 ok+unchanged 可缓存、`changed` 覆盖会使断言失败、`missing/encrypted/unsupported` 各自 `Reason` 与 **invalidate**、`other` source_id 不缓存、`version_missing`/`entries_missing`/`entry_malformed` 拒绝。
- **有界**：`MaxEntries=1024`、`MaxEntriesPerIdentity=4096`、`DefaultTtlSeconds=3600`；`Remember` 满时按 `CapturedAt` 淘汰最旧、超 per-source 界直接拒写；`TryGet`/`PruneExpired` 均裁剪（`SourceScanScheduler.cs:153-260`）；`SourceIdentityCacheIsBoundedAndPrunesExpiredEntries`（`:679-709`）断言非法输入拒绝、TTL 裁剪、上界 1024 与 per-source 4096。→ **有界且可断言**。
- **判别 B2 可信（静态）**：`B2` 的 `old` 片段在现行文件恰好出现 1 次；目标用例存在；日志 `RED_AS_EXPECTED` + `RESTORED sha256=c450b7c8…` 与现行文件一致（我未复现 B2，但静态链完整）。
- **P3 残差 R2A-03**：`totals` **整体缺失**时 `ParseTotals` 返回 `null`，`if (ParseTotals(value) is { HasChange: true })` 不命中 → 该响应被当作「无变更」缓存，与类注释 `SourceScanScheduler.cs:145`「ONLY … whose totals report no change」及卡 S-4 的字面不一致（详见 R2A-03）。

### C. AC-G3 冷缓存 — PASS

- **编排**：`ResolveWithColdCacheAsync`（`HostRuntime.cs:2032-2081`）先解析出冷源；`budget = min(cold, MaxOnDemandScansPerSlice=8)`；超预算先 warn `on_demand_budget_exhausted`；`_onDemandGate` 串行化并发切片；每个冷源在 `_identities.TryGet` 复查后**至多 1 次** `_onDemandScan`，`CancelAfter(OnDemandScanTimeout=30s)`；调用方取消原样上抛（不吞）；超时/异常 → warn 后继续下一个；结束后重新 `Resolve` 并用刷新后的冷源数回报。
- **冷源不铸造**：`RunSourceRange.Resolve` 对无 identity 的源 `cold.Add(target); continue;`（`:1789-1794`），绝不 `target.Version`。
- **不阻断**：`targets.Count == 0` 时直接 `return`（`:1996-2000`），dispatcher 继续 dispatch；`RunAuthorizerSkipsColdCacheSourcesAndStillReachesDispatch`（`:784-812`）用真实 `HostCommandDispatcher` 断言到达 dispatch（`SidecarErrorCode.ProcessExited`）且 `authorizeCalls=0`——**我独立复现 B3 后该用例 RED**，证明「删掉 cold 分支改铸占位版本」会被判别。
- **每源至多 1 次**：`RunAuthorizerPerformsOneBoundedOnDemandScanPerColdSource`（`:813-847`）断言第一次切片 1 次、第二次切片 0 次（warm）；**B4（`Take(0)`）我独立复现 RED**。
- **预算显式**：`RunAuthorizerOnDemandScanBudgetIsExplicitAndBounded`（`:848-875`）断言恰好 8 次扫描、`on_demand_budget_exhausted=4`、`cold_sources=12`、`on_demand_attempts=8`。
- **失败不阻断**：`RunAuthorizerOnDemandScanFailureIsASkipNotABlock`（`:876-899`）注入 `IOException` → 仍到达 dispatch、`authorizeCalls=0`。
- **P3 精度观察 R2A-04**：30s 是协作式取消截止（`CancelAfter`），Host 侧 grant 铸造里的 `SHA256.HashData(stream)`（`SourceReadCoordinator.cs:348`）**不可取消**，所以单次 on-demand 扫描可能超过 30s；「每切片 8×30s」不是硬上界（见 R2A-04）。

### D. AC-G4 生产口径可用边界 — PASS

- 我在本机重跑的真实 IPC 见证（见 §0.1 #15）逐条复现：`sv-img` 冷源 1 次 on-demand；`svf1`/`sv1` 来自周期扫描路径；image/folder/archive-first 的 `resolve_page_resource` 全部 OK；archive 第 2 成员 **typed** `SOURCE_ACCESS_DENIED`。
- 卡面/Handoff/EV 均写明「生产版本常量已修，但 2B/L-R1 未闭环」（卡 `:101-102`、Handoff `§3`、EV `§4.1`/`§7`）；未出现「全场景可用」「L-R1 全修」。
- **P2 覆盖上限 R2A-02**：`MaxEntriesPerIdentity=4096` 低于扫描默认 `max_entries=10000`（`SourceScanScheduler.cs:160` vs `:326`），>4096 成员的 folder 源可以正常扫描但**永不入缓存**，Run 永远走冷路径（每 Run 1 次全量扫描且不铸造）。AC-G4 的 IPC 用 2 成员 folder，未覆盖该形态；卡/Handoff 也未登记该上限。详见 R2A-02。

### E. AC-G5 managed 零回归 — PASS

- RUN-GRANT-1 的 best-effort 用例全部保留：`RunAuthorizationBestEffortSkipReachesDispatch_CoreRefusalDoesNot`、`RunAuthorizerTreatsMintFailuresAsBestEffortSkips`、`RunAuthorizerSkipsWhenTheCapabilityIsMissingWithoutMinting`、`RunAuthorizerSkipsWhenTheRegistryCannotBeRead`（`SourceRegistryTests.cs:298-478`）——我实跑 `SourceRegistry` **29 passed**。
- Core 面 managed 语义未变：`authorize_run_bindings` 对 `binding is None` 的页 `continue`（`src/infrastructure/resource_channel/source_read_refs.py:504-507`），因此冷源跳过/版本陈旧都不会把 managed 页判成不可授权；只有 referenced 页才会 typed 拒绝。
- 定向 pytest `tests/core/test_host_control.py tests/fea11/test_source_run_grant.py` **50 passed**（我实跑），与基线一致。
- 新增的冷缓存/扫描失败用例额外覆盖「不阻断 dispatch」，未见 managed 读/metadata 变化。

### F. AC-G6 R3-02 — PASS

- 实现：`AcceptRunAsync`（`HostRuntime.cs:79-92`）在写策略检查后**无条件** `await AuthorizePreparedRunForAcceptAsync(_preparedSlices, _runAuthorizer, preparedRunId, ct)`，再走 Core `AcceptRunAsync`；seam（`:101-114`）从 `_preparedSlices.Take` 取冻结 `{command, scope}` 并调 `AuthorizePreparedRunAsync`。
- 判别用例：`SourceRegistryTests.cs:900-940` 用反射构造未启动的 `HostRuntime`、写入 `_policy`/`_runAuthorizer`（warm cache）、以真实 `AcceptRunAsync` 触发冻结 slice 授权，断言 `CoreOperationException.Code == "SOURCE_ACCESS_DENIED"` 且 authorizer 收到 `reocr_all`。
- **我独立复现 B5**（删除 `AuthorizePreparedRunForAcceptAsync` 委托行）→ 目标用例 **RED**，恢复后 sha 一致（§4）。

### G. AC-G7 零漂移/证据 — PASS

- **scope**：`git diff --name-status 1b6152112..a0bafc89e` = `M` 5 文件，与 `changed-files.txt`（5 行）与卡 `allowed_paths` 完全对应；`out_of_scope=[]`。
- **零漂移面**：同一区间内 `doc/plan`、`doc/contracts`、`src/infrastructure/sqlite/schema.py`、`src/bootstrap/core_assembly.py`、`pyproject.toml`、`requirements.txt` **全部空 diff**；`CORE_PROTOCOL_MINOR=3`（`core_service.py:320`，两端一致）。
- **Run wire**：`SourceReadCoordinator.AuthorizeRunAsync` 的 host-control 帧仍是 `grant_ids[] + command + scope`，响应仍要求 `bound_pages`（`:185-201`）；本卡 diff 只新增了空 version 拒绝（`:312-318`），键集未变，与 C-16 §2.4 一致。
- **治理**：`verify_pins` 18/18 PASS；`check.ps1` 默认与 `-TaskPath` 均 `PASS (3 warnings)`；`generate_api_inventory.py --check` EXIT=0（以上均为我实跑）。
- **证据**：EV 21 行 sha256 全量复算 **21/21 匹配**；`scope-validation.log` 的 `changed=5 全 ALLOWED`、`zero-drift 全空`、`protocol_minor=3` 与我的独立 git 结果一致；`logs/discrimination.log` 的 6 个破坏点 `old` 片段唯一命中、restore sha 与现行文件一致、`final_rebuild exit_code=0`。
- **共享工作树披露**：`scope-validation.log` 的 shared-worktree note 与 Handoff `§2` 如实披露并发 2B-PREREQ-1 会话；2A 的 diff 按自有 commit 链计算，**该披露可接受且必要**。

### H. 回归/新问题 — PASS（无未登记行为变更；残差见 §6/§7）

- 未发现授权放宽、静默放行、数据破坏、未登记 wire/schema/依赖变更；未发现测试删除或断言弱化（`git show` 的删除行均为「等价重建 + 新增 identities 参数」）。
- 日志安全：新增日志只含计数与异常类型名（`cold_sources/on_demand_attempts/on_demand_scan timed out/skipped code=`），`SourceIdentity.ToString()` 只输出 `SourceIdentity(<source_id>)`（`SourceScanScheduler.cs:136`），不输出 version/entries；IPC 自带 `wire/stderr path leak -> 0`。
- 并发/成本：`_onDemandGate` 串行化冷填充（并发 Run 会排队）；on-demand 扫描绕过 scheduler 的 single-flight/backoff/status，可能与周期扫描重复（成本，非正确性）；已由 L-G8（延伸）部分登记。
- 新的「陈旧窗口」与「大目录上限」两个行为面已在 R2A-02/R2A-06 登记建议；均 fail-closed（Core 仍拒绝错误的 version/entry），不产生错误数据。

---

## 3. AC-G1…G8 逐条判定（简表）

| AC | 判定 | 一行证据 |
|---|---|---|
| AC-G1 | MET | `identity.VersionId` 唯一来源；IPC 4 passed；B1 RED（Core typed 拒绝，未 dispatch） |
| AC-G2 | MET | 仅 ok+unchanged 写入，其余 invalidate；1024/4096/3600s；2 条断言用例；B2 可信（静态） |
| AC-G3 | MET | 8/切片、1/源、30s、gate、失败/超时跳过；4 条用例；B3/B4 我独立 RED |
| AC-G4 | MET | 真实 IPC image/folder/archive-first OK；archive 第 2 成员 typed 拒绝；未夸大 |
| AC-G5 | MET | RUN-GRANT-1 用例全保留；managed 页 Core skip；pytest 50 passed |
| AC-G6 | MET | 真实 `AcceptRunAsync` 委托行判别；B5 我独立 RED |
| AC-G7 | MET | 5 文件 ⊆ allowed；零漂移面空；minor=3；wire 未改；pins/check/API 全 PASS |
| AC-G8 | MET | EV 21/21；全量数字一致；skip 无新增；未写全场景可用/L-R1 全修 |

---

## 4. 破坏性复跑记录

**备份**：`G:\CODEX\New Manga.workspace\FEA-11-RUN-GRANT-2A\review-r1\{B1,B3,B4,B5}-HostRuntime.cs.orig`（仓外、原始字节、未入库）。**复跑前**：`HEAD=44965532f`，`git status` 仅并发会话的 `doc/handoffs/DSH-PROGRESS-2026-11-07.md`；`HostRuntime.cs sha256=51dcd654…`。

| # | 破坏点（对被审字节） | 目标用例 | 构建 | 用例结果 | 恢复 | 恢复后 sha256 |
|---|---|---|---|---|---|---|
| B5 | 删除 `AcceptRunAsync → AuthorizePreparedRunForAcceptAsync` 委托行（`HostRuntime.cs:88-89`） | `AcceptRunAsyncDelegatesToTheAuthorizationSeam` | exit 0 | **RED (exit=1)** | 原字节写回 | `51dcd654…` ✔ |
| B4 | `Foreach cold … Take(budget)` → `Take(0)`（`HostRuntime.cs:2052`） | `RunAuthorizerPerformsOneBoundedOnDemandScanPerColdSource` | exit 0 | **RED (exit=1)** | 原字节写回 | `51dcd654…` ✔ |
| B1 | `identity.VersionId` → `"1"`（`HostRuntime.cs:1798`） | IPC `ProductionScanVersionChannelDrivesImageFolderAndArchiveFirstMember` | exit 0 | **RED (exit=1)** | 原字节写回 | `51dcd654…` ✔ |
| B3 | 删除冷源跳过，改用 `target.Version` 铸造（`HostRuntime.cs:1789-1794`） | `RunAuthorizerSkipsColdCacheSourcesAndStillReachesDispatch` | exit 0 | **RED (exit=1)** | 原字节写回 | `51dcd654…` ✔ |

- **B1 失败原因（单独捕获）**：
  ```
  NewManga.CoreClient.Wire.CoreOperationException : [SOURCE_ACCESS_DENIED] Run source-read authorization was refused
    at NewManga.Host.Sources.SourceReadCoordinator.AuthorizeRunAsync(...)
    at NewManga.Host.RunSourceAuthorizer.AuthorizeSliceAsync(...)
    at NewManga.Host.Tests.Fea11RunGrantIpcTests.ProductionScanVersionChannelDrivesImageFolderAndArchiveFirstMember()
  ```
  → 判别点正是「版本不再是 Core 权威值 → Core typed 拒绝 → Run 不 dispatch」，与 AC-G1 的判别口径一致。
- **恢复与最终状态**：4 次恢复后 `HostRuntime.cs` 均为 `51dcd654c981ca36a8e532268c894555c8af7c8ea1f245a92ac2a638ee805b31`（与 `EV.md §5.1` 一致）、`SourceScanScheduler.cs` 未被本 Review 触碰（`c450b7c8…`）；最终 `dotnet build NewManga.sln -c Release` **exit 0**；`git status --porcelain` 与复核前一致（仅并发会话那一个文件），`git diff a0bafc89e -- <5 scope 文件>` 为空。
- **B2/B6 未独立复现**（静态核对）：`B2`/`B6` 的 `old` 片段在现行文件各出现 **1 次**，目标用例存在，日志 `RED_AS_EXPECTED` + restore sha 与现行字节一致；可采信实现者记录。我独立复现的 4 个（B1/B3/B4/B5）与日志同口岸（HostRuntime.cs）的 restore sha 完全一致。

---

## 5. 证据与门禁实测（与 Lead/日志交叉核对）

| 场景 | 我实测 | 日志/Handoff 记载 | 一致性 |
|---|---|---|---|
| SourceRegistry | **29 passed / 0 / 0** | 29 passed（基线 21，+8） | 一致 |
| 真实 IPC（`NEWMANGA_FEA11_IPC=1`） | **4 passed**；未设 env **4 skipped** | 4 passed；不设 env 4 skipped | 一致 |
| 定向 pytest | **50 passed** | 50 passed | 一致 |
| 全量 pytest | 未重跑 | `3281 passed, 10 skipped, EXIT=0`（log 尾行） | Lead 实跑，我核对日志 |
| 全量 .NET | 未重跑 | 逐程序集相加 **1559 / 0 / 90，EXIT=0**（Host.Tests 212/59、App.Tests 720/7 等） | 与 Handoff/卡 `1559/0/90` 一致；基线 `1551/0/89` 的 +8/+1 解释成立（+8 单测、+1 新 IPC opt-in skip，`full-dotnet.log` 可见该用例 `[SKIP]`） |
| pins | **18/18 PASS** | 18/18 PASS | 一致（当前含 C-16 v1.4，C16 pin `ad25fb3c89bb` 与 2A 门禁日志相同；2A 区间无契约改动） |
| check（默认 / `-TaskPath`） | **PASS(3 warnings) ×2** | PASS(3 warnings) ×2 | 一致 |
| API inventory | **EXIT=0** | EXIT=0 | 一致 |
| scope diff | **5 文件全 ALLOWED** | 5 文件全 ALLOWED | 一致 |
| EV sha256 | **21/21 匹配** | 21 行 | 一致 |
| 判别性 | 6 个 `old` 各 1 次；restore sha 对齐；**4/6 独立 RED** | 6/6 RED + RESTORED + rebuild 0 | 一致（B2/B6 静态采信） |

**Manifest 核对**：`RESOURCE-MANIFEST.json` 有效 UTF-8（中文完整、无 U+FFFD），`file_count=76`，`fixtures/` 20 个抽样 sha256 与磁盘一致；但 top-level `delivery_head` = `923ce00fd52c3bd15e3ea588853d4c2152a73ea2`（见 R2A-01）。

---

## 6. Findings

| ID | 级别 | 文件/行 | 事实与影响 | 复现证据 | 最小修复 | 阻断 |
|---|---|---|---|---|---|---|
| **R2A-01** | **P2** | `verification/FEA-11-RUN-GRANT-2A/RESOURCE-MANIFEST.json:6`（及 `:11`）；`EV.md:116`；`tools/gen_manifest.py:83/98` | Manifest 的 `delivery_head` 写成 **`923ce00fd…`**（生成时的 `git HEAD`，实为 **2B-PREREQ-1 的 closeout 提交**），不是本卡 `delivery_head=a0bafc89e…`；`source_path` 与 EV `:116` 的「该 JSON 同时记录 delivery_head」会误导集成方把 2A 交付指向另一个卡的 commit。 | `C:/Python314/python.exe` 读 JSON：`delivery_head=923ce00fd…`；对照卡 `:17`/EV `:10`/`:157`。生成器 `_git_head()` 语义即 repo HEAD。 | closeout 时把该字段改为 `a0bafc89ec74be08e3d6d721105639df01a140a7`（或把字段重命名为 `repo_head_at_generation` 并另加 `delivery_head`），同步 EV `:116` 措辞；**不改被审实现/测试字节**。 | 否（证据元数据；closeout 必须修正） |
| **R2A-02** | **P2** | `SourceScanScheduler.cs:160`（`MaxEntriesPerIdentity=4096`）与 `:326`（`DefaultMaxEntriesPerSource=10000`）；`HostRuntime.cs:2032-2081`；Handoff `§3` L-G8 行 | 扫描允许 10000 条目，但身份缓存上限 4096；**4097…10000 成员的 folder 源永远无法入缓存**（`ReadSourceIdentity` 返回 `entries_over_bound` → invalidate）。后果：该源每个 Run 都触发 1 次 on-demand 全量扫描（Host 端逐成员 SHA-256 + Core 端扫描）却永不铸造；Handoff L-G8「周期扫描正常时缓存已暖，走不到该路径」对该形态**不成立**。AC-G4 的 IPC 只用 2 成员 folder，未暴露此上限。 | 代码对照 `:160`/`:326`/`:1825-1828`（`entries_over_bound` 分支）；on-demand 每次重扫路径（`:2032-2081`）。 | 二选一：(a) 把 `MaxEntriesPerIdentity` 调到与配置 `max_entries` 一致（内存需评估，约数 MB/源，1 万成员量级；该改动会改变交付字节，需新 head + 复审）；(b) 保持 4096，但在卡/Handoff/EV 的 L-G8 行**显式登记**「>4096 成员源不缓存、每 Run 重扫且不铸造」的边界（纯文档，可 closeout 完成）。 | 否（fail-closed；不产生错误授权，属覆盖/成本边界） |
| **R2A-03** | P3 | `SourceScanScheduler.cs:1778`（`ParseTotals(value) is { HasChange: true }`）与 `:1852-1865`（`ParseTotals` 在 `totals` 缺失时返回 `null`） | `totals` 整体缺失的 `status=ok` 响应会被当作「无变更」缓存，违反类注释 `:145`「whose totals report no change」的字面 fail-closed 语义；只有 Core 违反 C-17（不发 totals）时才可达，且缓存的仍是 Core 自己返回的 version、Core 授权仍会校验，故无越权/数据风险。 | 代码对照；`ReadSourceIdentity` 无 `totals_missing` 分支；现有矩阵用例不构造该形态。 | 在 `ReadSourceIdentity` 增 `ParseTotals(value) is null → Reject("totals_missing")`（一行），补矩阵用例；或改注释使其与实现一致。 | 否 |
| **R2A-04** | P3 | `HostRuntime.cs:2049-2073`（`CancelAfter(30s)`）；`SourceReadCoordinator.cs:348`（`SHA256.HashData(stream)` 不可取消） | 30s 是**协作式取消截止**，不是硬上界：on-demand 扫描在 Host 侧 grant 铸造（逐成员同步哈希，受 `maxBytes`/`maxEntries` 约束但不受 token 约束）阶段无法被打断，单源可超 30s；切片最坏也不是严格 8×30s。Run dispatch 会同步等待该阶段（L-G8 已承认成本，但「8×30s」措辞偏乐观；page 作用域的 managed Run 也会触发对全部已知源的冷填充）。 | 代码对照：token 仅在 `_gate.WaitAsync` 与 Core `SendHostControlAsync` 处被观察；`SHA256.HashData` 无 token 参数。 | 在 L-G8 行把「每切片 8 源 × 30s」改为「8 源；每源 30s 协作式截止，Host 端铸造哈希不受其约束，最坏为源大小线性」；如要硬界，需在 mint 循环中加入协作取消（新 head）。 | 否 |
| **R2A-05** | P3 | `HostRuntime.cs:169-183`（默认 `version = "1"`）；`SourceScanScheduler.cs:1534`（`_sources.IssueAsync(..., target.Version, ...)`）与 `:2179`（枚举目标 `"1"`）；`SourceReadCoordinator.cs:377` | 生产**扫描 grant** 的 `scope.version` 仍是被捏造的 `"1"`（pre-2A 遗留，Core 的 `ScanSourceSync` 不校验它，IPC 扫描成功即为证）；它不是 Run mint 的回退，但与卡 S-5/EV 的「禁止常量回退」措辞相邻，独立读者可能误以为生产 grant 中已无占位版本；若未来 Core 校验扫描 grant 的 version，扫描会断。 | `grep target.Version` 仅命中扫描路径；`IssueLockedAsync` 把该值写入 `scope.version`（`:377`）。 | 在卡/Handoff 明确「禁止常量」只约束 Run mint；登记该扫描 grant 残留（或缓存命中时用缓存 version 铸扫描 grant，属 2B/后续）。 | 否（pre-existing，非本卡引入） |
| **R2A-06** | P3 | `SourceScanScheduler.cs:1676-1704`（仅 `ProjectScanResult` 路径 invalidate）；`HostRuntime.cs:42`（TTL 1h）；`SourceScanScheduler.DefaultIntervalSeconds=900` | 缓存只在扫描响应时刷新：re-import 提交新版本、或源文件被外部修改后、下一次扫描前，缓存仍是旧 version → Run 铸造旧版本 → Core typed 拒绝（fail-closed，无错误数据）。窗口 = 下一轮扫描（默认 ≤900s，>8 源时按轮转更久）或 TTL 到期后的冷填充，最长约 1h。另有早退扫描路径（registry 不可解析、无基线 missing、budget deferred）不 invalidate，但 Run 侧会因 mint 失败跳过（同样 fail-closed）。 | 代码对照；Host 无 apply/import 后 `Forget` 的钩子；`ProjectScanResult` 之外的 return 分支见 `:1515-1527`/`:1541-1543`/`:1658-1663`。 | 登记为新 limitation（或并入 L-G15 残差）；若 `SourceOperationCoordinator` 的 apply 成功路径可回调，则 `identities.Forget(sourceId)`（小改，需新 head）。 | 否 |
| **R2A-07** | P3 | `HostRuntime.cs:1519-1540`；`SourceRegistryTests.cs:900-940`；`SourceReadCoordinator.cs:312-318`；`SourceScanScheduler.cs:506-512` | 覆盖残差：(a) 生产 `CreateRunSourceAuthorizer` 的接线（`identities`/`onDemandScan`）**没有被测试绑定**——IPC 用例自行重建同形 authorizer，B5 用例注入的是替身 authorizer；接线错误只能靠代码评审发现。(b) `on_demand_scan timed out` 分支、`_onDemandGate` 串行化、空 version 拒绝（`:312-318`）均无判别用例（超时无注入 seam）。(c) scope review 风险 6 要求「同一 source_id 只铸 1 个 Run grant」的显式断言不存在；实现上 `TargetSnapshot` 是 source_id 键字典（`:506-512`）故结构上不可能重复，但无测试。 | 静态检索 + 测试清单核对。 | 可选补：反射调用 `CreateRunSourceAuthorizer` 断言非空依赖 / 用短超时 seam 测 timeout / 增加 source_id 唯一性断言；不要求本轮返修。 | 否 |
| **R2A-08** | P3 | `SourceScanScheduler.cs:130-137`（`SourceIdentity` 含 `Entries`）与 `:153-260`（缓存） | 2A **缓存了 `entries[]` 但没有任何消费方**（仅测试读取）；上界乘积 1024×4096 可达数百万条 locator 字符串，无字节预算。这是为 2B 预留的数据，但 2A 已为其支付内存且扩大了 Core 可控数据的常驻面。 | `grep "\.Entries"`：生产端无读取（仅 IPC 用例断言 entries）。 | 2A 可只缓存 version（entries 留给 2B），或把 `MaxEntriesPerIdentity` 压小并登记；若保留，建议在 L-G8 注明内存上界。 | 否 |

> 说明：不存在 P0/P1；R2A-01/R2A-02 是两个 P2，均为**证据/覆盖边界**，不影响被审字节的授权正确性。若 Lead 选择「改常量 4096→10000」处理 R2A-02，则交付字节改变、本 Review 结论只对 `a0bafc89e` 有效，需对新 head 复审。

---

## 7. 回归与新问题（H 的展开）

- **未登记的行为变化**：未发现。Run wire（`grant_ids/command/scope → bound_pages`）、`CORE_PROTOCOL_MINOR`、schema/迁移、依赖、`NewManga.App/**` 全部零 diff；`SourceReadCoordinator` 仅新增空 `source_id/version` 拒绝（`INVALID_REQUEST`），生产两个调用点（扫描 `target.Version="1"`、Run `identity.VersionId` 非空）都满足该守卫，无合法路径被挡。
- **测试卫生**：删除的测试行全部是「等价重建 + 传入 identities」；无新增 skip 条件（新 IPC 用例复用既有 opt-in 属性 `Fea11RunGrantIpcFact`，skip 总数 89→90 已解释）；未把 L-G15 修复误写成 L-R1 全修——卡 `:101-102`、Handoff `§3`、EV `§4.1`/`§7` 均明确 deny。
- **扫描缓存副作用**：on-demand 扫描不入 scheduler 状态（`SourceScanStatus` 看不到）、与周期扫描可能重复（成本）；`_onDemandGate` 使并发 Run 串行等待；page 作用域 Run 会对全部已知源做冷填充（含 managed-only 场景）——均由 L-G8 部分覆盖，精度问题见 R2A-04。
- **日志泄密**：新增日志只含计数/异常类型名；`SourceIdentity.ToString` 只输出 source_id；IPC 断言 `wire/stderr path leak -> 0`（我重跑的见证文件亦为 0）。
- **潜在产品面**：`>4096` 成员 folder 的覆盖上限（R2A-02）与陈旧窗口（R2A-06）应在 closeout 写进 L-G8/L-G15 残差，避免后续被当成「folder 全量可用」。

---

## 8. 最终 verdict

**`approved`。**

- 被审 head `a0bafc89ec74be08e3d6d721105639df01a140a7` 的实现/测试字节：**P0=0、P1=0**，AC-G1…AC-G8 全部 **MET**；生产版本通道（L-G15 的 Run 面）已由真实 IPC + 独立破坏性复跑证明可判别，且无常量回退。
- 定向门禁、pins/check/API inventory、EV 21/21、scope 5 文件零漂移、6/6 判别点静态链与 4/6 独立 RED，全部一致；全量数字与 Lead/日志一致。
- **两个 P2 需在 closeout（或集成前）处理**：R2A-01 修正 `RESOURCE-MANIFEST.json` 的 `delivery_head`（纯文档，可关闭）；R2A-02 二选一——文档登记 >4096 成员源边界，或改常量并走新 head 复审。在该两处按上述方式关闭前，不建议把 2A 写成「folder 全量可用」；其余 6 个 P3 为非阻断观察。
- 集成建议：Lead 可将 `a0bafc89e` 纳入集成；closeout 时保留 L-G12②/L-R1 未闭环与 L-G1/L-G2/L-G8/L-G9/L-G10/L-G13/L-G14；本 Review 不代替 Lead 的 Review Appointment/集成验证与 push 决策。

---

## 9. 真实性声明

- 本报告是 fresh 上下文独立只读 Review：未参与 `FEA-11-RUN-GRANT-2A` 的实现、测试、证据生成或 Handoff 编写；与实现会话无共享上下文；事实以 `a0bafc89e` 的实现/测试字节与 `5c95d96f2` 的卡/Handoff/证据字节为准。
- 唯一仓库写入是本文件 `doc/reviews/FEA-11-RUN-GRANT-2A-r1.md`。未修改实现/测试/证据/卡/契约/STATUS/PLAN/LEDGER；未 `git add`/`commit`/`push`；未删除、移动或归档任何 tracked 文件。
- 破坏性复跑 4 次（B5/B4/B1/B3）：每次先备份原始字节到仓外 `review-r1/`，目标用例实跑（B1 为真实 IPC），随后**按原始字节写回**并 sha256 复核 `51dcd654…` 一致，最终 `dotnet build NewManga.sln -c Release` exit 0；复核后 `git status --porcelain` 与复核前一致（仅并发会话的 `doc/handoffs/DSH-PROGRESS-2026-11-07.md`，非本 Review 写入）。
- 运行副作用：仓外 workspace 的新增 IPC 夹具目录与本次复核的备份/核对脚本；未改写任何 tracked 证据；未运行会重写 `logs/discrimination.log` 的全脚本。
- 未重跑全量 pytest/.NET（按任务约定由 Lead 实跑并在文中明确）；全量数字来自日志尾行/逐程序集求和与 Handoff/EV 的交叉核对，未以静态判断冒充实测。
- 本报告所有「实测」均有命令与结果记录；未执行项（B2/B6 复现、全量套件、discrimination.py 全脚本）已明确标注。
