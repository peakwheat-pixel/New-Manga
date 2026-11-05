---
task_id: FEA-11-HOST-AUTH-1
reviewer: 独立上下文 fresh subagent（DSH 派发；parent session-20e77fbf-d068-4823-b34b-4a7a9efbd4b4；未参与实现与 r1/r2 审查）
reviewer_kind: subagent
author: DSH（Lead/Architect/Integrator；本卡实施）
base_commit: 7ab9eea87
reviewed_head: 74da4f230
decision: changes_requested
---

# Review：FEA-11-HOST-AUTH-1（r3）

> 本报告由 DSH 依据 r3 Reviewer 返回的完整报告正文落盘（2026-11-05）。Reviewer 只读 HEAD `74da4f230`；diff `dbd3069a2..HEAD`；工作树审查前后 clean；C-17 零 diff；无依赖变更；未 push。

## 结论
**changes_requested**：P0=0、P1=1、P2=9。有效顺序探针（R2-P2-01）已真正修复、输入严格化大部分成立；但 R2-P1-01 未完全闭合：typed 预提交白名单漏 `SOURCE_GRANT_EXPIRED`/`FILE_IDENTITY_CHANGED` 等（会被改写成 CORE_UNAVAILABLE 且留 host-authorized）；`retryable:false` 硬编码与 §8 逐 code 语义冲突；同 op/request digest 重试缺失且仅「待后续」。主体设计成立，无 P0 安全洞。

## AC 判定
- **AC1 MET**（4 + 3 个固定向量经 Python 独立复算一致）。
- **AC2 MET**（六字段/排序/canonical/注入；identity_digest 由 Core 复核属既有分工）。
- **AC3 PARTIAL**（顺序探针有效；typed 覆盖不足/retryable 错/同 op 重试缺失；e2e/ACK 重发/崩溃点可 L-8/L-9 limitation）。
- **AC4 PARTIAL**（用户接受的是 FEA-11 L-1，非 AC4 原文「r3 接受」；r3 未 approved）。

## Findings（摘要）
- **R3-P1-01（P1）**：(a) 白名单漏 code（SOURCE_GRANT_EXPIRED/FILE_IDENTITY_CHANGED 等）；(b) retryable 硬编码 false；(c) 同 op 重试缺失（C-17 §3.2 行 163），需实现或用户显式接受；(d) 用例缺口。
- P2-01 输入残余（plan_id 规则、grant_ids 重复/上限、未知字段静默丢弃）。
- P2-02 registry scope（全部 roots/同义反复）、多 registry 非原子、Begin 在 Authorize 之后（与 §3.2 转移表差异）。
- P2-03 receipt 核对/形状缺失（operation_id/request_digest/state/authorizations 未核对、commit_digest 未重算、CommitReceipt 形状不符）。
- P2-04 证据卫生（gates.log 旧 head/无失败 TRX、worktree_clean 未解释、卡计数过期）。
- P2-05 治理指针（STATUS/PLAN ready、reviewer 指 r1）。
- P2-06 MarkFailed 默认允许 null error_code 且可从 core-committed 直接 failed。
- P2-07 歧义 op id 只在文本 message、测试断言过弱、无 inner exception。
- P2-08 Minter 排序 ordinal（当前不可达）、P2-09 journal 时间戳未 Invariant（pre-existing）。

## 门禁复核（独立）
fea11 40 passed；Fea11HostAuthTests 7/7；Minter+Canonical 10/10；全量 .NET 首跑 App.Tests 1 failed（`FluentResidual2VisualEvidenceTests`，因 CoreClient WireLogSourceRedactionTests 写 tracked FEA-09 的跨 assembly 顺序 race，非本卡引入；已 checkout 恢复）；check PASS；pins 18/18；C-17 零 diff；工作树 clean；IPC 未重跑（Core 直连，非 Host e2e）。

## limitation 意见
- e2e/ACK 重发/崩溃点自动化 → 可接受（须引用 L-8/L-9，且 IPC 3/3 不是 Host e2e）。
- ACK fresh 授权 → 可接受（Core `_verify_fresh` 托底）。
- CommitReceipt canonical 重算 → 有条件可接受（须正式登记 owner）。
- **同 op 重试 → 当前不可自动接受**（需实现或用户显式接受）。

## done / closed_with_limitations
- done：不同意（AC3/AC4 PARTIAL）。
- closed_with_limitations：当前 head 不能无条件成立；前置：R3-P1-01(a)(b) 修、同 op 重试实现或用户接受、limitation 正式化、证据/治理 P2 收口。

## 自审声明
fresh subagent（parent session-20e77fbf），未参与实现/r1/r2；只读仓库；未 commit/push；未改冻结 C-17 字节；全量 .NET 后已 checkout 恢复 FEA-09；工作树 clean。
