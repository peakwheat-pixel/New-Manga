# 条件 3 · F11 真实窗口截图证据（2026-11-17，DSH）

> **2026-11-17 更正**：本文件初版对「右下翻页控件」「四角布局」「空态文案」的描述**与像素不符**，
> 已按独立视觉裁定 `doc/reviews/MAINT-1-GATE-CONDITION-3-VISUAL-ADJUDICATION-2026-11-17.md` 的 D1–D6 逐条更正。
> 以本版为准。

## 这次做了什么

用 **INSTALLER-MATRIX-1 的发布产物**（stage 内 `NewManga.App.exe`，sha256 `a3ec2133b5da3f619b752c818371ba54867b4c150fdba65b8c22d8b17f739230`，99,554,850 B）
在**真实桌面会话**启动（`NEWMANGA`/`--data-root` 指向 `BOOK-FIXTURE-1/isolated-data` 的副本，隔离、不碰真实 `%APPDATA%`），
等 Host 就绪后截图书架页，再发送 `{F11}` 截沉浸阅读器。

- 环境：`query session` → session 1 **Active**；`explorer` 1 个；`[Environment]::UserInteractive=True`。
- OS：**Microsoft Windows 11 专业版 / 10.0.26300.9711**（`(Get-CimInstance Win32_OperatingSystem).Caption` + `cmd /c ver` 实测）；DPI：**96 dpi（100% 缩放）**；PrimaryScreen **2560×1440**，工作区 **2560×1392**（48 px 任务栏）。
- 显示：PrimaryScreen **2560×1440**，工作区 **2560×1392**（**48 px 任务栏**，**100% 缩放**）。
- 截图矩形：`GetWindowRect` = `(-8, -8, 2576×1408)`（最大化窗口含 8 px 不可见边框）。
  ⇒ 图像里上/左各 8 px 黑带、右缘 8 px 桌面像素，**都是截取矩形的几何产物，不是应用边框或阅读器黑边**。

## 证据文件

| 文件 | sha256 | 内容 |
|---|---|---|
| `c3-01-library.png` | `c96f2c9ab1c073f9e1e47cbd6196143fa1b659e08cd600348a36a082801c6f1b` | 书架页：`书架 1/1 作品`、书卡 `BOOK-FIXTURE-1 日漫 JA 测试书`、右侧页列表 `001…008`、状态栏 **Host 就绪** |
| `c3-02-f11-immersive-empty.png` | `108258b9ea37a9f3b752ba77766221b14a8b6fe61305c424ca746bb685829e76` | **F11 沉浸阅读器**（见下「实测像素事实」） |
| `c3-startup.log` / `c3-host.log` / `c3-core_service.stderr.log` | — | 同一次运行的启动 / Host / Core stderr 日志 |

## 实测像素事实（替代初版的描述）

- **全屏 / 无窗口边框（通过）**：书架图里的 `New Manga` 标题栏、页签/工具带、`─ ☐ ✕` 在 F11 图**全部消失**；
  同一 `y=1400–1407` 带在书架图是**任务栏**、在 F11 图是**画布** ⇒ 任务栏被全屏窗口覆盖（正证据）。
- **顶部带控件（通过）**：`返回 (Esc)` x25–83、`阅读` x109–132（**这是 overlay 的 Title 文本，不是控件**）、
  `分页` x2347–2398、`Webtoon 纵向` x2403–2516、`RTL` x2530–2550；右侧余 17 px，**未越界**。
- **底部状态带（本组 c3-01/02 不覆盖；整屏组 c3-04 已覆盖，见下节）**：图像 `y≥1330` 的内容像素为 **0** —— 源码里的翻页/进度是**底部整条状态带**
  （`ReaderOverlay.axaml:100-121`：`上一页`/`下一页`/进度条/保存状态），而本次截取矩形止于屏幕 `y=1399`，
  该带落在**未被截取到的窗口底缘**。⇒ **初版写的「右下翻页控件点」在图上没有像素支持，已删除该说法。**
- **裁切与遮挡（通过）**：画布 `#F4F3F0` 占 **98.939%**；非背景像素仅 **4,936 px（0.138%）**；无黑边、无遮罩、无整幅浮层遮挡。
- **可读性（通过）**：1:1 原生像素（ClearType 彩边可证未缩放）；CJK 字形 11–12 px ⇒ 字号约 13–14 px；对比度约 **15:1**。
  **可辨但字号偏小。**
- **空态文案（逐字，与源码/二进制一致）**：`▲ 阻塞` / `页图不可用：Host 资源通道未接入或该页没有图像（不伪造图片）` / `—`
  （初版写成「页面不可用…未输入该页」，**已按实拍更正**）。

## 能证明什么 / 不能证明什么

**能证明**：发布产物可在真实桌面会话启动到 Host 就绪；F11 进入**全屏无边框**沉浸 overlay；**顶部带**控件完整可见、未越界；
画面无黑边/无遮挡；空数据时给出**诚实的空态**、不伪造图片。

**不能证明（不得用本证据冒充）**：
1. **底部状态带**（`上一页`/`下一页`/进度/保存状态）—— 未被截取，需按**全屏窗口矩形**重截（含窗口底缘）；
2. **内容渲染** —— 本次未选中任何页面，页面图像、分页 vs Webtoon 排版、缩放与内容裁切**零证据**；
3. 窗口与物理屏边界的严格重合（截图止于 `y=1399`）；
4. IME、气泡/题注、SFX 等 overlay 次级功能；
5. 单机单次观察，**不是矩阵**。

## 结论

**条件 3 的「F11 全屏/无边框视觉」由三份独立书面视觉裁定确认关闭**（`PARTIAL_PASS_FOR_OVERLAY_CHROME` / `PARTIAL_PASS_PLUS_BOTTOM_BAND` / `CONTENT_RENDERING_COVERED`）；**这不是人眼验证**。

仍未覆盖（不得外推）：**分页模式排版**（实测当前是 Webtoon 纵向）、Webtoon 实际滚动/整页可达、缩放/DPI、进度非 0% 态、实际翻页与禁用/焦点态、保存状态机其余取值、次级 overlay、可访问性、环境矩阵。

**外观一致性缺陷（不影响上述结论，已单独立卡）**：`READER-F11-STYLE-SCOPE-1`（D9）。

## 2026-11-17 补充取证：整屏重截（覆盖此前缺的窗口底缘）

按独立裁定 D1/D2 的建议，改用 **PrimaryScreen 整屏矩形（2560×1440）** 重截，而不是 `GetWindowRect`：

| 文件 | sha256 | 内容 |
|---|---|---|
| `c3-03-library-fullscreen.png` | `ef60d9ffc53c2820dcf55d328e2b9f67d26b301d4c7c5285ecc6bdb96d591c66` | 整屏书架页（含任务栏区域，窗口最大化） |
| `c3-04-f11-immersive-fullscreen.png` | `2183198b8daba875208c92efbbcfdca68374ab398f45a8c300115b072ee3d384` | **整屏 F11 沉浸阅读器（含窗口底缘）**：底部可见 `上一页` / `下一页`（左下）与进度/保存状态（右下）；顶部仍是 `返回 (Esc)` / `阅读` / `分页` / `Webtoon 纵向` / `RTL`；中央仍是空态「页图不可用…（不伪造图片）」 |

**这补上了此前「底部状态带未被截取」的缺口**：`上一页`/`下一页` 与右下进度/保存状态确实存在且完整可见，
此前「右下翻页控件点」的错误描述由本组证据正式替代。内容渲染（选中页面后的画面）**仍未覆盖**。

补充裁定见 `doc/reviews/MAINT-1-GATE-CONDITION-3-VISUAL-ADJUDICATION-2026-11-17.md` 的「补充裁定」节。

> **OS 记录更正（2026-11-17，reviewer-c3 F-1）**：初版写 `Windows 10 Pro / 2009 / build 26300` 是读了注册表遗留字段（`ProductName`/`ReleaseId`）。实测应为 **Windows 11 专业版 / 10.0.26300.9711**。以本次更正为准。

### 原始未压缩 PNG 的 sha256（仓外保留，不提交二进制大文件）

| 仓内 JPEG | 仓外原图 | 原图 sha256 |
|---|---|---|
| `c3-01-library.png`（原样） | `..\tmp\r20\f11c\01-library.png` | `c96f2c9ab1c073f9e1e47cbd6196143fa1b659e08cd600348a36a082801c6f1b` |
| `c3-02-f11-immersive-empty.png`（原样） | `..\tmp\r20\f11c\03-f11-reader.png` | `108258b9ea37a9f3b752ba77766221b14a8b6fe61305c424ca746bb685829e76` |
| `c3-03-library-fullscreen.png`（原样） | `..\tmp\r20\f11e\01-library-fullscreen.png` | `ef60d9ffc53c2820dcf55d328e2b9f67d26b301d4c7c5285ecc6bdb96d591c66` |
| `c3-04-f11-immersive-fullscreen.png`（原样） | `..\tmp\r20\f11e\02-f11-immersive-fullscreen.png` | `2183198b8daba875208c92efbbcfdca68374ab398f45a8c300115b072ee3d384` |
| `c3-05-reader-open-content.jpg`（q90） | `..\tmp\r22\f11c\01-reader-open.png` | `e34b8e81b37bbe003b305417ecf56eb74cd3e37a698ff8a0ff6144ef2ace760b` |
| `c3-06-f11-immersive-content.jpg`（q90） | `..\tmp\r22\f11c\02-f11.png` | `538d4891fd5cbf00731faffed2d89e1a5415926bb1b7524f2b029f3e098ed549` |

### 补充裁定要点（visual-c3b，2026-11-17）

- 底部带实测（原生像素）：`上一页` x17..52 / `下一页` x75..110 / 进度条轨道 x128..2456（**0% 填充**）/ 进度文本 `—` / 保存状态 `进度：未保存`（x2486..2551）；
  左 17 px、右 8 px、下留 16 行边距 ⇒ **未越界、未被裁切**。
- 上下两带互不遮挡：顶带 ink 止于 y40、底带起于 y1413，相隔 **1,372 行**。
- 整屏覆盖：2560×1440 **等于** PrimaryScreen 边界；四角全为画布色；任务栏在 F11 图 91.9% 为纯画布 ⇒ 被全屏窗口覆盖。
- 与上一组一致性：F11 重叠区 **0 / 3,584,000 px 差异**（逐像素相同）。
- **仍不覆盖**：内容渲染、进度条非零态、`上一页`/`下一页` 交互与禁用/焦点态、保存状态机其余取值、窗口与物理屏边界严格重合、任务栏色调差异成因、交互/次级 overlay/可访问性。

## 2026-11-17 第三次取证：内容渲染（关闭最后的「不覆盖」）

**关键发现（决定取证方式）**：F11 只是把**已经打开的**阅读器 VM 挂到无边框全屏窗口（`App.axaml.cs` 的 `WireImmersiveReader`
直接 `new ImmersiveReaderWindow(shell.ViewModel.Library.Reader)`，**不调用 `OpenAsync`**）。
所以「只按 F11」拿到的是**空态**（`Pages.Count==0`）；必须先 `阅读`（`LibraryViewModel.OpenReaderCommand` → `Reader.OpenAsync(book, chapter, page)`）。

**本次做法**：用 **UI Automation**（不是盲点坐标）按名称精确操作：
1. 启动发布产物（`--data-root` 指向隔离副本）；
2. `InvokePattern.Invoke()` 名为 **`阅读`** 的 Button（BookDetailPanel 的 primary 按钮，rect 约 2214,179）；
3. 等 8 s → 整屏截图（阅读器在**主窗口内**，有内容）；
4. 发 `{F11}` → 等 8 s → 整屏截图（**沉浸全屏 + 内容**）。

> 备注：此前 4 次失败都是**没有先打开阅读器**（盲点坐标 / 只 Invoke 页行都不够）。全屏 2560×1440。

| 文件 | sha256 | 说明 |
|---|---|---|
| `c3-05-reader-open-content.jpg` | `ba7b39fcae4cb634e18e4218f1dad5d4f190a41ece7cebe8cfd3ce7c65cfba6d` | 阅读器在主窗口内、**有页面图像**（JPEG q90；原 PNG 6,089,406 B 在 workspace 保留） |
| `c3-06-f11-immersive-content.jpg` | `8ce0fc0a1a0c8cfc88b4179105da5083e4486fc0253190946635c749dae15535` | **F11 沉浸全屏 + 有内容**：左上 `返回 (Esc)` + 面包屑 `BOOK-FIXTURE-1 日漫_JA 测试书 / 第 1 章`；右上 `分页`/`Webtoon 纵向`/`RTL`；底部 `上一页`/`下一页`；右下 **`第 1 / 8 页 · 0%`** 与 **`进度：续读到第 1 页（Core 已保存）`**（JPEG q90；原 PNG 6,630,224 B 在 workspace 保留） |

**这一组补上了此前的「内容渲染不覆盖」**：page 图像真实渲染（《Pepper & Carrot》日文版第 1 页）、分页模式布局、进度/保存状态文本均有像素证据。
仍未覆盖：Webtoon 纵向模式的实际排版、缩放/DPI 变化、进度条**非 0%** 态、`上一页/下一页` 的实际翻页与禁用态、次级 overlay（气泡/题注/SFX）。

### 第三次裁定（`visual-c3c`，`CONTENT_RENDERING_COVERED`）与三处更正

- **D7｜底部文案**：实拍是 `第 1 / 8 页 · 0%` + `进度：续读到第 1 页（Core 已保存）`。
  本文件上一版写的 `读完即存（Core 已挂载）` **不是实拍内容**（该串在发布 exe 中出现 0 次）——已在上表更正。
- **D8｜当前是 Webtoon 纵向模式，不是分页模式**：`Webtoon 纵向` chip 为 Accent 高亮，布局为 fit-width + 8 px raised 卡内边距；
  ⇒ **「分页模式布局」其实未被覆盖**（此前表述有误）。页面可见高度约 **38.2%**（2,542 px 宽 × 3,516 px 高的页在 y=1397 被视口截断）。
- **D9｜F11 沉浸窗丢失 shell 局部样式作用域（真实视觉缺陷，已单独立卡）**：
  `V2LocalStyles` 只在 `AppShellV2.axaml` 引入，`ImmersiveReaderWindow` 未引入 ⇒ 顶/底带由**白色变画布底色**、模式 chip **失去选中高亮**。
  这是「同页同态、外壳不一致」的可复现差异（两帧页面重叠区 **2,296,160 px 差异 0**，差异只在外壳）。
- 页面内容真实渲染已由像素比对确认：与 fixture page 1 缩放 2.1183× 后 **MAD 1.88、>30 差异 0.06%**（非占位图、非镜像）。

**仍不覆盖**（该裁定 T5）：分页模式排版、Webtoon 实际滚动与整页可达、缩放/DPI、进度非 0% 态、实际翻页与禁用/焦点/hover 态、
保存状态机其余取值、次级 overlay、加载/错误横幅、可访问性、窗口与物理屏边界严格重合、环境矩阵（深色主题/多分辨率/HiDPI）。
