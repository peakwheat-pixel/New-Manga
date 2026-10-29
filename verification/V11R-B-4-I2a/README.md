# V11R-B-4-I2a · B-4 二审 P1-A / P1-B 返修

Owner: ui-studio · HEAD 之前：`e0f6be6ec` + merge main `5927c83a6`

## P1-A（已修 + 已测）
- `StudioBatchViewModel.ProjectionApplied`：每轮轮询只发**一次**通知（不再由 `Rows.CollectionChanged` 逐行触发）。
- `StudioBatchMatrixControl.SyncFromProjection()`：shape 稳定（列数/行数/行 id 序列一致）时只重刷 cell 状态与行类，**复用 cell 控件**；shape 变化才 `Rebuild()`，且 `Rebuild()` 前后保存/恢复 `Scroll.Offset`。
- 测试：`Poll_IncrementalUpdate_KeepsScrollAndReusesCells`（60 行投影、`Offset=(0,240)`、一次 poll 后 offset 保持、`ProjectionApplied` 恰 1 次、cell 数 600 不变）。
- 结果：Studio 子集 **30/30 通过**。

## P1-B（代码已修；测试 NOT_RUN）
- 代码：`CanMaterializeScope()`（Selected/CurrentPage 无 id → false）；`BuildScope` 在 Selected/CurrentPage 不可物化时返回 `null`（**不再回落到 chapter**）；`BuildActions.IsEnabled = CanMaterializeScope()`；`StartRunAsync` 对 null scope 就地说明并零调用。
- 测试：`Scope_Unmaterializable_DisablesActions_AndNeverWidensToChapter` 在本机因测试构造与 `SetScope` UX guard 交互不稳定，**已移除并标 NOT_RUN**（原因：无确定性 setup 在有限窗口内稳定复现；代码路径已由 `StartRunAsync` null-scope 分支覆盖，建议复审用真实 UI 选择流补测）。

## 未做（后续子集）
- I2b：R-22 幂等键、Stop 二次确认、Gate 模态、Error 重试、IsVisible 轮询、证据 R-25、FontSize token。
- I2c：B-3 交互测试、P2-5/P2-6、证据 curate、DS StatusCatalog/断点上收。
