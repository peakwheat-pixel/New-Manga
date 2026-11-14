# Gate 条件 3 覆盖矩阵（2026-11-15，r3 定稿）

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
| ├ sidecar gate 测试 | **7 个** | **4 个 attribute 类型**：`[HostSidecarFact]`×2（`ChapterCreationTests`）、`[RunSidecarFact]`×2（`RunControllerTests`）、`[RunBookFixtureFact]`×1（`RunControllerTests`）、`[WritePolicySidecarFact]`×2（`WritePolicyUiTests` 1 + `StartupSelfCheckUiTests` 1） |
| └ 非 sidecar 的 4 个 skip | **4 个** | `PerformanceBaselineTests.Gated_HotSwitch_…`（perf 预算 gate）、`StartupDiagnosticsTests.RealProcessLaunchMatrix_…`（真实进程）、`Fea07Residual3CrashTests.{Park,Recover}_…`（崩溃注入） |
| `NewManga.Host.Tests` | **321 / 0 / 74 / 395** | 74 skip |
| `NewManga.CoreClient.Tests` | **186 / 0 / 26 / 212** | 26 skip |

### 1.1 **关键更正**：skip 不等于"全部卡在 E-2"

r1 复核指出、r2 复核再次纠正：**skip 的原因不止 sidecar**，而且我**无法仅凭类名可靠切分**。

| 层 | skip 总量 | 能确定的成分 |
|---|---|---|
| App.Tests | 11 | **7 个 sidecar gate**（4 个 attribute 类型，见 §2）+ **4 个非 sidecar**（perf 预算 gate、真实进程启动、崩溃注入 ×2） |
| Host.Tests | 74 | 按类分布见 §4.2；含 opt-in real-IPC（`NEWMANGA_FEA09/10/11/12_*_IPC`）、fixture（Book/Region）、sidecar |
| CoreClient.Tests | 26 | 按类分布见 §4.3 |

⇒ 先前"100 个 skip 全部卡 E-2"与"30 sidecar / 44 opt-in"两个说法**均已撤回**（后者来自二手结论，
我的实测无法复现该二分）。本文件只保留可实测的**类分布**。

## 3. GUI 层：四页 × 关键流程

图例：✅有覆盖　⚠️部分　❌NOT_RUN　— 不适用。

| 流程 \ 页面 | 书架 | 工作台 | 阅读器 | 设置 |
|---|---|---|---|---|
| **进入与空态** | ✅ `ShelfPage_EmptyHostFailure_…` (`FluentPageTests.cs:25`) — `State==Error`、`CurrentPage==Library`、Workbench 导航按钮非 null【核对】 | ✅ `WorkbenchPage_UnselectedState_…` (`:38`) — `State==Empty`、`RegionCanvas` 非 null、三 tab 点击后 `ActiveTab`+选中 class+token 颜色/圆角【核对】 | ✅ `ReaderPage_HostUnavailable_…` (`:90`) — `State==Error` 且 Content 是 `ReaderPageView`【核对】 | ✅ `SettingsPage_HostUnavailable_IsBrowsableButReadOnly` (`:104`) — `State==ReadOnly`、`IsReadOnly`、Content 是 `SettingsPageView`【核对】 |
| **四页 headless 渲染** | ✅ `FluentPages_RenderHeadlessPngEvidence` (`:258`) — 依次 Capture 四页并断言每帧 `PixelSize` 宽高 > 0；可选落盘 PNG【核对】 | 同左 | 同左 | 同左 |
| **错误态** | ✅ 同上；`Bookshelf_ImportTypedFailure_ShowsCodeAndDoesNotRefresh` (`ImportExportUiTests.cs:229`) — 面板出现 `IMPORT_SOURCE_UNAVAILABLE` 且不刷新【核对】 | ✅ `I12_WorkbenchErrorCard_ConsoleEntry_NavigatesToConsoleSpace` (`FluentResidualBatchATests.cs:80`)【摘要】 | ✅ `ReaderPage_HostUnavailable_…`【核对】 | ✅ **`LoadFailure_PutsTheViewModelInErrorState_WithRetryableMessage` / `LoadFailure_ShowsTheErrorBannerWithRetryAction`** (`SettingsErrorStateTests.cs:35/:53`) — 设置读取抛异常后 `State==Error`、文案含"设置读取失败…可以重试"，且真实视图树出现"设置错误" banner 与"重试"按钮【核对】**（`SETTINGS-ERROR-STATE-1` 补）** |
| **只读** | ✅ **`WritePolicyUiIntegrationTests.DefaultController_IsWritable_AndParityFalse_IsReadOnlyWithReason`**（`[WritePolicySidecarFact]`）—— 带新 sidecar 实测**真实执行并通过**（`GATE3-SIDECAR-COVERAGE-1`，7 passed/0 skipped 定向复跑）【实测】**（澄清：`WritePolicyUiTests` 是 4 个不依赖 sidecar 的普通 Fact，与本格无关）** | ✅ `Workbench_ReadOnlyHost_DisablesWrites_ShowsReason_ReadFaceStillWorks` (`RegionWorkbenchUiTests.cs`)【摘要】 | ✅ **`ReadOnlyHost_DoesNotPersist_ButReaderKeepsWorking`** (`ReaderProgressTests.cs:194`) — 只读 Host 下不持久化但阅读器仍工作【摘要】 | ✅ `SettingsPage_HostUnavailable_IsBrowsableButReadOnly`【核对】 |
| **导入** | ✅ `Bookshelf_ImportFiles_…` (`:153`)、`…Folder_…` (`:196`)、`…PickerCancel_…` (`:251`)、失败见上 | ✅ `Workbench_ImportFiles_OpensTheSameFlow` (`:267`)【摘要】 | — | — |
| **导出** | — | — | ✅ `Reader_ExportFlow_StartPollCompleteHistoryReveal` (`:316`) — 导出按钮→面板→Start→轮询→Completed→历史→reveal；`Reader_ExportScopeSelector_…` (`:420`)；`ExportStalePolicyTests` 四种 stale 策略【核对（主链路）】 | — |
| **阅读进度** | ✅ `CommittedSave_RefreshesShelfDetail_AndShelfMatchesReader` (`LibraryProgressRefreshTests.cs:103`)、`ClosingReader_ReReadsHostProjection_…` (`:133`)、`RefusedSave_DoesNotFabricateShelfRefresh` (`:205`)、`Import_RefreshesProgressLine_…` (`:166`)【摘要】 | — | ✅ 同左 + `SwitchingChapter_FlushesPreviousChapterProgress` (`ReaderChapterSelectorTests.cs:194`)、`Reader_ShowsWholeBookProgressFromTheHostProjection`【核对（整书进度）】 | — |
| **阅读偏好** | — | — | ✅ `ReaderPreferencePersistenceTests`（**9**，含在途/切书/合并/失败可见）+ `ReaderPreferenceWiringTests`（4，驱动真实按钮）+ `ReaderReadingPreferencesTests`（7，partial patch）【核对】 | — |
| **书签** | — | — | ✅ `Reader_BookmarkPanel_ListsExistingAndAddsAndDeletes` (`ReaderVisibleControlsTests.cs:58`)— 面板开→列出→添加→删除【核对】 | — |
| **Region 编辑** | — | ✅ `Workbench_RegionList_AndCanvasSelection_AreBidirectional`（列表→模型、画布→列表+模型双向）、`Workbench_ApplyType_Undo_Rerender_…`、`Workbench_LoadsRealBookChapterPageChain_…`、`MainWindow_WorkbenchNavigation_…`【核对（双向）】 | — | — |
| **主题/外观** | — | — | — | ✅ `Sink_MapsEveryThemeSettingsFieldIntoTheCanonicalDocument` (`AppearanceThemeSettingsSinkTests.cs:24`)【摘要】；`V2ThemeStudioTests`（七段顺序、切段保草稿、Esc 阶梯、未保存对话框）【摘要】 |
| **快捷键** | ✅ `FluentShell_BreakpointsA11yShortcutsAndReducedMotion_AreExplicit` (`:119`)— 18 gesture、`Conflicts` 空、Ctrl+D2→Workbench、Tab→Batch、文本聚焦不吞键【核对】 | ✅ 同左【核对】 | ✅ `F11_OnReaderPage_ReturnsToReaderPageAfterClose` (`F11HotkeyTests.cs:101`)【摘要】 | ✅ **`SettingsSpaceShortcutTests.ConsoleSpace_DoesNotSwallowGlobalShortcuts`**（新增，`GATE3-SETTINGS-SHORTCUT-1`）—— 用 `Ctrl+D3` 进 Console，断言 `State.CurrentSpace==SpaceId.Console`；**从 Console 按 `Ctrl+K`** 断言被处理且 `IsPaletteOpen`；`Esc` 关闭；`Ctrl+D2` 回 Studio。判别力实测：把 `ConsoleWorkspaceView.TryHandleKey` 改成 `=> true` 会使它变红【实测】。原 `ConsoleSpaceUsesWorkbenchConsole…` 只证明"设置不是 Space 入口"，不等于"快捷键仍生效"，已保留为旁证 |
| **焦点/a11y** | ✅ `EachFluentPage_PaintsTheKeyboardFocusRing` (`FluentFocusPageCoverageTests.cs:42`)— 遍历四页找 focusable+visible 控件并断言焦点环【核对（结构）】；`AC5_TabTraversal_…` (`FluentResidual3Tests.cs:1082`)、`AC5_UiaTree_…` (`:1260`)【摘要】 | 同左 | 同左 | 同左 |

## 4. Host / Core 层：实测 skip 分布（r2 复核后重写）

> **本节在 r2 复核后被彻底重写。** 上一版按"类"贴 `plain`/`sidecar` 标签，把
> `HostReaderChaptersIntegrationTests`(2) 与 `HostRegionWorkbenchIntegrationTests`(4) 误判为 `plain` 并
> 声称"计入 321 passed"。**r2 复核用实跑证伪：这两类分别是 `[BookFixtureFact]` / `[RegionFixtureFact]`，
> 6 个测试全部 SKIP。** 我的错误根因是**用源码正则推断 gate 与分类，而没有实测运行结果**。
>
> 本节现在只报**实测数字**（`dotnet test` 的 "已跳过" 输出），不再猜 gate 类型；也不列分母
> （总测试数未逐一实测，列分母会再次出错）。

### 4.1 三层 skip 总量（实测）

| 层 | 结果 |
|---|---|
| `NewManga.App.Tests` | 947 passed / 0 failed / **11 skipped** / 958 |
| `NewManga.Host.Tests` | 321 passed / 0 failed / **74 skipped** / 395 |
| `NewManga.CoreClient.Tests` | 186 passed / 0 failed / **26 skipped** / 212 |

### 4.2 Host.Tests 的 74 个 skip，按实测类分布

| 测试类 | skip 数 | 性质（据类名/attribute 判断，未逐条核实） |
|---|---|---|
| `Fea09UiImportIpcProductionTests` | 11 | opt-in real-IPC（`NEWMANGA_FEA09_IPC`） |
| `Fea11RunGrantIpcTests` | 7 | opt-in real-IPC（`NEWMANGA_FEA11_IPC`） |
| `Fea09UiImportIpcTests` | 5 | opt-in real-IPC |
| **`HostRegionWorkbenchIntegrationTests`** | **4** | **`[RegionFixtureFact]` — 需 region fixture，本环境 SKIP** |
| `GrantIssuerTests` | 4 | fixture/host-control |
| `Fea11HostAuthIpcTests` | 4 | opt-in real-IPC |
| `Fea11Residual4AIpcTests` | 4 | opt-in real-IPC |
| `Fea11ScanIpcTests` | 4 | opt-in real-IPC |
| `Fea11SourceIpcTests` | 3 | opt-in real-IPC |
| `HostRuntimeIntegrationTests` | 3 | sidecar |
| `HostReaderProgressIntegrationTests` | 3 | sidecar |
| `StartupSelfCheckTests` | 3 | fixture |
| `WritePolicyTests` | 3 | sidecar |
| **`HostReaderChaptersIntegrationTests`** | **2** | **`[BookFixtureFact]` — 需 book fixture，本环境 SKIP** |
| `ExportE2ETests` | 2 | sidecar + `NEWMANGA_EXPORT_*` |
| `Fea10RunIpcTests` | 1 | opt-in real-IPC |
| `Fea11WatchHostRuntimeTests` | 1 | host-runtime |
| `Fea12TrashUiIpcTests` | 1 | opt-in IPC |
| `Fea09RealIpcTests` | 1 | opt-in real-IPC |
| `Fea07Residual3IpcTests` | 1 | opt-in IPC |
| `ExportStalePolicyWireTests` | 1 | sidecar |
| `LegacyShellRealTests` | 1 | 需 legacy shell fixture |
| `RealTranslateProviderTests` | 1 | 需真实 provider |
| `SourceRecoveryIpcTests` | 1 | opt-in real-IPC |
| `SourceRegistryResilienceTests` | 1 | opt-in real-IPC |
| `Fea11Scan2HostRuntimeTests` | 1 | host-runtime |
| `CredentialPortTests` | 1 | sidecar |

**合计 74**（上表 27 行相加 = 74，与 `verification/GATE3-COVERAGE-MATRIX/host-skips.txt` 的 74 行逐名一致）。

**30 / 44 的二分可复现，予以恢复**（上一版撤回过度）：

- **30** = `HostSidecarFact` 22 + `BookFixture` 4（`HostReaderChaptersIntegrationTests` 2 + `Fea11RunGrantIpcTests` 内 2）
  + `RegionFixture` 4（`HostRegionWorkbenchIntegrationTests`）—— 即"需要 sidecar/fixture 才能跑"的 30 个。
- **44** = 74 − 30，即 opt-in real-IPC / 崩溃注入 / 需真实 provider / legacy fixture 等。
- 两者之和 74，与实测行数一致。**归属到单个类时仍需逐条看 attribute**，本节只主张总量可复现。

### 4.3 CoreClient.Tests 的 26 个 skip，按实测类分布

| 测试类 | skip 数 |
|---|---|
| `CommandIntegrationTests` | 6 |
| `CoreServiceIntegrationTests` | 4 |
| `RunBindingFixTests` | 4 |
| `CommandWiringB2Tests` | 3 |
| `HostBridgeIntegrationTests` | 3 |
| `CommandWiringB1Tests` | 2 |
| `TransRunPathFixTests` | 2 |
| `S4RegionReaderCommandTests` | 1 |
| `SidecarFailureTests` | 1 |

**合计 26。**

### 4.4 因此"Host/Core 层哪些流程有覆盖"能说到什么程度

- **有覆盖且已执行**：Host/CoreClient 的 **321 + 186 passed**。这些包含 wire 命令契约、命令覆盖、
  Host 单元面、Source 调度、Run 授权、以及各 IPC 类的非 skip 方法。
- **明确 NOT_RUN（本环境）**：上两表列出的 **74 + 26 = 100 个 skip**。其中真正属于"E-2 sidecar 过期"
  的子集**我无法仅凭类名可靠切分**（见 §4.2 的归因说明），因此**不再宣称具体比例**。
- **可安全执行的 GUI 之外的有力证据**：`CommandCoverageRoutingTests`(4, 无 sidecar) 与 wire 契约类
  （`CommandContractV11RTests` / `CommandParityContractTests`）在 passed 中。

## 5. 条件 3 的可判定结论（r3 修正）

1. **GUI 层（限定范围：本矩阵 §3 的 4 页 × 13 类）**：**所有 ❌ 格已清零**。`SETTINGS-ERROR-STATE-1` 补上了原先唯一缺的"设置页错误态"；但仍有 **2 个 ⚠️ 格**（书架只读走 `[WritePolicySidecarFact]` → 本环境 NOT_RUN；设置快捷键仅"非 Space 入口"一条），且 **§0 未纳**回收站/命令面板/源恢复/沉浸等其它 GUI 流程。
   仍有 2 格为借道同型断言（书架只读走 `[WritePolicySidecarFact]` → 本环境 NOT_RUN；设置快捷键仅"非 Space 入口"一条），标 ⚠️。
2. **Host/Core 层**：**321 + 186 passed** 是真实执行的覆盖（wire 契约、命令覆盖、Host 单元面、Source 调度、
   Run 授权、各 IPC 类的非 skip 方法）；**100 个 skip**（74 + 26）在本环境 NOT_RUN。
3. **剩余缺口分三类**：
   - **被 skip 的集成面**：三项目共 **111 个 skip**（Host 74 + CoreClient 26 + App 11）。其中 App 的 11 = 7 sidecar + 4 非 sidecar。我并不宣称它们全部因 E-2 ——
     归因需逐条核 attribute，本节只给类分布（§4.2/§4.3）。
   - **真无覆盖**：**本矩阵 4 页 × 13 类范围内 0 个 ❌ 格**（`SETTINGS-ERROR-STATE-1` 已补设置页错误态；见 `SettingsErrorStateTests.cs:35/:53`）。**这不等于"整个产品 GUI 无缺口"** —— 范围限定与 ⚠️ 格见 §0 与本节第 1 条。
   - **人工范畴**：真机窗口走查。
4. **条件 3 不能判 MET。** 要判 MET，需要：执行被 skip 的 111 个测试（其中大部分需 sidecar 或 opt-in
   环境与样本），或由 Owner 明确接受该边界。**在本矩阵限定的 4 页 × 13 类内，❌ 格已清零；剩下的是 2 个 ⚠️ 格、111 个 skip、以及未纳范围的 GUI 流程与真机走查。**
5. **撤回上一版三处错误（全部由 r1/r2 复核实测发现，均属我的判断失误）**：
   - "`HostReaderChaptersIntegrationTests` / `HostRegionWorkbenchIntegrationTests` 是 plain、计入 passed"
     → **错**：它们是 `[BookFixtureFact]` / `[RegionFixtureFact]`，6 个测试**全部 SKIP**。
   - "100 个 skip 全部卡 E-2" → **错**：其中含大量 opt-in real-IPC，属"未开启"而非 E-2。
   - "30 sidecar / 44 opt-in" 的二分 → **无法由我的实测复现**，已撤回，只保留类分布。
6. **方法教训**：本卡前两版都用"源码正则"推断 gate 与分类，因此连续两次被实跑证伪。
   本版所有数字改为**实测输出**（§4.1–§4.3 全部来自 `dotnet test` 的 "已跳过" 列表）。

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
- §4.2 的 30/44 总量二分可复现（与 74 行实测相加一致），但**逐类归属未逐条核实 attribute**。
## 8. 更新（2026-11-15，`GATE3-SIDECAR-COVERAGE-1`）

### 8.1 "书架只读"格 ⚠️ → ✅

`SIDECAR-REBUILD-1` 产出可用 sidecar 后，原来的 `[WritePolicySidecarFact]` 不再是"本环境跑不了"：

- 带 `NEWMANGA_CORECLIENT_SIDECAR_DIR` 跑 **App.Tests = 957 / 0 / 4 / 961**（无夹具 **950 / 0 / 11**）；
- 差集得到 **7 个转绿**测试，定向复跑 **7 passed / 0 skipped**；
- 其中 `WritePolicyUiIntegrationTests.DefaultController_IsWritable_AndParityFalse_IsReadOnlyWithReason`
  正是本格的证据。⇒ **本格改 ✅。**

**一处澄清**：本矩阵原先把 `WritePolicyUiTests` 与 `[WritePolicySidecarFact]` 混称。
实际是**两个类** —— `WritePolicyUiTests`（4 个普通 `[Fact]`）与
`WritePolicyUiIntegrationTests`（`[WritePolicySidecarFact]`）。已在上表更正。

### 8.2 skip 总量口径必须分开写

| 口径 | Host | CoreClient | App | 合计 |
|---|---|---|---|---|
| **无夹具** | 74 | 26 | 11 | **111**（§5 原先只写了这个） |
| **带新 sidecar** | 44 | 0 | 4 | **48** |

App 的 4 个（带夹具仍 skip）经差集确认是 **opt-in gated**（性能门控 / 崩溃注入 ×2 / 真进程启动矩阵），
**不是** sidecar 缺失。今后引用 skip 数**必须写明口径**。

### 8.3 7 个转绿的测试（FQN）

`StartupSelfCheckUiTests.SelfCheckFailure_IsVisibleInTheSnapshot`；
`RunControllerHostIntegrationTests.RunCommands_WhenReadOnly_PublishHostReadOnly` /
`…RunCommands_StartSuccessfulRun_ProjectRealPerPageState_AndReuseKey` /
`…RunCommands_MapCoreErrors_AndReuseIdempotencyKeys`；
`WritePolicyUiIntegrationTests.DefaultController_IsWritable_AndParityFalse_IsReadOnlyWithReason`；
`CreateChapterHostIntegrationTests.HostController_CreateChapter_SucceedsThenMapsCoreFailures` /
`…HostController_CreateChapter_WhenReadOnly_PublishesHostReadOnly`。

### 8.4 条件 3 仍未 MET

仍有 **48 个带夹具 skip**（Host 44 + App 4）、§0 未纳范围的 GUI 流程、真机走查。
本更新**只**把矩阵内 ❌ 与 ⚠️ 的**可见格**清零，**不**等于条件 3 满足。
## 9. 最后一个 ⚠️ 格闭合（2026-11-15，`GATE3-SETTINGS-SHORTCUT-1`）

矩阵 §3 的「设置 / 快捷键」格原为 ⚠️，证据只有 `ConsoleSpaceUsesWorkbenchConsoleAndSettingsRemainANonSpaceEntry`
—— 那证明的是"设置不是 Space 入口"，**不等于**"在设置页时全局快捷键仍然生效"。

**代码事实**（先读后写，未猜）：`AppShellViewModel.HandleKey` 的路由是
"workspace 先否决，再 shell KeyMap"，只有 `workspace.TryHandleKey(...)` 返回 `true` 才会**短路**掉 KeyMap。
而 `ConsoleWorkspaceView.TryHandleKey => false`（`WorkspaceAdapters.cs`），
`LibraryWorkspaceAdapter` 同样 `=> false`；只有 `StudioWorkspaceAdapter` 有选择性处理（R-17 Studio 键）。

**新增测试**：`NewManga.App.Tests.SettingsSpaceShortcutTests.ConsoleSpace_DoesNotSwallowGlobalShortcuts`

- `Ctrl+D3` → 断言 `State.CurrentSpace == SpaceId.Console`（确实在设置空间）；
- **从 Console 按 `Ctrl+K`** → 断言被处理且 `IsPaletteOpen`（全局快捷键没被空间吞掉）；
- `Esc` 关闭面板；`Ctrl+D2` → 断言回到 `SpaceId.Studio`（离开空间也正常）。

**判别力实测**：把 `ConsoleWorkspaceView.TryHandleKey` 临时改为 `=> true`（吞掉所有键）→ 该测试**变红**；
还原后通过，`PROBE` 标记计数 0（无残留）。⇒ 它真的守护"设置空间不吞键"。

**无夹具回归**：App.Tests **951 / 0 / 11 / 962**（新增 1 个测试；**skip 仍 11，未新增**）。

### 9.1 条件 3 矩阵的 ❌ / ⚠️ 均已清零

- **❌ 格：0**（`SETTINGS-ERROR-STATE-1` 清掉最后一个）。
- **⚠️ 格：0**（本卡清掉「设置 / 快捷键」）。

**这仍然不等于条件 3 MET**：带夹具 skip 仍有 **48**（Host 44 + App 4，均 opt-in/需真实 IPC）、
矩阵 §0 未纳范围的 GUI 流程（源恢复/沉浸阅读等）、真机走查未做。
## 10. 扩容：§0 未纳的 4 个 GUI 流程（2026-11-15，`GATE3-MATRIX-EXPAND-1`）

§0 声明过"4 页 × 13 类不等于整个产品 GUI 无缺口"，并点名了回收站/命令面板/源恢复/沉浸。本节把它们纳入评估。

### 10.1 实测（全部无夹具即可执行，0 skip）

| 流程 | 测试类（`NewManga.App.Tests`） | 实测 |
|---|---|---|
| **回收站** | `TrashUiTests` | **47 passed / 0 failed / 0 skipped** |
| **源恢复** | `SourceRecoveryUiTests` | **18 / 0 / 0** |
| **沉浸阅读窗口** | `V2ImmersiveReaderTests` | **4 / 0 / 0** |
| **F11 沉浸开关** | `F11HotkeyTests` | **9 / 0 / 0** |
| **命令面板（焦点/键盘）** | `FluentCommandPaletteFocusTests` | **1 / 0 / 0** |
| 组合 filter（以上全部） | — | **80 / 0 / 0**（比五类和 79 多 1，来自 `~CommandPalette` 另匹配到的类；不据此外推） |

**重要**：这五个类**不需要 sidecar**（0 skipped），所以它们是**当前环境就能反复复跑**的覆盖，
不是"等环境"的空白 —— 这一点与 §3 里那些 `[SidecarFact]` 的格不同。

### 10.2 逐流程的覆盖与缺口（**类名存在 ≠ 语义完整**）

| 流程 | 测试类**覆盖了什么**（从类与方法名可对应） | **仍缺什么**（本卡未验证） |
|---|---|---|
| 回收站 | 软删、恢复、彻底删除的 UI 交互与确认；保护语义的 UI 侧 | **ADJ-001 的完整保护矩阵**（软删/自动清理/显式彻底删除三层）是否逐条有测试，**未逐条核对**；真实文件层行为不在本类 |
| 源恢复 | `DiagnoseSourceRecoveryAsync` / `ReauthorizeSourceAsync` / `ResetSourceAsync` 的 UI 流程（18 个） | Host/Core 侧的 `source_resync` 编排在 **Host.Tests**（`Fea11HostAuthTests` / `Fea11HostAuthIpcTests`），本卡**未跑**它们；两层的衔接未作为一个端到端用例验证 |
| 沉浸阅读 | `V2ImmersiveReaderTests` 4 个 + `F11HotkeyTests` 9 个：F11 开关、Esc 阶梯、回到原页 | **真实窗口全屏/边框切换**在 headless 下不可验；真机走查仍缺 |
| 命令面板 | `FluentCommandPaletteFocusTests` 1 个：焦点行为 | **条目内容正确性、执行结果、Esc 关闭**在 `GATE3-SETTINGS-SHORTCUT-1` 的测试里间接覆盖了"打开/Esc/关闭"，但**条目逐项执行**未覆盖 |

### 10.3 本节的边界

- 上表**只**证明"这些流程有可执行的 GUI 测试且当前全绿"，**不**证明它们语义完整。
- `TrashUiTests` 的 47 与 `SourceRecoveryUiTests` 的 18 是**类级**数字；本卡**没有**逐条核对每个方法
  对应哪个产品语义 —— 那需要按方法名逐个读，属后续工作。
- **条件 3 仍不判 MET**：带夹具 skip 仍有 48、真机走查未做、上述逐流程缺口未闭合。
## 11. Host 44 个 skip 的归因与 opt-in 实测（2026-11-15，`GATE3-HOST-SKIP-TRIAGE-1`）

### 11.1 44 个 skip 需要 **opt-in 开关**，不是 sidecar 缺失

抽查 4 个类的 attribute：`Fea11ScanIpcFact` 的条件是 `NEWMANGA_FEA11_IPC != "1"`（其余同型）。
全 Host.Tests 的 opt-in 变量统计：`NEWMANGA_BUILD_PYTHON` 22 次、`NEWMANGA_FEA11_IPC` 8 次、
`NEWMANGA_FEA09_IPC` 3 次、`NEWMANGA_FEA11_CRASH_STATE` 2 次、`NEWMANGA_FEA12_UI_IPC` / `FEA10_IPC` /
`CORE_TILE_E2E` / `REAL_SHELL*` / `WORKSPACE_ROOT` 各 1–3 次。

⇒ 这与 §5 旧口径"大部分需 sidecar"**不完全一致**，本节更正为"需 opt-in 环境开关"。

### 11.2 打开 opt-in 后的实测（★ 重要）

```
379 passed / 15 failed / 1 skipped / 395   (1m10s)
```

对比未开 opt-in（带 sidecar）：**349 / 2~3 / 44 / 395**。

| 指标 | 未开 opt-in | 开 opt-in |
|---|---|---|
| pass | 349 | **379** |
| fail | 2~3 | **15** |
| skip | 44 | **1** |

**skip 44→1：44 个里 43 个真的执行了。**

### 11.3 15 个失败的归因

| 归因 | 数量 | 明细 |
|---|---|---|
| **环境**：Python Core 依赖缺失（`C:\Python314` 无 torch 等） | 3 | `Fea09RealIpcTests`、`Fea09UiImportIpcProductionTests` ×2（另 1 个 `E_` 亦同族） |
| **环境**：缺 `NEWMANGA_FEA11_CRASH_STATE` | 2 | `Fea11HostAuthIpcTests.CrashPoint_Park/Recover` |
| **★ schema 版本**：`Assert.Equal(9, schema_version)` vs 实际 **v14** | **7+** | `Fea11HostAuthIpcTests` ×2、`Fea11Residual4AIpcTests` ×4、`Fea11SourceIpcTests` ×2 |
| 原有（与 opt-in 无关） | 2 | `GrantIssuerTests.Import_…`、`Fea11WatchHostRuntimeTests`（`SOURCE_REGISTRY_BUSY`，已知 flaky） |

### 11.4 核心发现：`schema_version` 硬编码 9

```
Fea11HostAuthIpcTests.cs:418    Assert.Equal(9, seed.GetProperty("schema_version").GetInt32());
Fea11Residual4AIpcTests.cs:719  Assert.Equal(9, seed.GetProperty("schema_version").GetInt32());
Fea11SourceIpcTests.cs:63       Assert.Equal(9, receipt.GetProperty("schema_version").GetInt32());
```

新 sidecar 启动打印 `[core.schema] applied 14 migration(s) up to v14` ⇒ **schema_version = 14**。

⇒ **至少 7 个失败是"测试硬编码旧版本"，不是产品缺陷**；但这暴露了"换 sidecar / schema 升版
会让这些测试红"的真实兼容缺口。

**本卡不修**：改成 `== 14` 只是换硬编码；改成 `>= 9` 是**放宽断言**（纪律禁止）。
正确做法（读写产品常量，或断言 `>=9 且 <= 当前最大值`）需 DSH 裁决，且要先确认 v14 是**预期版本**
而非本地漂移。

### 11.5 对条件 3 的影响（诚实口径）

- **覆盖是可执行的**：43/44 在 opt-in 下真的跑了 —— 这比"44 个都跑不了"强。
- **但换 sidecar 引入了版本兼容缺口**：15 红里有 7+ 是 schema 版本、5 是环境依赖、2 原有。
- **不能说条件 3 变好**；条件 3 **仍不判 MET**。
