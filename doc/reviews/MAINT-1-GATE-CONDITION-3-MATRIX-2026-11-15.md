# Gate 条件 3 覆盖矩阵（2026-11-15，r2 返修版）

**Task**：`GATE3-COVERAGE-MATRIX`。**基线**：`d86f185ca`。
**条件原文**：「补齐**可安全执行的**完整 GUI / Core / Host 关键流程与 Avalonia TestHost；所有 blocked/skipped 项继续保留原结果」（`audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md:27`）。

> **r1 复核 REJECT 后的返修说明**：r1 指出三个 P1 —— ①本矩阵只盘了 GUI 四页，而条件 3 明确含 **Core / Host**，
> 且未声明范围；②结论口径混用（"类"与"格"混用，且"阅读器只读"实际有测试）；③sidecar 依赖只数了
> `[HostSidecarFact]`，实际有 4 类 gate。本版按此重写：**范围扩到 GUI + Core + Host 三层**，
> 数字全部重测，并新增 §5 失效（staleness）声明。

## 0. 范围声明（先划清，避免把局部当整体）

本矩阵覆盖 **三层**：

1. **GUI 层** —— `apps/desktop-avalonia/tests/NewManga.App.Tests`（Avalonia headless）。
2. **Host 层** —— `apps/desktop-avalonia/tests/NewManga.Host.Tests`。
3. **Core/客户端层** —— `apps/desktop-avalonia/tests/NewManga.CoreClient.Tests`（wire 契约与 sidecar 生命周期）。

**不在本矩阵内**：`NewManga.Presentation.Avalonia` / `NewManga.DesignSystem` 等其它测试项目的 UI 覆盖、
`--shell=legacy` 旧界面路径、以及**真机人工走查**（无法自动化）。

## 1. 方法与证据强度

每格给出：状态 → 代表测试 → 该测试**实际断言了什么**。强度三级，**逐格标注**：

- **【核对】** 我逐行读过该测试的断言。
- **【摘要】** 读过类/方法 summary 与方法名，**未**逐行核对断言 —— **不得当作已验证**。
- **【未覆盖】** 仓库内找不到针对该流程的测试。

## 2. 规模（全部本基线实测）

| 层 | 结果 | 说明 |
|---|---|---|
| `NewManga.App.Tests` | **947 / 0 / 11 / 958** | 无夹具全量 |
| ├ `[AvaloniaFact]` 文件 | **62 个** | headless 可跑，无需 sidecar |
| ├ sidecar gate 测试 | **7 个** | 4 类 gate：`[HostSidecarFact]`×2（`CreateChapterHostIntegrationTests`）、`[RunSidecarFact]`×3（`RunControllerHostIntegrationTests`）、`[WritePolicySidecarFact]`×1（`WritePolicyUiIntegrationTests`）、`[WritePolicySidecarFact]`×1（`StartupSelfCheckUiTests`） |
| └ 非 sidecar 的 4 个 skip | **4 个** | `PerformanceBaselineTests.Gated_HotSwitch_…`（perf 预算 gate）、`StartupDiagnosticsTests.RealProcessLaunchMatrix_…`（真实进程）、`Fea07Residual3CrashTests.{Park,Recover}_…`（崩溃注入） |
| `NewManga.Host.Tests` | **321 / 0 / 74 / 395** | 74 skip |
| `NewManga.CoreClient.Tests` | **186 / 0 / 26 / 212** | 26 skip |

### 1.1 **关键更正**：skip 不等于"全部卡在 E-2"

r1 复核指出、我也实测确认：Host.Tests 的 74 skip **由两类原因构成**：

| 原因 | 规模（r1 复核实测） | 与 E-2 的关系 |
|---|---|---|
| sidecar 缺失（`SidecarFact` 家族） | **30** | **是** E-2（仓库 sidecar 构建于 2026-10-23，早于多条现行命令） |
| opt-in real-IPC 环境变量（`NEWMANGA_FEA11_IPC` 22 处、`NEWMANGA_FEA09_IPC` 5、`NEWMANGA_FEA10_IPC` 2、`NEWMANGA_FEA11_CRASH_STATE` 4、`NEWMANGA_CORE_TILE_E2E`、`NEWMANGA_FEA07_A03`、`NEWMANGA_FEA11_CRASH_NEGATIVE`） | **44** | **否** —— 这些是需要显式开启的真实 IPC/崩溃注入测试，本就不在默认门禁里 |

⇒ 先前"100 个 skip 全部卡 E-2"的说法**错误**，已撤回。

## 3. GUI 层：四页 × 关键流程

图例：✅有覆盖　⚠️部分　❌NOT_RUN　— 不适用。

| 流程 \ 页面 | 书架 | 工作台 | 阅读器 | 设置 |
|---|---|---|---|---|
| **进入与空态** | ✅ `ShelfPage_EmptyHostFailure_…` (`FluentPageTests.cs:25`) — `State==Error`、`CurrentPage==Library`、Workbench 导航按钮非 null【核对】 | ✅ `WorkbenchPage_UnselectedState_…` (`:38`) — `State==Empty`、`RegionCanvas` 非 null、三 tab 点击后 `ActiveTab`+选中 class+token 颜色/圆角【核对】 | ✅ `ReaderPage_HostUnavailable_…` (`:90`) — `State==Error` 且 Content 是 `ReaderPageView`【核对】 | ✅ `SettingsPage_HostUnavailable_IsBrowsableButReadOnly` (`:104`) — `State==ReadOnly`、`IsReadOnly`、Content 是 `SettingsPageView`【核对】 |
| **四页 headless 渲染** | ✅ `FluentPages_RenderHeadlessPngEvidence` (`:258`) — 依次 Capture 四页并断言每帧 `PixelSize` 宽高 > 0；可选落盘 PNG【核对】 | 同左 | 同左 | 同左 |
| **错误态** | ✅ 同上；`Bookshelf_ImportTypedFailure_ShowsCodeAndDoesNotRefresh` (`ImportExportUiTests.cs:229`) — 面板出现 `IMPORT_SOURCE_UNAVAILABLE` 且不刷新【核对】 | ✅ `I12_WorkbenchErrorCard_ConsoleEntry_NavigatesToConsoleSpace` (`FluentResidualBatchATests.cs:80`)【摘要】 | ✅ `ReaderPage_HostUnavailable_…`【核对】 | ❌ **无**独立"设置加载失败"错误态测试（只有只读态）【未覆盖】 |
| **只读** | ⚠️ `[WritePolicySidecarFact]` 的 `WritePolicyUiTests` 覆盖只读写拒绝 → 需 sidecar，本环境 NOT_RUN【摘要】 | ✅ `Workbench_ReadOnlyHost_DisablesWrites_ShowsReason_ReadFaceStillWorks` (`RegionWorkbenchUiTests.cs`)【摘要】 | ✅ **`ReadOnlyHost_DoesNotPersist_ButReaderKeepsWorking`** (`ReaderProgressTests.cs:194`) — 只读 Host 下不持久化但阅读器仍工作【摘要】 | ✅ `SettingsPage_HostUnavailable_IsBrowsableButReadOnly`【核对】 |
| **导入** | ✅ `Bookshelf_ImportFiles_…` (`:153`)、`…Folder_…` (`:196`)、`…PickerCancel_…` (`:251`)、失败见上 | ✅ `Workbench_ImportFiles_OpensTheSameFlow` (`:267`)【摘要】 | — | — |
| **导出** | — | — | ✅ `Reader_ExportFlow_StartPollCompleteHistoryReveal` (`:316`) — 导出按钮→面板→Start→轮询→Completed→历史→reveal；`Reader_ExportScopeSelector_…` (`:420`)；`ExportStalePolicyTests` 四种 stale 策略【核对（主链路）】 | — |
| **阅读进度** | ✅ `CommittedSave_RefreshesShelfDetail_AndShelfMatchesReader` (`LibraryProgressRefreshTests.cs:103`)、`ClosingReader_ReReadsHostProjection_…` (`:133`)、`RefusedSave_DoesNotFabricateShelfRefresh` (`:205`)、`Import_RefreshesProgressLine_…` (`:166`)【摘要】 | — | ✅ 同左 + `SwitchingChapter_FlushesPreviousChapterProgress` (`ReaderChapterSelectorTests.cs:194`)、`Reader_ShowsWholeBookProgressFromTheHostProjection`【核对（整书进度）】 | — |
| **阅读偏好** | — | — | ✅ `ReaderPreferencePersistenceTests`（**9**，含在途/切书/合并/失败可见）+ `ReaderPreferenceWiringTests`（4，驱动真实按钮）+ `ReaderReadingPreferencesTests`（7，partial patch）【核对】 | — |
| **书签** | — | — | ✅ `Reader_BookmarkPanel_ListsExistingAndAddsAndDeletes` (`ReaderVisibleControlsTests.cs:58`)— 面板开→列出→添加→删除【核对】 | — |
| **Region 编辑** | — | ✅ `Workbench_RegionList_AndCanvasSelection_AreBidirectional`（列表→模型、画布→列表+模型双向）、`Workbench_ApplyType_Undo_Rerender_…`、`Workbench_LoadsRealBookChapterPageChain_…`、`MainWindow_WorkbenchNavigation_…`【核对（双向）】 | — | — |
| **主题/外观** | — | — | — | ✅ `Sink_MapsEveryThemeSettingsFieldIntoTheCanonicalDocument` (`AppearanceThemeSettingsSinkTests.cs:24`)【摘要】；`V2ThemeStudioTests`（七段顺序、切段保草稿、Esc 阶梯、未保存对话框）【摘要】 |
| **快捷键** | ✅ `FluentShell_BreakpointsA11yShortcutsAndReducedMotion_AreExplicit` (`:119`)— 18 gesture、`Conflicts` 空、Ctrl+D2→Workbench、Tab→Batch、文本聚焦不吞键【核对】 | ✅ 同左【核对】 | ✅ `F11_OnReaderPage_ReturnsToReaderPageAfterClose` (`F11HotkeyTests.cs:101`)【摘要】 | ⚠️ `ConsoleSpaceUsesWorkbenchConsoleAndSettingsRemainANonSpaceEntry` (`:166`)【摘要】 |
| **焦点/a11y** | ✅ `EachFluentPage_PaintsTheKeyboardFocusRing` (`FluentFocusPageCoverageTests.cs:42`)— 遍历四页找 focusable+visible 控件并断言焦点环【核对（结构）】；`AC5_TabTraversal_…` (`FluentResidual3Tests.cs:1082`)、`AC5_UiaTree_…` (`:1260`)【摘要】 | 同左 | 同左 | 同左 |

## 4. Host / Core 层：集成流程（r1 复核 R-001 补齐）

`git` 基线为 `d86f185ca`。gate 列含义：**plain** = 无 sidecar 也能跑（计入 321/186 passed）；
**sidecar** = `SidecarFact`；**opt-in** = 需显式环境变量。

| 流程 | 代表测试文件（方法数） | gate | 状态 |
|---|---|---|---|
| Host 运行时装配 / 生命周期 | `HostRuntimeIntegrationTests.cs`(4) | sidecar | ⚠️ 有覆盖，本环境 **NOT_RUN**（E-2） |
| 阅读器章节链（Host） | `HostReaderChaptersIntegrationTests.cs`(2) | **plain** | ✅ 本地可跑（计入 321 passed） |
| 阅读进度（Host） | `HostReaderProgressIntegrationTests.cs`(3) | sidecar | ⚠️ 有覆盖，NOT_RUN（E-2） |
| Region 工作台链（Host） | `HostRegionWorkbenchIntegrationTests.cs`(4) | **plain** | ✅ 本地可跑 |
| 导出端到端（Host） | `ExportE2ETests.cs`(2) | sidecar + `NEWMANGA_EXPORT_*` | ⚠️ NOT_RUN（E-2 + opt-in） |
| 写策略（Host） | `WritePolicyTests.cs`(6) | sidecar | ⚠️ NOT_RUN（E-2） |
| 凭据端口（Host） | `CredentialPortTests.cs`(11) | sidecar | ⚠️ NOT_RUN（E-2） |
| Source 扫描调度 | `SourceScanSchedulerTests.cs`(57) | **plain** | ✅ 本地可跑 |
| Source 恢复（IPC） | `SourceRecoveryIpcTests.cs`(5) | opt-in `NEWMANGA_FEA11_IPC` | ❌ 默认门禁外（非 E-2 原因） |
| Source 注册表韧性 | `SourceRegistryResilienceTests.cs`(10) | opt-in `NEWMANGA_FEA11_IPC` | ❌ 默认门禁外 |
| Run 授权续期 | `RunGrantRenewalTests.cs`(23) | **plain** | ✅ 本地可跑 |
| 安全 harness | `D4SecurityHarnessTests.cs`(7) | opt-in `NEWMANGA_EVIDENCE_DIR` | ❌ 默认门禁外 |
| Core tile 端到端 | `CoreTileEmitEndToEndTests.cs`(1) | opt-in `NEWMANGA_CORE_TILE_E2E` | ❌ 默认门禁外 |
| Host 单元面 | `HostUnitTests.cs`(14) | **plain** | ✅ 本地可跑 |
| wire 命令契约 | `CommandContractV11RTests` / `CommandParityContractTests` / `CommandWiringB1/B2`（CoreClient） | plain | ✅ 本地可跑 |
| 命令覆盖（六服务口径） | `CommandCoverageRoutingTests.cs`(4) | **plain** | ✅ 本地可跑（本会话 `CMD-COVERAGE-ASSERT-FIX` 修复） |
| sidecar 生命周期 / 失败 | `SidecarLifecycleTests` / `SidecarFailureTests`（CoreClient） | sidecar | ⚠️ NOT_RUN（E-2） |

**Host/Core 层的结论**：本地可跑部分（plain）**相当广**（Source 调度 57、Run 授权 23、Host 单元 14、
区域链 4、章节链 2、命令契约与覆盖）已在 321/186 passed 中真实执行；需 sidecar 的部分**全部** NOT_RUN
（E-2）；另有一组 opt-in real-IPC **本就不在默认门禁**（非 E-2，需显式开启，本环境未开启）。

## 5. 条件 3 的可判定结论（r2 修正）

1. **GUI 层覆盖广度**：四页 × 13 类流程中，**12 类有覆盖**；**唯一完全无覆盖的是"设置页错误态"一格**
   （`SettingsPage_HostUnavailable_IsBrowsableButReadOnly` 只覆盖只读态，不是加载失败态）。
   另有 2 格为"借道同型断言"（书架只读走 `[WritePolicySidecarFact]` → NOT_RUN；设置快捷键只有
   "Settings 不是 Space 入口"一条），标 ⚠️。
2. **Host/Core 层**：plain 部分相当广（Source 调度 57、Run 授权 23、Host 单元 14、区域链 4、章节链 2、
   wire 契约与命令覆盖），已在 321/186 passed 中真实执行；`SidecarFact` 部分全部 NOT_RUN（E-2）；
   opt-in real-IPC / 崩溃注入部分**不在默认门禁**（不是 E-2，是"未开启"）。
3. **剩余缺口按性质分三类**：
   - **E-2 阻塞**：所有 `SidecarFact` 家族（Host 30 skip + CoreClient 26 skip + App 7 个测试）；
   - **默认门禁外**：Host 44 个 opt-in real-IPC / 崩溃注入 + App 4 个（perf gate / 真实进程 / 崩溃注入）；
   - **真无覆盖**：**仅 1 格**（设置页错误态）；真机人工走查属另一范畴。
4. **条件 3 不能判 MET。** 推进路径按性质分：解 E-2（本环境不可行）/ 开启 opt-in 矩阵（需环境与样本）/
   补那 1 格未覆盖测试 / Owner 接受边界。
5. **撤回前版两处错误表述**：
   - "完全无覆盖仅 2 类" → 实际**只有 1 格**："阅读器只读"有测试（`ReaderProgressTests.cs:194`
     `ReadOnlyHost_DoesNotPersist_ButReaderKeepsWorking`）；
   - "100 个 skip 全部卡 E-2" → Host 74 skip 中**仅 30** 是 sidecar，**44** 是 opt-in real-IPC/崩溃注入。

## 6. 失效（staleness）声明 —— r1 复核 P2 要求

本矩阵是**基线 `d86f185ca` 的快照**，**没有任何自动机制**保证它与代码同步：
测试改名、移动、删除或新增都**不会**让本矩阵变红。因此：

- 任何后续 Task 若改动上述测试文件，**必须**在卡面登记"条件 3 矩阵可能过时"；
- Gate 裁决若引用本矩阵，必须注明其基线 commit；
- 重新生成成本较低（本卡为纯盘点），但不自动触发。

## 7. 本矩阵自身的限制（不得当作已证实）

- 标【摘要】的格（多数）**未**逐行核对断言；真正逐行核对的是标【核对】的 **12 格**。
- 未统计 `NewManga.Presentation.Avalonia` / `NewManga.DesignSystem` 等其它测试项目。
- 未核验 `--shell=legacy` 旧界面路径。
- 未做真机手动走查。
- §1.1 的 30/44 拆分数字来自 r1 复核的实测；我复核了 skip 的两类来源结构，未逐条重数 74 个。
