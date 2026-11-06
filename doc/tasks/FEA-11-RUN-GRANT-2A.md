---
id: FEA-11-RUN-GRANT-2A
title: Host Run source 版本通道（ScanSourceSync 缓存 + 有界 on-demand 扫描；无 UNFREEZE）
kind: implementation
governance_version: 3
status: done
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH」；`FEA-11-RUN-GRANT-2` 权威 scope review `doc/reviews/FEA-11-RUN-GRANT-2-scope-r1.md`（fresh subagent `22212d0c…`，**READY-WITH-UNFREEZE**；拆分口径：**2A Host-only = READY-TO-FREEZE，无需 UNFREEZE**；2B 容器成员 entry 需 C-16 v1.4）；Codex 裁决输入（`196dede9…`，建议 C-16 身份查询 1 pin）；DSH 裁决：采纳 scope review 拆分与 2A 零契约路径，Codex 方案作为被否决备选记录（见「DSH 裁决」）；R3-02 并入本卡；L-G1/2B 另卡
suggested_owner: codex
owner: run-grant-2a-impl
reviewer: 独立上下文 fresh subagent（未参与实现/返修）：r1 `61403414-6164-44b6-8fe6-da31515dfc98`（**approved** P0=0/P1=0/P2=2/P3=6；reviewed_head `a0bafc89e`）；报告 `doc/reviews/FEA-11-RUN-GRANT-2A-r1.md`
depends_on:
  - FEA-11-RUN-GRANT-1
base_commit: 9ec4826d6
branch: null
worktree: null
integration_commit: a0bafc89ec74be08e3d6d721105639df01a140a7
delivery_head: a0bafc89ec74be08e3d6d721105639df01a140a7
canonical_evidence_status: complete
resource_closeout_status: complete
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

- [x] **AC-G1 生产版本通道（P0 判别核心）**：Host 铸造 `scope.version` 来自 Core 权威数据（`ScanSourceSync` 响应），禁止常量 `"1"`。判别性：回退为 `"1"` → 目标用例 RED（Core typed `SOURCE_ACCESS_DENIED`、Run 不 dispatch）。真实 IPC：seed 后不手工传 version，由生产路径取得；`authorize → bound_pages≥1 → resolve_page_resource` 成功。 证据：`SourceIdentityCache`（`SourceScanScheduler.cs`）+ `RunSourceRange` 只取缓存 version（`HostRuntime.cs`；空 version mint 被 `SourceReadCoordinator` 拒绝）；真实 IPC `Fea11RunGrantIpcTests.ProductionScanVersionChannelDrivesImageFolderAndArchiveFirstMember`（scan 目标 Version 全为 `"1"`，缓存值 `sv1`/`svf1`/`sv-img` 全部来自真实 ScanSourceSync 响应；cold image → 1 次有界 on-demand 扫描 → `bound_pages=1` → resolve OK）；判别性 B1（回退 `"1"` → RED）、B6（scan→缓存断链 → RED）见 `verification/FEA-11-RUN-GRANT-2A/logs/discrimination.log`。 <<MET>>
- [x] **AC-G2 缓存新鲜度/来源**：仅缓存 `status=ok && changed=false`；`changed/encrypted/unsupported/missing` 不更新（不铸或 typed fail-closed）；仅内存、`source_id` 键、有界上界与过期裁剪断言。判别性：允许 `changed` 覆盖 → RED。 证据：`HostSourceScanExecutor.ReadSourceIdentity`/`ApplySourceIdentity`（仅 ok+unchanged 可缓存，其余一律 invalidate）；`SourceIdentityCache`（`MaxEntries=1024`、`MaxEntriesPerIdentity=4096`、`TTL=3600s`，`TryGet`/`Remember` 均裁剪）；用例 `SourceScanResponseRefreshesTheCacheOnlyWhenUnchangedAndOk`、`SourceIdentityCacheIsBoundedAndPrunesExpiredEntries`；判别性 B2（删除新鲜度门 → RED）。 <<MET>>
- [x] **AC-G3 冷缓存策略**：缺失 → 每源至多 1 次有界 on-demand 扫描；超时/失败跳过该源并继续 dispatch（best-effort，不阻断 managed-only Run）；无限重试/静默占位版本 → RED。 证据：`RunSourceAuthorizer.ResolveWithColdCacheAsync`（每切片最多 `MaxOnDemandScansPerSlice=8` 源、每源 `OnDemandScanTimeout=30s`、`_onDemandGate` 串行化并发切片、失败/超时仅 warn 跳过）；冷源只进 `ColdSources` 不铸造；用例 `RunAuthorizerSkipsColdCacheSourcesAndStillReachesDispatch`、`RunAuthorizerPerformsOneBoundedOnDemandScanPerColdSource`、`RunAuthorizerOnDemandScanBudgetIsExplicitAndBounded`、`RunAuthorizerOnDemandScanFailureIsASkipNotABlock`；判别性 B3（冷缓存回退占位 → managed Run 被阻断 RED）、B4（删除 on-demand 填充 → RED）；真实 IPC 的 cold image 源走生产 on-demand 路径。 <<MET>>
- [x] **AC-G4 生产口径可用边界**：真实 IPC 证明 image 单 entry + folder（逐成员）+ 归档首成员在**生产版本通道**下可用；多成员容器其余页仍 typed fail-closed（2B 未修），卡/Handoff 不得写「referenced Run 全场景可用」。 证据：真实 IPC `ProductionScanVersionChannelDrivesImageFolderAndArchiveFirstMember`（image/folder/archive-first-member 三源 resolve 全部 OK；archive second member → typed `SOURCE_ACCESS_DENIED`，L-G12② 边界保留）；见证文件 `G:\CODEX\New Manga.workspace\FEA-11-RUN-GRANT-2A\fixtures\ipc-*\run-grant-2a-version-channel.txt`（Resource Manifest 内）；卡/Handoff 明写「生产版本常量已修，但 2B/L-R1 仍未闭环」。 <<MET>>
- [x] **AC-G5 managed 零回归**：沿用 RUN-GRANT-1 AC-R5（Core 面 managed skip；Host best-effort 不阻断；managed 读/metadata 零变化）。 证据：RUN-GRANT-1 的 best-effort 用例全部保留并通过（`RunAuthorizationBestEffortSkipReachesDispatch_CoreRefusalDoesNot`、`RunAuthorizerTreatsMintFailuresAsBestEffortSkips`、`RunAuthorizerSkipsWhenTheCapabilityIsMissingWithoutMinting`、`RunAuthorizerSkipsWhenTheRegistryCannotBeRead`）+ 新增 `RunAuthorizerSkipsColdCacheSourcesAndStillReachesDispatch`（冷缓存不阻断 dispatch）与 `RunAuthorizerOnDemandScanFailureIsASkipNotABlock`；Core 面 managed 用例 `tests/fea11/test_source_run_grant.py` 50 passed 不变；全量 pytest/.NET 均不降（见 AC-G8）。 <<MET>>
- [x] **AC-G6 R3-02 收口**：`AcceptRunAsync` 对 `AuthorizePreparedRunForAcceptAsync` 的委托行有判别测试；删除委托 → RED。 证据：`SourceRegistryTests.AcceptRunAsyncDelegatesToTheAuthorizationSeam`（构造未启动 HostRuntime、注入 warm-cache authorizer、以真实 `AcceptRunAsync` 触发冻结 slice 授权 → typed `SOURCE_ACCESS_DENIED`；删除委托行后落到「Core unavailable」→ 用例 RED，判别性 B5）；原 seam 用例仍保留。 <<MET>>
- [x] **AC-G7 零漂移**：`doc/plan`/`doc/contracts`/`schema.py`/依赖/`NewManga.App/**` 零 diff；`CORE_PROTOCOL_MINOR=3`；Run wire 键集不变；`verify_pins` 18/18；`check.ps1`（默认 + `-TaskPath`）PASS；API inventory EXIT=0；scope diff ⊆ allowed_paths。 证据：`verification/FEA-11-RUN-GRANT-2A/scope-validation.log`（changed=5 全 ALLOWED；zero-drift surfaces 全 ZERO_DIFF；`protocol_minor=3 kept: YES`）、`changed-files.txt`；`logs/gates-governance.log`（PIN AUDIT PASS all 18 / Governance PASS(3 warnings) ×2 / API inventory EXIT=0）。**注**：本卡的零契约面按本卡自有 commit 链评估；同期 `FEA-11-RUN-GRANT-2B-PREREQ-1` 的 C-16 v1.4 UNFREEZE（commit `d8dcfc07a`）不属于本交付。 <<MET>>
- [x] **AC-G8 门禁/证据/不夸大**：全量 pytest **不降**（基线 3281/10，实测 3281/10）、全量 .NET **不降**（1551/0/89，实测 **1559/0/90**）、定向 50、SourceRegistry 29、真实 IPC 4；EV 每文件 sha256 + commit；Handoff 保留 L-G1/L-G2/L-G8/L-G9/L-G12②/L-G13/L-G15/**L-G16**，并明写「生产版本常量已修，但 2B/L-R1 仍未闭环」；不得表述为 L-R1 修复。 证据：`logs/full-pytest.log`（3281 passed / 10 skipped）、`logs/full-dotnet.log`（1559 / 0 / 90；基线 1551/0/89，+8 单测 +1 opt-in IPC skip）、`logs/feature.log`（50 passed）、`logs/host-unit.log`（29 passed）、`logs/host-ipc.log`（4 passed）、`logs/discrimination.log`（6/6 RED + RESTORED + rebuild OK）；`EV.md` 逐文件 sha256；`doc/handoffs/FEA-11-RUN-GRANT-2A-a0bafc89e.md` limitations/未宣称；卡面未写「全场景可用/L-R1 全修」。 <<MET>>

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
 
## Review r1 处置（DSH，2026-11-07；append-only）

- 独立 Review r1 `doc/reviews/FEA-11-RUN-GRANT-2A-r1.md`（fresh subagent `61403414-6164-44b6-8fe6-da31515dfc98`；reviewed_head `a0bafc89e`）：**approved，P0=0/P1=0/P2=2/P3=6**；AC-G1…AC-G8 全 MET；独立复现 B1/B3/B4/B5 破坏点 RED + 字节级恢复（sha `51dcd654…`）。
- **R2A-01（P2，已修）**：`RESOURCE-MANIFEST.json` `delivery_head` 由生成时 repo HEAD（`923ce00fd…`，实为 2B-PREREQ-1 closeout）改为本卡 `a0bafc89e…`；原值保留 `repo_head_at_generation`；`source_path` 文本同步（证据提交 `53dc38bd4`）。
- **R2A-02（P2，文档边界关闭，不新增 head）**：`SourceIdentityCache.MaxEntriesPerIdentity=4096` < `DefaultMaxEntriesPerSource=10000`；**>4096 成员的 folder 源永不入缓存**（每次 Run 触发 on-demand 全量扫描但不铸造；fail-closed、无错误授权）→ 登记 **L-G16**；不宣称 folder 全量可用；调大常量需新 head + 复审，本卡不做。
- R2A-03…R2A-08（P3）：登记接受/后续（见 EV §7.1）：`totals` 缺失分支、30s 协作式截止非硬上界（L-G8 措辞修正）、生产扫描 grant 残留占位 version（pre-2A）、缓存陈旧窗口（fail-closed）、authorizer 接线/超时/唯一性测试缺口、缓存 entries[] 内存上界（2B 预留）。
- 不改变 AC 判定、实现/测试字节（`a0bafc89e`）与 r1 approved 结论。

## Canonical Evidence

| evidence_id | AC | 路径 | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC-G1 | verification/FEA-11-RUN-GRANT-2A/EV.md | 53dc38bd4 | 2c87dbe3540e5d09470cd6ebafb0b56cde8d80e803d20e291314152c25d47651 | CANONICAL |
| EV-02 | AC-G7 | verification/FEA-11-RUN-GRANT-2A/changed-files.txt | 53dc38bd4 | 2ad94f2c4b8c4eae7eacfa8dc8b7c6fd09724d7f6e23fee130142c818daffbb4 | CANONICAL |
| EV-03 | AC-G7 | verification/FEA-11-RUN-GRANT-2A/scope-validation.log | 53dc38bd4 | 5b5398153451a55e4d9fb7757aa2faea1bdfd6d9127280a646e803163fb01e63 | CANONICAL |
| EV-04 | AC-G8 | verification/FEA-11-RUN-GRANT-2A/logs/full-pytest.log | 53dc38bd4 | f55e9282738d366d5879ec2916762fb1eb74bac6b4bd0f16379de0397861e0b4 | CANONICAL |
| EV-05 | AC-G8 | verification/FEA-11-RUN-GRANT-2A/logs/full-dotnet.log | 53dc38bd4 | 3a0c0e72e2e1e54e2564233b92567602390c1a220931194c72b80e4ab79bbf9c | CANONICAL |
| EV-06 | AC-G1…G6 | verification/FEA-11-RUN-GRANT-2A/logs/discrimination.log | 53dc38bd4 | ca320d379b7185b1f539d8986c3ade44933a9fe1d0f380a490768f0d21545c8e | CANONICAL |
| EV-07 | AC-G4 | verification/FEA-11-RUN-GRANT-2A/logs/host-ipc.log | 53dc38bd4 | 7ca56da55593952ba7169283d74d656d69cf1a1abe6aaa6e14764df1a5ef3974 | CANONICAL |
| EV-08 | AC-G5/AC-G6 | verification/FEA-11-RUN-GRANT-2A/logs/host-unit.log | 53dc38bd4 | e69daf14fbad2ee6399bc6cf6248c745d3858ad345a7fb9db77bf06d3755afd2 | CANONICAL |
| EV-09 | AC-G1 | verification/FEA-11-RUN-GRANT-2A/logs/feature.log | 53dc38bd4 | c0b655315f2b858a305e4a8efae88418de7adf91971f52034e0853d0b7857e7c | CANONICAL |
| EV-10 | AC-G7 | verification/FEA-11-RUN-GRANT-2A/logs/gates-governance.log | 53dc38bd4 | c30f4c56a50e3f2f2f17f881fd40efb59fe01eb46a5dbae8f2d2a398ab29da97 | CANONICAL |
| EV-11 | AC-G8 | verification/FEA-11-RUN-GRANT-2A/RESOURCE-MANIFEST.json | 53dc38bd4 | 3fe6ed57c47ac1d55460b5e406d9d8171293ee6211a51d85f5ee7c7cb2af2911 | CANONICAL |
| EV-12 | AC-G1…G6 | verification/FEA-11-RUN-GRANT-2A/tools/discrimination.py | 53dc38bd4 | 71d20b4091bd03891fccb732448da2b6b85083c2eade5c7f1db9c48e4457ce3f | CANONICAL |
| EV-13 | AC-G8 | verification/FEA-11-RUN-GRANT-2A/tools/gen_ev.py | 53dc38bd4 | 65f14609f6209da6506eb5418dd8d308063476e16423db41ce92255f46382b3c | CANONICAL |
| EV-14 | AC-G8 | verification/FEA-11-RUN-GRANT-2A/tools/gen_manifest.py | 53dc38bd4 | c1cde06b4fab1f705d45046af05700222ea9ef4c19a651d00632f88adc3fdbc3 | CANONICAL |
| EV-15 | AC-G7 | verification/FEA-11-RUN-GRANT-2A/tools/scope_validation.py | 53dc38bd4 | 0560f0d0b5698929a80c3803244a273778b61f382768429708b60e8191d09c7e | CANONICAL |
| EV-16 | AC-G1…G8 | doc/reviews/FEA-11-RUN-GRANT-2A-r1.md | 5e4a572ab | 540f9f3c6eb29a866ad7fc69bc5e694fb4fffe88109fe59b647d028d0d966708 | CANONICAL |
| EV-17 | AC-G8 | doc/handoffs/FEA-11-RUN-GRANT-2A-a0bafc89e.md | 53dc38bd4 | 03d3ec815fc2b04b8b3fb9217ce189d1e594d37c7b4aad2ec5252f012a2a4549 | CANONICAL |

## Resource Manifest

`verification/FEA-11-RUN-GRANT-2A/RESOURCE-MANIFEST.json`

## Closeout Record（2026-11-07）

- **状态**：`done`；`delivery_head`/`integration_commit` = `a0bafc89ec74be08e3d6d721105639df01a140a7`（实现 `aa0a5562b` + 测试 `a0bafc89e`；证据/卡/Handoff 文档提交 `5c95d96f2`/`53dc38bd4`）。
- **AC 判定**：AC-G1…AC-G8 **全 MET**（AC-G4 保留 L-G12②/L-G16 边界；AC-G2 缓存矩阵按 ok+unchanged；AC-G3 冷缓存 best-effort）。无 PARTIAL/BLOCKED。
- **Review 处置**：独立 r1 **approved（P0=0/P1=0/P2=2/P3=6）**；R2A-01 已修（Manifest `delivery_head`）、R2A-02 文档边界关闭（L-G16）、R2A-03…R2A-08 登记接受/后续；不改变字节与 AC。
- **门禁数字（before → after；Lead 实测）**：全量 pytest **3281/10 → 3281/10**；全量 .NET **1551/0/89 → 1559/0/90**（+8 单测 / +1 opt-in skip）；定向 python **50**；SourceRegistry **21→29**；真实 IPC **3→4**；pins **18/18**；check（默认 + `-TaskPath`）PASS(3w)；API inventory PASS；scope diff **5 文件 ⊆ allowed_paths**、禁止面零 diff、`CORE_PROTOCOL_MINOR=3`；判别性 **6/6** 破坏点 RED + 字节级 RESTORE。跑后均 `git checkout -- verification/FEA-09`。
- **limitations（保留）**：L-G1（300s）、L-G2（加密）、L-G8（扫描/铸造成本；on-demand 预算；30s 协作式截止非硬上界）、L-G9（Core 重启）、L-G10（L-R11）、L-G11、L-G12②（多成员容器其余成员仍不可授权）、L-G13（flaky）、L-G14（AcceptRun prepared-slice）、**L-G16（>4096 成员 folder 源不入缓存；每次 Run 重扫不铸造；folder 全量可用不成立）**、R2A-03…08 观察。**L-R1 未全修**；本卡只修 **L-G15（生产版本常量）**。
- **Resource Manifest / 资源处置**：仓内删除/移动/归档 0；仓外隔离根 `G:\CODEX\New Manga.workspace\FEA-11-RUN-GRANT-2A\`（IPC 夹具/门禁日志/复核备份，无独有产品数据）→ `PRESERVE_REFERENCED`；Manifest 已修 `delivery_head`。
- **指针清理**：STATUS 当前 Task → `FEA-11-RUN-GRANT-2`（2B 实现 ready）；PLAN 本节点 done；TASK_LEDGER 重生成。
- **push**：Lead 统一 push（PRE/POST/AHEAD 见后续 push 记录）。

### Closeout 补充（2026-11-07；记录修正）

- 独立 Review r1 在提交后对边界说明补一句事实澄清（工作树并发文件归属），文件 sha256 由 2e2079cd… 变为 540f9f3c…；卡 EV-16 已重签到 5e4a572ab 提交。**不改变** AC-G1…G8 判定、reviewed_head 0bafc89e、approved 结论与任何实现/测试/证据字节。
