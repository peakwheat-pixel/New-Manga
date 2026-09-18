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

**执行口径（2026-09-18 更新：双轴强制已取消）**：Review 必须覆盖 **Architecture**（分层/契约/依赖/安全/持久化）与 **Verification**（实际运行检查、逐项 PASS/FAIL/BLOCKED/NOT_RUN）。`code-review` 技能的 **Standards**（是否符合本仓库记录的标准）与 **Spec**（是否忠实实现来源 AC）是**可选视角**：可用可不用，**不再强制**，也**不再要求**分别报告、独立 sub-agent 并行执行、"两遍相互隔离"检查或偏差声明（并行双轴子代理能力在本会话不可用，用户 2026-09-18 决定取消该强制项）。

- **视角状态声明（建议）**：如采用了多个视角，建议各自标注 `executed`/`N/A` 并给一行小结；**缺声明不再导致 Review 未完成**。
- **批准门槛（不变）**：P0/P1 未解决或关键验证缺失时不可批准（见下「验证」与「结论」）。

## 范围与依据

需求/AC、diff、受影响调用链、共享契约、数据和 UI 边界；记录未审到的部分。

## Standards（可选视角）

按**本仓库记录下来的**标准审查，并逐条给出依据文件与条款：`AGENTS.md`、[09 协作协议](../09_COLLABORATION.md)、[02 技术架构](../02_TECHNICAL_ARCHITECTURE_.md)（§架构方向、§16 推荐源码边界）、D03/D06/D08 相关条文、本 Task 的允许/禁止范围。

仓库**未记录**标准的方面，适用 Fowler smell baseline（_Refactoring_ 第 3 章）作为**判断项**，必须带 label（如 "possible Divergent Change"、"possible Duplicated Code"），并引用对应 hunk。两条规则：**仓库记录的标准优先于 baseline**；**每个 smell 都是判断项而非硬性违规**。工具已强制的项（formatter/linter/类型检查）跳过，不重复报告。

写清：① 违反记录在案标准的**硬性项**（须引用标准文件 + 条款）；② 命中的 baseline smell（须引用 hunk）。建议 < 400 字。

## Spec（可选视角）

来源顺序：本 Task 文件的 AC → 其引用的 D01～D08 条文与 `doc/contracts/**` → `STATUS.md` 中的用户裁决。**不得**用聊天记录、旧仓库路径或目标图推断已有实现。

写清：① 来源要求但**缺失/部分完成**的项（引用 AC 原文）；② diff 中**来源未要求**的行为（scope creep）；③ **看似实现但实现有误**的项。每项引用来源原文。建议 < 400 字。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态/修订 commit |
|---|---|---|---|---|---|---|
| R-001 | P0/P1/P2 | 必填 | 必填 | 必填 | 必填 | open/fixed/deferred |

没有发现时明确写“在记录范围内未发现问题”；不能留模板占位行冒充 finding。

## 验证

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 必填 | 实际执行内容 | 必填 | PASS/FAIL/BLOCKED/NOT_RUN/N/A | 必填 |

**Architecture 与 Verification 两面分别给出结论**（如另用了 Standards/Spec 视角，一并写明）。P0/P1 未解决、关键验证缺失时不可批准。

## 结论与复审

固定 head 是否可交 Codex 集成、理由、剩余风险。复审追加新 head 与对应 findings disposition，不抹掉旧记录；集成后的测试由 Codex另行记录。
