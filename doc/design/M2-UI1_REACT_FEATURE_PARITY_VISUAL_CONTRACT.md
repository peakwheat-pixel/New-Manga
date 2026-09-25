# M2-UI1 · React Feature Parity & Visual Contract

- task: [M2-UI1](../tasks/M2-UI1.md)（owner Qoder，reviewer Codex，depends_on M2-D1=`done`）
- code_base: `6a68fdeb92d8a1c7903166a8076d6260bf8fa79a`（本文所有 `src/**` 行号与结论绑定此 commit；开工 HEAD `5d989ba` 相对 base 仅差 `doc/**`，`git diff --name-only 6a68fde 5d989ba` 零 `src/` 命中）
- 性质: 迁移契约（设计文档）。**不释放任何 React/Tauri/IPC 实现，不修改生产 QML/Tokens/Schema/T3.2.1**；本文与代码不一致处按 §7 冲突清单交 Codex 裁决，不以目标图推断已实现。
- 依据: [AD-001](../AD-001_TARGET_DESKTOP_ARCHITECTURE.md)（增量 parity / parity-before-removal，AD-001 第 30–32 行）、[UI_UX_GUI_DESIGN（Design F · Graphite Atelier）](../contracts/UI_UX_GUI_DESIGN.md)、[tokens-cand-f.json](../design/tokens-cand-f.json)、[Tokens.qml](../../src/ui/qml/theme/Tokens.qml)、[05_UI_MAPPING](../05_UI_MAPPING.md)、[04_USER_FLOW](../04_USER_FLOW.md)、[M2-D1 审计报告](../research/M2-D1_HEADLESS_QT_COUPLING_AUDIT.md)、真实 QML/测试源码。

## 0. 盘点总览（AC1 前提）

`rg --files src/ui/qml -g '*.qml'` 在 base 上恰得 **25 个 `.qml`**（清单与命令输出：`verification/M2-UI1/qml-inventory.txt`），另有 **1 个 `theme/qmldir`**（`module theme` + `singleton Tokens 1.0 Tokens.qml`）——它是 token 注册依赖，不计入 25。四个一级页面齐全：书架（6 文件）、工作台（9）、阅读器（1 + 共用 2 + 窗口 1）、设置（1），外加窗口/共用/壳层/主题（8）。

QML 侧的全部数据来源是 6 个上下文属性（`src/bootstrap/app.py:1035-1040`，M2-D1 结论 1/3）：`navigationViewModel`、`bookshelfViewModel`、`workbenchViewModel`、`readerViewModel`、`exportViewModel`、`settingsViewModel`。QML 不访问数据库/文件系统/模型（`src/ui/**` 零 SQL，M2-D1 W7）。

## 1. Feature Parity Matrix（UI1-AC1）

图例：**钉** = 被测试或契约钉住的 objectName（迁移时必须保留语义）；「未验证」= 本 Task 环境未取证的行为/画面。用户流程列引用 04_USER_FLOW（F§）与 05_UI_MAPPING（M§）。

### 1.1 壳层与入口

| # | 文件（行数） | 定位 | 可见功能与交互 | 输入 → 状态 → 输出 | 用户流程 | 现有测试 | 未验证项 |
|---|---|---|---|---|---|---|---|
| 1 | `Main.qml`（44） | ApplicationWindow 入口 | 1280×800 窗口、标题 "New Manga"、`Tokens.bgPage` 底色、11 个 palette 角色（含 REPAIR-13 的 `palette.buttonText: Tokens.inkInv` 原生控件补偿，:23-33）、挂载 AppShell（:41-43） | 无 VM 输入 → 常量 → 装配由 `bootstrap.app` 注入上下文后加载 | F§3 启动；M§3.1 | `tests/core/test_bootstrap.py`（路径/装配失败信息）；`tests/ui_shell/test_design_f_applied.py`（加载真实 Main.qml 树做运行时配色） | DPI 125–200% 下的实际呈现（基线仅 100%，见 §4 NOT_RUN） |
| 2 | `shell/AppShell.qml`（59） | 壳层 | 左 rail + `pageHost`（钉 `appShell`/`pageHost`）；四页**常驻实例化**，仅切 `visible`（:38-57，钉 `page-bookshelf/workbench/reader/settings`） | `navigationViewModel.currentPage` → 可见性 → 无命令 | M§3.1 规则 150-157（启动选书架、切换不销毁上下文、任务不停） | `tests/ui_shell/test_qml_shell.py`（12 用例，宿主加载） | 运行中任务跨页持续性的 GUI 级取证（依赖真实 pipeline，本 Task NOT_RUN） |
| 3 | `shell/PrimaryNavigationRail.qml`（46） | 一级导航 | Repeater over `navigationViewModel.pages`；按钮钉 `nav-<id>`；bookshelf 初始 focus（:31）；workbench 项挂 NavBadge（:36-42） | `pages`/`currentPage` → checked → `navigate(id)` | M§3.1 | `test_qml_shell.py`（四入口同级、切换） | 徽标 4Hz 节流刷新（契约 §8.1 要求，QML 未见节流实现 → 记 §7 C-11） |
| 4 | `shell/NavBadge.qml`（23） | 徽标件 | 单一 pill：`runSoft` 底 + `stRun` 字（:11-21），文本来自 `workbenchBadge` | `visible: workbenchRunning` + `text` → 无输出 | M§61 子集 | `test_design_f_applied.py`（静态断言 runSoft/stRun 配对，:236-241） | 非 running 语义（暂停/有失败）配色——VM 若给不同文本仍画 run 色 → §7 C-11 |

### 1.2 书架页（6）

| # | 文件 | 定位 | 可见功能与交互 | 输入 → 状态 → 输出 | 用户流程 | 现有测试 | 未验证项 |
|---|---|---|---|---|---|---|---|
| 5 | `bookshelf/BookshelfView.qml`（137） | 页面根 | 钉 `bookshelfView`；toolbar + 网格区 + 右固定详情 + `bookshelfEmptyState`（:63-78，钉 `emptyCreateBook`/`emptyImport`(禁用)）+ `newBookDialog`（:97-122，钉 `newBookTitleInput`/`newBookOriginalInput`）+ `importDialog` FileDialog（:126-136） | `shelf.*` → 布局/空态 → `createBook` / `importFilesFromUrls`；导入门控读 `detailArea.currentChapterId` 公开 alias（REPAIR-13，:24-25） | F§4–5、8；M§7/§8 | `test_repair13_import_entry.py`（5）；`test_design_f_applied.py` | 原生文件选择框的画面内容（grabWindow 不含原生子窗，见 §4 帧 05b） |
| 6 | `bookshelf/BookshelfToolbar.qml`（82） | 工具栏 | 高 `tbH`；钉 `btnCreateBook`、`btnImport`（enabled=`importReady`）、`importHint`（禁用原因文案）、`searchField`、`btnFavoritesFilter`、`btnArchivedFilter`、`btnSort`（recent/title 文案切换）、`btnViewMode`（grid/list 文案切换） | `shelf.favoritesOnly/archivedFilter/sortBy/viewMode` → checked/文本 → 对应 setter | F§4.1；M§7.1 | `test_repair13_import_entry.py`；VM 侧 `test_bookshelf_viewmodel.py`（18） | — |
| 7 | `bookshelf/BookGrid.qml`（71） | 网格/列表容器 | FocusScope 钉 `bookGrid`；GridView（钉 `bookGridView`，cell=`cardW+2*gutter`，gutter=4 局部值 :20）与 ListView（钉 `bookListView`，行高 64 字面量 :57）双挂载按 `viewMode` 切换；**故意无 Loader**（GC use-after-free 教训，:5-8 注释） | `shelf.bookListModel` → delegate 角色 → `bookSelected`/`setFavorite` | M§7.1 | `test_design_f_applied.py`（cell 必须取 `Tokens.cardW`，:243-248） | list 模式行高 64 未令牌化（§7 C-8） |
| 8 | `bookshelf/BookCard.qml`（119） | 卡片 | 封面占位「封面」（:41-53，TASK-007 无封面资产）；标题/原标题 ElideRight；「▣ 归档」三重编码徽标（skipSoft 底 + ink2 字，:74-90）；「进度 —」占位；按压/hover 三态底色（:24-25）；右上收藏 AbstractButton 钉 `favorite-<bookId>`（★/☆ + ToolTip，:99-118） | 6 个 delegate 角色 → 视觉态 → `cardActivated`/`favoriteToggled` | F§4.2；M§7.1 | `test_qml_shell.py`（经 AppShell 实例化）；VM 测试 | 真实封面渲染（未实现能力）；进度非「—」的呈现（字段未落地） |
| 9 | `bookshelf/BookDetailPanel.qml`（143） | 右固定详情 | 宽 `detW`；钉 `bookDetailPanel`、`detailEmptyState`、`detailFavorite`/`detailArchived`（CheckBox）、`chapterTitleInput`/`chapterNumberInput`/`btnCreateChapter`、`btnEnterTranslation`/`btnEnterReading`（enabled=有选中章节）、「编辑」「更多…」诚实禁用（:138-139）；公开 `currentChapterId` alias（:25） | `shelf.selectedBook` + `chapterListModel` → 表单/列表 → `setFavorite/setArchived/createChapter/enterTranslation/enterReading` | F§4.2/7；M§7.1 | `test_repair13_import_entry.py` | 作者/标签字段的富编辑（编辑窗未实现） |
| 10 | `bookshelf/ChapterList.qml`（107） | 章节列表 | 钉 `chapterList`/`chapterListView`；行高 `rowH`，选中行 `accentSoft` 底 + `Tokens.ink`（§6C R3-001 `ink/selected-row` 审计对，:37 + 注释 :9-11）；行内：编号、标题、类型·方向·页数摘要；行动作 进入翻译/进入阅读/删除（钉 `deleteChapter-<id>`）可用，编辑/页面管理/翻译设置诚实禁用（:78-80）；空态「暂无章节」 | `chapterListModel` → currentIndex/currentChapterId → `enterTranslation/enterReading/deleteChapter` | F§7.1；M§9 | VM 测试；`test_repair13_import_entry.py`（行点击选择） | **导入后行内页数不刷新**：`ChapterListModel` 仅 `set_chapters` 时 reset（`src/ui/models/library/models.py:113-132`），import 后不重选作品则显示旧值——基线帧 05==06 实证（§7 C-6） |

### 1.3 共用件（3）

| # | 文件 | 定位 | 可见功能与交互 | 输入 → 状态 → 输出 | 用户流程 | 现有测试 | 未验证项 |
|---|---|---|---|---|---|---|---|
| 11 | `common/EmptyState.qml`（34） | 空态槽件 | title + 可选 description + default-property actions Row | 属性 → 布局 → 无 | M§62 | 随宿主页面测试间接覆盖 | — |
| 12 | `common/CanvasCaption.qml`（26） | 画布浮字底 | `bgPanel` pill 承载文字（画布上无 ink-* 达 4.5:1，:5-8 注释；ui-reference `.vfloat` 语义） | text → 视觉 → 无 | — | `test_workbench`（overlay 场景中介于） | — |
| 13 | `common/ChapterPicker.qml`（182） | 章节选择浮窗 | Popup 480×320 字面量（:20-21）；根 objectName 按 action 切换（钉 `workbenchChapterPicker`/`readerChapterPicker`）；作品/章节双 ComboBox（钉 `chapterPickerBookList`/`chapterPickerChapterList`，含 native palette 补偿 :99-100,134-135）；空态文案（钉 `chapterPickerEmpty`）；取消/进入（钉 `chapterPickerCancel`/`chapterPickerAccept`）；Esc 关闭（:34-37）；`onOpened` 同步选中并 `shelf.selectBook` | `shelf.bookListModel/chapterListModel` → 表单 → `enterTranslation/enterReading` | F§15.2、33；M§62 | `test_qml_workbench.py`；`test_repair13_export_window_open.py`；TASK-059 后续 e2e（`fe9fca0` picker escape） | 双实例同名的测试定位歧义（probe 脚本按可见性过滤，见 capture.log） |

### 1.4 工作台（9）

| # | 文件 | 定位 | 可见功能与交互 | 输入 → 状态 → 输出 | 用户流程 | 现有测试 | 未验证项 |
|---|---|---|---|---|---|---|---|
| 14 | `workbench/WorkbenchView.qml`（247） | 页面根 | 钉 `workbenchView`；无 VM/无上下文时诚实空态 + `workbenchPickContext`（:51-63）；五区常驻：Toolbar/`commandErrorBar`/PageList|Viewer|Inspector/TaskProgress（:65-222）；全部 `w*` 别名带 null-guard（:27-42）；`Connections.onPageLocateRequested` → `pageListPanel.locatePage`（:164-169）；DirtyConfirmDialog 由 `onInspectorDirtyConfirmRequested` 打开、决策回 `resolveDirtyConfirm(action)`（:224-241） | `workbenchViewModel` 14 个读面 → 布局可见性 → 12 个命令转发 | F§15–16；M§15/16/55 | `test_qml_workbench.py`（16）；`test_qml_shell.py` 静态源检；`tests/workbench/test_command_error_surface.py` | 「已完成（有失败）」整批呈现的真实 pipeline 画面（NOT_RUN，§4） |
| 15 | `workbench/WorkbenchToolbar.qml`（101） | 工具栏 | implicitHeight `tbH`；钉 `toolbarContext`（书·章）、`toolbarPrevPage`/`toolbarNextPage`、模式四键 `modeOriginal/Clean/Translated/Compare`（highlighted 表当前）、批命令 `cmdTranslateAll`/`cmdTranslateUntranslated`（runActive 禁用）、`cmdTranslateSelected`（还需 hasSelection） | 5 属性 → 文本/highlighted/enabled → 6 信号 | F§11–13；M§17/56 | `test_qml_workbench.py` | — |
| 16 | `workbench/PageListPanel.qml`（155） | 页面列表 | 钉 `pageListPanel`（宿主钉 `pageListPanelHost`）；`implicitWidth: collapsed?36:176` 字面量（:23，值=契约 §8.1，未经 token）；折叠钮 `pageListCollapse`；tile 高 64/缩略 48 字面量；行内容：序号占位、文件名 ElideMiddle、状态字（○等待/●处理中/✓已完成/!失败/↷跳过/⏸阻塞 + 色 :110-127）、🔒（`pageLock-`，stLock）、▶运行中（`pagePipelineCurrent-`）；单/Ctrl/Shift 三 TapHandler（:64-75）；`locatePage` 滚动（:148-153） | `pageListModel` + `viewerPageId` → 选中底 `accentSoft`/当前 `bgActive`+focus 边框 → 3 信号 | F§10；M§18/19/61 | `test_qml_workbench.py`；`tests/workbench/test_page_list_model.py` | 真实缩略图（未实现）；blocked 字形 ⏸ 与契约 paused ⊘/blocked 语义错位（§7 C-4）；合成点击在本机不生效（§4 采集注记） |
| 17 | `workbench/ViewerPanel.qml`（134） | 画布 | 钉 `viewerPanel`（宿主 `viewerPanelHost`）；页名 `viewerPageName` + 模式标签 `viewerModeLabel`；原图 pane（钉 `viewerImagePane`，`bgCanvas` 底 + Image PreserveAspectFit）；RegionOverlay 仅 original 模式挂载（:96-102，产物图无保证同尺寸）；compare 双 pane（钉 `viewerComparePane`）；空态 `viewerEmpty`「在左侧选择一个 Page」+ CanvasCaption 诚实占位（「原图不可用/该模式暂无产物/译图尚未产出」） | imageUrl/translatedUrl/pageName/mode/vm → 图像+overlay → 无 | M§20 | `test_qml_workbench.py` | compare 模式实图（需译图产物，NOT_RUN） |
| 18 | `workbench/RegionInspector.qml`（161） | 右 Inspector | implicitWidth `inspW`；钉 `regionInspector`（宿主 `regionInspectorHost`）、`inspectorDirtyBadge`（"● 未保存" stWarnT）、`regionListView`（行高 `rowH`，选中 accentSoft+accent 边，钉 `regionRow-<id>`；`#序号`、译文/（无译文）ink2、🔒）、`inspectorTranslationInput`（TextArea，dirty 双向 :109-119）、`inspectorSave`/`inspectorDiscard`（enabled=dirty）、单 Region 命令 `regionCommandOcr`/`regionCommandRetranslate`/`regionCommandRetranslateFull` | regions/selectedRegionId/text/dirty → 表单 → 5 信号 | F§27；M§22–30（样式/修复/Lock/Revision 分组**未实现**） | `test_qml_workbench.py`；`tests/workbench/test_region_create_persistence.py`（VM 面） | 05 §27 样式控制、§28 修复、§29/30 Lock/Revision 界面（目标能力，QML 无 → 矩阵记未实现，见 §5 范围注） |
| 19 | `workbench/RegionOverlay.qml`（253） | 画布几何层 | 透明 Rectangle + Canvas；**页面尺寸只取 VM `viewerPageWidth/Height`**、归一化坐标才过界（:9-15 两条硬规则）；letterbox 数学与 Image 同参（:28-33）；已有 Region 描边（stRun/选中 accent，:80-91）；草稿 rect 拖拽 / polygon 逐点+右键闭合（stWarn :96-123）；工具 pill `regionToolbar`（`regionToolRect`/`regionToolPolygon`，bgPanel 浮底 :185-219）；操作提示 `regionToolHint`；Esc 取消 / Delete 删除选中（:241-247） | vm.inspectorRegions + 指针 → 画布 → `createRectangle/createPolygon/deleteRegion` | F§18；M§21 | `test_qml_workbench.py`（`_OverlayHost.qml`）；`tests/workbench/test_region_canvas.py` | 真实拖拽手势下的画面（合成事件不生效 → 草稿态基线 NOT_RUN，§4） |
| 20 | `workbench/TaskProgressPanel.qml`（321） | 底部进度 | implicitHeight `progH`/折叠 40 字面量；钉 `taskProgressPanel`（宿主 `taskProgressPanelHost`）；九态 badge 表 `badgeStyles`（:65-75，逐对=契约 §7.2 表；`completed_with_failures`=warn-soft/st-warn-t ✓）；乐观 `pausing→paused`（:77-81）；步流 `检测✓→OCR●→…`（:191-224）；当前页按钮 `taskProgressCurrentPage`；统计五键 `statCompleted/Failed/Blocked/Skipped/Waiting`；控制行 `btnPauseRun/StopRun/ContinueRun/RestartRun/AbandonRun/RetryFailed`（enablement 全取投影）；`taskProgressBlockedReason`；空态 `taskProgressEmpty`「当前无运行任务」；折叠条保名 `taskProgressPercentCompact/StatusCompact` | `progress` 投影 map → 徽标/按钮 enabled → 9 信号 | F§30–31；M§31–33 | `test_qml_workbench.py`；`tests/workbench/test_projection.py`（数据面） | 运行中/暂停/失败/中断的真实动画与 4Hz 节流画面（NOT_RUN）；「保留已提交成果」提示（契约 §7.2 Cancelled 主操作，QML 无 → §7 C-5） |
| 21 | `workbench/DirtyConfirmDialog.qml`（40） | 脏守卫窗 | 模态 Dialog；钉 `dirtyConfirmDialog`（宿主 `dirtyConfirmDialogHost`）、`dirtySave`/`dirtyDiscard`/`dirtyCancel`；NoAutoClose | 打开请求 → 决策 → `resolveDirtyConfirm` | F§27/32；M§55 | `test_qml_workbench.py` | — |

### 1.5 阅读器（1 + 窗口 1）

| # | 文件 | 定位 | 可见功能与交互 | 输入 → 状态 → 输出 | 用户流程 | 现有测试 | 未验证项 |
|---|---|---|---|---|---|---|---|
| 22 | `reader/ReaderView.qml`（328） | 页面根 | 钉 `readerView`；键盘 ←/→ 按 RTL/LTR 反向翻页（:39-56，webtoon 禁用）；工具栏（:84-162）：`readerChapterTitle`、`readerPickChapter`、`readerModeOriginal/Translated`（**英文标签** :106-118）、`readerPreviousPage/NextPage`（vertical 禁用，F-5 :122-127）、`readerContinueLast`、`readerRestart`、`readerProgress`（"N / M 页 · x%"）、`readerExportButton`（仅当 controller 就绪才建窗，F-13-2 :58-68）；`readerStatusBanner`（stWarnT）；`readerSummary`（最后阅读+累计秒）；Loader 切 paged/webtoon（:190-195）；webtoon：Flickable 按宽、瓦片带 `readerTilesHost`（TASK-045 F-5/F-11 :252-296）、500ms 节流 `saveScrollOffset`（:246-250）、R-003 解码后恢复偏移（:307-313）；`readerEmptyState` | `readerViewModel`（mode/direction/pageNumber/progressPercent/tiles/scrollOffsetY/exportController…） → 视图 → setMode/nextPage/previousPage/continueReading/restartFromBeginning/requestTiles/saveScrollOffset/openExporter | F§9、33–36；M§37–42 | `tests/reading_export/test_qml_contract.py`（13，真实 VM）；`test_repair13_export_window_open.py`；`test_webtoon_tiles.py`（数据面） | webtoon 瓦片滚动画面、阅读进度恢复画面（基线 NOT_RUN，§4）；「按宽滚动」全量验收属 TASK-020 口径 |
| 23 | `windows/ExportWindow.qml`（252） | 工具窗（C 类） | Window 560×480 字面量、ApplicationModal、同款 11 palette 角色（REPAIR-13 R-13-1 :26-42）；钉 `exportWindow`、`exportScope`、`exportMode`（translated/original）、`exportFormat`、`exportOutputPath`+浏览（FileDialog SaveFile）、`exportOverwritePolicy`（overwrite/skip/auto_rename）、`exportStalePolicy`（abort/continue）、`exportStaleBanner`（D06 §97 不装现行）、`exportStatus`、`exportRunButton`（running→"导出中…"）、`exportCancelButton`、`exportOpenFolderButton`、`exportRepeatButton`、`exportCloseButton` | controller 属性 → 表单/横幅 → setMode/setFormat/setOutputPath/setOverwritePolicy/setStalePolicy/startExport/cancelExport/openOutputFolder/repeatExport | F§37；M§51 | `test_qml_contract.py`；probe 实证 ZIP 含 2 页（本次基线 capture.log） | 5 种格式全集（`exportFormat(count==5)` 是 TASK-047 注册表面；probe 只跑 zip）；MOBI/PDF 画面 |

### 1.6 设置页（1）

| # | 文件 | 定位 | 可见功能与交互 | 输入 → 状态 → 输出 | 用户流程 | 现有测试 | 未验证项 |
|---|---|---|---|---|---|---|---|
| 24 | `settings/SettingsView.qml`（548） | 页面根 | 左类目列（钉 `settingsCategoryList`，12 类 :98-112，宽 180/圆角 6 字面量）+ 右内容窗；Provider 面板（profile 下拉+新建、ID/名称/类型/能力复选/base_url/model/API Key 密码框+「已存密钥」只显 flag（AC-SEC-001~003）、代理策略/网络/启用、删除/保存、能力默认绑定行 :309-351）；网络面板（模式/三类代理/用户名/密码/绕过/继承/TLS/回退/默认网络 :357-510）；危险 TLS 确认 Dialog（AC-SEC-005，:533-547，确认后带 `confirm_disable_tls` 重提交）；底部 `statusLabel`（saved=stOkT / failed=stFail）；类目 ≥3 显示「设置项将在后续切片接入」 | `settingsViewModel`（profiles/networks/capabilityList/bindings/defaultNetworkProfileId/networkModes） → 表单 → save/delete/setDefault/refresh；信号经 `Component.onCompleted` 命令式 connect（:30-45，context property 无变更通知的规避） | F§38；M§43–49 | `test_settings_viewmodel.py`（24）；`tests/network/**`（服务面） | 其余 10 个类目的界面（未实现，诚实占位即为 As-Is）；GUI 级设置页交互截图基线仅空 Provider 态（§4 帧 12） |

### 1.7 主题与注册

| # | 文件 | 定位 | 可见功能与交互 | 输入 → 状态 → 输出 | 用户流程 | 现有测试 | 未验证项 |
|---|---|---|---|---|---|---|---|
| 25 | `theme/Tokens.qml`（231） | 设计令牌单例 | 42 色 × dark/light + 21 几何（值与 `tokens-cand-f.json` 逐字一致，`test_design_tokens.py` 漂移即红）；`colorFor()` 把契约的 CSS `rgba()` 转 QML 色（:149-163，未识别值→全透明让测试失败而非猜色）；`mode` 属性存在但产品无切换入口（ND-4/ND-5 待决） | `mode` → 调色板选择 → 命名属性/`value()`/`geometry()` | — | `test_design_tokens.py`（7）；`test_design_f_applied.py`（运行时+对比度 24 对） | 亮色模式的产品内画面（无入口 → 基线 NOT_RUN） |
| — | `theme/qmldir` | token 注册依赖 | `module theme` + `singleton Tokens 1.0 Tokens.qml`——所有页面 `import "../theme"` 的前提 | — | — | 随全部 Tokens 测试 | React 侧对应物 = tokens.css + ThemeProvider（§3.4），无 QML 等价注册 |

**四页覆盖核对**：书架 #5–10、工作台 #14–21、阅读器 #22–23（+共用 #13）、设置 #24 —— AC1 的「四个一级页面齐全」成立。

## 2. React Component Map（UI1-AC2）

### 2.1 边界原则（不可谈判项）

1. **Python Core 是唯一业务权威**（AD-001；M2-D1 结论 2「Core 已 headless」）。React 组件树只消费 VM 投影快照、只发命令；**不得**出现 SQLite/文件系统/模型调用/任务状态推断（对应 QML 现有纪律：D05 §60「QML 不持业务逻辑」的平移）。
2. 六个上下文属性 → 六个 IPC 领域通道（navigation/bookshelf/workbench/reader/export/settings）。IPC 契约本身归后续 M2 契约/IPC Task（未释放），本表只声明**每个组件需要该通道的哪些读面与命令面**，与 QML 现用面一一对应，不新增能力（防范围膨胀）。
3. 状态分层：
   - **服务端态**（server state）：VM 投影，React 只读渲染；
   - **UI 态**：仅存在于组件本地且迁移时必须保持本地——hover/press 三态（BookCard:24-25）、PageList 折叠、TaskProgress 折叠、RegionOverlay 草稿点（`draftPoints/dragFrom/dragTo`，提交即弃）、Inspector 输入框未提交文本、picker 临时选中。
   - 判据：**QML 里凡是调 `vm.*()` 的都不算 UI 态**。
4. objectName 钉位平移为 `data-testid`（同名同语义），测试注册表（TASK-047 §4.7 体系 + §1 各表「钉」列）是 parity 测试的最小面。
5. 大二进制（页面像素/瓦片）沿用 M2-D1 结论 6：文件 URI 优先，跨语言传输方案等 IPC spike（M2-R1）定案，React 侧组件只接 URL。

### 2.2 映射表

| QML（现） | 拟议 React | 边界/拆分理由 | 状态来源（IPC 通道 → 读面） | 命令（→ IPC） |
|---|---|---|---|---|
| `Main.qml` | Tauri `main` 窗口配置 + `<AppRoot>`（ThemeProvider + 全局快捷键/焦点管理） | 窗口尺寸/最小窗/DPI 属 Tauri capability，不再是组件 | —（注入 tokens.css） | — |
| `AppShell.qml` | `<AppShell>` | **保持四页 keep-alive**（`display:none` 切换），语义=「切换不销毁上下文」 | navigation: `currentPage`, `pages` | — |
| `PrimaryNavigationRail.qml` | `<NavRail>` + `<NavButton>` | Repeater→map；checked 语义=aria-current | navigation: `pages`, `currentPage`, `workbenchRunning`, `workbenchBadge` | `navigate(id)` |
| `NavBadge.qml` | `<NavBadge>` | 纯展示 | （props） | — |
| `BookshelfView.qml` | `<BookshelfPage>` | 页面组合 + 两个对话框挂载 | bookshelf: `selectedBook`, `isEmpty`, `currentChapterId` 语义 | `createBook`, `importFiles` |
| `BookshelfToolbar.qml` | `<BookshelfToolbar>` | — | bookshelf: `favoritesOnly/archivedFilter/sortBy/viewMode` + importReady 派生 | `setSearchText/setFavoritesOnly/setArchivedFilter/setSortBy/setViewMode` |
| `BookGrid.qml` | `<BookShelfViewToggle>`（内 `<BookGrid>`/`<BookList>`） | 双挂载切换语义保留（虚拟列表选型归实现 Task） | bookshelf: `bookListModel` | `selectBook` |
| `BookCard.qml` | `<BookCard>` | 封面占位=同一诚实占位 | （list 角色 props） | `cardActivated`, `setFavorite` |
| `BookDetailPanel.qml` | `<BookDetailPanel>` | 编辑/更多保持禁用占位 | bookshelf: `selectedBook`, `chapterListModel` | `createChapter/enterTranslation/enterReading` |
| `ChapterList.qml` | `<ChapterList>` | 选中行底色对（accent-soft×ink）入视觉基线 | bookshelf: `chapterListModel` | `deleteChapter` + 选中语义 |
| `EmptyState.qml` | `<EmptyState>` | 共用件 | props | — |
| `CanvasCaption.qml` | `<CanvasCaption>` | 共用件（画布可读性契约的载体） | props | — |
| `ChapterPicker.qml` | `<ChapterPickerDialog>`（Radix Dialog 类） | 双实例单组件（action prop） | bookshelf: `bookListModel/chapterListModel/bookCount` | `selectBook/enterTranslation/enterReading` |
| `WorkbenchView.qml` | `<WorkbenchPage>` | 五区 grid 骨架；空态/有上下文两形态；commandErrorBar 保留 provisional 语义 | workbench: 14 读面（§1.4 #14 全列） | 12 命令面 |
| `WorkbenchToolbar.qml` | `<WorkbenchToolbar>` | — | workbench: `contextInfo/viewerMode/selectedPageCount/runStatus` | `stepPage/setViewerMode/startTranslate*` |
| `PageListPanel.qml` | `<PageListPanel>` + `<PageTile>`（**按 05 §60 目标边界拆出 Tile**） | 折叠宽/行高取 §3.2 待裁决值 | workbench: `pageListModel/viewerPageId` | `selectPage/togglePageSelected/selectRangeTo` + locate 事件订阅 |
| `ViewerPanel.qml` | `<ViewerPanel>` | compare 双 pane 语义保留 | workbench: `viewerImageUrl(For)/viewerPageName/viewerMode` | — |
| `RegionOverlay.qml` | `<RegionOverlay>`（**Canvas → SVG**） | letterbox/归一化两条硬规则原样平移（尺寸只从投影取、只有归一化值过界）；React 无 GC-uaf 问题但保留「单一数学」约束 | workbench: `inspectorRegions/inspectorRegionId/viewerPageWidth/Height` | `createRectangle/createPolygon/deleteRegion` |
| `RegionInspector.qml` | `<RegionInspector>` | 译文置顶重排（A/F §4）**不在本契约执行**，只登记为 F 实现切片差异 | workbench: `inspectorRegions/inspectorRegionId/inspectorText/hasDirtyEditor` | `selectRegion/setInspectorText/saveInspector/discardInspector/startRegionCommand` |
| `TaskProgressPanel.qml` | `<TaskProgressPanel>` | 九态 badge 表逐字平移（数据驱动，不推断步成败） | workbench: `taskProgress` 投影 | pause/stop/continue/restart/abandon/retry/filterByStatus/locatePipelinePage |
| `DirtyConfirmDialog.qml` | `<DirtyConfirmDialog>` | 模态不可点外关闭 | 事件流 `inspectorDirtyConfirmRequested` | `resolveDirtyConfirm` |
| `ReaderView.qml` | `<ReaderPage>` + `<PagedViewer>` + `<WebtoonViewer>`（按 05 §60 拆出 `<ReaderToolbar>`/`<ReaderNavigator>` 为**目标边界**，允许实现合并） | RTL 镜像、键盘翻页、瓦片带、滚动节流四语义必须原样 | reader: `hasChapter/mode/direction/pageNumber/pageCount/progressPercent/sourcePath/tiles/scrollOffsetY/statusMessage/bookSummary/canGoNext/Previous` | `setMode/nextPage/previousPage/continueReading/restartFromBeginning/saveScrollOffset/requestTiles/openExporter` |
| `ExportWindow.qml` | 独立 Tauri 子窗 `<ExportWindow>`（保持「工具窗」容器类，M§4 C 类） | 不用页内 Modal 冒充；stale 横幅语义保留 | export: `scopeSummary/mode/formats/outputPath/overwritePolicy/stalePolicy/staleWarning*/statusMessage/running/history/pageCount` | `setMode/setFormat/setOutputPath/setOverwritePolicy/setStalePolicy/startExport/cancelExport/openOutputFolder/repeatExport` |
| `SettingsView.qml` | `<SettingsPage>` + `<ProviderPane>` + `<NetworkPane>`（类目 ≥3 = 占位组件） | 密钥只写不回显（flag-only）是**契约级**约束，React input 同样 password+不回填 | settings: `profiles/networks/capabilityList/bindings/defaultNetworkProfileId/networkModes` | `save/delete/setDefault/saveBinding/clearBinding/refresh` + saved/failed/confirmationRequired 事件 |
| `Tokens.qml` + `qmldir` | `tokens.css`（42×2 色 + 21 几何 → `--bg-page` 等 kebab 同名变量）+ `<ThemeProvider data-theme>` | 见 §3；`colorFor` 的 rgba 转换是 QML-only 规避，React 直接消费 CSS `rgba()` | — | — |

### 2.3 调用关系（迁移后目标拓扑，与 M§58 同构）

```mermaid
flowchart LR
  CORE[Python Core\n(权威: SQLite/任务/管线)] -- IPC 快照 --> STORE[前端只读 store\n6 通道 = 6 上下文属性]
  STORE --> SHELL[AppShell] --> NAV[NavRail] & P1[BookshelfPage] & P2[WorkbenchPage] & P3[ReaderPage] & P4[SettingsPage]
  P2 --> PL[PageListPanel] --> VP[ViewerPanel] --> RO[RegionOverlay]
  VP --> RI[RegionInspector]
  P2 --> TP[TaskProgressPanel]
  P3 --> EW[ExportWindow 子窗]
  P1 -- enterTranslation/enterReading --> SHELL
  SHELL & P1 & P2 & P3 & P4 -- 命令(仅 VM 已有方法) --> CORE
```

## 3. Design Token Migration Map（UI1-AC3）

真值链不变（DDR-3）：`ui-reference.html`（视觉真值）→ `tokens-cand-f.json`（机器可读）→ `Tokens.qml`（生产转写，`test_design_tokens.py` 防漂移）。本表**不复制色值**（避免第四份真值），只登记名称/语义/落点。

### 3.1 色彩（42 × 2 mode）

| 族（契约 §7.1） | Tokens.qml 属性 | JSON 键 = 建议 CSS 变量（kebab 同名） | React 落点 |
|---|---|---|---|
| 底色 9 | `bgPage…bgPress` | `bg-page/bg-rail/bg-panel/bg-raised/bg-inset/bg-canvas/bg-hover/bg-active/bg-press` | 页面/面板容器 class；`bg-canvas` 双主题皆暗（light 也 `#26262a`）→ 阅读/画布衬底 |
| 线 3 | `border/borderStrong/divider` | 同名 | 描边/焦点外框/分隔 |
| 文字 5 | `ink/ink2/ink3/inkDis/inkInv` | `ink/ink-2/ink-3/ink-dis/ink-inv` | `ink-inv` 在 React 中回归本义（反色文字），不再承担原生控件补偿（§3.4 D-1） |
| 强调 6 | `accent…onAccent` | 同名 | 主操作唯一来源 |
| 状态 8+7 | `stOk/stOkT/stRun/stWarn/stWarnT/stFail/stSkip/stLock/stBlock` + `okSoft…blockSoft` | 同名 | `<StatusBadge>` 变体表：底= `*-soft`（CSS 原生支持 rgba，无需转换）、字= 对应 `-t`/主变体；**三重编码规则原样平移**（契约 §7.2） |
| 其他 3 | `focus/shadow/shadowSm` | `focus/shadow/shadow-sm` | 焦点环 2px；shadow 串在 CSS 直接可用（QML 需解析是转写层问题） |

### 3.2 几何（21 项，mode 无关）

| 令牌 | 值 | 生产现状 | React 迁移 |
|---|---|---|---|
| `fs-base/sm/lg/sub/title/disp` | 13/12/14/16/19/23 | 全 UI 经 `Tokens.fs*`，**QML 零 `font.family`**（实测 rg 零命中）→ 系统 UI 字 | `--fs-*` + 系统字体栈显式写入 CSS（React 默认字体≠Qt 默认，见 D-3） |
| `ctl-h/row-h/rail-w/pad-page/gap` | 36/42/68/16/12 | 广泛使用；例外见 D-2 | 同名变量 |
| `rad-sm/md/lg/win` | 8/11/14/16 | SettingsView 用字面量 6（D-2） | 同名变量 |
| `tb-h/list-w/insp-w/prog-h/det-w/card-w` | 52/176/288/150/336/158 | `list-w`/折叠 36、`prog-h`/折叠 40 在 QML 是**字面量恰等于契约 §8.1 值**（PageListPanel:23、TaskProgressPanel:35） | 变量化；折叠值 36/40 需先入令牌（D-2 裁决） |

### 3.3 状态语义映射

九态 PipelineRun 表（契约 §7.2 ↔ `TaskProgressPanel.badgeStyles:65-75` 逐对一致，含 `completed_with_failures`=warn-soft/st-warn-t「成功底+警示字不整批判失败」）；页级六态 ↔ `PageListPanel` 字形表（差异 C-4）；Region 八态（M§61）与「叠加语义不合并」规则：React 侧同样禁止单徽标合并 Process/Review/Lock——QML 现状已遵守（lock 用角标 🔒、译文锁定用行内 🔒、处理态独立）。

### 3.4 实际生产值 vs 文档目标 vs 需裁决差异（AC3 核心）

| # | 项 | 生产值（base） | 文档目标 | 处置建议（交 Codex） |
|---|---|---|---|---|
| D-1 | 原生控件补偿 | `Main.qml:23-33`、`ExportWindow.qml:26-42`、`ChapterPicker.qml:24-30,99-100,134-135` 用 `palette.buttonText=inkInv` 等让 Windows native style 控件「浅底深字」——基线帧 01/09/11 中按钮呈浅色系统面 | 契约 F 未覆盖此类（假定全自绘） | 记 **LEGACY-only 偏差**：React 全自绘后自然消失；QML 存续期 parity 比对须豁免 native 控件像素 |
| D-2 | 未令牌化几何字面量 | 列表行 64（BookGrid:57）、tile 64/48/36（PageListPanel:23,51,85）、ChapterList 高 220（BookDetailPanel:121）、picker 480×320（ChapterPicker:20-21）、导出窗 560×480（ExportWindow:19-20）、类目列 180/圆角 6（SettingsView:120,123）、newBookDialog 320/260（BookshelfView:103,112）、searchField 180（BookshelfToolbar:52）、regionList 160（RegionInspector:50）、TaskProgress 折叠 40（:35） | 契约 §8.1 只钉了其中 176/36/288/150/40 | 迁移时逐个登记为组件常量或补令牌；**圆角 6 与 rad-sm 8 不一致**是唯一视觉冲突项，需裁决 |
| D-3 | 字体族 | QML 未写 `font.family`（Qt 默认系统字） | F=系统 UI 字 | React 必须显式声明系统栈，否则浏览器默认≠Qt 默认，基线不可比 |
| D-4 | 亮色模式 | `Tokens.mode` 存在但产品无切换入口 | ND-4/ND-5 待决 | 迁移契约保留双主题令牌面；产品入口裁决前两侧都不做切换 |
| D-5 | rgba 转换 | `colorFor()` 是 QML-only 规避（Tokens.qml:144-163） | — | React 直接消费 CSS rgba，转换层不迁移；`test_design_tokens` 的漂移防线由「JSON→tokens.css 生成脚本」替代（实现 Task 交付） |
| D-6 | Q-011 表 | `WorkbenchView.qml` 硬编码色已在 T2.1.1 全部令牌化（现 :19/:97-98/:172 均 Tokens.*） | 契约 §10 Q-011 仍列 5 处硬编码 | **文档过时**，交 Codex 修订契约（§7 C-1） |

## 4. Visual Regression Baseline（UI1-AC4）

### 4.1 固定环境与口径

| 维度 | 钉定值 |
|---|---|
| 基线 commit | `6a68fde`（src 树与采集时 HEAD `5d989ba` 逐字节一致，证据 §4.5 第 3 行） |
| 平台 | Windows 11 `10.0.26200` x64；QPA=默认 windows 平台插件（**禁 offscreen**：无字体库，M2-D1 结论 3 + conftest 注记）；DPI 100% |
| 运行时 | `G:/CODEX/New Manga.task-envs/TASK-012-py312`（Python 3.12.3 / PySide6 6.11.2），`PYTHONDONTWRITEBYTECODE=1` |
| 窗口 | 1280×800 DIP，dark（F 默认），`colorScheme=Dark` 前置 |
| 数据 | 临时 data_root + 两张固定合成 PNG 夹具（a=红 400×600、b=蓝；sha 见 capture.log `[STEP] fixtures`），零真实用户库 |
| 工具 | `verification/M2-UI1/capture_baseline.py`（派生自 `verification/T3.2.1/repair-13/probe_ui_states.py`，唯一行为差异=窗口激活 + tile 选择 VM 直驱回退 + focus 重试；派生说明写在脚本 docstring） |

### 4.2 已采集帧（13 帧有效 + 1 帧降级）

帧清单、逐帧 sha256、状态描述见 `verification/M2-UI1/baseline-6a68fde/manifest.md`；原始日志 `capture.log`（含每按钮文字/底色采样表）与 `capture.stderr.log`（须零 QML 错误）。要点：

- 覆盖四页 + 新作品 Dialog + 章节选中（accent-soft 行）+ 导入后书架 + 阅读器活动章 + ChapterPicker + 导出窗（前/后）+ **工作台选中页**（11 帧：tile 选中边框、viewer 实图、RegionOverlay 工具 pill 与提示）+ 设置 Provider 态。
- 帧 05/05b/06 逐字节相同——**这本身是 As-Is 证据**（C-6 页数不刷新 + 原生 FileDialog 不进 grabWindow），不是采集失误；已在 manifest 注记。
- 帧 13（键盘焦点环）**降级**：`forceActiveFocus` 在本机不生效（三次尝试一致），该帧不得作为焦点视觉基线使用。

### 4.3 NOT_RUN 清单（未采集画面，不虚构基线图）

| 项 | 状态 | 原因 / 可复现步骤 |
|---|---|---|
| 焦点环视觉 | NOT_RUN | 本环境合成 focus 不生效；复现：Windows Sandbox 前台会话跑 `capture_baseline.py`（repair-13 原始运行证明可 PASS） |
| DPI 125/150/175/200 五档 | NOT_RUN | 需 OS 级缩放；步骤=改系统缩放后重跑脚本并核对 §8.2 降级序列（PageList 折叠/Inspector 覆盖/TaskProgress 折叠） |
| 亮色模式全部画面 | NOT_RUN | 产品无 mode 切换入口（D-4）；裁决后需加 `Tokens.mode="light"` 前置的变体脚本 |
| 任务运行/暂停/失败/中断态（九态徽标、步流、4Hz 节流） | NOT_RUN | 需真实 pipeline + Provider 凭据；步骤=装配带 run 的 workbench VM 后扩展脚本；数据面防线现由 `tests/workbench/test_projection.py` 承担 |
| Region 草稿态（拖拽中/多边形逐点） | NOT_RUN | 合成指针事件在本机不触达 TapHandler/MouseArea（两次采集实证）；需真实输入或 Sandbox |
| compare 模式实图、译图/修复图产物态 | NOT_RUN | 需跑通翻译/渲染产物链（依赖未授权切片） |
| webtoon 瓦片滚动、进度恢复画面 | NOT_RUN | 需 webtoon 夹具 + 进度数据；`test_webtoon_tiles.py` 只证数据面 |
| DirtyConfirmDialog、commandErrorBar 呈现 | NOT_RUN | 需运行中守卫/命令失败注入；帧未采 |
| 导出格式全集（5 格式）画面 | NOT_RUN | probe 仅 zip 实跑 |

### 4.4 比较与验收口径

1. **像素层**：同帧名同尺寸比对；因 Qt 光栅化对 GPU/驱动敏感，**不承诺 sha256 恒等**——基线帧的 sha256 是「本次采集的指纹」，比对工具与容差（建议逐通道 ±2、差异像素 ≤0.5%，实现 Task 落地时定）在 React 侧建立时写入其 Task。
2. **语义层（当前即可执行）**：`capture.log` 的按钮级「文字色/底色采样 + WCAG 对比度」表是确定性数值面，任何实现改动后重跑脚本，采样表须与 token 值一致（底色 ∈ `Tokens` 值集，native 控件豁免 D-1）。
3. **回归门**：`tests/ui_shell/test_design_f_applied.py` 24 对比态对 + `test_design_tokens.py` 漂移门先行；像素门在其后叠加。
4. React 每功能迁移的视觉验收 = 本表帧名逐一对位（同状态、同夹具、同窗口尺寸），加该功能新增帧。

### 4.5 采集证据链

`verification/M2-UI1/`：`qml-inventory.txt`（AC1 清单）、`capture_baseline.py`（派生脚本）、`baseline-6a68fde/{manifest.md, capture.log, capture.stderr.log, screenshots/*.png, attempt1-capture.log, attempt2-capture.log, screenshots-attempt1-failed/, screenshots-attempt2/}`（三次尝试全量保留，含失败原因注记）。

## 5. 逐功能 Parity Gate（UI1-AC5）

AD-001 第 30–32 条的操作化。任一 QML 功能在 React 侧「完成」的充要条件，按序执行、不可合并跳步：

1. **契约行**：该功能在本文 §1 矩阵有行（无行=未盘点，先补矩阵）；
2. **实现**：React 组件按 §2 映射落地，objectName→data-testid 同名，边界不越 §2.1；
3. **测试**：§1「现有测试」列所指用例在 React 测试面有等价断言（最小面=「钉」列 objectName 的行为），且全仓既有 `tests/**` 保持绿（QML 未删前不得改期望）;
4. **行为验证**：§1「输入→状态→输出」列逐条走查记录（Handoff 表格）；
5. **视觉验证**：§4 帧名对位比对（含该功能 NOT_RUN 项的补采），比对口径 §4.4；
6. **Release 决定**：Codex 出具该功能的集成/发布记录（含裁决 §7 相关冲突）；
7. **QML 保留**：1–6 全部通过前，生产 QML 对应文件/组件**不得删改**（本 Task 自身遵守：交付 diff 零 `src/**`）；只有第 6 步授权的移除切片才可动 QML。

范围声明：05 §60 目标组件树（PageTile/ViewerCanvas/ReaderToolbar/SettingsSectionList/各 windows/*）与 M§24–30/34–36/44–50/52–53 等界面是**未实现目标**，不构成本矩阵的 As-Is 行；迁移契约只覆盖 §1 的 25 个真实文件，新增产品功能不在本 Task 范围（Task 禁止范围）。

## 6. 未验证项汇总（诚实面）

除 §4.3 NOT_RUN 外：运行中任务跨页不停（依赖真实 pipeline）；4Hz 徽标节流（QML 未见实现证据，契约 §8.1 要求 vs `PrimaryNavigationRail` 直绑属性 → C-11）；真实封面/进度字段（TASK-007 未落地，占位即 As-Is）；Inspector 样式/修复/Lock/Revision 分组（M§27–30 目标）；设置其余 10 类目（占位即 As-Is）。

## 7. 冲突清单（文档 vs 代码，交 Codex 裁决）

| # | 冲突 | 证据 | 建议 |
|---|---|---|---|
| C-1 | 契约 §10 Q-011 硬编码表已过时 | `WorkbenchView.qml:19,97-98,172,185,205` 现全为 `Tokens.*`；T2.1.1 交付 | 修订契约或标注「已由 T2.1.1 消解」 |
| C-2 | 05 §60 目标树 ≠ 实际 25 文件树（11 个目标文件不存在，delegates 内联） | `qml-inventory.txt` vs 05:1954-2008 | 属目标边界非缺陷；迁移映射以本文 §2 为准 |
| C-3 | 原生控件浅底深字与 F 暗色面并存 | D-1；基线帧 01/09/11 | LEGACY-only 偏差入档，React 豁免 |
| C-4 | PageList blocked 用「⏸」，契约 §7.2 paused=⏸/blocked=⊘（TaskProgressPanel 用 ⊘ 正确） | PageListPanel.qml:114 vs TaskProgressPanel.qml:69 | 小修候选（实现切片），本文不擅改 |
| C-5 | 契约 §7.2 Cancelled 主操作「保留已提交成果（提示）」无 QML 呈现 | TaskProgressPanel 全文无 | 归实现 Task 或修订契约 |
| C-6 | 导入后章节行页数不刷新（需重选作品） | `models.py:113-132` 仅 set_chapters reset；VM import 路径不 refresh；帧 05==06 | As-Is 行为入 parity 基线；是否算缺陷归 Codex |
| C-7 | SettingsView 圆角 6 vs rad-sm 8；类目列宽 180 无令牌 | SettingsView.qml:120,123,151 | D-2 一并裁决 |
| C-8 | Reader 工具栏英文标签 Original/Translated 与全站中文并存 | ReaderView.qml:106-118 | 保持 As-Is（objectName+文案双钉），文案统一属产品裁决 |
| C-9 | NavBadge 恒用 run 色对，不随 `workbenchBadge` 语义变色 | NavBadge.qml:11,20 | 与 §7.2 三重编码有张力；实现切片或契约注记 |
| C-10 | 页级「已完成（有警告）/需校对」徽标（M§61/契约 §7.2 虚线框）无 QML 实现 | rg 零命中（本文 §0 核验命令） | 未实现能力，禁止在 parity 比对中当作回归 |
| C-11 | rail 徽标 4Hz 刷新节流无 QML 侧证据 | PrimaryNavigationRail.qml:36-42 直绑 | 待 M2-I1/投影层确认节流位置后注记 |

## 8. 交付边界自证

本 Task 写集合 = `doc/tasks/M2-UI1.md`、本文、`doc/handoffs/M2-UI1-*.md`（新增）、`verification/M2-UI1/**`（新增）。`src/**`、既有需求/设计文件、Schema、T3.2.1 证据零修改；`git diff --name-only <base> <delivery>` 全量清单与 `git diff --check` 结果见 Handoff 验证表。
