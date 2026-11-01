---
id: FEA-04
title: FEA-04 Current 适配（Frontends.Current + V2 state/route/VM adapter；保留旧入口）
kind: implementation
governance_version: 3
status: proposed
approval: dsh_ruling_2026-11-02_GOAL_FEA04
suggested_owner: zcode
owner: zcode
reviewer: fea04-scope-reviewer
depends_on:
  - FEA-02-CORE
  - FEA-03
base_commit: 91be6c134
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
review_appointment: "doc/reviews/FEA-04-scope-r1.md（reviewer fea04-scope-reviewer，DSH fresh 独立上下文派发）"
evidence_dir: verification/FEA-04
allowed_paths:
  - doc/tasks/FEA-04.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/**
  - doc/handoffs/FEA-04-*.md
  - apps/desktop-avalonia/src/NewManga.App/Views/V2/**
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/**
  - apps/desktop-avalonia/src/NewManga.App/Shell/V2/**
  - apps/desktop-avalonia/tests/**
  - verification/FEA-04/**
---

# FEA-04 Current 适配（范围冻结 v1，待独立复核）

## 来源与授权

1. 方案 §12.1 `:642`：S1 `FEA-04` Current 适配——交付 `Frontends.Current`、V2 state/route/VM adapter、**保留旧入口**；验收「当前可用行为不退化；无 VM 私有第二份业务真值；关闭/重建内容不 Dispose Host，不隐式 Start」。
2. 方案 §15.6 `:924`：写域 = `Views/V2/`、`ViewModels/V2/`、`Shell/V2/` 中 DSH 划分的 ui-shell/ui-studio 子目录及对应 tests；L3；§15.3 每字段迁出、现有行为基线与 fail-closed。
3. 方案 §15.3 `:876-886`：6 行现有字段迁出表（见下）。
4. 依赖：`FEA-02-CORE` done（ApplicationCore）、`FEA-03` done（draft journal/edit token/apply seam，集成 `76d947923`）。
5. **DSH 裁决**（[GOAL-PROGRESS](../checkpoints/GOAL-PROGRESS-2026-11-02.md)）：释放 FEA-04；owner 为 **ZCode**（方案指定设计/UI 主责）；若 ZCode 不可用，DSH 可指派 Codex 并按同一范围冻结执行。

## 冻结设计规则

### R-CURRENT（旧入口与行为基线）
- **R-CURRENT-1**：保留现有入口（V2/Current 既有路由与启动路径），不得删除或改名既有公开入口；新增适配层只能是**增量**。
- **R-CURRENT-2**：以现有测试为行为基线（`apps/desktop-avalonia/tests/**` 中 V2/Shell/VM 相关用例 + `dotnet test`）；不退化 = 基线用例全通过且关键断言不被弱化。
- **R-CURRENT-3**：`Frontends.Current` 门面只做**转发与状态映射**，不复制业务规则；任何业务真值仍在 Host/Core/ApplicationCore。

### R-STATE（§15.3 六项迁出）
- **R-STATE-1**：逐项迁出（表见下），每项须有「现状字段 → 新权威源 → 验收断言」三列证据。
- **R-STATE-2**：未迁出项**不得**静默丢弃：切换前 preflight 检测到未迁出且有损编辑态 → **fail-closed**（中止切换、保留旧树与缓冲）。
- **R-STATE-3**：VM 不得持有第二份业务真值（无私有 registry/缓存作为权威）；只允许 UI memento/选择态，且须在 Handoff 列出「允许的 UI 私有状态」清单。
- **R-STATE-4**：关闭/重建内容（窗口、view）**不得** Dispose Host；**不得**隐式 `Start`/重启 Core；Host 生命周期仍由既有 Host 装配决定。

### R-SWITCH（切换与恢复）
- **R-SWITCH-1**：`switch` 入口（Current ↔ Fluent）在 FEA-05 之前只允许**同进程**、由显式命令触发；preflight 失败 → 保持 Current 并返回结构化错误（不抛未处理异常）。
- **R-SWITCH-2**：切换前后 Run/reader 投影状态必须来自同一共享源（Host/Core），不得在 VM 内重建；切换不触发新的 Run。

## §15.3 迁出表（冻结）

| # | 现有源/字段 | 目标权威 | 迁出/验收 |
|---|---|---|---|
| S1 | `StudioInspectorViewModel._pendingRegionType` | EditingSession/DraftId + Core journal | 未保存 region type 切换前 flush；失败留旧 UI；保存失败仍可编辑 |
| S2 | `StudioPageViewModel._pendingNavigation/_lastRerenderSummary/_runProjection` | 意图 receipt/会话 UI memento/共享 Run 投影 | 未决确认不自动执行；旧回调不得重放；页面切换无投影回退 |
| S3 | `StudioBatchViewModel._runId/_projection/_intentIdempotencyKey` | RunMonitor + session intent store | 切 UI 相同 run/key；丢 ACK 后重试不二次启动 |
| S4 | `ReaderOverlayViewModel` book/pages/index/mode/direction/scroll | ReaderSession + Core 进度/按书偏好 | 保留 page ID 与语义锚点；未能无损映射则报告并留旧状态 |
| S5 | `ConsoleViewModel` monitor/筛选/选择 | 一个共享 RunMonitor + 会话筛选 | 切 UI 保留筛选；单轮每 Run 最多一次 snapshot/projection 查询 |
| S6 | `ShellState` selection/space/filter/surface stack；ThemeStudio editor draft | 跨 scheme Session 选择、UI memento、Appearance draft | 可映射逐项验证；未映射编辑/预览阻止切换，不能静默丢弃 |

## 验收标准（冻结版）

- [ ] **AC1 旧入口保留**：既有入口文件/路由/启动路径不改名不删除；`git diff` 显示只增不改（除必要的适配接线，需在 Handoff 逐处说明）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC2 行为基线不退化**：`dotnet test apps/desktop-avalonia/tests/**` 全通过（含 V2/Shell/VM 用例）；基线用例清单与前后计数写入 Handoff。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC3 无第二份业务真值**：VM 私有状态清单（Handoff）逐项说明「UI 态 vs 业务态」；业务态读取统一经 Host/Core/ApplicationCore；静态检查（grep 私有 registry/缓存）无新增权威副本。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC4 §15.3 六项迁出**：S1–S6 每项有「现状→新权威→断言」证据；未迁出项明确登记。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC5 fail-closed 切换**：存在未迁出且有损编辑态时切换被拒（结构化错误 + 旧树保留 + 缓冲不丢）；无未迁出项时切换成功且不触发新 Run。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC6 生命周期**：关闭/重建内容不 Dispose Host、不隐式 Start；Host 对象身份在前后不变（断言）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC7 回归与证据**：`dotnet test` 日志、基线对照表、v-matrix 证据入 `verification/FEA-04/**`。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC8 独立复核**：范围复核 r2 `approved`（P0/P1=0）；实现复核 `doc/reviews/FEA-04-r1.md` approved（P0/P1=0）。 <<PARTIAL: 范围冻结；待派发>>

## L 前置适用性判定

| 保留项 | 判定 | 再触发 |
|---|---|---|
| **L-1** 四表 DDL | **NOT_APPLICABLE**：不触 Source 四表、不改 `schema.py` | 需新表/迁移 → `blocked` |
| **L-2** M2-C1 字节修订 | **NOT_APPLICABLE**：不新增 wire 码（只看现有命令面）；若需新命令/码 → `blocked` | 新增 Host/Core 命令或 wire 码 → `blocked` |
| **L-5** 整库恢复锁 | **NOT_APPLICABLE**：不触备份/恢复 | 触恢复 → `blocked` |

## 禁止范围

- 不改 Host/Core/CoreClient/ApplicationCore 的公开契约与命令面；不新增 wire 码。
- 不改 `schema.py`/migrations、冻结契约字节、`doc/reviews/**`。
- 不实现 FEA-05（Fluent 独立界面）与 FEA-06 起的 UI 功能；本卡只做 Current 适配与切换 preflight。
- 不动用户数据、不 push、不合并 main；不降低既有测试断言。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

实现尚未开始。开始时在 `G:\CODEX\New Manga.workspace\` 建 task-env/worktree（分支 `feat/fea-04`）并补齐本表。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| doc-task | `doc/tasks/FEA-04.md` | NOT_APPLICABLE | - | - | 范围冻结；未访问用户数据 |
| build/temp（未来） | - | PENDING | ..\New Manga.workspace\ | - | 实现开始前补齐 |

## Closeout Record

- 2026-11-02：DSH 裁决释放（GOAL FEA-04；owner=ZCode，ZCode 不可用时 DSH 可指派 Codex）；范围冻结 v1；`proposed`，待上下文独立复核 r1。
