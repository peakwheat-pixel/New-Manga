---
id: FEA-11-AC4-GAPS-1
title: FEA-11 AC11-4 证据收口（并发 apply / DB 失败 / 第三区域 / 漂移矩阵与全表零写）
kind: implementation
governance_version: 3
status: in_review
approval: scope 已按 ZCode SCOPE-ADJ-2026-11-05 冻结，待 Lead（DSH）释放；承接 FEA-11 r7-acceptance L-5 与 AC11-4 证据缺口；释放时由 DSH 固定 base_commit、Owner 与上下文独立 Reviewer；**DSH 2026-11-05 释放（ready）**：ZCode SCOPE-ADJ 裁决已冻结范围；Owner 待派发；test-only；**2026-11-05 实施交付（in_review）**：Owner=`scanner-gaps-impl`（DSH Agent Teams），交付 head `95815ff7a`，AC1–AC4 MET、AC5 PARTIAL（独立 Review/负向探针待执行）；Reviewer 待 Review Appointment
suggested_owner: codex
owner: scanner-gaps-impl（DSH Agent Teams 成员；Lead `lead`）
reviewer: null   # 待 DSH Review Appointment：独立上下文 fresh subagent，未参与实现
depends_on:
  - FEA-11
base_commit: 51e139eff   # 释放点 main head（CORE closeout 后）
branch: null
worktree: null
integration_commit: null
delivery_head: 95815ff7a
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/FEA-11-AC4-GAPS-1
allowed_paths:
  - doc/tasks/FEA-11-AC4-GAPS-1.md
  - doc/reviews/FEA-11-AC4-GAPS-1-*.md
  - doc/handoffs/FEA-11-AC4-GAPS-1-*.md
  - verification/FEA-11-AC4-GAPS-1/**
  - tests/fea11/test_source_sync.py
  - tests/fea11/test_source_sync_storage.py
out_of_scope:
  - 任何 src 行为变更：service.py typed 映射、plan-time migrate revision 校验、grant 移入事务、跨实例 same-op replay
  - 契约/wire/schema：C-17/C-13/C-15/C-16/M2-C1 rev 2.13 字节、v8 DDL、错误闭集、命令表
  - Host/Avalonia/UI/FEA-12-UI；真实 IPC/HostRuntime 端到端（FEA-11 L-9）
  - 逐崩溃点杀进程矩阵、ACK/recovery 自动化（FEA-11/HOST-AUTH-1 残余 limitation）
  - AC11-3 匹配（FEA-11-MATCH-1）、AC11-1 定时/watcher（FEA-11-SCAN-1）、AC11-5（LINEAGE-1 done）、AC11-6/7
  - 拒绝审计写（C-17 §6.2 明文禁止；见 G12）；新依赖；真实用户数据/AppData/外部卷/回收站；push
---

# FEA-11-AC4-GAPS-1：AC11-4 证据收口

> **状态：`in_review`（2026-11-05 交付，Owner=`scanner-gaps-impl`，交付 head `95815ff7a`）。** 本卡 **test-only**：零 `src/**`、契约、schema 变更。AC1–AC4 已 MET（19 个新增用例 + 16 表零写比较集 + 门禁日志），AC5 PARTIAL（独立上下文 Review 与负向探针待 Reviewer 执行；`.NET` NOT_RUN）。AC11-4 是否 MET 由 Lead/Review 判定，本卡不自行宣告。
>
> 边界：本卡 **test-only**（只写测试与证据，不改 `src/**`、契约、schema）。范围事实基线：`main@604a2d343`（scope review 基线）；交付基线 `51e139eff`（main head `d8049fe6e`）。

## 来源与目标

- 承接链：`doc/tasks/FEA-11.md:106`（AC11-4 正文）→ `doc/reviews/FEA-11-r1.md:38`（R-011）→ r2 P1-3 → r4 P2 → `doc/reviews/FEA-11-r7-acceptance.md:22`（L-5：并发 apply / DB 失败 / 第三区域 BaseRevision 冲突证据缺失）；`verification/FEA-11/AC-MATRIX.md:26` 现状口径。
- 冻结依据：`G:\CODEX\New Manga.workspace\FEA-11\scope-review\FEA-11-AC4-GAPS-1-scope.md`（独立只读 scope review）+ ZCode SCOPE-ADJ-2026-11-05 裁决（Lead 2026-11-05 下发；含每卡必改项）。
- 目标（一个可观察交付）：AC11-4 的 **G1–G11 全部证据** 以判别性测试落盘——并发 apply（same-op replay / different-op typed / 双连接）、DB 失败注入整批回滚、第三区域双分支、五类漂移 + 授权失联 + 多项目末项 + 全表零写比较集；**零 src/契约/schema 变更**。G12（拒绝审计）按 C-17 §6.2 明文禁止，非缺口。
- 已具备能力（不得重做）：绑定漂移 11 表零写（`tests/fea11/test_source_scan.py:257-339`）、单项目末项回滚（`tests/fea11/test_source_sync.py:371-399`）、多项目 scope=all 无写（`:331-368`）、apply 前撤销 grant typed 拒绝零写（`:402-430`）、同 op 重放返回原 receipt（`:79-148`）、CAS/事务骨架（`src/application/sources/service.py:217-293`、`:358-426`）。

## Scope（冻结）

### In

| # | 范围 | 说明 |
|---|---|---|
| I1 | AC1 并发 apply | 同实例两线程 same-op / different-op + 两独立 stack/连接（文件 DB）；`恰好一次业务提交`；失败方 typed + 零业务写 |
| I2 | AC2 DB 失败注入 | 事务中途 + 最后一步整批回滚、plan 状态/重试；AC2-c wire 级 `SOURCE_SYNC_STORAGE_FAILED` 证据（新文件 `tests/fea11/test_source_sync_storage.py`） |
| I3 | AC3 第三区域双分支 | plan 自带过期 migrate revision → `STALE_BASE_REVISION`；现实漂移 → `SOURCE_PLAN_STALE(cause=manual)` |
| I4 | AC4 漂移矩阵 + 全表零写 | G4–G11（源/版本行/引用集合/决定/授权 generation/授权 EOF/人工 revision/保护/draft/Run/多项目末项/比较集） |
| I5 | AC5 证据/范围/门禁 | AC-MATRIX/EV/RESOURCE-MANIFEST/DELIVERY-MANIFEST/changed-files/logs；check/pins；独立 Review + 负向探针；`.NET NOT_RUN` 口径 |
| I6 | 测试装置 | 文件 DB + 两连接、SQLite trigger 注入、事件/屏障编排、`_full_snapshot` 助手；全部在 `tests/fea11/test_source_sync.py`（及新 storage 测试文件）本地实现 |

### Out

- 任何 **src 行为变更**：service 层未知异常包装、plan-time `migrate_revision_ids` ownership/current 校验、`_bind_operation_grant` 移入事务、跨实例 same-op replay（replay 检查移入事务）——均属行为变更，需另案裁决。
- 契约/wire/schema：C-17/C-13/C-15/C-16/M2-C1 rev 2.13 字节、v8 DDL、错误闭集、命令表；不新增命令/DTO/字段/表/迁移。
- Host/Avalonia/UI/FEA-12-UI；真实 IPC/HostRuntime 端到端；逐崩溃点杀进程矩阵；ACK/recovery 自动化。
- 拒绝审计落盘（C-17 §6.2 明文“不创建拒绝 receipt”）；真实用户数据；push；新依赖。

### 卡内冻结口径（防止实施歧义）

1. **AC1 语义**：把“仅一个成功”改判为「**恰好一次业务提交**」。same-operation 并发时第二个合法结果可以是 **返回原 receipt（`accepted=true`、同 `operation_id`/`request_digest`、`state='core-committed'`）**——这是 C-17 §6.2 replay 口径，不是 typed 冲突；different-operation 并发才要求 typed 冲突 ∈ `{SOURCE_OPERATION_CONFLICT, SOURCE_PLAN_STALE}`。跨实例 same-op replay 不作为断言（Out，见 AC1-d）。
2. **AC3 两分支**：AC3-a 使用“计划在确认后仍携带一个已非 current 的 migrate revision”的非 conforming Host 场景，期望 `STALE_BASE_REVISION`（防御性 seam 证据，不宣称现实可达）；AC3-b 使用现实漂移（plan 后改 region3 `current_revision_id`），期望 `SOURCE_PLAN_STALE(cause='manual')`（`manual_digest` 已含 current）。卡面明确：**不**把 `_migrate_revisions` 的 `STALE_BASE_REVISION` 当作现实漂移主路径。
3. **AC2-c**：存储失败必须经 host-control dispatch 投影为 `SOURCE_SYNC_STORAGE_FAILED`（`internal`/`retryable=true`，不泄露异常原文）；注入点必须在 `BEGIN IMMEDIATE` 与 `COMMIT` 之间；**禁止**在 `_bind_operation_grant`（commit 之后）注入并声称“事务回滚”。
4. **全表零写精确比较集**：统一 `_full_snapshot(conn)` 覆盖 16 张表：`pages, page_bindings, source_locations, source_versions, source_entries, source_sync_plans, source_operations, source_binding_publications, source_revision_lineage, regions, region_revisions, reading_progress, step_result_candidates, pipeline_runs, pipeline_run_targets, rendition_cache`；每表 `SELECT * ORDER BY 1` 转 `tuple`，返回 `{table: [rows]}`（失败时可打印差异）。不改 `tests/fea11/conftest.py`。
5. **G12 非缺口**：AC11-4 的“拒绝审计落盘”与 C-17 §6.2“不创建拒绝 receipt”冲突，冻结语义明确不创建；本卡只登记 Out，不实现、不补表。

## Acceptance Criteria

- [x] **AC1 并发 apply**：同实例 same-op replay、different-op typed 冲突、两独立 stack/连接同一文件 DB 三条并发证据 <<MET>>
  - **AC1-a same operation（同 service 实例两线程）**：两线程都返回；`source_operations` 对 `plan_id` 恰 1 行、`page_bindings` 只增一代、`source_binding_publications` 恰 1 套、`source_sync_plans.state='applied'` 恰一次；第二个响应 `operation_id`/`request_digest` 与第一个相同、`state='core-committed'`、`accepted=true`；全表快照中无第二次代次。判别力：允许两次提交则计数 >1；第二个被错误拒绝则 `accepted` 断言失败。
  - **AC1-b different operation（同实例两线程）**：一个成功；另一个 typed ∈ `{SOURCE_OPERATION_CONFLICT, SOURCE_PLAN_STALE}`；失败方以失败前快照为基线零业务写；不得出现未包装的 `sqlite3.*` 异常。判别力：若第二事务在 `take_confirmed` 前未检查 `existing_plan_op`，会撞 UNIQUE 抛未包装 `IntegrityError`。
  - **AC1-c 两独立 stack/两连接（文件 DB）**：`tmp_path` 文件 DB + `MigrationRunner` + `PRAGMA foreign_keys/journal_mode=WAL/busy_timeout`；两个 `SourceSyncStore`（各自连接）、两个 `SourceReadGrantRegistry`、两个 `build_source_sync_stack`；两 registry 以相同 `registry_id/generation/identity` 注册等价 grant；恰好一次业务提交；失败方 typed ∈ `{SOURCE_PLAN_STALE, SOURCE_OPERATION_CONFLICT}`；零业务写；不得 `database is locked`（出现即失败，不放宽断言）。该装置是 **service seam 防御性证据**，不是生产 IPC 并发（L1）。
  - **AC1-d（Out，不写断言）**：跨实例 same-op 并发可能返回 `SOURCE_PLAN_STALE` 而非 replay（replay 检查在 `BEGIN` 之前，`service.py:87` vs `:239`）。把 replay 检查移入事务属行为变更，Out；生产串行路径（单实例 RLock / registry commit_guard / 单线程 IPC）已满足 C-17 §6.2。
- [x] **AC2 DB 失败注入**：事务中途 + 最后一步整批回滚，以及 wire 级 SOURCE_SYNC_STORAGE_FAILED 证据 <<MET>>
  - **AC2-a 事务中途失败**：`CREATE TRIGGER ... BEFORE INSERT ON page_bindings WHEN NEW.page_id='p2' BEGIN SELECT RAISE(ABORT,'injected'); END;`（真实 SQLite 错误，`finally` 中 DROP）。apply 抛错；`_full_snapshot` 与失败前完全相等；plan 仍 `confirmed`、`applied_at IS NULL`；无 operation 行、无 publication/gate；移除 trigger 后同一 plan 重试（新 `operation_id`）成功。
  - **AC2-b 最后一步失败**：`CREATE TRIGGER ... BEFORE UPDATE ON source_operations WHEN OLD.state='host-authorized' BEGIN SELECT RAISE(ABORT,'injected'); END;`（命中 `commit_operation`，`source_sync.py:186-207`）。整批回滚（成功页数=0）；plan 仍 confirmed；重试成功。
  - **AC2-c wire 级 typed 证据**：经 host-control dispatch 的同一失败投影为 `SOURCE_SYNC_STORAGE_FAILED`（`internal`/`retryable=true`），不泄露异常原文（映射事实见 `src/bootstrap/core_service.py:1509-1516`、`:6189-6194`；测试落 `tests/fea11/test_source_sync_storage.py`）。须证明：失败发生在事务内 → 零业务写；错误 envelope 的 `code/category/retryable` 正确；不回显注入异常文本。
  - 禁止项：不得在 `_bind_operation_grant`（post-commit）注入并声称回滚（L3）；不得接受未包装 sqlite 异常作为“通过”。
- [x] **AC3 第三区域 BaseRevisionId（双分支）**：STALE_BASE_REVISION 防御分支 + 现实漂移 SOURCE_PLAN_STALE(cause=manual) <<MET>>
  - **AC3-a（plan 自带过期 revision）**：changed 页 + 3 个 region 各有 current revision（R1/R2/R3），另为 region3 建历史 revision `R3old`；plan decision=`bind` 且 `migrate_revision_ids=[R1,R2,R3old]`。期望 `STALE_BASE_REVISION`（C-17 §7.1/§8）；前两项迁移 + 新 binding + captured_v7 lineage 全部回滚；`_full_snapshot` 相等；`regions/region_revisions` 行数与内容不变（“其余区域不变”）。判别力：逐项提交会多出前两项新行；错误码为 `INVALID_REQUEST` 则失败。
  - **AC3-b（现实漂移）**：plan 确认后把 region3 `current_revision_id` 改为新 revision（同 region 新 revision 行，满足复合 FK）。期望 `SOURCE_PLAN_STALE(cause='manual')`；零写；记录**不会**到达 `_migrate_revisions` 的 `STALE_BASE_REVISION` 分支（`manual_digest` 覆盖 current）。
  - **AC3-c 口径登记**：AC3-a 是“非 conforming Host 可能产生的过期 plan”的防御证据；现实并发漂移由 AC3-b 的 CAS 路径覆盖。若 Lead 认为 `STALE_BASE_REVISION` 必须由现实漂移触发，需另案补 plan-time 校验（Out），本卡不扩。
- [x] **AC4 漂移矩阵 + 全表零写（G4–G11）**：G4–G10 逐项测试 + 16 表快照比较集 G11 <<MET>>

  | 子项 | 装置 | 期望 typed 结果 | 测试（建议名） |
  |---|---|---|---|
  | G4 源物理漂移 | plan 后覆盖 zip 字节（同路径） | `FILE_IDENTITY_CHANGED`（`source_strict_read.py:31-36`）；零写 | `T-drift-source-bytes` |
  | G4b 版本行漂移 | 篡改 `source_versions.content_digest` | `SOURCE_PLAN_STALE(cause='source')`（`service.py:417-426`） | `T-drift-source-version-row` |
  | G5 引用集合漂移 | plan 后新增/删除共享页 | `SOURCE_PLAN_STALE(cause='binding')`（`:365-371`） | `T-drift-reference-set` |
  | G6 决定/plan 失效 | confirm 后 `planner.invalidate(reason='decision')` | `SOURCE_PLAN_STALE(cause='decision')`；零写 | `T-drift-decision` |
  | G7 授权 generation 漂移 | 用 generation=2 的 grant 调 apply，baseline=1 | `SOURCE_PLAN_STALE(cause='authorization')`（`:170-176`） | `T-drift-authorization-generation` |
  | G8 授权失联 | `registry.revoke_all_for_session()` | `SOURCE_GRANT_REVOKED`（`source_read_refs.py:239-246`） | `T-drift-authorization-eof` |
  | G9 人工 revision | plan 后改 region current/text | `SOURCE_PLAN_STALE(cause='manual')`（`:402-404`） | `T-drift-manual` |
  | G9 保护位 | plan 后改 `region_locked` | `SOURCE_PLAN_STALE(cause='manual')`（`:405-408`） | `T-drift-protection` |
  | G9 draft | plan 后插入 `step_result_candidates` | `SOURCE_PLAN_STALE(cause='manual')`（`:409-412`） | `T-drift-draft` |
  | G9 Run | plan 后插入 `pipeline_runs`/`pipeline_run_targets` | `SOURCE_PLAN_STALE(cause='manual')`（`:413-416`） | `T-drift-run` |
  | G10 多项目末项 | b1+b2 共享 s1；scope=all；漂移 b2 最后一页 | 整批回滚；两项目零写（全表快照相等） | `T-multi-project-final-item` |
  | G11 比较集 | `_full_snapshot` 16 表（见冻结口径 4） | 所有测试共用；失败时打印逐表差异 | 全部测试 |

  共同断言：所有拒绝路径 `_full_snapshot` 前后逐行相等；无未包装 `sqlite3.*` 异常；错误码/`details.cause` 精确匹配上表；不得把“plan 状态被提前提交”作为通过。
- [ ] **AC5 证据、范围与门禁**：门禁/范围/日志已交付；独立上下文 Review 与负向探针待 Reviewer <<PARTIAL: 证据门禁项已齐（pytest 3183 passed/10 skipped、check.ps1 默认与 TaskPath 均 PASS、verify_pins 18/18、0 域外 diff、.NET NOT_RUN 已登记）；独立上下文 Review 与至少一次负向/变异探针尚未执行，按 AC5 现状只算 NOT_RUN>>
  - `pytest tests/fea11 -q` 全绿；`pytest tests -q -p no:warnings --tb=no` 全量通过，passed 数不低于释放日实测基线，不得新增 skip/failure；新增测试计数逐项记录（不引用旧卡数字代替实跑）。
  - `check.ps1`（默认与 `-TaskPath`）PASS；`verify_pins.ps1` 18/18；0 域外 diff；无新依赖；无 schema/migration 改动。
  - 证据：`verification/FEA-11-AC4-GAPS-1/{AC-MATRIX.md,EV.md,RESOURCE-MANIFEST.json,DELIVERY-MANIFEST.json,changed-files.txt,logs/*.log}`；隔离根 `G:/CODEX/New Manga.workspace/FEA-11-AC4-GAPS-1/`（不复用/不复写 FEA-11 tracked 证据）。
  - 独立上下文 Review（fresh subagent，`reviewer_kind=subagent`；非实现者）：必须实际运行新增测试，并至少做一次“负向/变异探针”（仓外副本/临时 worktree 移除一个 CAS 或回滚分支，证明对应用例变红），否则只算 NOT_RUN。
  - **`.NET` 口径（硬）**：本卡纯 Python 测试、0 C# diff → `.NET` 全量 **NOT_RUN**，理由写“0 C# 文件变更、纯 Python 测试”；**不得写 PASS**。若 Lead 另行要求全量，按 FEA-11 口径跑并分列 passed/failed/skipped。
  - AC11-4 判定：G1–G11 全部有判别性证据后，由 Lead/Review 判定 AC11-4 是否 MET；本卡不自行宣告 MET。

## 允许修改范围

frontmatter `allowed_paths` 为准（`evidence_dir` 已显式列入）：

- 测试：`tests/fea11/test_source_sync.py`（新增并发/DB 失败/第三区域/漂移矩阵测试 + 本地 `_full_snapshot`/`_file_db_stack` 助手）、**新增** `tests/fea11/test_source_sync_storage.py`（AC2-c wire 级 typed 证据，本地 fixture）。
- 文档/证据：本卡、Handoff、Review、`verification/FEA-11-AC4-GAPS-1/**`。
- 已移除：`src/application/sources/service.py`、`src/infrastructure/sqlite/source_sync.py`（本卡 test-only；不扩写域）。

## 禁止范围

- 不改 `src/**`（含 `service.py`/`source_sync.py`/`ports.py`/`core_assembly.py`/`model.py`）、契约字节、v8 DDL、错误闭集、命令表。
- 不改 `tests/fea11/conftest.py`；不改 `tests/core/**`；若必须共享 fixture 才能实现，停下报 DSH 窄批，不得自行扩写域。
- 不改 Host/Avalonia/UI/共享组合根；不做 FEA-12/13/14。
- 不写“拒绝审计 receipt”（C-17 §6.2）；不把 service 层回滚证据冒充 wire typed 证据；不把 post-commit 失败冒充事务回滚。
- 不新增依赖；不使用真实用户数据/AppData/外部卷/真实回收站；不 push。
- 不修改/删除 FEA-11、FEA-11-LINEAGE-1、FEA-11-HOST-AUTH-1 的 tracked 证据与 pin；证据/临时文件只写 `G:/CODEX/New Manga.workspace/FEA-11-AC4-GAPS-1/`。
- 不通过放宽断言/接受未包装 sqlite 异常/减少测试来“修绿”；不删测试、不把 skipped 计入 passed。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 并发 same-op / different-op | `python -m pytest tests/fea11/test_source_sync.py -q -p no:cacheprovider -k "concurrent"` | 生产 `ThreadRoutedConnection` facade + 隔离文件 DB（`:memory:` 单连接跨线程非安全） | **PASS**（`test_concurrent_same_operation_returns_the_original_receipt_once`、`..._different_operations_...`） | `logs/fea11-gaps1-tests.log`、`logs/fea11-tests.log` |
| AC1-c 双连接 | 同上（`_file_db_stack`，两独立 registry/store/stack） | `tmp_path` 文件 DB；FK/WAL/busy_timeout=5000 | **PASS**（`test_two_connection_stacks_commit_exactly_once_on_one_file_db`；无 `database is locked`） | 同上 |
| AC2 DB 失败注入 + 重试 | 同上（`RAISE(ABORT)` trigger 注入 2 例 + 重试） | 隔离 v8 fixture | **PASS**（`..._mid_transaction_...`、`..._final_step_...`） | 同上 |
| AC2-c wire typed | `python -m pytest tests/fea11/test_source_sync_storage.py -q -p no:cacheprovider` | 生产装配 `assemble_production_core`；host-control dispatch | **PASS**（`test_storage_failure_is_a_typed_wire_error_with_zero_business_writes`） | `logs/fea11-gaps1-tests.log` |
| AC3 两分支 | 同上（3 region + 过期 migrate revision / 现实漂移） | 隔离 fixture | **PASS**（`..._stale_migrate_revision_...`、`..._live_drift_is_plan_stale_manual`） | `logs/fea11-gaps1-tests.log` |
| AC4 G4–G11 | 同上（漂移矩阵 + `_full_snapshot` 16 表） | 隔离 fixture | **PASS**（11 个 `test_drift_*/test_multi_project_*` 用例） | `logs/fea11-gaps1-tests.log`；矩阵见 `AC-MATRIX.md` |
| AC5 门禁 | `pytest tests/fea11 -q`；`pytest tests -q -p no:warnings --tb=no`；`check.ps1`（含 `-TaskPath`）；`verify_pins.ps1`；`git diff --name-only` 范围核对 | 仓库根；释放日基线实跑 | **88 passed**；**3183 passed/10 skipped**（基线 3164/10）；check ×2 **PASS**；pins **18/18**；0 域外 diff | `verification/FEA-11-AC4-GAPS-1/{EV.md,changed-files.txt,logs/*.log}` |
| AC5 `.NET` | **NOT_RUN**（0 C# diff，纯 Python 测试；不得写 PASS） | — | **NOT_RUN** | `logs/dotnet-not-run.md`（说明） |

## 预期行为变更（Review 不判回归）

- 本卡 **test-only**：生产行为、wire、DTO、错误码、schema 零变化；不得出现“预期行为变更”。
- 既有测试期望原则上不改；仅当新增判别断言与既有断言冲突时，先停下报 DSH，不得自行放宽。
- AC1 的“仅一个成功”措辞在本卡内统一为“恰好一次业务提交”（语义更正，不是行为变更）。

## 依赖、风险与阻塞

- 硬依赖：`FEA-11`（`closed_with_limitations`；CAS/事务/迁移代码已在）。前置完成态：`FEA-11-PREREQ-1`（C-17 v1.0 / v8 DDL）、`FEA-11-LINEAGE-1`（done）、`FEA-11-HOST-AUTH-1`（closed_with_limitations，Host 侧路径层）。
- 并行边界：`FEA-11-MATCH-1` 写 `scanner.py`/`matcher.py`/`model.py` + `test_source_match.py`；本卡不得改这些文件（尤其 `model.py` 的 plan 校验）。`FEA-11-SCAN-1` 写 Host 侧，与本卡无文件交集。
- 主要风险：
  - R1 **范围不足**：若只做 L-5 三项，G4–G11 仍无断言 → AC11-4 保持 PARTIAL。本卡按裁决**纳入 AC4**，不以三项收口。
  - R2 AC1 措辞与 replay 矛盾 → 已按冻结口径 1 分列 same-op/different-op，禁止把“只一个 accepted=true”写成成功判据。
  - R3 AC3 错误码歧义 → 已按冻结口径 2 分两分支；plan-time 校验 Out。
  - R4 并发 flake（FEA-11 L-11 历史）→ 用事件/屏障编排，断言不变量（恰一次提交）而非“谁赢”；不 sleep；不依赖 `:memory:`。
  - R5 共享 registry `commit_guard` 串行化 → AC1-c 用两个独立 registry/stack；卡面说明这是 seam 防御测试（L1）。
  - R6 DB 注入误用 → 只在 `BEGIN` 与 `COMMIT` 之间注入；禁止 post-commit 冒充（L3）。
  - R7 比较集不全 → 统一 `_full_snapshot` 16 表，不用 9/11 表旧助手冒充。
  - R8 typed 投影 → AC2-c 必须行为级验证 `SOURCE_SYNC_STORAGE_FAILED`；不得只以静态映射表代替。
  - R9 busy_timeout（5s）→ 保持事务短小；出现 `database is locked` 视为失败，不放宽。
  - R10 门禁口径 → `.NET NOT_RUN` 必须显式写，不得以“历史全量通过”冒充本卡 PASS。
- 阻塞解除标准：scope 已冻结 → Lead 释放（固定 base/Owner/Reviewer）→ 实施 → 证据齐备 → 独立 Review（含负向探针）→ DSH 集成 closeout。

## 残余 limitation（预登记 L1–L4）

- **L1**：生产 Core 请求循环单线程（`src/bootstrap/core_service.py:7319-7338`），AC1-c 双连接测试是 service seam 防御性证据，不是端到端 IPC 并发。
- **L2**：AC3 现实漂移由 `SOURCE_PLAN_STALE(cause='manual')` 拦截；`_migrate_revisions` 的 `STALE_BASE_REVISION` 只在非 conforming plan 下可达（防御性分支）。
- **L3**：`_bind_operation_grant`（commit 之后）失败不在事务回滚证据内，是 post-commit 残余风险。
- **L4**：DB 失败用 SQLite trigger/测试注入模拟，不等于真实磁盘满/IO 错误；commit-time IO 失败未模拟。
- 备注：`G12` 拒绝审计按 C-17 §6.2 明文禁止，**不是缺口**，不登记为 limitation。

## 交付与运行记录

- **交付（2026-11-05，Owner=`scanner-gaps-impl`，DSH Agent Teams；Lead=`lead`）**
  - 实现 commit：`95815ff7a`（`tests/fea11/test_source_sync.py` +18 用例；新增 `tests/fea11/test_source_sync_storage.py` +1 用例）——**test-only**，零 `src/**`/契约/schema 变更。
  - 交付 head（实现）：`95815ff7a`；证据/卡面/Handoff 随后续文档提交落盘。
  - 基线：`pytest tests` 3164 passed/10 skipped；`pytest tests/fea11` 69 passed。
  - 交付后：`pytest tests` **3183 passed/10 skipped**（+19，无新增 skip/failure）；`pytest tests/fea11` **88 passed**。
  - 门禁：`check.ps1`（默认 + `-TaskPath`）PASS；`verify_pins.ps1` **18/18**；`git diff --name-only 51e139eff..HEAD -- src/ doc/plan doc/contracts apps` **空**。
  - 指针更新（Lead 执行，2026-11-05）：`doc/REBASELINE_PLAN.md` DAG 行 → `in_review`、`READY 节点：无`；`doc/STATUS.md` 当前 Task → `in_review`、下一步「独立 Review → closeout」；`TASK_LEDGER` 已刷新。Owner 只读于此（未改 STATUS/PLAN/LEDGER）。
  - 门禁记录说明：`logs/gates.log` 的一次运行先于「gates.log 自身登记进 Canonical Evidence」发生（当时 4 warnings，含该未登记项），登记后最终复核为 **PASS（3 warnings：14 个非终态 Task / STATUS 预算 80% / REBASELINE_PLAN 预算 80%，均为既有基线项）**；最终复核输出不重写 gates.log，故其 sha256 pin 与工作树字节一致。
  - `.NET`：**NOT_RUN**（0 C# 文件变更、纯 Python 测试；不得写 PASS）。
  - 证据：`verification/FEA-11-AC4-GAPS-1/`（`AC-MATRIX.md`、`EV.md`、`RESOURCE-MANIFEST.json`、`DELIVERY-MANIFEST.json`、`changed-files.txt`、`logs/`）；隔离根 `G:/CODEX/New Manga.workspace/FEA-11-AC4-GAPS-1/`（probes/logs）。
  - 实现者负向/变异探针自检（**非权威**，独立 Review 须自行复做）：3 项变异验证为 RED（replay 移除 / 逐项 commit / manual+protection CAS 移除），2 项被更强 CAS 遮蔽并如实登记 → `logs/mutation-probes.log`。
- Handoff：`doc/handoffs/FEA-11-AC4-GAPS-1-handoff.md`（待与本卡同批提交）。
- Review：尚无（独立上下文 Reviewer，须记录 session ID 与来源；作者不得自审）。
- 后续：独立 Review（实际运行新增测试 + 至少一次负向探针）→ DSH 集成 closeout（填写 `integration_commit` 并改 done / closed_with_limitations）。

## Canonical Evidence

进入 `in_review` 时逐项登记唯一当前证据（实现 `95815ff7a`；证据/日志按 sha256 pin，工作树原始字节）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-FEA11GAPS1-TESTS-SYNC | AC1–AC4 用例（18） | tests/fea11/test_source_sync.py | 95815ff7a | - | CANONICAL |
| EV-FEA11GAPS1-TESTS-STORAGE | AC2-c wire typed 用例（1） | tests/fea11/test_source_sync_storage.py | 95815ff7a | - | CANONICAL |
| EV-FEA11GAPS1-MATRIX | AC1–AC5 证据矩阵 | verification/FEA-11-AC4-GAPS-1/AC-MATRIX.md | - | 561ab55a14300c354766534019ce17512fb150e91bd45749fdca61c64bd33f4f | CANONICAL |
| EV-FEA11GAPS1-EV | 命令/结果/limitation 索引 | verification/FEA-11-AC4-GAPS-1/EV.md | - | 816739437e1ebb63c2768023745cbbc131939c77fc981036ba917345ac4da0df | CANONICAL |
| EV-FEA11GAPS1-RESOURCE | 资源清单 | verification/FEA-11-AC4-GAPS-1/RESOURCE-MANIFEST.json | - | 77b2d1a54d908145723788bfc879c30dea6375cc2a383b80fa20a9456644b1e5 | CANONICAL |
| EV-FEA11GAPS1-DELIVERY | 交付清单/门禁结果 | verification/FEA-11-AC4-GAPS-1/DELIVERY-MANIFEST.json | - | ab6340e982e7baaffc219068b86418623a23172d191619a9f7376991be050f18 | CANONICAL |
| EV-FEA11GAPS1-CHANGED | 变更文件与 0 域外 diff | verification/FEA-11-AC4-GAPS-1/changed-files.txt | - | 69c2598672791707baf9ac5025ab03cf24e436c981e3d006b6815721673b7141 | CANONICAL |
| EV-FEA11GAPS1-BASELINE | AC5 释放日基线（改前全量） | verification/FEA-11-AC4-GAPS-1/logs/baseline-full-pytest.log | - | 2dab2d10e0b7f23d767bf4c8cfb532035f1b0bfb3d62a4c6209038ca399b6af8 | SOURCE_PIN |
| EV-FEA11GAPS1-FEA11 | AC5 相关组 pytest | verification/FEA-11-AC4-GAPS-1/logs/fea11-tests.log | - | 3a86b1178e42829a7a5a4e1238f4c3e7bc0c551cb26cf5ee093652b0ad36c790 | CANONICAL |
| EV-FEA11GAPS1-GAPS1 | AC1–AC4 新增用例日志 | verification/FEA-11-AC4-GAPS-1/logs/fea11-gaps1-tests.log | - | a2e8c94142d8d318b889471e9c63fb27ca11c336f381673202202cfbe213eebf | CANONICAL |
| EV-FEA11GAPS1-FULL | AC5 全量 pytest（3183/10） | verification/FEA-11-AC4-GAPS-1/logs/full-pytest.log | - | b33fa00ac02211e6a060b4e315c093fb1b55904e5e0d489d87cb8f2bb3d04ce6 | CANONICAL |
| EV-FEA11GAPS1-PROBE | 负向/变异探针自检（非权威） | verification/FEA-11-AC4-GAPS-1/logs/mutation-probes.log | - | 9e0d43b965ee44ea3fdad88351b0c0100d8c7c15b3a33175c97f0ebbfb24d30c | SOURCE_PIN |
| EV-FEA11GAPS1-SCOPE | 0 产品/契约 diff | verification/FEA-11-AC4-GAPS-1/logs/scope-diff.log | - | 903e65ac3da4674dc6474f68fd0bb6cfedc4eeaa93de1de7c193ccf4ff59101a | CANONICAL |
| EV-FEA11GAPS1-DOTNET | `.NET` NOT_RUN 口径 | verification/FEA-11-AC4-GAPS-1/logs/dotnet-not-run.md | - | b2f2242858fcc88b0cd95bb29c3532c336a6e00a253fafa8af84deec8b2f9328 | CANONICAL |
| EV-FEA11GAPS1-GATES | AC5 门禁（command/EXIT/head） | verification/FEA-11-AC4-GAPS-1/logs/gates.log | - | 1178e95ecf82cf0d47d67aa983f24618496b0d647a1ca5e1050b44517fa3c97d | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（main 工作树；base `51e139eff`，main head `d8049fe6e`） | NOT_APPLICABLE | — | — | 未创建 linked worktree；实施只在 main 工作树 `tests/fea11/` 与 `verification/` 内 |
| temp | `G:\CODEX\New Manga.workspace\FEA-11-AC4-GAPS-1\`（仓外隔离根：`probes/`、`logs/`） | PRESERVE_REFERENCED | Same source location（仓外，不随仓库分发） | `verification/FEA-11-AC4-GAPS-1/RESOURCE-MANIFEST.json` | 无进程持有；产品代码/测试不引用该路径；`EV.md §4` 仅作探针脚本索引，仓内副本为 `logs/mutation-probes.log`；closeout 后可保留或删除 |
| agent-output | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 本卡未产生独立 agent-output；实现/证据直接写入仓库 `tests/fea11/` 与 `verification/FEA-11-AC4-GAPS-1/` |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`complete`（本卡实现的 canonical evidence 已逐项登记；Review/集成证据由 DSH closeout 补登）。
- resource_closeout_status：`pending`（Owner 未执行删除/迁移/归档；仓外隔离根保留供 Review 复核）。
- 删除、迁移、归档数量/字节数：0（Owner 无操作）。
- 未关闭项及保留原因：L1–L4（见上）；G12 非缺口。
- 当前指针清理：待 DSH closeout 时更新 STATUS / Plan / TASK_LEDGER 或说明无需更新。
