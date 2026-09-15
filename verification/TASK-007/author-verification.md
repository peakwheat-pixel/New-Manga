# TASK-007 作者验证记录

- 日期：2026-09-15（Asia/Shanghai）
- 作者：ZCode；被测 commit：`6ea4dd9241c0a24f60964b570cb768bb48dfa0f3`
- 环境：Windows 11 专业版 Build 26200 x64；Python 3.12.3（`G:/CODEX/New Manga.task-envs/TASK-005-py312` 任务环境，pytest 9.1.1）；本 Task 未新增任何依赖（decode 验证经端口注入，测试适配器用任务环境已有的 PySide6 QImage；生产 use case 零第三方导入）

## 实际执行命令与结果

| # | 命令（工作目录 = TASK-007 worktree 根） | 退出码 | 结果 |
|---|---|---|---|
| 1 | `python -m pytest tests/library -v`（任务计划命令；`G:/CODEX/New Manga.task-envs/TASK-005-py312/Scripts/python.exe`） | 0 | **25 passed**（AC-LIB/CH/IMPORT/PAGE 13 项 AC 对应用例） |
| 2 | `PYTHONPATH=src python -m pytest tests`（全量回归：core 守卫 + storage + library） | 0 | **62 passed**（core 6 + storage 31 + library 25） |
| 3 | `git diff --check 6b123fe <head> --` | 0 | PASS |
| 4 | `git status --short` 变更范围核对 | — | 仅 `src/domain/books/**`、`src/domain/pages/**`、`src/application/**`、`tests/library/**`（允许路径）；`src/infrastructure`、`src/ports`、`src/bootstrap`、`src/ui`、`tests/core`、`tests/storage`、依赖清单零触碰 |
| 5 | `grep -rn "import sqlite3\|PySide6" src/domain/ src/application/` | — | 仅 docstring 文字命中，无实际导入 |

## 开发过程中发现并修正的测试问题（供 Review 参考）

1. QML/QImage 对同尺寸纯色图生成**字节确定**的 PNG → 批量导入测试未区分内容时全部命中 hash 去重被 skip——测试数据改为不同尺寸。
2. `tests/library` 无包结构，`from .conftest import` 不可用——工厂/fakes 移入同目录 `helpers.py`（pytest 将测试目录插入 sys.path，`import helpers` 可用）。
3. 其余为断言对象/提供顺序笔误，逐一修正后全绿。

## NOT_RUN / N/A

| 项 | 状态 | 理由 |
|---|---|---|
| SQLite BookRepository 持久化与 schema 扩展 | NOT_RUN（范围外） | 允许路径不含 infrastructure/ports；Repository 契约在 application 侧定义并以 fake 驱动（含模拟重启）。SQLite 落地需 Codex 协调 TASK-006 边界后授权 |
| 生产 ImageDecoder 适配器装配 | NOT_RUN（范围外） | 端口已定义；Qt 适配器位于测试（真实解码已验证），生产装配属 bootstrap 切片 |
| 书架 UI / 搜索 / 回收站（D04 §4.1） | N/A | 本 Task 禁止 QML；UI 属 TASK-012+ |
| ReadingProgress / 最近阅读摘要（AC-LIB-004，非本 Task 主责 AC） | N/A | 属阅读器切片（TASK-015 域）；Book.last_opened_at 字段已就位 |
| PDF/MOBI/网页导入 | N/A | TASK-023 |
| 性能 / 大书架容量 | N/A | 无本 Task AC；D07 §11 容量测试属 Benchmark 阶段 |
| 多选交互（AC-PAGE-002）/Page 状态枚举 UI（AC-PAGE-003，非主责 AC） | N/A | UI 交互属 TASK-012+；Page 字段（locked/review_state/overall_status）已建模 |
