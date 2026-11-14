# FEA11-RECOVERY-ROOT-PATH-1 证据：恢复路径把 registry root 当容器

基线 `c68a67216`。承接 `MINT-FAILURE-DIAG-1` 暴露的 `UnauthorizedAccessException`。

## 1. 真实调用链（实测堆栈）

```
DescribeContainer
  ← IssueLockedAsync
  ← IssueAsync
  ← IssueForRecoveryAsync
  ← SourceOperationCoordinator.MintRecoveryGrantsAsync   ← 恢复路径
  ← SourceOperationCoordinator.AcknowledgeAsync
  ← HostRuntime.<StartInternalAsync>g__SourceOperationCompletionAsync
  ← HostCommandDispatcher.InvokeHostControlAsync
```

**不是测试直接调的** —— 是 Host 在 `AcknowledgeAsync` 时的**恢复授权**路径。

## 2. 根因（产品缺陷 P2）

`apps/desktop-avalonia/src/NewManga.Host/Sources/SourceOperationCoordinator.cs`
（`MintRecoveryGrantsAsync`）：

```csharp
var roots = live.Roots
    .Where(root => root.Readable)
    .Select(root => root.Root)
    .ToArray();
if (roots.Length == 0) throw new SourceAccessException("SOURCE_REGISTRY_UNAVAILABLE");
// R-r2-03: exactly one readable root, otherwise the source path would be guessed.
if (roots.Length != 1) throw new SourceAccessException("SOURCE_ACCESS_DENIED");
var readsCoordinator = reads ?? throw new SourceAccessException("CORE_UNAVAILABLE");
var grantId = await readsCoordinator
    .IssueForRecoveryAsync(
        baseline.RegistryId,
        live.Generation,
        roots[0],          // <-- REGISTRY ROOT（允许访问的根目录）
        sourceKind,        // <-- Core 权威的容器类型，实测为 "zip"
        material.SourceId,
        ...);
```

**`roots[0]` 是"注册表允许访问的根目录"，不是"容器文件路径"。**

- 当 `sourceKind == "folder"` 时，root 恰好就是容器，**碰巧成立**；
- 当 `sourceKind` 是 `zip`/`cbz`/`pdf`/`image` 时，root **是目录**，`IssueLockedAsync` 却按容器处理
  → `DescribeContainer(目录)` → `FileStream` 打开目录 → `UnauthorizedAccessException`
  →（修复前被兜底）`SOURCE_ENTRY_MISSING`。

**代码注释本身就点出了风险**（"otherwise the source path would be guessed"），
但"恰好一个 root"**并不能**让 root 等于容器文件 —— 限制数量解决不了语义错位。

## 3. 为什么这是产品缺陷而不是测试问题

测试传的是 `newZip`（文件），`registry.Register("fea11-r4a", [root])` 注册的是 root 目录 ——
**两者本就不同**，且这是**合法用法**（注册根目录 + 访问其下的具体容器）。
产品在**恢复**时却丢掉了原始容器路径、改用 root。

## 4. 正确方向（未实施，需裁决）

恢复时应使用**记录下来的容器路径**，而不是 registry root。候选来源：
1. journal entry 里若已记录容器路径 → 直接用它（首选，最贴近"恢复"语义）；
2. 从 `material`（plan materialization）里取容器路径；
3. 若确实没有权威来源，应 **typed 拒绝**（如 `SOURCE_PLAN_UNAVAILABLE`）而不是**猜一个目录**。

**不得**用"把 `roots[0]` 当路径但只在 `sourceKind=="folder"` 时用"这种补丁 —— 那会把 zip 类恢复全部拒掉，
是另一种静默降级。

## 5. 影响面（已确认与未确认）

- **已确认**：`Fea11Residual4AIpcTests.ProductionDispatcherFullSyncChain_NewKeyOldDigestConserved` 因此失败。
- **未确认**：其它走 `AcknowledgeAsync` 恢复路径的 source_kind（zip/cbz/pdf/image）是否同样受害 ——
  需按 sourceKind 逐个复跑，**本卡未做**。

## 6. 处置

**登记为产品缺陷 `E-9`（P2）**，不修（需 DSH 裁决恢复路径的权威来源）。
带 opt-in 三类基线仍 **12 passed / 1 failed**；条件 3 仍不判 MET。
