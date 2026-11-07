# FEA-11-L-S1-REGISTRY-RESILIENCE-1 Canonical Evidence（Registry 读取韧性；C-15 v1.5 §5）

> 结论先行：本卡把 `SourceAccessRegistry` 的「**文件级损坏**」与「**某根当前身份不可用/不匹配**」分开。`Load()` 现在只做文件级校验（magic/version/长度/DPAPI/JSON/持久化条目结构），**删除**逐根 `SourceSecurity.Identity()` 探针；`Authorize()` 在**同一把锁内、读盘之后**对「请求路径所属注册根」**逐请求**重核验 identity（存在/可读/volume+file id），不可用/不匹配 → 该请求 typed `SOURCE_REGISTRY_UNAVAILABLE` 且**零写**（循环先于任何 `Save`）、不跨调用缓存、不自动重建 identity / 不自动重授权 / 不自动恢复；`List()` 仍返回全部条目（不可用是**派生状态**，不新增持久字段、不删条目）；文件级损坏路径**一字未改**（fail-closed、`.corrupt-<utc>` 复制、不覆盖、不建空文件）。**不夸大**：产品内**仍无**根级恢复/重授权入口（B limitation）、`.corrupt-*` 无界复制未修（C limitation）、`SOURCE_REGISTRY_UNAVAILABLE` 码义已收窄但零新增码；调度器/运行时可用性投影不在本卡（D-6）。独立 Review 由 Lead 指派（本会话不自审）。

| 项 | 值 |
|---|---|
| task | `FEA-11-L-S1-REGISTRY-RESILIENCE-1`（冻结卡 `doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1.md`；`status` 未改） |
| Owner | `l-s1-impl`（DSH Agent Teams teammate；Lead `lead`） |
| base | 卡 `base_commit=55306cb84`；实现起点 `db12dc5e5`（工作树 clean，实测） |
| 本次 delivery_head | `b56c5a0e6adf6f4cba31f1b3b1d8ee950c7bb84b`（实现 `1ac8cc0b7` + 测试 `b56c5a0e6`；证据/卡/Handoff 为同批文档提交） |
| 分支/工作树 | `main` / `G:\CODEX\New Manga`（未创建 linked worktree、未 push） |
| 解释器/环境 | CPython 3.14.6 / PowerShell 7.6.8 / .NET SDK（net9.0）/ Windows 11（交互用户，DPAPI 原生） |
| 契约字节 | **本卡零变更**：`doc/plan/**`、`doc/contracts/**` 在起始 head..HEAD 全范围零 diff；C-15 v1.5 已由 PREREQ 会话冻结（pin `f9e376a0ed4c`），pins 18/18 |
| 依赖 | **零新增** |
| 共享工作树 | 同期 `FEA-11-L-S4-LOCATION-AUTH-REFRESH-1` 会话在同一 `main` 工作树提交 `6dd36aad7`/`0ebb234bf`（Python `src/**`+`tests/**`），落在本卡 head **之后**；本卡零 Python/契约/STATUS/PLAN/LEDGER diff，未暂存/提交其文件 |

## 1. 交付 commit 链（起点 `db12dc5e5` → delivery_head `b56c5a0e6`）

```text
b56c5a0e6 test(fea-11-l-s1): mixed-registry resilience matrix, file-level regression and gated mixed-registry IPC
1ac8cc0b7 feat(fea-11-l-s1): split registry file-level corruption from per-request root identity (C-15 v1.5)
db12dc5e5 docs(l-s1/l-s4): 释放 base_commit=55306cb84（A 实现起点）
```

## 2. 门禁实测（`b56c5a0e6`）

| Gate | 命令 | 结果 | 日志 |
|---|---|---|---|
| 构建（AC-L7） | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` | **成功 0 warning / 0 error（EXIT 0）** | `logs/build.log` |
| Host 单测（AC-L1/L2/L3）+ 既有回归 | `dotnet test tests/NewManga.Host.Tests/... --filter "FullyQualifiedName~SourceRegistry"` | **PASS 40 / 0 failed / 1 skipped（41）**；filter 基线 32（2A 21+8、2B +3），本卡 +8 | `logs/host-unit.log` |
| gated 真机 IPC（AC-L2/L6、D-7） | `$env:NEWMANGA_FEA11_IPC=1; dotnet test ... --filter "FullyQualifiedName~Ipc_MixedRegistry"` | **PASS 1 / 0 / 0**；隔离 receipt：`source_list_roots=2`、`IssueAsync(healthy)=minted`、`IssueAsync(missing)=SOURCE_REGISTRY_UNAVAILABLE zero_write=1 no_corrupt_copy=1`、`source_register_root=registered`、`List=3` | `logs/host-ipc.log` |
| 定向 Core 回归（AC-L7） | `C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | **PASS 74 passed**（基线 74，不降） | `logs/feature.log` |
| 全量 Python（AC-L7） | `C:/Python314/python.exe -m pytest tests -q` | **PASS 3317 passed / 10 skipped**；跑后 `git checkout -- verification/FEA-09` → `FEA09_STATUS=CLEAN` | `logs/full-pytest.log` |
| 全量 .NET（AC-L7） | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` | **PASS 1570 / 0 / 92**（基线 1562/0/91：+8 单测、+1 opt-in IPC skip）；跑后恢复 FEA-09 → `CLEAN` | `logs/full-dotnet.log` |
| 治理（AC-L5/L7） | `verify_pins.ps1` / `check.ps1`（默认 + `-TaskPath`）/ `generate_api_inventory.py --check` | **18/18 PASS** / **PASS(3 warnings)** ×2 / **EXIT=0** | `logs/gates-governance.log` |
| 范围（AC-L7） | `python verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/tools/scope_validation.py` | **PASS（changed=2 全 ALLOWED；zero-drift 全 ZERO_DIFF）** | `scope-validation.log`、`changed-files.txt` |
| 判别性（AC-L1…L4） | `python verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/tools/discrimination.py` | **5/5 RED_AS_EXPECTED + 5/5 字节级 RESTORED + final rebuild EXIT=0** | `logs/discrimination.log` |

**数字口径（诚实记录）**：

- 全量 pytest **3317/10**：卡基线 3305/10；差额 **+12 来自同期 `FEA-11-L-S4` 会话已提交的 Python 测试**（`6dd36aad7`/`0ebb234bf`），**不归属本卡**（本卡零 Python 改动）。
- 全量 .NET **1570/0/92**：卡基线 1562/0/91；差额 = **+8 本卡单测**、**+1 opt-in IPC skip**（`NEWMANGA_FEA11_IPC` 未设时跳过）。
- `SourceRegistry` filter **40/0/1**：基线 32（2A closeout 记录 29 = 21+8；2B +3）+ 本卡 8 = 40；IPC 用例在 filter 内计 1 skipped。
- skip 说明：.NET 92 skipped 全为既有环境门控（sidecar/UI/IPC opt-in 等），本卡仅新增 1 个 `NEWMANGA_FEA11_IPC` 门控用例。

## 3. 判别性验证（5 破坏点，删掉实现必须变红）

`logs/discrimination.log` 逐个破坏一条**已提交的**生产分支后运行**一个**目标用例，必须变红（exit≠0），随后按**原字节**恢复并复核 sha256（`restore=RESTORED sha256=0b0d524a…`），最后重新 build 恢复二进制（`final_rebuild exit_code=0`）：

| Case | 破坏点 | 目标用例 | 实测 |
|---|---|---|---|
| **B1** | `Load` 恢复逐根 identity 预探针（单根缺失再次判整库损坏；AC-L1/L2） | `MixedRegistry_ListReturnsEveryEntryIncludingTheUnavailableOne` | **RED_AS_EXPECTED + RESTORED** |
| **B2** | 删除 `Authorize` 的逐请求根身份补位（只删 Load 校验不补 Authorize → **被替换根重新获得授权**；AC-L3 安全核心） | `ReplacedRoot_AuthorizeIsTypedAndPersistsNoNewIdentity` | **RED_AS_EXPECTED + RESTORED** |
| **B3** | 缺失根当「无授权」（探针失败静默跳过，不再是 typed 拒绝；AC-L3） | `MissingRoot_AuthorizeIsTypedAndWritesNothing` | **RED_AS_EXPECTED + RESTORED**（实测得到 `SOURCE_ACCESS_DENIED` 而非 `SOURCE_REGISTRY_UNAVAILABLE`） |
| **B4** | 文件级损坏放宽为「空 registry」（fail-closed 移除；AC-L1） | `FileLevelCorruptionStaysWholeFileFailClosed` | **RED_AS_EXPECTED + RESTORED** |
| **B5** | 根外路径回退为「只做 reparse 检查」（containment 回退；AC-L3） | `MissingRoot_NeverAuthorizesAnyPathAndContainmentStaysExact` | **RED_AS_EXPECTED + RESTORED** |

> 未使用的候选破坏点：跨调用缓存探针（需引入静态缓存字段，改动面超出「一行破坏」口径）→ 该行为改由用例 `RootIdentityIsReProbedOnEveryAuthorize` 正向钉住（先成功、再删根、第二次即 typed）。

## 4. AC 矩阵（测试 → 证据映射）

| AC | 判定 | 判别性测试 | 证据 |
|---|---|---|---|
| AC-L1 文件级损坏仍整库 fail-closed | MET | `FileLevelCorruptionStaysWholeFileFailClosed`（12 例矩阵：short/truncated/magic/length/json/format_version/duplicate_id/generation/empty_roots/non_normalized_root/unreadable_flag/**真实 DPAPI 篡改**；每例断言「原字节保留 + corrupt 副本 + List/Authorize typed」）；既有 `SourceRegistryTests.EncryptedPersistenceGenerationCorruptionAndExplicitReset` 保持绿；判别 B4 | `logs/host-unit.log`、`logs/discrimination.log` |
| AC-L2 根级不可用不再整库不可读 | MET | `MixedRegistry_ListReturnsEveryEntryIncludingTheUnavailableOne`、`MixedRegistry_HealthyRootAuthorizeSucceedsAndOnlyPersistsItsLastUse`、`MissingRoot_AuthorizeIsTypedAndWritesNothing`、IPC `Ipc_MixedRegistry_ListRegisterMintSucceedAndMissingRootIsTyped`；判别 B1 | `logs/host-unit.log`、`logs/host-ipc.log`、`logs/discrimination.log` |
| AC-L3 授权期逐请求校验（安全核心） | MET | `ReplacedRoot_AuthorizeIsTypedAndPersistsNoNewIdentity`、`MissingRoot_NeverAuthorizesAnyPathAndContainmentStaysExact`、`RootIdentityIsReProbedOnEveryAuthorize`、`MissingRoot_AuthorizeIsTypedAndWritesNothing`；判别 B2/B3/B5 | `logs/host-unit.log`、`logs/discrimination.log` |
| AC-L4 不自动重建/恢复/重授权 | MET | `ReplacedRoot_*`（字节不变 + 持久化 identity 保持原值）、`RevokeAndExplicitResetAreUnaffectedByAnUnavailableRoot`（撤销/显式 reset 语义不变、无自动恢复） | `logs/host-unit.log` |
| AC-L5 错误码/语义零新 | MET | 断言错误码恒为 `SOURCE_REGISTRY_UNAVAILABLE`/`SOURCE_ACCESS_DENIED`/`SOURCE_GRANT_REVOKED`（无新码）；scope zero-drift；pins 18/18；API inventory EXIT=0 | `scope-validation.log`、`logs/gates-governance.log` |
| AC-L6 测试/证据 | MET | 混合 registry 单测 + 1 条 gated 真机 IPC + 判别性 5/5 RED + 字节级恢复 + 本 EV 逐文件 sha256 + Handoff | 本文件、`RESOURCE-MANIFEST.json`、`doc/handoffs/FEA-11-L-S1-REGISTRY-RESILIENCE-1-b56c5a0e6.md` |
| AC-L7 零漂移/门禁 | MET | 全量 pytest 3317/10（≥3305/10，+12 归属 L-S4）、全量 .NET 1570/0/92（基线 1562/0/91）、build 0/0、pins 18/18、check PASS(3w)×2、API EXIT=0、scope PASS、FEA-09 恢复 CLEAN | `logs/full-pytest.log`、`logs/full-dotnet.log`、`logs/build.log`、`logs/gates-governance.log`、`scope-validation.log` |
| AC-L8 不夸大 | MET | 本文件 §7 + Handoff §3 limitations/未宣称；卡面未写「恢复已可用/根级问题全解/L-R1 全修」 | 本文件、Handoff、卡面 |

## 5. 逐文件 sha256

### 5.1 交付文件（实现 + 测试，`b56c5a0e6`）

| 类别 | path | sha256 |
|---|---|---|
| 实现 | `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceAccessRegistry.cs` | `0b0d524ae52cfdc13f5622defd118fe922fd91a041e3cef21cd241044f1b4de3` |
| 测试（新增） | `apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRegistryResilienceTests.cs` | `cb0eee27e90c214fc4c9a237fe19eb5c2805ac9fc819327685f7b4e3f290c3dd` |

> `apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRegistryTests.cs` **本卡零 diff**（既有 DPAPI/字节级/Reset 覆盖原样保留并继续作为回归）。

### 5.2 证据文件（本目录，`EV.md` 与 `RESOURCE-MANIFEST.json` 除外）

| 类别 | path | sha256 |
|---|---|---|
| 证据 | `verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/changed-files.txt` | `517690346ac8d5c41d7f417fd80eff0b17c8564c53c910ce4ec40b6f841fb7e0` |
| 证据 | `verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/scope-validation.log` | `beba8426139e3bc5ffb9b3228d6bb916de6192d4f2bc35d0341532ddbda89b75` |
| 证据 | `verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/logs/build.log` | `7cee7cf2649f9cfb2b3cdce6a65caf3301b8d27a849dfcaf0f6b29527f44edfc` |
| 证据 | `verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/logs/host-unit.log` | `41a00278b8e38c8d222cdac8c2fcc5f6d4d2e2ab519a72b0071d726d917d7140` |
| 证据 | `verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/logs/host-ipc.log` | `eb1c9eb223bc1e124a1ec9ac85cc9b9c2201da6538e1aa7390554101c29eefdb` |
| 证据 | `verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/logs/feature.log` | `6e97cf0521897ed97d97ad0c017edab9fb0811d23bf625accbf10b43df12e4cc` |
| 证据 | `verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/logs/full-pytest.log` | `6ba6fe09025c475076b0656e2d077d36dfa935627215fd692284caf8804267e3` |
| 证据 | `verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/logs/full-dotnet.log` | `0465c582e3661a9c659b6a368057e18ef052189939336cd221b3eccdf3cc2ace` |
| 证据 | `verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/logs/gates-governance.log` | `42a7f77b97bb6f5a7f133ac5740c2c28eb071839131072bcda80f4f2d4092ea0` |
| 证据 | `verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/logs/discrimination.log` | `93ddc335db6d7179e321ff57908c36869c9cdb4d3abd61cff0b703380bdb9082` |
| 证据工具 | `verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/tools/discrimination.py` | `7d6074657c5b1263d9a033fce3d4c21a1bf5dbc499e9a62b1b3a2170a9bf4573` |
| 证据工具 | `verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/tools/gen_manifest.py` | `91897243fa2c51297e3bc75201649747607bd43b192769a65ea942dbd7e6de31` |
| 证据工具 | `verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/tools/scope_validation.py` | `7886534e67c7040b747d9ffc8b3c9556b5f6467f2d87410021205d9c9a83b503` |

> **自引用口径**：`EV.md` 不自我列入；`RESOURCE-MANIFEST.json` 在 `EV.md` 之后生成并**覆盖本目录全部文件（含 `EV.md`）**，因此其自身 sha256 不在此表（避免循环）。两者的 sha256 由 Lead closeout 时在卡面 Canonical Evidence 钉住。

### 5.3 文档（同批文档提交）

| 类别 | path | sha256 |
|---|---|---|
| 卡面（AC/交付记录） | `doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1.md` | `c18a2a3497a471d2a555e42975c681ddcbb909e8da9c29c63f97bedc6e0f00a0` |
| Handoff | `doc/handoffs/FEA-11-L-S1-REGISTRY-RESILIENCE-1-b56c5a0e6.md` | `22b902f664e0979008c449b48de57f48018eb66c39bfbd7d47b091a0bf9ad1fe` |
| 契约面 | `doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md` | **本卡零 diff**（v1.5 由 `FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1` 冻结，pin `f9e376a0ed4c`） |

> sha256 为**工作树字节**（检出配置 `core.autocrlf=true`；`verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/**` 未设 eol pin，与 RUN-GRANT-1/2A 证据同口径）。`RESOURCE-MANIFEST.json` 的仓外隔离根聚合 sha256 覆盖 workspace 全部文件（含 IPC 夹具与 discrimination 备份），逐文件详情见该 JSON 的 `children`；该 JSON 同时记录 `delivery_head`。

## 6. 复现命令

```powershell
# 1) 构建
dotnet build apps/desktop-avalonia/NewManga.sln -c Release
# 2) 定向 / Host 单测 / gated 真机 IPC（混合 registry）
C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q
dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~SourceRegistry"
$env:NEWMANGA_FEA11_IPC=1; dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~Ipc_MixedRegistry"
# 3) 全量（跑后恢复 FEA-09 tracked 字节）
C:/Python314/python.exe -m pytest tests -q; git checkout -- verification/FEA-09
dotnet test apps/desktop-avalonia/NewManga.sln -c Release; git checkout -- verification/FEA-09
# 4) 治理
pwsh -NoProfile -File tools/governance/verify_pins.ps1
pwsh -NoProfile -File tools/governance/check.ps1
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1.md
C:/Python314/python.exe tools/generate_api_inventory.py --check
# 5) 范围 + 判别性（判别性会临时改写并恢复实现文件；勿与并发实施同文件者同时运行）
C:/Python314/python.exe verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/tools/scope_validation.py
C:/Python314/python.exe verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/tools/discrimination.py
```

## 7. limitations / 未宣称（closeout 必须保留）

- **B（恢复/重授权入口不存在，未修）**：产品内仍无根级恢复/重授权入口（`source_reset_registry`/`source_revoke_root` App 侧 0 调用）。本卡只让「撤销/重置命令在 registry 部分不可用时仍可用」，**不**宣称用户可自行恢复；被替换根在该入口接线前无法在产品内恢复（B 卡）。
- **C（`.corrupt-*` 无界复制，未修）**：每次 `Load` 失败复制一份且无清理；本卡消除了「根缺失」这一主驱动，文件级损坏的放大仍在（另案）。
- **错误码码义收窄（零新增码）**：`SOURCE_REGISTRY_UNAVAILABLE` 现同时表示「文件级损坏」与「该请求所属根当前不可用」；词表细化需 C-16 §6 + C-06 各 1 pin，另案。
- **D-6 投影不在本卡**：`SourceScanScheduler`/`HostRuntime`/`SourceWatcher` 的可用性投影未改；`SourceScanScheduler.cs:1570-1571` 注释仍描述旧「整库不可读」口径（**注释过时，行为已按目标级 typed 工作**：既有 `Executor_EnumeratedTarget_ColdStartMissingRoot_IsRegistryUnavailable` / `..._ReplacedRoot_...` 仍绿）。
- **调度器级 mixed-registry 用例未新增**：`SourceScanSchedulerTests.cs` 不在 frozen `allowed_paths`（D-6）→ 以「registry 级混合单测 + 既有单目标 scheduler 用例 + 真实 IPC 混合」组合证据替代，**不**宣称调度器级混合矩阵已覆盖。
- **被替换根的物理「删除+重建」夹具未用**：NTFS 可能复用 File ID（scope review R4 flaky 风险），确定性夹具改为「注册侧 identity 与当前 identity 不匹配」（与替换后状态等价）；调度器既有真实重建用例保留并绿。
- **`SourceRegistryTests.cs` 未改**：既有覆盖原样保留，新矩阵在新文件，不重复断言。
- **未宣称**：不写「恢复已可用」「根级问题全解」「L-R1 全修」「调度器级混合矩阵已覆盖」；FEA-11 AC11-5/AC11-9 未回填；独立 Review 由 Lead 指派。

## 8. 生成信息

- generated_at_utc=2026-11-07T00:20:00+00:00（Asia/Shanghai 08:20；本文件为 Owner 手写，sha256 使用 `Get-FileHash -Algorithm SHA256` 实测值）
- delivery_head=b56c5a0e6adf6f4cba31f1b3b1d8ee950c7bb84b
- repo_head_at_generation=0ebb234bfd505ed72a351395b56c9a63303d5274（同期 L-S4 提交在 delivery_head 之后；不影响本卡字节与范围判定）
- generator=Owner 手写 + `verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/tools/{scope_validation,discrimination,gen_manifest}.py`
