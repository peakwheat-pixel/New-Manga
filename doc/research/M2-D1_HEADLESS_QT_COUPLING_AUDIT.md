# M2-D1 — Headless & Qt Coupling Audit（研究报告与分类矩阵）

| 项 | 值 |
|---|---|
| Task | [M2-D1](../tasks/M2-D1.md)（`kind: research`，只读审计；**不授权迁移实现**） |
| 规划依据 | [REBASELINE_PLAN](../REBASELINE_PLAN.md) M2 `PLANNED / NOT_RELEASED`；[AD-001](../AD-001_TARGET_DESKTOP_ARCHITECTURE.md) 约束 §31/§33/§34/§35 |
| Owner | DeepSeek Harness（Reviewer/Integrator = Codex，禁止自审） |
| 固定代码 base | `307a940265fc325076fe77698750392531f8fce1`（`master`） |
| Owner worktree HEAD | `bbeb4892746795be4bca92f4e5dda91a77c422a3`（`agent/deepseek/M2-D1-headless-qt-coupling-audit`） |
| 审计日期 | 2026-09-25（Asia/Shanghai） |
| 覆盖 | `src/domain`、`src/ports`、`src/application`、`src/infrastructure`、`src/bootstrap`、`src/ui`：**181 个 .py（32,101 行）+ 25 个 .qml（3,775 行）** |
| 证据索引 | [verification/M2-D1/09-evidence-manifest-and-coverage.md](../../verification/M2-D1/09-evidence-manifest-and-coverage.md) |
| 修改范围 | 仅本报告、`verification/M2-D1/**`、`doc/tasks/M2-D1.md`、新 Handoff。`src/**`、`tests/**`、打包、依赖、Schema、历史证据**零修改** |

## 0. 方法与证据口径

1. 先执行 Task 指定的必跑命令（[`02-required-rg.log`](../../verification/M2-D1/02-required-rg.log)，286 行命中，`EXIT=0`），再按调用链做 17 组补充检索（[`03-…log`](../../verification/M2-D1/03-supplementary-searches.log)）与写者/入口检索（[`04-…log`](../../verification/M2-D1/04-writer-and-entry-searches.log)）。
2. 耦合判定**不采信 grep 命中本身**：每条命中都回到源码区分「真实导入 / 注释或 docstring / 无关词（如 `connect` 命中 `connection`）」，并在下文给出 `路径:行`。
3. 运行期证据由隔离探针产生（[`probes/core_import_probe.py`](../../verification/M2-D1/probes/core_import_probe.py)）：`python -B` + `PYTHONDONTWRITEBYTECODE=1`，`NEWMANGA_DATA_ROOT`/`LOCALAPPDATA` 指向生成的临时目录并在结束后删除；探针后实测 `src/**` 内 `__pycache__` 数量为 **0**（源码未被写入）。**真实用户库与真实数据根从未被访问。**
4. 本审计由 5 个并行只读子审计（bootstrap、Qt 渲染/导入、SQLite 写者、UI/QML、Core 纯度）提供线索，其中**所有载重结论都由主审用独立命令与源码阅读复核**；未经复核的推断一律标 `UNVERIFIED` 或明确标注为推断。
5. 产品测试 **NOT_RUN**（源码未改；且本环境未安装 PySide6，Qt 相关测试套件无法执行）——按本 Task 完成 Gate「源码未改时产品测试可记 NOT_RUN，不得写成 PASS」执行。

### 0.1 环境边界（决定 D1-AC3 的可验证程度）

| 事实 | 值 | 证据 |
|---|---|---|
| 可用解释器 | 3.10 / 3.11 / 3.12 / 3.14 | `01-…log:71-76` |
| PATH 默认 `python` | `C:\Python314\python.exe`（3.14.6） | `01-…log:60-64` |
| **PySide6 是否安装** | **否**（四个解释器均无） | `05-…log` `qt_available=False` |
| 生产入口在该环境的实际结果 | `ModuleNotFoundError: No module named 'PySide6'` @ `src/bootstrap/app.py:36`，exit 1 | `06-…log` P2/P3 |
| 仓库是否有 headless 入口/打包面 | 根目录无 `main.py`/`run.py`/`__main__.py`/`*.spec`/`packaging/`（`git ls-files` 零命中，`E4 EXIT=1`） | `04-…log:289-292` |
| 是否存在 React/Tauri/Rust 产物 | 工作区零命中（无 `.rs`/`Cargo.toml`/`tauri.conf.json`/`.tsx`/`package.json`） | 独立检索 `EXIT=1` |

## 1. 执行摘要

- **Core 三层在导入期与运行期都不依赖 Qt**（强于 AD-001 的预期）：`src/domain` 13/13、`src/ports` 23/23、`src/application` 66/66 在一个**未安装 PySide6** 的解释器里全部导入成功（`imported_ok=102 imported_failed=0`，`EXIT=0`）。其中 `src/application` 唯一触碰 Qt 的模块是 `src/application/export/pdf_qt.py`，且两行 Qt 导入都在 `compose()` **函数体内**（`:19`、`:20`）。
- **Qt 耦合面是可枚举的 21 个模块**（占 181 个 .py 的 11.6%）：`src/infrastructure/rendering/{font_catalog,pixel_source_style,qt_compositor,qt_layout}.py`（4）、`src/bootstrap/app.py`（1）、`src/ui/**`（16）。其余 160 个模块在无 Qt 环境下导入成功。
- **Python Core 的持久化写者权威基本成立，但有一处必须记录的例外**：`src/ui/**` 与 `src/bootstrap/app.py` 内**零写入 SQL**（bootstrap 仅 2 条 `SELECT`，`app.py:466`、`:497`）；全仓 SQL 写语句只落在 9 个文件——`src/infrastructure/sqlite/**` 的 8 个 + **`src/infrastructure/providers/step_writes.py`**（`:249/:270/:365/:452/:500`，其 docstring `:1-11` 自述这是有意越界）。`src/infrastructure/sqlite/connection.py:347` 是生产库唯一的 `sqlite3.connect` 工厂，唯一调用点是 `src/bootstrap/app.py:605`。
- **当前不存在 headless 入口，且有两个互相独立的阻塞**：① 入口/组合根在**模块导入期**就绑定 Qt，`main()`（`app.py:1077`）无条件 `QGuiApplication`（`:1108`）并 `assemble_engine()` 加载 QML（`:1125`、`:1046`）；② 生产渲染链只装配了 Qt 实现（`QtFontCatalog` `:675`、`QtTextLayoutEngine` `:682`、`QtImageCompositor` `:683`、`PixelSourceStyleAnalyzer` `:676`），而仓库自带的 4 处测试夹具明确记录「**offscreen 平台不带字体数据库**」（`tests/rendering/conftest.py:3-6`、`tests/ui_shell/conftest.py:3-5`、`tests/workbench/conftest.py:3-6`、`tests/core/test_shutdown_drain.py:40-41`），`tests/core/test_bootstrap.py:3-5` 更明确「入口证据禁止强制 `QT_QPA_PLATFORM=offscreen`」。
- **已有可复用的无 Qt 像素通路**：`src/infrastructure/imaging/streaming_png.py`（纯 `struct`/`zlib` 的 PNG 扫描带读写）与 `webtoon_tiles.py`（TileGrid/TileCache/TiledPageRasterizer，零 Qt）已经证明「不靠 Qt PNG handler 也能解码分块」，这是 M2 最有价值的既有资产之一。
- **UI 树里还藏着两个已经是 Core 形状的 Qt-free 模块**（探针 P6）：`src/ui/models/tasks/projection.py`（336 行）与 `src/ui/viewmodels/workbench/region_canvas.py`（97 行）**按文件路径可在无 Qt 环境加载成功**，只因包 `__init__` 重导出了 Qt 兄弟模块而按模块名导入失败（`src/ui/models/tasks/__init__.py:8`、`src/ui/viewmodels/workbench/__init__.py:8-9`）。这是「目标架构已部分存在、且迁移成本最低」的直接证据（矩阵 M2D1-25/26）。
- **既有架构守卫只覆盖 domain 与 application→infrastructure**：`tests/core/test_architecture.py:12-16` 规定 `DOMAIN_FORBIDDEN = {PySide6, sqlite3, torch, transformers, onnxruntime}`、`UI_FORBIDDEN = {infrastructure}`、`APPLICATION_FORBIDDEN = {infrastructure}`——**没有任何守卫禁止 `src/application` 或 `src/ui` 导入 PySide6**，这正是 `application/export/pdf_qt.py` 能长期存在而未被告警的原因（矩阵 M2D1-04）。
- **大二进制边界现状**：分块阅读已经把像素落盘并以**文件 URI** 交给 UI（`reader/viewmodel.py:425`），符合「大二进制不进普通 IPC」的方向；但 provider 步骤输入是目前**整页 raw RGB32 bytes**（`bootstrap/app.py:283-288` `ImageFrame(width, height, "rgb32", bytes(image.constBits()))`）与整页/裁剪 PNG bytes（`:322-334`、`:290-320`），未来 IPC 不能把这些直接 JSON/Base64 序列化。
- **矩阵结果**（26 项）：KEEP 9、DECOUPLE 11、REPLACE（候选，需后续决策）3、LEGACY 2、UNVERIFIED 1（详见 §3）。**本报告不选择任何替代技术**，`REPLACE` 仅表示需要后续决策的候选。

## 2. 现状耦合事实

### 2.1 运行期导入图（探针 P1/P4/P5）

| 树 | .py | 导入 OK | Qt 阻塞 | 阻塞模块 |
|---|---:|---:|---:|---|
| `src/domain` | 13 | 13 | 0 | — |
| `src/ports` | 23 | 23 | 0 | — |
| `src/application` | 66 | 66 | 0 | —（`pdf_qt.py` 因惰性导入而通过） |
| `src/infrastructure` | 56 | 52 | 4 | `rendering/font_catalog.py`、`rendering/pixel_source_style.py`、`rendering/qt_compositor.py`、`rendering/qt_layout.py` |
| `src/bootstrap` | 2 | 1 | 1 | `bootstrap/app.py` |
| `src/ui` | 21 | 5 | 16 | `models/library/models.py`、`models/tasks{,.page_list_model,.projection}.py`、6 个 `viewmodels/*/viewmodel.py`、`viewmodels/workbench/run_controller.py`、5 个 viewmodel 包 `__init__` |
| **合计** | **181** | **160** | **21** | `src/ui` 通过的 5 个仅为包 `__init__` |

（`src/ui` 通过的 5 个：`ui`、`ui.models.library`、`ui.viewmodels`、`ui.viewmodels.bookshelf`、`ui.viewmodels.navigation`——即按**模块名**导入时 `src/ui` 内没有含逻辑的模块是无 Qt 的。）

**重要修正（探针 P6，[`10-probe-P6-qtfree-ui-modules.log`](../../verification/M2-D1/10-probe-P6-qtfree-ui-modules.log)）**：上表按**模块名**判定，会高估 `src/ui` 的 Qt 依赖。逐文件加载（`importlib.util.spec_from_file_location`，绕过包 `__init__`）证明 `src/ui` 内有**两个含逻辑且完全无 Qt 的模块**——`src/ui/models/tasks/projection.py`（336 行）与 `src/ui/viewmodels/workbench/region_canvas.py`（97 行）：两者 `A_by_module_name=FAIL (ModuleNotFoundError: PySide6)`、`B_by_file_path=OK`。原因是包 `__init__` 的重导出：`src/ui/models/tasks/__init__.py:8` 导入 `ui.models.tasks.page_list_model`、`src/ui/viewmodels/workbench/__init__.py:8-9` 导入 `RunController`/`WorkbenchViewModel`（均为 Qt 模块）。即这 433 行「已经是 Core 形状」的逻辑**被包初始化语句困在 UI 树里**，按模块名不可 headless 复用。

### 2.2 耦合点清单（模块级 vs 惰性）

**模块级（19 行，导入即需要 PySide6）**：

- `src/bootstrap/app.py:36` `from PySide6.QtCore import QTimer, QUrl`；`:37` `QGuiApplication`；`:38` `QQmlApplicationEngine`；`:42` `QQuickWindow`（`:39-41` 注释说明第 42 行是**刻意** eager，以保证 `rootObjects()[0]` 是强类型 QQuickWindow）。
- `src/ui/**` 9 个文件：`models/tasks/page_list_model.py:12`、`models/library/models.py:10`、`viewmodels/navigation/viewmodel.py:10`、`viewmodels/bookshelf/viewmodel.py:15`、`viewmodels/export/viewmodel.py:23-24`、`viewmodels/reader/viewmodel.py:28`、`viewmodels/settings/viewmodel.py:33`、`viewmodels/workbench/viewmodel.py:29`、`viewmodels/workbench/run_controller.py:18`。
- `src/infrastructure/rendering/font_catalog.py:11`、`pixel_source_style.py:24`、`qt_compositor.py:17-26`、`qt_layout.py:15`。

**惰性（函数内，16 行，导入期不需要 Qt）**：

- `src/bootstrap/app.py:256`（`_ManagedPageImageSource._page_image`）、`:284`（`page_frame`）、`:291-292`（`region_crop`）、`:324`（`page_png`）、`:418-419`（`_render_content_decoder`）、`:1147-1148`（`main._grab_and_quit`）。
- `src/infrastructure/importing.py:46-47`（`QtImageDecoder.decode`）、`:180-181`（`_PdfiumDocumentHandle.render_page`）、`:354-355`（`_MobiDocumentHandle.render_page`）。
- `src/application/export/pdf_qt.py:19-20`（`QtImagePdfComposer.compose`）。

**使用的 Qt 模块仅 4 个**：`QtCore`、`QtGui`、`QtQml`、`QtQuick`。

**动态/反射耦合：无 Qt 风险。** 全仓唯一的动态导入点是 `infrastructure/providers/detection_doctr.py:399`、`ocr_local.py:47`（provider 模型模块）与 `devices/manager.py:21`、`providers/dependencies.py:17`（`importlib.util.find_spec` 特性探测）；`src/domain`、`src/ports`、`src/application` 三棵树内 `importlib`/`import_module`/`__import__`/`pkgutil`/`entry_points` **零命中**，`getattr(` 仅 2 处自身字段读取（`application/settings/snapshots.py:50`、`ports/network/profiles.py:76`）。

### 2.3 组合根与启动序列

`src/bootstrap/app.py` 是唯一入口：`main()`（`:1077`）→ argparse（`:1078-1102`）→ `QT_SCALE_FACTOR`（`:1106`）→ **`QGuiApplication([sys.argv[0]])`（`:1108`）** → 数据根（`:1113-1121`：`--data-root` / `smoke`/`screenshot` 用 `tempfile.TemporaryDirectory` / `default_data_root()`）→ `assemble_services(db, managed)`（`:1122`）→ `assemble_engine(services)`（`:1125`，`:1033` 建 engine、`:1046` `engine.load(Main.qml)`、`:1047-1048` 无 rootObjects 即失败）→ 事件循环（`:1138`/`:1168`/`:1172`）。`if __name__ == "__main__"` 在 `:1182`。

`assemble_services`（`:596-1014`）是组合根：`:605` `open_database` → `:612` `MigrationRunner.apply_pending()` → 仓储/存储/导入链（`:614-651`）→ provider runtime（`:662-669`）→ **Qt 渲染栈（`:675-687`）** → handlers（`:723-752`）→ pipeline（`:775-783`）→ `:787` `recover_running_runs()` → 设置栈/VM（`:799-1014`）。它**自身不创建** `QGuiApplication`，但 `:670-674` 注释承认「Qt-based classes need a QGuiApplication instance, which the entry creates before calling this; pure headless consumers construct their own」。

装配期**eager 写**（与「只读审计」无关，但决定 headless 重建的行为面）：migration（`:612`）、`pipeline_defaults` 播种 INSERT（`:775` → `sqlite/pipeline.py:786-788`）、`recover_running_runs`（`:787`）、两个 legacy JSON 导入（`:833-834`，**即使 JSON 不存在也会写 marker**）、`open_database` 内部的 WAL/PRAGMA（`sqlite/connection.py:317-321`）、`storage.ensure_layout()`（`:616`）。

### 2.4 UI 投影 ↔ 持久化边界

- bootstrap 只把 6 个 ViewModel 作为 **context property** 注入 QML（`:1035-1040`），无 `qmlRegisterType`、无 `addImportPath`；`exportViewModel` 会在工作台上下文切换时被重新发布（`:1041-1045`）。
- **UI 层零 SQL**：`rg -n 'SELECT |INSERT |UPDATE |DELETE ' src/ui src/bootstrap` 只命中 bootstrap 的两条 `SELECT`（`app.py:466`、`:497`），`src/ui` **零命中**；`src/ui/**` 无 `import sqlite3`、无 `open_database`。
- ViewModel 只依赖 application 服务/端口（构造签名证据）：`BookshelfViewModel`(`library: LibraryService`, `importer`/`document_importer`) `bookshelf/viewmodel.py:34-42`；`ReaderViewModel(reading: ReadingService, catalog: ReaderPageCatalog, *, export_service, tile_factory)` `reader/viewmodel.py:51-59`；`ExportViewModel(service: ExportService, pages_provider, *, output_dir, folder_opener)` `export/viewmodel.py:68-78`；`SettingsViewModel(*, provider_store, network_service: NetworkProfileService, credential_store, pipeline_defaults: PipelineDefaultsService)` `settings/viewmodel.py:85-93`；`WorkbenchViewModel(*, pipeline: PipelineService, page_catalog, region_catalog, translation_editor, region_creator, region_deleter, navigation)` `workbench/viewmodel.py:80-91`。
- bootstrap 的两处 `connect`（`:914` `readerContextChanged`、`:987` `workbenchContextChanged`）槽体内夹带**业务读**（`library.get_chapter`、`page_catalog.list_pages`、`library.get_book`、`workbench.setContext(...)`），即「UI 投影 + 组合期的业务查询」混在同一槽内。
- 分层守卫现状：`tests/core/test_architecture.py:12-16` 只禁止 domain 使用 `PySide6/sqlite3/torch/...`、并禁止 ui/application 导入 `infrastructure`；**没有**「application/ui 不得导入 Qt」的守卫（见 §1 与 M2D1-04）。

### 2.5 SQLite 写者与连接权威

- **生产库唯一连接工厂**：`src/infrastructure/sqlite/connection.py:347` `sqlite3.connect(str(path), check_same_thread=False)`（全仓 5 处 `sqlite3.connect` 中唯一的 live-DB 工厂；其余 3 处在 `backup.py:66/253/353` 用于备份文件，1 处在 `connection.py:370` 的 `open_readonly`）。唯一调用点 `src/bootstrap/app.py:605`。
- **每线程一真实连接**：`ThreadRoutedConnection`（`connection.py:82`）docstring `:19` 「one real connection per thread」；`:317-321` 应用 `busy_timeout/foreign_keys/WAL/synchronous`；facade 自己**从不发 `BEGIN`**，事务边界由各适配器自持（`with self._conn:` 25 处 + 显式 `BEGIN IMMEDIATE` 7 处：`migrator.py:143`、`regions.py:215`、`artifacts.py:199`、`pipeline.py:578`、`step_writes.py:207/358/435`）。
- **写者面（精确）**：含 SQL 写语句的文件共 **9** 个 —— `src/infrastructure/sqlite/{artifacts,backup,pipeline,library,regions,migrator,reading_export,schema}.py` 与 `src/infrastructure/providers/step_writes.py`。
- **两个写者线程**是设计事实：GUI 线程 + `RunController` 的 `QThread` worker（`run_controller.py:101 start` → `:123 QThread(self)` → `:125 moveToThread` → `:126` 队列信号 → `:130 emit`），靠 per-thread 连接隔离而非单线程。
- **未接线/未调用（基线事实，非 Qt 问题）**：`open_readonly`（`connection.py:367`）在全 worktree **零调用点**；`release_current_thread_connection`（`:196`）与 `any_in_transaction`（`:221`）在 `src/` 内**只有定义与注释**（真实调用仅存在于 `tests/**`）；`SqliteBackupService`（`backup.py:32`）在 `src/` 内零引用；`WebtoonTileCacheSweeper`（`imaging/tile_cache_sweep.py:21`）在 `src/` 内零引用；**`pdf_qt.QtImagePdfComposer` 未注入**——`bootstrap/app.py:837` `ExportService(SqliteExportHistoryStore(conn))` 未传 `pdf_composer`，缺它时 `application/export/service.py:412-415` 抛 `PdfUnavailableError`。

### 2.6 大二进制边界现状（对应 AD-001 约束 4）

| 边界 | 形态 | 证据 |
|---|---|---|
| provider 步骤输入（帧） | **整页 raw RGB32 `bytes`** + 宽高 | `bootstrap/app.py:283-288`（`ImageFrame(width, height, "rgb32", bytes(image.constBits()))`） |
| provider 步骤输入（区域） | 裁剪 **PNG `bytes`** + 宽高 | `bootstrap/app.py:290-320` |
| 颜色步骤输入 | 整页 **PNG `bytes`** | `bootstrap/app.py:322-334` |
| 合成器边界 | PNG bytes in → PNG bytes out | `infrastructure/rendering/qt_compositor.py:40`、`:53-59` |
| 排版边界 | `LayoutRequest` dataclass → `LayoutResult` dataclass | `infrastructure/rendering/qt_layout.py:47` |
| PDF 合成 | 图像 bytes 序列 → PDF bytes | `application/export/pdf_qt.py:18` |
| Webtoon 分块到 UI | **文件 URI**（像素落盘，不进 IPC） | `ui/viewmodels/reader/viewmodel.py:425` `QUrl.fromLocalFile(str(path)).toString()`；`webtoon_tiles.py:317 tile_file() -> Path` |
| 导入落盘 | Managed Copy（源文件只读 + 托管副本） | `infrastructure/importing.py:84-115` |

结论（事实层）：**当前 UI 已经用文件 URI 传递分块像素**（可复用模式），但 provider/渲染链在**进程内**以大块 bytes 传递整页像素；一旦这些边界变成跨语言 IPC，必须按 AD-001 约束 4 另行决定传输方式（本报告不选型）。

## 3. 分类矩阵（D1-AC4）

分类语义：`KEEP` = 现状可复用、无需变更；`DECOUPLE` = 职责边界需要拆开（实现可保留，接口需重新定位）；`REPLACE` = 需要后续决策的替代候选（**不代表授权重写**）；`LEGACY` = 现状生产 UI，按 parity Gate 逐步退出；`UNVERIFIED` = 现有环境无法证实。

| ID | 位置（证据） | 耦合与职责 | 分类 | 理由 | 对 headless 的影响 | 风险 / 可复用条件 | 后续候选切片 |
|---|---|---|---|---|---|---|---|
| M2D1-01 | `src/domain/**`（13 mods, 1584 行） | 零 Qt / 零 sqlite3 / 零 IO；3 处纯度注释 `books/entities.py:3`、`constraints/entities.py:3`、`regions/entities.py:3` | **KEEP** | 探针 13/13 OK；纯度声明与实现一致 | 无阻塞 | 无 | — |
| M2D1-02 | `src/ports/**`（23 mods, 2164 行） | 纯 Protocol + DTO；`rendering/ports.py:5` 声明「free of Qt/sqlite types」 | **KEEP** | 探针 23/23 OK；零第三方 | 无阻塞 | 无 | — |
| M2D1-03 | `src/application/**` 除 `export/pdf_qt.py`（65 mods） | 用例/服务编排；依赖方向仅 application→ports→domain | **KEEP** | 探针 66/66 OK；零 `infrastructure/ui/bootstrap` 导入 | 无阻塞 | 无 | — |
| M2D1-04 | `src/application/export/pdf_qt.py:15-45` | `PdfComposer` 适配器；Qt 惰性 `:19-20`（`QImage`/`QPdfWriter`） | **DECOUPLE** | 它是 **application 层唯一 Qt 点**，层界例外；端口 `application/export/ports.py:25` 已存在，实现应落在 infrastructure 并由装配注入 | 导入期无阻塞（惰性），但调用即需 Qt | 低：端口已在；且**生产未接线**（`bootstrap/app.py:837`），迁移前需先裁定 PDF 路径是否要恢复可用 | 与 M2D1-16 合并为一个「装配与层界」切片 |
| M2D1-05 | `src/infrastructure/sqlite/**`（10 files, 4056 行） | 仓储/迁移/事务/备份；连接工厂 `connection.py:347` | **KEEP** | 零 Qt（仅 2 处注释提及）；探针 OK；单连接工厂 | 无阻塞（其调用者 bootstrap 有阻塞，见 M2D1-16） | 无；是「SQLite = 持久事实源」的落点 | — |
| M2D1-06 | `src/infrastructure/providers/step_writes.py:207-513` | `RegionStepWriter`/`ArtifactStepWriter`：**sqlite 包之外唯一的直接 SQL 写者**（5 条写语句 + 4 次 commit，含 3 处显式 `BEGIN IMMEDIATE`） | **KEEP**（附 NOTE） | 零 Qt，属 Python Core；但它是写者边界的**有意例外**（docstring `:1-11` 自述 frozen layers 无法修改才在此提供） | 对 headless 无 Qt 影响 | 风险：写者权威被两个包分担，M2 收敛时需明确归属 | 独立治理切片（非本 Task 授权范围） |
| M2D1-07 | `src/infrastructure/rendering/locator.py:20-50` | `SqlitePageArtifactLocator`：只读 SQLite（SELECT） | **KEEP** | 零 Qt；探针 OK | 无阻塞 | 无 | — |
| M2D1-08 | `src/infrastructure/imaging/{streaming_png,webtoon_tiles,tile_cache_sweep}.py` | 纯 stdlib PNG 扫描带读写 + 瓦片几何/LRU/按需解码 | **KEEP** | 零 Qt（`webtoon_tiles.py:21-23` 自述「no Qt import at all」；`streaming_png.py:48-50` 仅 `struct/zlib/accumulate`）；探针 OK | **正面**：已证明不依赖 Qt PNG handler 的像素通路存在 | 无；这是 M2 最可复用的既有资产 | 可作为未来 tile 传输/解码决策的输入 |
| M2D1-09 | `src/infrastructure/{transport,network,filesystem,credentials,settings,devices}/**`、`pipeline/assembly.py`、`providers/**`（除 step_writes 的写者属性） | 传输/代理/诊断、受控文件发布、凭据、provider runtime、pipeline 装配 | **KEEP** | 探针全 OK；零 Qt（`connect` 命中均为 socket/代理语义） | 无阻塞 | 无 | — |
| M2D1-10 | `src/infrastructure/importing.py`（`:46-47`、`:180-181`、`:354-355` 惰性 Qt） | `QtImageDecoder`/`PdfiumDocumentRaster`/`MobiDocumentRaster`/`ManagedCopyStoreAdapter` | **DECOUPLE** | 容器发现/排序/DRM 判定/Managed Copy 已是纯 stdlib 或 `pypdfium2`/`mobi`（`:142`、`:269`、`:386-398`）；**仅像素栅格化与 PNG 编码**用 `QImage`（`:211-222`、`:364-377`） | 导入期无阻塞；调用 `decode`/`render_page` 即需 Qt | 中：需为 PDF/MOBI 栅格与 PNG 编码选择替代（同仓 `streaming_png` 只解决 PNG 编解码，不解决 PDF 渲染） | 「导入面拆分：容器/元数据 vs 像素栅格」 |
| M2D1-11 | `src/infrastructure/rendering/qt_compositor.py:39-132` | `QtImageCompositor`；public 边界已是 `compose_page(bytes)->bytes`（`:40`）、`compose_region(bytes,bytes,box,op)->bytes`（`:53-59`） | **DECOUPLE** | Qt 只用在 `QPainter`/`QPainterPath` 绘制（`:80-104`），边界已是字节 | 调用即需 Qt（字体绘制更需平台字体） | 低-中：可另实现同端口；但文字描边/填充语义必须等价 | 「渲染端口实现拆分」 |
| M2D1-12 | `src/infrastructure/rendering/pixel_source_style.py:51-168` | `PixelSourceStyleAnalyzer`：PNG bytes + box → `SourceStyle` dataclass（`:52-54`） | **DECOUPLE** | Qt 仅用于解码与逐像素取色（`:55`、`:74`、`:152`）；同仓已有纯 stdlib PNG 解码器 | 调用即需 Qt | 低：边界干净（bytes/dataclass） | 同上 |
| M2D1-13 | `src/infrastructure/rendering/font_catalog.py:11-35` | `QtFontCatalog.resolve(family)->ResolvedFont`；用 `QFontDatabase.hasFamily`（`:28`、`:31`）与 `QFont().family()`（`:34`） | **REPLACE**（候选） | 职责是**枚举操作系统已安装字体**，Qt 之外无同层等价物；返回类型已是纯 dataclass（`ports/rendering/ports.py:68-72`） | 调用即需 Qt 且需平台字体库 | 决策点：无头/未来 UI 的字体来源与回退链（现回退链 `:16-23` 面向 Windows 产品边界） | 「字体与文本度量决策」切片（不选型） |
| M2D1-14 | `src/infrastructure/rendering/qt_layout.py:43-152` | `QtTextLayoutEngine.layout(LayoutRequest)->LayoutResult`；用 `QFont`/`QFontMetrics`（`:15`、`:49-51`、`:88-149`） | **REPLACE**（候选） | 文本度量/换行/竖排依赖 Qt 字体整形；无 Qt-free 等价实现 | 调用即需 Qt；仓库测试明示 offscreen 无字体库 | 决策点：度量/整形栈（且必须与 M2D1-11 的绘制语义一致） | 同 M2D1-13/11 合并 |
| M2D1-15 | `src/bootstrap/app.py`（`:36-42` 模块级 + `:256/:284/:291-292/:324/:418-419/:1147-1148` 惰性） | 组合根 + GUI 入口 + 三个 Qt 图像适配器（`_ManagedPageImageSource`、`_render_content_decoder`、`_grab_and_quit`） | **DECOUPLE** | Core 装配（`:596-1014`，除 Qt 渲染栈外）与 Qt 外壳/像素助手混在同一模块；`main()` 无条件 Qt+QML | **主阻塞**：`import bootstrap.app` 即需 Qt；`main()` 必然创建 QGuiApplication | 中：需把 Core 装配与 Qt 外壳拆成两个入口/两段函数，并把 Qt 图像助手移入 infrastructure | 「Core-only 装配缝」——最小可验证切片 |
| M2D1-16 | `src/ui/viewmodels/**`（14 个实现模块中的 9 个 + 5 个包 `__init__`，共 16 个 Qt 阻塞模块名） | QObject/Property/Signal/Slot 投影 + **混入的业务编排**；依赖 application 服务 | **LEGACY** | 现状生产 UI 的投影契约；AD-001 §30/§32 要求 parity 后才移除 | 导入即需 Qt | 中：编排调用多数已在 application 服务内；但按方法体估算，5 个含业务面的 VM 仍有 **≈55%~60% 的方法体属于业务编排**（判断值，非代码标记）：Settings ≈75%、Export ≈65%、Workbench ≈60%、Reader ≈55%、Bookshelf ≈50%；Navigation ≈10% | 「VM 编排残留审计 → 下沉 Core」：优先 Workbench 运行生命周期与 restore 准入、Settings 配置与凭据、Export 导出策略与线程 |
| M2D1-25 | `src/ui/models/tasks/projection.py`（336 行） | `PipelineRun → TaskProjection` 的纯数据投影/按钮矩阵/步骤流；`:16-17` 自述「no Qt imports, so tests can assert on it directly」 | **DECOUPLE** | 探针 P6：**按文件路径可加载、按模块名不可**；逻辑本身零 Qt，属 Core 形状却位于 UI 树 | 直接阻塞：包 `__init__` 使按名导入即失败 | 低：只需把模块迁出 UI 树（或避免在 `__init__` 重导出 Qt 兄弟） | 「Qt-free 逻辑迁出 UI 树」——成本最低的先行切片 |
| M2D1-26 | `src/ui/viewmodels/workbench/region_canvas.py`（97 行） | 归一化→页面像素几何 + 拒绝规则（`:38-39` half-up 舍入、`:42-56/:91-95` 非零面积）；`:3` 自述「Qt-free by design」 | **DECOUPLE** | 探针 P6 同结论；该模块承载**域规则**（几何校验）却是 UI 树内的工具模块 | 直接阻塞：同上 | 低：几何校验属域/应用职责，迁移后可被任何前端复用 | 同 M2D1-25 |
| M2D1-17 | `src/ui/models/library/models.py`、`models/tasks/*` | `QAbstractListModel` 角色模型 | **REPLACE**（候选） | 纯投影（角色/行数据），React 侧由状态层重建 | 导入即需 Qt | 低：无业务权威 | 「UI 投影替换」属 M2 后续 Feature 迁移 |
| M2D1-18 | `src/ui/qml/**`（25 files, 3775 行） | 四页 QML + 主题单例（`theme/qmldir` `singleton Tokens 1.0`）+ 3 个窗口 | **LEGACY** | 当前生产 UI 本体；AD-001 §32 要求 React 侧具备 Implementation+Tests+Visual/Behaviour Verification+Parity 证据后才可移除 | 需 QML 运行时 | 中：`Main.qml` 仅挂载 `AppShell`（`:32-34`），页面边界清晰，便于逐页 parity | 「逐页 Feature Parity」切片 |
| M2D1-19 | `ui/viewmodels/export/viewmodel.py:23-24,57-60,410`、`reader/viewmodel.py:185,425` | 平台服务：`QStandardPaths`（Documents 目录回退）、`QDesktopServices.openUrl`（打开目录）、`QUrl.fromLocalFile`（文件 URI 投影） | **DECOUPLE** | 这些是**平台/外壳能力**，不是业务权威；跨 UI 复用时必须由 Core/Shell 提供等价能力 | 调用即需 Qt | 低-中：语义明确（目录解析、打开目录、文件 URI 化） | 「Shell 平台服务边界」切片（与 Tauri shell 职责重合，属 AD-001 §22） |
| M2D1-20 | `run_controller.py:101-130`（QThread/moveToThread/队列信号）、`workbench/viewmodel.py:140`（QTimer 轮询）、`reader/viewmodel.py:69`（心跳 QTimer） | UI 侧并发/定时：worker 线程跑 `PipelineService.execute_run`、轮询刷新、阅读时长结算 | **DECOUPLE** | 真正的执行在 application/infrastructure；Qt 只承担线程与事件投递 | 导入即需 Qt | 中：需保证「两个写者线程」的连接隔离语义在未来外壳中仍成立（见 §2.5） | 「执行与事件投递边界」切片 |
| M2D1-21 | 无第二入口：`git ls-files` 零 `main.py`/`__main__.py`/`*.spec`；`bootstrap/app.py:1077/:1182` 是唯一入口 | 不存在可装配/运行 Core 的 headless 入口 | **DECOUPLE** | 缺一个「只装配 Core（无 Qt GUI/QML）」的入口或工厂 | **主阻塞**（与 M2D1-15 同源） | 低-中：`assemble_services` 的可复用部分已存在，需要参数化/拆分 Qt 渲染栈 | 同 M2D1-15 |
| M2D1-22 | 仓库测试夹具：`tests/rendering/conftest.py:3-6`、`tests/ui_shell/conftest.py:3-5`、`tests/workbench/conftest.py:3-6`、`tests/core/test_shutdown_drain.py:40-41`、`tests/core/test_bootstrap.py:3-5` | 「offscreen 平台不带字体数据库」「入口证据禁止强制 offscreen」 | **UNVERIFIED** | 本环境无 PySide6，无法运行任何 Qt 平台实验；offline 结论只能引用仓库自带陈述与静态依赖 | 直接决定「无 GUI 是否可行」 | 需在装有 PySide6（并对齐 3.12 口径）的环境复现：`QGuiApplication` + `QFontDatabase` 在 windows/offscreen/minimal 平台下的行为 | 「Headless 可行性实验」切片（新 Task，需装依赖） |
| M2D1-23 | `bootstrap/app.py:283-288`（整页 RGB32 bytes）、`:290-320`/`:322-334`（PNG bytes）、`qt_compositor.py:40/53`、`pdf_qt.py:18`、`reader/viewmodel.py:425`（文件 URI） | 大二进制边界的现状形态 | **DECOUPLE** | 分块像素已走文件 URI（可 KEEP 的模式）；整页 raw/PNG bytes 若跨语言必须重新设计传输 | 不直接阻塞 headless；阻塞未来 IPC 设计 | 中：需要容量/生命周期/安全验证（AD-001 §33 要求 later spike） | 「二进制传输 spike」切片 |
| M2D1-24 | `src/infrastructure/{pipeline,providers}`（除 step_writes 写属性）、`src/infrastructure/{sqlite,transport,filesystem,...}` 组合 | Core 的非 UI 基础设施整体 | **KEEP** | 探针 52/56 OK（失败 4 个均属 rendering）；零 Qt | 无阻塞 | 无 | — |

**分类计数**（26 项）：**KEEP 9**（M2D1-01/02/03/05/06/07/08/09/24）、**DECOUPLE 11**（04/10/11/12/15/19/20/21/23/25/26）、**REPLACE 3**（13/14/17）、**LEGACY 2**（16/18）、**UNVERIFIED 1**（22）。

## 4. Headless 可行性（D1-AC3）

**静态结论（可复现）**：当前**不存在**可运行的 headless 生产入口，且阻塞分两层、互相独立：

1. **入口/组合根层**：`src/bootstrap/app.py:36-42` 模块级导入 4 个 PySide6 模块 → `import bootstrap.app` 在无 Qt 环境必然失败（`06-…log` P2/P3，`EXIT=1`，`ModuleNotFoundError` @ `:36`）；`main()` 无条件 `QGuiApplication`（`:1108`）与 `assemble_engine`（`:1125`，`:1046` 加载 QML）。即便不使用 GUI，也没有第二个入口（M2D1-21）。
2. **渲染栈层**：生产装配只提供 Qt 端口实现（`bootstrap/app.py:675/676/682/683`），而字体/度量/绘制需要**具备字体数据库的平台插件**；仓库自带的 4 份测试夹具明确记录 offscreen 平台不提供字体库，且入口测试禁止强制 offscreen。

**运行期结论：`UNVERIFIED`（M2D1-22）**，阻塞原因照实记录：本审计环境**未安装 PySide6**（四个解释器均无），无法构造 `QGuiApplication`、无法加载 QML、无法渲染文字；因此「无 GUI 能否装配并运行」既**不能记为可运行**，也**不能记为已证不可行**。

**已证实的一侧（探针 P1）**：`src/domain` + `src/ports` + `src/application` 共 **102 个模块**在未安装 PySide6 的解释器中全部导入成功（`EXIT=0`），说明**Core 的导入面本身已是 headless 的**；但「Core 可被独立装配运行」还需要：非 Qt 的字体/度量/合成/样式端口实现，以及一个不 import bootstrap.app 的 Core 装配入口——这两点今天都不存在。

**本报告不选择**任何替代技术（AD-001 §34：不由本审计决定替代或改造）。

## 5. 待决问题（交 Codex/用户，不在本 Task 决策）

1. 无头与未来 UI 的**字体来源与文本度量**方案（M2D1-13/14）。
2. **PDF/MOBI 栅格化与 PNG 编码**的替代（M2D1-10）；注意同仓 `streaming_png` 已覆盖 PNG 编解码，但不覆盖 PDF 渲染。
3. **PDF 导出路径**是否恢复可用（今天 `pdf_composer` 未接线，`PdfUnavailableError`；M2D1-04）。
4. 跨语言 **IPC 的二进制传输形态**（整页 raw/PNG vs 文件句柄/自定义协议；M2D1-23）。
5. **写者边界**：是否把 `providers/step_writes.py` 的直接 SQL 收敛进 `sqlite/**`（M2D1-06）。
6. 未接线件的归属：`open_readonly`、`SqliteBackupService`、`WebtoonTileCacheSweeper`、`any_in_transaction`/`release_current_thread_connection` 是保持现状还是需要在 M2 前接线（§2.5）。
7. 「SQLite 作为唯一持久事实源」的部分性：trash manifest JSON、provider/network JSON profile stores、Windows 凭据库与 SQLite 并存（§2.5）。
8. `src/ui/qml` 25 文件 / 3775 行的**逐页 parity 顺序**与视觉验收方式（M2D1-18/19）。

## 6. 后续候选切片建议（不构成释放）

按 AD-001 §40 的逻辑顺序，本审计证据支持的最小后继切片：

1. **Core-only 装配缝**（对应 M2D1-15/21）：把 `assemble_services` 中与 Qt 无关的部分抽成可注入端口的装配，使 Core 能在无 Qt 进程内装配；这是解锁一切 headless 验证的最小切片。
2. **Headless 可行性实验**（对应 M2D1-22）：在装有 PySide6 的环境复现 `QGuiApplication` + `QFontDatabase` 在 windows/offscreen/minimal 的行为，给出可引用的实测结论。
3. **渲染端口实现拆分**（M2D1-11/12/13/14）：先做边界已在字节/dataclass 的合成器与样式分析器，再处理字体与度量决策。
4. **导入面拆分**（M2D1-10）：容器/元数据独立于像素栅格。
5. **UI 编排残留审计**（M2D1-16/20）：确认 ViewModel 中还剩多少业务编排需要下沉。
6. 上述均**未**被本 Task 授权；释放需 Codex 另行冻结范围（含 base、allowed paths、Owner、Reviewer）。

## 7. 未验证与限制（照实记录）

- 产品测试套件 **NOT_RUN**（源码未改；Qt 依赖缺失）。
- 一切 Qt 平台行为（字体、绘制、QML 加载）**UNVERIFIED**（无 PySide6）。
- `main()` 的三个模式（`--smoke-test`/`--screenshot`/正常启动）在真实 Qt 环境下**未执行**；`:1139-1170` 的 `shiboken6.wrapInstance` + `grabWindow` 路径未验证。
- 探针只测**导入**，不测行为；探针自身两次运行失败（P1 缺 `import importlib.util`、P6 未在 `exec_module` 前注册 `sys.modules`）均已保留为 `…-ATTEMPT1-failed.log`，不作为结论证据；修正后重跑的结论见对应正式日志。
- `docs/**`、`wiki/**` 的派生描述未作为事实来源（仅源码/测试为准）。
- 未审计 `tests/**` 的实现正确性（仅作为「产品边界/平台事实」的旁证引用其夹具注释）。
- 事务原子性、并发写者互斥等运行时性质为**代码推导**，未做运行时验证（未打开任何数据库）。

## 8. 与 AD-001 约束的对应

| AD-001 约束 | 本审计结论 |
|---|---|
| §21 React 不做 SQLite/Domain；§24/§35 SQLite 由 Python Core 独占写 | **基本成立**：`src/ui/**` 零 SQL；bootstrap 仅 2 条 SELECT；写语句全在 `src/infrastructure/**`。例外/部分性见 M2D1-06 与 §2.5 |
| §22 Rust/Tauri 不承载 domain、不是 DB writer | 当前工作区**不存在** Rust/React/Tauri 产物（`EXIT=1` 零命中），该约束目前靠「不存在」成立 |
| §23/§34 Core 最终 headless；Qt 依赖 `MIGRATION_AUDIT_REQUIRED` | **本 Task 即该审计**：Qt 依赖已枚举为 21 个模块；Core 导入面已证实 Qt-free；生产装配尚不可 headless（§4） |
| §30 增量/Strangler，无 big bang | 支持：Qt 面集中在 UI/渲染/入口，Core 与图像瓦片通路可原样复用 |
| §32 parity 后才移除 QML | 支持：`src/ui` 与 Core 之间已有端口/服务边界（§2.4） |
| §33 大二进制不得走普通 JSON/Base64 IPC | 现状：分块像素已走文件 URI（可复用）；整页 raw/PNG bytes 为进程内边界，跨语言前需 spike（M2D1-23） |
| §31 不重写正常工作的 domain/application/ports | 支持：这三层零 Qt，迁移无需重写 |
