---
id: GATE3-SIDECAR-COVERAGE-1
title: 用新 sidecar 把 App 层 7 个 skip 转真实执行（条件 3 推进）
kind: evidence
governance_version: 3
status: done
disposition: "条件 3：书架只读 ⚠️ 格依赖 [WritePolicySidecarFact]；新 sidecar 已具备条件"
approval: DSH 2026-11-15（SIDECAR-REBUILD-1 已产出可用 sidecar）
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - SIDECAR-REBUILD-1
base_commit: 766719dcc
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GATE3-SIDECAR-COVERAGE-1
allowed_paths:
  - doc/tasks/GATE3-SIDECAR-COVERAGE-1.md
  - doc/reviews/GATE3-SIDECAR-COVERAGE-1-*.md
  - doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md
  - doc/reviews/MAINT-1-RELEASE-GATE-ASSESSMENT-2026-11-14.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/GOAL-PROGRESS-2026-11-02.md
  - verification/GATE3-SIDECAR-COVERAGE-1/**
---

# GATE3-SIDECAR-COVERAGE-1：App 层 skip 转真实执行

## 背景（已实测）

条件 3 矩阵（`MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md`）记录：三项目共 **111 skip**
（Host 74 + CoreClient 26 + **App 11**），其中 APP 的 **7 个**依赖 `NEWMANGA_CORECLIENT_SIDECAR_DIR`
（`WritePolicySidecarFact` 等）。矩阵里"书架只读"格因此标 **⚠️**。

`SIDECAR-REBUILD-1` 已产出可用 sidecar（`build/sidecar/core-sidecar/core-sidecar`，capabilities 17 条）。
**本轮实测**：带 `NEWMANGA_CORECLIENT_SIDECAR_DIR` 跑 App.Tests：

```
957 passed / 0 failed / 4 skipped / 961 total  (5m10s)
```
对比无夹具 **950 / 0 / 11 / 961** ⇒ **skip 11→4、pass +7，且 0 failed**。

剩余 4 个 skip 经查**全部是 opt-in gated**（非 sidecar 缺失）：
`PerformanceBaselineTests.Gated_HotSwitch_…`、`Fea07Residual3CrashTests.Park_…` / `Recover_…`、
`StartupDiagnosticsTests.RealProcessLaunchMatrix_…`。

## Acceptance Criteria

- [x] **AC1 定格实测数字**：记录带 sidecar 的 App.Tests 结果（`957/0/4/961`）与命令、
      环境变量、sidecar 路径与 `core_service.exe` 的 sha256；同时记录无夹具基线（`950/0/11/961`）。
- [x] **AC2 逐条确认 7 个转绿的测试**：列出**具体 `FullyQualifiedName`**，证明它们是真实执行
      （不是被 skip），且能对应到条件 3 矩阵里的格子。
- [x] **AC3 更新矩阵**：把"书架只读"格从 **⚠️** 改为 **✅**，并注明证据（`WritePolicyUiTests` 4 个 Fact
      在本环境实测 4 passed / 0 skipped）。
- [x] **AC4 更正 skip 总量**：矩阵 §5 的"111 skip"改为 **104**（Host 74 + CoreClient 26 + App 4），
      并说明 App 的 4 个是 opt-in gated、**不是** sidecar 缺失。
- [x] **AC5 剩余 4 个 skip 定性**：逐个写明为何仍 skip（gated 条件是什么），不做无根据归因。
- [~] **AC6 不回归**（**部分**：App 无夹具 950/0/11 未变、带夹具 957/0/4 实测；Host/CoreClient 未在本卡重跑）：无夹具三项目不劣化（App 950/0/11、Host 321/0/74、CoreClient 192/0/30）；
      带 sidecar 的 Host（349/2~3）与 CoreClient（214/4）不劣化。**不得放宽任何断言。**
- [x] **AC7 不虚报**：不得声称条件 3 满足 —— 仍有 opt-in skip、未纳范围的 GUI 流程、真机走查。

## 允许修改范围

见 frontmatter（只更新证据与矩阵，不改产品代码与测试断言）。

## 禁止范围

- 不得为"凑数字"而删除/跳过测试，或把 opt-in 测试改成普通测试。
- 不得声称 111→104 等于"覆盖问题解决"。
- 不得声称条件 3 MET。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 带 sidecar 跑 App.Tests | 新 sidecar | NOT_RUN | 无 |
| AC2 | 列出 7 个转绿 FQN | 同上 | NOT_RUN | 无 |
| AC6 | 无夹具 + 带夹具全量 | — | NOT_RUN | 无 |

## 依赖、风险与阻塞

- **风险 R1**：App.Tests 带 sidecar 需 5 分 10 秒（无夹具约 1-2 分）—— 记录耗时。
- **风险 R2**：7 个转绿测试中有依赖真实 IPC 的，可能受环境波动影响；需记录是否稳定（重跑一次）。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际测试：尚无。
- 后续记录日期、commit、环境、结果、遗留项。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) | sha256_basis |
|---|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | 待填 | NOT_APPLICABLE | — | — | 本卡无新增派生物 |

## Closeout Record

- Closeout date / DSH：2026-11-15，DSH（Lead / Architect / Integrator）。
- canonical_evidence_status：`complete`。
- resource_closeout_status：`complete`（无派生物）。
- 删除、迁移、归档数量/字节数：0。
- **结论（限定）**：
  - 带新 sidecar 跑 **App.Tests = `957 / 0 / 4 / 961`**（5m10s），无夹具 **`950 / 0 / 11 / 961`**
    ⇒ **skip 11→4、pass +7、0 failed**。
  - 差集确定的 **7 个转绿测试**已用定向 filter 复跑，**7 passed / 0 skipped**（FQN 见证据 §2）。
  - **条件 3 矩阵**：`书架只读` 格 **⚠️ → ✅**；并把"`WritePolicyUiTests` 与 `WritePolicyUiIntegrationTests`
    混称"这一处澄清。
  - **skip 口径更正**：无夹具 **111**（74+26+11）/ 带夹具 **48**（44+0+4）。今后引用必须写明口径。
- **未达成**：条件 3 **仍不判 MET** —— 仍有 **48 个带夹具 skip**、§0 未纳范围的 GUI 流程、真机走查。
- **未做**：Host（带夹具 349/2~3）与 CoreClient（214/4）**未在本卡重跑**（AC6 部分）。
  它们的数字来自 `CORE-PIPE-EXCLUSIVE-1` / `PIPE-EXCLUSIVE-TRANSPORT-1` 的实测，本卡未复核。
- **自登记**：本卡把"7 个转绿"识别出来时，**第一次用的 filter 写错了**（`FullyQualifiedName~App.Tests`
  这种整类过滤不会命中），导致两次空输出；改用"无夹具 11 skip 与带夹具 4 skip 的差集"才定位准确。
