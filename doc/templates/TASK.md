---
id: TASK-xxx
title: 待填写
kind: design
status: proposed
approval: pending_user_review
suggested_owner: Codex
owner: null
reviewer: null
depends_on: []
base_commit: null
branch: null
worktree: null
integration_commit: null
---

# TASK-xxx：任务标题

## 来源与目标

需求文件/章节/AC ID、当前代码或测试证据；一个可观察的交付结果。不存在的代码路径必须标为拟议路径。

## Acceptance Criteria

- [ ] 具体前置条件、动作、预期结果及对应证据。
- [ ] 每项必要 AC 有实际验证记录，未跑项明确标 NOT_RUN/BLOCKED。

## 允许修改范围

- 明确相对项目根目录的文件/目录；共享接口、Schema、依赖变更单列。
- 本 Task、自己的 Handoff、经分配的测试/verification 路径。

## 禁止范围

写明非目标、依赖方模块、用户原始数据；范围扩大须先由 Codex登记。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| 必填 | 标注 planned，不伪装为已存在命令 | 必填 | NOT_RUN | 无 |

## 依赖、风险与阻塞

depends_on 必须是已存在 Task ID。区分硬依赖与可并行条件；记录未定契约及解除阻塞标准。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际测试：尚无。
- 后续实际记录包含日期、commit、环境、结果、遗留项；最终由 Codex填写 integration_commit 并改 done。
