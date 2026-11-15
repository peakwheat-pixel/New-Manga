# E9-FEASIBILITY-2：解锁 E-9 的可行性评估（先读代码）

基线 `1984eaf6e`。

## 1. 代码事实（读 `SourceOperationCoordinator.MintRecoveryGrantsAsync`，`:191` 起）

```csharp
var roots = live.Roots
    .Where(root => root.Readable)
    .Select(root => root.Root)
    .ToArray();
if (roots.Length == 0) throw new SourceAccessException("SOURCE_REGISTRY_UNAVAILABLE");
// R-r2-03: exactly one readable root, otherwise the source path would be guessed.
```

**它把 `registry.Roots`（注册时登记的根）直接当作"容器路径"用于 `Authorize(...)`。**

| 源类型 | registry root | 实际容器 | 是否一致 |
|---|---|---|---|
| **folder** | `D:\manga\book1` | `D:\manga\book1` | ✅ |
| **zip / cbz / pdf** | `D:\manga\book1.zip`（**就是容器本身**） | `D:\manga\book1.zip` | ✅ **一致** |

> **★★ 本节原先写的是"zip/cbz 源的 registry root 是父目录 `D:\manga`" —— 这个前提是错的，已更正。**
>
> **决定性证据**（`SourceImportModels.cs:800-809`）：
>
> ```csharp
> private async Task<IReadOnlyList<string>> IssueGrantsAsync(ReferenceImportSource source, ...)
> {
>     var path = Path.GetFullPath(source.Path);
>     var authorization = await FindOrRegisterRootAsync(path, cancellationToken);  // registry root = path
>     var kind = source.IsFolder ? "folder" : KindOf(path);
>     return new[] { await _sources.IssueAsync(
>         authorization.RegistryId, authorization.Generation, path, kind, ...) }; // sourcePath = 同一个 path
> ```
>
> 且 `SourceImportModels.cs:243` 的 `RegisterRoot(path)` 写的 `roots` 数组**只有 `path` 一项**。
>
> ⇒ **registry root 与 sourcePath 是同一个值，就是用户选中的那个路径**（zip 源即容器文件）。
>
> **我的错误**：写本节时我**没读 `RegisterRoot` 的实现和它的调用方**，凭"根 = 目录"的字面直觉下了结论。
> ZCode 在裁决中直接指出并给出 `SourceImportModels.cs:243-252` / `Fea11HostAuthIpcTests.cs:340-342` 的依据。

**⇒ 两层后果**：

1. **功能缺失**：对非 folder 源，recovery/ACK 会拿到"父目录"而不是"容器" ⇒ 现有实现在
   `source_kind != "folder"` 时**直接 typed 拒绝**（`SOURCE_PLAN_UNAVAILABLE`），这是**正确的自我保护**
   （宁可拒绝，不猜路径）。
2. **★ 安全问题**：**如果**放宽这个拒绝、直接用 `roots[0]` 去 `Authorize`，
   授权范围会变成**整个父目录**（`D:\manga`），而不是用户指定的那个 zip。
   **这会让 recovery 后的读权限比 apply 时更宽** —— 这是**提权**，不是等价恢复。

**⇒ 更正后：E-9 不是"缺少路径映射"，而是 `MintRecoveryGrantsAsync` 在**还没看 `roots[0]` 是文件还是目录**之前，
就按"root 必是目录"的假设做了 folder-only 拒绝 —— 属**过度保守**，不是"正确的自我保护"。

**路径就在 `roots[0]` 里**，不需要任何新的持久化。

## 2. 方案评估

### 方案 A：mint-time 持久化 `registry_id → container_path`

- **做法**：`IssueLockedAsync` 时（那里**确实持有** `sourcePath`）把 `(registryId, generation, containerPath)`
  写进 Host 私有的 DPAPI 状态文件；`MintRecoveryGrantsAsync` 查表拿路径。
- **改动面**：`SourceOperationCoordinator`（写 + 读）、一个新的小持久化类、相关测试。
- **契约影响**：**无**。C-17 管的是 journal / plan / payload / wire 帧；**Host 私有状态文件不在契约面内**。
- **安全影响**：**改善** —— 授权精确到**文件**而非**父目录**。
- **风险**：状态文件与 journal 可能不一致（例如 registry 被 revoke 后状态文件仍在）⇒
  需要以 registry 为准做**存在性与 revoke 校验**（现有代码已经校验 `RevokedAt`）。

### 方案 B：从 Core 读回容器路径

- **做法**：让 Core 在 `source_get_sync_plan_materialized` 里多返回 `container_path`。
- **契约影响**：**需要 UNFREEZE C-17**（响应形状变化）。
- **额外风险**：C-17 §5.2 **禁止绝对路径**出现在契约面上 ⇒ **大概率不可行**。

### 方案 C：在 RecoveryGrant / journal 里加字段

- **契约影响**：**需要 UNFREEZE**，且 journal 是**闭合形状**（ZCode 裁决已明确），
  且**绝对路径禁止**（§5.2）⇒ **不可行**。

### 方案 D：不做，改造 4 个被挡测试并永久记录限制

- **成本**：0 改动，4 个测试改为断言 typed 拒绝（已有 3 个改造完）。
- **代价**：非 folder 源的 **crash 恢复 / ACK 后发布** 永远不可用（用户可见的功能缺口）。

## 3. 我的建议

**方案 A 已被 ZCode 否决**（裁决见 `doc/reviews/E9-UNLOCK-ADJUDICATION-zcode-2026-11-15.md`）：
它要解决的是一个**不存在的问题**（路径并不缺失），反而引入新状态文件与 registry 的漂移面。

**ZCode 裁决采用方案 E**：在 `MintRecoveryGrantsAsync` 加一个**判别分支** ——
`sourceKind == "folder"` 走现状；非 folder 且 `File.Exists(roots[0])` 时**以 `roots[0]` 为 `sourcePath`** 重铸；
若 `Directory.Exists(roots[0])` 而 kind 是容器型，则维持 `SOURCE_PLAN_UNAVAILABLE` typed 拒绝（fail-closed 不变）。
**契约零改动**。

## 4. 影响面（E-9 当前成本）

被 E-9 挡住的测试共 **4 个**：

| 测试 | 状态 |
|---|---|
| `Fea11Residual4AIpcTests.ProductionDispatcherFullSyncChain_NewKeyOldDigestConserved` | 已改造 |
| `Fea11HostAuthIpcTests.Ack_SendsAFreshAuthorization_...` | 已改造 |
| `Fea11HostAuthIpcTests.Recovery_UsesAFreshAuthorization_...` | 已改造 |
| `Fea11HostAuthIpcTests.CrashPoint_Recover` | **未改造**（本轮发现） |

另有真实驱动 `crash-ack.ps1` 无法达到 `CRASH_POINT=SATISFIED`。
