# VERIFY-RECHECK-1 报告：REPACK-4 三项真机复测补证

- 父任务：RELEASE-REPACK-4（已收口 done，集成 `caa0fdda8`）
- 本任务：VERIFY-RECHECK-1（team task-56）
- 使用包：`task-envs/RELEASE-REPACK-4/out/NewManga-0.1.0-win-x64-models`（**未重打包**）
- 基线 HEAD：`caa0fdda8`；未改产品源码；未 push；无伪造证据。

## 1. Mica 复测（90s 窗口）→ **非回归**

| 阶段 | 结果 |
|---|---|
| 第 1 次运行（pid 54660） | 启动后 **100s** 再读：`window-material.log` 全部 `actual=None`（该 run 主窗被 Explorer 的 exports 窗口与沉浸阅读器遮挡）；`DWMWA_SYSTEMBACKDROP_TYPE` type=0 |
| 干净重启（关闭旧实例，主窗可见） | **`material=Mica; requested=Mica,Blur,None; actual=Mica`**（2026-10-27T17:17:53Z，约启动后 35s，<90s 窗口内）；窗口边缘像素为壁纸透色（四角 [166,166,166]/[122,130,136]/[65,83,114]/[78,82,96]），中心为主题色 [245,243,250] |
| 代码对照 | MICA-FIX-1（`c795cdb34`/merge `93aaaeb8c`）在 `4ea86e03a` 的祖先链上（=True）；`MainWindow.axaml` 的 Background 行与 `a256ae63b`（MICA-FIX-1 done）一致；`MainWindow.axaml.cs` 的 `MicaFallback`/`TransparencyLevelHint`/`WriteMaterialDiagnostics` 均在位 |

**结论**：**非回归**。`4be1c3f4f` 回退目标 `4ea86e03a` 已包含 MICA-FIX-1，代码无变化；REPACK-4 的 `actual=None` 是测量时序/窗口遮挡下的合成状态，不是代码回归。
（注：`DWMWA_SYSTEMBACKDROP_TYPE` 在两状态下均为 0，Avalonia 不上报该 DWM 属性，不能作为唯一判据。）

## 2. 4K@200% → **NOT_ACHIEVABLE（环境阻塞，未发生系统变更）**

- 基线：`Screen.AllScreens` 仅 1 块（`\\.\DISPLAY1` 2560×1440@96dpi=100%）；`Win32_DesktopMonitor` 显示 3840×2160 与 `WmiMonitorID=Mi TV` 说明 4K 屏物理连接但**未加入桌面**；`GetDpiForMonitor(3000,500)` hr=-2147024890（无有效 monitor）。
- 尝试：`DisplaySwitch.exe /extend`（两次）、`Win+P` 投影面板（截图 `recheck-4k-project-pane*.png`）、点击「扩展」（截图 `recheck-4k-extend-before/extended.png`）→ **仍 1 块屏、无缩放变化**。
- 因无系统变更，**无需还原**；未伪报 `GetDpiForWindow=192`。

## 3. Esc/H 键盘（沉浸窗聚焦后）→ **PASS**

- 流程：UIA「沉浸模式」→ 枚举窗口取最大窗口（`阅读器` h=7868716，0,0,2560×1440）→ `AttachThreadInput`+`SetForegroundWindow` → `keybd_event`。
- 判据：截图 sha16 `before=AB3DF5C1F663223B`、`immersive=F6CE796852411DB4`、`after_H=FDED931F9657C80D`、`after_Esc=392E1E10AFCD9E02`；窗口数=2。
- **H**：`esc-h-03-after-h.png` 中顶部 `Esc 退出 · F fit · H 隐藏 UI` 提示条消失（HUD 隐藏）→ H 生效。
- **Esc**：sha 变化、UI 状态回到阅读器 → Esc 生效。
- 对比 REPACK-4（后台仅按钮路径可用）：本次**先让沉浸窗获得前台焦点再发键**，键盘路径成立。

## 4. 证据文件

| 文件 | 内容 |
|---|---|
| `screens/recheck-mica-t0.png`、`recheck-mica-t100.png`、`recheck-mica-focused.png`、`recheck-mica-clean.png` | Mica 时序/遮挡/干净重启取色 |
| `mica-window-material-tail.log` | app 诊断日志末段（含 `actual=Mica` 行） |
| `screens/recheck-4k-*.png` | 显示状态、投影面板、扩展尝试 |
| `screens/esc-h-01..04.png` | Esc/H 前后与窗口数判据 |
| `recheck.json` | 三项结构化结论与 sha 值 |

## 5. 遗留

1. **4K@200%** 仍无法在本机验证：Mi TV 需系统识别为可用输出后才能临时扩展 + 200%，当前环境不具备（未做任何系统改动，无需还原）。
2. Mica 已闭环为非回归；后续真机验收只需在主窗可见状态（无全屏遮挡）下读取诊断日志即可。
3. Esc/H 键盘路径已验证；如产品后续把 `Esc 退出` 与 `H 隐藏 UI` 拆到独立窗口，可复用本判据。
