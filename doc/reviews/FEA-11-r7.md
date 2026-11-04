---
task_id: FEA-11
reviewer: fresh subagent（r7 独立上下文；parent session-20e77fbf-d068-4823-b34b-4a7a9efbd4b4；未参与实现/r1–r6）
reviewer_kind: subagent
author: DSH（Lead/Architect/Integrator）
base_commit: 0de62ee8a
reviewed_head: 85fa1da14
decision: changes_requested
---

# Review：FEA-11（r7）

> 说明：本报告由 DSH 依据 r7 Reviewer（fresh subagent，未参与实现/r1–r6）返回的完整报告正文落盘（2026-11-05）。Reviewer 只读 HEAD `85fa1da14`；审查前后工作树 clean；未改任何 tracked 文件；仅写仓外 `workspace/FEA-11/r7-review-probe/`；C-17/FEA-08-10 tracked 证据零 diff。

## 结论
**changes_requested**：P0=1、P1=0、P2=9。
- **P0-1 未闭合**：Host 仍从 payload 透传 `operation_id`/`authorization`（HostRuntime.cs:833/842-855/878），未调 `SourceAccessRegistry.Authorize`、无 canonical `authorization_digest`；`FEA-11-HOST-AUTH-1` 仍 proposed；**全仓无用户书面接受 Core-only limitation 记录** → 阻断 done 与 closed_with_limitations。
- r5 P1-04R 保持 fixed；r7 diff 仅文档/证据 8 文件，**无 src/tests 变更** → r6 的代码/测试类 finding 不可能在此 head 闭合。

## 关键独立验证
- `pytest tests/fea11` **40 passed**（1.07s，EXIT 0）；`pytest tests` **3051/10/0**（237.37s，EXIT 0，与 r7 log 一致）。
- check PASS（14 非终态、PLAN 80%）；pins 18/18；冻结契约/FEA-08-10 零 diff。
- 交付件：RESOURCE 13/13 sha/bytes 与实文件一致；changed-files 83/83 与 `3472cffd..3e675de59` 一致；DELIVERY `delivery_head=3e675de59` + evidence_note 诚实。**但 r7 log 未入 EV/RESOURCE/DELIVERY**；Handoff/STATUS/PLAN/AC-MATRIX/Task 卡仍 r5 口径；计数 1360/3051/40 未统一（1360 仅出现在日志）；Task 卡 `delivery_head: null`、EV pin 过期。
- IPC：4 次独立复跑均 3/3（EXIT 0），未复现首跑 flake；r7 log 的失败名在类名前缀处截断、无错误/TRX → 不能作为“已定位失败名”的证据。
- 全量 .NET NOT_RUN（只读约束 + FEA-09 证据），r7 log 1360/0/78 经算术核对（21+38+253+117+83+31+146+671=1360）。

## Findings
| ID | 级别 | 位置 | 问题 | 建议 | 状态 |
|---|---|---|---|---|---|
| R7-01 | P0 | HostRuntime.cs:833/842-855/878；SourceOperationCoordinator.cs:120；HOST-AUTH-1 | Host 未生成/编排 canonical HostAuthorization（operation_id/authorization 透传；无 Registry.Authorize/canonical digest）；无用户接受 → 阻断 done | 完成 HOST-AUTH-1 或取得用户书面 limitation 接受并落盘 | open |
| R7-02 | P2 | Handoff/STATUS/PLAN/AC-MATRIX/Task/EV/RESOURCE/DELIVERY | r7 log 未入证据索引；文档仍 r5 口径；计数 1360/3051/40 未统一；Task delivery_head null、EV pin 过期 | 最终 HEAD 重生成并统一 | partially |
| R7-03 | P2 | SourceOperationTests/Coordinator/Fea11SourceIpcTests | CommitReceipt normal+recovery 无测试 | 补断言 | open |
| R7-04 | P2 | HostRuntime.cs:958-1005 | capability 7 项 DTO/reason/聚合无测试；source.read/1 缺失时 reason null；CancellationToken.None | 补测试并收口语义 | open |
| R7-05 | P2 | service.py:467-478；test_source_relink.py | folder relink typed 拒绝无测试（N-04 仅文档） | 补用例 | open |
| R7-06 | P2 | Task:103/139/165/236；SCAN-1:41；AC-MATRIX:23；EV:7 | AC11-1 口径与 2026-11-04 DSH 裁决/SCAN-1 卡/r1 矛盾，误归因；无 watcher 实现 | 按 DSH 裁决重新统一 AC11-1 | open |
| R7-07 | P2 | Task:216-222 | 窄批权威节漏 5 个路径（含 test_core_service.py、test_source_command_parity.py） | 补齐 | open |
| R7-08 | P2 | test_source_command_parity.py | 纯静态解析、无 else、不验证 dispatch | 加强 | open |
| R7-09 | P2 | dsh-C6-r7.log | IPC 失败名截断、无 TRX；提交信息过度声明 | 保留 TRX 或登记 flake limitation | partially |
| R7-10 | P2 | Task:171；AC-MATRIX:29 | AC11-7 PARTIAL 无承接/limitation 登记 | 补登记 | open |

## AC 判定
AC11-2 MET（仅 Core seam）；其余 9 项 PARTIAL 方向基本诚实；AC11-1 口径/归因问题、AC11-10 交付件未定稿；未发现把未执行项标 MET。

## done / closed_with_limitations
- **done：不同意**（P0-1、LINEAGE-1 硬门禁、AC11-10 未终版、测试缺口）。
- **closed_with_limitations：唯一可行终态，但当前不成立**，前置：①用户书面接受 P0-1 Core-only limitation（或 HOST-AUTH-1 done）并落盘；②LINEAGE-1 门禁处置（完成或明改 PLAN，写明 UI/读路径/渲染/导出/Run 不得消费同步 binding）；③证据在最终 HEAD 重生成（含 r7 log）并统一计数；④补 recovery/capability/folder/parity 测试；⑤N-03/N-05 修正；⑥IPC flake 记录或登记。

## 建议
不要在本 head 重复 r7；待 DSH 完成 P0-1/LINEAGE-1 用户裁决与证据/测试收口后，用新 head 派 r8；若走 closed_with_limitations，必须把用户书面接受、limitation 清单与“UI/读路径不得消费同步 binding”写入 PLAN/Closeout/Task 并保留字节。

## 自审声明
fresh subagent（parent session-20e77fbf），未参与实现/r1–r6；只读仓库，未修改/commit/push；工作树前后 clean；未触碰真实用户数据/AppData/外部卷/回收站；未新增依赖。
