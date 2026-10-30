---
task: REALUSE-DATA-SAFETY-4
round: 1
reviewer: antigravity-headless
reviewer_participated_in_implementation: false
verdict: FAIL_WITH_MUST_FIX
reviewed_head: d05ef2078
reviewed_base: b8039aec8
captured_by: dsh-lead
capture_note: >
  Antigravity 原始回答逐字保存（agy headless --output-format json 的 response 字段）。
  正文未做任何编辑；审查者自行核对了 Core 侧能力字符串与 cleanup 白名单实现。
---

# REALUSE-DATA-SAFETY-4 独立审查（Round 1，Antigravity）

# 独立审查报告：REALUSE-DATA-SAFETY-4

- **审查对象**：`apps/desktop-avalonia`、`src/`、`doc/`
- **基线**：`main b8039aec8` -> **审查 HEAD**：`task/REALUSE-DATA-SAFETY-4 d05ef2078`
- **审查结论**：**`FAIL_WITH_MUST_FIX`**（发现阻断级功能缺陷：无法停用插件，以及操作后防重入锁自锁阻断界面刷新）

---

## 重点审查问题回答（逐项判定与依据）

### 1. 缓存清理的安全性
- **确认门能否被绕过？**：**不能**。
  - 在 UI 触发层，点击清理绑定 [ConsoleViewModel.cs#L533-L548](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Console/ConsoleViewModel.cs#L533-L548) 的 `RequestClearCache`，空预览时直接阻断提示，非空时强制弹出 `_requestConfirm` 危险确认弹窗。
  - 在 HostController 层，[HostController.cs#L1733-L1744](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs#L1733-L1744) 校验 `HOST_NOT_READY` 与 `HOST_READ_ONLY` 策略。
  - 在 HostRuntime 层，[HostRuntime.cs#L198](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs#L198) 执行 `RequireWritesAllowed()` 校验。UI 与后端均无法绕过确认门。
- **删除范围是否只限 Core 判定的 cache/ 前缀？**：**是的**。
  - C# 客户端向 Core 发送的 `cleanup.run` 请求体为空对象 `{}`，不传递任何由前端决定的路径。
  - Core 侧在 [cleanup.py#L140-L150](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/src/application/maintenance/cleanup.py#L140-L150) 中使用 [is_safe_relative_path](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/src/application/maintenance/cleanup.py#L229-L248) 严格白名单校验（强制以 `cache/` 开头，杜绝 `..` 路径穿越），底层物理文件删除受 `remover.remove_managed` 的根目录沙箱约束，绝对不会触碰原图、人工修改或锁定版本。
- **预览与执行之间如果状态变化，会不会删到预览之外的东西？**：
  - Core 的 `service.run()` 在执行时会**实时重新扫描**缓存目录；如果在预览与点击执行之间系统产生了新的安全瓦片/缓存，这些新缓存会被一同清理。
  - 但**所有被删除的文件均严格受限于 Core 的 `cache/` 安全白名单**，不会扩散到安全缓存以外的数据。
- **`cleanup.run` 失败项的 pending 语义在 UI 里是否完整？**：**不完整**（见下方必须修复清单问题 3）。
  - 当常规 `Targets` 已经被清空但存在残留失败项（`PendingCleanups > 0`）时，[ConsoleView.axaml#L165](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/Views/V2/Console/ConsoleView.axaml#L165) 的 `IsVisible="{Binding HasCleanupTargets}"` 会导致待重试提示被**错误隐藏**。
  - 此外，未接线 Core 已实现的 `cleanup.retry_pending` 命令，用户无法在 UI 上发起针对失败项的重试。

### 2. 插件开关语义
- **Core 的全局开关与单插件开关两段语义在 UI 的表达**：表达清晰准确。顶部有全局开关切换按钮 [ConsoleView.axaml#L122](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/Views/V2/Console/ConsoleView.axaml#L122)，每个插件有单独状态和开关按钮，且有横幅说明安全约束与两段生效规则。
- **`CanToggle` 的实现（全局关闭时禁用）**：合理且防御性良好。[PluginRowViewModel](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Console/ConsoleViewModel.cs#L2672) 中 `CanToggle = !IsRejected && globalEnabled;`，且 [ConsoleViewModel.cs#L400-L404](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Console/ConsoleViewModel.cs#L400-L404) 做了二次校验，避免了用户误以为单开即生效的错觉。
- **被拒绝（rejected）插件的处理**：处理正确。[PluginRowViewModel](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Console/ConsoleViewModel.cs#L2668-L2674) 准确展示 `ReasonText`，`CanToggle` 为 false 禁用操作，Core 侧 [service.py#L224](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/src/infrastructure/plugins/service.py#L224) 亦有 `PLUGIN_NOT_LOADED` 兜底。
- **严重缺陷**：实现中存在**无法停用插件**的致命错误（见下方问题 1）和**自锁阻断刷新**缺陷（见下方问题 2）。

### 3. 设备诊断的推导准确性
- **能力字符串核对**：核对通过。
  - Core 端定义在 [src/bootstrap/settings_commands.py#L32](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/src/bootstrap/settings_commands.py#L32)：`CAPABILITY_NAMES = ("OCR", "Translation", "Inpaint", "Detection", "Rendering")`。
  - C# 端定义在 [SettingsProfileContracts.cs#L17](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/Services/SettingsProfileContracts.cs#L17)：`public const string Detection = "Detection";`。
  - 二者大小写、单复数完全一致，`Capabilities.Contains(SettingsCapabilities.Detection)` 不会出现永远为 false 的情况。
- **Provider 列表未加载时的表现**：存在误导隐患（见下方问题 4）。在初始化中（`IsLoading == true`）或初始化失败时，因 `ProviderProfiles` 暂时为空，会被立即武断判定为“未绑定”并催促去配置。

### 4. 契约提案质量（[REALUSE-DATA-SAFETY-4-device-status-contract.md](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/doc/proposals/REALUSE-DATA-SAFETY-4-device-status-contract.md)）
- **是否真的不含绝对路径**：核对通过。`weights_label` 明确规范为文件名或版本标签，不含路径；`devices` 与 `detector` 结构均为逻辑标识与状态。
- **是否最小**：核对通过。单一只读命令 `diagnostics.device_status`，空参数，无夹带写操作，完全向后兼容。
- **`probe_error` 是否足够区分“无 GPU”与“探测损坏”**：设计充分。探测成功但无可用 GPU 时 `probe_error` 为 null，`devices` 表明无 GPU 可用；当底层库/驱动崩溃探测失败时，`probe_error` 返回 typed error code。

### 5. 回归与异常/可空路径
- Host 未就绪时，`GetCleanupPreviewAsync` 返回空预览，`ListPluginsAsync` 返回空清单，状态捕获并标记 `HOST_NOT_READY`，不会触发未捕获异常崩溃。
- 但是，新代码在布尔结果解析与防重入标志流转上引入了重大缺陷。

---

## 必须修复清单（MUST-FIX）

### 1. 【阻断级 P0】`CoreServiceClient` 将“停用”（`enabled: false`）的成功响应误判为调用失败
- **问题**：当用户停用全局插件或单插件时，方法永远返回 `false`，UI 弹出错误提示且不刷新。
- **依据**：
  - [CoreServiceClient.cs#L625-L627](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs#L625-L627)：
    ```csharp
    var result = RequireResult(response, "plugins.set_enabled");
    return result.ValueKind == JsonValueKind.Object
        && result.TryGetProperty("global_enabled", out var global)
        && global.ValueKind == JsonValueKind.True; // <-- 当停用时 Core 返回 {"global_enabled": false}，此处恒为 false！
    ```
  - [CoreServiceClient.cs#L650-L653](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs#L650-L653)：
    ```csharp
    var result = RequireResult(response, "plugins.set_plugin_enabled");
    return result.ValueKind == JsonValueKind.Object
        && result.TryGetProperty("enabled", out var value)
        && value.ValueKind == JsonValueKind.True; // <-- 当停用单插件时 Core 返回 {"enabled": false}，此处恒为 false！
    ```
  - [ConsoleViewModel.cs#L382-L386](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Console/ConsoleViewModel.cs#L382-L386) 与 [L423-L427](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Console/ConsoleViewModel.cs#L423-L427) 检查 `if (!ok)`，直接弹出“插件开关被拒绝：未知原因”并提前退出，后续流程全部中断。
- **建议**：
  改为判断返回的布尔字段存在且为有效布尔值（或其布尔值与入参一致），例如：
  `global.ValueKind == (enabled ? JsonValueKind.True : JsonValueKind.False)` 或 `global.ValueKind is JsonValueKind.True or JsonValueKind.False`。

### 2. 【阻断级 P0】操作完成后的自动刷新被防重入锁自身阻断（自锁 Bug）
- **问题**：在清理缓存、切换全局插件、切换单插件成功后，界面上的列表完全不会自动刷新，仍停留在旧状态。
- **依据**：
  - 清理操作：[ConsoleViewModel.cs#L552](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Console/ConsoleViewModel.cs#L552) 设置了 `IsCleanupBusy = true;`，在 [L566](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Console/ConsoleViewModel.cs#L566) 调用 `await RefreshCleanupPreviewAsync()`。而 [RefreshCleanupPreviewAsync](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Console/ConsoleViewModel.cs#L504-L507) 的第一行就是：
    ```csharp
    if (IsCleanupBusy)
    {
        return; // <-- 命中自锁，直接退出，根本不执行刷新！
    }
    ```
  - 插件操作：[ConsoleViewModel.cs#L378](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Console/ConsoleViewModel.cs#L378) 设置 `IsPluginsBusy = true;`，在 [L390](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Console/ConsoleViewModel.cs#L390) 调用 `await RefreshPluginsAsync()`；同理在 [RefreshPluginsAsync#L333-L336](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Console/ConsoleViewModel.cs#L333-L336) 被 `if (IsPluginsBusy) return;` 阻断退出。
  - 单元测试因仅使用了 `FakeHostController` 且没有断言集合变更（只断言了调用计数和最后提示文本），掩盖了这一问题。
- **建议**：
  将数据加载的核心逻辑抽离为无锁内部方法（如 `RefreshCleanupPreviewCoreAsync()` / `RefreshPluginsCoreAsync()`），或在 `finally` 块释放 `IsBusy` 锁后再触发刷新。

### 3. 【功能级 P1】`CleanupPendingText` 绑定在 `HasCleanupTargets` 上导致待重试提示被误隐藏
- **问题**：当常规缓存目标已清空但存在失败待重试项（`PendingCleanups > 0`）时，失败提示被彻底隐藏。
- **依据**：[ConsoleView.axaml#L165](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/Views/V2/Console/ConsoleView.axaml#L165)：
  ```xml
  <TextBlock Classes="meta" Text="{Binding CleanupPendingText}" TextWrapping="Wrap" IsVisible="{Binding HasCleanupTargets}" />
  ```
  如果常规文件都已被删除，`HasCleanupTargets` 为 `false`，用户将无法看到任何待重试失败项的信息。
- **建议**：
  在 ViewModel 中提供 `HasCleanupPending` 属性，或使用 `IsVisible="{Binding !!CleanupPendingText.Length}"`。

---

## 优化建议清单（SUGGESTIONS）

1. **【P2 体验】Provider 加载中/离线状态下的设备诊断文案处理**
   - **依据**：[ConsoleViewModel.cs#L448-L454](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Console/ConsoleViewModel.cs#L448-L454)。
   - **说明**：当 `IsLoading` 为 true 或 `_initialized` 为 false 时，`ProviderProfiles` 暂为空，直接提示未绑定并展示跳转按钮不够准确。建议在加载中时显示“正在检查 Provider 配置...”。
2. **【P2 代码卫生】XAML 中遗留未接入时期的死代码**
   - **依据**：[ConsoleView.axaml#L110-L112](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/Views/V2/Console/ConsoleView.axaml#L110-L112) 保留了 `<Button Classes="danger sm" Content="清理缓存与过期版本（能力待接入）"...>`，但在 Storage 分区已设为 `isWired: true` 之后，其父级容器永远不可见，属于无用冗余代码。
3. **【P2 布局】清理目标列表嵌套的 ScrollViewer 未限制高度**
   - **依据**：[ConsoleView.axaml#L170](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4/apps/desktop-avalonia/src/NewManga.App/Views/V2/Console/ConsoleView.axaml#L170) 的 `ScrollViewer` 置于 `StackPanel` 中未设置 `MaxHeight`，而外层已有全局滚动条，可能导致滚动冲突或失去虚拟化滚动效果。建议添加 `MaxHeight="260"`。

---

## 已检查且判定无问题的项

1. **冻结契约完整性**：未修改 `doc/contracts/` 下任何文件，提案以独立文档形式沉淀在 `doc/proposals/`，符合 AC3 与协作规则。
2. **清理范围受控性**：Core 侧白名单（`cache/` 前缀、无跨目录）在 `service.preview`、`service.run` 和 `retry_pending` 中均严格一致执行，物理上绝不会逃逸至业务图片或人工标记数据。
3. **能力字符串匹配性**：Core 的 `CAPABILITY_NAMES` 与 C# 端 `SettingsCapabilities.Detection` 完全一致。
4. **被拒绝插件防御**：对 rejected 插件的 status、reason 展现及禁用开关逻辑正确闭环。
5. **提案规范性**：`diagnostics.device_status` 提案严格遵循无绝对路径原则，`probe_error` 能有效区分硬件缺失与探测故障。

---

## 推荐下一步

交由任务 Owner（DSH）在工作区 `G:\CODEX\New Manga.workspace\worktrees\REALUSE-DATA-SAFETY-4` 中修复上述 MUST-FIX 问题 1（布尔解析）、问题 2（自锁刷新）与问题 3（Pending 显隐绑定），并在 `V2ConsoleUiTests.cs` 中补充覆盖以下回归断言：
1. 切换开关为停用（`SetPluginEnabledAsync(..., false)` / `SetPluginsGlobalEnabledAsync(false)`）时 CoreServiceClient 正确返回 true。
2. 清理执行后以及插件切换后，UI ViewModel 上的列表与状态能够自动刷新至最新。
修复提交后重新指派独立审查。
