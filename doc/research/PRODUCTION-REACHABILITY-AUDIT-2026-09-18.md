# 生产可达性盘点：UI 动作 → ViewModel → 服务 → 线程 → SQLite

- 性质：**独立只读盘点（As-Is 取证）**。不是 Review（无 `base_commit`/`reviewed_head`、不给出批准结论、不推翻任何已入档 Review），也不是 Task 交付物。
- 作者：Qoder（**非** 协作协议 §1 的 Codex / ZCode / DeepSeek Harness 任一角色；本次由用户指示"只做只读盘点，不动代码"）。
- 日期：**2026-09-18 取证、2026-09-19 落笔**（Asia/Shanghai；文件名取取证日）。代码基线：master `16f7d75`（TASK-045 集成 `e2a8f01` + 收口 `cb93d66` 之后一笔）。落笔前 `git status` 干净；**本文档自身是当前唯一未跟踪文件，未提交、未 push**——是否纳入主线由用户与 Codex 决定。
- 处置权：findings 的采纳、定性、是否另立 Task 与是否修订 `doc/10_CURRENT_STATE_AND_GAPS.md`/`STATUS.md`，**全部归 Codex**；产品范围取舍归用户。本文档不自行登记任何状态变化。

## 1. 一句话结论

**As-Is**：`doc/STATUS.md` 的「产品发布状态 NOT READY」是准确的；但**比文档口径更糟**——自动翻译整链在生产装配面上存在**四道彼此独立的结构性断点**（跨线程 SQLite、无 Region 创建入口、provider 绑定恒空、错误不上屏），因此即使补齐真实模型依赖（AC-RFULL-001 的既有 `BLOCKED` 条件），从 UI 点下「全部翻译」仍然跑不通。现有 **848 条测试无一穿过「生产装配 + 真 SQLite + worker 线程」这条真实路径**，故该结论无法被 `N passed` 类证据否证。

## 2. 执行证据口径

| 项 | 值 |
|---|---|
| 环境 | Windows 11 (10.0.26200) / Git Bash / venv `G:/CODEX/New Manga.task-envs/TASK-012-py312`（Python 3.12.3、pytest 9.1.1、PySide6_Essentials 6.11.2、pypdfium2 5.13.0、mobi 0.4.1） |
| 全仓（主口径） | `python -m pytest -q -rs` → **848 passed, 0 skipped**，exit 0，41.63s |
| 全仓（offscreen） | 同上但 `export QT_QPA_PLATFORM=offscreen` → **2 failed, 846 passed, 0 skipped** |
| 定向（offscreen 失败项单独复跑） | `python -m pytest tests/rendering -q` → 不设 offscreen **63 passed**；设 offscreen **2 failed, 61 passed** |
| 与 STATUS 口径的关系 | STATUS 记 `842 passed / 6 skipped`；本处 `848 / 0`。总数同为 848，差值即 `tests/network` 6 条 TLS：本机 `openssl` 可用 → 真实执行而非 skip。**与 TASK-041 R-006 已入档的口径勘误一致**，不构成冲突 |

### E-1（环境口径，P3，新登记）offscreen 会使字体度量类断言假失败

- **证据**：`tests/rendering/test_layout.py::TestFontAvailability::test_installed_font_is_reported_available` 与 `tests/rendering/test_source_style.py::TestPixelAnalyzer::test_two_horizontal_lines_estimate_size_and_direction` 在 `QT_QPA_PLATFORM=offscreen` 下失败，去掉该变量后同目录 63 条全绿。前者断言 `resolved_family == "Microsoft YaHei"`（`tests/rendering/test_layout.py:48,148`），后者对渲染出的像素带做高度测量（`tests/rendering/test_source_style.py:76-85`）。
- **判定**：**不是 master 回归**，是 Qt offscreen 平台插件下系统字体枚举/度量不同所致。
- **影响**：任何用 offscreen 取"全仓 N passed"证据的 Agent 会得到两条假失败。**Proposal**：在协作协议或 STATUS 的 flaky/环境节补一句「全仓口径须**不设** `QT_QPA_PLATFORM`」。（`doc/STATUS.md` 现有 flaky 表两条条目均不含此项，也未记录该插件依赖。）

## 3. Findings（逐条：级别 / 证据 / 触发 / 影响 / 复现 / 验证状态）

> 级别沿用仓库既有口径（P0 阻塞整链 / P1 严重 / P2 一般 / P3 轻微）；编号 `P-n` 只是本档索引，与 Task 编号无关。
> 验证状态口径：**VERIFIED** = 本文作者亲自读码或执行确认；**MECHANISM+STATIC** = 机制已实测、端到端仅静态链路成立；**NOT_RUN** = 需真实 GUI 会话才能观测。

### P-1（P0）生产任务执行走跨线程 SQLite 复用，首次持久化即抛错

- **证据**：`src/bootstrap/app.py:426` 在启动（GUI）线程 `open_database(...)`；`src/infrastructure/sqlite/connection.py:58` 为 `sqlite3.connect(str(path))`，**未传 `check_same_thread=False`**；`grep -rn "check_same_thread\|threading.local\|threadsafety" src/ tests/ --include=*.py` → **0 命中**（不存在按线程取连接的机制）。`src/ui/viewmodels/workbench/viewmodel.py:656` `self._controller.start(self._pipeline, run)` 把同一 `PipelineService` 交给 worker；`src/ui/viewmodels/workbench/run_controller.py:74-85`（`self._thread.start()` 于 `:84`、`_startRequested.emit` 于 `:85`）用 `QThread` + `moveToThread` + queued `_startRequested` 在 worker 线程执行 `service.execute_run(run_id)`；`src/application/tasks/service.py:715` `_require_run(run_id)` 与 `:729` `_persist(run)` 是该调用最早的两次 store 访问。
- **机制实测**（项目 venv、项目自己的 `open_database`、临时目录真 DB 文件）：GUI 线程创建的 conn 在另一线程 `execute` → `sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread.`（Python 3.12.3）
- **后果**：`_Worker.execute` 的 `except Exception`（`run_controller.py:37-39`）吞掉它 → `crashed` → `runCrashed` → `viewmodel.py:787` `commandError.emit(error)`。因 P-4 该信号无 UI 消费者 ⇒ **用户可见现象是"任务点了不推进、也没有任何报错"**，DB 中 run 停留在规划前状态。
- **验证状态**：**MECHANISM+STATIC**（机制 VERIFIED、端到端 NOT_RUN：本次未启动 GUI 会话点按钮）。
- **文档现状**：`doc/STATUS.md`、`doc/tasks/TASK-013.md`、`doc/reviews/*.md` 中 `grep check_same_thread|ProgrammingError|跨线程` → **0 命中**。TASK-013 仅声明 AC-NFR-UI-001 为「Mock 证据：worker 线程执行 + GUI 心跳存活测试」，未预见该断点。

### P-2（P0）生产里无法创建 Region，且无 `detect` handler ⇒ 区域类步骤无输入

- **证据**：`RegionEditingService.create_region` 定义于 `src/application/editing/service.py:247`，`grep -rn "create_region\|createRegion" src/` → 仅该定义（`src/ui/` 内 `addRegion|newRegion|createRegion` **0 命中**）。`grep -rn "\"detect\"\|'detect'\|StepKind.DETECT" src/` → 唯一命中是 `src/ui/models/tasks/projection.py:66` 的中文标签 `"检测"`，**`build_production_handlers` 未注册 detect**（`src/bootstrap/app.py:500-513`）。
- **后果**：无 Region ⇒ `src/infrastructure/providers/handlers.py:871-877` `_require_region` 抛 `ProviderInputError("step 'ocr' requires a Region target")`。
- **验证状态**：VERIFIED（静态）。端到端 NOT_RUN。

### P-3（P1）生产 Pipeline 的 provider 绑定与 settings 恒为空

- **证据**：`src/infrastructure/pipeline/assembly.py:19-28` 暴露 `settings` / `provider_bindings` / `constraint_snapshot_ref` / `context_policy` / `limits` 五个可选注入；`src/bootstrap/app.py:529-531` 只传 `handlers=` 与 `clean_probe=` ⇒ 全部取默认 `None`。
- **后果**：`run.provider_binding_snapshot` 无条目 ⇒ `handlers.py:817-824` `_chain` 抛 `ProviderNotConfigured("no provider binding configured for step 'ocr'")`。这是 P-1、P-2 之后**第三道**独立的墙。
- **关联**：根因链含 P-8（设置页空壳 ⇒ 没有任何入口写入 provider 绑定/凭据）。
- **验证状态**：VERIFIED（静态）。

### P-4（P1）`commandError` 在 QML 中没有任何消费者 ⇒ 所有命令失败静默

- **证据**：`grep -rn "commandError" src/ui/` → 13 处**全部在** `src/ui/viewmodels/workbench/viewmodel.py`（定义 `:65` + emit `:544,605,618,627,644,650,679,695,706,730,750,787`），`src/ui/qml/**` **0 命中**。
- **后果**：P-1 的崩溃、"未选择任何 Page"、"已有任务在运行"、PipelineError detail 全部不可见；它是 P-1/P-2/P-3 的**可见性放大器**。
- **验证状态**：VERIFIED。

### P-5（P1）书架「导入图片」入口实际打不开对话框

- **证据**：`src/ui/qml/bookshelf/BookshelfView.qml:21-26` 的 `onImportRequested` 读 `detailArea.chapters.currentChapterId`；`detailArea` 是 `BookshelfView.qml:70` 实例化的 `BookDetailPanel`，而 `chapters` 是 `BookDetailPanel.qml:105` 的 **`id`**（QML 中 `id` 不是实例属性，跨组件不可解析）⇒ 表达式求值抛 TypeError ⇒ 紧随其后的 `importDialog.open()`（`BookshelfView.qml:108-113`，`nameFilters: ["图片文件 (*.png *.jpg *.jpeg *.webp *.bmp)"]`）永不执行。
- **证据盲区**：`grep -rn "importRequested\|BookshelfView" tests/ --include=*.py` → 无任何测试发出该信号或加载 `BookshelfView.qml`；导入仅在 Python 层测 VM（`tests/ui_shell/test_bookshelf_viewmodel.py:156,168,179,188` 全部直接调用 `vm.importFilesFromUrls`）。
- **后果**：**通过 UI 无法导入页面**（Managed Copy 导入链在应用内不可达，尽管 `ImportImagesUseCase` 已装配于 `app.py:450`）。
- **验证状态**：VERIFIED（静态 + 跨组件 `id` 作用域规则）。运行时确证 NOT_RUN（需 GUI 会话）。

### P-6（P1）工作台三档视图（修复图/译图/对比）恒为空白

- **证据**：`src/bootstrap/app.py:108-120` `_ManagedPageCatalog.image_url` 第 109-110 行：`if mode != "original": return ""`，且该 catalog 于 `app.py:639` 注入 `WorkbenchViewModel(page_catalog=...)`。对照：阅读器侧 catalog **会**解析 TRANSLATED artifact（`app.py:253-263`，`locate_current(page_id, ArtifactType.TRANSLATED)`）。
- **后果**：同一份数据在阅读器可见、在工作台永久空白；`ViewerPanel.qml:75,106` 的占位是终态而非过渡态。
- **验证状态**：VERIFIED。

### P-7（P2）PDF / MOBI 导入：适配器已装配但无 UI 入口

- **证据**：`app.py:460` 装配 `ImportDocumentsUseCase`（真 `PdfiumDocumentRaster`/`MobiDocumentRaster`）；`BookshelfViewModel.importDocumentsFromUrls`（`src/ui/viewmodels/bookshelf/viewmodel.py:371`）存在；`grep -rni "document|pdf|mobi" src/ui/qml/` → **0 命中**。
- **验证状态**：VERIFIED。

### P-8（P2）设置页是空壳 ⇒ Provider / 凭据 / 网络策略全部不可达

- **证据**：`src/ui/qml/settings/SettingsView.qml:66-70` 内容区只有一个 `Label { text: "设置项将在后续切片接入" }`；12 个硬编码分类（`:12-26`，其中含"回收站"但 `TrashService` 无 VM 入口）。`src/bootstrap/app.py:708-712` 注册的就是 QML 能拿到的全部上下文属性——**恰 5 个**：`navigationViewModel`、`bookshelfViewModel`、`workbenchViewModel`、`readerViewModel`、`exportViewModel`，无 settings VM。
- **未接入面**（`src/` 内已实现、无 QML/VM 入口）：`application/settings/**`（`ProviderBindingResolver` @ `bindings.py:65`、`NetworkProfileService` @ `network.py:50`、`privacy.py:25`）、`infrastructure/credentials/**`、`application/maintenance/trash.py`（`app.py:468` 构造、`app.py:671` 塞进 `AppServices`，但 `AppServices` 其余字段一律不注册到 QML）、`sqlite/backup.py`、`RegionEditingService` 除读 + 人工译文外的全部方法（`editing/service.py:283-574` 的 delete/geometry/merge/split/reorder/confirm_final/restore_revision/set_revision_pinned，及 `:588+` 的 `EditingSession`）、`LibraryService.update_book:79 / update_chapter:162 / reorder_chapters:173 / 标签 :191-213`、`application/translation/context/**`、`recover_running_runs`（`application/tasks/service.py:859`，bootstrap 未调用 ⇒ 中断恢复 UI 永不出现）。
- **验证状态**：VERIFIED（静态可达性）。

### P-9（P2）导出面：PDF 必抛错；阅读器路径丢失上下文；独立导出窗口运行时不被使用

- **证据**：①`app.py:544-546` `ExportService(JsonHistoryDocumentStore(...))` **未传 `pdf_composer`**，而 `grep -rn "QtImagePdfComposer" src/` → 只有 `application/export/pdf_qt.py:15` 的定义，无任何实例化 ⇒ `application/export/service.py:412-414` 抛 `ExportError("PDF export requires a PdfComposer ...")`。②`src/ui/viewmodels/reader/viewmodel.py:459-461` 构造 `ExportViewModel(service, pages_provider, parent=self)`，`book_id`/`chapter_id`/`output_dir` 取默认（`export/viewmodel.py:73-75`）⇒ 文件名 stem 落为 `"export"`（`:360` `stem = self._chapter_id or "export"`）、输出目录落为 `default_output_dir()`（`:85`）而非数据根（对照 `app.py:619-624` 的路径 B 用 `output_dir=str(data_root / "exports")`）。③`src/ui/qml/reader/ReaderView.qml:57-62` 的 `ExportWindow { controller: rv.model ? rv.model.exportController : null }` ⇒ 路径 B 的 `exportViewModel` 上下文属性在运行时不被该窗口消费（TASK-038 文档写的"双路径"在 UI 上收敛成一条）。
- **验证状态**：VERIFIED（静态）。实际导出产物未跑（NOT_RUN）。

### P-10（P2）退出时不排空运行中的 run

- **证据**：`WorkbenchViewModel.shutdown`（`src/ui/viewmodels/workbench/viewmodel.py:789`）在 `src/` 内无调用者（`grep -rn "\.shutdown()" src/bootstrap/app.py` → 0 命中）。
- **后果**：与 P-1 叠加时，worker 线程与 run 状态在关闭期的行为未定义（未验证）。
- **验证状态**：VERIFIED（静态）。

### P-11（证据方法论）848 条测试为何看不见 P-1～P-5

- **证据**：所有驱动 run 的测试都用**内存 store**——`tests/workbench/workbench_helpers.py:151-152` `store=InMemoryPipelineStore(), snapshots=InMemorySnapshotProvider()` + `InMemoryTargetCatalog`（`:131`）；`grep -rn "SqlitePipelineStore" tests/workbench/` → **0 命中**。`tests/workbench/test_ui_responsiveness.py:22-49` 证明"确实在非 GUI 线程执行"，但其 executor 是 `DeterministicStepExecutor(on_execute=note_thread)`，**不触碰 sqlite**。`tests/core/test_bootstrap.py` 会调 `assemble_services`（`:99,180,242`）验证 schema/目录/失败关闭，但**从不发起 run**。`tests/providers/test_full_chain.py` 注册 `fake-ocr`/`fake-translate` 并注入 `provider_bindings`、用 SQL 直插 Region。
- **结论**：所谓"完整链已打通"（TASK-033）与"生产装配"（TASK-038）的证据在**各自声明的口径内成立**，但**没有任何一条断言覆盖 P-1 的路径组合**。文档从未声称覆盖，因此这不是文档造假，而是**验收面上的空白**。
- **验证状态**：VERIFIED。

## 4. 目标能力对账（As-Is 可用面）

| 一级页面 | 现在真的可用 | 不可见 / 坏掉 |
|---|---|---|
| 书架 | 建书、建章、删除章、搜索/收藏/归档/排序、进入翻译、进入阅读 | **导入图片（P-5）**、PDF/MOBI（P-7）；删除书与 `importSummary` 有 VM slot 但无 QML 入口（`grep deleteBook\|importSummary src/ui/qml/` = 0）；章节页数恒 0（`bookshelf/viewmodel.py:276`）。封面（`BookCard.qml:34-43`）与「进度：—」（`BookDetailPanel.qml:55`）是**码内已注明的诚实占位**，不算缺陷 |
| 工作台 | 选页、翻页、暂停/停止/续跑/重试、进度面板；Region 选择与人工译文编辑**动作已接通服务**（`RegionInspector.qml:109` `saveClicked` → `WorkbenchView.qml:127` → `viewmodel.py:540 saveInspector` → `save_manual_translation`） | **但 Region 无来源（P-2）⇒ 后两者实际没有可操作对象**；**任何 run 的真实执行（P-1）**、译图/修复图/对比（P-6）、错误提示（P-4） |
| 阅读器 | 打开章节、原图/译图切换、翻页与 RTL、续读位置、纵向分块滚动与恢复、导出（`single_image`/`zip`/`cbz`/`text` 四档） | 章节选择按钮恒 `enabled: false`（`ReaderView.qml:88,94`）、**PDF 档导出必抛错**（P-9）、导出落 Documents 而非数据根（`export/viewmodel.py:56-61`）、跳页无入口 |
| 设置 | 无 | 全页空壳（P-8） |

## 5. Proposal：建议的收口切分（**不由本文档执行、不自行释放**）

**Why**：这四道断点是串联的，任何单点修复都无法让「点一下能跑完并看见结果」成为可观察事实；把它们合成一个可达性切片，才能写出一条判别性的端到端测试。

建议 Codex 立一个 Task（暂名 **生产可达性收口**），依赖顺序如下，验收主 AC 为**一条穿过 `assemble_services` + 真 SQLite + QThread worker 的端到端 run 测试（修前失败、修后通过）**：

1. **线程与连接归属**（P-1）：先决定口径——每线程独立连接 / worker 内自开自关 / 单写者队列——再落地。此处涉及共享 seam，须 Codex 先定范围。
2. **错误可见**（P-4）：`commandError` 上屏。故意排在第 2 位：让后续每一步都能"看见自己为什么失败"。
3. **Region 来源**（P-2）：人工框选或 detect，二者是产品取舍，**归用户裁决**。
4. **绑定注入**（P-3）+ 设置页最小可写面（P-8 的最小子集）。
5. 书架 `detailArea.chapters`（P-5）与工作台 catalog（P-6）——各自 1～3 行，可并入本切片或另立 UI 缺陷切片。
6. P-7/P-9/P-10 建议登记为独立非阻塞 findings，不与本切片混做。

## 6. 本次未覆盖的风险（如实声明）

- 未在真实 GUI 会话中启动应用：P-1/P-2/P-3/P-5 的**用户可见现象**均为推断而非观察（标注 NOT_RUN）。
- 未审查 `doc/01`～`doc/08` 逐条需求与 `13_ACCEPTANCE_TRACEABILITY.md` 的映射完整性（本次只核"实际能不能跑到"）。
- 未复审任何已集成切片；不推翻也不确认 TASK-045 的 `done`。
- 未验证 TASK-046 的 overlap 议题（另见 `doc/tasks/TASK-046.md`），但本文档的 E-1 与 P-1 建议在其开工前由 Codex 一并知悉。
- 既有开放义务仍在：`doc/reviews/TASK-045-posthoc-zcode.md` 尚未存在（TASK-045 的 ZCode post-hoc 复审已委托未交付，见 `doc/handoffs/POSTHOC-REVIEW-BRIEF-TASK-045.md`）。
