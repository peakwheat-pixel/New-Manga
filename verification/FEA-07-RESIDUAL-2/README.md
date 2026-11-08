# FEA-07-RESIDUAL-2（R4a）证据索引

| 项 | 值 |
|---|---|
| 卡 | `doc/tasks/FEA-07-RESIDUAL-2.md`（FEA-07 收口 A，headless，**0 pin**） |
| base_commit | `0a39a78f0` |
| 实现提交（代码+测试） | `85207730e` |
| 文档/证据提交 | 见同分支紧随其后的 `docs(fea-07-residual-2): …` 提交（`git log --oneline -- verification/FEA-07-RESIDUAL-2`） |
| 作用域扩域 | DSH 2026-11-08 批准 **单文件**：`apps/desktop-avalonia/src/NewManga.App/Views/Presentation/PresentationWindow.cs`（+21 行纯加法；未改 `App.axaml.cs`/组合根/契约/pins） |
| 环境 | Windows 11（`Microsoft Windows NT 10.0.26300.0`）/ .NET `9.0.11` / Avalonia 11.3.22 headless / x64 |

## 1. 结论边界（不夸大）

- **达成**：AC-R4a-1（AC2 窗口层 draft owner）、AC-R4a-2（AC2 生命周期）、AC-R4a-3（AC6 指标与规模）、AC-R4a-4（AC8 证据与治理）。
- **不在本卡**：AC1/AC3/AC4 → `FEA-07-RESIDUAL-3`（R4b，gated/进程）。
- **NA（只登记一次，在 `doc/tasks/FEA-07.md` 的 AC5 行）**：AC5 原生双屏/拔屏/DPI 矩阵、AC1 原生 IME、AC2 真实双屏 broker 落位 = `NOT_APPLICABLE`（用户 2026-11-08 授权豁免；保留 `NOT_RUN`，不写成 PASS）。
- 本卡不写「FEA-07 完全实现 / 全部 limitation 关闭 / 可发布」；像素/UI 观感不作 AC 判据。
- 契约口径：只**引用** C-13 SC-D03（`doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md:55-66`）与冻结解释（`doc/tasks/FEA-07-RESIDUAL-2.md:45`），**不复述规则句**；`doc/plan/**`、`doc/contracts/**`、18 pins 零 diff。

## 2. 测试汇总（实跑）

| 套件 | 命令 | 结果 | 证据 |
|---|---|---|---|
| 定向 | `dotnet test apps/desktop-avalonia/tests/NewManga.Presentation.Avalonia.Tests/NewManga.Presentation.Avalonia.Tests.csproj -c Release` | **65 / 0 / 0**（基线 38 → +27） | `logs/directed-presentation-tests.log` |
| App | `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj -c Release` | **815 / 0 / 7**（基线 804 → +11） | `logs/app-tests.log` |
| 全量 | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` | **1771 / 0 / 102**（基线 1733 / 0 / 102 → +38 通过，skip 不变） | `logs/full-solution-tests.log` |
| pytest | 本卡零 Python 改动 → 未跑（不适用） | — | — |

全量逐程序集：Appearance 21、Presentation.Avalonia 65、ThemeEngine 253、DesignSystem 117、ApplicationCore 31、Host 302/71 skip、CoreClient 167/24 skip、App 815/7 skip；全部 `失败: 0`。

**环境注意项（诚实记录）**：本卡首次全量运行（工作树含未提交改动、且与其它程序集并发）出现过 1 次既有跨程序集 race：`NewManga.App.Tests.FluentResidual2VisualEvidenceTests.Captures_Residual2_Visual_Inventory_Only_When_Opted_In` 断言「自身 23 s 运行窗口内 `verification/**` 的 `git status` 不变」，而 `NewManga.CoreClient.Tests.WireLogSourceRedactionTests` 会并发重写 `verification/FEA-09/logs/wire-redacted.ndjson`。该用例未被本卡修改；单独运行 App.Tests 为 815/0/7，随后干净工作树全量为 1771/0/102（均 PASS）。原样摘录见 `logs/full-solution-first-run-cross-assembly-race.txt`；全量运行后按纪律 `git checkout -- verification/FEA-09`。

## 3. AC-R4a-1（AC2 窗口层 draft owner）

- 新增 `apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/Windows/DraftOwnershipRegistry.cs`：`(SessionId, RegionId)` owner registry（线程安全、结果不可变、`DraftWriteRejectedException` typed 写入拒绝），含 `DraftOwnershipScope`（窗口级身份 + 角色）；`WindowBroker` 加薄转发 `TryClaimDraft`/`ReleaseDraft`/`RequestDraftTransfer`（现有注册 API 不变）；`PresentationWindow` 暴露 `DraftOwnership`（`WindowToken`）。
- 机械覆盖（定向 27 个新测试中的 22 + 5）：同 key 跨 **OS 窗口**唯一 owner；第二个窗口 `ReadOnly` + typed `OtherWindowOwner`；`Floating` 窗口构造强制 `CanEdit=false`（首个 claim 也只读）；**同窗口内浮动面板共享同一 `DraftId`（`Shared`，不拒绝）**；显式转移互斥且幂等（`Transferred` → `Retained`）；`Release` 后可再 claim（新 `DraftId`）；64 并发 claim 恰好 1 owner；跨 Session 同一 Region 默认只读（冻结解释 `:45`）。
- 窗口级（`tests/NewManga.App.Tests/DraftOwnershipWindowTests.cs`，7 个）：`PresentationWindow.DraftOwnership` 暴露与唯一 `WindowToken`、Floating 只读、第二个窗口只读、同窗口面板共享 `DraftId`、**只读窗口写入被 typed 拒绝且 `FakeHostController.DraftWriteLog` 为空（Host 零写入）**、窗口间显式转移、窗口 `Release` 后 reclaim。
- 测试名（定向）：`DraftOwnershipRegistryTests.*`（22）、`WindowBrokerDraftForwardingTests.*`（5）；窗口级：`DraftOwnershipWindowTests.*`（7）。

## 4. AC-R4a-2（AC2 生命周期）

- `tests/NewManga.App.Tests/PresentationWindowHostLifecycleTests.cs`（3 个），逐项断言（不是聚合）：
  - `CloseAndRebuild_LeaveEveryHostLifecycleItemUnchanged`：关闭 → 重建 → 切换前后 `StartCalls` / `StartRequests` / `LifecycleLog` / `DisposeCalls` 逐项不变，`Changed` 事件零触发。
  - `SwitchingFrontends_DoesNotStartOrDisposeTheHost`：4 次切换后四项仍不变。
  - `WindowLifecycle_IsDiscriminatingAgainstHostStartAndDisposeCalls`：脚本化 `StartException`/`DisposeException` 未被消费（两个异常对象仍在），证明判别不是「计数器碰巧为 0」。
- `FakeHostController` 仅加测试侧 `DisposeCalls` / `DisposeException` / `DraftWriteLog`（默认行为不变）。

## 5. AC-R4a-3（AC6 指标与规模）

门槛未改：**热切换 p95 ≤ 1000 ms（W-5 冻结）**。断言改为 **3 次独立运行的 p95 中位数**。

`evidence/performance-baseline-r4a.json`（Release，headless，4 预热 + 20 测量/轮）：

| 轮 | 冷启动 ms（单独记录，不入门槛） | p50 ms | p95 ms | max ms | `uiThreadSchedulingGapMs` |
|---|---|---|---|---|---|
| 1 | 275.93 | 139.19 | 378.86 | 390.95 | 192.14 |
| 2 | 291.51 | 151.48 | 392.71 | 407.37 | 208.56 |
| 3 | 284.12 | 135.12 | 373.40 | 467.05 | 202.88 |
| **中位** | — | **139.19** | **378.86** | — | worst **208.56** |

- `passed=true`：中位 p95 378.86 ms ≤ 1000 ms。
- 新增 `uiThreadSchedulingGapMs`（UI 线程心跳最大间隔，5 ms 心跳）：首轮定标 worst 215.28 ms、复核定标 232.90 ms → **写死阈值 400 ms**（1.7x 余量；AC 建议初值 250 ms 因仅 7% 余量未采用，原因写在 `PerformanceBaselineTests.cs` 常量注释）。证据轮 worst 208.56 ms ≤ 400 ms。
- 冻结形状断言：`runs.Count == 3`、`IndependentRuns == 3`、中位数 = 排序后第 2 个 p95（防止退回单次口径）。
- 真实规模合成负载（`FakeHostController.ReadySnapshot(N)`，`evidence/performance-scale-r4a.json`，2 预热 + 10 测量/负载，**只记录不入门槛**，AC 口径）：

| 负载 | 快照书目 | 冷启动 ms | p50 ms | p95 ms | max ms |
|---|---|---|---|---|---|
| n50 | 50 | 1242.23 | 283.82 | 1196.19 | 1196.19 |
| n200 | 200 | 1218.66 | 864.82 | 2617.77 | 2617.77 |
| n500 | 500 | 2639.19 | 1859.72 | 5668.25 | 5668.25 |

> 观察（不伪造 PASS）：真实规模下 p95 明显超过 1000 ms（n50 已 1196 ms）。AC-R4a-3 对规模负载只要求**记录** p50/p95，W-5 门槛断言对象仍是上面的「3 次独立运行中位数」口径；该差距作为 R4b/后续的规模性能 residual 记录，不在本卡写 PASS。
- 冷启动首次切换单独记录（275.93/291.51/284.12 ms），从不进入 p95 门槛。

## 6. AC-R4a-4（AC8 证据与治理）

- 门禁：`tools/governance/check.ps1` **PASS（3 warnings，均为既有预算/Task 数提示）**；`tools/governance/verify_pins.ps1` **PIN AUDIT: PASS (all 18)**（0 pin：本卡不改契约字节）。输出见 `logs/governance.log`。
- `doc/tasks/FEA-07.md` **append-only** 回填 AC2/AC6/AC8 的 before/after（AC1/AC3/AC4 留给 R4b），三条 NA 只在 AC5 行写一次；历史 Review/证据字节未改。
- `doc/tasks/FEA-07-RESIDUAL-2.md`：追加 DSH 扩域说明 + `## Evidence` + `## Resource Manifest`（引用本目录 `RESOURCE-MANIFEST.json`）；卡面 `status` 未改（由 DSH closeout 落盘）。
- 未改：`doc/plan/**`、`doc/contracts/**`、18 pins、`src/**` 其它文件、`Switching/**` 事务逻辑、`AppearanceCoordinator`/`FrontendSelector`/组合根、`*.axaml`、`*.csproj`、`tools/e2e/**`、`scripts/**`。
- 全量运行后 `git checkout -- verification/FEA-09`（`verification/FEA-09/logs/wire-redacted.ndjson` 已复原，零 diff）。

## 7. 变异自检（判别力，4 组）

见 `mutation-selfcheck.md`：① owner 冲突恒 Owned → 5 RED；② 窗口插 Start/Dispose → 3 RED；③ UI gap 心跳固定 500 ms → `650.4 ms > 400 ms` RED；④ 单次 p95（去掉三次中位）→ `Expected: 3, Actual: 1` RED。复原逐字节（sha256 pre==post）+ 复绿。

## 8. 文件清单

| 文件 | 内容 |
|---|---|
| `README.md` | 本索引 |
| `RESOURCE-MANIFEST.json` | v1 Resource Manifest（worktree/temp/user-data/tracked-side-effect） |
| `evidence/performance-baseline-r4a.json` | AC6 热切换：3 轮 p50/p95/max/冷启动/UI gap/内存/句柄 + 中位 + passed |
| `evidence/performance-scale-r4a.json` | AC6 真实规模 N∈{50,200,500} 的 p50/p95（记录） |
| `logs/directed-presentation-tests.log` | 定向套件 65/0/0 |
| `logs/app-tests.log` | App 套件 815/0/7 |
| `logs/full-solution-tests.log` | 全量 1771/0/102 |
| `logs/performance-run.log` | 基线/规模证据生成运行（含 ITestOutputHelper 输出） |
| `logs/governance.log` | `check.ps1` + `verify_pins.ps1` |
| `logs/full-solution-first-run-cross-assembly-race.txt` | 第 2 节环境注意项的原始摘录 |
| `mutation-selfcheck.md` | 4 组变异 + sha256 + 复原/复绿 |
