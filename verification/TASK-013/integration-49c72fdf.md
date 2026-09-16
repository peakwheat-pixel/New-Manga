# TASK-013 生产 Pipeline seam 集成复验

## 固定对象

- base_commit：`126bab54e03849d2684921a5d7fb211f7ad7c23b`
- reviewed_head：`e5b58e7378a9fa4e5737220e51a9000a19a21a4e`
- Review report commit：`8f7c454321266ba65b3c5152dde19a39d5dfd7ad`
- integration_commit：`49c72fdf4d347be70636770c366c146650888ef4`
- integration parents：实现合并 `0bd74831e339eb1ede7f6b2b45b641728d488fcd`；Review 报告合并 `8f7c454321266ba65b3c5152dde19a39d5dfd7ad`
- 被排除对象：审计分支后续 `0eb49ae`，未纳入本次集成

## 范围与裁决

- 生产 seam 已集成：`SqliteTargetCatalog`、`SqlitePipelineStore`、`SqliteSnapshotProvider`、`ProductionStepExecutor`。
- R-01 **CLOSED**：移除 `verification/TASK-013/production-pipeline-seam-design.md` 行尾空白；`git diff --check` 通过。
- R-02 **CLOSED**：在 `doc/tasks/TASK-013.md` 登记本切片实际授权路径、Owner、Reviewer、固定 base/reviewed_head/integration_commit 与验收门槛。
- R-03 **CARRY_FORWARD**：不在本 seam 集成中处理；并入下一个 R-1 接线切片。
- R-1：`READY/NOT_RUN`。生产 seam 已就绪，但本轮不修改 `src/bootstrap/app.py`、QML，也不注入 `WorkbenchViewModel`。
- 约束核验：本轮未使用 InMemory/Deterministic 伪造生产绑定；R-1 仍须通过真实 Chapter→Book 查询、无硬编码 book id、不绕过 Managed Copy 与源文件只读路径。
- 冻结约束：未启动或释放 TASK-015、TASK-030 或其他冻结 Task；未 push、未合并无关分支。

## Windows 验证

环境：Windows `win32`；Python 3.12.3；PySide6 6.11.2；解释器 `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`；默认 Windows Qt，未设置 `QT_QPA_PLATFORM=offscreen`。

| 命令 | 结果 | skipped 与原因 |
|---|---:|---|
| `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests/pipeline -v` | **30 passed** | **0 skipped** |
| `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests/storage -v` | **33 passed** | **0 skipped** |
| `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests/workbench -v` | **51 passed** | **0 skipped** |
| `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests -q -rs` | **463 passed** | **6 skipped**：`tests/network/test_connection_tester.py:106`、`tests/network/test_transport_tls.py:39/47/62/69/83`，原因均为 `openssl unavailable` |

四条命令退出码均为 0。
