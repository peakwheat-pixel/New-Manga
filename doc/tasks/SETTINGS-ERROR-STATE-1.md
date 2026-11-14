---
id: SETTINGS-ERROR-STATE-1
title: 设置页加载失败态的判别测试（闭合条件 3 矩阵唯一无覆盖格）
kind: test
governance_version: 3
status: in_progress
disposition: "GATE3-COVERAGE-MATRIX §3 唯一「完全无覆盖」格（错误态/设置）；DSH 2026-11-15 释放"
approval: DSH 2026-11-15（纯测试补强，零生产代码改动）
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - GATE3-COVERAGE-MATRIX
base_commit: 418801499
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/SETTINGS-ERROR-STATE-1
allowed_paths:
  - doc/tasks/SETTINGS-ERROR-STATE-1.md
  - doc/reviews/SETTINGS-ERROR-STATE-1-*.md
  - doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/GOAL-PROGRESS-2026-11-02.md
  - verification/SETTINGS-ERROR-STATE-1/**
  - apps/desktop-avalonia/tests/NewManga.App.Tests/**
---

# SETTINGS-ERROR-STATE-1：设置页加载失败态的判别测试

## 来源与目标

`GATE3-COVERAGE-MATRIX` §3 的矩阵里，**唯一一格"完全无覆盖"是「错误态 / 设置」** ——
当时只有 `SettingsPage_HostUnavailable_IsBrowsableButReadOnly`（只读态），没有"加载失败态"测试。

**开卡前先核实现（按纪律）**，结论是：**实现早已存在**，缺的只是测试。

- `SettingsViewModel.LoadAsync`（`SettingsViewModel.cs:139-171`）有 try/catch：捕获任何异常后
  设 `State = FluentPageState.Error`、`Error = $"设置读取失败（{ex.GetType().Name}），可以重试。"`。
- 另有若干失败路径同样设 `Error`（外观保存失败 `:215-219`、coordinator 未注入 `:184-185`、
  只读拒绝 `:191-192`、`reason` 路径 `:198-199`）。

⇒ **本卡不改生产代码**，只补"可判别、能在回退时变红"的测试，并把矩阵该格改判。

**一个可观察交付结果**：当设置读取抛异常时，界面进入错误态并显示可重试文案；若该行为被回退
（异常被吞掉、状态停在 `Loading`/`ReadOnly`、或错误文案消失），测试必须失败。

## Acceptance Criteria

- [x] **AC1 VM 级判别测试**：注入一个在列举设置数据时抛异常的 Host，`await LoadAsync()` 后
      断言 `State == FluentPageState.Error`、`Error` 含"设置读取失败"与"可以重试"。
- [x] **AC2 视图级判别测试**：在真实 shell 里驱动同一失败，断言设置页内容为 `SettingsPageView`
      且**错误态可见**（不只是 VM 字段）。
- [x] **AC3 判别力实测**：临时把 `LoadAsync` 的 catch 改为吞掉异常（或去掉 `State = Error`），
      断言 AC1/AC2 变红；记录实验并**必须还原**。
- [x] **AC4 矩阵改判**：把 `MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md` §3「错误态 / 设置」格
      从 ❌ 改为 ✅（带测试名 + 文件:行），并同步 §5 第 1/3 条与 Gate 评估 §15 中"唯一无覆盖"的表述。
- [x] **AC5 零回归**：`App.Tests` 全量 0 failed 且 skip **不增加**（当前 11）。
- [x] **AC6 零生产代码改动**：`git diff` 不触及 `apps/desktop-avalonia/src/**`。

## 允许修改范围

见 frontmatter。只新增测试、改矩阵该格与三指针。

## 禁止范围

- **不得**修改 `src/**`（实现已存在）。
- **不得**放宽既有断言、不得新增 skip/xfail。
- **不得**把"VM 字段为 Error"当作"界面显示错误态"的证据 —— AC2 必须走真实视图。
- 矩阵改判必须有测试依据，不得只改符号。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | `dotnet test --filter SettingsErrorStateTests` | 无夹具 | **3 passed**（其中 AC1 1 项） | `verification/SETTINGS-ERROR-STATE-1/README.md` |
| AC2 | 同上（`[AvaloniaFact]` 驱动真实视图树） | 无夹具 | **PASS**：断言出现"设置错误"banner + "重试"按钮 | 同上 |
| AC3 | 临时把 `LoadAsync` 的 catch 改为吞异常（`Status = "PROBE swallowed " + ex.GetType().Name`） | 无夹具 | **2 failed / 1 passed**（`Expected: Error / Actual: Loading`）；对照测试 `HealthyLoad_DoesNotShowTheErrorBanner` 正确保持绿；已 `git checkout` 还原，`src/**` diff 归零 | 同上 |
| AC5 | `dotnet test tests/NewManga.App.Tests` | 无夹具 | **950 / 0 / 11 / 961**（本卡前 947/0/11/958，skip 未增加） | `four-pieces.log` |
| AC6 | `git diff --stat -- apps/desktop-avalonia/src` | 仓库根 | **0**（零生产代码改动） | 同上 |

## 依赖、风险与阻塞

- **硬依赖**：`GATE3-COVERAGE-MATRIX`（该格的出处）。
- **风险 R1**：`FakeHostController` 现有方法是否支持"抛异常"？若不支持，需要给 fake 增加可控失败开关
  （属测试替身扩展，不是生产代码）。
- **风险 R2**：设置页在错误态下是否仍渲染 `SettingsPageView`（而不是被 state host 替换）？
  需按实际渲染逻辑断言，不得凭猜测写断言。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无（须独立上下文）。
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

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：待填。
- 当前指针清理：待关闭时更新 STATUS / Plan / TASK_LEDGER / rolling checkpoint。
