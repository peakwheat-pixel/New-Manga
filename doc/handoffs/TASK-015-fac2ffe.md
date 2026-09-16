---
task_id: TASK-015
author: ZCode
recipient: Codex
base_commit: 1000ac82743b75df8b4b385bc7096a015e13f107
delivery_head: fac2ffe
status: in_review
---

# Handoff：TASK-015

## 交付结果

实现阅读器状态服务、五种导出、Reader/Export ViewModel 和 QML 界面。阅读状态与 ExportHistory 使用原子 JSON 状态文件，不修改 Schema/migration；导出先写同目录临时文件并以 `os.replace` 提交，失败/取消不覆盖既有目标。实现提交：`fac2ffe`。

## 验证证据

详见 [author-verification](../../verification/TASK-015/author-verification.md)。专项命令为 `$env:PYTHONPATH='src'; python -m pytest tests/reading_export -q`，退出码 0，`8 passed, 0 skipped`；Python compileall 退出码 0。

| 范围 | 状态 | 证据 |
|---|---|---|
| Original/Translated、RTL/LTR、独立进度/时长、重启、缺译图、stale | PASS（服务层） | `tests/reading_export/test_reading.py` |
| PNG/ZIP/CBZ/PDF/TXT、范围/顺序/命名、覆盖、取消保护、ExportHistory | PASS（服务层） | `tests/reading_export/test_export.py` |
| Reader/Export QML 契约文本 | PASS（静态） | `tests/reading_export/test_qml_contract.py` |
| QML 实际加载、Qt 图片 PDF 分支 | BLOCKED/NOT_RUN | 当前 Python 无 PySide6，无 qml/qmlscene |
| 全仓回归 | BLOCKED | 既有 Qt 测试收集因 PySide6 缺失退出 1；详见 verification |

## 接收方式

分支：`agent/zcode/TASK-015-reader-export`；worktree：`G:/CODEX/New Manga.worktrees/TASK-015-zcode`。请 DeepSeek Harness 在固定 `1000ac82743b75df8b4b385bc7096a015e13f107..fac2ffe` 上独立 Review，重点检查 PDF 可读性、ViewModel/QML 实际装配、状态文件路径注入和异常保护；不得由作者自审或直接集成。

## 风险与遗留

- 当前环境没有 PySide6，QML/Qt 分支为 BLOCKED/NOT_RUN。
- 本 Task 不改 `Main.qml`/bootstrap；生产入口装配需由 Codex按既有装配切片处理。
- 未修改 Schema、共享 Protocol、依赖清单、全局 STATUS 或其他 Task。
