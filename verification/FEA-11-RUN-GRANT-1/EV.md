# FEA-11-RUN-GRANT-1 Canonical Evidence（Run-scoped source-read 授权）

> 结论先行：本卡交付 **C-16 v1.3 §2.4 `AuthorizeSourceReadForRun`**（Core host-control 授权建立命令，第三 `_bindings` 生产者）与 **Host 铸造/绑定/接线**（Run 前置授权：mint → bind → dispatch；失败不 dispatch、返回授权自身 typed code）。在 **真实 migrations 库 + 真实 zip/PNG + 真实签名 grant + `assemble_core_services`** 下，经本命令绑定后 Run 目标展开、provider 读取**当前 binding** 像素、commit guard 通过、真实 Run 提交写出 region/revision/lineage。**不宣称**「referenced Run 全场景可用」或「L-R1 全修」：仍受 L-G1（300s 窗口）、L-G2（加密源）、L-G8（铸造 I/O 成本）、L-G9（Core 重启）、L-G10（两读面 gate 差异）、L-G11（Host 不提供 page→binding）、以及本卡实测的 **L-G12（Host 无 Core version 通道）** 限制；只承诺「窗口内可用 + Host 源范围/version 已知时可用」。

| 项 | 值 |
|---|---|
| task | `FEA-11-RUN-GRANT-1`（冻结卡 `doc/tasks/FEA-11-RUN-GRANT-1.md`；`status` 未改） |
| Owner | `run-grant-impl`（DSH Agent Teams teammate；Lead `lead`） |
| base | 卡 `base_commit=2067789ea`；实现起点 `a94052ba7` |
| delivery_head | `7ff49f1cc21346be0b4867304499ee17f7ffb84e`（实现+测试提交；证据/卡/Handoff 为同批文档提交） |
| 分支/工作树 | `main` / `G:\CODEX\New Manga`（未创建 linked worktree、未 push） |
| 解释器/环境 | CPython 3.14.6 / PowerShell 7 / .NET SDK（net9.0 测试目标）/ Windows 11 10.0.26300 |
| 契约字节 | **零变更**（`doc/plan`、`doc/contracts`、`schema.py`、迁移、依赖、`core_assembly.py`、`NewManga.App/**` 全空 diff；pins 18/18） |
| 依赖 | **零新增** |
| R-12 扩域 | `tests/core/test_core_service.py`、`tests/fea09/test_referenced_wire.py`（仅 capabilities 精确期望 additive +1；Lead 提交 `218775bca` 批准） |

## 1. 交付 commit 链（base `a94052ba7` → delivery_head `7ff49f1cc21346be0b4867304499ee17f7ffb84e`）

```text
7ff49f1cc test(fea-11-run-grant-1): discovery tests for the Run-scoped authorization (Python + .NET IPC)
85eace738 feat(fea-11-run-grant-1): C-16 v1.3 §2.4 AuthorizeSourceReadForRun + Host mint/bind wiring
218775bca docs(fea-11-run-grant-1): DSH 裁决 R-12 最小扩域（+tests/core/test_core_service.py、tests/fea09/test_referenced_wire.py；capabilities 精确等值断言 additive）
```

## 2. 门禁实测（`7ff49f1cc`）

| Gate | 命令 | 结果 | 日志 |
|---|---|---|---|
| 定向（AC-R1/R2/R3/R5） | `C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | **PASS 49 passed** | `logs/feature.log` |
| 真实 IPC（AC-R4） | `$env:NEWMANGA_FEA11_IPC=1; dotnet test ... --filter "FullyQualifiedName~Fea11RunGrant"` | **PASS 2 passed**（不设 env 时 2 skipped） | `logs/host-ipc.log` |
| Host 单测（AC-R4/R5） | `dotnet test ... --filter "FullyQualifiedName~SourceRegistry"` | **PASS 5 passed** | `logs/host-unit.log` |
| 全量 Python（AC-R6） | `C:/Python314/python.exe -m pytest tests -q` | **PASS 3280 passed / 10 skipped**（卡基线 3249/10，+31） | `logs/full-pytest.log` |
| 全量 .NET（AC-R6） | `dotnet test NewManga.sln -c Release` | **PASS 1535 / 0 / 88**（卡基线 1532/0/86） | `logs/full-dotnet.log` |
| 治理（AC-R6） | `verify_pins.ps1` / `check.ps1`（默认 + `-TaskPath`）/ `generate_api_inventory.py --check` | **18/18 PASS** / **PASS(3 warnings)** / **EXIT=0** | `logs/gates-governance.log` |
| 范围（AC-R6） | `python verification/FEA-11-RUN-GRANT-1/tools/scope_validation.py` | **PASS**（12 文件全 ALLOWED；禁止面全空；minor=3） | `scope-validation.log`、`changed-files.txt` |
| 判别性 | `python verification/FEA-11-RUN-GRANT-1/tools/discrimination.py` | **5/5 破坏点变红 + 5/5 字节级 RESTORED + rebuild OK** | `logs/discrimination.log` |

**跑后恢复**：全量 pytest / 全量 .NET 会重写 tracked `verification/FEA-09/logs/wire-redacted.ndjson`；两次均执行 `git checkout -- verification/FEA-09`（见 `logs/gates-governance.log` 尾注）。**已知 flaky/环境交互**：全量 .NET 首跑 1 例 `NewManga.App.Tests.FluentResidual2VisualEvidenceTests.Captures_Residual2_Visual_Inventory_Only_When_Opted_In` 失败，原因是该用例比较 `git status --porcelain -- verification` 前后快照（当时证据目录在运行中新建 + FEA-09 tracked 字节未恢复）；clean 工作树隔离复跑 **1535/0/88 全绿**，非产品缺陷，Handoff §2 如实记录。skip 说明：pytest 10 skipped 与 .NET 88 skipped 均为既有环境门控（无 provider 权重/GPU、sidecar/UI 集成 opt-in、本卡 2 个 `NEWMANGA_FEA11_IPC` 未设时跳过），本卡未新增 skip 条件。

## 3. 判别性验证（≥4 破坏点，删掉实现必须变红）

`logs/discrimination.log`（脚本 `tools/discrimination.py`）逐个破坏一条已提交的生产分支后运行**一个**目标用例，必须变红（exit≠0），随后按**原字节**恢复并复核 sha256，最后重新 build 恢复二进制：

| Case | 破坏点 | 目标用例 | 实测 |
|---|---|---|---|
| B1 | 删除 `authorize_run_bindings` 的映射写入 | `test_real_assembly_bound_grant_opens_the_run_target_provider_and_guard` | **RED_AS_EXPECTED + RESTORED** |
| B2 | 删除容器源 facts 与 `source_locations` 的核验 | `test_scope_and_facts_mismatch_is_refused` | **RED_AS_EXPECTED + RESTORED** |
| B3 | 删除「有 refused 页即整体失败」的原子性 | `test_authorization_is_entry_granular_and_refuses_other_pages` | **RED_AS_EXPECTED + RESTORED** |
| B4 | 删除 `command` 在 `COMMAND_CATALOG` 的取值域校验 | `test_forged_shape_requests_are_invalid_requests` | **RED_AS_EXPECTED + RESTORED** |
| B5 | 删除 Host dispatcher 的 Run 前置授权钩子 | `SourceRegistryTests.RunAuthorizationHookBlocksDispatchAndIsNotCalledForReadOnlyRuns` | **RED_AS_EXPECTED + RESTORED**（final_rebuild exit 0） |

## 4. AC 矩阵（测试 → 证据映射）

| AC | 判定 | 判别性测试 | 证据 |
|---|---|---|---|
| AC-R1 协议面 | MET | `tests/core/test_host_control.py`（host-only/session/closed shape/§6 typed/零 DB 写/能力公告，+13 用例）+ `tests/fea11/test_source_run_grant.py::test_forged_shape_requests_are_invalid_requests`、`::test_real_assembly_bound_grant_opens_the_run_target_provider_and_guard`（幂等） | `logs/feature.log`、`C-16 v1.3 §2.4` |
| AC-R2 真实装配 Run 端到端 | MET | `test_real_assembly_bound_grant_opens_the_run_target_provider_and_guard`、`test_real_run_commit_writes_expected_rows_after_authorization`、`test_real_run_without_authorization_writes_nothing`、`test_authorization_is_entry_granular_and_refuses_other_pages`；判别 B1/B2/B3 | `logs/discrimination.log`、`logs/feature.log` |
| AC-R3 fail-closed 6 例 | MET | `test_missing_grant_is_refused_and_writes_nothing`、`test_expired_grant_is_refused_with_the_frozen_priority`、`test_revoked_grant_is_refused_with_the_frozen_priority`、`test_scope_and_facts_mismatch_is_refused`、`test_pending_publication_gate_blocks_the_authorization`、`test_binding_switched_mid_run_is_typed_and_writes_nothing`、`test_authorization_never_leases_the_source`（source_lease spy 0） | `logs/feature.log` |
| AC-R4 Host 接线/生命周期/IPC | MET | `SourceRegistryTests.RunAuthorizationHookBlocksDispatchAndIsNotCalledForReadOnlyRuns`、`RunAuthorizationHookWithoutARefusalLetsTheRunCommandReachDispatch`、`RunGrantLedgerIsBoundedAndPrunesExpiredGrants`、`Fea11RunGrantIpcTests`（opt-in 2 实跑） | `logs/host-unit.log`、`logs/host-ipc.log` |
| AC-R5 managed 零回归 | MET | `test_managed_targets_are_skipped_not_refused`、`test_forged_shape_requests_are_invalid_requests`（TARGET_METADATA_KEYS 6 键）、全量 pytest/.NET 不降 | `logs/feature.log`、`logs/full-pytest.log`、`logs/full-dotnet.log` |
| AC-R6 零漂移与门禁 | MET | `scope_validation.py`（禁止面全空、minor=3）+ pins/check/API inventory + 全量 pytest/.NET | `scope-validation.log`、`changed-files.txt`、`logs/gates-governance.log` |
| AC-R7 证据/Handoff/不夸大 | MET | 本 EV 逐文件 sha256；`RESOURCE-MANIFEST.json`；Handoff §3 limitations（L-G1/2/8/9/10/11/**12**）与未宣称项；卡面未写「全场景可用/L-R1 全修」 | 本文件、`RESOURCE-MANIFEST.json`、`doc/handoffs/FEA-11-RUN-GRANT-1-7ff49f1cc.md` |

## 5. 逐文件 sha256

### 5.1 交付文件（实现 + 测试，`7ff49f1cc`）

| 类别 | path | sha256 |
|---|---|---|
| 实现/测试 | `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs` | `bde169fc931d53b9deb1666b5b25a08b4b7508ae6fd465c290093c7189efdd47` |
| 实现/测试 | `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs` | `7bebedbaab20f13b73da60e7baffaf18e556fb748dd8001d657dd6b674caef21` |
| 实现/测试 | `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs` | `d3329a613322fa3126dee873fdc8cc3a14d052be599a7a0f0c5b6cc631150e8f` |
| 实现/测试 | `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11RunGrantIpcTests.cs` | `adbe612d93455788e32a14b2be449aec2d0150196c276fe0b6b12add05d1a760` |
| 实现/测试 | `apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRegistryTests.cs` | `959ac418bbbda5d1a15321a908338a4e9b3e4fff4a988973ee6530f4fbd64315` |
| 实现/测试 | `src/bootstrap/core_service.py` | `9afc9d6d4281b024946f3d67b382effc8a0fe81b683b220f6fb6ff471b77a2c6` |
| 实现/测试 | `src/infrastructure/resource_channel/source_read_refs.py` | `c2680a09eef6e6b83d46a7740de797a90ef932a5b667f4752d68a92b3308d45a` |
| 实现/测试 | `tests/core/test_core_service.py` | `55e3dbd88005db2de7f21424817c25c1abf5c65f87828f360bf3215968a69665` |
| 实现/测试 | `tests/core/test_host_control.py` | `87ffdacf85115105c3cdaf82d5d21965d79dc207dc52cad65142b286e4b51239` |
| 实现/测试 | `tests/fea09/test_referenced_wire.py` | `3abcfe4df19242702dd75368a8c2c1b484d0793e350232785b8c74eab3dc8e2b` |
| 实现/测试 | `tests/fea11/test_source_run_grant.py` | `b7c2ef2b13bfd15a28eb400747edcfb5b8f73ce484e779855026ece60524482f` |

### 5.2 证据文件（本目录，`EV.md` 除外）

| 类别 | path | sha256 |
|---|---|---|
| 证据 | `verification/FEA-11-RUN-GRANT-1/changed-files.txt` | `147a6d0ee352d8e5a7f4c63641a49f2b454ee5cf92db2b364c06d4a7d397deb2` |
| 证据 | `verification/FEA-11-RUN-GRANT-1/logs/discrimination.log` | `ecc5c1d345e81026816e9e3f43d891938e79549da7498a148e7111f22ea3e727` |
| 证据 | `verification/FEA-11-RUN-GRANT-1/logs/feature.log` | `528c372ea46af20b4a5daef117658f36e4c02046dc834db5e74ef780fb82b292` |
| 证据 | `verification/FEA-11-RUN-GRANT-1/logs/full-dotnet.log` | `e8af77e75dba41f2dad372102e2f034228616a831569a169e947dc748c23d069` |
| 证据 | `verification/FEA-11-RUN-GRANT-1/logs/full-pytest.log` | `2c6699e84aa70b62ccaf54c87c50afe0c2e1b17f6cba0ce3040f910da526977c` |
| 证据 | `verification/FEA-11-RUN-GRANT-1/logs/gates-governance.log` | `af19250d5c72dda052778802f64a253c861947d82b0875fd626ba68e3b6a2db4` |
| 证据 | `verification/FEA-11-RUN-GRANT-1/logs/host-ipc.log` | `cf9dbf7f0a2db7589026df55ee967c9fd3c97017b9057f6ad5978fe8a23df627` |
| 证据 | `verification/FEA-11-RUN-GRANT-1/logs/host-unit.log` | `11b50a04279c805b9e1904469c04d1d393a6263383fa6ffa34934d5d779044b9` |
| 证据 | `verification/FEA-11-RUN-GRANT-1/RESOURCE-MANIFEST.json` | `476148d20ae0f32bd20f24fea03f320ae9380c8fda7c3fac18769a81db8bfb62` |
| 证据 | `verification/FEA-11-RUN-GRANT-1/scope-validation.log` | `17d5fed66be85f8b11853ce88e14ff3a5b916d5ce387f59aa7adc4a6e1a9e85b` |
| 证据 | `verification/FEA-11-RUN-GRANT-1/tools/discrimination.py` | `38923bcaf84be31016962777de3f095fbbf2c95f3284ab320166a4b790b2aa86` |
| 证据 | `verification/FEA-11-RUN-GRANT-1/tools/gen_ev.py` | `c7a19c484704cfd4ac3dafe4fb6d09bd3f8ef110ab4e2025fdb4e1f42e7d99c3` |
| 证据 | `verification/FEA-11-RUN-GRANT-1/tools/gen_manifest.py` | `6e5d6fd1e97ce3519ee62a279befe2eecba3898966a3c83b559d1071a2f84f10` |
| 证据 | `verification/FEA-11-RUN-GRANT-1/tools/scope_validation.py` | `eb0bc9eb947e72d6bfd20edbba7e3e92f144430606daa9d4b0926ea702fa0186` |

### 5.3 文档（同批文档提交）

| 类别 | path | sha256 |
|---|---|---|
| 卡面（AC/交付记录） | `doc/tasks/FEA-11-RUN-GRANT-1.md` | `77e1a2ac97bfc533ce612d94c0f9318f694359114510fb54817f4a04f9a5dc19` |
| Handoff | `doc/handoffs/FEA-11-RUN-GRANT-1-7ff49f1cc.md` | `c1b645766b65bfb65f16747ace25e0417ebd440ed8697d489a12ae94cf33f991` |

> `RESOURCE-MANIFEST.json` 的仓外隔离根聚合 sha256 覆盖工作区/日志/夹具全部文件（500 个），逐文件详情见该 JSON 的 ``children``。

## 6. 复现命令

```powershell
# 1) 定向
C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q
# 2) 全量 Python（跑后恢复 FEA-09 tracked 字节）
C:/Python314/python.exe -m pytest tests -q; git checkout -- verification/FEA-09
# 3) 真实 IPC（不设 env 时 2 skipped）
$env:NEWMANGA_FEA11_IPC=1; dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~Fea11RunGrant"
# 4) 全量 .NET（跑后恢复 FEA-09）
dotnet test apps/desktop-avalonia/NewManga.sln -c Release; git checkout -- verification/FEA-09
# 5) 治理
pwsh -NoProfile -File tools/governance/verify_pins.ps1
pwsh -NoProfile -File tools/governance/check.ps1
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-RUN-GRANT-1.md
C:/Python314/python.exe tools/generate_api_inventory.py --check
# 6) 范围 + 判别性
C:/Python314/python.exe verification/FEA-11-RUN-GRANT-1/tools/scope_validation.py
C:/Python314/python.exe verification/FEA-11-RUN-GRANT-1/tools/discrimination.py
```

## 7. limitations / 未宣称（closeout 必须保留）

- **L-G1**：单 grant ≤300s；窗口后的提交单元 fail-closed（typed），需重发 Run；定期重铸/重绑 follow-up。
- **L-G2**：加密 referenced 源仍不可 Run（`SOURCE_PASSWORD_REQUIRED` typed，不崩溃）。
- **L-G8**：铸造 I/O 成本与源大小线性相关（容器整文件 SHA-256 / folder 全量哈希），大库未标定。
- **L-G9**：Core 重启后 `_bindings`/grants 丢失，referenced Run 不可续跑（typed fail）。
- **L-G10**：L-R11（`read_gate` 与 resolve 面 gate 的「无 publication 行」判定不一致）另立 follow-up，本卡不碰。
- **L-G11**：binding 解析必须在 Core；Host 只传 `grant_ids + command + scope`。
- **L-G12（本卡实测新增，待 DSH 裁决）**：Host 侧无 Core `version_id` 通道（枚举 DTO 无 version、寒启动 `SourceScanTarget.Version` 固定 `"1"`），生产 Host 用既有 `IssueAsync` 铸出的容器 grant 通常与 `binding.accepted_source_version` 不匹配 → 授权 typed `SOURCE_ACCESS_DENIED`、不 dispatch（fail-closed）。Core 级机制完整可用（真实 grant/facts/entry 匹配）；Host 接线在 Host 已知源携带正确 version 时可用（.NET IPC 冻结 fixture `s1`/`sv1` 实跑成功）。缓解候选见 Handoff §3/§6。
- **未宣称**：不写「referenced Run 全场景可用」「L-R1 全修」；本卡只交付「窗口内可用 + Host 源范围/version 已知时可用」；FEA-11 AC11-5/AC11-9 未回填（由 Lead closeout 决定）。

## 8. 生成信息

- generated_at_utc=2026-11-06T16:49:54+00:00
- delivery_head=7ff49f1cc21346be0b4867304499ee17f7ffb84e
- generator=`verification/FEA-11-RUN-GRANT-1/tools/gen_ev.py`（sha256 由本地文件实时计算）
