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

**执行口径（强制，2026-09-17 用户批准）**：Review 必须包含 `code-review` 技能的**两轴口径** —— **Standards**（代码是否符合本仓库记录下来的标准）与 **Spec**（代码是否忠实实现来源 Task/AC）—— 再加上本仓库既有的 **Architecture** 与 **Verification**，共四轴。两轴（Standards/Spec）**分别报告、不合并、不跨轴排名**：任一变更可能通过一轴而在另一轴失败。

- **隔离要求**：技能要求两轴各由独立 sub-agent 执行以避免 context 互相污染。有独立执行者/线程时优先**并行**两个子审查；环境不支持时，必须做**两遍相互隔离**的检查（不得用一遍通读充当两轴），并在报告中显式声明该偏差与替代做法。
- **轴状态声明**：报告须逐轴声明 `executed` 或 `N/A`（N/A 必须给理由）；缺声明、或未执行且无理由 → Review 视为未完成，**不得批准**。

## 范围与依据

需求/AC、diff、受影响调用链、共享契约、数据和 UI 边界；记录未审到的部分。

## Standards

按**本仓库记录下来的**标准审查，并逐条给出依据文件与条款：`AGENTS.md`、[09 协作协议](../09_COLLABORATION.md)、[02 技术架构](../02_TECHNICAL_ARCHITECTURE_.md)（§架构方向、§16 推荐源码边界）、D03/D06/D08 相关条文、本 Task 的允许/禁止范围。

仓库**未记录**标准的方面，适用 Fowler smell baseline（_Refactoring_ 第 3 章）作为**判断项**，必须带 label（如 "possible Divergent Change"、"possible Duplicated Code"），并引用对应 hunk。两条规则：**仓库记录的标准优先于 baseline**；**每个 smell 都是判断项而非硬性违规**。工具已强制的项（formatter/linter/类型检查）跳过，不重复报告。

写清：① 违反记录在案标准的**硬性项**（须引用标准文件 + 条款）；② 命中的 baseline smell（须引用 hunk）。建议 < 400 字。

## Spec

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

四轴（**Standards、Spec**、Architecture、Verification）分别给出结论，并逐轴声明 `executed`/`N/A`；每轴末尾给一行小结（该轴发现数 + 本轴最严重项），**不跨轴排名、不合并两轴**。P0/P1 未解决、关键验证缺失时不可批准。

## 结论与复审

固定 head 是否可交 Codex 集成、理由、剩余风险。复审追加新 head 与对应 findings disposition，不抹掉旧记录；集成后的测试由 Codex另行记录。
