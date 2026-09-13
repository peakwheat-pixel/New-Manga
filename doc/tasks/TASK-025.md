---
id: TASK-025
title: 按批准契约实现 Plugin/Hooks 与可选扩展
kind: implementation
status: proposed
approval: pending_user_review
suggested_owner: ZCode
owner: null
reviewer: null
depends_on: [TASK-019, TASK-022, TASK-024]
base_commit: null
branch: null
worktree: null
integration_commit: null
---

# TASK-025：按批准契约实现 Plugin/Hooks 与可选扩展

本 Task 仅为规划，尚未授权、认领或实施。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D02 §12；D07 §71～72/110；TASK-024获批契约。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：本任务为设计/实验/基础工作，验收以下专属条件；关联产品 AC 不因本任务完成就自动 PASS。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [ ] 实现获批Hook的输入/输出Schema、版本兼容与错误隔离，插件不能绕过Repository破坏不变量。
- [ ] 文件/网络访问限定授权范围并可审计；不兼容插件被禁用并显示原因，Core继续运行。
- [ ] Plugin Agent仅在TASK-024明确保留且AC批准后实现其约定范围；否则记录正式范围决定而非静默省略。
- [ ] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。ready 前由 Codex与已冻结实际结构核对并收紧；不能自行扩展到整个 src/tests。

- src/ports/plugins/**
- src/infrastructure/plugins/**
- src/application/plugins/**
- src/ui/qml/settings/PluginSettings.qml
- tests/plugins/**
- doc/tasks/TASK-025.md
- doc/handoffs/TASK-025-*.md
- verification/TASK-025/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 计划：python -m pytest tests/plugins；崩溃插件、畸形返回、越界文件/网络尝试、不兼容版本和核心数据不变。
- 根据获批AC执行扩展流程；未定义AC时保持blocked不自行补产品行为。
- 以上均为计划，当前结果全部 NOT_RUN；命令中的测试目录需本 Task 实际建立后才能运行。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-019](TASK-019.md)、[TASK-022](TASK-022.md)、[TASK-024](TASK-024.md)。依赖必须已经集成 done 才可开始。

不得运行来源不明的插件；实验与产品Plugin Agent不是同一个开发Agent。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际执行/实验/测试：尚无。
- 最近状态：2026-09-13 接管规划创建；proposed，pending_user_review。
