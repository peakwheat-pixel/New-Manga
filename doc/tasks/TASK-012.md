---
id: TASK-012
title: 实现四页导航与书架 UI
kind: implementation
status: proposed
approval: pending_user_review
suggested_owner: ZCode
owner: null
reviewer: null
depends_on: [TASK-005, TASK-007]
base_commit: null
branch: null
worktree: null
integration_commit: null
---

# TASK-012：实现四页导航与书架 UI

本 Task 仅为规划，尚未授权、认领或实施。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

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
- 最近状态：2026-09-13 接管规划创建；proposed，pending_user_review。
