---
id: TASK-030
title: Main.qml/bootstrap 最小生产装配
kind: implementation
status: done
approval: approved
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
depends_on: [TASK-005, TASK-007, TASK-012, TASK-029, TASK-031]
base_commit: 087da45590c84227e9695eb829669e9cee805ef2
branch: agent/zcode/TASK-030-main-bootstrap-assembly
worktree: G:/CODEX/New Manga.worktrees/TASK-030-zcode
reviewed_head: c3f189396d9efdceb0e3e42ba7db62b25d77853a
implementation_merge: a58ff84
integration_commit: fef9dd3
review_report_commit: dba26372dc63d4d23acfd809e7b646106693c230
blocked_from: null
---

# TASK-030：Main.qml/bootstrap 最小生产装配

这是 TASK-012 范围变更请求的独立最小切片记录。本 Task 已完成实现、非作者独立 Review 与 Codex 串行集成；冻结的 TASK-013、TASK-015 及其他 Task 不受影响。

## 裁决与依赖核实

2026-09-16，Codex 按 TASK-012 Review 建议核对原始集成基线 `base_commit=78987c8`，并在 TASK-031 集成后的 `base_commit=087da45590c84227e9695eb829669e9cee805ef2` 复核装配依赖：

- SQLite `open_database`、`MigrationRunner`、`SqliteLibraryRepository` 已在主线存在，可作为后续装配的持久化依赖。
- TASK-031 已在 `integration_commit=e9d5185259ffa175b64d67d5ac00befadc6db643` 集成 `src/infrastructure/importing.py` 的生产 Qt `QImage` 解码与 Managed Copy 适配器，并以 `tests/library/test_production_adapters.py` 覆盖成功、失败清理、源文件只读和 D03 original 路径。
- `src/application/importing/images/ports.py` 仍是装配所依赖的 `ImageDecoder` 与 `ManagedCopyStore` Protocol；入口只消费该 seam，不重复实现适配器。
- SQLite `open_database`、`MigrationRunner`、`SqliteLibraryRepository` 与真实 Chapter→Book 查询已在主线可用；入口必须通过 `book_id_for_chapter` 绑定真实查询，不得硬编码 book id。

结论：范围变更**批准释放并已完成集成**。TASK-031 的生产 Qt 解码与 Managed Copy 适配器及 SQLite 依赖已就绪；TASK-030 仅负责 `Main.qml`/`bootstrap.app` 最小生产装配，不使用测试 fake/空实现，不绕过 Managed Copy 或真实 Chapter→Book 查询。

## 目标与 Acceptance Criteria

- [x] `src/ui/qml/Main.qml` 仅负责加载 `shell/AppShell.qml`，不新增业务逻辑。（入口窗口挂载，全部行为在 AppShell）
- [x] `src/bootstrap/app.py` 在唯一入口构造生产 `NavigationService`、`LibraryService`、`ImportImagesUseCase`、SQLite repository 与已核准的生产 `ImageDecoder`/`ManagedCopyStore`，并通过 `setContextProperty` 注入 `navigationViewModel`、`bookshelfViewModel`；不绕过 Managed Copy 或直接让 QML 访问数据库/文件。（`assemble_services`/`assemble_engine`；`book_id_for_chapter` 绑定真实 `SqliteLibraryRepository.get_chapter`）
- [x] Windows 默认 Qt 平台（不设置 `QT_QPA_PLATFORM=offscreen`）从 `python -m bootstrap.app --smoke-test` 启动完整 AppShell，退出码 0；任务环境为 Python 3.12.3 / PySide6 6.11.2。
- [x] 入口启动后完成 100%/150%/200% DPI 截图初验并将原始截图/步骤保存至 `verification/TASK-030/`；不能用 QML 单元装载替代入口证据。（100% 1280×800；150% 1920×1061；200% 1924×1062；另补 125% 完整高分辨率 1600×1000）
- [x] 真实导入探针证明源文件只读、Managed Copy 成功后才写 Page，重启后 SQLite 可读；`tests/ui_shell -v` 为 46 passed，集成全量通过数与 skip 数分列记录。（集成：382 passed / 6 skipped；bootstrap 8 passed / 0 skipped；ui_shell 46 passed / 0 skipped，见集成验证）
- [x] 非作者 DeepSeek Harness 独立 Review 与 Codex 集成复验完成后才能置 `done`。（Review `dba2637`；integration `fef9dd3`）

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
| 生产入口 smoke | Windows 默认 Qt：`PYTHONPATH=src G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m bootstrap.app --smoke-test` | executed；exit 0 | 已完成入口装配并复跑 |
| UI 回归 | `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests/ui_shell -v` | executed；46 passed, 0 skipped | 入口变更后复跑通过 |
| DPI 初验 | 100%/150%/200% Windows 缩放，另补 125% 完整高分辨率入口抓帧 | executed；实测尺寸已更正；150%/200% 受 1920×1080 显示器限制 | 记录可见范围结论，不宣称完整窗口无裁切 |
| 真实导入安全链 | 临时库/临时 managed root；源文件 hash/mtime、Managed Copy、Page 持久化前后探针；通过 `book_id_for_chapter` 绑定真实 Chapter→Book 查询 | executed；bootstrap 8 passed, 0 skipped | 真实生产装配测试通过 |

依赖已解除并完成集成；此记录不是 TASK-013/TASK-015 或其他冻结 Task 的释放。

## 交付记录

- 当前状态：`done`；Owner=`ZCode`，Reviewer=`DeepSeek Harness`；`base_commit=087da45590c84227e9695eb829669e9cee805ef2`；`reviewed_head=c3f189396d9efdceb0e3e42ba7db62b25d77853a`；branch=`agent/zcode/TASK-030-main-bootstrap-assembly`；worktree=`G:/CODEX/New Manga.worktrees/TASK-030-zcode`。
- `implementation_merge=a58ff84`；`integration_commit=fef9dd3`；`review_report_commit=dba26372dc63d4d23acfd809e7b646106693c230`。集成复验见 [integration-fef9dd3.md](../../verification/TASK-030/integration-fef9dd3.md)。
- 依赖核验：TASK-031 `integration_commit=e9d5185259ffa175b64d67d5ac00befadc6db643` 已提供生产 Qt 解码/Managed Copy；本 Task 已完成入口装配与集成验证。
- 参考：TASK-012 [Review](../reviews/TASK-012-ca5848b.md) 的 scope-change 建议与 [集成验证](../../verification/TASK-012/integration-78987c8.md)。
- 2026-09-16 ZCode 认领（`ready` → `in_progress`），开始入口装配实施：真实 SQLite/migration、生产 QtImageDecoder + ManagedCopyStoreAdapter（经 `book_id_for_chapter` 真实 Chapter→Book 查询）、Main.qml 挂 AppShell、setContextProperty 注入。
- 2026-09-16 实施完成置 `in_review`：实现提交 `c3f1893`（reviewed_head），Handoff 见 [TASK-030-c3f1893](../handoffs/TASK-030-c3f1893.md)；验证证据 [author-verification.md](../../verification/TASK-030/author-verification.md)——smoke exit 0、ui_shell 46 passed/0 skipped、bootstrap 7 passed/0 skipped、全量 387 passed/0 skipped、DPI 100/150/200% 入口截图、真实导入安全链探针；随后完成 DSH Review 与 Codex 集成收口。

## Review finding disposition

- **R-001 closed**：更正 `author-verification.md` 中 150%=`1920×1061`、200%=`1924×1062`；结论收窄为“可见范围内未观察到控件错位”，明确 1920×1080 显示器限制；补充默认 Windows Qt 下 125% 完整入口抓帧 `dpi-highres-125pct.png`（1600×1000）。
- **R-002 closed**：移除本文件 frontmatter 中预填的 `decision` 字段；Review 结论以独立报告 `dba2637` 为准。
- **R-003 closed**：`assemble_services` 在迁移、仓储、存储或服务装配异常时关闭已打开 SQLite 连接；主函数异常路径同时清理临时根；`test_assemble_services_closes_connection_when_migration_fails` 已通过。

## 两项登记事项

- **裁决①已落地**：数据根默认已登记至 D03 §18.1 与 D07 §33：`%LOCALAPPDATA%/New Manga`，`NEWMANGA_DATA_ROOT`/`--data-root` 可覆盖；设置 UI/迁移仍属 TASK-022。
- **裁决②已落地**：`src/bootstrap/app.py` 顶层 `QQuickWindow` 注释改为“强类型包装 + `_grab_and_quit` native-handle rewrap 第二道保险”，不再声称顶层导入是 `grabWindow()` 的必要条件。
