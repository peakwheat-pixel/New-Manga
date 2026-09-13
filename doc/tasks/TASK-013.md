---
id: TASK-013
title: 实现工作台与任务进度交互
kind: implementation
status: proposed
approval: pending_user_review
suggested_owner: ZCode
owner: null
reviewer: null
depends_on: [TASK-011, TASK-012, TASK-014]
base_commit: null
branch: null
worktree: null
integration_commit: null
---

# TASK-013：实现工作台与任务进度交互

本 Task 仅为规划，尚未授权、认领或实施。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D05 §15～36/55/61～65；D06 §74～79/102～103；D08 AC-PAGE/PROGRESS/NFR-UI/ERRUI。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-PAGE-002、AC-PAGE-003、AC-PROGRESS-001、AC-PROGRESS-002、AC-PROGRESS-003、AC-PROGRESS-004、AC-PROGRESS-005、AC-PROGRESS-006、AC-PROGRESS-007、AC-NFR-UI-001、AC-NFR-UI-002。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [ ] 固定PageList/Viewer/Inspector/底部TaskProgress同时可用，支持当前章节多选与命令入口、Region编辑和三种图/Compare。
- [ ] PageList与TaskProgress使用同一投影；Viewer当前页与Pipeline焦点分开；失败/完成/跳过统计定位正确。
- [ ] 暂停/停止/继续与状态按钮匹配；频繁百分比更新节流、关键事件及时响应；Dirty导航不丢编辑。
- [ ] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。ready 前由 Codex与已冻结实际结构核对并收紧；不能自行扩展到整个 src/tests。

- src/ui/qml/workbench/**
- src/ui/viewmodels/workbench/**
- src/ui/models/tasks/**
- tests/workbench/**
- doc/tasks/TASK-013.md
- doc/handoffs/TASK-013-*.md
- verification/TASK-013/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 计划：python -m pytest tests/workbench；选择切换、按钮enable、失败筛选、collapse、38成功2失败、模态覆盖确认。
- Mock长任务中操作UI不冻结；暂停反馈按获批AC阈值实测。
- 以上均为计划，当前结果全部 NOT_RUN；命令中的测试目录需本 Task 实际建立后才能运行。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-011](TASK-011.md)、[TASK-012](TASK-012.md)、[TASK-014](TASK-014.md)。依赖必须已经集成 done 才可开始。

单Region重全翻译只给专项锁任务级确认；Page/Region Lock仍阻止。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际执行/实验/测试：尚无。
- 最近状态：2026-09-13 接管规划创建；proposed，pending_user_review。
