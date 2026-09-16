# TASK-015 作者验证

## 环境

- Windows 10/11 PowerShell，工作路径 `G:/CODEX/New Manga.worktrees/TASK-015-zcode`
- Python `3.14.6`（`C:/Python314/python.exe`）
- pytest `9.1.1`
- `PySide6`：当前解释器未安装（`importlib.util.find_spec('PySide6') == False`）
- 固定基线：`1000ac82743b75df8b4b385bc7096a015e13f107`
- 被验证实现 head：`fac2ffe`

## 结果

| 项目 | 精确命令 | 退出码 | passed | skipped | 结论/原因 |
|---|---|---:|---:|---:|---|
| TASK-015 专项 | `$env:PYTHONPATH='src'; python -m pytest tests/reading_export -q` | 0 | 8 | 0 | PASS |
| Python 编译 | `$env:PYTHONPATH='src'; python -m compileall -q src/application/reading src/application/export src/ui/viewmodels/reader src/ui/viewmodels/export` | 0 | — | — | PASS |
| 全仓回归 | `$env:PYTHONPATH='src'; python -m pytest tests -q` | 1 | — | 6 | BLOCKED：6 个既有 Qt 测试收集错误，均为 `ModuleNotFoundError: No module named 'PySide6'`；6 个 skip 原因为既有 `openssl unavailable` |
| QML/Qt 运行时 | 无可执行 `qml/qmlscene`，且当前 Python 无 PySide6 | — | — | — | BLOCKED/NOT_RUN：缺 Qt 运行环境 |

专项测试覆盖：Original/Translated 模式与模式独立进度/时长、RTL/LTR、重启恢复、缺译图、stale 提示；PNG/ZIP/CBZ/PDF/TXT、稳定顺序、Unicode 文件名、路径穿越拒绝、覆盖策略、取消/失败目标保护和 ExportHistory。

## 未运行项

- 真实 PySide6 QML 加载、方向切换渲染和 Qt 图片 PDF 分支：`BLOCKED/NOT_RUN`，当前解释器没有 requirements 中的 PySide6。
- 真实磁盘满/权限拒绝：`NOT_RUN`，需要受控 Windows 测试卷；代码沿用 OS 异常并在临时文件失败时清理。
- 产物在外部阅读器的 PDF 像素级验收：`NOT_RUN`，当前环境无 Qt/PDF 阅读器；专项测试只验证有效 PDF 头/尾，不能替代外部阅读器验收。
