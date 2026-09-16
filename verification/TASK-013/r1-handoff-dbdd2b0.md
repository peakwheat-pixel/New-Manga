# R-1 生产 Workbench 装配切片 Handoff

## 固定信息

- 工作路径：`G:/CODEX/New Manga`
- Task：R-1 生产 Workbench 装配切片
- Owner：Codex
- Reviewer：DeepSeek Harness
- base_commit：`7c889cf`
- 生产 Pipeline seam 依赖：`integration_commit=49c72fdf`
- delivery_head：`dbdd2b0693d531adaf4fd2a7b1864fd639e81fb2`
- reviewed_head：待 DeepSeek Harness 独立 Review 固定，禁止预填

## 变更

本切片在生产入口增加真实 Workbench 依赖装配：

- `src/bootstrap/app.py` 复用现有 SQLite 连接、真实 `SqliteLibraryRepository` 和 Managed Copy 导入栈。
- 新建 `RegionEditingService(SqliteRegionRepository(conn))`，同时作为 Workbench 的 Region catalog 与人工译文写入服务。
- 通过已集成的 `build_production_pipeline(conn)` 构造真实 `SqliteTargetCatalog`、`SqlitePipelineStore`、`SqliteSnapshotProvider`、`ProductionStepExecutor`，不使用 InMemory/Deterministic 生产默认值。
- 构造 `WorkbenchViewModel`，注入真实 page/region/editor/navigation/pipeline 依赖。
- `assemble_engine` 通过 `setContextProperty("workbenchViewModel", ...)` 注入。
- `tests/core/test_bootstrap.py` 增加真实 SQLite Book→Chapter→Managed Copy Page→Region→人工译文→QML context property 验证，并断言四个生产 Pipeline adapter 类型。

修改路径仅为：

- `src/bootstrap/app.py`
- `tests/core/test_bootstrap.py`

## 验收对照

- [x] 真实 SQLite Page catalog：`SqliteLibraryRepository.list_pages(chapter_id)`。
- [x] 真实 SQLite Region catalog 与人工译文服务：`RegionEditingService(SqliteRegionRepository(conn))`。
- [x] 真实 Pipeline seam：生产 catalog/store/snapshot/executor 均由 `build_production_pipeline` 构造。
- [x] `setContextProperty("workbenchViewModel", ...)` 已在入口调用。
- [x] Chapter→Book 绑定沿用 `book_id_for_chapter` 的真实 `repository.get_chapter` 查询；未硬编码 book id。
- [x] 导入验证继续经 Qt 解码与 Managed Copy，源文件只读；本切片未绕过该路径。
- [x] R-03 CLOSED：固定 `base_commit=126bab5` 中 `src/ui/qml/workbench/WorkbenchView.qml` 的 `stepPage` 已仅转发 `workbench.vm.stepPage(delta)`；边界计算由 `WorkbenchViewModel.stepPage` 承担。`tests/workbench/test_workbench_viewmodel.py::test_step_page_is_viewmodel_owned_and_clamped` 通过。本切片未修改 UI。

## Windows 验证

环境：Windows `win32`；Python 3.12.3；PySide6 6.11.2；解释器 `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`；默认 Windows Qt，未设置 `QT_QPA_PLATFORM=offscreen`。

| 命令 | passed | skipped | 退出码 / skip 原因 |
|---|---:|---:|---|
| `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m bootstrap.app --smoke-test`（`PYTHONPATH=src`） | N/A | N/A | 0；入口 smoke 成功，无测试 skip |
| `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests/core/test_bootstrap.py -v` | 9 | 0 | 0 |
| `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests/workbench -v` | 51 | 0 | 0 |
| `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests -q -rs` | 464 | 6 | 0；6 项均为 `openssl unavailable`：`tests/network/test_connection_tester.py:106`、`tests/network/test_transport_tls.py:39/47/62/69/83` |

## Review 与集成状态

- 当前 delivery head 可交 DeepSeek Harness 独立 Review；Review 必须固定 `base=7c889cf`、`reviewed_head=dbdd2b0`，不得把本 Handoff 预填为 Review 结果。
- Review 通过后由 Codex 按 §6.6 串行集成并填写新的 `integration_commit`；本文件当前不填写该值。
- 真实 provider handler 不在本切片范围；无 handler 时生产执行器按既有 seam 返回 `PROVIDER_UNAVAILABLE`，不得替换为确定性假输出。
- 未修改 Schema/migration、共享 Protocol、依赖清单、AGENTS、QML、`src/domain/**`、TASK-012/TASK-013 已审实现或冻结 Task；未 push、未合并无关分支。
