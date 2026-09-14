# TASK-005 作者验证证据

## 固定对象与环境

| 项目 | 实际值 |
|---|---|
| `base_commit` | `d65901b953e6fb26043344ed3d668520847eb295` |
| 首次被测生产/测试提交 | `b318bdd5782681df6ff5398b80f8c597366c5b0b` |
| 首次 `reviewed_head` | `e914f39a0c721f717c45a01229cd6d0b82f0045e`；固定 head 复跑见 [Handoff](../../doc/handoffs/TASK-005-e914f39.md) 与 [独立 Review](../../doc/reviews/TASK-005-e914f39.md) |
| 分支 / worktree | `agent/codex/TASK-005-minimal-bootstrap` / `G:/CODEX/New Manga.worktrees/TASK-005-codex` |
| Git common directory | `G:/CODEX/New Manga/.git` |
| OS | Microsoft Windows NT 10.0.26200.0，AMD64 |
| CPU | AMD64 Family 25 Model 97 Stepping 2, AuthenticAMD |
| Python | 3.12.3，`G:/CODEX/New Manga.task-envs/TASK-005-py312/Scripts/python.exe` |
| Qt / PySide6 / pytest | 6.11.2 / 6.11.2 / 9.1.1 |

本文件与 `verify.ps1` 在首次生产/测试提交之后提交，因此上表明确区分两者；首次 `reviewed_head=e914f39` 的作者复跑记录在 Handoff，DeepSeek 独立复跑记录在 Review，不把较早的 `b318bdd` PASS 误引为固定 head 证据。Review 修订后的新固定 head 由对应新 Handoff 记录。

## TDD 记录

| 顺序 | 命令 | 实际结果 |
|---|---|---|
| Architecture RED | `python -m pytest tests/core/test_architecture.py -v` | 退出码 1；真实边界因 `src/domain` 不存在而 1 failed，两个合成违规测试 2 passed |
| Architecture GREEN | 同上 | 退出码 0；3 passed |
| Bootstrap RED 1 | `python -m pytest tests/core/test_bootstrap.py -v` | 退出码 1；`No module named bootstrap`，1 failed |
| Bootstrap GREEN 1 | 同上 | 退出码 0；真实 QML 加载，1 passed |
| Bootstrap RED 2 | 同上 | 退出码 1；有效 QML PASS，缺失 QML 错误返回 0，1 passed / 1 failed |
| Bootstrap GREEN 2 | 同上 | 退出码 0；2 passed |
| Core GREEN | `python -m pytest tests/core -v` | 退出码 0；5 passed，无 warning/error |
| Review R-001 RED | `python -m pytest tests/core/test_architecture.py::test_relative_from_import_reports_forbidden_alias -v` | 退出码 1；期望两个相对 alias 违规，实际扫描结果为空 |
| Review R-001 GREEN | 同上，然后 `python -m pytest tests/core -v` | 退出码 0；目标测试 1 passed，完整 core 6 passed |

以上命令中的 `python` 均为表中 Python 3.12 venv 的绝对解释器路径。

## 作者验证

执行：

```powershell
pwsh -NoProfile -File ./verification/TASK-005/verify.ps1 -BaseCommit d65901b953e6fb26043344ed3d668520847eb295 -ReviewedHead HEAD -PythonExe 'G:/CODEX/New Manga.task-envs/TASK-005-py312/Scripts/python.exe'
```

在 `b318bdd5782681df6ff5398b80f8c597366c5b0b` 上实际退出码为 0：

- PASS：base/head 祖先关系与 12 个已提交 allowed paths；
- PASS：Core/dev 精确锁定，未声明 PySide6 Addons 或重型 AI 依赖；
- PASS：`pip check`，Python 3.12.3，torch/transformers/onnxruntime 均未安装；
- PASS：core pytest 5 passed；
- PASS：真实 `Main.qml` offscreen 加载并退出 0；
- PASS：8 个本地 Markdown 链接、代码围栏和 `git diff --check`。

## 未运行与边界

| 项目 | 结果 | 原因 |
|---|---|---|
| 正常交互式窗口人工操作 | NOT_RUN | 本 Task 只要求自动 smoke；未实现业务 UI |
| PyInstaller 打包 / 安装器 | NOT_RUN | TASK-005 禁止创建打包配置；TASK-004 实验不能代替本 head 证据 |
| 干净 Windows VM / 物理机 | NOT_RUN | 当前不可得，仍是发布前 Gate |
| SQL / Migration / Repository | N/A | 本 Task 明确禁止实现 |
| OCR / Translation / Inpainting 质量 | N/A | 无 Provider 或模型实现 |
| 性能 / 内存 /容量 Benchmark | NOT_RUN | 本 Task 没有获批阈值或产品实现 |

本证据只证明最小工程入口和架构守卫，不代表四个一级页面、业务流程、模型质量、打包或发布就绪。
