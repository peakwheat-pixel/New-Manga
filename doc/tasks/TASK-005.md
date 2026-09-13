---
id: TASK-005
title: 建立最小工程入口与架构守卫
kind: implementation
status: proposed
approval: pending_user_review
suggested_owner: Codex
owner: null
reviewer: null
depends_on: [TASK-002, TASK-003, TASK-004]
base_commit: null
branch: null
worktree: null
integration_commit: null
---

# TASK-005：建立最小工程入口与架构守卫

本 Task 仅为规划，尚未授权、认领或实施。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D02 §1/14/16；D07 §83；D08 AC-OPTIONAL；G01/G18。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-OPTIONAL-001。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [ ] 采用 TASK-004 获批版本提供可重复安装/运行/测试入口；依赖锁定方式由实际工具确定，只保留一种。
- [ ] Core 无 torch/transformers 等重型可选依赖仍可启动；按需建模块，不批量生成空实现。
- [ ] 建立 Domain 禁止导入 Qt/SQLite/ML、UI 禁止直连具体存储/Provider 的可运行守卫。
- [ ] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。ready 前由 Codex与已冻结实际结构核对并收紧；不能自行扩展到整个 src/tests。

- pyproject.toml
- requirements*.txt
- uv.lock
- .gitignore
- src/bootstrap/**
- src/domain/__init__.py
- src/application/__init__.py
- src/ports/__init__.py
- src/infrastructure/__init__.py
- src/ui/__init__.py
- tests/core/**
- doc/tasks/TASK-005.md
- doc/handoffs/TASK-005-*.md
- verification/TASK-005/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 计划：python -m pytest tests/core；验证干净 Core 环境启动与可选依赖缺失。
- 至少一个真实边界违规会被守卫检测；启动失败产生可诊断错误。
- 以上均为计划，当前结果全部 NOT_RUN；命令中的测试目录需本 Task 实际建立后才能运行。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-002](TASK-002.md)、[TASK-003](TASK-003.md)、[TASK-004](TASK-004.md)。依赖必须已经集成 done 才可开始。

主线/依赖/启动装配由 Codex维护；应用骨架从本任务才开始。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际执行/实验/测试：尚无。
- 最近状态：2026-09-13 接管规划创建；proposed，pending_user_review。
