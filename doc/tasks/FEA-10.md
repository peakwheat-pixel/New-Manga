---
id: FEA-10
title: 快照 / 候选 / 提交安全（PreparedRun 两阶段 + canonical request builder + retry 快照 + candidate-only apply）
kind: implementation
governance_version: 3
status: in_progress
approval: **scope approved r6（Codex，P0=0/P1=0/P2=2 非阻断）+ DSH Appointment 2026-11-04**；硬前置 FEA-10-PREREQ-1 已 done；DSH 2026-11-04 释放 Owner 实施
suggested_owner: codex
owner: codex（认领 2026-11-04；DSH 释放）
claimed_at: 2026-11-04T07:44:00.000Z
reviewer: implementation Review 待 Appointment（全新上下文；不得由实现者自审）
depends_on:
  - FEA-00A-IMPL-1
  - FEA-03
  - FEA-09
  - FEA-10-PREREQ-1
base_commit: d831cf968cd856674c0320fe67ce854f4ef9d4b3
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-10
allowed_paths:
  - doc/tasks/FEA-10.md
  - doc/reviews/FEA-10-*.md
  - doc/handoffs/FEA-10-*.md
  - verification/FEA-10/**
  - src/application/tasks/service.py
  - src/application/tasks/store.py
  - src/application/tasks/projection.py
  - src/infrastructure/pipeline/assembly.py
  - src/infrastructure/pipeline/executor.py
  - src/infrastructure/sqlite/pipeline.py
  - src/infrastructure/providers/handlers.py
  - src/infrastructure/providers/retry.py
  - src/infrastructure/providers/step_writes.py
  - src/infrastructure/providers/registry.py
  - src/bootstrap/core_service.py
  - src/bootstrap/core_assembly.py
  - apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandRegistry.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/RunBindingDefaults.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/DomainServices.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/NullHostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/RunContracts.cs
  - apps/desktop-avalonia/src/NewManga.ApplicationCore/RunMonitor.cs
  - apps/desktop-avalonia/src/NewManga.ApplicationCore/RunStateStore.cs
  - apps/desktop-avalonia/src/NewManga.ApplicationCore/IntentCoordinator.cs
  - apps/desktop-avalonia/src/NewManga.ApplicationCore/RequestExecutor.cs
  - apps/desktop-avalonia/src/NewManga.ApplicationCore/DraftBuffer.cs
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/CoreServiceIntegrationTests.cs
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/WireTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/HostRuntimeIntegrationTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea10RunIpcTests.cs
  - apps/desktop-avalonia/tests/NewManga.ApplicationCore.Tests/DraftBufferTests.cs
  - apps/desktop-avalonia/tests/NewManga.ApplicationCore.Tests/IntentCoordinatorTests.cs
  - apps/desktop-avalonia/tests/NewManga.ApplicationCore.Tests/RequestExecutorTests.cs
  - apps/desktop-avalonia/tests/NewManga.ApplicationCore.Tests/RunMonitorTests.cs
  - apps/desktop-avalonia/tests/NewManga.ApplicationCore.Tests/TestSupport.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/RunControllerTests.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/RunIndexTests.cs
  - tests/core/test_p13_run_runtime.py
  - tests/core/test_p13_lifecycle_discriminators.py
  - tests/core/test_fea00a_pipeline_seam.py
  - tests/core/test_pipeline_defaults_assembly.py
  - tests/core/test_pipeline_defaults_service.py
  - tests/fea10/test_prepared_run.py
  - tests/fea10/test_snapshot_retry.py
  - tests/fea10/test_commit_zero_write.py
  - tests/fea10/test_idempotent_receipt.py
  - tests/fea10/support/restart_core.py
  - tests/pipeline/test_pipeline_production_seam.py
  - tests/pipeline/test_pipeline.py
  - tests/pipeline/test_run_store_cache_race.py
  - tests/pipeline/test_store.py
  - tests/pipeline/test_models.py
  - tests/pipeline/test_regionless_rebinding.py
  - tests/pipeline/test_retype_candidate_persistence.py
  - tests/pipeline/test_clean_availability.py
  - tests/pipeline/test_fea00a_source_boundaries.py
  - src/ports/translation/protocol.py
  - src/infrastructure/providers/translation_openai.py
  - src/infrastructure/providers/openai_client.py
out_of_scope:
  - 既有冻结契约字节（C-01b/C-05/C-08/C-13 等）与 M2-C1 wire 语义（协议注册归 FEA-10-PREREQ-1）
  - FEA-11/12/13/14 的范围；provider 新能力或新 UI 设计；source 重定位/同步实现
  - 真实用户数据/AppData/外部卷；push
  - 共享组合根（App.axaml/App.axaml.cs/NewManga.App.csproj/NewManga.sln）仅 DSH 单点提交
---

# FEA-10：快照 / 候选 / 提交安全

> 来源：`doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md` §10、§15.5、§15.6:931；`doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md`（SC-R01…SC-R09，pin `453f993c…`）；`doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md`（SC-D07/SC-D08）；`doc/reviews/ADJ-2026-11-04-NEXT-TASK.md`（Codex 裁决 + DSH 硬前置/拆分裁定 + scope r1/r2 处置）。
> 首轮只交卡/范围矩阵/契约缺口与独立 scope review；**不得写生产代码**。FEA-10 的 `ready` 以 `FEA-10-PREREQ-1` done 为硬前置。

## 目标

形成 **唯一 canonical request builder**、不可变 `PreparedRun`/payload、candidate-only 准备与受保护原子提交；保证「预览=实际发送」、已接受任务不被运行期配置/邻页变化改变、旧结果不越过最新人工修改。复用既有 Run store/scheduler/snapshot、revision/Lock CAS、`RegionStepWriter`/`SqliteTargetCatalog`/`DraftProtectionService`，不建第二套真值/调度器。

## 精确写域矩阵（文件级）

| 文件/目录 | 用途 | AC |
|---|---|---|
| `src/application/tasks/{service,store,projection}.py` | Prepare/Accept、retry、receipt、counts/projection | AC1/AC4/AC6/AC7 |
| `src/infrastructure/pipeline/{assembly,executor}.py` | prepared run 组装与执行（只读快照） | AC1/AC3 |
| `src/infrastructure/sqlite/pipeline.py` | Run store/事务、`BEGIN IMMEDIATE`、receipt | AC5/AC6/AC7 |
| `src/infrastructure/providers/{handlers,retry,step_writes,registry}.py` | provider 绑定快照、step seam、candidate 写入 | AC2/AC4/AC5 |
| `src/bootstrap/{core_service,core_assembly}.py` | `_RUN_COMMANDS`/dispatch/装配（协议注册后） | AC8/AC10 |
| `NewManga.CoreClient/CoreServiceClient.cs`、`Commands/{HostCommandDispatcher,HostCommandRegistry,RunBindingDefaults,DomainServices}.cs` | 生产客户端、命令注册/错误投影、Run 绑定默认值 | AC1/AC8 |
| `NewManga.Host/HostRuntime.cs` | Host 命令面/真实 IPC 路由 | AC8 |
| `NewManga.App/Services/{HostController,IHostController,NullHostController,RunContracts}.cs` | 生产 adapter/typed 端口 | AC8 |
| `NewManga.ApplicationCore/{RunMonitor,RunStateStore,IntentCoordinator,RequestExecutor,DraftBuffer}.cs` | intent/receipt/控制状态、UI 可观察投影 | AC5/AC6/AC7 |
| `src/ports/translation/protocol.py`、`src/infrastructure/providers/translation_openai.py`、`src/infrastructure/providers/openai_client.py` | request builder 边界：默认只读复用；如经 DSH 批准窄改，需证明现有 `payload_hash` 不等于 endpoint/model/body 全摘要 | AC2/AC3 |
| `tests/fea10/{test_prepared_run,test_snapshot_retry,test_commit_zero_write,test_idempotent_receipt}.py`、`tests/fea10/support/restart_core.py`、`tests/core/{test_p13_run_runtime,test_p13_lifecycle_discriminators,test_fea00a_pipeline_seam,test_pipeline_defaults_assembly,test_pipeline_defaults_service}.py`、`tests/pipeline/{test_pipeline_production_seam,test_pipeline,test_run_store_cache_race,test_store,test_models,test_regionless_rebinding,test_retype_candidate_persistence,test_clean_availability,test_fea00a_source_boundaries}.py` | Python 回归/新增（逐文件） | AC1–AC7 |
| `NewManga.CoreClient.Tests/{CoreServiceIntegrationTests.cs,WireTests.cs}` | 协议/回归 | AC8 |
| `NewManga.Host.Tests/{HostRuntimeIntegrationTests.cs,Fea10RunIpcTests.cs}`（**不含 RunMonitorTests.cs**；该测试在 ApplicationCore.Tests） | 真实 Host/IPC/回归 | AC8 |
| `NewManga.ApplicationCore.Tests/{DraftBufferTests,IntentCoordinatorTests,RequestExecutorTests,RunMonitorTests,TestSupport}.cs`、`NewManga.App.Tests/{RunControllerTests,RunIndexTests}.cs` | state/projection/adapter 测试 | AC6/AC8 |

共享接口新增/改动须 DSH 明确授权；组合根仍 DSH 单点提交。

## Acceptance Criteria（草案）

- [x] **AC1（Prepare 两阶段）**：`PrepareRun` 生成 `PreparedRunId/snapshotDigest/generation/expiresAt/displaySummary/redactedPayloadPreview` 且**零 DB 写、零执行**；`AcceptRun` 仅 digest 匹配后写 Run；候选过期→`RUN_PREVIEW_EXPIRED`；三码按 M2-C1 冻结投影。 <<MET>>
- [ ] **AC2（快照完整与敏感面）**：settings/provider snapshot 为完整可重放值；缺失/不完整→`RUN_SNAPSHOT_INCOMPLETE`；敏感认证材料不入普通快照/日志/错误/证据；强类型白名单落盘（非整字典）。 <<PARTIAL: 远程 typed config 已实现，其他 provider 完整版本/参数快照未闭环>>
- [ ] **AC3（预览 stale、配置隔离与 digest 语义）**：确认前目标/源/草稿/保护/配置变化→stale 拒绝零副作用；接受后 defaults/邻页变化不静默改变 payload。**`preparedDigest` 严格按冻结四元组算法校验**；另以 `payloadDigestPreview` 与 `payloadDigestSend` 比较（二者同源同值），**不要求四元组摘要与 payload 摘要相等**；邻页上下文不可变 pin 可验证。 <<PARTIAL: 已知源文本翻译与邻页 pin 已验证，上游 OCR 请求精确预览待 DSH 裁决>>
- [ ] **AC4（retry 两分支）**：同键重放返回原 Run 不新建；新 key 的 `RetryFailedTargets` 新建 Run（`source_run_id`）、目标=失败页子集、上下文按接受时重读冻结；凭据/版本不可用→阻塞；新配置须差异确认创建关联任务，不写回旧 run。 <<PARTIAL: retry 两分支已验证，凭据/版本 blocked 与新配置确认未闭环>>
- [x] **AC5（candidate-only 与零提前写）**：以下每个条件均单独故障注入并断言 seam 未成功时 `regions.text_json`、`current_revision_id`、`region_revisions` 行数与前态完全相同、Run receipt/counts 不增加、candidate 可诊断/恢复、成功时 live/revision/Run receipt 同事务：① revision 冲突；② Lock；③ manual/final 保护；④ `STALE_RUN_SNAPSHOT`；⑤ source lease 失效；⑥ PageBinding generation 变化；⑦ draft token/sequence 不匹配；⑧ DB 失败；⑨ pause/cancel；⑩ prepare 后崩溃重启。断言限定为**成功提交回执/完成计数不增加**；允许失败/控制状态按冻结语义合法持久化。**事务单位**：a) C-13 多 Region 编辑 apply = 单 `BEGIN IMMEDIATE` 覆盖全部目标 Region（全有/全无，逐 Region expected map）；b) Pipeline step seam = 以 `StepId/TargetIds` 为单位的单事务（`commit_step_result`，含 Run receipt/counts）；两者不得混用 candidate 存储。 <<MET>>
- [ ] **AC6（控制/完成口径）**：控制请求持久化≠状态改变；UI 不早于 Core 持久 status 显示 paused/cancelled；终态共同不变量（processing=0/waiting=0 + 各终态附加判据）；重启后同源可复读。 <<PARTIAL: 已修控制/终态边界，完整 UI 重连与终态专项矩阵未完成>>
- [x] **AC7（SC-R09 durable receipt）**：提交成功但响应丢失→同键重放找回原 `run_id`、无第二 Run；**关闭/重启 Core 并重开同一 DB 后同键仍找回原 Run**；同键异 fingerprint→`IDEMPOTENCY_KEY_REUSED`；相同 `request_id` 不同 key 视为两个操作；仅覆盖冻结三类带 key 操作（StartRun/RetryFailedTargets/ControlRun restart），不新增命令。 <<MET>>
- [x] **AC8（真实生产链路与回归）**：生产 assembly `Prepare/Accept/commit`；真实 Host↔Core IPC（`Fea10RunIpcTests`，`NEWMANGA_FEA10_IPC=1` 门径，隔离 DataRoot）；相关 pytest/.NET 全量不减少；旧 managed 路径、既有 Run 命令、`tests/core/test_p13_run_runtime.py` 等不回归。 <<MET>>
- [ ] **AC9（范围/冻结/证据）**：C-05/C-15/C-16/C-07 冻结字节与 FEA-08/FEA-09 closeout 未改；范围 diff 合规；独立实现 Review approved；DSH 集成；Handoff + EV + Resource Manifest。 <<BLOCKED: PLAN READY 指针不一致；独立 Review、DSH 集成与 commit pins 待完成>>
- [x] **AC10（不越界）**：不提前实现 FEA-11/12/13/14 或 provider 新能力；不新增未冻结 Schema/wire；source 校验消费既有能力；共享组合根仅 DSH 单点提交。 <<MET>>

## 验证矩阵（AC→文件→命令→断言→证据）

| AC | 测试文件（新增/复用） | 命令（CWD=`G:\CODEX\New Manga`） | 隔离环境 | 关键断言 | 证据 |
|---|---|---|---|---|---|
| AC1/AC2 | `tests/fea10/test_prepared_run.py`（新） | `python -m pytest tests/fea10 -q` | `G:/CODEX/New Manga.workspace/FEA-10/fixtures/<case>/`（每例唯一 DataRoot/DB） | Prepare 零 DB/零执行；过期/不完整码；敏感面 | `verification/FEA-10/logs/` |
| AC3/AC4 | `tests/fea10/test_snapshot_retry.py`（新）；复用 `tests/core/test_p13_run_runtime.py` | `python -m pytest tests/fea10 tests/core -q` | `G:/CODEX/New Manga.workspace/FEA-10/fixtures/<case>/` | 四元组 digest；payload digest 同值；stale；retry 两分支 | 同上 |
| AC5/AC6 | `tests/fea10/test_commit_zero_write.py`（新）；扩展 `tests/core/test_fea00a_pipeline_seam.py` | `python -m pytest tests/core tests/fea10 -q` | `G:/CODEX/New Manga.workspace/FEA-10/fixtures/<case>/` | 10 条件逐项三处零变化/完成数不增；事务单位；控制 pending | 同上 |
| AC7 | `tests/fea10/test_idempotent_receipt.py`（新）+ `tests/fea10/support/restart_core.py` | 同上；先 `python tests/fea10/support/restart_core.py --data-root <fixture> --db <fixture>/library.db --stop`，再 `python tests/fea10/support/restart_core.py --data-root <fixture> --db <fixture>/library.db --start`（两次调用复用同一 DataRoot/DB） | `G:/CODEX/New Manga.workspace/FEA-10/fixtures/<case>/` | 丢 ACK/重启找回；异 fingerprint；request_id 非键 | 同上 |
| AC8 | `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea10RunIpcTests.cs`（新，`[Fact]`/env 门）；既有 .NET 回归 | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release`；`dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build`；`$env:NEWMANGA_FEA10_IPC='1'; $env:NEWMANGA_BUILD_PYTHON='C:/Python314/python.exe'; dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --no-build --filter FullyQualifiedName~Fea10RunIpcTests` | `G:/CODEX/New Manga.workspace/FEA-10/fixtures/<case>/`（每例唯一 DataRoot） | 生产 assembly/IPC；回归不减少；日志含命令/EXIT | `verification/FEA-10/logs/dsh/` |
| AC9/AC10 | `check.ps1`、`verify_pins.ps1`、`git diff --name-only` | `pwsh -NoProfile -File tools/governance/check.ps1`；`pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 主工作树 | PASS/17/17/范围合规 | EV + Handoff |

## 依赖与硬前置

- 已完成：FEA-00A-IMPL-1（三处零变化/candidate 基础）、FEA-03、FEA-09。
- **硬前置 `FEA-10-PREREQ-1`**：C-08 块②协议注册（M2-C1 rev 2.12 + host `allowedRunErrorCodes`）；未 done 前本卡不得 ready/实施。
- 契约依据：C-08（pin `453f993c…`）、C-13/SD07-08、C-05/C-04b 接口；M2-C1/P11 既有命令语义；不新增 wire。
- 与 C-04b 的共享块②：DSH 在 ADJ 裁定**拆分**（C-04b 已冻结且删除线不属 FEA-10；硬前置独立为 PREREQ-1），不修改 C-08 冻结字节。

## 既有实现复用（不得重建）

`PipelineService.accept_start_run/accept_retry_failed_targets/commit_step_result`、`RegionStepWriter`、`SqliteTargetCatalog.commit_step`、`DraftProtectionService`、`FrozenRunSnapshots`/`PipelineStore`、`RunMonitor`/`RunStateStore`、现有 Run dispatch（`src/bootstrap/core_service.py` `_RUN_COMMANDS`）；缺口只在既有 seam 加深。

## 首轮交付（建卡阶段）

1. Task 卡 + 范围矩阵/契约缺口；
2. 精确 allowed_paths（已列文件级；新文件需在实施前由 DSH 确认）；
3. 独立 scope review + DSH 处置；
4. 不写生产代码、不 push。

## 实施与交付记录（Codex，2026-11-04）

- 实际实现基线：`aa7bcd6161be5df07e2b8bf546600fec04af038f`，main / 主工作树；卡中 `base_commit=d831cf...` 为 scope 历史，未冒充交付提交。
- 本次无 commit/push；`delivery_head` 留空，DSH 集成后填写。
- Handoff：[FEA-10-handoff](../handoffs/FEA-10-handoff.md)；逐 AC 证据与明确限制：[AC-MATRIX](../../verification/FEA-10/AC-MATRIX.md)。
- 当前为**部分交付 in_review**，不表示实现全部完成；AC2/AC3/AC4/AC6 PARTIAL，AC9 BLOCKED，禁止提前 done。
- 治理事实差异：DSH 释放后 Task 已 in_progress，而 PLAN/STATUS 仍 ready，Appointment 留有旧 blocked 前置文字；Owner 未修改写域外权威指针。`check.ps1` 因 READY DAG 与 Task 状态不一致失败；请 DSH 对账。
- 已跑：Python 全量 1036 passed；逐文件 204 passed；追加 provider 559 passed/4 skipped；FEA-10 33 passed；10 类故障/两事务单位 17 passed；stop/start 两次均 EXIT=0；pins 17/17。最终 .NET build 0 warning/0 error、全量 1344 passed/0 failed/75 skipped、真实 IPC 1 passed；均 EXIT=0，完整结果在 Handoff 与日志。
- 原始失败/重跑、隔离根、环境偏差、NOT_RUN、恢复方式均在 Handoff。早期既有回归继承系统 TEMP/TMP，在 AppData/Local/Temp 生成测试临时材料；最终门禁改用 workspace TEMP/TMP，不清理系统 TEMP，不隐瞒该偏差。

## DSH r1 复核与 r2 授权（2026-11-04）

- DSH 独立复跑门禁（`G:/CODEX/New Manga.workspace/FEA-10/logs/dsh/dsh-gates-r1.log`）：build EXIT=0（0 warning/0 error）、dotnet test EXIT=0（1344 passed / 0 failed / 75 skipped，不减少）、pytest 1036 passed、真实 IPC 1 passed、check PASS（4 warnings）、pins 17/17、范围 0 域外；FEA-09 证据被 DSH 跑测重写 1 文件（wire-redacted.ndjson），已恢复原字节并断言零 diff。
- PLAN/STATUS 的 READY 指针已由 DSH 对账修复（PLAN `READY 节点：无`、FEA-10 `in_progress`；STATUS 同步）；check.ps1 由 FAIL 转 PASS。
- 裁决全文：[ADJ-2026-11-04-FEA-10-R2](../reviews/ADJ-2026-11-04-FEA-10-R2.md)：AC3 口径限定；批准 request builder 三文件窄改；AC2/4/6 完成口径；r2 写域与完成标准。
- r1 字节已由 DSH 固定为阶段集成 commit（partial，不改变 AC 结论）；r2 由 Codex 全新实现会话续作补齐 AC2/3/4/6，Task 保持 `in_progress`。

## Canonical Evidence

工作树 SHA-256 pin 是本轮只读复核入口；遵守用户“不 commit”要求，commit 暂填 pending。DSH 固定集成/交付提交后补 commit，不能将起始 HEAD 填作包含新证据的 commit。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-FEA10-OWNER | AC1–AC10（含 PARTIAL/BLOCKED 与门禁索引） | verification/FEA-10/AC-MATRIX.md | pending | 814d6a1745990f0bec4dc61f5016de6ed76e0260df71b0bccfd0c5f7e6417009 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga | PRESERVE_REFERENCED | 原位 | verification/FEA-10/DELIVERY-MANIFEST.json | 主树，dirty 实现交付；无新 linked worktree，不移动/删除 |
| task-env / model / exchange | NOT_APPLICABLE | NOT_APPLICABLE | - | 无新增依赖/模型/交换目录 | 复用 Python314 / .NET 10 / Node 24 |
| test-material / temp | G:/CODEX/New Manga.workspace/FEA-10/fixtures | PRESERVE_REFERENCED | 原位 | verification/FEA-10/RESOURCE-MANIFEST.json | 每例独立 DB；仅同库重启场景复用指定库；测试结束后保留 |
| artifact | apps/desktop-avalonia/**/bin、obj | PRESERVE_REFERENCED | 原位 | 构建日志 | 既有构建布局；本次无清理/迁移 |
| evidence / agent-output | verification/FEA-10 | PRESERVE_REFERENCED | 原位 | 本表 Canonical Evidence + DELIVERY-MANIFEST | 原始命令/EXIT/失败历史保留 |
| early regression temp | C:/Users/49745/AppData/Local/Temp（既有测试默认 TEMP） | PRESERVE_UNKNOWN | 原位 | 未扫描/未清理 | 运行目录偏差；未接入真实应用库；交 DSH 裁决 |

## Closeout Record

- 阶段事实：2026-11-04 Codex r1 部分交付；DSH 独立复跑门禁通过并固定阶段集成 commit（partial）；Task `in_progress`（r2 续作中），未 closeout/done。
- canonical_evidence_status：`pending`（阶段字节已固定；最终 Review/集成后补 pins）。
- resource_closeout_status：`pending`（资源原位保留，DSH 最终 disposition）。
- 删除/迁移/归档：0；未清理 linked worktree、build、fixture 或早期临时材料（早期系统 TEMP 材料 PRESERVE_UNKNOWN）。
- 未关闭：AC2/3/4/6 续作（r2）、独立实现 Review、DSH 最终集成；详见 ADJ-2026-11-04-FEA-10-R2。
- 下一步：r2 完成 → DSH 门禁 → 最终集成提交 → 全新上下文 Codex Review → closeout；不自动开始 FEA-11，不 push。
