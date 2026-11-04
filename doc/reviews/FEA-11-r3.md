---
task_id: FEA-11
reviewer: 独立上下文子 agent（fresh subagent，parent session-20e77fbf-d068-4823-b34b-4a7a9efbd4b4）
reviewer_kind: subagent
author: DSH（Lead/Architect/Integrator）
base_commit: 44059968
reviewed_head: 00a1c27b
decision: changes_requested
---

# Review：FEA-11（r3）

> 说明：本报告由 DSH 依据 r3 Reviewer（fresh subagent，未参与实现/r1/r2）返回的完整报告正文落盘（2026-11-05）。Reviewer 只读 HEAD `00a1c27ba`，diff `44059968..00a1c27b`；工作树复核前后 clean；探针/日志在 `workspace/FEA-11/review-r3/`。

## 结论
**changes_requested**：P0=1（r2 P0-1 未闭合，deferral-accepted 但阻断 done）、P1=6（新发现/未闭合）、P2=11。两个关键返修（P1-1 共享源 stale 回归、P0-2 ACK 指挥面路由）独立验证**成立**；但生产 Host 面存在命令断链与恢复/终态缺陷，AC-MATRIX 与 Task 卡互相矛盾，承接 DAG 有环。

## r2 findings 处置核对
- fixed：P1-1（probe：`APPLY OK: state=core-committed`，full digest ≠ scoped）、P0-2 ACK 路由（dispatcher 优先 `_operationJournal`；`SourceSyncJournalTests` 9/9）、P2-9（`_verify_fresh` 集合相等）。
- partially：P1-2（AC11-9 已降级但证据仍不成立）、P1-3（AC11-4 降级但缺口无承接）、P2-6（Begin 已保护但 MarkFailed 可回退）、P2-8（folder relink 从 AttributeError 变为静默跳过）。
- not-fixed：P0-1（Host 自签授权）、P1-4（lineage 读隔离）。

## r3 新发现
- **P1-01**：生产 Host→Core 有 6 条 source 命令断链——Host CoreBindings 用 CamelCase（PlanSourceSync/Preview/Confirm/Invalidate/Get/Cancel），Core 应用通道只注册小写；经 Host 走 plan 生命周期/query 均 UNKNOWN_COMMAND，UI 无法走通同步流程。IPC 全链直连 Core 掩盖断链。
- **P1-02**：ACK/recovery 崩溃窗不可恢复——host-authorized（Core 已 COMMIT、Host 未 MarkCommitted）时 commit_digest 空，RecoverAsync 发空 digest 被 Core INVALID_REQUEST；AcknowledgeAsync 又要求 core-committed → 两边走不通。
- **P1-03**：MarkFailed 无状态守卫（acknowledged/recovered 可回退 failed）；Host 先 MarkFailed 再原样转发 Core，缺字段/状态不符时分叉。
- **P1-04**：`source_get_sync_capabilities` DTO 非 §5.2 契约（应 7 项 Capability），且无 capability 探针门（旧 Core 下会先建 journal 再被拒）。
- **P1-05**：承接 DAG 环——PLAN“LINEAGE-1 完成前 FEA-11 不得 done” + 承接卡 depends_on FEA-11 → 死锁。
- **P1-06**：folder relink 跳过物理身份校验（container_facts=None → 静默放行），回归 R-006 目标。

## P2（11 项）
AC-MATRIX 与卡矛盾（AC11-5/8 矩阵仍 MET）；卡正文过期；PLAN 行尾多列/仍写 ready/80% 预算；allowed_paths 未覆盖 r3 diff；承接卡 allowed_paths（exporting 不存在）；缺测试（P2-9/folder/Begin 竞态）；r2 报告未入库；r3 日志信息不足；Host 提交后仅核对 commit_digest；App.Tests/IPC flaky 未说明；AC11-4 无承接卡。

## AC 状态复核
AC11-2 仅 Core seam；AC11-5/8 矩阵应 PARTIAL；其余维持 PARTIAL；**in_review→done 不满足**。

## 承接裁决意见
HOST-AUTH-1 可接受（有条件，并接受为 P0-1 闭合路径）；LINEAGE-1 范围/AC 可接受但当前形式（DAG 环/exporting 路径）不可接受；MATCH-1/SCAN-1 可接受；AC11-4 无承接卡不可接受；lineage gate 方向正确但表述不可执行（需解环）。

## 门禁复核
pytest tests/fea11 37 passed；pytest tests 全量 3048/10/0（239.93s）；check PASS；pins 18/18；过滤 SourceSyncJournalTests 9/9、SourceOperationTests 5/5；全量 .NET/IPC 未跑（只读约束）；工作树 clean；C-17 零 diff。

## 对 done 的意见
不同意 done；closed_with_limitations 亦不同意（最低前置：P1-01/02/03 修复、P1-04/06 修或登记、P1-05 解环、P2-01 承接、文档一致性、AC11-10 EV/Handoff/Resource Manifest 终版）。limitation 清单至少含 AC11-1/3/4/5/6/7/8/9 各项，并明确“LINEAGE-1 前任何 UI/读路径不得消费同步 binding”。
