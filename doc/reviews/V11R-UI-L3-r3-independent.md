# 独立审查报告 · 第三轮（V11R 新 UI 终审 · L3 前置 / M2·M3 判定）

**审查者**：reviewer（独立、只读，未参与实现；本轮唯一写操作为本文件）
**基准**：冻结的 FUSION_SPEC / DESIGN_SYSTEM / V11R_AVALONIA_CONTRACT / V11R_SCREEN_SPECS / 任务卡；Lead 裁定 R-16/R-17/R-18/R-19/R-21/R-22/R-23/R-24/R-25；前两轮审查结论。
**Pins（已核实均为 main 祖先，以 git object 为准）**
- ui-shell 代码：`09f8ad183`（`09f8ad183938d9a19253f4307d21a6b803b8f412`，I1 返修）；ui-shell 证据：`23217ac25`（curated）。
- ui-studio 终态：`19797be986dae1542108105c32641f85fe049114`（I1→I2a→I2b→I2c）。
- main 当前 `5f4a0eee5`（含 `22b57ca91` B-1 合并、`68dd925a6` B-3/B-4 合并）。B-2 pin 仍为 `f3da3aaf3`（证据未 curate，按 Lead 指示按代码审、证据记 P3）。
- Lead 实测 main `App 249 / DS 67 / ThemeEngine 229 / Host 42 / CoreClient 45` 全绿——**我未重跑**，仅以两个 pin 的日志做一致性抽查（shell pin：App 237/5、DS 40、ThemeEngine 159；studio pin：App 241/6、DS 67、ThemeEngine 189、Host 42/24、CoreClient 45/22）。

**纪律**：只读；未改任何 worktree/证据/代码；未运行 build/test；只从 git object 与既有日志取事实；不采信自述，凡"声称已修"均回代码与测试求证。

---

## 一、结论

| 对象 | 结论 | 一句话理由 |
|---|---|---|
| **ui-shell（B-1/B-2）** | **PASS_WITH_ISSUES** | B-1 的 r1 问题基本全关闭（证据污染 135→23 且可复核、真实 ScrollViewer 保留、C# 令牌化、断点统一、loading 骨架、证据强度补齐、R-19 证据纪律落地）；但 **Intel-1 侧只做了 2/3 工作面**（IWorkspaceView 仅 Library/Console，Studio 无适配、`StudioWorkspaceContent` 未在 XAML 绑定，仍挂 `StudioPendingView`）；B-2 的 r2 P2（轮询恢复/状态词表 R-23）**未关闭**，B-2 证据未 curate。 |
| **ui-studio（B-3/B-4）** | **PASS_WITH_ISSUES** | 两个 P1 与多数 P2 已实质关闭且断言真实（Region 命中修复、Modal 真焦点、R-16 单一选择、矩阵增量+滚动保持、Stop 二次确认、R-22 意图级幂等、7 态 ⊆ DS StatusCatalog、断点/字号 ⊆ DS 令牌）；但 **Gate 模态声称"聚焦取消/Esc 取消"而代码两者都没有（P1，安全确认不可键盘取消且证据声称已实现）**；作用域物化的 P1-B **测试被移除标 NOT_RUN**；证据层仍残留字面量/恒真断言/0 偏移与 4 个无生成器的孤儿 JSON、B-3/B-4 主 README 陈旧。 |
| **整体（INT-1 / M2 / M3 / L3）** | **未达 L3；M2 未达；M3 未达** | INT-1 四项前置：①PARTIAL、②CLOSED（代码层）、③PARTIAL、④**NOT_CLOSED（R-24 无共用 poller，Console 仍独立 1s 轮询且不恢复）**；main 默认入口仍是旧 MainWindow，Studio 未接线。 |

---

## 二、r1 / r2 问题关闭情况（逐条）

### 2.1 r1 · V11R-B-1（ui-shell）

| 项 | 状态 | 依据 / 文件:行 |
|---|---|---|
| P1 证据目录污染（135 文件 / 57 重复） | **CLOSED** | `verification/V11R-B-1` @ `23217ac25` 实为 **23 个文件**（我以 fresh archive 复核：`ls-tree` 23）；`CLEANUP.md` 记录"删除 115 个外任务文件（57 个 SHA-256 字节级重复 + 58 个外任务独有）"，并给出可复核的 PowerShell 命令；`curate.ps1` 为唯一入库入口（R-19）。 |
| P2 滚动保留是假的（同义反复） | **CLOSED** | `Views/V2/Library/LibraryView.axaml:64-69`（`BooksScroll` + `ScrollChanged`）；`LibraryView.axaml.cs` 的 `OnBooksScrollChanged`/`RestoreScrollOffset` 真实读写 `ScrollViewer.Offset`；`ConsoleView.axaml:80` + `ConsoleView.axaml.cs:42,46` 同构。断言真实：`V2ShellUiTests.cs:640-665` 先 `Offset=(0,180)` 再跨空间往返，断言 state 与 Offset 一致。 |
| P2 C# 裸设计值 | **CLOSED（限本 Owner 目录，登记 D-14/D-15）** | 新增 `Shell/V2/ShellLayout.cs`（令牌解析 + 断点/比例常量）；`AppShellViewModel` 的 Palette/Confirm/搜索/排序/卡片/详情宽度全部改为 `ShellLayout.*`；`V2ConformanceTests.cs:28-47` 新增 C# 扫描（Thickness/Corner/FontSize/Opacity/Brush/布局字面量）与 allowlist（仅 `Shell/V2/ShellLayout.cs`），`:136-176` 执行。 |
| P2 断点三套 | **CLOSED** | `ShellLayout.cs:18-20` 1600/1280/1024；`V2ConformanceTests.cs:178-190` 断言三个常量并**禁用 1400/1200**（`CSharpOldBreakpoint` 正则扫 C#+XAML）。 |
| P2 loading 无骨架但文案声称有 | **CLOSED** | `LibraryView.axaml:118-122` 改为"与书卡同尺寸的骨架网格（保留列宽/缝隙几何）"，删除自证文案；`screens/…13-library-loading-skeleton.png`（34,277B 真渲染）。 |
| P2 ImportDock 低报能力 | **CLOSED** | `ImportDockViewModel.cs:110,139,159` 全部改为"走 Core CreateChapter（V11R-A-1）"，类注释同步。 |
| P2 证据强度夸大（四列/36px） | **CLOSED** | `V2ShellUiTests.cs:306` `Assert.Equal(36, TopBand.Bounds.Height)`；`:311` `Assert.Equal(4, ColumnCount)`；`:627/:635` 1280→3 列、1024→4 列。 |
| P2 `IWorkspaceView`（契约 §6.1） | **PARTIAL** | 接口已定义且含 R-17：`Shell/V2/IWorkspaceView.cs:15-33`（`Space/CreateContent/OnActivated/OnDeactivated/TryHandleKey`）；仅 2/3 实现：`ViewModels/V2/Shell/WorkspaceAdapters.cs:15`（Library）、`:43`（Console），`AppShellV2.axaml.cs:43-44` 注册；**Studio 无适配**，`V2WorkspaceHost.axaml:16` 仍 `<v:StudioPendingView/>`（而 `AppShellViewModel.cs:333-352` 已备好 `StudioWorkspaceContent`/`IsStudioPlaceholderVisible` 却无任何 axaml 绑定）。 |
| P3 queued 符号 / 死常量 / 假计数 / 主题入口 | **CLOSED** | `DEVIATIONS.md D-8` 更正为 `·`；`AC_COVERAGE` P2.9/P2.10 记录删除 `NotWiredCreateChapter`、`AttentionMenu` 隐藏假计数、主题管理器统一 `Initialize()`。 |

### 2.2 r1 · V11R-B-3（ui-studio）

| 项 | 状态 | 依据 / 文件:行 |
|---|---|---|
| **P1 Region 鼠标命中/hover 死代码** | **CLOSED** | `StudioRegionOverlay.cs:111-115`：删除 `IsHitTestVisible=false`，改为 `Background=null`（空区不拦截拖拽、Box 为真实命中目标）；Box 指针处理器仍在 `:58-64` 且 `PointerPressed` 设 `Handled`。`I1-FIX.md P1-1` 说明 headless 指针合成不稳定、指针测试未随提交（follow-up），`region-interaction.json` 用 `RegionBox.Select()/Page.HoverRegion()` 走同一处理逻辑（证据方法为"控制路径"而非真实指针，见 §六 UNVERIFIED）。 |
| **P1 Modal 默认焦点写死** | **CLOSED** | `StudioLeaveModal.cs:88-121`：打开捕获 `FocusBeforeOpen` → `Loaded` 聚焦「取消」；`:148-160` Tab/Shift+Tab 焦点陷阱；关闭回焦。真断言：`V2StudioConformanceTests.cs:161-188` 用 `FocusManager.GetFocusedElement()` 断言；`modal-focus.json` `default_focus_is_cancel/focus_trap_tab/esc_cancelled/focus_restored_to_trigger` 全为真值。 |
| P2 保存失败文案透明 | **CLOSED** | `I1-FIX P2-3`；`modal-focus.json error_text_has_ds_class:true`。 |
| P2 多选被 Region 遮蔽（FUSION 硬规则 1） | **CLOSED** | `StudioSelection.cs:31,42-66,130,157`：`ResolvedScope` 让**显式多选优先**；所有读写路由到 `ShellState.Selection`（唯一权威），`SelectionSummary` 由 ResolvedScope 派生。 |
| P2 AC4 裸间距（样式表/C#） | **NOT_CLOSED（部分降级为字体/断点）** | `StudioTheme.axaml` 仍含 25+ 裸间距/尺寸：`Padding="8,0"/"6,2"/"12,8"/"6,4"/"8,4"/"2,0"/"10,4"`（:90,117,124,131,136,148,155,164,171,198,204,215,267,285,310,335,341,372,387）与 `Width="480"`(:328)、`Width/Height="8"`(:288-289)、`Height="20"`(:389)；`V2StudioConformanceTests.cs:50-108` 只扫 **status 符号 / FontSize / 断点**，不扫 Padding/Margin/Width。I1-FIX 已把 P2-5 记为未完成，I2c 只完成字号/断点/符号三块。 |
| P2 loading 骨架 | **PARTIAL** | 代码已用 DS Skeleton：`StudioPageWorkspace.cs:370-390`（Panel/Row/BookCard 三种变体）；测试断言 `skeleton_present:true`，但**截图 NOT_RUN**、`loading_observed:false`（`loading-skeleton.json`：`"screenshot": "NOT_RUN: loading window too short for a frame"`）→ loading 态无视觉证据。 |
| P2 错误三重复呈现 | **CLOSED（代码）/ 证据 PARTIAL** | `StudioPageWorkspace.cs:194-198` 错误块与 host banner 互斥（`HasErrorText && !HostBannerVisible`），`:303` 空叠层同步；但 `error-block.json`（visible_error_blocks:1）**在当前测试树中已无生成器**（见 §五.2）。 |
| P2 错误路径不完备 | **CLOSED** | `StudioPageViewModel.cs:846` 捕获 `InvalidOperationException/IOException/TimeoutException` → Error+ErrorText（不再逸出 async 视图）。 |
| P3 门禁随 Host 实时/死代码 | **CLOSED（代码）/证据 PARTIAL** | `StudioPageViewModel.cs:761,1714` `BuildGate()` 在 Host 快照变化时重建；`gate-live.json` 同样无生成器（§五.2）。 |
| P3 图标体系缺失 | **PARTIAL（登记）** | `DEVIATIONS.md` 已登记 HUD/检查器仍以字符占位、DS 图标集上收为 follow-up；本轮未上收。 |

### 2.3 r2 · V11R-B-4（ui-studio）

| 项 | 状态 | 依据 / 文件:行 |
|---|---|---|
| **P1 矩阵轮询全量重建 + 滚动被重置** | **CLOSED** | 数据层：`StudioBatchViewModel.cs:365` 新增 `ProjectionApplied` 事件、`:744` 每轮仅一次；视图层改为增量 `SyncFromProjection`（shape 稳定复用 cell，shape 变化才 Rebuild 并保存/恢复 `Scroll.Offset`）。真断言：`V2StudioBatchTests.cs:491-524`（60 行投影、`Offset=(0,240)` 非零、一次 poll 后 offset 仍 240、`ProjectionApplied` 恰 1 次、cell 数 600 不变）。`poll-incremental.json` 为真实值。 |
| **P1 作用域静默扩大** | **PARTIAL（代码 CLOSED / 测试 NOT_RUN）** | 代码：`StudioBatchViewModel.cs:1184-1203` `CanMaterializeScope()`；`:1205-1245` `BuildScope` 优先用 `Selection.ResolvedScope`（R-16）且仅 All 才落 chapter；`:1044-1057` `StartRunAsync` 对 null scope/提交中**就地说明并零调用**；`:1348-1361` `action.IsEnabled = CanMaterializeScope() && !_submitInFlight`。**但 I2a README 自述 P1-B 测试"已移除并标 NOT_RUN"，在全测试树中 grep `CanMaterializeScope/Unmaterializable/NeverWidens` = 0 命中** → 该 P1 仅靠代码，无回归测试。 |
| **P2 R-22 幂等键（新裁定）** | **CLOSED（Batch 侧）** | `StudioBatchViewModel.cs:1059` 意图级生成（`_intentIdempotencyKey ??=`）、失败保留、成功清空（`:1082`）、提交中禁用（`:1061,1353`）；真断言 `V2StudioBatchTests.cs:530-566`（失败保留、重试同键、成功清空）。**跨支不齐**：Console 仍要求手填键（见 §五.1），R-22 的"意图级生成"未在 Console 一致。SubmitInFlight 行为仅代码保证、无动态挂起测试（I2b README 已声明）。 |
| **P2 Gate 模态焦点/Esc（I2b 声称已修）** | **NOT_CLOSED（P1，见 §四）** | `StudioBatchControls.cs:485-517` Gate 卡仅有 scrim/文本/两个按钮，**无 `Focus()`、无 Esc 处理器**；全树 `IsGateConfirmOpen` 只有 4 处（VM 定义/置真/置假），无键盘分支。对比 I2b README「打开聚焦取消、Esc 取消」= 与代码不符。 |
| **P2 Stop 二次确认** | **CLOSED** | `StudioBatchViewModel.cs:521-545`（arm/取消/确认）；模态在 `StudioBatchControls.cs:748-800`（默认取消聚焦、Esc、scrim 点击取消）；真断言 `V2StudioBatchTests.cs:568-605`（取消零 Control 调用、确认恰 1 次）。`stop-confirm.json` 为真实计数。 |
| **P2 FontSize=10（不在刻度）** | **CLOSED** | `StudioBatchControls.cs:110,154` 改 `StudioMetrics.FontXs`；`StudioMetrics.cs` 读 `Nm.FontSize.Xs`（DS 令牌，fallback 11）。`V2StudioConformanceTests.cs:77-80` 扫描 FontSize 字面量。 |
| **P2 错误态复用空态「开始处理」** | **PARTIAL** | 行为已修：`StudioBatchControls.cs:660` 按钮点击在 `State==Error` 时改走 `RefreshAsync()`（不再发起新 Run），`:730` Error 时隐藏空态卡（`error-state.json empty_card_hidden:true`）。但**按钮文案仍是「开始处理」**（`:660`），与 I2b README「主按钮改「重试读取」」不符；测试 `:607-632` **未断言重试语义/按钮文案**，仅记录 `primary_button`。 |
| **P2 仅 Batch 可见时轮询** | **NOT_CLOSED** | 轮询仍是 **attach/detach 驱动**：`StudioBatchControls.cs:596-611`（`AttachedToVisualTree → StartPolling`；`DetachedFromVisualTree → StopPolling`），而 Page/Batch 两工作区常驻树、只切 `IsVisible`（`StudioWorkspaceView.axaml.cs:218-223`）→ Page 模式仍在轮询。证据**自证失败**：`polling-visibility.json "no_reads_in_page_mode_observed": false`；对应测试 `V2StudioBatchTests.cs:634-655` **无任何断言**（注释称"计时竞态，改为记录 observed"）——测试恒通过，属 R-25 的"无断言测试"。 |
| **P2 证据 R-25（字面量/恒真/非 0 偏移）** | **NOT_CLOSED** | ①`gate.json impact_text`：`V2StudioBatchTests.cs:305` 写字面量，且与真实 `GateImpactText`（"门禁未清（失败 2 · 阻塞 1） · 作用域 · 选中 1 页 · …"）不一致；②`drilldown.json scroll_kept`：`:381/:400/:412` 仍取从未设置过的 `Offset`（0）比较，0==0 同义反复；③`:401` **占位恒真断言 `Assert.Contains("NOT_WIRED","NOT_WIRED")` 仍在**；④`:267` 死变量 `startsBefore` 仍在。仅新增的 I2 JSON（poll-incremental/intent-key/stop-confirm）为真实值。 |

---

## 三、INT-1 前置四项

| # | 前置 | 判定 | 证据 |
|---|---|---|---|
| ① | `IWorkspaceView`（含 `TryHandleKey`）被 Shell 与三个工作面实现 | **PARTIAL（2/3）** | 接口：`Shell/V2/IWorkspaceView.cs:15-33`（含 R-17 `TryHandleKey`）；实现：`WorkspaceAdapters.cs:15` Library、`:43` Console；**Studio 无实现**（studio pin 中 `StudioWorkspaceView.axaml.cs:17-20` 仍写"接口不在本分支"，且全 studio src grep `TryHandleKey` 仅命中旧 ReaderWorkbenchPages）；`AppShellV2.axaml.cs:43-44` 只注册两个；`V2WorkspaceHost.axaml:16` Studio 仍是 `StudioPendingView`，而 VM 侧 `AppShellViewModel.cs:333-352` 的 `StudioWorkspaceContent`/`IsStudioPlaceholderVisible` **没有任何 axaml 绑定**。 |
| ② | 单一 selection（R-16：ShellState 权威、Studio 投影） | **CLOSED（代码层）／运行时接线待 INT-1** | `ShellState.cs:169-267`（`SelectionChanged`/`SetSelection`/Select*）；`StudioSelection.cs:42-66,130,157`（投影+路由，不保留第二副本，多选优先）；Library/Console VM 均写 `ShellState`。运行时 Studio VM 尚未由 shell 构造注入（`StudioWorkspaceViewModel.cs:17-28` 接受 `StudioSelection`，但无生产调用者）。 |
| ③ | 键盘仲裁（shell 先问工作区，Studio Tab/Esc 能被接收） | **PARTIAL** | 机制已就绪：`AppShellViewModel.cs:720-741`（overlay/IME 之后先 `workspace.TryHandleKey`，false 才进 KeyMap）；`V2WorkspaceIntegrationTests` 覆盖 hook 顺序与首拒；`SwitchSpace` 先 deactivate 后 activate（`:557-569`）。**缺口**：Studio 未实现 `TryHandleKey`（无该方法），B-3 仍是 `StudioWorkspaceView.OnKeyDown`（`:145-167`）+ shell TopLevel Tunnel（`AppShellV2.axaml.cs:75,118-122`）→ 集成后 shell 会先吞 Tab/Esc，Studio 收不到；`keyboard-seam.json` 声称 `try_handle_key_exposed:true` 与代码不符（见 §四 P1-2）。 |
| ④ | Run 投影单一来源（R-24：Console/Batch 共用同一 poller/映射，Stop 一致确认） | **NOT_CLOSED** | 无共用 poller/映射类（全树 grep `IRunProjectionPoller/RunProjectionPoller` = 0）；Console 仍自有 `DispatcherTimer` 1s（`ConsoleViewModel.cs:509-511,539`）+ `ConsoleStatusText` 映射；Batch 自有可注入 750ms poller（`StudioBatchViewModel.cs:339`）+ `StudioStates` 映射；Page 另有 `IRunDataSource`（`StudioPageViewModel.cs:274,315,661`，默认 `NotWiredRunDataSource`）。Stop 确认语义已一致（两侧都确认），但实现两份。Console 切回不恢复轮询（`ConsoleViewModel.cs:289-297` 只恢复分区/滚动，`StartRunPolling` 唯一调用点 `:539`）。 |

---

## 四、本轮新发现（P1/P2/P3）

### P1

| 位置 | 问题 | 依据 | 建议修法 |
|---|---|---|---|
| `StudioBatchControls.cs:485-517`（Gate 模态）＋ `verification/V11R-B-4-I2b/README.md`「Gate 模态：…打开聚焦「取消」、`Esc` 取消」＋ `verification/V11R-B-4/gate.json` | **门禁确认模态不具备键盘/取消能力，且证据/README 声称已实现**：Gate 卡无 `Focus()`、无 Esc；scrim 无 PointerPressed（点击外部也不取消）→ 键盘用户的唯一出口是把指针移到「取消」按钮。而同一 pin 的 Stop 模态两者都有（`:777-799`），证明可实现却漏做。**用户后果**：门禁确认弹出后 Esc 无效、焦点仍留在被遮住的矩阵上，Tab 可穿到背后控件（非模态）。 | DESIGN_SYSTEM §6.2 `Modal`（默认焦点取消、Esc 关闭）、§8 浮层焦点/焦点陷阱；R-25（证据不得声称未实现的行为） | 复用 Stop 模态模式：打开 `Dispatcher.Post(()=>cancel.Focus(), Loaded)`、`KeyDown` 捕获 Esc→`CancelGate()`、Tab 焦点陷阱、scrim 点击=Cancel；补一条断言 `FocusManager` 与 Esc→零 StartRun 的测试；`I2b README` 与 `gate.json` 按真实结果重写。 |
| `verification/V11R-B-3/keyboard-seam.json`（`"try_handle_key_exposed": true`）＋ `V11R-B-3/I1-FIX.md` P2-9「`StudioWorkspaceView.TryHandleKey(key, modifiers)` 已实现」 | **证据与交付文档声称存在的方法在代码中不存在**（studio pin 全 src grep `TryHandleKey` 只命中旧 `ReaderWorkbenchPages.cs:2629`；`StudioWorkspaceView` 只有 `OnKeyDown`）。该字段直接支撑 INT-1 前置③的"已具备"，属 R-25 禁止的"证据声称未实现行为"；同时该 JSON 在当前测试树中**已无生成器**（见 §五.2），属陈旧产物。 | R-25；R-17；INT-1 前置③ | 要么真的在 `StudioWorkspaceView` 实现 `bool TryHandleKey(KeyEventArgs, ShellState)`（Page/Batch 分派 + IME 让位）并在 shell 注册后接线，要么删除该 JSON 字段并把 I1-FIX 的 P2-9 改回"未实现"；证据只由测试写入。 |

### P2

| 位置 | 问题 | 建议 |
|---|---|---|
| `V2StudioBatchTests.cs:634-655` + `polling-visibility.json` | 轮询可见性测试**零断言**（读前后计数只写 JSON，`no_reads_in_page_mode_observed:false`），测试恒通过；实现仍是 attach 驱动（`StudioBatchControls.cs:596-611`）→ 与 R-24/README 声明不符 | 让 Batch 工作区订阅 `IsVisibleChanged`（或由 `StudioWorkspaceView.ApplyMode` 调 `StartPolling/StopPolling`），并断言"Page 模式 N 个 poll 周期内投影读取次数增量=0"（允许一次 stopped 边界）；失败则该测试应红。 |
| `V2StudioBatchTests.cs:305,381-412,401,267` | R-25 残留：`impact_text` 字面量且与真实值不符；`scroll_kept` 0==0；占位恒真断言；死变量 | 全部改为真实对象读取：`impact_text = batch.GateImpactText`；drilldown 前设非 0 `Offset`；删除占位断言与死变量；删除 `host_accessed: host is not null` 这类恒真字段。 |
| `V2StudioPageTests.cs:443` | `leave-modal.json` 仍写死 `modal_default_focus:"取消"`（I1-FIX 已承认待 curate；I2c 另有真实 `modal-focus.json`） | 改为读取 `FocusManager` 的实际焦点元素；或删除该字段并只保留真实来源。 |
| `verification/V11R-B-3/{keyboard-seam,selection-authority,error-block,gate-live}.json` | **4 个孤儿证据**：当前测试树无任何生成器（grep 文件名/关键词=0），内容声称 I1 已修项，但无测试支撑 | 删除或在对应测试中恢复生成器并断言；B-3 主 README/AC 同步更新（当前仍写"App 166 / 21 tests / 实现 commit 4317624b1 / 10 阶段"，与 pin 的 App 241/6、29+ 测试不符）。 |
| `verification/V11R-B-4/README.md` | 主 README 陈旧：仍写 App 185/29、`V2StudioBatchTests 8 用例`、轮询"仅 Batch 可见"、无 I2a/I2b/I2c 内容（实际 App 241/6、Batch 13 用例、I2 5 用例） | 按 pin 重写质量门与交付清单，或把 I2a/I2b/I2c README 合并为主 README 的"返修记录"节。 |
| `StudioWorkspaceViewModel.cs:63-69`；`StudioPageViewModel.cs:661,682-683,1764`；`ShellCommands.cs:50,53`；`ShellItems.cs:76` | NOT_WIRED 文案陈旧：仍称 "Batch 模式在 V11R-B-4 交付 / Run 投影（V11R-A-2）未合入 / 能力待接入：CreateChapterAsync 尚未合入"，而 A-1/A-2/B-4 均已合入（main 与 pin 内）；`BuildNotWiredInventory` 生成的 `not-wired.json` 因而含过期条目 | 改为真实原因（无活动 Run / 无投影读数 / Studio 未由 shell 接线），并重新生成 `not-wired.json`/`page-load.json`；`BatchAvailable=false` 常量删除或改为 `Batch.IsWired`。 |
| `ConsoleViewModel.cs:509-539,282-297` | **r2 P2 未关闭**：切出 Console 停轮询、切回不恢复（`RestoreViewState` 只恢复分区/滚动）；"刷新 Run"也不重启（仅 `LoadRunCommand→LoadRunAsync:539`） | `OnActivated`（或 `RestoreViewState`）在 `HasRunLoaded && _runId != null` 时 `StartRunPolling()`；补"加载 Run→Ctrl+1→Ctrl+3→轮询恢复"测试。 |
| `ConsoleItems.cs:51`（`Status => IsWired ? Done : Blocked`）、`:266`（凭据 `Done : NotStarted`）、`:348-359`（绑定 `Done/NotStarted`）＋ `ConsoleView.axaml:39,64` | **R-23 未落地**：状态词表仍表达"是否接入/是否已保存"（分区显示 `● 完成`、凭据显示 `○ 未开始`） | 分区/凭据改中性 capability 文案（"已接入/待接入""已保存/未保存"）+ 中性色，或注册专用 `CapabilityBadge`；`V2ConsoleUiTests` 增加"状态符号不得为 Done/Blocked 语义"断言。 |
| `StudioTheme.axaml`（25+ 裸 Padding/Width，见 §二.2）＋ `V2StudioConformanceTests.cs:50-91` | **r1 P2 AC4 未关闭**：样式表裸间距仍在，conformance 只扫符号/字号/断点 | 优先把高频 padding 迁到 `Nm.Padding`/`Nm.Space`；扩展 conformance 扫 `Padding|Margin|Width|Height` 字面量（allowlist `StudioMetrics.cs`）；无法 token 化的登记 §2.4 例外并在 DEVIATIONS 说明。 |
| `keys…`/`iframe`—`StudioBatchControls.cs:581-583` + 测试缺位 | Gate 模态只是"行跨 5"的局部覆盖；未见 `StudioBatchWorkspace` 层面对"模态打开时背后控件不可交互"的处理（RowSpan 只解决视觉覆盖，背后按钮仍可 Tab/点击） | 与 P1 一并补：打开时 `IsEnabled=false` 或 `IsHitTestVisible=false` 背景层 + 焦点陷阱；补"Gate 打开时点动作条无效"断言。 |
| `V2StudioBatchTests.cs`（无 scope 测试） | R-22/P1-B 相关防线只有代码：`CanMaterializeScope` 无任何测试 | 见 P1-B：用一个稳定 setup（构造 `ShellState` 直接 `ClearMultiPage` 后 `ExecuteActionAsync`）断言"动作禁用 + 零 StartRun + BuildScope 不返回 chapter"。 |

### P3

| 位置 | 问题 | 建议 |
|---|---|---|
| `V2StudioBatchTests.cs:660` + `:738` | Error 态按钮文案仍是「开始处理」、tooltip 仍是「开始处理（翻译全部）」，与 I2b README「主按钮改重试读取」不符（行为已改，标签未改） | 按 `State` 切换文案（"重试读取"）与 tooltip；证据字段改为真实文案。 |
| `V2StudioPageTests.cs:451-503`（HudRing Esc） | r1 的 UNVERIFIED 仍在：只断言一次 Esc 后 `SelectedRegion==null`，未断言"先收检查器→再清选区"的逐级顺序；1600 下 `InspectorExpanded` 默认 true 与断言存在张力 | 断言两次 Esc 的中间态（`InspectorExpanded==false && SelectedRegion!=null` 后第二次才 null）。 |
| `verification/V11R-B-2/*` | 证据仍是 `f3da3aaf3` 时代（17 文件、AC 声称"切回恢复轮询/离开分区停"两条与代码不符） | Lead 已要求 curate；本报告按代码审，curate 后按 R-25 复核上述两条声明。 |
| `views/V2/Shell/V2WorkspaceHost.axaml` | Studio 分支半接线：VM 已有 `StudioWorkspaceContent`/`IsStudioPlaceholderVisible`，XAML 仍用 `StudioPendingView` 且无 placeholder 绑定 | INT-1 一并修（见 §七 最小修复集）。 |
| 图标/装饰 | HUD/检查器页签仍用字符占位；DS 图标集已交付但未上收（DEVIATIONS 已登记） | INT-1 后替换，或维持登记并在 L3 声明为已知偏差。 |
| shell DS 上收 | ui-shell pin 的 DS 仍是 Remediation 之前版本（无 `Nm.Size.Breakpoint.*`/`StatusCatalog`），故 shell 侧仍本地 `NmStatusInfo`/`StatusBadge`/`ShellLayout` 断点常量（D-14 已登记）；但 **main 上 DS 已交付**这些，合并后 shell 代码未跟进 | INT-1 阶段把 shell 的 `Statuses.cs`/`StatusBadge` 切 DS `StatusCatalog`、`ShellLayout` 断点切 `Nm.Size.Breakpoint.*`，删除本地符号表。 |

---

## 五、证据可信度（R-25 专项）

1. **B-1：达标**。23 个文件全部为本任务产物（fresh archive 复核）；`CLEANUP.md` 有可复核命令；`curate.ps1` 唯一入库入口；关键断言为真实值（36px/4 列/真实 Offset/hook 顺序），无字面量-backed JSON。
2. **B-3：部分达标**。I2c 新增的 `modal-focus.json`/`conformance.json`/`region-interaction.json` 由测试真实写出（focus 断言真实）；但仍有 **4 个孤儿 JSON**（keyboard-seam / selection-authority / error-block / gate-live，无生成器）与 **1 个字面量字段**（`leave-modal.json modal_default_focus`）、陈旧 `not-wired.json`；主 README 与 pin 状态不符。
3. **B-4：未达标**。`gate.json impact_text` 字面量且与实现不一致；`drilldown.json scroll_kept` 为 0 偏移同义反复；`Assert.Contains("NOT_WIRED","NOT_WIRED")` 占位断言仍在（R-25 明文禁止恒真断言）；`polling-visibility.json` 诚实记录了失败（observed=false）但对应测试零断言；主 README 陈旧。**正面**：I2 新增的 poll-incremental/intent-key/stop-confirm 三项为真实测量值（含非 0 偏移、真实调用计数）。
4. **NOT_RUN 诚实性**：I2a「P1-B 测试 NOT_RUN」、I2b「SubmitInFlight 未动态测」「轮询计数改 observed」、I2c「loading 截图 NOT_RUN」均**明确声明**，属诚实披露（但按 R-25，披露不能替代断言，相关项仍判 PARTIAL/NOT_CLOSED）。
5. **图片证据**：B-1 13 张（含 loading 骨架）与 B-3/B-4 既有截图为 headless 真渲染（我抽查 B-1 loading、B-4 矩阵截图，非占位）；`theme-canvas-*` 哈希方法沿用上轮结论（同一 blob → diffPixels=0 必然，方法有效但只覆盖页面图区域）。
6. **日志未由我重跑**：所有 App/DS/ThemeEngine 计数来自 pin 内日志与 Lead 实测；仅做"日志↔代码↔断言"一致性抽查，未发现矛盾（但 shell pin 的 app 237/5 与 main 249 的差额可由合并新增测试解释）。

---

## 六、已核实正确的关键点

1. **B-1 证据治理闭环**：R-19 落为可执行机制（temp-first、显式 curate、唯一文件名、失败重试不炸测试），并在 `CLEANUP.md` 给出可复核命令——这是本项目首个可复核的证据卫生样例。
2. **真实滚动保留**：`ScrollChanged` 写回 + `OnActivated` 恢复 + 非 0 Offset 往返断言（Library 与 Console 同构），r1 的同义反复已消除。
3. **C# 令牌化 + conformance 双层防线**：`ShellLayout` 单点解析 + C# 扫描 allowlist + 断点常量断言 + 禁用旧阈值正则，可防回归。
4. **B-3 Region 命中修复正确**：`Background=null` 而非隐藏整层，Box 为命中目标且 Handled，既恢复 hover/选择又不误吞拖拽——是正确的最小修复。
5. **Modal 真焦点**：`StudioLeaveModal` 具备打开捕获→加载优先级聚焦取消→Tab 陷阱→关闭回焦的完整链，且有 `FocusManager` 真断言与证据。
6. **R-16 单一选择**：`ShellState.Selection` 权威 + `StudioSelection` 投影路由 + `ResolvedScope`（多选优先），并在 B-4 的 `BuildScope`/`CanMaterializeScope` 复用——跨支语义终于一致。
7. **B-4 增量矩阵**：单次 `ProjectionApplied` + shape 稳定复用 cell + 非 0 偏移保持，60×10=600 cell 断言通过；r2 的 P1-A（重建风暴/滚动重置）实质关闭。
8. **R-22（Batch 侧）与 Stop 确认**：意图级键生成/失败保留/成功清空/提交中禁用，Stop arm→cancel 零调用→confirm 一次，均为真实断言；DS 符号（`StatusCatalog`/`NmStatusSymbols`）与断点/字号令牌在 Studio 已上收，`StudioStates` 不再本地发明符号。
9. **shell 键盘机理**：`IWorkspaceView.TryHandleKey` 首拒权在 overlay/IME 之后、KeyMap 之前；IntegrationTests 覆盖 hook 顺序与首拒；`SwitchSpace/SetStudioMode` 严格 deactivate→activate。

---

## 七、UNVERIFIED（只读环境无法确认）

| 项 | 原因 | 建议验证 |
|---|---|---|
| 两个 pin 的构建/测试 | 未重跑（禁写 bin/obj） | 集成机重跑 shell pin（App 237/5）、studio pin（App 241/6 + `--filter V2Studio`）并与日志 diff。 |
| Gate 模态真实行为 | 代码静态可证无 focus/Esc；headless 可达性仍需运行确认 | 单测：打开 gate → 断言 `FocusManager` 为取消按钮；按 Esc → `IsGateConfirmOpen==false` 且零 StartRun。 |
| Studio 指针命中（Region） | I1-FIX 声明 headless 指针合成不稳定；证据走控制路径 | 真实窗口或 Windows 输入层点击 Region，断言 hovered/selected class 与 `SelectedRegion`。 |
| `Polling_IsVisibilityControlled` 的真实读取数 | 测试仅 observed、无断言；headless 计时竞态 | 注入固定 interval + 手动 `Dispatcher.UIThread.RunJobs()` 驱动 tick，断言 Page 模式零读取；或直接断言 `IsPolling==false`（修复后）。 |
| P1-B 作用域物化 | 测试被移除（NOT_RUN） | 补稳定 setup（直接操作 `ShellState` 清理多选后调用 `ExecuteActionAsync`），断言 action disabled + 零 StartRun + `BuildScope()` 不含 chapter。 |
| 240 页真实矩阵性能 | 测试用 60 行；生产 240 行未测 | 集成机 240 页投影跑滚动/框选，观测帧时间与 GC；确认增量路径不随行数线性重建。 |
| 真实 Core E2E / DPI 三档 | 沿用 NOT_RUN | INT-1 用真实 sidecar 跑 E2E-01，DPI 100/150/200 截图。 |
| B-3 Esc 逐级顺序 | 测试未断言中间态 | 见 §四 P3。 |

---

## 八、最终判断

### 是否可合入 main
**代码层面：可（已合入且 main 绿）。但"可合入"不等于"可交付"**：本报告把 §四 P1 与 §三 ④ 作为**进入 INT-1 的硬前置**；在默认入口仍是旧 MainWindow 的前提下，合入不改变产品行为，可接受。**切换默认入口（INT-1）之前必须关闭**：

- **P1-1** Gate 模态焦点/Esc（安全确认 + R-25 证据声称不实）；
- **P1-2** Studio `TryHandleKey` 缺失（证据谎报）→ 必须先真实现，否则 ③ 无法成立；
- **R-24**（④）：Console/Batch/Page 共用单一 Run 投影 poller + Console 恢复轮询 + 统一映射；否则同一 Run 在两个空间显示不同口径、Console 数据冻结；
- **INT-1 接线**：Studio `IWorkspaceView` 适配 + `AppShell2` 注册 + `V2WorkspaceHost` 绑定 Studio 内容/占位 + MainWindow 切换；
- **R-25 清理**：gate/drilldown/占位断言/孤儿 JSON/陈旧 README/`not-wired` 文案，全部按真实值重建；
- **R-23**（B-2 状态词表）、**R-22**（Console 与 R-22 对齐：意图级生成/重试复用，而不是手填）。

### 是否达到 M2（新壳可用）：**否**
- 默认入口未切：`App.axaml.cs:62` 仍 `new MainWindow(controller, options)`，`Views/MainWindow.axaml` 仍是旧 `PageHost` 布局；新壳 `AppShellV2` 只在 headless 测试中可用。
- Studio 未在新壳内可达：`V2WorkspaceHost.axaml:16` 仍 `StudioPendingView`；无 Studio 适配/注册；B-2 证据未 curate、轮询/状态词表问题未修。
- 因此"新壳可用"目前仅覆盖 Library/Console 两个工作面，且 Console 仍有功能回归（轮询不恢复）。

### 是否达到 M3（全工作面）：**否**
- 缺 Theme Studio 真实实现（C-2）、Studio 未接线（INT-1）、R-24 未落地、键盘仲裁仅 2/3、DS 上收 shell 侧未完成（StatusCatalog/断点/图标）、Console 状态词表 R-23 未落地。
- L3 的现场验收前提（真实 Core E2E、DPI 三档、240 页矩阵性能、Gate 安全键盘路径）均未具备。

### 最小修复集（按优先级，供 Lead 派单）
1. **INT-1 前置（阻塞）**：
   a. Studio 实现 `IWorkspaceView`（`CreateContent/OnActivated/OnDeactivated/TryHandleKey`；TryHandleKey 分派 Page/Batch + IME 让位），shell 注册；`V2WorkspaceHost` 绑定 `StudioWorkspaceContent`+Studio placeholder；`MainWindow`/`App.axaml.cs` 切新壳（保留回滚开关）。
   b. R-24：抽 `IRunProjectionSource/Poller`（可注入 interval），Console 1s/Batch 750ms/Page band 共用；Console `OnActivated` 恢复轮询；统一 `TaskProjectionInfo → 视图` 映射；Stop 确认共用同一模态组件。
2. **安全/证据硬伤**：Gate 模态 focus+Esc+焦点陷阱+scrim 取消 + 真断言；删除/重生成 `keyboard-seam.json` 等 4 个孤儿证据；`gate.json/drilldown.json/leave-modal.json` 去字面量与 0==0；删占位断言。
3. **P1-B 回补**：作用域物化确定性测试；SubmitInFlight 动态挂起测试（可注入 fake 挂起钩子）。
4. **R-23/R-22**：Console 分区/凭据改中性词表；Console 幂等键改意图级生成/重试复用（或由 Lead 明确 Console 手填为受控偏差）。
5. **AC4 收尾**：`StudioTheme.axaml` 裸 Padding/Width 迁移或 §2.4 登记；conformance 扩到 spacing；shell DS 上收（StatusCatalog/断点）。
6. **证据重冻结**：B-2 curate；B-3/B-4 主 README 与 pin 对齐；删除孤儿 JSON；`not-wired/page-load` 文案按 A-1/A-2/B-4 已合入事实重写。

### 建议复审 pin
- 建议在 **INT-1 接线 + 上述 1–6 完成后**，由 Lead 给出新的固定 pin（ui-shell/`v11r/ui-shell` 与 ui-studio/`v11r/ui-studio` 各自 fix head + main 集成 merge commit），再发起一次终审；本次不建议在修复前切默认入口或宣称 L3。

---

**报告结束。** 我只读审查，未修改任何 worktree/证据/代码；如需复核修复后的固定 pin，请重新派发。
