---
id: TASK-011
title: 实现命令计划、任务调度与可恢复进度
kind: implementation
status: proposed
approval: pending_user_review
suggested_owner: Codex
owner: null
reviewer: null
depends_on: [TASK-008, TASK-009, TASK-010]
base_commit: null
branch: null
worktree: null
integration_commit: null
---

# TASK-011：实现命令计划、任务调度与可恢复进度

本 Task 仅为规划，尚未授权、认领或实施。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D03 §20～24；D06 §25～94；D08 AC-CMD/PIPE/PAUSE/STOP/CRASH/RETRY/LOCK/CONFLICT。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-LOCK-001、AC-LOCK-002、AC-LOCK-003、AC-LOCK-004、AC-LOCK-005、AC-CMD-001、AC-CMD-002、AC-CMD-003、AC-CMD-004、AC-PIPE-001、AC-PIPE-002、AC-PIPE-003、AC-PIPE-004、AC-PAUSE-001、AC-PAUSE-002、AC-PAUSE-003、AC-STOP-001、AC-STOP-002、AC-STOP-003、AC-CRASH-001、AC-CRASH-002、AC-CRASH-003、AC-RETRY-001、AC-RETRY-002、AC-CONFLICT-001、AC-CONFLICT-002。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [ ] 覆盖冻结后的所有Page/Region命令，复用有效OCR、严格rerender、stale、prerequisite、不可变目标/配置快照。
- [ ] 实现资源上限、每步提交、双重Lock/Revision写回保护；暂停安全边界、停止保留成功成果、崩溃识别interrupted。
- [ ] 失败页重试创建新Run并记录来源；状态/跳过原因/百分比/页计数同一投影，覆盖空计划和非Page直接target。
- [ ] 先用确定性Mock验证完整依赖和失败路径；Mock结果不能证明AI质量。
- [ ] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。ready 前由 Codex与已冻结实际结构核对并收紧；不能自行扩展到整个 src/tests。

- src/domain/tasks/**
- src/application/tasks/**
- src/application/translation/pipeline/**
- tests/pipeline/**
- doc/tasks/TASK-011.md
- doc/handoffs/TASK-011-*.md
- verification/TASK-011/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 计划：python -m pytest tests/pipeline；命令矩阵、Run中selection变化、全锁定/全跳过、取消计数、38成功2失败。
- Step故障注入、pause/stop竞态、crash重启、10→12写回冲突、Provider消失、上下文只写目标。
- 以上均为计划，当前结果全部 NOT_RUN；命令中的测试目录需本 Task 实际建立后才能运行。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-008](TASK-008.md)、[TASK-009](TASK-009.md)、[TASK-010](TASK-010.md)。依赖必须已经集成 done 才可开始。

共享Schema与DTO变更必须同步来源文档与调用者；不可用线程强杀破坏事务。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际执行/实验/测试：尚无。
- 最近状态：2026-09-13 接管规划创建；proposed，pending_user_review。
