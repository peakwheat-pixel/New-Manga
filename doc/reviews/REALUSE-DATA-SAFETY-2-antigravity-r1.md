---
task: REALUSE-DATA-SAFETY-2
round: 1
reviewer: antigravity-headless
reviewer_participated_in_implementation: false
verdict: FAIL_WITH_MUST_FIX
reviewed_head: 770e8a633
reviewed_base: a29e0f516
captured_by: dsh-lead
capture_note: >
  Antigravity 原始回答逐字保存（agy headless，--output-format json 的 response 字段）。
  下方正文未做任何编辑；DSH 未参与该结论的形成。
---

# REALUSE-DATA-SAFETY-2 独立审查（Round 1，Antigravity）

## 审查结论：`FAIL_WITH_MUST_FIX`

---

## 必须修复清单（MUST FIX）

### 1. `HostController.StartAsync` 重试时未 Dispose 旧 `_runtime`，导致 Win32 Named Mutex 及进程资源泄露，使重试必败

- **问题**：在 `HostController.StartAsync` 中，当上一次启动失败（`State != Ready`）且用户触发重试时，代码将 `_startTask` 和 `_runtime` 直接置空后重新发起 `StartCoreAsync`。但上一次失败的 `_runtime` **从未被释放（未调用 `DisposeAsync`）**。
- **依据**：
  - [HostController.cs](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-2/apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs#L77-L81)：
    ```csharp
    if (_startTask is { IsCompleted: true } && _snapshot.State != HostViewState.Ready)
    {
        _startTask = null;
        _runtime = null; // 未调用 staleRuntime.DisposeAsync()
        ...
    ```
  - [HostRuntime.cs](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-2/apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs#L528-L535)：在 `StartInternalAsync` 中首先调用 `SingleInstanceGuard.TryAcquire`，成功获取系统级命名互斥体 `_guard = guard!;`。
  - [SingleInstance.cs](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-2/apps/desktop-avalonia/src/NewManga.Host/SingleInstance.cs#L186-L208)：Win32 命名互斥体运行在专用后台线程中，只要未调用 `Dispose()`，该后台线程就会一直持有互斥体（超时时间长达 10 分钟）。
- **影响分析**：
  若首次启动在获取互斥体之后发生失败（例如 `SidecarLocator.Locate` 失败、管道 I/O 异常、或自检未通过等），`_runtime` 会处于非空且持有互斥体的状态。当用户在 UI 点击“重试”时，旧的 `_runtime` 被直接赋空抛弃，互斥体依然被旧后台线程占用。重试执行的第二次 `StartInternalAsync` 在尝试获取同一个互斥体时会必定失败（返回 `false`），直接走入：
  ```csharp
  _log.Warn("single-instance mutex already owned; exiting without spawning sidecars");
  Result = HostStartResult.AlreadyRunning();
  ```
  **重试结果会被永久误判为「已有 New Manga 主机在运行」，导致重试功能彻底失效，且未释放的 sidecar 进程和日志句柄会残留泄露。**
- **建议修法**：
  在 `StartAsync` 重试路径中，暂存旧实例 `var staleRuntime = _runtime; _runtime = null;`，并在进入新的 `StartCoreAsync` 之前异步释放该实例：
  ```csharp
  // 示意：在重试创建新启动任务时，先清理旧 runtime 资源
  return _startTask ??= StartWithCleanupAsync(staleRuntime, cancellationToken);

  private async Task StartWithCleanupAsync(IAsyncDisposable? staleRuntime, CancellationToken ct)
  {
      if (staleRuntime is not null)
      {
          try { await staleRuntime.DisposeAsync().ConfigureAwait(false); } catch { /* 忽略清理期异常 */ }
      }
      await StartCoreAsync(ct).ConfigureAwait(false);
  }
  ```
- **严重级别**：`MUST_FIX`（功能性阻断缺陷 + 操作系统级资源泄露）

---

## 建议改进清单（非阻断性 / Code Smell）

### 2. `StudioBatchViewModel.cs` 中存在死代码（Dead Code）
- **问题**：在 `StudioBatchViewModel.cs` 的第 1124–1127 行存在重复且不可达的 `if (started is null)` 分支。
- **依据**：[StudioBatchViewModel.cs](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-2/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Studio/StudioBatchViewModel.cs#L1100-L1127)：
  在第 1100 行已执行 `if (started is null) { ... return null; }`；后续第 1124 行再次判断 `if (started is null) { return null; }` 永远不会为真。
- **建议修法**：删除 1124–1127 行冗余代码。
- **严重级别**：`LOW`

### 3. `StudioBatchControls.cs` 错误态空态卡片主按钮的两段式点击体验
- **问题**：在 [StudioBatchControls.cs](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-2/apps/desktop-avalonia/src/NewManga.App/Views/V2/Studio/Controls/StudioBatchControls.cs#L712) 中：
  ```csharp
  _startButton = StudioUi.Button("开始处理", "primary", () => {
      if (_viewModel.State == StudioBatchRunState.Error) { _ = _viewModel.RefreshAsync(); }
      else { _ = _viewModel.StartProcessingAsync(); }
  });
  ```
  在 `PROVIDER_NOT_CONFIGURED` 拒绝后，卡片主按钮依然是“开始处理”，但此时 `State == Error`，点击会触发 `RefreshAsync()`。由于此时从未创建成功过 Run（`_runId` 为空），`RefreshAsync()` 只会把 `State` 重置为 `NoRun`。用户需要**第二次点击**同一个按钮，才会真正发起 `StartProcessingAsync()`。
- **建议修法**：虽然两段式流转逻辑闭环且未静默失败，但建议在无 `_runId` 的错误态下直接重新发起处理，或刷新恢复后自动引导重跑。
- **严重级别**：`SUGGESTION`

### 4. 治理检查器状态与 Ledger 校验失败
- **问题**：运行 `pwsh -NoProfile -File tools/governance/check.ps1` 报告：
  - `FAIL: TASK_LEDGER 已过期：声明 8 个非终态 Task，实际 7 个`
  - `FAIL: READY DAG 只允许 status: ready；REALUSE-DATA-SAFETY-2 当前为 in_review`
- **建议修法**：按独立审查规则，本审查者不修改任何文件。后续由 Lead / DSH 在推进或收口时运行 `python tools/governance/task_ledger.py --write` 并同步状态。
- **严重级别**：`GOVERNANCE_NOTICE`

---

## 判定无问题的项（逐项回答重点审查问题）

### 1. AC1 是否真正消除“静默失败”？空态卡片改动是否安全？
- **无遗漏启动入口**：
  经对整个 `apps/desktop-avalonia/` 代码库排查，启动 Run 的业务能力**仅存在于** `StudioBatchViewModel.StartRunAsync`（由空态卡片主按钮 `StartProcessingAsync` 及动作栏四项批处理动作触发）。
  - 全局命令面板 [ShellCommands.cs](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-2/apps/desktop-avalonia/src/NewManga.App/Shell/V2/ShellCommands.cs#L51-L77)：涉及 Run 投影与导出的命令（`attention.next`、`export.run`）均标记为 unavailable 且附带未接入文案，无静默执行路径；
  - 快捷键映射 [KeyMap.cs](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-2/apps/desktop-avalonia/src/NewManga.App/Shell/V2/KeyMap.cs)：无直接触发 StartRun 的按键；
  - 工作台 Page 模式：专用于单页视图与标定，无批处理 Run 启动入口。
- **空态卡片可见性（`_emptyHost.IsVisible = !hasData`）在各状态下的视觉与交互表现**：
  - `NoRun`：`hasData == false`，卡片显示“无活动 Run”，正确；
  - `NotWired`：`hasData == false`，卡片显示未接入说明且按钮禁用，正确；
  - `Loading`：`hasData == false`，卡片显示“正在读取任务投影…”，正确；
  - `有旧投影时 Error / Partial`：已有旧投影时，轮询失败进入的是 `StudioBatchRunState.Partial`（此时 `HasData == true`，[StudioBatchViewModel.cs#L424](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-2/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Studio/StudioBatchViewModel.cs#L424)），卡片依然隐藏，矩阵数据得以保留；而若在旧投影存在时执行批处理动作被拒绝进入 `Error`，卡片显示出来以优先向用户呈现强阻断原因，符合视觉交互预期。

### 2. AC2 状态诚实性是否有遗漏路径？
- **状态徽标与文本诚实性**：
  - [AppShellViewModel.cs#L380-L387](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-2/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Shell/AppShellViewModel.cs#L380-L387)：`StatusBandState` 已切分为 `IsHostWritable ? NmStatus.Done : NmStatus.Blocked`，只读模式下状态徽标返回黄色/阻断（`Blocked`），绝不会呈现代表全通的绿色 `Done`。
  - `HostStatusText` 与 `StatusBandRight`：已显式附加 `Host 就绪（只读：...）` 及其原因。
  - Console 诊断页与 Library 页：模式行直接绑定 `ModeLine`，并新增“启动自检”行，全程序未发现托盘图标或假绿色状态泄漏。
- **单 sidecar 单例保证（正常路径）**：
  在 `State == Ready` 时，`_startTask is { IsCompleted: true } && _snapshot.State != HostViewState.Ready` 为 false，不会重置 `_startTask`，保证正常运行时单 sidecar 绝不重复启动。

### 3. AC3 语义变更是否安全？
- **`Passed` 语义安全，未掩盖真实契约问题**：
  [StartupSelfCheck.cs#L73-L120](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-2/apps/desktop-avalonia/src/NewManga.Host/StartupSelfCheck.cs#L73-L120) 严格验证了 `core.ping` 能够提供的全部真实信息（ProtocolMajor、ProtocolMinor 下限、必需能力集）。旧代码因未能枚举 66 个命令面而一律标记为 Degraded，导致该字段在 12/12 次正常启动中失去信息量。将这层边界明确区分为“启动握手通过 = Passed，命令面全量逐条比对 = 由 Parity Tests 覆盖并在 Detail 留痕”，设计是清晰且诚实的。
- **写入控制与错误透传正常**：
  `Passed` 下 `WritesBlocked` 为 false，写入保持正常开放；任何版本或能力缺失均严格返回 `Failed` 并切断写网关（进入 `ReadOnlySelfCheckFailed`）；自检探测失败返回 `Degraded` 并保留 typed error code，且已通过 [ConsoleView.axaml#L461](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-2/apps/desktop-avalonia/src/NewManga.App/Views/V2/Console/ConsoleView.axaml#L461) 渲染到界面供用户排查。

### 4. 测试有效性与契约变更合理性
- **`ErrorState_ShowsRetryInsteadOfStart_AndHidesEmptyCard` 改写合理**：
  历史测试之所以断言“隐藏空态卡”，是固化了旧实现中的缺陷逻辑（导致错误发生时无任何控件展示错误文案）。本次实现将其重命名为 `ErrorState_ShowsRetryAndKeepsTheCardVisible_SoTheReasonIsReadable`，并断言 `Assert.True(view.BatchWorkspace.EmptyStateHost.IsVisible);`，是对历史错误断言的正向纠偏。
- **新增测试真实有效**：
  新增的 `StartRunWithoutProvider_ShowsActionableGuidance_AndTheCardStaysVisible`、`StartRunFailure_KeepsTheTypedCodeForOtherRefusals`、`ReadOnlyHost_IsNotShownAsGreenReady` 与 `WritableHost_KeepsGreenReadyState` 分别真实验证了文案引导、卡片可见性、只读阻断徽标与可写状态，全量 813 个测试全部绿灯通过。

---

## 推荐下一步

根据 [AGENTS.md](file:///g:/CODEX/New%20Manga/AGENTS.md) 规则，本次审查未修改任何文件，未执行任何 Git 写操作。
建议将本审查报告反馈给 **dsh-lead**，优先修复 **MUST FIX 1**（在 `HostController.StartAsync` 重试路径加入旧 `_runtime` 的 `DisposeAsync` 清理逻辑），修复后重新进入独立审查。
