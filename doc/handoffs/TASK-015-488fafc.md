---
task_id: TASK-015
author: ZCode
recipient: DeepSeek Harness（独立 Review）、Codex（集成）
base_commit: 1000ac82743b75df8b4b385bc7096a015e13f107
delivery_head: 488fafc
supersedes: TASK-015-fac2ffe.md（前轮 head fac2ffe 的实现已被本 head 完全重写取代，请仅审查 1000ac8..488fafc）
status: in_review
---

# Handoff：TASK-015 阅读器与五种成果导出（第二轮交付）

## 为什么有第二轮

前轮交付 `fac2ffe`（handoff `TASK-015-fac2ffe.md`，`6917b0b`）在会话中断后经复核
不满足 Task 的 AC 深度（服务层缺 D03 §29/31 字段语义、无方向/类型校验、导出无
覆盖策略三态与 History 字段完整性、QML 与 D05 §37~42/51 不符、测试仅 8 例）。
本轮按协议 §5 全量重写并生成新 head，请 Review 固定 `1000ac8..488fafc`。
旧 handoff 文件在本提交中删除（Git 历史可溯）。

## 提交列表

- `488fafc` feat: rewrite reader session and five-format export per D03/D04/D05/D06
  （17 files，+3813/−395；本 head 即交付内容）

变更路径全部在 Task 白名单内：`src/application/reading/**`、`src/application/export/**`、
`src/ui/qml/reader/**`、`src/ui/viewmodels/reader/**`、`src/ui/qml/windows/ExportWindow.qml`、
`src/ui/viewmodels/export/**`、`tests/reading_export/**`（未触碰 Schema/migration、共享
Protocol、依赖清单、AGENTS、其他 Task 与 bootstrap）。

## 做了什么

### application/reading（D03 §29、D04 §33~36、D05 §37~41）

- `ports.py`：`ReaderPage`（含 translated/current revision 对 → stale 判定）、
  `ReaderPageCatalog` 端口、`ProgressDocumentStore` 端口 + 原子 JSON 实现。
- `service.py`：`ReadingService`——进度行按 D03 §29 字段（progress_id/last_page_id/
  scroll_offset_x_y/progress_percent/last_read_at/total_read_seconds/updated_at），
  以 `(book_id, chapter_id, mode)` 为主键**每模式独立位置与时长**（AC-READ-001/002）；
  webtoon ⇔ vertical、paged ⇔ rtl/ltr 校验（D03 §4.2）；恢复按 last_page_id 优先、
  页面消失时钳制（重排不丢位置、缩章不越界）；缺译图回退原图 + 明确提示、stale
  译图保持显示 + 明确提示（D06 §97 精神）；`book_summary`/`chapter_summaries`
  提供 AC-LIB-004 书架摘要数据（同秒写入有确定性 tie-break）。

### application/export（D03 §31、D04 §37、D06 §96~97）

- `ports.py`：`PdfComposer` 端口（PDF 编码可注入）、`HistoryDocumentStore` + 原子 JSON。
- `service.py`：五种格式（`single_image/zip/cbz/pdf/text`）；范围=调用方给定页序；
  归档条目 `NNNN_安全文件名`（保 Unicode、去路径穿越与 Windows 非法字符）；
  覆盖策略 overwrite/skip/auto_rename；stale/缺译默认拒绝（`StaleExportError`
  列出页并列出两个用户选项），`stale_policy=continue` 显式继续（stale 用现有译图、
  缺译以原图替代并在结果与 History 留痕）；**临时文件 + `os.replace` 末步提交**，
  取消/失败/磁盘错误清理 temp 且既有目标与源文件不动（源只读）；ExportHistory
  记录 D03 §31 全字段 + status(completed/skipped/cancelled/failed) + detail；
  `repeat()` 按快照"使用相同设置再次导出"。
- `pdf_qt.py`：Qt PDF composer（QPdfWriter，页面=图像尺寸）；PySide6 在 `compose`
  内延迟导入，无 Qt 环境的导入/测试不受影响；未注入 composer 时 PDF 明确报
  `PdfUnavailableError`，不静默产出占位文件。

### UI（D05 §37~42、§51）

- `ReaderViewModel`：openChapter（经注入 catalog）、模式/翻页/跳页、webtoon
  scroll 保存恢复、5s 心跳 + 每操作 `settleReadingTime` 累计时长（崩溃粒度=心跳）、
  `bookSummary` 摘要、`openExporter()` 惰性创建导出控制器。
- `ExportViewModel`：D05 §51 全字段（范围/格式/内容模式/输出/覆盖/ stale 策略）、
  D06 §97 stale 警告文案流转（abort=提示重渲染或继续、continue=确认文案）、
  后台线程导出 + 协作取消、`openOutputFolder`（可注入，默认 QDesktopServices）、
  `repeatExport`。
- `ReaderView.qml`：Toolbar（章节标题/模式高亮/上一页下一页/继续上次位置/从头
  开始/进度显示/导出入口/`readerPickChapter` 保持 TASK-012 禁用占位）、缺译与
  stale 横幅、paged 键序（RTL：Left=前进；LTR：Right=前进）、webtoon 纵向
  Flickable（按宽适配 + 500ms 节流保存 scroll_offset_y + 恢复）、无 ViewModel
  时空态可加载（`typeof` 保护，生产装配未注入不崩溃）。
- `ExportWindow.qml`：controller 由阅读器传入或 `exportViewModel` 上下文属性兜底；
  导出/取消/打开所在文件夹/再次导出（D03 §31/D04 §37）；stale 横幅常显逻辑。

## 测试（63 例；证据见 author-verification）

| 环境 | 命令 | 退出码 | 结果 |
|---|---|---:|---|
| Python 3.12.3 + PySide6 6.11.2（task-envs/TASK-014-py312） | `PYTHONPATH=src python -m pytest tests/reading_export -q` | 0 | 63 passed, 0 skipped |
| 同上 | `PYTHONPATH=src python -m pytest tests -q` | 0 | 535 passed, 0 skipped（两轮稳定） |
| Python 3.14.6 无 PySide6 | 同专项命令 | 0 | 42 passed, 3 skipped（skip 原因逐条记录） |

覆盖：重启继续阅读、双模式独立进度/时长、RTL/LTR 键序（QML 实测键事件）、
webtoon scroll 持久化、缺译图、stale 拦截/继续、五格式内容与页序、Unicode 与
非法文件名、覆盖三策略、取消/失败/磁盘错误下目标与源文件完好、ExportHistory
字段、repeat、产物回读（zip testzip、PDF 结构、text、真实 Qt PDF 头尾+页数）。

## 未跑项与风险（诚实清单）

- PDF 像素级外部阅读器验收 NOT_RUN（Essentials 无 QtPdf、验收机无阅读器）；
  当前为结构级回读。
- 真实磁盘满/权限拒绝未注入（用 monkeypatch OSError 覆盖同一控制流）。
- Webtoon 完整按宽滚动验收归 TASK-020；本 Task 交付数据链路。
- 生产装配接线不在白名单：`bootstrap/app.py` 未注入 `readerViewModel`，生产
  ReaderView 当前显示空态（不崩溃）。接线指引见下节。
- 阅读进度/ExportHistory 落 JSON 文档存储（行结构=未来 SQLite 列结构）；
  Schema/migration 冻结不可改，迁移入库待后续 Task。
- AC-LIB-004 的 BookDetailPanel 显示接线不在白名单（该文件属于 TASK-007/012
  范围）；本 Task 交付 `ReadingService.book_summary()/chapter_summaries()` 数据
  与字段语义，UI 接线需 Codex 明确范围变更。

## 集成装配指引（Codex；以下文件均不在本 Task 白名单）

1. `bootstrap/app.py` 组装（composition root 内，与 `_ManagedPageCatalog` 同模式）：

   ```python
   from application.export import ExportService, JsonHistoryDocumentStore
   from application.export.pdf_qt import QtImagePdfComposer
   from application.reading import ReadingService
   from ui.viewmodels.reader.viewmodel import ReaderViewModel

   reading = ReadingService(JsonProgressDocumentStore(data_root / "reading_progress.json"))
   export_service = ExportService(
       JsonHistoryDocumentStore(data_root / "export_history.json"),
       pdf_composer=QtImagePdfComposer(),
   )
   reader = ReaderViewModel(reading, <ReaderPageCatalog adapter>, export_service=export_service)
   root_context.setContextProperty("readerViewModel", reader)
   ```

   `<ReaderPageCatalog adapter>`：按 `SqliteLibraryRepository.list_pages(chapter_id)`
   （sort_order 序）组装 `ReaderPage`；译图路径与 revision 取自
   `SqliteArtifactRepository`（需按 `(page_id, artifact_type='translated')` 查
   current revision——现有接口无按页查询，需要一条 SELECT 或补充仓储方法，
   这属于共享接口变更，须 Codex 裁量）；`text` 聚合 Region `final_translation`。
2. 书架入口已具备：`BookshelfViewModel.enterReading()`（TASK-012）发出
   `readerContext`；ReaderViewModel.openChapter 由装配层桥接该上下文。
3. ExportHistory/reading_progress 文件建议放 `data_root`（与 library.db 同级）。

## 复现方式

- 专项：`PYTHONPATH=src python -m pytest tests/reading_export -q`
- 全量：`PYTHONPATH=src python -m pytest tests -q`（需含 PySide6 的解释器；
  推荐任务环境 `G:/CODEX/New Manga.task-envs/TASK-014-py312`）
- 人工冒烟（可选）：`PYTHONPATH=src python -m bootstrap.app --smoke-test`

## 下一接收者

DeepSeek Harness 独立 Review（固定 `base=1000ac8`、`head=488fafc`）；Review 通过后
由 Codex 按协议 §6 集成并决定装配接线/SQLite 迁移的范围变更登记。Owner 不自标
approved/done。
