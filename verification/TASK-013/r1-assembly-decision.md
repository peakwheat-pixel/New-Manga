# TASK-013 R-1 生产装配范围裁决

## 固定信息

- Task：TASK-013
- 生产 Pipeline seam 集成提交：`49c72fdf4d347be70636770c366c146650888ef4`
- R-1 集成提交：`734d5b39a3185bf612276dada6b089b55c9e574d`
- R-1 固定 base：`7c889cff531ef412d7774263e85f1d43e3c2ed7a`
- R-1 reviewed_head：`7f3be549d97d2b9858867f2e7f7f861e0542342e`
- 原实现 base：`46646d5`
- reviewed_head：`da1daf11e65fdc80f20450bec1f5e87234b826c7`
- Owner：Codex
- Reviewer：DeepSeek Harness
- 状态：`DONE`（独立 Review approved，已按 §6.6 集成并完成主线复验）

## 裁决

R-1 作为独立最小生产装配切片批准登记，不并入 TASK-013 的已审实现，也不释放 TASK-015 或其他冻结 Task。生产 Pipeline seam 已由 `49c72fdf` 提供；本轮由 Codex 在独立白名单内完成 `src/bootstrap/app.py` 的生产 `WorkbenchViewModel` 装配，并按 §6.6 以 `734d5b3` 集成。Workbench 通过真实 SQLite、真实 Chapter→Book 查询、Managed Copy 原图路径和 `setContextProperty("workbenchViewModel", ...)` 接入生产入口。

拟议完整路径：

- `G:/CODEX/New Manga/src/bootstrap/app.py`
- `G:/CODEX/New Manga/tests/core/test_bootstrap.py`
- `G:/CODEX/New Manga/verification/TASK-013/**`
- `G:/CODEX/New Manga/doc/00_INDEX.md`
- `G:/CODEX/New Manga/doc/12_ROADMAP.md`
- `G:/CODEX/New Manga/doc/STATUS.md`
- `G:/CODEX/New Manga/doc/tasks/README.md`

## Seam 核实

| 依赖 | 生产事实 | 结论 |
|---|---|---|
| page catalog | `SqliteLibraryRepository.list_pages(chapter_id)` | READY |
| region catalog | `SqliteRegionRepository.list_regions/get_region` | READY |
| manual translation | `RegionEditingService.save_manual_translation` | READY |
| navigation | `NavigationViewModel` | READY |
| pipeline catalog | `SqliteTargetCatalog` 提供真实层级查询与 Revision/Lock guard | READY |
| pipeline store/snapshot/executor | `SqlitePipelineStore`、`SqliteSnapshotProvider`、`ProductionStepExecutor` 已由本轮集成 | READY |

因此不得在 `assemble_services` 中用内存/确定性对象伪造生产 `WorkbenchViewModel`。本轮已按该约束建立并注入 `workbenchViewModel`，并验证真实 Chapter→Book/页面/Region 查询；未硬编码 book id，未绕过 Managed Copy 或源文件只读路径。

## 接线验收门槛

1. `PipelineService` 使用真实 `TargetCatalog`、`PipelineStore`、`SnapshotProvider` 和 StepExecutor，禁止 InMemory 默认值进入生产入口。
2. `assemble_services` 构造真实页面/Region/人工编辑依赖，`assemble_engine` 注入 `workbenchViewModel`；无 Schema、共享 Port、依赖清单或 TASK-012 实现改动。
3. Windows 默认 Qt（不设 offscreen）完成入口 smoke、WorkBench/UI 与全量回归；passed/skipped 分列并逐项记录 skip 原因。
4. 验证源文件只读、Managed Copy 与真实 Chapter→Book 查询链，确认失败路径不写 Page。
