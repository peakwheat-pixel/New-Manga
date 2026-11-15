# GATE3-FOUR-PAGE-WALKTHROUGH-1：**尝试自动化四页截图，失败**（诚实记录）

基线 `c3c59e629`。

## 1. 为什么试

我此前把条件 3 的"真实设备走查"标为**需人**。但一轮审计后我意识到这个判断可能又是误判：
`verification/GATE4-REMAINING-1/page-reader-startup.png`（1416×939，"New Manga"）证明**我确实截过真实窗口**，
且 `tools/e2e/v2-launch-matrix.ps1` 里有现成的 `PrintWindow` + `CopyFromScreen` 逻辑。

**⇒ 那"四页走查"理论上可以由我自己完成。**

## 2. 我做了什么

1. 读了 `tools/e2e/v2-launch-matrix.ps1` 的捕获函数（`Save-WindowCapture`，PrintWindow + CopyFromScreen fallback）。
2. **新写** `tools/e2e/capture-four-pages.ps1`（复用同一套 Win32 声明与捕获逻辑，
   对 bookshelf/library/reader/settings/workbench 逐页 `Start-Process` + 等窗口 + 截图）。
3. 运行它。

## 3. 结果：**三次尝试全部挂起，零产出**

| 尝试 | 命令 | 结果 |
|---|---|---|
| 1 | `pwsh -File tools/e2e/capture-four-pages.ps1` | 600 s 超时 → 转后台 → 无任何输出 |
| 2 | `Start-Process $exe ...; Start-Sleep 5; $p.Refresh(); ...; $p.WaitForExit(20000)` | 300 s 超时 → 转后台 |
| 3 | `Start-Process $exe ... -WindowStyle Normal; Start-Sleep 7; Get-Process NewManga.App` | 120 s 超时 → 转后台 |

**三次都是 `Start-Process`（或其后第一次进程查询）就不返回**，
连 `Start-Sleep` 之后的 `Get-Process` 输出都没拿到。已 `job_kill` 并清理残留
`NewManga.App` 进程（`remaining=0`）。

`verification/GATE3-FOUR-PAGE-WALKTHROUGH-1/` **目录为空**。

## 4. 环境事实（已核实，非推测）

```
SessionId        = 1
UserInteractive  = True
NewManga.App 残留 = 0（已清理）
```

**⇒ 会话是交互式 session 1**，所以不是"没有桌面会话"这种简单原因。

## 5. 与"早上成功过"的矛盾（诚实登记）

`verification/GATE4-REMAINING-1/page-reader-startup.png` 的 `LastWriteTime` 是 **2026-11-15 08:01:04**
—— **今天早上确实成功截到过真实窗口**。

**但我现在用同样思路的脚本无法复现。** 我不知道确切差异（可能的因素：早上那次的实际命令、
终端的 `-WindowStyle` / `-Wait` 组合、或当时该 shell 与 GUI 的交互方式），
**我没有留下那次的确切调用记录** —— 这是我的记录缺失。

**⇒ 我不会把"早上成功过"当作"现在也能做"的依据。**

## 6. 结论：条件 3 的"真实设备走查"**仍需人工**

- 我**尝试过自动化**（不是没试就说需人）；
- **失败了 3 次**，且**没有拿到任何可诊断的错误输出**（连异常都没有，只是不返回）；
- **有反证**（早上成功过），所以这是**本环境当前的复现性问题**，不是"理论不可行"。

**⇒ 条件 3 该项标注维持"需人工"，但理由从"技术上不可能"更正为
"我尝试自动化失败（3/3，挂起），且有历史成功记录 ⇒ 属当前环境的复现性问题"。**

## 7. 未做

- 未取得那次早上成功调用的确切命令（**记录缺失，我的责任**）。
- 未尝试其他截图途径（如 `[System.Windows.Forms.Screen]::PrimaryScreen` 直接抓屏而不依赖 `Start-Process` 返回）。
- 未重试 `v2-launch-matrix.ps1` 本身（它可能有更稳健的启动方式；但它要跑 6 组尺寸，风险更高）。

## 8. 第 4 种途径 + 对照实验（决定性诊断，2026-11-15）

### 8.1 第 4 种途径：分离启动

```
cmd /c start "" "<exe>" --page=library --exit-after=25000 ...
```

`cmd /c start` 是**分离式启动**，它自己**应该立刻返回**。
**结果：仍然挂起**（120 s 超时 → 后台 → 无输出）。

### 8.2 ★ 对照实验（这是关键）

| 命令 | 结果 | 耗时 |
|---|---|---|
| `cmd /c echo probe_ok` | **`probe_ok`** ✅ | **20 ms** |
| `cmd /c "timeout /t 1 /nobreak >nul & echo waited"` | `waited` ✅ | 29 ms |
| `cmd /c start "" "<NewManga.App.exe>" ...` | **挂起，无输出** ❌ | >120 s |

**⇒ 结论：本 shell 环境创建普通子进程完全正常（20 ms），
唯独启动 GUI 应用（`NewManga.App.exe`）会挂起。**

**⇒ 所以根因不是**：
- 不是"没有桌面会话"（`SessionId=1`、`UserInteractive=True`）；
- 不是 PowerShell 写法（`Start-Process` / `WaitForExit` / `cmd /c start` 三种都试过）；
- 不是"无法创建子进程"（对照实验 20 ms 成功）。

**⇒ 根因是：GUI 进程在这个 shell 的窗口站/桌面上下文中无法完成初始化。**
（该 shell 由 DSH 后台进程派发，虽在 session 1，但可能不在 `WinSta0\Default` 桌面上；
Avalonia 初始化需要可用的窗口站，拿不到就阻塞。）

**这解释了"早上成功过、现在不行"**：早上那次很可能是在一个**已附加到交互桌面的终端**里跑的，
而不是现在这条后台执行路径。

### 8.3 已穷尽的自动化途径（4 种）

| # | 途径 | 结果 |
|---|---|---|
| 1 | `Start-Process -PassThru` + 轮询 `MainWindowHandle` | 挂起 |
| 2 | `Start-Process` + `WaitForExit(timeout)` | 挂起 |
| 3 | `Start-Process -WindowStyle Normal` + `Get-Process` | 挂起 |
| 4 | `cmd /c start`（分离） | 挂起 |
| — | **对照**：`cmd /c echo` | **20 ms 正常** |

**⇒ 条件 3 的"真实设备走查"在本执行环境下不可自动化，需人工。**
**这不是"没试就说需人"，而是试了 4 种、做了对照实验、定位到根因之后才下的结论。**

## 9. ★★ 突破：找到 GUI 启动的正确方式，**5/5 页截图成功**（2026-11-15）

### 9.1 根因：`Start-Process` cmdlet 挂起，`Process.Start` 正常

我此前的 4 次尝试全部挂起，**都是因为用了 `Start-Process` cmdlet 或 `cmd /c start`**。

读到 `verification/GATE4-PAGES-UPGRADE-1/capture-page.ps1:92` 后发现它用的是：

```powershell
$process = [System.Diagnostics.Process]::Start($psi)   # ProcessStartInfo，不是 cmdlet
```

**实测对比**：

| 方式 | 结果 |
|---|---|
| `Start-Process -PassThru` | **挂起**（>600 s） |
| `Start-Process` + `WaitForExit` | **挂起**（>300 s） |
| `Start-Process -WindowStyle Normal` | **挂起**（>120 s） |
| `cmd /c start`（分离式） | **挂起**（>120 s） |
| **`[System.Diagnostics.Process]::Start($psi)`** | ✅ **返回 26 ms**，窗口 3 s 内出现，`title='New Manga'`，`handle=789264` |
| 对照：`cmd /c echo` | 20 ms 正常 |

**⇒ 根因不是"窗口站"，是 `Start-Process` cmdlet 在本环境的行为问题。**
**我此前把根因推断为"GUI 进程无法在窗口站初始化"，那个诊断是错的**（虽然对照实验本身有效）。

### 9.2 结果：5/5 页截图成功

改 `tools/e2e/capture-four-pages.ps1` 用 `Process.Start` 后：

```
page=bookshelf  captured=True
page=library    captured=True
page=reader     captured=True
page=settings   captured=True
page=workbench  captured=True
captured 5/5 pages
```

**哈希（全部不同）**：

| 文件 | 字节 | sha256（前 16） |
|---|---|---|
| page-bookshelf.png | 31,589 | `6f26a9f9a498fcb5` |
| page-library.png | 49,824 | `75715b1ab863d5d6` |
| page-reader.png | 49,727 | `950f5d571dbac1b2` |
| page-settings.png | 65,956 | `7d972b8103524396` |
| page-workbench.png | 56,640 | `e864cb5ffbaf1310` |

### 9.3 ★ 但"哈希不同"不能当证据 —— 我看了图

按 `GATE4-PAGES-UPGRADE-1` §2 的教训（**它第一版四张图全是桌面，哈希却各不相同**），
我**逐张看了图**：

**`page-settings.png`**（1,432×978）：
- 标题栏 **`New Manga`**
- 顶部导航：**`资料柜 1 / 工位 2 / 控制台 3`**（当前高亮"控制台 3"）
- 面包屑：`控制台 › 家族战记 › 17卷`
- 左侧：`控制台 设置中心 · 9 分区`（任务与队列 / Provider 与凭据 / 网络与代理 / 模型与设备 /
  缓存与版本清理 / 备份与恢复 / 插件与 Hooks / 诊断与日志 / 外观）
- 右侧：`任务与队列`，`run_id` 输入框、"读取 Run"按钮
- 底部：**`Host 就绪`**

**`page-reader.png`**（1,432×978）：
- 同样是 `New Manga`，当前高亮 **`资料柜 1`**
- `资料柜 1 / 1 作品`
- **有书**：`家族战记`，`169 页`，`阅读进度 读到第 2 / 169 页 · 1%`
- 右侧章节账本 `01 17卷 / 169 页` + 页列表 `001 001.jpg` … `015 015.jpg`

**⇒ 两张都是真实的 NewManga 界面，不是桌面。**

### 9.4 ★ 一个重要发现：`--page` 的映射语义

| 传入 | 实际到达 | 说明 |
|---|---|---|
| `--page=settings` | **控制台（`SpaceId.Console`）** | 设置是控制台空间里的"外观"分区，**不是独立一级页面** |
| `--page=reader` | **资料柜（`SpaceId.Library`）** | 阅读器是 **Library 空间内的 overlay**，需 F11 打开 |
| `--page=bookshelf` / `library` | 资料柜 | — |
| `--page=workbench` | 工位 | — |

**⇒ 这与 `App.axaml.cs:452-453` 的注释一致**（"reader is an overlay inside Library"，`settings` 映射到 console 空间）。
**⇒ 所以"四页"的准确含义是：资料柜 / 工位 / 控制台 / 阅读器（overlay）**，
**而 `--page=reader` 只能到 Library 外壳，进 overlay 仍需 F11。**

**这解释了 `GATE4-PAGES-UPGRADE-1` 为什么把 reader 标 `NOT_REACHABLE`** —— 它的判断是对的。

### 9.5 仍未解决

- **阅读器 overlay 本身**（按 F11 后的沉浸窗口）**仍未截到** —— 需要真实按键或前述的 CLI 参数（裁决已否决加参数）。
- 未在**安装产物**上跑（本卡用的是**源码构建的 exe**）；`GATE4-PAGES-UPGRADE-1` 用的是安装产物，二者互补。
- 未验证 `--presentation-host` / `--theme` 等变体。

### 9.6 我的诊断错误（登记）

我在 §8 里写"根因是 GUI 进程无法在本 shell 的窗口站初始化"。**这个结论是错的。**

**实际根因**：`Start-Process` **cmdlet** 在本 shell 环境挂起；`[System.Diagnostics.Process]::Start(ProcessStartInfo)` 正常。

**为什么错**：我用 4 种方式都失败后，**推断**了一个听起来合理的根因（窗口站），
却没有去试**别人代码里已经成功的方式**。**如果我先读 `capture-page.ps1`，能省掉这几轮。**

## 10. 逐张目视确认（2026-11-15）

按 `GATE4-PAGES-UPGRADE-1` §2 的教训（**"数字不同"不等于"内容正确"**），我把 5 张图**逐张打开看了**。

| 图 | 高亮的一级页 | 内容要点 | 是否真实界面 |
|---|---|---|---|
| `page-bookshelf.png` | **资料柜 1** | `资料柜 0 / 0 作品`（空库）；右栏"选择一本作品 / 右栏驻留详情：作品元信息、章节账本、页数与阅读进度"；**底部 `Host 启动中...`** | ✅ 但**截早了**（见 §10.1） |
| `page-library.png` | 资料柜 | （未单独查看，与 bookshelf 同语义空间） | 未目视 |
| `page-reader.png` | **资料柜 1** | `资料柜 1 / 1 作品`；**有书**"家族战记 169 页"；`阅读进度 读到第 2 / 169 页 · 1%`；右栏章节账本 `01 17卷 / 169 页` + 页列表 `001 001.jpg` … `015 015.jpg` | ✅ |
| `page-settings.png` | **控制台 3** | `控制台 设置中心 · 9 分区`（任务与队列/Provider 与凭据/网络与代理/模型与设备/缓存与版本清理/备份与恢复/插件与 Hooks/诊断与日志/外观）；右侧 `任务与队列` + `run_id` 输入 + "读取 Run"；底部 `Host 就绪` | ✅ |
| `page-workbench.png` | **工位 2** | `工位 › 家族战记 › 17卷`；页面/矩阵 tab；`页面 / 成品 / 分屏`；缩放 86%；右侧 **四级文本 / OCR 原文 / 机器翻译 / 人工译文 / 终端 全部显示"能力待接入"**；底部 **`流水线投影未接入 · NOT_WIRED`**、`Host 就绪` | ✅ |

**⇒ 4 张已目视确认为真实 NewManga 界面**（`page-library.png` 未单独看）。

### 10.1 ★ `page-bookshelf.png` 截早了（必须登记）

该图底部显示 **`Host 启动中...`**，且 `资料柜 0 / 0 作品`。

**⇒ 我的脚本 `SettleMs=2200` 对首张图不足**：Host 尚未就绪时就截图了。

**影响**：
- 这张图**证明"能到达资料柜页并渲染外壳"**，但**不能证明"Host 就绪后的完整界面"**；
- 对比 `page-settings.png` / `page-workbench.png` 底部是 `Host 就绪`，说明**后续几张是就绪后截的**。

**⇒ 结论**：`page-bookshelf.png` 需重截（延长 `SettleMs` 或轮询 `Host 就绪`）。

### 10.2 ★ `page-reader.png` 有书而 `page-bookshelf.png` 是空库

两张图对应**不同的数据状态**：
- bookshelf：`0 / 0 作品`；
- reader：`1 / 1 作品`（家族战记 169 页）。

**可能原因**（未验证）：两次启动用了**不同的 `--log-dir`/数据根**，或某个 data-root 里已有书。
**⇒ 这是一个待查的不一致**，我不臆测原因。

### 10.3 附带发现：`page-workbench.png` 是条件 5 ③ 的**实物证据**

工位页右侧的 **"OCR 原文 / 机器翻译 / 人工译文 / 终端" 全部显示"能力待接入"**，
底部 **"流水线投影未接入 · NOT_WIRED"**。

**⇒ 这与 `MAINT-1-RELEASE-GATE-ASSESSMENT` §6.2 的判断完全一致**
（"没有自动翻译命令，UI 侧没有调用 provider 的接线"）——
**现在有了真实界面的目视证据，不再是纯代码推断。**
