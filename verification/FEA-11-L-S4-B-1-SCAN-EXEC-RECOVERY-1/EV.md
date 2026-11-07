# FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1（L-S4-B-1）：扫描执行面恢复 — 证据（EV）

> 本 EV 只陈述**实跑**事实；未跑项目逐项标注。措辞红线（AC-SER-6）：只承诺
> **枚举 target 的扫描执行恢复**——即用户完成 B1 显式「重新授权」→ 既有 refresh 完成 reattest →
> 枚举恢复之后，**下一个未被既有 backoff 抑制的 tick** 可用 target 自身已核验的 live
> `(registry_id, generation)` 铸 grant 并成功发送 `ScanSourceSync`。**不**承诺 Run 面恢复、**不**承诺
> 撤销后自动恢复/自动重新授权/自愈，**不**承诺 folder、B2、L-S4-1、L-R1。

- Task：`doc/tasks/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1.md`（Owner=`l-s4b1-impl`，Lead=`lead`；卡面 `status` 由 Lead 维护，本 EV 不改）
- 契约：**零契约变更**（0 UNFREEZE / 18 pins 不变；C-16 v1.5 `a7f57ebd…`、C-17 v1.1 `aefa0fa5…` 字节零改动）
- 卡 `base_commit=58395b9a2`；**实现起点 `16082d3a9`**（Lead 释放提交，`main` clean）
- **delivery_head=`bcc88e4a2`**；交付 commit 链：
  - `8709d6159` feat：`SourceScanScheduler.cs` 枚举 target 执行面改用自身已核验 live entry（+ 纯函数 `SelectEnumeratedEntry`）
  - `bcc88e4a2` test：新增 `SourceScanExecutionRecoveryTests.cs`（8 例）+ gated IPC `Fea11ScanIpcTests` 断言 tick 由 error 升级为 ok
  - （随后同批 docs/evidence 提交记录本 EV/Handoff/卡面；不属于实现字节）
- 权限依据：卡面 + 权威 scope review `doc/reviews/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1-scope-r1.md`（READY-TO-FREEZE；推荐 Host-only 形状；0 UNFREEZE / 18 pins 不变）+ ZCode 故障转移裁决（READY-TO-FREEZE，无翻案项；TOCTOU/backoff/scope 提示）
- 环境：Windows 11 / PowerShell 7 / CPython 3.14.6 / .NET SDK 10.0.401（测试目标 net9.0）；零新依赖、零 schema/迁移、零 Core/Python 改动

## 1. AC 达成（AC-SER-1…6 全 MET）

| AC | 结果 | 关键证据（实跑） |
|---|---|---|
| **AC-SER-1 枚举执行面恢复（主 AC）** | MET | `SourceScanScheduler.cs`：`VerifyEnumeratedTarget(target, out entry)` 以 out 参数返回**同一次 `Registry.List()` 快照**中已核验的 live 条目，`ScanAsync` 枚举分支直接以它铸 grant（不再二次 `ResolveRegistryEntry(target.Path)`）。单测 `SourceScanExecutionRecoveryTests.SelectEnumeratedEntry_UsesTheTargetsOwnLiveEntry_WhenARevokedSiblingSharesThePath`：同一 entries 快照下**旧路径解析返回 null**（before）而按 target 自身 id 选中 live 条目；`ScanAsync_RecoveredEnumeratedTarget_PassesTheAuthorizationGate_InsteadOfBeingDenied` 证明 recovered target 越过授权门（不再返回 `Error(SOURCE_ACCESS_DENIED)`）。gated 真 IPC：`tick_verdict.last_result="ok"`、`scan_frames=1`、`counts.unchanged=1`（见 §2、`logs/ipc-closed-loop.json`） |
| **AC-SER-2 fail-closed 矩阵不变** | MET | `SelectEnumeratedEntry` 对 target **自己的** registry 逐项 typed：缺失 → `Skipped(SOURCE_REGISTRY_UNAVAILABLE)`、撤销 → `Skipped(SOURCE_GRANT_REVOKED)`、代次漂移 → `Skipped(SOURCE_REGISTRY_BUSY)`；root 缺失/替换 → `Error(SOURCE_REGISTRY_UNAVAILABLE)`；整库不可读 → 既有 typed（`Error(SOURCE_REGISTRY_UNAVAILABLE)`）。单测：`SelectEnumeratedEntry_IsTypedOnMissingRegistryAndGenerationDrift`、`SelectEnumeratedEntry_NeverFallsBackToALiveSibling_WhenTheTargetsOwnEntryIsRevoked`、`ScanAsync_EnumeratedTarget_OwnRegistryRevokedMissingOrDrifted_IsTypedSkip`、`ScanAsync_EnumeratedTarget_MissingOrReplacedRoot_IsRegistryUnavailable`、`ScanAsync_EnumeratedTarget_UnreadableRegistry_IsTypedFailClosed`；既有 4 条 `SourceScanSchedulerTests.Executor_EnumeratedTarget_*` 原样通过。全部 typed 路径**零 grant/零 frame**（null-Core fixture 下若发生 mint/frame 会抛异常而非返回 outcome） |
| **AC-SER-3 非枚举语义零变化** | MET | `ResolveRegistryEntry` 实现字节未改（仅注释补充「服务非枚举 target」）；既有 `SourceScanSchedulerTests.RegistryResolution_PrefersExactMatch_AndFailsClosedOnRevokedExactEntry` 原样通过；新增 `ScanAsync_NonEnumeratedTarget_KeepsThePathResolverSemantics`（exact-first / revoked-exact→null / containment fallback + executor 层 `Error(SOURCE_ACCESS_DENIED)`） |
| **AC-SER-4 无自动授权/无 identity 重建/不写 registry 结构** | MET | 扫描路径不调用 `Register`/`Revoke`/`Reset`；不写 roots/identity/generation；单测在 recover/fail-closed/根缺失/替换前后比较 `DescribeRegistryEntries`（不含既有 `last_used_at`）**全等**，旧 revoked 行仍在且 `revoked_at`/generation 不变、条目数不变；gated IPC 断言 reattest 后与 tick 后 Host registry 结构全等（`host_registry_unchanged=true`） |
| **AC-SER-5 零漂移/门禁** | MET | pins **18/18**（C16 `a7f57ebd…`、C17 `aefa0fa5…`、C15 `f9e376a0…`）；C-16/C-17 git blob 与实现起点**逐 blob 相同**；`PROTOCOL_MINOR=3`；check（默认 + `-TaskPath`）**PASS(3 warnings)**；API inventory **EXIT=0**（61 不变）；scope diff ⊆ allowed_paths（changed=23，禁止面零 diff）；全量 pytest **3360/10**（起点实测同值，不降）；全量 .NET **1652/0/94**（起点 1644/0/94，+8 为本卡新增测试；94 skipped 不变）；跑后 `verification/FEA-09` 已恢复 |
| **AC-SER-6 不夸大** | MET | 本 EV/Handoff/卡面只承诺**枚举 target 的扫描执行恢复**（且限定「B1 显式动作 → 既有 refresh（冷启动/App 成功分支）→ 枚举 → 下一个未被 backoff 抑制的 tick」）；明确登记 Run 面（`HostRuntime.RunSourceRange` 仍走按路径解析）、B2、folder（L-S4-2）、L-S4-1、L-R1 保留；未写「自动恢复/自愈/自动重新授权/撤销后自动放行」 |

### before / after（同一 gated 测试，生产/测试字节判别）

| 状态 | 证据 | tick 结果 |
|---|---|---|
| **before**：L-S4-B 交付时的同一闭环（`30bdeb4ce`） | `verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/logs/ipc-closed-loop.json` | `last_result="error"`（`SOURCE_ACCESS_DENIED`：path 解析先命中同路径 revoked 旧行；L-S4-B 只承诺枚举恢复） |
| **after**：本卡 `bcc88e4a2` | `verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/logs/ipc-closed-loop.json`（测试原样落盘后复制） | `last_result="ok"`、`scan_frames=1`、`counts.unchanged=1`、`path_hits=0`、`host_registry_unchanged=true`、`other_tables_unchanged=true` |
| 判别性破坏：把枚举分支改回 path resolver（B1/B1b） | `logs/discrimination.log` | 单测 RED + **gated 同一测试 RED**；恢复后复绿 |

## 2. 定向 / gated / 全量（实跑）

| 场景 | 命令 | 结果 | 日志 |
|---|---|---|---|
| 构建 | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` | **PASS（0 warning / 0 error）** | `logs/build.log` |
| Host 单测（新） | `dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~SourceScanExecutionRecovery"` | **8 passed / 0 failed / 0 skipped** | `logs/host-unit.log` |
| 回归（registry/scheduler/reattest） | 同上 `--filter "FullyQualifiedName~SourceRegistry\|FullyQualifiedName~SourceReattest\|FullyQualifiedName~SourceScanSchedulerTests"` | **123 passed / 0 failed / 1 skipped**（skipped = 既有另一 gated 用例，需其独立环境变量；含 L-S4-B `SourceReattestTests` 24 例与既有 scheduler 全量） | `logs/regression.log` |
| gated 真 IPC | `NEWMANGA_FEA11_IPC=1 dotnet test … --filter "FullyQualifiedName~Fea11ScanIpc"` | **4 passed / 0 failed / 0 skipped**（含升级后的 B1→reattest→枚举→**tick ok** 闭环） | `logs/host-ipc.log`、`logs/ipc-closed-loop.json/.txt`、`logs/ipc-fixture.txt` |
| 定向 pytest（回归） | `C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | **89 passed / 0 failed**（卡面命名「定向 74」的实跑计数 89；本卡零 Python 改动） | `logs/regression-74.log` |
| 全量 Python | `C:/Python314/python.exe -m pytest tests -q` | **3360 passed / 10 skipped / 257.51s**（实现起点实测同值，无降级） | `logs/full-pytest.log` |
| 全量 .NET | `dotnet test NewManga.sln -c Release`（cwd `apps/desktop-avalonia`） | **1652 passed / 0 failed / 94 skipped**（起点 1644/0/94；+8 = 本卡新测试） | `logs/full-dotnet.log` |
| 治理 pin | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PIN AUDIT: PASS (all 18)**，EXIT=0 | `logs/gates.log` |
| 治理 check | `check.ps1`（默认）与 `check.ps1 -TaskPath doc/tasks/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1.md` | **PASS (3 warnings)** ×2，EXIT=0 | `logs/gates.log` |
| API inventory | `C:/Python314/python.exe tools/generate_api_inventory.py --check` | **EXIT=0**（IHostController 54 + IRunController 6 + IReaderProgressSink 1 = **61** 不变） | `logs/gates.log` |
| scope | `C:/Python314/python.exe verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/tools/scope_validation.py` | **PASS**（delivery 23 文件全 ALLOWED；禁止面零 diff；`PROTOCOL_MINOR=3`；C16/C17 blob 零漂移；卡 `status` 未改） | `scope-validation.log`、`changed-files.txt` |
| 判别性 | `C:/Python314/python.exe verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/tools/discrimination.py` | **6/6 RED_AS_EXPECTED + 逐例 sha256 复原 + 复绿** | `logs/discrimination.log` |

- **跑后恢复**：全量 .NET 重写 tracked `verification/FEA-09/logs/wire-redacted.ndjson` → 已 `git checkout -- verification/FEA-09`（`git status -- verification/FEA-09` 为空）。
- **证据容器**：`scope-validation.log` / `changed-files.txt` 的 delivery 列表（23）在 `RESOURCE-MANIFEST.json` 生成**之前**采集，故不含 manifest 自身（manifest 是容器、不自我哈希）；manifest 逐文件 sha256 见 §8/文件本身。
- **并发披露**：共享 `main` 同期仅 Lead 的 docs 提交（`16082d3a9` = 释放实现起点；`58395b9a2..16082d3a9` 实测 docs-only）。本卡提交全部显式 pathspec，未夹带他人字节；`git diff 16082d3a9..HEAD -- src tests`（Python/Core）为零。

## 3. 判别性（6/6，`logs/discrimination.log`）

| # | 破坏点 | 目标用例 | 结果 |
|---|---|---|---|
| B1 | 枚举分支改回按路径 `ResolveRegistryEntry` | `ScanAsync_RecoveredEnumeratedTarget_PassesTheAuthorizationGate…` | **RED**（返回 `Error(SOURCE_ACCESS_DENIED)`） |
| B1b | 同上破坏点，在 **gated 真 IPC** 闭环上 | `Fea11ScanIpcTests.ReauthorizedSource_IsReattested_ThenEnumerated_WithoutReimport` | **RED**（tick 非 ok / 无 `ScanSourceSync`） |
| B2 | 删 `SelectEnumeratedEntry` 的撤销检查（撤销后自动放行） | `SourceScanExecutionRecovery`（2 例） | **RED** |
| B3 | 删代次漂移检查 | `SourceScanExecutionRecovery`（2 例） | **RED** |
| B4 | 删注册根 volume/file identity 比较（把替换文件当同一源） | `ScanAsync_EnumeratedTarget_MissingOrReplacedRoot…` | **RED** |
| B5 | target 自身条目缺失时回落任意 live 条目（扩授权面） | `SourceScanExecutionRecovery`（2 例） | **RED** |

驱动逐例：写入破坏 → 目标测试必须非 0 退出 → 原字节回写（sha256 = `a528e8da…`，MATCH=True）→ 复跑必须绿。最终树 `final_sha256` 与原始一致。

## 4. 实现摘要（只读变更，零契约）

- `SourceScanScheduler.cs`
  - `VerifyEnumeratedTarget(target, out SourceAuthorization? entry)`：在**同一次** `Registry.List()` 快照上核验并把已核验的 live 条目交给调用方（消除 verify→mint 之间第二次 `List()` 的 TOCTOU 窗口；revoke 仍由 mint 内 `Authorize` 兜底）。
  - `ScanAsync`：枚举 target 使用该 out 条目；**非枚举 target 仍用** `ResolveRegistryEntry(target.Path)`（语义零变化）。
  - 新增 `public static SelectEnumeratedEntry(entries, target, out verdict)`：纯函数（无 I/O、无写）；只接受 target 自己的 `registry_id` 且 `revoked_at is null` 且 generation 相等的条目，否则返回既有 typed skip；**不回落**其它 live 条目。
  - `ResolveRegistryEntry` 仅补注释（明确它服务非枚举 target）。
- 未改：`ResolveRegistryEntry` 实现、`SourceAccessRegistry`、`SourceReadCoordinator`、`SourceWatcher`、planner/pre-pass/`TryMap`、`HostRuntime`/`RunSourceRange`、状态枚举、错误码、任何契约/Core/schema/依赖。

## 5. 已知 limitation（本卡，必须保留）

- **Run 面未含（卡 S-4）**：`HostRuntime.RunSourceRange.Resolve`（`HostRuntime.cs:1785` 一带）仍使用按路径 `ResolveRegistryEntry`；本卡**不改**、**未测** Run 预授权在「同路径 revoked 旧条目」下的行为。若需修复另卡（如 `L-S4-B-2-RUN-RANGE-RESOLVE`）。
- **B2 `roots_available`**：字段已冻结，实现延后（无消费者）。
- **folder（L-S4-2）**、**L-S4-1**、**L-R1**、多根 first-root 启发式：未修/保留。
- **backoff 口径**：本卡只承诺「下一个未被既有 backoff 抑制的 tick」；同会话此前已 error 的 scheduler 可能因既有 backoff 延迟恢复（gated 证据使用新 scheduler 的首次 tick）。
- **revoked 行累积**：B1 既有行为（旧行永久保留），本卡只读、不删除/不改写。
- 非枚举 target 的 `ResolveRegistryEntry` 语义不变（C-17 §5.3 零改动）。

## 6. 真实性声明

1. **实跑**：§2 所有 PASS 数字均来自本 EV 记录命令的现场执行（日志在 `logs/`）；未跑项均在本节 §5/本条列明。
2. **NOT_RUN**：Run 面（`RunSourceRange`）相关任何测试/IPC；folder/B2/L-S4-1/L-R1；真实用户数据/回收站/AppData；`git push`；linked worktree；契约 byte-level 复核（本卡零契约改动，pins/blob 比对即为证明）。
3. **判别力**：§3 的 6 个破坏点均实际造成对应用例非 0 退出，且逐例原字节复原后复绿；不是「重跑到绿」。
4. **未夸大**：不得把本卡读成「Run 面恢复」「自动恢复/自愈」「撤销后自动放行」「自动重新授权」；只有 B1 显式动作之后的**枚举 target 扫描执行**恢复。
5. **证据归因**：全部数字属于 `delivery_head=bcc88e4a2` 的代码/测试树；随后同批 docs/evidence 提交不含实现字节。
6. **外部依赖**：gated 真 IPC 使用真实 Python Core（`C:/Python314/python.exe`）与仓库外 fixture 根 `G:/CODEX/New Manga.workspace/FEA-11/fixtures/scan-*/`；fixture 路径/哈希记录在 `logs/ipc-fixture.txt`。

## 7. 复现（repo root）

```powershell
# 构建 + 新单测 + 回归
dotnet build apps/desktop-avalonia/NewManga.sln -c Release
dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~SourceScanExecutionRecovery"
dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~SourceRegistry|FullyQualifiedName~SourceReattest|FullyQualifiedName~SourceScanSchedulerTests"

# gated 真 IPC（真实 Python Core）
$env:NEWMANGA_FEA11_IPC='1'
dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~Fea11ScanIpc"

# 全量
C:/Python314/python.exe -m pytest tests -q
cd apps/desktop-avalonia; dotnet test NewManga.sln -c Release; cd ../..

# 治理 / scope / 判别性
pwsh -NoProfile -File tools/governance/verify_pins.ps1
pwsh -NoProfile -File tools/governance/check.ps1
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1.md
C:/Python314/python.exe tools/generate_api_inventory.py --check
C:/Python314/python.exe verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/tools/scope_validation.py
C:/Python314/python.exe verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/tools/discrimination.py
# 全量跑后恢复 tracked 测试副作用
git checkout -- verification/FEA-09
```
