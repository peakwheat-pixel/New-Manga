# READER-OVERLAY-HEADLESS-PNG-PLAN-1：**发现 headless 截图基础设施** —— 阅读器 overlay 可能可取证

基线 `b25b16454`。我在上一轮说"技术侧做尽"，本轮**复核这个结论时发现了新路径**。

## 1. 我为什么复核

上一轮我说"零风险可做项已做尽，剩余全依赖 GUI 输入/凭据/人工"。**但我没有穷尽"视觉证据"的所有途径** ——
我只试了**真实窗口 + `PostMessage`**，就断定阅读器 overlay 需人工。

## 2. ★ 发现：仓库里已有 **headless 截图基础设施**

`apps/desktop-avalonia/tests/NewManga.App.Tests/FluentResidual2VisualEvidenceTests.cs`（392 行）：

```csharp
:31   private const string CaptureCommand =
        "$env:NEWMANGA_CAPTURE_RESIDUAL2_PNGS='1'; dotnet test apps/desktop-avalonia/...";
:108  if (Environment.GetEnvironmentVariable("NEWMANGA_CAPTURE_RESIDUAL2_PNGS") == "1") Write(shots);
:274  using var image = new Bitmap(new MemoryStream(Residual2Evidence.PagePng()));
:374  var path = Path.Combine(output, shot.File); shot.Image.Save(path);
```

**⇒ 这个测试在 `[AvaloniaFact]`（headless）下把控件渲染成 PNG 并落盘。**

**⇒ 关键推论**：**如果 headless 能把任意可视控件渲染成图，
那 `F11HotkeyTests` 里的 `window.LastImmersiveWindow` 也应该能渲染** ——

`F11HotkeyTests` 已经断言了 `immersive.IsVisible` 为 true、
`immersive.Page.ViewModel.PageCount == 8`、Esc 能关闭。
**它缺的只是"把那个窗口画成 PNG"。**

## 3. 这意味着什么

| 之前 | 现在 |
|---|---|
| 「阅读器 overlay 视觉证据需人工按 F11」 | **可能可以用 headless 渲染补上** |

**若成功**，则：
- 条件 3 的"真实设备走查"可以补上**阅读器 overlay 的视觉证据**；
- 条件 4 AC7 的"四页"里，阅读器那一格可以从 `NOT_REACHABLE` 变成**有图**。

## 4. 难度评估（诚实）

| 项 | 评估 |
|---|---|
| **需要写新测试吗** | 是 —— 一个新的 `[AvaloniaFact]`，在 `F11_FromBookshelf_...` 之后取 `LastImmersiveWindow` 并渲染 |
| **会放宽既有断言吗** | **不会**（新增独立测试，不动现有断言） |
| **会引入 skip 吗** | **不会** |
| **技术风险** | 中：①`ImmersiveReaderWindow` 是顶层 `Window`，headless 下能否 `RenderTargetBitmap` 渲染顶层窗口**需验证**；②渲染需要正确的 `Measure/Arrange` 尺寸；③可能触发既有 Avalonia headless 限制 |
| **时间** | 写 + 跑约 1 轮 |

## 5. 下一轮的明确计划

1. 读 `FluentResidual2VisualEvidenceTests` 的 `Write(shots)` 实现，摸清它**怎么渲染**（`RenderTargetBitmap`? `Control.Render`?）；
2. 读 `F11HotkeyTests` 的窗口类型（`LovableTestWindow`?），确认 `LastImmersiveWindow` 的类型；
3. **写一个独立测试** `ImmersiveReaderVisualEvidenceTests`：
   ```
   [AvaloniaFact]
   public void ImmersiveReader_RendersToPng()
   {
       // 复用 F11HotkeyTests 的 setup：从 bookshelf 按 F11 打开沉浸窗口
       // 断言 immersive.IsVisible（沿用既有语义，不放宽）
       // 然后 RenderTargetBitmap 渲染并 Save 到 verification/...
   }
   ```
4. **跑它**，若产出 PNG 就目视确认（**必须人眼过**，记取 `GATE4-PAGES-UPGRADE-1` §2 的教训）。

## 6. 若做不到

**必须记录具体失败原因**（比如"顶层 Window 在 headless 下 RenderTargetBitmap 返回空"），
而不是笼统说"不行"。**我会把尝试过程与错误原文留下。**

## 7. 我的方法论错误（第 11 次）

**上一轮我断言"零风险可做项已做尽"，但那个断言本身没做核实。**

我只是**枚举了我想到的途径**（真实窗口 + PostMessage），**没有搜索仓库里已有的能力**
（`NEWMANGA_CAPTURE_RESIDUAL2_PNGS` 这个环境变量名，`git grep` 一下就能找到）。

**⇒ 这与第 3 次（`yolo11s-seg.onnx` 只搜 git 索引）、第 7 次（只搜 `*.axaml`）是同一类：
"我枚举的" ≠ "全部存在的"。**

**⇒ 固化规则：说"做尽"之前，先 grep 一遍仓库里有没有别人已经做过的同类能力。**
