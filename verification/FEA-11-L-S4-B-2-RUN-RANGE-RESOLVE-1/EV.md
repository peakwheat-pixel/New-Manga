# FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1（L-S4-B-2）：Run 源范围解析恢复 — 证据（EV）

> 本 EV 只陈述**实跑**事实；未跑项目逐项标注。措辞红线（AC-RUN-8）：只承诺
> **「B1 显式重授权 → 既有 refresh/reattest → 枚举 → Run 预授权/冷源分类」**这一段的恢复。**不**承诺
> 「Run 全面恢复」、**不**承诺自动恢复/自愈/自动重新授权/撤销后自动放行，**不**承诺扫描面（已由
> L-S4-B-1 交付）、B2、folder（L-S4-2）、L-S4-1、L-R1、2C。managed-only Run 不依赖 source 授权，不在承诺面内。

- Task：`doc/tasks/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1.md`（Owner=`l-s4b1-impl`，Lead=`lead`；卡面 `status` 由 Lead 维护，本 EV 不改）
- 契约：**零契约变更**（0 UNFREEZE / 18 pins 不变；C-16 v1.5 `a7f57ebd…`、C-17 v1.1 blob 逐 blob 相同）
- 卡 `base_commit=2ef3f1024`；**实现起点 `e78c144bb`**（Lead 释放提交，`main` clean；其后 Lead 另有 docs-only `7be65026e` owner 字段对齐，先于本卡实现提交）
- **delivery_head=`fad1ec776`**；交付 commit 链：
  - `f6b5a761a` feat：`HostRuntime.cs` 的 `RunSourceRange.Resolve` 枚举分支复用 `SelectEnumeratedEntry`（+ XML 注释）
  - `fad1ec776` test：新增 `SourceRunRangeResolutionTests.cs`（9 例）+ gated `Fea11RunGrantIpcTests` 新闭环
  - （随后同批 docs/evidence 提交记录本 EV/Handoff/卡面；不属于实现字节）
- 权限依据：卡面 + 权威 scope review `doc/reviews/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1-scope-r1.md`（READY-TO-FREEZE；推荐 Host-only，复用 L-S4-B-1 `SelectEnumeratedEntry`；0 UNFREEZE / 18 pins）+ Lead 派发指令（R-1…R-7）
- 环境：Windows 11 / PowerShell 7 / CPython 3.14.6 / .NET SDK 10.0.401（测试目标 net9.0）；零新依赖、零 schema/迁移、零 Core/Python 改动；`SourceScanScheduler.cs` 零字节（直接复用 public static helper）

## 1. AC 达成（AC-RUN-1…8 全 MET）

| AC | 结果 | 关键证据（实跑） |
|---|---|---|
| **AC-RUN-1 枚举 target 的 Run 范围恢复（主 AC）** | MET | `RunSourceRange.Resolve` 的 `target.IsEnumerated` 分支改用 `SelectEnumeratedEntry(registryEntries, target, out _)` 选 target 自身 live 条目；单测 `Resolve_EnumeratedTarget_UsesItsOwnLiveEntry_WhenARevokedSiblingSharesThePath`：同一 entries 快照下 **path-only resolver = null**（before）而 Run 范围返回 1 个 scope（RegistryId/Generation=live、path/kind/version/容器成员一致、`Unresolved=0`）；gated 真 IPC：before `path_resolver=null`→ after `targets=1/unresolved=0/registry_id=live/bound_pages=1/minted=1/resolve p1 OK`（`logs/ipc-closed-loop.json`） |
| **AC-RUN-2 fail-closed 矩阵与不回落 sibling** | MET | target 自身 registry 缺失/撤销/代次漂移 → `Unresolved`（单测 2 例 + gated revoked-target 实测 `unresolved=1/targets=0`）；同路径 live sibling 不采用（`NeverFallsBackToALiveSibling`）；未解析时零 grant、零 `AuthorizeSourceReadForRun` 帧（authorizer 单测 `authorizeCalls=0` + gated before `authorize_frames=0`） |
| **AC-RUN-3 非枚举 target 语义零变化** | MET | `ResolveRegistryEntry` 字节未改（scope 禁止面零 diff；`SourceScanScheduler.cs` 零改动）；非枚举 Run target 在同状态（同路径 revoked+live）下仍 `Unresolved`（单测 `Resolve_NonEnumeratedTarget_KeepsThePathOnlyResolver`，并验证既有 exact-match 仍解析 live 条目）；既有 `RunSourceRangePrefersTheRunProjectAndSkipsUnresolvedSources`、`RunSourceRangeUsesTheCachedCoreVersionAndReportsColdSources` 原样通过（`SourceRegistryTests` 32/0/0） |
| **AC-RUN-4 冷源 on-demand 分类恢复** | MET | 枚举 live + 空 `SourceIdentityCache` → `ColdSources=1`/`Unresolved=0`（单测 + gated `cold_before_scan`）；authorizer 恰 1 次 bounded on-demand scan 后第二次 Resolve 进 `Targets` 并 mint，第二次 slice 不再扫描（`Authorizer_EnumeratedColdSource_PerformsOneOnDemandScan_ThenMints`）；预算/超时/失败仍 skip（既有 `MaxOnDemandScansPerSlice=8`、30s 用例原样通过） |
| **AC-RUN-5 无自动授权/无 identity 重建/不写 registry/不抛** | MET | 解析路径只读 registry 快照；不调用 `Register`/`Revoke`/`Reset`；单测用真实 `SourceAccessRegistry`（旧 revoked + 新 live 同路径）断言解析前后 `DescribeRegistryEntries`（不含既有 `last_used_at`）全等、旧 revoked 行保留、条目数不变；异常安全：`try/catch` 只把失败降级为 `Unresolved`（`Resolve_DuplicateRegistryId_IsUnresolved_NotThrown` 判别）；gated 亦断言 `host_registry_unchanged=true` |
| **AC-RUN-6 gated 真实 IPC 闭环（before/after）** | MET | 真实 Python Core + 真实 `SourceAccessRegistry` + 真实 zip/referenced 页：B1 形（Register→`AlignRegistryAsync`→Revoke→Register 同 root→`AlignRegistryAsync` 到 live，测试侧对齐=既有 reattest 的结果，本卡不再发 reattest）。before：`path_resolver=null`、`resolve_page_resource` = `SOURCE_ACCESS_DENIED`、`authorize_frames=0`；after：`targets=1/unresolved=0`、live `(registry_id,generation)`、`bound_pages=1`、`minted=1`、`resolve p1` OK、`reattest_frames=0`、wire/stderr 无 fixture 路径（`logs/ipc-closed-loop.json/.txt`） |
| **AC-RUN-7 零契约/零漂移** | MET | C16 工作树 sha 命中 `a7f57ebd…`；C-16/C-17 git blob 与实现起点逐 blob 相同；`PROTOCOL_MINOR=3`；pins 18/18；`src/**`/`tests/**` 零 diff（无 Core/Python/schema/依赖变更）；`NewManga.CoreClient`/`NewManga.App` 零 diff（无新命令/能力/错误码）；API inventory 61 不变（EXIT=0） |
| **AC-RUN-8 门禁/不夸大/触发口径** | MET | check（默认 + `-TaskPath`）PASS(3 warnings)；全量 pytest **3360/10**（≥ 起点基线 3360/10）、全量 .NET **1661/0/95**（起点 1652/0/94；+9 本卡新单测，+1 新 gated fact 默认 skip）；跑后 `verification/FEA-09` CLEAN；本 EV/Handoff/卡面无「自动恢复/自愈/自动重新授权/撤销后放行/Run 全面恢复/扫描面恢复/B2/folder/2C」承诺，恢复口径固定为「B1 显式动作 → 既有 refresh/reattest → 枚举 → Run 预授权/冷源分类」 |

### before / after（同一条 gated 真实 IPC，生产字节判别）

| 状态 | 事实（同一 fixture/同一目标） |
|---|---|
| **before**（本卡修复前的 resolver 语义） | path-only `ResolveRegistryEntry` 对同路径 revoked 旧条目 fail-closed → null；`RunSourceRange` 计 `Unresolved`；`resolve_page_resource` 无 grant → `SOURCE_ACCESS_DENIED`；`AuthorizeSourceReadForRun` 0 帧 |
| **after**（`fad1ec776`） | 枚举 target 用自身 live `(registry_id, generation)` → `Targets=1`/`Unresolved=0` → `AuthorizeRunAsync` `bound_pages=1`/`minted=1` → `resolve p1` OK；`host_registry_unchanged=true`、`reattest_frames=0`、wire 无路径 |
| 判别性破坏 | 把枚举分支改回 path resolver → 单测 4 红 + **gated 同测试 RED**；恢复后复绿（`logs/discrimination.log`） |

## 2. 定向 / gated / 全量（实跑）

| 场景 | 命令 | 结果 | 日志 |
|---|---|---|---|
| 构建 | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` | **PASS（0 warning / 0 error）** | `logs/build.log` |
| Host 单测（新） | `dotnet test …/NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~SourceRunRangeResolution"` | **9 passed / 0 failed / 0 skipped** | `logs/host-unit.log` |
| 回归（Run 范围既有） | 同上 `--filter "FullyQualifiedName~SourceRegistryTests"` | **32 passed / 0 failed / 0 skipped**（含既有 Run range/authorizer 用例） | `logs/regression.log` |
| gated 真 IPC | `NEWMANGA_FEA11_IPC=1 … --filter "FullyQualifiedName~Fea11RunGrantIpc"` | **6 passed / 0 failed / 0 skipped**（含新 B1 live-entry→Run 范围→bind→resolve 闭环） | `logs/host-ipc.log`、`logs/ipc-closed-loop.json/.txt`、`logs/ipc-fixture.txt` |
| 定向 pytest（回归） | `C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | **89 passed / 0 failed**（零 Python 改动；与前卡同选择集） | `logs/regression-74.log` |
| 全量 Python | `C:/Python314/python.exe -m pytest tests -q` | **3360 passed / 10 skipped / 262.86s**（起点基线 3360/10，无降级） | `logs/full-pytest.log` |
| 全量 .NET | `dotnet test NewManga.sln -c Release`（cwd `apps/desktop-avalonia`） | **1661 passed / 0 failed / 95 skipped**（起点 1652/0/94；+9 新单测、+1 新 gated skip） | `logs/full-dotnet.log` |
| 治理 pin | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PIN AUDIT: PASS (all 18)**，EXIT=0 | `logs/gates.log` |
| 治理 check | `check.ps1`（默认）与 `-TaskPath doc/tasks/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1.md` | **PASS (3 warnings) ×2 / EXIT=0** | `logs/gates.log` |
| API inventory | `C:/Python314/python.exe tools/generate_api_inventory.py --check` | **EXIT=0**（61 不变） | `logs/gates.log` |
| scope | `C:/Python314/python.exe verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/tools/scope_validation.py` | **PASS**（delivery 21 文件全 ALLOWED；禁止面零 diff；`PROTOCOL_MINOR=3`；C16/C17 blob 零漂移；卡 `status` 未改） | `scope-validation.log`、`changed-files.txt` |
| 判别性 | `C:/Python314/python.exe verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/tools/discrimination.py` | **5/5 RED_AS_EXPECTED + 逐例 sha256 复原 + 复绿** | `logs/discrimination.log` |

- **跑后恢复**：全量 .NET 重写 tracked `verification/FEA-09/logs/wire-redacted.ndjson` → 已 `git checkout -- verification/FEA-09`（`git status -- verification/FEA-09` 为空）。
- **并发披露**：共享 `main` 同期 Lead 提交 docs-only `7be65026e`（卡 owner 对齐）；本卡提交全部显式 pathspec；`git diff e78c144bb..HEAD -- src tests` 为空。
- **证据容器**：`scope-validation.log` / `changed-files.txt` 的 delivery 列表（21）在 `RESOURCE-MANIFEST.json` 生成**之前**采集，故不含 manifest 自身（manifest 是容器、不自我哈希）。

## 3. 判别性（5/5，`logs/discrimination.log`）

| # | 破坏点 | 目标用例 | 结果 |
|---|---|---|---|
| B1 | 枚举分支改回按路径 `ResolveRegistryEntry` | `SourceRunRangeResolution`（4 例红） | **RED**（`Unresolved=1`/`Targets` 空） |
| B1b | 同一破坏点，在 **gated 真 IPC** 闭环上 | `Fea11RunGrantIpcTests.ReauthorizedLiveEntry_RunRangeResolvesAndBindsOverRealIpc` | **RED** |
| B2 | 改写成接受任意 live 条目（撤销 target 被同路径 sibling 自动放行） | `Resolve_EnumeratedTarget_NeverFallsBackToALiveSibling…` | **RED** |
| B3 | 删掉解析异常兜底（Host 侧失败抛给 best-effort authorizer） | `Resolve_DuplicateRegistryId_IsUnresolved_NotThrown` | **RED** |
| B4 | own-entry 逻辑被错误应用到所有 target（非枚举授权面扩大） | `Resolve_NonEnumeratedTarget_KeepsThePathOnlyResolver` | **RED** |

驱动逐例：写入破坏 → 目标测试必须非 0 退出 → 原字节回写（sha256 = `c91deee6…`，MATCH=True）→ 复跑必须绿。最终树 `final_sha256` 与原始一致。

## 4. 实现摘要（只读变更，零契约）

- `HostRuntime.cs` `RunSourceRange.Resolve`（唯一生产改动）：
  - `target.IsEnumerated` → `HostSourceScanExecutor.SelectEnumeratedEntry(registryEntries, target, out _)`；`try/catch`（排除 `OutOfMemoryException`）把解析失败降级为 `null` → `unresolved++`（AC-RUN-5「不抛」）。
  - `!target.IsEnumerated` → `HostSourceScanExecutor.ResolveRegistryEntry(registryEntries, target.Path)`（**字节未改**，AC-RUN-3）。
  - 顺序保持「先 entry 后 identity」：live 但 Core version 冷 → 既有 `ColdSources` 分类与 bounded on-demand scan（AC-RUN-4）。
  - `RunSourceRange` XML 注释补充「授权来源随 target 形状」的口径（AC-RUN-1/2/3）。
- 未改：`SourceScanScheduler.cs` / `ResolveRegistryEntry` / `SourceAccessRegistry` / `SourceReadCoordinator` / `RunSourceAuthorizer` / `RunCommandPolicy` / App / 契约 / Core / schema / 依赖。

## 5. 已知 limitation（本卡，必须保留）

- **不修扫描面**（L-S4-B-1 已 done）与 `ResolveRegistryEntry` 非枚举语义；不实现 B2 `roots_available`、folder（L-S4-2）、L-S4-1、L-R1、多根 first-root。
- **「Run 预授权/冷源分类恢复」≠「Run 全面恢复」**：managed-only Run 本就无需 source 授权；Host 侧 mint 仍可能因文件缺失/身份漂移 typed skip（best-effort，不阻断 dispatched Run 的 managed 页）。
- **Scheduler 未启动/枚举失败时 `known` 为空**：无 target 可选，本卡不产生 grant（既有配置行为）。
- gated 闭环的 Core `source_locations` 由测试侧 `AlignRegistryAsync` 对齐（等价于既有 L-S4-B reattest 的结果）；本卡**不**发送 `ReattestSourceLocation`（`reattest_frames=0`），reattest 往返由 L-S4-B 证据覆盖。
- 2C 长 Run（>300s 失权）仍保留；L-R11/C-04b/SCAN-RH/UI P3 保留。

## 6. 真实性声明

1. **实跑**：§2 所有 PASS 数字均来自本 EV 记录命令的现场执行（日志在 `logs/`）；未跑项在 §5/本条列明。
2. **NOT_RUN**：2C 长 Run；folder/B2/L-S4-1/L-R1；真实用户数据/回收站/AppData；`git push`；linked worktree；契约 byte-level 复核（零契约改动，pins/blob 比对即为证明）；完整 Core reattest 往返（本卡不涉及，L-S4-B 证据覆盖）。
3. **判别力**：§3 的 5 个破坏点均实际造成对应用例非 0 退出，且逐例原字节复原后复绿；B4 的最终破坏点经修正后为**行为级 RED**（编译通过、断言失败）。
4. **未夸大**：不得把本卡读成「Run 全面恢复/自动恢复/自愈/撤销后放行/扫描面恢复」；恢复口径只有「B1 显式动作 → 既有 refresh/reattest → 枚举 → Run 预授权/冷源分类」。
5. **证据归因**：数字属于 `delivery_head=fad1ec776` 的代码/测试树；随后同批 docs/evidence 提交不含实现字节。
6. **外部依赖**：gated 真 IPC 使用真实 Python Core（`C:/Python314/python.exe`）与仓外 fixture 根 `G:/CODEX/New Manga.workspace/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/fixtures/ipc-*/`；fixture 路径/哈希见 `logs/ipc-fixture.txt`。

## 7. 复现（repo root）

```powershell
dotnet build apps/desktop-avalonia/NewManga.sln -c Release
dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~SourceRunRangeResolution"
dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~SourceRegistryTests"
$env:NEWMANGA_FEA11_IPC='1'
dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~Fea11RunGrantIpc"
C:/Python314/python.exe -m pytest tests -q
cd apps/desktop-avalonia; dotnet test NewManga.sln -c Release; cd ../..
pwsh -NoProfile -File tools/governance/verify_pins.ps1
pwsh -NoProfile -File tools/governance/check.ps1
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1.md
C:/Python314/python.exe tools/generate_api_inventory.py --check
C:/Python314/python.exe verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/tools/scope_validation.py
C:/Python314/python.exe verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/tools/discrimination.py
git checkout -- verification/FEA-09
```
