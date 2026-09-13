---
id: TASK-020
title: 实现 Webtoon 分块处理与阅读
kind: implementation
status: proposed
approval: pending_user_review
suggested_owner: ZCode
owner: null
reviewer: null
depends_on: [TASK-013, TASK-015, TASK-019]
base_commit: null
branch: null
worktree: null
integration_commit: null
---

# TASK-020：实现 Webtoon 分块处理与阅读

本 Task 仅为规划，尚未授权、认领或实施。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D03 §5；D05 §20/40；D06 §17/67～70；D07 §14～17；D08 AC-WEBTOON/CAP。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-WEBTOON-001、AC-WEBTOON-002、AC-WEBTOON-003、AC-WEBTOON-004、AC-WEBTOON-005。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [ ] 一张超长图保持一Page，Tile仅为可重建Cache；按模型约束处理并回映到原图坐标。
- [ ] 长图按宽适配、按需解码、限制预取/内存，阅读位置重启恢复；Region/Mask/Render一致。
- [ ] 验证Tile边界重叠Region去重与拼接，非目标范围不变，清缓存不会破坏业务真值。
- [ ] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。ready 前由 Codex与已冻结实际结构核对并收紧；不能自行扩展到整个 src/tests。

- src/infrastructure/imaging/webtoon/**
- src/ui/qml/workbench/ViewerCanvas.qml
- src/ui/qml/reader/**
- src/ui/viewmodels/reader/**
- src/application/reading/**
- tests/webtoon/**
- doc/tasks/TASK-020.md
- doc/handoffs/TASK-020-*.md
- verification/TASK-020/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 计划：python -m pytest tests/webtoon；坐标往返、Tile边界、单Page数、滚动恢复和两模式阅读。
- 按授权fixture验证约1600x200000px，记录峰值内存/耗时，不将建议预算宣称实测。
- 以上均为计划，当前结果全部 NOT_RUN；命令中的测试目录需本 Task 实际建立后才能运行。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-013](TASK-013.md)、[TASK-015](TASK-015.md)、[TASK-019](TASK-019.md)。依赖必须已经集成 done 才可开始。

允许修改既有Viewer/Reader，必须先集成依赖并避免与TASK-013/015并行写同文件。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际执行/实验/测试：尚无。
- 最近状态：2026-09-13 接管规划创建；proposed，pending_user_review。
