---
task_id: FEA-11
reviewer: 独立上下文子 agent（fresh subagent，parent session-20e77fbf-d068-4823-b34b-4a7a9efbd4b4）
reviewer_kind: subagent
author: DSH（Lead/Architect/Integrator）
base_commit: 5aadb3cd
reviewed_head: 44059968
decision: changes_requested
---

# Review：FEA-11（r2）

> 说明：本报告由 DSH 依据 r2 Reviewer（fresh subagent，未参与实现/r1）返回的完整报告正文落盘（2026-11-05）。Reviewer 只读 HEAD `44059968`，diff `5aadb3cd..44059968`；工作树复核前后 clean；探针/日志在 `workspace/FEA-11/review-r2/`。

## 结论
**changes_requested（P0=2 / P1=4 / P2=10）**。r1 13 条 P0/P1：5 fixed（R-003/4/5/6/8）、5 partially（R-002/7/10/11/13）、R-012 deferral-accepted、R-001 deferral-rejected（不可作 done 依据）、R-009 deferral 仅任务拆分；**新回归 P1-1**（R-007 宇宙不一致 → 共享源 scope=current apply 必 stale）。

## P0
- **P0-1（R-001）**：Host 仍不自签 HostAuthorization、不写 Registry durable authorization；operation_id/authorization 由调用方提供，Host 仅 journal 后透传。承接 HOST-AUTH-1 作为返修计划可接受，作为 done 依据不可接受。
- **P0-2（R-002）**：ACK/recovery 方法体已修（6 字段、真实 CommitReceipt digest、Core 成功后才落 acknowledged），但**未接生产命令面**（三命令仍直通 Core；`SourceSyncJournalTests.cs:44-48` 断言 ACK 不被 journal 包装）；capability handler 缺失；6 字段 ACK 成功路径无测试。

## P1
- **P1-1（新回归，最重要）**：scanner 全源 `reference_set_digest` 与 `service._verify_cas` 的 project-scoped 重算不一致 → 共享源 + scope=current 的合法 apply 永远 stale（probe：full 4be8644f… vs scoped b44b6d2f…）。
- **P1-2（AC11-9）**：IPC 为 Core 直连，未走 HostRuntime/dispatcher；无 pre-sync 旧 binding/旧键不可变断言 → MET 不诚实。
- **P1-3（AC11-4）**：缺并发 apply、DB 失败、第三区域 BaseRevisionId 冲突 → MET 不成立。
- **P1-4（AC11-5）**：lineage 只写不读、regions 不隔离；LINEAGE-1 作为任务拆分可接受，AC11-5 不可 done-with-limitation。

## P2（10 项摘要）
AC-MATRIX 陈旧（3042/31/75、AC11-5/8 仍 MET）；卡内状态矛盾；allowed_paths 列不存在文件；证据日志无命令/EXIT/恢复步骤；IPC flake 未定位；Begin 覆盖 acknowledged；folder relink AttributeError；`_verify_fresh` 校验不全；R-003/R-005/R-008 无仓库内回归测试；承接卡未进 PLAN。

## 门禁复核
pytest tests/fea11 36 passed；pytest tests 全量 3047/10/0（239.81s）；check PASS；pins 18/18；IPC 3/3；全量 .NET NOT_RUN（只读约束）；工作树 clean。

## 对 done 的意见
不同意 done。可接受 done-with-limitation 仅限 AC11-1（SCAN-1）、AC11-3（MATCH-1）、AC11-7（读投影/UI），且需承接进 PLAN + Closeout limitation + 产品方接受；AC11-5（安全隔离）、AC11-8（P0）、AC11-9（证据）不可。
