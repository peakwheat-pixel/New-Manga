# FEA-07-RESIDUAL-2（R4a）证据索引

| 项 | 值 |
|---|---|
| 卡 | `doc/tasks/FEA-07-RESIDUAL-2.md`（FEA-07 收口 A，headless，**0 pin**） |
| base_commit | `0a39a78f0` |
| 实现提交（代码+测试） | `85207730e` |
| 文档/证据提交（首轮） | `9ec6b196b` |
| r1 返修提交 | 见 `git log --oneline -- verification/FEA-07-RESIDUAL-2`（`fix(fea-07-residual-2): r1 返修…`） |
| 作用域扩域 | DSH 2026-11-08 批准**单文件**：`apps/desktop-avalonia/src/NewManga.App/Views/Presentation/PresentationWindow.cs`，改动 **+26/−5（净 +21 行，纯加法，无功能删除）**；未改 `App.axaml.cs`/组合根/契约/pins |
| Review 状态 | 独立 Review r1 = **approved**（P0=0/P1=0/**P2=4**/P3=12）；本目录含 r1 返修（P2-001/002/003/004、P3-001/008/010） |
| 环境 | Windows 11（`Microsoft Windows NT 10.0.26300.0`）/ .NET `9.0.11` / Avalonia 11.3.22 headless / x64 |

## 1. 结论边界（不夸大）

- **达成**：AC-R4a-1（AC2 窗口层 draft owner）、AC-R4a-2（AC2 生命周期）、AC-R4a-3（AC6 指标与规模）、AC-R4a-4（AC8 证据与治理）。
- **不在本卡**：AC1/AC3/AC4 → `FEA-07-RESIDUAL-3`（R4b，gated/进程）。
- **NA（只登记一次，在 `doc/tasks/FEA-07.md` 的 AC5 行）**：AC5 原生双屏/拔屏/DPI 矩阵、AC1 原生 IME、AC2 真实双屏 broker 落位 = `NOT_APPLICABLE`（用户 2026-11-08 授权豁免；保留 `NOT_RUN`，不写成 PASS）。
- **P2-002 / L-R4a-1（r1 明示）**：AC2 的**窗口层机制**已 MET；但**生产组合根**当前只有一个 `PresentationWindow`，**未注入共享 `DraftOwnershipRegistry`**，`WindowBroker.RegisterSecondary` **零调用**，**无 Floating 生产实例** ⇒ 跨窗口（真实双屏/浮窗）场景尚未在生产路径可见。跨窗接线（组合根注入 + Floating/Inspector 真实窗口 + 多窗口生命周期）由**多窗口功能卡**承接（见卡内「Residual / 待接线（L-R4a-1）」）；本目录不写「跨窗已生产可用」。
- 本卡不写「FEA-07 完全实现 / 全部 limitation 关闭 / 可发布」；像素/UI 观感不作 AC 判据。
- 契约口径：只**引用** C-13 SC-D03（`doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md:55-66`）与冻结解释（`doc/tasks/FEA-07-RESIDUAL-2.md:45`），**不复述规则句**；`doc/plan/**`、`doc/contracts/**`、18 pins 零 diff。

## 2. 测试汇总（实跑，r1 返修后）

| 套件 | 命令 | 结果 | 证据 |
|---|---|---|---|
| 定向 | `dotnet test apps/desktop-avalonia/tests/NewManga.Presentation.Avalonia.Tests/NewManga.Presentation.Avalonia.Tests.csproj -c Release` | **71 / 0 / 0**（基线 38 → +33） | `logs/directed-presentation-tests.log` |
| App | `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj -c Release` | **816 / 0 / 7**（基线 804 → +12） | `logs/app-tests.log` |
| 全量 | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` | **1778 / 0 / 102**（基线 1733/0/102 → +45 通过，skip 不变） | `logs/full-solution-tests.log` |
| pytest | 本卡零 Python 改动 → 未跑（不适用） | — | — |

全量逐程序集（r1 后）：Appearance 21、Presentation.Avalonia 71、ThemeEngine 253、DesignSystem 117、ApplicationCore 31、Host 302/71 skip、CoreClient 167/24 skip、App 816/7 skip；全部 `失败: 0`。

**环境注意项（诚实记录；两例均为既有/无关用例，本卡未修改它们）**：

1. 首轮全量（工作树含未提交改动时）出现既有跨程序集 race：`FluentResidual2VisualEvidenceTests.Captures_Residual2_Visual_Inventory_Only_When_Opted_In` 断言「自身 23 s 窗口内 `verification/**` 的 `git status` 不变」，而 `NewManga.CoreClient.Tests.WireLogSourceRedactionTests` 并发重写 `verification/FEA-09/logs/wire-redacted.ndjson`。摘录：`logs/full-solution-first-run-cross-assembly-race.txt`。
2. r1 返修后一次全量运行中 `FluentR2ReworkTests.R3001_OtherControlPress_Wheel_AndShellHandledKey_WakeHiddenBarsAndRenewDeadline(Reduce/All/0)` 命中一次 hit-test 断言（满负载下命中 `ReaderPage` 而非目标 Button）；同 head 单独跑 App 套件 816/0/7，随后全量 1778/0/102 PASS。摘录：`logs/full-solution-r1-flake-hit-test.txt`。

两例均与 draft owner/生命周期/性能断言无关；每次全量后按纪律 `git checkout -- verification/FEA-09`（零 diff）。

## 3. AC-R4a-1（AC2 窗口层 draft owner）

- 新增 `apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/Windows/DraftOwnershipRegistry.cs`：`(SessionId, RegionId)` owner store（线程安全、结果不可变、`DraftWriteRejectedException` typed 写入拒绝），含 `DraftOwnershipScope`（窗口身份 + 角色，**构造即注册角色**）；`WindowBroker` 薄转发 `TryClaimDraft`/`ReleaseDraft`/`RequestDraftTransfer`（现有注册 API 不变）；`PresentationWindow` 暴露 `DraftOwnership`（`WindowToken`），`Floating` 构造强制 `CanEdit=false`。
- 机制覆盖（定向 33 = registry 23 + scope 5 + broker 转发 5）：同 key 跨 **OS 窗口**唯一 owner；第二个窗口 `ReadOnly` + typed `OtherWindowOwner`；`Floating` 恒只读（首个 claim 也只读）；**同窗口内浮动面板共享同一 `DraftId`（`Shared`，不拒绝）**；显式转移互斥且幂等（`Transferred` → 当前 owner 重复 = `Retained`+可编辑；**旧 owner 重复 = `Retained`+`CanEdit=false`+`NotOwner`**）；**未注册 target 的 transfer typed 拒绝（`UnknownWindow`，不猜角色）**；`Release` 后可再 claim（新 `DraftId`）；64 并发 claim 恰 1 owner；跨 Session 同 Region 只读；**`EnsureWritable` 绑窗口身份 + 实时 owner（他人/过期 result → typed `NotOwner`）**。
- 窗口级（`tests/NewManga.App.Tests/DraftOwnershipWindowTests.cs`，8 个）：暴露 + 唯一 `WindowToken`、Floating 只读、第二窗口只读、同窗口面板共享、**只读写入 typed 拒绝且 `FakeHostController.DraftWriteLog` 为空（Host 零写入）**、窗口间显式转移、**`Floating` 仅构造未 claim 时 transfer 被拒且原 owner 保留编辑**（r1 transfer-before-claim）、窗口 `Release` 后 reclaim。
- 规则引用：C-13 SC-D03 `doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md:55-66` + 冻结解释 `doc/tasks/FEA-07-RESIDUAL-2.md:45`（**只引用不复述**，`FEA-C10-r1.md:83`）。

## 4. AC-R4a-2（AC2 生命周期）

`tests/NewManga.App.Tests/PresentationWindowHostLifecycleTests.cs`（3 个），逐项断言（不是聚合）：

- `CloseAndRebuild_LeaveEveryHostLifecycleItemUnchanged`：关闭 → 重建 → 切换前后 `StartCalls` / `StartRequests` / `LifecycleLog` / `DisposeCalls` 逐项不变，`Changed` 事件零触发。
- `SwitchingFrontends_DoesNotStartOrDisposeTheHost`：4 次切换后四项仍不变。
- `WindowLifecycle_IsDiscriminatingAgainstHostStartAndDisposeCalls`：脚本化 `StartException`/`DisposeException` 未被消费（两个异常对象仍在），证明判别不是「计数器碰巧为 0」。

`FakeHostController` 仅测试侧加法：`DisposeCalls` / `DisposeException` / `DraftWriteLog`（默认行为不变）。

## 5. AC-R4a-3（AC6 指标与规模）

门槛未改：**热切换 p95 ≤ 1000 ms（W-5 冻结）**；断言 = **3 次独立运行 p95 中位数**（每轮 4 预热 + 20 测量），并固定形状（3 轮、中位 = 排序第 2 个 p95）。

`evidence/performance-baseline-r4a.json`（`passed=true`）：

| 轮 | 冷启动 ms（单独记录，不入门槛） | p50 ms | p95 ms | max ms | `uiThreadSchedulingGapMs` |
|---|---|---|---|---|---|
| 1 | 275.93 | 139.19 | 378.86 | 390.95 | 192.14 |
| 2 | 291.51 | 151.48 | 392.71 | 407.37 | 208.56 |
| 3 | 284.12 | 135.12 | 373.40 | 467.05 | 202.88 |
| **中位** | — | **139.19** | **378.86** | — | worst **208.56** |

**`uiThreadSchedulingGapMs` 定标（r1 P2-004，`evidence/ui-gap-calibration-r4a.json`）**：`tools/calibrate-ui-gap.ps1` 3 轮独立重跑（每轮 3 次子运行 × [4 预热 + 20 测量]，5 ms 心跳）：

| 定标轮 | 子运行 gap ms | worst gap ms | 中位 p95 ms | passed |
|---|---|---|---|---|
| 1 | 249.44 / 207.34 / 199.00 | 249.44 | 401.28 | true |
| 2 | 223.30 / 197.60 / 202.19 | 223.30 | 387.99 | true |
| 3 | 227.85 / 203.81 / 206.42 | 227.85 | 389.47 | true |

→ **budget 400 ms**（worst 249.44 ms，余量 **37.64% ≥ 10%**，verdict `KEEP 400 ms`）。历史 ad-hoc 观测 215.28 / 232.90 ms 只作历史注记，本文件才是提交的定标证据。

真实规模合成负载（`FakeHostController.ReadySnapshot(N)`，`evidence/performance-scale-r4a.json`，2 预热 + 10 测量/负载，**只记录不入门槛**，AC 口径）：

| 负载 | 快照书目 | 冷启动 ms | p50 ms | p95 ms | max ms |
|---|---|---|---|---|---|
| n50 | 50 | 1242.23 | 283.82 | 1196.19 | 1196.19 |
| n200 | 200 | 1218.66 | 864.82 | 2617.77 | 2617.77 |
| n500 | 500 | 2639.19 | 1859.72 | 5668.25 | 5668.25 |

> 观察（不伪造 PASS）：真实规模下 p95 明显超过 1000 ms（n50 已 1196 ms）。AC-R4a-3 对规模负载只要求**记录** p50/p95，W-5 门槛断言对象仍是上面的「3 次独立运行中位数」口径；该差距作为 R4b/后续的规模性能 residual 记录。
- 冷启动首次切换单独记录（275.93/291.51/284.12 ms），从不进入 p95 门槛。

## 6. AC-R4a-4（AC8 证据与治理）

- 门禁：`tools/governance/check.ps1` **PASS（3 warnings，均为既有预算/Task 数提示）**；`tools/governance/verify_pins.ps1` **PIN AUDIT: PASS (all 18)**（0 pin）。输出见 `logs/governance.log`。
- `doc/tasks/FEA-07.md` **append-only** 回填 AC2/AC6/AC8 的 before/after（AC1/AC3/AC4 留给 R4b），三条 NA 只在 AC5 行写一次；r1 返修注记追加在回填节末尾；历史 Review/证据字节未改。
- `doc/tasks/FEA-07-RESIDUAL-2.md`：DSH 扩域说明 + r1 返修表 + `## Residual / 待接线（L-R4a-1）` + `## Canonical Evidence` + `## Resource Manifest`；卡面 `status` 未改（由 DSH closeout 落盘）。
- 未改：`doc/plan/**`、`doc/contracts/**`、18 pins、`src/**` 其它文件、`Switching/**` 事务逻辑、`AppearanceCoordinator`/`FrontendSelector`/组合根、`*.axaml`、`*.csproj`、`tools/e2e/**`、`scripts/**`。
- 全量运行后 `git checkout -- verification/FEA-09`（零 diff）。

## 7. 变异自检（判别力，5 组）

见 `mutation-selfcheck.md`：① owner 冲突恒 Owned → 5 RED；② 窗口插 Start/Dispose → 3 RED；③ UI gap 心跳固定 500 ms → `650.4 ms > 400 ms` RED；④ 单次 p95（去掉三次中位）→ `Expected: 3, Actual: 1` RED；⑤（r1）删除构造即注册角色 → transfer-before-claim `Expected: FloatingWindowReadOnly, Actual: UnknownWindow` RED（纯测试 3/71 失败）。全部复原 sha256 MATCH + 复绿。

## 8. 文件清单

| 文件 | 内容 |
|---|---|
| `README.md` | 本索引 |
| `RESOURCE-MANIFEST.json` | v1 Resource Manifest（worktree/evidence/temp/test-fixture/user-data/tracked-side-effect/tool） |
| `evidence/performance-baseline-r4a.json` | AC6 热切换：3 轮 p50/p95/max/冷启动/UI gap/内存/句柄 + 中位 + passed |
| `evidence/performance-scale-r4a.json` | AC6 真实规模 N∈{50,200,500} 的 p50/p95（记录） |
| `evidence/ui-gap-calibration-r4a.json` | r1 P2-004：`uiThreadSchedulingGapMs` 3 轮定标（worst 249.44 ms，余量 37.64%，KEEP 400 ms） |
| `tools/calibrate-ui-gap.ps1` | 定标脚本（3 轮独立重跑 + 落盘 JSON/日志） |
| `logs/directed-presentation-tests.log` | 定向套件 71/0/0 |
| `logs/app-tests.log` | App 套件 816/0/7 |
| `logs/full-solution-tests.log` | 全量 1778/0/102 |
| `logs/performance-run.log` | 基线/规模证据生成运行（含 ITestOutputHelper 输出） |
| `logs/ui-gap-calibration.log` / `ui-gap-round{1,2,3}.log` | 定标汇总 + 每轮原始 dotnet test 输出 |
| `logs/governance.log` | `check.ps1` + `verify_pins.ps1` |
| `logs/full-solution-first-run-cross-assembly-race.txt` | 环境注意项 1 原始摘录 |
| `logs/full-solution-r1-flake-hit-test.txt` | 环境注意项 2 原始摘录 |
| `logs/gates-lead.log` | Lead r1 复核时点的门禁运行（HEAD `9ec6b196b`，返修前），保留为历史门禁证据 |
| `mutation-selfcheck.md` | 5 组变异 + sha256 + 复原/复绿 |

## 9. 复现（隔离、不触真实数据）

```powershell
# 定向 / App / 全量
dotnet test apps/desktop-avalonia/tests/NewManga.Presentation.Avalonia.Tests/NewManga.Presentation.Avalonia.Tests.csproj -c Release
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj -c Release
dotnet test apps/desktop-avalonia/NewManga.sln -c Release

# 性能证据（写入本目录 evidence/）
$env:NEWMANGA_FEA07_METRICS_PATH       = "$PWD/verification/FEA-07-RESIDUAL-2/evidence/performance-baseline-r4a.json"
$env:NEWMANGA_FEA07_SCALE_METRICS_PATH = "$PWD/verification/FEA-07-RESIDUAL-2/evidence/performance-scale-r4a.json"
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj -c Release --filter "FullyQualifiedName~PerformanceBaselineTests"

# UI gap 3 轮定标
pwsh -NoProfile -File verification/FEA-07-RESIDUAL-2/tools/calibrate-ui-gap.ps1

# 治理门禁
pwsh -NoProfile -File tools/governance/check.ps1
pwsh -NoProfile -File tools/governance/verify_pins.ps1

# 全量后恢复既有副作用
git checkout -- verification/FEA-09
```
