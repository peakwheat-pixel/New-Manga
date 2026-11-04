---
task_id: FEA-11
reviewer: 独立上下文子 agent（fresh subagent，parent session-20e77fbf-d068-4823-b34b-4a7a9efbd4b4）
reviewer_kind: subagent
author: DSH（Lead/Architect/Integrator）
base_commit: 00a1c27b
reviewed_head: 89d54ef4
decision: changes_requested
---

# Review：FEA-11（r4）

> 说明：本报告由 DSH 依据 r4 Reviewer（fresh subagent，未参与实现/r1/r2/r3）返回的完整报告正文落盘（2026-11-05）。Reviewer 只读 HEAD `89d54ef44`，diff `00a1c27b..89d54ef4`；工作树复核前后 clean；探针/日志在 `workspace/FEA-11/review-r4/`。

## 结论
**changes_requested**：P0=1（r2 P0-1 Host 自签授权，deferral-accepted 但阻断 done）、**P1=1（P1-04 capability 值 + probe 门）**、P2=13。r3 的 6 条 P1 中 **P1-01/02/03/05/06 已实质修复**（P1-01 用真实 Core 探针独立证实：6 条命令不再 UNKNOWN_COMMAND，旧名仍 UNKNOWN_COMMAND）；**P1-04 仅修形状，值违反 §5.2 且探针门缺失**。

## 关键独立验证
- P1-01：静态对表 14/14 通道正确；真实 Core stdio：6 条命令返回类型化业务错误（INVALID_REQUEST/SOURCE_OPERATION_NOT_FOUND）；反向对照旧名仍 UNKNOWN_COMMAND；`ApplySourceSyncPlan` 走应用面返回 HOST_ONLY_REQUIRED。
- 门禁：pytest fea11 37/0；pytest tests 3048/0/10；check PASS；pins 18/18；C-17 零 diff；工作树 clean（全量 .NET/IPC 未复跑，只读约束）。

## r3 findings 处置
- fixed：P1-01、P1-02、P1-03、P1-05、P1-06（其中 P1-02/03/06 无测试）。
- partially：P1-04（name 用 probe token `source.sync.*` 且第 7 项为 source.read/1，违反 §5.2 闭集；无 probe 门；可用性恒 true）。
- P2：AC-MATRIX 与卡矛盾、卡正文过期、PLAN 行尾/ready/r3 待派、allowed_paths 缺 r3 diff、LINEAGE-1 exporting 路径不存在、缺测试、r2 报告未入库、r3 日志信息不足、P2-09 完整 CommitReceipt 未保存、AC11-4 无承接卡、N-01 无注册表对表回归、N-03 AC11-1 消费者不成立、N-04 folder relink 限制未登记、N-05 不存在的 allowed_paths、N-06 AC11-10 缺 EV/Manifests。

## AC 判定
AC11-2 MET（仅 Core seam）；其余 9 项 PARTIAL；**done 不满足**（P0-1 deferral 未获接受、P1-04、AC11-10 证据件缺失、LINEAGE-1 串行门禁）。

## closed_with_limitations 意见
当前不成立；最低前置：P1-04 闭集值 + probe 门（Begin 前拒绝）、最小回归测试、文档单一口径、AC11-10 交付件、AC11-4 承接、P0-1 limitation 显式接受、limitation 清单（AC11-1…10 + “LINEAGE-1 前 UI/读路径不得消费同步 binding”）。
