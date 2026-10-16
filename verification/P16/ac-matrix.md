# P16 AC 矩阵

固定实现 head 由 `doc/tasks/P16.md` 与 Owner Handoff 记录。基线：`093430c75a46d28ed759ec646039bf2f55e3d429`。
聚焦日志：`verification/P16/pytest-p16.log`；全量 Core 日志：`verification/P16/pytest-tests-core.log`。

| AC | 状态 | 实现 / 判别用例 | 证据与边界 |
|---|---|---|---|
| AC1 | PASS（Core wire） | `test_reader_projection_progress_modes_layouts_and_restart` | 覆盖原图/译图 opaque resource ref、独立 original/translated 进度、RTL/LTR/Webtoon、长图单 Page、source-pixel `scroll_offset_y` 保存重开往返、事件发出前已持久化。contract §6.3 把显示坐标↔原图像素换算放在 Reader view；Core 接收并恢复逻辑 Page 原图像素坐标。WebView 显示转换仍属后续 host/UI 工作。 |
| AC2 | PASS | `test_five_export_formats_preserve_order_hash_lineage_and_pdf_text` | PNG 单页、ZIP、CBZ、PDF image-only/searchable dual-layer、文本 JSON/TXT/Markdown；断言页顺序、文件 SHA-256、每页 lineage/hash/revision、ZIP manifest 与 CBZ ComicInfo、PDF 文本可检索。 |
| AC3 | PASS（安全 Gate） | `test_export_target_ref_rejections_make_zero_target_writes[<case>-<code>]` 六参数；`test_export_target_ref_scope_denial_and_atomic_concurrent_consumption`；`test_replayed_ref_is_never_reconsumed_after_successful_export` | 六拒绝均断言错误码、现存目标字节不变、同目录无临时产物、源原图/译图不变、错误不泄露路径。额外验证 `REF_SCOPE_DENIED`。12 线程竞争只 1 次消费成功，其余 11 次为 replay 拒绝；成功导出后再放同一引用也被拒绝且输出字节不变。 |
| AC4 | PASS | 上述 AC1 Reader 测试、`test_five_export_formats_preserve_order_hash_lineage_and_pdf_text` | 两类事件均为 §3 `Event<T>` JSONL envelope；在持久快照可读后 emit；payload 不含路径或 `ExportTargetRef`。未假设送达、重放或排序。 |
| AC5 | PASS | `test_stale_abort_consumes_ref_and_continue_records_frozen_lineage`；`test_cancel_before_publish_keeps_existing_target_and_cleans_temporary_file` | stale abort 返回 typed detail 且不产生 job；continue lineage 固定旧 revision；取消不覆盖既存文件并清理临时文件；History 记录终态。 |
| AC6 | PASS | `tests/core/test_core_service.py`、`test_core_service_retype.py`、`test_core_service_settings.py`、`test_p13_run_runtime.py` 及其他协议回归 | request/response/event envelope 为 major 2/minor 1。未改 resource channel；§10.1/§10.2 既有读路径与 grant 语义保持原实现。全量 Core 回归见日志。 |
| AC7 | PASS | `verification/P16/scope-audit.md` | 最终 `093430c..HEAD` 文件清单仅在 Task allowlist；未改冻结契约、`pdf_qt.py`、`tests/reading_export/**`、Schema/migration、依赖或 Tauri/Rust。 |
| AC8 | PASS | `tests/core/test_p16_reader_export.py`（12 cases，含 6 个 rejection parameter cases） | P16 聚焦用例 12 passed；全量 `tests/core` 352 passed。AC3 逐类负向与并发/重放判别另见 `ac3-target-ref-matrix.md`。 |
| AC9 | NOT_RUN / BLOCKED（非 Owner 工作） | 非作者独立 Review、Coordinator 集成未执行 | 当前交付进入 `in_review`，本分支固定实现 head 提交；Owner 不自审、不合并。Review 应由 DeepSeek Harness 承担；Review 与集成后需由 Coordinator 运行集成 Gate 并关闭 Task。 |

## 执行摘要

- 环境：`G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe`（Python 3.12 task-env）。
- 聚焦命令：`python -m pytest tests/core/test_p16_reader_export.py -q` → 12 passed，exit code 0。
- 完整命令：`python -m pytest tests/core -q` → 352 passed、0 failed、1 existing Pillow deprecation warning，exit code 0。
- `NOT_RUN`：非作者 Review、Coordinator 集成和集成后 Gate；不把 Owner 自检记作通过。
