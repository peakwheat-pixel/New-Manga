---
task: FEA-06-RESIDUAL-4B
task_id: FEA-06-RESIDUAL-4B
reviewer: independent sub-agent (4B r1, read-only, not involved in implementation)
reviewer_kind: subagent
base_commit: 9d0186a3d
reviewed_head: 42123ae67
date: 2026-11-14
verdict: approved
p0: 0
p1: 0
p2: 3
p3: 6
scope: "9d0186a3d..42123ae67（5 文件 / +816 −5）：RegionTextComparePanel.cs（新）、WorkbenchViewModel.cs、WorkbenchPageView.cs、FluentResidualBatchATests.cs（I13 改写）、RegionTextComparePanelTests.cs（新）"
---

# FEA-06-RESIDUAL-4B r1：第三刀 UI「查看对照」独立复核

## 0. 结论

**`approved`。P0 = 0，P1 = 0，P2 = 3，P3 = 6（全部登记，不阻断本刀代码验收）。**

本报告由**未参与实现与设计**的独立上下文子 agent 出具，只读被审对象；所有数字与行为均为本轮实测，不采信卡面或实现者自述。

**通过的关键面（逐项证据见 §2–§3）**：

- **AC5 负向不变量真实且未被削弱**：旧 `DoesNotContain("查看对照")` 已按规格翻为**正向断言**（冲突态恰有一个入口按钮），**且同文件内并存**「投影不可用 → 面板零文本行、只有 typed 原因」的负向断言；另有一例独立负向用例，断言面板不回退本地草稿、不复用其它 region 的 L1。
- **`DraftErrorMap` 仍为 19 键**：`REGION_TEXT_PROJECTION_UNAVAILABLE` / `HOST_NOT_READY` **未**进入该映射；`TARGET_NOT_FOUND` 是父提交即存在的既有键（父/子两侧键集合逐字相同），不是新增。
- **AC4 固定优先级落地**：① `HOST_NOT_READY`（不发投影请求）→ ② `REGION_TEXT_PROJECTION_UNAVAILABLE`（端口 `null`）→ ③ `TARGET_NOT_FOUND`（目标 region 缺失 / 未知 page）；`regions: []` + `page_size: null` 走 ③，**不**渲染成空态或「无冲突」。
- **AC3 的 L2 实时性成立**：用户可见文本始终等于当前 `DraftText`，且**重排后不回落成旧值**（面板重建时用实时 `DraftText` 覆盖快照）。
- **「恰好一次」落在 VM**：生产代码中唯一的投影调用点在 `WorkbenchViewModel.OpenRegionCompareAsync`，端口层无缓存；一次打开 = 1 次、关闭再开 = 2 次均可复现。
- **零越界**：diff 恰为 5 文件；`FluentUi.cs`、`CoreServiceClient`、`IHostController`、`HostRuntime`、inventory、冻结记录、PLAN、STATUS、TASK_LEDGER **零改动**。
- **门禁全绿**：`check.ps1`（默认 + 4B TaskPath）PASS (3 warnings)/EXIT 0；`verify_pins.ps1` 18/18 PASS（C07 = `498882eb…`）；`generate_api_inventory.py --check` EXIT 0（`1/80/6 = 87`）。
- **定向测试**：14 / 0 failed / 0 skipped，EXIT 0（真实运行，逐例列名见 §3.8）。

**收口判断**：4B **可以进入收口**；AC1/AC2/AC3/AC4/AC5/AC7 可判（AC4 的"文案两两不同"机械断言缺一条，见 P2-2），**AC6 本轮未由本 reviewer 复跑、AC8 当前不可判**（全量测试日志尚未落盘；证据 README 已在复核期间由 DSH 补齐，见 §5/P2-3）。收口前必须处置 P2-1/P2-2 或经 DSH 明示登记为 limitation，并补 P2-3 的 4B-3 原始日志（详见 §5）。

---

## 1. 复核口径与环境

- **只读**：未修改被审对象，未 commit/push/checkout；仅新建本报告。定向测试与门禁产生的 `bin/`/`obj/` 构建产物均被既有 ignore 规则吸收（测试运行时 `git status --short` 为空）。
- **工作树**：复核**开始时** `HEAD = 42123ae67`（被审 head），`git status --short` 为空；复核**期间**仓库由 DSH 前进到 `e6b4009fc`（**doc-only**：`git diff --name-only 42123ae67 HEAD` = `doc/tasks/FEA-06-RESIDUAL-4A.md`、`doc/tasks/FEA-06-RESIDUAL-4B.md`；`git diff 42123ae67 HEAD -- apps/ src/` 为空），并新建了未跟踪的 `verification/FEA-06-RESIDUAL-4B/README.md`（10:34，见 P2-3）；复核**结束时** `HEAD = e6b4009fc`、未跟踪文件 = 本报告 + 该 README。代码字节始终等价于被审 head；本报告的代码/行号判定全部基于 `42123ae67`。
- **规格上下文**：`e6b4009fc` 给 4A 增补了 **S1-c**（L2 实时性判据：重排后不得回落旧值），给 4B 增补了 R-9…R-12 裁决。第 4 项（AC3 实时性）直接按 S1-c 判定；其余各项仍以被审 commit 时已冻结的 v1.1 规格为准。
- **未采信**：卡面自述的"测试通过/门禁通过/无越界"一律由本轮命令重新取得原始输出。

---

## 2. 逐项判定（必做 10 项）

| # | 复核项 | 判定 | 证据（文件:行号 / 命令） |
|---|---|---|---|
| 1 | AC5 负向不变量真实且未削弱 | **PASS** | 父提交 `FluentResidualBatchATests.cs:668-669` 旧 `DoesNotContain(查看对照)` 已删除；子提交 `:672-674` 改为 `Assert.Single(...)` 正向断言；**同文件** `:676-687` 并存负向断言（`ProjectionUnavailable` + `BaseLayer/WorkingLayer` 双 null + 全视图无 `"draft text"` TextBlock）；另有独立用例 `RegionTextComparePanelTests.cs:296-318`（零 L1 泄漏、零本地回退、面板内唯一按钮仍是「关闭」）。 |
| 2 | `DraftErrorMap` 仍 19 键；两新码未加入；`TARGET_NOT_FOUND` 为既有键 | **PASS** | 子提交 `WorkbenchViewModel.cs:934-947`：19 键（父提交同一块亦 19 键，键集合 `Compare-Object` 无差异）；`TARGET_NOT_FOUND` 在父提交 `9d0186a3d` 的同名映射中已存在（本轮从 `git show 9d0186a3d:...` 解析确认）；面板本地码在 `RegionTextComparePanel.cs:35-40`，测试 `RegionTextComparePanelTests.cs:288-291` 断言 19 / 两码 absent / `TARGET_NOT_FOUND` present。 |
| 3 | AC4 固定优先级 + `regions: []` + `page_size: null` 非「无冲突」 | **PASS**（附 P3-1 文案偏差） | `WorkbenchViewModel.cs:788-793`（①，先于调用）→ `:800-806`（②）→ `:811-826`（③）；`:813` 仅当 `Regions.Count == 0 && PageWidth != null && PageHeight != null` 才判空态，否则 `:823` `TargetNotFound`。测试 `RegionTextComparePanelTests.cs:204-219 / 221-236 / 238-254 / 256-272` 四场景；`:252-253` 断言 `[] + null` 不渲染空态文案。 |
| 4 | AC3 L2 取实时 `DraftText`，重排后不回落旧值 | **PASS** | VM 打开时 `WorkbenchViewModel.cs:845` 取 `DraftText`（非 `Draft.Patch`）；View 层 `WorkbenchPageView.cs:180-186` 在 `DraftText` 变化时原地更新 L2，`:710-714` 每次重排重建面板后**再用当前 `DraftText` 覆盖快照**；`DraftText` 变更同时触发 `HasUnsavedDraft` 通知（`WorkbenchViewModel.cs:73-80`、`FluentViewModelBase.cs:44-57`）→ 走 `WorkbenchPageView.cs:188` 全量 `Render()`，即测试 `RegionTextComparePanelTests.cs:96-115` 实际覆盖了"重排后仍显示当前值"。 |
| 5 | 「恰好一次」位置可辩护 + 1/2 次可复现 | **PASS** | 生产代码唯一调用点 `WorkbenchViewModel.cs:795-798`（注释与实现一致，不传 `regionIds`）；入口只有 `WorkbenchPageView.cs:704-705` 的按钮；端口层无缓存（Fake 每次记录 `FakeHostController.cs:1206-1215`）。测试 `RegionTextComparePanelTests.cs:54-66`（`Assert.Single(host.RegionTextCalls)` 且 `RegionIds == null`）与 `:137-161`（打开 1 次 → 关闭 → 再开 2 次）。 |
| 6 | 未改 `FluentUi.Banner` 签名 | **PASS** | `git diff --quiet 9d0186a3d 42123ae67 -- .../Controls/FluentUi.cs` → **EXIT 0**、diff 0 行；冲突横幅调用保持原 5 参形态（`WorkbenchPageView.cs:700-701`），「查看对照」是同一纵向容器内的独立控件。 |
| 7 | 视觉证据缺口是否支撑 AC3/AC4/AC5 | **PASS（结构性证据可接受）** | 无像素/截图基线；结构断言覆盖双栏存在/标题/只读/唯一按钮/AutomationProperties；`TextWrapping.Wrap` 只在代码层（`RegionTextComparePanel.cs:199-200`），无测试断言。结论与依据见 §3.7：**结构性证据可接受**，但只能表述为"结构性验收"，不得称"已完成视觉验收"。 |
| 8 | 测试真实性（实跑、无 skip/xfail、既有断言只加强） | **PASS** | 实跑 14 通过 / 0 失败 / 0 跳过 / EXIT 0（§3.8 原始输出）；两个被审测试文件**无**任何 `Skip=`/xfail；`FluentResidualBatchATests.cs` 仅删 1 条被规格要求反转的旧断言，其余既有断言原样保留（加强为 `Assert.Single`）。 |
| 9 | 越界 | **PASS** | `git diff --name-status 9d0186a3d 42123ae67` 恰 5 文件（A/M/M/M/A，816 插入 / 5 删除）；`IHostController.cs` / `HostRuntime.cs` / `CoreServiceClient.cs` / inventory / 冻结记录 / `STATUS.md` / `REBASELINE_PLAN.md` / `TASK_LEDGER.md` 的 diff 输出均为 **0 行**。 |
| 10 | 门禁四件套 | **PASS** | §3.10 原始输出：`check.ps1` 默认与 `-TaskPath doc/tasks/FEA-06-RESIDUAL-4B.md` 均 `PASS (3 warnings)`/EXIT 0；`verify_pins.ps1` `PIN AUDIT: PASS (all 18)`，C07 `498882eb1750`；`--check` `OK: rendered counts match FEA-C07 doc`，EXIT 0（stdout `IHostController 80` / 合计 `87`）。 |

---

## 3. 关键证据详述

### 3.1 AC5：正向与负向断言并存（最关键项）

**父提交（`9d0186a3d`）原断言**（`apps/desktop-avalonia/tests/NewManga.App.Tests/FluentResidualBatchATests.cs:668-669`）：

```csharp
Assert.DoesNotContain(shell.WorkbenchView.GetVisualDescendants().OfType<Button>(),
    button => button.Content?.ToString()?.Contains("查看对照", ...) == true);
```

**子提交（`42123ae67`）同文件**：

- 正向：`:672-674` —— `Assert.Single(...查看对照...)`，并要求 `AutomationProperties.GetName == "查看对照"`（比原反向断言更强：不仅存在，而且**恰好一个**、a11y 名一致）。
- 负向（**同一用例**）：`:676-687` —— fake 未注册投影 ⇒ 点击入口后断言 `panel.Status == ProjectionUnavailable`、`ReasonCode == REGION_TEXT_PROJECTION_UNAVAILABLE`、`BaseLayer`/`WorkingLayer` **均为 null**、整个视图（不只面板）无任何 `"draft text"` TextBlock。
- 独立负向用例：`RegionTextComparePanelTests.cs:296-318` —— 投影里只有**别的 region** 的文本时，断言 `TargetNotFound`、两层 null、全视图不含 `"别人家的译文"` 与 `"draft text"`、面板内唯一按钮是「关闭」。

**结构性保证**（面板不会伪造）：`RegionTextComparePanel.cs:116-124` 只在 `BaseLayer`/`WorkingLayer` 非 null 时构建文本行；失败记录由 `WorkbenchViewModel.cs:868-873` 创建，两层恒为 null。因此"投影不可用 ⇒ 零对照文本行"不是靠测试碰巧通过，而是构造上不可能渲染。

**判定：PASS**。旧断言按 4A S5 要求翻为正向，负向断言**同时新增且落在同一用例**，另有独立用例加强；未发现任何"只改旧断言"的削弱。

### 3.2 `DraftErrorMap` 19 键闭集

- 子提交 `WorkbenchViewModel.cs:934-947` 共 **19** 键；父提交同一块的键集合与子提交 `Compare-Object` **完全一致**（含 `TARGET_NOT_FOUND`，父提交 `git show 9d0186a3d:...` 实测存在）。
- `REGION_TEXT_PROJECTION_UNAVAILABLE` 与 `HOST_NOT_READY` 仅存在于 `RegionTextComparePanel.cs:35-40` 的 `RegionCompareReasonCodes`（面板本地原因码），**未**进入 `DraftErrorMap`。
- 测试 `RegionTextComparePanelTests.cs:288-291` 机械守住三点：`Assert.Equal(19, DraftErrorMap.Codes.Count)`、两新码 `DoesNotContain`、`TARGET_NOT_FOUND` `Contains`。

**判定：PASS**。`TARGET_NOT_FOUND` 是**借用同名既有键**，不是新增；4B 卡 AC5 把三者统称"面板本地原因码"的措辞与 4A P2-5 及本实测不一致，属卡面文字问题（P3-2），不影响实现。

### 3.3 AC4：三条原因的固定优先级与空集合语义

实现顺序（`WorkbenchViewModel.cs`）：

1. `:788-793`：`_host.Snapshot.State != HostViewState.Ready` → `HostNotReady`，**在投影调用之前 return**（test `:204-219` 断言 `Assert.Empty(host.RegionTextCalls)`）。
2. `:796-798` 调用一次；`:800-806` 返回 `null` → `ProjectionUnavailable`。
3. `:808-826` 按 region id 匹配；找不到时：
   - `:813` `Regions.Count == 0 && PageWidth != null && PageHeight != null` → `EmptyPage`（"该页没有区域"，**非失败态**，无原因码）；
   - 否则 `:822-825` → `TargetNotFound`。

`RegionPageTextProjection` 的 `page_size: null` 在严格解析中映射为 `PageWidth/PageHeight` 双 null（`RegionTextProjection.cs:238-258`；该解析器要求 `page_size` 字段**必须存在**，缺失即 `FormatException`，因此 VM 的"双 null = extent 不可读"判定不会把 malformed 结果误判成未知 page），测试用 `new RegionPageTextProjection("page-1", null, null, [])` 构造（`RegionTextComparePanelTests.cs:241-243`），断言 `TargetNotFound` 且不出现空态文案（`:248-253`）。三条 reasons 的文案在源码中各不相同（`:790-791` / `:802-804` / `:823-824`），未合并。

**判定：PASS**。`[] + page_size: null` 不会被渲染成「无冲突」或空态；另有 `[] + page_size` 的非失败空态用例（`:256-272`）。

### 3.4 AC3：L2 实时性（含"重排后回落旧值"判定）

**实现分工**：VM 的 `Compare` 记录是打开瞬间快照（`WorkbenchViewModel.cs:849-857`）；实时性由 View 保证：

1. `DraftText` 变化 → `WorkbenchPageView.cs:180-186` 命中 `DraftText` 分支，原地 `panel.UpdateWorkingText(_viewModel.DraftText)` 后 **return**（不整页重排）；
2. 同一 setter 随后发 `HasUnsavedDraft` 通知（`WorkbenchViewModel.cs:78`、`FluentViewModelBase.cs:56-57`），View 在 `WorkbenchPageView.cs:188` 执行 `Render()` → `RenderStatusHost` 重建冲突卡；
3. 重建时 `WorkbenchPageView.cs:710-714` **先按快照建面板，再用实时 `DraftText` 覆盖 L2 文本块**（`RegionTextComparePanel.cs:155-170` 同时刷新可见文本与 `AutomationProperties.Name`）。

因此两条路径（原地更新 / 整页重排）最终显示的都是**当前** `DraftText`；快照中的旧 `WorkingLayer.Text` 在覆盖后不会出现在视觉树里（该记录字段只被测试读取）。测试 `RegionTextComparePanelTests.cs:96-115` 先断言初始 `"draft text"`，改 `DraftText` 为 `"刚输入的实时文本"` 并 `RunJobs()`（此时确实经历上述 `Render()`）后，断言面板 TextBlock 含新值、**不含**旧值。

**判定：PASS**。未发现 L2 回落旧值；"重排后回落成旧值"的 P1 条件不成立。L1 快照按 R-9 设计接受。

### 3.5 「恰好一次」的边界

- 生产代码调用点唯一：`WorkbenchViewModel.cs:796-798`；`grep` 全 App 源码仅此一处调用 `ListPageRegionTextsAsync`（其余为接口/实现/Fake）。
- 无缓存：VM 不保存投影；每次 `OpenRegionCompareAsync` 都发一次；关闭只清状态（`:862-866`），不发请求（test `:144-160`）。
- 重排不重复调用：打开后的 `Render()` 从 `Compare` 快照重建面板，不再调用端口（test `:59-66` 在 `RunJobs()` 后仍 `Assert.Single`）。
- 可复现的 1/2 次：test `:137-161` 断言打开后 1 次、关闭+再开后 2 次。

**判定：PASS**。断言位置（VM + UI 计数）可辩护：不在端口层加缓存，符合 4B R-10。

### 3.6 `FluentUi.Banner` 零改动

`git diff --quiet 9d0186a3d 42123ae67 -- apps/desktop-avalonia/src/NewManga.App/Controls/FluentUi.cs` 返回 `EXIT=0`，`git diff` 输出 0 行。冲突横幅调用仍为 `FluentUi.Banner(StatusKind.Stale, "并发冲突", _viewModel.Error, "重读草稿", …)`（`WorkbenchPageView.cs:700-701`），「查看对照」作为同一 `Stack` 容器内的独立 `Button`（`:704-705`）渲染，Banner 单 action 语义未被挪用。

### 3.7 视觉证据缺口：明确结论

**结论：结构性证据可接受（限定为"结构性验收"，不构成视觉验收）。**

依据：

- **AC4/AC5 本质是状态与"零伪造"不变量**，可由结构断言完全判定；本轮已覆盖成功/四类失败/空态、零文本行、唯一按钮、双层 null 等全部判别点。
- **AC3 的关键用户面**（冲突态才出现入口、双栏存在、标题与 `AutomationProperties.Name`、无输入控件、无覆盖/应用动作、Esc/关闭、投影一次）均有结构断言；`TextWrapping=Wrap` 与"无固定高度"**仅代码层可证**（`RegionTextComparePanel.cs:199-200`，未设 `Height`），新增测试**未**断言这两点（P3-3）。
- **像素/主题/对比度**无法由结构证据保证；但面板只使用既有样式类与既有主题笔刷（`FluentUi.Stack/Text/Card/Button`），不新增颜色常量，回归风险有限。

**附带要求**：按 DSH R-12（`doc/tasks/FEA-06-RESIDUAL-4B.md:225-230`），证据 README 必须写明"无像素级证据，用户可见效果未做截图层验收"，收口 limitation 必须登记该项；**不得**把本结论表述为"已完成视觉验收"。若产品需要像素确认，另开冒烟卡（可复用 `tools/p2-ui-smoke.ps1`）。

### 3.8 测试真实性（本轮实跑）

命令（工作树、`HEAD=e6b4009fc`，代码与被审 head 一致）：

```powershell
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests `
  --filter "FullyQualifiedName~RegionTextComparePanelTests|FullyQualifiedName~I13_WorkbenchConflictRow" --nologo
```

原始结果（两次运行一致）：

```text
已通过! - 失败: 0，通过: 14，已跳过: 0，总计: 14，持续时间: 3 s - NewManga.App.Tests.dll (net9.0)
EXITCODE=0            # 外壳耗时 12.3 s
```

14 例逐名通过（detailed logger 实测）：`RegionTextComparePanelTests` 13 例（`ConflictState_ShowsCompareEntry_AndKeepsTheBannerAction`、`OpenCompare_RendersTwoReadOnlyLayers_AndCallsTheProjectionExactlyOnce`、`WorkingLayer_FollowsTheLiveDraftText_NotThePersistedPatch`、`RevisionDrift_RaisesTheTypedNotice_AndShowsBothRevisions`、`Close_RestoresTheBannerOnly_AndReopenCallsOncePerOpen`、`Escape_ClosesTheComparePanel`、`CompareEntry_IsAbsentOutsideTheConflictState`、`HostNotReady_IsReportedFirst_WithoutRequestingTheProjection`、`ProjectionUnavailable_IsReportedSecond_AndRendersNoLayers`、`EmptyRegionsWithNullPageExtent_IsTargetNotFound_NeverAnEmptyOrSafeState`、`EmptyRegionsWithPageExtent_IsTheEmptyPageState_WithoutAReasonCode`、`FailureReasonCodes_ArePairwiseDistinct_AndDoNotExtendTheFrozenDraftErrorMap`、`FailurePanel_NeverRendersAnyCompareText`）+ `FluentResidualBatchATests.I13_WorkbenchConflictRow_ConflictBannerShowsWithoutFabricatedCompare`。

- **无新增 skip/xfail**：过滤运行 `已跳过: 0`；两个被审测试文件内无任何 `Skip=`/xfail 属性（其余文件中的 gated skip 与本卡无关）。
- **既有断言只加强**：`FluentResidualBatchATests.cs` 的 diff 仅删除 1 条被规格要求反转的旧断言（+1 行注释改写），新增 20 行；其余 I13 断言原样保留。

### 3.9 越界核对

```text
git diff --name-status 9d0186a3d 42123ae67
A  .../Controls/RegionTextComparePanel.cs
M  .../ViewModels/Fluent/WorkbenchViewModel.cs
M  .../Views/Fluent/WorkbenchPageView.cs
M  .../tests/NewManga.App.Tests/FluentResidualBatchATests.cs
A  .../tests/NewManga.App.Tests/RegionTextComparePanelTests.cs
```

- `git diff --numstat` 合计 `+816 / −5`；**仅**上述 5 文件。
- 对 `IHostController.cs`、`HostRuntime.cs`、`CoreServiceClient.cs`、`doc/plan/FEA-C07_API_INVENTORY.md`、`doc/plan/FEA-CONTRACT-FROZEN-C07.md`、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md` 逐个 `git diff` → 输出 **0 行**。
- 复核开始时 `git status --short` 为空；结束时未跟踪文件仅本报告与 DSH 在复核期间新建的 `verification/FEA-06-RESIDUAL-4B/README.md`（构建产物未入库）。

### 3.10 门禁四件套（本轮原始输出）

| 门禁 | 命令 | 结果 |
|---|---|---|
| ① | `pwsh -NoProfile -File tools/governance/check.ps1` | `Governance check: PASS (3 warnings)`，`EXIT=0`（Task: MAINT-1-RELEASE-MONITOR） |
| ② | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-06-RESIDUAL-4B.md` | `Governance check: PASS (3 warnings)`，`EXIT=0` |
| ③ | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `PIN AUDIT: PASS (all 18)`，`OK C07 498882eb1750`，`EXIT=0` |
| ④ | `python tools/generate_api_inventory.py --check` | `OK: rendered counts match FEA-C07 doc`，`EXIT=0`；stdout `\| IHostController \| 80 \| 4 \|`、`\| **合计** \| **87** \|`、`#80 ListPageRegionTextsAsync → Task<RegionPageTextProjection?>` |

3 条 warning 均为既有预算/非终态台账提示（`9 个非终态 Task`、STATUS 80% 预算、PLAN 80% 预算），与本 diff 无关。

---

## 4. 发现清单

### P0

无。

### P1

无。

（按 4A S5 的硬规则：只把旧断言翻正向、不同时补负向断言才判 P1；本刀两条并存，故不成立。）

### P2（收口前处置或经 DSH 明示登记）

- **P2-1（S6 焦点未实现）**：4A S6 要求"面板打开后焦点落在 `关闭` 按钮"（`doc/tasks/FEA-06-RESIDUAL-4A.md:142`）。`RegionTextComparePanel` 构造与 `WorkbenchPageView.cs:708-718` 挂载路径均**没有** `Focus()`，测试也无焦点断言。用户可见影响：键盘用户打开后焦点仍在「查看对照」按钮，必须 Tab 才能到「关闭」；不满足已冻结的 a11y 判据。修复很小（面板 `AttachedToVisualTree` 后 `CloseButton.Focus()` + 一条 headless 断言），建议 4B-4 内完成；若不修，须由 DSH 明示登记为 limitation。
- **P2-2（AC4"文案两两不同"缺机械断言）**：4B AC4 明确要求"分别断言码与**文案**两两不同"（`doc/tasks/FEA-06-RESIDUAL-4B.md:99`）。现有测试只断言 `Status` + `ReasonCode`（`RegionTextComparePanelTests.cs:204-254`），唯一"两两不同"断言只针对**码**（`:275-292`），**未**比较三条 `ReasonText`。实现本身正确（三条文案见 `WorkbenchViewModel.cs:790-791` / `:802-804` / `:823-824`），但若未来有人把三条文案合并，现有测试不会变红——这正是 P2-2 想禁止的失败模式。建议补一条 `Assert.Equal(3, reasonTexts.Distinct().Count())` 或逐字断言。
- **P2-3（收口证据未落地，非代码缺陷）**：复核期间 DSH 新建了 `verification/FEA-06-RESIDUAL-4B/README.md`（10:34，未跟踪；已含 R-12 的"无像素级证据"披露与 P2-1/P2-2 登记，方向正确，**不在本刀被审 diff 内，本报告不为其内容背书**）。但 `logs/` 仍只有 4B-2b 的 4 份日志（`api-inventory.log`、`gates-2026-11-14-4b2b.log`、`member-table-eq-stdout.log`、`pin-before-after.log`，均为 09:59），**缺** 4B-3 的 build/App.Tests/CoreClient.Tests/门禁原始日志（`doc/tasks/FEA-06-RESIDUAL-4B.md:150-161` 的证据计划）。这是 AC7/AC8 的收口阻断项，建议 4B-4 补齐后再提交证据。
  - 附带（范围外，仅提示）：该 README 的 AC1 证据行把 `ListPageRegionTextsAsync` 定到 `IHostController.cs:277`，实测该行是 `SetRegionTypeAsync` 的文档注释，新方法在 `:557`；`FakeHostController.cs:1215` 是 `return` 行（方法体起于 `:1208`）。建议 DSH 在提交前校正，避免证据索引与源码行号错位。

### P3（登记，不阻断）

- **P3-1**：`TARGET_NOT_FOUND` 的处置文案为"目标区域已变化；请重新读取页面。"（`WorkbenchViewModel.cs:824`），4A S5 表规定的是"目标页面已变化；请重新读取页面"（`doc/tasks/FEA-06-RESIDUAL-4A.md:132`）；且该码把"region 不在投影"与"page 未知"合并，S5 只定义了后者。功能正确、文案更贴合 region 缺失场景，建议收口时登记或回 4A 补 errata。
- **P3-2**：4B AC5 把 `TARGET_NOT_FOUND` 与两个新码并列为"面板本地原因码，不得加入该映射"（`doc/tasks/FEA-06-RESIDUAL-4B.md:100`），与 4A P2-5（仅 `REGION_TEXT_PROJECTION_UNAVAILABLE` 为本地码）及实测（`TARGET_NOT_FOUND` 本就在 19 键内）不一致；实现与测试的处理正确，建议收口修正卡面措辞。
- **P3-3**：新增测试**未**断言 `TextWrapping=Wrap`、无固定高度、两栏 Stack 的 `AutomationProperties.Name`（`RegionTextComparePanelTests.cs` 全文无 `Wrap`/`Height`/`Focus` 断言）；R-12 裁决文本称结构性断言含"换行属性"，与测试实际覆盖面不符。代码事实成立（`RegionTextComparePanel.cs:199-200`），Evidence README 应如实写成"代码审阅"而非"测试断言"。
- **P3-4**：对照状态未在"离开 Conflict / 页面重载 / `LoadPageAsync` 改写 `SelectedRegion`"时收起。`WorkbenchViewModel.cs:494`、`:903-906` 可改写 `SelectedRegion` 而不调用 `CloseRegionCompare`；`WorkbenchPageView.cs:708` 只凭 `IsCompareVisible && Compare` 渲染。理论上"对照打开 → 导航离开/重载 → 再次进入冲突态"会用旧 `Compare` 快照自动重开面板（L2 会被刷新、L1 不会），且无需用户点「查看对照」。建议在 `State` 变为非 Conflict 或 `LoadPageAsync` 时 `CloseRegionCompare()`；当前未在常规 UI 流程复现，故登记不阻断。
- **P3-5**：I13 里新增的 `DoesNotContain("draft text")`（`FluentResidualBatchATests.cs:686-687`）在该用例中 `DraftText` 实为空串（该 fake 未设 `ScriptedDrafts`，`CurrentDraft == null`），若实现回退会渲染"（空文本）"而非 `"draft text"`；该行本身不构成回退检测。真正的回退检测由 `FailurePanel_NeverRendersAnyCompareText`（`:296-318`，该用例 `DraftText == "draft text"`）与 `Assert.Null(BaseLayer/WorkingLayer)` 承担，故不影响 AC5 结论。
- **P3-6**：4A S4 的"RegionBox 内纵向排列"未字面成立——面板挂在 `_statusHost`（`WorkbenchPageView.cs:167`，与既有冲突横幅同容器），并非 RegionBox 内部；与既有结构一致，且 R-4 已披露该偏差，登记即可。

---

## 5. 4B 是否可进入收口（AC1–AC8 是否可判）

**可以进入收口流程**：本刀 P0 = 0 / P1 = 0，AC3/AC4/AC5 的实现判 PASS，无阻断性代码缺陷。但"进入收口"不等于"AC 全部已判 PASS"：

| AC | 本轮可判性 | 说明 |
|---|---|---|
| AC1 端口与生产链路 | **可判（前两刀）** | 本提交零改动；实测签名/实现齐备（`IHostController.cs:557`、`HostController.cs:1005-1026`、`HostRuntime.cs:848-858`、`NullHostController.cs:181`、`FakeHostController.cs:1208-1215`、`CoreServiceClient.cs:1166`），定向测试构建通过。 |
| AC2 统计 80/87 + pin v1.10 | **可判 PASS** | `--check` EXIT 0、stdout 80/87；`verify_pins` 18/18、C07 `498882eb…`；v1.9 原值保留。 |
| AC3 UI | **可判 PASS（结构性）** | 入口/双栏/只读/标题/Esc/关闭/恰好一次均实测通过；焦点（P2-1）与 Wrap/高度断言（P3-3）为缺口。 |
| AC4 空态/失败态 | **实现 PASS；机械验收 PARTIAL** | 优先级、空集合语义、四场景实现正确；"文案两两不同"缺断言（P2-2）。 |
| AC5 负向不变量 | **可判 PASS** | 正向+负向并存，另有独立负向用例；19 键未扩。 |
| AC6 wire 形状与解析 | **本轮未复跑** | 属 4B-1 前刀；本 reviewer 未执行 CoreClient.Tests（不属被审 5 文件），需 DSH 用 4B-1 证据复跑确认后判。 |
| AC7 门禁 + 零越界 | **可判 PASS（证据待落盘）** | 四项 EXIT 0、零越界均实测；但 4B-3 的门禁原始日志尚未进 `verification/FEA-06-RESIDUAL-4B/logs/`（P2-3）。 |
| AC8 全量测试 + 独立 Review | **当前不可判** | 全量 App.Tests / CoreClient.Tests 日志缺失（本轮只跑定向 14 例）；证据 README 已由 DSH 在复核期间补建（未跟踪、本报告不为其内容背书）；本报告即独立 Review，待 DSH 回填/复核后可判。 |

**收口前置动作（建议顺序）**：

1. 处置 P2-1（S6 焦点）与 P2-2（AC4 文案断言）——修，或由 DSH 在 4B 卡/Handoff 明示登记为 limitation；
2. 补齐 4B-3 的 build/App.Tests/CoreClient.Tests/门禁原始日志到 `verification/FEA-06-RESIDUAL-4B/logs/`；复核期间新建的 README 先校正 AC1 行号（`IHostController.cs:277 → :557`）再提交（P2-3）；
3. DSH 复跑全量 App.Tests 与 CoreClient.Tests（AC8/AC6），并把本报告结论回填 4B 卡；
4. 登记 P3-1…P3-6（可并入收口记录的 limitation/后续项）。

---

## 6. 限制与未做项

- **未做全量测试**：只按用户指定 filter 跑了 14 例；`NewManga.App.Tests` 全量与 `NewManga.CoreClient.Tests` 未由本 reviewer 复跑（AC6/AC8 因此标注"未复跑/不可判"）。
- **无像素/截图验证**：未启动真实窗口、未做主题/对比度/像素基线；结论限定为结构性验收（§3.7）。
- **未验证真实键盘端到端**：`Esc` 由 `HandleKeyForTest` 与真实 `OnWorkbenchKeyDown` 共用逻辑（`WorkbenchPageView.cs:219-235`），headless 下未注入真实键事件；与 R-11 已披露的缺口一致。
- **门禁运行点**：在工作树 `HEAD=e6b4009fc` 运行（复核期间由 DSH 新增的 doc-only 提交；`apps/` 与 `src/` 零差异），未 checkout 到 `42123ae67`（遵守只读约束）。
- **未核验**：4B-1/4B-2 的历史证据日志内容只做了索引级检查（`verification/FEA-06-RESIDUAL-4B/logs/` 4 份），未逐行复算 pin/成员表（本报告聚焦 4B-3 diff）。

---

*报告结束。本文件为只读复核产物，不构成 approved 的代写或代码修改授权。*
