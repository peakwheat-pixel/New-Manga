# TASK-030 作者验证（Author Verification）

- 作者：ZCode（实现）· Reviewer：DeepSeek Harness（独立，非作者）
- base_commit：`087da45590c84227e9695eb829669e9cee805ef2`
- 分支：`agent/zcode/TASK-030-main-bootstrap-assembly`
- worktree：`G:/CODEX/New Manga.worktrees/TASK-030-zcode`
- reviewed head：见 [Handoff](../../doc/handoffs/)（实现提交以 Handoff 固定的 delivery head 为准）

## 1. 环境

| 项 | 值 |
|---|---|
| OS | Windows 11（win32 10.0.26200 x64） |
| Python | 3.12.3（隔离环境 `G:/CODEX/New Manga.task-envs/TASK-012-py312`） |
| PySide6 | 6.11.2 |
| Qt 平台 | **Windows 默认平台**（所有验证均未设置 `QT_QPA_PLATFORM=offscreen`） |
| 显示器 | 虚拟显示器 "Mi TV" 1920×1080（DPR 1.0；150/200% 经 `QT_SCALE_FACTOR` 注入） |

## 2. 命令与结果（passed / skipped 分列）

全部在 worktree 根目录、Windows 默认 Qt 平台执行；输出原文保存于本目录。

| # | 命令 | 退出码 | passed | skipped | 证据 |
|---|---|---|---|---|---|
| 1 | `PYTHONPATH=src …python.exe -m bootstrap.app --smoke-test` | 0 | —（入口进程，无测试项） | — | [smoke-test.txt](smoke-test.txt) |
| 2 | `…python.exe -m pytest tests/ui_shell -v` | 0 | **46 passed** | **0 skipped** | [pytest-ui_shell.txt](pytest-ui_shell.txt) |
| 3 | `…python.exe -m pytest tests/core/test_bootstrap.py -v` | 0 | **7 passed** | **0 skipped** | [pytest-bootstrap.txt](pytest-bootstrap.txt) |
| 4 | `…python.exe -m pytest tests -q -rs` | 0 | **387 passed** | **0 skipped** | [pytest-full.txt](pytest-full.txt) |

skip 原因：无 skip 发生（`-rs` 无输出）；TASK-012 基线 46 passed 全数保持。

## 3. DPI 100%/150%/200% 截图初验（入口真实启动）

经 `python -m bootstrap.app --screenshot <png> --scale <s>` 从唯一入口启动完整生产栈
（临时数据根），真实渲染 AppShell 后抓帧，非 QML 单元装载替代：

| 档位 | 命令 | 退出码 | 证据 |
|---|---|---|---|
| 100% | `--screenshot verification/TASK-030/dpi-10pct.png --scale 1.0` | 0 | [dpi-10pct.png](dpi-10pct.png)（1280×800） |
| 150% | `--screenshot verification/TASK-030/dpi-15pct.png --scale 1.5` | 0 | [dpi-15pct.png](dpi-15pct.png)（1920×1200，文字/控件等比放大） |
| 200% | `--screenshot verification/TASK-030/dpi-20pct.png --scale 2.0` | 0 | [dpi-20pct.png](dpi-20pct.png)（2560×1600） |

三张截图均可见：左侧导航 Rail 四项（书架选中）、Toolbar（新建作品/导入/搜索/收藏/归档/排序/列表）、
D05 §62 空状态「还没有作品」与右侧「未选择作品」面板，布局在 150%/200% 下无错位、无裁切。

实现注记：抓帧用 `QQuickWindow.grabWindow()`（shiboken downcast）而非 `QScreen.grabWindow`——
后者在本机虚拟显示器上返回空帧。PySide6 wrapper 类型取决于包装发生时已导入的 Python 类型，
因此 `bootstrap/app.py` 顶层显式导入 `QQuickWindow`，否则 rootObjects()[0] 退化为 QWindow。

## 4. 真实导入安全链（生产栈探针）

由 `tests/core/test_bootstrap.py::test_import_safety_chain` 在真实装配上证明
（`assemble_services`：真实 SQLite + migration + `QtImageDecoder` + `ManagedCopyStoreAdapter` +
`SqliteLibraryRepository` sink，无任何 fake）：

1. 建 Book/Chapter → 导入临时目录中的真实 PNG 文件（QImage 生成）；
2. **源文件只读**：导入前后 mtime_ns + sha256 不变（AC-IMPORT-002 / D07 §37）；
3. **Managed Copy 先于 Page**：managed 文件逐字节等于源字节，路径为
   `books/{真实book_id}/chapters/{真实chapter_id}/original/…`——book id 来自
   `book_id_for_chapter` 绑定的真实 `SqliteLibraryRepository.get_chapter` 查询，零硬编码；
4. **重启可读**：全新连接重开 SQLite，`list_pages` 取回同一 page_id / source_hash /
   managed_original_ref / 尺寸（7×5）。

反证由 `test_import_unknown_chapter_fails_copy_and_writes_no_page` 证明：未知 chapter 使
copy 失败（`book_id_for_chapter` 抛错），无 Page 落库、源文件原样。

## 5. NOT_RUN / 边界（如实记录）

| 项 | 状态 | 说明 |
|---|---|---|
| 真实 `%LOCALAPPDATA%` 数据根启动 | NOT_RUN | 入口验证一律走 `--data-root`/临时根，避免污染真实用户数据；默认路径逻辑由代码审查与 `default_data_root()` 单元语义覆盖 |
| 多显示器矩阵 / 拖拽双屏 | NOT_RUN | 归 TASK-022/026 |
| 键盘焦点全量矩阵 | NOT_RUN | 归 TASK-022 |
| 文件对话框原生交互端到端 | NOT_RUN | 原生对话框不可无头驱动；QML→VM→用例调用契约由 tests/ui_shell 覆盖 |
| 工作台/阅读器/设置真实内容 | N/A | TASK-013/015/022 交付，本切片仅装配 |
