---
task_id: FEA-11-HOST-AUTH-1
reviewer: 独立上下文 fresh subagent（DSH 派发；parent session-20e77fbf-d068-4823-b34b-4a7a9efbd4b4；未参与实现与 r1–r6 审查）
reviewer_kind: subagent
author: DSH（Lead/Architect/Integrator；本卡实施）
base_commit: 7ab9eea87
reviewed_head: 04954d209
decision: changes_requested
---

# Review：FEA-11-HOST-AUTH-1（r7）

> 本报告由 DSH 依据 r7 Reviewer 返回的完整报告正文落盘（2026-11-05）。Reviewer 只读 HEAD `04954d209`；diff `9b70b836..HEAD`；工作树审查前后 clean；C-17 零 diff；pins 18/18；未 push。

## 结论
**changes_requested：P0=0 / P1=0 / P2=2 / P3=2。** r6 五项中 3 项已实质完成（R6-P2-01/04/05），2 项部分：R6-P2-02 只补了 capability 的 error.Code（digest/CommitDigest 守卫仍无用例）；R6-P2-03 卡面 AC3 勾选行仍 19/19。无 P0/P1、无新增安全洞。

## AC 判定
- **AC1 MET**（5/5，Python 独立复算 5 向量一致）；
- **AC2 MET**（6/6，固定向量独立复算一致；ApplyRequest 注入接线）；
- **AC3 PARTIAL**（顺序/typed 失败/retry fresh auth/守卫/capability 已实现 22/22；缺 HostRuntime e2e、ACK 重发/崩溃点矩阵、retry 冻结命令、plan 预检（已 deferral）；另两个守卫用例缺口）；
- **AC4 MET（路径层）**（`FEA-11-r3.md:38` 逐字核对）。

## r6 findings 核对
- R6-P2-01 **fixed/deferral-accepted**（plan 有效性 deferral + Core take_confirmed 事务内 fail-closed 核实）；
- R6-P2-02 **partially**（capability 已补；digest/CommitDigest 守卫无用例）；
- R6-P2-03 **partially**（状态行已改；AC3 勾选行仍 19/19）；
- R6-P2-04 **fixed**（STATUS/PLAN/reviewer/allowed_paths）；
- R6-P2-05 **partially 3/4**（head 更正/不实句删除/dirty 路径；TRX 残留降 P3）。

## 本轮 findings
- **R7-P2-01**：retry digest 守卫（HostOperationOrchestrator.cs:106-111）与 CommitDigest 守卫（:68-71、SourceOperationCoordinator.cs:324-327）缺测试；给出公开 API 构造方案。
- **R7-P2-02**：卡面行 87 仍 19/19（应 24/24 19 方法）；行 59 仍「待 r6」。
- **R7-P3-01**：卡面「含 flaky 说明」与当前 gates.log 不符；full .NET 1390 仅历史 log。
- **R7-P3-02**：卡面行 52「状态：proposed / 当前透传」措辞过期。

## 门禁复核（Reviewer 实跑）
fea11 40 passed；Fea11HostAuthTests 22/22；Host.Tests 105/0/49；Canonical+Minter 11/11；check PASS；pins 18/18；C-17 零 diff；**可选全量 .NET 在 HEAD 1393/0/78**；IPC 3/3；工作树前后 clean。

## done / closed_with_limitations
- done：不同意（AC3 PARTIAL）。
- closed_with_limitations：方向同意；补齐 R7-P2-01/02 两个 P2 小项后可收口，limitation 清单基本完整（HostRuntime e2e、ACK 重发/崩溃点矩阵、retry 仅 Host 编排 API、plan 有效性 Core 兜底、R4 系列 deferral）。

## 自审声明
fresh subagent（parent session-20e77fbf），未参与实现/r1–r6；只读仓库；未 commit/push；全量 .NET 后恢复 FEA-09；工作树前后 clean。
