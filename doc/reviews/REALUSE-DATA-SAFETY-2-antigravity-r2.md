---
task: REALUSE-DATA-SAFETY-2
round: 2
reviewer: antigravity-headless
reviewer_participated_in_implementation: false
verdict: PASS
reviewed_head: f0e207db5
reviewed_base: a29e0f516
previous_round: FAIL_WITH_MUST_FIX (doc/reviews/REALUSE-DATA-SAFETY-2-antigravity-r1.md)
captured_by: dsh-lead
capture_note: >
  Antigravity 复核原始回答逐字保存（同一会话续接，agy --conversation）。
  下方正文未做任何编辑；复核者自行运行了全量测试。
---

# REALUSE-DATA-SAFETY-2 独立审查复核（Round 2，Antigravity）

## 复核结论：`PASS`

---

### 1. MUST FIX 1（重试未释放旧 runtime 导致互斥体泄漏必报 AlreadyRunning）
- **状态**：**已修复**
- **依据**：
  - [HostController.cs#L83-L126](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-2/apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs#L83-L126)：在 `StartAsync` 重试分支中，将旧实例提取为 `staleRuntime = _runtime; _runtime = null;` 并传入 `StartCoreAsync`；在发起新尝试前执行 `await staleRuntime.DisposeAsync().ConfigureAwait(false)`，确保前一次尝试占有的 Win32 命名互斥体（`_guard`）及 sidecar 进程/管道句柄完全释放。
  - [HostRuntime.cs#L78-L97](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-2/apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs#L78-L97)：在 `HostRuntime.StartAsync` 外层增加保护——若 `StartInternalAsync` 抛出未在内部 catch 的逃逸异常，首先执行 `await runtime.DisposeAsync()` 释放互斥体后再 `throw;`，彻底杜绝了互斥体在异常逃逸路径上的泄漏可能。
  - 经全面审查 `HostRuntime.DisposeAsync()` 与 `SingleInstanceGuard.Dispose()`，两处均有 `_disposed` 幂等守卫，`StartCoreAsync` 亦捕获了良性清理异常并以 Debug 输出记录，不存在二次释放或对象已释放抛错风险。

---

### 2. 建议 2（`StudioBatchViewModel` 中的死代码）
- **状态**：**已修复**
- **依据**：
  - [StudioBatchViewModel.cs#L1120-L1126](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-2/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Studio/StudioBatchViewModel.cs#L1120-L1126)：原先在第 1100 行已处理 `if (started is null) { ... return null; }` 之后的冗余 `if (started is null) { return null; }` 分支确已完全删除，代码路径干净。

---

### 3. 新增回归测试的有效性与复现能力
- **状态**：**已修复且测试有效**
- **依据**：
  - [HostControllerRetryTests.cs#L16-L57](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-2/apps/desktop-avalonia/tests/NewManga.App.Tests/HostControllerRetryTests.cs#L16-L57)：测试通过配置不存在的 sidecar 路径（`SidecarDirectoryOverride`），精准让首次启动在“已成功获取 Win32 命名互斥体之后、定位 sidecar 二进制时”发生失败（返回带有 `SidecarExeMissing` 的 `HostViewState.Failed`）。
  - **因果反推验证**：若回退本次修复，第二次 `StartAsync` 重试会因前一个后台线程依然霸占互斥体，导致 `SingleInstanceGuard.TryAcquire` 返回 `false` 并走到 `AlreadyRunning`，从而使断言 `Assert.NotEqual(HostViewState.AlreadyRunning, controller.Snapshot.State)` 必定失败。本测试准确捕获并锁定了原缺陷，运行耗时约 20ms，1/1 通过。

---

### 4. 是否因修复引入新问题或与单例假设冲突
- **状态**：**已检查并判定无问题**
- **依据**：
  - [HostController.cs#L84-L106](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-2/apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs#L84-L106)：重试清理守卫严格受 `_snapshot.State != HostViewState.Ready` 约束。当启动成功时该条件恒为 false，`staleRuntime` 始终为 null，已就绪的正常运行实例绝不会被误 Dispose；`_startTask ??=` 保证了正常状态下返回既有任务，单 sidecar 单例假设完好。
  - 全解决方案测试（`dotnet test apps/desktop-avalonia/NewManga.sln`）全量回归通过：816 个测试通过，0 个失败（其中 `NewManga.App.Tests` 330 个测试全绿）。

---

## 推荐下一步

本分支代码实现、缺陷修复与回归防护测试均已完备且通过验证。
建议由 **dsh-lead** 接手执行后续收口流程：
1. 运行 `python tools/governance/task_ledger.py --write` 同步任务账本并解除治理检查器报错；
2. 将 `doc/tasks/REALUSE-DATA-SAFETY-2.md` 的状态推进至 `done` 并完成合流集成。
