# R-1 生产 Workbench 装配独立 Review

## 固定对象

- Reviewer：DeepSeek Harness
- Owner：Codex
- base_commit：`7c889cff531ef412d7774263e85f1d43e3c2ed7a`
- reviewed_head：`7f3be549d97d2b9858867f2e7f7f861e0542342e`
- implementation revision：`97e5172c7505d16045f4e76ea2ae3ac367234547`
- decision：**approved**
- 本报告不填写 `integration_commit`。

## 审查结论

- 未发现 P0/P1；此前 `74c33a8` 的 R-001/R-002 已通过修订消失。
- `app.py` 使用真实 `build_production_pipeline(conn)`、`SqliteRegionRepository`、`RegionEditingService`，没有 InMemory/Deterministic 生产默认绑定。
- `assemble_engine()` 通过 `setContextProperty("workbenchViewModel", services.workbench)` 注入。
- `navigation.workbenchContextChanged` 经真实 `LibraryService.get_chapter()` / `get_book()` 查询后调用 `WorkbenchViewModel.setContext()`；无硬编码 book id。
- Page 来自 `SqliteLibraryRepository.list_pages()`；原图 URL 仅由 Managed Copy 根目录校验后的 `file:` URL 提供，不读取源文件。
- R-03 已关闭：固定 `126bab5` 中 `WorkbenchView.qml` 的 `stepPage` 只转发到 ViewModel，边界计算在 ViewModel；本切片未修改 QML。
- `7c889cf..7f3be54` 仅涉及 R-1 实现、测试与 `verification/TASK-013/**`；未改 Schema、Protocol、依赖、Domain、QML 或冻结 Task。
- `git diff --check` 通过，工作树干净。

## 非阻塞事项

- P2：`src/bootstrap/app.py` 模块注释曾写“两个 ViewModel context property”，已在本次集成收口改为“三个”。
- P2：全局状态文档仍处于集成前 `READY/NOT_RUN` 口径，将在 Codex integration_commit 中更新。
- `doc/tasks/TASK-013.md` 的历史 R-1 段落不在本 R-1 明确白名单内，本次不修改；当前 R-1 状态以本目录证据和四份全局元数据为准。

## 验证

环境：Windows `win32`、Python 3.12.3、PySide6 6.11.2、默认 Windows Qt，未设置 `QT_QPA_PLATFORM=offscreen`。

| 检查 | passed | skipped | 结果 |
|---|---:|---:|---|
| 默认 Windows Qt smoke | N/A | N/A | 退出码 0 |
| `tests/core/test_bootstrap.py` | 11 | 0 | 退出码 0 |
| `tests/workbench` | 51 | 0 | 退出码 0 |
| 全量 `tests` | 466 | 6 | 退出码 0；6 项均为 `openssl unavailable` |

真实导航上下文、Managed Copy 原图、人工译文和路径越界负例均通过。

## 决定

`reviewed_head=7f3be549d97d2b9858867f2e7f7f861e0542342e` 可交 Codex 按 §6.6 串行集成。集成时由 Codex 填写新的 `integration_commit`，并按协议复跑验证。
