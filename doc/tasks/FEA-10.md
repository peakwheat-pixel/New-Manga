---
id: FEA-10
title: 快照 / 候选 / 提交安全（PreparedRun 两阶段 + canonical request builder + retry 快照 + candidate-only apply）
kind: implementation
governance_version: 3
status: proposed
approval: pending scope review r4（Codex 2026-11-04 裁决首选；须先完成 FEA-10-PREREQ-1 协议注册）
suggested_owner: codex
owner: null
reviewer: pending scope review（独立上下文；实施 Review 另行 Appointment）
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
  - src/application/tasks/__init__.py
  - src/infrastructure/pipeline/assembly.py
  - src/infrastructure/pipeline/executor.py
  - src/infrastructure/pipeline/__init__.py
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
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/RunMonitorTests.cs
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
  - tests/pipeline/conftest.py
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
| `NewManga.CoreClient/{CoreServiceClient.cs, Commands/*}` | 生产客户端、命令注册/错误投影、Run 绑定默认值 | AC1/AC8 |
| `NewManga.Host/HostRuntime.cs` | Host 命令面/真实 IPC 路由 | AC8 |
| `NewManga.App/Services/{HostController,IHostController,NullHostController,RunContracts}.cs` | 生产 adapter/typed 端口 | AC8 |
| `NewManga.ApplicationCore/{RunMonitor,RunStateStore,IntentCoordinator,RequestExecutor,DraftBuffer}.cs` | intent/receipt/控制状态、UI 可观察投影 | AC5/AC6/AC7 |
| `src/{ports/translation/protocol.py,infrastructure/providers/translation_openai.py,openai_client.py}` | request builder 边界：默认只读复用；如经 DSH 批准窄改，需证明现有 `payload_hash` 不等于 endpoint/model/body 全摘要 | AC2/AC3 |
| `tests/fea10/`（新）、`tests/core/test_{p13_run_runtime,p13_lifecycle_discriminators,fea00a_pipeline_seam,pipeline_defaults_assembly,pipeline_defaults_service}.py`、`tests/pipeline/` | Python 回归/新增 | AC1–AC7 |
| `NewManga.CoreClient.Tests/{CoreServiceIntegrationTests,WireTests}.cs` | 协议/回归 | AC8 |
| `NewManga.Host.Tests/{HostRuntimeIntegrationTests,RunMonitorTests,Fea10RunIpcTests}.cs` | 真实 Host/IPC/回归 | AC8 |
| `NewManga.ApplicationCore.Tests/{DraftBufferTests,IntentCoordinatorTests,RequestExecutorTests,RunMonitorTests,TestSupport}.cs`、`NewManga.App.Tests/{RunControllerTests,RunIndexTests}.cs` | state/projection/adapter 测试 | AC6/AC8 |
| `NewManga.Host.Tests/RunMonitorTests.cs` **不写**（该测试实际在 ApplicationCore.Tests） | — | — |

共享接口新增/改动须 DSH 明确授权；组合根仍 DSH 单点提交。

## Acceptance Criteria（草案）

- [ ] **AC1（Prepare 两阶段）**：`PrepareRun` 生成 `PreparedRunId/snapshotDigest/generation/expiresAt/displaySummary/redactedPayloadPreview` 且**零 DB 写、零执行**；`AcceptRun` 仅 digest 匹配后写 Run；候选过期→`RUN_PREVIEW_EXPIRED`；三码按 M2-C1 冻结投影。
- [ ] **AC2（快照完整与敏感面）**：settings/provider snapshot 为完整可重放值；缺失/不完整→`RUN_SNAPSHOT_INCOMPLETE`；敏感认证材料不入普通快照/日志/错误/证据；强类型白名单落盘（非整字典）。
- [ ] **AC3（预览 stale、配置隔离与 digest 语义）**：确认前目标/源/草稿/保护/配置变化→stale 拒绝零副作用；接受后 defaults/邻页变化不静默改变 payload。**`preparedDigest` 严格按冻结四元组算法校验**；另以 `payloadDigestPreview` 与 `payloadDigestSend` 比较（二者同源同值），**不要求四元组摘要与 payload 摘要相等**；邻页上下文不可变 pin 可验证。
- [ ] **AC4（retry 两分支）**：同键重放返回原 Run 不新建；新 key 的 `RetryFailedTargets` 新建 Run（`source_run_id`）、目标=失败页子集、上下文按接受时重读冻结；凭据/版本不可用→阻塞；新配置须差异确认创建关联任务，不写回旧 run。
- [ ] **AC5（candidate-only 与零提前写）**：以下每个条件均单独故障注入并断言 seam 未成功时 `regions.text_json`、`current_revision_id`、`region_revisions` 行数与前态完全相同、Run receipt/counts 不增加、candidate 可诊断/恢复、成功时 live/revision/Run receipt 同事务：① revision 冲突；② Lock；③ manual/final 保护；④ `STALE_RUN_SNAPSHOT`；⑤ source lease 失效；⑥ PageBinding generation 变化；⑦ draft token/sequence 不匹配；⑧ DB 失败；⑨ pause/cancel；⑩ prepare 后崩溃重启。断言限定为**成功提交回执/完成计数不增加**；允许失败/控制状态按冻结语义合法持久化。**事务单位**：a) C-13 多 Region 编辑 apply = 单 `BEGIN IMMEDIATE` 覆盖全部目标 Region（全有/全无，逐 Region expected map）；b) Pipeline step seam = 以 `StepId/TargetIds` 为单位的单事务（`commit_step_result`，含 Run receipt/counts）；两者不得混用 candidate 存储。
- [ ] **AC6（控制/完成口径）**：控制请求持久化≠状态改变；UI 不早于 Core 持久 status 显示 paused/cancelled；终态共同不变量（processing=0/waiting=0 + 各终态附加判据）；重启后同源可复读。
- [ ] **AC7（SC-R09 durable receipt）**：提交成功但响应丢失→同键重放找回原 `run_id`、无第二 Run；**关闭/重启 Core 并重开同一 DB 后同键仍找回原 Run**；同键异 fingerprint→`IDEMPOTENCY_KEY_REUSED`；相同 `request_id` 不同 key 视为两个操作；仅覆盖冻结三类带 key 操作（StartRun/RetryFailedTargets/ControlRun restart），不新增命令。
- [ ] **AC8（真实生产链路与回归）**：生产 assembly `Prepare/Accept/commit`；真实 Host↔Core IPC（`Fea10RunIpcTests`，`NEWMANGA_FEA10_IPC=1` 门径，隔离 DataRoot）；相关 pytest/.NET 全量不减少；旧 managed 路径、既有 Run 命令、`tests/core/test_p13_run_runtime.py` 等不回归。
- [ ] **AC9（范围/冻结/证据）**：C-05/C-15/C-16/C-07 冻结字节与 FEA-08/FEA-09 closeout 未改；范围 diff 合规；独立实现 Review approved；DSH 集成；Handoff + EV + Resource Manifest。
- [ ] **AC10（不越界）**：不提前实现 FEA-11/12/13/14 或 provider 新能力；不新增未冻结 Schema/wire；source 校验消费既有能力；共享组合根仅 DSH 单点提交。

## 验证矩阵（AC→文件→命令→断言→证据）

| AC | 测试文件（新增/复用） | 命令（CWD=`G:\CODEX\New Manga`） | 隔离环境 | 关键断言 | 证据 |
|---|---|---|---|---|---|
| AC1/AC2 | `tests/fea10/test_prepared_run.py`（新） | `python -m pytest tests/fea10 -q` | 临时 DataRoot/DB | Prepare 零 DB/零执行；过期/不完整码；敏感面 | `verification/FEA-10/logs/` |
| AC3/AC4 | `tests/fea10/test_snapshot_retry.py`（新）；复用 `tests/core/test_p13_run_runtime.py` | `python -m pytest tests/fea10 tests/core -q` | 临时 DB | 四元组 digest；payload digest 同值；stale；retry 两分支 | 同上 |
| AC5/AC6 | `tests/fea10/test_commit_zero_write.py`（新）；扩展 `tests/core/test_fea00a_pipeline_seam.py` | `python -m pytest tests/core tests/fea10 -q` | 隔离 DB | 10 条件逐项三处零变化/完成数不增；事务单位；控制 pending | 同上 |
| AC7 | `tests/fea10/test_idempotent_receipt.py`（新）+ `tests/fea10/support/restart_core.py` | 同上，并由 `restart_core.py` 停止/重启 Core 后重开同一 DB | `G:/CODEX/New Manga.workspace/FEA-10/` 下隔离根 | 丢 ACK/重启找回；异 fingerprint；request_id 非键 | 同上 |
| AC8 | `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea10RunIpcTests.cs`（新，`[Fact]`/env 门）；既有 .NET 回归 | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release`；`dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build`；`$env:NEWMANGA_FEA10_IPC='1'; $env:NEWMANGA_BUILD_PYTHON='C:/Python314/python.exe'; dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --no-build --filter FullyQualifiedName~Fea10RunIpcTests` | `G:/CODEX/New Manga.workspace/FEA-10/fixtures/<case>/`（每例唯一 DataRoot） | 生产 assembly/IPC；回归不减少；日志含命令/EXIT | `verification/FEA-10/logs/dsh/` |
| AC9/AC10 | `check.ps1`、`verify_pins.ps1`、`git diff --name-only` | `pwsh -NoProfile -File tools/governance/check.ps1`；`verify_pins.ps1` | 主工作树 | PASS/17/17/范围合规 | EV + Handoff |

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

## Closeout Record

- 未开始（proposed，scope review r4 待派发）。
