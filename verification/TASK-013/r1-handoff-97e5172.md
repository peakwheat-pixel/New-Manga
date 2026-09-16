# R-1 生产 Workbench 装配切片 Handoff（修订）

## 固定信息

- 工作路径：`G:/CODEX/New Manga`
- Task：R-1 生产 Workbench 装配切片
- Owner：Codex
- Reviewer：DeepSeek Harness
- base_commit：`7c889cff531ef412d7774263e85f1d43e3c2ed7a`
- 生产 Pipeline seam 依赖：`integration_commit=49c72fdf4d347be70636770c366c146650888ef4`
- implementation delivery head：`97e5172c7505d16045f4e76ea2ae3ac367234547`
- 前一轮 Review candidate：`74c33a87d8a8182f653cc24f26533b02ddc6777d`，因 R-001/R-002 P1 changes requested；本修订不沿用该 reviewed head
- 本文件为实现修订 Handoff；`reviewed_head` 由 DeepSeek Harness 独立复审后固定，禁止预填

## 修订内容

- `src/bootstrap/app.py` 将 `navigation.workbenchContextChanged` 绑定到真实的 `LibraryService.get_chapter/get_book` 查询，再调用 `WorkbenchViewModel.setContext`；书架进入翻译后不再停留在空态。
- 增加仅面向 Viewer 原图的 `_ManagedPageCatalog`：Page 仍来自 `SqliteLibraryRepository`，`managed_original_ref` 通过 `ManagedFileStorage.absolute_path` 解析，校验最终路径位于 Managed Copy 根目录且文件存在后才返回 `file:` URL；不读取源文件，不暴露路径越界。
- `WorkbenchViewModel` 继续使用已集成的生产 Pipeline seam、真实 SQLite Region repository 和 `RegionEditingService` 人工译文写入。
- `tests/core/test_bootstrap.py` 增加导航上下文同步与 Managed Copy 原图 URL 回归测试，并保留生产 adapter 类型断言。

本修订仅修改：

- `src/bootstrap/app.py`
- `tests/core/test_bootstrap.py`
- 本 Handoff/验证元数据

未修改 QML、Schema/migration、共享 Protocol、依赖清单、AGENTS、`src/domain/**`、TASK-012/TASK-013 已审 UI 实现或冻结 Task。

## 验收对照

- [x] 生产入口构造真实 SQLite Page/Region/人工译文依赖。
- [x] 生产 Pipeline 使用真实 `SqliteTargetCatalog`、`SqlitePipelineStore`、`SqliteSnapshotProvider`、`ProductionStepExecutor`，没有 InMemory/Deterministic 默认绑定。
- [x] 通过 `setContextProperty("workbenchViewModel", ...)` 注入。
- [x] 书架→工作台事件经真实 Chapter→Book 查询同步上下文；未硬编码 book id。
- [x] 原图 URL 仅来自 Managed Copy，且解析结果受 Managed Copy 根目录约束。
- [x] R-03 CLOSED：固定 `126bab5` 已有 `WorkbenchView.qml` 的 `stepPage` 纯转发与 ViewModel 边界计算；本任务未改 UI，现有 `tests/workbench/test_workbench_viewmodel.py::test_step_page_is_viewmodel_owned_and_clamped` 通过。
- [ ] DeepSeek Harness 独立复审：待执行。
- [ ] Codex §6.6 集成及 `integration_commit`：待 Review approved 后执行。

## Windows 验证

环境：Windows `win32`；Python 3.12.3；PySide6 6.11.2；解释器 `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`；默认 Windows Qt，未设置 `QT_QPA_PLATFORM=offscreen`。

| 命令 | passed | skipped | 退出码 / skip 原因 |
|---|---:|---:|---|
| `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m bootstrap.app --smoke-test`（`PYTHONPATH=src`） | N/A | N/A | 0；默认 Windows Qt 入口 smoke 成功 |
| `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests/core/test_bootstrap.py -v` | 11 | 0 | 0 |
| `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests/workbench -v` | 51 | 0 | 0 |
| `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests -q -rs` | 466 | 6 | 0；6 项均为 `openssl unavailable`：`tests/network/test_connection_tester.py:106`、`tests/network/test_transport_tls.py:39/47/62/69/83` |

## 接收动作

1. DeepSeek Harness 只读审查 `7c889cff531ef412d7774263e85f1d43e3c2ed7a..97e5172c7505d16045f4e76ea2ae3ac367234547`，固定新的 `reviewed_head` 并记录 findings。
2. 若 approved，Codex 按 §6.6 保留实现与 Review 的串行集成提交，填写新的 `integration_commit`，再运行同四组验证。
