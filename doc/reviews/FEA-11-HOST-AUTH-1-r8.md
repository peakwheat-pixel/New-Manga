---
task_id: FEA-11-HOST-AUTH-1
reviewer: 独立上下文 fresh subagent（DSH 派发；parent session-20e77fbf-d068-4823-b34b-4a7a9efbd4b4；未参与实现与 r1–r7 审查）
reviewer_kind: subagent
author: DSH（Lead/Architect/Integrator；本卡实施）
base_commit: 7ab9eea87
reviewed_head: cbd561b432f73bce3308d68366f79f408cee000a
decision: approved
---

# Review：FEA-11-HOST-AUTH-1（r8）

> 本报告由 DSH 依据 r8 Reviewer 返回的完整报告正文落盘（2026-11-05）。Reviewer 只读 HEAD `cbd561b4`；diff `04954d20..HEAD`；工作树审查前后 clean；C-17 零 diff；pins 18/18；未 push。

## 结论
**approved：P0=0 / P1=0 / P2=0 / P3=5。** r7 两个 P2 已实质处置：R7-P2-01 两条守卫用例已补（24/24，19 方法；用例 1 真判别，用例 2 行为正确但非单点判别，残留 P3）；R7-P2-02 卡面 24/24 与 AC4 行已更新。R7-P3-01 部分处置；**R7-P3-02 未实际修复**（卡面行 52 原文未变）。AC3 仍 PARTIAL，故 **不同意 done，同意 closed_with_limitations**；closed_with_limitations 须按 `doc/09_COLLABORATION.md:79` 由用户明确裁决，保留 AC3/AC4 原始状态与 limitation，不得改写为 PASS。

## AC 判定
- **AC1 MET**（5/5；request_digest 公式与 C-17:26 一致；non-BMP）。
- **AC2 MET**（6/6；Apply 注入）。
- **AC3 PARTIAL**（顺序/typed 失败/failed+error_code/歧义/retry fresh auth/kind+digest+CommitDigest 守卫/capability 门 24/24；缺 ACK 重发/崩溃点矩阵、HostRuntime e2e、dispatcher retry 命令、receipt 核对）。
- **AC4 MET（路径层）**（`FEA-11-r3.md:38` 逐字一致）。

## 门禁复核（r8 实跑）
fea11 **40 passed**；Fea11HostAuthTests **24/24（19 方法）**；Canonical+Minter **11/11**；Host.Tests **107/0/49**；全量 .NET **1395/0/78**；check PASS（2 warnings）；pins 18/18；C-17 零 diff；IPC 首次 **2/3**（`ScanWithAHostIssuedGrant_WorksEndToEnd`，未捕获详情）/单独 1/1/随后 5×3/3 → flake 观察；工作树前后 clean。

## P3 残留
- **R8-P3-01**：R7-P3-02 未修复（卡面行 52 仍「当前为透传实现」）；closure 记录须如实注明。
- **R8-P3-02**：reviewer 仍 r1–r6；STATUS/PLAN 仍「r1–r6」；AC4 行未记 r7=changes_requested。
- **R8-P3-03**：gates.log 1393 是 r7 Reviewer 记录（非当前 HEAD）；当前 HEAD 1395/0/78 未入 log；24/24 无 command/EXIT；IPC flake 口径需保留。
- **R8-P3-04**：R7-P2-01 用例 2 不单点判别（`:324-327` 未覆盖）；不影响公共行为。
- **R8-P3-05**：卡面行 61 仍写「R7-P2-01 守卫补测（已补测）登记 deferral」，自相矛盾。

## done / closed_with_limitations
- done：不同意（AC3 PARTIAL）。
- **closed_with_limitations：同意（附条件）**。须用户明确裁决；closure 记录保留 AC3 PARTIAL 与 limitation，不得改写为 PASS，不得进入 READY DAG；closure commit 内修正 R8-P3-01/02 并如实记录。

## Limitation 清单（10 项，closure 确认）
1. HostRuntime→Core 真实 sidecar + dispatcher 接线 e2e 未自动化（IPC 为 Core 直连）。
2. ACK 重发/崩溃点矩阵（C-17 §3.3）未自动化。
3. retry 仅为 Host 编排 API（dispatcher 无冻结 retry 命令，UI/命令面不可达）。
4. Host 侧 plan 有效性预检未实现（依赖 Core `take_confirmed` 事务内 fail-closed，R6-P2-01）。
5. ACK/recovery 前 receipt 核对与 CommitReceipt canonical 重算未实现（R4-P2-03）。
6. Host 输入规则精度未收口（R4-P2-01）。
7. Registry scope/多 registry 原子性/Begin 与 Authorize 顺序崩溃窗口（R4-P2-02）。
8. 分类精度：黑名单含未产出码、typed 歧义分支用例（R4-P2-07）。
9. `source.read/1` 缺失时 capability item reason 语义（R6 P2-4）。
10. R7-P2-01 用例 2 判别力残留/R8-P3 文档指针/证据待收口。

## 自审声明
fresh subagent（parent session-20e77fbf），未参与实现/r1–r7；只读仓库；未 commit/push；全量 .NET 后恢复 FEA-09；最终工作树 clean。
