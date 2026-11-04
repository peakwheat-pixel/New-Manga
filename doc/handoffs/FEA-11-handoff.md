# FEA-11 Handoff（DSH 返修阶段 → r5 复审交接）

状态：**changes_requested（返修完成，待 r5 复审）**。Owner：DSH（ZCode/Codex 额度耗尽期间接手）；Reviewer：fresh subagent（r1/r2/r3/r4 均独立上下文）。

## 恢复点

- 仓库：`G:/CODEX/New Manga`（main）；交付基线 HEAD 见本文件提交。
- Task：`doc/tasks/FEA-11.md`（10 AC；AC11-2 MET（仅 Core seam），其余 9 项 PARTIAL 并内联原因）。
- 契约：`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md`（v1.0 FROZEN，pin 18/18）。
- Review 历史：`doc/reviews/FEA-11-r1.md`（P0=2/P1=11/P2=12）、`FEA-11-r2.md`（P0=2/P1=4/P2=10）、`FEA-11-r3.md`（P0=1/P1=6/P2=11）、r4（P0=1 deferral/P1=1/P2=13；正文由 DSH 落盘 `FEA-11-r4.md`）。
- 进度：`G:/CODEX/New Manga.workspace/FEA-10/agent-output/DSH-PROGRESS-2026-11-04.md`。

## 已完成（实施 + r1–r4 返修）

### Phase A/B（Core seam）
v8 迁移四表；`src/application/sources/*`（scanner/matcher/planner/service/runtime/model/ports/errors/identity）；`src/infrastructure/sqlite/source_sync.py`；`core_service.py` dispatch/capability/渲染去重；`core_assembly.py` 装配；`tests/fea11/*`。

### Phase C（Host/C# 与真实 IPC）
C1 `SourceOperationCoordinator`（DPAPI 原子 journal、状态机、Begin 终态保护）；C2 命令注册（15 命令、通道切分）；C3 dispatcher journal/operationJournal 路由 + HostRuntime 注入（ACK/recovery/failure 6 字段、真实 CommitReceipt digest、capability probe 门）；C4 真实 IPC 全链（new_zip：changed→pending gate→ACK→新 binding v2→源守恒）。

### r1–r4 返修
- r1：R-003 新增页 grant→binding、R-004 fail_operation SQL/recover、R-005 无页 missing 投影、R-006 relink 物理身份、R-007 全源 reference digest、R-008 COMMIT 前重验、R-010 IPC new_zip、P0-2 ACK 接线。
- r2：P1-1 回归修复（`_verify_cas` 全源）、P0-2 生产接线、Begin 终态、folder relink 防御、`_verify_fresh` 严格化。
- r3：P1-01 命令名对齐（Host↔Core）、P1-02 recovery 取 receipt、P1-03 failure 校验/终态、P1-04 capability DTO、P1-05 DAG 解环、P1-06 folder relink 拒绝。
- r4：P1-04 闭集值 + probe 门；回归测试（registry 缺失）；文档单一口径；AC11-4 承接卡；证据件（EV/Manifests）。

## 剩余（r5 前/后）

1. **r5 复审**（新上下文；reviewed_head = 本 Handoff 的 HEAD）。
2. **P0-1** Host 自签 HostAuthorization → 承接 `FEA-11-HOST-AUTH-1`（proposed；需产品显式接受 Core-only limitation 或该卡完成）。
3. **R-009** lineage 读隔离 → `FEA-11-LINEAGE-1`（禁止 done-with-limitation 的安全项）。
4. **AC11-4** 并发/DB 失败/第三区域 → `FEA-11-AC4-GAPS-1`（proposed）。
5. **AC11-3** pixel profile → `FEA-11-MATCH-1`；AC11-1 定时/watcher → `FEA-11-SCAN-1`。
6. 未清 P2：IPC flaky 定位；capability 门/聚合已补（r5 residual 返修）。

## 门禁（`verification/FEA-11/logs/dsh-C6-r6.log`）

- pytest 全量 **3051 passed / 0 failed / 10 skipped**；`tests/fea11` **40 passed**；全量 .NET **1359 passed / 0 failed / 78 skipped**（重跑确认；首次环境竞争 688/EXIT=1 已记录）；`NEWMANGA_FEA11_IPC=1` **3/3**（flaky 已记录）；check PASS；pins 18/18。
- 冻结契约/组合根/FEA-08-10 tracked 证据零 diff；未 push。
- 已知 flaky：App.Tests 全量偶发 1；IPC 在全量 .NET 之后偶发 1（复跑 3/3）。

## 交付件（AC11-10）

- `verification/FEA-11/EV.md`、`RESOURCE-MANIFEST.json`、`DELIVERY-MANIFEST.json`、`changed-files.txt`、`AC-MATRIX.md`、`logs/dsh-C6-r1..r4.log`。
- `canonical_evidence_status: pending`（待 r5 approved + 集成提交后回填）。

## 交接指令（r5 Reviewer）

> 只读 `G:/CODEX/New Manga` 的 r5 reviewed_head；按 `doc/templates/REVIEW.md` 输出报告；核对 r4 findings（P1-04 闭集/probe 门、测试、文档、交付件、P2 项）、AC 状态与 done/closed_with_limitations 意见；不得修改工作树、不得 commit/push；报告交 DSH 落盘 `doc/reviews/FEA-11-r5.md`。
