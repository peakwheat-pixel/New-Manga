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
