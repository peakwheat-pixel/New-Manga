# FEA-11-RUN-GRANT-1 Canonical Evidence（Run-scoped source-read 授权；Review r2 返修版）

> 结论先行：本卡交付 **C-16 v1.3 §2.4 `AuthorizeSourceReadForRun`**（Core host-control 授权建立命令，第三 `_bindings` 生产者）与 **Host 铸造/绑定/接线**。r1（P1=1/P2=3/P3=7）与 r2（P2=2/P3=2）findings 均已处置：Host 预授权为 **best-effort**（能力缺失/无相关源/mint I/O 失败 → 跳过并继续 dispatch；只有 Core 对目标页的 typed 拒绝才阻断，R-5 不变）；**folder kind 检测已修正**（声明 kind 优先 → `Directory.Exists` → folder），并新增**真实目录源 IPC 证据**（folder mint → Core 绑定 `bound_pages=1` → resolve 成功）；AcceptRun 前置授权抽出可测 seam 并有接线测试；能力缺失用例已改为判别性（删能力门即变红）。**不宣称**「referenced Run 全场景可用」或「L-R1 全修」：仍受 L-G1（300s）、L-G2（加密源）、L-G8（mint I/O 成本）、L-G9（Core 重启）、L-G10（两读面 gate 差异）、L-G11（Host 不提供 page→binding）、**L-G12（version 通道 + 多成员容器仅首成员）**、L-G14（AcceptRun prepared-slice）限制；可用边界 = **image 单 entry 源 + folder 源（逐成员匹配）+ zip/cbz/pdf 归档首成员**。独立 **r3 窄面复审由 Lead 指派**。

| 项 | 值 |
|---|---|
| task | `FEA-11-RUN-GRANT-1`（冻结卡 `doc/tasks/FEA-11-RUN-GRANT-1.md`；`status` 未改） |
| Owner | `run-grant-impl`（DSH Agent Teams teammate；Lead `lead`） |
| base | 卡 `base_commit=2067789ea`；实现起点 `a94052ba7` |
| 历史 head | r1 `7ff49f1cc`（r1 reviewed）/ `b28133392`（r1 证据）；r2 `3ffabeb81`（r2 reviewed）/ `781523aab`（r2 证据） |
| 本次 delivery_head | `a11ded0d3794bdb1afa5f7889d2e25aa4ea7b853`（Review r2 返修；证据/卡/Handoff 为同批文档提交） |
| 分支/工作树 | `main` / `G:\CODEX\New Manga`（未创建 linked worktree、未 push） |
| 解释器/环境 | CPython 3.14.6 / PowerShell 7 / .NET SDK（net9.0 测试目标）/ Windows 11 10.0.26300 |
| 契约字节 | **零变更**（`doc/plan`、`doc/contracts`、`schema.py`、迁移、依赖、`core_assembly.py`、`NewManga.App/**` 全空 diff；pins 18/18） |
| 依赖 | **零新增** |
| R-12 扩域 | `tests/core/test_core_service.py`、`tests/fea09/test_referenced_wire.py`（仅 capabilities 精确期望 additive +1；Lead 提交 `218775bca` 批准） |

## 1. 交付 commit 链（base `a94052ba7` → delivery_head `a11ded0d3`）

```text
a11ded0d3 test(fea-11-run-grant-1): r2 discriminators (folder source, capability gate, AcceptRun wiring)
9e1861ee0 fix(fea-11-run-grant-1): folder kind detection + AcceptRun wiring seam (Review r2 R2-01/R2-03)
b8a4b2092 docs(fea-11-run-grant-1): Review r2 报告入库（changes_requested P0=0/P1=0/P2=2/P3=2；R2-01 folder 边界、R2-02 判别性）
781523aab docs(fea-11-run-grant-1): Review r1 处置 evidence + card AC + handoff (delivery head 3ffabeb81)
3ffabeb81 test(fea-11-run-grant-1): Review r1 discriminators (Host best-effort, AC-R4 coverage, L-G12 boundary)
04317256c fix(fea-11-run-grant-1): Host Run pre-authorization is best-effort (Review r1 R1-01/R1-04)
15ecafca3 docs(fea-11-run-grant-1): Review r1 报告入库（changes_requested P0=0/P1=1/P2=3/P3=7；reviewer session 62c6bf16）
cddfc8fad docs(fea-11-run-grant-1): Review r1 处置——AC-R5 口径修订（Core 面 + Host best-effort）、L-G12 扩写（version + 容器成员 entry）、findings 返修清单（P1/P2 必返修）
b28133392 docs(fea-11-run-grant-1): evidence + card AC + handoff (delivery head 7ff49f1cc)
7ff49f1cc test(fea-11-run-grant-1): discovery tests for the Run-scoped authorization (Python + .NET IPC)
85eace738 feat(fea-11-run-grant-1): C-16 v1.3 §2.4 AuthorizeSourceReadForRun + Host mint/bind wiring
218775bca docs(fea-11-run-grant-1): DSH 裁决 R-12 最小扩域（+tests/core/test_core_service.py、tests/fea09/test_referenced_wire.py；capabilities 精确等值断言 additive）
```

## 2. 门禁实测（Review r2 返修后；`a11ded0d3`）

| Gate | 命令 | 结果 | 日志 |
|---|---|---|---|
| 定向（AC-R1/R2/R3/R5） | `C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | **PASS 50 passed** | `logs/feature.log` |
| Host 单测（AC-R4/R5/R1-01/R1-02/R1-04/R2-02/R2-03） | `dotnet test ... --filter "FullyQualifiedName~SourceRegistry"` | **PASS 21 passed**（r1 17 + 4） | `logs/host-unit.log` |
| 真实 IPC（AC-R4/R1-01/R1-03/R2-01） | `$env:NEWMANGA_FEA11_IPC=1; dotnet test ... --filter "FullyQualifiedName~Fea11RunGrant"` | **PASS 3 passed**（含真实 folder 源 mint→绑定→resolve；不设 env 时 3 skipped） | `logs/host-ipc.log` |
| 全量 Python（AC-R6） | `C:/Python314/python.exe -m pytest tests -q` | **PASS 3281 passed / 10 skipped** | `logs/full-pytest.log` |
| 全量 .NET（AC-R6） | `dotnet test NewManga.sln -c Release` | **PASS 1551 / 0 / 89**（r1 r2 基线 1547/0/88，+4 单测；3 个 IPC opt-in 未设 env 时 skipped） | `logs/full-dotnet.log` |
| 治理（AC-R6） | `verify_pins.ps1` / `check.ps1`（默认 + `-TaskPath`）/ `generate_api_inventory.py --check` | **18/18 PASS** / **PASS(3 warnings)** / **EXIT=0** | `logs/gates-governance.log` |
| 范围（AC-R6） | `python verification/FEA-11-RUN-GRANT-1/tools/scope_validation.py` | **PASS（changed=31 全 ALLOWED；禁止面全空；minor=3）** | `scope-validation.log`、`changed-files.txt` |
| 判别性（9 点） | `python verification/FEA-11-RUN-GRANT-1/tools/discrimination.py` | **9/9 破坏点 RED_AS_EXPECTED + 9/9 字节级 RESTORED + rebuild OK** | `logs/discrimination.log` |

**跑后恢复**：全量 pytest / 全量 .NET 会重写 tracked `verification/FEA-09/logs/wire-redacted.ndjson`；均执行 `git checkout -- verification/FEA-09`。**已知 flaky/环境交互**：全量 .NET 首次运行时若 `verification/` 正在写入，`NewManga.App.Tests.FluentResidual2VisualEvidenceTests` 会因 `git status --porcelain -- verification` 快照差异失败；clean tree 隔离复跑 **1551/0/89 全绿**（非产品缺陷）。skip 说明：pytest 10 skipped 与 .NET 89 skipped 均为既有环境门控
（无 provider 权重/GPU、sidecar/UI 集成 opt-in、本卡 3 个 `NEWMANGA_FEA11_IPC` 未设时跳过），本卡未新增 skip 条件。

## 3. 判别性验证（9 破坏点，删掉实现必须变红）

`logs/discrimination.log`（脚本 `tools/discrimination.py`，`repo_head=a11ded0d3`）逐个破坏一条已提交的生产分支后运行**一个**目标用例，必须变红（exit≠0），随后按**原字节**恢复并复核 sha256，最后重新 build 恢复二进制：

| Case | 破坏点 | 目标用例 | 实测 |
|---|---|---|---|
| B1 | 删除 `authorize_run_bindings` 的映射写入 | `test_real_assembly_bound_grant_opens_the_run_target_provider_and_guard` | **RED_AS_EXPECTED + RESTORED** |
| B2 | 删除容器源 facts 与 `source_locations` 的核验 | `test_scope_and_facts_mismatch_is_refused` | **RED_AS_EXPECTED + RESTORED** |
| B3 | 删除「有 refused 页即整体失败」的原子性 | `test_authorization_is_entry_granular_and_refuses_other_pages` | **RED_AS_EXPECTED + RESTORED** |
| B4 | 删除 `command` 在 `COMMAND_CATALOG` 的取值域校验 | `test_forged_shape_requests_are_invalid_requests` | **RED_AS_EXPECTED + RESTORED** |
| B5 | 删除 Host dispatcher 的 Run 前置授权钩子 | `SourceRegistryTests.RunAuthorizationHookBlocksDispatchAndIsNotCalledForReadOnlyRuns` | **RED_AS_EXPECTED + RESTORED** |
| B6 | 删除 Host 预授权 best-effort 跳过（mint 失败重新阻断） | `SourceRegistryTests.RunAuthorizationBestEffortSkipReachesDispatch_CoreRefusalDoesNot` | **RED_AS_EXPECTED + RESTORED** |
| **B7（R2-02 新增）** | 删除能力门（能力缺失仍 mint） | `RunAuthorizerSkipsWhenTheCapabilityIsMissingWithoutMinting` | **RED_AS_EXPECTED + RESTORED** |
| **B8（R2-03 新增）** | 删除 AcceptRun 的授权接线调用 | `AcceptRunAuthorizationSeamUsesTheFrozenSlice` | **RED_AS_EXPECTED + RESTORED** |
| **B9（R2-01 新增）** | 删除 folder kind 检测（目录重新被误判 image） | `RunSourceRangeKindDetectsFolderSources` | **RED_AS_EXPECTED + RESTORED**（final_rebuild exit 0） |

## 4. AC 矩阵（测试 → 证据映射；Review r1/r2 修订后）

| AC | 判定 | 判别性测试 | 证据 |
|---|---|---|---|
| AC-R1 协议面 | MET | `tests/core/test_host_control.py`（host-only/session + 逐表快照零写/closed shape/§6 typed/能力公告，13 用例）+ `test_forged_shape_requests_are_invalid_requests`、`test_real_assembly_bound_grant_opens_the_run_target_provider_and_guard`（幂等） | `logs/feature.log` |
| AC-R2 真实装配 Run 端到端 | MET | `test_real_assembly_bound_grant_opens_the_run_target_provider_and_guard`（真实 `assemble_core_services`：target/provider/commit guard）；`test_real_run_commit_writes_expected_rows_after_authorization`（RENDITION-1 同构 harness：in-memory migrations + `build_run_harness`，非 assemble —— R1-09）；`test_real_run_without_authorization_writes_nothing`；判别 B1/B2/B3 | `logs/discrimination.log`、`logs/feature.log` |
| AC-R3 fail-closed 6 例 | MET | `test_missing_grant_*`、`test_expired_*`、`test_revoked_*`、`test_scope_and_facts_mismatch_is_refused`、`test_pending_publication_gate_blocks_the_authorization`、`test_binding_switched_mid_run_*`；`test_authorization_never_leases_or_reads_the_source`（`source_lease`+`read_entry_bytes` 双 spy 0）；`test_per_page_gate_refusal_uses_the_shared_gate_predicate`（mixed binding per-page gate） | `logs/feature.log` |
| AC-R4 Host 接线/生命周期/IPC | MET | `SourceRegistryTests`（**21 例**：dispatcher 4 命令钩子/只读不触发、pause/stop/abandon、**能力缺失判别性（B7）**、`PreparedRunSlices`、**AcceptRun 接线 seam（B8）**、`RunSourceRange` book 过滤/known=0/unresolved、**folder kind（B9）**、best-effort/Core 阻断判别、剪枝上界）；`Fea11RunGrantIpcTests`（**3 实跑**：首成员成功/多成员 fail-closed/mint 部分失败/**真实 folder 源 mint→绑定→resolve**、wire 无路径） | `logs/host-unit.log`、`logs/host-ipc.log` |
| AC-R5 managed 零回归（修订口径） | MET | Core 面：`test_managed_targets_are_skipped_not_refused`（`bound_pages=0`、零映射、零 DB 写、metadata 6 键）；Host best-effort：`RunAuthorizationBestEffortSkipReachesDispatch_CoreRefusalDoesNot`、`RunAuthorizerTreatsMintFailuresAsBestEffortSkips`、`RunAuthorizerSkipsWhenTheCapabilityIsMissingWithoutMinting`、`RunAuthorizerSkipsWhenTheRegistryCannotBeRead`；IPC mint 失败/partial | `logs/feature.log`、`logs/host-unit.log`、`logs/host-ipc.log`、`logs/full-pytest.log`、`logs/full-dotnet.log` |
| AC-R6 零漂移与门禁 | MET | `scope_validation.py`（changed=31 全 ALLOWED、禁止面全空、minor=3）+ pins/check/API inventory + 全量 pytest/.NET | `scope-validation.log`、`changed-files.txt`、`logs/gates-governance.log` |
| AC-R7 证据/Handoff/不夸大 | **PARTIAL（待 r3）** | 本 EV 逐文件 sha256；`RESOURCE-MANIFEST.json`（含动态 `delivery_head`）；Handoff §3 limitations（L-G1/2/8/9/10/11/**12 修正**/13/**14**）与未宣称项；卡面未写「全场景可用/L-R1 全修」；**r1/r2 findings 均已处置 → 独立 r3 窄面复审待 Lead 指派** | 本文件、`RESOURCE-MANIFEST.json`、Handoff |

### 4.1 Review r1/r2 findings 处置映射

| Finding | 状态 | 判别性证据 |
|---|---|---|
| R1-01（P1）Host best-effort | CLOSED（r2 确认） | B6、`RunAuthorizationBestEffortSkipReachesDispatch_*`、IPC mint/partial |
| R1-02①④（P2） | CLOSED（r2 确认） | `RunCommandPolicy`/pause-stop、`RunSourceRange` |
| R1-02②（P2）能力缺失判别 | **FIXED（r2）** | `RunAuthorizerSkipsWhenTheCapabilityIsMissingWithoutMinting`（known 源 + 计数）、`RunAuthorizerCapabilityMissingStillReachesDispatch`、**B7** |
| R1-03（P2）L-G12 | **FIXED（r2 修正）** | L-G12 边界重写；**真实 folder 源 IPC**、`RunSourceRangeKindDetectsFolderSources`、**B9** |
| R1-04（P2）typed 错误面 | CLOSED（r2 确认） | `MapMintFailure` 单测、IPC missing/partial |
| R1-05…R1-11（P3） | CLOSED（r2 确认） | 卡 I-1/I-2、双 spy、mixed gate、EV harness 措辞、L-G14 |
| R2-01（P2）folder 边界 | **FIXED** | `KindOfSource` 修正 + folder IPC + B9 |
| R2-02（P2）能力缺失判别 | **FIXED** | 见 R1-02② + B7 |
| R2-03（P3）AcceptRun 接线 | **FIXED** | `HostRuntime.AuthorizePreparedRunForAcceptAsync` + 2 接线用例 + B8 |
| R2-04（P3）I-2/Manifest 口径 | **FIXED** | 卡 I-2 两行改写；Manifest `delivery_head`/`source_path` 动态更新 |

## 5. 逐文件 sha256

### 5.1 交付文件（实现 + 测试，`a11ded0d3`）

| 类别 | path | sha256 |
|---|---|---|
| 实现/测试 | `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs` | `bde169fc931d53b9deb1666b5b25a08b4b7508ae6fd465c290093c7189efdd47` |
| 实现/测试 | `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs` | `6184a0f0b7bca202c1eaa832103a7265de1e94d09969c3b62d580d20cf201802` |
| 实现/测试 | `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs` | `218ed792496a4a8efb723da62abbbf8ceb8f935c43373b21417f83cdb1b969c7` |
| 实现/测试 | `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11RunGrantIpcTests.cs` | `3c0879cc5c41bfab100bdd755055c1c85eac71ee390ab6946de62c5a5ce20d18` |
| 实现/测试 | `apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRegistryTests.cs` | `b75f836ffccfb0e4bceab6e9240e5a3a6f94e05d449cf766a590c429574012f8` |
| 实现/测试 | `src/bootstrap/core_service.py` | `9afc9d6d4281b024946f3d67b382effc8a0fe81b683b220f6fb6ff471b77a2c6` |
| 实现/测试 | `src/infrastructure/resource_channel/source_read_refs.py` | `c2680a09eef6e6b83d46a7740de797a90ef932a5b667f4752d68a92b3308d45a` |
| 实现/测试 | `tests/core/test_core_service.py` | `55e3dbd88005db2de7f21424817c25c1abf5c65f87828f360bf3215968a69665` |
| 实现/测试 | `tests/core/test_host_control.py` | `07e0876390f51978375cfb3f37ccd47f495bde836768c7f61b20c2e4ac6bc8bc` |
| 实现/测试 | `tests/fea09/test_referenced_wire.py` | `3abcfe4df19242702dd75368a8c2c1b484d0793e350232785b8c74eab3dc8e2b` |
| 实现/测试 | `tests/fea11/test_source_run_grant.py` | `d186c7e076fac587c5e6170e9fd9bdd8222fc80880b4e21f2996b5f91b3f24d8` |

### 5.2 证据文件（本目录，`EV.md` 除外）

| 类别 | path | sha256 |
|---|---|---|
| 证据 | `verification/FEA-11-RUN-GRANT-1/changed-files.txt` | `362f9b12839fd144c10bcad0ec7b2fe6122a8eb215c3d6afd5e56d205a9db607` |
| 证据 | `verification/FEA-11-RUN-GRANT-1/logs/discrimination.log` | `97bb690ab99945b3d4667b8e0d3642c7ea432c7d2391a5320f433b1575a3bfb4` |
| 证据 | `verification/FEA-11-RUN-GRANT-1/logs/feature.log` | `f462f7342634e250b898dfc9409ecf4379bd87999e5595d6e73b566a996fdb33` |
| 证据 | `verification/FEA-11-RUN-GRANT-1/logs/full-dotnet.log` | `a19eb94884b31273b90e4c9a39edca1fb7c93736807e6a5db90e3d2b1d3a518b` |
| 证据 | `verification/FEA-11-RUN-GRANT-1/logs/full-pytest.log` | `9b6a79a6369e0da485bdf9a97834ce1869b184e01f37e3cea919ea8462c232de` |
| 证据 | `verification/FEA-11-RUN-GRANT-1/logs/gates-governance.log` | `b53fef2eac8d7922184f301eb1bc42204fd6884177c9f132f81f29672f0c29af` |
| 证据 | `verification/FEA-11-RUN-GRANT-1/logs/host-ipc.log` | `ebfb8992fc22e7f176cb5217805db487ebc132aebda7e336d356f572ab68d7e5` |
| 证据 | `verification/FEA-11-RUN-GRANT-1/logs/host-unit.log` | `cb170efb19f3d288ade97ff27d1b920b56945634a3187e02e7cef8a7aa8d5aee` |
| 证据 | `verification/FEA-11-RUN-GRANT-1/RESOURCE-MANIFEST.json` | `9d1f22f65da39ddbd424d7a88fa42c43fd8da5845f6d9e6dbdf7c689ea5171dd` |
| 证据 | `verification/FEA-11-RUN-GRANT-1/scope-validation.log` | `a7ed90938f4467fcd2575a45cc4b77919d54015d470090176394533a1811de4c` |
| 证据 | `verification/FEA-11-RUN-GRANT-1/tools/discrimination.py` | `0a931b6a8c8a17259b9408abac762f8ad14bd544d73b2604047d0686099a5ce2` |
| 证据 | `verification/FEA-11-RUN-GRANT-1/tools/gen_ev.py` | `527a22593a5444137aa263d655f05058fd939cc89bb4e009bc3e23edd4b373fe` |
| 证据 | `verification/FEA-11-RUN-GRANT-1/tools/gen_manifest.py` | `f7a551a71a7aaa9622d33b382b6bb61e21d8bfc9d3e7e3ec2a84574961d64066` |
| 证据 | `verification/FEA-11-RUN-GRANT-1/tools/scope_validation.py` | `eb0bc9eb947e72d6bfd20edbba7e3e92f144430606daa9d4b0926ea702fa0186` |

### 5.3 文档（同批文档提交）

| 类别 | path | sha256 |
|---|---|---|
| 卡面（AC/处置记录） | `doc/tasks/FEA-11-RUN-GRANT-1.md` | `47e18d490010839d7349e4ef75b8d9217a23e68fb7a342e7b6e1944024aba6d6` |
| Handoff（Review r2 返修） | `doc/handoffs/FEA-11-RUN-GRANT-1-a11ded0d3.md` | `298fa8a349d35c4094f71a83debbfb92315fc5efb96d5dafaff9b7e28630b27b` |

> `RESOURCE-MANIFEST.json` 的仓外隔离根聚合 sha256 覆盖工作区/日志/夹具全部文件（1455 个），逐文件详情见该 JSON 的 ``children``；该 JSON 同时记录 `delivery_head`。

## 6. 复现命令

```powershell
# 1) 定向
C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q
# 2) Host 单测 / 真实 IPC（含 folder 源）
dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~SourceRegistry"
$env:NEWMANGA_FEA11_IPC=1; dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~Fea11RunGrant"
# 3) 全量（跑后恢复 FEA-09 tracked 字节）
C:/Python314/python.exe -m pytest tests -q; git checkout -- verification/FEA-09
dotnet test apps/desktop-avalonia/NewManga.sln -c Release; git checkout -- verification/FEA-09
# 4) 治理
pwsh -NoProfile -File tools/governance/verify_pins.ps1
pwsh -NoProfile -File tools/governance/check.ps1
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-RUN-GRANT-1.md
C:/Python314/python.exe tools/generate_api_inventory.py --check
# 5) 范围 + 判别性
C:/Python314/python.exe verification/FEA-11-RUN-GRANT-1/tools/scope_validation.py
C:/Python314/python.exe verification/FEA-11-RUN-GRANT-1/tools/discrimination.py
```

## 7. limitations / 未宣称（closeout 必须保留）

- **L-G1**：单 grant ≤300s；窗口后的提交单元 fail-closed（typed），需重发 Run；定期重铸/重绑 follow-up。
- **L-G2**：加密 referenced 源仍不可 Run（`SOURCE_PASSWORD_REQUIRED` typed，不崩溃）。
- **L-G8**：铸造 I/O 成本与源大小线性相关（容器整文件 SHA-256 / folder 全量哈希），大库未标定。
- **L-G9**：Core 重启后 `_bindings`/grants 丢失，referenced Run 不可续跑（typed fail）。
- **L-G10**：L-R11（`read_gate` 与 resolve 面 gate 的「无 publication 行」判定不一致）另立 follow-up。
- **L-G11**：binding 解析必须在 Core；Host 只传 `grant_ids + command + scope`。
- **L-G12（r2 修正）Host→Core 源身份通道缺失**：①**version 通道**（枚举 DTO 无 version、寒启动 version 固定 `"1"`）→ 生产 Host grant 的 `scope.version` 通常与 `binding.accepted_source_version` 不匹配 → typed `SOURCE_ACCESS_DENIED`、不 dispatch（fail-closed）；②**容器成员 entry 身份通道**（Host 单容器 entry、locator=容器名/ordinal=0 vs Core 成员 `source_entries` 匹配）→ 多成员归档只有首成员可被授权，其余 fail-closed。**当前可用边界 = image 单 entry 源 + folder 源（逐成员匹配，真实目录源 IPC 证明）+ zip/cbz/pdf 归档首成员**；follow-up 候选 `FEA-11-RUN-GRANT-2`（proposed）。
- **L-G14（R1-11）**：`HostRuntime.AcceptRunAsync` 需同进程先 `PrepareRunAsync`（冻结 slice），缺失/过期 → `RUN_STALE_PREVIEW`；仓内 App 无 Prepare/Accept 调用点。
- **未宣称**：不写「referenced Run 全场景可用」「L-R1 全修」；只交付「窗口内可用 + image 单 entry 源 + folder 源 +归档首成员（L-G12 边界）」；FEA-11 AC11-5/AC11-9 未回填；独立 r3 窄面复审由 Lead 指派。

## 8. 生成信息

- generated_at_utc=2026-11-06T18:35:54+00:00
- delivery_head=a11ded0d3794bdb1afa5f7889d2e25aa4ea7b853
- generator=`verification/FEA-11-RUN-GRANT-1/tools/gen_ev.py`（sha256 由本地文件实时计算）
