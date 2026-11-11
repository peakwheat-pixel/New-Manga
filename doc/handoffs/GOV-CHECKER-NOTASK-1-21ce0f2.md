---
task_id: GOV-CHECKER-NOTASK-1
author: Codex
recipient: 独立 Reviewer / ZCode Integrator
base_commit: 0201dc9612faa9eea9104b8e0568414e4a7bad5a
delivery_head: 21ce0f24f2c4b0a153f85163eadc64b36b7bf72b
status: review_requested
---

# Handoff：GOV-CHECKER-NOTASK-1

## 交付结果

实现 commit `21ce0f24f2c4b0a153f85163eadc64b36b7bf72b` 只修改 `tools/governance/check.ps1`：活动指针优先，未指定 TaskPath 且无活动指针时识别 ZCode v2 白名单和路径排除；明确空窗输出一条 warning 并继续全局检查。释放及 §4.4 裁决见 Task 卡及其证据表。

AC1/AC2：隔离矩阵 31/31 断言通过，包括 12 个基线场景、路径和语法边界、两种变异及逐字节恢复。终态和 pending 构造包含额外错误，断言核查目标错误行，不以 EXIT 单独证明。AC3：活动指针状态的交付门禁已测；收口空窗下主树 default、独立 Review、最终裁决和资源 closeout 尚未完成。

## 验证证据

| AC/场景 | 实际命令或步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1/AC2 | `python verification/GOV-CHECKER-NOTASK-1/implementation_matrix.py` | Windows；仓外隔离 checkout `21ce0f2` | 31/31 断言、两种变异、恢复 SHA 均通过，EXIT 0 | `verification/GOV-CHECKER-NOTASK-1/implementation-run-21ce0f2-r3.log`、`implementation-notes.md` |
| AC3 交付门禁 | `check.ps1` default / `-TaskPath`、`verify_pins.ps1`、`python tools/generate_api_inventory.py --check` | clean main HEAD `b76c4ab0621b3ec27433727d86078f0958b9d264` | 四项 EXIT 0，18 pins、API 86；有当前 Task 指针 | `verification/GOV-CHECKER-NOTASK-1/delivery-gates-b76c4ab.log` |
| AC3 收口 | 空窗 default 与最终 gate | 主树关闭 Task 后 | NOT_RUN | 待生成 |

## 接收方式

仓库 `G:/CODEX/New Manga`，`main`。Reviewer 应只读固定的送审 HEAD，核验 diff、v2 白名单和路径排除、指针优先、TaskPath 不变、31 场景及两种变异，并记录实际 reviewed head 和独立会话 ID。ZCode Integrator 之后裁决生命周期与收口，特别是 AC3 含 Review 和收口门禁的先后依赖。

## 下一任务建议

当前任务尚未完成；先完成独立 Review 和最终裁决。后续 Task 尚未释放，无需下一步操作。

## 风险与遗留

- 空窗主树 gate 仍 NOT_RUN；隔离副本结果不代替关闭后的实测。
- 仓外两个基线副本、实现副本及诊断日志保留，未做清理。资源 closeout 待裁决。
- 既有历史 evidence 的 checkout 字节差异和缺失 pyc 在隔离终态样本中产生额外错误，详见 `verification/GOV-CHECKER-NOTASK-1/README.md`。
- 不改变冻结契约、其他治理工具或历史 pin；未 push。
