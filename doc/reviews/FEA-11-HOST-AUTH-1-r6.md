---
task_id: FEA-11-HOST-AUTH-1
reviewer: 独立上下文 fresh subagent（DSH 派发；parent session-20e77fbf-d068-4823-b34b-4a7a9efbd4b4；未参与实现与 r1–r5 审查）
reviewer_kind: subagent
author: DSH（Lead/Architect/Integrator；本卡实施）
base_commit: 7ab9eea87
reviewed_head: 9b70b836d
decision: changes_requested
---

# Review：FEA-11-HOST-AUTH-1（r6）

> 本报告由 DSH 依据 r6 Reviewer 返回的完整报告正文落盘（2026-11-05）。Reviewer 只读 HEAD `9b70b836d`；diff `37987f946..HEAD`；工作树审查前后 clean；C-17 零 diff；pins 18/18；未 push。

## 结论
**changes_requested：P0=0 / P1=0 / P2=5。** r5 六项中 deferral 表与 allowed_paths 已完成；§3.2:163 守卫 4/5（kind/digest/预校验前移已实现，plan 有效性未预检也未登记）；测试判别力不足；卡面计数、gates.log 可审计性、STATUS/PLAN 指针未完成。无 P0/P1。

## AC 判定
- **AC1 MET**（5/5，Python 独立复算）；
- **AC2 MET**（6/6，固定向量独立复算）；
- **AC3 PARTIAL**（typed 失败/retry fresh auth/kind-digest 守卫已实现 22/22；缺 HostRuntime e2e、ACK 重发/崩溃点矩阵、retry 无冻结 wire 命令、plan 有效性 Host 预检未做）；
- **AC4 MET（路径层）**（`FEA-11-r3.md:38`）；终态应为 `closed_with_limitations`。

## r5 findings 核对
- R5-P2-01 **partially（4/5）**：kind 比对/digest 相等/预校验前移已实现；plan 有效性未预检未登记。
- R5-P2-02 **partially**：新授权持久化与 kind mismatch 测试有判别力；capability 测试只断言异常类型（空断言）；缺 digest 守卫/CommitDigest 分支/typed 歧义用例。
- R5-P2-03 **fixed**（allowed_paths 已加 HostErrorCodes.cs）。
- R5-P2-04 **not fixed**（卡面 19/19（14 方法）← 实际 22/22（17 方法）；1390 未标 provenance）。
- R5-P2-05 **partially**（IPC env 已写；full pytest head 标注错误；code-unchanged 句不实；dirty 无路径）。
- R5-P2-06 **fixed / deferral-accepted**。
- R5-P2-07 **not fixed**（STATUS/PLAN 仍 r1–r3；卡面 reviewer/状态/待 r5 元数据）。

## 本轮 findings
- **R6-P2-01**：plan 有效性未预检（§3.2:163 守卫列含 plan confirmed/有效）；Core `take_confirmed` 事务内 fail-closed 兜底；需登记 limitation 并限定卡面表述。
- **R6-P2-02**：capability 测试空断言（未校验 error.Code）；缺 digest 守卫/CommitDigest/typed 歧义用例。
- **R6-P2-03**：卡面计数不实且与提交信息矛盾（22/22 17 方法）；1390 为 r5 数字未标 provenance。
- **R6-P2-04**：STATUS/PLAN 指针停在 r1–r3；卡面 reviewer/状态/待 r5 未更新；STATUS/REBASELINE 不在 allowed_paths。
- **R6-P2-05**：gates.log provenance 不可核（full pytest head 标注错、code-unchanged 不实、dirty 无路径、无 TRX）。

## 门禁复核
fea11 40 passed；Fea11HostAuthTests 22/22；Host.Tests 105/0/49；Canonical+Miniter 11/11；check PASS；pins 18/18；C-17 零 diff；工作树 clean；full pytest/.NET/IPC 未复跑（gates.log 数字非 Reviewer 复跑）。

## done / closed_with_limitations
- done：不同意（AC3 PARTIAL）。
- closed_with_limitations：方向同意，当前 HEAD 不满足；完成 5 项最低返修（卡面计数/收口指针/gates.log/plan 有效性登记/能力测试判别力）后可收口（不 push），limitation 至少保留：HostRuntime e2e、ACK 重发/崩溃点矩阵、retry 仅 Host 编排 API、plan 有效性由 Core take_confirmed 兜底、既有 deferral。

## 自审声明
fresh subagent（parent session-20e77fbf），未参与实现/r1–r5；只读仓库；未 commit/push；工作树前后 clean；C-17 零 diff；pins 18/18。
