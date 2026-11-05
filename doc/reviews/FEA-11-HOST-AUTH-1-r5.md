---
task_id: FEA-11-HOST-AUTH-1
reviewer: 独立上下文 fresh subagent（DSH 派发；parent session-20e77fbf-d068-4823-b34b-4a7a9efbd4b4；未参与实现与 r1–r4 审查）
reviewer_kind: subagent
author: DSH（Lead/Architect/Integrator；本卡实施）
base_commit: 7ab9eea87
reviewed_head: 37987f946
decision: changes_requested
---

# Review：FEA-11-HOST-AUTH-1（r5）

> 本报告由 DSH 依据 r5 Reviewer 返回的完整报告正文落盘（2026-11-05）。Reviewer 只读 HEAD `37987f946`；diff `45caa9c18..HEAD`；工作树审查前后 clean；C-17 零 diff；无依赖变更；未 push。

## 结论
**changes_requested：P0=0 / P1=0 / P2=7（本轮新发现）**。r4-P1-01 四项最低返修**均已落实**且可复跑（`RetryFailed` 原子写新授权；`RetryAsync` capability 门内重读 Registry→Authorize→mint→落盘→dispatch；typed 拒绝再落 failed；CommitDigest/Retryable 拒绝；committed-failure 用 §8 投影；`Fea11HostAuthTests` 19/19）。但 r4 退出条件未全满足：R4-P2-01/02/03 的 deferral 无 owner/编号；R4-P2-06/07 未收口；`RetryAsync` 未执行 §3.2:163 的 kind/request_digest 守卫；卡面/gates.log 有计数与 TRX 陈述不实；`HostErrorCodes.cs` 超 allowed_paths。无 P0 安全洞、无新 P1。

## AC 判定
- **AC1 MET**（5 向量 Python 独立复算一致，含 non-BMP `dc00aa…`）。
- **AC2 MET**（六字段/code-point/canonical/注入；Minter 6/6；3 固定向量一致）。
- **AC3 PARTIAL**（typed 失败/retry 四项已完成；ACK 重发/恢复/崩溃点与 HostRuntime e2e 未自动化；retry 无冻结 wire 命令；§3.2:163 kind/digest 守卫未完整执行）。
- **AC4 MET（路径层）**：`FEA-11-r3.md:38` 已接受本卡为 P0-1 闭合路径；实际闭合取决于 AC3。

## R4 findings 核对
- R4-P1-01 **closed**（四项落实；残余转 R5-P2-01/02）。
- R4-P2-01/02/03 **not-fixed；deferral 未按 r4 登记（无 owner/编号）**。
- R4-P2-04 **fixed**（HostErrorCodes §8 闭集+投影）。
- R4-P2-05 **fixed**（grant_ids 逗号拒绝）。
- R4-P2-06 **partially fixed**（AC 行/计数/TRX 陈述仍有不实）。
- R4-P2-07 **partially fixed**（分类精度补测 deferral 未登记）。
- R4-P2-08 **fixed**（non-BMP 向量）。

## 本轮新发现（P2）
- **R5-P2-01**：RetryAsync 未执行 §3.2:163 Host 侧守卫（kind 由命令名推导未与 entry.Kind 比对；未断言 minted.RequestDigest==entry.RequestDigest；state/Retryable/CommitDigest 预校验在 Registry.Authorize 之后；plan 有效性未预检）。
- **R5-P2-02**：新 retry 路径测试判别力不足（未直接测 RetryFailed 的 CommitDigest 分支/journal 新授权字段/RetryAsync capability/typed 歧义）。
- **R5-P2-03**：`HostErrorCodes.cs` 超 allowed_paths。
- **R5-P2-04**：卡面计数/门禁陈述不一致（19/19 或 14 methods/19 cases、1390、AC 行、TRX）。
- **R5-P2-05**：gates.log 可审计性不足（worktree_clean_after/自我指涉说明/IPC 命令 env/TRX）。
- **R5-P2-06**：deferral 未按 r4 要求登记 owner/编号。
- **R5-P2-07**：STATUS/PLAN 指针仍 r1–r3。

## 门禁复核
fea11 40 passed；Host.Tests 102/0/49（整程序集）；Canonical+Miniter 11/11；check PASS；pins 18/18；C-17 零 diff；工作树 clean；全量 pytest/.NET 与 IPC 未复跑（gates.log 数字非 Reviewer 复跑结果）。

## done / closed_with_limitations
- done：不同意（AC3 PARTIAL）。
- closed_with_limitations：方向同意，当前 head 不满足；6 项最低返修清单（deferral 表/卡面计数/门禁日志/allowed_paths/§3.2:163 守卫与测试/收口指针）完成后可 closed_with_limitations，不 push。

## 自审声明
fresh subagent（parent session-20e77fbf），未参与实现/r1–r4；只读仓库，未修改任何文件、未 commit/push；工作树前后 clean；C-17 零 diff；pins 18/18。
