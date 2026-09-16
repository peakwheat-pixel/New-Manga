---
id: TASK-012
title: 实现四页导航与书架 UI
kind: implementation
status: done
approval: approved
decision: approved
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
depends_on: [TASK-005, TASK-007]
base_commit: 2cceb1e734c5079870662b7a28da316e46444810
branch: agent/zcode/TASK-012-navigation-library-ui
worktree: G:/CODEX/New Manga.worktrees/TASK-012-zcode
reviewed_head: ca5848b746210564a2503e8c5f59e0a2118e56a1
implementation_merge: b324d4b09c6f755c37c8df75b5a1c566e882ce8f
integration_commit: 78987c8fe5df5650bf7f674d6a9b79afbc48a5ab
review_report_commit: 084db6000f4505f95c6451df8bc5aadefd93f5ff
---

# TASK-012：实现四页导航与书架 UI

本 Task 已完成实现、独立 Review 与 Codex 串行集成（`integration_commit=78987c8`）。Owner 为 ZCode，Reviewer 为 DeepSeek Harness；当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

2026-09-15 实施完成，状态 `in_progress` → `in_review`，delivery head `ca5848b`，已交 DeepSeek Harness 独立 Review（见 [Handoff](../handoffs/TASK-012-ca5848b.md)）。

## 来源与目标

D05 §2～12/43/62；D08 AC-NAV/LIB/CH/WIN；G16。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-NAV-001、AC-NAV-002、AC-NAV-003。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [x] 启动默认书架且只有四个同级入口；无上下文时显示文档规定的空状态，切换保留上下文。（python 服务层 + QML 装载双层测试）
- [x] 书架包含Toolbar/虚拟化作品列表/固定BookDetail/ChapterList，接入TASK-007用例和导入入口。
- [x] 依据D05建立最小视觉基线，标清新设计而非既有截图（[ui-baseline](../ui-baseline.md)）；空/禁用态已验证；键盘焦点全量矩阵 NOT_RUN，归 TASK-022。
- [x] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后完成。（`integration_commit=78987c8`）

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。ready 前由 Codex与已冻结实际结构核对并收紧；不能自行扩展到整个 src/tests。

- src/ui/qml/shell/**
- src/ui/qml/bookshelf/**
- src/ui/qml/common/**
- src/ui/qml/workbench/WorkbenchView.qml
- src/ui/qml/reader/ReaderView.qml
- src/ui/qml/settings/SettingsView.qml
- src/ui/viewmodels/navigation/**
- src/ui/viewmodels/bookshelf/**
- src/ui/viewmodels/__init__.py
- src/ui/models/library/**
- src/application/navigation/**
- tests/ui_shell/**
- doc/ui-baseline.md
- doc/tasks/TASK-012.md
- doc/handoffs/TASK-012-*.md
- verification/TASK-012/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 计划：python -m pytest tests/ui_shell；导航、CRUD/导入绑定、Book+Chapter跳转、切换后上下文。
- 100%/150%/200%DPI初验并保存截图；完整多屏矩阵在TASK-022/026。
- 实际结果（2026-09-15 固定 reviewed head）：`pytest tests/ui_shell` 46 passed、`pytest tests` 290 passed, 6 skipped（exit 0；skip 均为 `openssl unavailable`），见 [author-verification](../../verification/TASK-012/author-verification.md)；集成主线复验为 46 passed、368 passed, 6 skipped，见 [integration verification](../../verification/TASK-012/integration-78987c8.md)。
- 100%/150%/200% DPI 截图初验仍 `NOT_RUN (BLOCKED)`：入口装配已登记为独立 TASK-030，但该切片依赖的生产 Qt 解码与 Managed Copy 实现尚未在主线就绪；完整多屏矩阵在 TASK-022/026。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-005](TASK-005.md)、[TASK-007](TASK-007.md)。依赖必须已经集成 done 才可开始。

阶段性空页面仅作为骨架，不能宣称工作台/Reader/Settings功能完成。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：[TASK-012-ca5848b](../handoffs/TASK-012-ca5848b.md)（delivery/reviewed head `ca5848b`，已集成）。
- Review：[TASK-012-ca5848b](../reviews/TASK-012-ca5848b.md)，`report_commit=084db60`，decision=`approved`。
- 实际执行/实验/测试：[author-verification.md](../../verification/TASK-012/author-verification.md) —— 固定 head 全仓 `290 passed, 6 skipped`、`tests/ui_shell` 46 passed；集成复验见 [integration-78987c8](../../verification/TASK-012/integration-78987c8.md)。
- 最近状态：2026-09-15 用户批准与 TASK-010 并行释放；`ready`，等待 ZCode 在指定 worktree 认领并转 `in_progress`。
- 最近状态：2026-09-15 ZCode 认领（`in_progress`），开始 D05/D08 需求阅读与 TDD 实施。
- 最近状态：2026-09-15 实施完成置 `in_review`（01f5bdb 认领 → c9b3fac 计划+scope-change → cf0df63/17a4a48 TDD → 967dbc0 QML+装载测试 → ca5848b 基线+证据）：四页常驻导航（仅切 visible）、书架 Toolbar/Grid/Card/DetailPanel/ChapterList/新建Dialog/导入入口、三骨架页 §62 空状态、EmptyState；`Main.qml`/`bootstrap` 装配 scope-change request 待 Codex 裁决，DPI 截图初验因此 BLOCKED（NOT_RUN），键盘全量归 TASK-022。
- 最近状态：2026-09-16 Codex 以 `b324d4b` 合并作者交付、以 `78987c8` 合并 approved Review；四条 AC 勾选，R-001/R-002 closed；TASK-030 独立装配切片已建立但因生产 Qt 解码/Managed Copy 依赖缺失保持 `BLOCKED`，未释放 TASK-013/TASK-015 等冻结任务。

## 实施计划（in_progress，ZCode）

边界结论（对照 base=`2cceb1e` 实际结构核对）：

- 现有 UI 仅有 TASK-005 的 `src/ui/qml/Main.qml`（空 ApplicationWindow）与 `src/bootstrap/app.py`（加载 Main.qml）。两者均**不在白名单**。
- 装配方案：本切片交付完整 `shell/AppShell.qml`（含四页导航与书架），通过上下文属性消费 `navigationViewModel`/`bookshelfViewModel`；`Main.qml` 与 bootstrap 装配保持原状。
- **范围变更请求（待 Codex 裁决，本切片不实施）**：应用真正展示新 Shell 需要两处白名单外改动——`src/ui/qml/Main.qml` 改为加载 `shell/AppShell.qml`（约 3 行）、`src/bootstrap/app.py` 构造服务与 ViewModel 并 `setContextProperty`。已按协议暂停越界部分，其余全部在白名单内完成；AppShell 可在测试中独立加载验证（tests/ui_shell 注入真实 ViewModel）。
- 架构守卫：`src/ui/**` 不 import `infrastructure`（tests/core 守卫已覆盖）；QML 不写业务逻辑，全部经 ViewModel；ViewModel 依赖 application 层用例（LibraryService、ImportImagesUseCase、NavigationService），不依赖 sqlite/文件系统。

模块与 TDD 顺序：

1. `src/application/navigation/service.py`：`NavigationService`——四页枚举（bookshelf/workbench/reader/settings）、默认 bookshelf（AC-NAV-001）、拒绝第五 Route（AC-NAV-002）、切换保留 Book/Chapter/Page 上下文（AC-NAV-003）、`enter_workbench(book,chapter)` / `enter_reader(book,chapter,page)` 携带上下文（D05 §67）。
2. `src/ui/viewmodels/navigation/`：`NavigationViewModel(QObject)`——currentPage/pages 属性、navigate 槽、workbench/reader 上下文属性与信号。
3. `src/ui/models/library/`：`BookListModel` / `ChapterListModel`（QAbstractListModel，角色绑定 D05 §7.1/§9 字段；阅读进度 TASK-007 无字段，诚实显示“—”，不虚构）。
4. `src/ui/viewmodels/bookshelf/`：`BookshelfViewModel(QObject)`——绑定 LibraryService + importer（ImportImagesUseCase 的调用方 seam）+ NavigationService；搜索/收藏/归档筛选、排序、Grid/List；CRUD 槽（新建/删除/收藏/归档/新建章节/删除章节）；导入入口（调用 importer 并暴露报告摘要）；空状态（D05 §62）；选中同步 Detail。
5. QML（白名单内，全部薄绑定）：`shell/AppShell.qml`、`shell/PrimaryNavigationRail.qml`（固定四入口+worktail 徽标占位）；`bookshelf/BookshelfView|BookshelfToolbar|BookGrid|BookCard|BookDetailPanel|ChapterList.qml`；`common/EmptyState.qml`；`workbench/WorkbenchView.qml`、`reader/ReaderView.qml`（§62 空状态骨架）、`settings/SettingsView.qml`（§43.1 固定分类列表+占位面板）。键盘 Tab/方向键焦点与 disabled 态随绑定给出。
6. `tests/ui_shell/`：navigation service/VM、bookshelf VM（内存 repo fake + stub importer）、列表模型角色、QML AppShell 装载测试（QQmlComponent + 注入 VM）。
7. `doc/ui-baseline.md`：最小视觉基线（D05 §3.1/§7 布局、颜色/字体/间距/状态），明确标注“新设计基线，非既有截图”。

## 范围变更裁决：TASK-030

本 Task 不修改 `Main.qml` 或 `bootstrap/app.py`。为使当前 Shell 具备真实入口，批准建立独立最小切片 [TASK-030](TASK-030.md)，固定 `base_commit=78987c8`、Owner=`ZCode`、Reviewer=`DeepSeek Harness`，只允许 `src/ui/qml/Main.qml`、`src/bootstrap/app.py` 及该 Task 自有验证/交接文档。

主线依赖核实（`78987c8`）：SQLite `open_database`/`MigrationRunner`/`SqliteLibraryRepository` 已存在；但 `ImageDecoder` 与 `ManagedCopyStore` 只有 `src/application/importing/images/ports.py` Protocol，Qt 解码实现仅在 `tests/library/helpers.py`，`ManagedFileStorage` 没有 `store_original`。因此 TASK-030 的实现门禁为 `BLOCKED`，须先有已授权的生产适配器；不得在入口装配中使用测试 fake、空实现或绕过 Managed Copy。

### Review findings disposition

| finding | disposition |
|---|---|
| R-001 全量计数口径 | **closed**：固定 reviewed head 更正为 `290 passed, 6 skipped`，并列出 `openssl unavailable`；集成主线为 `368 passed, 6 skipped`。 |
| R-002 授权口径/白名单写法 | **closed**：共享状态文档元数据权限已写入协作协议；`src/ui/viewmodels/__init__.py` 已补入本 Task 白名单。 |
