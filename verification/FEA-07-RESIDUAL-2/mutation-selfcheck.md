# FEA-07-RESIDUAL-2 变异自检（AC-R4a-1/2/3 判别力）

- 时点：2026-11-08（Asia/Shanghai），实现 head `85207730e`（base `0a39a78f0`）；①②③④ 首轮交付、⑤ r1 返修、⑥⑦ r2 返修（代码提交 `a03a6794a`）
- 环境：Windows 11 / .NET 9 / Avalonia headless（`Avalonia.Headless.XUnit`）
- 方法：对最终源码逐个注入单点变异 → 跑对应测试断言 RED → 复原（①–④ `git checkout --`；⑤⑥⑦ 备份副本覆盖）→ 记录 sha256 前后一致 → 复绿
- 纪律：变异只用于判别力自检，不进入交付提交；复原后 `git status --porcelain` 为空

## 汇总

| # | 目标 AC | 变异点 | 判别断言（测试） | 结果 | 复原 sha256（pre == post） |
|---|---|---|---|---|---|
| ① | AC-R4a-1 | `DraftOwnershipRegistry.TryClaim`：跨窗口 owner 冲突恒判 `Granted`/可编辑（改写 owner，不再 typed ReadOnly） | `DraftOwnershipRegistryTests.SameKeyFromSecondOsWindow_IsReadOnlyWithTypedDenial`、`ConcurrentClaims_ProduceExactlyOneOwner`、`SameWindowPanels_ShareOneDraftIdWithoutRejection`、`ExplicitTransfer_MovesOwnershipExclusivelyAndKeepsTheDraftId`、`WindowBrokerDraftForwardingTests.SharedRegistryAcrossBrokers_KeepsASingleOwner` | **RED**：失败 5 / 通过 60 / 总计 65 | `bd927657bd533e5442996f300210345ccaf9dd220757eff655e277dffe12b05f` |
| ② | AC-R4a-2 | `PresentationWindow` 构造插 `StartAsync`、`Closing` 插 `DisposeAsync`（窗口生命周期拥有 Host 的错误实现） | `PresentationWindowHostLifecycleTests`（3 个：逐项计数、切换、判别性 Start/Dispose 抛错） | **RED**：失败 3 / 通过 0 / 总计 3 | `5fef0cbd8588f7dbed48fe386ffb333c74fa407d3612b695c2d2fa5865ef839c` |
| ③ | AC-R4a-3（gap） | UI 线程心跳 interval 5 ms → **固定 500 ms 延迟** | `PerformanceBaselineTests.HotSwitch_P95MedianOfThreeIndependentRuns_StaysWithinTheFrozenW5Budget` 的 `uiThreadSchedulingGapMs` 断言 | **RED**：`ui thread scheduling gap 650.4 ms exceeds the calibrated 400 ms budget` | `5d90f84f502cc3e6b210a0211fd458923e69b4af9d1c9ab7c9ee767e7c62be21` |
| ④ | AC-R4a-3（三次中位） | `IndependentRuns = 3` → **1**（单次运行 gate，去掉中位数口径） | 同测试内的冻结形状断言（`Assert.Equal(3, runs.Count)`） | **RED**：`Assert.Equal() Failure: Expected: 3, Actual: 1` | `5d90f84f502cc3e6b210a0211fd458923e69b4af9d1c9ab7c9ee767e7c62be21` |
| ⑤ | AC-R4a-1（r1 P2-003：transfer-before-claim） | 删除 `DraftOwnershipScope` 构造时的 `RememberWindow(WindowToken, Role)`（角色只在首次 claim 时才登记） | `DraftOwnershipScopeTests.ScopeRegistersItsRoleAtConstruction_SoAFloatingTransferTargetIsRefusedBeforeAnyClaim`（+ 同组 2 个）、`DraftOwnershipWindowTests.TransferToAConstructedButUnclaimedFloatingWindow_IsRefusedAndTheOwnerKeepsEdit` | **RED**：纯测试失败 3 / 通过 68 / 总计 71；窗口级 `Expected: FloatingWindowReadOnly / Actual: UnknownWindow` | `c84cac5a41fd146eb9b96570f0656e5354d27442796d3b47af9a31b1383dac67` |
| ⑥ | AC-R4a-3（r2 R2-001：gap 断言不得在默认套件） | 把 r1 样式 `uiThreadSchedulingGapMs ≤ 400 ms` 断言加回默认套件，跑**并行全量** | 默认套件 `HotSwitch_…` 的 gap 断言（负载下不稳定） | **RED**（满载）：`ui thread scheduling gap 619.0 ms exceeds the calibrated 400 ms budget`；同轮 gap 491.75 / 457.55 / 619.00；全量 815 passed / 1 failed / 8 skipped | `f73ac3a6f5f44211956b4c527ab0b5f7e449db6f4be56f7e7613ba1027d45752` |
| ⑦ | AC-R4a-3（W-5 门槛活性） | p95 门槛方向改反（断言 `medianP95 > 1000`，即"门槛改成 >1000"） | 默认套件 `HotSwitch_…` 的 p95 断言 | **RED**：`hot switch median p95 667.0 ms exceeds the frozen W-5 budget 1000 ms`（runs 558.7/667.0/675.4） | `f73ac3a6f5f44211956b4c527ab0b5f7e449db6f4be56f7e7613ba1027d45752` |

## 逐项命令与证据

### ① owner 冲突恒 Owned（AC-R4a-1）

```powershell
dotnet test apps/desktop-avalonia/tests/NewManga.Presentation.Avalonia.Tests/NewManga.Presentation.Avalonia.Tests.csproj -c Release --nologo
# -> 失败! - 失败: 5，通过: 60，总计: 65
git checkout -- apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/Windows/DraftOwnershipRegistry.cs
```

失败测试：`SameKeyFromSecondOsWindow_IsReadOnlyWithTypedDenial`、`ConcurrentClaims_ProduceExactlyOneOwner`（64 个 claim 全部变 owner）、`SameWindowPanels_ShareOneDraftIdWithoutRejection`、`ExplicitTransfer_MovesOwnershipExclusivelyAndKeepsTheDraftId`、`SharedRegistryAcrossBrokers_KeepsASingleOwner`。

### ② 窗口插入 Start/Dispose（AC-R4a-2）

```powershell
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj -c Release --nologo --filter "FullyQualifiedName~PresentationWindowHostLifecycleTests"
# -> 失败! - 失败: 3，通过: 0，总计: 3
git checkout -- apps/desktop-avalonia/src/NewManga.App/Views/Presentation/PresentationWindow.cs
```

三个用例全部 RED：`CloseAndRebuild_LeaveEveryHostLifecycleItemUnchanged`（`StartCalls`/`DisposeCalls` 变化）、`SwitchingFrontends_DoesNotStartOrDisposeTheHost`、`WindowLifecycle_IsDiscriminatingAgainstHostStartAndDisposeCalls`（脚本化 Start/Dispose 异常被消费）。

### ③ UI gap 心跳 500 ms（AC-R4a-3）

```powershell
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj -c Release --nologo --filter "FullyQualifiedName~HotSwitch_P95MedianOfThreeIndependentRuns"
# -> 失败! - 失败: 1，总计: 1（ui thread scheduling gap 650.4 ms > 400 ms）
git checkout -- apps/desktop-avalonia/tests/NewManga.App.Tests/PerformanceBaselineTests.cs
```

### ④ p95 单次（AC-R4a-3）

```powershell
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj -c Release --nologo --filter "FullyQualifiedName~HotSwitch_P95MedianOfThreeIndependentRuns"
# -> 失败! - 失败: 1，总计: 1（Expected: 3, Actual: 1）
git checkout -- apps/desktop-avalonia/tests/NewManga.App.Tests/PerformanceBaselineTests.cs
```

## 复原与复绿

- 七个变异全部复原；每次复原后 `Get-FileHash -Algorithm SHA256` 与变异前一致（见表 pre==post）；`git status --porcelain` 为空（交付提交前）。
- r2 后复绿：`NewManga.Presentation.Avalonia.Tests` **72/0/0**；`NewManga.App.Tests` **816/0/8**（gated 性能门禁用例默认 skip）；全量 `NewManga.sln` **1779/0/103**（`logs/full-solution-tests.log` 与 `logs/full-solution-tests-run2.log`，跑 2 次均 0 failed）；专用串行性能门禁 **3 轮 PASS**（`evidence/perf-gate-r2a.json`）。
- 行尾说明（不影响内容）：变异用 `edit` 工具写入的行是 LF，而工作区文件为 CRLF；`git checkout` 复原时触发行尾规范化，`git diff HEAD` 为空（内容与提交字节一致）。上表 sha256 是**规范化后的 canonical 工作区字节**。
- ⑤ 的复原用「备份副本覆盖 + 触达 LastWriteTime」而不是 `git checkout`（r1 返修尚未提交时，`git checkout` 会退回未返修的 HEAD 字节）；覆盖后 sha256 与变异前一致，并显式刷新 mtime 以避免 MSBuild 增量跳过旧 DLL。
- ⑥⑦ 的复原同样用「备份副本覆盖 + 触达 LastWriteTime」（r2 返修未提交时）。

## 判别力结论

- AC-R4a-1：owner 冲突判定（唯一 owner / typed ReadOnly / 并发单 owner）可被单点变异检出（①）；**构造即注册角色**与 transfer-before-claim 拒绝可被检出（⑤）。
- AC-R4a-2：窗口生命周期对 Host 的零调用（Start/Dispose）可被单点变异检出（②），且异常脚本证明判别不是"计数器碰巧为 0"。
- AC-R4a-3：三次 p95 中位数口径与 W-5 门槛可被检出（④⑦）；`uiThreadSchedulingGapMs` 的**默认套件断言**被证明在负载下不稳定（⑥，这是 r2 P1 的成因）；gap 断言自 r2 起只在专用串行门禁生效，门槛 700 ms 按串行负载分布定标（空载 worst 249.44、负载串行 worst 460.88、并行全量 619.00）。
- **历史说明**：③（固定 500 ms 心跳延迟 → 650.4 ms > 400 ms RED）是 r1 的 400 ms 门槛证据；r2 起门槛按负载方差重定标为 700 ms，故 500 ms 固定延迟不再被判 RED——这是有意的取舍（避免在负载波动的工作站上误报），已在 `evidence/ui-gap-loaded-condition-r2a.json` 记录。

## ⑤ 移除构造即注册角色（r1 新增；transfer-before-claim）

```powershell
# 变异：删除 DraftOwnershipScope 构造函数中的 _broker.Drafts.RememberWindow(windowToken, role);
dotnet test apps/desktop-avalonia/tests/NewManga.Presentation.Avalonia.Tests/NewManga.Presentation.Avalonia.Tests.csproj -c Release --nologo
# -> 失败! - 失败: 3，通过: 68，总计: 71
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj -c Release --nologo --filter "FullyQualifiedName~DraftOwnershipWindowTests.TransferToAConstructedButUnclaimedFloatingWindow"
# -> 失败! - 失败: 1，总计: 1（Expected: FloatingWindowReadOnly, Actual: UnknownWindow）

# 复原（备份副本覆盖后 sha256 与变异前一致）
Copy-Item $env:TEMP\r4a-registry-baseline.cs apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/Windows/DraftOwnershipRegistry.cs -Force
(Get-Item apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/Windows/DraftOwnershipRegistry.cs).LastWriteTime = Get-Date
# sha256 = c84cac5a41fd146eb9b96570f0656e5354d27442796d3b47af9a31b1383dac67（pre == post）
# 复绿：定向 71/0/0
```

RED 的三条纯测试：`ScopeRegistersItsRoleAtConstruction_SoAFloatingTransferTargetIsRefusedBeforeAnyClaim`（`Expected: FloatingWindowReadOnly, Actual: UnknownWindow`）、`EnsureWritable_RejectsAStaleResultAfterATransfer`、`TransferToAConstructedButUnclaimedFloatingWindow_IsRefusedAndTheOwnerKeepsEdit`（两者 `Expected: Transferred, Actual: ReadOnly`）。

## ⑥ gap 断言改回默认套件（r2 R2-001；记录满载不稳定证据，不作为复绿要求）

```powershell
# 变异：在默认套件 HotSwitch_… 的 p95 断言后加回 r1 样式 gap 断言（≤ 400 ms），然后跑并行全量
$env:NEWMANGA_FEA07_METRICS_PATH = "$env:TEMP\r2-mutation-gap-default-metrics.json"
dotnet test apps/desktop-avalonia/NewManga.sln -c Release --nologo
# -> 失败! - 失败: 1，通过: 815，已跳过: 8，总计: 824
#    ui thread scheduling gap 619.0 ms exceeds the calibrated 400 ms budget
#    同轮 recorded gap: 491.75 / 457.55 / 619.00 ms；medianP95 748.34 ms
# 复原（备份副本覆盖 + 触达 LastWriteTime）
Copy-Item $env:TEMP\r2-perf-baseline.cs apps/desktop-avalonia/tests/NewManga.App.Tests/PerformanceBaselineTests.cs -Force
(Get-Item apps/desktop-avalonia/tests/NewManga.App.Tests/PerformanceBaselineTests.cs).LastWriteTime = Get-Date
# sha256 = f73ac3a6f5f44211956b4c527ab0b5f7e449db6f4be56f7e7613ba1027d45752（pre == post）
```

满载失败原始日志：`logs/mutation-gap-default-full-run-r2a.log`；同轮 metrics：`evidence/loaded-fullrun-gap-metrics-r2a.json`。
结论：**这正是 r2 P1 的成因**——同一断言在并行 full-suite 下会因负载误报，所以它只能留在专用串行门禁。

## ⑦ p95 门槛方向改反（r2；证明 W-5 门槛仍带电）

```powershell
# 变异：默认套件 p95 断言由 "medianP95 <= 1000" 改为 "medianP95 > 1000"
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj -c Release --nologo --filter "FullyQualifiedName~HotSwitch_P95MedianOfThreeIndependentRuns"
# -> 失败! - 失败: 1，总计: 1
#    hot switch median p95 667.0 ms exceeds the frozen W-5 budget 1000 ms（runs 558.7 / 667.0 / 675.4）
# 复原同 ⑥（备份副本覆盖 + 触达 LastWriteTime），sha256 f73ac3a6…（pre == post），复绿
dotnet test ... --filter "FullyQualifiedName~HotSwitch_P95MedianOfThreeIndependentRuns"
# -> 已通过!（默认套件 1/0/0）
```
