---
task_id: FEA-11
reviewer: 独立上下文子 agent（fresh subagent，parent session-20e77fbf-d068-4823-b34b-4a7a9efbd4b4）
reviewer_kind: subagent
author: DSH（Lead/Architect/Integrator；实施由 DSH 主会话接手完成）
base_commit: 3472cffd
reviewed_head: 5aadb3cd
decision: changes_requested
---

# Review：FEA-11（r1）

> 说明：本报告由 DSH 依据 Reviewer（fresh subagent）返回的审查结论落盘。Reviewer 未参与 FEA-11 实现，只读 HEAD `5aadb3cd`，diff 范围 `3472cffd..5aadb3cd`，按 `doc/templates/REVIEW.md` 输出；Reviewer 的探针/日志留在 `G:/CODEX/New Manga.workspace/FEA-11/review/`（probe_findings.py、probe_unbound_missing.py、pytest-full.log、dotnet-full.log、ipc-full.log、scratch-*）。Reviewer 返回的是摘要；以下 findings 与判定如实转录，Reviewer 原始表格未单独落盘（如需要可由 DSH 派新上下文 Review 复核）。

## 结论

**changes_requested**：P0=2、P1=11、P2=12。P0/P1 未解决前不可批准，不得进入 done。

## P0 findings

| ID | 级别 | 文件/位置 | 触发与影响 | 复现证据 | 建议 | 处理 |
|---|---|---|---|---|---|---|
| R-001 | P0 | `HostRuntime.cs:800-827`、`SourceOperationCoordinator.cs:64-107` | Host durable authorization 是空壳：Coordinator 自建 `op-` id 但不注入 Core ApplyRequest；`Authorize` 只存 `sha256(raw payload)` + `"host-session"`，未调用 `SourceAccessRegistry.Authorize`、未生成 HostAuthorization；返回 operation_id 与 Core 不一致。C-17 §3.2/§5.2 要求 Host durable 授权在先、operationId 与请求绑定 | 代码审查 | 由 Host 生成完整 HostAuthorization（host_receipt/operation/request_digest/authorization_digest/authorizations/authorized_at）并注入 ApplyRequest；Authorize 必须走 Registry 持久化授权；op id 由 Host 持久化并作为请求的一部分 | open |
| R-002 | P0 | `SourceOperationCoordinator.cs:64-107`、`HostCommandDispatcher` journal 委托 | Host ACK/recovery 未接线且实现错误：`AcknowledgeAsync` 只发 `operation_id+commit_digest`（CompletionRequest 必填 6 字段，真实 IPC 已返回 INVALID_REQUEST）；commit_digest 是 result raw text 的 sha256 而非 CommitReceipt canonical digest；Core 瞬时失败时 Host 已先落 acknowledged 且不重试；`source_get_sync_capabilities` 声明 HostLocal 但无 handler；AC-MATRIX:30 与卡 AC11-8=MET 矛盾 | 真实 IPC 复现 INVALID_REQUEST | ACK 必须以 6 字段 CompletionRequest 发送、commit_digest 用 CommitReceipt canonical digest、Core 失败不先落 acknowledged（可失败重试/恢复）、补 capability handler、修正 AC 证据矛盾 | open |

## P1 findings（关键）

| ID | 位置 | 问题 | 建议 |
|---|---|---|---|
| R-003 | `service.py:291-314` | 新增页不入 grant→binding 映射（probe 复现 SOURCE_ACCESS_DENIED） | added 决策的新页 apply 后同样 bind_imported_entry |
| R-004 | `source_sync.py:241-258` | `fail_operation` SQL 5 参数/4 占位（probe 复现 ProgrammingError）；`recover_operation` 只接受 core-committed，failed→recovered 永远 STATE_CONFLICT | 修 SQL 占位；恢复状态机允许 failed→recovered |
| R-005 | scanner diff | 未绑定旧成员被删时 scan 产出 page_id=null 的 missing DiffItem → PlanBody INVALID_REQUEST（probe 复现） | 页级投影同样过滤无页 missing（与 unchanged 一致），并补测试 |
| R-006 | relink | 只比 container digest；测试用"复制文件"也当 relink（C-17 要求物理同一） | relink 校验物理身份（identity digest），测试改真实改名/移动 |
| R-007 | scan scope | scope=current/all 只查询传入 project_ids，未捕获全源共享引用集合 | scope=all 按源的全部引用集合计算 |
| R-008 | apply | COMMIT 前未重验 grant/撤销 | 事务内/COMMIT 前重验 grant 有效与撤销代次 |
| R-009 | lineage | 只写 captured/migrated，无 native 写入、无读路径消费（AC11-5 隔离未实现） | 补 native lineage 写入与读路径消费/隔离断言 |
| R-010 | IPC 全链 | 用 old_zip（same_container）：无新 binding、无 pending gate、未读新字节（AC11-9 不成立） | 全链改用 new_zip，验证新 binding/门控/新字节/旧键不可变 |
| R-011 | AC11-4 | 缺多项目/并发/整批最后一项/撤销/DB 失败/第三区域冲突证据 | 补对应零写/CAS 测试 |
| R-012 | AC11-3 | 生产路径 new entry 不写 pixel profile，pixel 匹配实际不可达；无独立 match 测试/真实 FEA-09 旧库 fixture | 补 profile 写入与独立 match 测试/旧库 fixture |
| R-013 | 范围 | 25 个代码/测试文件超出卡内 allowed_paths（HostCommandDispatcher/HostCommandModel、identity.py、referenced/scanner.py、3 个 resource_channel 文件、tests/fea09/* 12 个、ipc support 等）；allowed 的 restart_core.py/test_source_match.py/test_source_plan.py 不存在；另有 3 个治理指针 + FEA-11-SCAN-1 卡 | DSH 逐项窄批登记（见处置记录），或扩大 allowed_paths 并复审 |

## P2 findings（摘要）

12 项（Reviewer 返回为计数与摘要级）：AC-MATRIX 与 Task 卡状态矛盾、allowed_paths 清单与实际文件不符、AC11-10 恢复 FEA-09 evidence 步骤未显式记录、App.Tests flaky 未登记、pytest 与 .NET 跳过数差异（75 vs 78，3 个 opt-in）未在证据处解释等；按 P2 处置（登记/文档修正）。

## AC 判定（Reviewer）

- AC11-2：**可接受**（有保留：需补 scope=all/新增页证据）。
- AC11-1 / AC11-7 / AC11-10：PARTIAL **可接受为 in_review**，不满足 done（AC11-1 理由两处矛盾、watcher 消费者无实现；AC11-7 诊断接线未实现且无承接；AC11-10 需迁移失败回滚证据）。
- AC11-3 / AC11-4 / AC11-5 / AC11-6 / AC11-8 / AC11-9：**MET 不成立，不可接受**（AC11-3 的 PARTIAL 理由不足——是实现缺失而非仅 fixture 缺口）。

## 门禁复核（Reviewer 独立复跑）

pytest tests/fea11 31 passed；pytest tests **3042 passed / 10 skipped / 0 failed**（235.84s）；dotnet test 全量 **1355 passed / 0 failed / 78 skipped**（3 个 opt-in IPC 被 skip，与卡上 75 差 3）；`NEWMANGA_FEA11_IPC=1` Fea11SourceIpcTests **3/3 passed**；check.ps1 PASS（2 warnings）；verify_pins.ps1 **18/18 PASS**。提醒：全量 .NET 会重写 tracked `verification/FEA-09/logs/wire-redacted.ndjson`（已知 debt）——Reviewer 跑后已 `git checkout` 恢复，最终 clean；AC11-10 的 gate 流程应显式记录该恢复步骤。

## 范围/冻结/自审

C-17 v1.0 字节零 diff（blob `9c6394bf…`、sha256 `86b89ff8…`），FEA-08/09/10 证据、App/sln、依赖均零 diff；未 push。自审边界：实现为 DSH 主会话，Reviewer 为 fresh subagent（未参与实现、只读、无 commit/push）。范围越界见 R-013。

## DSH 处置（待执行，见 Task 卡「Review r1 处置」）

按 P0 → P1 优先返修；P2 登记/defer；返修后复跑门禁并请求复审（新 reviewed_head）。
