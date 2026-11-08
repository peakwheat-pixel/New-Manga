# FEA-07-RESIDUAL-2（R4a）证据索引

| 项 | 值 |
|---|---|
| 卡 | `doc/tasks/FEA-07-RESIDUAL-2.md`（FEA-07 收口 A，headless，**0 pin**） |
| base_commit | `0a39a78f0` |
| 实现提交（代码+测试，首轮） | `85207730e` |
| 文档/证据提交（首轮） | `9ec6b196b` |
| r1 返修提交 | `bacf6c307` |
| r2 返修提交（代码+测试） | `a03a6794a`（本文档/证据紧随其后：`docs(fea-07-residual-2): r2 证据与归因…`，见 `git log --oneline -- verification/FEA-07-RESIDUAL-2`） |
| 作用域扩域 | DSH 2026-11-08 批准**单文件**：`apps/desktop-avalonia/src/NewManga.App/Views/Presentation/PresentationWindow.cs`，改动 **+26/−5（净 +21，无功能删除）**；未改 `App.axaml.cs`/组合根/契约/pins |
| Review 状态 | r1 **approved**（P0=0/P1=0/P2=4/P3=12）；r2 **changes_requested**（P0=0/**P1=1**/P2=1/P3=7）→ 本轮 r2 返修已处置（gap 门槛移入专用门禁、证据归因、pytest/JSON/措辞） |
| 环境 | Windows 11（`Microsoft Windows NT 10.0.26300.0`）/ .NET `9.0.11` / Avalonia 11.3.22 headless / x64 |

## 1. 结论边界（不夸大）

- **达成**：AC-R4a-1（AC2 窗口层 draft owner）、AC-R4a-2（AC2 生命周期）、AC-R4a-3（AC6 指标与规模）、AC-R4a-4（AC8 证据与治理）。
- **不在本卡**：AC1/AC3/AC4 → `FEA-07-RESIDUAL-3`（R4b，gated/进程）。
- **NA（只登记一次，在 `doc/tasks/FEA-07.md` 的 AC5 行）**：AC5 原生双屏/拔屏/DPI 矩阵、AC1 原生 IME、AC2 真实双屏 broker 落位 = `NOT_APPLICABLE`（用户 2026-11-08 授权豁免；保留 `NOT_RUN`，不写成 PASS）。
- **P2-002 / L-R4a-1**：AC2 的**窗口层机制**已 MET；但**生产组合根**当前只有一个 `PresentationWindow`，**未注入共享 `DraftOwnershipRegistry`**，`WindowBroker.RegisterSecondary` **零调用**，**无 Floating 生产实例** ⇒ 跨窗口（真实双屏/浮窗）场景尚未在生产路径可见。跨窗接线（组合根注入 + Floating/Inspector 真实窗口 + 多窗口生命周期）由**多窗口功能卡**承接（卡内「Residual / 待接线（L-R4a-1）」）；本目录不写「跨窗已生产可用」。
- 本卡不写「FEA-07 完全实现 / 全部 limitation 关闭 / 可发布」；像素/UI 观感不作 AC 判据。
- 契约口径：只**引用** C-13 SC-D03（`doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md:55-66`）与冻结解释（`doc/tasks/FEA-07-RESIDUAL-2.md:45`），**不复述规则句**；`doc/plan/**`、`doc/contracts/**`、18 pins 零 diff。

## 2. 测试汇总（实跑，r2 返修后）

| 套件 | 命令 | 结果 | 证据 |
|---|---|---|---|
| 定向 | `dotnet test apps/desktop-avalonia/tests/NewManga.Presentation.Avalonia.Tests/NewManga.Presentation.Avalonia.Tests.csproj -c Release` | **72 / 0 / 0**（基线 38 → +34） | `logs/directed-presentation-tests.log` |
| App | `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj -c Release` | **816 / 0 / 8**（基线 804 → +12 通过；**8 skip** = 既有 7 + gated 性能门禁用例默认 skip） | `logs/app-tests.log` |
| 全量（×2） | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` | **1779 / 0 / 103**（基线 1733/0/102；skip +1 = gated 用例默认 skip），两次运行均 `失败: 0` | `logs/full-solution-tests.log`、`logs/full-solution-tests-run2.log` |
| 专用串行性能门禁 | `pwsh -NoProfile -File verification/FEA-07-RESIDUAL-2/tools/verify-fea07-perf.ps1`（`NEWMANGA_FEA07_PERF=1`，默认门禁不跑） | 3 轮 **PASS**（worst gap 340.90 ms ≤ 700，margin 51.3%；p95 全部 ≤1000） | `evidence/perf-gate-r2a.json`、`logs/perf-gate*.log` |
| pytest | 本卡零 Python 改动 | `pytest tests -q` = **3394 passed / 1 failed / 10 skipped**；失败为**既有 flaky** `test_plugin_sandbox.py::test_sandbox_job_kills_grandchildren`，隔离复跑该文件 **16 passed**；`git diff bf4207d4a..HEAD -- tests/ src/` **为空** | `logs/pytest-r2.txt` |

全量逐程序集（r2）：Appearance 21、Presentation.Avalonia 72、ThemeEngine 253、DesignSystem 117、ApplicationCore 31、Host 302/71 skip、CoreClient 167/24 skip、App 816/8 skip；全部 `失败: 0`。

**环境注意项（诚实记录；均为既有/无关用例或环境负载，本卡未修改被测用例）**：

1. 首轮全量（工作树含未提交改动时）出现既有跨程序集 race：`FluentResidual2VisualEvidenceTests.…Only_When_Opted_In` 断言「自身 23 s 窗口内 `verification/**` 的 `git status` 不变」，而 `NewManga.CoreClient.Tests.WireLogSourceRedactionTests` 并发重写 `verification/FEA-09/logs/wire-redacted.ndjson`。摘录：`logs/full-solution-first-run-cross-assembly-race.txt`。
2. r1 后一次全量中 `FluentR2ReworkTests.R3001_…(Reduce/All/0)` 命中一次 hit-test 断言（满负载下命中 `ReaderPage`）；同 head 单独 App 套件与随后全量均通过。摘录：`logs/full-solution-r1-flake-hit-test.txt`。
3. **本机在 r2 期间有外部应用持续占用 CPU（约 5.6/32 core）**：同一 gap 指标在空载串行 ~249 ms、负载串行 300–461 ms、并行全量 472–619 ms。这正是 r2 P1 的根因，处置见 §5 与 `evidence/ui-gap-loaded-condition-r2a.json`。

每次全量后按纪律 `git checkout -- verification/FEA-09`（零 diff）。

## 3. AC-R4a-1（AC2 窗口层 draft owner）

- 新增 `apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/Windows/DraftOwnershipRegistry.cs`：`(SessionId, RegionId)` owner store（线程安全、结果不可变、`DraftWriteRejectedException` typed 写入拒绝），含 `DraftOwnershipScope`（窗口身份 + 角色，**构造即注册角色**）；`WindowBroker` 薄转发 `TryClaimDraft`/`ReleaseDraft`/`RequestDraftTransfer`（现有注册 API 不变）；`PresentationWindow` 暴露 `DraftOwnership`（`WindowToken`），`Floating` 构造强制 `CanEdit=false`；`WindowRole.Unknown` 为**诊断专用**（未注册 token 的 typed 拒绝不再猜测 `Main`）。
- 机制覆盖（定向 34 = registry 23 + scope 6 + broker 转发 5）：同 key 跨 **OS 窗口**唯一 owner；第二个窗口 `ReadOnly` + typed `OtherWindowOwner`；`Floating` 恒只读（首个 claim 也只读）；**同窗口内浮动面板共享同一 `DraftId`（`Shared`，不拒绝）**；显式转移互斥且幂等（`Transferred` → 当前 owner 重复 = `Retained`+可编辑；**旧 owner 重复 = `Retained`+`CanEdit=false`+`NotOwner`**）；**未注册 target 的 transfer typed 拒绝（`UnknownWindow` + `WindowRole.Unknown`，不猜角色）**；`Release` 后可再 claim（新 `DraftId`）；64 并发 claim 恰 1 owner；跨 Session 同 Region 只读；**`EnsureWritable` 绑窗口身份 + 实时 owner + `DraftId`（他人/转移后/Release+reclaim 后旧 result → typed `NotOwner`）**。
- 窗口级（`tests/NewManga.App.Tests/DraftOwnershipWindowTests.cs`，8 个）：暴露 + 唯一 `WindowToken`、Floating 只读、第二窗口只读、同窗口面板共享、**只读写入 typed 拒绝且 `FakeHostController.DraftWriteLog` 为空（Host 零写入）**、窗口间显式转移、**`Floating` 仅构造未 claim 时 transfer 被拒且原 owner 保留编辑**（r1 transfer-before-claim）、窗口 `Release` 后 reclaim。
- 规则引用：C-13 SC-D03 `doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md:55-66` + 冻结解释 `doc/tasks/FEA-07-RESIDUAL-2.md:45`（**只引用不复述**，`FEA-C10-r1.md:83`）。

## 4. AC-R4a-2（AC2 生命周期）

`tests/NewManga.App.Tests/PresentationWindowHostLifecycleTests.cs`（3 个），逐项断言（不是聚合）：

- `CloseAndRebuild_LeaveEveryHostLifecycleItemUnchanged`：关闭 → 重建 → 切换前后 `StartCalls` / `StartRequests` / `LifecycleLog` / `DisposeCalls` 逐项不变，`Changed` 事件零触发。
- `SwitchingFrontends_DoesNotStartOrDisposeTheHost`：4 次切换后四项仍不变。
- `WindowLifecycle_IsDiscriminatingAgainstHostStartAndDisposeCalls`：脚本化 `StartException`/`DisposeException` 未被消费（两个异常对象仍在），证明判别不是「计数器碰巧为 0」。

`FakeHostController` 仅测试侧加法：`DisposeCalls` / `DisposeException` / `DraftWriteLog`（默认行为不变）。

## 5. AC-R4a-3（AC6 指标与规模）

**门槛未改**：热切换 p95 ≤ **1000 ms（W-5 冻结）**；断言 = **3 次独立运行 p95 中位数**（每轮 4 预热 + 20 测量）并固定形状（3 轮、中位 = 排序第 2 个 p95）。**规模只记录不改口径**。

**r2 R2-001 处置（gap 指标分层）**：

| 套件 | gap 行为 |
|---|---|
| 默认套件 `HotSwitch_P95MedianOfThreeIndependentRuns_StaysWithinTheFrozenW5Budget` | 只断言 p95 3 次中位；`uiThreadSchedulingGapMs` **只记录**（JSON `gapGateApplied=false`、`p95Passed`、`passed=p95Passed`） |
| 专用串行性能门禁 `Gated_HotSwitch_UiThreadSchedulingGapStaysWithinThePerfGateBudget` | 断言 p95 + gap（`p95Passed`/`gapPassed`/`passed=both`）；仅 `NEWMANGA_FEA07_PERF=1` 启用，**默认 skip + reason**；由 `tools/verify-fea07-perf.ps1` 串行运行，默认门禁不跑 |

`evidence/performance-baseline-r4a.json`（默认套件，`passed=true`、`gapGateApplied=false`）：

| 轮 | 冷启动 ms（单独记录，不入门槛） | p50 ms | p95 ms | max ms | `uiThreadSchedulingGapMs`（记录） |
|---|---|---|---|---|---|
| 1 | 275.93 | 139.19 | 378.86 | 390.95 | 192.14 |
| 2 | 291.51 | 151.48 | 392.71 | 407.37 | 208.56 |
| 3 | 284.12 | 135.12 | 373.40 | 467.05 | 202.88 |
| **中位** | — | **139.19** | **378.86** | — | worst **208.56** |

**串行性能门禁用 gap 预算 = 700 ms**，定标证据：

| 来源 | 条件 | worst gap ms |
|---|---|---|
| `evidence/ui-gap-calibration-r4a.json`（raw，r1 空载 3 轮） | 空载串行 | **249.44**（223.30 / 227.85） |
| `evidence/ui-gap-calibration-r4a.json`（raw，r2 3 轮，本机有外部负载） | 负载串行 | **454.61**（372.13 / 300.12） |
| `logs/perf-gate-round1.log`（预算 400，首轮 gated 尝试） | 负载串行 | **460.88**（376.05 / 420.99）→ 400 预算 RED（即 P1 现象） |
| `evidence/perf-gate-r2a.json`（3 轮，预算 700） | 负载串行 | **340.90**（308.29 / 282.75）→ **PASS，margin 51.3%** |
| `evidence/fullrun-recorded-gap-metrics-r2a.json`（r2 全量 #1） | 并行全量（只记录） | **515.71**（472.34 / 510.22） |
| 评审 r2 观测 | 并行全量 / 负载隔离 | **513.55** / 437.34、471.81 |

结论与口径：**700 ms 仅适用于串行/空载性能门禁**（1.52x 负载串行 worst 460.88、2.81x 空载 worst 249.44）；默认套件不 assert gap，只把值写进 JSON，因此并行 full-suite 的 472–619 ms 不会再造成误报。详见 `evidence/ui-gap-loaded-condition-r2a.json`。

真实规模合成负载（`FakeHostController.ReadySnapshot(N)`，`evidence/performance-scale-r4a.json`，2 预热 + 10 测量/负载，**只记录不入门槛**）：

| 负载 | 快照书目 | 冷启动 ms | p50 ms | p95 ms | max ms |
|---|---|---|---|---|---|
| n50 | 50 | 1242.23 | 283.82 | 1196.19 | 1196.19 |
| n200 | 200 | 1218.66 | 864.82 | 2617.77 | 2617.77 |
| n500 | 500 | 2639.19 | 1859.72 | 5668.25 | 5668.25 |

> 观察（不伪造 PASS）：真实规模下 p95 明显超过 1000 ms（n50 已 1196 ms）。AC-R4a-3 对规模负载只要求**记录** p50/p95；该差距作为 R4b/后续的规模性能 residual 记录。

## 6. AC-R4a-4（AC8 证据与治理）

- 门禁：`tools/governance/check.ps1` **PASS（3 warnings，既有预算/Task 数提示）**（含 `-TaskPath doc/tasks/FEA-07.md`）；`tools/governance/verify_pins.ps1` **PIN AUDIT: PASS (all 18)**（0 pin）。输出见 `logs/governance.log`。
- `doc/tasks/FEA-07.md` **append-only** 回填 AC2/AC6/AC8 before/after（AC1/AC3/AC4 留给 R4b），三条 NA 只在 AC5 行写一次；r1/r2 注记追加在回填节；历史 Review/证据字节未改。
- `doc/tasks/FEA-07-RESIDUAL-2.md`：扩域说明 + r1/r2 返修表 + `Residual / 待接线（L-R4a-1）` + `Canonical Evidence` + `Resource Manifest`；卡面 `status` 未改（DSH closeout 落）。
- **Canonical Evidence 归因（r2 R2-002）**：r2 触及的实现/测试文件 commit 填 `a03a6794a`；r1 后未再改的填 `bacf6c307`（如 `DraftOwnershipWindowTests.cs`）；首轮未再改的填 `85207730e`；证据文件填 `-` + 工作树 sha256（全表 0 mismatch）。
- 未改：`doc/plan/**`、`doc/contracts/**`、18 pins、`src/**` 其它文件、`Switching/**` 事务逻辑、`AppearanceCoordinator`/`FrontendSelector`/组合根、`*.axaml`、`*.csproj`、`tools/e2e/**`、`scripts/**`。
- 全量后 `git checkout -- verification/FEA-09`（零 diff）。

## 7. pytest（r2 R2-009）

- `pytest tests -q` = **3394 passed / 1 failed / 10 skipped**；唯一失败是**既有 flaky** `test_plugin_sandbox.py::test_sandbox_job_kills_grandchildren`（插件沙箱子进程断言），**隔离复跑该文件 16 passed**。
- 本卡**零 Python 改动**：`git diff --name-only bf4207d4a..HEAD -- tests/ src/` 为空、`git status --porcelain -- tests/ src/` 为空（2026-11-08 复核）。
- 处置：该 flaky 不在本卡范围（属插件沙箱测试的时序敏感性），登记为环境/既有 flaky 证据，不影响 AC-R4a-1…4；证据见 `logs/pytest-r2.txt`。

## 8. 变异自检（判别力，7 组）

见 `mutation-selfcheck.md`：① owner 冲突恒 Owned → 5 RED；② 窗口插 Start/Dispose → 3 RED；③ UI gap 心跳固定 500 ms（r1 400 ms 门槛）→ 650.4 ms RED（历史）；④ 单次 p95 → `Expected: 3, Actual: 1` RED；⑤（r1）删除构造即注册角色 → transfer-before-claim RED；⑥（r2）gap 断言改回默认套件 → **并行全量 RED：619.0 ms > 400**（P1 成因证据）；⑦（r2）p95 门槛方向改反 → 默认套件 RED（667.0 ms）。全部复原 sha256 MATCH；⑥ 按要求不作复绿要求。

## 9. 文件清单

| 文件 | 内容 |
|---|---|
| `README.md` | 本索引 |
| `RESOURCE-MANIFEST.json` | v1 Resource Manifest（worktree/evidence/temp/test-fixture/user-data/tracked-side-effect/tool） |
| `evidence/performance-baseline-r4a.json` | 默认套件 AC6：3 轮 p50/p95/max/冷启动/UI gap（记录）/内存/句柄 + 中位 + `p95Passed` |
| `evidence/performance-scale-r4a.json` | AC6 真实规模 N∈{50,200,500} 的 p50/p95（记录） |
| `evidence/perf-gate-r2a.json` + `perf-gate-round{1,2,3}.json` | 专用串行性能门禁 3 轮：gap/p95 分布 + `p95Passed`/`gapPassed`/`passed` + verdict |
| `evidence/ui-gap-calibration-r4a.json` + `ui-gap-calibration-round{1,2,3}.json` | raw 定标（不断言 gap）+ 每轮原始 metrics |
| `evidence/ui-gap-loaded-condition-r2a.json` | 负载敏感性汇总（空载/负载串行/并行全量/变异观测/评审观测） |
| `evidence/fullrun-recorded-gap-metrics-r2a.json` | 并行全量运行中默认套件记录的 gap（472.34/510.22/515.71） |
| `evidence/loaded-fullrun-gap-metrics-r2a.json` | 变异 ⑥ 同轮记录的 gap（491.75/457.55/619.00） |
| `tools/verify-fea07-perf.ps1` | 专用串行性能门禁运行器（`NEWMANGA_FEA07_PERF=1`，落盘 JSON/日志） |
| `tools/calibrate-ui-gap.ps1` | raw 定标运行器（不套 gap 断言，保存每轮原始 metrics） |
| `logs/directed-presentation-tests.log` | 定向套件 72/0/0 |
| `logs/app-tests.log` | App 套件 816/0/8 |
| `logs/full-solution-tests.log`、`full-solution-tests-run2.log` | 全量两次 1779/0/103 |
| `logs/perf-gate.log` + `perf-gate-round{1,2,3}.log` | 专用门禁汇总 + 每轮原始输出 |
| `logs/ui-gap-calibration.log` + `ui-gap-round{1,2,3}.log` | 定标汇总 + 每轮原始输出 |
| `logs/governance.log` | `check.ps1`（含 `-TaskPath doc/tasks/FEA-07.md`）+ `verify_pins.ps1` |
| `logs/pytest-r2.txt` | pytest 证据与零 Python diff 复核 |
| `logs/mutation-gap-default-full-run-r2a.log` | 变异 ⑥ 满载失败原始日志 |
| `logs/full-solution-first-run-cross-assembly-race.txt`、`full-solution-r1-flake-hit-test.txt` | 环境注意项 1/2 原始摘录 |
| `logs/gates-lead.log`、`gates-lead-final.log` | Lead 复核时点门禁运行（历史字节，保留） |
| `mutation-selfcheck.md` | 7 组变异 + sha256 + 复原/复绿 |

## 10. 复现（隔离、不触真实数据）

```powershell
# 定向 / App / 全量（默认门禁；gated 性能门禁用例自动 skip + reason）
dotnet test apps/desktop-avalonia/tests/NewManga.Presentation.Avalonia.Tests/NewManga.Presentation.Avalonia.Tests.csproj -c Release
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj -c Release
dotnet test apps/desktop-avalonia/NewManga.sln -c Release

# 专用串行性能门禁（不在默认门禁内）
pwsh -NoProfile -File verification/FEA-07-RESIDUAL-2/tools/verify-fea07-perf.ps1 -Rounds 3

# raw gap 定标（只记录，不断言）
pwsh -NoProfile -File verification/FEA-07-RESIDUAL-2/tools/calibrate-ui-gap.ps1 -Rounds 3

# 默认套件性能证据（写入本目录 evidence/）
$env:NEWMANGA_FEA07_METRICS_PATH       = "$PWD/verification/FEA-07-RESIDUAL-2/evidence/performance-baseline-r4a.json"
$env:NEWMANGA_FEA07_SCALE_METRICS_PATH = "$PWD/verification/FEA-07-RESIDUAL-2/evidence/performance-scale-r4a.json"
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj -c Release --filter "FullyQualifiedName~PerformanceBaselineTests"

# 治理门禁
pwsh -NoProfile -File tools/governance/check.ps1
pwsh -NoProfile -File tools/governance/verify_pins.ps1

# 全量后恢复既有副作用
git checkout -- verification/FEA-09
```
