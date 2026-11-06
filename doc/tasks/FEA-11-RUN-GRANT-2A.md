---
id: FEA-11-RUN-GRANT-2A
title: Host Run source 版本通道（ScanSourceSync 缓存 + 有界 on-demand 扫描；无 UNFREEZE）
kind: implementation
governance_version: 3
status: ready
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH」；`FEA-11-RUN-GRANT-2` 权威 scope review `doc/reviews/FEA-11-RUN-GRANT-2-scope-r1.md`（fresh subagent `22212d0c…`，**READY-WITH-UNFREEZE**；拆分口径：**2A Host-only = READY-TO-FREEZE，无需 UNFREEZE**；2B 容器成员 entry 需 C-16 v1.4）；Codex 裁决输入（`196dede9…`，建议 C-16 身份查询 1 pin）；DSH 裁决：采纳 scope review 拆分与 2A 零契约路径，Codex 方案作为被否决备选记录（见「DSH 裁决」）；R3-02 并入本卡；L-G1/2B 另卡
suggested_owner: codex
owner: run-grant-impl
reviewer: 独立上下文 fresh subagent（未参与实现/返修；只读交付 head；session 见 `doc/reviews/FEA-11-RUN-GRANT-2A-r1.md`）
depends_on:
  - FEA-11-RUN-GRANT-1
base_commit: 9ec4826d6
branch: null
worktree: null
integration_commit: null
delivery_head: a0bafc89ec74be08e3d6d721105639df01a140a7
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-RUN-GRANT-2A
allowed_paths:
  - doc/tasks/FEA-11-RUN-GRANT-2A.md
  - doc/reviews/FEA-11-RUN-GRANT-2A-*.md
  - doc/handoffs/FEA-11-RUN-GRANT-2A-*.md
  - verification/FEA-11-RUN-GRANT-2A/**
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11RunGrantIpcTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRegistryTests.cs
out_of_scope:
  - 容器成员 entry 通道（2B；需 C-16 v1.4 UNFREEZE）与 2B 相关 Core 改动
  - 长 Run 定期重铸/重绑（L-G1，另卡）；加密源（L-G2）；Core 重启（L-G9）；L-R11 gate 统一（L-G10）
  - 契约/schema/依赖/wire/错误码；`C-17 ScanTarget` 扩展；新 host-control 命令；`NewManga.App/**`；UI
  - 真实用户数据/AppData/外部卷/回收站；push
---

# FEA-11-RUN-GRANT-2A：Host Run source 版本通道

> **状态：`ready`（scope 冻结；无 UNFREEZE；依赖 RUN-GRANT-1 done）。**
> 来源：`FEA-11-RUN-GRANT-1` L-G12①（生产 Host `scope.version` 恒为 `"1"` → referenced Run 在 dispatch 前 100% 被 typed 拒绝）；scope review `doc/reviews/FEA-11-RUN-GRANT-2-scope-r1.md` 的 **2A** 切片。

## DSH 裁决（2026-11-07）

| # | 裁决 | 内容 |
|---|---|---|
| S-1 | **拆卡** | 2A（本卡，Host-only，零契约）先做；2B（容器成员 entry，C-16 v1.4）拆为 `FEA-11-RUN-GRANT-2B-PREREQ-1` + 实现卡；2C（长 Run 续期）另卡；R3-02 并入本卡。 |
| S-2 | **最小数据通道** | 采用 scope review 推荐：Host 缓存既有 `ScanSourceSync` 响应中的 Core 权威 `source.version_id` + `source.entries[]`（仅 `status=ok && changed=false`），冷缓存至多一次有界 on-demand 扫描；**不扩展 C-17 DTO、不新增 host-control 命令**（Codex 的 C-16 身份查询方案作为备选记录：其契约面更大，本卡不采纳）。 |
| S-3 | **P0 纠正** | 生产 Host version 恒 `"1"` 是**完全阻断**（不是「边界收窄」）；`FEA-11-RUN-GRANT-1` 卡面 L-G12① 措辞以 append-only Closeout 补充纠正并登记 **L-G15（生产版本常量阻断）**。 |
| S-4 | **缓存约束** | 仅缓存 `ok && !changed` 的权威值；`changed/encrypted/unsupported/missing` 不更新（不铸或 typed fail-closed）；仅内存、以 `source_id` 为键、有界（上界/过期裁剪可断言）；冷缓存每源至多 1 次有界扫描，失败跳过该源并继续 dispatch（best-effort，不阻断 managed-only）。 |
| S-5 | **禁止项** | 禁止 Host 自行推断 locator/ordinal（成员身份必须来自 Core 权威）；禁止常量回退；禁止把本卡写成「L-R1 修复」或「全场景可用」。 |
| S-6 | **R3-02** | 本卡补 `AcceptRunAsync → AuthorizePreparedRunForAcceptAsync` 委托行判别性测试（删委托 → RED）。 |

## In（冻结）

1. **Host 源身份缓存**（`SourceReadCoordinator`/`SourceScanScheduler`/`HostRuntime`）：从既有 `ScanSourceSync` 响应缓存 `source.version_id` + `entries[]`（Core 权威 locator/ordinal）；仅 `status=ok && changed=false`；内存、`source_id` 键、有界（与 R-8 同构上界/过期裁剪）。
2. **Run 铸造改用缓存版本**：`RunSourceRange` 用缓存 version（无缓存 → 有界 on-demand 扫描 ≤1 次/源；仍无 → 跳过该源，不阻断 Run；**不得**回退 `"1"`）。
3. **R3-02 收口**：`AcceptRunAsync` 委托行判别性测试。
4. **测试/证据/Handoff/卡面**：真实 IPC（不手工传 version）证明生产路径；判别性破坏点；EV/Manifest。

## Out

- 容器成员 entry 通道（2B）与任何契约/Core/UNFREEZE 改动；长 Run 续期；加密源；Core 重启；L-R11 gate；UI/App；schema/依赖/wire；真实用户数据；push。

## Acceptance Criteria（v3）

- [x] **AC-G1 生产版本通道（P0 判别核心）**：Host 铸造 `scope.version` 来自 Core 权威数据（`ScanSourceSync` 响应），禁止常量 `"1"`。判别性：回退为 `"1"` → 目标用例 RED（Core typed `SOURCE_ACCESS_DENIED`、Run 不 dispatch）。真实 IPC：seed 后不手工传 version，由生产路径取得；`authorize → bound_pages≥1 → resolve_page_resource` 成功。 <<MET>> 证据：`SourceIdentityCache`（`SourceScanScheduler.cs`）+ `RunSourceRange` 只取缓存 version（`HostRuntime.cs`；空 version mint 被 `SourceReadCoordinator` 拒绝）；真实 IPC `Fea11RunGrantIpcTests.ProductionScanVersionChannelDrivesImageFolderAndArchiveFirstMember`（scan 目标 Version 全为 `"1"`，缓存值 `sv1`/`svf1`/`sv-img` 全部来自真实 ScanSourceSync 响应；cold image → 1 次有界 on-demand 扫描 → `bound_pages=1` → resolve OK）；判别性 B1（回退 `"1"` → RED）、B6（scan→缓存断链 → RED）见 `verification/FEA-11-RUN-GRANT-2A/logs/discrimination.log`。
- [x] **AC-G2 缓存新鲜度/来源**：仅缓存 `status=ok && changed=false`；`changed/encrypted/unsupported/missing` 不更新（不铸或 typed fail-closed）；仅内存、`source_id` 键、有界上界与过期裁剪断言。判别性：允许 `changed` 覆盖 → RED。 <<MET>> 证据：`HostSourceScanExecutor.ReadSourceIdentity`/`ApplySourceIdentity`（仅 ok+unchanged 可缓存，其余一律 invalidate）；`SourceIdentityCache`（`MaxEntries=1024`、`MaxEntriesPerIdentity=4096`、`TTL=3600s`，`TryGet`/`Remember` 均裁剪）；用例 `SourceScanResponseRefreshesTheCacheOnlyWhenUnchangedAndOk`、`SourceIdentityCacheIsBoundedAndPrunesExpiredEntries`；判别性 B2（删除新鲜度门 → RED）。
- [x] **AC-G3 冷缓存策略**：缺失 → 每源至多 1 次有界 on-demand 扫描；超时/失败跳过该源并继续 dispatch（best-effort，不阻断 managed-only Run）；无限重试/静默占位版本 → RED。 <<MET>> 证据：`RunSourceAuthorizer.ResolveWithColdCacheAsync`（每切片最多 `MaxOnDemandScansPerSlice=8` 源、每源 `OnDemandScanTimeout=30s`、`_onDemandGate` 串行化并发切片、失败/超时仅 warn 跳过）；冷源只进 `ColdSources` 不铸造；用例 `RunAuthorizerSkipsColdCacheSourcesAndStillReachesDispatch`、`RunAuthorizerPerformsOneBoundedOnDemandScanPerColdSource`、`RunAuthorizerOnDemandScanBudgetIsExplicitAndBounded`、`RunAuthorizerOnDemandScanFailureIsASkipNotABlock`；判别性 B3（冷缓存回退占位 → managed Run 被阻断 RED）、B4（删除 on-demand 填充 → RED）；真实 IPC 的 cold image 源走生产 on-demand 路径。
- [x] **AC-G4 生产口径可用边界**：真实 IPC 证明 image 单 entry + folder（逐成员）+ 归档首成员在**生产版本通道**下可用；多成员容器其余页仍 typed fail-closed（2B 未修），卡/Handoff 不得写「referenced Run 全场景可用」。 <<MET>> 证据：真实 IPC `ProductionScanVersionChannelDrivesImageFolderAndArchiveFirstMember`（image/folder/archive-first-member 三源 resolve 全部 OK；archive second member → typed `SOURCE_ACCESS_DENIED`，L-G12② 边界保留）；见证文件 `G:\CODEX\New Manga.workspace\FEA-11-RUN-GRANT-2A\fixtures\ipc-*\run-grant-2a-version-channel.txt`（Resource Manifest 内）；卡/Handoff 明写「生产版本常量已修，但 2B/L-R1 仍未闭环」。
- [x] **AC-G5 managed 零回归**：沿用 RUN-GRANT-1 AC-R5（Core 面 managed skip；Host best-effort 不阻断；managed 读/metadata 零变化）。 <<MET>> 证据：RUN-GRANT-1 的 best-effort 用例全部保留并通过（`RunAuthorizationBestEffortSkipReachesDispatch_CoreRefusalDoesNot`、`RunAuthorizerTreatsMintFailuresAsBestEffortSkips`、`RunAuthorizerSkipsWhenTheCapabilityIsMissingWithoutMinting`、`RunAuthorizerSkipsWhenTheRegistryCannotBeRead`）+ 新增 `RunAuthorizerSkipsColdCacheSourcesAndStillReachesDispatch`（冷缓存不阻断 dispatch）与 `RunAuthorizerOnDemandScanFailureIsASkipNotABlock`；Core 面 managed 用例 `tests/fea11/test_source_run_grant.py` 50 passed 不变；全量 pytest/.NET 均不降（见 AC-G8）。
- [x] **AC-G6 R3-02 收口**：`AcceptRunAsync` 对 `AuthorizePreparedRunForAcceptAsync` 的委托行有判别测试；删除委托 → RED。 <<MET>> 证据：`SourceRegistryTests.AcceptRunAsyncDelegatesToTheAuthorizationSeam`（构造未启动 HostRuntime、注入 warm-cache authorizer、以真实 `AcceptRunAsync` 触发冻结 slice 授权 → typed `SOURCE_ACCESS_DENIED`；删除委托行后落到「Core unavailable」→ 用例 RED，判别性 B5）；原 seam 用例仍保留。
- [x] **AC-G7 零漂移**：`doc/plan`/`doc/contracts`/`schema.py`/依赖/`NewManga.App/**` 零 diff；`CORE_PROTOCOL_MINOR=3`；Run wire 键集不变；`verify_pins` 18/18；`check.ps1`（默认 + `-TaskPath`）PASS；API inventory EXIT=0；scope diff ⊆ allowed_paths。 <<MET>> 证据：`verification/FEA-11-RUN-GRANT-2A/scope-validation.log`（changed=5 全 ALLOWED；zero-drift surfaces 全 ZERO_DIFF；`protocol_minor=3 kept: YES`）、`changed-files.txt`；`logs/gates-governance.log`（PIN AUDIT PASS all 18 / Governance PASS(3 warnings) ×2 / API inventory EXIT=0）。**注**：本卡的零契约面按本卡自有 commit 链评估；同期 `FEA-11-RUN-GRANT-2B-PREREQ-1` 的 C-16 v1.4 UNFREEZE（commit `d8dcfc07a`）不属于本交付。
- [x] **AC-G8 门禁/证据/不夸大**：全量 pytest **不降**（基线 3281/10）、全量 .NET **不降**（1551/0/89）、定向 + 真实 IPC 实跑记录；EV 每文件 sha256 + commit；Handoff 保留 L-G1/L-G2/L-G8/L-G9/L-G12②/L-G13/L-G15，并明写「生产版本常量已修，但 2B/L-R1 仍未闭环」；不得表述为 L-R1 修复。 <<MET>> 证据：`logs/full-pytest.log`（3281 passed / 10 skipped）、`logs/full-dotnet.log`（1559 / 0 / 90；基线 1551/0/89，+8 单测 +1 opt-in IPC skip）、`logs/feature.log`（50 passed）、`logs/host-unit.log`（29 passed）、`logs/host-ipc.log`（4 passed）、`logs/discrimination.log`（6/6 RED + RESTORED + rebuild OK）；`EV.md` 逐文件 sha256；`doc/handoffs/FEA-11-RUN-GRANT-2A-a0bafc89e.md` limitations/未宣称；卡面未写「全场景可用/L-R1 全修」。

## 已知 limitation（预登记）

- **L-G12②（2B）**：多成员容器其余页仍 typed fail-closed；本卡不改。
- **L-G15（本卡修复对象，验证后仍保留历史登记）**：生产 Host version 恒 `"1"` → referenced Run dispatch 前 typed 拒绝（本卡修；修后需证据证明生产路径不再用常量）。
- L-G1（300s）、L-G2（加密）、L-G8（扫描/铸造 I/O 成本）、L-G9（Core 重启）、L-G10（L-R11）、L-G13（flaky）；L-R1 **未全修**。

## 测试要求

| 场景/AC | 命令或步骤 | 预期 | 证据 |
|---|---|---|---|
| AC-G1…G5 定向 | `pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q`（沿用既有 Python 面）+ .NET `NEWMANGA_FEA11_IPC=1 --filter Fea11RunGrant`（真实 Core、不手工传 version） | 全绿；破坏点变红 | `logs/feature.log`、`logs/host-ipc.log`、`logs/discrimination.log` |
| AC-G6 单测 | `dotnet test ... --filter "FullyQualifiedName~SourceRegistry"` | 21+ passed；删委托 RED | `logs/host-unit.log` |
| AC-G7/G8 门禁 | 全量 pytest/.NET、pins、check、API inventory、scope diff | 不降/不漂移 | `logs/gates.log` 等 |

## 交付记录（Owner 回填；不改 status）

- **Owner**：`run-grant-2a-impl`（DSH Agent Teams teammate；Lead `lead`）。
- **实现/测试 commit 链**（显式 pathspec，未 push；均在 `main`）：
  - `aa0a5562b` — `feat(fea-11-run-grant-2a)`: `SourceIdentityCache` + 扫描响应新鲜度门 + `RunSourceRange` 只用缓存 version + `RunSourceAuthorizer` 有界 on-demand 冷缓存填充 + 空 version mint 拒绝
  - `a0bafc89e` — `test(fea-11-run-grant-2a)`: Host 单测 8 例（缓存/冷缓存/预算/失败/委托行）+ 真实 IPC 生产版本通道用例；**`delivery_head`**
  - 证据/卡/Handoff 同批文档提交（`verification/FEA-11-RUN-GRANT-2A/**`、本卡、`doc/handoffs/FEA-11-RUN-GRANT-2A-a0bafc89e.md`）
- **实现落点**：`SourceScanScheduler.cs`（`SourceIdentityCache`/`SourceIdentity`/`SourceIdentityEntry`/`SourceScanIdentityVerdict` + `HostSourceScanExecutor.ReadSourceIdentity`/`ApplySourceIdentity` + `ProjectScanResult(expectedSourceId)`）；`HostRuntime.cs`（`_sourceIdentities`/`_scanExecutor`、`RunSourceRangeResolution`、`RunSourceAuthorizer` 冷缓存编排、`ScanSourceOnDemandAsync`）；`SourceReadCoordinator.cs`（空 `source_id`/`version` → `INVALID_REQUEST`，禁止静默占位）。
- **门禁实测**（`delivery_head=a0bafc89e`；均真跑）：`dotnet build NewManga.sln -c Release` **成功 0 warning/0 error**；定向 `pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` → **50 passed**；`SourceRegistry` → **29 passed**；`NEWMANGA_FEA11_IPC=1` 的 `Fea11RunGrant` → **4 passed**（含新增生产版本通道用例）；全量 `pytest tests` → **3281 passed / 10 skipped**（基线 3281/10，不降）；全量 `dotnet test NewManga.sln -c Release` → **1559 / 0 / 90**（基线 1551/0/89：+8 单测、+1 opt-in IPC skip）；`verify_pins` **18/18 PASS**；`check.ps1`（默认 + `-TaskPath`）**PASS(3 warnings)**；`generate_api_inventory.py --check` **EXIT=0**；scope **PASS（changed=5 全 ALLOWED；zero-drift 全空；minor=3）**；判别性 **6/6 破坏点 RED_AS_EXPECTED + 6/6 字节级 RESTORED + final rebuild EXIT=0**。跑后均 `git checkout -- verification/FEA-09`。
- **未运行项**：无（上述门禁全部实跑）。已知 flaky/环境交互：全量 .NET 若在 `verification/` 正在写入期间运行，`FluentResidual2VisualEvidenceTests` 会因 git-status 快照失败（本卡两次全量均在证据落盘后运行，未命中）。
- **证据索引**：`verification/FEA-11-RUN-GRANT-2A/EV.md`（每文件 sha256 + AC 矩阵）、`logs/feature.log`、`logs/host-unit.log`、`logs/host-ipc.log`、`logs/full-pytest.log`、`logs/full-dotnet.log`、`logs/gates-governance.log`、`logs/discrimination.log`、`scope-validation.log`、`changed-files.txt`、`RESOURCE-MANIFEST.json`。
- **不夸大**：本卡只修「生产 Host 铸造 `scope.version` 恒为 `"1"` 的版本通道」（L-G15）；**L-G12②（多成员容器其余成员 entry，2B）仍未闭环**、**L-R1 未全修**；不得表述为「referenced Run 全场景可用」。L-G1/L-G2/L-G8/L-G9/L-G10/L-G12②/L-G13/L-G14 保留。

