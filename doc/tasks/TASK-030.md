---
id: TASK-030
title: Main.qml/bootstrap 最小生产装配
kind: implementation
status: blocked
approval: approved
decision: approved_with_dependency_block
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
depends_on: [TASK-005, TASK-007, TASK-012, TASK-029]
base_commit: 78987c8fe5df5650bf7f674d6a9b79afbc48a5ab
branch: null
worktree: null
integration_commit: null
blocked_from: proposed
---

# TASK-030：Main.qml/bootstrap 最小生产装配

这是 TASK-012 范围变更请求的独立最小切片记录。范围已批准独立追踪，但当前不释放、不认领、不实施；冻结的 TASK-013、TASK-015 及其他 Task 不受影响。

## 裁决与依赖核实

2026-09-16，Codex 按 TASK-012 Review 建议核对 `base_commit=78987c8`：

- SQLite `open_database`、`MigrationRunner`、`SqliteLibraryRepository` 已在主线存在，可作为后续装配的持久化依赖。
- `src/application/importing/images/ports.py` 仅定义 `ImageDecoder` 与 `ManagedCopyStore` Protocol。
- Qt `QImage` 解码实现仅在 `tests/library/helpers.py` 的测试适配器；主线 `src/infrastructure` 没有生产 `ImageDecoder.decode` 实现。
- `src/infrastructure/filesystem/managed_storage.py` 提供临时文件/发布接口，但没有 `ManagedCopyStore.store_original` 生产实现。

结论：范围变更**批准建立、当前 BLOCKED**。在生产 Qt 解码与 Managed Copy 适配器通过独立授权切片进入主线之前，不修改入口，不用测试 fake/空实现，不声称应用可用。

## 目标与 Acceptance Criteria

- [ ] `src/ui/qml/Main.qml` 仅负责加载 `shell/AppShell.qml`，不新增业务逻辑。
- [ ] `src/bootstrap/app.py` 在唯一入口构造生产 `NavigationService`、`LibraryService`、`ImportImagesUseCase`、SQLite repository 与已核准的生产 `ImageDecoder`/`ManagedCopyStore`，并通过 `setContextProperty` 注入 `navigationViewModel`、`bookshelfViewModel`；不绕过 Managed Copy 或直接让 QML 访问数据库/文件。
- [ ] Windows 默认 Qt 平台（不设置 `QT_QPA_PLATFORM=offscreen`）从 `python -m bootstrap.app --smoke-test` 启动完整 AppShell，退出码 0；任务环境为 Python 3.12.3 / PySide6 6.11.2。
- [ ] 入口启动后完成 100%/150%/200% DPI 截图初验并将原始截图/步骤保存至 `verification/TASK-030/`；不能用 QML 单元装载替代入口证据。
- [ ] 真实导入探针证明源文件只读、Managed Copy 成功后才写 Page，重启后 SQLite 可读；`tests/ui_shell -v` 为 46 passed，集成全量通过数与 skip 数分列记录。
- [ ] 非作者 DeepSeek Harness 独立 Review 与 Codex 集成复验完成后才能置 `done`。

## 允许修改范围

- `src/ui/qml/Main.qml`
- `src/bootstrap/app.py`
- `tests/core/test_bootstrap.py`
- `doc/tasks/TASK-030.md`
- `doc/handoffs/TASK-030-*.md`
- `verification/TASK-030/**`

生产 ImageDecoder/ManagedCopyStore 适配器不属于本切片；如尚未由其他已授权 Task 提供，必须先另建并批准依赖切片，不能在 TASK-030 越界实现。

## 禁止范围

不得修改 `src/domain/**`、Schema/migration、依赖清单、`src/ui` 其他文件、TASK-012 已审实现、TASK-013/TASK-015 或其他 Task、AGENTS、用户源文件。不得将 tests fake 当作生产装配。

## 测试与阻塞

| 场景 | 计划命令/步骤 | 当前状态 | 解除条件 |
|---|---|---|---|
| 生产入口 smoke | Windows 默认 Qt：`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m bootstrap.app --smoke-test` | **BLOCKED** | 生产 ImageDecoder + ManagedCopyStore 可装配 |
| UI 回归 | `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests/ui_shell -v` | planned；TASK-012 集成基线为 46 passed | 入口变更后复跑 |
| DPI 初验 | 100%/150%/200% Windows 缩放，保存截图 | **BLOCKED** | 入口可真实启动 |
| 真实导入安全链 | 临时库/临时 managed root；源文件 hash/mtime、Managed Copy、Page 持久化前后探针 | **BLOCKED** | 生产两个适配器已就绪 |

解除阻塞前：不创建分支/worktree，不写生产代码；此记录不是 TASK-013/TASK-015 的释放。

## 交付记录

- 当前状态：`BLOCKED`，无 Handoff、无 Review、无 integration_commit。
- 参考：TASK-012 [Review](../reviews/TASK-012-ca5848b.md) 的 scope-change 建议与 [集成验证](../../verification/TASK-012/integration-78987c8.md)。
