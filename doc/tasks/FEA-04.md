---
id: FEA-04
title: FEA-04 Current 适配（Frontends.Current + V2 state/route/VM adapter；保留旧入口）
kind: implementation
governance_version: 3
status: ready
approval: dsh_ruling_2026-11-02_GOAL_FEA04_Q16_Q20
suggested_owner: zcode
owner: zcode
reviewer: fea04-scope-reviewer
depends_on:
  - FEA-02-CORE
  - FEA-03
base_commit: 7a9135260
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
review_appointment: "doc/reviews/FEA-04-scope-r1.md、r2（reviewer fea04-scope-reviewer，DSH fresh 独立上下文派发；Review 由该席位写，不在本卡 allowed_paths）"
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
  - apps/desktop-avalonia/tests/NewManga.App.Tests/**
  - apps/desktop-avalonia/tests/NewManga.ApplicationCore.Tests/**
  - verification/FEA-04/**
---

# FEA-04 Current 适配（范围冻结 v3，待独立复核）

## 来源与授权

1. 方案 §12.1 `:642`：S1 `FEA-04` Current 适配——`Frontends.Current`、V2 state/route/VM adapter、**保留旧入口**；验收「行为不退化；无 VM 私有第二份业务真值；关闭/重建不 Dispose Host，不隐式 Start」。
2. 方案 §15.6 `:924`：写域 = `Views/V2/`、`ViewModels/V2/`、`Shell/V2/` 中 DSH 划分的 ui-shell/ui-studio 子目录及**对应 tests**；L3；§15.3 每字段迁出、行为基线、fail-closed。
3. 方案 §15.3 `:880-887`：S1–S6 迁出表（见下）。
4. 依赖：`FEA-02-CORE` done、`FEA-03` done（集成 `76d947923`）。**FEA-02-BRIDGE 的收窄切片（ApplicationCore 本地缓冲）由 FEA-03 交付（`DraftBuffer.cs`）；其 Host 生命周期/`ExitCoordinator` 部分未实施，本卡不依赖，按 R-STATE-4 维持既有装配**（方案 `:922`/§15.5 `:910` 的 BRIDGE 原义未被本卡声称已交付）。
5. **DSH 裁决**（[GOAL-PROGRESS-2026-11-02](../checkpoints/GOAL-PROGRESS-2026-11-02.md) Q-12/Q-16…Q-20）：
   - **Q-16**：本卡**不实现 wire**；S1–S3 权威为 ApplicationCore 本地（`DraftBuffer`/`IntentCoordinator`/`RunMonitor`）；S4 的 Core 进度经**既有** `IHostController` 读接口（`IHostController.cs:161/106`）；**S4 只做映射，不新增命令**；wire 接线由 FEA-05/FEA-07 承担（deferral 表）。
   - **Q-17**：`NewManga.App.csproj` 加 `NewManga.ApplicationCore` 引用是唯一单点例外（写域已列；Handoff 记录）。
   - **Q-18**：`Frontends.Current` 落 `Shell/V2/Frontends/`；route adapter 落 `Views/V2/Route/`；不新建工程、不改 sln。
   - **Q-19**：`switch` **只做 preflight**；不实现切换入口、不启动 Fluent（FEA-07 承担）。
   - **Q-20**：**"有损编辑态"与 blocker 形状冻结**（见 R-STATE-2）：`PreflightBlocker(Code, Source, Detail)`，Code ∈ {`PENDING_REGION_TYPE`,`PENDING_CONFIRMATION`,`UNFLUSHED_RUN_KEY`,`UNMAPPED_READER_ANCHOR`,`UNMAPPED_SHELL_STATE`}；任一存在即 `allowed=false`。

## 冻结设计规则

### R-CURRENT
- **R-CURRENT-1**：既有入口的**公开签名与路由**不改名、不删除；`Views/V2`/`ViewModels/V2`/`Shell/V2` 内部实现可改；新增适配层只做增量。
- **R-CURRENT-2**：行为基线 = `dotnet test apps/desktop-avalonia/NewManga.sln --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings` 在冻结点 `91be6c134` 的**逐工程通过计数**（Handoff 记录前后对比；不允许弱化断言，只允许新增）。
- **R-CURRENT-3**：`Frontends.Current` 只做转发与状态映射；业务真值仍在 Host/Core/ApplicationCore。

### R-STATE
- **R-STATE-1**：S1–S6 逐项迁出；权威源按项：**S1/S3/S5 = ApplicationCore 本地对象**（`DraftBuffer`/`IntentCoordinator`/单例 `RunMonitor`）；**S2/S6 = UI memento**（会话选择/布局/确认态，不承载业务真值）；**S4 = 既有 `IHostController` 只读投影 + Core 持久进度**；每项须有「现状字段 → 新权威 → 断言」证据。
- **R-STATE-2（Q-20，冻结）**：preflight 谓词——S1 存在未 flush 的 `_pendingRegionType` → `PENDING_REGION_TYPE`；S2 存在未决确认 → `PENDING_CONFIRMATION`；S3 存在未 ACK 的 run/intent key → `UNFLUSHED_RUN_KEY`；S4 无法无损映射 reader 锚点 → `UNMAPPED_READER_ANCHOR`；S6 `ShellState`/Appearance draft 有未映射编辑 → `UNMAPPED_SHELL_STATE`。任一存在即 fail-closed（中止 + 旧树保留 + 缓冲不丢 + 结构化结果）。
- **R-STATE-3**：VM 不得持有第二份业务真值；允许的 UI 私有状态 = 选择态/布局/memento（Handoff 逐项列出并区分业务态；静态检查口径 = 新增的私有缓存/registry 字段须在 Handoff 说明且不得作为读取权威）。
- **R-STATE-4**：关闭/重建内容不得 Dispose Host、不得隐式 `Start`；Host 生命周期归既有装配。

### R-SWITCH（preflight-only，Q-19）
- **R-SWITCH-1**：提供 `preflight`：返回 `{allowed: bool, blockers: PreflightBlocker[]}`；不允许时**零 Host/Core 副作用**。
- **R-SWITCH-2**：preflight 读取的 Run/reader 投影来自共享源（单例 `RunMonitor`/Host 投影），不得在 VM 内重建。
- **R-SWITCH-3**：不实现切换执行、不启动 Fluent、不改运行期路由（FEA-07）。

## §15.3 迁出表（冻结，S1–S6）

| # | 现有源/字段 | 目标权威（Q-16 修正） | 迁出/验收 |
|---|---|---|---|
| S1 | `StudioInspectorViewModel._pendingRegionType` | `DraftBuffer` + `DraftId`（ApplicationCore 本地） | 未保存 region type 切换前 flush；失败留旧 UI；保存失败仍可编辑 |
| S2 | `StudioPageViewModel._pendingNavigation/_lastRerenderSummary/_runProjection` | 会话 UI memento + 单例 `RunMonitor` 投影 | 未决确认不自动执行；旧回调不得重放；页面切换无投影回退 |
| S3 | `StudioBatchViewModel._runId/_projection/_intentIdempotencyKey` | `RunMonitor` + `IntentCoordinator`（`ExecuteAsync(intentKey)`；既有 `IDEMPOTENCY_KEY_REUSED`） | 切 UI 相同 run/key；丢 ACK 后重试不二次启动 |
| S4 | `ReaderOverlayViewModel` book/pages/index/mode/direction/scroll | 既有 `IHostController` 只读投影 + Core 持久进度 | 保留 page ID 与语义锚点；无法无损映射 → `UNMAPPED_READER_ANCHOR` 并留旧状态 |
| S5 | `ConsoleViewModel` monitor/筛选/选择 | 单例 `RunMonitor` + 会话筛选 | 切 UI 保留筛选；单轮每 Run 最多一次 snapshot/projection 查询 |
| S6 | `ShellState` selection/space/filter/surface stack；ThemeStudio Appearance draft | 跨 scheme Session 选择、UI memento、Appearance draft（**preflight 只读**） | 可映射逐项验证；未映射编辑 → `UNMAPPED_SHELL_STATE`，不静默丢弃 |

## 验收标准（冻结版）

- [ ] **AC1 旧入口保留**：公开签名/路由不变；`git diff` 只允许内部实现 + 适配层新增，每处改动 Handoff 说明。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC2 行为基线不退化**：`dotnet test apps/desktop-avalonia/NewManga.sln --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings` 在 `91be6c134` 的逐工程计数为基线；实现后同命令逐工程 ≥ 基线（Handoff 附前后表）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC3 无第二份业务真值**：VM 私有状态清单（Handoff）逐项区分 UI 态/业务态；业务态读取统一经 R-STATE-1 的权威源；新增私有缓存/registry 字段零个或逐项说明。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC4 §15.3 六项迁出**：S1–S6 每项「现状→新权威→断言」；**未迁出项必须在 Handoff 明确登记**（不得静默省略）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC5 fail-closed preflight**：Q-20 五个 blocker 各有用例；存在任一 blocker → `allowed=false` + 对应 `PreflightBlocker` + 零 Host/Core 副作用；无 blocker → `allowed=true` 且不触发新 Run。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC6 生命周期**：关闭/重建内容前后 `hostBefore`/`hostAfter` 满足 `ReferenceEquals(hostBefore, hostAfter)`；`FakeHostController.StartCalls`/`HostController.StartRequests` 计数不增。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC7 回归与证据**：sln 测试日志、基线对照表、preflight blocker 矩阵入 `verification/FEA-04/**`。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC8 独立复核**：本卡冻结版的范围复核 approved（P0/P1=0，报告见 `doc/reviews/FEA-04-scope-r*.md`）；实现复核 `doc/reviews/FEA-04-r1.md` approved（P0/P1=0）。 <<PARTIAL: 范围冻结；待派发>>

## L 前置适用性判定

| 保留项 | 判定 | 再触发 |
|---|---|---|
| **L-1** 四表 DDL | **NOT_APPLICABLE**：不触 Source 四表、不改 `schema.py` | 需新表/迁移 → `blocked` |
| **L-2** M2-C1 字节修订 | **NOT_APPLICABLE**：Q-16 不触 wire/命令面（S4 只用既有读接口）；需透传 Draft 命令 → `blocked`（FEA-05/07 + 先完成 M2-C1） | 新增 Host/Core 命令或 wire 码 → `blocked` |
| **L-5** 整库恢复锁 | **NOT_APPLICABLE**：不触备份/恢复 | 触恢复 → `blocked` |

## 禁止范围

- 不改 Host/Core/CoreClient 的公开契约、命令面与 wire 码；不改 sln/新建工程（Q-18）。
- 不改 `schema.py`/migrations、冻结契约字节；`doc/reviews/**` 由 Review 席位写（不在本卡写域）。
- 不实现切换执行入口/不启动 Fluent（Q-19）；不实现 FEA-05 起的 UI 功能；S6 Appearance draft 仅 preflight 只读。
- 除 `NewManga.App.csproj` 的 ApplicationCore 引用单点（Q-17）外，不改其它工程文件。
- 不动用户数据、不 push、不合并 main；不降低既有测试断言。

## 契约 deferral 登记

| 条款 | deferral 归属 | 说明 |
|---|---|---|
| FEA-03 Q-8/R-JOURNAL-4③ 的 wire 接线 | `FEA-05`/`FEA-07`（Q-16） | 本卡只用 ApplicationCore 本地权威 |
| 运行期 Current↔Fluent 切换 | `FEA-07`（Q-19） | 本卡只做 preflight |
| S4 进度写回（若需要） | 既有 `IHostController` 命令面或 FEA-14-READ | 本卡只读映射 |

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

- 2026-11-02：DSH 裁决释放（Q-12；owner=ZCode）；v1（`e34796862`）。
- 2026-11-02：r1 `changes_requested`（P0×3/P1×9/P2×8）→ v2（`55543c10d`）：Q-16…Q-19 处置。
- 2026-11-02：r2 `changes_requested`（P0=0/P1×3/P2×12）→ **v3**：R2-01（AC2 改 sln 命令 + 逐工程基线计数）、R2-02（Q-20 blocker 五谓词 + `PreflightBlocker(Code,Source,Detail)`）、R2-03（写域收窄 `NewManga.App.Tests/**` + `ApplicationCore.Tests/**`）；P2 批修（AC6 hostBefore/hostAfter、R-STATE-1/S4 经既有 `IHostController`、S1/S3 类型更正、S6 preflight 只读、§15.3 行号 `:880-887`、AC4 恢复未迁出登记、AC8→r3、route adapter 落 `Views/V2/Route/`、FEA-02-BRIDGE 书面处置、`doc/reviews` 写权说明）。
- 2026-11-02：`proposed`，派独立复核 r3；**通过前不 ready**。
- 2026-11-02：r3 changes_requested（P0=0/P1×1/P2×10）→ 处置 R3-01（**GOAL-PROGRESS 补 Q-20 书面裁决** + approval 改 …_Q16_Q20）与 R3-02/R3-03（FEA-02-BRIDGE 陈述更正；R-STATE-1 按项列权威源）。**DSH 判定 P1 闭合，按 r3 复核者给定闭合法置 eady**；R3-01 的「Q-20 已登记 + approval 已更新」即本条。
