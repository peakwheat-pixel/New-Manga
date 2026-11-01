---
task_id: FEA-04
review_id: FEA-04-r1
kind: implementation-review
reviewer: fea04-impl-reviewer
reviewer_kind: subagent
reviewer_source: DSH fresh 独立上下文派发（Team Lead=lead；本席位未参与 FEA-04 的起草、实现或 DSH 返修，只读被审 head）
base_commit: 68c72ba57
reviewed_head: 8777b74f7
date: 2026-11-02
timezone: Asia/Shanghai
conclusion: changes_requested
counts: { P0: 0, P1: 4, P2: 15, total: 19 }
scope: 仅实现交付复核（FEA-04 AC1–AC8 与 DSH 返修正确性）；不构成集成批准
---

# FEA-04 实现复核 r1（实现交付 + DSH 返修）

**结论：`changes_requested`（P0 = 0、P1 = 4、P2 = 15）**

**一句话理由**：编译与 sln 全量测试可复现（930 passed / 0 failed / 60 skipped），旧入口与禁改面完好；但 **S3/S5 在 DSH 返修后退化为「仅门面」**（共享 `RunMonitor<T>` 在生产路径没有任何消费者，Batch 投影权威回到 VM 私有字段 `_projection`，Console/Shell 仍由 legacy `RunStatusMonitor` 轮询），**Page 管线带投影丢失**（`ApplyRunProjection` 丢弃入参），且 **AC7 证据目录仍停留在 Codex 的 NOT_RUN 状态、缺少 DSH 930 运行的原始日志，AC2 基线计数从未实测**。这些问题均可定点修复，无需重做实现。

## 审查基线

| 项 | 值 | 证据 |
|---|---|---|
| 主仓库 | `G:\CODEX\New Manga`（main，只读被审对象所在 worktree；仅写本报告） | `git rev-parse HEAD` → `c6f9a2944`（main 另有 2 个 docs 提交，不含实现） |
| worktree / 分支 | `G:\CODEX\New Manga.workspace\FEA-04` / `feat/fea-04` | `git rev-parse HEAD` → `8777b74f72dfc81dfea0652aa991585b3329581b` |
| 被审 base / head | `68c72ba57` / `8777b74f7`（卡 frontmatter `base_commit` 为 `7a9135260`；`68c72ba57` 是 Codex 交付时的 HEAD、`feat/fea-04` 三提交的父） | `git log --oneline 68c72ba57..8777b74f7` → `160bd0a4d`、`00bf4b578`、`8777b74f7` |
| diff 规模 | 39 文件，+1847 / −208 | `git diff --stat 68c72ba57..8777b74f7` |
| worktree 状态 | 审查前后 `git status --short` 均为空（clean）；构建输出 `bin/obj` 被忽略 | `git status --porcelain` |
| 环境 | Windows；.NET SDK `10.0.401`；目标 `net9.0`；`tests/NewManga.runsettings`（`MaxCpuCount=1`） | `dotnet --version` |
| 本次执行 | `dotnet build`（`--no-restore`）+ 卡内冻结 sln 测试命令的 `--no-build` 复跑；无 UI/真机/真实 Core sidecar 运行 | 见 §验证 |

**视角声明**：Architecture = executed（分层/权威源/生命周期）；Verification = executed（build + sln test 复跑、证据核对）；Spec（AC 对照）= executed；Standards 仅取仓库记录条款（AGENTS.md、协作协议 Task 生命周期、卡内 R-* 规则）。**未执行**：任何被审源码/文档写入，任何 commit/push/merge，任何 UI 截图/真机验证。

---

## 1. 范围与禁改面（核查点 1）

**结论：PASS。**

- `git diff --name-only 68c72ba57..8777b74f7` 的全部 39 个路径逐一匹配卡 `allowed_paths` 的 13 条前缀（脚本判定 **0 个越界**）：`doc/handoffs/FEA-04-*.md`、`doc/tasks/FEA-04.md`、`NewManga.App.csproj`、`Views/V2/**`、`ViewModels/V2/**`、`Shell/V2/**`、`tests/NewManga.App.Tests/**`、`verification/FEA-04/**`。
- 禁改面机械检查 0 命中：无 `NewManga.Host/`、`NewManga.CoreClient/`、`NewManga.ApplicationCore/` 源码改动，无 `*.sln`、无 `schema.py`/migrations、无 `doc/contracts/**`（冻结契约字节未动）。
- `NewManga.App.csproj` 仅 +1 行：`<ProjectReference Include="..\NewManga.ApplicationCore\NewManga.ApplicationCore.csproj" />`（Q-17 单点例外，符合卡 `:49`）。
- 未新建工程、未改 sln（Q-18）；未实现切换执行/未启动 Fluent（Q-19）；无 wire/命令面新增（Q-16）。
- 新增文件仅 4 个源/测试文件 + 文档/证据：`Shell/V2/Frontends/CurrentFrontend.cs`、`Shell/V2/Frontends/CurrentSessionMemento.cs`、`Views/V2/Route/CurrentRouteAdapter.cs`、`tests/NewManga.App.Tests/FEA04CurrentAdapterTests.cs`；`FakeHostController.cs` 为修改（+22 行，仅测试 helper）。
- `doc/reviews/**` 未出现在 diff 中（Review 写权在席位，符合卡 `:105`）。

## 2. AC1 旧入口保留（核查点 2）

**结论：基本 PASS（P2 文档项：IMPL-16、IMPL-17）。**

对 13 个被改 `.cs` 做公开成员机械对比（`git show base:file` vs head，逐行提取 `^\s*public` 后排序 diff）：

- **无任何公开成员被删除**。ShellState / StudioBatchViewModel / StudioPageViewModel / StudioInspectorViewModel 里被 diff 标出的 “REMOVED” 行全部是**实现体换写**（属性表达式从 `_field` 改为 `_session.*`/`Projection`），签名与名称不变。
- `ShellDeepLink`（`:28 TryParse` / `:122 ToQuery`）零改动 → 公开路由/深链格式保留；`Views/V2/Route/CurrentRouteAdapter.cs` 只是在既有边界上做纯映射（`TryMap`/`Map`/`ToShellDeepLink`），不导航、不读 Host。
- 新增公开面（均为增量，未破坏旧入口）：`CurrentFrontend`/`CurrentSessionMemento`/`CurrentRunDataSource`（后者无引用，见 IMPL-10）、`CreateShellState`、三处 `Current` 属性（AppShellV2 `:81`、AppShellViewModel `:159`、RunStatusMonitor `:18`）、`ShellState(CurrentShellMemento)` 构造重载（无参构造保留）、`RunStatusMonitor(CurrentFrontend)` 重载（`IRunController` 构造保留）、`StudioInspectorViewModel.PendingDraftId`/`SetPendingRegionTypeAsync`、`ReaderOverlayViewModel.WebtoonScrollPercent`。
- **P2**：Handoff 只列文件清单，未按 AC1 要求逐处给出“公开成员变更=0”的机械点（r3 R3-08 建议未落）→ IMPL-16；且 `doc/handoffs/FEA-04-68c72ba57.md` 以混合 CRLF 入库，head 范围 `git diff --check` **exit 2**（与 Handoff `:111` “PASS” 声明不符）→ IMPL-17。

## 3. AC2 行为基线（核查点 3）

**结论：测试事实 PASS（复跑一致）；基线计数证据 FAIL（IMPL-04）。**

### 3.1 复跑命令与结果（本席位独立执行）

```text
dotnet test apps/desktop-avalonia/NewManga.sln --no-build \
  --settings apps/desktop-avalonia/tests/NewManga.runsettings \
  --verbosity normal --results-directory %TEMP%\FEA04-review-rerun-results
```

`EXIT=0`，日志 `%TEMP%\FEA04-review-rerun-test.log`（`--verbosity`/`--results-directory` 仅为取证追加，不改语义；工作树 clean 状态下运行，二进制时间戳 03:24:12/03:25:46 晚于源码最后修改 03:24:09/03:25:45，对应当前 head）。

| 工程 | passed | failed | skipped | total | DSH 证据（sln-test-results.md） |
|---|---|---|---|---|---|
| NewManga.Host.Tests | 51 | 0 | 28 | 79 | 51/0/28/79 ✓ |
| NewManga.ThemeEngine.Tests | 235 | 0 | 0 | 235 | 235/0/0/235 ✓ |
| NewManga.DesignSystem.Tests | 85 | 0 | 0 | 85 | 85/0/0/85 ✓ |
| NewManga.CoreClient.Tests | 116 | 0 | 25 | 141 | 116/0/25/141 ✓ |
| NewManga.ApplicationCore.Tests | 31 | 0 | 0 | 31 | 31/0/0/31 ✓ |
| NewManga.App.Tests | 412 | 0 | 7 | 419 | 412/0/7/419 ✓ |
| **合计** | **930** | **0** | **60** | **990** | 930/0/60/990 ✓ |

新增 `FEA04CurrentAdapterTests` 16 项（1 个 5 行 `[Theory]` + 11 个 `[Fact]`）全部 passed。60 个 skip 的原因只有两类，均为环境型 sidecar fixture（`NEWMANGA_CORECLIENT_SIDECAR_DIR` / `NEWMANGA_MODELS_SIDECAR_DIR`），与本次改动无关。

### 3.2 编译

`dotnet build apps/desktop-avalonia/NewManga.sln --no-restore --verbosity minimal` → `EXIT=0`、**0 warnings / 0 errors**（3.9s，增量）。本步骤使用既有 `obj` 资产，未复验 NuGet restore（Codex 交付时的 `path1` 阻断不在本轮触达）；head 可编译。

### 3.3 基线对照与断言弱化

- **基线从未实测**：`verification/FEA-04/baseline-comparison.md:7-8` 与 Handoff `:94/:107` 均记录基线 build/test `BLOCKED/NOT_RUN`；DSH 未在隔离检出 `91be6c134`/`68c72ba57` 上运行同命令。`sln-test-results.md:16` 把 **419（含新增 16 项）** 当作基线并写“其余工程同上”，属自相矛盾；Handoff `:159` 的“基线 403 项”无证据。
- 可推导口径（本席位核对）：本次 diff **未修改任何既有测试文件**（仅新增 `FEA04CurrentAdapterTests.cs` 与 `FakeHostController.cs` helper +22 行）；6 个测试工程中只有 `NewManga.App.Tests` 引用 App（其余测试工程仅引用各自被测工程），故基线 = 当前计数，唯一差值为 App.Tests `419 − 16 = 403`。据此 AC2 的“逐工程 ≥ 基线、failed=0”在计数上成立，但这是**推导**，不满足卡 `:58/:86` 要求的“逐工程前后表 + 实测”。
- **断言弱化**：既有测试未被改动或删除 → 无既有断言弱化。两处测试适配判定：`FEA04CurrentAdapterTests.cs:251` 的 `ToQuery().TrimStart('?')` 属**轻微弱化**（`ShellDeepLink.ToQuery` 固定返回 `"?" + parts`，原比较可校验前缀，现被 `TrimStart` 掩盖）→ IMPL-08；`:305-309` 的“先发起 refresh、再等 gate”是**顺序修复**（原顺序会等不到 gate），不属弱化。

## 4. AC3 / AC4 S1–S6 迁出（核查点 4）

**结论：S1/S2/S4/S6 迁出到位（个别语义 P2）；S3/S5 FAIL（IMPL-01），S2 附带管线回归（IMPL-02）。**

| 项 | 现状 → 新权威（head 实测） | 断言/证据 | 判定 |
|---|---|---|---|
| **S1** | `StudioInspectorViewModel._pendingRegionType` 已删；Inspector 经 `_page.PendingRegionTypeDraft`/`GetOrCreateRegionTypeDraft` 使用 `CurrentFrontend` 管理的 `DraftBuffer`+DraftId（`StudioInspectorViewModel.cs:282-330`、`StudioPageViewModel.cs:486-505`）；Page 切页/保存前 `FlushAsync(PageChange)`，失败留旧页（`StudioPageViewModel.cs:1234-1244`） | `FEA04CurrentAdapterTests.cs:35-57/94-161`（flush 失败不写 Host、丢弃不 flush）；测试通过 | **PASS（带 P2）**：flush 是本地 no-op seam（`CurrentFrontend.cs:176`），Host 保存失败+取消模态后 `PENDING_REGION_TYPE` 不再出现 → IMPL-12 |
| **S2** | `_pendingNavigation/_lastRerenderSummary/_runProjection` 已删；改 memento（`CurrentStudioMemento.PendingNavigationPageId/PendingMode/HasPendingConfirmation/LastRerenderSummary`）+ 共享投影（`CurrentFrontend.cs:94-98`） | 未决确认不自动执行、不保存 delegate（`StudioPageViewModel.cs:1674-1728`）；但**投影链路断**：`RunProjection` 读从未刷新的 monitor 缓存，`ApplyRunProjection` 丢弃入参 → 管线带回归 | **PASS（迁出）但行为 FAIL** → IMPL-02 |
| **S3** | `_runId` → memento ✔、`_intentIdempotencyKey` → `CurrentRunIntentCoordinator` ✔；**`_projection` 被 DSH 恢复为 VM 字段（`StudioBatchViewModel.cs:337/406/747`），投影读走 `RunControllerRunDataSource→IRunController.GetTaskProjectionAsync`（`:359`），不经共享 `RunMonitor`** | 丢 ACK 复用同 key（`FEA04CurrentAdapterTests.cs:163-199`，通过）；“两个消费者经同一 Monitor”仅测试 `RunMonitor` 自身（`:288-321`），生产无消费者 | **FAIL** → IMPL-01 |
| **S4** | Reader 写 `CurrentReaderMemento`（PageId/SemanticAnchor/Layout/Direction/ScrollOffset，`ReaderOverlayViewModel.cs:154-163/187-215/416-435`）；page ID 不在新投影时 `AnchorMapped=false`、保留旧树（`:262-311`） | `FEA04CurrentAdapterTests.cs:254-285` 通过；错误 `UNMAPPED_READER_ANCHOR` 可从真实状态派生 | **PASS（带 P2）**：`SemanticAnchor` 实为 page ID 别名；滚动恢复只在 `Loaded` 一次 → IMPL-18 |
| **S5** | Console 的裸 snapshot/projection 字段已删 ✔；筛选/选择/输入进 memento ✔；**但监视器仍是 legacy `Shell/V2/RunStatusMonitor`（Host 轮询 `RunStatusMonitor.cs:212-280`），不是 ApplicationCore `RunMonitor<T>`；`CurrentFrontend.RunMonitor` 生产无订阅者** | R-24 共享轮询仍通过（App.Tests 全绿）；**同一 Run 仍被 Batch 自己的 DispatcherTimer 再查一次**（`StudioBatchControls.cs:630-635`→`StudioBatchViewModel.cs:635-683`），S5“单轮每 Run ≤1 次 snapshot/projection 查询”在生产消费者层面不成立 | **FAIL** → IMPL-01 |
| **S6** | Shell selection/space/mode/view filter/surface stack 进 `CurrentShellMemento`（`ShellState.cs` 全量改走 `_session`）；ThemeStudio Appearance draft 由 `CurrentFrontend.UpdateAppearanceDraft` 只读记录（`ThemeStudioViewModel.cs:866-873`） | `Before` 用例：重建后 Selection/Space/Mode 保留（`FEA04CurrentAdapterTests.cs:202-233`）；dirty Appearance → `UNMAPPED_SHELL_STATE`（`CurrentFrontend.cs:138-139`） | **PASS（带 P2）**：`dirty ≡ unmapped`，未做“可映射逐项验证”；`CurrentShellMemento.HasUnmappedState` 生产无置位者 → IMPL-19 |

**VM 私有状态清单 / 未迁出登记（AC3/AC4）**：Handoff `:69-74`（S1–S6 表）、`:78-87`（私有状态审计）是 **Codex 版本**，DSH 返修只追加了 `:147-159` 的记录，未回改这些表：
- `:71` 仍称 S3“投影来自 RunMonitor StateStore”、`:73` 仍称 S5“单例 Current RunMonitor”、`:84` 仍称“Start intent、Run ID 与投影权威均在 Current 对象”——与 head 实现相反；
- `:82` 描述的 `RunStatusMonitor` 字段（`_current/_subscription/_pollingEnabled`）与 head 的基线恢复版（`_runId/_snapshot/_projection/_pollingEnabled/_inFlight/_knownRunIds/_timer`）不符；
- `_projection`（S3 明确要迁出的字段）未被登记为“未迁出项”，违反 AC4“未迁出项必须在 Handoff 明确登记（不得静默省略）”。
→ 归入 IMPL-01（实现侧）与 IMPL-16（文档侧）。

## 5. AC5 fail-closed preflight（核查点 5）

**结论：接口形状与五 blocker 覆盖 PASS；零副作用断言真实；两处证据/语义 P2。**

- **形状**：`PreflightBlocker(string Code, string Source, string Detail)` + `CurrentPreflightResult(bool Allowed, IReadOnlyList<PreflightBlocker>)`（`CurrentFrontend.cs:14-17`），`Code` 五值、`Source ∈ {S1,S2,S3,S4,S6}` 与 Q-20 冻结一致；S5 无 blocker 已在注释说明（`:127-130`）。
- **五 blocker 各有用例**：`FEA04CurrentAdapterTests.cs:13-32`（theory 5 例）+ `:60-92`（真实状态派生 5 个并校验顺序）+ 矩阵 `verification/FEA-04/preflight-blocker-matrix.md:7-11`。
- **`allowed=false` 零副作用**：`Capture`（`:351-360`）比较 `StartCalls/StartRequests/RefreshCalls/ReaderLoadCount/RunSnapshotRequests/TaskProjectionRequests/StartRunRequests/SetRegionTypeCalls/LifecycleLog`；阻断与允许路径均断言前后不变（`:23/31/79/87/333/338`）。代码层面 `Preflight` 只读 memento/DraftBuffer/IntentCoordinator，未触 Host（`:131-154`）。
- **`allowed=true` 不触发新 Run**：`:324-339` 覆盖（注：该用例传入空 `CurrentPreflightSignals`，绕过了真实派生路径）。
- **不实现切换执行（FEA-07）**：diff 内无切换入口/`Process.Start`/Fluent 启动；route adapter 只映射（`CurrentRouteAdapter.cs:15-37`）→ PASS。
- **P2**：公开重载 `Preflight(CurrentPreflightSignals?)`（`:20-25/131`）可整体覆盖真实状态，单个调用即可绕过 fail-closed；theory 用 `SignalsFor` 注入（`:341-349`）只证明“映射不写错”，不证明“现状能触发” → IMPL-06（真实派生已由 `:60-92` 覆盖，故不升 P1）。

## 6. AC6 生命周期（核查点 6）

**结论：测试通过，但断言基本空转（P2，IMPL-05）。**

- 用例 `FEA04CurrentAdapterTests.cs:202-233`：两个 `AppShellViewModel` 共用同一 `FakeHostController`；断 `Assert.Same(hostBefore, second.Current.HostController)`、Selection/Space/Mode 保留、`StartCalls`/`StartRequests`/`LifecycleLog` 不增。
- 问题：① `FakeHostController.StartRequests => StartCalls`（`FakeHostController.cs:23`），卡要求的两个计数实际是**同一个计数器**，不构成独立证据（真实 `HostController.StartRequests` 未被调用/断言）；② 用例没有“关闭内容”路径，也没有 `Dispose` spy（`LifecycleLog` 仅记录 `start`/`refresh`，而 `DisposeAsync` 直接 `ValueTask.CompletedTask`、无记录，`FakeHostController.cs:17-62,994`），因此“不 Dispose Host”**无法被该测试发现**；③ 两个 VM 由同一 controller 实例构造，`Assert.Same` 必然成立，接近同义反复。
- 代码层面：diff 中不存在对 Host 的 `DisposeAsync`/`StartAsync` 调用（仅 `DraftBuffer.DisposeAsync`，`CurrentFrontend.cs:231`），R-STATE-4 在实现上未被违反；缺的是**可失败的断言**。

## 7. AC7 / AC8 证据与复核（核查点 7）

**结论：AC8 前置条件满足；AC7 FAIL（IMPL-03）。**

- **AC8 前置（范围复核）**：r3 报告 P0=0/P1=1（R3-01），其给定闭合法是“GOAL-PROGRESS 补 Q-20 行 + 改 approval 字符串”。实测 head 满足：`doc/checkpoints/GOAL-PROGRESS-2026-11-02.md:28` 有 Q-20 书面行；卡 `:7` `approval: dsh_ruling_2026-11-02_GOAL_FEA04_Q16_Q20`；`:139` Closeout 记录“Q-20 已登记 + approval 已更新”；`doc/reviews/FEA-04-scope-r1/r2/r3.md` 在 `68c72ba57` 入库。→ 范围前置 **PASS**。
- **AC7 FAIL**：
  1. **无 DSH 930 运行的原始日志/trx**：`verification/FEA-04/` 只有 Codex 的失败/`NOT_RUN` 日志；`sln-test-results.md` 只有汇总表。本席位复跑可复现 930/0/60，但**证据目录不含该次运行的判别力 artefact**（REVIEW 模板 Q-009：日志须带 EXIT 与命令头、逐次入库）。
  2. **三份证据 md 与 head 矛盾**：`baseline-comparison.md:7-8` 仍写“交付未提交/dirty/基线不可得”；`lifecycle-assertions.md:10-12` 写“NOT_RUN，未获得执行断言”，且 `:10` 的“RunStatusMonitor.Dispose 只释放 Current RunMonitor 的订阅”与 head 实现相反（`RunStatusMonitor.cs:282-285` 只 `StopTimer()`）；`preflight-blocker-matrix.md:7-11/17` 仍逐行“未执行”。DSH 只更新了 `sln-test-results.md`（`git show 8777b74f7 --stat`）。
  3. **命令不一致**：`sln-test-results.md:3` 记录的命令带 `--blame-hang --blame-hang-timeout 120s`，非卡 `:58/:86` 的冻结命令；且 `:16` 基线行自相矛盾（见 IMPL-04）。

## 8. DSH 返修的正确性专项（核查点 8）

| # | 返修项 | 判定 |
|---|---|---|
| 1 | `StudioBatchViewModel._dataSource` 恢复 `RunControllerRunDataSource` 与 S3“共享 RunMonitor”冲突？ | **冲突（P1, IMPL-01）**。恢复后 Batch 投影直读 `IRunController.GetTaskProjectionAsync`（`StudioBatchViewModel.cs:359`），S3 的投影权威重新落到 VM 私有 `_projection`（`:337/406/747`），共享 `RunMonitor` 无消费者。合理解法不是恢复而是“把 Batch 接到共享 monitor 并给测试 seed snapshot+projection”，或按 AC4 登记未迁出。 |
| 2 | `Projection => _projection` 与 `ApplyProjection` 写入是否一致（无重复源）？ | **单写一致**（`ApplyProjection` 是唯一写入点，`:747`），但**权威回退**（同 1）；另“清空 Run”分支删掉了基线的 `_projection = null`（`:644-653`），清空后 `Projection/ProgressText/CanPause` 残留旧 Run → IMPL-09。 |
| 3 | 移除 `EnsureRunSubscription` 自动订阅是否留下死代码/未用字段？ | **是（P2, IMPL-10）**。`EnsureRunSubscription`（`:738-745`）只剩 `_runSubscription?.Dispose(); _runSubscription = null;`，`_runSubscription`（`:314`）从未被赋非空；`using Avalonia.Threading`（`:2`）随之无用；`CurrentRunDataSource`（`StudioRunControllerDataSource.cs:129-155`）全库无引用；`CurrentSessionMemento.KnownRunIds`/`RememberRunId` 只由无生产调用者的 `SubscribeRun` 喂入；`RunObserved` 无生产触发。 |
| 4 | `RunStatusMonitor` 从基线恢复 + `Current` 属性/重载是否产生双源？ | **是（P1, IMPL-01）**。`RunStatusMonitor` 仍是 Host 轮询（`:212-280`），与 `CurrentFrontend.RunMonitor<T>`（`CurrentFrontend.cs:43/84`）并存；`Current` 属性只是暴露门面，不参与轮询/订阅。S5 的“单例 RunMonitor”未落地。 |
| 5 | `CurrentRunIntentCoordinator`“仅 ACK 清 key”是否与既有 `IDEMPOTENCY_KEY_REUSED` 语义一致？ | **一致（有 P2）**。同 key 重试不二次启动（`:261-280`，测试 `:163-199` 通过），与 ApplicationCore `IntentCoordinator`“in-flight 去重 + 原 key 前传”一致；但 `ExecuteAsync` 对“typed rejection”与“ACK 丢失”都返回 null → key 永久保留、`UNFLUSHED_RUN_KEY` 无清除路径 → IMPL-13。 |
| 6 | 测试适配（`ToQuery` TrimStart、读-后-等 gate 顺序）是否弱化断言？ | **TrimStart 轻微弱化（P2, IMPL-08）**；gate 顺序是**修复**（原顺序等不到 `RunSnapshotGateStarted`），不是弱化。 |
| 7 | `RaiseMany` 归位是否正确？ | 正确（Batch `:305-308`、Page `:237-240`），但两处私有 helper 定义在 `public const` 之前、且两个类各复制一份 → 命名/顺序 P2 级（并入 IMPL-10 的整洁性说明）。 |
| 8 | 930/0/60 是否可复现？ | **是**（本席位同环境同命令 EXIT=0，逐工程一致，见 §3.1）。 |

## 9. 质量（核查点 9）

- **死代码/未用字段**：见 IMPL-10。另 `CurrentFrontend` 的 `GetRun/SubscribeRun/RefreshRunAsync` 三个方法在生产只剩 `StudioPageViewModel.cs:711` 一处 `GetRun` 消费者，而该缓存无人填充。
- **`_projection` 线程安全**：写入点在 `RefreshAsync`/`ApplyProjection`（UI 线程或测试线程池 continuation），读取点（`Projection`、`HeaderLine`、`CanPause`）无锁；生产 UI 单线程下可接受，但 `TickAsync` 在无 `SynchronizationContext` 的测试环境与 `GetProjectionAsync(...).ConfigureAwait(true)` 组合会引入测试抖动风险（当前 930 通过，未暴露）→ 并入 IMPL-09/IMPL-14 说明。
- **异常路径**：`StudioInspectorViewModel.SetPendingRegionType` 改 fire-and-forget（`:296-298`），只捕 `InvalidOperationException`，其余异常成为未观察任务，UI 无失败反馈（IMPL-12）；`CurrentFrontend.ClearRegionTypeDraft` 的 `_ = removed.DisposeAsync()` 未观察异常（`:231`，当前 wrapper 先查注册可提前返回，风险低）。
- **Dispatcher**：`StudioPageViewModel.OnCurrentRunObserved` 正确用 `Dispatcher.UIThread.CheckAccess/Post`（`:1744-1758`）；`ReaderOverlay.axaml.cs` 用 `DispatcherPriority.Loaded` 恢复滚动（`:13-28`），但只在控件 `Loaded` 时一次，换书/重开不重放（IMPL-18）。`StudioBatchViewModel` 的 `using Avalonia.Threading` 已无用（IMPL-10）。
- **命名/结构**：`CurrentRunView`、`PreflightBlocker`、`CurrentPreflightSignals` 命名清晰；`RaiseMany` 位置小瑕疵；`CurrentFrontend.Active` 全局静态单点见 IMPL-14/15。

## 10. 未完成项与 Handoff 诚实性（核查点 10）

- **Codex 交付诚实**：Handoff `:7` `status: partial`、`:94-100` 明列 `BLOCKED/NOT_RUN`、`:124` 明列未完成项、`:140` 风险“当前无法确认 C# 编译或测试结果”、`:141` 明确 DraftBuffer 本地 flush/no wire —— 诚实。
- **DSH 返修诚实但有遗漏**：`:147-159` 记录了编译修复、`_dataSource` 恢复、`Projection` 回退、订阅移除、`RunStatusMonitor` 恢复、IntentCoordinator 语义、测试适配与 930 结果（含“基线同代码路径 403”），未把“未迁移 S3 `_projection` / S5 legacy monitor”登记为未迁出（IMPL-01）；未同步旧表（IMPL-16）。
- **Task 卡/指针**：`doc/tasks/FEA-04.md:14-19` 的 `branch/worktree/delivery_head` 仍为 null、`:140` Closeout 仍写“AC2 回归计数与动态断言仍 NOT_RUN”，未记录 DSH 返修与 head `8777b74f7`；`doc/checkpoints/GOAL-PROGRESS-2026-11-02.md:3` 仍写 HEAD `55543c10d`（r3 R3-10 的指针问题复现）→ IMPL-16。

---

## Findings

| 编号 | 级别 | 位置（head = `8777b74f7`） | 问题 | 建议 |
|---|---|---|---|---|
| **IMPL-01** | **P1** | `ViewModels/V2/Studio/StudioBatchViewModel.cs:337,359,406,738-745`；`Shell/V2/Frontends/CurrentFrontend.cs:43,84,94-116`；`Shell/V2/RunStatusMonitor.cs:212-280`；`ViewModels/V2/Console/ConsoleViewModel.cs:869-874`；`doc/handoffs/FEA-04-68c72ba57.md:71,73,84` | **S3/S5 退化为「仅门面」**：DSH 返修把 Batch 投影权威退回 VM 私有 `_projection`（直读 `IRunController.GetTaskProjectionAsync`），移除唯一订阅后 `CurrentFrontend.RunMonitor<T>` 在生产路径**无任何订阅/刷新消费者**；Console/Shell 仍由 legacy `RunStatusMonitor` Host 轮询，且与 Batch 自带 `DispatcherTimer`（`StudioBatchControls.cs:630-635`）并存 → 同一 Run 每轮被两处查询，违反 S5“单轮每 Run ≤1 次 snapshot/projection 查询”与 R-STATE-1“S3/S5 = 单例 RunMonitor”；Handoff 未把该项登记为未迁出，且 S3/S5 表述与 head 相反（AC3/AC4） | 二选一：**(a) 接线**——Batch `IRunDataSource` 用 `CurrentRunDataSource`，`CurrentFrontend.ReadRunAsync` 兼容既有 Host 投影 seam，`RunStatusMonitor` 降为 Current monitor 的 dispatcher 薄适配；测试用 `FakeHostController` seed snapshot+projection（不放宽断言）。**(b) 登记**——若本卡不做，按 AC4 在 Handoff 逐项登记 S3 `_projection`、S5 legacy monitor 为未迁出（原因 + 后续 Task + DSH 裁决），并修正 AC3/AC4 表述 |
| **IMPL-02** | **P1** | `ViewModels/V2/Studio/StudioPageViewModel.cs:711,1327-1334,1365-1371`；`Shell/V2/Studio/StudioWorkspaceView.axaml.cs:206-210,225,246` | **Page 管线带投影丢失（行为回归）**：`ApplyRunProjection(projection)` 不再写入任何缓存（入参完全未使用），`RunProjection` 改读从未被刷新的 `CurrentFrontend.RunMonitor` 缓存；`SyncBatchAsync` 的既有推送（进入 Batch / 点阶段、`:225/:246`）因此失效 → 基线 `_runProjection = projection`（基线 `StudioPageViewModel.cs:1328`）的 V11R-B-4 行为退化，现有测试未覆盖（全绿不代表行为未退化） | 恢复 `ApplyRunProjection` 写入 Page 级投影缓存（或让共享 monitor 成为唯一源并保证 Batch 刷新会 publish），补一个“Batch 刷新后 Page 管线带呈现投影阶段”的用例 |
| **IMPL-03** | **P1** | `verification/FEA-04/sln-test-results.md:3,16`；`lifecycle-assertions.md:10-12`；`preflight-blocker-matrix.md:7-11,17`；`baseline-comparison.md:7-8` | **AC7 证据与 head 不符**：无 DSH 930 运行的原始日志/trx（Q-009 判别力 artefact 缺失）；三份 md 仍写 `NOT_RUN/未执行`；`lifecycle-assertions.md:10` 的断言描述与 head 相反（`RunStatusMonitor.Dispose` 只 `StopTimer`，无 Current monitor 订阅）；`sln-test-results.md:3` 命令带 `--blame-hang`，非卡内冻结命令 | 用卡 `:58/:86` 冻结命令重跑并把**原始控制台日志/trx 入 `verification/FEA-04/`**；更新三份 md 到 head 状态（未跑项保持 NOT_RUN）；删除与实现相反的断言描述 |
| **IMPL-04** | **P1** | `verification/FEA-04/sln-test-results.md:16`；`doc/handoffs/FEA-04-68c72ba57.md:94,135,159`；卡 `:58,:86` | **AC2 逐工程基线计数从未实测**：`sln-test-results.md:16` 把 419（含新增 16 项）当基线且“其余工程同上”；Handoff “基线 403”无运行证据；基线测量未在隔离检出 `91be6c134`/`68c72ba57` 执行 → 不满足“Handoff 附前后表” | 在隔离 worktree 检出冻结基线运行同命令并记录逐工程 passed/failed/skipped；或至少书面写清推导口径（本次 diff 未改既有测试源码、仅 App.Tests +16）并由 DSH 认可 |
| **IMPL-05** | P2 | `FEA04CurrentAdapterTests.cs:202-233`；`tests/NewManga.App.Tests/FakeHostController.cs:23,17-62`；卡 `:90` | **AC6 断言空转**：`StartRequests => StartCalls` 与 `StartCalls` 是同一计数，非独立证据；无“关闭内容”路径、无 Dispose spy（`LifecycleLog` 只记 start/refresh），因此“不 Dispose Host”无法被该测试发现；两个 VM 同一 controller 实例，`Assert.Same` 近同义反复 | 增加 Host 异步 Dispose 的 spy/计数断言与一条“关闭内容”路径；或改用可包装真实 `HostController` 的 fake 记录 `DisposeAsync`/`StartAsync` |
| **IMPL-06** | P2 | `Shell/V2/Frontends/CurrentFrontend.cs:20-25,131`；`FEA04CurrentAdapterTests.cs:19-32,341-349` | **AC5 的证据被 signals 注入稀释**：公开重载 `Preflight(CurrentPreflightSignals?)` 可整体覆盖真实状态（fail-closed 可用单次调用绕过）；theory 5 例用注入布尔证明映射，而非“现状能触发”（真实派生仅 `:60-92` 一例兜底） | 将 signals 重载改为 `internal`/仅测试可见（`InternalsVisibleTo` 或在测试内构造状态），公开 API 只保留无参 `Preflight()` |
| **IMPL-07** | P2 | `FEA04CurrentAdapterTests.cs:288-321`；对照 `StudioBatchControls.cs:630-635`；卡 `:80` | **S5 去重用例名不副实**：名为 “Rebuilt_batch_and_shell_subscribers…”，实际只用 `CurrentFrontend.SubscribeRun` 两个临时订阅，未涉及 Batch/Shell 消费者；生产仍有 Batch 独立轮询 → 消费者级“每轮一次 snapshot/projection”无断言 | 改为在真实消费者路径上断言调用计数（或在 IMPL-01 方案 a 落地后断言共享 monitor 的请求计数） |
| **IMPL-08** | P2 | `FEA04CurrentAdapterTests.cs:251`；`Shell/V2/ShellDeepLink.cs:122-154` | **route 测试前缀断言被弱化**：`ToQuery()` 固定返回 `"?" + parts`，`TrimStart('?')` 掩盖前缀差异（DSH 称“前缀容错”） | 恢复严格比较 `Assert.Equal(query, deepLink.ToQuery())`（或对 `"?"` 前缀单独断言） |
| **IMPL-09** | P2 | `StudioBatchViewModel.cs:337,406,644-653,747` | **清空 Run 后残留旧投影**：基线的 `_projection = null` 在 `RunId` 为空分支被删除；`SetRunId(null)` 后 `Projection/ProgressText/CanPause` 等仍读旧 Run，UI 可能显示上一 Run 的可用动作（`ControlAsync` 因 RunId 为空会 no-op，故非数据安全） | 在空 Run 分支恢复清空并 `RaiseProjectionProps()`；`SetRunId(null)` 同步清空 |
| **IMPL-10** | P2 | `StudioBatchViewModel.cs:2,314,738-745`；`StudioRunControllerDataSource.cs:129-155`；`CurrentSessionMemento.cs:17-32`；`CurrentFrontend.cs:100-111`；`StudioPageViewModel.cs:237-240`、`StudioBatchViewModel.cs:305-308` | **死代码/未用成员**：`EnsureRunSubscription` 恒空转、`_runSubscription` 从不赋非空、`CurrentRunDataSource` 无引用、`CurrentSessionMemento.KnownRunIds/RememberRunId` 无生产生产者、`RunObserved` 无生产触发、Batch 的 `using Avalonia.Threading` 无用；`RaiseMany` 两处复制且置于 `public const` 前 | 删除或接入（IMPL-01 方案 a）；`RaiseMany` 移到类末尾或抽公共基类 |
| **IMPL-11** | P2 | `CurrentFrontend.cs:185`；`NewManga.ApplicationCore/DraftBuffer.cs:115-126,133-143,200-211` | **`DraftBuffer` 第三参数是 debounce，不是 TTL**：`TimeSpan.FromDays(30)` 形似保留期误用，实际把去抖 flush 禁用，并依赖这一副作用避免“no-op flush 把状态标 Flushed”；语义不清 | 显式常量+注释（或为 DraftBuffer 增加“不调度 debounce”的用法），并在 Handoff 说明本地 flush seam 的语义 |
| **IMPL-12** | P2 | `CurrentFrontend.cs:176-185,207-220`；`StudioPageViewModel.cs:1234-1244`；`StudioInspectorViewModel.cs:296-298`；`FEA04CurrentAdapterTests.cs:120-138` | **S1 flush 语义浅 + 失败反馈弱**：本地 no-op flush 成功即 `Flushed`；Host 保存失败后若用户取消模态，`Inspector.HasPendingTypeEdit` 仍真但 `PENDING_REGION_TYPE` 不再出现（现有用例只覆盖模态未关时）；`SetPendingRegionType` fire-and-forget 只捕 `InvalidOperationException`，失败无 UI 反馈 | blocker 同时读 `Inspector.PendingRegionType/HasPendingTypeEdit` 或记录“Host 未确认”标记；把 Inspector 调用点 async 化 |
| **IMPL-13** | P2 | `CurrentFrontend.cs:261-280` | **intent key 永久保留**：`ExecuteAsync` 对 typed rejection 与 ACK 丢失都返回 null，只有 `Run != null` 才清 key → 一次被拒 Start 后 `UNFLUSHED_RUN_KEY` 永久阻断 preflight 且无清除路径 | 区分“in-flight/丢 ACK”与“被拒绝/终止”：后者释放 key 或提供显式 `AcknowledgeFailure`；同步补充 preflight 语义说明 |
| **IMPL-14** | P2 | `CurrentSessionMemento.cs:6-15,49-52`；`CurrentFrontend.cs:34-70,100-111`；`StudioPageViewModel.cs:285-290` | **memento 线程安全与事件生命周期**：除 `KnownRunIds` 外 memento 无锁，`PageIndex`/`UpdateWebtoonProgress`/`OnCurrentRunObserved` 可能跨线程写；Page 构造订阅 `RunObserved` 无退订，内容重建/多 workspace 累积 handler（弱引用防 Page 泄漏但不减 handler 数量） | memento 加锁或统一 UI 线程写入；Page 实现 `IDisposable` 并退订（或改为一次性广播注册） |
| **IMPL-15** | P2 | `CurrentFrontend.cs:34-60`；`AppShellViewModel.cs:43-44`；`ThemeStudioViewModel.cs:866-873` | **静态 `Active` 全局可变单点**：`Activate` 由每个 AppShellViewModel 构造时覆盖；ThemeStudio 经静态 `UpdateAppearanceDraft` 写到“最后创建”的 frontend，多 Shell/多 Host（含并发测试）时不保证归属 | ThemeStudio 持有其宿主 `CurrentFrontend` 引用（由 shell 注入），去掉全局静态路由 |
| **IMPL-16** | P2 | `doc/handoffs/FEA-04-68c72ba57.md:69-74,78-87,93-100,140`；`doc/tasks/FEA-04.md:14-19,140`；`doc/checkpoints/GOAL-PROGRESS-2026-11-02.md:3` | **文档/指针未同步**：Handoff 的 S1–S6、VM 私有状态、AC 表仍是 Codex 版（与 head 相反）；Task 卡 `delivery_head/branch/worktree` 仍 null、Closeout 仍称 `NOT_RUN`；GOAL-PROGRESS 当前 HEAD 仍 `55543c10d`（r3 R3-10 复现） | DSH 在处置 findings 时同批更新 Handoff 表、Task 卡与 GOAL-PROGRESS 指针 |
| **IMPL-17** | P2 | `doc/handoffs/FEA-04-68c72ba57.md`（blob CRLF）；`.gitattributes` | **head 范围 `git diff --check` = exit 2**：新入库 Handoff 为混合换行（147 CR / 159 LF），逐行被判 trailing whitespace；与 Handoff `:111` 的 “git diff --check PASS” 声明不符 | 统一 LF（`git add --renormalize`）或按仓库既有惯例为 handoff 加 `text eol=lf`；同步更新 diff-check 证据 |
| **IMPL-18** | P2 | `CurrentSessionMemento.cs:70-76`；`ReaderOverlayViewModel.cs:154-163,262-311`；`ReaderOverlay.axaml.cs:13-28` | **S4 锚点/滚动恢复偏浅**：`SemanticAnchor` 实为 page ID 别名（无独立语义锚点）；Webtoon 滚动偏移只在 `Loaded` 恢复一次，重开 reader/换书不重放 | 在 Handoff 说明“语义锚点 = page ID”的当前语义并登记 FEA-14-READ；把滚动恢复挂到打开/重开路径（`OpenAsync` 完成后而非控件 `Loaded`） |
| **IMPL-19** | P2 | `CurrentFrontend.cs:62-70,138-139`；`ThemeStudioViewModel.cs:866-873` | **S6 Appearance 只做“dirty≡unmapped”兜底**：未按卡 `:81` 做“可映射逐项验证”，任何 dirty draft 都 fail-closed；`UpdateAppearanceDraft` 只记 Id/Name，未验证映射 | 至少在 Handoff 说明当前策略（保守 fail-closed）与后续可映射判定归属（FEA-05/07），或补最小映射谓词 |

**汇总：P0 = 0；P1 = 4（IMPL-01…04）；P2 = 15（IMPL-05…19）；合计 = 19。**

---

## 验证

| 场景 | 命令 / 步骤 | 环境 / commit | 结果 | 证据 |
|---|---|---|---|---|
| 范围机械检查 | 脚本比对 `git diff --name-only` 与卡 `allowed_paths` 13 前缀 | worktree，`8777b74f7` | **PASS**（0 越界） | 本次会话输出 |
| 禁改面检查 | 同上，匹配 `NewManga.(Host\|CoreClient\|ApplicationCore)/`、`*.sln`、`schema.py`、`doc/contracts/` | 同上 | **PASS**（0 命中） | 本次会话输出 |
| 公开成员对比 | 逐文件 `git show base:file` vs `head:file` 提取 `public` 行 diff | `68c72ba57` vs `8777b74f7` | **PASS**（无删除；仅新增，见 §2） | 本次会话输出 |
| 编译 | `dotnet build apps/desktop-avalonia/NewManga.sln --no-restore --verbosity minimal` | Windows / `8777b74f7` | **PASS**（EXIT=0，0 warnings/0 errors，3.9s） | `%TEMP%\FEA04-review-build.log` |
| AC2 sln 测试（复跑） | `dotnet test apps/desktop-avalonia/NewManga.sln --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings --verbosity normal --results-directory %TEMP%\FEA04-review-rerun-results` | Windows / `8777b74f7`，二进制与 head 源码时间戳一致 | **PASS**（EXIT=0；930/0/60，逐工程见 §3.1） | `%TEMP%\FEA04-review-rerun-test.log` |
| FEA-04 新用例 | 同上日志过滤 `FEA04CurrentAdapterTests` | 同上 | **PASS**（16/16） | 同上 |
| 基线逐工程计数 | 未在隔离检出 `91be6c134`/`68c72ba57` 运行 | — | **NOT_RUN** | IMPL-04 |
| AC5 blocker / 零副作用 | 静态核对 + 用例执行（`FEA04CurrentAdapterTests.cs:13-92/324-339`） | `8777b74f7` | **PASS（带 P2）** | IMPL-06 |
| AC6 生命周期 | 静态核对 + 用例执行（`:202-233`） | `8777b74f7` | **PARTIAL**（行为未见违反，断言空转） | IMPL-05 |
| S1–S6 迁出 | 静态核对（`git diff` + 文件阅读） | `8777b74f7` | **S1/S2/S4/S6 PASS（带 P2）；S3/S5 FAIL；S2 行为回归** | IMPL-01/02 |
| AC7 证据一致性 | 逐文件比对 `verification/FEA-04/**` 与 head | `8777b74f7` | **FAIL** | IMPL-03 |
| `git diff --check`（head 范围） | `git diff --check 68c72ba57..8777b74f7` | `8777b74f7` | **FAIL**（EXIT=2，Handoff CRLF） | IMPL-17 |
| UI / 真机 / 真实 sidecar | 未执行（本席位无 UI 环境，60 skip 为 sidecar fixture） | — | **NOT_RUN** | 边界声明 |

---

## 结论与复审

- **对 reviewed_head `8777b74f7` 的判定：`changes_requested`（P0=0、P1=4、P2=15）。** 依 REVIEW 模板“P0/P1 未解决或关键验证缺失时不可批准”：本实现**可编译、sln 全量测试可复现通过、范围与旧入口完好**，但 **AC4 的 S3/S5 权威源退化为门面（IMPL-01）**、**S2 关联的 Page 管线带投影回归（IMPL-02）**、**AC7 证据不实/缺失（IMPL-03）**、**AC2 基线表未实测（IMPL-04）** 四项 P1 未闭合，因此不能判 `approved`。
- **复审方式**：修复后追加新 head 与对应 disposition（不抹掉本报告）；P1 修复必须重新跑卡内冻结 sln 命令并把原始日志入库。P2 可与 P1 同批修，不阻塞下一轮（除非 DSH 将其升格）。
- **边界声明**：本报告只审实现交付与 DSH 返修，**不构成集成批准**，也不构成对方案/契约/范围的再批准；`approved`/`changes_requested` 仅针对 `68c72ba57..8777b74f7` 的实现内容。本席位未参与 FEA-04 的起草、实现或 DSH 返修；未修改任何被审源码/文档（仅写本报告文件）；未 commit/push/merge；未执行 UI/真机验证。所有行号基于 `8777b74f7` 实测；行号存在性不证明调用链完整。
