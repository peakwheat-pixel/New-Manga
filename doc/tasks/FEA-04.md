---
id: FEA-04
title: FEA-04 Current 适配（Frontends.Current + V2 state/route/VM adapter；保留旧入口）
kind: implementation
governance_version: 3
status: proposed
approval: dsh_ruling_2026-11-02_GOAL_FEA04_Q16_Q19
suggested_owner: zcode
owner: zcode
reviewer: fea04-scope-reviewer
depends_on:
  - FEA-02-CORE
  - FEA-03
base_commit: e34796862
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
  - apps/desktop-avalonia/src/NewManga.App/NewManga.App.csproj
  - apps/desktop-avalonia/src/NewManga.App/Views/V2/**
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/**
  - apps/desktop-avalonia/src/NewManga.App/Shell/V2/**
  - apps/desktop-avalonia/tests/**
  - verification/FEA-04/**
---

# FEA-04 Current 适配（范围冻结 v2，待独立复核）

## 来源与授权

1. 方案 §12.1 `:642`：S1 `FEA-04` Current 适配——交付 `Frontends.Current`、V2 state/route/VM adapter、**保留旧入口**；验收「当前可用行为不退化；无 VM 私有第二份业务真值；关闭/重建内容不 Dispose Host，不隐式 Start」。
2. 方案 §15.6 `:924`：写域 = `Views/V2/`、`ViewModels/V2/`、`Shell/V2/` 及对应 tests；L3；§15.3 每字段迁出、现有行为基线与 fail-closed。
3. 方案 §15.3 `:876-886`：6 行现有字段迁出表（S1–S6）。
4. 依赖：`FEA-02-CORE` done（ApplicationCore）、`FEA-03` done（draft journal/edit token/apply seam，集成 `76d947923`）。
5. **DSH 裁决**（[GOAL-PROGRESS-2026-11-02](../checkpoints/GOAL-PROGRESS-2026-11-02.md) Q-12/Q-16…Q-19）：
   - **Q-16（处置 r1-F-01）**：本卡**不实现 wire**（不改 Host/CoreClient/命令面）；S1–S3 的"目标权威"收窄为 **ApplicationCore 本地权威**（`DraftBuffer`/`IntentCoordinator`/`RunMonitor`/会话 memento）；wire 接线由 `FEA-05`（Fluent 独立界面）或 `FEA-07`（运行期切换）在其范围内承担，并在本卡 Handoff 登记 deferral。
   - **Q-17（处置 r1-F-02）**：`NewManga.App.csproj` 加 `NewManga.ApplicationCore` 引用为 **DSH 单点授权的唯一例外**（本卡写域已列该文件）；提交时在 Handoff 记录该单点。
   - **Q-18（处置 r1-F-03）**：`Frontends.Current` 落 **`Shell/V2/Frontends/`**（in-app 门面），不新建工程、不改 sln。
   - **Q-19（处置 r1-F-04）**：`switch` **只做 preflight**（判定 + fail-closed 结果），**不实现**切换入口、不启动 Fluent；运行期切换由 `FEA-07` 承担。

## 冻结设计规则

### R-CURRENT
- **R-CURRENT-1**：既有入口的**公开签名与路由**不改名、不删除（`Views/V2`、`ViewModels/V2`、`Shell/V2` 内部实现可改）；新增适配层只做增量。
- **R-CURRENT-2**：行为基线 = `dotnet test apps/desktop-avalonia/tests` 现有用例（以 `FEA-03` 合并后 `91be6c134` 为冻结点）全通过；基线用例清单与前后计数写入 Handoff，关键断言不得弱化。
- **R-CURRENT-3**：`Frontends.Current`（`Shell/V2/Frontends/`）只做**转发与状态映射**；业务真值仍在 Host/Core/ApplicationCore。

### R-STATE
- **R-STATE-1**：S1–S6 逐项迁出，每项须有「现状字段 → 新权威源 → 验收断言」三列证据；**权威源限于 ApplicationCore 本地对象**（Q-16）。
- **R-STATE-2**：未迁出项不得静默丢弃：preflight 检测到未迁出且有损编辑态 → **fail-closed**（中止 + 旧树保留 + 缓冲不丢 + 结构化错误）。
- **R-STATE-3**：VM 不得持有第二份业务真值；允许的 UI 私有状态 = 选择态/布局/memento，须在 Handoff 逐项列出并与业务态区分。
- **R-STATE-4**：关闭/重建内容不得 Dispose Host、不得隐式 `Start`；Host 生命周期归既有装配。

### R-SWITCH（preflight-only，Q-19）
- **R-SWITCH-1**：本卡提供 `preflight`：返回 `{allowed: bool, blockers: [...]}`；不允许时不得产生任何 Host/Core 副作用。
- **R-SWITCH-2**：preflight 读取的 Run/reader 投影必须来自共享源（Host/Core 投影或单例 RunMonitor），不得在 VM 内重建。
- **R-SWITCH-3**：**不实现**切换执行入口、不启动 Fluent、不改运行期路由（FEA-07 承担）。

## §15.3 迁出表（冻结，S1–S6 同 v1）

| # | 现有源/字段 | 目标权威（Q-16 限定） | 迁出/验收 |
|---|---|---|---|
| S1 | `StudioInspectorViewModel._pendingRegionType` | `EditingSession`/`DraftId` + `DraftBuffer`（ApplicationCore） | 未保存 region type 切换前 flush；失败留旧 UI；保存失败仍可编辑 |
| S2 | `StudioPageViewModel._pendingNavigation/_lastRerenderSummary/_runProjection` | 意图 receipt/会话 UI memento/共享 Run 投影（RunMonitor） | 未决确认不自动执行；旧回调不得重放；页面切换无投影回退 |
| S3 | `StudioBatchViewModel._runId/_projection/_intentIdempotencyKey` | `RunMonitor` + session intent store | 切 UI 相同 run/key；丢 ACK 后重试不二次启动 |
| S4 | `ReaderOverlayViewModel` book/pages/index/mode/direction/scroll | `ReaderSession` + Core 进度/按书偏好 | 保留 page ID 与语义锚点；未能无损映射则报告并留旧状态 |
| S5 | `ConsoleViewModel` monitor/筛选/选择 | 一个共享 `RunMonitor` + 会话筛选 | 切 UI 保留筛选；单轮每 Run 最多一次 snapshot/projection 查询 |
| S6 | `ShellState` selection/space/filter/surface stack；ThemeStudio editor draft | 跨 scheme Session 选择、UI memento、Appearance draft | 可映射逐项验证；未映射编辑/预览阻止切换，不能静默丢弃 |

## 验收标准（冻结版）

- [ ] **AC1 旧入口保留**：既有入口的公开签名/路由不变（`git diff` 只允许内部实现改动 + 适配层新增；每处改动在 Handoff 说明）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC2 行为基线不退化**：`dotnet test apps/desktop-avalonia/tests` 以 `91be6c134` 为冻结点全通过；基线用例清单 + 前后计数入 Handoff。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC3 无第二份业务真值**：VM 私有状态清单（Handoff）逐项区分「UI 态 vs 业务态」；业务态统一经 ApplicationCore 本地权威（Q-16）；grep 无新增权威副本。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC4 §15.3 六项迁出**：S1–S6 每项「现状→新权威→断言」证据。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC5 fail-closed preflight**：存在未迁出且有损编辑态 → preflight `allowed=false` + blockers + 零 Host/Core 副作用；无 blocker → `allowed=true` 且不触发新 Run（Q-19）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC6 生命周期**：关闭/重建内容前后 `ReferenceEquals(host, host)` 不变；`FakeHostController.StartCalls`/`HostController.StartRequests` 计数不增（不隐式 Start）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC7 回归与证据**：`dotnet test` 日志、基线对照表、preflight 矩阵入 `verification/FEA-04/**`。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC8 独立复核**：范围复核 r2 `approved`（P0/P1=0）；实现复核 `doc/reviews/FEA-04-r1.md` approved（P0/P1=0）。 <<PARTIAL: 范围冻结；待派发>>

## L 前置适用性判定

| 保留项 | 判定 | 再触发 |
|---|---|---|
| **L-1** 四表 DDL | **NOT_APPLICABLE**：不触 Source 四表、不改 `schema.py` | 需新表/迁移 → `blocked` |
| **L-2** M2-C1 字节修订 | **NOT_APPLICABLE**：Q-16 明确不触 wire/命令面；若后续需透传 Draft 命令 → `blocked`（转 FEA-05/07 并先完成 M2-C1） | 新增 Host/Core 命令或 wire 码 → `blocked` |
| **L-5** 整库恢复锁 | **NOT_APPLICABLE**：不触备份/恢复 | 触恢复 → `blocked` |

## 禁止范围

- 不改 Host/Core/CoreClient 的公开契约、命令面与 wire 码（Q-16）。
- 不改 `schema.py`/migrations、冻结契约字节、`doc/reviews/**`；不改 sln/新建工程（Q-18）。
- 不实现切换执行入口/不启动 Fluent（Q-19）；不实现 FEA-05 起的 UI 功能。
- 除 `NewManga.App.csproj` 的 **ApplicationCore 引用单点**（Q-17，Handoff 记录）外，不改 `NewManga.App` 其它工程文件。
- 不动用户数据、不 push、不合并 main；不降低既有测试断言。

## 契约 deferral 登记

| 条款 | deferral 归属 | 说明 |
|---|---|---|
| FEA-03 Q-8/R-JOURNAL-4③ 的 wire 接线 | `FEA-05`/`FEA-07`（Q-16） | 本卡只用 ApplicationCore 本地权威；不触命令面 |
| 运行期 Current↔Fluent 切换 | `FEA-07`（Q-19） | 本卡只做 preflight |

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

- 2026-11-02：DSH 裁决释放（GOAL Q-12；owner=ZCode，不可用时 DSH 可指派 Codex）；范围冻结 v1（`e34796862`）。
- 2026-11-02：范围复核 r1 `changes_requested`（P0×3/P1×9/P2×8）→ v2 处置：Q-16（wire defer，S1–S3 收窄 ApplicationCore 本地权威）、Q-17（csproj 单点授权）、Q-18（Frontends.Current 落 `Shell/V2/Frontends/`）、Q-19（switch preflight-only）；AC1/AC2/AC6 改可机械判定；新增「契约 deferral 登记」。
- 2026-11-02：`proposed`，派独立复核 r2。
