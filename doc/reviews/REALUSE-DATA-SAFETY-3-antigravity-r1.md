---
task: REALUSE-DATA-SAFETY-3
round: 1
reviewer: antigravity-headless
reviewer_participated_in_implementation: false
verdict: FAIL_WITH_MUST_FIX
reviewed_head: 46ebc31df
reviewed_base: 8b1ca6723
captured_by: dsh-lead
capture_note: >
  Antigravity 原始回答逐字保存（agy headless --output-format json 的 response 字段）。
  正文未做任何编辑；审查者自行运行了测试并复现了一处测试失败。
---

# REALUSE-DATA-SAFETY-3 独立审查（Round 1，Antigravity）

# 独立审查报告：REALUSE-DATA-SAFETY-3（AC2 / AC3 / AC4）

- **审查对象工作区**：`G:\CODEX\New Manga.workspace\worktrees\REALUSE-DATA-SAFETY-3`
- **审查分支**：`task/REALUSE-DATA-SAFETY-3`（HEAD `46ebc31df`，基线 `main 8b1ca6723`）
- **审查范围**：`git diff 8b1ca6723..46ebc31df`
- **任务卡**：`doc/tasks/REALUSE-DATA-SAFETY-3.md`
- **审查结论**：**FAIL_WITH_MUST_FIX**

---

## 重点审查问题答复

### 1. AC3 是否牺牲数据新鲜度

**结论：存在确凿的数据新鲜度牺牲、失效点缺失及严重的数据静默错位风险。**

依据代码与架构调用链路：
1. **`LoadReaderBookAsync` 存在严重的“静默打开错误书籍”风险**：
   - **依据**：[`HostController.cs:329-342`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3/apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs#L329-L342)
   - **机制**：
     ```csharp
     var books = _snapshot.Books;
     if (books.Count == 0)
     {
         books = await runtime.ListBooksAsync(cancellationToken).ConfigureAwait(false);
     }
     BookSummary? book = null;
     if (!string.IsNullOrWhiteSpace(bookId))
     {
         book = books.FirstOrDefault(candidate => string.Equals(candidate.BookId, bookId, StringComparison.Ordinal));
     }
     book ??= books.FirstOrDefault(candidate => (candidate.PageCount ?? 0) > 0) ?? books.FirstOrDefault();
     ```
   - **风险**：若启动后有新书通过外部导入、恢复备份或外部进程写入，当前会话的 `_snapshot.Books` 并不为空但**不包含该 `bookId`**。此时 `book` 为 `null`，紧接着在第 341 行被 `book ??= ...` **静默 fallback 成第一本书**！阅读器会静默打开完全不相干的作品，造成极其隐蔽的数据错位。
2. **备份恢复（`RestoreBackupAsync`）后完全未失效缓存**：
   - **依据**：[`HostController.cs:1642-1669`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3/apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs#L1642-L1669)
   - **机制**：用户在控制台或恢复面板执行 `RestoreBackupAsync` 后，Core 底层 SQLite 数据库被整库回滚替换。但 `HostController` 既没有清空 `_chapterCache`，也没有调用 `RefreshBooksAsync()`。恢复后，用户在整个会话内看到的依然是恢复前的旧书架与旧章节列表。
3. **用户主动刷新无法刷新章节列表（章节缓存无失效出口）**：
   - **依据**：[`LibraryViewModel.cs:553-568`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/LibraryViewModel.cs#L553-L568) 与 [`HostController.cs:18, 454`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3/apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs#L18)
   - **机制**：用户在 Library 界面点击“刷新”按钮（`RefreshAsync`）只会调用 `_controller.RefreshBooksAsync()`；而 `HostController` 的 `_chapterCache` 是内部私有的 `Dictionary`，没有对 `RefreshBooksAsync` 联动清空，也未暴露任何使章节缓存失效的接口。只要不新建章节，该会话内即使用户主动刷新，章节列表也永久命中缓存。
4. **并发安全性缺陷（Concurrency Hazard）**：
   - **依据**：[`HostController.cs:18`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3/apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs#L18)
   - **机制**：`_chapterCache` 使用裸 `Dictionary<string, IReadOnlyList<ChapterSummary>>`，没有任何锁保护。在异步并发调用 `ListChaptersAsync` 与 `CreateChapterAsync` 时存在并发读写，会导致数据损坏或抛出 `InvalidOperationException`。

---

### 2. 测试改动的合理性与当前测试构建失败

**结论：测试改动在设计思路上符合新契约，但实施中引入了致命笔误，导致自动化测试直接失败（已在本地完整复现）。**

1. **测试直接失败（Blocking Issue）**：
   - **依据**：[`apps/desktop-avalonia/tests/NewManga.App.Tests/V2ShellUiTests.cs:718, 722, 746-749`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3/apps/desktop-avalonia/tests/NewManga.App.Tests/V2ShellUiTests.cs#L718-L749)
   - **运行结果**：
     ```text
     [FAIL] NewManga.App.Tests.V2ShellUiTests.LoadingState_RendersSameGeometrySkeleton_WithoutSelfJustifyingCopy
     Assert.False() Failure: Expected False, Actual True (at line 749)
     ```
   - **原因剖析**：
     在第 718 行已执行了 `await shell.Initialization;`（首屏复用快照已结束）；第 722 行通过 `_ = shell.ViewModel.Library.RefreshAsync();` 发起测试专用的刷新并触发 `SnapshotGate`；在第 746 行 `gate.SetResult(true)` 后，第 747 行却错误地写成了 `await shell.Initialization;`（这是个早已处于 `RanToCompletion` 状态的 Task！），根本没有等待第 722 行的 refresh 任务结束，导致第 749 行断言 `Assert.False(shell.ViewModel.Library.IsLoading)` 时直接因竞态失败。
2. **在新契约下的测试断言合理性**：
   - 在新契约下，“冷启动/就绪启动时不发起额外网络读”，因此在正常启动场景下，界面确实**不应**出现 Loading 骨架屏，而是秒开。
   - 要测试“加载中渲染骨架屏”这一 UI 几何行为，测试用例显式调用 `RefreshAsync` 是合理的，但必须正确持有该异步 Task 并执行 `await refreshTask;`。
   - 对于 `Int2_LibraryCenterState_HasExactlyOneVisibleBlock_ForEveryCombination` 的 (d) 项（Ready + error），真实 Host 启动若读书架失败，`_snapshot.State` 会置为 `Failed`，首屏初始化依然能呈现错误；但测试用例中的 `FakeHostController.StartAsync` 并没有模拟这一行为，因此需要显式 `RefreshAsync` 才能把 `failing.RefreshException` 抛出。这反映了测试替身 `FakeHostController` 与真实 `HostController` 在启动期行为上的差异，但作为 UI 错误态的单独覆盖是可以接受的。

---

### 3. AC2 的 KnownRunIds 是否误导

**结论：UI 提示文案诚实，但输入交互存在严重的无效 Run 污染和后台无限轮询缺陷。**

1. **文案说明本身合格**：
   - **依据**：[`ConsoleViewModel.cs:241-244`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Console/ConsoleViewModel.cs#L241-L244)
   - 界面明确标明：“本会话出现过的 Run（点击读取）；冻结契约没有「列出 Run」命令，跨会话的 Run 仍需输入 run_id。”没有向用户暗示这是服务端全量列表，符合诚实性要求。
2. **交互缺陷（严重问题）**：
   - **依据**：[`ConsoleViewModel.cs:652`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Console/ConsoleViewModel.cs#L652) 与 [`RunStatusMonitor.cs:100-137`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3/apps/desktop-avalonia/src/NewManga.App/Shell/V2/RunStatusMonitor.cs#L100-L137)
   - **机制**：
     当用户在文本框手动输入一个不存在的、甚至拼写错误的 `run_id` 并点击“读取 Run”时，代码在尚未确认该 Run 是否有效之前，直接调用了 `_runMonitor.Track(runId)`。
     - 该拼写错误的垃圾字符串立即被永久记录进 `_knownRunIds`，并作为 Chip 按钮展示在第一位；
     - `RunStatusMonitor` 将 `_runId` 设为此无效 ID 并**启动了 1 秒间隔的 `DispatcherTimer`**；
     - 随后每次轮询均因目标不存在而失败，底部状态栏持续显示 `Run · 状态未知 · <bad_id>`，应用陷入持续的无效网络请求轮询中。

---

### 4. AC4 映射是否覆盖 Core 真值

**结论：存在关键终态漏映射、出现幽灵错误码、并遗漏了 Core 实际高频抛出的重要错误码。**

核对 `src/domain/tasks/models.py`、`src/ports/providers/errors.py` 与 `src/application/tasks/service.py`：

1. **终态状态映射漏掉 `cancelled`（`NmStatus` 出现严重偏差）**：
   - **依据**：[`RunStatusMonitor.cs:285-295`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3/apps/desktop-avalonia/src/NewManga.App/Shell/V2/RunStatusMonitor.cs#L285-L295)
   - Core 枚举：`PipelineRunStatus.CANCELLED = "cancelled"`（[`src/domain/tasks/models.py:98`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3/src/domain/tasks/models.py#L98)）。
   - 现状：`RunStateText` 正确映射为“已取消”，但 `RunStateStatus` 中漏掉了 `"cancelled" or "canceled" or "stopped"`，导致取消的 Run 状态落入 `_ => NmStatus.NotStarted`！图标与颜色直接变成了“未开始”（灰色空心圆 ○），导致状态语义完全颠倒。
2. **存在虚构代码（Ghost Code）**：
   - **依据**：[`RunStatusMonitor.cs:329`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3/apps/desktop-avalonia/src/NewManga.App/Shell/V2/RunStatusMonitor.cs#L329) 中的 `"PROVIDER_UNKNOWN"`。
   - 经全面检索 Core 源码，没有任何地方定义或抛出 `PROVIDER_UNKNOWN`，Core 对应的是 `PROVIDER_NOT_IMPLEMENTED`（[`src/ports/providers/errors.py:95`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3/src/ports/providers/errors.py#L95)）。
3. **遗漏 Core 真实高频步骤错误码**：
   - 核对 [`src/ports/providers/errors.py`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3/src/ports/providers/errors.py) 与 [`src/application/tasks/service.py`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3/src/application/tasks/service.py)，以下在实际管线中高频发生的错误码完全未在 `StepErrorText` 中本地化：
     - `PROVIDER_AUTH_FAILED`（API Key 错误 / 401 / 403 认证拒绝）：用户配错 Provider 的第一高发错误；
     - `PROVIDER_TIMEOUT`（模型响应超时 / 连接超时）；
     - `PROVIDER_UNAVAILABLE`（本地模型服务未开启或端口不可达）；
     - `PROVIDER_DEPENDENCY_MISSING`（缺少依赖库或模型权重未下载）；
     - `STEP_FAILED`（步骤执行时底层未捕获异常的默认兜底错误码，`service.py:930`）；
     - `INPUT_REVISION_CHANGED` / `LOCK_CHANGED`（并发修改 / 锁状态冲突，`service.py:765`）；
     - `RESOURCE_LIMIT_EXCEEDED`（超额资源熔断，`service.py:909`）。

---

### 5. 是否引入回归或新的可维护性问题

**结论：是，引入了 1 处测试回归、1 处线程安全隐患、以及 1 处死循环空转风险。**（详见下表）

---

## 必须修复清单（MUST-FIX）

| 序号 | 级别 | 问题描述 | 代码依据（文件:行号） | 修复建议 |
| :--- | :--- | :--- | :--- | :--- |
| **MF-01** | **Blocker** | **测试套件回归失败**：`LoadingState_...` 单元测试由于等待了错误的 Task，断言必定失败。 | [`V2ShellUiTests.cs:722, 746-749`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3/apps/desktop-avalonia/tests/NewManga.App.Tests/V2ShellUiTests.cs#L722-L749) | 将第 722 行改为 `var refreshTask = shell.ViewModel.Library.RefreshAsync();`，并在第 747 行将 `await shell.Initialization;` 改为 `await refreshTask;`。 |
| **MF-02** | **Critical** | **数据静默错位**：`LoadReaderBookAsync` 中若指定的 `bookId` 未在快照中命中，直接 fallback 到第一本书，造成阅读器静默打开错误书籍。 | [`HostController.cs:336-342`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3/apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs#L336-L342) | 若 `!string.IsNullOrWhiteSpace(bookId)` 且在 `books` 中未找到，应降级调用一次 `await runtime.ListBooksAsync(cancellationToken)` 重新尝试匹配；仍未找到时才返回 `null`，严禁静默 fallback 到其他书籍。 |
| **MF-03** | **Critical** | **数据新鲜度与缓存一致性缺陷**：备份恢复后未清空章节缓存，且书架刷新不联动章节失效。 | [`HostController.cs:18, 1660-1662`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3/apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs#L1660-L1662) | 1. 在 `RestoreBackupAsync` 成功后，必须清空 `_chapterCache` 并调用 `RefreshBooksAsync()`；<br>2. 在 `RefreshBooksAsync()` 内部清空 `_chapterCache`，确保用户点击刷新时章节能够同步刷新。 |
| **MF-04** | **Major** | **并发线程安全风险**：`_chapterCache` 使用非线程安全的普通 `Dictionary` 且未加锁。 | [`HostController.cs:18, 299, 454-464`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3/apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs#L18) | 将 `Dictionary` 改为 `ConcurrentDictionary<string, IReadOnlyList<ChapterSummary>>`，或使用 `lock` 保护读写。 |
| **MF-05** | **Major** | **无效 Run 污染与后台定时器空转**：Console 中输入错误 run_id 导致永久污染 `KnownRunIds` 并陷入后台持续报错轮询。 | [`ConsoleViewModel.cs:652-664`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Console/ConsoleViewModel.cs#L652-L664) | 仅当读取成功（Snapshot 或 Projection 非空）时才调用 `_runMonitor.Track(runId)`；若读取失败，不应记住该 ID 并停止轮询。 |
| **MF-06** | **Major** | **`RunStateStatus` 漏掉 `cancelled` 导致状态图标颠倒**。 | [`RunStatusMonitor.cs:285-295`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3/apps/desktop-avalonia/src/NewManga.App/Shell/V2/RunStatusMonitor.cs#L285-L295) | 在 `RunStateStatus` 中将 `"cancelled" or "canceled" or "stopped"` 映射为 `NmStatus.Failed` 或 `NmStatus.Skipped`，绝不能落入 `NotStarted`。 |
| **MF-07** | **Minor** | **Core 真实步骤错误码遗漏与幽灵错误码**。 | [`RunStatusMonitor.cs:326-339`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3/apps/desktop-avalonia/src/NewManga.App/Shell/V2/RunStatusMonitor.cs#L326-L339) | 1. 将幽灵代码 `PROVIDER_UNKNOWN` 改为 `PROVIDER_NOT_IMPLEMENTED`（"Provider 未实现"）；<br>2. 补充 `PROVIDER_AUTH_FAILED`（"Provider 认证失败"）、`PROVIDER_TIMEOUT`（"请求超时"）、`PROVIDER_UNAVAILABLE`（"服务不可用"）、`PROVIDER_DEPENDENCY_MISSING`（"缺少运行依赖"）、`STEP_FAILED`（"步骤执行失败"）的中文映射。 |

---

## 已检查且判定无问题的项

1. **AC2 的架构分层与契约守约性**：
   - 严格遵守了“不修改冻结契约 `V11R_COMMAND_CONTRACT_V1.md`”的约束，未向 Core 增设非法的 List Run 命令。
   - `StudioBatchViewModel` 在创建 Run 后通过 `onRunTracked` 回调将真实 RunId 送往 `AppShellViewModel.TrackRun` 的接线清晰且解耦良好。
   - `RunIndexTests.cs`（4 个用例）对上限 12 个、最近优先（LRU）、去重及空白过滤的逻辑测试严密有效。
2. **AC3 的启动去重目标（基本链路）**：
   - `LibraryViewModel.InitializeAsync` 将首屏默认参数设为 `forceHostRead: false`，复用 Host 启动时已经由 `StartCoreAsync` 拉取并保留在 `_snapshot.Books` 中的快照，成功将启动期 Library 重复调用 `ListBooks` 降为 0 次。
   - `StartupReadDedupTests.cs`（3 个用例）对首屏 0 次、显式刷新 1 次、冷快照 1 次的调用计数断言清晰有效。
3. **AC4 错误码双通道保留设计**：
   - `StepErrorText` 在输出中文解释的同时，始终保留了原始 upper-snake 错误码标识符（格式为 `说明（CODE）`），未知错误码原样透传，未出现模糊或抹除诊断信息的违规行为。
4. **控制台 UI Chip 接线**：
   - `ConsoleView.axaml` 中使用 Chip 按钮展示 KnownRuns，点击后联动 `SelectCommand` 触发填充与读取，布局使用设计系统 Token，无硬编码像素。

---

## 推荐下一步

由任务 Owner（DSH）针对上述清单（**MF-01 ~ MF-07**）实施修复并提交 commit：
1. 优先修复 **MF-01**（修复 `V2ShellUiTests.cs` 中的 Task await 笔误，恢复 CI 绿灯）；
2. 修复 **MF-02 ~ MF-04**（保护数据新鲜度与线程安全，杜绝 Reader 静默打开错书与 Backup 恢复后残留脏缓存）；
3. 修复 **MF-05 ~ MF-07**（补齐错误码映射、修复取消状态图标、拦截无效 Run 轮询）；
4. 重新运行全量测试套件并提交独立审查复审。
