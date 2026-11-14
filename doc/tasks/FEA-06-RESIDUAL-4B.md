---
id: FEA-06-RESIDUAL-4B
title: RegionBox「查看对照」实现：ListPageRegionTextsAsync 端口 + 冲突态双栏面板 + C-07 统计翻转 80/87
kind: implementation
governance_version: 3
status: proposed
disposition: "RO-1 拆卡的实现卡（2026-11-14）；消费 `FEA-06-RESIDUAL-4A` 冻结的规格 v1/v1.1，scope 未冻结、未释放"
approval: 待 DSH scope review 释放；前置＝`FEA-06-RESIDUAL-4A` 独立复核 approved 且 C-07 v1.9 重冻
suggested_owner: null
owner: null
reviewer: null
depends_on:
  - FEA-06-RESIDUAL-4A
base_commit: 756ab29e2f2a0039f89f696de18c09fd92368814
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-06-RESIDUAL-4B
allowed_paths:
  - doc/tasks/FEA-06-RESIDUAL-4B.md
  - doc/reviews/FEA-06-RESIDUAL-4B-*.md
  - doc/reviews/CONTRACT-UNFREEZE-*-C07-4B.md
  - doc/handoffs/FEA-06-RESIDUAL-4B-*.md
  - apps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/NullHostController.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/Fluent/WorkbenchViewModel.cs
  - apps/desktop-avalonia/src/NewManga.App/Views/Fluent/WorkbenchPageView.cs
  - apps/desktop-avalonia/src/NewManga.App/Controls/RegionTextComparePanel.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/FakeHostController.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/FluentResidualBatchATests.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/RegionTextComparePanelTests.cs
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/RegionWriteCommandTests.cs
  - doc/plan/FEA-C07_API_INVENTORY.md
  - doc/plan/FEA-CONTRACT-FROZEN-C07.md
  - doc/TASK_LEDGER.md
  - verification/FEA-06-RESIDUAL-4B/**
out_of_scope:
  - 不改 Core（`src/**`）：`list_page_region_texts` 已实现并注册分发，本卡零 Core 改动
  - 不加/改任何 wire 命令（`HostCommandRegistry.cs` / `HostCommandDispatcher.cs` 零改动；命令面不新增）
  - 不改 `FluentUi.Banner` 单 action 签名、不改 `FluentPageState` 枚举、不改 `RegionSummary` 形状、不改 `RegionPageTextProjection` 解析器
  - 不新增 `DraftErrorMap` 键（19 键闭集，P2-5）
  - 不做「以某一方覆盖 / 自动合并」等写动作（4A S5）
  - 不改 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`（DSH 维护；`proposed` 不触发 DAG 登记）
  - 不改 `FEA-06-RESIDUAL-4A` 卡与 `CONTRACT-UNFREEZE-2026-11-14-C07-RO1.md`（只消费，不修改）
  - 不 push 远端
---

# FEA-06-RESIDUAL-4B：「查看对照」实现（端口 + 面板 + 统计翻转）

## 来源与目标

用户 2026-11-14 撤销 Q7 `OUT` 并重开「查看对照」（[RO-1 裁决](../reviews/MAINT-1-RO-1-REOPEN-RESIDUAL-4-2026-11-14.md) §3 R3/R4、§4 拆卡表）。契约前置已由 [`FEA-06-RESIDUAL-4A`](FEA-06-RESIDUAL-4A.md) 完成：**对照内容规格 v1 + r1 处置的 v1.1 硬约束**已冻结，`ListPageRegionTextsAsync` 已在 C-07 计划节预授权（v1.9，pin `91e51ab7…`）。本卡只做**落地**：把预授权的 1 个端口接通到 UI，并按 `FEA-CONTRACT-FROZEN-C07.md` §3 完成**统计翻转 80/87 + pin v1.10**。

**当前事实基线（本卡起草时只读核实，2026-11-14，HEAD `756ab29e2`）**：

| 事实 | 证据 |
|---|---|
| 端口方法在 App 侧**不存在** | `apps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs`（79 方法，`LoadPageRegionsAsync` 在 `:262-264`） |
| 生产实现链是 4 跳 | `HostController.cs:17`（`IHostController` 实现）→ `HostRuntime.cs:826-840`（`ListRegionsAsync` 门控样板：`_readerIoGate` + `CoreService ?? throw NotReady()`）→ `CoreServiceClient.cs:1104`（wire 调用样板） |
| **CoreServiceClient 里没有任何 `list_page_region_texts`** | `Select-String region_texts` 于 `CoreServiceClient.cs` → 0 命中（wire 调用与解析都要新写） |
| 解析器**已在库且已测** | `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/RegionTextProjection.cs:224-281`（`RegionPageTextProjection.Parse`，严格解析）；用例 `tests/NewManga.CoreClient.Tests/Commands/RegionWriteCommandTests.cs:435/492/514-551` |
| wire 面已就绪、**只收两个字段** | `HostCommandRegistry.cs:191/357/465`、`HostCommandDispatcher.cs:868-871`（仅 `page_id` 必填 + `region_ids` 可选；**无 `expected_revision`**） |
| Core handler 语义 | `src/bootstrap/core_service.py:3533`（`handle_list_page_region_texts`）、`:7787/:7796`（分发）；未知 page 也返回 `regions: []` 且 `page_size: null`（P2-3 依据） |
| 冲突态现状 | `WorkbenchViewModel.OpenDraftAsync` 在 `CanEdit=false`/`Token=null`/`conflict` 分类时置 `FluentPageState.Conflict`（`WorkbenchViewModel.cs:589-609`）；横幅 `WorkbenchPageView.cs:656-660`（已有单 action「重读草稿」） |
| L2 实时文本口径 | `WorkbenchViewModel.DraftText`（`:70-77`）、`_persistedDraftText`/`HasUnsavedDraft`（`:31-32`/`:95`）、草稿输入框在 `CurrentDraft != null` 时可编辑（`WorkbenchPageView.cs:703-705`） |
| 反射式「冻结面」测试不命中新方法名 | `SourceRecoveryUiTests.cs:39-46`、`TrashUiTests.cs:446-456`、`Fea11SourceIpcTests.cs:452-460` 均为 `DoesNotContain` 具体名（`Source`/`Sync`/`Missing`、`PurgeTrashAsync`、`ListTrashAsync` 等），`ListPageRegionTextsAsync` **不命中**；仍须实跑确认（R-3） |

## 消费的规格（**以 4A 卡为准，本卡不复制、不另起一套**）

| 4A 规格 / 处置 | 4B 落地位置 | 机械验收 |
|---|---|---|
| **S3** 端口签名 + S7 边界；载体 §3「不接受 `expected_revision`」 | `IHostController` / `HostController` / `HostRuntime` / `CoreServiceClient` / `NullHostController` / Fake | AC1、AC6 |
| **S1** 两层定义（L1 权威读投影，L2 本地态） | 面板 + `WorkbenchViewModel` | AC3 |
| **P2-4**（规格 v1.1）：L2 文本 = VM **实时** `DraftText`，**不得**取 `Draft.Patch` | `WorkbenchViewModel` 暴露对照数据 | AC3 |
| **S2** 字段表（RegionType/SfxPolicy/Origin/RevisionNo/文本/来源；空串 `（空文本）` 约定） | 面板控件 | AC3 |
| **S2-a** `IsConflict` 派生（`HasRevisionDrift := L1.RevisionNo != L2.RevisionNo`），不新增字段/枚举 | `WorkbenchViewModel` | AC3 |
| **S4** 布局（冲突横幅下方纵向双栏；**不改** `FluentUi.Banner` 签名） | `WorkbenchPageView` | AC3 |
| **S5** 交互（只读、无一键覆盖、`Esc`/关闭）+ **P2-2** 失败原因固定优先级 | 面板 + VM | AC4 |
| **P2-3** 空集合语义（`regions: []` 不等于「无区域」） | VM 判别 | AC4 |
| **P2-5** 新码不进 `DraftErrorMap` 19 键闭集 | VM | AC5 |
| **S5 负向不变量**（投影不可用零文本行） | 测试 | AC5 |
| **S6** a11y（`AutomationProperties.Name`、Tab/Esc、只用既有笔刷） | 面板 | AC3 |
| **P2-6** allowed 面含 `WorkbenchViewModel.cs`/`WorkbenchPageView.cs` | 本卡 `allowed_paths` | — |

## Acceptance Criteria

全部 AC 必须可机械验收（命令、文件结构或命名测试可判）。未跑项标 `NOT_RUN`，不得记 PASS。

- [ ] **AC1 端口与生产链路**：`IHostController` 新增 `Task<RegionPageTextProjection?> ListPageRegionTextsAsync(string pageId, IReadOnlyList<string>? regionIds = null, CancellationToken cancellationToken = default)`，签名与 inventory 第 **#80** 行、4A S3 **逐字一致**；四处实现齐备：① `HostController` 委派 runtime、就绪门控同 `LoadPageRegionsAsync` 样板（未就绪/`IsUiFacingFailure` → `null`）② `HostRuntime` 走 `_readerIoGate` + `NotReady()`（同 `ListRegionsAsync` `:826-840`）③ `CoreServiceClient` 发 wire `list_page_region_texts`（payload **仅** `page_id` + 可选 `region_ids`，**不得**含 `expected_revision`）并用 `RegionPageTextProjection.Parse` 严格解析 ④ `NullHostController` 与测试 `FakeHostController` 返回 `null`（降级语义与既有读方法一致）。`dotnet build apps/desktop-avalonia/NewManga.sln` 0 error。
- [ ] **AC2 统计翻转 + pin v1.10**：[inventory](../plan/FEA-C07_API_INVENTORY.md) 统计行 `:20` `IHostController 79→80`、`:22` 合计 `86→87`；正式成员表在 `:114`（`RestoreBackupAsync`）之后、非方法成员 `:115` 之前插入第 **#80** 行 `ListPageRegionTextsAsync` / `Task<RegionPageTextProjection?>`；`变更类别` `:24` 的 `79→80`、`43→44`；「RO-1 计划追加」节标为**已落地**（保留节作历史口径，同 S5 节做法）。成员表与 `python tools/generate_api_inventory.py` stdout **逐行一致**（`ALL_MATCH: True`），`--check` **EXIT 0**（`1/80/6 = 87`）。pin 重算为 **v1.10**：冻结记录 §1 新行置顶 + **v1.9 原值 `91e51ab7…` 保留为「前一 pin（v1.9）」不改写**，§1B（登记 v1.10 与复核 pending）/§2 条件 3（`1/80/6=87`）/§3/§5 同步；新载体 `doc/reviews/CONTRACT-UNFREEZE-*-C07-4B.md`；`verify_pins.ps1` **18/18 PASS** 且 C07 = 新 pin。
- [ ] **AC3 UI（冲突态双栏、只读）**：仅当 `FluentPageState.Conflict` **且** `SelectedRegion != null` 时出现入口按钮（`Content` 与 `AutomationProperties.Name` 均为 `查看对照`）与面板；非冲突态 `IsVisible == false` 且**既有渲染零变化**。面板为纵向双栏（上 = L1 基底 / 下 = L2 工作副本），两栏各有标题与 `AutomationProperties.Name`（`基底文本（只读）` / `当前工作副本（只读）`），行高自适应、`TextWrapping=Wrap`、无固定高度。**L2 文本取 `WorkbenchViewModel.DraftText`（实时）**，控件创建后对 `DraftText` 的修改必须反映到面板（P2-4 判别断言）；L1 取 `RegionPageTextProjection` 对应 region 的 `Text.FinalTranslation` + `FinalSource`，L2 来源固定显示 `本地草稿`/`本地无草稿`；空串按 `（空文本）` 显示且**不得跨层填充**。面板内不得出现任何输入控件或「覆盖/应用」动作（断言：面板内可点击 `Button` 仅「关闭」）。`Esc` 关闭；关闭后恢复「仅横幅」原状。投影调用**恰好一次**（Fake 计数断言）。
- [ ] **AC4 空态 / 失败态（固定优先级，各自可测）**：按 **P2-2** 顺序判别且互不合并文案——① Host 未就绪（`IHostController.Snapshot.State != HostViewState.Ready`）→ `HOST_NOT_READY`；② 端口返回 `null` → `REGION_TEXT_PROJECTION_UNAVAILABLE`；③ 投影非 `null` 但目标 region 不在结果中，**或** `Regions.Count == 0 && PageSize is null`（未知 page，**P2-3**）→ `TARGET_NOT_FOUND`。以上三种为**失败态**，面板只显示原因与「关闭」，**零文本行**。**空态（非失败）**：`Regions.Count == 0 && PageSize is not null` → 显示「该页没有区域」空态，不使用上述三码。判别：4 个 Fake 场景（未就绪 / null / 目标缺失 / `[]`+`null` / `[]`+有 page_size）分别断言码与文案**两两不同**，且 `[] + page_size: null` **不得**渲染成「无冲突」或空态。**调用口径（本卡定）**：端口调用**不传 `regionIds`**（整页一次，与 S1-a「一页一次」一致），`TARGET_NOT_FOUND` 一律由**本地成员判定**得出；理由是 Host 的 `IsUiFacingFailure` 会把 Core 抛出的 `CoreOperationException` 统一吞成 `null`（`HostController.cs:2932`），若改传 `regionIds` 则 Core 的 `TARGET_NOT_FOUND` 会退化成 ② `REGION_TEXT_PROJECTION_UNAVAILABLE` 而误判优先级（见 R-8）。
- [ ] **AC5 负向不变量（不得削弱）**：投影不可用时面板**零文本行**、不显示任何伪造/回退值（不得用本地文本、缓存或 L1 推测填充）。既有 `I13_WorkbenchConflictRow_ConflictBannerShowsWithoutFabricatedCompare`（`FluentResidualBatchATests.cs:642-670`）：原 `DoesNotContain(查看对照)` **反向断言改写为正向断言**（冲突态存在该按钮）**且必须同时新增**「投影不可用 → 面板无任何文本行、只有 typed 原因」断言——两条并存才算保持不变量。`DraftErrorMap` 键数保持 **19**（`WorkbenchViewModel.cs:806-835`，**P2-5**：`REGION_TEXT_PROJECTION_UNAVAILABLE` / `HOST_NOT_READY` / `TARGET_NOT_FOUND` 为面板本地原因码，**不得**加入该映射，也不得改 FEA-05 §3 码表）。判别：`grep` 断言两处测试名存在、`DraftErrorMap` 键数 = 19。
- [ ] **AC6 wire 形状与解析**：`NewManga.CoreClient.Tests` 新增/扩展用例断言：客户端发出的命令名为 `list_page_region_texts`、payload **仅** `page_id` + 可选 `region_ids`（**无** `expected_revision`）；真实 Core 形状 JSON 经 `RegionPageTextProjection.Parse` 正确取值（含 `page_size: null` 与 `geometry: null` 两种合法形态）；字段缺失/类型错误 → `FormatException`（沿用既有严格解析语义，不得放宽）。`HostCommandRegistry.cs` / `HostCommandDispatcher.cs` **零改动**（不新增命令）。
- [ ] **AC7 门禁四件套 + 零越界**：① `pwsh -NoProfile -File tools/governance/check.ps1`；② 同脚本 `-TaskPath doc/tasks/FEA-06-RESIDUAL-4B.md`；③ `pwsh -NoProfile -File tools/governance/verify_pins.ps1`；④ `python tools/generate_api_inventory.py --check`。四者原始输出与 EXIT 码留 `verification/FEA-06-RESIDUAL-4B/logs/`；**本提交所含路径** ⊆ `allowed_paths`；`git diff --name-only <base>..HEAD -- src` 为空（零 Core 改动）；无 DDL/schema diff。
- [ ] **AC8 测试与独立 Review**：App.Tests 全量 + CoreClient.Tests 全量 `0 failed`（日志留证，含 `EXIT=0`）；新增判别测试覆盖 AC3/AC4/AC5 的每条断言；**独立 Review 由未参与实现的上下文执行**（本项目独立性＝上下文独立），P0/P1/P2 处置后形成 `doc/reviews/FEA-06-RESIDUAL-4B-r*.md` 结论回填；实现者不得自审、不得代写 approved。

## 允许修改范围

- 本卡、`doc/reviews/FEA-06-RESIDUAL-4B-*.md`、`doc/handoffs/FEA-06-RESIDUAL-4B-*.md`、`doc/reviews/CONTRACT-UNFREEZE-*-C07-4B.md`
- 端口与生产链路（5 个文件）：`IHostController.cs`、`HostController.cs`、`NullHostController.cs`、`src/NewManga.Host/HostRuntime.cs`、`src/NewManga.CoreClient/CoreServiceClient.cs`
- UI（2 个既有文件 + 1 个可选新控件）：`WorkbenchViewModel.cs`、`WorkbenchPageView.cs`、`Controls/RegionTextComparePanel.cs`（新建；若最终选择内联进 View，则不创建该文件，Handoff 须说明）
- 测试（4 个文件）：`FakeHostController.cs`、`FluentResidualBatchATests.cs`、`RegionTextComparePanelTests.cs`（新建）、`CoreClient.Tests/Commands/RegionWriteCommandTests.cs`
- 契约（2 个文件）：`doc/plan/FEA-C07_API_INVENTORY.md`、`doc/plan/FEA-CONTRACT-FROZEN-C07.md`
- `doc/TASK_LEDGER.md`：**仅限一次机械重生成**（迟早必然失配：新增本卡后 `task files 600→601`、`non-terminal 8→9`，`check.ps1:272-283` 会报台账过期）。执行 `python tools/governance/task_ledger.py --write` 前须取得 DSH 授权；若 DSH 选择自行重生成，则本条不使用
- `verification/FEA-06-RESIDUAL-4B/**`（含 frontmatter `evidence_dir`，已显式列入 `allowed_paths`）

## 禁止范围

- `src/**`（Python Core）任何改动；`HostCommandRegistry.cs`、`HostCommandDispatcher.cs`；任何 schema/DDL。
- `FluentUi.Banner` 签名、`FluentPageState` 枚举、`RegionSummary` 形状、`RegionPageTextProjection` 解析语义、`DraftErrorMap` 码表。
- `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`（DSH 维护；`proposed` 不触发 DAG 登记，PLAN 64/64 行已满）。
- `FEA-06-RESIDUAL-4A` 卡与 `CONTRACT-UNFREEZE-2026-11-14-C07-RO1.md`（只消费不修改）。
- 任何「以某一方覆盖 / 自动合并 / 批量应用」的写动作；任何远端写操作。

## 测试与验证矩阵

| 场景 / AC | 命令或步骤 | 判别 | 证据 |
|---|---|---|---|
| AC1 编译与链路 | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` | 0 error；`grep` 5 文件各含新方法 | `logs/dotnet-build.log` |
| AC2 统计/成员表/pin | `python tools/generate_api_inventory.py --check`；逐行比对脚本 stdout；`verify_pins.ps1` | `--check` EXIT 0（`1/80/6=87`）；`ALL_MATCH: True`；C07=新 pin | `logs/api-inventory.log`、`logs/pin-before-after.log` |
| AC3/AC4/AC5 UI 与负向 | `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --nologo` | 新增判别用例全绿；App.Tests 全量 0 failed | `logs/dotnet-app-tests.log` |
| AC6 wire 形状 | `dotnet test apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/NewManga.CoreClient.Tests.csproj --nologo` | 新增用例全绿；payload 字段集合断言 | `logs/dotnet-coreclient-tests.log` |
| R-3 反射面复核 | 上述两个测试工程全量 | `SourceRecoveryUiTests`/`TrashUiTests`/`Fea11SourceIpcTests` 保持绿 | 同上 |
| AC7 门禁 | 四件套 | 四项 EXIT=0 | `logs/gates-*.log` |
| AC8 独立 Review | 由 DSH 派独立上下文 | 报告落 `doc/reviews/FEA-06-RESIDUAL-4B-r*.md` | 报告本身 |

## 风险与回滚

| # | 风险 | 处置 |
|---|---|---|
| R-1 | 新增卡使 `doc/TASK_LEDGER.md` 计数失配 → `check.ps1:272-283` 报错 | 释放时由 DSH 授权一次 `task_ledger.py --write`（同 4A R-1 先例），台账纳入同一 commit |
| R-2 | `doc/REBASELINE_PLAN.md` 64/64 行已满，`ready/in_progress` 无行可登记 | 登记由 DSH 统一处理；`proposed` 不触发 DAG 检查，卡可先存在 |
| R-3 | 反射式「冻结面」测试可能因新方法名而红 | 已核实三处均为 `DoesNotContain` 具体名且新名不命中（见事实基线表）；**仍须实跑**，若意外红则视为发现并 STOP 回报，不得改测试绕过 |
| R-4 | 冲突横幅已有单 action（「重读草稿」），「查看对照」只能外置 → 与设计文档 `06-page-workbench.md:50`「冲突条（原因 + 查看对照）」字面略有偏差 | 4A S4 已裁决「不改 `FluentUi.Banner` 签名」，按钮作为同一纵向容器内的独立控件；Review 时须确认视觉仍表达「冲突条内含该动作」 |
| R-5 | **统计翻转与代码不同步**会重演 EDIT-1 式 pin 漂移 | 顺序固定：改代码 → 重跑脚本 → 改 inventory 成员表/统计 → **同一 commit 内**重算 pin → 写冻结记录/载体；`--check` 在改 inventory 前必红，属预期中间态，不得提交 |
| R-6 | `CoreServiceClient` 新增公开方法可能被其它契约测试枚举 | 不新增 wire 命令、不动 `HostCommandRegistry`；若出现非预期红点，按 R-3 同样 STOP 回报 |
| R-7 | 4A 未 r2 approved 就释放 4B → 实现依据的规格未冻结 | 卡前置写明：4A 独立复核 `approved` + C-07 v1.9 重冻后才可 `ready` |
| R-8 | **`TARGET_NOT_FOUND` 通道口径未在 4A 规格里定死**：若 4B 传 `regionIds` 而该 region 已消失，Core 抛 `CoreOperationException(TARGET_NOT_FOUND)`，被 `HostController.IsUiFacingFailure`（`HostController.cs:2932`）吞成 `null` → 会被误判成 ② `REGION_TEXT_PROJECTION_UNAVAILABLE`，与 P2-2 优先级冲突；要保留错误码就必须改**已预授权**的返回类型（`RegionPageTextProjection?`）→ 触发第二次 UNFREEZE | **本卡取不传 `regionIds` 路线**（整页一次 + 本地成员判定），签名与 v1.9 预授权完全一致、零额外 UNFREEZE。若 DSH 改为「必须传 `regionIds`」，须先在 4A 补 errata 并重新评估签名，不得在 4B 内私改 |

**回滚**：代码侧单 commit revert 即可（无 DDL、无数据迁移）。若已翻转统计/pin 而实现需回滚，**必须**把 inventory 恢复 79/86 并重算 pin（记 v1.11，v1.10 原值保留），不得留下「doc 说 80 而代码 79」的半翻转状态。

## 证据计划（`verification/FEA-06-RESIDUAL-4B/`）

| 文件 | 内容 |
|---|---|
| `README.md` | AC1–AC8 结论表、pin v1.9→v1.10 前后值、NOT_RUN 清单、复现命令 |
| `logs/dotnet-build.log` | `dotnet build` 全量与 EXIT |
| `logs/dotnet-app-tests.log` | App.Tests 全量（含新增判别用例）+ EXIT |
| `logs/dotnet-coreclient-tests.log` | CoreClient.Tests 全量（wire 形状/解析）+ EXIT |
| `logs/api-inventory.log` | 脚本全量 stdout + `--check` + EXIT（`1/80/6=87`） |
| `logs/member-table-eq-stdout.log` | 正式成员表 vs stdout 逐行 `ALL_MATCH` |
| `logs/pin-before-after.log` | 旧 pin 复现（`git show <base>:...`）+ 新 pin 双口径 |
| `logs/gates-<date>.log` | 门禁四件套原始输出与 EXIT |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（无独立 worktree；DSH 决定是否建） | NOT_APPLICABLE | — | — | 未创建 |
| build | `apps/desktop-avalonia` 构建产物（`bin/`、`obj/`） | DELETE_SAFE | — | — | 构建产物，按仓库既有忽略规则处理；不提交 |
| test-material | Fake/JSON 测试夹具（内联于测试文件） | PRESERVE_REFERENCED | — | — | 由测试代码内联，无外置夹具 |
| artifact | `verification/FEA-06-RESIDUAL-4B/**` | PRESERVE_REFERENCED | — | 见 README 索引 | 门禁/测试原始日志 |
| user-data | NOT_APPLICABLE（不访问用户数据根） | NOT_APPLICABLE | — | — | 未访问 |

## Closeout Record

- Closeout date / DSH：待关闭时填写（当前 `proposed`，未释放）。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写（预期 0）。
- 未关闭项及保留原因：无（尚未实施）。
- 当前指针清理：本轮不改 `STATUS` / `REBASELINE_PLAN`；`FEA-06` AC3 保持 **PARTIAL**，直到本卡集成验证通过并经 DSH 裁决后才可改 MET。
