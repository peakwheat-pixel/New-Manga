---
task_id: TASK-xxx
reviewer: 待填写
author: 待填写
base_commit: null
reviewed_head: null
decision: pending
---

# Review：TASK-xxx

Reviewer 不能是变更作者。decision 为 pending / changes_requested / approved / blocked；只有对该 reviewed_head 的实际审查才有效。

## 范围与依据

需求/AC、diff、受影响调用链、共享契约、数据和 UI 边界；记录未审到的部分。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态/修订 commit |
|---|---|---|---|---|---|---|
| R-001 | P0/P1/P2 | 必填 | 必填 | 必填 | 必填 | open/fixed/deferred |

没有发现时明确写“在记录范围内未发现问题”；不能留模板占位行冒充 finding。

## 验证

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 必填 | 实际执行内容 | 必填 | PASS/FAIL/BLOCKED/NOT_RUN/N/A | 必填 |

Spec、Architecture、Verification 三轴分别给出结论。P0/P1 未解决、关键验证缺失时不可批准。

## 结论与复审

固定 head 是否可交 Codex 集成、理由、剩余风险。复审追加新 head 与对应 findings disposition，不抹掉旧记录；集成后的测试由 Codex另行记录。
