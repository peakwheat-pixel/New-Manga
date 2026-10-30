---
task: REALUSE-DATA-SAFETY-4
round: 2
reviewer: antigravity-headless
reviewer_participated_in_implementation: false
verdict: PASS
reviewed_head: 37dcd6d9f
reviewed_base: b8039aec8
previous_round: FAIL_WITH_MUST_FIX (doc/reviews/REALUSE-DATA-SAFETY-4-antigravity-r1.md)
captured_by: dsh-lead
capture_note: >
  Antigravity 复核原始回答逐字保存（同一会话续接）。正文未做任何编辑；复核者对我修复过程中
  误伤的其它 bool 写方法做了全工程符号审计并确认无残留。
---

# REALUSE-DATA-SAFETY-4 独立审查复核（Round 2，Antigravity）

# 独立复核报告：REALUSE-DATA-SAFETY-4（Round 2）

- **复核对象**：`task/REALUSE-DATA-SAFETY-4`
- **复核 HEAD**：`37dcd6d9f`（代码修复提交：`3844851e8`）
- **基线**：`main b8039aec8`
- **复核结论**：**`PASS`**

---

## 逐项复核判定（文件与代码行依据）

### M1（阻断）插件/全局开关无法停用（`{"enabled": false}` 误判为失败）
- **判定**：**已修复**
- **依据**：
  - [CoreServiceClient.cs#L636-L657](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs#L636-L657)：`SetPluginsGlobalEnabledAsync` 校验 Core 返回的 `global_enabled` 属性，有效布尔值（`True` 或 `False`）均转为 `bool?` 返回，仅当响应结构异常时返回 `null`。
  - [CoreServiceClient.cs#L665-L690](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs#L665-L690)：`SetPluginEnabledAsync` 同样将 Core 返回的布尔值转为 `bool?`。
  - [HostRuntime.cs#L180-L194](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs#L180-L194) 与 [IHostController.cs#L405-L408](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs#L405-L408)：接口契约及运行时统一透传 `Task<bool?>`。
  - [HostController.cs#L1645-L1706](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs#L1645-L1706)：`HOST_NOT_READY`、`HOST_READ_ONLY`、参数非法及异常分支均返回 `null`，成功调用返回 `bool?`。
  - [ConsoleViewModel.cs#L381-L387](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Console/ConsoleViewModel.cs#L381-L387) 及 [L422-L428](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Console/ConsoleViewModel.cs#L422-L428)：UI 端使用 `if (confirmed is null)` 判断调用成败，`confirmed.Value` 判断新状态，成功支持停用分支。
- **误伤排查**：对全工程 `bool?` 符号进行全局审计，仅上述两处插件开关方法使用了 `Task<bool?>`，其余写方法（如备份、还原、网络配置、Provider 等）均保持原有签名和布尔语义，**无残留误伤**。

---

### M2（阻断）写路径置 `IsBusy` 后调用刷新触发自锁，导致界面不更新
- **判定**：**已修复**
- **依据**：
  - [ConsoleViewModel.cs#L329-L336](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Console/ConsoleViewModel.cs#L329-L336)：`RefreshPluginsAsync` 作为公开守卫入口，防范用户并发手动刷新；核心加载逻辑拆分为私有方法 `RefreshPluginsCoreAsync`。写操作（[L390](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Console/ConsoleViewModel.cs#L390)、[L431](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Console/ConsoleViewModel.cs#L431)）完成后直接调用 `RefreshPluginsCoreAsync`，绕开守卫完成重新加载。
  - [ConsoleViewModel.cs#L510-L518](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Console/ConsoleViewModel.cs#L510-L518)：清理预览同样拆分为公开入口 `RefreshCleanupPreviewAsync` 与核心方法 `RefreshCleanupPreviewCoreAsync`，供清理操作（[L574](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Console/ConsoleViewModel.cs#L574)）与重试操作（[L618](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Console/ConsoleViewModel.cs#L618)）调用。
- **状态复位与重入排查**：两处模块的所有业务流程均有完整的 `try ... finally { IsBusy = false; }` 双重兜底（写操作方法与 Core 刷新方法各自维护独立 `finally` 块），无论发生网络异常、Core 拒绝、还是 UI 渲染异常，`IsPluginsBusy` 与 `IsCleanupBusy` 均保证被清零复位，**无状态泄漏或并发重入隐患**。

---

### M3（功能）待重试失败项被 `HasCleanupTargets` 遮蔽
- **判定**：**已修复**
- **依据**：
  - [ConsoleViewModel.cs#L477](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Console/ConsoleViewModel.cs#L477)：新增独立计算属性 `public bool HasCleanupPending => !string.IsNullOrWhiteSpace(_cleanupPendingText);`，并在预览加载后触发通知（[L533](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Console/ConsoleViewModel.cs#L533)）。
  - [ConsoleView.axaml#L165-L169](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/Views/V2/Console/ConsoleView.axaml#L165-L169)：视图层将待重试提示与操作按钮放入独立 `Grid`，其显隐属性直接绑定为 `IsVisible="{Binding HasCleanupPending}"`。当常规缓存列表为空但存在待重试项时，提示及操作按钮依然完整显示。

---

### M4（体验）Provider 列表未加载时误判并展示“未绑定”
- **判定**：**已修复**
- **依据**：
  - [ConsoleViewModel.cs#L450-L457](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Console/ConsoleViewModel.cs#L450-L457)：引入 `_providersLoaded` 状态标记，文案实现三态分流：
    - 未读取：`"检测能力：Provider 列表尚未读取，暂时无法判断（切换到「Provider 与凭据」会自动加载）。"`
    - 已读取且具备启用检测能力的 Provider：`"检测能力：已有启用且声明「检测」的 Provider，检测步骤可以提交。"`
    - 已读取但不具备：`"检测能力：未绑定——提交检测会失败并返回 PROVIDER_NOT_CONFIGURED..."`
  - [ConsoleViewModel.cs#L2365](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Console/ConsoleViewModel.cs#L2365)：`RefreshProvidersAsync` 执行完成后设置 `_providersLoaded = true` 并触发属性变更。

---

### M5（功能）`cleanup.retry_pending` 四层接线与确认门打通
- **判定**：**已修复**
- **依据**：
  - 客户端层：[CoreServiceClient.cs#L572-L588](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs#L572-L588) 实现 `RetryPendingCleanupsAsync`，向 Core 发送 `cleanup.retry_pending` 并复用 `ParseCleanupOutcome` 解析。
  - 宿主运行层：[HostRuntime.cs#L165-L170](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs#L165-L170) 严格执行 `RequireWritesAllowed()` 写安全门检查。
  - 控制器层：[HostController.cs#L1758-L1783](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs#L1758-L1783) 实现就绪状态检查、只读策略防护与异常映射。
  - 视图模型层：[ConsoleViewModel.cs#L584-L622](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Console/ConsoleViewModel.cs#L584-L622) 提供 `RetryPendingCleanupsCommand`，强制弹出 `ConfirmRequest`（危险写操作确认），并在重试完成后自动调用 `RefreshCleanupPreviewCoreAsync` 刷新 pending 数量。
  - 视图层：[ConsoleView.axaml#L167-L168](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/Views/V2/Console/ConsoleView.axaml#L167-L168) 增加“重试失败项”按钮，与忙碌状态联动禁用。

---

## 回归测试有效性验证

对 `V2ConsoleUiTests.cs` 新增的 5 个测试用例进行逻辑路径与逆向回归分析：
1. **`PluginsSection_DisablingAPlugin_IsReportedAsSuccess`**（[L938-L956](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/tests/NewManga.App.Tests/V2ConsoleUiTests.cs#L938-L956)）：
   - 断言了停用时 `PluginsLastResult` 包含“已停用”且通知不包含“被拒绝”。在旧代码下返回 false 会进入被拒通知并提前退出，断言必挂，**测试敏感有效**。
2. **`PluginsSection_RefreshAfterToggle_ActuallyReloadsTheList`**（[L962-L981](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/tests/NewManga.App.Tests/V2ConsoleUiTests.cs#L962-L981)）：
   - 断言写操作后 `fake.PluginListCalls > before`。在旧代码下受忙碌标志自锁影响，刷新不会执行，等待必超时失败，**测试敏感有效**。
3. **`StorageSection_PendingFailures_StayVisibleWithAnEmptyTargetList`**（[L987-L1000](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/tests/NewManga.App.Tests/V2ConsoleUiTests.cs#L987-L1000)）：
   - 验证空目标列表下 `HasCleanupPending` 依然为 true。在旧代码下无此属性且视图层隐藏，断言必挂，**测试敏感有效**。
4. **`StorageSection_RetriesPersistedFailuresThroughTheConfirmGate`**（[L1003-L1024](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/tests/NewManga.App.Tests/V2ConsoleUiTests.cs#L1003-L1024)）：
   - 完整验证“弹出确认框前未调用 -> 确认后调用 -> 结果展示为待重试项已清空”，**测试敏感有效**。
5. **`DevicesSection_SaysUnknown_BeforeAnyProviderListArrives`**（[L1027-L1044](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/tests/NewManga.App.Tests/V2ConsoleUiTests.cs#L1027-L1044)）：
   - 验证未启动完成的控制器下不会输出 `PROVIDER_NOT_CONFIGURED`，而是必须包含“尚未读取”。在旧代码下直接输出未绑定，断言必挂，**测试敏感有效**。

全套测试运行结果：373 passed, 7 skipped, 0 failed（总计 380 个测试）。

---

## 总结论

**PASS**

所有第一轮审查发现的阻断级缺陷（M1、M2）与功能缺陷（M3、M4、M5）均已按最小侵入、架构一致的原则完整修复，未引入新的重入漏洞或写方法语义误伤，回归测试覆盖充分且有效。

### 推荐下一步

交由 Lead / Integrator（DSH）执行任务收尾与主线集成：
1. 依据 [协作协议 §4](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/doc/09_COLLABORATION.md#4-task-文件约定)，在 `doc/tasks/REALUSE-DATA-SAFETY-4.md` 中填写 Canonical Evidence 的 commit 与 sha256，将任务状态从 `in_review` 推进至集成阶段；
2. 将 `task/REALUSE-DATA-SAFETY-4` 分支变更合并至 `main`。
