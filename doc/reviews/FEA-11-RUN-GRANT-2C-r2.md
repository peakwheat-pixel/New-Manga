---
task: FEA-11-RUN-GRANT-2C
task_id: FEA-11-RUN-GRANT-2C
title: 2C 长 Run 续期实现独立 Review r2（r1 返修复审：Host 接线判别 + 轮前预算；C-06 v1.3 / C-16 v1.6）
reviewer: fresh subagent（独立上下文；session a4410d0a-cb74-43d2-8379-7c5a9d8a88d6；未参与本卡实现、返修、scope review 或契约前置；只读）
session: a4410d0a-cb74-43d2-8379-7c5a9d8a88d6
parent_session: session-3ac1953a-094e-4339-889a-284df2b7b34d
reviewer_kind: fresh_subagent_independent_impl_review
author: l-s4b1-impl
repo: G:\CODEX\New Manga
branch: main
base_commit: c5f1b416f
reviewed_head: 7c95bb3c4
verdict: approved
decision: approved
date: 2026-11-07
---

# FEA-11-RUN-GRANT-2C 独立实现 Review r2（r1 返修复审）

## 结论先行

- **verdict = `approved`（P0=0 / P1=0 / P2=1 / P3=7）。**
- **P1-01 按 r1 的判别口径关闭**：`HostRuntime` 的续期安装行已抽成唯一方法 `StartRunGrantRenewal()`，新增 3 个 Host 接线用例。我自跑 **Probe-C**（删除 `StartRunGrantRenewal()` 的赋值体，等价于 reviewer 的「续期整体关闭」）：全量 Host **281 passed / 2 failed / 65 skipped**，恰为 `HostWiring_DispatchThenProductionTick_RenewsTheSameFrozenScope` 与 `HostWiring_ManagedOnlyRun_StartsNoRenewal` 两条 RED；恢复后 sha256 `bae563e1…` MATCH、`git hash-object` `0098ff5f…`、重建 0/0、复盘 **19/0/0**。**AC-2C-1「删续期 → RED」成立。**
- 第三个 `HostWiring_DisabledOption_InstallsNoLoopAndNeverTracks` 在 Probe-C 下不 RED 是**正确语义**：它判别的是「option 关闭 → 不安装」（与「安装行被删」同向结果），不是安装行删除方向；删除方向已由两条主用例承担，不影响 P1-01 关闭。
- **P2-01 关闭**：`roundBudget` 在进入单轮前传入 mint 路径（`TickAsync → _renew(...,roundBudget,...)` → `RenewRunGrantsAsync → AuthorizeSliceAsync(...,roundBudget)` → `ResolveWithColdCacheAsync(...,roundBudget)`）；每个 on-demand 冷扫描 timeout = `min(30s, 剩余预算)`、耗尽即停并留余 cold；事后守护保留；超预算 → `SkippedBudget` typed skip + `BudgetSkips` 计数 + 保留跟踪 + 真实 mint 照计 `Renewals`；预算取消与 caller token 未混淆，不把 `RoundBudget` 当作 Run 失败。4 个预算用例成立，D5/D9 判别 RED。
- **P3 处置**：①预算 mint/bound/code 与 `Renewals` 计数已落地；②`LedgerStatus()` 已接入 `RenewRunGrantsAsync` 成功日志（非死代码）；③EV/Handoff 已无 TBD/字面 `\n`，数字基本填实；④manifest 已排除 `__pycache__/*.pyc`，`repo_head_at_generation=7c95bb3c4…` 可到达（非 amend 孤儿）；⑤FROZEN-C16 §2 第 8 行已 ✅（Lead 早前提交，确认即可）。
- **残留（不阻断）**：**P2=1**——3 个 HostWiring 用例驱动的是 `HostRuntime` 的生产方法，**没有**穿过 `HostCommandDispatcher` 实例、`StartInternalAsync` 的安装调用点或 `AcceptRunAsync` 的启动调用点；我另做 3 个「删调用点」探针，每次全量 Host 均 **283/0/65 全绿**（见 §5）。这是 r1 P1-01 的窄化残留，当前代码行为正确，建议 closeout 前补 dispatcher/AcceptRun 级判别或登记 limitation。另有 P3×7（生产 liveness 探针无测试、预算事后守护吞 typed code、r1 P3-04 typed code 折叠未处置、EV/Handoff 少量口径滞后、预算窗口未计 probe/mint 超时、manifest 历史提交 sha 口径、测试 seam 为 public/死代码）。
- **不夸大口径 PASS**：卡/EV/Handoff 一致写「有续期 + 子限制」；未发现「任意长 Run 可用 / L-G1 关闭 / Run 全面恢复 / 自动恢复 / 自愈 / 自动重新授权 / 撤销后放行」表述。

## 1. 基线与只读事实

| 项 | 值 | 来源 |
|---|---|---|
| HEAD / branch | `3945e1f5c` / `main` | 实测 |
| 领先 origin | 3 个未 push 提交：`7c95bb3c4`、`03361fec6`、`3945e1f5c` | `git log --oneline origin/main..HEAD` |
| delivery head | `7c95bb3c4`（初版 `e5e9c4c52`；实现 `c40489b5d`） | 卡 `:17`、EV `:14-18` |
| 实现起点 | `c5f1b416f`（scope 脚本口径）；卡 `base_commit=fdd170039` | `verification/.../tools/scope_validation.py:48-49` |
| 工作树（开始/结束） | **clean**；结束时唯一未跟踪项为本报告 `doc/reviews/FEA-11-RUN-GRANT-2C-r2.md`（待 Lead 入库） | `git status --porcelain` |
| 返修 diff | 4 文件 +545/−72：`HostOptions.cs`、`HostRuntime.cs`、`RunGrantRenewal.cs`、`RunGrantRenewalTests.cs` | `git show --stat 7c95bb3c4` |
| `src/**`（Core/Python 生产） | **0 行 diff**（`git diff c5f1b416f 7c95bb3c4 -- src/`） | 实测 |
| App / Run wire / `CoreServiceClient` / `RunContracts` | **0 行 diff** | 实测 |
| `+300` / `MaxRunGrants` / `MaxTrackedPayloads` | 仍为 `_clock()+300`、`64`、`256`（`SourceReadCoordinator.cs:603,74,77`） | 实测 |
| pins | **18/18**；C06 v1.3 `75f8e2b4…`、C16 v1.6 `b8f46fb1…` | 自跑 `verify_pins.ps1` |
| 卡 status | `ready`（未改；Lead 维护） | 卡 `:6` |
| FROZEN-C16 §2 第 8 行 | ✅（r6 approved，行 51） | `doc/plan/FEA-CONTRACT-FROZEN-C16.md:51` |
| manifest | 21 个证据文件 sha256 **21/21 MATCH**；`repo_head_at_generation=7c95bb3c4234599eab404e2061d71e04edfaf9da` 可到达（`main` 包含）；无 `__pycache__/*.pyc` | 实测 + `git cat-file` |
| gated 证据 | `renewal-ipc.json` sha256 `0bde5be4…` 与本次 gated 产出**逐字节相同** | 实测 |
| 全量基线（日志/Lead 口径，未重跑） | pytest **3363/10 EXIT=0**，.NET **1680/0/96 EXIT=0**；卡/EV/Handoff 一致；`STATUS.md:14` 仍写 1674/0/96（Lead 维护，滞后） | `logs/full-*.log`、`doc/STATUS.md` |

## 2. A–I 逐项核对

| 项 | 判定 | 依据（实测/字节） |
|---|---|---|
| **A 续期主 AC** | **PASS（P1-01 关闭；P2 残留）** | 生产 HostRuntime 接线用例驱动真实 pre-auth summary → 真实 `RunDispatchedAsync` → `Track` → 生产 `TickAsync` → `RenewRunGrantsAsync`；Probe-C 使 2 条主用例 RED；Python fake clock 窗口后读/提交 typed 失败、续期后恢复；gated 同 scope 二轮 `bound_pages=1`、页可读。残留：dispatcher/StartInternalAsync/AcceptRun 三处调用点删除后测试仍全绿（R2-01）。 |
| **B 不延长/不扩 scope/不改 command** | PASS | 每轮 `IssueLockedAsync` 新 GUID + `expiry=_clock()+300`（`SourceReadCoordinator.cs:603`），旧 payload 不写；`Renewal_NeverWidensTheFrozenCommandOrScope`；gated 两帧 command/scope 逐字节相等、`new_grant_id=true`；Python 续期后旧 grant 仍 `SOURCE_GRANT_EXPIRED`。 |
| **C 撤销/漂移即停** | PASS（P3 探针缺口） | 每轮 `RenewRunGrantsAsync → AuthorizeSliceAsync` → 逐源 `IssueLockedAsync` → `Registry.Authorize` + 物理 facts（`SourceReadCoordinator.cs:277-353`）；typed/全 skip → `StoppedTyped` 停止不重试；Python 不同 scope/command typed 拒绝零映射。生产 `ProbeRunLivenessAsync` 无测试（R2-02）。 |
| **D 失败不放行/不自动重试** | PASS（P3 边界） | 任一 typed/异常/全 skip → `Stop` 并移除、不 reattest/不新建 Run（`RunGrantRenewal.cs:328-405`）；gated `reattest_frames=0`、registry 结构不变；Core `authorize_run_bindings` 任一页拒绝整请求、零映射（`source_read_refs.py:504-537`）。预算事后守护先于 typed 判定的边界见 R2-03。 |
| **E 预算/间隔/轮次** | PASS（P2-01 关闭） | 默认 interval=240/max=12/budget=50；`Normalize` 只接受 240..249 与 1..100；`240+50<300`；`_gate` 串行 mint；预算进入 mint 路径、每扫描 `min(30s,剩余)`、耗尽即停；超预算 typed skip + 计数 + 保留跟踪 + mint 照计；轮次上限按尝试次数；终态/关停停止。窗口未计 probe/mint 超时（R2-06）。 |
| **F 接线/无 App/零 wire/既有值不变** | PASS（P2 证据缺口） | dispatcher `runAuthorizeWithResult` + `runDispatched`（`HostCommandDispatcher.cs:71-93,173-225`，Host 内部，零 wire）；`AcceptRun` 与 post-dispatch 两入口；`+300`/TTL/`MaxRunGrants`/`MaxTrackedPayloads` 零改动；App 零 diff。调用点判别缺口见 R2-01。 |
| **G 不夸大/L-G1** | PASS（P3 文档滞后） | 卡 `:55,61,75`、EV `:3-6,117-135`、Handoff `:64-72` 一致「有续期 + 子限制」，保留单步 >300s/续期失败/L-G2/L-G9/L-R1/L-G16/未 dispatch pending；无禁止词。EV/Handoff 的「typed 停止」与 7/7 残留见 R2-05。 |
| **H 独立实跑** | PASS | 见 §4；build 0/0、19/0/0、Probe-C 281/2/65、gated 7/0/0、pytest 3、pins 18/18、check×2 PASS(3w)、API 0、scope PASS；另做 3 个调用点破坏探针并逐字节恢复。 |
| **I 证据/判别性/scope** | PASS（P3 卫生） | manifest 21/21 sha 实测一致；discrimination 9/9 RED_AS_EXPECTED；delivery 32 文件 ⊆ allowed_paths、`src/**` 与禁止面零 diff、C15/C17 blob 零漂移、`PROTOCOL_MINOR=3`、卡 status 未改；gated JSON 逐字节一致。r1 P3-04 typed code 未处置（R2-04）、manifest 历史 sha 口径（R2-07）。 |

## 3. 重点核对（逐项结论）

### 3.1 P1-01（r1：Host 接线无判别测试）——**关闭（按 r1 口径）；P2 残留**

- **生产入口链**：`HostWiring_DispatchThenProductionTick_RenewsTheSameFrozenScope`（`RunGrantRenewalTests.cs:577-647`）在**真实 `HostRuntime` 实例**上：
  1. `AuthorizeRunCommandForTestsAsync` → 生产 `RunAuthorizeWithResultAsync`（即 dispatcher 的 `runAuthorizeWithResult` 同一方法）返回 Host-owned summary；
  2. `NotifyRunDispatchedForTestsAsync` → 生产 `RunDispatchedAsync`（即 dispatcher 的 `runDispatched` 同一方法）→ `MaybeStartRunGrantRenewal` → `ObserveDispatch` → `Track`；
  3. `TickRunGrantRenewalForTestsAsync` → 已安装 loop 的生产 `TickAsync`；`_renew` 是生产 `RenewRunGrantsAsync`（非 fake）；
  4. 断言 dispatch + renewal 两次 `authorize` 调用、同一 `command`、`Renewals=1`。
- **seam 性质**：3 个 `HostWiring_*` 只做转发（`StartRunGrantRenewalForTests` → `StartRunGrantRenewal`；`NotifyRunDispatchedForTestsAsync` → `RunDispatchedAsync`；`TickRunGrantRenewalForTestsAsync` → `TickAsync`），没有测试专用假实现替代生产语义；唯一注入是 `HostOptions.RunGrantRenewalLivenessProbe`（生产默认 null → 真实 `ProbeRunLivenessAsync`）和测试 `RunSourceAuthorizer` 的 mint delegate（既有单测边界）。
- **Probe-C（我自跑）**：`probe-c-apply.py` 删除 `StartRunGrantRenewal()` 的赋值体 → 全量 Host **281/2/65**，恰好 `HostWiring_DispatchThenProductionTick_RenewsTheSameFrozenScope` 与 `HostWiring_ManagedOnlyRun_StartsNoRenewal` RED；恢复后 sha256 MATCH、`git hash-object` `0098ff5f…`、重建 0/0、**19/0/0**。**AC-2C-1「删续期 → RED」成立。**
- **第三个 `HostWiring_DisabledOption_*` 不 RED 的评价**：正确。它判别「option 关闭 → 不安装 loop / 不 Track」，与「安装行被删」产生同样的 null 状态，因此 Probe-C 下继续通过是预期；删除方向由前两条承担，**不构成 P1-01 缺口**。
- **P2 残留（R2-01）**：3 条用例没有穿过 `HostCommandDispatcher` 实例、`StartInternalAsync` 的安装调用点、`AcceptRunAsync` 的启动调用点。我另做 3 个删调用点探针（见 §5）：每次全量 Host **283/0/65 全绿**。即「功能方法」有判别，「生产调用点」仍无。当前代码行为正确，故判 P2（测试完整性/未来回归风险），不改变 P1-01 关闭。

### 3.2 P2-01（r1：预算是事后检查）——**关闭**

- `RunGrantRenewal.TickAsync`（`RunGrantRenewal.cs:340-349`）：`roundBudget = RunGrantRenewalOptions.RoundBudget`（50s），在 **进入单轮前** 传给 `_renew`。
- `HostRuntime.RenewRunGrantsAsync`（`:1626-1667`）：`authorizer.AuthorizeSliceAsync(command, scope, token, roundBudget)`。
- `RunSourceAuthorizer.AuthorizeSliceAsync`（`:2371-2440`）→ `ResolveWithColdCacheAsync`（`:2451-2516`）：每个冷扫描 `scanTimeout = min(OnDemandScanTimeout=30s, totalRoundBudget - stopwatch.Elapsed)`；`remaining <= 0` 时 `break` 并留余 cold；`_onDemandGate` 串行。
- 事后守护保留（`:371-385`）：`elapsed > roundBudget` → `BudgetSkip("RENEWAL_ROUND_BUDGET_EXCEEDED")`；若该轮实际 `Renewed`，先 `_renewals++`（真实 mint 不被吞）；`BudgetSkip` 增 `_budgetSkips`、写 `LastCode`、保留 `_runs`（下一 interval 再试），不是续期成功、不是 Run 失败。
- **caller token 辨析**：`catch (OperationCanceledException)` 中 `if (token.IsCancellationRequested) throw;`，否则 `BudgetSkip("RENEWAL_ROUND_CANCELLED")`——未把预算取消误当 caller 取消，也未把 `RoundBudget` 当 Run 失败。
- **判别性**：`Renewal_RoundOverBudget_SkipsTheRoundAndKeepsTracking`（`:239-277`，断言 `budgets=[50s]`、`BudgetSkips=1`、`Renewals=1`、`Attempts=1`、保留跟踪）、`Renewal_BudgetSkip_DoesNotConsumeTheGateOrStopTheRun`（`:280-309`，断言下一 tick 可续期、两次 mint 照计）、`AuthorizeSliceAsync_BoundsOnDemandScansByTheRoundBudget`（`:474-500`，实测 <1.5s 而非 30s）、`AuthorizeSliceAsync_WithoutRoundBudget_KeepsTheFrozenOnDemandTimeout`（`:503-523`，dispatch 路径无回归）。D5（删事后守护）与 D9（预算不再传 cold fill）均 RED。

### 3.3 P3-01…P3-05（r1 P3 处置）

| r1 P3 | 判定 | 依据 |
|---|---|---|
| ① 预算路径记录 minted/bound/code，真实 mint 计入 `Renewals` | **PASS** | `RunGrantRenewal.cs:371-385,411-428`；测试断言 `minted`/`bound_pages`/`code`/`Renewals=1`（`:270-274`）。 |
| ② `LedgerStatus()` 真实调用，不再死代码 | **PASS** | `HostRuntime.cs:1656-1663` 在每成功轮读 `Sources.LedgerStatus()` 并记 `tracked/max/grants`；HostWiring 用例实际走到该路径。 |
| ③ EV/Handoff 去 TBD/字面 `\n`、数字填实 | **PASS（残留 R2-05）** | 三文件无 `TBD`/字面 `\n`；19/32/7/7/0/92/3363/1680/18/9 等数字已填。但 EV `:62` 仍 7/7（§3/卡/Handoff 为 9/9）；EV §5 两处/Handoff `:33,70` 仍写「typed 停止」（现为 skip）；Handoff frontmatter/§4/§5 仍 `e5e9c4c52`。 |
| ④ manifest 排除 `__pycache__`、head 可到达 | **PASS（P3 口径残留 R2-07）** | 21 文件无 `__pycache__`/`.pyc`；`repo_head_at_generation=7c95bb3c4…` 可到达、`main` 包含、非 amend 孤儿；manifest 21/21 sha 与当前字节一致。历史提交行的 sha 用最终快照（R2-07）。 |
| ⑤ FROZEN-C16 §2 第 8 行 ✅ | **PASS** | `doc/plan/FEA-CONTRACT-FROZEN-C16.md:51` 为 ✅；Lead 早前提交，本卡未动契约字节。 |
| r1 P3-04（typed skip code 折叠，未在返修清单） | **未处置（R2-04）** | `RenewRunGrantsAsync` 仍把全 skip 折叠为 `RENEWAL_NO_TARGETS`、null 为 `RENEWAL_NOT_AUTHORIZED`，丢 `SOURCE_GRANT_REVOKED`/`SOURCE_REGISTRY_BUSY`；EV §3.1 P3 处置未列此项。 |

### 3.4 L-G1 口径

卡 `:55,61,75`、EV `:3-6,117-135`、Handoff `:64-72` 一致：**「有续期 + 子限制」**，保留单步 >300s、续期失败、L-G2、L-G9、L-R1 残余、L-G16、未 dispatch 的 pending Run 不在范围、L-G8 成本放大；**未**出现「任意长 Run 可用 / L-G1 关闭 / Run 全面恢复 / 自动恢复 / 自愈 / 自动重新授权 / 撤销后放行」。EV `:126,128`/Handoff `:33,70` 的「typed 停止」措辞与新 skip 语义不一致（R2-05），但未改变「不关闭」口径。

### 3.5 真实性 / 新风险

- **证据字节**：manifest 21/21 sha 与当前字节一致；gated `renewal-ipc.json` 与本次产出逐字节相同（`0bde5be4…`）；`logs/host-unit.log` 19/0/0、`regression.log` 32/0/7、`gates.log` pins/check/API 数字、`full-*.log` 3363/10 与 1680/0/96 均与卡/EV/Handoff 一致（STATUS 1674 为 Lead 滞后）。
- **scope 外改动**：无。返修 4 文件 + docs/evidence；`src/**`、App、Run wire、`+300`/TTL/`MaxRunGrants`/`MaxTrackedPayloads`、C-06/C-16/C-15/C-17 字节零 diff；`PROTOCOL_MINOR=3`。
- **测试 seam 泄漏**：`*ForTests*` 与 `RunGrantRenewalLivenessProbe` 均为 Host 内部 C# 成员，未成为 IPC 命令/UI 能力；但为 `public`（R2-08）。
- **fail-closed 语义**：每轮重走 `Registry.Authorize` + facts；typed/全 skip 停止；Core 整请求原子拒绝；预算 skip/typed 边界见 R2-03；未发现放行/扩权/延长 TTL/绕过撤销/新增 wire。

## 4. 独立实跑（本会话，repo root）

| # | 场景 | 命令（摘要） | 结果 |
|---|---|---|---|
| 1 | 构建 | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` | **0 warning / 0 error，EXIT=0** |
| 2 | 续期+接线单测 | `dotnet test ...Host.Tests.csproj -c Release --no-build --filter "FullyQualifiedName~HostWiring|FullyQualifiedName~RunGrantRenewal"` | **19 passed / 0 failed / 0 skipped，EXIT=0**（Probe-C 恢复后复跑同） |
| 3 | **Probe-C** | `probe-c-apply.py` → build → 全量 Host `--no-build` → `probe-c-restore.py` → 复核 → build → #2 | **281 passed / 2 failed / 65 skipped，EXIT=1**；恰为 `HostWiring_DispatchThenProductionTick_RenewsTheSameFrozenScope` + `HostWiring_ManagedOnlyRun_StartsNoRenewal`；恢复 `bae563e1…` MATCH=True、blob `0098ff5f…`、重建 0/0、**19/0/0** |
| 4 | gated 真 IPC | `$env:NEWMANGA_FEA11_IPC='1'; dotnet test ... --filter "FullyQualifiedName~Fea11RunGrantIpc"` | **7 passed / 0 failed / 0 skipped，EXIT=0**；新 fixture `renewal-ipc.json` sha256 `0bde5be4…` == 入库证据 == manifest |
| 5 | fake clock | `C:/Python314/python.exe -m pytest tests/fea11/test_source_run_grant.py -q -p no:warnings -k "after_the_window or past_the_window or never_rebinds"` | **3 passed, 27 deselected** |
| 6 | pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PIN AUDIT: PASS (all 18)，EXIT=0** |
| 7 | check | `check.ps1`（默认 + `-TaskPath doc/tasks/FEA-11-RUN-GRANT-2C.md`） | **PASS (3 warnings) ×2，EXIT=0** |
| 8 | API | `C:/Python314/python.exe tools/generate_api_inventory.py --check` | **EXIT=0** |
| 9 | scope | `C:/Python314/python.exe verification/FEA-11-RUN-GRANT-2C/tools/scope_validation.py` | **PASS changed=32、out_of_scope=[]、forbidden=[]、minor=3、pins_ok=True、blobs_ok=True，EXIT=0**；`git diff c5f1b416f 7c95bb3c4 -- src/` **0 行** |
| 10 | 全量 Host（恢复后额外复跑） | `dotnet test ...Host.Tests.csproj -c Release --no-build` | **283 passed / 0 failed / 65 skipped，EXIT=0** |
| 11 | 全量 pytest/.NET | **未重跑**（采信 Lead/日志） | pytest **3363/10 EXIT=0**；.NET **1680/0/96 EXIT=0**；卡/EV/Handoff 一致 |

- **scope 口径**：`git diff c5f1b416f`（工作树 vs 起点）为 37 文件 = 32 delivery + 5 CONCURRENT_NON_DELIVERY（`doc/STATUS.md`、`doc/handoffs/DSH-HANDOFF-2026-11-06.md`、`doc/handoffs/DSH-PROGRESS-2026-11-07.md`、`doc/plan/FEA-CONTRACT-FROZEN-C16.md`、`doc/reviews/FEA-11-RUN-GRANT-2C-r1.md`）；32 delivery 全 ALLOWED。
- **scope 脚本写入恢复**：脚本会重写 `scope-validation.log`（仅时间戳）与 `changed-files.txt`；我已 `git checkout -- verification/FEA-11-RUN-GRANT-2C/scope-validation.log` 恢复，sha256 `58e56d4e…` 与 manifest 一致；`changed-files.txt` 字节未变。

## 5. 破坏性复跑（先备份字节，结束逐字节恢复 + sha 复核）

| # | 破坏点 | 目标测试 | 结果 | 恢复 |
|---|---|---|---|---|
| **Probe-C**（任务指定） | `StartRunGrantRenewal()` 删除赋值体（`_runGrantRenewal = CreateRunGrantRenewal();` → 注释） | 全量 `NewManga.Host.Tests`（348） | **281 passed / 2 failed / 65 skipped，EXIT=1**；2 个失败恰为 `HostWiring_DispatchThenProductionTick_RenewsTheSameFrozenScope` 与 `HostWiring_ManagedOnlyRun_StartsNoRenewal` | `HostRuntime.cs` sha256 `bae563e1…` MATCH=True；`git hash-object` `0098ff5f…`；BYTES_EQUAL=True；重建 0/0；复盘 19/0/0 |
| R2-01-a（我附加） | 删除 `StartInternalAsync` 的 `StartRunGrantRenewal();` 调用 | 全量 Host | **283/0/65 GREEN**（调用点无判别） | 恢复后 blob `0098ff5f…` MATCH、全量 283/0/65 |
| R2-01-b（我附加） | 删除 dispatcher 构造里的 `runDispatched: RunDispatchedAsync` | 全量 Host | **283/0/65 GREEN**（dispatcher 活线无判别） | 恢复后 blob `0098ff5f…` MATCH、全量 283/0/65 |
| R2-01-c（我附加） | 删除 `AcceptRunAsync` 的 `MaybeStartRunGrantRenewal(...)` | 全量 Host | **283/0/65 GREEN**（AcceptRun 活线无判别） | 恢复后 blob `0098ff5f…` MATCH、全量 283/0/65 |

- 备份位于 `G:\CODEX\New Manga.workspace\FEA-11-RUN-GRANT-2C\review-r2\`；未写 `verification/FEA-09/**`；结束 tracked 工作树 0 行（唯一未跟踪为本报告）。

## 6. AC-2C-1…8 判定

| AC | 判定 | 说明 |
|---|---|---|
| AC-2C-1 续期主 AC | **MET（P2 证据缺口）** | 生产 HostRuntime 接线用例 + Probe-C 2 RED；fake clock before/after；gated 二轮。调用点判别见 R2-01，不改变 MET 的语义判定。 |
| AC-2C-2 不延长/不扩/不改 | MET | 新 id、旧 `expires_at` 不变、command/scope 同值（单测 + Python + gated）。 |
| AC-2C-3 撤销/漂移即停 | MET | 每轮重走 Authorize+facts；typed 停止不重试；生产 liveness 探针无测试（R2-02）。 |
| AC-2C-4 失败不放行/不自动重试 | MET（P3 边界） | typed/异常/全 skip → 停止；Core 整请求原子拒绝；`reattest_frames=0`；预算事后守护吞 typed code 的边界（R2-03）。 |
| AC-2C-5 预算/间隔/轮次 | MET | 240+50<300；`_gate` 串行；预算进入 mint 路径；超预算 skip + 计数 + 保留跟踪；4 用例 + D5/D9；窗口未计 probe/mint 超时（R2-06）。 |
| AC-2C-6 接线/无 App | MET（P2 证据缺口） | 代码接线、零 wire、零 App、既有值不变均在；调用点判别见 R2-01。 |
| AC-2C-7 不夸大 | MET | 只降级不关闭，子限制清单完整；EV/Handoff 少量措辞滞后（R2-05）。 |
| AC-2C-8 门禁 | MET | pins 18/18、check×2、API、scope、build、19/0/0、gated 7/0/0、pytest 3 均自跑通过；全量为 Lead/日志口径（未重跑）。 |

## 7. Findings

| ID | 级别 | 位置 | 问题与影响 | 证据 | 建议 |
|---|---|---|---|---|---|
| R2-01 | **P2** | `HostRuntime.cs:1237`、`:1260-1261`、`:102`；`HostCommandDispatcher.cs:173-225` | 3 个 HostWiring 用例驱动 HostRuntime 方法，未穿过生产调用点；删除 `StartInternalAsync` 的安装调用、dispatcher 的 `runDispatched:` 参数、或 `AcceptRunAsync` 的启动调用，全量 Host 均 **283/0/65 全绿**。当前代码正确；未来删除调用点会静默关闭续期，测试不红。 | §5 三个附加探针 | closeout 前补 dispatcher/AcceptRun 级判别（fake Core/dispatcher 或扩展 `AcceptRunAsyncDelegatesToTheAuthorizationSeam` 断言 Track）；`StartInternalAsync` 调用点可用启动集成或登记 limitation。 |
| R2-02 | P3 | `HostRuntime.cs:1674-1716`；`RunGrantRenewalTests.cs:565` | 生产 `ProbeRunLivenessAsync` 无测试：接线用例一律注入 `RunGrantRenewalLivenessProbe=Alive`；删/改终态映射（恒 Alive）不会被发现，终态 Run 会续 mint 至轮次上限（Core 仍 fail-closed，不产生越权读）。 | 静态 grep + 全量 283/0/65 | 把 status 映射抽纯函数单测，或 fake Core 测 `RUN_NOT_FOUND`/terminal/typed 三路。 |
| R2-03 | P3 | `RunGrantRenewal.cs:371-390` | 事后预算分支先于 `!outcome.KeepsTracking`：若 `_renew` 返回 `StoppedTyped` 且耗时 >50s，被改写成 `SkippedBudget`、保留跟踪、下一轮重试、`LastCode` 被覆盖；r1 P3-03 的「真实 mint 计数」已修，「吞 typed code/重试」未修。窗口窄（需 >50s），fail-closed，无越权读。 | 静态代码；r1 P3-03 | 先判 `!KeepsTracking` 再判预算，或保留原始 `Code`；若按 AC-2C-4 严格口径可升 P2。 |
| R2-04 | P3 | `HostRuntime.cs:1644-1654` | r1 P3-04 未处置：全 skip → `RENEWAL_NO_TARGETS`、null → `RENEWAL_NOT_AUTHORIZED`，丢失 `SOURCE_GRANT_REVOKED`/`SOURCE_REGISTRY_BUSY` 等 §6 code；EV §3.1 返修清单未列此项。诊断口径，非放行。 | 静态代码；r1 P3-04 | 保留首个 typed skip code 进 `Status.LastCode`/日志。 |
| R2-05 | P3 | `EV.md:62,126,128`；Handoff `:7,33,70,76,90`；`STATUS.md:14` | 文档口径滞后：EV §2 仍 7/7（§3/卡/Handoff 9/9）；EV §5/Handoff 仍写「超预算 typed 停止/单轮 >50s 即停止」（现为 skip + 保留跟踪）；Handoff frontmatter/§4/§5 仍 `e5e9c4c52`；STATUS 基线 1674/0/96 vs 1680/0/96（Lead 维护）。 | 实测字节 | Lead closeout 时一次清理；不改实现字节。 |
| R2-06 | P3 | `HostRuntime.cs:1674-1716`（probe）、`:1642`（mint）；`RunGrantRenewal.cs:343-385` | 预算窗口只计 `_renew`（cold fills + bind），不含每轮 `ProbeRunLivenessAsync`（可用 `RequestTimeout=30s`）与 mint 自身请求超时；最坏 `probe + round > 60s` 时新 grant 可能晚于旧 grant 的 300s TTL，出现连续性缺口（Core fail-closed）。`AuthorizeSliceAsync` 注释「mint never waits for more than the remaining budget」不准确；EV「不长期占用 mint gate」偏强。 | 静态代码；`HostOptions.cs:73` | 把 probe/mint 计入预算，或在 EV/Handoff 的子限制里如实写最坏值；修注释。 |
| R2-07 | P3 | `RESOURCE-MANIFEST.json:35-96`；`gen_manifest.py:54-71` | `changed_files` 的 `(commit,path,sha256)` 对早期提交使用最终工作树 sha：`c40489b5d:HostRuntime.cs` 实际 blob sha256 `fce654b8…`，manifest 写 `bae563e1…`；`file_count=12` 为 12 条 (commit,path)，唯一路径 8。note 已写「generation-time snapshot」，故非假哈希，但按提交归因会误读。 | 实测 `git cat-file` | 用 `git cat-file blob` 的 sha，或把 sha 标注为「final snapshot」并去重。 |
| R2-08 | P3 | `HostRuntime.cs:1729-1771`；`HostOptions.cs:159-164`；`RunGrantRenewal.cs:173,266,506` | 测试 seam 为 `public`（非 internal/InternalsVisibleTo）；`Untrack` 无调用者、`_lifetime` 从未用于任何 token（死代码）。无 wire/UI 能力，属卫生项。 | grep | 改 `internal` + `InternalsVisibleTo`，或删除死代码并注明测试专用性。 |

## 8. 结论与复审建议

- **可交 DSH 集成**：`delivery_head=7c95bb3c4` 的 r1 返修在语义、判别证据、门禁与 L-G1 口径上成立；P0/P1=0，P2=1（调用点测试完整性）+ P3×7（非阻断）。
- **建议在 closeout 前**：①优先补 R2-01 的 dispatcher/AcceptRun 判别（或显式登记 limitation）；②一次 docs 清理（R2-05）；③若按 AC-2C-4 严格口径，考虑 R2-03/R2-04。以上均不改本卡交付行为，不要求重开实现。
- **复审建议**：以新 head 增量复核 R2-01 的补充测试与 R2-05 的文档修正；其余 P3 可在集成 docs 一次性闭环。

## 9. 真实性声明

1. **写入范围**：本会话唯一仓库写入为本报告 `doc/reviews/FEA-11-RUN-GRANT-2C-r2.md`；临时文件在 `G:\CODEX\New Manga.workspace\FEA-11-RUN-GRANT-2C\review-r2\`；未修改实现/测试/证据/卡/契约任何字节，未 `git add/commit/push`。Probe-C 与 3 个附加调用点探针均先备份、后逐字节恢复：`HostRuntime.cs` 最终 sha256 `bae563e14254e0a8dd660cd7314ccf0e679292bd7599ac47a9a3d5cb0d78946e`、`git hash-object 0098ff5fe6e6e01a6be40e23f9b768dd216de1d3`、`BYTES_EQUAL=True`。`scope_validation.py` 重写的 `scope-validation.log` 已恢复（sha256 `58e56d4e…`）；`changed-files.txt` 未变。结束 tracked 工作树 0 行；`git status --porcelain` 唯一未跟踪项为本报告（待 Lead 入库）。
2. **独立性**：本会话为父会话 `session-3ac1953a-094e-4339-889a-284df2b7b34d` 派发的 fresh subagent（session `a4410d0a-cb74-43d2-8379-7c5a9d8a88d6`），未参与本卡实现、返修、scope review 或 PREREQ-1；只读 `7c95bb3c4` 实现/测试字节与 `3945e1f5c` 证据字节。
3. **实测/未跑**：build、19/0/0、Probe-C 281/2/65、gated 7/0/0、3 例 fake-clock、pins 18/18、check×2、API、scope、全量 Host 283/0/65、3 个附加调用点探针为本会话实测；**全量 pytest/.NET 未重跑**（采信 Lead/日志：pytest 3363/10 EXIT=0、.NET 1680/0/96 EXIT=0，已核卡/EV/Handoff 数字）；未做真实 300s 墙钟、真实用户数据、`git push`、linked worktree；契约 byte-level 未重审（pins 18/18 + 固定字节比对承担）。
4. **口径**：L-G1 只降级不关闭；本报告不声称 L-G1 关闭、任意长 Run、Run 全面恢复、自动恢复、自愈、自动重新授权或撤销后放行。
