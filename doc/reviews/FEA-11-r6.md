---
task_id: FEA-11
reviewer: 独立上下文子 agent（fresh subagent；parent session-20e77fbf-d068-4823-b34b-4a7a9efbd4b4）
reviewer_kind: subagent
author: DSH（Lead/Architect/Integrator）
base_commit: ac4b6fabc
reviewed_head: 0de62ee8a
decision: changes_requested
---

# Review：FEA-11（r6）

> 说明：本报告由 DSH 依据 r6 Reviewer（fresh subagent，未参与实现/r1–r5）返回的完整报告正文落盘（2026-11-05）。Reviewer 只读 HEAD `0de62ee8a`；审查前后工作树 clean；未修改文件、未 commit/push；未新增依赖；C-17/FEA-08-10 tracked 证据零 diff。

## 结论
**changes_requested**（对 `0de62ee8a`）。
- **P0=1**：P0-1 Host 未生成/编排完整 HostAuthorization（仍由 payload 透传；未调 SourceAccessRegistry.Authorize、无 canonical authorization_digest、operation_id 非 Host 生成）；`FEA-11-HOST-AUTH-1` 仍 proposed 且无用户显式接受 limitation → **阻断 done**。
- **P1=0**：r5 P1-04R 代码层已修（HostLocal 可达、reason 闭集、直接 await、probe 门/kind 映射成立）。
- **P2=8**：证据件/Manifests/文档在最终 HEAD 未对齐（P2-11 not-fixed）；capability/recovery receipt 无测试；N-03（AC11-1 消费者口径矛盾）/N-04（folder relink limitation 未登记）not-fixed；N-05/N-06 partial；parity 无 else、IPC flake 无失败明细。
- **done 不成立；closed_with_limitations 当前亦不成立**（需用户书面接受 P0-1 limitation + LINEAGE-1 门禁处置 + 证据/测试补齐）。

## 关键验证（独立实跑）
- `pytest tests/fea11` **40 passed**（1.07s，EXIT 0）；`pytest tests` **3051/10/0**（233.56s，EXIT 0）；check PASS（14 非终态、PLAN 80%）；pins 18/18；C-17 与 FEA-08/09/10 零 diff；changed-files 82/82 与 diff 一致。
- capability 路径静态核对（HostLocalAsync → await RunCapabilityProbeAsync；7 项 DTO；reason=capability_missing；gate/kind 映射）成立；**无自动化测试覆盖**；`source.read/1` 缺失时 reason 仍 null、CancellationToken.None、未聚合本地状态（P2）。
- P2-09：normal+recovery 均写 CommitReceiptJson，但无断言；保存的是 Operation JSON 包装；仅空 digest 分支回填（partially）。
- 交付件：EV/Manifests 的 head/sha/bytes 未在最终 HEAD 重生成（EV 仍 d0e49471、r6 log 哈希来自草稿、AC-MATRIX 哈希 ac4b 版本）；Handoff 标题/STATUS/PLAN/AC-MATRIX/Task 卡仍有 r5 口径与 1359→1360、3042→3051、31→40 等过期计数；r6 log 为人工复合摘要（无失败测试名/TRX）。
- .NET/IPC 未独立复跑（只读约束 + FEA-09 证据）；依赖 r6 log：1360/0/78；IPC 首跑 1 failed/2 passed → 复跑 3/3（如实记录，失败原因未定位）。

## AC 判定
AC11-2 MET（仅 Core seam）；其余 9 项 PARTIAL 方向诚实；但 AC11-1/AC11-6/AC11-10 登记/证据不完整（N-03/N-04/P2-11），不能据此 closeout。

## done / closed_with_limitations
- done 不成立（P0-1、LINEAGE-1 硬门禁、交付件未定稿、测试缺口、AC11-10 未完成）。
- closed_with_limitations 为唯一可行路径，前置：①用户书面接受 P0-1 Core-only limitation（或 HOST-AUTH-1 完成）；②LINEAGE-1 门禁处置（完成或明改 PLAN，并写明“UI/读路径/渲染/导出/Run 不得消费同步 binding”）；③证据在最终 HEAD 重生成并对齐；④补 capability/recovery/folder 测试；⑤AC11-10 最终 Review + DSH 集成验证。

## 处置建议（优先级）
1. 不标 done；用户决定 P0-1 limitation 与 LINEAGE-1 门禁。
2. 最终 HEAD 重生成 EV/Manifests/changed-files/Handoff/STATUS/PLAN/AC-MATRIX/Task 卡并在证据提交说明中标注 evidence_commit。
3. 补最小回归测试（capability 7 项/reason、recovery receipt、folder relink、parity else/dispatch）；IPC flake 保留失败名/TRX 或登记 limitation。
4. 修 N-03（AC11-1 口径统一）/N-04（folder relink limitation 入 AC11-6/矩阵）/N-05（窄批 allowed_paths 权威位置）。
5. capability 语义收口（reason 非空、聚合本地状态、用请求 token）。
