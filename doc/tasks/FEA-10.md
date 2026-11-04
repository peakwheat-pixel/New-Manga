---
id: FEA-10
title: 快照 / 候选 / 提交安全（PreparedRun 两阶段 + canonical request builder + retry 快照 + candidate-only apply）
kind: implementation
governance_version: 3
status: proposed
approval: pending scope review（Codex 2026-11-04 裁决首选；须先完成 FEA-10-PREREQ-1 协议注册）
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
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/
  - apps/desktop-avalonia/src/NewManga.CoreClient/Diagnostics/
  - apps/desktop-avalonia/src/NewManga.Host/
  - apps/desktop-avalonia/src/NewManga.App/Services/
  - apps/desktop-avalonia/tests/
  - apps/desktop-avalonia/src/NewManga.ApplicationCore/
out_of_scope:
  - 既有冻结契约字节（C-01b/C-05/C-08/C-13 等）与 M2-C1 wire 语义（协议注册归 FEA-10-PREREQ-1）
  - FEA-11/12/13/14 的范围；provider 新能力或新 UI 设计
  - 真实用户数据/AppData/外部卷；push
  - 共享组合根（App.axaml/App.axaml.cs/NewManga.App.csproj/NewManga.sln）仅 DSH 单点提交
---

# FEA-10：快照 / 候选 / 提交安全

> 来源：`doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md` §10、§15.5、§15.6:931；`doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md`（SC-R01…SC-R09，已冻结）；`doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md`（SC-D07/SC-D08）；`doc/reviews/ADJ-2026-11-04-NEXT-TASK.md`（Codex 裁决首选 + DSH 修正硬前置）。
> 首轮只交卡/范围矩阵/契约缺口与独立 scope review；**不得写生产代码**。FEA-10 的 `ready` 以 `FEA-10-PREREQ-1` done 为硬前置。

## 目标

在 FEA-00A/03/09 已交付的基础上，形成 **唯一 canonical request builder**、不可变 `PreparedRun`/payload、candidate-only 准备与受保护的原子提交链；保证「预览=实际发送」、已接受任务不被运行期配置/邻页变化改变、旧结果不越过最新人工修改。复用现有 Run store/scheduler/snapshot 与 revision/Lock CAS，不建立第二套业务真值。

## 范围（草案）

1. `PreparedRun` 两阶段（SC-R01）：`PrepareRun` 只计算快照+摘要+`preparedDigest`，不写 DB、不触发执行；`AcceptRun` 校验 digest 后写 `pipeline_runs`；stale → `RUN_STALE_PREVIEW`；候选 store 在 Host（SC-R04）。
2. canonical request builder（§10.1/§15.5）：预览与发送共用同一对象；认后 defaults 变化不改变 payload；邻页/上下文内容不可变 pin 入快照；摘要覆盖 endpoint/model/body/blob digest/参数。
3. retry 快照来源（SC-R08）：默认失败重试创建关联 Run、复用源 Run 的**目标集合**，但上下文/设置按接受时重新读取冻结；凭据/版本不可用则阻塞；用户选择新配置须展示差异并确认创建关联新任务；同键重放不新建。
4. candidate-only 准备与原子 apply（C-13 SC-D07/08、§10.3/§15.5）：结果先入 candidate/staging；提交事务重验 source lease、PageBinding generation、revision、Lock/manual/final、draft token/sequence；失败/冲突时 live 文本、current 指针、revision 行数零提前变化；candidate 可诊断/恢复。
5. 控制/完成口径（SC-R06/R07）：接受≠状态改变；完成只认 Core 持久状态与 counts 不变量；UI 不提前展示 paused/cancelled。
6. 真实生产 assembly 回归与真实 Host↔Core IPC；相关 pytest/.NET 测试、证据与 Handoff。

## Acceptance Criteria（草案）

- [ ] **AC1 唯一 request builder + 快照完整**：预览与发送从同一已确认对象生成；`preparedDigest` 覆盖目标/设置/provider 绑定/约束；`settings/provider` 为完整可重放值；缺失→`RUN_SNAPSHOT_INCOMPLETE`；敏感认证材料不入普通快照/日志。
- [ ] **AC2 预览 stale 与配置变化隔离**：确认前目标/源/草稿/保护/配置变化 → stale 拒绝且零副作用；接受后 defaults/邻页变化不静默改变 payload；邻页原文/不可变 blob pin 可验证。
- [ ] **AC3 retry 两分支**：同键重放返回原 Run 不新建；新 key 的 `RetryFailedTargets` 新建 Run、目标=失败页子集、上下文按接受时重读冻结；凭据/版本不可用→阻塞；新配置须差异确认。
- [ ] **AC4 candidate-only + 零提前写**：构造 revision/Lock/`STALE_RUN_SNAPSHOT`/DB 失败/pause/cancel/崩溃重启，seam 未成功时 `regions.text_json`、`current_revision_id`、`region_revisions` 行数与前态完全相同；candidate 可诊断/恢复；成功同事务。
- [ ] **AC5 控制/完成口径**：接受后控制请求持久化≠状态改变；UI 不早于 Core 持久 status 显示 paused/cancelled；终态 counts 不变量与重启后同源可复读。
- [ ] **AC6 真实生产链路与回归**：生产 assembly prepare/commit；真实 Host↔Core IPC；相关 pytest/.NET 全量不减少；旧 managed 路径、既有 Run 命令行为不回归。
- [ ] **AC7 范围/冻结/证据**：C-05/C-15/C-16/C-07 冻结字节与 FEA-08/FEA-09 closeout 未改；范围 diff 合规；独立实现 Review approved；DSH 集成（build/test/check/pins/真实 IPC）；Handoff + EV + Resource Manifest。
- [ ] **AC8 不越界**：不提前实现 FEA-11/12/13/14 或 provider 新能力；不新增未冻结 Schema/wire；共享组合根仅 DSH 单点提交。

## 依赖与硬前置

- 已完成：FEA-00A-IMPL-1（三处零变化/candidate 基础）、FEA-03、FEA-09。
- **硬前置 `FEA-10-PREREQ-1`**：C-08 块②协议注册（M2-C1 rev 2.12 + host `allowedRunErrorCodes`）；未 done 前本卡不得 ready/实施。
- 契约依据：C-08（冻结 pin `453f993c…`）、C-13/SD07-08、C-05/C-04b 接口；M2-C1/P11 既有命令语义；不新增 wire（防止在实现阶段临时扩协议）。

## 验证等级与证据

- 等级：**L2 高风险** + 隔离故障注入 + 真实 IPC；UI 可观察行为涉及处补 L3，不得 fake 替代。
- 记录命令、环境、EXIT、skip/BLOCKED/NOT_RUN；证据 `verification/FEA-10/**`；Review 上下文独立（2026-10-31 规则）。

## 首轮交付（建卡阶段）

1. Task 卡（本文件）+ 范围矩阵/契约缺口列表；
2. 精确 allowed_paths（建卡阶段由 DSH 缩到实际文件）；
3. 独立 scope review（全新 Codex）报告 + DSH 处置；
4. 不写生产代码、不 push。

## Closeout Record

- 未开始（proposed，scope review 待派发）。
