# FEA-07-RESIDUAL-2 变异自检（AC-R4a-1/2/3 判别力）

- 时点：2026-11-08（Asia/Shanghai），实现 head `85207730e`（base `0a39a78f0`）；①②③④ 于首轮交付时执行，⑤ 于 r1 返修时追加
- 环境：Windows 11 / .NET 9 / Avalonia headless（`Avalonia.Headless.XUnit`）
- 方法：对最终源码逐个注入单点变异 → 跑对应测试断言 RED → 复原（①–④ `git checkout --`；⑤ 备份副本覆盖）→ 记录 sha256 前后一致 → 复绿
- 纪律：变异只用于判别力自检，不进入交付提交；复原后 `git status --porcelain` 为空

## 汇总

| # | 目标 AC | 变异点 | 判别断言（测试） | 结果 | 复原 sha256（pre == post） |
|---|---|---|---|---|---|
| ① | AC-R4a-1 | `DraftOwnershipRegistry.TryClaim`：跨窗口 owner 冲突恒判 `Granted`/可编辑（改写 owner，不再 typed ReadOnly） | `DraftOwnershipRegistryTests.SameKeyFromSecondOsWindow_IsReadOnlyWithTypedDenial`、`ConcurrentClaims_ProduceExactlyOneOwner`、`SameWindowPanels_ShareOneDraftIdWithoutRejection`、`ExplicitTransfer_MovesOwnershipExclusivelyAndKeepsTheDraftId`、`WindowBrokerDraftForwardingTests.SharedRegistryAcrossBrokers_KeepsASingleOwner` | **RED**：失败 5 / 通过 60 / 总计 65 | `bd927657bd533e5442996f300210345ccaf9dd220757eff655e277dffe12b05f` |
| ② | AC-R4a-2 | `PresentationWindow` 构造插 `StartAsync`、`Closing` 插 `DisposeAsync`（窗口生命周期拥有 Host 的错误实现） | `PresentationWindowHostLifecycleTests`（3 个：逐项计数、切换、判别性 Start/Dispose 抛错） | **RED**：失败 3 / 通过 0 / 总计 3 | `5fef0cbd8588f7dbed48fe386ffb333c74fa407d3612b695c2d2fa5865ef839c` |
| ③ | AC-R4a-3（gap） | UI 线程心跳 interval 5 ms → **固定 500 ms 延迟** | `PerformanceBaselineTests.HotSwitch_P95MedianOfThreeIndependentRuns_StaysWithinTheFrozenW5Budget` 的 `uiThreadSchedulingGapMs` 断言 | **RED**：`ui thread scheduling gap 650.4 ms exceeds the calibrated 400 ms budget` | `5d90f84f502cc3e6b210a0211fd458923e69b4af9d1c9ab7c9ee767e7c62be21` |
| ④ | AC-R4a-3（三次中位） | `IndependentRuns = 3` → **1**（单次运行 gate，去掉中位数口径） | 同测试内的冻结形状断言（`Assert.Equal(3, runs.Count)`） | **RED**：`Assert.Equal() Failure: Expected: 3, Actual: 1` | `5d90f84f502cc3e6b210a0211fd458923e69b4af9d1c9ab7c9ee767e7c62be21` |
| ⑤ | AC-R4a-1（r1 P2-003：transfer-before-claim） | 删除 `DraftOwnershipScope` 构造时的 `RememberWindow(WindowToken, Role)`（角色只在首次 claim 时才登记） | `DraftOwnershipScopeTests.ScopeRegistersItsRoleAtConstruction_SoAFloatingTransferTargetIsRefusedBeforeAnyClaim`（+ 同组 2 个）、`DraftOwnershipWindowTests.TransferToAConstructedButUnclaimedFloatingWindow_IsRefusedAndTheOwnerKeepsEdit` | **RED**：纯测试失败 3 / 通过 68 / 总计 71；窗口级 `Expected: FloatingWindowReadOnly / Actual: UnknownWindow` | `c84cac5a41fd146eb9b96570f0656e5354d27442796d3b47af9a31b1383dac67` |

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

- 五个变异全部复原；每次复原后 `Get-FileHash -Algorithm SHA256` 与变异前一致（见表 pre==post）；`git status --porcelain` 为空。
- 复原后复绿：`NewManga.Presentation.Avalonia.Tests` **71/0/0**；`NewManga.App.Tests` **816/0/7**；全量 `NewManga.sln` **1778/0/102**（`logs/full-solution-tests.log`）。
- 行尾说明（不影响内容）：变异用 `edit` 工具写入的行是 LF，而工作区文件为 CRLF；首次复原时 `git checkout` 触发了行尾规范化，`git diff HEAD` 为空（内容与提交字节一致）。上表 sha256 是**规范化后的 canonical 工作区字节**。
- ⑤ 的复原用「备份副本覆盖 + 触达 LastWriteTime」而不是 `git checkout`（r1 返修尚未提交，`git checkout` 会退回未返修的 HEAD 字节）；覆盖后 sha256 与变异前一致，并显式刷新 mtime 以避免 MSBuild 增量跳过旧 DLL。

## 判别力结论

- AC-R4a-1：owner 冲突判定（唯一 owner / typed ReadOnly / 并发单 owner）可被单点变异检出（①）；**构造即注册角色**与 transfer-before-claim 拒绝可被检出（⑤）。
- AC-R4a-2：窗口生命周期对 Host 的零调用（Start/Dispose）可被单点变异检出（②），且异常脚本证明判别不是"计数器碰巧为 0"。
- AC-R4a-3：`uiThreadSchedulingGapMs` 与"三次 p95 中位数"口径各自可被检出（③④）；1000 ms 门槛本身未被修改。

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

RED 的三条纯测试：`ScopeRegistersItsRoleAtConstruction_SoAFloatingTransferTargetIsRefusedBeforeAnyClaim`（`Expected: FloatingWindowReadOnly, Actual: UnknownWindow`）、`EnsureWritable_RejectsAStaleResultAfterATransfer`、`TransferToAConstructedButUnclaimedInspectorWindow_IsAllowedAndKeepsIdentity`（两者 `Expected: Transferred, Actual: ReadOnly`）。
