# Gate 条件 3 覆盖矩阵（2026-11-15）

**Task**：`GATE3-COVERAGE-MATRIX`。**基线**：`d86f185ca`。
**条件原文**：「补齐**可安全执行的**完整 GUI / Core / Host 关键流程与 Avalonia TestHost；所有 blocked/skipped 项继续保留原结果」（`audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md`）。

## 0. 方法与证据强度（先说边界）

- 本矩阵**不是**测试文件目录的复述。每格给出：状态 → 代表测试 → 该测试**实际断言了什么**。
- 证据强度分三级，**逐格标注**：
  - **【核对】** 我逐行读过该测试的断言。
  - **【摘要】** 我读过该类/方法的 summary 与方法名，但**未**逐行核对断言 —— 计分时不得当作已证实。
  - **【未覆盖】** 仓库内找不到针对该流程的测试。
- 规模（实测，本基线）：

| 层 | 数字 | 说明 |
|---|---|---|
| `NewManga.App.Tests` | **947 passed / 0 failed / 11 skipped / 958** | 无夹具全量；11 skip 为历史既有 |
| 其中 `[AvaloniaFact]` 文件 | **61 个** | headless 可跑，无需 sidecar |
| 其中 `[HostSidecarFact]` | **仅 2 个**（均在 `ChapterCreationTests.cs`） | 需真实 sidecar |
| `NewManga.Host.Tests` | 321 / 0 / **74 skipped** | 74 skip 即 E-2 阻塞面 |
| `NewManga.CoreClient.Tests` | 186 / 0 / **26 skipped** | 26 skip 即 E-2 阻塞面 |
| 可见测试方法（App.Tests 粗计，不含 Theory 多 case） | 825 | — |

**关键结构性事实**：GUI 层（App.Tests）**几乎不依赖 sidecar** —— 只有 2 个测试类需要。E-2 的阻塞主要落在
Host.Tests（74）与 CoreClient.Tests（26）的集成层。

## 1. 四页 × 关键流程矩阵

图例：✅有覆盖　⚠️部分覆盖　❌NOT_RUN　— 不适用。
每格末尾的 【核对】/【摘要】/【未覆盖】是**该格最弱证据**的强度。

| 流程 \ 页面 | 书架 (Library) | 工作台 (Workbench) | 阅读器 (Reader) | 设置 (Settings) |
|---|---|---|---|---|
| **进入与空态** | ✅ `ShelfPage_EmptyHostFailure_LeavesRetrySurfaceAndNavigationAvailable` (`FluentPageTests.cs:25`) — 断言 `State==Error`、`CurrentPage==Library`、Workbench 导航按钮非 null 【核对】 | ✅ `WorkbenchPage_UnselectedState_OffersReturnToShelf` (`:38`) — `State==Empty`、`RegionCanvas` 非 null、三个 tab 点击后 `ActiveTab` + 选中 class + token 颜色/圆角 【核对】 | ✅ `ReaderPage_HostUnavailable_ShowsRecoverableErrorState` (`:90`) — `State==Error` 且 `FluentPageHost.Content` 是 `ReaderPageView` 【核对】 | ✅ `SettingsPage_HostUnavailable_IsBrowsableButReadOnly` (`:104`) — `State==ReadOnly`、`IsReadOnly==true`、Content 是 `SettingsPageView` 【核对】 |
| **四页 headless 渲染** | ✅ `FluentPages_RenderHeadlessPngEvidence` (`:258`) — 依次 Capture shelf/workbench/reader/settings 四帧并断言每帧 `PixelSize` 宽高 > 0；可选落盘 PNG（`NEWMANGA_CAPTURE_FLUENT_PNGS=1`）【核对】 | 同左 | 同左 | 同左 |
| **错误态** | ✅ 同"进入与空态"；另 `Bookshelf_ImportTypedFailure_ShowsCodeAndDoesNotRefresh` (`ImportExportUiTests.cs:229`) 断言面板出现 `IMPORT_SOURCE_UNAVAILABLE` 且**不刷新** 【核对】 | ✅ `I12_WorkbenchErrorCard_ConsoleEntry_NavigatesToConsoleSpace` (`FluentResidualBatchATests.cs:80`) — 错误卡可导航到 Console 【摘要】 | ✅ `ReaderPage_HostUnavailable_…` 【核对】 | ⚠️ 只读态见上；**无**独立"设置加载失败"错误态测试 【未覆盖】 |
| **只读** | ⚠️ `WritePolicyUiIntegrationTests`（`[HostSidecarFact]`）覆盖只读写拒绝，但需 sidecar → 本环境 NOT_RUN 【摘要】 | ✅ `Workbench_ReadOnlyHost_DisablesWrites_ShowsReason_ReadFaceStillWorks` (`RegionWorkbenchUiTests.cs`) — 断写面禁用 + 原因可见 + 读面仍工作 【摘要】 | ⚠️ Reader 只读由 `FluentPageTests.SettingsPage_…` 同型覆盖，Reader 本身无独立只读测试 【摘要】 | ✅ `SettingsPage_HostUnavailable_IsBrowsableButReadOnly` 【核对】 |
| **导入** | ✅ `Bookshelf_ImportFiles_CallsHostWithPickerPathsChapterAndRefreshes` (`:153`)、`Bookshelf_ImportFolder_PassesTheFolderPathAndPolicy` (`:196`)、`Bookshelf_ImportPickerCancel_LeavesFlowClosed` (`:251`)、失败见上 【核对（失败/取消）；其余摘要】 | ✅ `Workbench_ImportFiles_OpensTheSameFlow` (`:267`) 【摘要】 | — | — |
| **导出** | — | — | ✅ `Reader_ExportFlow_StartPollCompleteHistoryReveal` (`:316`) — 点击导出→面板可见→Start→轮询→Completed→历史→reveal 全链路；`Reader_ExportScopeSelector_ShowsThreeScopesAndOrderPreview` (`:420`)；`ExportStalePolicyTests` 覆盖 stale 策略四种分支 【核对（主链路）；策略摘要】 | — |
| **阅读进度** | ✅ `CommittedSave_RefreshesShelfDetail_AndShelfMatchesReader` (`LibraryProgressRefreshTests.cs:103`)、`ClosingReader_ReReadsHostProjection_…` (`:133`)、`RefusedSave_DoesNotFabricateShelfRefresh` (`:205`)、`Import_RefreshesProgressLine_…` (`:166`) 【摘要】 | — | ✅ 同左 + `SwitchingChapter_FlushesPreviousChapterProgress` (`ReaderChapterSelectorTests.cs:194`)、整书进度 `Reader_ShowsWholeBookProgressFromTheHostProjection` (`ReaderVisibleControlsTests.cs`) 【核对（整书进度）；其余摘要】 | — |
| **阅读偏好** | — | — | ✅ `ReaderPreferencePersistenceTests`（8，含在途/切书/合并/失败可见）+ `ReaderPreferenceWiringTests`（4，驱动真实按钮）+ `ReaderReadingPreferencesTests`（7，部分 patch 语义）【核对】 | — |
| **书签** | — | — | ✅ `Reader_BookmarkPanel_ListsExistingAndAddsAndDeletes` (`ReaderVisibleControlsTests.cs:58`) — 面板开→列出→添加→删除→空态 【核对】 | — |
| **Region 编辑** | — | ✅ `Workbench_RegionList_AndCanvasSelection_AreBidirectional`（列表→模型、画布→列表+模型双向）、`Workbench_ApplyType_Undo_Rerender_RefreshRealRegionData`、`Workbench_LoadsRealBookChapterPageChain_AndProjectsRegionGeometry`、`MainWindow_WorkbenchNavigation_LoadsTheRealRegionChain` 【核对（双向）；其余摘要】 | — | — |
| **主题 / 外观** | — | — | — | ✅ `Sink_MapsEveryThemeSettingsFieldIntoTheCanonicalDocument` (`AppearanceThemeSettingsSinkTests.cs:24`) + `V2ThemeStudioTests`（七段顺序、切段保草稿、Esc 阶梯、未保存对话框）【摘要】 |
| **快捷键** | ✅ `FluentShell_BreakpointsA11yShortcutsAndReducedMotion_AreExplicit` (`:119`) — 断言 18 个 gesture、`Conflicts` 为空、Ctrl+D2→Workbench、Tab→Batch、文本聚焦时不吞键 【核对】；`F11HotkeyTests`（书架→沉浸→Esc 还原、修正键不触发、不吞其他键）【摘要】 | ✅ 同左（Tab→Batch）【核对】 | ✅ `F11_OnReaderPage_ReturnsToReaderPageAfterClose` (`F11HotkeyTests.cs:101`) 【摘要】 | ⚠️ `ConsoleSpaceUsesWorkbenchConsoleAndSettingsRemainANonSpaceEntry` (`:166`) 断言 Settings 不是 Space 入口 【摘要】 |
| **焦点 / a11y** | ✅ `EachFluentPage_PaintsTheKeyboardFocusRing` (`FluentFocusPageCoverageTests.cs:42`) — 遍历四页，找 focusable+visible 控件并断言焦点环 【核对（遍历结构）】；`AC5_TabTraversal_LibraryReaderSettings_CoversFocusableSet_NoConsecutiveRepeats` (`FluentResidual3Tests.cs:1082`)、`AC5_UiaTree_InteractiveNodesAreNamed_AndOverlayFocusRoundTrips` (`:1260`)、`FluentShell_…` 断言导航按钮 `AutomationProperties.Name` 【摘要】 | 同左 | 同左 | 同左 |
| **Host 生命周期 / 恢复** | ⚠️ `HostController_…` 集成（`[HostSidecarFact]`）→ E-2 NOT_RUN；headless 侧仅错误态 【摘要】 | ⚠️ 同左 | ⚠️ 同左 | ⚠️ 同左 |

## 2. 按可执行性分层（这是条件 3 的实际形态）

### 2.1 有覆盖且**无夹具即可跑**（可安全执行）
上表 ✅/⚠️ 中所有 `[AvaloniaFact]`/`[Fact]` 项：四页进入与空态、四页 headless 渲染、书架/工作台/阅读器
错误态、导入全分支、导出全链路、阅读进度与刷新、阅读偏好、书签、Region 编辑、主题、快捷键、焦点与 a11y。
这些已在 `dotnet test NewManga.App.Tests`（947/0/11）中**真实执行并通过**。

### 2.2 有覆盖但**需真实 sidecar**（E-2 阻塞，NOT_RUN）
- `ChapterCreationTests` 的 2 个 `[HostSidecarFact]`。
- `WritePolicyUiIntegrationTests` 的只读写拒绝。
- `NewManga.Host.Tests` 的 **74 个 skip**、`NewManga.CoreClient.Tests` 的 **26 个 skip**。
- 共同原因：仓库 sidecar 构建于 **2026-10-23**，早于多条现行命令（E-2）；重建需 PyInstaller，本环境 PyPI 不可达。

### 2.3 **完全无覆盖**
- 设置页的"加载失败/错误态"（只有只读态）。
- 阅读器的独立"只读"测试（借道设置页同型断言）。
- 真实窗口的人工交互矩阵（无法自动化，需真机）。

## 3. 条件 3 的可判定结论

**条件 3 不能判 MET，但可以从含糊的"部分"细化为：**

1. **"可安全执行的"部分已大面覆盖**：四页 + 13 类关键流程中，**11 类**在 headless 下有真实断言，
   且四页有 PNG 级渲染证据（§1 第 2 行）。这比 Gate 评估 §2 里"部分"的表述精确得多。
2. **剩余缺口的性质已明确**，且**没有一项是"GUI 没做"**：
   - 集成层（Host/CoreClient 的 100 个 skip）**全部**卡在 E-2 sidecar；
   - 2 类完全无覆盖（设置错误态、阅读器只读）；
   - 真实窗口矩阵属人工验证范畴。
3. **因此条件 3 的推进路径是"解 E-2"或"Owner 接受该边界"**，而不是继续补 headless 测试。
   若 E-2 不能解（本环境确实不能），则条件 3 应作为**已知边界**提交 Owner 裁决，
   而不是无限期停留在"部分"。

## 4. 本矩阵自身的限制（不得当作已证实）

- 上表多数格标【摘要】：我读了类/方法 summary 与方法名，**未**逐行核对每条断言。真正被逐行核对的是
  标【核对】的 12 格。**不得**把【摘要】格当作"已验证"。
- 未统计 `NewManga.Presentation.Avalonia` / `NewManga.DesignSystem` 等其它测试项目对 UI 的覆盖。
- 未核验 `--shell=legacy` 旧界面路径。
- 未做真机手动走查。
