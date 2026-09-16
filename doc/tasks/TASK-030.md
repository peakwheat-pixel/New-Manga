---
id: TASK-030
title: Main.qml/bootstrap 最小生产装配
kind: implementation
status: ready
approval: approved
decision: approved
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
depends_on: [TASK-005, TASK-007, TASK-012, TASK-029, TASK-031]
base_commit: 087da45590c84227e9695eb829669e9cee805ef2
branch: agent/zcode/TASK-030-main-bootstrap-assembly
worktree: G:/CODEX/New Manga.worktrees/TASK-030-zcode
integration_commit: null
blocked_from: null
---

# TASK-030：Main.qml/bootstrap 最小生产装配

这是 TASK-012 范围变更请求的独立最小切片记录。用户已授权释放本切片；当前状态为 `ready`，等待 ZCode 认领后实施。冻结的 TASK-013、TASK-015 及其他 Task 不受影响。

## 裁决与依赖核实

2026-09-16，Codex 按 TASK-012 Review 建议核对原始集成基线 `base_commit=78987c8`，并在 TASK-031 集成后的 `base_commit=087da45590c84227e9695eb829669e9cee805ef2` 复核装配依赖：

- SQLite `open_database`、`MigrationRunner`、`SqliteLibraryRepository` 已在主线存在，可作为后续装配的持久化依赖。
- TASK-031 已在 `integration_commit=e9d5185259ffa175b64d67d5ac00befadc6db643` 集成 `src/infrastructure/importing.py` 的生产 Qt `QImage` 解码与 Managed Copy 适配器，并以 `tests/library/test_production_adapters.py` 覆盖成功、失败清理、源文件只读和 D03 original 路径。
- `src/application/importing/images/ports.py` 仍是装配所依赖的 `ImageDecoder` 与 `ManagedCopyStore` Protocol；入口只消费该 seam，不重复实现适配器。
- SQLite `open_database`、`MigrationRunner`、`SqliteLibraryRepository` 与真实 Chapter→Book 查询已在主线可用；入口必须通过 `book_id_for_chapter` 绑定真实查询，不得硬编码 book id。

结论：范围变更**批准释放、当前 READY**。TASK-031 的生产 Qt 解码与 Managed Copy 适配器及 SQLite 依赖已就绪；TASK-030 仅负责 `Main.qml`/`bootstrap.app` 最小生产装配，不使用测试 fake/空实现，不绕过 Managed Copy 或真实 Chapter→Book 查询。

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

生产 ImageDecoder/ManagedCopyStore 适配器已由 TASK-031 提供；本切片只消费既有 Protocol 与生产适配器，不重复实现，不扩大到其他 `src/` 路径。

## 禁止范围

不得修改 `src/domain/**`、Schema/migration、依赖清单、`src/ui` 其他文件、TASK-012 已审实现、TASK-013/TASK-015 或其他 Task、AGENTS、用户源文件。不得将 tests fake 当作生产装配。

## 测试与阻塞

| 场景 | 计划命令/步骤 | 当前状态 | 解除条件 |
|---|---|---|---|
| 生产入口 smoke | Windows 默认 Qt：`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m bootstrap.app --smoke-test` | planned | 完成入口装配并复跑 |
| UI 回归 | `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests/ui_shell -v` | planned；TASK-012 集成基线为 46 passed | 入口变更后复跑 |
| DPI 初验 | 100%/150%/200% Windows 缩放，保存截图 | planned | 入口可真实启动 |
| 真实导入安全链 | 临时库/临时 managed root；源文件 hash/mtime、Managed Copy、Page 持久化前后探针；通过 `book_id_for_chapter` 绑定真实 Chapter→Book 查询 | planned | 完成入口装配并复跑 |

当前依赖已解除；已登记专用分支/worktree。Owner 认领后将状态改为 `in_progress`；此记录不是 TASK-013/TASK-015 或其他冻结 Task 的释放。

## 交付记录

- 当前状态：`READY`；Owner=`ZCode`，Reviewer=`DeepSeek Harness`；`base_commit=087da45590c84227e9695eb829669e9cee805ef2`；branch=`agent/zcode/TASK-030-main-bootstrap-assembly`；worktree=`G:/CODEX/New Manga.worktrees/TASK-030-zcode`；尚无 Handoff、Review、`integration_commit`。
- 依赖核验：TASK-031 `integration_commit=e9d5185259ffa175b64d67d5ac00befadc6db643` 已提供生产 Qt 解码/Managed Copy；当前仅等待入口实现、独立 Review 与 Codex 集成验证。
- 参考：TASK-012 [Review](../reviews/TASK-012-ca5848b.md) 的 scope-change 建议与 [集成验证](../../verification/TASK-012/integration-78987c8.md)。
