# E9-RECOVERY-PATH-FIX-1 证据

基线 `d3bd09751`。修 E-9（P2）。**本卡只做了"诚实的失败"，没有让它成功**。

## 1. 查询结论：没有任何权威容器路径

| 来源 | 有容器路径？ |
|---|---|
| `JournalEntry`（16 个字段） | **无** |
| `AuthorizationJson` → `ReadAuthorizationBaselines`（只解析 registry_id / identity_digest / generation） | **无** |
| `SourceSyncPlanMaterialization`（Format/PlanId/PlanDigest/Kind/SourceId/VersionId/ContentDigest/Entries/ReferenceSetDigest/State/ExpiresAt） | **无** |

⇒ 恢复路径**没有任何权威容器路径可用**。

## 2. 改动（typed 拒绝）

`SourceOperationCoordinator.MintRecoveryGrantsAsync`，`roots` 校验后插入：

```csharp
if (!string.Equals(sourceKind, "folder", StringComparison.Ordinal))
{
    throw new SourceAccessException("SOURCE_PLAN_UNAVAILABLE");
}
```

理由（已写进注释）：registry root 是**授权边界**，不是容器文件；`roots[0]` 只在 `folder` 时碰巧等价。
没有权威路径就 typed 拒绝，**不猜目录** —— 猜到的是谎话。

## 3. 效果（错误码更准确，但**测试仍失败**）

| 项 | 前 | 后 |
|---|---|---|
| `Fea11Residual4AIpcTests.ProductionDispatcherFullSyncChain_…` | `SOURCE_ENTRY_MISSING` + inner `UnauthorizedAccessException` | **`SOURCE_PLAN_UNAVAILABLE`** |
| 该测试结论 | FAIL | **FAIL（仍）** |

**本卡没有让它转绿**：它期望"恢复成功"，而无权威路径时成功不可能。本卡把
"误导性的文件系统错误"变成"明确的计划不可用"。

## 4. 真正修复需要什么（未做，需 UNFREEZE）

要在持久化位置**记录容器路径**（journal 的 AuthorizationJson 增记 container_path，或 plan materialization 加字段）。
**这是契约变更**，需 DSH 裁决载体与兼容性。

## 5. 回归

无夹具 `Host.Tests`：**325 / 0 / 74 / 399**（与改动前逐项一致，**0 failed**）。
`Fea11RunGrantIpcTests:137` 的 `SOURCE_ENTRY_MISSING` 走 `AuthorizeRunAsync` + `MapMintFailure`，不受影响。

## 6. 未做

- **无**专门的 typed 拒绝判别测试（`MintRecoveryGrantsAsync` 是 private，构造成本高）——
  目前只由 `Fea11Residual4AIpcTests` 的失败形态**间接**覆盖，**如实标注**。
- 未实测 `sourceKind=="folder"` 的恢复是否仍正常（不受新分支影响，但未跑）。
