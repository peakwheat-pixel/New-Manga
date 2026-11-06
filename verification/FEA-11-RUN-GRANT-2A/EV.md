# FEA-11-RUN-GRANT-2A Canonical Evidence（Host Run source 版本通道；无 UNFREEZE）

> 结论先行：本卡修复 **L-G15（生产 Host 铸造 `scope.version` 恒为 `"1"` → referenced Run dispatch 前 100% typed 拒绝）**：Host 在真实 `ScanSourceSync` 响应后把 **Core 权威 `source.version_id` + `source.entries[]`** 写入有界内存缓存（仅 `status=ok && changed=false`；其余观测一律 invalidate），Run 铸造**只**从缓存取 version（禁止常量回退、禁止 Host 自行推断 locator/ordinal），冷缓存时**每源至多 1 次有界 on-demand 扫描**（每切片 8 源、30s 超时；失败/超时/预算耗尽 → 跳过该源并继续 dispatch）。真实 IPC 已证明 image 单 entry + folder（逐成员）+ 归档首成员在**生产版本通道**下 `authorize → bound_pages=1 → resolve_page_resource` 成功。**不夸大**：**L-G12②（多成员容器其余成员 entry，2B）仍未闭环**、**L-R1 未全修**；不得表述为「referenced Run 全场景可用」。独立 Review 由 Lead 指派（本会话不自审）。

| 项 | 值 |
|---|---|
| task | `FEA-11-RUN-GRANT-2A`（冻结卡 `doc/tasks/FEA-11-RUN-GRANT-2A.md`；`status` 未改） |
| Owner | `run-grant-2a-impl`（DSH Agent Teams teammate；Lead `lead`） |
| base | 卡 `base_commit=9ec4826d6`；实现起点 `1b6152112`（工作树 clean，实测） |
| 本次 delivery_head | `a0bafc89ec74be08e3d6d721105639df01a140a7`（实现 `aa0a5562b` + 测试 `a0bafc89e`；证据/卡/Handoff 为同批文档提交） |
| 分支/工作树 | `main` / `G:\CODEX\New Manga`（未创建 linked worktree、未 push） |
| 解释器/环境 | CPython 3.14.6 / PowerShell 7.6.8 / .NET SDK（net9.0 测试目标）/ Windows 11 |
| 契约字节 | **本卡零变更**（按本卡 commit 链：`doc/plan`、`doc/contracts`、`schema.py`、迁移、依赖、`core_assembly.py`、`NewManga.App/**` 全空 diff；pins 18/18） |
| 依赖 | **零新增** |
| 共享工作树 | 同期 `FEA-11-RUN-GRANT-2B-PREREQ-1` 会话在同一 `main` 工作树提交 `d8dcfc07a`（C-16 v1.4 UNFREEZE）；本卡 scope 校验只按本卡自有 commit 计算，未触碰该会话文件 |

## 1. 交付 commit 链（起点 `1b6152112` → delivery_head `a0bafc89e`）

```text
a0bafc89e test(fea-11-run-grant-2a): version-channel, cold-cache and AcceptRun-delegation discriminators
aa0a5562b feat(fea-11-run-grant-2a): Core-authoritative scan version cache drives Run grant minting
1b6152112 docs(fea-11-run-grant-2): 释放 base_commit=9ec4826d6（2A / 2B-PREREQ-1）
```

## 2. 门禁实测（`a0bafc89e`）

| Gate | 命令 | 结果 | 日志 |
|---|---|---|---|
| 构建（AC-G7） | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` | **成功 0 warning / 0 error** | — |
| 定向 Python（AC-G5 回归） | `C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | **PASS 50 passed** | `logs/feature.log` |
| Host 单测（AC-G2/G3/G6 + RUN-GRANT-1 回归） | `dotnet test ... --filter "FullyQualifiedName~SourceRegistry"` | **PASS 29 passed**（基线 21，+8） | `logs/host-unit.log` |
| 真实 IPC（AC-G1/G3/G4） | `$env:NEWMANGA_FEA11_IPC=1; dotnet test ... --filter "FullyQualifiedName~Fea11RunGrant"` | **PASS 4 passed**（基线 3，+1 生产版本通道；不设 env 时 4 skipped） | `logs/host-ipc.log` |
| 全量 Python（AC-G8） | `C:/Python314/python.exe -m pytest tests -q` | **PASS 3281 passed / 10 skipped**（基线 3281/10，不降） | `logs/full-pytest.log` |
| 全量 .NET（AC-G8） | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` | **PASS 1559 / 0 / 90**（基线 1551/0/89：+8 单测、+1 opt-in IPC skip） | `logs/full-dotnet.log` |
| 治理（AC-G7） | `verify_pins.ps1` / `check.ps1`（默认 + `-TaskPath`）/ `generate_api_inventory.py --check` | **18/18 PASS** / **PASS(3 warnings)** / **EXIT=0** | `logs/gates-governance.log` |
| 范围（AC-G7） | `python verification/FEA-11-RUN-GRANT-2A/tools/scope_validation.py` | **PASS（changed=5 全 ALLOWED；zero-drift 全空；minor=3）** | `scope-validation.log`、`changed-files.txt` |
| 判别性（AC-G1/G2/G3/G6） | `python verification/FEA-11-RUN-GRANT-2A/tools/discrimination.py` | **6/6 破坏点 RED_AS_EXPECTED + 6/6 字节级 RESTORED + final rebuild EXIT=0** | `logs/discrimination.log` |

**跑后恢复**：全量 pytest / 全量 .NET 会重写 tracked `verification/FEA-09/logs/wire-redacted.ndjson`；两次均执行 `git checkout -- verification/FEA-09`（事后 `git status` 复查无 FEA-09 残留）。**已知 flaky**：全量 .NET 在 `verification/` 正在写入期间 `FluentResidual2VisualEvidenceTests` 会因 git-status 快照失败；本卡先落盘证据再跑全量，两次均未命中。skip 说明：pytest 10 skipped 与 .NET 90 skipped 均为既有环境门控（无 provider 权重/GPU、sidecar/UI 集成 opt-in、4 个 `NEWMANGA_FEA11_IPC` 未设时跳过），本卡未新增 skip 条件（新增的 1 个 IPC 用例使用既有 opt-in 属性）。

## 3. 判别性验证（6 破坏点，删掉实现必须变红）

`logs/discrimination.log` 逐个破坏一条**已提交的**生产分支后运行**一个**目标用例，必须变红（exit≠0），随后按**原字节**恢复并复核 sha256，最后重新 build 恢复二进制：

| Case | 破坏点 | 目标用例 | 实测 |
|---|---|---|---|
| **B1** | Run 铸造版本回退常量 `"1"`（AC-G1） | IPC `ProductionScanVersionChannelDrivesImageFolderAndArchiveFirstMember` | **RED_AS_EXPECTED + RESTORED** |
| **B2** | `changed`/非 ok 观测可覆盖缓存（AC-G2） | `SourceScanResponseRefreshesTheCacheOnlyWhenUnchangedAndOk` | **RED_AS_EXPECTED + RESTORED** |
| **B3** | 冷缓存回退占位版本（删除跳过分支；AC-G3） | `RunAuthorizerSkipsColdCacheSourcesAndStillReachesDispatch` | **RED_AS_EXPECTED + RESTORED** |
| **B4** | 删除有界 on-demand 冷缓存填充（AC-G3） | `RunAuthorizerPerformsOneBoundedOnDemandScanPerColdSource` | **RED_AS_EXPECTED + RESTORED** |
| **B5** | 删除 `AcceptRunAsync → AuthorizePreparedRunForAcceptAsync` 委托行（AC-G6/R3-02） | `AcceptRunAsyncDelegatesToTheAuthorizationSeam` | **RED_AS_EXPECTED + RESTORED** |
| **B6** | `ScanSourceSync` 响应不再写入身份缓存（AC-G1 生产路径断链） | IPC 同上 | **RED_AS_EXPECTED + RESTORED**（final_rebuild exit 0） |

## 4. AC 矩阵（测试 → 证据映射）

| AC | 判定 | 判别性测试 | 证据 |
|---|---|---|---|
| AC-G1 生产版本通道 | MET | IPC `ProductionScanVersionChannelDrivesImageFolderAndArchiveFirstMember`（scan 目标 Version=`"1"`，实际铸造 version 来自真实扫描响应；cold image 走 on-demand；`bound_pages=1` → resolve OK）、`Fea11RunGrantIpcTests` 既有 3 例保留；`RunSourceRangeUsesTheCachedCoreVersionAndReportsColdSources`；判别 B1/B6 | `logs/host-ipc.log`、`logs/discrimination.log` |
| AC-G2 缓存新鲜度 | MET | `SourceScanResponseRefreshesTheCacheOnlyWhenUnchangedAndOk`（ok+unchanged 可缓存；changed/missing/encrypted/unsupported/malformed/source 不匹配 → invalidate；`version_missing`/`entries_missing`/`entry_malformed` 拒绝）、`SourceIdentityCacheIsBoundedAndPrunesExpiredEntries`（上界 1024、per-source 4096、TTL 裁剪、非法输入拒绝）；判别 B2 | `logs/host-unit.log`、`logs/discrimination.log` |
| AC-G3 冷缓存策略 | MET | `RunAuthorizerSkipsColdCacheSourcesAndStillReachesDispatch`（冷源跳过 + dispatch 到达）、`RunAuthorizerPerformsOneBoundedOnDemandScanPerColdSource`（1 次/源、二次不重扫）、`RunAuthorizerOnDemandScanBudgetIsExplicitAndBounded`（8 上限 + 预算 warn）、`RunAuthorizerOnDemandScanFailureIsASkipNotABlock`（失败不阻断）；IPC 的 cold image 生产 on-demand；判别 B3/B4 | `logs/host-unit.log`、`logs/host-ipc.log`、`logs/discrimination.log` |
| AC-G4 生产口径边界 | MET | IPC 同一用例：image 单 entry / folder 逐成员 / 归档首成员 resolve OK；归档第 2 成员 typed `SOURCE_ACCESS_DENIED`（L-G12② 保留） | `logs/host-ipc.log`、`G:\CODEX\New Manga.workspace\FEA-11-RUN-GRANT-2A\fixtures\ipc-*\run-grant-2a-version-channel.txt` |
| AC-G5 managed 零回归 | MET | RUN-GRANT-1 的 best-effort 用例全部保留通过（mint 失败/能力缺失/registry 不可读 → dispatch 到达；Core typed 拒绝 → 阻断）+ 新增冷缓存/扫描失败跳过；Core 面 `tests/fea11/test_source_run_grant.py` 50 passed；全量不降 | `logs/feature.log`、`logs/host-unit.log`、`logs/full-pytest.log`、`logs/full-dotnet.log` |
| AC-G6 R3-02 | MET | `AcceptRunAsyncDelegatesToTheAuthorizationSeam`（真实 `HostRuntime.AcceptRunAsync` → 冻结 slice 授权 → typed 拒绝；删除委托 → 落到 Core unavailable → RED）；原 seam 2 例保留；判别 B5 | `logs/host-unit.log`、`logs/discrimination.log` |
| AC-G7 零漂移与门禁 | MET | `scope_validation.py`（changed=5 全 ALLOWED、zero-drift 全空、minor=3）+ pins/check/API inventory | `scope-validation.log`、`changed-files.txt`、`logs/gates-governance.log` |
| AC-G8 证据/Handoff/不夸大 | MET | 本 EV 逐文件 sha256；`RESOURCE-MANIFEST.json`（动态 `delivery_head`）；Handoff §3 limitations（L-G15 已修但 2B/L-R1 未闭环）与未宣称项；卡面未写「全场景可用/L-R1 全修」 | 本文件、`RESOURCE-MANIFEST.json`、Handoff |

### 4.1 与 RUN-GRANT-1 的边界继承

| RUN-GRANT-1 边界 | 本卡（2A）后状态 |
|---|---|
| L-G12① version 通道（生产 `"1"` → 100% typed 拒绝） | **已修**（本卡；Core 权威扫描版本，禁常量） |
| L-G12② 容器成员 entry（多成员其余页） | **未修**（2B；C-16 v1.4 UNFREEZE 前置由 `2B-PREREQ-1` 会话提交） |
| L-G15（生产版本常量阻断） | **已修**（本卡）；历史登记保留 |
| L-G1/L-G2/L-G8/L-G9/L-G10/L-G11/L-G13/L-G14 | 保留（未碰；L-G8 加 on-demand 预算注记） |
| L-R1 | **未全修**（只修版本通道一条阻断） |

## 5. 逐文件 sha256

### 5.1 交付文件（实现 + 测试，`a0bafc89e`）

| 类别 | path | sha256 |
|---|---|---|
| 实现/测试 | `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs` | `51dcd654c981ca36a8e532268c894555c8af7c8ea1f245a92ac2a638ee805b31` |
| 实现/测试 | `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs` | `fb48aa2fbf41c3d89b312db92c802a3c3ecd53f82996814cbe94aeaece7f7429` |
| 实现/测试 | `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs` | `c450b7c855efde89568c6c155f25085dfa9248e9779ed150f0e748242ca55d19` |
| 实现/测试 | `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11RunGrantIpcTests.cs` | `4cb7238e2a2ade81335c37d65ac8b994cad3c1d519642f0630cbc4384bed2522` |
| 实现/测试 | `apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRegistryTests.cs` | `2b7ba4ba039ce6c79896a5e17dafafd864779df81ee21cbef570e43db1f86a04` |

### 5.2 证据文件（本目录，`EV.md` 除外）

| 类别 | path | sha256 |
|---|---|---|
| 证据 | `verification/FEA-11-RUN-GRANT-2A/changed-files.txt` | `2ad94f2c4b8c4eae7eacfa8dc8b7c6fd09724d7f6e23fee130142c818daffbb4` |
| 证据 | `verification/FEA-11-RUN-GRANT-2A/logs/discrimination.log` | `ca320d379b7185b1f539d8986c3ade44933a9fe1d0f380a490768f0d21545c8e` |
| 证据 | `verification/FEA-11-RUN-GRANT-2A/logs/feature.log` | `c0b655315f2b858a305e4a8efae88418de7adf91971f52034e0853d0b7857e7c` |
| 证据 | `verification/FEA-11-RUN-GRANT-2A/logs/full-dotnet.log` | `3a0c0e72e2e1e54e2564233b92567602390c1a220931194c72b80e4ab79bbf9c` |
| 证据 | `verification/FEA-11-RUN-GRANT-2A/logs/full-pytest.log` | `f55e9282738d366d5879ec2916762fb1eb74bac6b4bd0f16379de0397861e0b4` |
| 证据 | `verification/FEA-11-RUN-GRANT-2A/logs/gates-governance.log` | `2c2ff57b6084491dde12870e417e95ab3807165fd01356f6eaca83769d480b63` |
| 证据 | `verification/FEA-11-RUN-GRANT-2A/logs/host-ipc.log` | `7ca56da55593952ba7169283d74d656d69cf1a1abe6aaa6e14764df1a5ef3974` |
| 证据 | `verification/FEA-11-RUN-GRANT-2A/logs/host-unit.log` | `e69daf14fbad2ee6399bc6cf6248c745d3858ad345a7fb9db77bf06d3755afd2` |
| 证据 | `verification/FEA-11-RUN-GRANT-2A/RESOURCE-MANIFEST.json` | `087cb2baffaa92e4c5b44e92e7e72c93d8992125c424f3162fd5287ebd5082a0` |
| 证据 | `verification/FEA-11-RUN-GRANT-2A/scope-validation.log` | `5b5398153451a55e4d9fb7757aa2faea1bdfd6d9127280a646e803163fb01e63` |
| 证据 | `verification/FEA-11-RUN-GRANT-2A/tools/discrimination.py` | `71d20b4091bd03891fccb732448da2b6b85083c2eade5c7f1db9c48e4457ce3f` |
| 证据 | `verification/FEA-11-RUN-GRANT-2A/tools/gen_ev.py` | `65f14609f6209da6506eb5418dd8d308063476e16423db41ce92255f46382b3c` |
| 证据 | `verification/FEA-11-RUN-GRANT-2A/tools/gen_manifest.py` | `c1cde06b4fab1f705d45046af05700222ea9ef4c19a651d00632f88adc3fdbc3` |
| 证据 | `verification/FEA-11-RUN-GRANT-2A/tools/scope_validation.py` | `0560f0d0b5698929a80c3803244a273778b61f382768429708b60e8191d09c7e` |

### 5.3 文档（同批文档提交）

| 类别 | path | sha256 |
|---|---|---|
| 卡面（AC/交付记录） | `doc/tasks/FEA-11-RUN-GRANT-2A.md` | `8f06fc726aaf1dc8d7c251abfaafcdf1dba452b7f582ec8fb8c6fc6e33c469ce` |
| Handoff | `doc/handoffs/FEA-11-RUN-GRANT-2A-a0bafc89e.md` | `61e70856a630c4d35e609c80abeb5e7d9ddd9b5f8cead5193dc91e875cac53f8` |
| 契约面 | `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md` | **本卡零 diff**（C-16 v1.4 UNFREEZE 属 `FEA-11-RUN-GRANT-2B-PREREQ-1` commit `d8dcfc07a`，非本交付） |

> sha256 为**工作树字节**（检出配置 `core.autocrlf=true`；本仓库未对 `verification/FEA-11-RUN-GRANT-2A/**` 设 eol pin，与 RUN-GRANT-1 证据同口径）。`RESOURCE-MANIFEST.json` 的仓外隔离根聚合 sha256 覆盖工作区/日志/夹具全部文件（76 个），逐文件详情见该 JSON 的 `children`；该 JSON 同时记录 `delivery_head`。

## 6. 复现命令

```powershell
# 1) 构建
dotnet build apps/desktop-avalonia/NewManga.sln -c Release
# 2) 定向 / Host 单测 / 真实 IPC（生产版本通道）
C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q
dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~SourceRegistry"
$env:NEWMANGA_FEA11_IPC=1; dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~Fea11RunGrant"
# 3) 全量（跑后恢复 FEA-09 tracked 字节）
C:/Python314/python.exe -m pytest tests -q; git checkout -- verification/FEA-09
dotnet test apps/desktop-avalonia/NewManga.sln -c Release; git checkout -- verification/FEA-09
# 4) 治理
pwsh -NoProfile -File tools/governance/verify_pins.ps1
pwsh -NoProfile -File tools/governance/check.ps1
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-RUN-GRANT-2A.md
C:/Python314/python.exe tools/generate_api_inventory.py --check
# 5) 范围 + 判别性
C:/Python314/python.exe verification/FEA-11-RUN-GRANT-2A/tools/scope_validation.py
C:/Python314/python.exe verification/FEA-11-RUN-GRANT-2A/tools/discrimination.py
```

## 7. limitations / 未宣称（closeout 必须保留）

- **L-G15（本卡修复对象）**：生产 Host `scope.version` 恒 `"1"` → 授权前 typed 拒绝；**已修**（版本只来自 Core 权威扫描响应；禁止常量回退）。
- **L-G12②（2B）**：多成员容器其余成员页仍 typed fail-closed；本卡真实 IPC 明确保留该边界，**不改**。
- **L-G1**：单 grant ≤300s；窗口后 fail-closed；定期重铸/重绑另卡。
- **L-G2**：加密源仍不可 Run（typed，不崩溃）；`encrypted` 观测不写缓存。
- **L-G8（延伸）**：冷缓存 on-demand 扫描使 Run 前置成本与源大小线性相关；每切片 8 源 × 30s 显式预算，大库未标定。
- **L-G9**：Core 重启后 grants/bindings 丢失不可续跑；缓存为内存态，重启后按冷缓存路径重建。
- **L-G10**：L-R11 两读面 gate 差异未碰。
- **L-G11**：binding 解析在 Core；Host 只传 `grant_ids + command + scope`。
- **L-G13**：已知 flaky 按「如实记录 + 隔离复跑」处理。
- **L-G14**：`AcceptRunAsync` 需同进程先 `PrepareRunAsync`（`RUN_STALE_PREVIEW`）。
- **未宣称**：不写「referenced Run 全场景可用」「L-R1 全修」；只交付「生产版本通道修复 + image 单 entry + folder 逐成员 + 归档首成员（L-G12② 边界之外仍 fail-closed）」；FEA-11 AC11-5/AC11-9 未回填；独立 Review 由 Lead 指派。

## 8. 生成信息

- generated_at_utc=2026-11-06T21:46:59+00:00
- delivery_head=a0bafc89ec74be08e3d6d721105639df01a140a7
- repo_head_at_generation=923ce00fd52c3bd15e3ea588853d4c2152a73ea2
- generator=`verification/FEA-11-RUN-GRANT-2A/tools/gen_ev.py`（sha256 由本地文件实时计算）
