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

## 返修轮已关闭的 finding（供 closeout 对照）

- **R3-001（P1）**：`page_order` 为 1-based（`src/application/tasks/projection.py:206-207` fallback `index + 1`；
  `tests/library/test_import_images.py:42` `(1, 1)`）——映射边界归一为 1-based 显示序，矩阵与页面条均不再 `+1`；
  判别测试 `R3001_OneBasedPageOrder_IsRenderedVerbatim_InMatrixAndPageStrip`。
- **R3-002（P1）**：webtoon 末页/单页/第二页失败时彻底清空第二页（Source/可见性/bytes/bitmap/尺寸）；
  判别测试 `R3002_WebtoonLastPage_ClearsStaleSecondaryImage`。
- **R3-005（P2）**：A1 断言方向改为 `focusSet ⊆ visited`（全覆盖）；
  判别测试 `AC5_TabTraversal_LibraryReaderSettings_CoversFocusableSet_NoConsecutiveRepeats`。
- **R3-007（P2）**：章节切换/终态释放 Run 跟踪并轮换意图键，「开始处理」可再次使用；
  判别测试 `R3007_AfterRunLifecycle_ChapterSwitchAndTerminalState_AllowANewRun`。
- **R3-013（P2）**：证据测试在无 `.git` / 无任务卡的导出目录**真 Skip**（保留零写入前提）。
  契约：`AvaloniaFactAttribute` 是 sealed（不能继承后条件 Skip），动态 `SkipException` 在本仓库
  Avalonia+xunit 链路会被记为失败（已实测）。实现改用自定义 `[GitBackedAvaloniaFact]`：复刻
  Avalonia 的 `XunitTestCaseDiscoverer` 接线（`AvaloniaUIFactDiscoverer` → 在 Avalonia Dispatcher 上运行），
  在特性构造期做前置判定并设置 `FactAttribute.Skip`；仓库根以**测试程序集 Location** 向上定位
  （discovery 期 `AppContext.BaseDirectory` 不是测试输出目录，已验证）。探针：把 `.git` 判定改为 false →
  该测试变为 `已跳过`；复原后 20/20 通过。
  见 `FluentResidual3VisualEvidenceTests` 的 `GitBackedAvaloniaFactAttribute` /
  `FluentResidual3EvidencePreconditions`。

## 复现

- 定向：`dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj -c Release`
- 证据（opt-in）：`$env:NEWMANGA_CAPTURE_RESIDUAL3_PNGS='1'` 后运行 `FluentResidual3VisualEvidenceTests`
