---
id: TASK-013
title: 实现工作台与任务进度交互
kind: implementation
status: in_review
approval: approved
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
depends_on: [TASK-011, TASK-012, TASK-014]
base_commit: 46646d58b3f645fa30fe7e10fae050218f9c55bb
branch: agent/zcode/TASK-013-workbench-task-progress
worktree: G:/CODEX/New Manga.worktrees/TASK-013-zcode
delivery_head: da1daf1
integration_commit: null
---

# TASK-013：实现工作台与任务进度交互

本 Task 已由 Owner=ZCode 完成实现并交付独立 Review（2026-09-16）：交付 head 固定 `da1daf1`（base `46646d5`），Handoff 与测试证据齐全，状态 `in_review`，待 Reviewer=DeepSeek Harness 审查、Codex 集成验证。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。TASK-015 及其他冻结 Task 不受本次授权影响。

## 来源与目标

D05 §15～36/55/61～65；D06 §74～79/102～103；D08 AC-PAGE/PROGRESS/NFR-UI/ERRUI。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-PAGE-002、AC-PAGE-003、AC-PROGRESS-001、AC-PROGRESS-002、AC-PROGRESS-003、AC-PROGRESS-004、AC-PROGRESS-005、AC-PROGRESS-006、AC-PROGRESS-007、AC-NFR-UI-001、AC-NFR-UI-002。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [x] 固定PageList/Viewer/Inspector/底部TaskProgress同时可用，支持当前章节多选与命令入口、Region编辑和三种图/Compare。（实现 commit `da1daf1`；Clean/Translated 产物占位与几何画布编辑的范围边界见 Handoff）
- [x] PageList与TaskProgress使用同一投影；Viewer当前页与Pipeline焦点分开；失败/完成/跳过统计定位正确。（`src/ui/models/tasks/projection.py` 单一投影；与 `get_task_progress` 口径一致性有专项测试）
- [x] 暂停/停止/继续与状态按钮匹配；频繁百分比更新节流、关键事件及时响应；Dirty导航不丢编辑。（D06 §103 按钮矩阵 9 状态测试；250 ms 节流；暂停乐观反馈 ≤200 ms 断言；dirty 三键确认对话框）
- [x] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。（Handoff 已交付，Review 进行中，done 仍需独立 Review 通过与 Codex 集成）

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
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

### 实际执行记录（executed，2026-09-16）

- 环境：Windows 10.0.26200 x64；Python 3.12.3；PySide6 6.11.2；解释器 `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`；默认 Windows Qt 平台，未设置 offscreen。
- 命令：`python -m pytest tests/workbench` → **50 passed, 0 skipped**，退出码 0。无 skip 项，无逐项 skip 原因需要登记。
- 命令：`python -m pytest`（全量回归，testpaths=tests）→ **465 passed, 0 skipped**，退出码 0；含 TASK-012 已审 `tests/ui_shell` 套件与架构守卫，无回归。
- 证据：[windows-pytest-workbench.txt](../../verification/TASK-013/windows-pytest-workbench.txt)、[windows-pytest-full-suite.txt](../../verification/TASK-013/windows-pytest-full-suite.txt)。
- AC-NFR-UI-001 为 Mock 证据：worker 线程执行 + GUI 心跳存活测试；真实 AI 负载下的性能结论不在本 Task 范围（D07 目标值需 Benchmark）。

## 依赖、风险与阻塞

硬依赖：[TASK-011](TASK-011.md)、[TASK-012](TASK-012.md)、[TASK-014](TASK-014.md)。依赖必须已经集成 done 才可开始。

单Region重全翻译只给专项锁任务级确认；Page/Region Lock仍阻止。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：[TASK-013 工作台切片 Handoff](../handoffs/TASK-013-workbench-task-progress.md)，固定 base=`46646d5`、delivery_head=`da1daf1`。
- Review：尚无（已交付 DeepSeek Harness 独立 Review）。
- 实际执行/实验/测试：见上文“实际执行记录”与 [verification/TASK-013](../../verification/TASK-013/)。
- 最近状态：2026-09-13 接管规划创建；2026-09-16 依赖 TASK-011/012/014 全部完成后，用户授权释放本 Task，登记 `ready`；2026-09-16 ZCode 认领并完成实现（实现 commit `da1daf1`，Windows 验证 50 passed/0 skipped、全量 465 passed/0 skipped），Handoff 交付，Task 置 `in_review`，待独立 Review。
