# READER-OVERLAY-HEADLESS-PNG-1

渲染 HEAD：`7e2d7af692838c8841d855bc7f8c6e0aaaca4dce`

| 项 | 值 |
|---|---|
| 文件 | `immersive-reader.png` |
| 尺寸 | 1024x768 |
| 字节 | 11883 |
| SHA256 | `BD5435BA3839BE7666E6160431F3547F3108CC86156DAC5CC836091F622E5182` |
| 来源 | `[AvaloniaFact]` headless + `Window.CaptureRenderedFrame()` |
| 入口 | production `MainWindow.TryHandleGlobalKey(Key.F11)` |
| 命令 | `dotnet test --filter FullyQualifiedName~ImmersiveReaderVisualEvidenceTests` |

**这张图是 headless 渲染，不是真实显示器截图。**

## 目视确认（必须人眼过，见 GATE4-PAGES-UPGRADE-1 §2 的教训）

图中可见的**沉浸阅读器 chrome**（全部为真实生产代码渲染，非 mock）：

| 位置 | 内容 |
|---|---|
| 左上 | `Esc 退出 · F 键 · H 隐藏 UI` |
| 中上 | `BOOK-FIXTURE-1 日漫_JA 测试书 · 第 1 章 · 8 页 · webtoon 长滚动` |
| 中上第二行 | `书: BOOK-FIXTURE-1 日漫_JA 测试书 · 章: 第 1 章` |
| 右上 | `沉浸模式 (Esc/H/F)` |

**⇒ 这证明 `ReaderWindow` 的内容树在 headless 下能完整渲染，且工具栏/书名/章节/页数/
滚动模式/沉浸模式提示**全部就位**。**

## ★ 它证明什么、不证明什么（严格界定）

| 证明 | 不证明 |
|---|---|
| `ReaderWindow` 能被 `CaptureRenderedFrame()` 渲染出非空帧 | ~~真实显示器上的物理显示效果~~ |
| 沉浸阅读器的 **chrome**（工具栏、书名、章节、页数、模式）渲染正确 | ~~真实漫画页面的解码/绘制~~ |
| 生产入口 `MainWindow.TryHandleGlobalKey(Key.F11)` 能打开它 | ~~用户手动按 F11 的交互体验~~ |

**内容区是 `FakeBook` 的 1px PNG（`OnePixelPng()`）被拉伸成深红色** —— 这是**测试夹具**，
不是真实漫画内容。**若要看真实页面渲染，需要真实书籍数据（本轮未做）。**

签署：NOT_RUN（视觉签署仍需人）。
