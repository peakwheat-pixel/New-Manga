---
id: TASK-012
title: 实现四页导航与书架 UI
kind: implementation
status: in_progress
approval: approved
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
depends_on: [TASK-005, TASK-007]
base_commit: 2cceb1e734c5079870662b7a28da316e46444810
branch: agent/zcode/TASK-012-navigation-library-ui
worktree: G:/CODEX/New Manga.worktrees/TASK-012-zcode
integration_commit: null
---

# TASK-012：实现四页导航与书架 UI

本 Task 已获用户批准释放；2026-09-15 ZCode 在指定 worktree 认领，状态 `ready` → `in_progress`，与 TASK-010（另一 ZCode 会话）并行。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D05 §2～12/43/62；D08 AC-NAV/LIB/CH/WIN；G16。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-NAV-001、AC-NAV-002、AC-NAV-003。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [ ] 启动默认书架且只有四个同级入口；无上下文时显示文档规定的空状态，切换保留上下文。
- [ ] 书架包含Toolbar/虚拟化作品列表/固定BookDetail/ChapterList，接入TASK-007用例和导入入口。
- [ ] 依据D05建立最小视觉基线，标清新设计而非既有截图；关键键盘操作、焦点、空/加载/错误/禁用可用。
- [ ] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。

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
- 以上均为计划，当前结果全部 NOT_RUN；命令中的测试目录需本 Task 实际建立后才能运行。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-005](TASK-005.md)、[TASK-007](TASK-007.md)。依赖必须已经集成 done 才可开始。

阶段性空页面仅作为骨架，不能宣称工作台/Reader/Settings功能完成。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际执行/实验/测试：尚无。
- 最近状态：2026-09-15 用户批准与 TASK-010 并行释放；`ready`，等待 ZCode 在指定 worktree 认领并转 `in_progress`。
- 最近状态：2026-09-15 ZCode 认领（`in_progress`），开始 D05/D08 需求阅读与 TDD 实施。

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
