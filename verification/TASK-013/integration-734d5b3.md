# TASK-013 R-1 生产 Workbench 装配集成复验

## 固定对象

- 工作路径：`G:/CODEX/New Manga`
- Task：R-1 生产 Workbench 装配切片
- Owner：Codex
- Reviewer：DeepSeek Harness
- base_commit：`7c889cff531ef412d7774263e85f1d43e3c2ed7a`
- 生产 Pipeline seam 依赖：`integration_commit=49c72fdf4d347be70636770c366c146650888ef4`
- reviewed_head：`7f3be549d97d2b9858867f2e7f7f861e0542342e`
- Review：[`r1-review-7f3be54.md`](r1-review-7f3be54.md)，decision=`approved`
- integration_commit：`734d5b39a3185bf612276dada6b089b55c9e574d`
- integration parent：实现交付 `7f3be549d97d2b9858867f2e7f7f861e0542342e`；独立 Review `r1-review-7f3be54.md` 已随集成提交纳入
- 被排除对象：实现交付前的首轮候选 `74c33a8`；TASK-013 审计分支后续未授权提交；无关分支；TASK-015 及其他冻结 Task

## 集成范围与裁决

- [x] `src/bootstrap/app.py` 构造真实生产 `WorkbenchViewModel`。
- [x] `PipelineService` 使用 `build_production_pipeline(conn)` 的真实 SQLite catalog/store/snapshot/executor；生产入口未绑定 InMemory/Deterministic 实现。
- [x] Page 来自真实 SQLite `SqliteLibraryRepository`；Region 与人工译文来自真实 SQLite `SqliteRegionRepository` / `RegionEditingService`。
- [x] 书架进入工作台时，经 `NavigationViewModel` 的上下文事件执行真实 `Chapter -> Book` 查询，并使用 `book_id_for_chapter` 语义；未硬编码 book id。
- [x] `assemble_engine()` 通过 `setContextProperty("workbenchViewModel", ...)` 注入。
- [x] Viewer 原图仅解析 Managed Copy 根目录内的 `managed_original_ref`；不读取源文件，不绕过源文件只读路径。
- [x] R-001/R-002：首轮 Review 指出的导航上下文同步与 Managed Copy 原图 URL 已修复并获复审批准。
- [x] R-03：固定 `126bab5` 的 `WorkbenchView.qml` 仅转发 `stepPage`，边界计算由 ViewModel 持有；R-1 未修改 QML。
- [x] 未修改 Schema/migration、共享 Protocol、依赖清单、`src/domain/**`、TASK-012/TASK-013 已审实现、冻结 Task 或 AGENTS；未 push、未合并无关分支。

## 验收证据

环境：Windows `win32`；Python 3.12.3；PySide6 6.11.2；解释器 `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`；默认 Windows Qt，未设置 `QT_QPA_PLATFORM=offscreen`。

| 命令 | passed | skipped | 退出码 / skip 原因 |
|---|---:|---:|---|
| `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m bootstrap.app --smoke-test`（`PYTHONPATH=src`） | N/A | N/A | 0；入口 smoke 成功 |
| `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests/core/test_bootstrap.py -v` | 11 | 0 | 0 |
| `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests/workbench -v` | 51 | 0 | 0 |
| `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests -q -rs` | 466 | 6 | 0；`tests/network/test_connection_tester.py:106` 与 `tests/network/test_transport_tls.py:39/47/62/69/83` 均因 `openssl unavailable` skip |

`passed` 与 `skipped` 已分列。所有未执行项：无；不适用项仅为 smoke（非 pytest 用例计数），记为 `N/A`。全量命令未使用 offscreen，退出码为 0。

## 结论

R-1 已按 §6.6 完成独立 Review 后的串行集成，`integration_commit` 由 Codex 填写为 `734d5b39a3185bf612276dada6b089b55c9e574d`。R-03 已关闭，真实 SQLite / Chapter→Book / Managed Copy / context-property 验收门槛均通过。TASK-015 及其他冻结 Task 继续保持冻结。
