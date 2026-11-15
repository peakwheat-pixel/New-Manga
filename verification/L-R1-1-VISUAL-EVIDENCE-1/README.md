# L-R1-1-VISUAL-EVIDENCE-1：四项控件的**视觉证据**（headless 渲染，一个环境变量就产出了）

基线 `1242d8d87`。

## 1. 怎么产出的（比我预想的简单得多）

上一轮我还在计划"写新测试渲染书签面板"，本轮 grep 后发现 **`FluentPageTests.cs:286` 已经支持**：

```
NEWMANGA_CAPTURE_FLUENT_PNGS=1
```

**一条命令**：

```powershell
$env:NEWMANGA_CAPTURE_FLUENT_PNGS="1"
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj `
  --filter "FullyQualifiedName~FluentPageTests"
```

**结果**：`10 passed / 0 failed / 0 skipped / 1 s`，产出 `verification/FEA-06-RESIDUAL-1/png/`：

| 文件 | 字节 |
|---|---|
| `shelf.png` | 82 KB |
| `workbench.png` | 31 KB |
| **`reader.png`** | **34 KB**（1180×780，sha256 `ce5a79c2fcb4…`） |
| `settings.png` | 52 KB |

## 2. ★ 目视确认 `reader.png` —— **L-R1-1 四项控件全部可见**

图里是完整的 **`ReaderPageView`**（不是沉浸 overlay，是工作台内的阅读器页面）：

| 区域 | 可见控件 |
|---|---|
| **顶部工具栏** | `返回` · `阅读器` · **`单页 / 双页`** · **`反向翻页`** · `全屏` · **`书签`** |
| **左侧浮动工具条** | **`放大`** · **`缩小`** · **`适合页面`** · `反向翻页` · `全屏` · `隐藏浮动工具条` |
| **底部操作栏** | `上一页` · `下一页` · **`缩小`** · **`放大`** · **`适合页面`** · **`重置进度`** |
| **内容区** | `本章节暂无页面` / `返回书架选择其他章节` / `返回` 按钮 |
| **状态栏** | 左下 `Fluent · builtin.fluent · 阅读器 · Medium`；右下 `Medium · 1024–1279` |

### 对应 `L-R1-1` 的四项

| L-R1-1 的项 | 图里的控件 | 同时有测试 |
|---|---|---|
| **书签面板** | 顶部 **`书签`** 按钮 | `ReaderVisibleControlsTests:58` |
| **整书进度** | 底部 **`上一页` / `下一页`** | `ReaderVisibleControlsTests:30/:44` |
| **reset 确认** | 底部 **`重置进度`** | `ReaderVisibleControlsTests:95` |
| **偏好应用** | **`单页 / 双页`** · **`反向翻页`** · **`放大`/`缩小`/`适合页面`** | `ReaderPreferencePersistenceTests:49` |

**⇒ 四项**全部**同时**有：源码（`ReaderPageView.cs`）+ 行为测试（`ReaderVisibleControlsTests`）+ **视觉证据（本图）**。

## 3. ★ 它证明什么、不证明什么

| 证明 | 不证明 |
|---|---|
| `ReaderPageView` 的工具栏/浮动条/底部操作栏在 headless 下渲染完整 | ~~真实显示器上的像素级外观~~ |
| 四项控件的**按钮存在且可见**（不是"代码里有但没显示"） | ~~点击后的真实交互体验~~（那由测试覆盖） |
| 四页结构（shelf/workbench/reader/settings）各有独立截图 | ~~真实书籍内容的渲染~~（图里是"本章节暂无页面"） |

**内容区是 `本章节暂无页面`** —— 因为 `FluentPageTests` 的夹具没有真实书页。**这不是缺陷**，是夹具限制。

## 4. ★ 我的方法论错误（第 12 次）

**上一轮我还在"计划写新测试渲染书签面板"。**

**而 `NEWMANGA_CAPTURE_FLUENT_PNGS=1` 一条命令就能产出四页图** —— 它**一直在那里**。

**⇒ 与第 11 次（`CaptureRenderedFrame`）、第 7 次（`*.axaml`）、第 3 次（git 索引）同源：
我反复在"自己从头推理"，而不是"先 grep 仓库里已有的能力"。**

**⇒ 这已经是第 4 次同类错误（3/7/11/12）。**

**⇒ 我把它升级为硬规则：任何"要写新东西"的念头出现时，先花 30 秒 grep 环境变量名、测试类名、关键 API。**
