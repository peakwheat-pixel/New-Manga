# TASK-005 集成验证

- 日期：2026-09-14（Asia/Shanghai）
- `base_commit`：`d65901b953e6fb26043344ed3d668520847eb295`
- `reviewed_head`：`f3430080d88f07d789c21e76d5b5b4310fbf3458`
- `integration_commit`：`6607f751c61663e589cf73b6a7bdebf65b9edc45`
- 环境：Windows `10.0.26200.0`；Python `3.12.3`；pytest `9.1.1`

## 结果

| 检查 | 结果 |
|---|---|
| `verification/TASK-005/verify.ps1` 固定 base/head 复跑 | PASS；退出码 0；16 个允许路径、精确依赖、Python 环境、6 个 core 测试、真实 QML smoke、链接/围栏与 fixed-head diff check 均通过 |
| `python -m pytest tests/core` | PASS；退出码 0；6 passed |
| `git diff --check d65901b 6607f75 --` | PASS；退出码 0 |
| `git diff --name-only d65901b 6607f75` | PASS；18 个路径；未修改 TASK-006～TASK-027 |
| merge | PASS；`ort` 无冲突 |

### verify.ps1 完整复现命令

固定 base/head 复跑所用完整命令如下。该命令在 `integration_commit=6607f75` 的主线（master）环境复跑：工作区当时 checkout `6607f75`，`-ReviewedHead` 显式传入 `f343008`（而非默认 `HEAD`），保证被验证对象严格为被审 head 而非 merge commit：

```bash
pwsh -NoProfile -File ./verification/TASK-005/verify.ps1 -BaseCommit d65901b953e6fb26043344ed3d668520847eb295 -ReviewedHead f3430080d88f07d789c21e76d5b5b4310fbf3458 -PythonExe 'G:/CODEX/New Manga.task-envs/TASK-005-py312/Scripts/python.exe'
```

实际结果以上表为准，保持不变：退出码 0；依赖检查（`pip check` 与 torch/transformers/onnxruntime 缺失断言）PASS；`tests/core` 6 tests passed；真实 QML smoke PASS。

PyInstaller、干净 Windows VM、正常交互窗口、SQL、Provider、模型质量与性能仍为 `NOT_RUN` / `N/A`；本 Task 只证明最小工程入口和架构守卫，不证明业务功能或发布就绪。
