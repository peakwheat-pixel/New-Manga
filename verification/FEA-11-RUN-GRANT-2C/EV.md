# FEA-11-RUN-GRANT-2C：2C 长 Run 续期 — 证据（EV）

> 本 EV 只陈述**实跑**事实；未跑项目逐项标注。措辞红线（AC-2C-7/8）：本卡最多把 L-G1 从「无续期」
> **降级**为「有续期但仍有子限制」，**不得**写「L-G1 关闭 / 任意长 Run 可用 / Run 全面恢复 /
> 自动恢复 / 自愈 / 自动重新授权 / 撤销后放行」。续期只在 **B1/用户显式动作与既有 dispatch 之后**的
> 非终态 Run 上生效，且每轮都重走既有授权路径（`Registry.Authorize` + 物理 facts 复核），失败即停。

- Task：`doc/tasks/FEA-11-RUN-GRANT-2C.md`（Owner 由 Lead 指派；`status` 由 Lead 维护，本 EV 不改）
- 契约：**C-06 v1.3**（§2.2 mid-run 重复建立；pin `75f8e2b4…`）+ **C-16 v1.6**（§2.4 重复调用；pin
  `b8f46fb1…`）已由 PREREQ `FEA-11-RUN-GRANT-2C-PREREQ-1`（done，2 pins）冻结；本卡**零契约字节改动**
  （pins 18/18，C-06/C-16 工作树字节 == 冻结 pin）。
- 卡 `base_commit=fdd170039`；**实现起点 `c5f1b416f`**（派发时 HEAD `0475adc72`；其后 Lead 的
  `c5f1b416f` 为 PREREQ 冻结记录 docs-only 修正，`0475adc72..c5f1b416f` 实测仅 PREREQ 文档）
- **delivery_head=`7c95bb3c4`**（Review r1 返修后；初版交付 `e5e9c4c52`）；交付 commit 链：
  - `c40489b5d` feat：`RunGrantRenewal.cs`（新）+ `HostRuntime` 接线 + `HostOptions` + `SourceReadCoordinator`（仅计数）+ `HostCommandDispatcher`（result-carrying 预授权 + post-dispatch 钩子）
  - `e5e9c4c52` test：`RunGrantRenewalTests.cs`（13 例）+ gated `Fea11RunGrantIpcTests` 新增一条 + `tests/fea11/test_source_run_grant.py` 新增 3 例（fake clock）
  - `7c95bb3c4` fix：**Review r1 返修**——Host 接线判别测试（HostRuntime seam + 3 用例）+ 轮前预算约束（budget 传入 cold-fill）+ P3 处置
  - （随后同批 docs/evidence 提交记录本 EV/Handoff/卡面；不属于实现字节）
- 权限依据：卡面（`status: ready`；In/Out；AC-2C-1…8）+ 权威 scope review
  `doc/reviews/2C-LONG-RUN-RENEWAL-scope-r1.md`（READY-WITH-UNFREEZE；方案 a）+ ZCode 裁决（APPROVE
  2 pins / 方案 a）+ PREREQ closeout（C-06 v1.3 + C-16 v1.6 重冻，pins 18/18）
- 环境：Windows 11 / PowerShell 7 / CPython 3.14.6 / .NET SDK 10.0.401（测试目标 net9.0）；零新依赖、零
  schema/迁移、**零 Core/Python 生产代码改动**（唯一的 Python 改动是允许的 in-process 测试文件）

## 1. AC 达成（AC-2C-1…8 全 MET）

| AC | 结果 | 关键证据（实跑） |
|---|---|---|
| **AC-2C-1 续期主 AC** | MET | in-process fake clock（真实装配）：同一 Run 的引用页在 300s 窗口后**读**（`ProviderInputError`）与**提交**（`SourceImportError SOURCE_ACCESS_DENIED`）分别 typed 失败且零业务写（`tests/fea11/test_source_run_grant.py::test_run_read_and_commit_fail_after_the_window_with_zero_business_writes`）；**续期**（新 grant + 同一冻结 `{command,scope}` 重新授权）后同一 Run 的读与提交恢复（`test_renewed_grant_keeps_the_same_run_readable_past_the_window`）。Host 侧：`RunGrantRenewalTests.Renewal_RebindsAfterTheWindow_AndTheRunKeepsReading`（每轮新 grant、同一 slice、计数递增）；gated 真 IPC：`renewal-ipc.json`（同 scope 两轮、2 帧 `RegisterSourceReadGrant`（run 面增量）、2 帧 `AuthorizeSourceReadForRun`、`bound_pages=1`、页仍可读）。**Host 接线（Review r1 P1-01）**：`HostWiring_DispatchThenProductionTick_RenewsTheSameFrozenScope` 在生产 HostRuntime 上走真实 pre-auth→dispatch 通知→Track→生产 Tick（renew=真实 `RenewRunGrantsAsync`）；Probe-C 复现后该用例 RED（见 §3.1）。判别性 D1/D2/D7/D8 → RED |
| **AC-2C-2 不延长/不扩 scope/不改 command** | MET | 每轮新 grant id（gated `new_grant_id=true`；单元测试每轮调用冻结 slice）；旧 grant `expires_at` 不变且永不延长（Python：续期后 `_checked(G1)` 仍 `SOURCE_GRANT_EXPIRED`；gated 2 个不同 grant id）；command/scope 逐字节相同（gated 两帧 payload 断言 + 单元 `Renewal_NeverWidensTheFrozenCommandOrScope`，第二次 Track 的加宽尝试被忽略）。判别性 D2 → RED |
| **AC-2C-3 撤销/漂移即停** | MET | 续期每轮走同一 `AuthorizeSliceAsync`（`RunSourceRange.Resolve` → 逐源 `IssueLockedAsync` → `Registry.Authorize` 校验 live/generation/根包含/volume-file identity + 物理 facts 重算）→ 撤销/漂移/根替换→ typed skip（mint 全部失败）→ `RENEWAL_NO_TARGETS` 停止；单元 `Renewal_StopsOnRevokedRegistry_WithoutAnyRetry`（typed 停止 + 不重试 + `IsTracking=false`）、`Renewal_ProbeFailure_IsAFailClosedStop_NotRetry`。判别性 D3 → RED |
| **AC-2C-4 失败不放行/不自动重试成自动恢复** | MET | 任一 typed/异常/全 skip → 停止续期、不重试、不 reattest、不新建 Run（gated `reattest_frames=0`；单元 cases 断言 `renewCalls==1`、后续 `StoppedNotTracked`）；续期失败只停止续期，Run 仍由 Core fail-closed（本卡零 Core 改动）。 |
| **AC-2C-5 预算/间隔** | MET | `interval=240s`、`maxRenewals=12` 默认；选项归一化拒绝非法值（<240 或 >249、RoundBudget=50）；`interval + round budget = 290 < 300`（单元断言）；round budget 在进入单轮前传入 mint 路径（每个 on-demand 冷扫描 timeout=min(30s, 剩余预算)，耗尽即停并留余 cold；`AuthorizeSliceAsync_BoundsOnDemandScansByTheRoundBudget` 判别实际用时 <1.5s 而非 30s）；单轮超预算 → **`SkippedBudget` typed skip + 计数**（保留跟踪、下一 interval 再试；**真实 mint 照计**，`Renewal_RoundOverBudget_SkipsTheRoundAndKeepsTracking` / `Renewal_BudgetSkip_DoesNotConsumeTheGateOrStopTheRun`）；轮次上限按**尝试次数**计（`Renewal_DoesNotExceedTheRoundsCap`）；每轮一次 `AuthorizeRunAsync`（coordinator `_gate` 串行）；成本与 ledger 计数：`SourceReadCoordinator.LedgerStatus()` 可观测（既有 `PruneExpired` 维持 256 上限，未改）；终态/关停停止（`Renewal_StopsAtTerminalRun_AndOnShutdown`）。判别性 D4/D5/D6 → RED |
| **AC-2C-6 接线点/无 App 改动** | MET | `HostCommandDispatcher` 新增可选 `runAuthorizeWithResult` + `runDispatched`（Host 内部零 wire；旧 `runAuthorize` 保留）；`HostRuntime` 在 dispatcher post-dispatch 与 `AcceptRun` 两个入口启动续期（同一冻结 slice）；`RunGrantRenewalStatus` 可观测；App/UI **零 diff**；`+300`/TTL/`MaxRunGrants`/`MaxTrackedPayloads` 既有值不变（`SourceReadCoordinator` 仅新增 `LedgerStatus()` 计数方法）；`src/**` 零 diff。 |
| **AC-2C-7 L-G1 只降级不关闭 + 不夸大** | MET | 本 EV/Handoff/卡面措辞：L-G1 =「有续期，但仍有子限制」；保留「单步 >300s / 续期失败 / L-G2 加密源 / L-G9 Core 重启 / L-R1 残余 / L-G16 >4096 成员」；未写「任意长 Run / L-G1 关闭 / Run 全面恢复 / 自动恢复 / 自愈 / 自动重新授权 / 撤销后放行」。 |
| **AC-2C-8 门禁** | MET | 构建 **PASS 0 warning/0 error**；pins **18/18**（C06 v1.3 `75f8e2b4…`、C16 v1.6 `b8f46fb1…`）；check（默认+`-TaskPath`）**PASS(3 warnings)**；API inventory **EXIT=0**；scope **PASS**（delivery ⊆ allowed_paths、`src/**` 零 diff、禁止面零 diff、卡 status 未改）；全量 pytest **3363/10**（起点 3360/10，+3 本卡 Python 用例）、全量 .NET **1680/0/96**（起点 1661/0/95 → +19 单测、+1 新 gated skip；Lead 给定 1660/0/95 亦不降）；判断性 **9/9 RED_AS_EXPECTED**；跑后 `verification/FEA-09` CLEAN |

### before / after（时间维：in-process fake clock；同 scope 二轮：真实 IPC）

| 状态 | 事实 |
|---|---|
| **before**（无续期，窗口后） | 引用页读 → `ProviderInputError`（`SOURCE_ACCESS_DENIED`）；Run 提交 guard → `SourceImportError SOURCE_ACCESS_DENIED`（`DB_FAILED` 路径）；零业务写；旧 grant `SOURCE_GRANT_EXPIRED`（不延长） |
| **after（一次续期轮）** | 新 grant id + 同一冻结 `{command, scope}` 重新 `AuthorizeSourceReadForRun` → `bound_pages=1`；同一 Run 的读 + 提交恢复；旧 grant 仍 `SOURCE_GRANT_EXPIRED`（未被延长）；`find_bound_for_source` 选中续期后的新 grant |
| 不同 scope/command 的「续期」 | typed 拒绝（`SOURCE_ACCESS_DENIED` / `INVALID_REQUEST`），零映射写入；页面保持不可读直到使用冻结 pair（AC-2C-3） |
| gated 真实 IPC | 同冻结 scope 两轮：2 帧 `RegisterSourceReadGrant`（run 面增量）+ 2 帧 `AuthorizeSourceReadForRun`，`new_grant_id=true`、`bound_pages=1`、`resolve p1` OK、wire 无路径、`reattest_frames=0`、Host registry 结构不变（`logs/renewal-ipc.json`） |

## 2. 定向 / gated / 全量（实跑）

| 场景 | 命令 | 结果 | 日志 |
|---|---|---|---|
| 构建 | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` | **PASS（0 warning / 0 error）** | `logs/build.log` |
| Host 续期单测 | `--filter "FullyQualifiedName~RunGrantRenewal"` | **19 passed / 0 failed / 0 skipped**（13 初版 + 6 返修：2 Host 接线 + 2 预算 + 2 authorizer 预算/无预算） | `logs/host-unit.log` |
| 回归（Run 授权既有） | `--filter "SourceRegistryTests\|Fea11RunGrantIpc"`（无 gated env） | **32 passed / 0 failed / 7 skipped**（gated 默认 skip；既有 Run 范围/冷源/预算用例原样通过） | `logs/regression.log` |
| gated 真 IPC | `NEWMANGA_FEA11_IPC=1 … --filter Fea11RunGrantIpc` | **7 passed / 0 failed / 0 skipped**（含新「同 scope 二轮 = 续期轮」） | `logs/host-ipc.log`、`logs/renewal-ipc.json/.txt`、`logs/ipc-fixture.txt` |
| 定向 pytest | `pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | **92 passed**（基线 89 + 本卡 3 例） | `logs/regression-74.log` |
| 全量 Python | `pytest tests -q` | **3363 passed / 10 skipped / 286.76s**（起点 3360/10，+3 本卡） | `logs/full-pytest.log` |
| 全量 .NET | `dotnet test NewManga.sln -c Release`（cwd `apps/desktop-avalonia`） | **1680/0/96**（起点 1661/0/95 → +19 单测、+1 新 gated skip；Lead 给定 1660/0/95 亦不降） | `logs/full-dotnet.log` |
| 治理 pin | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PIN AUDIT: PASS (all 18)**（C06 v1.3 `75f8e2b4…`、C16 v1.6 `b8f46fb1…`），EXIT=0 | `logs/gates.log` |
| 治理 check | `check.ps1`（默认）与 `-TaskPath doc/tasks/FEA-11-RUN-GRANT-2C.md` | **PASS (3 warnings) ×2 / EXIT=0** | `logs/gates.log` |
| API inventory | `C:/Python314/python.exe tools/generate_api_inventory.py --check` | **EXIT=0**（61 不变） | `logs/gates.log` |
| scope | `python verification/FEA-11-RUN-GRANT-2C/tools/scope_validation.py` | **PASS**（delivery 32 文件全 ALLOWED；`src/**` 与禁止面零 diff；C06/C16 pin 命中、C15/C17 blob 零漂移；`PROTOCOL_MINOR=3`；卡 status 未改） | `scope-validation.log`、`changed-files.txt` |
| 判别性 | `python verification/FEA-11-RUN-GRANT-2C/tools/discrimination.py` | **7/7 RED_AS_EXPECTED + 逐例 sha256 复原 + 复绿** | `logs/discrimination.log` |

- **跑后恢复**：全量 .NET 后 `git checkout -- verification/FEA-09`（实跑时 tracked 的 `wire-redacted.ndjson` 会被重写；已恢复）。
- **证据容器**：`scope-validation.log` / `changed-files.txt` 的 delivery 列表（32）在 `RESOURCE-MANIFEST.json` 生成**之前**采集，故不含 manifest 自身（manifest 是容器、不自我哈希）。
- **并发披露**：共享 `main` 同期 Lead 提交 `c5f1b416f`（PREREQ 冻结记录 docs-only 修正；`0475adc72..c5f1b416f` 仅 PREREQ 文档），已在 scope 中作为 CONCURRENT_NON_DELIVERY 记录；本卡提交全部显式 pathspec。

## 3. 判别性（9/9，`logs/discrimination.log`）

| # | 破坏点 | 目标用例 | 结果 |
|---|---|---|---|
| D1 | 续期从不启动（`ObserveDispatch` 恒 false） | `RunGrantRenewalTests`（类级） | **RED** |
| D2 | 续期改用更宽 scope（非 Run 冻结 slice） | `RunGrantRenewalTests`（类级） | **RED** |
| D3 | typed 拒绝被当作续期成功（撤销后继续） | `Renewal_StopsOnRevokedRegistry_WithoutAnyRetry` | **RED** |
| D4 | 删除每 Run 轮次上限 | `Renewal_DoesNotExceedTheRoundsCap` | **RED** |
| D5 | 删除单轮预算的事后守护（超预算不再 skip/计数） | `Renewal_RoundOverBudget_SkipsTheRoundAndKeepsTracking` | **RED** |
| D6 | 终态 Run 仍被续期 | `Renewal_StopsAtTerminalRun_AndOnShutdown` | **RED** |
| D7 | 授权结果伪造成 0/0「成功」（发了就算成功） | `AuthorizeSliceAsync_ReturnsTheRealMintAndBindCounts` | **RED** |
| **D8** | **Review r1 Probe-C**：Host 安装行 `StartRunGrantRenewal()` 被移除（续期不接线） | `HostWiring_DispatchThenProductionTick_RenewsTheSameFrozenScope` | **RED**（修复前同 Probe-C 全绿；见 §3.1） |
| **D9** | **Review r1 P2-01**：round budget 不再传入 on-demand 冷填充 | `AuthorizeSliceAsync_BoundsOnDemandScansByTheRoundBudget` | **RED** |

驱动逐例：写入破坏 → 目标测试必须非 0 退出 → 原字节回写（sha256 MATCH=True）→ 复跑必须绿。最终树与原始 sha256 一致。

### 3.1 Review r1 返修（P1-01 / P2-01 / P3）

**P1-01（判别证据，最关键）**：初版 gated「续期轮」是测试**直接连调** `coordinator.AuthorizeRunAsync` 两次，不经过 Host 接线；Reviewer 的 Probe-C（`_runGrantRenewal = null`）下全量 Host 277/0/65 + gated 7/0/0 全绿 → 「删续期 → RED」未以生产接线路径成立。返修：

- `HostRuntime` 抽出**唯一安装行** `StartRunGrantRenewal()` 并与生产 start 路径共用；新增 Host 接线测试 seam（`StartRunGrantRenewalForTests` / `AuthorizeRunCommandForTestsAsync` / `NotifyRunDispatchedForTestsAsync` / `NotifyAcceptedRunForTestsAsync` / `TickRunGrantRenewalForTestsAsync`）+ `HostOptions.RunGrantRenewalLivenessProbe` 测试 seam。
- 新用例 `HostWiring_DispatchThenProductionTick_RenewsTheSameFrozenScope`：在生产 `HostRuntime` 实例上走「真实 pre-auth summary → 真实 dispatch 通知（`RunDispatchedAsync`）→ `Track` → 真实 `TickAsync`（renew 委托 = 生产 `RenewRunGrantsAsync`，同一冻结 scope）」，断言 `authorize` 调 2 次（dispatch+续期）、`Renewals=1`；`HostWiring_ManagedOnlyRun_StartsNoRenewal`（bound_pages=0 不启动）；`HostWiring_DisabledOption_InstallsNoLoopAndNeverTracks`（不接线方向）。
- **Probe-C 复现（`logs/probe-c.log`）**：把安装行内容删除（与 Reviewer Probe-C 等价）→ 全量 Host **281 passed / 2 failed / 65 skipped**（恰为新接线用例 RED；gated 仍 7/0/0，因 gated 不经过 Host 循环）；恢复后源码 sha256 逐字节复原（MATCH=True）并全量复绿。修复前同一 Probe-C 为 **277/0/65 全绿**（Reviewer 观察），修复后为 **2 RED** —— 即 AC-2C-1「删续期 → RED」现在以生产接线路径成立。判别性 D8 固化该破坏点。

**P2-01（预算执行）**：round budget 从「事后检查」改为**进入单轮前**约束——`TickAsync` 把 `RoundBudget` 传给生产 renew 委托；`HostRuntime.RenewRunGrantsAsync` → `AuthorizeSliceAsync(..., roundBudget)` → `ResolveWithColdCacheAsync(..., roundBudget)`：每个 on-demand 冷扫描 timeout = `min(30s, 剩余预算)`，预算耗尽即停并保留剩余 cold；单轮超预算 → `SkippedBudget` typed skip + 计数（保留跟踪、下一 interval 再试；真实 mint 照计），事后守护保留为 belt-and-braces。判别性 D9；单元 `AuthorizeSliceAsync_BoundsOnDemandScansByTheRoundBudget` 断言实际用时 <1.5s（而非 30s×8）。

**P3 处置**：①预算停止路径记录 `minted/bound_pages/code` 且把真实 mint 计入 `Renewals`（`Renewal_RoundOverBudget_SkipsTheRoundAndKeepsTracking` 断言）；②`SourceReadCoordinator.LedgerStatus()` 接入 `RenewRunGrantsAsync` 成功日志（真实 status，不再是死代码）；`RunGrantRenewalStatus` 增 `Attempts/BudgetSkips`；③EV/Handoff 的 TBD 与证据计数填实；④manifest 排除 `__pycache__/*.pyc`，并在**可到达**的 docs commit 上重新生成（不再出现 amend 孤儿 head）；⑤FROZEN-C16 §2 第 8 行由 Lead 单独修复，本卡未动。

## 4. 实现摘要（Host-only；零契约/零 Core/零 wire/零 App）

- **`Sources/RunGrantRenewal.cs`（新）**：`RunGrantRenewalOptions`（enabled/interval=240/maxRenewals=12 +
  `RoundBudgetSeconds=50`；`interval + round < 300`；非法值回退默认）、`RunGrantRenewal`（每 Run 一个 loop；
  `Track`/`ObserveDispatch`/`Untrack`/`TickAsync`/`Status`/`DisposeAsync`；`TimeProvider` 注入；
  `RunLiveness {Alive, Terminal, Unknown}`；typed 停止 kind 全集；counts-only 日志与状态；
  终态词表 = C-08 的 completed/completed_with_failures/failed/cancelled/interrupted）。
- **`HostRuntime.cs`**：`RunGrantRenewalStatus` 可观测；dispatcher `runAuthorizeWithResult`（返回冻结
  `{command, scope}` + 真实 counts 的 Host-owned summary）与 `runDispatched`（post-dispatch 启动续期）；
  `AcceptRun` 同一 slice 启动；`RenewRunGrantsAsync`（同一 `AuthorizeSliceAsync` 路径；`null`/全 skip →
  停止）；`ProbeRunLivenessAsync`（既有 `GetRunSnapshot`；终态/缺失/未知 → 停止）；`StopRunGrantRenewalAsync`
  在 dispose/停机先停；`AuthorizeSliceAsync` 返回 `RunAuthorizationResult?`（不得「发了就算成功」）。
- **`HostOptions.cs`**：`RunGrantRenewalEnabled`（默认 true）、`RunGrantRenewalIntervalSeconds`（240）、
  `RunGrantRenewalMaxRenewals`（12）、`RunGrantRenewalTimeProvider`。
- **`Sources/SourceReadCoordinator.cs`**：仅新增 `LedgerStatus()`/`RunGrantLedgerStatus` 计数；
  `+300`、TTL、`MaxRunGrants`、`MaxTrackedPayloads` 既有值**零改动**。
- **`Commands/HostCommandDispatcher.cs`**：新增可选 `runAuthorizeWithResult` + `runDispatched`（Host 内部，
  零 wire；旧 `runAuthorize` 保留兼容）；post-dispatch 钩子失败绝不影响已 dispatch 的 Run。
- **零改动**：`src/**`（Core/Python 生产代码）、Run wire/`RunContracts`、能力/错误闭集/TTL、App/UI、
  C-06/C-16/C-15/C-17 字节、schema/依赖。

## 5. L-G1 状态与子限制（必须保留）

**L-G1：从「无续期」降级为「有续期 + 子限制」，不关闭。** 仍保留：

1. **单步 >300s**：一个 provider 步骤本身超过 300s 时，续期窗口无法覆盖（续期只保证「窗口前/中」有 live grant）。
   - **预算 skip 语义（Review r1 P2-01）**：单轮超过 50s 预算时本轮被 **typed skip**（保留跟踪、下一 interval 再试，尝试次数计入 `maxRenewals` 硬上限）；这是「本轮跳过」，不是「续期成功」，也不是「Run 失败」。
2. **续期失败**：Core typed 拒绝 / 全 source mint skip / Host 能力缺失 / 探测未知 → 停止续期（不重试、不 reattest、不自动重新授权）；Run 余下页由 Core fail-closed。
3. **加密源（L-G2）**、**Core 重启（L-G9）**、**viewer 无活跃 Run 时读引用页（L-R1 残余）**、**>4096 成员（L-G16）**：本卡不修。
4. **多 Run 排队**：续期只在 dispatch 后启动；**尚未 dispatch 的 pending Run 不在本卡范围**（其 grant 尚未铸造）。
5. **成本**：每轮重新 mint（容器整文件 sha256 / folder 逐成员）——L-G8 成本按 240s 周期放大；单轮超过 50s 预算即 typed 停止（不长期占用 mint gate）。
6. **mint 期间撤销/漂移**：续期与用户撤销竞态由每轮 `Registry.Authorize` + Core per-page 原子匹配兜底；失败即停，绝不放行。
7. `SourceIdentityCache` TTL=3600s > 240s×12≈48min；超过 1h 的 Run 可能触发 bounded on-demand 扫描（≤8/轮、30s/源），本轮超预算即停止（AC-2C-5）。

## 6. 真实性声明

1. **实跑**：§2 所有 PASS 数字均来自本 EV 记录命令的现场执行；未跑项见 §5/本条。
2. **NOT_RUN**：真实 300s 墙钟等待（**不做**；时间维用 in-process fake clock）；真实用户数据/回收站/AppData；`git push`；linked worktree；契约 byte-level 复核（本卡零契约改动，pins/blob 比对即为证明）；完整 gated Core 时钟前推（真子进程 Core 无法 monkeypatch —— 已由 Python in-process 测试承担）。
3. **判别力**：§3 的 7 个破坏点均实际造成对应用例非 0 退出，且逐例原字节复原后复绿。
4. **未夸大**：本卡不宣称「L-G1 关闭 / 任意长 Run 可用 / Run 全面恢复 / 自动恢复/自愈/自动重新授权/撤销后放行」；只承诺「多步长 Run 在续期窗口内可持续（Host 周期重铸同一冻结 scope 的 grant + 重发既有授权命令）」。
5. **证据归因**：数字属于 `delivery_head=7c95bb3c4`（返修后）的代码/测试树；初版 `e5e9c4c52` 的数字保留在历史证据中，返修后全部重跑并覆盖本 EV；随后同批 docs/evidence 提交不含实现字节。
6. **外部依赖**：gated 真 IPC 使用真实 Python Core（`C:/Python314/python.exe`）与仓外 fixture 根
   `G:/CODEX/New Manga.workspace/FEA-11-RUN-GRANT-2C/fixtures/ipc-*/`；Python in-process 测试使用同根 `fixtures/test_*`。

## 7. 复现（repo root）

```powershell
dotnet build apps/desktop-avalonia/NewManga.sln -c Release
dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~RunGrantRenewal"
dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~SourceRegistryTests|FullyQualifiedName~Fea11RunGrantIpc"
$env:NEWMANGA_FEA11_IPC='1'
dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~Fea11RunGrantIpc"
C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q
C:/Python314/python.exe -m pytest tests -q
cd apps/desktop-avalonia; dotnet test NewManga.sln -c Release; cd ../..
pwsh -NoProfile -File tools/governance/verify_pins.ps1
pwsh -NoProfile -File tools/governance/check.ps1
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-RUN-GRANT-2C.md
C:/Python314/python.exe tools/generate_api_inventory.py --check
C:/Python314/python.exe verification/FEA-11-RUN-GRANT-2C/tools/scope_validation.py
C:/Python314/python.exe verification/FEA-11-RUN-GRANT-2C/tools/discrimination.py
git checkout -- verification/FEA-09
```
