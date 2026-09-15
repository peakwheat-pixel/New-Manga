# TASK-008 作者验证记录

- 日期：2026-09-15（Asia/Shanghai）
- 作者：ZCode；被测 commit：`1f373ac2240fb5fc6304e447b7d0fd873310aef1`
- 环境：Windows 11 专业版 Build 26200 x64；Python 3.12.3（`G:/CODEX/New Manga.task-envs/TASK-005-py312` 任务环境，pytest 9.1.1）；本 Task 未新增依赖，领域/应用层零第三方导入

## 实际执行命令与结果

| # | 命令（工作目录 = TASK-008 worktree 根） | 退出码 | 结果 |
|---|---|---|---|
| 1 | `python -m pytest tests/editing`（任务计划命令；3.12 任务环境） | 0 | **17 passed**（几何往返/reading_order/合并拆分/四级文本/人工保护/覆盖拒绝/恢复/Pin/Dirty） |
| 2 | `PYTHONPATH=src python -m pytest tests` | 0 | **79 passed**（core 6 + storage 31 + library 25 + editing 17） |
| 3 | `git diff --check f129ae9 <head> --` | 0 | PASS |
| 4 | `git diff --name-only f129ae9 <head>` 越界过滤（tests/library、src/ports、src/infrastructure、src/bootstrap、src/ui、tests/core、tests/storage） | — | 0 命中；11 个变更文件全部在允许路径 |
| 5 | `grep -rn "import sqlite3\|PySide6" src/domain/regions src/application/editing` | — | 无实际导入（仅 docstring 文字） |

## 开发过程中发现并修正的问题（供 Review 参考）

1. **final 解析语义修正**：`resolve_final` 初版只检查 edited 非空，漏掉 D03 §8.3 的「人工**确认**」条件——补 `edited_confirmed` 标志（`save_manual_translation` 不置位、`confirm_final` 置位），空字符串/未确认文本回落 machine，空白且无机器译文回落空（none）。测试 `test_final_resolution_rules` 固化四象限。
2. **confirm_final 空文本**：纯 OCR（无人工译文）确认不应抛错——确认动作作用于 Region 校对状态；有非空 edited 才同时确认 final。
3. **越界自查与回退**：为解决 `tests/editing/helpers.py` 与既有 `tests/library/helpers.py` 同名模块冲突，初版误改了 tests/library（不在允许路径）；自查发现后回退 library 至 base 原状，仅重命名 editing 侧为 `region_helpers.py`（允许路径内）。最终 diff 对 tests/library 零触碰（复核过滤 0 命中）。

## NOT_RUN / N/A

| 项 | 状态 | 理由 |
|---|---|---|
| SQLite RegionRepository 持久化与 schema 扩展 | NOT_RUN（范围外） | 允许路径不含 infrastructure/ports；契约消费侧定义，fake 驱动含模拟重启；落地需 Codex 协调 TASK-006 边界 |
| StepResultCandidate 落库 | NOT_RUN（承接 TASK-011） | 契约 §8.1/§10 的 Candidate 表依赖 StepRun；本切片冲突以 `GuardedWriteOutcome` 返回，payload 交管道层持久化 |
| Page Lock 消费（page_locked 对自动处理的跳过） | N/A | page_locked 在 TASK-007 Page 实体；Pipeline 对 Lock 的消费属 TASK-011 |
| TextStyle 完整字段与自动字号（AC-STYLE） | N/A（非本 Task 主责） | 保留最小样式快照进 Revision；完整样式属 TASK-014 |
| UI 编辑交互 / autosave 计时器获批 | N/A | 禁止 QML；EditingSession 提供 flush 语义，autosave 策略属 UI 切片 |
| 性能 / Region 数量压力 | N/A | 无本 Task AC |
