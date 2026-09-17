---
id: TASK-023
title: 实现 PDF/MOBI 导入路线
kind: implementation
status: proposed
approval: pending_user_review
suggested_owner: ZCode
owner: null
reviewer: null
depends_on: [TASK-007, TASK-009, TASK-012, TASK-024]
base_commit: null
branch: null
worktree: null
integration_commit: null
---

# TASK-023：实现 PDF/MOBI 导入路线

本 Task 仅为规划，尚未授权、认领或实施。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D01 §2；D02 §8；D04 §8；D05 §52；G17。网页导入已按 U-1 取消；本任务规划仅覆盖 PDF/MOBI。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：本任务为设计/实验/基础工作，验收以下专属条件；关联产品 AC 不因本任务完成就自动 PASS。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [ ] 依据用户批准的格式支持范围实现PDF/MOBI解析，复用Managed Copy/Page用例。
- [ ] 保留排序/来源/重复策略，畸形/加密/不支持输入可诊断，取消和失败不破坏已导入数据。
- [ ] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。ready 前由 Codex与已冻结实际结构核对并收紧；不能自行扩展到整个 src/tests。

- src/application/importing/documents/**
- src/infrastructure/importers/**
- tests/import_formats/**
- doc/tasks/TASK-023.md
- doc/handoffs/TASK-023-*.md
- verification/TASK-023/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 计划：python -m pytest tests/import_formats；自制多页PDF/MOBI、损坏/不支持输入、顺序和源Hash。
- 以上均为计划，当前结果全部 NOT_RUN；命令中的测试目录需本 Task 实际建立后才能运行。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-007](TASK-007.md)、[TASK-009](TASK-009.md)、[TASK-012](TASK-012.md)、[TASK-024](TASK-024.md)。依赖必须已经集成 done 才可开始。

缺少格式契约不得自行发明行为；所有测试素材应有明确使用许可。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际执行/实验/测试：尚无。
- 最近状态：2026-09-13 接管规划创建；proposed，pending_user_review。
