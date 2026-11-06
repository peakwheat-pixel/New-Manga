---
task: FEA-12-UI-RESIDUAL-1
title: FEA-12-UI-RESIDUAL-1 独立实现 Review r1（App-only 四项 P3 残余：能力防御边 / preview 刷新 / cleanup retry 提示 / 只读双原因文案）
reviewer: fresh subagent（独立上下文；未参与实现/返修；只读）
session: b135fbb8-d81a-4cf6-aeb4-ce2aa7168deb（DSH fresh subagent）
parent_session: session-c2883c5f-dcf8-400d-b161-9c84f562486a
reviewer_kind: subagent
date: 2026-11-06
repo: G:\CODEX\New Manga
branch: main
reviewed_head: 8e3bd03d6
reviewed_docs: 323001fec/08a02f315/7cbaca739
reviewed_base: 9c6ba2da1
decision: approved
findings: P0=0/P1=0/P2=0/P3=4
---

# FEA-12-UI-RESIDUAL-1 独立实现 Review r1（只读）

> **结论先行：`approved`（P0=0 / P1=0 / P2=0 / P3=4）。**
>
> - 四项冻结实现（I-1…I-4）与 5 个新判别测试逐项符合卡面 In/AC-R1…AC-R5；我未发现行为缺陷、越域改动或虚假证据。
> - 独立复跑全部达到卡面数字：定向 `TrashUiTests` **40/0/0**（两次，含恢复后复跑）；全量 .NET **1532/0/86**（8 项目分列与卡面一致）；`pytest tests -q` **3249 passed / 10 skipped / 0 failed（EXIT=0）**；pins **18/18**；check **PASS(3 warnings)**；API inventory **EXIT=0**。
> - 12 个 Canonical Evidence 文件 sha256 **全部与卡面一致**；`changed-files.txt` 与 `git diff --name-only 9c6ba2da1..323001fec` **完全一致**（16 条）；仓外隔离根 10 文件聚合 sha **`97fdbd1e…` 复算一致**。
> - 我另做 **3 处独立破坏性复跑**（不是抄它们的 9 个）：恢复 `&& !HasCapabilityGap`、删除 I-3 的 `_notify`、删除 I-2 的 `await ReloadAsync()` —— **3/3 断言失败变红（EXIT=1）**，随后 `git checkout` 恢复、`git hash-object` == HEAD blob、`git status` clean，并复跑定向 **40/0/0** 证明无残留。
> - 4 个 **P3** 均为非阻塞观察：通知文案先于刷新完成（F1）、AC-R2「其它失败码不变」只有代码保证没有回归测试（F2）、`EV.md` 证据索引漏列 EV-12 自身（F3）、`ITrashController is null` 防御路径 + Host 只读的新可见组合未测（F4）。**不改变任何 AC 判定。**
> - L-R1「I-1 生产不可达」我做了独立可达性复核（不只复述 scope review）：`HostCommandDispatcher` 只在 `RequiredCapabilities(name).Count > 0` 时调用能力门，`library_delete_book_permanently` 无映射，唯一另一处 gate 调用只针对 `source_scan_sync`；Core 的 delete 路径不产生 `CORE_CAPABILITY_MISSING`。**L-R1 前提成立**，且卡/Handoff/EV 三处都明确「defensive invariant only / 不得写成修复用户可见 bug」。

只读纪律：本 Review 未改生产代码/测试/契约/STATUS/PLAN/LEDGER/证据，未 commit/push；仓内唯一新增为本文件。破坏性复跑产生的改动已逐字节恢复（见 §7）。

---

## 1. 基线核验

| 项 | 任务/卡面给定 | 实测（2026-11-06） | 结论 |
|---|---|---|---|
| 分支 / 工作树 | main / clean | `git rev-parse HEAD=7cbaca739d4681352fd39f4df8db72922af37ef3`；`git status --short` 空 | ✅ |
| 被审实现范围 | base `9c6ba2da1` → 实现+测试 `8e3bd03d6` | `git diff --numstat 9c6ba2da1..8e3bd03d6` = `TrashViewModel.cs +32/−8`、`TrashUiTests.cs +183/−0`（2 files, +215/−8） | ✅ 与卡/Handoff 数字一致 |
| 卡/Handoff/证据 | `323001fec` | `git log -1 -- verification/FEA-12-UI-RESIDUAL-1` = `323001fec`；`git diff --stat 323001fec..HEAD -- verification/FEA-12-UI-RESIDUAL-1` 空（12 文件） | ✅ |
| Lead 文档提交 | `08a02f315` / `7cbaca739` | 只改 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`、本卡卡面；`git diff --stat 8e3bd03d6..HEAD -- apps/ doc/contracts doc/plan src/` 空 | ✅ 非代码审查对象 |
| 实现后代码漂移 | 无 | `git diff --name-only 8e3bd03d6..HEAD -- apps/` 空 | ✅ |
| delivery_head | `8e3bd03d6` | 卡面 `delivery_head: 8e3bd03d6`、Handoff 同值、实现 commit 同值 | ✅ 三处自洽 |
| 定向基线 | before 35 / after 40 | 证据 EV-1 tail = `通过: 35`；我实跑 after = `通过: 40`（两次） | ✅ |
| 全量基线 | before 1527/0/86 → after 1532/0/86 | 我实跑 = **1532 passed / 0 failed / 86 skipped**（8 项目 21+38+253+117+31+185+167+720） | ✅ |
| pytest | 3249/10 | 我隔离复跑 = **3249 passed / 10 skipped / 0 failed，EXIT=0（261.22 s）** | ✅（首次并发尝试见 §6） |
| 治理 | pins 18/18、check PASS(3 warnings)、API inventory PASS | 我实跑：`PIN AUDIT: PASS (all 18)`；`Governance check: PASS (3 warnings)`；API inventory EXIT=0 | ✅ |
| FEA-09 副作用 | 全量后恢复 | 全量后 `M verification/FEA-09/logs/wire-redacted.ndjson` → `git checkout -- verification/FEA-09` EXIT=0 → clean | ✅ |

---

## 2. 逐项实现核对（A. 代码正确性）

### 2.1 I-1 / AC-R1 delete-time capability 防御边

**代码**（`TrashViewModel.cs:786-798`）：删除结果为 `TrashDeleteOutcome.CapabilityMissing` 时，**已删除**对页级 `_capabilityMissing = true` / `_capabilityMessage = "Core 未公布删除能力…"` 的写入；保留 `_deleteOutcomeCode = result.Code ?? TrashErrorCodes.CapabilityMissing`、`DeleteResultTitle="删除被拒绝"`、含 typed code 与「未删除任何内容」的结果文案；新增 `_previewBlockedReason` 使同一预览不可再确认；`RaisePreviewStates()` + `RaiseStates()`。

| 要求 | 实测 | 证据 |
|---|---|---|
| 未设页级 `_capabilityMissing/_capabilityMessage` | 该分支无这两处赋值；`_capabilityMissing` 的赋值点只有构造器 `:102`、空控制器/无 probe 路径 `:419`/`:443`、probe 结果 `:452 = !_readAvailable`，均不在 delete 分支 | `git diff` + grep（赋值点 `:102/:419/:443/:452`） |
| 列表保持 | 该分支不动 `Items`；`ShowList => !IsLoading && !HasError && !_capabilityMissing && !_probeFailed && Items.Count>0`（`:222`） | 测试 `:757-760` 断言 `ShowList=true`、`ShowCapabilityState=false`、`Items.Count==2` |
| typed 结果 | `DeleteOutcomeCode=="CORE_CAPABILITY_MISSING"`、`DeleteResultTitle=="删除被拒绝"`、文案含 `CORE_CAPABILITY_MISSING` / `未删除任何内容` | 测试 `:763-768` |
| `CanConfirmDelete=false` | `CanConfirmDelete` 含 `!IsPreviewBlocked`（`:323-326`），`_previewBlockedReason` 已置 | 测试 `:770` |
| 零成功提示 | 测试 `DoesNotContain`「已彻底删除」「清理重试成功」 | 测试 `:771-773` |
| 零额外帧、零新 probe | 分支不发帧；`TrashProbeGolden==1` | 测试 `:754-755` |
| 能力布尔不变（不推断） | 未改 `_readAvailable/_writeAvailable/_previewAvailable`；测试断言 `CanWrite/CanPreview/HasCapabilityGap` | 测试 `:760-762` |
| defensive-only 明示 | 代码注释 `:787-789`；卡 L-R1（`:105`）；Handoff §1/§5；EV §5 | 三处一致，无「修复用户可见 bug」表述 |

**L-R1 的独立可达性复核（我未只复述 scope review）**：

| 事实 | 位置 | 结论 |
|---|---|---|
| dispatcher 只在 `requiredCapabilities.Count > 0` 时调用能力门 | `HostCommandDispatcher.cs:103-108` | delete 不在该集合 |
| `RequiredCapabilities` 映射只有 preview/list/move/restore/purge | `HostCommandRegistry.cs:94-101` | `library_delete_book_permanently` → 空 |
| 唯一另一处 gate 调用是 `descriptor.Name == "source_scan_sync"` | `HostCommandDispatcher.cs:241-244` | delete 也不会走 source-sync 门 |
| Core 的 delete handler 无 `CORE_CAPABILITY_MISSING`（该码只出现在 referenced import/source sync 路径） | `src/bootstrap/core_service.py:4925/4983/5005` 等 | delete 不产生该码 |
| App 映射：`CORE_CAPABILITY_MISSING → TrashDeleteOutcome.CapabilityMissing` | `HostController.cs:3083` | 分支存在但无生产触发源 |

⇒ **「defensive invariant only / 生产不可达」准确**（前提：正常装配的 App 使用实现了 `ITrashController` 的 HostController/NullHostController，`LibraryViewModel.cs:66-70`）。

### 2.2 I-2 / AC-R2 preview `BOOK_NOT_FOUND` 自动刷新

**代码**（`:648-658`）：`IsPreviewLoading=false` 之后、通用失败分支（`:660`）之前，新增 `!preview.Ok && Code == BOOK_NOT_FOUND`（`StringComparison.Ordinal`）前置分支：`_notify("作品已不存在（BOOK_NOT_FOUND）：已刷新回收站列表", NmStatus.Failed)` → `ResetPreview()`（关面板）→ `RaisePreviewStates()` → `await ReloadAsync()` → `return`。

| 要求 | 实测 | 证据 |
|---|---|---|
| notify + 关面板 + Reload | 三条均在分支内且 `await` 完成 | 测试 `:782-812` |
| 恰 2 个 list 帧（初始+刷新）、0 delete、1 preview、probe 2 | 全部断言通过 | 测试 `:793-797` |
| 幽灵行清除 | 刷新页只含 `book-1`，`Items.Count==1` | 测试 `:798-800` |
| 不自动重试 preview | 只有 1 个 preview 帧；分支 `return` 不再进入预览 | 测试 `:796` |
| 其它失败码不变 | 通用分支（`:660-666`）diff 未触碰，条件为精确 code 相等 | `git diff`（仅新增分支） |
| 提示真的能到达用户 | `_notify` 是注入的 `Action<string,NmStatus>`（ctor `:71-75`），不是 VM `_statusMessage`；后续 `ReloadAsync→ResetTransientState→ResetPreview` 不清它 | `:946-949`、`:921-944` |

> 观察（P3-F1）：通知文案在 `await ReloadAsync()` **之前**发出，措辞却是完成态「已刷新」；若刷新自身失败（L-R3），用户会同时看到「已刷新」与列表错误态。该文案由 scope review §2.2 冻结，且既有 delete-time NotFound 分支（`:771-776`）本来就是同一模式，故不判缺陷。

### 2.3 I-3 / AC-R3 cleanup retry `BOOK_NOT_FOUND`

**代码**（`:846-853`）：NotFound 分支在 `ResetPreview()` 之前补 `_notify("作品已不存在（BOOK_NOT_FOUND）：已刷新回收站列表", Failed)`，随后 `ResetPreview()` + `await ReloadAsync()` + `RaisePreviewStates()`；digest 仍用首次 `_activeDigest`（`:825`），`_cleanupPendingVisible = (Outcome == CleanupPending)`（`:841`）使 NotFound 时 `IsCleanupPending/CanRetryCleanup=false`。

| 要求 | 实测 | 证据 |
|---|---|---|
| 提示在 `ResetPreview()` 后仍到达用户 | 旧实现只有 `_deleteOutcomeText` 会被清空；新 `_notify` 走注入回调，不依赖 VM 字段 | 测试 `:842-846`；`_notify` 传递链见 §2.2 |
| digest 沿用首次逐字节值 | 三次 delete 帧的 `inventory_digest` 全部等于第一次 | 测试 `:833-841`（`Assert.Equal(firstDigest, …)` ×2） |
| 状态复位 | `IsCleanupPending=false`、`CanRetryCleanup=false`、`IsPreviewOpen=false` | 测试 `:847-849` |
| 列表刷新 | 2 个 list 帧（初始+刷新） | 测试 `:845` |
| 不伪报成功 / 不自动重试 / 不重跑 preview | 只 1 个 preview 帧；`DoesNotContain`「清理重试成功」「已彻底删除」 | 测试 `:846`、`:850-852` |
| 3 个 delete 帧 | 断言的是 3 条含 `inventory_digest` 的 payload（等价于 3 帧 delete，其它帧无该键） | 测试 `:833-836` |

> 说明：`:842-845` 仍会先写 `_deleteOutcomeCode/_deleteOutcomeText` 再被 `ResetPreview()` 清空（对 NotFound 是死赋值），但非 NotFound 分支需要这两行；`:848-849` 注释已如实说明，不构成缺陷。

### 2.4 I-4 / AC-R4 只读 / 能力缺口双原因文案

**代码**：`ShowHostReadOnlyBanner => _hostReadOnly`（`:193`，去掉 `&& !HasCapabilityGap`）；`HostReadOnlyBannerText` = 「Host 处于只读模式（HOST_READ_ONLY）：不会执行任何写入；软删/恢复/彻底删除已禁用。」（`:199-200`，删去「回收站可浏览」）。

| 要求 | 实测 | 证据 |
|---|---|---|
| 仅由 `_hostReadOnly` 决定 | 表达式只剩 `_hostReadOnly`；`_hostReadOnly` 仅由 `_writesAllowed()` 在 `ProbeAndLoadAsync`（`:411`）与构造器（`:104`）赋值 | 代码 + `RaiseStates` 已含该属性（`:967`） |
| 组合态双 banner | write 缺口 + Host 只读：`ShowHostReadOnlyBanner=true` 且 `ShowCapabilityDegraded=true`，`HOST_READ_ONLY` 与 `CORE_CAPABILITY_MISSING` 分别出现、互不冒充 | 测试 `:859-888` |
| read 缺失 + Host 只读 | `ShowCapabilityState=true`、只读 banner 仍可见、文案不含「可浏览」、能力文案不含 `HOST_READ_ONLY` | 测试 `:890-911` |
| 单一原因仍单 banner | 既有用例保持：仅 Host 只读 → banner=true / degraded=false（`:176-180`）；仅能力缺失 → banner=false（`:529-531,550-554,576-579,599-600`），40/0 全绿 | 定向复跑 |
| 未改 XAML | `git diff 9c6ba2da1..8e3bd03d6` 只 2 个 App 文件；XAML 绑定仍是 `ShowHostReadOnlyBanner` / `ShowCapabilityDegraded`（`RecycleBinView.axaml:66-67,80`） | 无需改，绑定天然兼容 |

### 2.5 边界（AC-R5 写域）

| 检查 | 命令 | 结果 |
|---|---|---|
| 实现提交写域 | `git diff --name-only 9c6ba2da1..8e3bd03d6` | 仅 `TrashViewModel.cs` + `TrashUiTests.cs`（⊆ allowed_paths） |
| 含证据/卡/Handoff | `git diff --name-only 9c6ba2da1..323001fec` | 16 条，全部在 allowed_paths；与 `changed-files.txt` 完全一致 |
| 禁止面 | `git diff --stat 8e3bd03d6..HEAD -- apps/ doc/contracts doc/plan src/`；`git diff --stat 9c6ba2da1..HEAD -- doc/tasks/FEA-12-UI.md` | 均空 |
| 依赖 | 变更文件仅上述 2 个；无 `.csproj/props/targets/pyproject/lock` diff | ✅ |
| Host/CoreClient/DesignSystem/XAML/Fake/LibraryViewModel/端口/契约 | `git diff --name-only 9c6ba2da1..323001fec` 中均不出现 | ✅ |

---

## 3. 测试真实性与判别性（B）

### 3.1 5 个新测试的真实性

| 测试 | 行 | VM 层 / fake | 无窗口 / 无 sleep | 关键断言（会在实现变坏时红） |
|---|---|---|---|---|
| `Delete_CapabilityMissing_DoesNotTurnThePageIntoReadCapabilityMissing` | `:741` | `NewTrash()` → 真 `TrashViewModel` + `FakeHostController`（唯一构造点 `:26`） | 是（新测试区间无 `Avalonia/Dispatcher/Delay/Sleep`，grep 为空） | 帧数、probe 次数、`Items`、`ShowList/ShowCapabilityState`、typed 结果、`CanConfirmDelete`、无成功提示 |
| `Preview_BookNotFound_ClosesPanel_AndReloadsTheList` | `:782` | 同上（`ScriptedTrashPages/Previews`） | 是 | 2 list / 0 delete / 1 preview / probe 2、幽灵行、面板关闭、notice |
| `CleanupRetry_SecondRetryBookNotFound_NotifiesAndRefreshes_WithSameDigest` | `:814` | 同上（`ScriptedTrashDeletes` ×3） | 是 | 3 条逐书 digest 逐字节相等、1 preview、2 list、notice、状态复位、无成功提示 |
| `HostReadOnly_PlusWriteCapabilityGap_ShowsBothIndependentCauses` | `:859` | 同上（`TrashCapabilities` + `Snapshot with { WritesAllowed=false }`，均在 `EnterAsync` 前设置） | 是 | 双 banner、两 code 不互相冒充、列表真实 |
| `HostReadOnly_PlusReadCapabilityMissing_ShowsCapabilityStateAndReadOnlyReason` | `:890` | 同上 | 是 | 能力态 + 只读原因、不含「可浏览」、`ShowList/ShowEmptyState=false` |

- 新测试通过 `ConfirmDeleteCommand.Execute(null)` / `RetryCleanupCommand.Execute(null)` 触发（`RelayCommand` fire-and-forget），之所以确定性，是 fake 返回已完成的 `Task`，await 同步续行；这是既有测试的同一模式，不引入 sleep/时钟。
- 断言对象是 VM 可观察状态与 fake 记录的帧/payload，不依赖 Avalonia 渲染。

### 3.2 入库变异日志复核（`logs/scope-mutations.log`）

- 结构完整：M1…M9 每条都标注 `(AC-Rx / I-x)`，**M 编号与 AC 映射明确**；末尾汇总 `M1…M9 EXIT=1 RED as expected`（`:584-592`），并记录 `bytes restored from pristine backup: MATCH (sha256=E0F0DD26…)`（`:581`）。
- **确为断言失败而非编译错误**：全日志 `error CS|error MSB` 匹配 0 条；每条均出现 xUnit `[FAIL]` + 具体断言（`Assert.True/Equal/Contains/DoesNotContain`）+「失败! … 失败: 1」+`EXIT=1`。
- 我抽查了失败点与 AC 的对应：M1 `Assert.True(ShowList)`；M2 `Assert.Equal 2 vs 1`（list 帧）；M3/M5 `Assert.Contains`（notice）；M4 `Assert.Equal 2`（未刷新）；M6 `Assert.Equal`（digest 不同）；M7 `Assert.Equal 2`（list 帧）；M8 `Assert.True(ShowHostReadOnlyBanner)`；M9 `Assert.DoesNotContain("可浏览")`。
- 证据中的 pristine sha `E0F0DD26…` 与交付 blob（`git cat-file` LF 43033 bytes）sha256 一致 —— 说明它们恢复的是逐字节交付内容，不是「看起来没坏」。

### 3.3 我自己的破坏性复跑（独立于 M1…M9）

| # | 破坏 | 目标用例 | 实测 | 恢复 |
|---|---|---|---|---|
| A | `ShowHostReadOnlyBanner => _hostReadOnly` 改回 `&& !HasCapabilityGap` | `HostReadOnly_PlusWriteCapabilityGap_ShowsBothIndependentCauses` | **1 failed / 0 passed，`Assert.True() Failure`，EXIT=1** | `git checkout` → status clean |
| B | 删除 I-3 的 `_notify(...)`（保留 Reset/Reload） | `CleanupRetry_SecondRetryBookNotFound_NotifiesAndRefreshes_WithSameDigest` | **1 failed，`Assert.Contains() Failure: Filter not matched in collection`，EXIT=1** | 同上 |
| C | 删除 I-2 的 `await ReloadAsync().ConfigureAwait(true)` | `Preview_BookNotFound_ClosesPanel_AndReloadsTheList` | **1 failed，`Assert.Equal() Failure: Expected 2 / Actual 1`，EXIT=1** | 同上 |

恢复证明（见 §7）：三次 `dotnet test` 变红后 `git checkout -- <file>`，`git status --short` 空、`git hash-object` == `git rev-parse HEAD:<path>` == `df5203df…`，并复跑定向 **40/0/0**。

---

## 4. AC 与 limitation 精度（C）

### 4.1 AC-R1…AC-R5

| AC | 卡面判定（Owner） | 我的独立判定 | 依据 |
|---|---|---|---|
| AC-R1 | `<<MET>>`（defensive only） | **MET**（defensive invariant only） | §2.1 + 测试 `:741-780` + M1/我的 A |
| AC-R2 | `<<MET>>` | **MET** | §2.2 + 测试 `:782-812` + M2/M3/M4/我的 C |
| AC-R3 | `<<MET>>` | **MET** | §2.3 + 测试 `:814-857` + M5/M6/M7/我的 B |
| AC-R4 | `<<MET>>` | **MET** | §2.4 + 测试 `:859-911` + M8/M9/我的 A |
| AC-R5 | `<<MET>>` | **MET** | §2.5 + §5/§6 门禁 + 证据 sha |

### 4.2 limitation

| limitation | 卡面/Handoff/EV 是否如实 | 核对 |
|---|---|---|
| **L-R1** ① 生产不可达、只钉防御不变量、不得写成修复用户可见 bug | 三处均有；无夸大表述 | 可达性我独立复核成立（§2.1） |
| **L-R2** `CORE_CAPABILITY_MISSING` 不在 `AllowedDeleteTrashErrorCodes`（Host/Core 旧债） | 三处均登记，明确本卡不修 | `git diff` 未触碰 Host/CoreClient |
| **L-R3** ② 刷新失败只显示列表错误态、不自动重试 | 三处均登记 | 代码 `:656` 只 `await` 一次；无循环 |
| **L-R4** ③ 面板关闭、提示只经 notify | 三处均登记 | `ResetPreview()` 在 notify 之后；L-R4 描述准确 |
| **L-R5** ④ 组合态视觉冗余 | 三处均登记 | 两个 `AlertBanner` 同时可见（XAML `:66,80`） |
| **L-R6** 证据层级：VM 级 fake，无新增真实 IPC/无 L2 | 三处均登记 | 5 个测试全 fake；无 Host.Tests 变更 |
| **L-R7** 只读文案移除「可浏览」、read 可用时信息量略减 | 三处均登记 | 文案 `:199-200`；测试断言不含「可浏览」 |
| **L3/L4** `NOT_RUN` | 卡 `:112`、Handoff `:45`、EV `:94` 三处一致，未声称通过 | ✅ |
| FEA-12-UI 历史 AC 未回填 | 卡 `:144`、EV `:95`；`git diff 9c6ba2da1..HEAD -- doc/tasks/FEA-12-UI.md` 为空 | ✅ |

### 4.3 其它未登记 limitation / 观察

1. **relaod 失败时通知文案仍称「已刷新」**（P3-F1）：L-R3 只登记了「只显示列表错误态」，没提通知与错误态并存的矛盾；建议在 L-R3 里补一句，或把文案改成「正在刷新」。
2. **AC-R2「其它失败码不变」无回归测试**（P3-F2）：`TrashUiTests` 中 `TrashPreviewResult.Failure(...)` 只有新测试这一处（`:789`）；`OldCorePreview/BusyPreview` 都是 `Ok=true`。行为不变目前只由「新增分支用精确 code 相等且通用分支 diff 未改」保证。
3. **auto-refresh 会重置分页**：`ReloadAsync()` 置 `_nextCursor=null`（`:396-406`），若用户已 `LoadMore` 多页后触发 preview `BOOK_NOT_FOUND`，刷新回到第一页。这是既有刷新语义（既有 delete-time NotFound `:775` 同样如此），非本卡引入，但可考虑在 L-R3 一并说明。
4. **`ITrashController is null` + Host 只读的新可见组合未测**（P3-F4）：构造器会置 `_capabilityMissing=true` 与 `_hostReadOnly=!_writesAllowed()`；旧公式因 `HasCapabilityGap` 抑制 banner，新公式会显示。生产 `LibraryViewModel.cs:66-70` 的 `controller as ITrashController` 在现行两种 Host 下均非空，属防御路径，影响极低。
5. 定时/并发：本卡未引入定时器；`_generation` 在 `ReloadAsync`/`EnterAsync` 递增，preview 与 delete 都有 generation 早退保护，未发现新的竞态。
6. fake 覆盖不到的真实 Host 行为：已由 L-R6 覆盖（无真实 IPC / 无 cleanup-retry NotFound 的 L2 证据）。

---

## 5. 门禁实测（独立复跑）

| Gate | 卡面预期 | 我的实测 | 结果 |
|---|---|---|---|
| 定向 `dotnet test apps/desktop-avalonia/NewManga.sln -c Release --filter FullyQualifiedName~TrashUiTests` | 40/0/0 | **40 passed / 0 failed / 0 skipped**（79 ms）；恢复后再跑 **40/0/0**（78 ms） | ✅ |
| 全量 `dotnet test … -c Release` | 1532/0/86（before 1527/0/86） | **1532 passed / 0 failed / 86 skipped**；8 项目 21+38+253+117+31+185(skip 55)+167(skip 24)+720(skip 7) | ✅ 与卡面分列完全一致 |
| `pytest tests -q` | 3249/10 | **3249 passed / 10 skipped / 10 warnings，EXIT=0（261.22 s）**（隔离复跑） | ✅ |
| `verify_pins.ps1` | 18/18 PASS | `PIN AUDIT: PASS (all 18)`，EXIT=0 | ✅ |
| `check.ps1` | PASS(3 warnings) | `Governance check: PASS (3 warnings)`（9 非终态 Task / STATUS 80% / PLAN 80%），EXIT=0 | ✅ |
| `generate_api_inventory.py --check` | PASS | EXIT=0（`IHostController=54` / `IRunController=6` / `IReaderProgressSink=1`） | ✅ |
| scope diff | ⊆ allowed_paths | 见 §2.5 | ✅ |
| L3/L4 | NOT_RUN | 未运行；本 Review 不声称通过 | ✅ |

**pytest 过程如实记录**：第一次我把 pytest 与全量 .NET 并行跑，日志在 84% 处中断（无 summary 行、单个 `F` 出现在 48%），`$LASTEXITCODE=1`；随后我**隔离单跑**（无其它 dotnet 进程）得到 3249/10/0、EXIT=0，与卡面 EV-5（3249/10，278.59 s）一致，`git status` 仍 clean。并行那次未留下可归因的失败摘要，我**不**把它算作本卡缺陷，也不作为门禁证据。

> 备注：`check.ps1` 本次输出 STATUS 3027 bytes，而 EV-6 记录为 3051 bytes —— 差异来自 Lead 其后对 `doc/STATUS.md` 的文档提交（`08a02f315`），非本卡代码；warning 数与结论不变。

---

## 6. 证据 sha256 复核

| 证据 | 文件 | 卡面 sha256 | 我复算 | 结论 |
|---|---|---|---|---|
| EV-1 | `logs/gates-targeted-before.log` | `ea544fed…2d31e` | `ea544fedda4828a02a5652b33ac7ce69ce741c0282eaf86c2ff1b1ab6672d31e` | ✅ |
| EV-2 | `logs/gates-targeted-after.log` | `3128e92f…626f0` | `3128e92f44ffea5f4dd1b7d074d95d37d2e22195369a4755739fea95165626f0` | ✅ |
| EV-3 | `logs/gates-dotnet-before.log` | `baab20fd…40a88` | `baab20fdfc22b9c9ffc479496e5e487dcb9ae624bd36b12de7363f31fe040a88` | ✅ |
| EV-4 | `logs/gates-dotnet-after.log` | `3fbf0840…80c20` | `3fbf0840f9d4d5f07d053a132a846e9b701938298abb8d8d92f112b1f5180c20` | ✅ |
| EV-5 | `logs/gates-pytest.log` | `69beb5ca…704d` | `69beb5ca4c805327d2fc47e3290a88eaf700a824b384bb0e1b114af19753704d` | ✅ |
| EV-6 | `logs/gates-governance.log` | `2b832619…12d76` | `2b83261984c08eaf48a8380c122217143fb379d0c0701d6e1db28e4fbb512d76` | ✅ |
| EV-7 | `logs/scope-validation.log` | `a21eede2…b2894` | `a21eede24ea5f701b3ed56f9fe37eb3b941f6973bb2dcc5c3c3a4566319b2894` | ✅ |
| EV-8 | `logs/scope-mutations.log` | `f95d4152…892de` | `f95d41527212d65005c12a2df3f7c0129ad24455dc4ecee5e1529f11762892de` | ✅ |
| EV-9 | `logs/gates.log` | `d0ad1457…f353` | `d0ad14579d3904b363adbbbd74fc3e416ac488b8bdb519faed142e6b1c79f353` | ✅ |
| EV-10 | `RESOURCE-MANIFEST.json` | `1c78ec61…0ed7` | `1c78ec610f5bec011a7850d3bd0697e43f9d482360b72c3dcc9e90247dc80ed7` | ✅ |
| EV-11 | `changed-files.txt` | `1e0ba244…f4b50` | `1e0ba244e5bec73c900b45c221a7c3aeeb4da1d74b1879024835d473096f4b50` | ✅ |
| EV-12 | `EV.md` | `ec71f55a…7109e` | `ec71f55a11eacd679d873b625ae98d0b28d4fb60e01ee799cadc67049cf7109e` | ✅ |

- **commit 核对**：12 个文件的最后提交均为 `323001fec`（`git log -1 -- verification/FEA-12-UI-RESIDUAL-1`），且 `git diff 323001fec..HEAD -- verification/FEA-12-UI-RESIDUAL-1` 为空；卡面表中 commit 全为 `323001fec`，✅。
- **`changed-files.txt`**：内容（去掉注释行）16 条 == `git diff --name-only 9c6ba2da1..323001fec`，顺序也一致，无差异 ✅。
- **RESOURCE-MANIFEST**：仓外隔离根 `G:\CODEX\New Manga.workspace\FEA-12-UI-RESIDUAL-1\` 现有 **10 文件**；按 manifest 声明的聚合口径（按路径排序的 `relative/path|sha256` 行以 `\n` 连接、UTF-8）复算 = **`97fdbd1e5bb0fc8d15eb44f42cd88580e76eb43b25b0fa086222abb792d28428`**，与卡面/EV 一致 ✅；逐文件 sha 亦全部一致（含 `temp/TrashViewModel.pristine.cs = e0f0dd26…`，与交付 blob 相同）。我未向该隔离根写入任何文件（Review 复跑日志另放 `…\New Manga.workspace\r1-review\`，避免破坏其 10 文件聚合）。

---

## 7. 破坏性复跑与恢复证明

| 阶段 | 命令/操作 | 关键输出 |
|---|---|---|
| 起点 | `git rev-parse HEAD` / `git status --short` | `7cbaca739…` / 空 |
| 基线 sha | VM 文件 sha256 | `e0f0dd262ae0526aed6f42327a43988d9541503fe585d06086c6d4f3426f9269`（== `git cat-file` blob） |
| 变异 A | 文本替换 → 定向 A | `Assert.True() Failure`，失败 1，EXIT=1 |
| 变异 B | 文本替换 → 定向 B | `Assert.Contains() Failure`，失败 1，EXIT=1 |
| 变异 C | 文本替换 → 定向 C | `Assert.Equal() Failure: Expected 2 / Actual 1`，失败 1，EXIT=1 |
| 恢复 | `git checkout -- apps/desktop-avalonia/src/…/TrashViewModel.cs` | `git status --short` 空；`git hash-object` = `git rev-parse HEAD:<path>` = `df5203dff06442eb0113dcb076841e5b7cdc927d` |
| 复核 | 恢复后再跑定向 `TrashUiTests` | **40 passed / 0 failed / 0 skipped** |
| FEA-09 | 全量 .NET 后 `git checkout -- verification/FEA-09` | 恢复后 status 空 |

> 字节口径说明（如实记录）：仓库 `core.autocrlf=true`，且 `apps/**/*.cs` 无 `eol=lf` 规则。我最初以「交付时工作树字节」为基准（LF，sha256 `e0f0dd26…`）；变异后 `git checkout` 会按 autocrlf 写出 CRLF（44108 bytes，sha256 `9acf9841…`），但 git 内容完全一致（`git hash-object` == HEAD blob `df5203df…`、`git diff --quiet` EXIT=0）。为让 `git status` 干净（autocrlf 下 LF 工作树会显示 stat-only ` M`），最终以 `git checkout` 的规范 CRLF 状态收尾，并用 `git hash-object` == HEAD blob 证明内容零差异；`TrashUiTests.cs` 全程未被触碰。**未产生任何 staged/committed 内容。**

最终状态：HEAD `7cbaca739`，`git status --short` 仅 `?? doc/reviews/FEA-12-UI-RESIDUAL-1-r1.md`（本报告；写入前为空），FEA-09 clean，无 push。

---

## 8. Findings

| ID | 级别 | 文件:行 | 问题 | 证据 | 建议 |
|---|---|---|---|---|---|
| **F1** | P3 | `TrashViewModel.cs:653-656`、`:850-852` | 「已刷新回收站列表」在 `await ReloadAsync()` **之前**发出完成态通知；若刷新失败（L-R3），通知与列表错误态矛盾 | 代码顺序；L-R3 卡面 `:107`；既有 delete-NotFound `:771-776` 同模式 | 文案改「正在刷新回收站列表」，或 Reload 成功后再通知；若维持现状，请在 L-R3 明示「刷新失败时通知仍称已刷新」 |
| **F2** | P3 | `TrashUiTests.cs`（新测试区间）与 AC-R2 | AC-R2 末条「其它 preview 失败码行为不变」没有回归测试；唯一 `TrashPreviewResult.Failure` 用例是本卡的 BOOK_NOT_FOUND | `ScriptedTrashPreviews` 仅 3 处：`:212`(Ok)、`:230`(Ok)、`:789`(本卡)；通用分支 `:660-666` diff 未改 | 加一个小用例（如 `CORE_UNAVAILABLE` → `HasPreviewError=true`、0 刷新、无 notify），或把 EV/Handoff 措辞降为「结构未变、未单独测试」 |
| **F3** | P3 | `verification/FEA-12-UI-RESIDUAL-1/EV.md:61-73` | EV.md 自身 §3 证据索引只有 EV-1…EV-11，缺卡面定义的 EV-12（= EV.md 自己）；卡面表是完整的 | 卡面 `:150-163` vs EV.md `:61-73` | 在 EV.md 索引补 EV-12 自引用行（或 closeout 说明其自指） |
| **F4** | P3 | `TrashViewModel.cs:99-105` + `:193` | `ITrashController is null` 的构造器路径 + Host 只读：旧公式因 `HasCapabilityGap` 抑制 banner，新公式会在能力缺失态旁同时显示只读 banner；该组合无测试（测试只用一个 fake 构造点 `:26`） | 构造器 `:99-105`；`LibraryViewModel.cs:66-70` 生产两实现均非空；既有能力测试均带 controller | 视为防御路径接受的观察；若要钉住，加一个 `new TrashViewModel(null, () => false, …)` 的 VM 级用例 |

**无 P0/P1/P2**：未发现行为错误、安全/数据风险、越域改动、虚假证据或门禁不达标。

---

## 9. Reviewer 过程与声明

- 只读范围：`TrashViewModel.cs`、`TrashUiTests.cs`、`FakeHostController.cs`、`HostController.cs`、`HostCommandDispatcher.cs`、`HostCommandRegistry.cs`、`core_service.py`、`core_assembly.py`、`RecycleBinView.axaml`、卡/scope review/Handoff/EV/logs；`FakeHostController.cs` 与端口/契约文件确认零 diff。
- 未参与 FEA-12-UI-RESIDUAL-1 的实现或返修；未获取实现会话上下文，结论仅基于被审 head 的代码/测试/证据与本次独立实跑。
- 仓内未 commit/push，未改生产代码/测试/契约/STATUS/PLAN/LEDGER/证据；仓外复跑日志在 `G:\CODEX\New Manga.workspace\r1-review\`（评审自用成品，不属于本卡证据；未写入本卡隔离根以免破坏其 10 文件聚合 sha）。
- 建议 Lead 处置：F1–F4 均为 P3，可在 closeout 记录或并入后续小修，不阻塞集成；`canonical_evidence_status`/`resource_closeout_status` 与 AC 终判由 DSH 按本报告 + 集成验证落定。

UI-RESIDUAL-1-REVIEW: approved — P0/P1/P2 均为 0，AC-R1…AC-R5 独立判定全 MET；四项实现与 5 个判别测试符合冻结语义，定向 40/0/0、全量 1532/0/86、pytest 3249/10、pins 18/18、check PASS(3 warnings)、API inventory PASS，12 证据 sha/commit、changed-files、隔离根聚合 sha 全部复核一致；3 处独立破坏性复跑全红并逐字节恢复；4 个 P3（通知时序 F1、AC-R2 末条无回归测试 F2、EV.md 索引缺 EV-12 F3、null 控制器+只读未测 F4）为非阻塞观察，L-R1 生产不可达前提经独立可达性复核成立，L3/L4 仍 NOT_RUN。
