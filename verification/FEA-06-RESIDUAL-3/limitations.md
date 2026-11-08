# FEA-06-RESIDUAL-3 limitations（r1 返修登记）

> 本文件由实现者（`fea06-residual3-impl`）登记，只记录**实现侧已收窄的口径与 re-home 线索**；
> 权威记录是 `doc/tasks/FEA-06-RESIDUAL-3.md` 与 r1 Review 报告（`doc/reviews/FEA-06-RESIDUAL-3-r1.md`）。
> 本卡 `doc/**` 不可改，因此 limitation 在此留痕，供 closeout 引用。**本文件与 `visuals/**` 像素证据都不作 AC 判据。**

| id | finding | 本卡处置 | re-home |
|---|---|---|---|
| **L-R3-1** | R3-003：webtoon「连续页」口径过宽 | AC-3 口径**收窄为「当前页 + 后继页（两页连续）」**；未实现全章长滚动 / 窗口化加载 / 滚动窗口回收 | `FEA-06-RESIDUAL-5`（未建，先登记） |
| **L-R3-2** | R3-004：DesignSystem `ReaderPage` 的 automation peer `GetAutomationControlType()==None` | **不扩域改 DesignSystem**（不在本卡 allowed_paths）；测试内改为**显式类型白名单常量 + 注释**登记例外（该控件已具名「当前漫画页面」）；其余 Tab 落点必须命中白名单 | DesignSystem 回修（peer 类型/ControlTheme） |
| **L-R3-3** | R3-009：DesignSystem `BatchMatrix : ScrollViewer` 无自己的 ControlTheme → 永远不可滚动 | 保留 App 侧 `FluentBatchMatrix : ScrollViewer`（`StyleKeyOverride => typeof(ScrollViewer)`）规避，样式仍用 `fluent-batch-matrix`；DS 原控件未改 | DesignSystem 回修（补 ControlTheme / StyleKeyOverride） |
| **L-R3-4** | R3-008 / R3-011 / R3-012 | 按 DSH/r1 裁决登记 limitation，本卡**不返修**、实现侧无对应改动；细节与口径以 r1 Review 报告与 closeout 为准 | 见 `doc/reviews/FEA-06-RESIDUAL-3-r1.md`（由 DSH 落盘） |
| **L-R3-5** | r2-P3：证据测试的 self-skip 依赖 Avalonia **内部类型名** | `[GitBackedAvaloniaFact]` 的 `[XunitTestCaseDiscoverer("Avalonia.Headless.XUnit.AvaloniaUIFactDiscoverer", "Avalonia.Headless.XUnit")]` 是字符串接线，引用 Avalonia 包内部类型；Avalonia 升级（改名/挪命名空间/discoverer 实现变化）会让该属性在 discovery 期失败或退化为不可 Skip。升级 Avalonia 时必须复核该类型仍存在，并重跑证据测试的「非 Git 导出 → skipped」探针 | 证据测试自身（`FluentResidual3VisualEvidenceTests`）；Avalonia 升级时复核 |
| **L-R3-6** | r2-P3-4：`Views/ImportExportPanels.cs:247-252` 章节标签 off-by-one（`第 {Chapter.SortOrder + 1} 章`） | **未改**：该文件是 `Views/ImportExportPanels.cs`（不在本卡 allowed_paths：只允许 `Views/Fluent/**`）。核查结果：章节 `sort_order` 也是 **1-based**（`src/application/library/service.py` `create_chapter` 的 `next_order = max(import_order)+1`，`sort_order = import_order = next_order`），因此该标签与已修的页面标签属同类缺陷 | re-home（Fluent 导入/导出面板的章节标签；需允许 `Views/ImportExportPanels.cs` 的后续卡） |

## 返修轮已关闭的 finding（供 closeout 对照）

- **R3-001（P1）**：`page_order` 为 1-based（`src/application/tasks/projection.py:206-207` fallback `index + 1`；
  `tests/library/test_import_images.py:42` `(1, 1)`）——映射边界归一为 1-based 显示序，矩阵与页面条均不再 `+1`；
  判别测试 `R3001_OneBasedPageOrder_IsRenderedVerbatim_InMatrixAndPageStrip`（另含
  `P3001_ShelfPreviewThumbnails_RenderOneBasedPageOrder` 书架预览缩略图）。
- **R3-002（P1）**：webtoon 末页/单页/第二页失败时彻底清空第二页（Source/可见性/bytes/bitmap/尺寸）；
  判别测试 `R3002_WebtoonLastPage_ClearsStaleSecondaryImage`。
- **R3-005（P2）**：A1 断言方向改为 `focusSet ⊆ visited`（全覆盖）；
  判别测试 `AC5_TabTraversal_LibraryReaderSettings_CoversFocusableSet_NoConsecutiveRepeats`。
- **R3-007（P2）**：章节切换/终态释放 Run 跟踪并轮换意图键，「开始处理」可再次使用；
  判别测试 `R3007_AfterSuccessfulRun_ChapterSwitch_AllowsANewRun`、`R3007_TerminalProjection_ReleasesRunTracking_AndAllowsANewRun`、
  `P3009_SameChapterRefresh_KeepsRunTrackingAndPolling`（同章节刷新不清跟踪）。
- **r2-P1（P1，R3-007 修正）**：终态集合逐字对齐 Core `_TERMINAL_STATUSES`
  （`src/application/tasks/projection.py:163-171`：completed / completed_with_failures / failed / cancelled；
  `interrupted` 是可恢复态，见 `:432-435`）；终态但仍有 UI 动作可用时（`completed_with_failures` +
  `can_retry_failed`，`:437-438`）**保留 RunId 只停表**，避免「继续/重试失败」enabled-but-inert；
  控制/重试成功后恢复轮询并跟踪子 Run（`new_run_id`）。判别测试
  `R3008_CompletedWithFailures_RetryFailedSendsOneFrame`、`R3008_Interrupted_ContinueSendsOneFrame`。
- **R3-013（P2）**：证据测试在无 `.git` / 无任务卡的导出目录**真 Skip**（保留零写入前提）。
  契约：`AvaloniaFactAttribute` 是 sealed（不能继承后条件 Skip），动态 `SkipException` 在本仓库
  Avalonia+xunit 链路会被记为失败（已实测）。实现改用自定义 `[GitBackedAvaloniaFact]`：复刻
  Avalonia 的 `XunitTestCaseDiscoverer` 接线（`AvaloniaUIFactDiscoverer` → 在 Avalonia Dispatcher 上运行），
  在特性构造期做前置判定并设置 `FactAttribute.Skip`；仓库根以**测试程序集 Location** 向上定位
  （discovery 期 `AppContext.BaseDirectory` 不是测试输出目录，已验证）。探针：把 `.git` 判定改为 false →
  该测试变为 `已跳过`；复原后 21/21 通过（见 L-R3-5 的升级复核要求）。
  见 `FluentResidual3VisualEvidenceTests` 的 `GitBackedAvaloniaFactAttribute` /
  `FluentResidual3EvidencePreconditions`。

## 复现

- 定向：`dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj -c Release`
- 证据（opt-in）：`$env:NEWMANGA_CAPTURE_RESIDUAL3_PNGS='1'` 后运行 `FluentResidual3VisualEvidenceTests`
