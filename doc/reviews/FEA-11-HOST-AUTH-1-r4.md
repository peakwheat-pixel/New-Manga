---
task_id: FEA-11-HOST-AUTH-1
reviewer: 独立上下文 fresh subagent（DSH 派发；parent session-20e77fbf-d068-4823-b34b-4a7a9efbd4b4；未参与实现与 r1/r2/r3 审查）
reviewer_kind: subagent
author: DSH（Lead/Architect/Integrator；本卡实施）
base_commit: 7ab9eea87
reviewed_head: 45caa9c18
decision: changes_requested
---

# Review：FEA-11-HOST-AUTH-1（r4）

> 本报告由 DSH 依据 r4 Reviewer 返回的完整报告正文落盘（2026-11-05）。Reviewer 只读 HEAD `45caa9c18`；diff `74da4f230..HEAD`；工作树审查前后 clean；C-17 零 diff；无依赖变更；未 push。

## 结论
**changes_requested**：P0=0、P1=1、P2=8。R3-P1-01(a)(b) 已实质修复、门禁可复跑；但 R3-P1-01(c) 的 `RetryAsync`/`RetryFailed` 不符合 C-17 §3.2 行 163/159/164：**复用旧授权而非重新授权 + 新授权 durable；重试 typed 拒绝不落 failed；无法区分未提交 failed 与已提交 failed**。不是 e2e/测试覆盖 limitation，不能仅靠 L-8/L-9 关闭。无 P0 安全洞。

## AC 判定
- **AC1 MET**（4 + 3 固定向量 Python 独立复算一致）。
- **AC2 MET**（六字段/code-point/canonical/注入；Minter 6/6）。
- **AC3 PARTIAL**（顺序探针有效但只证 Registry 早于 Core；retry 未达 §3.2:163/159/164；e2e/ACK 重发/崩溃点可 L-8/L-9）。
- **AC4 MET（路径层）**：`FEA-11-r3.md:38` 已接受 HOST-AUTH-1 为 P0-1 闭合路径；卡面应改引该行；P0-1 实际闭合仍取决于 AC1–AC3。

## Findings
- **R4-P1-01（P1，阻断）**：(1) retry 未重新授权/未落新授权（复用旧 AuthorizationJson）；(2) retry 的 typed 拒绝不落 failed；(3) 无法区分未提交 failed 与已提交 failed（RetryFailed 不查 CommitDigest）；(4) 生产不可达（仅测试调用 RetryAsync）+ 绕过 capability/plan 守卫。
  最低返修：coordinator 原子写新授权；RetryAsync 锁后重读 Registry→Authorize→落新授权→dispatch，typed 拒绝 MarkFailed；拒绝 CommitDigest!=null；committed-failure 用 §8 retryable；补 5 类测试。
- **R4-P2-01**：输入残余（plan_id 字符集、grant_ids 重复/上限、嵌套未知字段、generation 范围）。
- **R4-P2-02**：Registry scope/多 registry 非原子/`Begin` 在 Authorize 之后（与 §3.2:156-157 崩溃窗口差异）。
- **R4-P2-03**：receipt 只核 commit_digest，不核 operation_id/request_digest/state，不重算 canonical CommitReceipt；测试 lookup 返回 op-x 仍通过。
- **R4-P2-04**：committed-failure 只校验 code 非空、默认 retryable=true（§8 逐 code 语义被忽略）。
- **R4-P2-05**：grant_ids 逗号拼 CSV，含逗号 id 会被拆坏。
- **R4-P2-06**：卡面计数过期（Minter 3/3→6/6、.NET 1370→1381、AC4「r2」）；gates.log 的 head/TRX/worktree_clean 说明不足；STATUS/PLAN 变更未登记 allowed_paths。
- **R4-P2-07**：分类精度/用例（黑名单含未产出码、缺 typed 歧义分支）。
- **R4-P2-08**：non-BMP canonical 向量缺失。

## 门禁复核
fea11 40 passed；Fea11HostAuthTests 11/11；Minter+Canonical 10/10；check PASS；pins 18/18；C-17 零 diff；工作树 clean；全量 .NET 未复跑；IPC 首跑 1 failed/2 passed→复跑 3/3（Core 直连，非 Host e2e）。

## done / closed_with_limitations 意见
- done：不同意（AC3 PARTIAL + R4-P1-01）。
- closed_with_limitations：当前 head 不同意；R4-P1-01 必须修（或用户显式接受新 retry limitation）；修复后 P2-01/02/03/04/05 可 deferral（需 owner/编号），P2-06/07/08 收口。

## 自审声明
fresh subagent（parent session-20e77fbf），未参与实现/r1–r3；只读仓库；未 commit/push；C-17 零 diff；工作树 clean；IPC 隔离 fixture 在仓外。
