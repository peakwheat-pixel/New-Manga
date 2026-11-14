---
task: TRANS-ENTRY-UI
task_id: TRANS-ENTRY-UI
reviewer: independent sub-agent (r2, read-only, not involved in r1)
reviewer_agent: agent-8（lead 派发；独立上下文；未参与本卡实现、返修与 r1 复核）
reviewer_kind: subagent
author: DSH（实施会话）
base_commit: a9591dc1b
reviewed_head: fdda639a1
verdict: changes_requested
decision: changes_requested
date: 2026-11-14
scope: read-only
---

# Review：TRANS-ENTRY-UI（L1-T-C）r2 — 只核 r1 的三条 P1

> **结论：`changes_requested`。本卡暂不能收口。**
> 三条 P1 中 **P1-1、P1-3 已真实关闭**（含判别力实测）；**P1-2 只关闭了两个面中的一半**——Fluent 矩阵的 `ErrorCell` 与 Studio drawer 的 **step 行**已接映射，但 r1 明确指认的 **drawer 详情行**（`StudioBatchViewModel.cs:616-618` 的 `row.ErrorCode ?? "无错误码"`）**仍是裸码**，且整条执行期接线**没有任何测试**（grep 为 0）。剩余返修为 1 行代码 + 1 条测试。
> 另发现 6 条 P2、3 条 P3（均为可读性/证据一致性/边缘误判，不阻断架构面）。

## 0. 审查者、固定点与方法

- **身份**：`agent-8`，lead 派发的独立上下文子 agent；**只读**复核；**未参与**本卡实现、返修，也**未参与** r1。仓库内唯一新增文件是本报告。
- **固定点**：`reviewed_head = fdda639a1`（父 `a9591dc1b`）。复核开始时 `HEAD = fdda639a1`，工作树干净（`git status --short` 空）。
- **方法**：只针对 r1 的三条 P1 及其接缝做窄复核——逐行读 `fdda639a1` 的 diff、其调用链与两侧事实（Host 就绪语义 / Core 折叠语义 / 绑定写入语义）；用**临时改副本 + 还原 + SHA-256 核对**验证新测试的判别力；实跑 `dotnet test` 与四件套门禁。
- **零越界自证**：临时验证只改过 1 个文件 1 行，见 §2.1(c)；已按字节还原，SHA-256 与改前一致，工作树恢复干净。

## 1. 逐项结论（只评 r1 的三条 P1）

| # | 复核项 | 结论 | 一句话证据 |
|---|---|---|---|
| 1 | **P1-1** 空章判定是否与「非就绪/读失败」真正分开 | **PASS（主根因已关闭）** | `WorkbenchViewModel.cs:200` 现在要求 `_host.Snapshot.State == HostViewState.Ready`；非 Ready 时不再产出空章句，且有**判别力已实测**的测试（回退该行 → `UnreadyHost_DoesNotPretendTheChapterIsEmpty` 红）。残留 1 条 P3：**Ready + 读失败**仍返回空列表（`HostController.cs:973-980` 吞异常且不改 Snapshot），此子路径未被状态门覆盖 |
| 2 | **P1-2** 执行期是否接上四类文案 | **FAIL（部分关闭：2/3 面）** | ✅ `FluentRunProjection.cs:260-266`（经 `WorkbenchPageView.cs:618` 渲染）与 ✅ `StudioBatchControls.cs:450`（drawer step 行）已接 `TranslateErrorText.ForCode`；❌ `StudioBatchViewModel.cs:616-618` 的 drawer **详情行**仍 `row.ErrorCode` 原样输出（渲染于 `StudioBatchControls.cs:437-438, 464`，drawer 在 `:578` 实例化）；❌ 全仓测试对 `ErrorCell`/`DrawerDetail`/`StudioBatchDrawerControl` 的引用 **为 0** |
| 3 | **P1-3** README 与设置页文案是否改对 | **PASS（内容达标）** | `verification/TRANS-ENTRY-UI/README.md:50,71` 已承认设置页**有** book/chapter 入口并引 `Pages.cs:1141`；`ProviderBindingsSection.cs:86` 含「当前仅全局绑定驱动执行」，且「会保存并显示、不驱动执行」与 Core 语义逐字相符。残留 2 条 P2：`**…**` 星号会原样显示、Console 的 scope 提示未同步；另任务卡旧说法未更正 |

## 2. 逐项证据

### 2.1 P1-1：空章句是否只在「就绪且确实 0 页」时出现

**(a) 代码事实：状态门成立。**

`WorkbenchViewModel.cs:192-205`：

```csharp
var pages = await _host.ListChapterPagesAsync(_chapterId, cancellationToken);
chapterLooksEmpty = pages.Count == 0 && _host.Snapshot.State == HostViewState.Ready;   // :200
```

失败分支（`:228-231`）仍为 `chapterLooksEmpty ? EmptyChapter : ForCode(_host.Snapshot.LastError)`。

**（b）两个谓词确实同源，不会「门开了但列表是空的」或反之。**

| 侧 | 判定 | 位置 |
|---|---|---|
| 读页返回空 | `_runtime is null \|\| !_runtime.Result.IsReady` → `Array.Empty` | `HostController.cs:963-970` |
| 就绪定义 | `HostOptions.IsReady => Status == HostStatus.Ready` | `HostOptions.cs:21` |
| Snapshot 状态 | `HostStatus.Ready → Ready`、`AlreadyRunning → AlreadyRunning`、其余 `→ Failed` | `HostController.cs:3042-3048` |

⇒ **Starting / Failed / AlreadyRunning 三种非 Ready 状态，读页必返回空列表，且状态门必为 false**；r1 表里「Host 未就绪 → 谎称空章」这一行已从机制上消除。`AlreadyRunning` 同样 `IsReady=false`，不会因「非 Ready 但有页」产生反向漏判。

**（c）测试判别力：实测。** 我把 `:200` 临时改回 `chapterLooksEmpty = pages.Count == 0;`（保留注释、只改这一行），跑滤镜用例：

```
dotnet test …NewManga.App.Tests.csproj --filter "FullyQualifiedName~TranslateEntryUiTests"
[xUnit.net] NewManga.App.Tests.TranslateEntryUiTests.UnreadyHost_DoesNotPretendTheChapterIsEmpty [FAIL]
失败! - 失败: 1，通过: 5，已跳过: 0，总计: 6        EXIT=1
```

- 失败的正是 `UnreadyHost_DoesNotPretendTheChapterIsEmpty`（`TranslateEntryUiTests.cs:103-123`）——它断言 `vm.Error != EmptyChapter` 且 `== ForCode("INVALID_REQUEST")`，回退后 `chapterLooksEmpty=true`，两条断言同时不成立 ⇒ **这条测试真的会红，有判别力**。
- `ReadyHostWithNoPages_ShowsTheEmptyChapterSentence`（`:86-101`）在回退版下**仍绿**——它不判别状态门（Ready 场景回退后行为不变），它的价值是**钉住正向输出**（`vm.Error == EmptyChapter`、且 `DoesNotContain("INVALID_REQUEST")`），防止「一刀切不再显示空章句」的过度修正。两条测试**互补**，可接受。
- 该测试确实走到了 StartRun 失败分支（不是被前置门拦下）：`ScriptedStartRuns.Enqueue(null)` + `ScriptedStartRunErrorCode="INVALID_REQUEST"`，且 `HostViewSnapshot.WritesAllowed` 默认 `true`（`IHostController.cs:31`）⇒ `IsReadOnly=false`，`StartRunAsync` 通过 `:159` 的守卫。
- **还原与核对**：`Copy-Item` 还原后 `SHA-256 = 0A18D7D925CBB6F1D1E6FE94527446420FE32A5E5BEEAF620C2EF4F37E0D5ED4`，与改前逐字节一致；`git status --short` 为空。

**（d）残留（P3，不阻断）：`Ready` 门不等价于「探测成功」。** `HostController.ListChapterPagesAsync` 的 `catch (Exception ex) when (IsUiFacingFailure(ex))`（`:977-980`）同样返回空列表，且**不改 Snapshot**；`IsUiFacingFailure`（`:2964-2968`）包含 `CoreOperationException`/`IOException`/`OperationCanceledException` 等。即：**Host 仍 Ready、但一次读页失败**时，`pages.Count == 0` 为真 ⇒ 仍会给出空章句。r1 的 P1-1 原文把「读失败」与「未就绪」并列为根因，本轮修法只覆盖后者。概率低于未就绪路径、且真正空的章节给出的句子并不假，故记 **P3 残留**，建议后续用「探测是否成功」的显式信号（如 `IReadOnlyList? ` 可空返回或 out 标记）替代状态推断；不要在没改契约的情况下硬做。

**（e）只读场景不再可达：** `IsReadOnly => _host is null || !_host.Snapshot.WritesAllowed`（`:97`），`StartRunAsync` 在 `:159` 直接返回 ⇒ r1 表中「只读模式显示空章句」这一行在新实现下**根本进不到失败分支**，该行随之失效（不是靠文案掩盖）。

### 2.2 P1-2：执行期两个用户可见面

**(a) Fluent 批次矩阵：已接。**

```csharp
// FluentRunProjection.cs:260-266
public string ErrorCell => string.IsNullOrWhiteSpace(ErrorCode)
    ? FluentRunProjection.Missing
    : NewManga.App.Services.TranslateErrorText.ForCode(ErrorCode);
```

渲染点 `WorkbenchPageView.cs:618`（`FluentUi.Text(row.ErrorCell, …)`）。⇒ 401/403、429、4xx 在执行期矩阵里显示四类句，**不再是裸码**。

**(b) Studio drawer step 行：已接。** `StudioBatchControls.cs:450`：

```csharp
row.Children.Add(StudioUi.Text(step.ErrorCode is null ? string.Empty
    : NewManga.App.Services.TranslateErrorText.ForCode(step.ErrorCode), "meta"));
```

**(c) Studio drawer 详情行：仍是裸码（P1-2 未关闭的那一半）。**

```csharp
// StudioBatchViewModel.cs:616-618
public string DrawerDetail => _drawerRow is { } row
    ? $"{row.StateLabel} · {row.ErrorCode ?? "无错误码"} · steps {row.Row.Steps.Count}"
    : string.Empty;
```

绑定与渲染链：`StudioBatchControls.cs:437-438`（`_detail.Bind(TextBlock.TextProperty, … DrawerDetail)`）→ `:464`（`column.Children.Add(_detail)`）→ `:578`（`Drawer = new StudioBatchDrawerControl(viewModel)`）。**这正是 r1 §3 表格 P1-2 行原文指认的 `StudioBatchViewModel.cs:616-618`**，`fdda639a1` 未触该文件。用户选中一条失败页行时看到的是 `失败 · PROVIDER_AUTH_FAILED · steps 3`——与 r1 判定的「地图没画在错误发生的地方」完全同形。同类裸码还有 cell/row 的 `Tooltip`（`:82`、`:156`）。

**(d) 未知码保留原码：成立。**

```csharp
// TranslateErrorText.cs:60
_ => $"{code.Trim()}（未识别的错误码，请连同此码反馈）",
```

`EMPTY_TARGET_SELECTION`、`HOST_NOT_READY`、`HOST_READ_ONLY`、`ARTIFACT_WRITE_FAILED` 等都会**带着原码**出现，诊断信息没有被吞。

**(e) 非 provider 错误没有被硬套四类：成立。** `StudioInspectorPanel.cs:446-448` 的 `HistoryError` 直接 `Bind` 到 `TextBlock.Text`（历史读失败是内部文本，非 provider 码），**没有**经过 `ForCode`。`ForCode` 的兜底分支也只追加后缀、不替换成语义句，故不会把「历史读失败」说成 401/额度/限流。

**(f) 无测试保护（P2）。** 全仓测试：

```
grep -rn "ErrorCell" apps/desktop-avalonia/tests   → 0
grep -rn "StudioBatchDrawerControl|DrawerDetail"   → 0
grep -rn "ForCode" apps/desktop-avalonia/tests     → 5（全部在 TranslateEntryUiTests 的常量层/VM 层）
```

⇒ 把 `:260-266` 与 `:450` 整段回退成裸码，**测试仍全绿**。AC8「每类文案至少一条测试（断言用户可见字符串）」在执行期面上**仍未落地**（r1 对 AC3 提过的同一条批评在这里复现）。

### 2.3 P1-3：README 与设置页限定

**(a) README 已承认入口存在。** `verification/TRANS-ENTRY-UI/README.md:50`：

> **事实更正**：设置页本来就有 book/chapter 绑定入口（`Views/Pages.cs:1141` 实例化 `ProviderBindingsSection`，`:89-94` 有 scope/书/章选择器）。r1 指出我先前写「没有入口」是**不实**。…

`Pages.cs:1141` 实测存在（`Bindings = new ProviderBindingsSection(…)`），`:1451` 挂进「绑定」分栏。**与事实一致 ✅**。§4.3（`:71`）同步改写。

**(b) 设置页文案含要求句，且描述准确。** `ProviderBindingsSection.cs:85-88`：

> 把某个 provider profile 绑定到 (scope, capability) 槽位；**当前仅全局绑定驱动执行**：book/chapter 范围的绑定会保存并显示，但 Run 执行链只读全局槽位（跨书/跨章按槽位解析尚未接入）。book/chapter 范围用真实书库选择器。

准确性逐条核对 Core 侧：

| 文案断言 | Core 事实 | 结论 |
|---|---|---|
| 「会保存」 | `settings_commands.py:758-760`：无论 scope 都执行 `self._binding_store().save_bindings(rows)` | ✅ |
| 「并显示」 | `:794-818` 的 resolve 读同一 binding rows / run 快照 | ✅ |
| 「执行链只读全局槽位」 | `:747-753` `writes_flat_slot = scope["kind"] == "global"`；`:779-787` clear 同理 | ✅ |
| 「跨书/跨章按槽位解析尚未接入」 | 同上（扁平槽只有一格） | ✅ |

⇒ **P1-3 的判定条件（必须标注「当前仅全局绑定驱动执行」且不得反向暗示）已满足。**

**(c) 残留 P2-1：`**…**` 会原样显示。** 该文本经 `Ui.Text`（`Pages.cs:19-26`：`new TextBlock { Text = text, … }`）直接赋给 `TextBlock.Text`，**没有 Markdown 解析**。用户看到的是字面带星号的 `**当前仅全局绑定驱动执行**`。同文件其余文案（`:84`）均无 Markdown 习惯。修法：去掉两对 `**`（或改用 `bold` 片段）。

**(d) 残留 P2-2：Console 面未同步。** V2 Console 仍提供 book/chapter 的绑定 scope（`ConsoleViewModel.cs:1804-1823`，含「当前作品（book: …）」等标签），无「仅全局驱动执行」提示；r1 的返修建议原文即包含「以及 Console 的 binding scope 提示」。同一误导面在另一个入口仍开着。

**(e) 残留 P2-3：任务卡仍留着已被推翻的说法。** `doc/tasks/TRANS-ENTRY-UI.md:91` 仍写「AC5 **设置页无 scoped 入口，登记「未提供」**」，且 `reviewer: null`（`:11`）、AC 全部 `[ ]`（`:50-58`）、`delivery_head: null`（`:19`）。`fdda639a1` **未触碰任务卡**——更正只落在证据 README 里，权威任务文档仍是旧结论。

## 3. 新增问题核查（r1 之外的回归面）

| 检查 | 结论 | 证据 |
|---|---|---|
| `ForCode` 对 `EMPTY_TARGET_SELECTION` 的映射是否会误导 | **不会误导，但也不会现身** | Core 在 wire 前把 `EMPTY_TARGET_SELECTION` **折叠**成 `INVALID_REQUEST`（`core_service.py:6821-6822`），UI 收不到该码；若哪天收到，`:60` 会保留原码 + 「未识别」后缀。可接受 |
| `ForCode` 对 `INVALID_REQUEST` / `INVALID_INPUT` 的映射是否会误导 | **有误导面，且本轮把暴露面扩大了（P2）** | 两者共用「可能是模型名写错（404），也可能是账户额度/余额不足（402）」（`:30-31, :59`）。`INVALID_REQUEST` 是 Core 的**通用 validation 码**（如 `core_service.py:6696-6703` 的 payload 校验），且被折叠的 `EMPTY_TARGET_SELECTION`（"scope expands to no active pages"，`src/infrastructure/sqlite/pipeline.py:848`）也走这条路——例如章节**有页但页全部失效**时，用户会被指去改模型名/查额度。此前该句只在 StartRun 拒绝时出现，现在**每一行失败的矩阵单元格**都会显示它 → 误导面扩大。建议按 r1 §5.2.3：`INVALID_INPUT` 保留此句，`INVALID_REQUEST` 用「请求被拒绝（通用校验失败）」 |
| 四类文案是否仍互不相同 | **PASS** | `TranslateErrorText.cs:19-38` 四句互异；`TranslateEntryUiTests.cs:45-47` 断言 `Distinct == 4` |
| 未知码是否吞掉诊断 | **PASS** | `:60` 保留 `code.Trim()` |
| `ForCode(null)` 的旧坑 | **仍在（P3）** | `:49-52` 把「无错误码」映射成「还没有可用的翻译模型 Provider」。`ErrorCell` 用 `IsNullOrWhiteSpace` 挡住了空串/空白（`:260`），但 `StudioBatchControls.cs:450` **只判 `null`**——wire 上若出现 `"error_code": ""`（`RunJson.ReadString` 原样返回空串，`RunContracts.cs:584-594`），会显示成"未配置 Provider"。属潜伏缺陷 |
| 已知码是否丢掉机器码 | **P3** | `ErrorCell` 只输出自然语言句，401/429 句里虽有状态码但没有 `PROVIDER_AUTH_FAILED` 这类可反馈的标识；同仓 `RunStatusMonitor.StepErrorText` 的口径是 `中文（CODE）`（`:366`）——两处口径不一致 |

## 4. 实测记录

| 场景 | 命令（工作目录 `G:\CODEX\New Manga`） | 结果 |
|---|---|---|
| App.Tests（全量，新编） | `dotnet build … /NewManga.App.Tests.csproj -t:Rebuild` → `dotnet test … --no-build` | **PASS 921 / 0 failed / 11 skipped（932）**，5 m 50 s，`EXIT=0` |
| 判别力实验（回退版） | 同项目 `--filter "FullyQualifiedName~TranslateEntryUiTests"` | **1 failed / 5 passed / 6**，失败者 = `UnreadyHost_DoesNotPretendTheChapterIsEmpty`，`EXIT=1`；**已还原**（SHA-256 复核一致） |
| 治理门禁（默认） | `pwsh -NoProfile -File tools/governance/check.ps1` | `Governance check: PASS (3 warnings)`，`EXIT=0` |
| 治理门禁（本卡） | `… check.ps1 -TaskPath doc/tasks/TRANS-ENTRY-UI.md` | `PASS (3 warnings)`，`EXIT=0` |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `PIN AUDIT: PASS (all 18)`，`EXIT=0` |
| API 清单 | `python tools/generate_api_inventory.py --check` | `OK: rendered counts match FEA-C07 doc`，`EXIT=0`（计数仍 `1/80/6=87`，见 `doc/plan/FEA-C07_API_INVENTORY.md`；本卡未改 `IHostController`） |

**必须披露的一次自摆乌龙的测量（如实记录，避免误导后继者）**：我第一次跑全量时得到 **920 passed / 1 failed**，看似「提交本身这条测试就是红的」。复核后确认是**测量错误**：`Copy-Item` 还原时把源文件 mtime 还原成旧时间戳（`19:59:33`），而程序集是临时改动版编译的（`20:19:07`），MSBuild 判定「已最新」**跳过了重编**，于是测试跑的是**回退版位**。此后 `-t:Rebuild`（程序集 `:20:26:11`）+ `--no-build` 复跑即 **921/0/11**。凡「改副本验证」后必须强制重建，否则得到的是假红。

**未跑**：`NewManga.CoreClient.Tests` / `NewManga.Host.Tests`（本轮窄复核只需 App.Tests 的 921/0/11；且 r1 已记录 CoreClient 运行会向 `verification/FEA-09/logs/wire-redacted.ndjson` 追加一行的测试副作用，避免制造无关工作树变化）。

## 5. 零越界核查

```
$ git diff fdda639a1^ fdda639a1 --name-only
apps/desktop-avalonia/src/NewManga.App/ViewModels/Fluent/FluentRunProjection.cs
apps/desktop-avalonia/src/NewManga.App/ViewModels/Fluent/WorkbenchViewModel.cs
apps/desktop-avalonia/src/NewManga.App/Views/ProviderBindingsSection.cs
apps/desktop-avalonia/src/NewManga.App/Views/V2/Studio/Controls/StudioBatchControls.cs
apps/desktop-avalonia/tests/NewManga.App.Tests/TranslateEntryUiTests.cs
doc/reviews/TRANS-ENTRY-UI-r1.md
verification/TRANS-ENTRY-UI/README.md
```

- `src/**`（Python Core）：**0 文件**；`doc/contracts/**`：**0 文件**；`IHostController.cs` / wire 命令表：**未出现**。
- 题面口径「只含 `apps/desktop-avalonia/**` 与 `verification/TRANS-ENTRY-UI/**`」**严格讲被 `doc/reviews/TRANS-ENTRY-UI-r1.md` 超出**；但该路径在任务卡 `allowed_paths` 内（`doc/tasks/TRANS-ENTRY-UI.md:25` 的 `doc/reviews/TRANS-ENTRY-UI-*.md`），属 r1 复核入库，**不视为越界**。
- 复用 `IHostController.Snapshot`（C07 已列的 4 个非方法成员之一），**没有新增成员** → AC7 成立。

## 6. Findings

| ID | 级别 | 文件/行 | 问题 | 证据 | 建议 |
|---|---|---|---|---|---|
| R2-P1-1 | **P1** | `StudioBatchViewModel.cs:616-618`；渲染 `StudioBatchControls.cs:437-438, 464`（实例化 `:578`） | drawer 详情行仍原样输出 `row.ErrorCode`（`?? "无错误码"`）——正是 r1 P1-2 指认的面，`fdda639a1` 未改；用户看失败页仍见裸码 | 代码逐行 + `git diff` 不含该文件 | 改为 `row.ErrorCode is null ? "无错误码" : TranslateErrorText.ForCode(row.ErrorCode)`（Tooltip `:82/:156` 可选） |
| R2-P2-1 | P2 | `TranslateEntryUiTests.cs`；`FluentRunProjection.cs:260`；`StudioBatchControls.cs:450` | 执行期接线**零测试**：回退整段映射测试仍全绿；AC8 只覆盖了 VM 层 | `grep ErrorCell/DrawerDetail/ForCode` 结果 | 加 1 例：构造含 `PROVIDER_AUTH_FAILED` 的 `FluentRunRow`（或 `StudioRunStepState`），断言 `ErrorCell` 含「401/403」且未知码含原码 |
| R2-P2-2 | P2 | `TranslateErrorText.cs:30-31, 59` | `INVALID_REQUEST` 与 `INVALID_INPUT` 共用「模型名/额度」句；接进矩阵后误导面扩大（通用校验失败、折叠后的空目标集都会这么提示） | `core_service.py:6696-6703, 6821-6822`；`pipeline.py:848` | 拆成两句：`INVALID_INPUT` 保留现句，`INVALID_REQUEST` 用通用拒绝句 |
| R2-P2-3 | P2 | `ProviderBindingsSection.cs:86` | 文案里 `**…**` 是 Markdown 语法，`Ui.Text` 是纯 `TextBlock`（`Pages.cs:19-26`），用户会看到字面星号 | 代码逐行 | 去掉 `**` |
| R2-P2-4 | P2 | `ConsoleViewModel.cs:1804-1823` | 另一个 book/chapter 绑定的用户入口仍未标注「仅全局驱动执行」 | 代码逐行 | 同步一句限定提示 |
| R2-P2-5 | P2 | `doc/tasks/TRANS-ENTRY-UI.md:11,19,50-58,91` | 任务卡仍写「AC5 设置页无 scoped 入口，登记未提供」（已被证伪）；`reviewer: null`、AC 未勾、`delivery_head: null` | 文件逐行；`fdda639a1` 未改任务卡 | 收口前更正 AC5 记录、登记 reviewer、勾 AC、填 delivery_head |
| R2-P2-6 | P2 | `verification/TRANS-ENTRY-UI/README.md:59,82-87` | 证据数字仍是 919/930（现为 **921/932**）；§5 称 P1-2「已修」与代码事实不符（详情行未接） | 文件逐行 + 实测 | 同步数字；把 P1-2 写成「step 行已接、详情行未接」 |
| R2-P3-1 | P3 | `HostController.cs:973-980, 2964-2968` | Ready 状态下读页失败仍返回空列表且不改 Snapshot ⇒ 状态门无法区分「真 0 页」与「读失败」 | 代码逐行 | 后续用显式「探测成功」信号（不新增 IHostController 成员亦可：捕获读失败后自行置未知） |
| R2-P3-2 | P3 | `FluentRunProjection.cs:260-266` | 已知码在矩阵里丢了机器码，与 `RunStatusMonitor.StepErrorText`（`:366` `中文（CODE）`）口径不一致 | 两处对比 | 需要反馈码的句子补 `（CODE）` |
| R2-P3-3 | P3 | `TranslateErrorText.cs:49-52`；`StudioBatchControls.cs:450` | `ForCode(null/"")` 仍映射成「未配置」；step 行只判 `null`，空串会显示误导句 | 代码逐行；`RunContracts.cs:584-594` | step 行改判 `IsNullOrWhiteSpace`；`ForCode` 对未知/空码给独立句 |

## 7. 结论：三条 P1 是否已真实关闭？本卡能否收口？

**逐条回答：**

1. **P1-1：已真实关闭**（就「Host 未就绪」这条主根因）。状态门与读页的失败谓词同源，非 Ready ⇒ 必不产出空章句；新测试经**回退实验证明会红**，正向测试互补。残留 `Ready + 读失败` 的 P3 已登记。
2. **P1-2：未完全关闭。** 矩阵 `ErrorCell` ✅、drawer step 行 ✅、未知码保留 ✅、非 provider 错误未被硬套 ✅；但 **drawer 详情行仍是裸码**（r1 指名的那一处），且整条接线**无测试**。这是**一个 1 行改动 + 1 条测试**的差距。
3. **P1-3：已真实关闭**（内容层）。README 承认入口并引 `Pages.cs:1141`；设置页文案含要求句且与 Core 语义逐字相符。残留 2 条 P2（Markdown 星号、Console 未同步）与 1 条任务卡记录问题。

**本卡能否收口：暂不能（`changes_requested`）。** 差口很小，但落点正是 r1 判 P1 的那个用户可见面，且当前**没有任何测试**保护这条接线——按「P0/P1 未解决不可批准」，不给 approved。

**最小返修清单（r3 前）：**

1. `StudioBatchViewModel.cs:617` → `TranslateErrorText.ForCode(row.ErrorCode)`（保留 `?? "无错误码"`）。
2. 补 1 条执行期映射测试（`ErrorCell` 401/403 + 未知码保留原码；能同时覆盖 drawer 更佳）。
3. 顺手：`ProviderBindingsSection.cs:86` 去掉 `**`；`doc/tasks/TRANS-ENTRY-UI.md` 更正 AC5 记录与 reviewer；证据 README §3 数字改 921/932、§5 修正 P1-2 表述。
4. 建议（可 defer，需在任务卡登记 disposition）：R2-P2-2 的 `INVALID_REQUEST` 拆分、R2-P2-4 的 Console 提示、R2-P3-1 的「探测成功」信号。

**复审**：修完在新的 head 上出 r3（本报告只对 `fdda639a1` 有效）。
