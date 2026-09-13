---
task_id: TASK-xxx
author: 待填写
recipient: Codex
base_commit: null
delivery_head: null
status: draft
---

# Handoff：TASK-xxx

## 交付结果

实际完成范围、变更路径与提交列表；与任务 Acceptance Criteria 逐项对照。delivery_head 指向实现提交，本 Handoff 可在后续文档提交中记录该 hash。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| 必填 | 原样记录 | 必填 | PASS/FAIL/BLOCKED/NOT_RUN/N/A | 仓库相对路径或可访问证据 |

明确哪些未运行、为什么；不得将 Mock 成功表述为模型质量达标。

## 接收方式

分支、worktree、启动/复现命令、前置条件、数据路径、已批准的依赖变化；下一步接收者需要做的具体检查。

## 风险与遗留

未解决问题、用户选择、破坏性操作/迁移影响、回退方法、关联 Task；无需重复项目背景。

## 实验附录（仅实验任务）

数据来源与许可、数据 Hash、模型/权重版本和 Hash、Provider/Runtime、硬件、网络策略、参数、运行次数、原始结果、质量判断办法、失败样例、限制、建议。Secret 不入报告。
