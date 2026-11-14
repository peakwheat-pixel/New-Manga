# E8-STUDIO-BINDING-1：V2 Studio 成批 XAML 绑定错误的根因与修复

基线 `2ec97f525`。修 E-8（P2）。

## 1. 真实日志（不是猜的）

`G:\CODEX\New Manga.workspace\task-envs\GATE4-READER-PAGE-1\logs\library\startup.log`：

```
[Binding]An error occurred binding 'IsEnabled' to 'IsEnabled' at 'IsEnabled':
  'Could not find a matching property accessor for 'IsEnabled' on
   'NewManga.App.ViewModels.V2.Studio.StudioPageViewModel'.' (Button #40214598)
[Binding]An error occurred binding 'Text' to 'ActiveTabLabel' at 'ActiveTabLabel':
  'Could not find a matching property accessor for 'ActiveTabLabel' on
   'NewManga.App.ViewModels.V2.Studio.StudioPageViewModel'.' (TextBlock #12595404)
[Binding]An error occurred binding 'Source' to 'CurrentPage.Image' at 'CurrentPage': 'Value is null.'
```

8 个 `IsEnabled` + 1 个 `ActiveTabLabel` + 1 个 `CurrentPage.Image` null。

## 2. 根因：**三个控件没有可解析的 DataContext**

我一开始误以为 `StudioPageViewModel` 缺 `IsEnabled` —— **错了**，它有（`:202`）。
真正的问题是**绑定写成了裸绑定**（不带 `Source`），而**这些控件的 DataContext 解析不到目标 VM**。

| 控件 | 是否设 DataContext | 裸绑定结果 |
|---|---|---|
| `StudioPageWorkspace` | **`L48: DataContext = viewModel`** | ✅ 正常工作（其 11 处裸绑定**不是 bug**） |
| `StudioInspectorPanel` | `L89: panel.DataContext = _inspector`，但 `:70` 的绑定**写在赋值之前** | ⚠️ 首次解析失败（时序） |
| **`StudioLeaveModal`** | **完全没设** | ❌ 3 处裸绑定**永久失效** |
| **`StudioHudRingControl`** | **完全没设** | ❌ 8 个 `IsEnabled` **全失效**（循环里 8 个 slot，与日志的 8 条完全对应） |

**这正是日志里恰好 8 条 `IsEnabled` 的原因** —— `StudioHudRingControl` 为 8 个 HUD slot 各建一个 Button。

## 3. 修复（4 处，与正确写法对齐）

正确的模板就在同文件里：

```csharp
// StudioInspectorPanel.cs:75 —— 已有 Source（正确）
regionSummary.Bind(TextBlock.TextProperty,
    new Binding(nameof(StudioPageViewModel.SelectedRegionSummary)) { Source = _page });

// StudioBatchControls.cs:751 —— 已有 Source（正确）
button.Bind(IsEnabledProperty,
    new Binding(nameof(StudioBatchActionViewModel.IsEnabled)) { Source = captured });
```

改动的 4 处：

| 文件:行 | 改动 |
|---|---|
| `StudioHudRingControl.cs:47` | `IsEnabled` 绑定加 **`{ Source = captured }`**（`captured` 是循环里已存在的局部变量，即该 slot 的 VM） |
| `StudioInspectorPanel.cs:70` | `ActiveTabLabel` 绑定加 **`{ Source = _inspector }`**（消除时序依赖，不再依赖 `:89` 的 DataContext 赋值） |
| `StudioLeaveModal.cs:42/46/53` | `LeaveBody` / `LeaveError` / `LeaveSaveEnabled` 三处加 **`{ Source = _viewModel }`** |

## 4. 未做（诚实登记）

- **没有加判别测试**。`StudioHudRingControl` 虽有公开 `Buttons` 属性可断言 `IsEnabled`，
  但其构造需要完整的 `StudioPageViewModel`，成本较高；本轮时间不足，**未写**。
  ⇒ 这 4 处修复**目前只有编译保证，没有回归测试固定住**。
- **没有跑真实 App 验证日志里 8 条是否消失**（需要重新启动安装后的应用）。
- `CurrentPage.Image` 那条（`Value is null`）**未处理** —— 它是「图片源为 null」的运行时提示，
  与绑定路径错误不同类，需单独判断是否为缺陷。

## 5. 下一轮必须补的

1. 用 `[AvaloniaFact]` 构造 `StudioHudRingControl` + 桩 VM，断言 `Buttons[i].IsEnabled` 跟随 slot；
   **回退 `{ Source = captured }` 后该测试必须变红**。
2. 重新启动安装后的应用，确认 `startup.log` 里 8 条 `IsEnabled` 与 `ActiveTabLabel` 消失。
## 6. 补完：判别测试已加（E8-STUDIO-BINDING-2，2026-11-15）

上一节 §4 登记"没有判别测试"。**本节更正**：已补。

### 6.1 测试

`tests/NewManga.App.Tests/StudioBindingSourceTests.cs`，`[AvaloniaFact]`：

- 断言 `StudioHudRingControl.Buttons.Count == 8`（与生产日志里恰好 8 条 `IsEnabled` 失败对应）；
- 对**每个** slot：设 `slot.IsEnabled = false` ⇒ 断言 `ButtonFor(action).IsEnabled == false`；
  再设 `true` ⇒ 断言为 `true`。
- **断言方向有讲究**：**禁用方向才有判别力** —— 绑定解析失败时 `Button.IsEnabled` 落回控件默认值（true），
  所以断言 `false` 会红；只断言 `true` 则无论绑定是否生效都通过。

### 6.2 判别力（实测）

把 `StudioHudRingControl.cs:47` 的 `{ Source = captured }` 去掉后重跑：

```
slot ShowTextTier: IsEnabled=false but the button is still enabled (binding did not resolve)
失败! - 失败: 1，通过: 0
```

**变红且消息准确**。已还原（`PROBE` 计数 0）。

### 6.3 回归

无夹具 `App.Tests` 全量：**954 / 0 / 11 / 965**（前值 953 / 0 / 11 / 964 —— **+1 测试，skip 仍 11，0 failed**）。

### 6.4 仍未做（诚实）

- `StudioLeaveModal` 的 `SaveEnabled` **未测**：`LeaveSaveEnabled` 是**派生只读**属性
  （源码里只有 `Raise(nameof(LeaveSaveEnabled))`），要驱动它得模拟完整的"离开确认"状态机，本轮未做。
  ⇒ 那 3 处修复**仍只有编译保证**。
- `StudioInspectorPanel` 的 `ActiveTabLabel` **未测**：需要构造 `StudioInspectorViewModel`，
  本轮未做。⇒ 同样只有编译保证。
- **仍未重跑真实 App** 验证 `startup.log` 里那 9 条是否消失。
