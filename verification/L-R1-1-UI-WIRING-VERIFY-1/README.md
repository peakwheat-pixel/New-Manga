# L-R1-1-UI-WIRING-VERIFY-1：控件**确实接线了** —— 但我为此连错了两次

基线 `23b361c7b`。本卡核实 `L-R1-1` / `L-R2-1` 的四项控件是否真的接线。
**结论：全部接线。但我得出结论的过程犯了两次方法错误。**

## 1. 结论（先行）

`apps/desktop-avalonia/src/NewManga.App/Views/Fluent/ReaderPageView.cs`（**737 行**）
以 **C# 代码构建** Reader UI，四项控件**全部存在并绑定**：

| L-R1-1 的四项 | 代码证据 |
|---|---|
| **书签面板** | `:279` `FluentUi.Button("书签", ..., ToggleBookmarkPanel, "书签")`；`:291` `"添加当前页书签"`；`:295` `"关闭书签面板"`；`:338` `"删除"`；`:60` `Border _bookmarkPanelHost`；`:152` `_bookmarkPanelHost = BuildBookmarkPanel()` |
| **整书进度** | `:414` `"上一页"` → `_viewModel.PreviousAsync()`；`:419` `"下一页"` → `_viewModel.NextAsync()`；`:616` 页码跳转 `JumpToPageAsync(index)` |
| **reset 确认** | `:424` `"重置进度"`；`:153` `"确认重置进度"` → `ConfirmResetAsync()`；`:154` `"取消"` → `HideResetConfirm` |
| **偏好应用** | `:275` `"单页 / 双页"` → `ToggleDoublePagePersistingAsync()`；`:276` `"反向翻页"` → `ToggleDirectionPersistingAsync()`；`:393-395` 缩放 → `ZoomByPersistingAsync()` / `ResetZoomPersistingAsync()` |

**⇒ `L-R1-1` / `L-R2-1` 的"可见控件未接线"已不成立；它们被 `ReaderPageView.cs` 补上了。**

## 2. ★ 我为此犯的两次方法错误（原样登记）

### 2.1 第一次：只搜 XAML，错误断言"控件不存在"

我先搜了**全部 `.axaml`**：

```
书签 → 0 命中
偏好 → 0 命中
重置 → 只有 ImportDockView.axaml（源授权，不是阅读器）
进度 → 只有 ConsoleView.axaml / BookDetailPanel.axaml（且是文案）
```

又读了 `ReaderOverlay.axaml`（123 行），确认它只有 7 个 Command
（`CloseCommand` / `ToggleLayoutCommand`×2 / `ToggleDirectionCommand` / `RetryCommand` / `PreviousPageCommand` / `NextPageCommand`），
**没有**书签/进度/reset/偏好。

**于是我断言"阅读器这四项控件在 XAML 里不存在"并宣布"L-R1-1/L-R2-1 确实没接线"。**

**这是错的**：**Reader UI 不在 XAML 里，而是在 C# 里用代码构建**（`ReaderPageView.cs`）。
**我用了错误的搜索范围，却给出了确定性结论。**

### 2.2 第二次：搜 C# 后推翻自己

搜 `BookmarkPanel` / `ReadingProgress` / `ResetConfirm` 拿到命中后，我才定位到 `ReaderPageView.cs`，
发现**控件全在**。

**⇒ 我在同一轮里先给出错误结论、再自己推翻它。**

## 3. 这次错误的性质与之前几次不同

| # | 项 | 错误类型 |
|---|---|---|
| 1 | `L-F1-3` | 没读裁决原文 |
| 2 | `E-9` | 没读 `RegisterRoot` 实现 |
| 3 | `yolo11s-seg.onnx` | 搜索范围不完整（只搜索引，漏 gitignore） |
| 4 | 签名 | 没查 SignPath 路径 |
| 5 | `reader` 入口 | 没读命令/事件链 |
| 6 | `INSTALLER-MATRIX-1` | 没查实物证据目录就改状态 |
| **7** | **L-R1-1/L-R2-1** | **搜索范围不完整（只搜 XAML，漏 C# 构建的 UI）** |

**⇒ 第 3 次与第 7 次是同一类**：**`*.axaml` 之于 C# 构建的 UI，正如 `git grep` 之于 gitignore 的文件** ——
**"我以为搜索覆盖了全部"，其实只覆盖了会让我看到"不存在"的那一半。**

## 4. 这次错误为什么危险

**我差一点就用它去改 STATUS。**

我当时的下一步是"若静态显示没接线，那就是真缺陷"，准备把条件 1 的 8/8 打成虚报。
**如果我没有多搜一次 C#，我会把一个正确完成的功能登记成缺陷，并可能触发一次不必要的返工。**

**⇒ 结论：在宣布"某某不存在"之前，必须先确认搜索范围覆盖了所有可能的实现形式（XAML / C# 代码构建 / 其他）。**

## 5. 未做

- 未**运行** UI 测试验证这些控件的真实可见性（`F11HotkeyTests` 等是 headless 的，与本卡的静态核实互补）。
- 未核实 `FEA-14-READ-2` 的 limitation 是否已被后来的某张卡正式关闭（本卡只证明"代码里有控件"，
  不证明"那张 limitation 卡被走完流程关闭"）。
