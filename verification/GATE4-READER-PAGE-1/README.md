# GATE4-READER-PAGE-1 证据：reader 页的真实入口

卡面：`doc/tasks/GATE4-READER-PAGE-1.md`。基线 `33712b622`。

## 1. ★ 更正上一轮的错误结论

`GATE4-PAGES-UPGRADE-1` 里我写的是"`--page=reader` 在空库下回落到书架"。**这是错的。**

**真因（代码事实）**：`App.axaml.cs` 的 `SpaceForStartupPage`：

```csharp
private static SpaceId? SpaceForStartupPage(string page) =>
    page.ToLowerInvariant() switch
    {
        "bookshelf" or "library" or "reader" => SpaceId.Library,
        "workbench" or "studio" => SpaceId.Studio,
        "settings" or "console" => SpaceId.Console,
        _ => (SpaceId?)null,
    };
```

**`bookshelf` / `library` / `reader` 三者映射到同一个 `SpaceId.Library`**，
所以 `reader.png` 与 `bookshelf.png` 哈希相同**与库里有没有书无关** —— 是映射本身决定的。
本卡更正，并已同步改 `GATE4-PAGES-UPGRADE-1/README.md` 与 Gate 评估 §18。

## 2. 阅读器是什么（代码事实）

阅读器**不是第四个空间**，而是**独立的沉浸式窗口**：

- `App.axaml.cs:515` 订阅 `shell.ViewModel.ImmersiveReaderRequested` → 创建 `ImmersiveReaderWindow`；
- 该事件只有两个触发点（`V2/Shell/AppShellViewModel.cs`）：
  1. **裸 F11**（无修饰键、无文本焦点、无确认框/命令面板时）；
  2. `ShellCommandIds.LibraryImmersiveReader` 命令。
- 另有普通阅读视图：`ShellCommandIds.LibraryOpenReader` → `Library.OpenReaderAsync()`。

两者都要求**先选中一本书**（Library 空间里点击书籍卡片）。

## 3. 能否无交互到达：**不能**（有实测依据）

`verification/GATE4-READER-PAGE-1/capture-reader.ps1` 的做法：启动到 Library → 轮询等窗口 →
`ShowWindow(SW_RESTORE)` → `SetForegroundWindow` → `keybd_event(VK_F11)` → 等 4 秒 → 找新窗口。

**实测输出**：

```
shell window: handle=1376488 title='New Manga'
foreground=66368 (shell=1376488, match=False)      <-- SetForegroundWindow FAILED
after F11: mainHandle=1376488 title='New Manga'    <-- no new window
NEEDS_INTERACTION
```

**关键证据是 `match=False`**：`SetForegroundWindow` 从**非交互进程**提权前台**失败**
（Windows 的前台锁策略），于是 `keybd_event` 发出的 F11 **没有送进 shell**，
也就不会触发 `ImmersiveReaderRequested`。
**这不是"我没试"，是"试了且能证明为什么不行"。**

**结论**：在"只给命令行参数 + 不注入鼠标点击"的约束下，**阅读器不可达**。
标记为 `NEEDS_INTERACTION`，缺的一步是：**在资料柜里选中一本书**（需要指针点击）。

**为什么不用 `SendInput` 模拟点击**：可以，但点击坐标依赖卡片布局（随窗口尺寸、书籍数量变化），
一旦点偏就会截到别的画面 —— 这正是本卡前一版"截到桌面却以为成功"的同一类风险。
在没有可靠元素定位手段的前提下，**选择不伪造**。

## 4. 有书的资料柜（已目视确认）

`--page=library` + `BOOK-FIXTURE-1/isolated-data` 副本（1 book / 1 chapter / 8 pages）：

- `pages/library-with-books.png`，1416×939，variance 2753.1，50,482 B，sha256 `2c6b8f04f72fa008…`
- **人眼确认**：标题 `New Manga`；面包屑 `资料柜 > BOOK-FIXTURE-1 日漫_JA 测试书 > 第 1 章`；
  书籍卡片 `BOOK-FIXTURE-1 日漫_JA 测试书` / `8 页`；右栏有 **`阅读`** 按钮、
  阅读进度 `读到第 1 / 8 页 13%`、章节账本、8 个页面条目；底栏 `Host 就绪`。

这张图**证明**：①资料柜在有书时能正常渲染；②`阅读` 按钮确实存在于 UI（说明"进入阅读器"是 UI 动作）；
③因此"reader 页"的可达性缺口**只在交互层**，不在渲染层或数据层。

## 5. 隔离与数据保护

- 所有启动 `--data-root=<workspace 隔离目录>`（`...\GATE4-READER-PAGE-1\data`）。
- 用户数据根 `%APPDATA%\com.newmanga.desktop` 清单 SHA-256 在本次全部实验前后均为
  `6ae4d6da17a87b5729cb20ab7f4df6662ddd68079c72b28f2bba62ac1c46d9b2`（实测 `unchanged: True`）。

## 6. 对条件 4 的影响（更正后的口径）

- 四个一级"页面"在 v2 shell 里实际是 **3 个空间**（Library / Studio / Console）+ **沉浸式阅读器窗口**。
- 参数可到达：**书架（=`library`）/ 工作台（=`workbench`）/ 设置（=`settings`）** —— 3/3。
- **阅读器**：需 UI 交互（选中书 → `阅读` 或 F11），**参数方式不可达**，标 `NEEDS_INTERACTION`。
- 因此"四页可达性"应表述为：**三个空间可达 + 阅读器需交互**，**不是**"四页全部可达"。
