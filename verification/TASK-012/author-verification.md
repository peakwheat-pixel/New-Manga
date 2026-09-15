# TASK-012 作者验证（Author Verification）

- 作者：ZCode（实现）· Reviewer：DeepSeek Harness（独立，非作者）
- base_commit：`2cceb1e734c5079870662b7a28da316e46444810`
- reviewed_head：见 [Handoff](../../doc/handoffs/)（本文件所在提交的子提交链，Handoff 中固定）
- 分支：`agent/zcode/TASK-012-navigation-library-ui`
- worktree：`G:/CODEX/New Manga.worktrees/TASK-012-zcode`

## 1. 环境

| 项 | 值 |
|---|---|
| OS | Windows 11（win32 10.0.26200 x64） |
| Python | 3.12.3（隔离环境 `G:/CODEX/New Manga.task-envs/TASK-012-py312`，按 requirements-dev.txt 锁定） |
| PySide6 | 6.11.2 |
| pytest | 9.1.1 |
| 显示平台 | Qt 默认 Windows 平台（QML 需要 font database，offscreen 不可用于 QML/UI 测试；TASK-005 冒烟用 offscreen 子进程，仅装载不实例化 Controls） |

## 2. 命令与结果

| 命令（worktree 根目录执行） | 退出码 | 结果 | 证据 |
|---|---|---|---|
| `…/TASK-012-py312/python.exe -m pytest tests -q` | 0 | 296 passed（含 tests/core 架构守卫） | [pytest-full-20260915.txt](pytest-full-20260915.txt) |
| `…/TASK-012-py312/python.exe -m pytest tests/ui_shell -v` | 0 | 46 passed（35 python + 11 QML 装载/行为） | [pytest-ui_shell-verbose-20260915.txt](pytest-ui_shell-verbose-20260915.txt) |

两次运行均为 2026-09-15 本机执行，输出原文保存于本目录。

## 3. AC 对照

| AC | 覆盖 | 证据（测试） |
|---|---|---|
| AC-NAV-001 启动默认书架 | ✅ Python + QML | `test_defaults_to_bookshelf_with_four_entries`、`test_startup_lands_on_bookshelf`（rail checked=[T,F,F,F]、page-bookshelf visible） |
| AC-NAV-002 一级页面只有四个 | ✅ Python + QML | `test_navigate_rejects_fifth_route`（服务层拒绝）、`test_appshell_declares_exactly_four_top_level_pages`（rail 恰好 4 项、四页对象存在） |
| AC-NAV-003 切换保持上下文 | ✅ Python + QML | `test_context_*`（服务层 book/chapter/page 保留、运行中任务标记不清除）、`test_switching_pages_only_toggles_visibility_and_keeps_context`（settings→bookshelf 后模型行数不变、页面未销毁） |
| AC-LIB-001 新建 Book | ✅ Python + QML | `test_bookshelf_viewmodel`（createBook → refreshBooks）；`test_creating_book_clears_empty_state_and_populates_grid`、`test_new_book_dialog_flow_creates_book`（QML Dialog→use case 端到端） |
| AC-CH-001..004 章节 | ✅ Python + QML | chapter CRUD/排序测试；`test_enter_buttons_follow_chapter_selection`、`chapterListView.count` 断言 |
| 导入入口（D05 §7/§8） | ✅ Python（QML 对话框交互见 NOT_RUN） | `importPages`/`importFilesFromUrls` 测试（StubImporter 记录调用、URL→ImportSource） |
| 空状态（D05 §62） | ✅ QML | `test_shelf_and_detail_empty_states`、`test_workbench_and_reader_are_honest_skeletons` |

架构守卫（tests/core/test_architecture.py）随全仓 296 passed：`src/ui` 无 infrastructure import，
domain 层无 Qt/sqlite 依赖。

## 4. NOT_RUN / 边界（如实记录）

| 项 | 状态 | 说明 |
|---|---|---|
| 100%/150%/200% DPI 截图初验 | **NOT_RUN（BLOCKED）** | 应用装配不在本切片白名单：`Main.qml`/`bootstrap/app.py` 的 scope-change request 待 Codex 裁决（见 TASK-012.md 实施计划），当前无法从入口启动完整应用截图。AppShell 可由测试独立装载（test_qml_shell），DPI 完整矩阵归 TASK-022/026 |
| 键盘 Tab/方向键焦点全量 | NOT_RUN | Rail 首按钮 focus 已设；全量键盘矩阵归 TASK-022 |
| 导入 FileDialog 原生交互 | NOT_RUN | 原生文件对话框无法无头驱动；QML→`importFilesFromUrls` 的调用契约已由 python 侧测试覆盖，端到端交互归 TASK-022 |
| 工作台/阅读器/设置真实内容 | N/A（设计边界） | 本切片仅 §62 空状态骨架，TASK-013/015/022 交付 |
| 阅读进度显示 | 诚实占位 | TASK-007 无字段，UI 显示"—"，不虚构（D05 §7.1） |

## 5. 实现要点（供 Review 参考）

- `NavigationService`：不可变 `PageContext`/`replace` 状态；`navigate()` 拒绝非一级页；
  `set_workbench_activity` 的 badge 不因切换页面清除。
- QML 遵守 D05 §60（无业务逻辑）：全部决策在 ViewModel/Service；四页常驻仅切 `visible`。
- 已记录的 PySide6 6.11 平台事实（test_qml_shell 模块 docstring 与代码注释）：
  `QQmlComponent.status` 在 PySide6 中是方法；Repeater delegate item 不在 QObject 树
  （`Repeater.itemAt` 经 python wrapper 返回 None，经 QML 内部调用正常）；Loader item 为
  JS ownership，存在被 QML GC 回收的窗口期（BookGrid 因此不用 Loader，双 view 常驻切
  visible）；QML 无法调用非 slot 的 python 模型方法（ChapterList 行选中从 delegate 角色取
  chapterId，不走 roleForName/data）；QML delegate 绑定字符串字段需要 python 侧预转
  （datetime→ISO 字符串，否则到达 QML 为 undefined）。
- 工作台/阅读器骨架页的入口按钮 disabled，避免暗示不存在的能力。
