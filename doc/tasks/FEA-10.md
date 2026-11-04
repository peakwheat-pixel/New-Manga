---
id: FEA-10
title: 快照 / 候选 / 提交安全（PreparedRun 两阶段 + canonical request builder + retry 快照 + candidate-only apply）
kind: implementation
governance_version: 3
status: proposed
approval: pending scope review r2（Codex 2026-11-04 裁决首选；须先完成 FEA-10-PREREQ-1 协议注册）
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
  - src/application/tasks/
  - src/infrastructure/pipeline/
  - src/infrastructure/providers/
  - src/infrastructure/sqlite/
  - src/bootstrap/core_service.py
  - src/bootstrap/core_assembly.py
  - apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/
  - apps/desktop-avalonia/src/NewManga.CoreClient/Diagnostics/
  - apps/desktop-avalonia/src/NewManga.Host/
  - apps/desktop-avalonia/src/NewManga.App/Services/
  - apps/desktop-avalonia/src/NewManga.ApplicationCore/
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/
  - apps/desktop-avalonia/tests/NewManga.App.Tests/
  - apps/desktop-avalonia/tests/NewManga.ApplicationCore.Tests/
  - tests/core/test_p13_run_runtime.py
  - tests/core/test_fea00a_pipeline_seam.py
  - tests/core/test_pipeline_defaults_assembly.py
  - tests/core/test_pipeline_defaults_service.py
  - tests/fea10/
  - tests/pipeline/
out_of_scope:
  - 既有冻结契约字节（C-01b/C-05/C-08/C-13 等）与 M2-C1 wire 语义（协议注册归 FEA-10-PREREQ-1）
  - FEA-11/12/13/14 的范围；provider 新能力或新 UI 设计；source 重定位/同步实现
  - 真实用户数据/AppData/外部卷；push
  - 共享组合根（App.axaml/App.axaml.cs/NewManga.App.csproj/NewManga.sln）仅 DSH 单点提交
---

# FEA-10：快照 / 候选 / 提交安全

> 来源：`doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md` §10、§15.5、§15.6:931；`doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md`（SC-R01…SC-R09，已冻结 pin `453f993c…`）；`doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md`（SC-D07/SC-D08）；`doc/reviews/ADJ-2026-11-04-NEXT-TASK.md`（Codex 裁决 + DSH 修正硬前置 + 拆分裁定 r1）。
> 首轮只交卡/范围矩阵/契约缺口与独立 scope review；**不得写生产代码**。FEA-10 的 `ready` 以 `FEA-10-PREREQ-1` done 为硬前置。

## 目标

在 FEA-00A/03/09 已交付基础上，形成 **唯一 canonical request builder**、不可变 `PreparedRun`/payload、candidate-only 准备与受保护的原子提交链；保证「预览=实际发送」、已接受任务不被运行期配置/邻页变化改变、旧结果不越过最新人工修改。复用现有 Run store/scheduler/snapshot、revision/Lock CAS、`RegionStepWriter`/`SqliteTargetCatalog`/`DraftProtectionService`，不建立第二套业务真值或调度器。

## 范围（草案）

1. `PreparedRun` 两阶段（SC-R01/R04）：`PrepareRun` 只计算快照+摘要+`preparedDigest`，**零 DB 写、零执行**；`AcceptRun` 校验 digest 后写 `pipeline_runs`；stale→`RUN_STALE_PREVIEW`；候选在 Host 侧保存≤10min，过期→`RUN_PREVIEW_EXPIRED`。
2. canonical request builder（§10.1/§15.5）：预览与发送共用同一已确认对象；`preparedDigest`（C-08 四元组）与**实际发送 payload digest**分别记录并断言一致；敏感认证材料不入普通快照/日志。
3. retry 快照来源（SC-R08）：同键重放不新建；新 key 的 `RetryFailedTargets` 新建 Run、目标=失败页子集、上下文按接受时重读冻结；凭据/版本不可用→阻塞；新配置须差异确认创建关联任务。
4. candidate-only 准备与原子 apply（C-13 SC-D07/08、§10.3/§15.5）：结果先入 candidate/staging；提交事务重验 source lease、PageBinding generation、revision、Lock/manual/final、draft token/sequence；失败/冲突时 live 文本、current 指针、revision 行数零提前变化；candidate 可诊断/恢复；成功时 live/revision/Run receipt 同事务。
5. 控制/完成口径（SC-R06/R07）与 SC-R09 durable receipt：接受≠状态改变；完成只认 Core 持久状态与 counts 不变量；提交成功但响应丢失后同键重放找回原 Run；同键异 fingerprint 拒；`request_id` 不能充当去重键。
6. 真实生产 assembly 回归与真实 Host↔Core IPC；相关 pytest/.NET 测试、证据与 Handoff；上下文独立 Review。

## Acceptance Criteria（草案）

- [ ] **AC1（Prepare 两阶段）**：`PrepareRun` 生成 `PreparedRunId/snapshotDigest/generation/expiresAt/displaySummary/redactedPayloadPreview` 且**零 DB 写、零执行**；`AcceptRun` 仅在 digest 匹配时写 Run；候选过期→`RUN_PREVIEW_EXPIRED`；三种错误码按 M2-C1 冻结投影。
- [ ] **AC2（快照完整与敏感面）**：settings/provider snapshot 为完整可重放值；缺失/不完整→`RUN_SNAPSHOT_INCOMPLETE`；敏感认证头/密钥不入普通快照、日志、错误、证据；强类型白名单落盘（非整字典）。
- [ ] **AC3（预览 stale 与配置隔离）**：确认前目标/源/草稿/保护/配置变化→stale 拒绝零副作用；接受后 defaults/邻页变化不静默改变 payload；`preparedDigest` 四元组与**实际 endpoint/model/body/blob digest/影响行为参数**一致；邻页上下文不可变 pin 可验证。
- [ ] **AC4（retry 两分支）**：同键重放返回原 Run 不新建；新 key 的 `RetryFailedTargets` 新建 Run（`source_run_id`）、目标=失败页子集、上下文按接受时重读冻结；凭据/版本不可用→阻塞；用户新配置须差异确认创建关联任务，不写回旧 run。
- [ ] **AC5（candidate-only 与零提前写）**：构造 revision/Lock/`STALE_RUN_SNAPSHOT`/DB 失败/pause/cancel/崩溃重启，seam 未成功时 `regions.text_json`、`current_revision_id`、`region_revisions` 行数与前态完全相同，Run receipt 不增加完成数；candidate 可诊断/恢复；成功时 live/revision/Run receipt 同事务。**区分** C-13 多 Region 编辑 apply 与 Pipeline step seam 的事务单位，不混用两层 candidate。
- [ ] **AC6（控制/完成口径）**：接受后控制请求持久化≠状态改变；UI 不早于 Core 持久 status 显示 paused/cancelled；终态共同不变量（processing=0/waiting=0 + 各终态附加判据）；重启后同源可复读。
- [ ] **AC7（SC-R09 durable receipt）**：提交成功但响应丢失→同键重放找回原 `run_id`、无第二 Run；同键异 fingerprint→`IDEMPOTENCY_KEY_REUSED`；相同 `request_id` 不同 key 视为两个操作；仅覆盖冻结的三类带 key 操作（StartRun/RetryFailedTargets/ControlRun restart），不新增命令。
- [ ] **AC8（真实生产链路与回归）**：生产 assembly prepare/commit；真实 Host↔Core IPC；相关 pytest/.NET 全量不减少；旧 managed 路径、既有 Run 命令行为、`tests/core/test_p13_run_runtime.py` 等不回归。
- [ ] **AC9（范围/冻结/证据）**：C-05/C-15/C-16/C-07 冻结字节与 FEA-08/FEA-09 closeout 未改；范围 diff 合规；独立实现 Review approved；DSH 集成（build/test/check/pins/真实 IPC）；Handoff + EV + Resource Manifest。
- [ ] **AC10（不越界）**：不提前实现 FEA-11/12/13/14 或 provider 新能力；不新增未冻结 Schema/wire；source 校验消费既有能力；共享组合根仅 DSH 单点提交。

## 验证矩阵（AC→测试→命令→断言→证据）

| AC | 测试文件（新增/复用） | 命令 | 隔离环境 | 关键断言 | 证据 |
|---|---|---|---|---|---|
| AC1/AC2 | `tests/fea10/test_prepared_run.py`（新） | `python -m pytest tests/fea10 -q` | 临时 DataRoot | Prepare 零 DB 写/零执行；过期码；快照完整/敏感面 | `verification/FEA-10/logs/` |
| AC3/AC4 | `tests/fea10/test_snapshot_retry.py`（新）；复用 `test_p13_run_runtime.py` | 同上 + `tests/core` | 临时 DB | digest 一致；stale；同键/新键两分支；新配置差异 | 同上 |
| AC5/AC6 | `tests/core/test_fea00a_pipeline_seam.py`（扩展）+ `tests/fea10/test_commit_zero_write.py`（新） | `python -m pytest tests/core tests/fea10 -q` | 隔离 DB | 三处零变化；receipt 不增加；控制 pending；同事务 | 同上 |
| AC7 | `tests/fea10/test_idempotent_receipt.py`（新） | 同上 | 临时 DB/重启脚本 | 丢 ACK 找回；异 fingerprint 拒；request_id 非键 | 同上 |
| AC8 | 上述 + `dotnet test` 全量 + 真实 IPC 用例（`NEWMANGA_FEA09_IPC=1` 门径扩展或新门） | `dotnet build`；`dotnet test`；真实 IPC | 隔离 fixture | 生产 assembly/IPC 通过；回归不减少 | `verification/FEA-10/logs/dsh/` |
| AC9/AC10 | `check.ps1`、`verify_pins.ps1`、范围 diff | 治理命令 | 主工作树 | PASS/17/17/范围合规 | EV + Handoff |

## 依赖与硬前置

- 已完成：FEA-00A-IMPL-1（三处零变化/candidate 基础）、FEA-03、FEA-09。
- **硬前置 `FEA-10-PREREQ-1`**：C-08 块②协议注册（M2-C1 rev 2.12 + host `allowedRunErrorCodes`）；未 done 前本卡不得 ready/实施。
- 契约依据：C-08（pin `453f993c…`）、C-13/SD07-08、C-05/C-04b 接口；M2-C1/P11 既有命令语义；不新增 wire。
- 与 C-04b 的共享块②：C-08 冻结记录 §3 原要求「与 C-04b 共用 Task、分提交/AC」；DSH 在 ADJ 裁定**拆分**（C-04b 已冻结且删除线不属 FEA-10 范围，硬前置独立成 PREREQ-1），记录替代安排；不得据此改 C-04b/删除线语义。

## 既有实现复用（不得重建）

`PipelineService.accept_start_run/accept_retry_failed_targets/commit_step_result`、`RegionStepWriter`、`SqliteTargetCatalog.commit_step`、`DraftProtectionService`、`FrozenRunSnapshots`/`PipelineStore`、现有 Run 命令 dispatch（`src/bootstrap/core_service.py` `_RUN_COMMANDS`）；如有缺口只在既有 seam 加深，不新建同类存储/调度器。

## 首轮交付（建卡阶段）

1. Task 卡（本文件）+ 范围矩阵/契约缺口；
2. 精确 allowed_paths（建卡阶段由 DSH 缩到实际文件）；
3. 独立 scope review（全新 Codex）报告 + DSH 处置；
4. 不写生产代码、不 push。

## Closeout Record

- 未开始（proposed，scope review r2 待派发）。
