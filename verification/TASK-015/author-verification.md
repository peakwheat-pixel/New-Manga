# TASK-015 作者验证（实现 head `488fafc`）

取代 [fac2ffe 轮](author-verification.md@6917b0b) 的同文件记录（Git 历史可溯）；本轮实现按
协作协议 §5 生成新的 head 与 Handoff，见 [TASK-015-488fafc](../../doc/handoffs/TASK-015-488fafc.md)。

## 环境

- OS：Windows 11 Pro（win32 10.0.26200 x64），Git Bash + PowerShell 混用
- 工作路径：`G:/CODEX/New Manga.worktrees/TASK-015-zcode`
- 固定基线：`1000ac82743b75df8b4b385bc7096a015e13f107`
- 被验证实现 head：`488fafc`
- **环境 A（完整 Qt）**：`G:/CODEX/New Manga.task-envs/TASK-014-py312/Scripts/python.exe`，
  Python 3.12.3，PySide6 6.11.2（`PySide6_Essentials`），pytest 9.1.1
- **环境 B（无 Qt）**：`C:/Python314/python.exe`，Python 3.14.6，pytest 9.1.1，
  `importlib.util.find_spec('PySide6') is False`

## 结果

### 环境 A：完整功能验证（命令与退出码逐条）

| # | 精确命令（Git Bash，CWD=worktree） | 退出码 | passed | skipped | 结论 |
|---|---|---:|---:|---:|---|
| A1 | `PYTHONPATH=src "$PY" -m pytest tests/reading_export -q` | 0 | 63 | 0 | PASS：专项 63 例（阅读 15 / 导出 28 / ViewModel 12 / QML 契约 8） |
| A2 | `PYTHONPATH=src "$PY" -m pytest tests -q` | 0 | 535 | 0 | PASS：全仓回归（连续两轮运行均 535 passed，无顺序依赖） |
| A3 | `PYTHONPATH=src "$PY" -m pytest tests --collect-only -q` | 0 | 535 collected | — | PASS：收集数一致 |

### 环境 B：无 PySide6 解释器的分列行为

| # | 精确命令 | 退出码 | passed | skipped | skip 原因 |
|---|---|---:|---:|---:|---|
| B1 | `PYTHONPATH=src python -m pytest tests/reading_export -q` | 0 | 42 | 3 | 见下 |
| B2 | `PYTHONPATH=src python -m pytest tests -q` | 1 | — | 8 skipped + 6 collection errors | 6 个 error 均为 `ModuleNotFoundError: No module named 'PySide6'`（tests/workbench、tests/ui_shell 等 Qt 套件收集失败）；与 TASK-013 记录一致：该解释器不具备 Qt 依赖，非本 Task 引入 |

B1 的 3 个 skip 逐条原因（`-rs` 输出原文）：

1. `SKIPPED [1] tests\reading_export\test_qml_contract.py:21: PySide6 not installed in this interpreter`（QML 契约 8 例整体跳过）
2. `SKIPPED [1] tests\reading_export\test_viewmodels.py:21: PySide6 not installed in this interpreter`（ViewModel 12 例整体跳过）
3. `SKIPPED [1] tests\reading_export\test_export.py:421: PySide6 not installed`（真实 Qt PDF 回读 1 例）

## AC 覆盖对照（测试证据）

| AC | 覆盖测试（tests/reading_export/） | 结果 |
|---|---|---|
| AC-READ-001 模式切换 | test_reading::test_modes_keep_independent_progress_and_duration；test_viewmodels::test_reader_open_chapter_exposes_state | PASS |
| AC-READ-002 独立进度 | 同上 + 重启恢复 test_resume_restores_position_and_duration_after_restart | PASS |
| AC-READ-003 RTL | test_qml_contract::test_reader_rtl_ltr_key_order（RTL Left=前进） | PASS（环境 A） |
| AC-READ-004 LTR | 同上（LTR Right=前进） | PASS（环境 A） |
| AC-READ-005 Webtoon | test_reader_webtoon_swaps_in_vertical_viewer（纵向 Flickable + scroll_offset_y 持久化）；完整按宽滚动验收归 TASK-020 | PASS（环境 A，部分转 TASK-020） |
| AC-LIB-004 书架摘要 | test_book_summary_shape_for_ac_lib_004（最近章节/进度/最后阅读/累计时长） | PASS |
| AC-EXPORT-001 五格式 | test_zip_*、test_cbz_*、test_single_image_*、test_pdf_*、test_text_* | PASS |
| AC-EXPORT-002 History | test_history_row_carries_d03_31_fields（D03 §31 全字段） | PASS |
| AC-EXPORT-003 Stale | test_translated_export_with_stale_pages_is_refused_by_default / …continue_with_existing_versions；QML banner 测试 | PASS |
| 重启继续阅读 | test_resume_restores_position_and_duration_after_restart；test_webtoon_scroll_offset_persisted_and_restored | PASS |
| 缺译图 | test_missing_translated_shows_original_with_message；test_translated_export_can_explicitly_continue…（原图替代） | PASS |
| Unicode 文件名 | test_zip_keeps_scope_order_and_unicode_names；test_auto_rename…；VM test：书名.zip | PASS |
| 已有目标文件 | overwrite/skip/auto_rename 三策略各 1 例 | PASS |
| 磁盘错误 | test_disk_error_on_final_write_keeps_target；test_failure_mid_export…；test_store_write_failure… | PASS |
| 取消保护 | test_cancel_before_replace_publishes_nothing；VM cancel 测试 | PASS |
| 产物重读 | zip 回读（namelist+testzip）；PDF 结构回读（页数/xref）；text 回读；真实 Qt PDF 头尾+页对象计数 | PASS |
| 失败/取消不破坏源文件 | test_source_files_are_never_modified | PASS |

## NOT_RUN / BLOCKED 项（不掩盖）

| 项 | 状态 | 原因与恢复条件 |
|---|---|---|
| PDF 外部阅读器像素级验收 | NOT_RUN | 环境 A 无 PDF 阅读器与 QtPdf 模块（PySide6 Essentials 不含）；当前为结构级回读。恢复条件：装有阅读器的验收机 |
| 真实磁盘满/权限拒绝注入 | NOT_RUN（以 monkeypatch 注入 OSError 等价覆盖控制流） | 需受控 Windows 测试卷；服务路径已有 temp+replace 保护并有 monkeypatch 用例 |
| Webtoon 完整按宽滚动验收 | 移交 TASK-020（Task 文件已注明） | 需长图渲染切片；本 Task 交付数据字段、纵向 Flickable 与 scroll_offset 持久化 |
| 生产装配接线（bootstrap 注入 readerViewModel / 页面目录 adapter） | NOT_IN_SCOPE | `src/bootstrap/app.py` 不在 TASK-015 允许路径；接线代码见 Handoff §集成装配指引，待 Codex 集成 |
| 章节内切换列表（Reader Nav 数据源） | NOT_IN_SCOPE | 章节列表数据源在 library/bookshelf 装配（白名单外）；`readerPickChapter` 保持 TASK-012 诚实占位（禁用） |
