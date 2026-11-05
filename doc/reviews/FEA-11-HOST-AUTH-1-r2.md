---
task_id: FEA-11-HOST-AUTH-1
reviewer: 独立上下文 fresh subagent（DSH 派发；parent session-20e77fbf-d068-4823-b34b-4a7a9efbd4b4；未参与实现与 r1 审查）
reviewer_kind: subagent
author: DSH（Lead/Architect/Integrator；本卡实施）
base_commit: 7ab9eea87
reviewed_head: dbd3069a2
decision: changes_requested
---

# Review：FEA-11-HOST-AUTH-1（r2）

> 本报告由 DSH 依据 r2 Reviewer 返回的完整报告正文落盘（2026-11-05）。Reviewer 只读 HEAD `dbd3069a2`；diff `7ab9eea87..dbd3069a2`（r1 后增量 `24a0bbca..dbd3069a2`）；工作树审查前后 clean；C-17 零 diff；无依赖变更；未 push。

## 结论
**changes_requested**：P0=0、P1=1、P2=10。方向与主体实现成立（Host 真正自签六字段/operation_id 注入/Registry durable 先于 Core；canonical 摘要经独立复算 7 个全部一致）。r1 P1-2 scope/元数据部分已修；**P1-1 仅部分修复**：非法 digest 零 journal 已补，但失败-重试语义未闭合，且顺序探针为空断言。

## AC 判定
- **AC1 MET**（canonical 4 向量独立复算一致；缺 non-BMP/控制字符专项向量，不改判）。
- **AC2 MET**（六字段/排序/digest/注入；固定 id 外部向量一致；identity_digest 由调用方提供、Core 复核属既有分工）。
- **AC3 PARTIAL**（顺序代码正确；顺序断言无效；typed 预提交失败不落 failed/error_code/retryable；新 op id 重试与 C-17 §3.2 行 163 冲突；e2e/ACK 重发/崩溃点自动化可接受为 L-8/L-9 limitation）。
- **AC4 PARTIAL**（用户 limitation 依据是 `FEA-11-r7-acceptance.md` L-1，非 AC4 原文「r3 复审接受」；措辞应改引 r7 裁决）。

## 关键 findings
- **R2-P1-01（P1）**：失败-重试语义与 C-17 §3.2 不一致（typed 失败留 host-authorized、无 error_code/retryable；同 op 重试未实现；失败不暴露 operation_id → dangling journal/pending gate 风险）。**不在 e2e/ACK/崩溃点 limitation 内**。
- **R2-P2-01（P2）**：顺序探针空断言（Register 已设 LastUsedAt；删除 Authorize 仍通过）。
- **R2-P2-02（P2）**：输入 fail-closed 残余（plan_digest 零值回退、grant_ids 静默、generation 未包装、plan_id/identity_digest 未校验）。
- **R2-P2-03（P2）**：registry roots scope 同义反复、多 registry 非原子、Begin 顺序与 §3.2 转移表差异。
- **R2-P2-04（P2）**：P2-6 语义缺口（error_code/retryable、CommitReceipt 重算）非「形状」。
- **R2-P2-05（P2）**：P2-7 ACK fresh 授权需正式 limitation（Core `_verify_fresh` 托底）。
- **R2-P2-06（P2）**：证据卫生（gates.log HEAD 旧、TRX 未入库、计数 stale）。
- **R2-P2-07（P2）**：治理指针（STATUS/PLAN 仍 ready；卡 reviewer 指 r1）。
- P2-9/P2-10/P2-2：记录/deferral 可接受。

## DSH 裁决评估
- AC3 e2e/ACK 重发/崩溃点 → limitation：可接受（须引用 L-8/L-9，且不得用 IPC 3/3 当 Host e2e 证据）。
- P2-6 形状：部分可接受（内部编码），但缺 error_code/retryable/CommitReceipt 属语义缺口需修或登记。
- P2-7 ACK fresh：有条件可接受（须写明契约偏差 + owner，不能只说「不改变安全边界」）。
- P2-8/9/10：测试债务可接受，但失败 TRX 归档与最终 head 证据须在集成前闭环。

## 门禁复核（独立）
fea11 40 passed；pytest 全量 3051/10/0；CoreClient 过滤 10 passed；Fea11HostAuthTests 5 passed；IPC 3/3 首跑（Core 直连非 Host e2e）；check PASS；pins 18/18；C-17 零 diff；工作树 clean；全量 .NET NOT_RUN（避免重写 FEA-09）。

## done / closed_with_limitations
- done：不同意（AC3/AC4 PARTIAL）。
- closed_with_limitations：当前 head 不能无条件成立——e2e/ACK/崩溃点可由 L-8/L-9 承接，但 **R2-P1-01 不在其中**；须修复或作为新的用户接受 limitation 正式登记；顺序断言须有效。建议返修顺序：P1（失败语义/重试/disclose op id/有效顺序断言）→ P2 输入 → P2 处置 → 证据/治理 → 新 head 派 r3。

## 自审声明
fresh subagent（parent session-20e77fbf），未参与实现/r1；只读仓库，未修改 tracked 文件、未 commit/push；未运行全量 .NET（避免重写 FEA-09）；工作树前后 clean。
