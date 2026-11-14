---
id: GATE3-HOST-SKIP-TRIAGE-1
title: Host 44 个带夹具 skip 的逐条归因 —— opt-in 后 skip 44→1，但暴露 schema 版本兼容问题
kind: evidence
governance_version: 3
status: done
disposition: "条件 3：Host 44 skip 需归因；实测发现它们要 opt-in 变量而非 sidecar，且 opt-in 后暴露 schema 9 vs 14"
approval: DSH 2026-11-15
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - GATE3-SIDECAR-COVERAGE-1
base_commit: 7b661e193
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/GATE3-HOST-SKIP-TRIAGE-1
allowed_paths:
  - doc/tasks/GATE3-HOST-SKIP-TRIAGE-1.md
  - doc/reviews/GATE3-HOST-SKIP-TRIAGE-1-*.md
  - doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md
  - doc/reviews/MAINT-1-RELEASE-GATE-ASSESSMENT-2026-11-14.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/GOAL-PROGRESS-2026-11-02.md
  - verification/GATE3-HOST-SKIP-TRIAGE-1/**
---

# GATE3-HOST-SKIP-TRIAGE-1：Host skip 归因

## 1. 44 个 skip 的真实原因（实测）

带 sidecar（`NEWMANGA_CORECLIENT_SIDECAR_DIR`）跑 Host.Tests ⇒ **44 skip**（与矩阵 §4.2 一致）。

抽 4 个类的 attribute 看条件：

| 属性 | 条件 |
|---|---|
| `Fea11ScanIpcFact` | `NEWMANGA_FEA11_IPC != "1"` ⇒ skip |
| `Fea07Residual3A03Fact` / `Fea12IpcFact` / `Fea11Residual4AIpcFact` | 同类模式 |

**全 Host.Tests 的 opt-in 变量统计**：

```
22 次  NEWMANGA_BUILD_PYTHON
 8 次  NEWMANGA_FEA11_IPC
 3 次  NEWMANGA_EVIDENCE_DIR
 3 次  NEWMANGA_FEA09_IPC
 2 次  NEWMANGA_FEA11_CRASH_STATE
 1 次  NEWMANGA_CORE_TILE_E2E / FEA10_IPC / FEA11_CRASH_NEGATIVE / FEA12_UI_IPC /
        REAL_SHELL / REAL_SHELL_ROOT / WORKSPACE_ROOT
```

⇒ **44 个 skip 需要 opt-in 开关，不是 sidecar 缺失**。这与矩阵 §5 旧口径（"大部分需 sidecar"）**不完全一致**。

## 2. 打开 opt-in 后的实测（★ 重要）

设 `NEWMANGA_FEA11_IPC=1`、`NEWMANGA_FEA09_IPC=1`、`NEWMANGA_FEA12_UI_IPC=1`、
`NEWMANGA_FEA10_IPC=1`、`NEWMANGA_BUILD_PYTHON=C:\Python314\python.exe`、
`NEWMANGA_WORKSPACE_ROOT=<workspace>` + sidecar 目录，跑 Host.Tests 全量：

```
379 passed / 15 failed / 1 skipped / 395   (1m10s)
```

对比带夹具（未开 opt-in）：**349 / 2~3 / 44 / 395**

| 指标 | 未开 opt-in | 开 opt-in |
|---|---|---|
| pass | 349 | **379**（+30） |
| fail | 2~3 | **15**（+12） |
| skip | 44 | **1**（-43） |

## 3. 15 个失败的归因（逐条）

| # | 测试 | 归因 | 性质 |
|---|---|---|---|
| 1–3 | `Fea09RealIpcTests.ReferencedImportAndResolveOverRealStdio`、`Fea09UiImportIpcProductionTests.E_…` / `G_…` / `H_…` | `SidecarExeMissing: executable not found: python` 或 `FILE_IDENTITY_CHANGED` / `new container must produce a changed page` | **环境**：`C:\Python314` 缺 Python Core 依赖（torch 等） |
| 4–7 | `Fea11HostAuthIpcTests.Recovery_…` / `CrashPoint_Park` / `Ack_…` / `CrashPoint_Recover` | `NEWMANGA_FEA11_CRASH_STATE is required` + `Assert.Equal Expected: 9` | **环境**（另一个 opt-in 变量未设）+ schema |
| 8–11 | `Fea11Residual4AIpcTests.ProductionDispatcher*`（4 个） | `Assert.Equal Expected: 9` | **schema** |
| 12–13 | `Fea11SourceIpcTests.FullSyncChain_…` / `HostControlSurfaceRefuses…` | `Assert.Equal Expected: 9` | **schema** |
| 14 | `GrantIssuerTests.Import_IntoNewChapter_…` | （原有，与 opt-in 无关） | — |
| 15 | `Fea11WatchHostRuntimeTests.Ready_ArmsWatcher_…` | `SOURCE_REGISTRY_BUSY`（已知 flaky） | 原有 |

## 4. ★ 核心发现：`schema_version` 硬编码 9 vs 新 sidecar 的 v14

3 处硬编码：

```
Fea11HostAuthIpcTests.cs:418   Assert.Equal(9, seed.GetProperty("schema_version").GetInt32());
Fea11Residual4AIpcTests.cs:719 Assert.Equal(9, seed.GetProperty("schema_version").GetInt32());
Fea11SourceIpcTests.cs:63      Assert.Equal(9, receipt.GetProperty("schema_version").GetInt32());
```

而新 sidecar（`SIDECAR-REBUILD-1` 产物）启动时打印
`[core.schema] applied 14 migration(s) up to v14` ⇒ **schema_version = 14**。

⇒ **至少 7 个失败是"测试硬编码旧 schema 版本"，不是产品缺陷。**

**但这本身是个真实问题**：换 sidecar（schema 升级）会让这些测试变红。
**本卡不修**，原因：
1. 改成 `== 14` 只是把硬编码换个数字，下次迁移还会红；
2. 改成 `>= 9` 会**放宽断言**（纪律禁止）；
3. 正确做法（从产品常量读 / 断言 `>= 9 且 <= 当前最大值`）需要 DSH 裁决是否算"放宽"，
   且要确认 v14 是**预期**的产品 schema 版本（不是本地漂移）。

## 5. 对条件 3 的影响（诚实口径）

- **好消息**：44 skip 里 **43 个在 opt-in 下真的执行了**（skip 44→1）——
  这比"44 个都跑不了"好得多，且证明了覆盖**存在**而非缺失。
- **坏消息**：执行后 **15 个红**，其中 **7+ 是 schema 版本不一致**、**7 是环境缺依赖**。
  ⇒ **不能**说"条件 3 变好了"；只能说"**覆盖是可执行的，但换 sidecar 引入了版本兼容缺口**"。
- **条件 3 仍不判 MET。**

## 6. 未做

- 未逐个核对剩余 29 个（44 - 15 已归因）失败/通过的具体分类；本卡只抓了失败集。
- 未确认 `schema_version=14` 是否为**预期产品版本**（可能是本地 workspace 漂移）。
- 未处理 `NEWMANGA_FEA11_CRASH_STATE` 等剩余 opt-in 变量。
