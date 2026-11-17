# 条件 3 · F11 真实窗口截图证据（2026-11-17，DSH）

## 这次做了什么

用 **INSTALLER-MATRIX-1 的发布产物**（stage 里的 `NewManga.App.exe`，99,554,850 B）在**真实桌面会话**上启动应用，
数据根指向 `BOOK-FIXTURE-1/isolated-data` 的副本（隔离，不碰真实 `%APPDATA%`），然后：
1. 等 Host 就绪（20 s）→ 截书架页；
2. 发送 `{F11}` → 截沉浸阅读器。

## 命令与环境（可复现）

```powershell
$stage = 'G:\CODEX\New Manga.workspace\task-envs\INSTALLER-MATRIX-1\stage\NewManga-0.1.1-win-x64\app'
$exe   = Join-Path $stage 'NewManga.App.exe'
# 数据根 = BOOK-FIXTURE-1/isolated-data 的副本；日志根独立
$args  = '--data-root "<copy>" --log-dir "<out>\logs"'
Start-Process -FilePath $exe -ArgumentList $args -WorkingDirectory $stage
# 窗口显示后：ShowWindow(SW_MAXIMIZE) → SetForegroundWindow → 等 20 s
# 截图：GetWindowRect + Graphics.CopyFromScreen → PNG
# 然后 SendKeys '{F11}' → 等 5 s → 再截一张
```

- 会话：`query session` 显示 session 1 **Active**，`explorer` 1 个，`[Environment]::UserInteractive=True`。
- 窗口：`-8,-8 2576x1408`（最大化；分辨率 2576×1408，任务栏外）。
- 应用退出后无残留进程（脚本核对过）。

## 证据文件

| 文件 | sha256 | 内容 |
|---|---|---|
| `c3-01-library.png` | `c96f2c9ab1c073f9e1e47cbd6196143fa1b659e08cd600348a36a082801c6f1b` | 书架页：`书架 1/1 作品`、书卡 `BOOK-FIXTURE-1 日漫 JA 测试书`、右侧章节/页列表 `001…008`（`ja_Pepper-and-Carrot_by-David-Revoy…`）、状态栏 **Host 就绪** |
| `c3-02-f11-immersive-empty.png` | `108258b9ea37a9f3b752ba77766221b14a8b6fe61305c424ca746bb685829e76` | **F11 沉浸阅读器**：无窗口边框/无标题栏；左上 `返回 (Esc)`、`阅读`；右上 `分页`、`Webtoon 纵向`、`RTL`；右下翻页控件点；中央空态提示「页面不可用：Host 资源通道未输入该页没有图像（不伪造图片）」 |
| `c3-startup.log` / `c3-host.log` / `c3-core_service.stderr.log` | — | 同一次运行的启动/Host/Core stderr 日志 |

## 能证明什么 / 不能证明什么

**能证明**：
- 发布产物能在真实 Windows 桌面会话启动并到 **Host 就绪**；
- **F11 会把阅读器切到全屏沉浸 overlay**：没有窗口边框/标题栏，控件贴在四角（左上返回/阅读、右上模式、右下翻页），
  阅读区铺满 2576×1408，**没有裁切**、没有遮挡整幅的浮层；
- 空数据时给出**诚实的空态提示**，不伪造图片。

**不能证明**（如实登记，不得用这份证据冒充）：
- **没有页面图像**：本次未选中具体页（脚本的双击未命中书架卡片，截图字节未变可证），
  因此**阅读内容区的渲染质量、分页/Webtoon 两种模式的布局、缩放与裁切**都**未覆盖**；
- 未覆盖 IME、题注/气泡、SFX 等 overlay 次级功能；
- 这是一次**单机单次**观察，不是矩阵。

## 结论

条件 3 的状态从 `AGENT_ADJUDICATION_PENDING`（无任何真实窗口证据）推进为
**`PARTIAL_WINDOW_EVIDENCE`**：overlay 的**全屏/无边框/控件布局**已有真实截图可裁定；
**内容渲染**仍缺「选中页面后的 F11 截图」，仍不是 MET。
