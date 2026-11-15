# GATE3-READER-OVERLAY-1：尝试用 `PostMessage` 发 F11 触发沉浸阅读器 —— **未成功**

基线 `6b0c6c05e`。承接"GUI 已能启动"的突破，尝试**不靠物理按键**打开阅读器 overlay。

## 1. 依据

- `ShellCommands.cs:37` `LibraryImmersiveReader = "library.reader.immersive"`；
- `AppShellViewModel.cs:1188-1190` 处理为 `ImmersiveReaderRequested?.Invoke(...)`；
- `App.axaml.cs:512-534` 订阅并**惰性创建** `ImmersiveReaderWindow`；
- 裸 F11 经 `MainWindow.TryHandleGlobalKey` 到达上述命令。

**假设**：向主窗口 `PostMessage(WM_KEYDOWN/WM_KEYUP, VK_F11)` 应能触发同一条链。

## 2. 实测

```
handle=2034366 title='New Manga'
before_post: title='New Manga'
post_down=True post_up=True          ← PostMessage 调用本身成功
after_post: handle=2034366 title='New Manga'   ← 但窗口没有变化
```

**⇒ 失败**：`PostMessage` 返回 True，但窗口的 handle 与 title 均未变化。

## 3. 为什么可能失败（分析，未验证）

1. **`PostMessage` 把消息投递到窗口的消息队列，但 Avalonia 的键盘输入可能走
   `WM_INPUT` / Raw Input 或需要 `WM_SYSKEYDOWN`**，而非同步的 `WM_KEYDOWN` 投递；
2. **需要窗口处于前台/有键盘焦点** —— 本环境 `SetForegroundWindow` 结果未验证成功
   （前一次探测里 `foreground_matches=False`）；
3. **沉浸窗口可能是新的顶层窗口**，`MainWindowHandle` 不变是预期的；
   **但我没有枚举到新窗口**（`EnumWindows` 在本环境对该进程返回 **0 个可见窗口**，
   说明枚举本身受限，可能也有真正的新窗口但看不见）。

## 4. 我放弃了什么、为什么

- **尝试过**：写了一个完整的探测脚本（`tools/e2e/probe-reader-overlay.ps1`），
  含 `EnumWindows`、`PostMessage`、`PrintWindow` 截图；
- **失败原因之一是我的脚本改坏了**（两次 Python 字符串续行错误），**已删除那个脚本**；
- **最终用 inline 命令跑通了 `PostMessage` 部分**，确认"消息能发出、窗口无反应"。

**⇒ 结论：`PostMessage(WM_KEYDOWN, VK_F11)` 不足以触发沉浸阅读器。**
至少在本环境、这种投递方式下不行。**我没有继续尝试 Raw Input / 模拟真实键盘钩子**
（那会更接近"伪造输入"，且在无交互桌面下更可能失败）。

## 5. 因此

**阅读器 overlay 的真实截图仍未取得。**
条件 3 / 条件 4 AC7 的"阅读器页"仍只能依赖：
- `F11HotkeyTests`(9) + `V2ImmersiveReaderTests`(4) 的 headless 覆盖（**驱动生产 public 方法**）；
- **但不含真实窗口的视觉证据**。

**⇒ 这一项仍需人工按一次 F11。我试了，没成功，如实登记。**

## 6. 顺带说明：本卡没有产出任何截图

`verification/GATE3-READER-OVERLAY-1/` 下只有 `overlay-probe.txt`（探测日志）与本说明。
**没有 PNG** —— 因为窗口没有变成阅读器，截出来的只会是资料柜。
